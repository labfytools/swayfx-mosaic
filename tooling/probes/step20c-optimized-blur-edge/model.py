#!/usr/bin/env python3
"""Reuse V1 ideal kernels; compare hypothesis with R3 native reconstruction order.

CONTRACT: no GLSL/native precision equivalence, FBO contents or causal proof.
INVARIANT: model prediction is fixed before fitting; no kernel/offset fitting.
"""
import ast
import hashlib
import json
import re
import sys
from pathlib import Path
import numpy as np
from PIL import Image

lab=Path(sys.argv[1]).resolve()
fixture=Path(__file__).resolve().parent
historical=fixture.parent/'step20c-optimized-blur-cache/edge-model.py'
source=historical.read_text()
# WHY: reuse the exact reviewed functions without executing the historical writer.
# CONTRACT: retain only function definitions/imports and W,H constants from its AST.
module=ast.parse(source)
selected=[node for node in module.body if isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef))
          or (isinstance(node,ast.Assign) and any(isinstance(t,ast.Tuple) for t in node.targets))]
context={}
exec(compile(ast.Module(body=selected,type_ignores=[]),str(historical),'exec'),context)
rebuild=context['rebuild'];pattern=context['pattern']
run=lab/'runs/R3'
lines=(run/'compositor.log').read_text().splitlines()
commits=[]
for line in (run/'background.log').read_text().splitlines():
    if line.startswith('CLIENT_COMMIT '):
        commits.append((int(re.search(r'ns=(\d+)',line)[1]),re.search(r'pattern=([AB])',line)[1]))
rebuilds=[int(re.search(r'ns=(\d+)',line)[1]) for line in lines
          if line.startswith('OPT_GPU_REBUILD ') and 'output=HEADLESS-1' in line]
ping=np.zeros((600,800,3));pong=ping.copy();states=[]
for ns in rebuilds:
    current=next((c for t,c in reversed(commits) if t<ns),None)
    image=pattern(current) if current else np.zeros((600,800,3))
    cache=rebuild(image,ping,pong)
    states.append((ns,current,cache))
events=[json.loads(line) for line in (run/'events.jsonl').read_text().splitlines()]
metrics={};predictions={};actuals={}
for event in events:
    if event['kind']!='capture' or event['output']!='HEADLESS-1' or event['tag']=='P0-FX0':continue
    ns,current,cache=next(s for s in reversed(states) if s[0]<event['before_ns'])
    predicted=np.round(cache*(119/255)+[68,32,16])
    actual=np.array(Image.open(run/event['path']).convert('RGB')).astype(float)
    predictions[event['tag']]=predicted;actuals[event['tag']]=actual
    rois={'center':(520,100,720,500),'boundary':(720,50,800,550),
          'physical_right':(750,0,800,600),'glass_bottom':(480,550,800,600)}
    measurements={}
    for name,(l,t,r,b) in rois.items():
        d=np.abs(predicted[t:b,l:r]-actual[t:b,l:r])
        measurements[name]={'mean_abs_channel_error':float(d.mean()),
                            'max_channel_error':float(d.max()),'within_one_channel':float((d<=1).mean())}
    metrics[event['tag']]={'source':current,'model_rebuild_ns':ns,'ROIs':measurements}
distribution={}
for first,second in [('P1-B-natural','P2-B-explicit'),('P0-FX2','P3-A-natural')]:
    pd=predictions[second]-predictions[first];nd=actuals[second]-actuals[first]
    # Model applies only to the measured glass, not the entire composited source.
    pd[:,:480]=0;pm=np.any(pd!=0,axis=2);nm=np.any(nd!=0,axis=2)
    union=(pm|nm).sum();intersection=(pm&nm).sum()
    disagreement=np.abs(pd-nd)
    distribution[first+' -> '+second]={
        'predicted_changed_pixels_in_visible_glass':int(pm.sum()),'native_changed_pixels':int(nm.sum()),
        'mask_intersection':int(intersection),'mask_union':int(union),
        'mask_jaccard':float(intersection/union) if union else 1,
        'predicted_max_channel':float(np.abs(pd).max()),'native_max_channel':float(np.abs(nd).max()),
        'delta_residual_mean_abs_channel':float(disagreement[:,480:].mean()),
        'predicted_columns':pm.sum(axis=0).astype(int).tolist(),
        'predicted_rows':pm.sum(axis=1).astype(int).tolist(),
        'native_columns':nm.sum(axis=0).astype(int).tolist(),'native_rows':nm.sum(axis=1).astype(int).tolist(),
        'interpretation':'fixed-kernel history compatibility only; native FBO tail and mediump behavior unobserved'}
(lab/'results/edge-model-comparison.json').write_text(json.dumps({
    'model_source':str(historical),'model_sha256':hashlib.sha256(historical.read_bytes()).hexdigest(),
    'native_schedule':'R3 OPT_GPU_REBUILD timestamps only; no invented timestamps for untraced runs',
    'rebuild_count':len(rebuilds),'metrics':metrics,'distributions':distribution,
    'causality':'NOT DEMONSTRATED; no GPU readback or intervention'},indent=2)+'\n')
print(json.dumps({'rebuild_count':len(rebuilds),'metrics':metrics,
                  'distributions':{k:{n:v for n,v in d.items() if not n.endswith(('columns','rows'))}
                                   for k,d in distribution.items()}},indent=2))
