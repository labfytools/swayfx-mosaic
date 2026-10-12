"""EXPERIMENTAL scaling adapter; only private fixture code is generated."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument('lab', type=Path)
p.add_argument('mode', choices=('control', 'private_standard', 'private_mosaic'))
p.add_argument('geometry', choices=('G0', 'G1', 'G2', 'G3'))
p.add_argument('--camera-pairs', type=int, choices=(0, 1), default=0)
p.add_argument('--outside-y', type=int, choices=(140,190), default=190)
p.add_argument('--placement', choices=('b_cross', 'both_cross'), default='b_cross')
p.add_argument('--scenario', choices=('main', 'outside', 'calibration'), default='main')
a = p.parse_args()
lab = a.lab.resolve()
repo = Path(__file__).resolve().parents[3]
if a.camera_pairs and (a.mode != 'private_mosaic' or a.geometry not in ('G1', 'G2') or a.scenario != 'main'):
    p.error('pairs only in G1/G2 main Mosaic runs')
# WHY: repeat attempts must not create a new scientific budget.
# CONTRACT: single lab-wide ledger; failure/interruption consumes reservation.
# INVARIANT: hold exclusive lock through launch and child cleanup, never reset.
lock = (lab / 'fractional-campaign.lock').open('a')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
ledger = lab / 'fractional-camera-budget.json'
if not ledger.exists() and any((lab / 'runs').glob('*-fractional-*')):
    p.error('existing campaign has no ledger; refusing silent budget reset')
state = json.loads(ledger.read_text()) if ledger.exists() else {'consumed': 0, 'attempts': []}
if type(state['consumed']) is not int or not 0 <= state['consumed'] <= 2:
    p.error('invalid persisted budget')
if state['consumed'] != sum(t['reserved'] for t in state['attempts']):
    p.error('inconsistent persisted reservations')
if state['consumed'] + a.camera_pairs > 2:
    p.error('global two-pair budget exhausted')
state['consumed'] += a.camera_pairs
state['attempts'].append({'geometry': a.geometry, 'mode': a.mode, 'scenario': a.scenario, 'placement': a.placement, 'outside_y': a.outside_y, 'reserved': a.camera_pairs})
tmp = ledger.with_suffix('.tmp')
with tmp.open('w') as f:
    f.write(json.dumps(state, indent=2) + '\n'); f.flush(); os.fsync(f.fileno())
tmp.replace(ledger)
# CONTRACT: record all attempts including zero-pair controls before launch.
scales = {'G0': (1, 1), 'G1': (1.25, 1.25), 'G2': (1.25, 1), 'G3': (1.5, 1)}[a.geometry]
modes = [(int(800*s), int(600*s)) for s in scales]
pattern = Image.new('RGB', (64, 64))
for y in range(64):
    for x in range(64):
        pattern.putpixel((x, y), (245,245,245) if (x//8)%2 == 0 else (15,25,45))
pattern.save(lab / 'fx-checker.png')
s = (repo / 'tooling/probes/step20c-applied-state-input/run.py').read_text()
s = s.replace("'hidden_click', 'toggle'))", "'hidden_click', 'toggle', 'scale'))")
s = s.replace("f'{args.mode}-{args.kind}-asi{args.asi_mode}-{time.time_ns()}'", "f'{args.mode}-fractional-"+a.geometry+'-'+a.scenario+"-{time.time_ns()}'")
for i in (0,1):
    old = f'output HEADLESS-{i+1} resolution 800x600 position {(-800 if i==0 else 0)} 0'
    new = f'output HEADLESS-{i+1} resolution {modes[i][0]}x{modes[i][1]} scale {scales[i]} position {(-800 if i==0 else 0)} 0'
    assert old in s;s=s.replace(old,new)
s = s.replace("output.get('scale') != 1.0", "output.get('scale') != EXPECTED_SCALES[output['name']]")
s = s.replace("['grim', '-o', output, str(path)]", "['grim', '-s', str(EXPECTED_SCALES[output]), '-o', output, str(path)]")
# WHY: grim's default multi-output scale can differ from the target output.
# CONTRACT: request that output's scale, then assert PNG dimensions against mode.
s = s.replace("record('capture', tag=tag", """with Image.open(path) as png:
            dimensions = list(png.size)
        out = next(o for o in outputs if o['name'] == output)
        mode = out['current_mode']
        if dimensions != [mode['width'], mode['height']]:
            raise RuntimeError(f'capture/mode mismatch {dimensions} {mode}')
        record('capture_geometry', tag=tag, output=output, dimensions=dimensions,
               scale=out['scale'], transform=out['transform'], rect=out['rect'], mode=mode)
        record('capture', tag=tag""")
s = s.replace("'nested-client'), 'b_cross'", "'nested-client'), " + repr(a.placement))
s = s.replace("Path('/usr/bin/sway')", "lab / 'standard-build/sway/sway'")
s = s.replace("from pathlib import Path", "from pathlib import Path\nfrom PIL import Image\nEXPECTED_SCALES = " + repr(dict(zip(('HEADLESS-1','HEADLESS-2'),scales))))
scenario = r'''    if args.kind == 'scale':
        def wev_calibrate(proc, logname, node):
            # CONTRACT: logical enter infers origin; independent motion checks the delta.
            text = lambda: (run / logname).read_text()
            r, w = node['rect'], node['window_rect']
            origin = [r['x'], 300 if logname == 'wev-left.log' else 250]
            x, y = origin[0] + 20, origin[1] + 30
            inject('move', 790, 10)
            time.sleep(.05)
            before = len(text())
            inject('move', x, y)
            wait(lambda: re.search(r'enter:[^\n]*x, y: ([\d.]+), ([\d.]+)', text()[before:]))
            enter = re.findall(r'enter:[^\n]*x, y: ([\d.]+), ([\d.]+)', text()[before:])[-1]
            ex, ey = map(float, enter)
            if ex != 20 or not 0 <= ey < 100:
                raise RuntimeError(f'calibration enter out of expected interior: {enter}')
            applied_origin = [x-ex, y-ey]
            before = len(text())
            inject('move', x+40, y+20)
            wait(lambda: f'x, y: {ex+40:.6f}, {ey+20:.6f}' in text()[before:])
            for button in ('left', 'right'):
                inject(button, x+40, y+20)
            wait(lambda: 'button: 272' in text() and 'button: 273' in text())
            record('pointer_calibration', global_point=[x+40,y+20], local_expected=[ex+40,ey+20],
                   rect=r, content=w, requested_origin=origin, surface_origin=applied_origin, coordinate_source='client enter origin and independent motion delta', log=logname, passed=True)
        command('[app_id="wev"] floating enable')
        command('[app_id="wev"] border none')
        command('[app_id="wev"] move position 250 250')
        time.sleep(.3)
        ref = find(tree(), lambda n: n.get('app_id') == 'wev')
        wev_calibrate(None, 'wev.log', ref)
        command('workspace 1')
        cal = spawn(['stdbuf','-oL','wev'], 'wev-left.log')
        wait(lambda: find(tree(), lambda n: n.get('app_id') == 'wev' and n['id'] != ref['id']))
        left = find(tree(), lambda n: n.get('app_id') == 'wev' and n['id'] != ref['id'])
        command(f"[con_id={left['id']}] floating enable")
        command(f"[con_id={left['id']}] border none")
        command(f"[con_id={left['id']}] move absolute position -750 300")
        time.sleep(.3)
        left = find(tree(), lambda n: n.get('id') == left['id'])
        wev_calibrate(cal, 'wev-left.log', left)
        # Cross the output boundary and return with both targets still alive.
        inject('move', 310,300); inject('move', -690,350)
        snapshot('S0-calibrated')
        command(f"[con_id={left['id']}] kill")
        cal.wait(timeout=8)
        command('workspace 1')
        command('[app_id="org.mosaic.NestedGrabProbe"] focus')
        if args.mode == 'private_mosaic': scroll(400)
        if SCENARIO != 'calibration':
            spawn(['swaybg','-i',str(lab/'fx-checker.png'),'-m','tile'], 'swaybg.log')
            command('gaps inner 24')
            if args.mode != 'private_mosaic':
                command('move right');command('move right')
            command('shadows disable');command('blur disable')
            command('shadow_blur_radius 16');command('shadow_offset 30 0')
            command('shadow_color #000000A0');command('blur_radius 5');command('blur_passes 3')
            time.sleep(.3);snapshot('FX0-off')
            command('shadows enable');time.sleep(.25);snapshot('FX1-shadow')
            command('shadows disable');command('blur enable')
            time.sleep(.25);snapshot('FX2-blur')
            command('shadows enable');time.sleep(.25);snapshot('FX4-combined')
            command('shadows disable');command('blur disable')
            time.sleep(.25);snapshot('S1-effects-off-reference')
            open_chain('scale')
            time.sleep(.25);snapshot('S2-chain-stable')
            # Predeclared logical edge grid: hover does not dismiss valid grabs.
            for x in (-2,-1,0,1,2,20):
                before = len(client_text())
                inject('move',x,190);time.sleep(.08)
                record('boundary_hover',global_point=[x,190],client_events=client_text()[before:])
            snapshot('S3-boundary')
            if SCENARIO == 'outside':
                before = len(re.findall(r'POINTER_BUTTON target=POPUP_[AB][^\n]*state=1',client_text()))
                inject('right',20,OUTSIDE_Y);time.sleep(.25)
                after = len(re.findall(r'POINTER_BUTTON target=POPUP_[AB][^\n]*state=1',client_text()))
                record('exterior_click',popup_buttons_before=before,popup_buttons_after=after,
                       done_a=count('POPUP_A POPUP_DONE'),done_b=count('POPUP_B POPUP_DONE'))
                snapshot('S2-exterior-click')
            else:
                for pair in range(CAMERA_PAIRS):
                    scroll(1280);time.sleep(.25);snapshot('S5-hidden')
                    inject('move',-700,190);time.sleep(.1)
                    scroll(400);time.sleep(.25);snapshot('S5-return')
                    record('camera_pair_complete',pair=pair+1)
                command('layout splith');time.sleep(.3);snapshot('S7-standard')
                o=owner();ac,bc=configured('POPUP_A'),configured('POPUP_B')
                bx=o['rect']['x']+o['window_rect']['x']+ac[0]+bc[0]+35
                by=o['rect']['y']+o['window_rect']['y']+ac[1]+bc[1]+30
                inject('move',bx,by);inject('right',bx,by);time.sleep(.1)
                record('standard_return_hit',global_point=[bx,by])
                snapshot('S7-standard-hit')
    elif args.kind == 'cycles':
'''
scenario=scenario.replace('OUTSIDE_Y',str(a.outside_y))
scenario=scenario.replace('SCENARIO',repr(a.scenario)).replace('CAMERA_PAIRS',str(a.camera_pairs))
assert s.count("    if args.kind == 'cycles':\n") == 1
s=s.replace("    if args.kind == 'cycles':\n",scenario)
s = s.replace("run.mkdir(parents=True, mode=0o700)", "run.mkdir(parents=True, mode=0o700)\n(run / 'fixture-source.py').write_text(Path(__file__).read_text())")
generated=lab/f'fractional-{a.geometry}-{a.mode}-{a.scenario}-attempt{len(state["attempts"])}.py';generated.write_text(s)
raise SystemExit(subprocess.call([sys.executable,str(generated),str(lab),a.mode,'scale','--max-seconds','120','--max-captures','50','--max-bytes','35000000']))
