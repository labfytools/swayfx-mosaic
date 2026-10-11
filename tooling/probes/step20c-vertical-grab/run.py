"""EXPERIMENTAL vertical/horizontal two-output nested XDG grab runner.

Usage: python run.py LAB {control,private_standard,private_mosaic} SCENARIO GEOMETRY
SCENARIO: visible, b_cross, both_cross, below_left, below_right, hidden,
          below_a, hidden_click, toggle
GEOMETRY: vertical, horizontal (horizontal b_cross regression only)
"""
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

if len(sys.argv) != 5:
    raise SystemExit(__doc__)
LAB = pathlib.Path(sys.argv[1]).resolve()
case, scenario, geometry = sys.argv[2:5]
assert case in ('control', 'private_standard', 'private_mosaic')
assert scenario in ('visible', 'b_cross', 'both_cross', 'below_left', 'below_right', 'below_a',
                    'hidden', 'hidden_click', 'toggle')
assert geometry in ('vertical', 'horizontal')
if geometry == 'horizontal' and scenario != 'b_cross':
    raise SystemExit('horizontal regression uses b_cross')
if scenario in ('hidden', 'hidden_click', 'toggle') and case != 'private_mosaic':
    raise SystemExit('this scenario requires private_mosaic')
assert LAB.is_dir() and (LAB / 'nested-client').is_file()
placement = ('b_cross' if geometry == 'horizontal' else
             'v_visible' if scenario == 'visible' else
             'v_both_cross' if scenario in ('both_cross', 'below_a') else 'v_b_cross')
run = LAB / f'run-{geometry}-{case}-{scenario}'
run.mkdir(mode=0o700, exist_ok=False)
runtime = pathlib.Path(tempfile.mkdtemp(prefix='mvg-', dir='/tmp'))
# WHY: keep both Unix socket names below sockaddr_un.sun_path even if LAB is
# long; the compositor derives its IPC path from XDG_RUNTIME_DIR.
if len(os.fsencode(str(runtime / 'sway-ipc.4294967295.2147483647.sock'))) >= 108:
    raise RuntimeError('private IPC socket path exceeds Linux sockaddr_un.sun_path')
(run / 'runtime-path').write_text(str(runtime) + '\n')
output2 = ('output HEADLESS-2 resolution 800x600 position 0 600\n'
           if geometry == 'vertical' else
           'output HEADLESS-2 resolution 800x600 position 800 0\n')
(run / 'config').write_text(
    'output HEADLESS-1 resolution 800x600 position 0 0\n' + output2 +
    'workspace 1 output HEADLESS-1\nworkspace 2 output HEADLESS-2\n'
    'focus_follows_mouse no\n')
env = os.environ.copy()
env.update(XDG_RUNTIME_DIR=str(runtime), WLR_BACKENDS='headless',
           WLR_HEADLESS_OUTPUTS='2', WLR_RENDERER='pixman')
env.pop('WAYLAND_DISPLAY', None)
env.pop('SWAYSOCK', None)
env.pop('I3SOCK', None)
env.pop('LD_LIBRARY_PATH', None)
compositor_env = env.copy()
if case == 'control':
    binary = pathlib.Path('/usr/bin/sway')
else:
    binary = LAB / 'mosaic-build/sway/swayfx-mosaic'
    compositor_env['LD_LIBRARY_PATH'] = str(LAB / 'scenefx-build')
files = []
children = []


def spawn(argv, name, *, debug=False, stdin=None):
    log = (run / name).open('w')
    files.append(log)
    child_env = env.copy()
    if debug:
        child_env['WAYLAND_DEBUG'] = '1'
    proc = subprocess.Popen(argv, env=child_env, stdin=stdin, stdout=log,
                            stderr=subprocess.STDOUT, text=True,
                            start_new_session=True)
    children.append(proc)
    return proc


def wait(fn, seconds=12):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        result = fn()
        if result:
            return result
        if compositor.poll() is not None:
            raise RuntimeError(f'compositor exited {compositor.returncode}')
        if 'pointer' in globals() and pointer.poll() is not None:
            raise RuntimeError(f'virtual pointer exited {pointer.returncode}')
        time.sleep(.05)
    raise RuntimeError('timeout waiting for probe event')


def ipc(*args):
    return json.loads(subprocess.run(['swaymsg', '-s', str(sock), *args],
                      env=env, text=True, capture_output=True, check=True,
                      timeout=5).stdout)


