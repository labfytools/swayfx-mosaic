"""EXPERIMENTAL applied-state/input headless campaign. See README."""
import argparse
from PIL import Image, ImageDraw
import sys
from budget import Budget
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

parser.add_argument('--cycles', type=int, default=3)
parser.add_argument('--asi-mode', type=int, choices=(0, 1, 2), default=0)
parser.add_argument('--test-hold', action='store_true')
parser.add_argument('--test-timeout', action='store_true')
parser.add_argument('--moves', type=int, default=18)
parser.add_argument('--max-seconds', type=int, default=120)
parser.add_argument('--max-captures', type=int, default=16)
parser.add_argument('--max-bytes', type=int, default=30_000_000)
args = parser.parse_args()
if not (1 <= args.max_seconds <= 120 and 1 <= args.max_captures <= 16 and
        1 <= args.max_bytes <= 30_000_000):
    parser.error('static R90 run bounds exceeded')
if not 1 <= args.cycles <= 30 or not 1 <= args.moves <= 40:
    parser.error('cycle/move bounds exceeded')

lab = args.lab.resolve()
if not (lab / 'nested-client').is_file():
    parser.error('prepared LAB required')
budget = Budget(lab)
budget.reserve(args.mode)
run = lab / 'runs' / f'{args.mode}-static-r90-{time.time_ns()}'
run.mkdir(parents=True, mode=0o700)
(run / 'fixture-source.py').write_text(Path(__file__).read_text())
# WHY: five asymmetric markers identify whether PNG uses logical or buffer axes.
# CONTRACT: predeclared logical centers and distinct exact RGB codes.
marker_path = run / 'marker.png'
marker = Image.new('RGB', (800, 600), (30, 30, 46))
draw = ImageDraw.Draw(marker)
for name, box, color in (
    ('TL', (15, 15, 44, 44), (255, 32, 32)),
    ('TR', (755, 15, 784, 44), (32, 255, 32)),
    ('BL', (15, 555, 44, 584), (32, 32, 255)),
    ('BR', (755, 555, 784, 584), (255, 255, 32)),
    ('C', (385, 285, 414, 314), (192, 32, 255))):
    draw.rectangle(box, fill=color)
marker.save(marker_path)

runtime = Path(tempfile.mkdtemp(prefix='mtd-', dir='/tmp'))
if len(os.fsencode(str(runtime / 'sway-ipc.4294967295.2147483647.sock'))) >= 108:
    raise RuntimeError('IPC socket path exceeds sockaddr_un')
(run / 'runtime-path').write_text(str(runtime) + '\n')
(run / 'config').write_text(
    'output HEADLESS-1 resolution 750x1000 scale 1.25 transform 90 position -800 0\n'
    'output HEADLESS-2 resolution 800x600 position 0 0\n'
    'workspace 1 output HEADLESS-1\nworkspace 2 output HEADLESS-2\n'
    'focus_follows_mouse no\n')
(run / 'config').write_text((run / 'config').read_text() + f'output * bg {marker_path} fill\n')
env = os.environ.copy()
env.update(XDG_RUNTIME_DIR=str(runtime), WLR_BACKENDS='headless',
           WLR_HEADLESS_OUTPUTS='2', WLR_RENDERER='pixman')
for key in ('SWAYSOCK', 'I3SOCK', 'WAYLAND_DISPLAY', 'LD_LIBRARY_PATH'):
    env.pop(key, None)
compositor_env = env.copy()
compositor_env['ASI_MODE'] = str(args.asi_mode)
if args.test_hold or args.test_timeout:
    compositor_env['ASI_TEST_HOLD_AFTER_PRESENT'] = '1'
readback_dir = None
if args.asi_mode:
    readback_dir = lab / 'buffers' / run.name
    readback_dir.mkdir(parents=True, mode=0o700)
    compositor_env['BI_OUTPUT_DIR'] = str(readback_dir)
(run / 'asi-mode.json').write_text(json.dumps({'mode': args.asi_mode,
    'readback_dir': str(readback_dir) if readback_dir else None}) + '\n')
