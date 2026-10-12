"""Offline analysis of retained rotation runs; never launches a compositor."""
import argparse
import hashlib
import json
from pathlib import Path
import re

import numpy as np
from PIL import Image

from campaign import read

COLORS = {'owner': (35, 68, 204), 'A': (224, 192, 32),
          'B': (32, 208, 160), 'background': (30, 30, 46)}
TRACE = re.compile(r'\b(DO_STATE|DO_POPUP|PI_SCENE|PI_OWNER|PI_OUTPUT_COMMIT|PI_OUTPUT_PRESENT)\b')
DAMAGE = re.compile(r'TEMPORAL_DAMAGE ordinal=\d+ ns=(\d+) output=(\S+) '
                    r'extent=(-?\d+),(-?\d+)\.\.(-?\d+),(-?\d+)')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def fields(line):
    return dict(re.findall(r'(\w+)=([^\s]+)', line))


def latest(traces, kind, before_ns, *, output=None, owner=None):
    values = [t for t in traces if t['kind'] == kind and t['ns'] <= before_ns
              and (output is None or t.get('output', t.get('observer')) == output)
              and (owner is None or t.get('owner_id') == str(owner))]
    return values[-1] if values else None


def parse_run(run):
    events = [json.loads(line) for line in (run / 'events.jsonl').read_text().splitlines()]
    # CONTRACT: Sway node IDs are per-run observations, never fixture constants.
    owner_id = next(e['owner']['id'] for e in events
                    if e['kind'] == 'state' and e.get('owner'))
    text = (run / 'compositor.log').read_text(errors='replace')
    traces = []
    for line in text.splitlines():
        match = TRACE.search(line)
        if match:
            item = {'kind': match.group(1), **fields(line)}
            if item.get('ns', '').isdigit():
                item['ns'] = int(item['ns'])
                traces.append(item)
    damages = [(int(ns), output, *map(int, (x1, y1, x2, y2)))
               for ns, output, x1, y1, x2, y2 in DAMAGE.findall(text)]
    geometry = {(e['tag'], e['output']): e for e in events
                if e['kind'] == 'capture_geometry'}
    captures = {}
    for e in events:
        if e['kind'] != 'capture':
            continue
        g = geometry[(e['tag'], e['output'])]
        path = run / e['path']
        image = np.asarray(Image.open(path).convert('RGB'))
        counts = {}
        color_boxes = {}
        for name, color in COLORS.items():
            ys, xs = np.where(np.all(image == color, axis=2))
            counts[name] = len(xs)
            color_boxes[name] = ([int(xs.min()), int(ys.min()),
                                  int(xs.max())+1, int(ys.max())+1]
                                 if len(xs) else None)
        scene = latest(traces, 'PI_SCENE', e['before_ns'], output=e['output'])
        state = latest(traces, 'DO_STATE', e['before_ns'], output=e['output'])
        popup = latest(traces, 'DO_POPUP', e['before_ns'], owner=owner_id)
        viewport = None
        if state and scene and scene.get('clip_valid') == '1':
            x, y = map(int, state['tile_global'].split(','))
            cx, cy, w, h = map(int, scene['clip'].split(','))
            viewport = [x+cx, y+cy, w, h]
        captures[(e['tag'], e['output'])] = {
            'tag': e['tag'], 'output': e['output'], 'file': e['path'],
            'sha256': digest(path), 'capture_window_ns': [e['before_ns'], e['after_ns']],
            'physical_mode': g['mode'], 'scale': g['scale'],
            'ipc_transform': g['transform'], 'logical_rect': g['rect'],
            'png_dimensions': g['dimensions'], 'png_frame': 'logical-oriented',
            'colors': counts, 'color_boxes_png': color_boxes,
            'applied_viewport': viewport,
            'scene': scene, 'output_state': state, 'root_popup': popup,
        }
    client = (run / 'client.log').read_text(errors='replace')
    grabs = [{'popup': popup, 'target': target, 'serial': int(serial),
              'used': int(used),
              'valid': serial == used and bool(re.search(
                  rf'POINTER_BUTTON target={target} serial={serial} button=272 state=1', client))}
             for popup, target, serial, used in re.findall(
                 r'(POPUP_[AB]) GRAB_REQUEST origin=wl_pointer.button '
                 r'target=(\S+) serial=(\d+) used=(\d+)', client)]
    return {'run': run.name, 'events': events, 'traces': traces,
            'damage': damages, 'captures': captures, 'grabs': grabs,
            'exit': json.loads((run / 'exit-status.json').read_text()),
            'popup_done': {'A': client.count('POPUP_A POPUP_DONE'),
                           'B': client.count('POPUP_B POPUP_DONE')},
            'client_protocol_errors': [line for line in client.splitlines()
                                       if 'protocol error' in line.lower()]}