def find(node, predicate):
    if isinstance(node, dict):
        if predicate(node):
            return node
        for child in node.get('nodes', []) + node.get('floating_nodes', []):
            result = find(child, predicate)
            if result:
                return result
    return None


def tree():
    return ipc('-t', 'get_tree')


def ws():
    return find(tree(), lambda n: n.get('type') == 'workspace' and n.get('name') == '1')


def owner():
    return find(tree(), lambda n: n.get('app_id') == 'org.mosaic.NestedGrabProbe')


def logged(s):
    path = run / 'client.log'
    return path.exists() and s in path.read_text()


def configured(name):
    """The server's last role configure, not the positioner request."""
    matches = re.findall(rf'{name} ROLE_CONFIGURE x=(-?\d+) y=(-?\d+) w=(\d+) h=(\d+)',
                         (run / 'client.log').read_text())
    if not matches:
        raise RuntimeError(f'missing {name} ROLE_CONFIGURE')
    return tuple(map(int, matches[-1]))


def verify_outputs():
    expected = {'HEADLESS-1': (0, 0, 800, 600),
                'HEADLESS-2': (0, 600, 800, 600) if geometry == 'vertical'
                else (800, 0, 800, 600)}
    actual = {}
    data = ipc('-t', 'get_outputs')
    (run / 'outputs-verified.json').write_text(json.dumps(data, indent=2))
    for output in data:
        if output.get('name') in expected and output.get('active'):
            rect = output['rect']
            if output.get('scale') != 1.0 or output.get('transform') != 'normal':
                raise RuntimeError(f'unexpected output scale/transform: {output}')
            actual[output['name']] = (rect['x'], rect['y'], rect['width'], rect['height'])
    if actual != expected:
        raise RuntimeError(f'output geometry mismatch: {actual} != {expected}')
    return expected


def capture(tag):
    (run / f'tree-{tag}.json').write_text(json.dumps(tree(), indent=2))
    (run / f'outputs-{tag}.json').write_text(json.dumps(ipc('-t', 'get_outputs'), indent=2))
    for output, label in (('HEADLESS-1', 'left'), ('HEADLESS-2', 'right')):
        subprocess.run(['grim', '-o', output, str(run / f'{label}-{tag}.png')],
                       env=env, check=True, timeout=8, stdout=subprocess.DEVNULL)


def inject(action, x, y):
    if int(x) != x or int(y) != y:
        raise ValueError(f'nonintegral pointer request: {x},{y}')
    x, y = int(x), int(y)
    if not (0 <= x < extent[0] and 0 <= y < extent[1]):
        raise ValueError(f'pointer request outside {extent}: {x},{y}')
    marker = f'INJECT_DONE {action} {x},{y}'
    pointer.stdin.write(f'{action} {x} {y}\n')
    pointer.stdin.flush()
    wait(lambda: marker in (run / 'pointer.log').read_text())


def command(value):
    client.stdin.write(value + '\n')
    client.stdin.flush()
    wait(lambda: f'COMMAND {value}' in (run / 'client.log').read_text())


