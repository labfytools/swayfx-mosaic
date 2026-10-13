#!/usr/bin/env python3
"""One reserved, deadline-limited run per mode; only owned headless processes."""
import argparse,json,os,re,shutil,signal,subprocess,time
from pathlib import Path
import numpy as np
from PIL import Image
from budget import reserve,DEFAULT
p=argparse.ArgumentParser();p.add_argument('lab',type=Path);p.add_argument('mode',choices=['C0','C1','C2']);a=p.parse_args()
lab=a.lab.resolve();mode=a.mode
if not (lab/'clients').is_file():p.error('prepared LAB required')
reserve(lab,mode,'run')
run=lab/'runs'/mode;run.mkdir(mode=0o700)
runtime=run/'runtime';runtime.mkdir(mode=0o700)
(run/'fixture-source.py').write_text(Path(__file__).read_text())
(run/'config').write_text('''output HEADLESS-1 resolution 800x600 scale 1 transform normal position -800 0
output HEADLESS-2 resolution 800x600 scale 1 transform normal position 0 0
workspace 1 output HEADLESS-1
workspace 2 output HEADLESS-2
focus_follows_mouse no
mouse_warping none
default_border none
font monospace 8
shadows disable
blur disable
blur_xray disable
blur_radius 5
blur_passes 3
blur_noise 0
blur_brightness 1
blur_contrast 1
blur_saturation 1
corner_radius 0
animation_duration_ms 0
''')
env={k:v for k,v in os.environ.items() if k not in ['SWAYSOCK','I3SOCK','WAYLAND_DISPLAY','LD_LIBRARY_PATH','OPT_TRACE','SAVED_TRACE','SAVED_HIT_TRACE','FX_TRACE']}
env.update(XDG_RUNTIME_DIR=str(runtime),WLR_BACKENDS='headless',WLR_HEADLESS_OUTPUTS='2',WLR_RENDERER='gles2')
private=mode!='C0'
binary=lab/('mosaic-build/sway/swayfx-mosaic' if private else 'pristine-build/sway/sway')
env['LD_LIBRARY_PATH']=str(lab/('scenefx-build' if private else 'scene0-build'))
if private:env['OPT_TRACE']='1'
children=[];files=[];comp=None;sock=None;failure=None;started=time.monotonic();captures=[]

def event(kind,**data):
 with (run/'events.jsonl').open('a') as out:out.write(json.dumps({'kind':kind,'ns':time.monotonic_ns(),**data})+'\n')
def guard():
 if time.monotonic()-started>150:raise TimeoutError('run deadline')
 for q in run.glob('*.log'):
  if q.stat().st_size>25_000_000:raise RuntimeError('bounded log exceeded')
def spawn(argv,name,stdin=False):
 guard();f=(run/name).open('w');files.append(f)
 child=subprocess.Popen(argv,env=env,stdin=subprocess.PIPE if stdin else subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,text=stdin,start_new_session=True);children.append(child)
 event('spawn',argv=argv,pid=child.pid);return child
def wait(fn,seconds=8):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  guard();result=fn()
  if result:return result
  if comp and comp.poll() is not None:raise RuntimeError('compositor exited')
  time.sleep(.025)
 raise TimeoutError('fixture wait')
def ipc(*args):
 guard();r=subprocess.run(['swaymsg','-s',str(sock),*args],env=env,capture_output=True,text=True,timeout=5,check=True)
 data=json.loads(r.stdout);event('ipc',args=args,data=data);return data
def command(s):
 r=ipc(s)
 if not r or not all(v.get('success') for v in r):raise RuntimeError('IPC rejected '+s)
def nodes(n):
 yield n
 for c in n.get('nodes',[])+n.get('floating_nodes',[]):yield from nodes(c)