binary = lab / 'standard-build/sway/sway' if args.mode == 'control' else lab / 'mosaic-build/sway/swayfx-mosaic'
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
    actual = {o['name']: tuple(o['rect'][k] for k in ('x','y','width','height')) for o in outputs if o['active']}
    rotated = True
    h1 = next(o for o in outputs if o['name'] == 'HEADLESS-1')
    h2 = next(o for o in outputs if o['name'] == 'HEADLESS-2')
    wanted_mode = (750, 1000) if rotated else (1000, 750)
    if (actual != expected or h1['scale'] != 1.25 or h2['scale'] != 1 or
            h2['transform'] != 'normal' or h1['transform'] != ('90' if rotated else 'normal') or
            (h1['current_mode']['width'], h1['current_mode']['height']) != wanted_mode):
        raise RuntimeError(f'applied rotation geometry gate failed: {actual} {h1}')
    record('state', tag=tag, workspaces=ipc('-t','get_workspaces'), workspace=workspace(), owner=owner(), outputs=outputs)
    for output, side in (('HEADLESS-1', 'left'), ('HEADLESS-2', 'right')):
        if capture_count >= args.max_captures:
            raise RuntimeError('capture count bound exceeded')
        path = run / f'{side}-{tag}.png'
        before = time.monotonic_ns()
        subprocess.run(['grim', '-s', str(next(o['scale'] for o in outputs if o['name']==output)), '-o', output, str(path)], env=env, check=True,
                       stdout=subprocess.DEVNULL, timeout=10)
        after = time.monotonic_ns()
        capture_count += 1
        capture_bytes += path.stat().st_size
        if capture_bytes > args.max_bytes:
            raise RuntimeError('capture byte bound exceeded')
        out = next(o for o in outputs if o['name']==output)
        dimensions = list(Image.open(path).size)
        record('capture_geometry',tag=tag,output=output,dimensions=dimensions,rect=out['rect'],scale=out['scale'],transform=out['transform'],mode=out['current_mode'], physical_expected=[out['current_mode']['width'],out['current_mode']['height']])
        record('capture', tag=tag, output=output, path=path.name,
               before_ns=before, after_ns=after, size=path.stat().st_size)


