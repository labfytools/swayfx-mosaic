#!/usr/bin/env python3
"""One headless run of staged static compositor with measured tiled crossing.

WHY: resolved relocations do not demonstrate real compositor execution.
CONTRACT: verify /proc executable/library identity before mapping any client.
INVARIANT: owned sockets/groups only, one camera correction, durable captures.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from PIL import Image,ImageChops
from support import environment,reserve,save,sha

p=argparse.ArgumentParser();p.add_argument('lab',type=Path);a=p.parse_args();lab=a.lab.resolve()
assert json.loads((lab/'results/static-stage-manifest.json').read_text())['status']=='PASS'
assert json.loads((lab/'results/binary-elf.json').read_text())['status']=='PASS'
reserve(lab,'run');run=lab/'run';run.mkdir();runtime=Path(tempfile.mkdtemp(prefix='msr-',dir='/tmp'))
runtime.chmod(0o700);(run/'runtime-path').write_text(str(runtime)+'\n')
(run/'config').write_text('output HEADLESS-1 resolution 800x600 scale 1 transform normal position -800 0\noutput HEADLESS-2 resolution 800x600 scale 1 transform normal position 0 0\nworkspace 1 output HEADLESS-1\nworkspace 2 output HEADLESS-2\nfocus_follows_mouse no\nseat seat0 hide_cursor 100\n')
env=environment();env.update(XDG_RUNTIME_DIR=str(runtime),WLR_BACKENDS='headless',WLR_HEADLESS_OUTPUTS='2',WLR_RENDERER='pixman')
binary=lab/'stage-static/usr/bin/swayfx-mosaic';processes=[];files=[];failure=None;compositor=None;events=[]
started=time.monotonic();finished=threading.Event();expired=threading.Event()

def event(kind,**data):
    row={'ns':time.monotonic_ns(),'kind':kind,**data};events.append(row)
    with (run/'events.jsonl').open('a') as out:out.write(json.dumps(row)+'\n')

def stop_owned():
    for proc in list(processes):
        try:os.killpg(proc.pid,signal.SIGTERM)
        except ProcessLookupError:pass

def watchdog():
    while not finished.wait(.1):
        if time.monotonic()-started>150 or any(x.stat().st_size>64*1024*1024 for x in run.glob('*.log')):
            expired.set();stop_owned();return

thread=threading.Thread(target=watchdog,daemon=True);thread.start()

def spawn(name,argv,stdin=False,extra=None):
    assert not expired.is_set()
    out=(run/(name+'.log')).open('w');files.append(out)
    proc=subprocess.Popen(list(map(str,argv)),env={**env,**(extra or {})},stdin=subprocess.PIPE if stdin else subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,text=True,start_new_session=True)
    processes.append(proc);event('spawn',name=name,pid=proc.pid,argv=list(map(str,argv)));return proc

def wait(predicate,seconds=8):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if expired.is_set():raise RuntimeError('deadline/log bound exceeded')
        if compositor and compositor.poll() is not None:raise RuntimeError('compositor exited '+str(compositor.returncode))
        value=predicate()
        if value:return value
        time.sleep(.025)
    raise RuntimeError('fixture wait timed out')

def log(name):return (run/(name+'.log')).read_text(errors='replace')

def ipc(*args):
    assert sock.is_relative_to(runtime) and sock.is_socket()
    result=subprocess.run(['swaymsg','-s',str(sock),*args],env=env,capture_output=True,text=True,timeout=5,check=True)
    data=json.loads(result.stdout);event('ipc',args=args,result=data);return data

def cmd(value):
    data=ipc(value);assert all(x.get('success') for x in data),(value,data)

def nodes(node):
    yield node
    for child in node.get('nodes',[])+node.get('floating_nodes',[]):yield from nodes(child)

def find(app):return next((n for n in nodes(ipc('-t','get_tree')) if n.get('app_id')==app),None)

def inject(action,x,y):
    assert -800<=x<800 and 0<=y<600
    marker=f'INJECT_DONE {action} {x+800},{y}';before=log('pointer').count(marker)
    pointer.stdin.write(f'{action} {x+800} {y}\n');pointer.stdin.flush()
    wait(lambda:log('pointer').count(marker)>before)
    time.sleep(.15);event('pointer',action=action,global_point=[x,y],target_tail=log('target').splitlines()[-6:] if (run/'target.log').exists() else [])

def capture(tag,output):
    reserve(lab,'capture');path=run/(tag+'.png')
    subprocess.run(['grim','-s','1','-o',output,str(path)],env=env,check=True,timeout=5,stdout=subprocess.DEVNULL)
    im=Image.open(path).convert('RGB');assert im.size==(800,600)
    event('capture',file=path.name,output=output,sha256=sha(path));return im

def measure(owner):
    rows=[x for x in log('compositor').splitlines() if 'PI_OWNER output=HEADLESS-1 ' in x and f' id={owner["id"]} ' in x]
    assert rows,'applied owner trace unavailable'
    line=rows[-1];m=re.search(r'scene_valid=1 scene=(-?\d+),(-?\d+) applied_size=(\d+),(\d+)',line);assert m,line
    x,y,w,h=map(int,m.groups());win=owner['window_rect']
    return {'id':owner['id'],'scene':[x,y,w,h],'window_rect':win,'source_box':[x+win['x'],y+win['y'],win['width'],win['height']],'raw':line}

try:
    compositor=spawn('compositor',[binary,'-d','-c',run/'config'],extra={'LD_DEBUG':'bindings','LD_BIND_NOW':'1'})
    sock=wait(lambda:next(iter(runtime.glob('sway-ipc.*.sock')),None))
    display=wait(lambda:next((x for x in runtime.glob('wayland-*') if x.is_socket()),None))
    env.update(SWAYSOCK=str(sock),WAYLAND_DISPLAY=display.name)
    maps=Path(f'/proc/{compositor.pid}/maps').read_text();(run/'proc-maps.txt').write_text(maps)
    exe=Path(f'/proc/{compositor.pid}/exe').resolve();assert exe==binary and sha(exe)==sha(binary),'wrong executable'
    paths=sorted({line.split()[-1] for line in maps.splitlines() if len(line.split())>=6 and line.split()[-1].startswith('/')})
    pair=json.loads((lab/'results/wlroots-qualified-pair.json').read_text());wl=Path(pair['library'])
    assert not any('libscenefx' in x for x in paths),'wrong SceneFX shared mapping'
    loaded_wl=[Path(x) for x in paths if 'libwlroots' in x];assert len(loaded_wl)==1 and loaded_wl[0].resolve()==wl and sha(wl)==pair['sha256'],'wrong wlroots mapping'
    assert not any('/swayfx-mosaic-' in x and Path(x)!=binary for x in paths),'old LAB dependency'
    save(lab,'loader-mappings',{'status':'PASS','pid':compositor.pid,'exe':str(exe),'sha256':sha(exe),'paths':paths,'wlroots_sha256':sha(wl),'SceneFX_shared':False})
    outputs=ipc('-t','get_outputs');actual={o['name']:(o['rect']['x'],o['rect']['y'],o['rect']['width'],o['rect']['height'],o['scale'],o['transform']) for o in outputs if o['active']}
    assert actual=={'HEADLESS-1':(-800,0,800,600,1.0,'normal'),'HEADLESS-2':(0,0,800,600,1.0,'normal')},actual
    save(lab,'headless-outputs',outputs)
    pointer=spawn('pointer',[lab/'pointer-daemon','1600','600'],stdin=True);wait(lambda:'POINTER_READY' in log('pointer'))
    cmd('workspace 2');ref=spawn('reference',[lab/'static-reference'],stdin=True);wait(lambda:find('org.mosaic.StaticReference'))
    time.sleep(.4);inject('move',-790,590);baseline=capture('h2-reference','HEADLESS-2')
    cmd('workspace 1');filler=spawn('filler',[lab/'static-reference'],stdin=True);wait(lambda:len([n for n in nodes(ipc('-t','get_tree')) if n.get('app_id')=='org.mosaic.StaticReference'])==2)
    target=spawn('target',[lab/'saved-client'],stdin=True);wait(lambda:find('org.mosaic.SavedBufferProbe'))
    cmd('layout mosaic');time.sleep(.5)
    owner=find('org.mosaic.SavedBufferProbe');before=measure(owner);x,y,w,h=before['source_box'];desired=-w//2;delta=x-desired
    event('camera-calculation',before=before,desired_left=desired,delta=delta)
    if delta:reserve(lab,'camera');cmd(f'layout mosaic scroll {delta}')
    time.sleep(.5);owner=find('org.mosaic.SavedBufferProbe');after=measure(owner);x,y,w,h=after['source_box']
    assert x<0<x+w and -800<x,'real source crossing absent'
    save(lab,'scene-clips',{'before':before,'after':after,'delta':delta,'clips':[s for s in log('compositor').splitlines() if 'PI_SCENE output=HEADLESS-1' in s][-4:]})
    inject('move',-790,590);left=capture('h1-mosaic','HEADLESS-1');right=capture('h2-mosaic','HEADLESS-2')
    colors={(35,68,204),(32,208,160)};left_count=sum(v in colors for v in left.get_flattened_data());right_count=sum(v in colors for v in right.get_flattened_data())
    diff=ImageChops.difference(baseline,right).getbbox()
    save(lab,'pixel-analysis',{'retained_h1_target_pixels':left_count,'forbidden_h2_target_pixels':right_count,'whole_H2_difference_bbox':diff,'source_crossing':after['source_box']})
    assert left_count>0 and right_count==0 and diff is None,'forbidden pixel leakage/reference difference'
    visible_x=max(-780,min(-20,x+max(20,w//4)));visible_y=min(550,y+80)
    target_before=log('target').count('BUTTON ');inject('right',visible_x,visible_y);visible_buttons=log('target').count('BUTTON ')-target_before
    assert visible_buttons>=2,'visible target input missing'
    target_before=log('target').count('BUTTON ');ref_before=log('reference').count('BUTTON ')
    clipped_x=max(20,min(x+w-20,200));inject('right',clipped_x,visible_y)
    invisible_buttons=log('target').count('BUTTON ')-target_before;reference_buttons=log('reference').count('BUTTON ')-ref_before
    save(lab,'input-analysis',{'visible_point':[visible_x,visible_y],'visible_target_button_events':visible_buttons,'forbidden_point':[clipped_x,visible_y],'forbidden_target_button_events':invisible_buttons,'reference_button_events':reference_buttons})
    assert invisible_buttons==0 and reference_buttons>=2,'forbidden target hit/reference missing'
    inject('move',-790,590);repeat=capture('h2-mosaic-repeat','HEADLESS-2');assert ImageChops.difference(baseline,repeat).getbbox() is None,'unstable H2 reference'
    cmd('layout splith');time.sleep(.5);inject('move',-790,590)
    standard_left=capture('h1-standard','HEADLESS-1');standard_right=capture('h2-standard','HEADLESS-2')
    scene_lines=[s for s in log('compositor').splitlines() if 'PI_SCENE output=HEADLESS-1' in s]
    assert scene_lines and 'clip_valid=0' in scene_lines[-1],'residual Mosaic clip'
    standard_owner=find('org.mosaic.SavedBufferProbe');standard_measure=measure(standard_owner)
    sx,sy,sw,sh=standard_measure['source_box'];before_buttons=log('target').count('BUTTON ');inject('right',sx+sw//2,sy+min(80,sh//2));standard_buttons=log('target').count('BUTTON ')-before_buttons
    assert standard_buttons>=2 and ImageChops.difference(baseline,standard_right).getbbox() is None,'standard regression'
    save(lab,'standard-layout',{'status':'PASS sampled only','scene_trace':scene_lines[-1],'owner':standard_measure,'target_button_events':standard_buttons,'H2_equal':True})
    save(lab,'popup-ownership',{'status':'NOT TESTED','reason':'root-grab fixture not added to the single minimal tiled scenario; historical pristine/grab evidence retained'})
    cmd('exit');compositor.wait(timeout=5);assert compositor.returncode==0
except Exception as exc:
    failure=f'{type(exc).__name__}: {exc}';event('failure',message=failure)
finally:
    finished.set();thread.join(timeout=1);stop_owned()
    for proc in processes:
        try:proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=3)
        try:os.killpg(proc.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    for out in files:out.close()
    elapsed=time.monotonic()-started
    save(lab,'static-runtime',{'status':'PASS' if failure is None else 'INCONCLUSIVE','failure':failure,'duration_seconds':elapsed,'binary':str(binary),'sha256':sha(binary),'process_exit_codes':[{'pid':x.pid,'argv':x.args,'exit':x.returncode} for x in processes],'runtime_removed':str(runtime),'cleanup':'all owned groups reaped'})
    shutil.rmtree(runtime)
    damage=[s for s in log('compositor').splitlines() if 'TEMPORAL_DAMAGE ' in s]
    save(lab,'damage-analysis',{'status':'OBSERVED' if damage else 'NOT TESTED','extents':damage,'all_frames':'NOT TESTED'})
print('STATIC_RUNTIME',failure or 'PASS')
if failure:raise SystemExit(1)