def find(app):return next((n for n in nodes(ipc('-t','get_tree')) if n.get('app_id')==app),None)
def log(name):return (run/name).read_text()
def snapshot(tag,only_h2=False):
 outs=ipc('-t','get_outputs');expected={'HEADLESS-1':(-800,0,800,600),'HEADLESS-2':(0,0,800,600)}
 actual={o['name']:tuple(o['rect'][k] for k in ['x','y','width','height']) for o in outs if o['active']}
 if actual!=expected or any(o['scale']!=1 or o['transform']!='normal' for o in outs if o['active']):raise RuntimeError('output geometry gate')
 (run/(tag+'-outputs.json')).write_text(json.dumps(outs,indent=2)+'\n')
 (run/(tag+'-tree.json')).write_text(json.dumps(ipc('-t','get_tree'),indent=2)+'\n')
 for name in (['HEADLESS-2'] if only_h2 else ['HEADLESS-1','HEADLESS-2']):
  reserve(lab,mode,'capture');q=run/(tag+'-'+name+'.png');before=time.monotonic_ns()
  subprocess.run(['grim','-s','1','-o',name,str(q)],env=env,timeout=5,check=True,stdout=subprocess.DEVNULL)
  if Image.open(q).size!=(800,600):raise RuntimeError('capture size gate')
  record={'tag':tag,'output':name,'path':q.name,'before_ns':before,'after_ns':time.monotonic_ns()};captures.append(record);event('capture',**record)
def image(tag,out='HEADLESS-1'):return np.array(Image.open(run/(tag+'-'+out+'.png')).convert('RGB'))
def native_gate():
 text=log('compositor.log')
 return 'OPT_BLUR_USE' in text and 'OPT_REGEN_RESULT' in text and any('OPT_REGEN_RESULT' in x and 'output=HEADLESS-1' in x and 'result=1' in x for x in text.splitlines()) and any('OPT_BLUR_USE' in x and 'output=HEADLESS-1' in x and 'optimized=1' in x and 'chosen=(nil)' not in x for x in text.splitlines())
def mutate(pattern):
 reserve(lab,mode,'mutation');before=log('background.log').count('CLIENT_COMMIT ');event('mutation_reserved',pattern=pattern)
 background.stdin.write(pattern+'\n');background.stdin.flush()
 wait(lambda:log('background.log').count('CLIENT_COMMIT ')>before)
 count=log('background.log').count('CLIENT_COMMIT ')
 if count!=before+1:raise RuntimeError('unexpected background commits')
 event('mutation_received_client',pattern=pattern,count=count);time.sleep(.35)
