#!/usr/bin/env python3
"""One immutable-static headless process, two genuinely grabbed XDG chains.

WHY: outside dismissal must not preclude standard-return measurements.
CONTRACT: every mutation/injection/capture consumes a persistent reservation.
INVARIANT: only owned groups/sockets; actual codes survive terminal IPC failure.
"""
import argparse
import fcntl
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
from PIL import Image
from support import sha,save,reserve,environment,verify
from model import *
from authorization import authorize
from observations import applied_model,output_model,viewport_model,verify_owner_occlusion
from ipc_predicates import nodes,workspace,validate_outputs,validate_reference,measure_owner,scene_from_log,validate_camera
from predicates import Defect,COLORS,paint,point,equal,reference,protocol,geometry,mapped,pair,dismissal,root_clip,popup_pixels,terminal,terminal_exchange

p=argparse.ArgumentParser();p.add_argument('lab',type=Path);p.add_argument('--future-authorization',type=Path)
args=p.parse_args();lab=args.lab.resolve()
# Fail CLOSED before owner/lock/ledger/runtime creation or any subprocess.
auth=authorize(lab,args.future_authorization)
OWNER=Path(auth['owner_registry']);BINARY=Path(auth['binary']);BINARY_SHA=auth['binary_sha256'];WLROOTS_SHA=auth['wlroots_sha256']
require(not __import__('sys').flags.optimize,'assertions required')
assert OWNER.read_text().strip()==str(lab) and (lab/'campaign-owner').read_text().strip()==str(OWNER)
lock=(lab/'run.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
freeze=verify(lab/'results/fixture-freeze-sha256.txt');gate=json.loads((lab/'results/offline-gate.json').read_text())
assert gate['marker']=='SWAYFX_MOSAIC_STATIC_NESTED_GEOMETRY_OFFLINE_GATE=READY_FOR_NEW_RUNTIME' and gate['fixture_sha256']==freeze['sha256']
assert json.loads((lab/'results/binary-identity.json').read_text())['status']=='PASS'
assert sha(BINARY)==sha(lab/'swayfx-mosaic')==BINARY_SHA
assert not (lab/'run').exists(),'run path already used'
reserve(lab,'run')
run=lab/'run';run.mkdir();runtime=Path(tempfile.mkdtemp(prefix='msng-',dir='/tmp'));runtime.chmod(0o700)
assert len(os.fsencode(str(runtime/'sway-ipc.4294967295.2147483647.sock')))<108
(run/'runtime-path').write_text(str(runtime)+'\n')
config='output HEADLESS-1 resolution 800x600 scale 1 transform normal position -800 0\noutput HEADLESS-2 resolution 800x600 scale 1 transform normal position 0 0\nworkspace 1 output HEADLESS-1\nworkspace 2 output HEADLESS-2\nfocus_follows_mouse no\nseat seat0 hide_cursor 100\n'
(run/'config').write_text(config)
env=environment();env.update(XDG_RUNTIME_DIR=str(runtime),WLR_BACKENDS='headless',WLR_HEADLESS_OUTPUTS='2',WLR_RENDERER='pixman')
processes=[];files=[];comp=None;pointer=None;failure=None;stage='startup';measures=False;rescue=False
started=time.monotonic();finished=threading.Event();expired=threading.Event();chains={};clips={};root_boundary={};captures=[];clicks=[];owners={};camera_rows=[]

def event(kind,**data):
    with (run/'events.jsonl').open('a') as out:out.write(json.dumps(dict(ns=time.monotonic_ns(),kind=kind,**data))+'\n')

def spawn(name,argv,debug=False):
    assert not expired.is_set()
    out=(run/(name+'.log')).open('w');files.append(out)
    proc=subprocess.Popen(list(map(str,argv)),stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,
        text=True,start_new_session=True,env={**env,**({'WAYLAND_DEBUG':'1'} if debug else {})})
    processes.append((name,proc));event('spawn',name=name,pid=proc.pid,argv=list(map(str,argv)));return proc

def stop_owned(sig=signal.SIGTERM):
    for name,proc in list(processes):
        try:os.killpg(proc.pid,sig)
        except ProcessLookupError:pass

def watchdog():
    while not finished.wait(.1):
        if time.monotonic()-started>150 or any(p.stat().st_size>32*1024*1024 for p in run.glob('*.log')):
            expired.set();stop_owned();return

thread=threading.Thread(target=watchdog,daemon=True);thread.start()

def log(name):return (run/(name+'.log')).read_text(errors='replace')

def wait(fn,seconds=6):
    end=min(time.monotonic()+seconds,started+143)
    while time.monotonic()<end:
        if expired.is_set():raise RuntimeError('deadline/log bound exceeded')
        if comp is not None and comp.poll() is not None:raise RuntimeError('unexpected compositor exit '+str(comp.returncode))
        value=fn()
        if value:return value
        time.sleep(.025)
    raise RuntimeError('fixture wait timeout at '+stage)

def ipc(*args):
    assert sock.is_relative_to(runtime) and sock.is_socket()
    r=subprocess.run(['swaymsg','-s',str(sock),*args],env=env,capture_output=True,text=True,timeout=4)
    event('ipc',args=args,exit=r.returncode,stdout=r.stdout,stderr=r.stderr)
    assert r.returncode==0,('IPC failure',args,r.returncode)
    return json.loads(r.stdout)

def cmd(text):
    assert all(x['success'] for x in ipc(text)),text

def snapshot(tag):
    tree=ipc('-t','get_tree');outputs=ipc('-t','get_outputs');ws=ipc('-t','get_workspaces')
    data=dict(ns=time.monotonic_ns(),tree=tree,outputs=outputs,workspaces=ws,focused=[n['id'] for n in nodes(tree) if n.get('focused')])
    save(lab,tag+'-snapshot',data);return data

def find(app,pid):
    candidates=[n for n in nodes(ipc('-t','get_tree')) if n.get('app_id')==app and n.get('pid')==pid]
    assert len(candidates)<=1
    return candidates[0] if candidates else None

def capture(tag,output):
    reserve(lab,'capture');time.sleep(.20)
    path=run/(tag+'.png');assert not path.exists()
    before=time.monotonic_ns()
    r=subprocess.run(['grim','-s','1','-o',output,str(path)],env=env,capture_output=True,text=True,timeout=4)
    event('capture',file=path.name,output=output,start_ns=before,exit=r.returncode,stderr=r.stderr)
    assert r.returncode==0
    im=Image.open(path).convert('RGB');assert im.size==(800,600)
    captures.append(dict(file=path.name,output=output,sha256=sha(path),ns=time.monotonic_ns()))
    save(lab,'captures',captures);return im

def inject(action,xy,grab=False):
    assert action in ['left','right','move'] and len(xy)==2
    x,y=xy;assert type(x) is int and type(y) is int and -800<=x<800 and 0<=y<600
    kinds=['move'] if action=='move' else ['click','move']+(['grab'] if grab else [])
    reserve(lab,*kinds)
    marker=f'INJECT_DONE {action} {x+800},{y}';before=log('pointer').count(marker)
    pointer.stdin.write(f'{action} {x+800} {y}\n');pointer.stdin.flush()
    wait(lambda:log('pointer').count(marker)>before);time.sleep(.18)
    event('injection',action=action,global_point=xy,sent=[x+800,y],extent=[1600,600],grab=grab)

def buttons(name):
    return [s for s in log(name).splitlines() if s.startswith(('POINTER_BUTTON ','BUTTON '))]

def click(tag,name,xy,grab=False,action='right'):
    before={n:len(buttons(n)) for n in [name,'reference','filler']}
    t0=time.monotonic_ns();inject(action,xy,grab)
    row=dict(tag=tag,global_point=xy,action=action,start_ns=t0,end_ns=time.monotonic_ns(),events={n:buttons(n)[before[n]:] for n in before})
    clicks.append(row);save(lab,'clicks',clicks);return row

def delivery(row,name,target):
    assert not row['events']['reference'] and not row['events']['filler'],'other client received visible popup button'
    return pair(row['events'][name],target)

def correlate_pointer(name,xy,rect,target):
    # WHY: an injection request alone does not identify applied popup origin.
    rows=re.findall(rf'POINTER_(?:ENTER|MOTION) target={target} .*?x=([\d.-]+) y=([\d.-]+)',log(name))
    assert rows,'missing pointer local coordinates'
    local=list(map(float,rows[-1]));expected=[xy[0]-rect[0],xy[1]-rect[1]]
    prov=Provenance(1,1,'pointer-sample','actual pointer log')
    pointer_local(xy,Rect(Space.GLOBAL,*rect,prov),local)
    return dict(global_point=xy,local=local,rectangle=rect)

def close_client(proc,name,value):
    proc.stdin.write(value+'\n');proc.stdin.flush()
    code=proc.wait(timeout=3);assert code==0,(name,code)
    assert 'TOPLEVEL DESTROY' in log(name)
    wait(lambda:find('org.mosaic.NestedGrabProbe',proc.pid) is None)

# CONTRACT: applied owner, paint and XDG surface size are distinct measurements.
def owner_state(name,proc,tag):
    snap=snapshot(tag);ws=workspace(snap['tree'],'1');owner=next(n for n in nodes(ws) if n.get('pid')==proc.pid)
    assert owner['app_id']=='org.mosaic.NestedGrabProbe' and owner['shell']=='xdg_shell' and owner['visible']
    assert ws['output']=='HEADLESS-1' and owner['focused'] and snap['focused']==[owner['id']]
    measured=measure_owner(log('compositor'),owner);scene=scene_from_log(log('compositor'),'HEADLESS-1')
    assert scene['workspace']==ws['id']
    measured['workspace']=ws['id']
    return snap,ws,owner,measured,scene

def open_chain(name):
    global stage
    reserve(lab,'chain');cmd('workspace 1');proc=spawn(name,[lab/'nested-client','static_cross'],debug=True)
    wait(lambda:find('org.mosaic.NestedGrabProbe',proc.pid) and 'TOPLEVEL MAP ' in log(name));time.sleep(.6)
    snap,ws,owner,before,sc=owner_state(name,proc,name+'-before-camera')
    assert ws['layout']=='mosaic'
    current=ws['mosaic']['rows'][0]['scroll_x'];x,w=before['horizontal_content'];desired=-w//2;delta=int(x-desired)
    if delta:
        reserve(lab,'camera');cmd(f'[con_id={owner["id"]}] layout mosaic scroll {delta}');time.sleep(.6)
    snap,ws,owner,after,scene=owner_state(name,proc,name+'-applied')
    validate_camera(current,ws['mosaic']['rows'][0]['scroll_x'],delta,scene)
    assert scene['clip_valid'] and scene['global_clip']==[-800,0,800,600]
    assert not scene_from_log(log('compositor'),'HEADLESS-2')['clip_valid']
    refstate=validate_reference(snap,refid,ref.pid)
    camera_rows.append(dict(chain=name,before=current,delta=delta,after=scene['scroll'],before_owner=before,after_owner=after,scene=scene,reference=refstate))
    save(lab,'camera-calibration',camera_rows)
    if name=='E1':
        stage='reference';inject('move',[-790,590]);time.sleep(.5)
        first=capture('H2-reference-1','HEADLESS-2');time.sleep(.6)
        second=capture('H2-reference-2','HEADLESS-2');cmp=reference(first,second)
        save(lab,'reference-stability',dict(status='PASS',comparison=cmp,reference=refstate,interval='>=600ms',focus=snap['focused']))
        global baseline
        baseline=first
    root_boundary[name]=time.monotonic_ns()
    stage=name+'-open-A';topim=capture(name+'-top','HEADLESS-1')
    topbox=paint(topim,'TOPLEVEL')['bbox'];assert topbox
    # Tiled scene+window offset is checked against actual painted blue origin.
    applied=applied_model(after,owner,log(name),name+'-mosaic')
    content_rect=content(applied);origin=[content_rect.x,content_rect.y]
    out=output_model(snap,'HEADLESS-1',content_rect.provenance)
    verify_paint(content_rect,out,topbox,paint(topim,'TOPLEVEL')['count'],viewport_model(scene,content_rect.provenance))
    assert topbox[0]-800==origin[0]
    assert origin[1]==after['scene'][1]+owner['deco_rect']['height']+owner['window_rect']['y']
    owners[name]=dict(id=owner['id'],pid=proc.pid,workspace=ws['id'],logical_rect=owner['rect'],applied=after,drawn_size=[420,320],paint=paint(topim,'TOPLEVEL'),content_origin=origin)
    save(lab,'applied-owner-geometry',owners)
    top_point=point(topim,'TOPLEVEL',-800)
    require(0 <= top_point[0]-origin[0] < applied.native.rectangle.width and 0 <= top_point[1]-origin[1] < applied.native.rectangle.height, 'opening-point-native-input-bounds')
    cp=click(name+'-open-A',name,top_point,True,'left')
    wait(lambda:'POPUP_A MAP ' in log(name));time.sleep(.25)
    correlate_pointer(name,top_point,content_rect.values(),'TOPLEVEL')
    aim=capture(name+'-A','HEADLESS-1');ap=point(aim,'POPUP_A',-800)
    stage=name+'-open-B';click(name+'-open-B',name,ap,True,'left')
    wait(lambda:'POPUP_B MAP ' in log(name));time.sleep(.3)
    prot=protocol(log(name));g=geometry(log(name),origin,content_rect.provenance)
    # Actual configure/ACK/map drives geometry; requests are predictions only.
    g['positioner_prediction']={'flags':0,'A':[100,80,350,170],'B':[100,60,300,130],'evidence':'source-backed prediction only'}
    require(all(value=='EXERCISED' for value in g['crossing'].values()),'popup crossing NOT EXERCISED')
    correlate_pointer(name,ap,g['A'],'POPUP_A')
    left=capture(name+'-mosaic-H1','HEADLESS-1');right=capture(name+'-mosaic-H2','HEADLESS-2')
    rgb=popup_pixels(left,right,g,True,baseline)
    clip=root_clip(log('compositor'),origin,True,owner['id'],root_boundary[name],time.monotonic_ns())
    chains[name]=dict(protocol=prot,geometry=g,pixels=rgb,owner=owners[name])
    clips[name]=dict(tile=scene,root=clip,child=clip['child'])
    save(lab,'grab-serials',{n:v['protocol']['grabs'] for n,v in chains.items()})
    save(lab,'xdg-protocol-order',{n:v['protocol'] for n,v in chains.items()})
    save(lab,'popup-root-geometry',{n:v['geometry']['A'] for n,v in chains.items()})
    save(lab,'popup-nested-geometry',{n:v['geometry']['B'] for n,v in chains.items()})
    save(lab,'applied-clips',clips);save(lab,'mosaic-pixels',{n:v['pixels'] for n,v in chains.items()})
    return proc,owner,g,left

try:
    comp=spawn('compositor',[lab/'swayfx-mosaic','-d','-c',run/'config'])
    sock=wait(lambda:next(iter(runtime.glob('sway-ipc.*.sock')),None))
    display=wait(lambda:next((x for x in runtime.glob('wayland-*') if x.is_socket()),None))
    env.update(WAYLAND_DISPLAY=display.name,SWAYSOCK=str(sock))
    assert Path(f'/proc/{comp.pid}/exe').resolve()==lab/'swayfx-mosaic'
    maps=Path(f'/proc/{comp.pid}/maps').read_text();(run/'proc-maps.txt').write_text(maps)
    paths=sorted({s.split()[-1] for s in maps.splitlines() if len(s.split())>=6 and s.split()[-1].startswith('/')})
    wl=Path('/usr/lib/libwlroots-0.20.so').resolve()
    assert [Path(x).resolve() for x in paths if 'libwlroots' in x]==[wl] and sha(wl)==WLROOTS_SHA
    assert not any('libscenefx' in x for x in paths)
    save(lab,'dependency-mappings',dict(status='PASS',paths=paths,wlroots=str(wl),wlroots_sha256=sha(wl),SceneFX_shared=False))
    outputs=ipc('-t','get_outputs');validate_outputs(outputs);save(lab,'output-geometry',outputs)
    pointer=spawn('pointer',[lab/'pointer-daemon']);wait(lambda:'POINTER_READY' in log('pointer'))
    cmd('workspace 2');ref=spawn('reference',[lab/'static-reference'],debug=True)
    rn=wait(lambda:find('org.mosaic.StaticReference',ref.pid));refid=rn['id'];cmd(f'[con_id={refid}] border none')
    cmd('workspace 1');filler=spawn('filler',[lab/'static-reference'],debug=True)
    wait(lambda:find('org.mosaic.StaticReference',filler.pid));cmd('layout mosaic')
    E1,owner1,g1,im1=open_chain('E1')
    stage='E1-visible-B';xy=point(im1,'POPUP_B',-800);row=click(stage,'E1',xy)
    result=delivery(row,'E1','POPUP_B');coords=correlate_pointer('E1',xy,g1['B'],'POPUP_B');mapped(log('E1'))
    save(lab,'mosaic-input',dict(status='PASS',pair=result,coordinates=coords,click=row))
    stage='E1-forbidden-B';B=g1['B'];xy=[int((max(0,B[0])+min(800,B[0]+B[2]))//2),B[1]+30]
    assert B[0]<=xy[0]<B[0]+B[2] and 8<=xy[0]<792
    cut=len(log('E1'));row=click(stage,'E1',xy);time.sleep(.3)
    ds=dismissal(log('E1')[cut:],row['events']['E1']);save(lab,'dismissal',ds)
    refpair=row['events']['reference'];assert len(refpair) in [0,2]
    save(lab,'forbidden-input',dict(status='PASS',click=row,popup_events=row['events']['E1'],reference_events=refpair,dismissal=ds))
    inject('move',[-790,590]);clean=capture('E1-dismissed-H2','HEADLESS-2')
    assert equal(baseline,clean)['equal'],'E1 dismissal residue'
    close_client(E1,'E1','close_owner')
    E2,owner2,g2,im2=open_chain('E2');assert owner2['id']!=owner1['id'] and E2.pid!=E1.pid
    s1=[g['serial'] for g in chains['E1']['protocol']['grabs']];s2=[g['serial'] for g in chains['E2']['protocol']['grabs']]
    assert len(set(s1+s2))==4 and max(s1)<min(s2),'serial reuse across chains'
    stage='E2-standard';mapped(log('E2'));standard_boundary=time.monotonic_ns();reserve(lab,'transition');cmd(f'[con_id={owner2["id"]}] layout splith');time.sleep(.6)
    snap,ws,std_owner,std_measure,std_scene=owner_state('E2',E2,'standard')
    assert ws['id']==owners['E2']['workspace'] and ws['layout']=='splith'
    if std_scene['clip_valid'] or std_scene['layout_enum']!=1:raise Defect('standard tiled clip retained')
    mapped(log('E2'))
    stdleft=capture('standard-H1','HEADLESS-1');stdright=capture('standard-H2','HEADLESS-2')
    blue=paint(stdleft,'TOPLEVEL')['bbox'];assert blue
    stdapplied=applied_model(std_measure,std_owner,log('E2'),'E2-standard')
    stdcontent=content(stdapplied);stdorigin=[stdcontent.x,stdcontent.y]
    fresh_standard(applied_model(owners['E2']['applied'],owners['E2']['applied']['IPC'],log('E2'),'E2-mosaic').scene,stdapplied.scene)
    # Blue is occluded by A/B; full pixel mask checked against actual geometry below.
    assert blue[0]-800==stdorigin[0] and blue[1]==stdorigin[1]
    stdg=geometry(log('E2'),stdorigin,stdcontent.provenance);stdclip=root_clip(log('compositor'),stdorigin,False,owner2['id'],standard_boundary,time.monotonic_ns())
    stdrgb=popup_pixels(stdleft,stdright,stdg,False,baseline)
    save(lab,'standard-return',dict(status='PASS',same_workspace=ws['id'],owner=std_owner,applied=std_measure,scene=std_scene,root_clip=stdclip,child_clip='no independent clip in exact source; standard B pixels/input exercise removed inherited boundary',geometry=stdg,mapped_before_and_after=True,no_prior_popup_done=True))
    verify_owner_occlusion(stdleft,stdright,stdcontent,stdg,False)
    save(lab,'standard-popup-pixels',stdrgb)
    stage='E2-standard-B';xy=point(stdright,'POPUP_B',0);row=click(stage,'E2',xy)
    Bpair=delivery(row,'E2','POPUP_B');Bcoords=correlate_pointer('E2',xy,stdg['B'],'POPUP_B');mapped(log('E2'))
    E2.stdin.write('close_b\n');E2.stdin.flush();wait(lambda:'COMMAND close_b DONE' in log('E2'))
    assert 'POPUP_B DESTROY ' in log('E2') and 'POPUP_A DESTROY ' not in log('E2') and 'POPUP_A POPUP_DONE ' not in log('E2')
    stage='E2-standard-A';Aimage=capture('standard-A-H2','HEADLESS-2');assert paint(Aimage,'POPUP_B')['count']==0
    xy=point(Aimage,'POPUP_A',0);rowA=click(stage,'E2',xy);Apair=delivery(rowA,'E2','POPUP_A')
    Acoords=correlate_pointer('E2',xy,stdg['A'],'POPUP_A')
    save(lab,'standard-popup-input',dict(status='PASS',B=Bpair,A=Apair,B_coordinates=Bcoords,A_coordinates=Acoords,explicit_B_close=True,A_survived=True))
    stage='E2-cleanup';close_client(E2,'E2','close_owner');time.sleep(.35)
    final=capture('final-H2','HEADLESS-2');assert equal(baseline,final)['equal'],'final H2 residue'
    assert not any(paint(final,n)['count'] for n in ['POPUP_A','POPUP_B'])
    snap=snapshot('final');validate_reference(snap,refid,ref.pid)
    assert filler.poll() is None and ref.poll() is None
    measures=True;event('measurements-completed',status='PASS');stage='completed'
except Exception as exc:
    failure=dict(type=type(exc).__name__,message=str(exc),stage=stage,verdict='BLOCKED' if isinstance(exc,Defect) else 'INCONCLUSIVE')
    event('failure',**failure)
finally:
    # WHY: shutdown transport outcome is not folded into check=True scientific gates.
    exit_data=None
    if comp is not None and comp.poll() is None and 'sock' in globals() and sock.is_socket():
        # WHY: record transport evidence before wait can raise or time out.
        def record_terminal(stdout,stderr):
            (run/'terminal-exit.stdout').write_text(stdout)
            (run/'terminal-exit.stderr').write_text(stderr)
        exit_data=terminal_exchange(subprocess.run,comp.wait,
            ['swaymsg','-s',str(sock),'exit'],env,measures,
            lambda:log('compositor'),
            lambda:any(re.search(r'wl_display[^\n]*\.error\(|protocol error',log(n),re.I)
                       for n,_ in processes if n not in ['compositor','pointer']),
            expired.is_set,record_terminal)
    if exit_data is None:exit_data=dict(scientific_cleanup_pass=False,compositor_exit=comp.poll() if comp else None,measurements_completed=measures)
    codes=[]
    for name,proc in reversed(processes):
        if proc.poll() is None:
            try:proc.wait(timeout=.7)
            except subprocess.TimeoutExpired:
                if name=='pointer':proc.stdin.close() # normal EOF destroys virtual pointer
                else:
                    rescue=True
                    try:os.killpg(proc.pid,signal.SIGTERM)
                    except ProcessLookupError:pass
                try:proc.wait(timeout=.7)
                except subprocess.TimeoutExpired:
                    rescue=True
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    proc.wait(timeout=.7)
        codes.append(dict(name=name,pid=proc.pid,exit=proc.returncode))
        if proc.stdin and not proc.stdin.closed:proc.stdin.close()
    finished.set();thread.join(timeout=1)
    for out in files:out.close()
    for name,proc in processes:
        try:os.killpg(proc.pid,0)
        except ProcessLookupError:pass
        else:rescue=True;os.killpg(proc.pid,signal.SIGKILL)
    assert all(not Path('/proc',str(row['pid'])).exists() for row in codes),'owned process residual'
    private_sockets=[str(p) for p in runtime.iterdir() if p.is_socket()]
    shutil.rmtree(runtime)
    exit_data.update(rescue_cleanup=rescue,owned_process_codes=codes)
    exit_data['scientific_cleanup_pass']=bool(exit_data['scientific_cleanup_pass'] and not rescue and all(row['exit']==0 for row in codes))
    exit_data['all_owned_reaped']=all(not Path('/proc',str(row['pid'])).exists() for row in codes)
    if rescue:exit_data['scientific_cleanup_pass']=False
    if measures and (not exit_data['scientific_cleanup_pass'] or any(r['exit']!=0 for r in codes)):
        failure=dict(type='TerminalCleanupFailure',message='terminal/process evidence failed',stage='completed',verdict='INCONCLUSIVE')
    save(lab,'terminal-exit',exit_data)
    save(lab,'cleanup',dict(status='PASS' if not rescue else 'RESCUE',runtime=str(runtime),runtime_removed=not runtime.exists(),owned_processes=codes,sockets_before_owned_directory_removal=private_sockets,private_socket_residual=False))
    save(lab,'runtime',dict(status='PASS' if failure is None else failure['verdict'],failure=failure,stage=stage,measurements_completed=measures,duration_seconds=time.monotonic()-started,watchdog=expired.is_set(),rescue_cleanup=rescue,runner_exit=0 if failure is None else 1))
    verify(lab/'results/fixture-freeze-sha256.txt')
print('RUNTIME', 'PASS' if failure is None else failure)
raise SystemExit(0 if failure is None else 1)
