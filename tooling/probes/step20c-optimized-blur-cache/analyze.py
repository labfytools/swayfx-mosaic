#!/usr/bin/env python3
"""Offline facts from immutable logs/PNGs; category evidence stays separate."""
import hashlib,json,re,sys
from pathlib import Path
import numpy as np
from PIL import Image
lab=Path(sys.argv[1]).resolve();out=lab/'results';fixture=Path(__file__).resolve().parent
ROIS={'glass':[520,100,720,500],'source':[20,100,160,500],'boundary':[720,50,800,550]}
def write(name,data):(out/(name+'.json')).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fields(line):return {k:v for k,v in re.findall(r'([A-Za-z_]+)=([^ ]+)',line)}
def parsed(lines,name):return [{'event':name,**fields(x),'raw':x} for x in lines if re.search(r'\b'+name+r'\b',x)]
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def diff(a,b):
 d=np.abs(a.astype(int)-b.astype(int));mask=np.any(d,axis=2);ys,xs=np.where(mask)
 return {'pixels':int(mask.sum()),'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if mask.any() else None,'max_channel':int(d.max()),'mean_abs_channel':float(d.mean())}
def roi(a,box):l,t,r,b=box;return a[t:b,l:r]
def comparisons(a,b):return {'whole':diff(a,b),**{n:diff(roi(a,box),roi(b,box)) for n,box in ROIS.items()}}
data={};renderers={};pixels={};contrast={};phases={};source={};lifetimes={};damage={};budgets={}
for mode in ['C0','C1','C2']:
 run=lab/'runs'/mode;status=json.loads((run/'exit-status.json').read_text());events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()];lines=(run/'compositor.log').read_text().splitlines()
 traces={name:parsed(lines,name) for name in ['OPT_NODE_CREATE','OPT_NODE_RENDER','OPT_DIRTY_SET','OPT_REGEN_ATTEMPT','OPT_REGEN_RESULT','OPT_DIRTY_CLEAR','OPT_CACHE_ALLOC','OPT_CACHE_STATE','OPT_CACHE_DESTROY','OPT_FBO_DESTROY','OPT_GPU_REBUILD','OPT_GPU_RESULT','OPT_GPU_COPY','OPT_GPU_COPY_DRAWN','OPT_BLUR_USE','OPT_REGULAR_NODE','OPT_BACKGROUND_COMMIT','OPT_BUFFER_DRAW','OPT_OUTPUT_BUFFER','TEMPORAL_DAMAGE','PI_OUTPUT_COMMIT','PI_OUTPUT_PRESENT','PI_SCENE','PI_OWNER']}
 data[mode]={'status':status,'events':events,'traces':traces}
 renderers[mode]={'gles':[x for x in lines if 'Using OpenGL' in x or 'GL renderer:' in x or 'GL vendor:' in x or 'EGL vendor:' in x],'loaded_libraries':[x for x in (run/'library-maps.txt').read_text().splitlines() if 'libscenefx' in x or 'libwlroots' in x],'FX_pass_observed':bool(traces['OPT_CACHE_STATE']),'native_control':mode!='C0'}
 cs=parsed((run/'background.log').read_text().splitlines(),'CLIENT_COMMIT');source[mode]={'client_commits':cs,'server_commits':traces['OPT_BACKGROUND_COMMIT'],'draws':traces['OPT_BUFFER_DRAW'],'layer_paths_valid':all(e['layer']=='0' and e['parent']==e['background'] and e['background_parent']==e['global_background'] and e['opt_parent']==e['blur_tree'] for e in traces['OPT_BACKGROUND_COMMIT'] if e['mapped']=='1') if traces['OPT_BACKGROUND_COMMIT'] else None,'pointer_identity_warning':'Buffer/resource IDs can be reused after release; phase, sequence and native lifetime delimit identity.'}
 lifetime=[]
 for allocation in traces['OPT_CACHE_ALLOC']:
  ns=int(allocation['ns']);cid=allocation['cache'];destroy=next((e for e in traces['OPT_CACHE_DESTROY'] if e['cache']==cid and int(e['ns'])>ns),None)
  states=[e for e in traces['OPT_CACHE_STATE'] if e['cache']==cid and int(e['ns'])>=ns and (not destroy or int(e['ns'])<int(destroy['ns']))]
  lifetime.append({'allocation':allocation,'destroy':destroy,'states':states,'distinct_blur_objects':sorted(set(e['blur'] for e in states)),'reuse_count':sum(e['reuse']=='1' for e in states),'observed_sizes':sorted(set(e['size'] for e in states)),'fbos_dropped_then_destroyed':[{k:destroy[k],'events':[e for e in traces['OPT_FBO_DESTROY'] if e['fbo_object']==destroy[k] and int(e['ns'])>=int(destroy['ns'])]} for k in ['blur','plain']] if destroy else None})
 lifetimes[mode]=lifetime
 if status['failure']:
  pixels[mode]={'status':'NOT EXERCISED','reason':status['failure']};contrast[mode]={'status':'NOT EXERCISED'};continue
 imgs={e['tag']+'-'+e['output']:rgb(run/e['path']) for e in events if e['kind']=='capture'}
 pairs=[('P0-FX0','P0-FX2'),('P0-FX2','P1-B-natural'),('P1-B-natural','P2-B-explicit'),('P0-FX2','P3-A-natural')]
 pixels[mode]={'capture_hashes':{p.name:sha(p) for p in run.glob('*.png')},'comparisons':{a+' -> '+b:comparisons(imgs[a+'-HEADLESS-1'],imgs[b+'-HEADLESS-1']) for a,b in pairs if b+'-HEADLESS-1' in imgs},'H2_full':{k:diff(imgs['P0-FX0-HEADLESS-2'],v) for k,v in imgs.items() if 'HEADLESS-2' in k}}
 contrast[mode]={}
 for name,img in imgs.items():
  if 'HEADLESS-1' not in name:continue
  r=roi(img,ROIS['glass']).astype(float);lum=r@[.2126,.7152,.0722]
  contrast[mode][name]={'luminance_std':float(lum.std()),'luminance_adjacent_mean':float(np.abs(np.diff(lum,axis=1)).mean()),'rgb_mean':r.mean(axis=(0,1)).tolist(),'RGB_adjacent_mean':float(np.abs(np.diff(r,axis=1)).mean())}
 phase={}
 for tag,kind in [('P0-FX2','enable'),('P1-B-natural','B'),('P2-B-explicit','cycle'),('P3-A-natural','A')]:
  capture=next(e for e in events if e['kind']=='capture' and e['tag']==tag and e['output']=='HEADLESS-1');end=capture['after_ns']
  if kind=='enable':start=next(e['after_ns'] for e in events if e['kind']=='capture' and e['tag']=='P0-reference')
  elif kind=='cycle':start=next(e['ns'] for e in events if e['kind']=='explicit_cycle_start')
  else:start=next(e['ns'] for e in events if e['kind']=='mutation_reserved' and e['pattern']==kind and (kind!='A' or e['ns']>next(c['after_ns'] for c in events if c['kind']=='capture' and c['tag']=='P1-B-natural')))
  phase[tag]={'start_ns':start,'end_ns':end,'trace':{n:[e for e in v if 'ns' in e and start<=int(e['ns'])<=end] for n,v in traces.items()}}
 phases[mode]=phase
 damage[mode]={}
 for old,new in [('P0-FX0','P0-FX2'),('P0-FX2','P1-B-natural'),('P1-B-natural','P2-B-explicit'),('P2-B-explicit','P3-A-natural')]:
  oldcap=next(e for e in events if e['kind']=='capture' and e['tag']==old and e['output']=='HEADLESS-1');newcap=next(e for e in events if e['kind']=='capture' and e['tag']==new and e['output']=='HEADLESS-1')
  mask=np.any(imgs[old+'-HEADLESS-1']!=imgs[new+'-HEADLESS-1'],axis=2);cover=np.zeros((600,800),bool);extents=[]
  for e in traces['OPT_OUTPUT_BUFFER']:
   if e['output']!='HEADLESS-1' or not oldcap['before_ns']<=int(e['ns'])<=newcap['after_ns']:continue
   b=[int(x) for x in e['damage'].split(',')];extents.append(e)
   l,t,r,bottom=b;cover[max(0,t):min(600,bottom),max(0,l):min(800,r)]=True
  damage[mode][old+' -> '+new]={'changed_pixels':int(mask.sum()),'uncovered_by_observed_output_damage_extents':int((mask&~cover).sum()),'output_damage':extents,'limitations':'Extent union only; not exact region/minimal damage, every frame, native PNG buffer identity or physical presentation.'}
