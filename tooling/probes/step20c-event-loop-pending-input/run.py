"""Bounded private headless runner with distinct submission and completion."""
import argparse
from pathlib import Path
import subprocess
import sys

ap = argparse.ArgumentParser()
ap.add_argument('lab', type=Path)
ap.add_argument('mode', choices=('control', 'private_standard', 'private_mosaic'))
ap.add_argument('--cycles', type=int, default=5)
ap.add_argument('--sequential', action='store_true')
ap.add_argument('--surface-trace', choices=('0', '1'), default='1')
args = ap.parse_args()
if not 1 <= args.cycles <= 5:
    ap.error('at most five timing attempts')
lab = args.lab.resolve()
repo = Path(__file__).resolve().parents[3]
original = (repo / 'tooling/probes/step20c-applied-state-input/run.py').read_text()
old = "choices=('cycles', 'buffer_cycles', 'identity', 'outside', 'hidden_click', 'toggle')"
assert original.count(old) == 1
adapted = original.replace(old, old[:-1] + ", 'pending')")
anchor = "    if args.kind == 'cycles':\n"
assert adapted.count(anchor) == 1
scenario = '''    if args.kind == 'pending':
        # CONTRACT: requests retain normal IPC/Wayland paths. A submission
        # record never claims server application; native traces decide order.
        def submit_ipc(value):
            record('ipc_submitted', value=value)
            return subprocess.Popen(['swaymsg', '-s', str(sock), value], env=env,
                                    text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

        def complete_ipc(proc, value):
            out, err = proc.communicate(timeout=8)
            record('ipc_completed', value=value, exit_code=proc.returncode,
                   output=out, error=err)
            result = json.loads(out)
            if proc.returncode or not isinstance(result, list) or not result or not all(
                    x.get('success') for x in result):
                raise RuntimeError(f'IPC command rejected: {value}: {out} {err}')

        def submit_client(value):
            before = count(f'COMMAND {value} DONE')
            record('client_submitted', value=value)
            client.stdin.write(value + '\\n')
            client.stdin.flush()
            return before

        def complete_client(value, before):
            wait(lambda: count(f'COMMAND {value} DONE') > before)
            record('client_completed', value=value)

        o = owner()
        camera = workspace()['mosaic']['rows'][0]['scroll_x'] if args.mode == 'private_mosaic' else 0
        x = int(o['rect']['x'] - camera + o['window_rect']['x'] + 100)
        y = int(o['rect']['y'] + o['window_rect']['y'] + 150)
        snapshot('pending-P0-reference')
        inject('move', x, y)
        inject('right', x, y)
        wait(lambda: count('POINTER_BUTTON target=TOPLEVEL') >= 1)
        record('pending_point', global_point=[x, y], owner_id=o['id'])
        for i in range(args.cycles):
            record('pending_cycle_start', cycle=i + 1)
            if args.sequential:
                if args.mode == 'private_mosaic': command('layout mosaic scroll 200')
                client_command('region_empty_top')
            else:
                # E2: launch ordinary camera activity and submit the client
                # request before waiting for either acknowledgement.
                value = ('layout mosaic scroll 200' if args.mode == 'private_mosaic'
                         else '[app_id="org.mosaic.NestedGrabProbe"] border pixel 2')
                proc = submit_ipc(value)
                before = submit_client('region_empty_top')
                complete_ipc(proc, value)
                complete_client('region_empty_top', before)
            inject('move', x, y)
            inject('right', x, y)
            if i == 0: snapshot('pending-P1-empty')
            if args.sequential:
                if args.mode == 'private_mosaic': command('layout mosaic scroll -200')
                client_command('region_full_top')
            else:
                # E3: the client request is submitted first. This does not
                # assert that the server fd is ready before repaint.
                before = submit_client('region_full_top')
                value = ('layout mosaic scroll -200' if args.mode == 'private_mosaic'
                         else '[app_id="org.mosaic.NestedGrabProbe"] border pixel 3')
                proc = submit_ipc(value)
                complete_client('region_full_top', before)
                complete_ipc(proc, value)
            prior = count('POINTER_BUTTON target=TOPLEVEL')
            inject('move', x, y)
            inject('right', x, y)
            wait(lambda: count('POINTER_BUTTON target=TOPLEVEL') > prior)
            record('pending_cycle_end', cycle=i + 1)
        snapshot('pending-P4-restored')
    elif args.kind == 'cycles':
'''
adapted = adapted.replace(anchor, scenario.replace('args.sequential', str(args.sequential)))
generated = lab / 'event-loop-pending-input-run-generated.py'
generated.write_text(adapted)
env = __import__('os').environ.copy()
env['CPI_SURFACE_TRACE'] = args.surface_trace
raise SystemExit(subprocess.call([sys.executable, str(generated), str(lab),
    args.mode, 'pending', '--cycles', str(args.cycles), '--asi-mode', '0',
    '--max-seconds', '120', '--max-captures', '12'], env=env))