def inject(action, x, y):
    outputs = [o for o in ipc('-t','get_outputs') if o['active']]
    min_x = min(o['rect']['x'] for o in outputs)
    min_y = min(o['rect']['y'] for o in outputs)
    max_x = max(o['rect']['x']+o['rect']['width'] for o in outputs)
    max_y = max(o['rect']['y']+o['rect']['height'] for o in outputs)
    if not any(o['rect']['x']<=x<o['rect']['x']+o['rect']['width'] and o['rect']['y']<=y<o['rect']['y']+o['rect']['height'] for o in outputs):
        raise ValueError('global point is outside applied outputs')
    sent_x,sent_y = int(x-min_x),int(y-min_y)
    width,height = max_x-min_x,max_y-min_y
    marker=f'INJECT_DONE {action} {sent_x},{sent_y}'
    before=(run/'pointer.log').read_text().count(marker)
    record('pointer_request',action=action,global_point=[x,y],sent=[sent_x,sent_y],extent=[width,height],minimum=[min_x,min_y])
    pointer.stdin.write(f'{action} {sent_x} {sent_y} {width} {height}\n');pointer.stdin.flush()
    wait(lambda: (run/'pointer.log').read_text().count(marker)>before)


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
    if readback_dir:
        (readback_dir / 'enable').touch()
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
    time.sleep(1.0)
    snapshot('startup')
    pointer = spawn([str(lab / 'pointer-daemon'), '1600', '600'], 'pointer.log', stdin=True)
    wait(lambda: 'POINTER_READY' in (run / 'pointer.log').read_text())
    command('workspace 1')
    command('layout mosaic' if args.mode == 'private_mosaic' else 'layout splith')
    spawn(['kitty', '--class', 'A', '-o', 'cursor_blink_interval=0',
           '-o', 'background=#aa2222', '/usr/bin/sleep', '900'], 'A.log')
    wait(lambda: len(workspace()['nodes']) >= 1)
    client = spawn([str(lab / 'nested-client'), 'rot_cross'], 'client.log', stdin=True, debug=True)
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
        scroll(640)
        record('initial_camera', value=640)
    time.sleep(.25)
    # EXPERIMENTAL fragment inserted inside the inherited bounded runner's try.
    # WHY: persistence observations precede reference clicks that can dismiss grabs.
    # CONTRACT: four reserved dynamic actions per mode; no additional camera pair.
    dynamic_stage = 'D0'
    initial_ws_id = workspace()['id']
    initial_owner_id = owner()['id']
    ref_right = find(tree(), lambda n: n.get('app_id') == 'wev')['id']
    command('workspace 1')
    left_proc = spawn(['stdbuf','-oL','wev'], 'wev-left.log')
    wait(lambda: find(tree(), lambda n: n.get('app_id') == 'wev' and n['id'] != ref_right))
    ref_left = find(tree(), lambda n: n.get('app_id') == 'wev' and n['id'] != ref_right)['id']
    command('shadows disable'); command('blur disable')

    def closed():
        client_command('close_a')
        time.sleep(.12)

    def calibrate(tag):
        outputs = {o['name']: o for o in ipc('-t','get_outputs') if o['active']}
        active = {w['output']:w for w in ipc('-t','get_workspaces') if w['visible']}
        for out, con_id, logname in [('HEADLESS-1',ref_left,'wev-left.log'),('HEADLESS-2',ref_right,'wev.log')]:
            name = active[out]['name']
            command(f'[con_id={con_id}] move container to workspace {name}')
            command(f'[con_id={con_id}] floating enable')
            command(f'[con_id={con_id}] border none')
            command(f'[con_id={con_id}] resize set 200 150')
            ox=outputs[out]['rect']['x']+50; oy=400
            command(f'[con_id={con_id}] move absolute position {ox} {oy}')
            time.sleep(.25)
        # WHY: after return both references can temporarily share workspace 1.
        # CONTRACT: relocate BOTH before scoring input, avoiding mutual occlusion.
        for out, con_id, logname in [('HEADLESS-1',ref_left,'wev-left.log'),('HEADLESS-2',ref_right,'wev.log')]:
            ox=outputs[out]['rect']['x']+50; oy=400
            text=lambda: (run/logname).read_text()
            # Force a different surface, then accept actual enter or motion.
            inject('move', outputs['HEADLESS-2' if out=='HEADLESS-1' else 'HEADLESS-1']['rect']['x']+10,10)
            before=len(text());inject('move',ox+20,oy+30)
            pattern=r'(?:enter:[^\n]*|motion:[^\n]*)x, y: ([\d.]+), ([\d.]+)'
            wait(lambda: re.search(pattern,text()[before:]))
            ex,ey=map(float,re.findall(pattern,text()[before:])[-1])
            if ex != 20 or not 0 <= ey < 100:
                raise RuntimeError(f'calibration interior mismatch {tag} {out}: {ex},{ey}')
            before=len(text());inject('move',ox+60,oy+50)
            wait(lambda: f'x, y: {ex+40:.6f}, {ey+20:.6f}' in text()[before:])
            before=len(text())
            inject('left',ox+60,oy+50);inject('right',ox+60,oy+50)
            wait(lambda: 'button: 272' in text()[before:] and 'button: 273' in text()[before:])
            record('pointer_calibration',tag=tag,output=out,con_id=con_id,global_point=[ox+60,oy+50],local_expected=[ex+40,ey+20],surface_origin=[ox+20-ex,oy+30-ey],passed=True)
        for x in (-2,-1,0,1,2):inject('move',x,550)
        inject('move',outputs['HEADLESS-1']['rect']['x']+110,450)
        command('workspace 1')

    def stable(tag, expected_owner):
        # CONTRACT: repeated geometry and paired settled captures are evidence,
        # not proof that intermediate configurations each had a presentation.
        time.sleep(.35)
        before=ipc('-t','get_outputs')
        time.sleep(.12)
        after=ipc('-t','get_outputs')
        if before != after:
            raise RuntimeError(f'unstable output IPC at {tag}')
        ws=workspace();o=owner()
        current=next(w for w in ipc('-t','get_workspaces') if w['id']==initial_ws_id)
        if ws['id']!=initial_ws_id or o['id']!=initial_owner_id or current['output']!=expected_owner:
            raise RuntimeError(f'workspace/owner identity mismatch at {tag}')
        snapshot(tag)
        time.sleep(.16);snapshot(tag+'-repeat')
        record('identity',tag=tag,workspace_id=ws['id'],owner_id=o['id'],output=current['output'],layout=ws['layout'],order=[n['id'] for n in ws['nodes']],mosaic=ws.get('mosaic'),focused=current['focused'])

    def owner_hit(tag):
        o=owner();ws=workspace()
        scroll_x=ws['mosaic']['rows'][0]['scroll_x'] if args.mode=='private_mosaic' else 0
        point=[int(o['rect']['x']-scroll_x+o['window_rect']['x']+100),150]
        before=len(client_text());inject('move',*point);inject('right',*point)
        delivered='POINTER_BUTTON target=TOPLEVEL' in client_text()[before:]
        record('owner_hit',tag=tag,point=point,delivered=delivered,events=client_text()[before:])
        if not delivered:raise RuntimeError(f'visible owner input failed {tag}')


    # WHY: exact colors identify PNG orientation before interpreting output pixels.
    # CONTRACT: marker positions/colors were fixed before the first transition.
    colors = {'TL':(255,32,32),'TR':(32,255,32),'BL':(32,32,255),
              'BR':(255,255,32),'C':(192,32,255)}
    def marker_gate(tag, rotated):
        im = Image.open(run / f'left-{tag}.png').convert('RGB')
        points = {name: [] for name in colors}
        reverse = {v:k for k,v in colors.items()}
        for y in range(im.height):
            for x in range(im.width):
                name = reverse.get(im.getpixel((x,y)))
                if name: points[name].append((x,y))
        centers = {}
        for name, positions in points.items():
            if len(positions) < 100:
                raise RuntimeError(f'{tag}: marker {name} absent ({len(positions)})')
            centers[name] = [sum(p[0] for p in positions)/len(positions),
                             sum(p[1] for p in positions)/len(positions)]
        logical = (im.size == (1000,750) and
                   centers['TL'][0] < centers['TR'][0] and
                   centers['TL'][1] < centers['BL'][1])
        physical = (im.size == (750,1000) and
                    centers['TL'][0] > centers['BL'][0] and
                    centers['TL'][1] < centers['TR'][1])
        frame = 'logical-oriented PNG' if logical else 'physical-buffer-oriented PNG' if physical else 'unknown'
        record('marker_calibration', tag=tag, dimensions=list(im.size),
               centers=centers, counts={k:len(v) for k,v in points.items()},
               png_frame=frame)
        if (rotated and not (logical or physical)) or (not rotated and not logical):
            raise RuntimeError(f'{tag}: PNG frame not established')
        return frame

    # CONTRACT: static R90 from compositor startup; no transform command.
    marker_gate('startup', True)
    calibrate('static-R90')
    command('[app_id="org.mosaic.NestedGrabProbe"] focus')
    snapshot('reference')
    owner_hit('static-R90')
    open_chain('rot-cross')
    o=owner(); ws=workspace(); a_cfg=configured('POPUP_A'); b_cfg=configured('POPUP_B')
    sx=ws['mosaic']['rows'][0]['scroll_x'] if args.mode=='private_mosaic' else 0
    base_x=o['rect']['x']-sx+o['window_rect']['x']
    base_y=o['rect']['y']+o['window_rect']['y']
    a_box=[base_x+a_cfg[0],base_y+a_cfg[1],base_x+a_cfg[0]+a_cfg[2],base_y+a_cfg[1]+a_cfg[3]]
    b_box=[a_box[0]+b_cfg[0],a_box[1]+b_cfg[1],a_box[0]+b_cfg[0]+b_cfg[2],a_box[1]+b_cfg[1]+b_cfg[3]]
    record('applied_popup_geometry',owner_id=o['id'], owner_rect=o['rect'],window_rect=o['window_rect'],
           camera=sx,a_configure=a_cfg,b_configure=b_cfg,a_box=a_box,b_box=b_box,
           a_h1=[max(-800,a_box[0]),a_box[1],min(0,a_box[2]),a_box[3]],
           a_h2=[max(0,a_box[0]),a_box[1],min(800,a_box[2]),a_box[3]],
           b_h1=[max(-800,b_box[0]),b_box[1],min(0,b_box[2]),b_box[3]],
           b_h2=[max(0,b_box[0]),b_box[1],min(800,b_box[2]),b_box[3]])
    if not (b_box[0] < 0 < b_box[2] and b_box[2]>=16):
        record('geometry_gate',result='NOT EXERCISED',box=b_box)
    else:
        record('geometry_gate',result='CROSSING',box=b_box)
    # WHY: evaluate a shared y within B and scan both sides of the boundary.
    y=int((max(0,b_box[1])+min(600,b_box[3]))/2)
    for x in range(-3,4):
        before=len(client_text()); inject('move',x,y)
        record('border_hover',point=[x,y],client_events=client_text()[before:])
    inside_x=max(-30,int((max(-800,b_box[0])+min(0,b_box[2]))/2))
    before=len(client_text()); inject('move',inside_x,y); inject('right',inside_x,y)
    record('visible_b_button',point=[inside_x,y],client_events=client_text()[before:])
    snapshot('after-visible-button')
    # A left/right roles may dismiss on exterior click. Preserve it last.
    if b_box[2]>0:
        outside_x=min(30,int(b_box[2]/2))
        before=len(client_text()); inject('move',outside_x,y); inject('right',outside_x,y)
        record('forbidden_b_button',point=[outside_x,y],client_events=client_text()[before:])
    time.sleep(.15)
    snapshot('after-forbidden-button')

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
