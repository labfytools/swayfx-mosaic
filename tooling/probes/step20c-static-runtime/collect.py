#!/usr/bin/env python3
"""Recalculate bounded results from retained raw evidence, without new execution.

WHY: a fixture stop must not be upgraded to a demonstrated compositor defect.
CONTRACT: retain failed raw gates and explicit NOT TESTED downstream cells.
INVARIANT: never alter old results/manifests or refund experiment reservations.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
from PIL import Image,ImageChops
from support import REPO,save,sha
p=argparse.ArgumentParser();p.add_argument('lab',type=Path);a=p.parse_args();lab=a.lab.resolve()
assert not (lab/'results/evidence-sha256.txt').exists(),'sealed results are immutable'
run=lab/'run';text=(run/'compositor.log').read_text();runtime=json.loads((lab/'results/static-runtime.json').read_text())
rows=[]
for line in text.splitlines():
    m=re.search(r"binding file (.*?) \[0\] to (.*?) \[0\].*symbol `([^']+)'",line)
    if m and 'libwlroots' in m[1] and m[3].startswith('wlr_scene_'):
        row={'consumer':m[1],'provider':m[2],'symbol':m[3]}
        if row not in rows:rows.append(row)
binary=lab/'stage-static/usr/bin/swayfx-mosaic';own=[r for r in rows if r['provider']==str(binary)];wl=[r for r in rows if 'libwlroots' in r['provider']]
assert len(rows)==34 and len(own)==31 and len(wl)==3
expected={'wlr_scene_subsurface_tree_create','wlr_scene_surface_try_from_buffer','wlr_scene_surface_create'}
assert {r['symbol'] for r in wl}==expected
save(lab,'runtime-bindings',{'status':'PASS','records':rows,'executable':31,'wlroots':3,'historical_pattern':'same 31/3 suppliers; full semantic ABI still unproven'})
renderer=[s for s in text.splitlines() if re.search(r'\[render/fx_renderer/fx_renderer.c:\d+\].*(Using OpenGL|GL vendor:|GL renderer:)',s)]
save(lab,'renderer',{'observed':renderer,'requested_env':'WLR_RENDERER=pixman','actual':'SceneFX FX / OpenGL ES, AMD Radeon 780M; headless outputs, not pixman renderer'})
reference=Image.open(run/'h2-reference.png').convert('RGB');mosaic=Image.open(run/'h2-mosaic.png').convert('RGB');left=Image.open(run/'h1-mosaic.png').convert('RGB')
# This fixed interior matches the mapped reference's IPC client bounds. The
# comparison is supplemental evidence; it never replaces failed whole-H2 gate.
events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
trees=[e['result'] for e in events if e['kind']=='ipc' and e['args']==['-t','get_tree']]
def nodes(n):
    yield n
    for child in n.get('nodes',[])+n.get('floating_nodes',[]):yield from nodes(child)
refs=[n for n in nodes(trees[-1]) if n.get('app_id')=='org.mosaic.StaticReference' and n['rect']['x']>=0];assert len(refs)==1
ref=refs[0];rect=ref['rect'];win=ref['window_rect'];deco=ref['deco_rect']
# IPC rect/window_rect describe the standard reference content, while
# applied Mosaic target geometry is retained separately from scene traces.
x=rect['x']+win['x'];y=rect['y']+win['y'];box=(x,y,x+win['width'],y+win['height'])
assert 0<=box[0]<box[2]<=800 and 0<=box[1]<box[3]<=600
points=[(i%800,i//800,a,b) for i,(a,b) in enumerate(zip(reference.get_flattened_data(),mosaic.get_flattened_data())) if a!=b]
interior_equal=ImageChops.difference(reference.crop(box),mosaic.crop(box)).getbbox() is None
colors={(35,68,204),(32,208,160)}
mask=Image.new('L',left.size);mask.putdata([255 if v in colors else 0 for v in left.get_flattened_data()]);target_box=mask.getbbox()
save(lab,'pixel-reference-diagnostic',{'whole_H2_changed_pixels':len(points),'whole_H2_bbox':ImageChops.difference(reference,mosaic).getbbox(),'reference_IPC':ref,'measured_interior_box':box,'interior_equal':interior_equal,'all_differences_outside_interior':all(not(box[0]<=x<box[2] and box[1]<=y<box[3]) for x,y,_,_ in points),'color_changes':[{'before':a,'after':b,'count':c} for (a,b),c in Counter((a,b) for _,_,a,b in points).most_common(8)],'H1_target_color_bbox':target_box,'interpretation':'focus/decor changes supported by IPC and color changes; no whole-output PASS; no rerun'})
for name in ['input-analysis','popup-ownership','standard-layout']:
    if not (lab/'results'/(name+'.json')).exists():save(lab,name,{'status':'NOT TESTED','reason':'single run stopped at whole-H2 reference gate before downstream measurement'})
decisions=[{'id':'D1','decision':'private static SceneFX for immediate experimental STEP20C candidate'}, {'id':'D2','decision':'separate full notices for incorporated components in future private stage'}, {'id':'D3','decision':'project owns embedded SceneFX monitoring/review/rebuild/requalification; people and SLA unassigned'}, {'id':'D4','decision':'strict exact SceneFX/wlroots build pairs; stock updates independent; standard fallback'}]
save(lab,'decisions',{'date':'2026-10-13','authority':'explicit user ticket','decisions':decisions,'scope':'documentation/private prototypes; current package unchanged','production':'not authorized'})
save(lab,'security-maintenance-policy',{'responsible':'swayfx-mosaic project','individual_release_owner':None,'security_reviewer':None,'SLA':None,'required_before_public_distribution':'designate release maintainer and security reviewer','record':['SceneFX commit/provenance/checksums','ordered private patches','toolchain/options/dependencies','incorporated code/notices','qualified wlroots builds','tests','published binary hashes'],'monitor':['security fixes','renderer','shaders','dependencies','ABI','buffer lifetime','clipping','damage'],'workflow':['detect upstream changes/advisories','review relevance and exposure','review patch and clip interaction','rebuild','requalify pair','record evidence','separate publication decision'],'automatic_updates':False,'fallback':'ordinary SwayFX; never downgrade/replace system libraries for rollback'})
save(lab,'upstream-direction',{'direction':'SCENEFX_UPSTREAM_MAINTAINED_CLIP_API','historical_dossier':str(REPO/'docs/design/STEP20C_SCENEFX_STATIC_DISTRIBUTION_CONTRACT.md'),'static':'transitory experimental preference','maintained_API':['ownership','errors','bounds','lifetime','hit testing','damage','versioning'],'popup_ownership':'Mosaic specific','contact':False,'adoption':'not presumed'})
pair=json.loads((lab/'results/wlroots-qualified-pair.json').read_text());pair['qualification_scope']='build/model/stage/loader/headless startup and sampled tiled pixels; input/standard return unqualified';pair['required_after_update']=['identify exact pair','headers/symbols','shared layouts','rebuild','relocations','model tests','private stage/notices','authorized headless','relevant graphical paths','separate release decision'];save(lab,'wlroots-qualified-pair',pair)
# Legal/source closure is intentionally distinguished from successful file staging.
licenses=json.loads((lab/'results/license-inventory.json').read_text());licenses['status']='PARTIAL DISTRIBUTION QUALIFICATION; root/generated/source comments staged, exact archive extraction and final legal review remain open';save(lab,'license-inventory',licenses)
not_tested=['root valid grab popup','nested popup','measured clipped input','standard layout return','all-frame damage','vertical/scaled/rotated geometry','migration/resize','saved buffers/effects/optimized blur','atomic applied generation','other wlroots versions','bit reproducibility','install/upgrade/rollback','final legal compliance']
matrix={'build':'PASS','real_usr_prefix':'PASS','stage_with_notices':'PASS','ELF_and_relocations':'PASS','runtime_library_identity':'PASS','headless_startup_IPC_client_mapping':'PASS','static_clips_set_and_get':'OBSERVED','sampled_tiled_pixels':'retained H1 / zero target colors H2; reference interior identical','whole_H2_reference':'FAIL fixture gate; focus/decor mismatch','input':'NOT TESTED','standard_return':'NOT TESTED','runtime_scenario':runtime['status'],'other_cells':{x:'NOT TESTED' for x in not_tested}}
save(lab,'matrix',matrix)
save(lab,'summary',{'verdict':'PARTIALLY_FEASIBLE','architecture':'UNDECIDED','runtime_scenario':runtime['status'],'reason':'static build/stage/loader/headless function; reference fixture gate prevents input/standard return qualification; notice/security/full ABI gates remain','budget':json.loads((lab/'results/budget.json').read_text())['used'],'not_tested':not_tested,'reruns':0,'production':'NOT YET SUPPORTED','STEP20C':'NEXT'})
print('PARTIALLY_FEASIBLE; runtime scenario INCONCLUSIVE; bindings 31/3; H2 interior equal',interior_equal)
