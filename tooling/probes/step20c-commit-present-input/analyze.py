"""Order executed server callbacks; keep client receipt on its own clock."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('lab', type=Path)
args = ap.parse_args()
lab = args.lab.resolve()
out = lab / 'commit-present-input-results'
out.mkdir(exist_ok=True)
markers = {
    'ORDER_SURFACE_COMMIT': 'surface_commit',
    'BI_STAGE': 'output_build',
    'PI_OUTPUT_COMMIT': 'output_commit',
    'PI_OUTPUT_PRESENT': 'output_present',
    'ASI_HIT': 'scene_hit',
    'ASI_DELIVERY': 'pointer_delivery',
}


def save(name, value):
    (out / name).write_text(json.dumps(value, indent=2) + '\n')


events = []
matrix = {}
client_delivery = {}
pixels = {}
for mode in ('control', 'private_standard', 'private_mosaic'):
    matches = sorted((lab / 'runs').glob(f'{mode}-ordering-asi0-*'))
    if len(matches) != 1:
        raise RuntimeError(f'expected one {mode} run, found {len(matches)}')
    run = matches[0]
    status = json.loads((run / 'exit-status.json').read_text())
    if status['failure'] is not None:
        raise RuntimeError(f'{mode} runner failed: {status["failure"]}')
    for line_number, line in enumerate((run / 'compositor.log').read_text(errors='replace').splitlines()):
        for marker, kind in markers.items():
            if marker + ' ' not in line:
                continue
            fields = dict(re.findall(r'(\w+)=([^ ]+)', line.split(marker + ' ', 1)[1]))
            if 'ns' not in fields:
                continue
            events.append({'mode': mode, 'kind': kind, 'line': line_number,
                           **fields, 'ns': int(fields['ns'])})
            break
    client = (run / 'client.log').read_text(errors='replace')
    client_delivery[mode] = {
        'run': str(run),
        'top_button_presses': len(re.findall(
            r'POINTER_BUTTON target=TOPLEVEL[^\n]*button=273 state=1', client)),
        'region_empty_commands': client.count('COMMAND region_empty_top DONE'),
        'region_full_commands': client.count('COMMAND region_full_top DONE'),
        'popup_grabs': client.count('GRAB_REQUEST'),
        'client_lines': [x for x in client.splitlines() if
                         'COMMAND region_' in x or
                         'POINTER_BUTTON target=TOPLEVEL' in x],
    }
    pixels[mode] = {}
    for tag in ('ordering-P0-reference', 'ordering-P1-empty', 'ordering-P4-restored'):
        pixels[mode][tag] = Image.open(run / f'left-{tag}.png').getpixel((342, 175))
    matrix[mode] = {'run': str(run), 'runner_failure': None,
                    'duration_seconds': status['duration_seconds'],
                    'captures': status['captures'],
                    'pixels': pixels[mode], **{k: v for k, v in
                    client_delivery[mode].items() if k != 'client_lines'}}

# Same-process timestamps can be ordered. Equal timestamps retain log order.
events.sort(key=lambda e: (e['mode'], e['ns'], e['line']))
target_mutations = [e for e in events if e['kind'] == 'surface_commit'
                    and e.get('input_changed') == '1'
                    and e.get('width') == '420' and e.get('height') == '320']
with (out / 'event-order.jsonl').open('w') as dst:
    for event in events:
        dst.write(json.dumps(event) + '\n')
for name, kind in (
        ('surface-commits.json', 'surface_commit'),
        ('output-commits.json', 'output_commit'),
        ('presentations.json', 'output_present'),
        ):
    save(name, [e for e in events if e['kind'] == kind])
save('input-regions.json', target_mutations)
save('client-delivery.json', client_delivery)

hits = []
for hit in (e for e in events if e['kind'] == 'scene_hit'):
    prior_inputs = [e for e in target_mutations if e['mode'] == hit['mode']
                    and e['ns'] <= hit['ns']]
    prior_commits = [e for e in events if e['mode'] == hit['mode']
                     and e['kind'] == 'output_commit'
                     and e.get('output') == hit.get('output') and e['ns'] <= hit['ns']]
    prior_presents = [e for e in events if e['mode'] == hit['mode']
                      and e['kind'] == 'output_present'
                      and e.get('output') == hit.get('output') and e['ns'] <= hit['ns']]
    next_presents = [e for e in events if e['mode'] == hit['mode']
                     and e['kind'] == 'output_present'
                     and e.get('output') == hit.get('output') and e['ns'] > hit['ns']]
    hits.append({**hit,
                 'last_target_input': prior_inputs[-1] if prior_inputs else None,
                 'last_output_commit_seq': prior_commits[-1].get('commit_seq')
                     if prior_commits else None,
                 'last_present_seq': prior_presents[-1].get('commit_seq')
                     if prior_presents else None,
                 'next_present_seq': next_presents[0].get('commit_seq')
                     if next_presents else None,
                 'input_identity_inferred': hit.get('surface') == '(nil)'})
save('scene-hits.json', hits)

timelines = []
for mode in ('control', 'private_standard', 'private_mosaic'):
    group = [e for e in events if e['mode'] == mode]
    commits = [e for e in group if e['kind'] == 'output_commit']
    presents = {(e.get('output'), e.get('commit_seq')): e for e in group
                if e['kind'] == 'output_present'}
    for commit in commits:
        present = presents.get((commit.get('output'), commit.get('commit_seq')))
        between = [e for e in group if present and
                   commit['ns'] < e['ns'] < present['ns'] and
                   e['kind'] in ('surface_commit', 'scene_hit', 'pointer_delivery')]
        timelines.append({'mode': mode, 'output': commit.get('output'),
                          'commit_seq': commit.get('commit_seq'),
                          'commit_ns': commit['ns'],
                          'present_ns': present['ns'] if present else None,
                          'presented': present.get('presented') if present else None,
                          'gap_ns': present['ns'] - commit['ns'] if present else None,
                          'between': between,
                          'input_mutation_between': any(e in target_mutations
                              for e in between),
                          'hit_between': any(e['kind'] == 'scene_hit' for e in between)})
save('timelines.json', timelines)
for mode in matrix:
    group = [e for e in events if e['mode'] == mode]
    intervals = [x for x in timelines if x['mode'] == mode]
    matrix[mode].update({
        'surface_input_commits': sum(e in target_mutations for e in group),
        'native_commits': sum(e['kind'] == 'output_commit' for e in group),
        'native_presents': sum(e['kind'] == 'output_present' for e in group),
        'commit_present_interleavings': sum(x['input_mutation_between'] for x in intervals),
        'commit_mutation_hit_present': sum(x['input_mutation_between'] and
            any(e['kind'] == 'scene_hit' for e in x['between']) for x in intervals),
        'gap_ns_min': min((x['gap_ns'] for x in intervals if x['gap_ns'] is not None),
                          default=None),
        'gap_ns_max': max((x['gap_ns'] for x in intervals if x['gap_ns'] is not None),
                          default=None),
    })
save('matrix.json', matrix)
summary = {'modes': list(matrix), 'interleavings': sum(x['input_mutation_between']
           for x in timelines), 'commit_mutation_hit_present': sum(
           x['input_mutation_between'] and x['hit_between'] for x in timelines),
           'clock_contract': 'server timestamps only; client order separate',
           'p2': 'OBSERVED' if any(x['input_mutation_between'] for x in timelines)
           else 'INCONCLUSIVE', 'rejected_backend_commit': 'NOT TESTED'}
save('summary.json', summary)
with (out / 'source-sha256.txt').open('w') as dst:
    for p in (Path(__file__), Path(__file__).parent / 'run.py',
              Path(__file__).parent / 'prepare.sh',
              Path(__file__).parent / 'surface-ordering.patch'):
        dst.write(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.resolve()}\n')
with (out / 'artifact-sha256.txt').open('w') as dst:
    for p in sorted(out.glob('*.json')) + [out / 'event-order.jsonl',
                                           out / 'source-sha256.txt']:
        dst.write(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p}\n')
print(json.dumps(summary))
