"""Offline analysis; preserves raw files and never launches a compositor."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from PIL import Image, ImageChops

parser = argparse.ArgumentParser()
parser.add_argument('lab', type=Path)
args = parser.parse_args()
lab = args.lab.resolve()
repo = Path(__file__).resolve().parents[3]
results = lab / 'results'
results.mkdir(exist_ok=True)


def write(name, value):
    (results / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def fields(line):
    return dict(re.findall(r'(\w+)=([^\s]+)', line))


def ns(line):
    match = re.search(r'\bns=(\d+)', line)
    return int(match.group(1)) if match else None


def count_changed(left, right):
    a = Image.open(left).convert('RGB')
    b = Image.open(right).convert('RGB')
    diff = ImageChops.difference(a, b)
    box = diff.getbbox()
    n = sum(any(px) for px in diff.get_flattened_data())
    return {'pixels': n, 'box': box, 'dimensions': a.size}


def color_count(path, color):
    im = Image.open(path).convert('RGB')
    return sum(px == color for px in im.get_flattened_data())


matrix = {}
lifecycle = {}
timeline = {}
identities = {}
buffers = {}
parentage = {}
clips = {}
renders = {}
hits = {}
delivery = {}
commits = {}
presents = {}
damage = {}
pixels = {}
timeouts = {}
for mode in ('control', 'private_standard', 'private_mosaic'):
    paths = sorted((lab / 'runs').glob(f'saved-{mode}-*'))
    if len(paths) != 1:
        raise RuntimeError(f'{mode}: expected exactly one run, found {len(paths)}')
    run = paths[0]
    events = [json.loads(line) for line in (run / 'events.jsonl').read_text().splitlines()]
    lines = (run / 'compositor.log').read_text().splitlines()
    client = (run / 'client.log').read_text().splitlines()
    exit_state = json.loads((run / 'exit-status.json').read_text())
    identity = next((x for x in events if x['kind'] == 'identity'), None)
    identities[mode] = {'owner': identity['owner'] if identity else None,
                        'workspace': identity['workspace'] if identity else None}
    tree_events = [{'event': line.split()[0], **fields(line)} for line in lines
                   if line.startswith(('SB_TREE_CREATE', 'SB_TREE_DESTROY', 'SB_ENABLE'))]
    buffer_events = [fields(line) for line in lines if line.startswith('SB_BUFFER_CREATE')]
    render_events = [fields(line) for line in lines if line.startswith('SB_RENDER')]
    lifecycle[mode] = tree_events
    buffers[mode] = buffer_events
    parentage[mode] = [{'tree': x.get('tree'), 'parent': x.get('parent'),
                        'content': x.get('content'), 'view': x.get('view'),
                        'container': x.get('con'), 'ns': x.get('ns')}
                       for x in tree_events if x['event'] == 'SB_TREE_CREATE']
    clips[mode] = [line for line in lines if 'PI_SCENE output=HEADLESS-1' in line]
    renders[mode] = render_events
    hits[mode] = [x for x in events if x['kind'] in ('pointer', 'hit_sample')]
    delivery[mode] = [line for line in client if line.startswith(('ENTER', 'LEAVE', 'MOTION', 'BUTTON'))]
    commits[mode] = [line for line in lines if 'PI_OUTPUT_COMMIT ' in line]
    presents[mode] = [line for line in lines if 'PI_OUTPUT_PRESENT ' in line]
    damage[mode] = {'status': 'NOT TESTED', 'reason': 'no transaction-scoped physical damage extents captured'}
    timeouts[mode] = [line for line in lines if 'timed out' in line]
    timeline[mode] = {
        'client': [line for line in client if line.startswith(('XDG_CONFIGURE', 'HELD', 'ACK', 'COMMIT', 'PONG', 'EXIT'))],
        'episodes': [x for x in events if x['kind'] in ('episode_start', 'held', 'timeout_observed', 'failure')],
        'transactions': [line for line in lines if 'Transaction ' in line and
                         any(word in line for word in ('committing', 'ready', 'timed out'))],
    }
    px = {}
    for side in ('left', 'right'):
        reference = run / f'{side}-reference.png'
        px[side] = {}
        for tag in ('ack-held', 'ack-applied', 'timeout-held', 'timeout-applied'):
            path = run / f'{side}-{tag}.png'
            if path.exists():
                px[side][tag] = {
                    'full_reference_diff': count_changed(reference, path),
                    'initial_client_color_pixels': color_count(path, (35, 68, 204)),
                    'alternate_client_color_pixels': color_count(path, (32, 208, 160)),
                }
    pixels[mode] = px
    episode_data = {}
    for kind in ('ack', 'timeout'):
        start = next((x['ns'] for x in events if x['kind'] == 'episode_start' and x['episode'] == kind), None)
        capture = next((x['after_ns'] for x in events if x['kind'] == 'capture'
                        and x['tag'] == f'{kind}-held' and x['output'] == 'HEADLESS-2'), None)
        created = [x for x in buffer_events if start and capture and
                   start < int(x['ns']) < capture]
        nodes = {x['node'] for x in created}
        rendered = [x for x in render_events if start and capture and
                    start < int(x['ns']) < capture and x.get('node') in nodes]
        episode_data[kind] = {'start_ns': start, 'held_capture_end_ns': capture,
                              'saved_buffers_created': len(created),
                              'created_nodes_rendered': len({x['node'] for x in rendered}),
                              'render_entries': len(rendered),
                              'created_nodes': sorted(nodes),
                              'rendered_nodes': sorted({x['node'] for x in rendered})}
    owner = identities[mode]['owner'] or {}
    workspace = identities[mode]['workspace'] or {}
    scroll = workspace.get('mosaic', {}).get('rows', [{}])[0].get('scroll_x', 0)
    # IPC rect is the logical owner; applied tile_scene in PI_SCENE is the
    # private camera translation. Actual render entries remain the authority.
    predicted_left = owner.get('rect', {}).get('x', 0) - scroll
    predicted_right = predicted_left + owner.get('rect', {}).get('width', 0)
    boundary = predicted_left < 0 < predicted_right
    matrix[mode] = {'exit': exit_state, 'episodes': episode_data,
                    'owner_id': owner.get('id'), 'workspace_id': workspace.get('id'),
                    'layout': workspace.get('layout'), 'observed_scroll': scroll,
                    'owner_camera_box_estimate': [predicted_left, predicted_right],
                    'target_boundary_estimate': boundary,
                    'target_boundary_gate': 'NOT EXERCISED' if mode == 'private_mosaic' and not boundary else 'CONTROL_OR_CANDIDATE',
                    'input_during_snapshot': 'NOT TESTED' if not hits[mode] else 'PARTIAL',
                    'damage_coverage': 'NOT TESTED'}

budget = json.loads((lab / 'saved-budget.json').read_text())
write('saved-buffer-lifecycle.json', lifecycle)
write('transaction-timeline.json', timeline)
write('view-identities.json', identities)
write('buffer-identities.json', buffers)
write('scene-parentage.json', parentage)
write('clip-observations.json', clips)
write('render-entries.json', renders)
write('pointer-hits.json', hits)
write('client-delivery.json', delivery)
write('output-commits.json', commits)
write('presentations.json', presents)
write('damage-analysis.json', damage)
write('pixel-analysis.json', pixels)
write('timeout-analysis.json', timeouts)
write('budget.json', budget)
write('matrix.json', matrix)
summary = {'result': 'INCONCLUSIVE', 'architectural_conclusion': 'UNDECIDED',
           'reason': 'Mosaic target snapshot did not cross x=0; target was outside H1 after relative scroll applied to existing camera',
           'standard_fixture_incident': 'pointer sampling overran the 1200 ms ACK window; its reserved ACK episode failed and no second standard run was made',
           'runs': {mode: matrix[mode]['exit']['failure'] for mode in matrix},
           'budget': budget,
           'unexercised': ['target partial-boundary clipping', 'saved-target pixels on H1',
                           'node-at/input during Mosaic target snapshot', 'camera hide while target snapshot active',
                           'mapped-view destruction', 'transaction-scoped damage coverage',
                           'native output buffer identity', 'all intermediate frames']}
write('summary.json', summary)


def manifest(paths, destination):
    with destination.open('w') as out:
        for path in sorted(set(paths)):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            out.write(f'{digest}  {path}\n')


source_files = [p for root in ('standard', 'mosaic', 'scenefx')
                for p in (lab / root).rglob('*') if p.is_file() and '.git' not in p.parts]
source_files += [p for p in (repo / 'tooling/probes/step20c-saved-transaction-buffer').iterdir()
                 if p.is_file()]
manifest(source_files, results / 'source-sha256.txt')
evidence_files = [p for p in (lab / 'runs').rglob('*') if p.is_file()]
evidence_files += [p for p in results.iterdir() if p.is_file() and p.name not in
                   ('source-sha256.txt', 'evidence-sha256.txt')]
evidence_files += [lab / 'saved-budget.json', lab / 'saved-build-log.txt']
manifest(evidence_files, results / 'evidence-sha256.txt')
print(f'RESULT=INCONCLUSIVE RESULTS={results}')
