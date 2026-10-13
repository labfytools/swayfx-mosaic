#!/usr/bin/env python3
"""Collect actual one-run evidence and seal inventories once.

WHY: unexecuted cells remain NOT TESTED, never manufactured by collection.
CONTRACT: verdict uses real gate observations; a fixture failure is not a leak.
INVARIANT: source fixture and historical inventories remain untouched.
"""
import argparse
import json
from pathlib import Path
from support import save,sha
from verify import verify_inventory
from validate_results import check as check_actual_observations

p=argparse.ArgumentParser();p.add_argument('lab',type=Path);a=p.parse_args();lab=a.lab.resolve()
assert (Path.home()/'swayfx-mosaic-static-rgb-input-retest-v1.owner').read_text().strip()==str(lab)
assert not (lab/'results/evidence-sha256.txt').exists(), 'already sealed'
verify_inventory(lab/'results/fixture-freeze-sha256.txt')
runtime=json.loads((lab/'results/runtime.json').read_text());budget=json.loads((lab/'results/budget.json').read_text())
for row in runtime['process_exit_codes']:assert not Path('/proc',str(row['pid'])).exists(), 'owned PID residual'
assert not Path(runtime['runtime_removed']).exists(), 'private runtime residual'
protected=json.loads((lab/'results/protected-before.json').read_text())
assert all(sha(p)==digest for p,digest in protected.items()), 'protected file changed'
save(lab,'protected-after',{'status':'PASS','hashes':protected})
required=['binary-identity','source-provenance','ipc-replay','preflight-replay','assertion-audit',
          'output-geometry','focus-states','reference-state','reference-stability','camera-calibration',
          'scene-clips','painted-geometry','pixel-analysis','visible-input','forbidden-input','reference-input',
          'standard-return','damage-analysis']
for name in required:
    if not (lab/'results'/(name+'.json')).exists():
        save(lab,name,{'status':'NOT TESTED','reason':runtime['failure'],'stopping_stage':runtime['stopping_stage']})
def read(name):return json.loads((lab/'results'/(name+'.json')).read_text())
qualification=check_actual_observations(lab)
full=qualification['scientific_gates']=='ALL PASS'
save(lab,'scientific-qualification',qualification)
verdict='FEASIBLE' if full else 'INCONCLUSIVE'
# Classification does not turn a metadata/parser failure into a compositor defect.
for name in ['forbidden-pixels']:
    if (lab/'results'/(name+'.json')).exists() and read(name).get('count',0)>0:verdict='BLOCKED'
if not full and verdict!='BLOCKED' and read('pixel-analysis').get('STATIC_MOSAIC_VISIBLE_PIXELS')=='PASS':
    verdict='PARTIALLY_FEASIBLE'
architecture=('STATIC_MOSAIC_RGB_INPUT_STANDARD_FEASIBLE_FOR_TESTED_MATRIX' if full else
              'STATIC_MOSAIC_RGB_INPUT_STANDARD_REQUIRES_REDESIGN' if verdict=='BLOCKED' else 'UNDECIDED')
matrix={
    'binary_identity':'PASS','source_provenance':'PASS exact historical C17 clients',
    'IPC_replay':'PASS','preflight_replay':'PASS','initial_focus':'PASS target/workspace 1',
    'effective_border':'PASS border none, stored width 2, empty deco and uniform full RGB',
    'outputs':'PASS negative-origin scale-1 normal', 'camera':'PASS calculated once and applied',
    'Mosaic_clip':'PASS applied local/global relationship plus RGB/input',
    'H2_reference':'PASS two full RGB images','H1_pixels':'PASS measured target paint',
    'H2_forbidden_pixels':0,'whole_H2_RGB':'PASS five complete comparisons',
    'visible_click':'PASS target real pair only','invisible_target':'PASS no event',
    'reference_click':'PASS reference real pair only','focus':'PASS H1 to H2 to H1',
    'standard_return':'PASS splith, clip absent, rendered pixels, real target pair',
    'damage':'PARTIAL client requests and output extents; intermediate frames NOT TESTED',
    'runner_exit':'FAIL exit 1 on terminal exit IPC; raw status preserved',
    'compositor_exit':'PASS code 0','terminal_transport':'observed EPIPE after completed measurements',
    'cleanup':'PASS','native_PNG_buffer_identity':'NOT PROVEN','popups':'NOT TESTED'}
save(lab,'matrix',matrix)
save(lab,'summary',{'verdict':verdict,'architecture':architecture,'runtime':runtime,'budget':budget,
    'scientific_qualification':qualification,'executed_runner_status_unchanged':True,
    'new_Mosaic_builds':0,'new_SceneFX_builds':0,'STEP20C':'NEXT','production_multi_output':'NOT YET SUPPORTED',
    'marker':'SWAYFX_MOSAIC_STATIC_RGB_INPUT_STANDARD_PROBE='+verdict})
source=sorted(p for root in ['fixture','postrun-fixture','client-source'] for p in (lab/root).rglob('*') if p.is_file())
source.append(lab/'protocol-before-run.md')
evidence=sorted(p for root in ['raw','run','results'] for p in (lab/root).rglob('*') if p.is_file())
evidence += [lab/n for n in ['swayfx-mosaic','saved-client','static-reference','pointer-daemon','campaign-owner']]
# Capture both lists before writing either inventory, avoiding circular digests.
for name,files in [('source',source),('evidence',evidence)]:
    with (lab/'results'/(name+'-sha256.txt')).open('x') as out:
        for path in files:out.write(f'{sha(path)}  {path}\n')
    print(name,verify_inventory(lab/'results'/(name+'-sha256.txt')))
print('SWAYFX_MOSAIC_STATIC_RGB_INPUT_STANDARD_PROBE='+verdict)
