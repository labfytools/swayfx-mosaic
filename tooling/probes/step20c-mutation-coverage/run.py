"""Adapt the frozen trace-only runner in a disposable lab for T3/T4.

The generated copy, sockets and captures stay outside Git. Existing process
cleanup, output geometry checks and explicit swaymsg socket remain intact.
"""
import argparse
from pathlib import Path
import subprocess
import sys

ap = argparse.ArgumentParser()
ap.add_argument('lab', type=Path)
ap.add_argument('mode', choices=('control', 'private_standard', 'private_mosaic'))
ap.add_argument('scenario', choices=('content', 'input_region', 'hold_exit'))
args = ap.parse_args()
lab = args.lab.resolve()
repo = Path(__file__).resolve().parents[3]
original = (repo / 'tooling/probes/step20c-applied-state-input/run.py').read_text()
old_choices = "choices=('cycles', 'buffer_cycles', 'identity', 'outside', 'hidden_click', 'toggle')"
new_choices = "choices=('cycles', 'buffer_cycles', 'identity', 'outside', 'hidden_click', 'toggle', 'mutation_content', 'mutation_input_region', 'mutation_hold_exit')"
assert original.count(old_choices) == 1
adapted = original.replace(old_choices, new_choices)
anchor = "    if args.kind == 'cycles':\n"
assert adapted.count(anchor) == 1
scenario_code = '''    if args.kind == 'mutation_content':
        # WHY: a client buffer replacement must not be mistaken for a
        # geometry/clip mutation merely because it creates output damage.
        snapshot('content-before')
        client_command('recolor_top')
        time.sleep(.25)
        snapshot('content-after')
        record('mutation_content', owner_id=owner()['id'],
               top_maps=count('TOPLEVEL MAP'))
    elif args.kind == 'mutation_input_region':
        # CONTRACT: no XDG popup/grab is active. Both hits address the same
        # global point; the client log proves actual toplevel delivery.
        o = owner()
        camera = workspace()['mosaic']['rows'][0]['scroll_x'] if args.mode == 'private_mosaic' else 0
        x = int(o['rect']['x'] - camera + o['window_rect']['x'] + 100)
        y = int(o['rect']['y'] + o['window_rect']['y'] + 150)
        inject('move', x, y)
        inject('right', x, y)
        wait(lambda: count('POINTER_BUTTON target=TOPLEVEL') >= 1)
        snapshot('region-full-before')
        client_command('region_empty_top')
        inject('move', x, y)
        inject('right', x, y)
        snapshot('region-empty')
        client_command('region_full_top')
        before = count('POINTER_BUTTON target=TOPLEVEL')
        inject('move', x, y)
        inject('right', x, y)
        wait(lambda: count('POINTER_BUTTON target=TOPLEVEL') > before)
        snapshot('region-full-after')
        record('mutation_input_region', point=[x,y], owner_id=o['id'])
    elif args.kind == 'mutation_hold_exit':
        # CONTRACT: terminate the private compositor from the runner after a
        # normal event-loop present has intentionally retained one extra lock.
        # Never destroy an output inside its own callback.
        open_chain('hold-exit')
        wait(lambda: 'ASI_TEST_HOLD id=1' in (run / 'compositor.log').read_text())
        record('hold_exit_requested', first_hold_retained=True)
    elif args.kind == 'cycles':
'''
adapted = adapted.replace(anchor, scenario_code)
generated = lab / 'mutation-run-generated.py'
generated.write_text(adapted)
kind = 'mutation_' + args.scenario
flags = ['--asi-mode', '1', '--test-hold'] if args.scenario == 'hold_exit' else ['--asi-mode', '0']
raise SystemExit(subprocess.call([sys.executable, str(generated), str(lab),
    args.mode, kind, *flags, '--max-seconds', '120',
    '--max-captures', '12']))