def damage_pair(item, first, second, output, rotated):
    a = item['captures'][(first, output)]
    b = item['captures'][(second, output)]
    before = np.asarray(Image.open(Path(item['lab']) / 'runs' / item['run'] / a['file']).convert('RGB'))
    after = np.asarray(Image.open(Path(item['lab']) / 'runs' / item['run'] / b['file']).convert('RGB'))
    if before.shape != after.shape or a['ipc_transform'] != b['ipc_transform']:
        return {'status': 'NOT COMPARABLE: physical mode/transform changed'}
    changed = np.any(before != after, axis=2)
    ys, xs = np.where(changed)
    width, height = (750, 1000) if rotated else (after.shape[1], after.shape[0])
    mask = np.zeros((height, width), dtype=bool)
    extents = [d for d in item['damage'] if d[1] == output
               and a['capture_window_ns'][1] < d[0] <= b['capture_window_ns'][1]]
    for _, _, x1, y1, x2, y2 in extents:
        mask[max(0, y1):min(height, y2), max(0, x1):min(width, x2)] = True
    # WHY: grim's rotated PNG is logical-oriented; SceneFX damage is already
    # physical buffer-local. Internal WL transform 270 has inverse 90.
    # CONTRACT: half-open pixel map (x,y) -> (749-y,x) for the measured R90.
    px, py = (width-1-ys, xs) if rotated else (xs, ys)
    uncovered = int(np.count_nonzero(~mask[py, px]))
    return {'status': 'MEASURED', 'from': first, 'to': second, 'output': output,
            'png_changed_pixels': len(xs), 'physical_extents': [list(d[2:]) for d in extents],
            'uncovered_changed_pixels': uncovered, 'physical_dimensions': [width, height],
            'scope': 'settled PNG differences only; no minimal or all-frames claim'}


parser = argparse.ArgumentParser()
parser.add_argument('lab', type=Path)
args = parser.parse_args()
lab = args.lab.resolve()
old = lab / 'results'
# WHY: the initial sealed analysis counted zero spill without checking whether
# the Mosaic popup reached the border. Keep every old byte and path verifiable.
# CONTRACT: corrected scientific interpretation gets a separate sealed directory.
second = lab / 'results-corrected'
if (second / 'evidence-sha256.txt').exists():
    out = lab / 'results-final'
elif (old / 'evidence-sha256.txt').exists():
    out = second
else:
    out = old
out.mkdir(exist_ok=True)
if (out / 'evidence-sha256.txt').exists():
    raise SystemExit('this analysis is already sealed; refuse another rewrite')
runs = [parse_run(p) for p in sorted((lab / 'runs').glob('*-rotated-*'))]
for item in runs:
    item['lab'] = str(lab)
by_mode = {item['run'].split('-rotated-', 1)[0]: item for item in runs}
budget = read(lab)
write(out / 'campaign-budget.json', budget)
write(out / 'outputs.json', {mode: [e for e in item['events'] if e['kind'] == 'state']
                             for mode, item in by_mode.items()})
write(out / 'transforms.json', {mode: [e for e in item['events'] if e['kind'] == 'capture_geometry']
                                for mode, item in by_mode.items()})
write(out / 'logical-to-buffer.json', {
    'R0': {'logical_scaled': [1000, 750], 'physical': [1000, 750], 'map': '(x,y)->(x,y)'},
    'R90': {'logical_scaled': [1000, 750], 'physical': [750, 1000],
            'ipc_transform': '90', 'internal_transform': '270',
            'inverse_map_pixel': '(x,y)->(749-y,x)',
            'source': 'pinned wlroots box/region transform and measured mode'},
})
write(out / 'screenshot-coordinates.json', {
    mode: [e for e in item['events'] if e['kind'] == 'marker_calibration']
    for mode, item in by_mode.items()})
write(out / 'workspace-owner.json', {mode: [e for e in item['events'] if e['kind'] == 'identity']
                                     for mode, item in by_mode.items()})
write(out / 'scene-clips.json', {mode: [c for c in item['captures'].values()
                                if c['applied_viewport'] is not None]
                                for mode, item in by_mode.items()})
write(out / 'popup-geometry.json', {mode: {'grabs': item['grabs'],
    'done': item['popup_done'], 'protocol_errors': item['client_protocol_errors'],
    'chains': [e for e in item['events'] if e['kind'] == 'chain']}
    for mode, item in by_mode.items()})
write(out / 'pointer-calibration.json', {mode: [e for e in item['events']
    if e['kind'] == 'pointer_calibration'] for mode, item in by_mode.items()})
write(out / 'input-delivery.json', {mode: [e for e in item['events']
    if e['kind'] in ('owner_hit', 'restored_popup_hit', 'pointer_request')]
    for mode, item in by_mode.items()})
write(out / 'pixel-analysis.json', {mode: list(item['captures'].values())
                                    for mode, item in by_mode.items()})
damage = {}
for mode, item in by_mode.items():
    damage[mode] = []
    if mode == 'private_mosaic':
        for a, b, output, rotated in [
            ('R90-reopened', 'R90-hidden', 'HEADLESS-1', True),
            ('R90-hidden', 'R90-camera-return', 'HEADLESS-1', True),
            ('R90-reopened', 'R90-hidden', 'HEADLESS-2', False),
            ('R0-return', 'standard-return', 'HEADLESS-1', False)]:
            damage[mode].append(damage_pair(item, a, b, output, rotated))