write('renderer-identity',renderers);write('background-source',source);write('source-layers',source);write('pixel-comparisons',pixels);write('blur-contrast',contrast);write('offscreen-buffer-lifetime',lifetimes);write('damage-analysis',damage);write('phase-events',phases)
for file,names in [('blur-node-identities',['OPT_NODE_CREATE','OPT_NODE_RENDER','OPT_REGULAR_NODE']),('blur-mode-selection',['OPT_BLUR_USE','OPT_REGULAR_NODE']),('optimized-node-state',['OPT_NODE_RENDER','OPT_DIRTY_SET','OPT_DIRTY_CLEAR']),('dirty-events',['OPT_DIRTY_SET','OPT_DIRTY_CLEAR']),('cache-rebuild-events',['OPT_REGEN_ATTEMPT','OPT_REGEN_RESULT','OPT_GPU_REBUILD','OPT_GPU_RESULT','OPT_GPU_COPY','OPT_GPU_COPY_DRAWN']),('regular-blur-use',['OPT_BLUR_USE','OPT_REGULAR_NODE']),('output-clips',['PI_SCENE','PI_OWNER','OPT_REGULAR_NODE','OPT_BUFFER_DRAW']),('output-commits',['OPT_OUTPUT_BUFFER','PI_OUTPUT_COMMIT']),('presentations',['PI_OUTPUT_PRESENT'])]:write(file,{m:{k:d['traces'][k] for k in names} for m,d in data.items()})
write('background-mutations',{m:{'submissions':source[m]['client_commits'],'actual_count':len(source[m]['client_commits'])} for m in data})
budget=json.loads((out/'campaign-budget.json').read_text());assert sum(s['run'] for s in budget['modes'].values())==3
for mode in data:
 assert len(source[mode]['client_commits'])==budget['modes'][mode]['mutation']
 assert len(data[mode]['status']['captures'])==budget['modes'][mode]['capture']
 assert data[mode]['status']['duration']<150 and data[mode]['status']['runtime_removed']
