"""EXPERIMENTAL adapter; inherited bounded process/socket cleanup stays intact."""
import argparse
from pathlib import Path
import subprocess
import sys
from campaign import Campaign
from scenario import SCENARIO

p = argparse.ArgumentParser()
p.add_argument('lab', type=Path)
p.add_argument('mode', choices=('control', 'private_standard', 'private_mosaic'))
p.add_argument('--source-only', action='store_true',
               help='generate and syntax-check the child without reserving a run')
a = p.parse_args()
lab = a.lab.resolve()
repo = Path(__file__).resolve().parents[3]
# WHY: one lock covers all modes, rotations and complete child cleanup.
# CONTRACT: repeated/failed runs cannot silently replenish campaign budgets.
# INVARIANT: no dynamic action is launched before its persistent reservation.
if not a.source_only:
    campaign = Campaign(lab)
    campaign.begin(a.mode)
s = (repo / 'tooling/probes/step20c-applied-state-input/run.py').read_text()
s = s.replace("f'{args.mode}-{args.kind}-asi{args.asi_mode}-{time.time_ns()}'",
              "f'{args.mode}-rotated-{time.time_ns()}'")
s = s.replace('output HEADLESS-1 resolution 800x600 position -800 0',
              'output HEADLESS-1 resolution 1000x750 scale 1.25 position -800 0')
s = s.replace("Path('/usr/bin/sway')", "lab / 'standard-build/sway/sway'")
s = s.replace("    snapshot('startup')", "    time.sleep(1.0)\n    snapshot('startup')")
s = s.replace('import argparse', 'import argparse\nfrom PIL import Image, ImageDraw\nimport sys\nsys.path.insert(0, '+repr(str(Path(__file__).parent.resolve()))+')\nfrom campaign import reserve')
s = s.replace("run.mkdir(parents=True, mode=0o700)", """run.mkdir(parents=True, mode=0o700)
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
""")
s = s.replace('env = os.environ.copy()', "(run / 'config').write_text((run / 'config').read_text() + f'output * bg {marker_path} fill\\n')\nenv = os.environ.copy()", 1)
start = s.index("    expected = {'HEADLESS-1':")
end = s.index("    for output, side in", start)
s = s[:start]+'''    expected = {'HEADLESS-1': (-800, 0, 800, 600), 'HEADLESS-2': (0, 0, 800, 600)}
    actual = {o['name']: tuple(o['rect'][k] for k in ('x','y','width','height')) for o in outputs if o['active']}
    rotated = globals().get('rotation_stage') == 'R90'
    h1 = next(o for o in outputs if o['name'] == 'HEADLESS-1')
    h2 = next(o for o in outputs if o['name'] == 'HEADLESS-2')
    wanted_mode = (750, 1000) if rotated else (1000, 750)
    if (actual != expected or h1['scale'] != 1.25 or h2['scale'] != 1 or
            h2['transform'] != 'normal' or h1['transform'] != ('90' if rotated else 'normal') or
            (h1['current_mode']['width'], h1['current_mode']['height']) != wanted_mode):
        raise RuntimeError(f'applied rotation geometry gate failed: {actual} {h1}')
    record('state', tag=tag, workspaces=ipc('-t','get_workspaces'), workspace=workspace(), owner=owner(), outputs=outputs)
'''+s[end:]
s = s.replace("['grim', '-o', output, str(path)]", "['grim', '-s', str(next(o['scale'] for o in outputs if o['name']==output)), '-o', output, str(path)]")
s = s.replace("        record('capture', tag=tag", """        out = next(o for o in outputs if o['name']==output)
        dimensions = list(Image.open(path).size)
        record('capture_geometry',tag=tag,output=output,dimensions=dimensions,rect=out['rect'],scale=out['scale'],transform=out['transform'],mode=out['current_mode'], physical_expected=[out['current_mode']['width'],out['current_mode']['height']])
        record('capture', tag=tag""")
start=s.index('def inject(action, x, y):');end=s.index('\ndef client_command',start)
s=s[:start]+'''def inject(action, x, y):
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
    pointer.stdin.write(f'{action} {sent_x} {sent_y} {width} {height}\\n');pointer.stdin.flush()
    wait(lambda: (run/'pointer.log').read_text().count(marker)>before)

'''+s[end:]
start=s.index("    if args.kind == 'cycles':\n");end=s.index('except Exception as exc:',start)
scenario=SCENARIO
s=s[:start]+scenario+'\n'+s[end:]
generated=lab/f'rotated-{a.mode}.py'
generated.write_text(s)
if a.source_only:
    import ast
    ast.parse(s, filename=str(generated))
    print(f'SOURCE_ONLY_PASS={generated}')
    raise SystemExit(0)
raise SystemExit(subprocess.call([sys.executable,str(generated),str(lab),a.mode,'cycles','--max-seconds','360','--max-captures','120','--max-bytes','70000000'], pass_fds=(campaign.lock.fileno(),)))
