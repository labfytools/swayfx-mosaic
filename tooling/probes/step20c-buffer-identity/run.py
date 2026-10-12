"""EXPERIMENTAL buffer-identity headless campaign. See README."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time

parser = argparse.ArgumentParser()
parser.add_argument('lab', type=Path)
parser.add_argument('mode', choices=('control', 'private_standard', 'private_mosaic'))
parser.add_argument('kind', choices=('cycles', 'buffer_cycles', 'identity', 'outside', 'hidden_click', 'toggle'))
parser.add_argument('--cycles', type=int, default=10)
parser.add_argument('--moves', type=int, default=18)
parser.add_argument('--max-seconds', type=int, default=900)
parser.add_argument('--max-captures', type=int, default=400)
parser.add_argument('--max-bytes', type=int, default=250_000_000)
args = parser.parse_args()
if not 1 <= args.cycles <= 30 or not 1 <= args.moves <= 40:
    parser.error('cycle/move bounds exceeded')
if args.kind in ('identity', 'buffer_cycles', 'hidden_click', 'toggle') and args.mode != 'private_mosaic':
    parser.error('camera/toggle requires private_mosaic')
lab = args.lab.resolve()
if not (lab / 'nested-client').is_file():
    parser.error('prepared LAB required')
run = lab / 'runs' / f'{args.mode}-{args.kind}-{time.time_ns()}'
run.mkdir(parents=True, mode=0o700)
runtime = Path(tempfile.mkdtemp(prefix='mtd-', dir='/tmp'))
if len(os.fsencode(str(runtime / 'sway-ipc.4294967295.2147483647.sock'))) >= 108:
    raise RuntimeError('IPC socket path exceeds sockaddr_un')
(run / 'runtime-path').write_text(str(runtime) + '\n')
(run / 'config').write_text(
    'output HEADLESS-1 resolution 800x600 position -800 0\n'
    'output HEADLESS-2 resolution 800x600 position 0 0\n'
    'workspace 1 output HEADLESS-1\nworkspace 2 output HEADLESS-2\n'
    'focus_follows_mouse no\n')
env = os.environ.copy()
env.update(XDG_RUNTIME_DIR=str(runtime), WLR_BACKENDS='headless',
           WLR_HEADLESS_OUTPUTS='2', WLR_RENDERER='pixman')
for key in ('SWAYSOCK', 'I3SOCK', 'WAYLAND_DISPLAY', 'LD_LIBRARY_PATH'):
    env.pop(key, None)
compositor_env = env.copy()
binary = Path('/usr/bin/sway') if args.mode == 'control' else lab / 'mosaic-build/sway/swayfx-mosaic'
if args.mode != 'control':
    compositor_env['LD_LIBRARY_PATH'] = str(lab / 'scenefx-build')
files, children, events = [], [], []
started = time.monotonic()
capture_count = 0
capture_bytes = 0


def record(kind, **fields):
    entry = {'monotonic_ns': time.monotonic_ns(), 'kind': kind, **fields}
    events.append(entry)
    with (run / 'events.jsonl').open('a') as out:
        out.write(json.dumps(entry) + '\n')
    return entry


def spawn(argv, log_name, *, stdin=False, debug=False):
    log = (run / log_name).open('w')
    files.append(log)
    child_env = env.copy()
    if debug:
        child_env['WAYLAND_DEBUG'] = '1'
    proc = subprocess.Popen(argv, env=child_env, stdin=subprocess.PIPE if stdin else None,
                            stdout=log, stderr=subprocess.STDOUT,
                            start_new_session=True, text=stdin)
    children.append(proc)
    return proc


def wait(predicate, seconds=12):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if time.monotonic() - started > args.max_seconds:
            raise RuntimeError('run duration bound exceeded')
        result = predicate()
        if result:
            return result
        if compositor.poll() is not None:
            raise RuntimeError(f'compositor exited {compositor.returncode}')
        if 'pointer' in globals() and pointer.poll() is not None:
            raise RuntimeError(f'pointer exited {pointer.returncode}')
        if 'client' in globals() and client.poll() is not None:
            raise RuntimeError(f'client exited {client.returncode}')
        time.sleep(.04)
    raise RuntimeError('timeout waiting for event')


def ipc(*argv):
    completed = subprocess.run(['swaymsg', '-s', str(sock), *argv], env=env,
                               text=True, capture_output=True, check=True, timeout=8)
    result = json.loads(completed.stdout)
    record('ipc', argv=list(argv), result=result)
    return result


def command(value):
    result = ipc(value)
    if not isinstance(result, list) or not result or not all(x.get('success') for x in result):
        raise RuntimeError(f'IPC command rejected: {value}: {result}')


def find(node, predicate):
    if isinstance(node, dict):
        if predicate(node):
            return node
        for child in node.get('nodes', []) + node.get('floating_nodes', []):
            found = find(child, predicate)
            if found:
                return found
    return None


def tree():
    return ipc('-t', 'get_tree')


def workspace():
    return find(tree(), lambda n: n.get('type') == 'workspace' and n.get('name') == '1')


def owner():
    return find(tree(), lambda n: n.get('app_id') == 'org.mosaic.NestedGrabProbe')


def client_text():
    return (run / 'client.log').read_text()


def count(marker):
    return client_text().count(marker)


def configured(name):
    matches = re.findall(rf'{name} ROLE_CONFIGURE x=(-?\d+) y=(-?\d+) w=(\d+) h=(\d+)',
                         client_text())
    if not matches:
        raise RuntimeError(f'no {name} role configure')
    return tuple(map(int, matches[-1]))


def snapshot(tag):
    global capture_count, capture_bytes
    t = tree()
    outputs = ipc('-t', 'get_outputs')
    (run / f'tree-{tag}.json').write_text(json.dumps(t, indent=2) + '\n')
    (run / f'outputs-{tag}.json').write_text(json.dumps(outputs, indent=2) + '\n')
    expected = {'HEADLESS-1': (-800, 0, 800, 600), 'HEADLESS-2': (0, 0, 800, 600)}
    actual = {}
    for output in outputs:
        if output.get('name') in expected and output.get('active'):
            rect = output['rect']
            if output.get('scale') != 1.0 or output.get('transform') != 'normal':
                raise RuntimeError('output scale/transform mismatch')
            actual[output['name']] = (rect['x'], rect['y'], rect['width'], rect['height'])
    if actual != expected:
        raise RuntimeError(f'output geometry mismatch: {actual}')
    for output, side in (('HEADLESS-1', 'left'), ('HEADLESS-2', 'right')):
        if capture_count >= args.max_captures:
            raise RuntimeError('capture count bound exceeded')
        path = run / f'{side}-{tag}.png'
        before = time.monotonic_ns()
        subprocess.run(['grim', '-o', output, str(path)], env=env, check=True,
                       stdout=subprocess.DEVNULL, timeout=10)
        after = time.monotonic_ns()
        capture_count += 1
        capture_bytes += path.stat().st_size
        if capture_bytes > args.max_bytes:
            raise RuntimeError('capture byte bound exceeded')
        record('capture', tag=tag, output=output, path=path.name,
               before_ns=before, after_ns=after, size=path.stat().st_size)


def inject(action, x, y):
    if not (-800 <= x < 800 and 0 <= y < 600):
        raise ValueError('global pointer out of bounds')
    sent = x + 800
    marker = f'INJECT_DONE {action} {sent},{y}'
    before = (run / 'pointer.log').read_text().count(marker)
    record('pointer_request', action=action, global_point=[x, y], sent=[sent, y],
           extent=[1600, 600], output='HEADLESS-1' if x < 0 else 'HEADLESS-2')
    pointer.stdin.write(f'{action} {sent} {y}\n')
    pointer.stdin.flush()
    wait(lambda: (run / 'pointer.log').read_text().count(marker) > before)


def client_command(value):
    marker = f'COMMAND {value} DONE'
    before = count(marker)
    record('client_request', value=value)
    client.stdin.write(value + '\n')
    client.stdin.flush()
    wait(lambda: count(marker) > before)


def scroll(target):
    current = workspace()['mosaic']['rows'][0]['scroll_x']
    command(f'layout mosaic scroll {target-current:g}')
    wait(lambda: workspace()['mosaic']['rows'][0]['scroll_x'] == target)
    record('camera_observed', target=target, owner_id=owner()['id'])


def open_chain(cycle):
    a_before, b_before = count('POPUP_A MAP'), count('POPUP_B MAP')
    o = owner()
    scroll_x = workspace()['mosaic']['rows'][0]['scroll_x'] if args.mode == 'private_mosaic' else 0
    top_x = int(o['rect']['x'] - scroll_x + o['window_rect']['x'] + 100)
    inject('move', top_x, 150)
    inject('left', top_x, 150)
    wait(lambda: count('POPUP_A MAP') > a_before)
    snapshot(f'{cycle}-S1-A')
    a_cfg = configured('POPUP_A')
    a_x = int(o['rect']['x'] - scroll_x + o['window_rect']['x'] + a_cfg[0] + 40)
    a_y = int(o['rect']['y'] + o['window_rect']['y'] + a_cfg[1] + 35)
    inject('move', a_x, a_y)
    inject('left', a_x, a_y)
    wait(lambda: count('POPUP_B MAP') > b_before)
    snapshot(f'{cycle}-S2-B')
    b_cfg = configured('POPUP_B')
    b_x = int(o['rect']['x'] - scroll_x + o['window_rect']['x'] + a_cfg[0] + b_cfg[0] + 35)
    b_y = int(o['rect']['y'] + o['window_rect']['y'] + a_cfg[1] + b_cfg[1] + 30)
    inject('move', b_x, b_y)
    inject('right', b_x, b_y)
    time.sleep(.12)
    snapshot(f'{cycle}-S3-visible')
    record('chain', cycle=cycle, owner_id=o['id'], scroll_x=scroll_x,
           a_configure=a_cfg, b_configure=b_cfg,
           top_global=[top_x, 150], a_global=[a_x, a_y], b_global=[b_x, b_y])


def cycle_once(number):
    label = f'cycle-{number:03d}'
    record('cycle_start', cycle=number)
    snapshot(f'{label}-S0-reference')
    open_chain(label)
    if args.mode == 'private_mosaic':
        scroll(1280)
        snapshot(f'{label}-S4-hidden-immediate')
        time.sleep(.18)
        snapshot(f'{label}-S4-hidden-stable')
        inject('move', -700, 190)
        time.sleep(.1)
        snapshot(f'{label}-S4-hidden-hover')
        scroll(400)
        snapshot(f'{label}-S5-return-immediate')
        time.sleep(.18)
        snapshot(f'{label}-S5-return-stable')
    client_command('close_b')
    snapshot(f'{label}-S6-close-B-immediate')
    time.sleep(.18)
    snapshot(f'{label}-S6-close-B-stable')
    a_cfg = configured('POPUP_A')
    o = owner()
    scroll_x = workspace()['mosaic']['rows'][0]['scroll_x'] if args.mode == 'private_mosaic' else 0
    a_x = int(o['rect']['x'] - scroll_x + o['window_rect']['x'] + a_cfg[0] + 20)
    a_y = int(o['rect']['y'] + o['window_rect']['y'] + a_cfg[1] + 20)
    before_a = len(re.findall(r'POINTER_BUTTON target=POPUP_A[^\n]*button=273 state=1', client_text()))
    inject('move', a_x, a_y)
    inject('right', a_x, a_y)
    wait(lambda: len(re.findall(r'POINTER_BUTTON target=POPUP_A[^\n]*button=273 state=1',
                               client_text())) > before_a)
    snapshot(f'{label}-S6-A-interaction')
    client_command('close_a')
    snapshot(f'{label}-S7-close-A-immediate')
    time.sleep(.18)
    snapshot(f'{label}-S7-close-A-stable')
    record('cycle_end', cycle=number, owner_id=owner()['id'], client_alive=client.poll() is None)


compositor_log = (run / 'compositor.log').open('w')
files.append(compositor_log)
compositor = None
failure = None
try:
    compositor = subprocess.Popen([str(binary), '-c', str(run / 'config'), '-d'],
                                  env=compositor_env, stdout=compositor_log,
                                  stderr=subprocess.STDOUT, start_new_session=True)
    def sockets():
        s = next(iter(runtime.glob('sway-ipc.*.sock')), None)
        w = next((p for p in runtime.glob('wayland-*') if p.suffix != '.lock'), None)
        return (s, w) if s and w else None
    sock, way = wait(sockets)
    env.update(SWAYSOCK=str(sock), WAYLAND_DISPLAY=way.name)
    snapshot('startup')
    pointer = spawn([str(lab / 'pointer-daemon'), '1600', '600'], 'pointer.log', stdin=True)
    wait(lambda: 'POINTER_READY' in (run / 'pointer.log').read_text())
    command('workspace 1')
    command('layout mosaic' if args.mode == 'private_mosaic' else 'layout splith')
    spawn(['kitty', '--class', 'A', '-o', 'cursor_blink_interval=0',
           '-o', 'background=#aa2222', '/usr/bin/sleep', '900'], 'A.log')
    wait(lambda: len(workspace()['nodes']) >= 1)
    client = spawn([str(lab / 'nested-client'), 'b_cross'], 'client.log', stdin=True, debug=True)
    wait(lambda: owner() and 'TOPLEVEL MAP' in client_text())
    for name in ('C', 'D'):
        spawn(['kitty', '--class', name, '-o', 'cursor_blink_interval=0',
               '/usr/bin/sleep', '900'], f'{name}.log')
        time.sleep(.25)
    command('workspace 2')
    spawn(['stdbuf', '-oL', 'wev'], 'wev.log')
    wait(lambda: find(tree(), lambda n: n.get('app_id') == 'wev'))
    command('workspace 1')
    command('[app_id="org.mosaic.NestedGrabProbe"] focus')
    if args.mode == 'private_mosaic':
        scroll(400)
    time.sleep(.25)
    if args.kind == 'cycles':
        for i in range(1, args.cycles + 1):
            cycle_once(i)
    elif args.kind == 'buffer_cycles':
        if args.cycles > 3:
            parser.error('buffer probe permits at most three pairs')
        open_chain('buffer')
        snapshot('buffer-visible-start')
        for i in range(args.cycles):
            record('buffer_pair_start', pair=i + 1, owner_id=owner()['id'])
            scroll(1280)
            snapshot(f'buffer-hidden-{i+1}-immediate')
            time.sleep(.18)
            snapshot(f'buffer-hidden-{i+1}-stable')
            scroll(400)
            snapshot(f'buffer-return-{i+1}-immediate')
            time.sleep(.18)
            snapshot(f'buffer-return-{i+1}-stable')
            record('buffer_pair_end', pair=i + 1, owner_id=owner()['id'],
                   a_maps=count('POPUP_A MAP'), b_maps=count('POPUP_B MAP'))
        client_command('close_b')
        client_command('close_a')
        snapshot('buffer-closed')
    elif args.kind == 'identity':
        # CONTRACT: ten settled changes are five complete 400/1280 pairs.
        # Twelve following requests omit intervening captures; acceptance is
        # recorded, but coalesced intermediate presentations remain possible.
        snapshot('identity-S0-reference')
        open_chain('identity')
        for i in range(10):
            target = 1280 if i % 2 == 0 else 400
            record('transition_start', series='settled', index=i, target=target)
            scroll(target)
            snapshot(f'identity-settled-{i:02d}-immediate')
            time.sleep(.18)
            snapshot(f'identity-settled-{i:02d}-stable')
        for i in range(12):
            target = 1280 if i % 2 == 0 else 400
            record('transition_start', series='rapid', index=i, target=target)
            scroll(target)
            if i % 4 == 3:
                snapshot(f'identity-rapid-{i:02d}')
        snapshot('identity-rapid-final')
        # CONTRACT: this input check follows camera return without closing or
        # recreating either XDG popup; a fresh button is delivered to B.
        o = owner()
        a_cfg, b_cfg = configured('POPUP_A'), configured('POPUP_B')
        current_scroll = workspace()['mosaic']['rows'][0]['scroll_x']
        b_x = int(o['rect']['x'] - current_scroll + o['window_rect']['x'] +
                  a_cfg[0] + b_cfg[0] + 35)
        b_y = int(o['rect']['y'] + o['window_rect']['y'] +
                  a_cfg[1] + b_cfg[1] + 30)
        before_b = len(re.findall(r'POINTER_BUTTON target=POPUP_B[^\n]*button=273 state=1',
                                  client_text()))
        inject('move', b_x, b_y)
        inject('right', b_x, b_y)
        wait(lambda: len(re.findall(r'POINTER_BUTTON target=POPUP_B[^\n]*button=273 state=1',
                                   client_text())) > before_b)
        record('post_return_B_button', global_point=[b_x, b_y], owner_id=o['id'])
        snapshot('identity-post-return-B-button')
        client_command('close_b')
        client_command('close_a')
        snapshot('identity-closed')
    elif args.kind == 'outside':
        snapshot('outside-S0-reference')
        open_chain('outside')
        inject('move', 100, 350)
        inject('left', 100, 350)
        time.sleep(.18)
        snapshot('outside-dismissed')
    elif args.kind == 'hidden_click':
        snapshot('hidden-click-S0-reference')
        open_chain('hidden-click')
        scroll(1280)
        snapshot('hidden-click-hidden')
        before_buttons = len(re.findall(r'POINTER_BUTTON target=POPUP_[AB][^\n]*state=1',
                                        client_text()))
        inject('move', -700, 190)
        inject('right', -700, 190)
        wait(lambda: 'POPUP_B POPUP_DONE' in client_text() and
             'POPUP_A POPUP_DONE' in client_text())
        after_buttons = len(re.findall(r'POINTER_BUTTON target=POPUP_[AB][^\n]*state=1',
                                       client_text()))
        record('hidden_click_target', popup_buttons_before=before_buttons,
               popup_buttons_after=after_buttons)
        snapshot('hidden-click-dismissed')
        scroll(400)
        snapshot('hidden-click-returned')
    else:
        snapshot('toggle-S0-reference')
        open_chain('toggle')
        command('layout splith')
        snapshot('toggle-standard-immediate')
        time.sleep(.4)
        snapshot('toggle-standard-stable')
        o = owner()
        a_cfg, b_cfg = configured('POPUP_A'), configured('POPUP_B')
        b_x = int(max(20, o['rect']['x'] + o['window_rect']['x'] +
                      a_cfg[0] + b_cfg[0] + 20))
        b_y = int(o['rect']['y'] + o['window_rect']['y'] + a_cfg[1] + b_cfg[1] + 30)
        if b_x < 0:
            raise RuntimeError('standard B sample does not cross x=0')
        inject('move', b_x, b_y)
        inject('right', b_x, b_y)
        snapshot('toggle-standard-click')
        client_command('close_b')
        client_command('close_a')
        snapshot('toggle-closed')
except Exception as exc:
    failure = repr(exc)
    record('failure', error=failure)
finally:
    for proc in children + ([compositor] if compositor is not None else []):
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    for proc in children + ([compositor] if compositor is not None else []):
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5)
    (run / 'exit-status.json').write_text(json.dumps({
        'failure': failure, 'compositor': None if compositor is None else compositor.returncode,
        'children': [{'argv': p.args, 'returncode': p.returncode} for p in children],
        'captures': capture_count, 'capture_bytes': capture_bytes,
        'duration_seconds': time.monotonic() - started}, indent=2) + '\n')
    for file in files:
        file.close()
    shutil.rmtree(runtime)
    record('cleanup', runtime_removed=not runtime.exists())
print(f'RUN={run} FAILURE={failure} CAPTURES={capture_count}')
if failure:
    raise SystemExit(1)
