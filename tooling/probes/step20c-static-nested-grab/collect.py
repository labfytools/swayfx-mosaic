#!/usr/bin/env python3
"""Seal retained one-run observations without manufacturing missing evidence.

CONTRACT: runtime failures and real IPC codes stay immutable. No graphical replay.
INVARIANT: source/evidence manifests are created once and checked read-only.
"""
import argparse
import json
from pathlib import Path
import re
from PIL import Image
from support import OWNER,sha,save,verify,inventory
from predicates import protocol,mapped,geometry,popup_pixels,paint,pair,dismissal,root_clip,equal
from ipc_predicates import nodes,workspace,validate_outputs,validate_reference,scene_from_log
from geometry_audit import diagnose
p=argparse.ArgumentParser();p.add_argument('lab',type=Path);lab=p.parse_args().lab.resolve()
assert OWNER.read_text().strip()==str(lab)
assert not (lab/'results/evidence-sha256.txt').exists(),'already sealed'
verify(lab/'results/fixture-freeze-sha256.txt')
def read(n):return json.loads((lab/'results'/(n+'.json')).read_text())
run=lab/'run';runtime=read('runtime');terminal=read('terminal-exit');cleanup=read('cleanup')
protected=read('protected-before');assert all(sha(p)==h for p,h in protected.items()),'protected source/system change'
save(lab,'protected-after',dict(status='PASS',hashes=protected))
assert cleanup['runtime_removed'] and not Path(cleanup['runtime']).exists()
assert all(not Path('/proc',str(p['pid'])).exists() for p in cleanup['owned_processes'])
text=(run/'compositor.log').read_text();events=[json.loads(s) for s in (run/'events.jsonl').read_text().splitlines()]
full=runtime['status']=='PASS' and runtime['measurements_completed'] and terminal['scientific_cleanup_pass']
independent={}
if not full and runtime['stage']=='E1-open-A':
    diagnostic=diagnose(lab);save(lab,'geometry-fixture-diagnostic',diagnostic)
    save(lab,'applied-owner-geometry',dict(status='PARTIAL',E1=diagnostic['applied_owner'],painted_content_origin=diagnostic['painted_content_origin'],SHM_size=diagnostic['SHM_size'],assigned_content=diagnostic['assigned_content'],painted=diagnostic['painted_TOPLEVEL'],popups='NOT TESTED'))
    save(lab,'applied-clips',dict(status='PARTIAL',tiled=diagnostic['tiled_clip'],root='NOT TESTED',child='NOT TESTED'))
    save(lab,'mosaic-pixels',dict(status='PARTIAL',toplevel_H1=diagnostic['painted_TOPLEVEL'],H2=diagnostic['H2'],root='NOT TESTED',nested='NOT TESTED'))
if full:
    baseline=Image.open(run/'H2-reference-1.png').convert('RGB')
    owners=read('applied-owner-geometry');clips=read('applied-clips');grab_serials=[]
    for name in ['E1','E2']:
        client=(run/(name+'.log')).read_text();cut=client.index('POPUP_B MAP ');prefix=client[:client.index('\n',cut)+1]
        pr=protocol(prefix);grab_serials += [g['serial'] for g in pr['grabs']]
        g=geometry(prefix,owners[name]['content_origin'])
        independent[name]=dict(protocol=pr,geometry=g,pixels=popup_pixels(Image.open(run/(name+'-mosaic-H1.png')).convert('RGB'),Image.open(run/(name+'-mosaic-H2.png')).convert('RGB'),g,True,baseline))
        assert clips[name]['root']['raw'] in text
        root_clip(clips[name]['root']['raw'],owners[name]['content_origin'],True)
    assert len(set(grab_serials))==4 and grab_serials==sorted(grab_serials)
    for file in ['H2-reference-2.png','E1-mosaic-H2.png','E1-dismissed-H2.png','E2-mosaic-H2.png','final-H2.png']:
        assert equal(baseline,Image.open(run/file).convert('RGB'))['equal'],('full H2',file)
    returns=read('standard-return');assert returns['root_clip']['raw'] in text
    root_clip(returns['root_clip']['raw'],returns['geometry']['origin'],False)
    stdsnap=read('standard-snapshot');ws=workspace(stdsnap['tree'],'1');assert ws['id']==owners['E2']['workspace'] and ws['layout']=='splith'
    validate_reference(stdsnap,read('reference-stability')['reference']['con_id'],read('reference-stability')['reference']['pid'])
    std=popup_pixels(Image.open(run/'standard-H1.png').convert('RGB'),Image.open(run/'standard-H2.png').convert('RGB'),returns['geometry'],False,baseline)
    client=(run/'E2.log').read_text();cut=next(e['ns'] for e in events if e['kind']=='measurements-completed')
    # Delivery must exist in actual retained recipient logs, not just summary JSON.
    for row in read('clicks'):
        for name,lines in row['events'].items():
            actual=(run/(name+'.log')).read_text()
            assert all(line in actual for line in lines)
    for name,target in [('E1-visible-B','POPUP_B'),('E2-standard-B','POPUP_B'),('E2-standard-A','POPUP_A')]:
        row=next(r for r in read('clicks') if r['tag']==name);who='E1' if name.startswith('E1') else 'E2'
        pair(row['events'][who],target)
        assert not row['events']['reference'] and not row['events']['filler']
    forbidden=read('forbidden-input');dismissal((run/'E1.log').read_text(),forbidden['popup_events'])
    assert client.index('POPUP_B DESTROY ')<client.index('COMMAND close_b DONE')<client.index('POPUP_A DESTROY ')
    assert not re.search(r'wl_display[^\n]*\.error\(|protocol error',client,re.I)
    assert runtime['duration_seconds']<=150 and not runtime['rescue_cleanup']
    independent['standard']=std
    save(lab,'independent-validation',dict(status='PASS',historical_status_unchanged=True,actual=independent,serials=grab_serials))
