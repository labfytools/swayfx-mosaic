"""Offline, bounded analysis of the one target-crossing LAB; no compositor run."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from PIL import Image, ImageChops

parser = argparse.ArgumentParser()
parser.add_argument('lab', type=Path)
args = parser.parse_args()
lab = args.lab.resolve()
results = lab / 'results'
results.mkdir(exist_ok=True)
repo = Path(__file__).resolve().parents[3]
run_dirs = {mode: next((lab / 'runs').glob(f'saved-{mode}-*'))
            for mode in ('control', 'private_standard', 'private_mosaic')}


def write(name, value):
    (results / f'{name}.json').write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def events(mode):
    return [json.loads(line) for line in (run_dirs[mode] / 'events.jsonl').read_text().splitlines()]


def diff(a, b):
    first = Image.open(a).convert('RGB')
    second = Image.open(b).convert('RGB')
    d = ImageChops.difference(first, second)
    return {'box': d.getbbox(), 'changed_pixels': sum(1 for p in d.get_flattened_data() if p != (0, 0, 0))}


def count_color(path, color):
    im = Image.open(path).convert('RGB')
    return sum(1 for pixel in im.get_flattened_data() if pixel == color)

budget = json.loads((lab / 'target-budget.json').read_text())
write('budget', budget)
preflight = json.loads((results / 'target-preflight.json').read_text())
write('target-geometry', {'source_before': {k: preflight['before'][k] for k in ('left', 'right', 'width', 'source_size', 'dest', 'src_box', 'transform')},
                          'source_after': {k: preflight['after'][k] for k in ('left', 'right', 'width', 'source_size', 'dest', 'src_box', 'transform')}})
write('camera-calibration', {k: preflight[k] for k in ('current_scroll', 'desired_scroll', 'delta')})
mosaic = run_dirs['private_mosaic']
me = events('private_mosaic')
saved = [e for e in me if e['kind'] == 'saved_target']
log = (mosaic / 'compositor.log').read_text()
client = (mosaic / 'client.log').read_text()
ack_node = saved[0]['node']
ack_buffer = saved[0]['buffer']
render = [line for line in log.splitlines() if 'SB_RENDER ' in line and f'node={ack_node}' in line]
destroy = [line for line in log.splitlines() if 'SB_TREE_DESTROY ' in line and f'view={preflight["after"]["view"]}' in line]
held_color = (32, 208, 160)
pixels = {}
for mode, run in run_dirs.items():
    ref = run / 'right-reference.png'
    pixels[mode] = {p.stem: diff(ref, p) for p in sorted(run.glob('right-*.png'))}
    pixels[mode]['target_color_on_h2_held'] = (count_color(run / 'right-ack-held.png', held_color)
        if (run / 'right-ack-held.png').exists() else None)
pixels['private_mosaic']['target_color_on_h1_ack_held'] = count_color(mosaic / 'left-ack-held.png', held_color)
pixels['private_mosaic']['target_color_on_h1_reference'] = count_color(mosaic / 'left-reference.png', held_color)
write('pixel-analysis', pixels)
write('saved-tree-identity', {'target_view': preflight['after']['view'], 'target_container': preflight['after']['container'],
                              'ack_saved_node': ack_node, 'ack_destroy_observations': destroy,
                              'e2_saved_node': saved[1]['node'] if len(saved) > 1 else None})
write('saved-buffer-identity', {'source_node': preflight['after']['source_node'], 'source_buffer': preflight['after']['source_buffer'],
                                'ack_saved_buffer': ack_buffer, 'ack_same_source': ack_buffer == preflight['after']['source_buffer'],
                                'e2_saved_buffer': saved[1]['buffer'] if len(saved) > 1 else None,
                                'e2_note': 'new source buffer after E1 ACK; executed runner compared it with stale pre-E1 pointer'})
write('scene-parentage', {'ack_creation': [line for line in log.splitlines() if 'SB_TREE_CREATE ' in line and f'view={preflight["after"]["view"]}' in line][-2:],
                          'ack_saved_node_trace': [line for line in log.splitlines() if 'TARGET_SAVED ' in line and f'node={ack_node}' in line][-1:],
                          'source_path_contract': 'saved tree under view scene tree; Mosaic tiled clip is ancestor per source audit'})
write('saved-target-crossing', {'e1': saved[0]['global_box'], 'e1_crosses_x0': saved[0]['global_box'][0] < 0 < saved[0]['global_box'][2],
                                'e2': saved[1]['global_box'] if len(saved) > 1 else None,
                                'e2_crosses_x0': len(saved) > 1 and saved[1]['global_box'][0] < 0 < saved[1]['global_box'][2],
                                'e2_status': 'NOT EXERCISED through timeout due to fixture pointer correlation'})
write('transaction-timeline', {mode: [e for e in events(mode) if e['kind'] in ('episode_start', 'saved_target', 'held', 'timeout_observed', 'failure', 'cleanup')]
                               for mode in run_dirs})
write('configure-ack', {mode: [line for line in (run / 'client.log').read_text().splitlines()
                               if line.startswith(('HELD ', 'ACK ', 'COMMIT ', 'PONG '))]
                        for mode, run in run_dirs.items()})
write('render-entries', {'e1_target': render, 'e1_observed': bool(render), 'e2_target': [line for line in log.splitlines()
    if len(saved) > 1 and 'SB_RENDER ' in line and f'node={saved[1]["node"]}' in line]})
write('clip-observations', {'e1_target_render_visible': [re.search(r'visible=([^ ]+)', x).group(1) for x in render],
                            'e1_applied_clip': [line for line in log.splitlines() if 'PI_SCENE output=HEADLESS-1' in line and 'scroll=160 tile_scene=-160,0 clip_valid=1 clip=160,0,800,600' in line][:2],
                            'source_audit': 'scene_node_intersect_clip and scene_node_point_inside_clip walk ancestors'})
write('pointer-hits', {'status': 'NOT TESTED during target hold', 'reason': 'ACK window prioritized target snapshot and protocol'})
write('client-delivery', {'status': 'NOT TESTED during target hold'})
write('damage-analysis', {'status': 'LIMITED', 'render_damage_e1': [re.search(r'damage=([^ ]+)', x).group(1) for x in render],
                           'complete_intermediate_frames': 'NOT TESTED'})
write('lifetime', {'e1_target_saved_tree_destroy_observed': bool(destroy), 'destroy_trace': destroy,
                   'e2_timeout_cleanup': 'NOT TESTED', 'all_gpu_references_released': 'NOT PROVEN',
                   'mapped_view_destroy_during_transaction': 'NOT TESTED'})
write('timeout', {mode: [line for line in (run / 'compositor.log').read_text().splitlines() if 'timed out' in line]
                  for mode, run in run_dirs.items()})
write('matrix', {'C2_E1': 'TARGET CROSSING/RENDER/ACK OBSERVED; H2 whole-image mismatch 253 pixels',
                 'C2_E2': 'TARGET CREATED AND CROSSES; fixture stale-buffer correlation stopped before timeout',
                 'C0_E1_E2': 'COMPLETED', 'C1_E1_E2': 'COMPLETED',
                 'target_hold_input': 'NOT TESTED', 'complete_damage': 'NOT TESTED'})
write('summary', {'result': 'PARTIALLY_FEASIBLE', 'architectural_conclusion': 'UNDECIDED',
                  'target_ack_crossing_and_render': True, 'target_ack_h1_color_pixels': pixels['private_mosaic']['target_color_on_h1_ack_held'],
                  'target_ack_h2_color_pixels': pixels['private_mosaic']['target_color_on_h2_held'],
                  'target_ack_h2_full_diff': pixels['private_mosaic']['right-ack-held'],
                  'target_timeout_cleanup': 'NOT TESTED',
                  'reason': 'E1 target crossing/render and allowed H1 pixels observed; H2 reference mismatch, input/damage and target E2 cleanup remain unqualified'})

source_files = sorted((repo / 'tooling/probes/step20c-saved-buffer-target-crossing').glob('*'))
source_files += [repo / 'tooling/probes/step20c-saved-transaction-buffer/sway-saved-trace.patch',
                 repo / 'tooling/probes/step20c-saved-transaction-buffer/scenefx-saved-trace.patch']
for source_root in (lab / 'mosaic', lab / 'standard', lab / 'scenefx'):
    source_files.extend(source_root.rglob('*'))
source_files.extend(lab.glob('*.c'))
source_files.extend(lab.glob('*.h'))
source_files = [p for p in source_files if p.is_file()]

def manifest(paths, dest):
    dest.write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p}\n' for p in sorted(paths)))

manifest(source_files, results / 'source-sha256.txt')
evidence_files = (list((lab / 'runs').glob('**/*')) + list(results.glob('*.json')) +
                  list(lab.glob('*-log.txt')) +
                  [lab / 'target-budget.json', lab / 'source-sha256.txt'])
manifest([p for p in evidence_files if p.is_file()], results / 'evidence-sha256.txt')
print('RESULT=PARTIALLY_FEASIBLE', 'RUNS=3', 'CAPTURES=' + str(sum(budget['captures'].values())))
