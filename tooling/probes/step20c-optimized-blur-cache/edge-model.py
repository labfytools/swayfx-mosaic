"""Offline model of the audited blur1/blur2 kernels, never a GPU run.

WHY: determine whether a scaled written domain and full-size sampler clamp
can explain the observed history-dependent boundary pixels.
CONTRACT: hypotheses use 8-bit rounding and ideal bilinear samples, not GLES
precision, native framebuffer readback or proof of actual tail contents.
INVARIANT: historical logs/PNGs stay immutable; no renderer algorithm edits.
"""
import json,re,sys
from pathlib import Path
import numpy as np
from PIL import Image
lab=Path(sys.argv[1]);results={}
W,H=800,600

def sample(src,x,y):
 x=np.clip(x,0,W-1);y=np.clip(y,0,H-1)
 x0=np.floor(x).astype(int);y0=np.floor(y).astype(int)
 x1=np.minimum(x0+1,W-1);y1=np.minimum(y0+1,H-1)
 ax=(x-x0)[...,None];ay=(y-y0)[...,None]
 return ((1-ax)*src[y0,x0]+ax*src[y0,x1])*(1-ay)+((1-ax)*src[y1,x0]+ax*src[y1,x1])*ay

def rebuild(source,ping,pong):
 current=source
 for down,i in [(True,i) for i in range(3)]+[(False,i) for i in [2,1,0]]:
  dst=pong if current is ping else ping
  w=W//(2**(i+1) if down else 2**i);h=H//(2**(i+1) if down else 2**i)
  yy,xx=np.mgrid[:h,:w]
  if down:
   x=(xx+.5)*2-.5;y=(yy+.5)*2-.5
   v=sample(current,x,y)*4
   for dx,dy in [(-5,-5),(5,5),(5,-5),(-5,5)]:v+=sample(current,x+dx,y+dy)
   v/=8
  else:
   x=(xx+.5)/2-.5;y=(yy+.5)/2-.5
   v=np.zeros((h,w,3))
   for dx,dy,weight in [(-2.5,0,1),(-1.25,1.25,2),(0,2.5,1),(1.25,1.25,2),(2.5,0,1),(1.25,-1.25,2),(0,-2.5,1),(-1.25,-1.25,2)]:v+=sample(current,x+dx,y+dy)*weight
   v/=12
  dst[:h,:w]=np.round(v)
  current=dst
 return current.copy()

def pattern(c):
 colors=np.array([[245,245,245],[15,25,45]] if c=='A' else [[32,192,224],[176,32,64]],dtype=float)
 return np.broadcast_to(colors[(np.arange(W)//8)%2],(H,W,3)).copy()
for mode in ['C1','C2']:
 run=lab/'runs'/mode;lines=(run/'compositor.log').read_text().splitlines();client=(run/'background.log').read_text().splitlines()
 commits=[]
 for line in client:
  if line.startswith('CLIENT_COMMIT '):commits.append((int(re.search(r'ns=(\d+)',line)[1]),re.search(r'pattern=([AB])',line)[1]))
 rebuilds=[int(re.search(r'ns=(\d+)',x)[1]) for x in lines if x.startswith('OPT_GPU_REBUILD ') and 'output=HEADLESS-1' in x]
 ping=np.zeros((H,W,3));pong=ping.copy();cache=ping.copy();states=[]
 for ns in rebuilds:
  current=next((c for t,c in reversed(commits) if t<ns),None)
  src=pattern(current) if current else np.zeros((H,W,3))
  cache=rebuild(src,ping,pong);states.append((ns,current,cache))
 events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
 metrics={}
 for e in events:
  if e['kind']!='capture' or e['output']!='HEADLESS-1' or e['tag']=='P0-FX0':continue
  ns,c,cache=next(v for v in reversed(states) if v[0]<e['before_ns'])
  final=np.round(cache*(119/255)+[68,32,16])
  actual=np.array(Image.open(run/e['path']).convert('RGB')).astype(float)
  # Predefined boundary ROI is compared without fitting offsets or kernels.
  expected=final[50:550,720:800];observed=actual[50:550,720:800]
  d=np.abs(expected-observed)
  metrics[e['tag']]={'source':c,'model_mae_boundary':float(d.mean()),'model_max_channel_error':float(d.max()),'within_one_channel':float((d<=1).mean())}
 # Pure same-input repeated regeneration must be invariant for a correct source-only model.
 ping=np.zeros((H,W,3));pong=ping.copy()
 aa=rebuild(pattern('A'),ping,pong);bb=rebuild(pattern('B'),ping,pong);bb2=rebuild(pattern('B'),ping,pong);aa2=rebuild(pattern('A'),ping,pong)
 metrics['ideal_model_history']={'B_repeat_changed_pixels':int(np.any(bb!=bb2,axis=2).sum()),'A_return_changed_pixels':int(np.any(aa!=aa2,axis=2).sum()),'explanation':'Upsample taps exceed the freshly written reduced domain; texture clamp is at the full-size FBO boundary. This is a source-supported hypothesis, not native GPU tail proof.'}
 results[mode]=metrics
out=lab/'results/edge-model.json';out.write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
