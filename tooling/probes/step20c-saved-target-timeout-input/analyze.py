#!/usr/bin/env python3
"""Derive bounded, reproducible facts from the single retained timeout run."""
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageChops

lab = Path(sys.argv[1]).resolve()
repo = Path(__file__).resolve().parents[3]
run = next((lab / 'runs').glob('timeout-mosaic-*'))
out = lab / 'results'
events = [json.loads(line) for line in (run / 'events.jsonl').read_text().splitlines()]
log = (run / 'compositor.log').read_text().splitlines()
client = (run / 'client.log').read_text().splitlines()
reference = (run / 'reference.log').read_text().splitlines()
preflight = json.loads((out / 'target-preflight.json').read_text())
stability = json.loads((out / 'reference-stability.json').read_text())
budget = json.loads((lab / 'timeout-budget.json').read_text())
status = json.loads((run / 'exit-status.json').read_text())

def write(name, obj):
    (out / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')

def first(kind):
    return next(e for e in events if e['kind'] == kind)

def fields(line):
    return dict(re.findall(r'([A-Za-z_]+)=([^ ]+)', line))

def rgb(name):
    return Image.open(run / name).convert('RGB')

def diff(a, b):
    image = ImageChops.difference(rgb(a), rgb(b))
    return {'changed_pixels': sum(p != (0, 0, 0) for p in image.get_flattened_data()),
            'box': image.getbbox()}

def color(name, triplet):
    return sum(p == triplet for p in rgb(name).get_flattened_data())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

saved = first('saved_target')
node = saved['node']
tree = saved['tree']
view = saved['view']
source = saved['source']
start_ns = int(fields(saved['saved_trace'])['ns'])
created = next(x for x in log if x.startswith('SB_BUFFER_CREATE ') and
               f'node={node}' in x and f'parent={tree}' in x and
               0 <= start_ns - int(fields(x)['ns']) < 1_000_000_000)
enabled = next(x for x in log if x.startswith('SB_ENABLE ') and
               f'view={view}' in x and f'tree={tree}' in x and
               int(fields(x)['ns']) >= start_ns)
destroyed = next(x for x in log if x.startswith('SB_TREE_DESTROY ') and
                 f'view={view}' in x and f'tree={tree}' in x and
                 int(fields(x)['ns']) > start_ns)
render = [x for x in log if x.startswith('SB_RENDER ') and f'node={node}' in x
          and int(fields(x)['ns']) >= start_ns and
          int(fields(x)['ns']) < int(fields(destroyed)['ns'])]
timeout = next(x for x in log if 'timed out (1 waiting)' in x)
timeout_event = first('timeout_observed')
held = next(x for x in client if x.startswith('HELD ') and 'serial=50' in x)
hits = [x for x in log if x.startswith('TARGET_HIT ') and
        int(fields(x)['ns']) < int(fields(destroyed)['ns']) and
        int(fields(x)['ns']) > int(fields(created)['ns'])]
surfaces = [next((log[i + 1] for i, line in enumerate(log) if line == hit and
                  i + 1 < len(log) and
                  log[i + 1].startswith('TARGET_HIT_SURFACE ')), None)
            for hit in hits]
right_names = ['right-reference-a.png', 'right-reference-b.png',
               'right-held.png', 'right-timeout-applied.png']
right = {name: {**diff(right_names[0], name), 'sha256': sha(run / name),
                'old_target_pixels': color(name, (32, 208, 160)),
                'new_target_pixels': color(name, (35, 68, 204))}
         for name in right_names}
left = {name: {'old_target_pixels': color(name, (32, 208, 160)),
               'new_target_pixels': color(name, (35, 68, 204))}
        for name in ['left-reference-a.png', 'left-reference-b.png',
                     'left-held.png', 'left-timeout-applied.png']}
reference_events = [x for x in events if x['kind'] == 'capture' and
                    x['path'].startswith('right-reference')]
client_exit_ns = int(fields(next(x for x in client if x.startswith('EXIT ')))['ns'])
post_destroy_same_node = [x for x in log if x.startswith('SB_RENDER ') and
                          f'node={node}' in x and
                          int(fields(destroyed)['ns']) < int(fields(x)['ns']) <
                          client_exit_ns]

write('reference-pixel-diff.json', {'preflight': stability,
      'capture_gap_seconds': (reference_events[1]['before_ns'] -
                              reference_events[0]['before_ns']) / 1e9,
      'full_rgb': right})
write('camera-applied.json', {k: preflight[k] for k in
      ('current_scroll', 'desired_scroll', 'delta')})
write('source-buffer.json', {k: source[k] for k in
      ('view', 'container', 'source_node', 'source_buffer', 'left', 'top',
       'width', 'right', 'source_size', 'dest', 'src_box', 'transform')})
write('saved-target.json', {'view': view, 'tree': tree, 'node': node,
      'buffer': saved['buffer'], 'box': saved['box'],
      'source_buffer_equal': saved['buffer'] == source['source_buffer'],
      'created': created, 'enabled': enabled, 'destroyed': destroyed})
write('scene-parentage.json', {'source_parent': fields(source['raw'])['parent'],
      'saved_parent': fields(created)['parent'], 'saved_tree': tree,
      'tree_parent': fields(saved['tree_trace'])['parent'],
      'source_node': source['source_node'], 'saved_node': node,
      'target_owner_id': source['owner']['id'],
      'target_workspace_id': source['workspace']['id']})
write('render-entries.json', {'target_node': node, 'held_entries': render,
      'same_node_entries_between_destroy_and_client_exit': post_destroy_same_node,
      'pointer_reuse_after_client_exit_must_not_be_counted_as_same_tree': True})
scene = [x for x in log if 'PI_SCENE output=HEADLESS-1' in x and
         int(fields(x)['ns']) >= int(fields(created)['ns']) and
         int(fields(x)['ns']) < int(fields(destroyed)['ns'])]
write('clip-analysis.json', {'saved_global_box': saved['box'],
      'held_render_visible': fields(render[0])['visible'],
      'outer_tiled_clip': scene[0] if scene else None,
      'post_timeout_clip': next((x for x in log if
      'PI_SCENE output=HEADLESS-1' in x and 'clip=160,0,740,540' in x), None),
      'interpretation': 'Held visible right edge x=0 matches outer Mosaic clip; '
      'after timeout x=-30 matches gap-adjusted outer clip. No independent '
      'content-clip causality is inferred.'})
write('target-pixel-analysis.json', {'full_h1_target_color_counts': left,
      'saved_held_pixels': left['left-held.png']['old_target_pixels']})
write('whole-h2-comparison.json', {'full_rgb': right,
      'all_equal': all(v['changed_pixels'] == 0 for v in right.values()),
      'no_target_color': all(v['old_target_pixels'] == 0 and
      v['new_target_pixels'] == 0 for v in right.values())})
write('input-hits.json', {'held_hits': hits, 'surface_associations': surfaces,
      'seat_notification': 'not directly traced',
      'h2_reference_motion_received': any(x.startswith('MOTION ') and
      'x=98.00 y=75.00' in x for x in reference),
      'target_motion_during_hold': [x for x in client if x.startswith('MOTION ') and
      int(fields(x)['ns']) >= int(fields(held)['ns']) and
      int(fields(x)['ns']) < int(fields(destroyed)['ns'])]})
write('client-delivery.json', {'held_configure': held,
      'target_ack_serial_50': [x for x in client if x.startswith('ACK ') and
      'serial=50' in x], 'reference_motion': [x for x in reference if
      x.startswith('MOTION ')], 'target_exit': [x for x in client if
      x.startswith('EXIT ')]})
write('transaction-timeline.json', {'held': held, 'saved_created': created,
      'render': render[0], 'timeout': timeout,
      'saved_destroyed': destroyed,
      'hold_to_destroy_seconds': (int(fields(destroyed)['ns']) -
      int(fields(held)['ns'])) / 1e9,
      'other_transactions_after_controlled_client_cleanup': True})
write('timeout.json', {'natural_timeout': timeout, 'event': timeout_event,
      'no_target_ack': not any(x.startswith('ACK ') and 'serial=50' in x
      for x in client), 'client_alive_at_timeout': timeout_event['client_alive'],
      'target_tree_destroyed': destroyed})
write('lifetime.json', {'source_buffer': source['source_buffer'],
      'saved_buffer': saved['buffer'], 'saved_tree_destroyed': destroyed,
      'no_same_node_render_between_destroy_and_client_exit':
      not bool(post_destroy_same_node),
      'gpu_texture_release': 'NOT TESTED'})
write('damage-analysis.json', {'held_target_render': render[0],
      'held_damage_extent': fields(render[0])['damage'],
      'post_timeout_h1_target_pixels': left['left-timeout-applied.png'],
      'h2_changed_pixels': right['right-timeout-applied.png']['changed_pixels'],
      'all_intermediate_frames': 'NOT TESTED'})
write('budget.json', {'reserved': budget, 'limits': {'run': 1, 'episode': 1,
      'camera': 1, 'capture': 12, 'seconds': 150},
      'duration_seconds': status['duration_seconds'], 'failure': status['failure']})
core = (stability['stable'] and saved['buffer'] == source['source_buffer'] and
        saved['box'][0] < 0 < saved['box'][2] and bool(render) and
        left['left-held.png']['old_target_pixels'] > 0 and
        all(v['changed_pixels'] == 0 for v in right.values()) and
        bool(destroyed) and timeout_event['client_alive'])
verdict = 'PARTIALLY_FEASIBLE' if core else 'INCONCLUSIVE'
write('matrix.json', {'ack_e1_historical': 'PARTIALLY_FEASIBLE',
      'new_timeout_core': 'PASS' if core else 'FAIL',
      'input_sampled': len(hits) == 2, 'damage_complete': False,
      'native_gpu_lifetime_complete': False})
write('summary.json', {'verdict': verdict, 'core_pass': core,
      'architecture': 'SAVED_TARGET_TIMEOUT_CLIPPING_FEASIBLE_FOR_TESTED_MATRIX'
      if core else 'UNDECIDED', 'run': str(run),
      'limits': ['full transactional damage', 'all GPU/texture references',
      'intermediate frames', 'seat notification on saved node',
      'unmeasured input paths']})

# Source manifest covers exact executed fixture and private source trees; no
# build products enter this source list. Evidence manifest covers all retained
# raw run inputs, captures and derived JSON without a self-hash cycle.
fixture = repo / 'tooling/probes/step20c-saved-target-timeout-input'
sources = [p for p in fixture.iterdir() if p.is_file()] + [run / 'fixture-source.py']
for root in (lab / 'mosaic', lab / 'standard', lab / 'scenefx-git'):
    sources.extend(p for p in root.rglob('*') if p.is_file() and
                   '.git' not in p.parts and 'subprojects/packagecache' not in str(p))
sources.extend(p for p in (lab / 'nested-client.c', lab / 'pointer-daemon.c',
                           lab / 'virtual-pointer-client.h', lab / 'virtual-pointer-protocol.c',
                           lab / 'xdg-shell-client.h', lab / 'xdg-shell-protocol.c')
               if p.is_file())
sources = sorted(set(sources))
evidence = sorted(set(p for p in run.iterdir() if p.is_file()) |
                  set(p for p in out.iterdir() if p.is_file() and
                      not p.name.endswith('-sha256.txt')) |
                  {lab / 'timeout-budget.json', lab / 'saved-timeout-build-log.txt'})
for name, paths in [('source-sha256.txt', sources), ('evidence-sha256.txt', evidence)]:
    (out / name).write_text(''.join(f'{sha(p)}  {p}\n' for p in paths))
print(f'{verdict} source={len(sources)} evidence={len(evidence)}')
