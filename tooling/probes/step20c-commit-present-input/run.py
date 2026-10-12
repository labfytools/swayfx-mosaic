"""Adapt the frozen headless runner for bounded input-only ordering attempts."""
import argparse
from pathlib import Path
import subprocess
import sys

ap = argparse.ArgumentParser()
ap.add_argument('lab', type=Path)
ap.add_argument('mode', choices=('control', 'private_standard', 'private_mosaic'))
ap.add_argument('--cycles', type=int, default=5)
args = ap.parse_args()
if not 1 <= args.cycles <= 5:
    ap.error('at most five region cycles')
lab = args.lab.resolve()
repo = Path(__file__).resolve().parents[3]
original = (repo / 'tooling/probes/step20c-applied-state-input/run.py').read_text()
old = "choices=('cycles', 'buffer_cycles', 'identity', 'outside', 'hidden_click', 'toggle')"
assert original.count(old) == 1
adapted = original.replace(old, old[:-1] + ", 'ordering')")
anchor = "    if args.kind == 'cycles':\n"
assert adapted.count(anchor) == 1
scenario = '''    if args.kind == 'ordering':
        # CONTRACT: all surface input changes originate in the normal client;
        # only private Mosaic gets a camera request to supply output damage.
        o = owner()
        camera = workspace()['mosaic']['rows'][0]['scroll_x'] if args.mode == 'private_mosaic' else 0
        x = int(o['rect']['x'] - camera + o['window_rect']['x'] + 100)
        y = int(o['rect']['y'] + o['window_rect']['y'] + 150)
        snapshot('ordering-P0-reference')
        inject('move', x, y)
        inject('right', x, y)
        wait(lambda: count('POINTER_BUTTON target=TOPLEVEL') >= 1)
        record('ordering_point', global_point=[x, y], owner_id=o['id'])
        for i in range(args.cycles):
            record('ordering_cycle_start', cycle=i + 1)
            if args.mode == 'private_mosaic':
                command('layout mosaic scroll 200')
                record('ordering_camera_request', cycle=i + 1, delta=200)
            client_command('region_empty_top')
            inject('move', x, y)
            inject('right', x, y)
            if i == 0:
                snapshot('ordering-P1-empty')
            if args.mode == 'private_mosaic':
                command('layout mosaic scroll -200')
                record('ordering_camera_request', cycle=i + 1, delta=-200)
            before = count('POINTER_BUTTON target=TOPLEVEL')
            client_command('region_full_top')
            inject('move', x, y)
            inject('right', x, y)
            wait(lambda: count('POINTER_BUTTON target=TOPLEVEL') > before)
            record('ordering_cycle_end', cycle=i + 1)
        snapshot('ordering-P4-restored')
    elif args.kind == 'cycles':
'''
adapted = adapted.replace(anchor, scenario)
generated = lab / 'commit-present-input-run-generated.py'
generated.write_text(adapted)
raise SystemExit(subprocess.call([sys.executable, str(generated), str(lab),
    args.mode, 'ordering', '--cycles', str(args.cycles), '--asi-mode', '0',
    '--max-seconds', '120', '--max-captures', '12']))