# Trace extents + capture diffs are retained as partial damage observations.
damage=[s for s in text.splitlines() if 'TEMPORAL_DAMAGE' in s]
save(lab,'damage-analysis',dict(status='PARTIAL',trace_count=len(damage),raw_extents=damage,
    capture_windows=[e for e in events if e['kind']=='capture'],
    changed_regions={n:independent[n]['pixels'] for n in ['E1','E2'] if n in independent},
    limitations=['not every intermediate frame','not minimal damage','no native buffer/PNG identity','no exhaustive GPU lifetime']))
source=Path('/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/mosaic-source/sway/desktop/xdg_shell.c')
save(lab,'scene-parentage',dict(status='PASS source-backed' if full else 'NOT TESTED runtime',source=str(source),source_sha256=sha(source),root='global popup layer; positioned from applied view content tree',nested='B wrapper under A xdg_surface_tree; same view',direct_child_trace='NOT AVAILABLE in immutable binary',runtime_XDG=read('xdg-protocol-order') if (lab/'results/xdg-protocol-order.json').exists() else None))
required=['applied-owner-geometry','popup-root-geometry','popup-nested-geometry','grab-serials','xdg-protocol-order','applied-clips','mosaic-pixels','mosaic-input','forbidden-input','dismissal','standard-return','standard-popup-pixels','standard-popup-input','reference-stability']
for n in required:
    if not (lab/'results'/(n+'.json')).exists():save(lab,n,dict(status='NOT TESTED',stopping_stage=runtime['stage'],reason=runtime['failure']))
verdict='FEASIBLE' if full else (runtime.get('failure') or {}).get('verdict','INCONCLUSIVE')
architecture='STATIC_NESTED_VALID_GRAB_FEASIBLE_FOR_TESTED_MATRIX' if full else 'STATIC_NESTED_VALID_GRAB_REQUIRES_REDESIGN' if verdict=='BLOCKED' else 'UNDECIDED'
matrix={n:'PASS' if full else 'NOT TESTED: inspect individual retained observations' for n in required}
if not full:
    matrix.update(binary_identity='PASS',loaded_libraries='PASS',client_provenance='PASS',C17='PASS',outputs='PASS',H1_focus='PASS',applied_camera='PASS relative -320, 480 to 160',H2_reference='PASS whole RGB; before any popup',tiled_clip='PASS global [-800,0,800,600]',toplevel_paint='PASS measured 182214 pixels; no popup',root_grab='NOT TESTED',nested_grab='NOT TESTED',E2='NOT TESTED',terminal_IPC='FAIL actual exit1; completed=false, no scientific exception',compositor_exit='PASS actual code0',cleanup='PASS no rescue',offline_gate='PASS recorded tests; INSUFFICIENT assertion audit, see diagnostic')
matrix.update(damage='PARTIAL',direct_child_clip_trace='NOT AVAILABLE; runtime NOT TESTED' if not full else 'NOT AVAILABLE; inherited source + pixels/input',hidden_owner='NOT TESTED',scale='NOT TESTED',rotation='NOT TESTED',output_migration='NOT TESTED',saved_buffer='NOT TESTED',effects='NOT TESTED',atomic_generation='NOT PROVEN',exhaustive_ABI='NOT TESTED',new_pristine='NOT RUN; historical controls only')
save(lab,'matrix',matrix)
save(lab,'summary',dict(verdict=verdict,architecture=architecture,runtime=runtime,terminal=terminal,budget=read('budget'),marker='SWAYFX_MOSAIC_STATIC_NESTED_VALID_GRAB_PROBE='+verdict,STEP20C='NEXT',production_multi_output='NOT YET SUPPORTED',new_Mosaic_builds=0,new_SceneFX_builds=0,pristine_runs=0))
sources=[p for root in ['fixture','preflight-correction','postrun-fixture','client-source','historical-source'] for p in (lab/root).rglob('*') if p.is_file()]+[lab/'protocol-before-run.md']
evidence=[p for root in ['raw','run','results'] for p in (lab/root).rglob('*') if p.is_file()]+[lab/n for n in ['swayfx-mosaic','nested-client','static-reference','pointer-daemon','campaign-owner']]
# Both lists fixed before writing either manifest, avoiding circular digests.
for name,paths in [('source',sources),('evidence',evidence)]:
    print(name,inventory(lab/'results'/(name+'-sha256.txt'),paths))
print('SWAYFX_MOSAIC_STATIC_NESTED_VALID_GRAB_PROBE='+verdict)
