#!/usr/bin/env python3
"""Offline collection of the single stopped run; never creates runtime evidence.

WHY: an IPC metadata predicate is not a pixel or input failure.
CONTRACT: retain the executed runner unchanged and label unexercised cells.
INVARIANT: seal once; --verify never rewrites results or manifests.
"""
import argparse, json, re, shutil
from pathlib import Path
from support import save, sha
p=argparse.ArgumentParser();p.add_argument('lab',type=Path);p.add_argument('--verify',action='store_true');a=p.parse_args();lab=a.lab.resolve()
assert (Path.home()/'swayfx-mosaic-static-followup-v1.owner').read_text().strip()==str(lab)
results=lab/'results'
if not a.verify:
    assert not (results/'evidence-sha256.txt').exists()
    runtime=json.loads((results/'runtime.json').read_text())
    snap=json.loads((results/'preflight-snapshot.json').read_text())
    def nodes(n):
        yield n
        for c in n.get('nodes',[])+n.get('floating_nodes',[]):yield from nodes(c)
    ns=list(nodes(snap['tree']))
    ref=next(n for n in ns if n.get('app_id')=='org.mosaic.StaticReference' and n['rect']['x']==0)
    target=next(n for n in ns if n.get('app_id')=='org.mosaic.SavedBufferProbe')
    filler=next(n for n in ns if n.get('app_id')=='org.mosaic.StaticReference' and n['id']!=ref['id'])
    assert ref['border']=='none' and ref['current_border_width']==2
    assert ref['deco_rect']==dict(x=0,y=0,width=0,height=0)
    assert ref['window_rect']==dict(x=0,y=0,width=800,height=600)
    assert filler['border']=='normal' and target['focused'] and not ref['focused']
    assert runtime['status']=='INCONCLUSIVE' and runtime['failure']=='AssertionError: '
    budget=json.loads((results/'budget.json').read_text())
    assert budget['used']==dict(run=1,capture=0,camera=1,visible_click=0,forbidden_click=0,standard_click=0,move=0)
    assert not list((lab/'run').glob('*.png')) and runtime['duration_seconds']<150
    for name in ['target','reference','filler']:
        text=(lab/'run'/(name+'.log')).read_text()
        assert not any(s.startswith('BUTTON ') for s in text.splitlines())
        assert 'error=0' in text
    for rec in runtime['process_exit_codes']:assert not Path('/proc',str(rec['pid'])).exists()
    assert not Path(runtime['runtime_removed']).exists()
    compositor=(lab/'run/compositor.log').read_text()
    owner=[s for s in compositor.splitlines() if 'PI_OWNER output=HEADLESS-1 ' in s and f' id={target["id"]} ' in s][-1]
    clips=[s for s in compositor.splitlines() if 'PI_SCENE output=' in s]
    save(lab,'fixture-incident',{'status':'CONFIRMED FIXTURE ERROR','failed_predicate':'reference current_border_width == 0','actual':ref,'filler':filler,'reason':'border none sets enum B_NONE without resetting stored thickness; IPC reports stored thickness even when rendered border is disabled','source_sites':['sway/commands/border.c:cmd_border','sway/ipc-json.c:ipc_json_describe_container','sway/desktop/transaction.c:arrange_container'],'runner_modified_after_run':False,'rerun':False})
    save(lab,'owner-geometry',{'status':'OBSERVED scene and IPC only','target':target,'scene_trace':owner,'client_commits':[s for s in (lab/'run/target.log').read_text().splitlines() if s.startswith('COMMIT ')],'painted_content':'NOT TESTED; no PNG','native_buffer_rectangle':'NOT ESTABLISHED'})
    save(lab,'clip-observations',{'status':'OBSERVED applied traces only','traces':clips,'pixel_validation':'NOT TESTED'})
    for name in ['reference-preflight','reference-pixel-analysis','permitted-pixels','forbidden-pixels','target-input','reference-input','standard-return']:
        save(lab,name,{'status':'NOT TESTED','reason':'run stopped at incorrect stored-border-width assertion before first capture or injection; no retry'})
    matrix={'binary_identity':'PASS','loaded_libraries':'PASS','output_geometry':'PASS','reference_border_mode':'PASS IPC none; stored thickness 2','reference_visible_pixels':'NOT TESTED','initial_focus':'PASS target/workspace 1','camera':'PASS calculated +160, applied 0 to 160','applied_clip':'OBSERVED global [-800,0,800,600]','H2_preflight':'NOT TESTED','H1_pixels':'NOT TESTED','H2_pixels':'NOT TESTED','whole_H2_RGB':'NOT TESTED','visible_click':'NOT TESTED','forbidden_click':'NOT TESTED','reference_delivery':'NOT TESTED','focus_RGB_stability':'NOT TESTED','splith_return':'NOT TESTED','clip_removal':'NOT TESTED','standard_click':'NOT TESTED','popups':'NOT TESTED','damage':'available setup extents only; no PNG or every-frame proof','cleanup':'PASS'}
    save(lab,'matrix',matrix)
    save(lab,'summary',{'verdict':'INCONCLUSIVE','architecture':'UNDECIDED','reason':'incorrect fixture interpretation of current_border_width under border none stopped the only run before RGB/input gates','budget':budget['used'],'builds':{'SceneFX':0,'Mosaic':0,'historical_clients_only':3},'STEP20C':'NEXT','production_multi_output':'NOT YET SUPPORTED','reruns':0,'new_labs':1})
    # Keep the executed fixture separate from the later offline collector.
    shutil.copytree(Path(__file__).parent,lab/'final-fixture')
    source=sorted(p for root in ['fixture','final-fixture','client-source'] for p in (lab/root).rglob('*') if p.is_file())
    evidence=sorted(p for root in ['raw','run','results'] for p in (lab/root).rglob('*') if p.is_file())
    evidence += [lab/name for name in ['swayfx-mosaic','saved-client','static-reference','pointer-daemon','campaign-owner']]
    for name,files in [('source',source),('evidence',evidence)]:
        with (results/(name+'-sha256.txt')).open('x') as out:
            for f in files:out.write(f'{sha(f)}  {f}\n')
for name in ['source','evidence']:
    manifest=results/(name+'-sha256.txt');lines=manifest.read_text().splitlines()
    for line in lines:
        digest,path=line.split('  ',1);assert sha(path)==digest,path
    print(name,len(lines),sha(manifest),'PASS')
