"""Rotation scenario inserted into the inherited bounded runner try/finally."""
from pathlib import Path

# Reuse the published two-reference correction and real XDG-grab helpers.
# WHY: both references are positioned before either input calibration is scored.
# CONTRACT: the dynamic-output fixture source is read-only; no old campaign runs.
repo = Path(__file__).resolve().parents[3]
namespace = {}
exec((repo / 'tooling/probes/step20c-dynamic-output/scenario.py').read_text(), namespace)
PREFIX = namespace['SCENARIO'].split("    calibrate('D0')", 1)[0]
PREFIX = PREFIX.replace("    command('output * bg #1e1e2e solid_color')\n", '')

SCENARIO = PREFIX + r'''
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

    rotation_stage = 'R0'
    marker_gate('startup', False)
    calibrate('R0')
    command('[app_id="org.mosaic.NestedGrabProbe"] focus')
    stable('R0', 'HEADLESS-1'); owner_hit('R0')
    open_chain('R0-chain'); stable('R0-popups', 'HEADLESS-1')

    reserve(lab, args.mode, 'R90')
    record('dynamic_launch', action='R90',
           command='output HEADLESS-1 mode 750x1000 scale 1.25 transform 90 position -800 0')
    command('output HEADLESS-1 mode 750x1000 scale 1.25 transform 90 position -800 0')
    rotation_stage = 'R90'
    stable('R90-popups', 'HEADLESS-1')
    command('workspace 3')
    time.sleep(.5)
    snapshot('R90-marker')
    marker_gate('R90-marker', True)
    command('workspace 1')
    stable('R90-workspace-return', 'HEADLESS-1')
    closed(); calibrate('R90')
    command('[app_id="org.mosaic.NestedGrabProbe"] focus')
    owner_hit('R90')
    open_chain('R90-chain'); stable('R90-reopened', 'HEADLESS-1')

    if args.mode == 'private_mosaic':
        initial_camera = workspace()['mosaic']['rows'][0]['scroll_x']
        reserve(lab,args.mode,'camera_hide'); record('dynamic_launch',action='camera_hide')
        scroll(1280); stable('R90-hidden', 'HEADLESS-1')
        reserve(lab,args.mode,'camera_return'); record('dynamic_launch',action='camera_return')
        scroll(initial_camera); stable('R90-camera-return', 'HEADLESS-1')
        a = configured('POPUP_A'); b = configured('POPUP_B'); o = owner()
        sx = workspace()['mosaic']['rows'][0]['scroll_x']
        bx = int(o['rect']['x']-sx+o['window_rect']['x']+a[0]+b[0]+35)
        by = int(o['rect']['y']+o['window_rect']['y']+a[1]+b[1]+30)
        before = len(client_text())
        inject('move',bx,by); inject('right',bx,by)
        record('restored_popup_hit',point=[bx,by],
               delivered='POINTER_BUTTON target=POPUP_B' in client_text()[before:])

    reserve(lab,args.mode,'R0')
    record('dynamic_launch',action='R0',
           command='output HEADLESS-1 mode 1000x750 scale 1.25 transform normal position -800 0')
    command('output HEADLESS-1 mode 1000x750 scale 1.25 transform normal position -800 0')
    rotation_stage = 'R0'
    stable('R0-return', 'HEADLESS-1')
    if args.mode == 'private_mosaic':
        command('layout splith')
        stable('standard-return', 'HEADLESS-1')
'''