write('matrix',{'C0':'NOT EXERCISED: failed duplicate initial configure fixture, no retry','C1':'central natural invalidation PASS; boundary history differences unresolved','C2':'central natural invalidation and sampled final clip PASS; boundary history differences unresolved','instrumentation_neutrality':'NOT TESTED: C0 has no captures','P5':'NOT EXERCISED: no extra camera pair','budget_deviation':'C0 second initial image reserved only after observation; actual 2 charged, no refund'})
write('summary',{'verdict':'PARTIALLY_FEASIBLE','architecture':'UNDECIDED','private_central_updates':True,'full_H2_stable':True,'boundary_equivalence':False,'reason':['C0 graphical control missing','instrumentation neutrality unqualified','shared C1/C2 boundary differences up to six RGB levels, source-only cache equivalence unqualified'],'lab':str(lab)})
# Source manifest records actual compiled trees and each executed runner/client.
# Evidence excludes its own digest and source list; never touches saved manifests.
sources=list(fixture.glob('*'))
for name in ['scene0','scenefx','mosaic','pristine']:
 sources.extend(p for p in (lab/name).rglob('*') if p.is_file() and 'subprojects' not in p.parts)
sources.extend(p for run in (lab/'runs').iterdir() for p in [run/'fixture-source.py',run/'client-source.c'] if p.is_file())
sources.extend(p for p in lab.glob('*') if p.suffix in ['.h','.c','.xml'])
sources=sorted(set(p for p in sources if p.is_file()))
(out/'source-sha256.txt').write_text(''.join(f'{sha(p)}  {p}\n' for p in sources))
evidence=sorted([p for p in (lab/'runs').rglob('*') if p.is_file()]+[p for p in out.iterdir() if p.is_file() and not p.name.endswith('-sha256.txt')]+[lab/'build.log'])
(out/'evidence-sha256.txt').write_text(''.join(f'{sha(p)}  {p}\n' for p in evidence))
print('PARTIALLY_FEASIBLE sources',len(sources),'evidence',len(evidence),'source_manifest',sha(out/'source-sha256.txt'),'evidence_manifest',sha(out/'evidence-sha256.txt'))