compositor_log = (run / 'compositor.log').open('w')
files.append(compositor_log)
compositor = None
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
    verify_outputs()
    extent = (800, 1200) if geometry == 'vertical' else (1600, 600)
    pointer = spawn([str(LAB / 'pointer-daemon'), *map(str, extent)], 'pointer.log',
                    stdin=subprocess.PIPE)
    wait(lambda: 'POINTER_READY' in (run / 'pointer.log').read_text())
    ipc('workspace 1')
    ipc('layout mosaic' if case == 'private_mosaic' else 'layout splith')
    spawn(['kitty', '--class', 'A', '-o', 'background=#aa2222',
           '/usr/bin/sleep', '90'], 'A.log')
    wait(lambda: len(ws()['nodes']) >= 1)
    client = spawn([str(LAB / 'nested-client'), placement], 'client.log',
                   debug=True, stdin=subprocess.PIPE)
    wait(lambda: owner() and logged('TOPLEVEL MAP'))
    for label in ('C', 'D'):
        spawn(['kitty', '--class', label, '/usr/bin/sleep', '90'], label + '.log')
        time.sleep(.35)
    ipc('workspace 2')
    spawn(['stdbuf', '-oL', 'wev'], 'wev.log')
    ordinary = wait(lambda: find(tree(), lambda n: n.get('app_id') == 'wev'))
    ordinary_rect = ordinary['rect']
    ipc('workspace 1')
    ipc('[app_id="org.mosaic.NestedGrabProbe"] focus')
    if case == 'private_mosaic':
        current = ws()['mosaic']['rows'][0]['scroll_x']
        ipc(f'layout mosaic scroll {400-current:g}')
    time.sleep(.4)
    o = owner()
    scroll = ws()['mosaic']['rows'][0]['scroll_x'] if case == 'private_mosaic' else 0
    # CONTRACT: IPC rect is logical in Mosaic; the applied content origin
    # includes camera translation and the container's window rectangle.
    rendered_x = o['rect']['x'] - scroll + o['window_rect']['x']
    rendered_y = o['rect']['y'] + o['window_rect']['y']
    top_x = int(max(40, min(760, rendered_x + 100)))
    inject('left', top_x, 150)
    wait(lambda: logged('POPUP_A MAP'))
    a_cfg = configured('POPUP_A')
    a_x = int(max(40, min(760, rendered_x + a_cfg[0] + 40)))
    a_y = int(min(585, rendered_y + a_cfg[1] + 35))
    inject('left', a_x, a_y)
    wait(lambda: logged('POPUP_B MAP'))
    b_cfg = configured('POPUP_B')
    time.sleep(.3)
    capture('open')
    a_global = (rendered_x + a_cfg[0], rendered_y + a_cfg[1], a_cfg[2], a_cfg[3])
    b_global = (a_global[0] + b_cfg[0], a_global[1] + b_cfg[1], b_cfg[2], b_cfg[3])
    boundary = 600 if geometry == 'vertical' else 800
    crossing = (b_global[1] < boundary < b_global[1] + b_global[3]
                if geometry == 'vertical' else
                b_global[0] < boundary < b_global[0] + b_global[2])
    measurements = {'geometry': geometry, 'case': case, 'scenario': scenario,
                    'requested_extent': extent, 'owner_id': o['id'],
                    'owner_rect': o['rect'], 'owner_window_rect': o['window_rect'],
                    'scroll_x': scroll, 'ordinary_rect': ordinary_rect,
                    'popup_a_configure': a_cfg, 'popup_b_configure': b_cfg,
                    'popup_a_global_estimate': a_global,
                    'popup_b_global_estimate': b_global,
                    'crossing_estimate': crossing, 'sample_points': []}
    (run / 'measurements.json').write_text(json.dumps(measurements, indent=2))
    print('CHAIN_OPEN', case, scenario, placement, 'owner_id', o['id'],
          'owner_rect', o['rect'], 'scroll', scroll,
          'top_click', (top_x, 150), 'a_click', (a_x, a_y),
          'a_configure', a_cfg, 'b_configure', b_cfg,
          'a_global_estimate', a_global, 'b_global_estimate', b_global,
          'crossing_estimate', crossing,
          'client_alive', client.poll() is None, flush=True)
    if scenario == 'visible':
        # A and B receive separate right clicks without dismissing the grab.
        inject('right', min(760, a_global[0] + a_global[2] - 8), a_global[1] + 20)
        inject('right', min(760, b_global[0] + 40), b_global[1] + 30)
        time.sleep(.2)
        capture('visible-clicks')
    elif scenario in ('b_cross', 'both_cross', 'below_left', 'below_right', 'below_a'):
        if geometry == 'vertical':
            if not crossing:
                print('INCONCLUSIVE no configured B crossing', flush=True)
                actions = []
            else:
                upper_b_y = min(590, b_global[1] + 20)
                # WHY: the destination client starts below its workspace
                # decoration; a point just below y=600 can miss wev entirely.
                below_y = int(max(boundary + 4, ordinary_rect['y'] + 15))
                below_x = int(min(790, a_global[0] + 8 if scenario == 'below_a'
                                  else b_global[0] + 40))
                target_bottom = (a_global[1] + a_global[3] if scenario == 'below_a'
                                 else b_global[1] + b_global[3])
                if below_y >= target_bottom or not (
                        ordinary_rect['x'] <= below_x < ordinary_rect['x'] + ordinary_rect['width']):
                    print('INCONCLUSIVE no popup-covered point inside wev', ordinary_rect,
                          a_global, b_global, flush=True)
                    actions = []
                else:
                    upper_x = int(min(790, b_global[0] + 40))
                    actions = [('move', upper_x, upper_b_y),
                               ('right', upper_x, upper_b_y),
                               ('move', below_x, below_y)]
                    if scenario in ('both_cross', 'below_a'):
                        actions.insert(0, ('right', int(a_global[0] + a_global[2] - 8),
                                           min(585, int(a_global[1] + 20))))
                    actions.append(('left' if scenario == 'below_left' else 'right', below_x, below_y))
                    print('BOUNDARY_POINT', below_x, below_y, 'upper_B', upper_b_y,
                          'ordinary_rect', ordinary_rect, flush=True)
                    measurements['sample_points'].extend(
                        [{'purpose': 'visible_popup_b', 'global': [upper_x, upper_b_y]},
                         {'purpose': 'lower_popup_a' if scenario == 'below_a'
                          else 'lower_popup_b', 'global': [below_x, below_y]}])
                    (run / 'measurements.json').write_text(json.dumps(measurements, indent=2))
        else:
            actions = [('move', 700, 190), ('right', 700, 190),
                       ('move', 900, 190), ('right', 900, 190)]
            measurements['sample_points'].extend(
                [{'purpose': 'historical_visible_popup_b', 'global': [700, 190]},
                 {'purpose': 'historical_clipped_popup_b', 'global': [900, 190]}])
            (run / 'measurements.json').write_text(json.dumps(measurements, indent=2))
        for action, x, y in actions:
            inject(action, x, y)
            time.sleep(.2)
            capture(f'{action}-{x}-{y}')
    elif scenario in ('hidden', 'hidden_click'):
        assert case == 'private_mosaic'
        ipc('layout mosaic scroll 880')
        time.sleep(.5)
        capture('hidden')
        print('HIDDEN_STATE', ws()['mosaic'], 'owner_id', owner()['id'],
              'a_done', logged('POPUP_A POPUP_DONE'),
              'b_done', logged('POPUP_B POPUP_DONE'), flush=True)
        inject('move', 100, 190)
        time.sleep(.2)
        capture('hidden-hover')
        if scenario == 'hidden_click':
            inject('right', 100, 190)
            time.sleep(.2)
            capture('hidden-click')
        ipc('layout mosaic scroll -880')
        time.sleep(.4)
        capture('returned')
    elif scenario == 'owner':
        ipc(f'[con_id={o["id"]}] kill')
        time.sleep(.4)
        capture('owner-destroyed')
    elif scenario == 'toggle':
        assert case == 'private_mosaic'
        ipc('layout splith')
        time.sleep(.4)
        capture('standard')
        standard_owner = owner()
        standard_top_x = standard_owner['rect']['x'] + standard_owner['window_rect']['x']
        standard_top_y = standard_owner['rect']['y'] + standard_owner['window_rect']['y']
        toggle_x = int(min(790, standard_top_x + a_cfg[0] + b_cfg[0] + 40))
        toggle_y = int(min(1150, max(640, standard_top_y + a_cfg[1] + b_cfg[1] + 40)))
        print('STANDARD_RETURN_POINT', toggle_x, toggle_y,
              'owner_rect', standard_owner['rect'], flush=True)
        measurements['standard_owner_rect'] = standard_owner['rect']
        measurements['sample_points'].append(
            {'purpose': 'standard_popup_b', 'global': [toggle_x, toggle_y]})
        (run / 'measurements.json').write_text(json.dumps(measurements, indent=2))
        inject('right', toggle_x, toggle_y)
        time.sleep(.2)
        capture('standard-click')
    print('FINAL', 'a_done', logged('POPUP_A POPUP_DONE'),
          'b_done', logged('POPUP_B POPUP_DONE'),
          'client_alive', client.poll() is None, flush=True)
finally:
    for child in children:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
    if compositor is not None and compositor.poll() is None:
        os.killpg(compositor.pid, signal.SIGTERM)
    # CONTRACT: only process groups started by this runner are terminated.
    # Reap them before removing their private socket directory.
    for proc in [*children, *([compositor] if compositor is not None else [])]:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5)
    (run / 'exit-status.json').write_text(json.dumps({
        'compositor': None if compositor is None else compositor.returncode,
        'children': [{'argv': proc.args, 'returncode': proc.returncode}
                     for proc in children]}, indent=2))
    for file in files:
        file.close()
    shutil.rmtree(runtime)
