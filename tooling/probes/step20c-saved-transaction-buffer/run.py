"""One reserved headless run with a real held XDG configure per episode."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time
from PIL import Image
from budget import reserve

parser = argparse.ArgumentParser()
parser.add_argument('lab', type=Path)
parser.add_argument('mode', choices=('control', 'private_standard', 'private_mosaic'))
args = parser.parse_args()
lab = args.lab.resolve()
if not (lab / 'saved-client').is_file():
    parser.error('prepared LAB required')
state = reserve(lab, args.mode)
run = lab / 'runs' / f'saved-{args.mode}-{time.time_ns()}'
run.mkdir(parents=True, mode=0o700)
(run / 'fixture-source.py').write_text(Path(__file__).read_text())
runtime = Path(tempfile.mkdtemp(prefix='mst-', dir='/tmp'))
(run / 'runtime-path').write_text(str(runtime) + '\n')
(run / 'config').write_text(
    'output HEADLESS-1 resolution 800x600 scale 1 transform normal position -800 0\n'
    'output HEADLESS-2 resolution 800x600 scale 1 transform normal position 0 0\n'
    'workspace 1 output HEADLESS-1\nworkspace 2 output HEADLESS-2\n'
    'focus_follows_mouse no\n')
env = os.environ.copy()
for key in ('SWAYSOCK', 'I3SOCK', 'WAYLAND_DISPLAY', 'LD_LIBRARY_PATH'):
    env.pop(key, None)
env.update(XDG_RUNTIME_DIR=str(runtime), WLR_BACKENDS='headless',
           WLR_HEADLESS_OUTPUTS='2', WLR_RENDERER='pixman', SAVED_TRACE='1')
binary = lab / ('standard-build/sway/sway' if args.mode == 'control'
                else 'mosaic-build/sway/swayfx-mosaic')
if args.mode != 'control':
    env['LD_LIBRARY_PATH'] = str(lab / 'scenefx-build')
started = time.monotonic()
captures = 0
events = []
processes = []
logs = []
failure = None
compositor = None


def record(kind, **kw):
    event = {'ns': time.monotonic_ns(), 'kind': kind, **kw}
    events.append(event)
    with (run / 'events.jsonl').open('a') as file:
        file.write(json.dumps(event) + '\n')


def spawn(argv, name, *, stdin=False, use_env=None):
    file = (run / name).open('w')
    logs.append(file)
    proc = subprocess.Popen(argv, env=use_env or env, stdout=file,
                            stderr=subprocess.STDOUT, start_new_session=True,
                            stdin=subprocess.PIPE if stdin else None, text=stdin)
    processes.append(proc)
    return proc


def wait(predicate, seconds=8):
    limit = time.monotonic() + seconds
    while time.monotonic() < limit:
        if time.monotonic() - started > 150:
            raise RuntimeError('150 second run bound exceeded')
        value = predicate()
        if value:
            return value
        if compositor and compositor.poll() is not None:
            raise RuntimeError(f'compositor exit {compositor.returncode}')
        time.sleep(.025)
    raise RuntimeError('wait timed out')


def ipc(*argv):
    result = subprocess.run(['swaymsg', '-s', str(sock), *argv], env=env,
                            capture_output=True, text=True, timeout=5, check=True)
    value = json.loads(result.stdout)
    record('ipc', argv=list(argv), result=value)
    return value


def command(value):
    result = ipc(value)
    if not result or not all(x.get('success') for x in result):
        raise RuntimeError(f'IPC rejected {value}: {result}')


def find(node, predicate):
    if isinstance(node, dict):
        if predicate(node):
            return node
        for child in node.get('nodes', []) + node.get('floating_nodes', []):
            match = find(child, predicate)
            if match:
                return match
    return None


def client_log():
    return (run / 'client.log').read_text()


def compositor_log():
    return (run / 'compositor.log').read_text()


def client_command(value):
    marker = f'COMMAND {value} DONE'
    before = client_log().count(marker)
    client.stdin.write(value + '\n')
    client.stdin.flush()
    wait(lambda: client_log().count(marker) > before)
    record('client_command', value=value)


def inject(action, x, y):
    if not -800 <= x < 800 or not 0 <= y < 600:
        raise ValueError('pointer point outside applied outputs')
    marker = f'INJECT_DONE {action} {x + 800},{y}'
    before = (run / 'pointer.log').read_text().count(marker)
    pointer.stdin.write(f'{action} {x + 800} {y} 1600 600\n')
    pointer.stdin.flush()
    wait(lambda: (run / 'pointer.log').read_text().count(marker) > before)
    record('pointer', action=action, global_point=[x, y],
           client_tail=client_log().splitlines()[-5:])


def snapshot(tag):
    global captures
    outputs = ipc('-t', 'get_outputs')
    actual = {o['name']: (o['rect']['x'], o['rect']['y'],
              o['rect']['width'], o['rect']['height']) for o in outputs if o['active']}
    if actual != {'HEADLESS-1': (-800, 0, 800, 600), 'HEADLESS-2': (0, 0, 800, 600)}:
        raise RuntimeError(f'output geometry invalid: {actual}')
    for name, side in (('HEADLESS-1', 'left'), ('HEADLESS-2', 'right')):
        if captures >= 20:
            raise RuntimeError('capture budget exceeded')
        path = run / f'{side}-{tag}.png'
        before = time.monotonic_ns()
        subprocess.run(['grim', '-s', '1', '-o', name, str(path)], env=env,
                       check=True, timeout=5, stdout=subprocess.DEVNULL)
        after = time.monotonic_ns()
        captures += 1
        size = Image.open(path).size
        if size != (800, 600):
            raise RuntimeError(f'PNG dimensions invalid: {size}')
        record('capture', tag=tag, output=name, path=path.name,
               before_ns=before, after_ns=after, size=size)
    (run / f'tree-{tag}.json').write_text(json.dumps(ipc('-t', 'get_tree'), indent=2) + '\n')


def episode(kind, gaps):
    reserve(lab, args.mode, kind)
    record('episode_start', episode=kind, gaps=gaps)
    client_command('hold_next_configure')
    old_held = client_log().count('HELD ns=')
    old_tree = compositor_log().count('SB_TREE_CREATE')
    command(f'gaps inner current set {gaps}')
    wait(lambda: client_log().count('HELD ns=') > old_held, 3)
    wait(lambda: compositor_log().count('SB_TREE_CREATE') > old_tree, 3)
    record('held', client=client_log().splitlines()[-12:],
           saved=compositor_log().splitlines()[-30:])
    snapshot(f'{kind}-held')
    # The private-standard ACK episode exhausted its 1200 ms window during
    # six pointer commands. Preserve that incident and prioritize the actual
    # Mosaic snapshot lifetime; no unmeasured input claim follows.
    if kind == 'ack':
        old_destroy = compositor_log().count('SB_TREE_DESTROY')
        client_command('release_configure')
        wait(lambda: compositor_log().count('SB_TREE_DESTROY') > old_destroy, 3)
        snapshot('ack-applied')
    else:
        wait(lambda: 'timed out' in compositor_log().split('SB_TREE_CREATE')[-1], 3)
        record('timeout_observed')
        snapshot('timeout-applied')


try:
    file = (run / 'compositor.log').open('w')
    logs.append(file)
    compositor = subprocess.Popen([str(binary), '-c', str(run / 'config'),
                                   '-d', '-Dtxn-timeout=1200'], env=env,
                                  stdout=file, stderr=subprocess.STDOUT,
                                  start_new_session=True)
    def sockets():
        s = next(iter(runtime.glob('sway-ipc.*.sock')), None)
        w = next((p for p in runtime.glob('wayland-*') if p.suffix != '.lock'), None)
        return (s, w) if s and w else None
    sock, way = wait(sockets)
    env.update(SWAYSOCK=str(sock), WAYLAND_DISPLAY=way.name)
    if args.mode != 'control':
        pointer = spawn([str(lab / 'pointer-daemon'), '1600', '600'],
                        'pointer.log', stdin=True)
        wait(lambda: 'POINTER_READY' in (run / 'pointer.log').read_text())
    command('workspace 1')
    command('layout mosaic' if args.mode == 'private_mosaic' else 'layout splith')
    spawn(['kitty', '--class', 'A', '/usr/bin/sleep', '900'], 'A.log')
    wait(lambda: len(find(ipc('-t', 'get_tree'),
         lambda n: n.get('type') == 'workspace' and n.get('name') == '1')['nodes']) >= 1)
    client = spawn([str(lab / 'saved-client')], 'client.log', stdin=True)
    wait(lambda: 'COMMIT ns=' in client_log())
    for name in ('C', 'D'):
        spawn(['kitty', '--class', name, '/usr/bin/sleep', '900'], f'{name}.log')
        time.sleep(.2)
    command('workspace 2')
    spawn(['kitty', '--class', 'REFERENCE', '-o', 'background=#303038',
           '/usr/bin/sleep', '900'], 'reference.log')
    wait(lambda: bool(find(ipc('-t', 'get_tree'),
         lambda n: n.get('type') == 'workspace' and n.get('name') == '2')['nodes']))
    command('workspace 1')
    if args.mode == 'private_mosaic':
        command('layout mosaic scroll 400')
    time.sleep(.2)
    tree = ipc('-t', 'get_tree')
    owner = find(tree, lambda n: n.get('app_id') == 'org.mosaic.SavedBufferProbe')
    workspace = find(tree, lambda n: n.get('type') == 'workspace' and n.get('name') == '1')
    if not owner or not workspace:
        raise RuntimeError('owner/workspace calibration failed')
    record('identity', owner=owner, workspace=workspace)
    snapshot('reference')
    episode('ack', 30)
    episode('timeout', 50)
except Exception as exc:
    failure = repr(exc)
    record('failure', message=failure)
finally:
    for proc in processes + ([compositor] if compositor else []):
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    for proc in processes + ([compositor] if compositor else []):
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5)
    for file in logs:
        file.close()
    (run / 'exit-status.json').write_text(json.dumps({
        'failure': failure, 'captures': captures,
        'duration_seconds': time.monotonic() - started,
        'compositor': compositor.returncode if compositor else None,
        'children': [{'args': p.args, 'code': p.returncode} for p in processes]},
        indent=2) + '\n')
    shutil.rmtree(runtime)
    record('cleanup', runtime_removed=not runtime.exists())
print(f'RUN={run} FAILURE={failure} CAPTURES={captures}')
if failure:
    raise SystemExit(1)
