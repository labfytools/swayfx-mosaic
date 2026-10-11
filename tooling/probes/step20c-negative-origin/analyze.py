"""Summarize retained headless evidence without treating counts as a verdict.

Usage: python analyze.py LAB
Requires Pillow for PNG decoding. Writes analysis.json inside each run directory.
"""
import json
from pathlib import Path
import re
import sys

from PIL import Image

if len(sys.argv) != 2:
    raise SystemExit(__doc__)
lab = Path(sys.argv[1]).resolve()
colors = {'A_yellow': (224, 192, 32), 'B_green': (32, 208, 160)}


def open_image(path):
    return Image.open(path).convert('RGB')


def local_points(lines, pattern):
    points = []
    for line in lines:
        match = re.search(pattern, line)
        if match:
            points.append(tuple(map(float, match.groups())))
    return points


for run in sorted(lab.glob('run-*')):
    if not (run / 'exit-status.json').exists():
        continue
    client = (run / 'client.log').read_text()
    ordinary = (run / 'wev.log').read_text()
    compositor = (run / 'compositor.log').read_text()
    result = {
        'run': run.name,
        'exit_status': json.loads((run / 'exit-status.json').read_text()),
        'grab_requests': re.findall(
            r'(POPUP_[AB]) GRAB_REQUEST origin=wl_pointer.button target=(\w+) serial=(\d+) used=(\d+)',
            client),
        'popup_parents': re.findall(
            r'(POPUP_[AB]) CREATE wl=(\d+) xdg=(\d+) role=(\d+) parent=(\w+) parent_xdg=(\d+)',
            client),
        'popup_done_order': re.findall(r'(POPUP_[AB]) POPUP_DONE', client),
        'popup_destroy_order': re.findall(r'(POPUP_[AB]) DESTROY', client),
        'popup_buttons': re.findall(
            r'POINTER_BUTTON target=(POPUP_[AB]) serial=(\d+) button=(\d+) state=(\d+)',
            client),
        'ordinary_buttons': re.findall(
            r'button: serial: (\d+); time: \d+; button: (\d+).*state: ([01])',
            ordinary),
        'scene_clip_logs': re.findall(
            r'PROBE_POPUP_CLIP owner=(\S+) local=(-?\d+),(-?\d+) (\d+)x(\d+)',
            compositor),
        'hidden_owner_logs': re.findall(r'PROBE_POPUP_HIDDEN_OWNER[^\n]*', compositor),
        'captures': {},
        'open_sample_rgb': {},
    }
    reference_path = run / 'pointer-validation.json'
    if reference_path.exists():
        reference = json.loads(reference_path.read_text())
        owner_points = local_points(reference['owner_motion_lines'],
                                    r'x=(-?[\d.]+) y=(-?[\d.]+)')
        ordinary_points = local_points(reference['ordinary_motion_lines'],
                                       r'x, y: (-?[\d.]+), (-?[\d.]+)')
        if len(owner_points) >= 2 and len(ordinary_points) >= 2:
            result['pointer_observed'] = [
                {'requested_global': list(reference['global_points'][i]),
                 'observed_output': output, 'observed_surface_local': list(point)}
                for i, output, point in zip(range(4),
                    ('HEADLESS-1', 'HEADLESS-2', 'HEADLESS-1', 'HEADLESS-2'),
                    (owner_points[-2], ordinary_points[-2],
                     owner_points[-1], ordinary_points[-1]))]
    for path in sorted(run.glob('*.png')):
        if not path.name.startswith(('left-', 'right-')):
            continue
        image = open_image(path)
        pixels = image.get_flattened_data()
        result['captures'][path.name] = {
            'size': list(image.size),
            'exact_color_pixels': {name: pixels.count(rgb) for name, rgb in colors.items()},
        }
    measurements_path = run / 'measurements.json'
    if measurements_path.exists():
        result['measurements'] = json.loads(measurements_path.read_text())
        # CONTRACT: the private log's clip is local to the root popup tree.
        # Subtracting it from the output viewport origin recovers that applied
        # scene-tree origin; XDG role configure offsets locate A and B below it.
        if result['scene_clip_logs']:
            clip = result['scene_clip_logs'][-1]
            left = result['measurements']['verified_outputs']['HEADLESS-1']
            root_x, root_y = left[0] - int(clip[1]), left[1] - int(clip[2])
            a = result['measurements']['popup_a_configure']
            b = result['measurements']['popup_b_configure']
            result['applied_scene_from_clip'] = {
                'root_popup_tree': [root_x, root_y],
                'popup_a': [root_x + a[0], root_y + a[1], a[2], a[3]],
                'popup_b': [root_x + a[0] + b[0], root_y + a[1] + b[1], b[2], b[3]],
            }
        for sample in result['measurements']['sample_points']:
            x, y = sample['global']
            output = 'left' if x < result['measurements']['verified_outputs']['HEADLESS-2'][0] else 'right'
            origin = result['measurements']['verified_outputs'][
                'HEADLESS-1' if output == 'left' else 'HEADLESS-2']
            path = run / f'{output}-open.png'
            if path.exists():
                local = (int(x - origin[0]), int(y - origin[1]))
                image = open_image(path)
                result['open_sample_rgb'][sample['purpose']] = {
                    'global': [x, y], 'output': output, 'local': list(local),
                    'rgb': list(image.getpixel(local)) if (
                        0 <= local[0] < image.width and 0 <= local[1] < image.height) else None,
                }
    (run / 'analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    print(run.name, result['captures'].get('left-open.png', {}).get('exact_color_pixels'),
          result['captures'].get('right-open.png', {}).get('exact_color_pixels'))