def alarm(s,f):raise TimeoutError('150 second watchdog')
signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,150)
try:
 f=(run/'compositor.log').open('w');files.append(f)
 comp=subprocess.Popen([str(binary),'-d','-c',str(run/'config')],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 def sockets():
  s=next(iter(runtime.glob('sway-ipc.*.sock')),None);w=next((q for q in runtime.glob('wayland-*') if q.is_socket()),None)
  return (s,w) if s and w else None
 sock,way=wait(sockets);env.update(SWAYSOCK=str(sock),WAYLAND_DISPLAY=way.name)
 (run/'library-maps.txt').write_text(Path(f'/proc/{comp.pid}/maps').read_text())
 event('renderer_start',pid=comp.pid,binary=str(binary),library=env['LD_LIBRARY_PATH'])
 reserve(lab,mode,'mutation');event('mutation_reserved',pattern='A',initial=True)
 background=spawn([str(lab/'clients'),'background'],'background.log',True)
 wait(lambda:'CLIENT_COMMIT ' in log('background.log'))
 command('workspace 1');command('layout mosaic' if mode=='C2' else 'layout splith')
 filler=spawn([str(lab/'clients'),'filler'],'filler.log',True);wait(lambda:find('org.mosaic.BlurFiller'))
 glass=spawn([str(lab/'clients'),'glass'],'glass.log',True);wait(lambda:find('org.mosaic.BlurGlass'))
 command('workspace 2');reference=spawn([str(lab/'clients'),'reference'],'reference.log',True);wait(lambda:find('org.mosaic.StaticReference'))
 command('[app_id="org.mosaic.BlurGlass"] focus');time.sleep(.5)
 if mode=='C2':
  tree=ipc('-t','get_tree');ws=next(n for n in nodes(tree) if n.get('type')=='workspace' and n.get('name')=='1');owner=next(n for n in nodes(ws) if n.get('app_id')=='org.mosaic.BlurGlass')
  current=ws['mosaic']['rows'][0]['scroll_x'];left=owner['rect']['x']+owner['window_rect']['x']-current
  delta=int(left+owner['window_rect']['width']//2)
  reserve(lab,mode,'calibration');event('camera_calibration',current=current,logical=owner['rect'],window=owner['window_rect'],delta=delta)
  command('layout mosaic scroll '+str(delta));time.sleep(.35)
 if log('background.log').count('CLIENT_COMMIT ')!=1:raise RuntimeError('unexpected initial background image count')
 snapshot('P0-FX0');time.sleep(.75);snapshot('P0-reference',True)
 if not np.array_equal(image('P0-FX0','HEADLESS-2'),image('P0-reference','HEADLESS-2')):raise RuntimeError('H2 preflight instability')
 # Source A must be visible outside glass before interpretation of any cache.
 source=image('P0-FX0')[100:500,20:160]
 colors={tuple(x) for x in source.reshape(-1,3)}
 if not {(245,245,245),(15,25,45)}<=colors:raise RuntimeError('unblurred source gate')
 command('[app_id="org.mosaic.BlurGlass"] blur enable');time.sleep(.35);snapshot('P0-FX2')
 roi0=image('P0-FX0')[100:500,520:720].astype(float);roi2=image('P0-FX2')[100:500,520:720].astype(float)
 adjacent0=np.abs(np.diff(roi0,axis=1)).mean();adjacent2=np.abs(np.diff(roi2,axis=1)).mean()
 if adjacent0<=5 or adjacent2>=adjacent0*.8 or not np.any(roi0!=roi2):raise RuntimeError('visible filtering gate')
 if private and not native_gate():raise RuntimeError('optimized native use gate')
 event('P0_gate',source=True,filtering=True,native_optimized=bool(private),adjacent_fx0=adjacent0,adjacent_fx2=adjacent2)
 mutate('B');snapshot('P1-B-natural')
 if private:
  reserve(lab,mode,'cycle');event('explicit_cycle_start')
  command('[app_id="org.mosaic.BlurGlass"] blur disable');time.sleep(.15)
  command('[app_id="org.mosaic.BlurGlass"] blur enable');time.sleep(.35);snapshot('P2-B-explicit')
 mutate('A');snapshot('P3-A-natural')
 event('complete',camera_pair='NOT EXERCISED: main mutation evidence is distinct and sufficient')
except Exception as exc:
 failure=repr(exc);event('failure',error=failure)
finally:
 signal.setitimer(signal.ITIMER_REAL,0)
 # WHY: request normal compositor teardown first so cache destructors can log.
 # CONTRACT: explicit private socket, then only recorded owned process groups.
 if comp and comp.poll() is None and sock:
  try:command('exit');comp.wait(timeout=5)
  except (subprocess.SubprocessError,RuntimeError,OSError):pass
 for c in children+([comp] if comp else []):
  if c.poll() is None:
   try:os.killpg(c.pid,signal.SIGTERM)
   except ProcessLookupError:pass
 for c in children+([comp] if comp else []):
  try:c.wait(timeout=3)
  except subprocess.TimeoutExpired:
   os.killpg(c.pid,signal.SIGKILL);c.wait(timeout=3)
 for f in files:f.close()
 shutil.rmtree(runtime)
 (run/'exit-status.json').write_text(json.dumps({'failure':failure,'duration':time.monotonic()-started,'compositor':comp.returncode if comp else None,'children':[{'args':c.args,'pid':c.pid,'code':c.returncode} for c in children],'runtime_removed':not runtime.exists(),'captures':captures},indent=2)+'\n')
 shutil.copy2(DEFAULT,lab/'results/campaign-budget.json')
 event('cleanup',runtime_removed=not runtime.exists())
print(mode,'FAILURE='+str(failure),'RUN='+str(run),flush=True)
if failure:raise SystemExit(1)
