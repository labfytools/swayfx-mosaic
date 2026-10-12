"""Offline, single-seal analysis of the static R90 runs and their raw evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import re

import numpy as np
from PIL import Image

COLORS = {'A': (224, 192, 32), 'B': (32, 208, 160)}
TRACE = re.compile(r'\b(DO_STATE|DO_POPUP|PI_SCENE|PI_OWNER|PI_OUTPUT_COMMIT|PI_OUTPUT_PRESENT)\b')
DAMAGE = re.compile(r'TEMPORAL_DAMAGE ordinal=\d+ ns=(\d+) output=(\S+) '
                    r'extent=(-?\d+),(-?\d+)\.\.(-?\d+),(-?\d+)')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def fields(line):
    return dict(re.findall(r'(\w+)=([^\s]+)', line))


def bbox(mask):
    yy, xx = np.where(mask)
    return [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1] if len(xx) else None


def latest(traces, kind, before, **constraints):
    found = [x for x in traces if x['kind'] == kind and x['ns'] <= before and
             all(x.get(k) == v for k, v in constraints.items())]
    return found[-1] if found else None


def image(path):
    return np.asarray(Image.open(path).convert('RGB'))


def colors(path):
    im = image(path)
    return {name: {'pixels': int(mask.sum()), 'box': bbox(mask)}
            for name, color in COLORS.items()
            for mask in [np.all(im == color, axis=2)]}


def damage_coverage(run, a, b, output, damages):
    before, after = image(run / a['path']), image(run / b['path'])
    changed = np.any(before != after, axis=2)
    yy, xx = np.where(changed)
    width, height = (750, 1000) if output == 'HEADLESS-1' else (800, 600)
    mask = np.zeros((height, width), dtype=bool)
    extents = [d for d in damages if d[1] == output and
               a['after_ns'] < d[0] <= b['after_ns']]
    for _, _, x1, y1, x2, y2 in extents:
        mask[max(0, y1):min(height, y2), max(0, x1):min(width, x2)] = True
    # WHY: grim H1 is logical-oriented; inherited damage extents already use
    # physical buffer-local coordinates after SceneFX inverse rotation.
    # CONTRACT: measured static R90 maps PNG (x,y) to buffer (749-y,x).
    px, py = (width - 1 - yy, xx) if output == 'HEADLESS-1' else (xx, yy)
    return {'from': a['tag'], 'to': b['tag'], 'output': output,
            'changed_png_pixels': int(len(xx)), 'changed_box_png': bbox(changed),
            'physical_extents_count': len(extents),
            'uncovered_changed_pixels': int(np.count_nonzero(~mask[py, px])),
            'physical_extents': [list(d[2:]) for d in extents],
            'scope': 'settled PNG pair only; no intermediate-frame claim'}


parser = argparse.ArgumentParser()
parser.add_argument('lab', type=Path)
args = parser.parse_args()
lab = args.lab.resolve()
out = lab / 'results'
if out.exists():
    raise SystemExit('sealed results exist; refusing overwrite')
runs = sorted((lab / 'runs').glob('*-static-r90-*'))
if len(runs) != 3:
    raise SystemExit('exactly three retained runs required')
budget = json.loads((lab / 'partial-campaign-budget.json').read_text())
if sorted(budget['runs']) != ['control', 'private_mosaic', 'private_standard']:
    raise SystemExit('campaign ledger incomplete')

outputs, geometry, intersections, grabs, clips = {}, {}, {}, {}, {}
hits, delivery, pixels, damages_out, matrix, summary_runs = {}, {}, {}, {}, {}, {}
source_paths = []
for tree in (lab / 'mosaic', lab / 'scenefx', lab / 'standard'):
    source_paths.extend(p for p in tree.rglob('*') if p.is_file())
source_paths.extend(p for p in lab.glob('*.c'))
source_paths.extend(p for p in lab.glob('*.h'))
source_paths.extend(p for p in Path(__file__).parent.glob('*') if p.is_file())

for run in runs:
    mode = run.name.split('-static-r90-', 1)[0]
    events = [json.loads(line) for line in (run / 'events.jsonl').read_text().splitlines()]
    by_kind = lambda kind: [e for e in events if e['kind'] == kind]
    geom = by_kind('applied_popup_geometry')[-1]
    gate = by_kind('geometry_gate')[-1]
    client = (run / 'client.log').read_text(errors='replace')
    log = (run / 'compositor.log').read_text(errors='replace')
    traces = []
    for line in log.splitlines():
        m = TRACE.search(line)
        if m:
            item = {'kind': m[1], **fields(line)}
            if item.get('ns', '').isdigit():
                item['ns'] = int(item['ns'])
                traces.append(item)
    damage = [(int(ns), output, *map(int, (x1, y1, x2, y2)))
              for ns, output, x1, y1, x2, y2 in DAMAGE.findall(log)]
    captures = {(e['tag'], e['output']): e for e in by_kind('capture')}
    capture_geometry = {(e['tag'], e['output']): e for e in by_kind('capture_geometry')}
    outputs[mode] = {'states': by_kind('state'), 'capture_geometry': by_kind('capture_geometry'),
                     'markers': by_kind('marker_calibration'),
                     'pointer_calibration': by_kind('pointer_calibration')}
    geometry[mode] = geom
    intersections[mode] = {k: geom[k] for k in ('a_h1', 'a_h2', 'b_h1', 'b_h2')}
    parsed_grabs = [{'popup': p, 'target': t, 'serial': int(s), 'used': int(u),
                     'real_button': bool(re.search(rf'POINTER_BUTTON target={t} serial={s} button=272 state=1', client))}
                    for p, t, s, u in re.findall(
                        r'(POPUP_[AB]) GRAB_REQUEST origin=wl_pointer.button target=(\S+) serial=(\d+) used=(\d+)', client)]
    grabs[mode] = {'requests': parsed_grabs,
                   'role_configures': re.findall(r'(POPUP_[AB]) ROLE_CONFIGURE x=(-?\d+) y=(-?\d+) w=(\d+) h=(\d+)', client),
                   'xdg_configure_acks': re.findall(r'(POPUP_[AB]) XDG_CONFIGURE serial=(\d+) ack', client),
                   'maps': re.findall(r'(POPUP_[AB]) MAP wl=(\d+) xdg=(\d+)', client),
                   'protocol_errors': [line for line in client.splitlines() if 'protocol error' in line.lower()]}
    capture = captures[('rot-cross-S2-B', 'HEADLESS-1')]
    before = capture['before_ns']
    clips[mode] = {'output_state': latest(traces, 'DO_STATE', before, observer='HEADLESS-1'),
                   'tiled': latest(traces, 'PI_SCENE', before, output='HEADLESS-1'),
                   'root_popup': latest(traces, 'DO_POPUP', before, owner_id=str(geom['owner_id'])),
                   'owner': latest(traces, 'PI_OWNER', before, id=str(geom['owner_id'])),
                   'native_commits': sum(t['kind'] == 'PI_OUTPUT_COMMIT' for t in traces),
                   'native_presents': sum(t['kind'] == 'PI_OUTPUT_PRESENT' for t in traces)}
    hits[mode] = {'border_hovers': by_kind('border_hover'),
                  'visible_b_button': by_kind('visible_b_button'),
                  'forbidden_b_button': by_kind('forbidden_b_button')}
    delivery[mode] = {'client_grabs': grabs[mode],
                      'visible_b_events': by_kind('visible_b_button')[-1]['client_events'],
                      'forbidden_b_events': by_kind('forbidden_b_button')[-1]['client_events'],
                      'popup_done_A': client.count('POPUP_A POPUP_DONE'),
                      'popup_done_B': client.count('POPUP_B POPUP_DONE'),
                      'client_log': str(run / 'client.log')}
    pair = {}
    for output, side in (('HEADLESS-1', 'left'), ('HEADLESS-2', 'right')):
        a, b = captures[('reference', output)], captures[('rot-cross-S2-B', output)]
        before_im, popup_im = image(run / a['path']), image(run / b['path'])
        diff = np.any(before_im != popup_im, axis=2)
        pair[output] = {'reference': {'path': a['path'], 'sha256': digest(run / a['path']),
                                      'window_ns': [a['before_ns'], a['after_ns']]},
                        'popup': {'path': b['path'], 'sha256': digest(run / b['path']),
                                  'window_ns': [b['before_ns'], b['after_ns']]},
                        'png_dimensions': list(popup_im.shape[1::-1]),
                        'output': capture_geometry[('rot-cross-S2-B', output)],
                        'reference_diff_pixels': int(diff.sum()), 'reference_diff_box': bbox(diff),
                        'colors': colors(run / b['path'])}
    pixels[mode] = pair
    damages_out[mode] = [damage_coverage(run, captures[('reference', output)],
                        captures[('rot-cross-S2-B', output)], output, damage)
                         for output in ('HEADLESS-1', 'HEADLESS-2')]
    status = json.loads((run / 'exit-status.json').read_text())
    matrix[mode] = {'run_failure': status['failure'], 'captures': status['captures'],
                    'duration_seconds': status['duration_seconds'],
                    'geometry_gate': gate['result'], 'B_box': geom['b_box'],
                    'A_box': geom['a_box'], 'grab_count': len(parsed_grabs),
                    'H1_B_pixels': pair['HEADLESS-1']['colors']['B']['pixels'],
                    'H2_B_pixels': pair['HEADLESS-2']['colors']['B']['pixels'],
                    'H2_full_reference_diff': pair['HEADLESS-2']['reference_diff_pixels']}
    summary_runs[mode] = {'run': str(run), 'exit': status}

if not all(matrix[m]['geometry_gate'] == 'CROSSING' for m in matrix):
    verdict = 'INCONCLUSIVE'
elif matrix['private_mosaic']['H2_full_reference_diff'] or matrix['private_mosaic']['H2_B_pixels']:
    verdict = 'BLOCKED'
elif any(matrix[m]['run_failure'] for m in matrix):
    verdict = 'INCONCLUSIVE'
else:
    # P2 root-popup input was not independently clicked in the one-chain run.
    verdict = 'PARTIALLY_FEASIBLE'

out.mkdir()
write(out / 'geometry.json', geometry)
write(out / 'popup-positions.json', {m: {'A': x['a_box'], 'B': x['b_box']} for m, x in geometry.items()})
write(out / 'popup-intersections.json', intersections)
write(out / 'output-transforms.json', outputs)
write(out / 'client-grabs.json', grabs)
write(out / 'scene-clips.json', clips)
write(out / 'pointer-hits.json', hits)
write(out / 'client-delivery.json', delivery)
write(out / 'pixel-differences.json', pixels)
write(out / 'damage.json', damages_out)
write(out / 'budget.json', budget)
write(out / 'matrix.json', matrix)
write(out / 'summary.json', {'result': verdict, 'architectural_conclusion':
                            'ROTATED_PARTIAL_POPUP_CLIP_FEASIBLE_FOR_TESTED_MATRIX'
                            if verdict in ('FEASIBLE', 'PARTIALLY_FEASIBLE') else 'UNDECIDED',
                            'runs': summary_runs, 'unexercised': ['separate A input and exterior hit',
                            'raw framebuffer', 'intermediate frames', 'saved buffers',
                            'optimized blur cache', 'inner shadow', 'ABI/package']})
write(out / 'source-provenance.json', {'pinned_swayfx': 'fd71a6bdc061bd633b488ae7b83e8a6981d22f86',
     'mosaic_private_base': 'cd550382b311efdbfe3ed892f4e1d281d852e754',
     'scenefx': '37ccd723bef49e6891156ffafce8f549f01446cc',
     'client_base_sha256': '2e40c98af72a0df8b316810589a0be8f4425a763db1de448b49a7813956b6f7d',
     'client_patch_sha256': digest(Path(__file__).parent / 'rot-cross-client.patch')})
(out / 'source-sha256.txt').write_text(''.join(f'{digest(p)}  {p.resolve()}\n' for p in sorted(set(source_paths))))
evidence = [p for p in sorted(run_file for run in runs for run_file in run.rglob('*') if run_file.is_file())]
evidence += [lab / 'partial-campaign-budget.json', lab / 'partial-build-log.txt']
evidence += [p for p in out.iterdir() if p.is_file() and p.name != 'evidence-sha256.txt']
(out / 'evidence-sha256.txt').write_text(''.join(f'{digest(p)}  {p.resolve()}\n' for p in sorted(set(evidence))))
print(f'RESULT={verdict} LAB={lab} SOURCES={len(set(source_paths))} EVIDENCE={len(set(evidence))}')
