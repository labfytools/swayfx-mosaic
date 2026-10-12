"""Correlate bounded headless mutations without assigning input a frame ID."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil

from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('lab', type=Path)
args = ap.parse_args()
lab = args.lab.resolve()
repo = Path(__file__).resolve().parents[3]
out = lab / 'mutation-results'
out.mkdir(exist_ok=True)
fixture = Path(__file__).parent
shutil.copyfile(fixture / 'inventory.json', out / 'inventory.json')


def fields(line, marker):
    if marker not in line:
        return None
    return dict(re.findall(r'(\w+)=([^ ]+)', line.split(marker, 1)[1]))


def read_run(mode, kind):
    matches = sorted((lab / 'runs').glob(f'{mode}-{kind}-asi0-*'))
    if len(matches) != 1:
        raise RuntimeError(f'expected one {mode}/{kind} run, got {len(matches)}')
    run = matches[0]
    events = [json.loads(x) for x in (run / 'events.jsonl').read_text().splitlines()]
    log = (run / 'compositor.log').read_text(errors='replace').splitlines()
    records = {key: [f for line in log if (f := fields(line, key + ' '))]
               for key in ('ASI_MUTATION', 'ASI_HIT', 'BI_STAGE',
                           'PI_OUTPUT_COMMIT', 'PI_OUTPUT_PRESENT',
                           'ASI_LOCKED', 'ASI_RELEASE')}
    commits = {(x['output'], x['commit_seq']) for x in records['PI_OUTPUT_COMMIT']}
    presents = {(x['output'], x['commit_seq']) for x in records['PI_OUTPUT_PRESENT']}
    client = (run / 'client.log').read_text(errors='replace')
    status = json.loads((run / 'exit-status.json').read_text())
    return run, events, records, client, status, commits, presents


matrix = {}
for mode in ('control', 'private_standard', 'private_mosaic'):
    for kind in ('cycles', 'mutation_content', 'mutation_input_region'):
        run, events, rec, client, status, commits, presents = read_run(mode, kind)
        entry = {
            'run': str(run), 'mode': mode, 'scenario': kind,
            'runner_failure': status['failure'], 'captures': status['captures'],
            'commits': len(commits), 'presents': len(presents),
            'unpaired_commits': sorted([list(x) for x in commits - presents]),
            'hit_count': len(rec['ASI_HIT']),
            'epoch_events': len(rec['ASI_MUTATION']),
            'buffer_locks': len(rec['ASI_LOCKED']),
            'buffer_releases': len(rec['ASI_RELEASE']),
            'popup_grabs': client.count('GRAB_REQUEST'),
            'popup_creates': [x for x in client.splitlines() if 'POPUP_' in x and ' CREATE ' in x],
            'popup_destroys': [x for x in client.splitlines() if 'POPUP_' in x and ' DESTROY ' in x],
        }
        if kind == 'cycles':
            entry['A_buttons_after_B_close'] = len(re.findall(
                r'POINTER_BUTTON target=POPUP_A[^\n]*button=273 state=1', client))
            entry['camera_stages'] = [
                {k: x.get(k) for k in ('output', 'scroll', 'tile_scene', 'clip', 'epoch')}
                for x in rec['BI_STAGE'] if x.get('phase') == 'COMMIT_ACCEPTED'
                and x.get('output') == 'HEADLESS-1'
                and x.get('scroll') in ('400', '1280')]
        elif kind == 'mutation_content':
            entry['client_new_buffer'] = 'COMMAND recolor_top DONE' in client and (
                client.count('TOPLEVEL MAP') >= 2)
            entry['pixels'] = {tag: Image.open(run / f'left-content-{tag}.png').getpixel((342, 175))
                               for tag in ('before', 'after')}
            boundary = [e for e in events if e['kind'] == 'client_request'
                        and e['value'] == 'recolor_top'][0]['monotonic_ns']
            entry['commits_after_request'] = [x for x in rec['PI_OUTPUT_COMMIT']
                if x['output'] == 'HEADLESS-1' and int(x['ns']) > boundary]
            entry['stages_after_request'] = [{k: x.get(k) for k in
                ('commit_seq', 'scroll', 'tile_scene', 'clip', 'epoch', 'ns')}
                for x in rec['BI_STAGE'] if x.get('phase') == 'COMMIT_ACCEPTED'
                and x['output'] == 'HEADLESS-1' and int(x['ns']) > boundary]
        else:
            entry['pixels'] = {tag: Image.open(run / f'left-region-{tag}.png').getpixel((342, 175))
                               for tag in ('full-before', 'empty', 'full-after')}
            entry['client_top_button_presses'] = len(re.findall(
                r'POINTER_BUTTON target=TOPLEVEL[^\n]*button=273 state=1', client))
            entry['hit_sequence'] = [
                {k: x.get(k) for k in ('ns', 'epoch', 'lx', 'ly', 'node', 'surface',
                                       'logical_scroll', 'tile_scene', 'clip')}
                for x in rec['ASI_HIT'] if x.get('lx') == '-458.00' or
                (mode == 'private_standard' and x.get('lx') == '-458.00')]
        matrix[f'{mode}/{kind}'] = entry

(out / 'scenario-matrix.json').write_text(json.dumps(matrix, indent=2) + '\n')
hold_runs = sorted((lab / 'runs').glob('private_mosaic-mutation_hold_exit-asi1-*'))
if len(hold_runs) != 1:
    raise RuntimeError(f'expected one real output-destroy run, got {len(hold_runs)}')
hold = hold_runs[0]
hold_log = (hold / 'compositor.log').read_text(errors='replace').splitlines()
hold_status = json.loads((hold / 'exit-status.json').read_text())
lifetime = {
    'runtime_output_destroy': {
        'run': str(hold), 'runner_failure': hold_status['failure'],
        'compositor_exit': hold_status['compositor'],
        'locks': [fields(x, 'ASI_LOCKED ') for x in hold_log if 'ASI_LOCKED ' in x],
        'releases': [fields(x, 'ASI_RELEASE ') for x in hold_log if 'ASI_RELEASE ' in x],
        'selected_present_retained': any('ASI_TEST_HOLD id=1 ' in x for x in hold_log),
    },
    'runtime_rejected_commit': 'NOT TESTED',
    'synthetic_rejected_commit': 'see lifetime-model.c; no backend triggered',
}
(out / 'lifetime.json').write_text(json.dumps(lifetime, indent=2) + '\n')
sources = [
    fixture / 'mutation-client.patch', fixture / 'prepare.sh', fixture / 'run.py', fixture / 'analyze.py',
    fixture / 'inventory.json', fixture / 'lifetime-model.c',
    lab / 'nested-client.c', lab / 'mosaic/sway/desktop/transaction.c',
    lab / 'mosaic/sway/desktop/output.c', lab / 'mosaic/sway/desktop/xdg_shell.c',
    lab / 'mosaic/sway/input/cursor.c', lab / 'mosaic/sway/input/seat.c',
    lab / 'scenefx/types/scene/wlr_scene.c',
    lab / 'wlroots/types/scene/surface.c',
    lab / 'wlroots/types/scene/subsurface_tree.c',
]
with (out / 'source-sha256.txt').open('w') as dst:
    for p in sources:
        dst.write(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p}\n')
with (out / 'artifact-sha256.txt').open('w') as dst:
    for p in sorted((lab / 'runs').glob('*')):
        if not p.is_dir() or ('asi0' not in p.name and 'mutation_hold_exit-asi1' not in p.name):
            continue
        for f in sorted(p.rglob('*')):
            if f.is_file():
                dst.write(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f}\n')
    for p in (out / 'inventory.json', out / 'scenario-matrix.json',
              out / 'lifetime.json', out / 'source-sha256.txt'):
        dst.write(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p}\n')
print(f'MATRIX={out / "scenario-matrix.json"} SOURCES={len(sources)} '
      f'ARTIFACTS={len((out / "artifact-sha256.txt").read_text().splitlines())}')
