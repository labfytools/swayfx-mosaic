"""EXPERIMENTAL negative/positive-origin nested XDG grab runner.

Usage: python run.py LAB {control,private_standard,private_mosaic} SCENARIO GEOMETRY
SCENARIO: pointer, visible, b_cross, both_cross, a_cross, outside, hidden,
          hidden_click, toggle
GEOMETRY: negative, positive
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
assert scenario in ('pointer', 'visible', 'b_cross', 'both_cross', 'a_cross', 'outside',
                    'hidden', 'hidden_click', 'toggle')
assert geometry in ('negative', 'positive')
if scenario in ('hidden', 'hidden_click', 'toggle') and case != 'private_mosaic':
    raise SystemExit('this scenario requires private_mosaic')
assert LAB.is_dir() and (LAB / 'nested-client').is_file()
placement = ('visible' if scenario in ('pointer', 'visible', 'outside') else
             'both_cross' if scenario in ('both_cross', 'a_cross') else 'b_cross')
run = LAB / f'run-{geometry}-{case}-{scenario}'
run.mkdir(mode=0o700, exist_ok=False)
runtime = pathlib.Path(tempfile.mkdtemp(prefix='mno-', dir='/tmp'))
# WHY: keep both Unix socket names below sockaddr_un.sun_path even if LAB is
# long; the compositor derives its IPC path from XDG_RUNTIME_DIR.
if len(os.fsencode(str(runtime / 'sway-ipc.4294967295.2147483647.sock'))) >= 108:
    raise RuntimeError('private IPC socket path exceeds Linux sockaddr_un.sun_path')
(run / 'runtime-path').write_text(str(runtime) + '\n')
origin_x = -800 if geometry == 'negative' else 0
output2_x = origin_x + 800
output2 = f'output HEADLESS-2 resolution 800x600 position {output2_x} 0\n'
(run / 'config').write_text(
    f'output HEADLESS-1 resolution 800x600 position {origin_x} 0\n' + output2 +
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
    expected = {'HEADLESS-1': (origin_x, 0, 800, 600),
                'HEADLESS-2': (output2_x, 0, 800, 600)}
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
    """Convert a signed global point only after verifying layout bounds."""
    if not isinstance(x, int) or not isinstance(y, int):
        raise ValueError(f'nonintegral global pointer request: {x},{y}')
    if not (origin_x <= x < origin_x + extent[0] and 0 <= y < extent[1]):
        raise ValueError(f'global point outside verified layout: {x},{y}')
    normalized_x = x - origin_x
    output = 'HEADLESS-1' if x < output2_x else 'HEADLESS-2'
    local_x = x - (origin_x if output == 'HEADLESS-1' else output2_x)
    entry = {'action': action, 'global': [x, y],
             'layout_min': [origin_x, 0], 'sent': [normalized_x, y],
             'extent': list(extent), 'expected_output': output,
             'expected_output_local': [local_x, y]}
    injection_log.append(entry)
    (run / 'injections.json').write_text(json.dumps(injection_log, indent=2))
    marker = f'INJECT_DONE {action} {normalized_x},{y}'
    pointer.stdin.write(f'{action} {normalized_x} {y}\n')
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
    verified_outputs = verify_outputs()
    injection_log = []
    extent = (1600, 600)
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
    # CONTRACT: logical IPC X and camera displacement are distinct. A scene
    # log and sampled pixels must corroborate this applied-content estimate.
    rendered_x = o['rect']['x'] - scroll + o['window_rect']['x']
    rendered_y = o['rect']['y'] + o['window_rect']['y']
    top_x = int(max(origin_x + 40, min(output2_x - 40, rendered_x + 100)))
    right_x = int(max(output2_x + 30, ordinary_rect['x'] + 30))
    right_y = int(max(80, ordinary_rect['y'] + 30))
    calibration = [(top_x, 150), (right_x, right_y),
                   (top_x + 5, 160), (right_x + 5, right_y + 5)]
    for x, y in calibration:
        inject('move', x, y)
        time.sleep(.13)
    capture('pointer-reference')
    calibration_evidence = {'global_points': calibration,
        'owner_motion_lines': [line for line in (run / 'client.log').read_text().splitlines()
                               if ('POINTER_MOTION target=TOPLEVEL' in line or
                                   'POINTER_ENTER target=TOPLEVEL' in line)],
        'ordinary_motion_lines': [line for line in (run / 'wev.log').read_text().splitlines()
                                  if 'motion' in line.lower() or 'enter' in line.lower()]}
    (run / 'pointer-validation.json').write_text(json.dumps(calibration_evidence, indent=2))
    if len(calibration_evidence['owner_motion_lines']) < 2 or not calibration_evidence['ordinary_motion_lines']:
        raise RuntimeError('pointer calibration did not show motion on both clients')
    if scenario == 'pointer':
        for action, x, y in [('right', top_x, 150), ('left', right_x, right_y),
                             ('right', right_x + 5, right_y + 5),
                             ('left', top_x + 5, 160)]:
            inject(action, x, y)
            time.sleep(.2)
        capture('pointer-buttons')
        print('POINTER_REFERENCE', calibration_evidence, flush=True)
    else:
        inject('left', top_x, 150)
        wait(lambda: logged('POPUP_A MAP'))
        a_cfg = configured('POPUP_A')
        a_x = int(max(origin_x + 40, min(output2_x - 40, rendered_x + a_cfg[0] + 40)))
        a_y = int(min(585, rendered_y + a_cfg[1] + 35))
        inject('left', a_x, a_y)
        wait(lambda: logged('POPUP_B MAP'))
        b_cfg = configured('POPUP_B')
        time.sleep(.3)
        capture('open')
        a_global = (rendered_x + a_cfg[0], rendered_y + a_cfg[1], a_cfg[2], a_cfg[3])
        b_global = (a_global[0] + b_cfg[0], a_global[1] + b_cfg[1], b_cfg[2], b_cfg[3])
        a_cross = a_global[0] < output2_x < a_global[0] + a_global[2]
        b_cross = b_global[0] < output2_x < b_global[0] + b_global[2]
        measurements = {'geometry': geometry, 'case': case, 'scenario': scenario,
                        'verified_outputs': verified_outputs, 'layout_origin': [origin_x, 0],
                        'layout_extent': extent, 'owner_id': o['id'], 'owner_rect': o['rect'],
                        'owner_window_rect': o['window_rect'], 'rendered_content_estimate': [rendered_x, rendered_y],
                        'scroll_x': scroll, 'ordinary_rect': ordinary_rect,
                        'popup_a_configure': a_cfg, 'popup_b_configure': b_cfg,
                        'popup_a_global_estimate': a_global, 'popup_b_global_estimate': b_global,
                        'popup_a_crossing_estimate': a_cross, 'popup_b_crossing_estimate': b_cross,
                        'sample_points': []}
        def save():
            (run / 'measurements.json').write_text(json.dumps(measurements, indent=2))
        save()
        print('CHAIN_OPEN', case, scenario, placement, 'owner_id', o['id'],
              'owner_rect', o['rect'], 'scroll', scroll, 'a_configure', a_cfg,
              'b_configure', b_cfg, 'a_global', a_global, 'b_global', b_global,
              'a_cross', a_cross, 'b_cross', b_cross, flush=True)
        if scenario == 'visible':
            for purpose, rect in [('visible_a', a_global), ('visible_b', b_global)]:
                x = int(max(origin_x + 20, min(output2_x - 20, rect[0] + 20)))
                y = int(rect[1] + 20)
                measurements['sample_points'].append({'purpose': purpose, 'global': [x, y]})
                inject('right', x, y)
            capture('visible-clicks')
        elif scenario in ('b_cross', 'both_cross', 'a_cross'):
            if not b_cross or (scenario in ('both_cross', 'a_cross') and not a_cross):
                print('INCONCLUSIVE configured popup crossing absent', flush=True)
            else:
                left_b = (int(min(output2_x - 20, b_global[0] + 40)), int(b_global[1] + 30))
                right_b = (int(max(output2_x + 20, ordinary_rect['x'] + 15,
                                   b_global[0] + 20)), int(max(b_global[1] + 30,
                                   ordinary_rect['y'] + 15)))
                if not (b_global[0] <= left_b[0] < output2_x and
                        b_global[0] <= right_b[0] < b_global[0] + b_global[2] and
                        b_global[1] <= right_b[1] < b_global[1] + b_global[3] and
                        ordinary_rect['x'] <= right_b[0] < ordinary_rect['x'] + ordinary_rect['width']):
                    print('INCONCLUSIVE no verified popup/wev overlap', left_b, right_b, flush=True)
                else:
                    actions = []
                    if scenario in ('both_cross', 'a_cross'):
                        left_a = (int(a_global[0] + 20), int(a_global[1] + 20))
                        right_a = (int(max(output2_x + 10, a_global[0] + a_global[2] - 15)),
                                   int(a_global[1] + 20))
                        actions += [('right', *left_a, 'visible_a')]
                    actions += [('right', *left_b, 'visible_b')]
                    if scenario == 'a_cross':
                        actions += [('right', *right_a, 'crossing_a')]
                    else:
                        actions += [('right', *right_b, 'crossing_b')]
                    for action, x, y, purpose in actions:
                        measurements['sample_points'].append(
                            {'purpose': purpose, 'global': [x, y], 'action': action})
                        save()
                        inject(action, x, y)
                        time.sleep(.2)
                        capture(f'{purpose}-{action}')
        elif scenario == 'outside':
            outside = (int(max(output2_x + 30, ordinary_rect['x'] + 20)),
                       int(min(500, max(300, ordinary_rect['y'] + 200))))
            measurements['sample_points'].append({'purpose': 'outside_click', 'global': outside})
            save()
            inject('left', *outside)
            time.sleep(.2)
            capture('outside')
        elif scenario in ('hidden', 'hidden_click'):
            ipc('layout mosaic scroll 880')
            time.sleep(.5)
            capture('hidden')
            hidden_owner = owner()
            hidden_scroll = ws()['mosaic']['rows'][0]['scroll_x']
            hidden_x = hidden_owner['rect']['x'] - hidden_scroll + hidden_owner['window_rect']['x']
            measurements['hidden_owner_applied_estimate'] = [hidden_x,
                    hidden_owner['rect']['y'] + hidden_owner['window_rect']['y'],
                    hidden_owner['window_rect']['width'], hidden_owner['window_rect']['height']]
            measurements['hidden_scroll_x'] = hidden_scroll
            save()
            inject('move', origin_x + 100, 190)
            time.sleep(.2)
            capture('hidden-hover')
            if scenario == 'hidden_click':
                inject('right', origin_x + 100, 190)
                time.sleep(.2)
                capture('hidden-click')
            ipc('layout mosaic scroll -880')
            time.sleep(.4)
            capture('returned')
        elif scenario == 'toggle':
            ipc('layout splith')
            time.sleep(.4)
            capture('standard')
            standard_owner = owner()
            standard_top_x = standard_owner['rect']['x'] + standard_owner['window_rect']['x']
            standard_top_y = standard_owner['rect']['y'] + standard_owner['window_rect']['y']
            toggle_x = int(max(output2_x + 20,
                               standard_top_x + a_cfg[0] + b_cfg[0] + 20))
            toggle_y = int(standard_top_y + a_cfg[1] + b_cfg[1] + 30)
            measurements['standard_owner_rect'] = standard_owner['rect']
            measurements['sample_points'].append(
                {'purpose': 'standard_popup_b', 'global': [toggle_x, toggle_y]})
            save()
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
