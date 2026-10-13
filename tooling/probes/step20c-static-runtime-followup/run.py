#!/usr/bin/env python3
"""One budgeted follow-up of the unchanged verified static compositor.

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
from pixels import analyze, compare, interior, button_pair

p=argparse.ArgumentParser();p.add_argument('lab',type=Path);a=p.parse_args();lab=a.lab.resolve()
assert json.loads((lab/'results/binary-identity.json').read_text())['status']=='PASS'
assert sha(lab/'swayfx-mosaic')=='f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b'
assert (Path.home()/'swayfx-mosaic-static-followup-v1.owner').read_text().strip()==str(lab)
reserve(lab,'run');run=lab/'run';run.mkdir();runtime=Path(tempfile.mkdtemp(prefix='msr-',dir='/tmp'))
runtime.chmod(0o700);(run/'runtime-path').write_text(str(runtime)+'\n')
(run/'config').write_text('output HEADLESS-1 resolution 800x600 scale 1 transform normal position -800 0\noutput HEADLESS-2 resolution 800x600 scale 1 transform normal position 0 0\nworkspace 1 output HEADLESS-1\nworkspace 2 output HEADLESS-2\nfocus_follows_mouse no\nseat seat0 hide_cursor 100\n')
env=environment();env.update(XDG_RUNTIME_DIR=str(runtime),WLR_BACKENDS='headless',WLR_HEADLESS_OUTPUTS='2',WLR_RENDERER='pixman')
binary=lab/'swayfx-mosaic';processes=[];files=[];failure=None;compositor=None;events=[]
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

def inject(action,x,y,kind='move'):
    reserve(lab,kind)
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
    return {'id':owner['id'],'scene':[x,y,w,h],'window_rect':win,'horizontal_content':[x+win['x'],win['width']],'raw':line,'IPC':owner}

# WHY: global focus becomes H2 after the forbidden-region click. Workspace and
# owner IDs, rather than global command context, bind the standard-return test.
focus_states=[]
def snapshot(tag):
    tree=ipc('-t','get_tree');outputs=ipc('-t','get_outputs');workspaces=ipc('-t','get_workspaces')
    row={'tag':tag,'ns':time.monotonic_ns(),'tree':tree,'outputs':outputs,'workspaces':workspaces,
         'focused':[n['id'] for n in nodes(tree) if n.get('focused')]}
    focus_states.append(row);save(lab,'focus-states',focus_states)
    save(lab,tag+'-snapshot',row)
    return tree

def workspace(tree,name):
    return next(n for n in nodes(tree) if n['type']=='workspace' and n['name']==name)

def scene(output):
    rows=[s for s in log('compositor').splitlines() if 'PI_SCENE output='+output+' ' in s]
    assert rows,'scene trace absent';line=rows[-1]
    m=re.search(r'workspace=(\d+) layout=(\d+) scroll=(-?[\d.]+) tile_scene=(-?\d+),(-?\d+) clip_valid=(\d+) clip=(-?\d+),(-?\d+),(\d+),(\d+)',line);assert m,line
    v=list(map(float,m.groups()))
    return {'workspace':int(v[0]),'layout_enum':int(v[1]),'scroll':v[2],
            'tile_local':v[3:5],'clip_valid':bool(v[5]),'clip_local':v[6:10],
            'global_clip':[(-800 if output=='HEADLESS-1' else 0)+v[3]+v[6],v[4]+v[7],v[8],v[9]],'raw':line}

def camera(tree):return workspace(tree,'1')['mosaic']['rows'][0]['scroll_x']
def buttons(name):return [x for x in log(name).splitlines() if x.startswith('BUTTON ')]
def measured_click(kind,point):
    before={n:len(buttons(n)) for n in ['target','reference','filler']}
    inject('right',*point,kind=kind)
    row={'global_point':point,'events':{n:buttons(n)[before[n]:] for n in before},
         'tails':{n:log(n).splitlines()[-15:] for n in before},'ns':time.monotonic_ns()}
    save(lab,kind,row);return row

def whole(tag,baseline,im):
    value=compare(baseline,im);save(lab,tag,value);assert value['equal'],'whole H2 differs: '+tag
    return value

try:
    compositor=spawn('compositor',[binary,'-d','-c',run/'config'])
    sock=wait(lambda:next(iter(runtime.glob('sway-ipc.*.sock')),None))
    display=wait(lambda:next((x for x in runtime.glob('wayland-*') if x.is_socket()),None))
    env.update(SWAYSOCK=str(sock),WAYLAND_DISPLAY=display.name)
    maps=Path(f'/proc/{compositor.pid}/maps').read_text();(run/'proc-maps.txt').write_text(maps)
    exe=Path(f'/proc/{compositor.pid}/exe').resolve();assert exe==binary and sha(exe)==sha(binary)
    paths=sorted({line.split()[-1] for line in maps.splitlines() if len(line.split())>=6 and line.split()[-1].startswith('/')})
    wl=Path('/usr/lib/libwlroots-0.20.so').resolve()
    assert not any('libscenefx' in x for x in paths)
    assert [Path(x).resolve() for x in paths if 'libwlroots' in x]==[wl]
    assert sha(wl)=='7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837'
    assert not any('/swayfx-mosaic-' in x and Path(x)!=binary for x in paths)
    save(lab,'dependency-mappings',{'status':'PASS','exe':str(exe),'paths':paths,'wlroots_sha256':sha(wl),'SceneFX_shared':False})
    outputs=ipc('-t','get_outputs');actual={o['name']:(o['rect']['x'],o['rect']['y'],o['rect']['width'],o['rect']['height'],o['scale'],o['transform']) for o in outputs if o['active']}
    assert actual=={'HEADLESS-1':(-800,0,800,600,1.0,'normal'),'HEADLESS-2':(0,0,800,600,1.0,'normal')},actual
    save(lab,'output-geometry',outputs)
    pointer=spawn('pointer',[lab/'pointer-daemon','1600','600'],stdin=True);wait(lambda:'POINTER_READY' in log('pointer'))
    cmd('workspace 2');ref=spawn('reference',[lab/'static-reference'],stdin=True,extra={'WAYLAND_DEBUG':'1'})
    reference=wait(lambda:find('org.mosaic.StaticReference'));refid=reference['id']
    cmd(f'[con_id={refid}] border none')
    cmd('workspace 1');filler=spawn('filler',[lab/'static-reference'],stdin=True)
    wait(lambda:len([n for n in nodes(ipc('-t','get_tree')) if n.get('app_id')=='org.mosaic.StaticReference'])==2)
    target=spawn('target',[lab/'saved-client'],stdin=True,extra={'WAYLAND_DEBUG':'1'})
    wait(lambda:find('org.mosaic.SavedBufferProbe'))
    cmd('layout mosaic');time.sleep(.6)
    tree=snapshot('before-camera');owner=find('org.mosaic.SavedBufferProbe');targetid=owner['id'];wsid=workspace(tree,'1')['id']
    before=measure(owner);sc_before=scene('HEADLESS-1');scroll_before=camera(tree)
    assert sc_before['scroll']==scroll_before
    x,w=before['horizontal_content'];desired=-w//2;delta=x-desired
    reserve(lab,'camera');cmd(f'layout mosaic scroll {delta}')
    time.sleep(.6);owner=find('org.mosaic.SavedBufferProbe');after=measure(owner)
    tree=snapshot('preflight');scroll_after=camera(tree);sc_after=scene('HEADLESS-1')
    save(lab,'camera-calibration',{'before':scroll_before,'delta':delta,'desired_left':desired,'after':scroll_after,'before_scene':sc_before,'after_scene':sc_after})
    assert scroll_after==scroll_before+delta and sc_after['scroll']==scroll_after
    x,w=after['horizontal_content'];assert x<0<x+w and -800<x
    assert sc_after['clip_valid'] and sc_after['global_clip']==[-800,0,800,600]
    assert sc_after['workspace']==wsid
    reference=next(n for n in nodes(tree) if n['id']==refid)
    assert reference['pid']==ref.pid and reference['border']=='none' and reference['current_border_width']==0 and reference['visible']
    assert reference in list(nodes(workspace(tree,'2')))
    assert reference['rect']=={'x':0,'y':0,'width':800,'height':600}
    assert not reference['focused'] and owner['focused']
    assert next(z for z in ipc('-t','get_workspaces') if z['focused'])['name']=='1'
    save(lab,'owner-geometry',{'before':before,'after':after,'reference':reference,'last_client_commit':[s for s in log('target').splitlines() if s.startswith('COMMIT ')][-1]})
    save(lab,'clip-observations',{'mosaic':sc_after,'H2':scene('HEADLESS-2')})
    inject('move',-790,590);time.sleep(.6)
    baseline=capture('h2-reference-1','HEADLESS-2');time.sleep(.6);second=capture('h2-reference-2','HEADLESS-2')
    comparison=compare(baseline,second)
    save(lab,'reference-preflight',{'H2_REFERENCE_STABLE':comparison['equal'],'H2_WHOLE_RGB_EQUAL':comparison['equal'],'reference':reference,'focus':focus_states[-1]['focused'],'hashes':{n:sha(run/n) for n in ['h2-reference-1.png','h2-reference-2.png']}})
    save(lab,'reference-pixel-analysis',comparison)
    assert comparison['equal'] and all(c==(48,48,56) for c in baseline.get_flattened_data()),'reference preflight failed'
    left=capture('h1-mosaic','HEADLESS-1');right=capture('h2-mosaic','HEADLESS-2')
    visible=analyze(left);forbidden=analyze(right)
    save(lab,'permitted-pixels',visible);save(lab,'forbidden-pixels',forbidden)
    assert visible['count']>0 and forbidden['count']==0
    whole('v1-H2-comparison',baseline,right)
    bx,by,bw,bh=visible['bbox'];assert bx-800==x and bw==800
    last_commit=[s for s in log('target').splitlines() if s.startswith('COMMIT ')][-1]
    dimensions=re.search(r'size=(\d+)x(\d+)',last_commit);assert dimensions
    assert int(dimensions[1])==w and bh-by==int(dimensions[2])
    # Paint proves vertical position; only horizontal continuation is inferred
    # from the applied scene, IPC offset and actual configured client width.
    px,py=interior(left);permitted=(px-800,py)
    forbidden_point=(min(100,int(x+w)-30),py);assert forbidden_point[0]>=20
    assert x<forbidden_point[0]<x+w and right.getpixel(forbidden_point)==(48,48,56)
    save(lab,'click-points',{'permitted':permitted,'forbidden':forbidden_point,'paint_bbox':visible['bbox'],'horizontal_content':[x,w]})
    click=measured_click('visible_click',permitted);events_visible=button_pair(click['events']['target'])
    assert not click['events']['reference'] and not click['events']['filler']
    save(lab,'target-input',{'status':'PASS visible','point':permitted,'events':events_visible})
    tree=snapshot('after-visible');assert camera(tree)==scroll_after
    assert measure(find('org.mosaic.SavedBufferProbe'))['horizontal_content']==[x,w]
    click=measured_click('forbidden_click',forbidden_point);events_reference=button_pair(click['events']['reference'])
    assert not click['events']['target'] and not click['events']['filler'],'invisible target or wrong client input'
    save(lab,'reference-input',{'status':'PASS','point':forbidden_point,'events':events_reference,'invisible_target_events':click['events']['target']})
    tree=snapshot('after-reference');assert camera(tree)==scroll_after
    assert next(n for n in nodes(tree) if n['id']==refid)['focused']
    inject('move',-790,590);time.sleep(.6)
    whole('post-click-H2-comparison',baseline,capture('h2-after-clicks','HEADLESS-2'))
    cmd(f'[con_id={targetid}] layout splith');time.sleep(.6)
    tree=snapshot('standard');standard_ws=workspace(tree,'1');assert standard_ws['id']==wsid and standard_ws['layout']=='splith'
    standard_owner=next(n for n in nodes(standard_ws) if n['id']==targetid);assert standard_owner['visible']
    standard_left=capture('h1-standard','HEADLESS-1');standard_right=capture('h2-standard','HEADLESS-2')
    whole('standard-H2-comparison',baseline,standard_right)
    standard_scene=scene('HEADLESS-1');standard_h2=scene('HEADLESS-2')
    assert standard_scene['workspace']==wsid and not standard_scene['clip_valid'] and not standard_h2['clip_valid']
    sx,sy=interior(standard_left);point=(sx-800,sy)
    click=measured_click('standard_click',point);events_standard=button_pair(click['events']['target'])
    assert not click['events']['reference'] and not click['events']['filler']
    snapshot('after-standard-click');inject('move',-790,590);time.sleep(.6)
    whole('final-H2-comparison',baseline,capture('h2-standard-after-click','HEADLESS-2'))
    save(lab,'standard-return',{'status':'STANDARD_RETURN_PASS','workspace':standard_ws,'owner':measure(standard_owner),'scene':standard_scene,'H2_scene':standard_h2,'point':point,'events':events_standard,'pixels':analyze(standard_left),'H2_equal':True})
    assert all(p.poll() is None for p in [target,ref,filler,pointer])
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
    shutil.rmtree(runtime)
    save(lab,'runtime',{'status':'PASS' if failure is None else 'INCONCLUSIVE','failure':failure,'duration_seconds':time.monotonic()-started,'process_exit_codes':[{'pid':x.pid,'argv':x.args,'exit':x.returncode} for x in processes],'runtime_removed':str(runtime),'cleanup':'owned groups reaped, runtime removed'})
    damage=[s for s in log('compositor').splitlines() if 'TEMPORAL_DAMAGE ' in s] if (run/'compositor.log').exists() else []
    save(lab,'damage-analysis',{'extents':damage,'all_frames':'NOT TESTED','PNG_native_buffer_identity':'NOT PROVEN','client_damage':'wl_surface_damage_buffer full SHM at actual commits; see client source/protocol logs'})
print('STATIC_FOLLOWUP',failure or 'PASS')
if failure:raise SystemExit(1)