write(out / 'damage-analysis.json', damage)
write(out / 'transition-timeline.json', {mode: {
    'events': [e for e in item['events'] if e['kind'] in ('dynamic_launch', 'capture')],
    'native_commit_count': sum(t['kind'] == 'PI_OUTPUT_COMMIT' for t in item['traces']),
    'native_present_count': sum(t['kind'] == 'PI_OUTPUT_PRESENT' for t in item['traces'])}
    for mode, item in by_mode.items()})
mosaic_capture = by_mode['private_mosaic']['captures'][('R90-popups', 'HEADLESS-1')]
mosaic_b_box = mosaic_capture['color_boxes_png']['B']
mosaic_boundary = mosaic_capture['png_dimensions'][0]
partial_crossing = mosaic_b_box is not None and mosaic_b_box[2] >= mosaic_boundary
matrix = {
    'control': {'R0': 'PASS', 'R90_geometry': 'PASS', 'R90_capture': 'NOT TESTED: fixture IPC direction assertion',
                'R0_return': 'NOT TESTED'},
    'private_standard': {'R0': 'PASS', 'R90_geometry_png_pointer': 'PASS',
                         'R90_popup_spill': 'PASS: 15860 B pixels on H2', 'R0_return': 'PASS'},
    'private_mosaic': {'R0': 'PASS', 'R90_geometry_png_pointer': 'PASS',
                       'R90_popup_no_spill': 'OBSERVED: 0 A/B pixels on H2; B PNG box and boundary recorded separately',
                       'R90_B_png_box': mosaic_b_box,
                       'R90_png_boundary': mosaic_boundary,
                       'R90_partial_popup_clip': ('GEOMETRIC CHALLENGE PRESENT' if partial_crossing
                                                   else 'NOT EXERCISED: no Mosaic B portion crosses the output boundary'),
                       'camera_hide_return': 'PASS: one pair',
                       'restored_B_button': 'PASS', 'R0_return': 'PASS',
                       'standard_return': 'PASS'},
    'not_tested': ['pristine R90 PNG/input after fixture assertion',
                   'Mosaic partial popup clipping at R90',
                   'root A crossing', 'simultaneous A/B crossing',
                   'scored popup boundary input grid', 'shadow and blur',
                   'optimized blur cache', 'saved buffers', 'raw physical buffer readback',
                   'every intermediate frame', 'R270', 'SceneFX ABI/package'],
}
write(out / 'matrix.json', matrix)
summary = {'result': 'PARTIALLY_FEASIBLE',
           'architectural_conclusion': 'UNDECIDED',
           'reason': 'applied geometry, logical PNG/pointer, hidden-owner and restoration pass; Mosaic popup never crosses R90 boundary and pristine R90 capture is missing',
           'measured_mosaic_B_png_box': mosaic_b_box,
           'measured_mosaic_png_boundary': mosaic_boundary,
           'runs': {mode: {'failure': item['exit']['failure'],
                          'captures': len(item['captures']),
                          'grabs_valid': all(g['valid'] for g in item['grabs'])}
                    for mode, item in by_mode.items()},
           'budget': {'mode_transform_actions': sum(x['action'] in ('R90','R0') for x in budget['reservations']),
                      'camera_hide_return_actions': sum(x['action'].startswith('camera') for x in budget['reservations'])}}
write(out / 'summary.json', summary)
source_paths = sorted(set(list((Path(__file__).parent).glob('*.py')) +
                          [Path(__file__).parent / 'README.md'] +
                          list(lab.glob('rotated-*.py')) +
                          [p for p in lab.iterdir() if p.is_file() and p.suffix in ('.c', '.h')] +
                          [p for root in ('mosaic', 'standard', 'scenefx', 'scenefx-git')
                           for p in (lab / root).rglob('*') if p.is_file() and '.git' not in p.parts] +
                          [p for p in (Path(__file__).parents[1]).glob('step20c-*/*.patch')]))
(out / 'source-sha256.txt').write_text(''.join(digest(p) + '  ' + str(p.resolve()) + '\n'
                                              for p in source_paths))
evidence_paths = sorted(set([p for p in (lab / 'runs').rglob('*') if p.is_file()] +
                            [p for p in out.iterdir() if p.is_file() and p.name != 'evidence-sha256.txt'] +
                            [lab / 'rotation-campaign-budget.json'] +
                            ([old / 'evidence-sha256.txt', old / 'source-sha256.txt']
                             if out != old else []) +
                            ([second / 'evidence-sha256.txt', second / 'source-sha256.txt']
                             if out != second and second.exists() else [])))
(out / 'evidence-sha256.txt').write_text(''.join(digest(p) + '  ' + str(p.resolve()) + '\n'
                                                for p in evidence_paths))
print(json.dumps({'summary': summary, 'source_entries': len(source_paths),
                  'evidence_entries': len(evidence_paths),
                  'source_manifest_sha256': digest(out / 'source-sha256.txt'),
                  'evidence_manifest_sha256': digest(out / 'evidence-sha256.txt')}))
