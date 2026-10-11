import json, os, pathlib, signal, subprocess, sys, time
LAB=pathlib.Path(__file__).resolve().parent
case=sys.argv[1]
assert case in ('control','private_standard','private_mosaic','private_mosaic_hit')
mode=sys.argv[2] if len(sys.argv)>2 else ''
assert mode in ('','boundary_left','boundary_right','standard_return',
                'lifecycle_switch','lifecycle_destroy','outside_left','visible_left',
                'fully_visible')
run=LAB/('run-'+case+('-'+mode if mode else ''))
run.mkdir(exist_ok=True)
run.chmod(0o700)
config=('output HEADLESS-1 resolution 800x600 position 0 0\n'
        'output HEADLESS-2 resolution 800x600 position 800 0\n'
        'workspace 1 output HEADLESS-1\nworkspace 2 output HEADLESS-2\n'
        'focus_follows_mouse no\n')
(run/'config').write_text(config)
e=os.environ.copy()
e.update(XDG_RUNTIME_DIR=str(run),WLR_BACKENDS='headless',WLR_HEADLESS_OUTPUTS='2',WLR_RENDERER='pixman')
e.pop('WAYLAND_DISPLAY',None);e.pop('SWAYSOCK',None)
compositor_env=e.copy()
if case.startswith('private'):
    binary=LAB/'mosaic-build/sway/swayfx-mosaic'
    compositor_env['LD_LIBRARY_PATH']=str(LAB/'scenefx-build')
else:
    binary=pathlib.Path('/usr/bin/sway')
    compositor_env.pop('LD_LIBRARY_PATH',None)
e.pop('LD_LIBRARY_PATH',None)
files=[];children=[]
def spawn(args,name,debug=False):
    f=(run/name).open('w');files.append(f)
    env=e.copy()
    if debug:env['WAYLAND_DEBUG']='1'
    p=subprocess.Popen(args,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    children.append(p)
    return p
def wait(fn,seconds=10):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        v=fn()
        if v:return v
        if compositor.poll() is not None:raise RuntimeError('compositor exited '+str(compositor.returncode))
        time.sleep(.05)
    raise RuntimeError('timeout')
def ipc(*args):
    return json.loads(subprocess.run(['swaymsg','-s',str(sock),*args],env=e,text=True,
        capture_output=True,timeout=5,check=True).stdout)
def tree():return ipc('-t','get_tree')
def find_app(node,app):
    if isinstance(node,dict):
        if node.get('app_id')==app:return node
        for child in node.get('nodes',[])+node.get('floating_nodes',[]):
            found=find_app(child,app)
            if found:return found
    return None
def workspace(node,name):
    if isinstance(node,dict):
        if node.get('type')=='workspace' and node.get('name')==name:return node
        for child in node.get('nodes',[]):
            found=workspace(child,name)
            if found:return found
    return None
def shot(tag):
    (run/f'tree-{tag}.json').write_text(json.dumps(tree(),indent=2))
    (run/f'outputs-{tag}.json').write_text(json.dumps(ipc('-t','get_outputs'),indent=2))
    for out,name in [('HEADLESS-1','left'),('HEADLESS-2','right')]:
        subprocess.run(['grim','-o',out,str(run/f'{name}-{tag}.png')],env=e,check=True,timeout=8,
            stdout=subprocess.DEVNULL)
def inject(button,x,y):
    marker=f'INJECT_DONE {button} {x},{y}'
    injector.stdin.write(f'{button} {x} {y}\n');injector.stdin.flush()
    wait(lambda:marker in (run/'pointer.log').read_text())
def logged(pattern):
    path=run/'client.log'
    return pattern in path.read_text() if path.exists() else False
log=(run/'compositor.log').open('w');files.append(log)
compositor=subprocess.Popen([str(binary),'-c',str(run/'config'),'-d'],env=compositor_env,
    stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
try:
    def sockets():
        s=next(iter(run.glob('sway-ipc.*.sock')),None)
        w=next((x for x in run.glob('wayland-*') if x.suffix!='.lock'),None)
        return (s,w) if s and w else None
    sock,way=wait(sockets)
    e.update(SWAYSOCK=str(sock),WAYLAND_DISPLAY=way.name)
    pointer_log=(run/'pointer.log').open('w');files.append(pointer_log)
    injector=subprocess.Popen([str(LAB/'pointer-daemon')],env=e,stdin=subprocess.PIPE,
        text=True,stdout=pointer_log,stderr=subprocess.STDOUT,start_new_session=True)
    children.append(injector)
    wait(lambda:'POINTER_READY' in (run/'pointer.log').read_text())
    ipc('workspace 1');ipc('layout mosaic' if case.startswith('private_mosaic') else 'layout splith')
    spawn(['kitty','--class','A','-o','background=#aa2222','/usr/bin/sleep','60'],'A.log')
    wait(lambda:len(workspace(tree(),'1')['nodes'])>=1)
    if mode=='fully_visible':e['PROBE_POPUP_FULLY_VISIBLE']='1'
    client=spawn([str(LAB/'grab-client')],'client.log',True)
    wait(lambda:find_app(tree(),'org.mosaic.ValidGrabProbe'))
    for label in ('C','D'):
        spawn(['kitty','--class',label,'/usr/bin/sleep','60'],label+'.log')
        time.sleep(.35)
    ipc('workspace 2')
    spawn(['stdbuf','-oL','wev'],'wev.log')
    time.sleep(.5)
    ipc('workspace 1')
    ipc('[app_id="org.mosaic.ValidGrabProbe"] focus')
    if case.startswith('private_mosaic'):
        current=workspace(tree(),'1')['mosaic']['rows'][0]['scroll_x']
        ipc(f'layout mosaic scroll {400-current:g}')
    time.sleep(.5)
    ws=workspace(tree(),'1');owner=find_app(ws,'org.mosaic.ValidGrabProbe')
    (run/'owner-before.json').write_text(json.dumps({'owner':owner,'workspace':ws.get('mosaic')},indent=2))
    rect=owner['rect']
    scroll=ws['mosaic']['rows'][0]['scroll_x'] if case.startswith('private_mosaic') else 0
    x=int(max(30,min(770,rect['x']-scroll+int(rect['width']*.55))));y=rect['y']+130
    print('OPEN_POINT',x,y,'OWNER_RECT',rect,flush=True)
    inject('left',x,y)
    wait(lambda:logged('POPUP_XDG_CONFIGURE'))
    time.sleep(.35)
    shot('open')
    print('POPUP_OPEN',logged('POPUP_GRAB_REQUEST'),'CLIENT_ALIVE',client.poll() is None,flush=True)
    if mode.startswith('boundary_'):
        inject('move',700,150);time.sleep(.2);shot('visible-hover')
        inject('right',700,150);time.sleep(.2);shot('visible-click')
        inject('move',900,150);time.sleep(.2);shot('boundary-hover')
        inject(mode.split('_')[1],900,150)
        time.sleep(.4);shot('boundary-click')
        print('BOUNDARY',mode,'POPUP_DONE',logged('POPUP_DONE'),
              'CLIENT_ALIVE',client.poll() is None,flush=True)
        sys.exit(0)
    if mode=='standard_return':
        print('STANDARD_RESULT',ipc('layout splith'),flush=True)
        time.sleep(.4);shot('standard-open')
        inject('move',900,150);inject('right',900,150)
        time.sleep(.35);shot('standard-click')
        print('STANDARD_POPUP_DONE',logged('POPUP_DONE'),'CLIENT_ALIVE',client.poll() is None,flush=True)
        sys.exit(0)
    if mode=='outside_left':
        inject('left',900,400)
        time.sleep(.4);shot('outside-left')
        print('OUTSIDE_LEFT_POPUP_DONE',logged('POPUP_DONE'),
              'CLIENT_ALIVE',client.poll() is None,flush=True)
        sys.exit(0)
    if mode=='visible_left':
        inject('move',700,150);inject('left',700,150)
        time.sleep(.3);shot('visible-left')
        print('VISIBLE_LEFT_POPUP_DONE',logged('POPUP_DONE'),
              'CLIENT_ALIVE',client.poll() is None,flush=True)
        sys.exit(0)
    if mode=='fully_visible':
        inject('move',350,150);inject('left',350,150);inject('right',350,150)
        time.sleep(.3);shot('fully-visible-clicks')
        print('FULLY_VISIBLE_POPUP_DONE',logged('POPUP_DONE'),
              'CLIENT_ALIVE',client.poll() is None,flush=True)
        sys.exit(0)
    if case.startswith('private_mosaic'):
        print('SCROLL_RESULT',ipc('layout mosaic scroll 880'),flush=True)
        time.sleep(.6)
        shot('hidden')
        ws=workspace(tree(),'1');owner=find_app(ws,'org.mosaic.ValidGrabProbe')
        print('HIDDEN_OWNER_RECT',owner['rect'],'MOSAIC',ws.get('mosaic'),flush=True)
        print('POPUP_DONE_BEFORE_CLICK',logged('POPUP_DONE'),flush=True)
        if mode=='lifecycle_switch':
            print('SWITCH_RESULT',ipc('workspace 2'),flush=True)
            time.sleep(.45);shot('switched')
            print('SWITCH_POPUP_DONE',logged('POPUP_DONE'),'CLIENT_ALIVE',client.poll() is None,flush=True)
            sys.exit(0)
        if mode=='lifecycle_destroy':
            print('DESTROY_RESULT',ipc(f'[con_id={owner["id"]}] kill'),flush=True)
            time.sleep(.45);shot('destroyed')
            print('DESTROY_POPUP_DONE',logged('POPUP_DONE'),'CLIENT_ALIVE',client.poll() is None,flush=True)
            sys.exit(0)
        inject('move',100,150)
        time.sleep(.25);shot('hidden-hover')
        print('POPUP_DONE_AFTER_HOVER',logged('POPUP_DONE'),flush=True)
        if case.endswith('_hit'):
            inject('right',100,150)
            time.sleep(.25);shot('hidden-click')
            print('POPUP_DONE_AFTER_HIDDEN_CLICK',logged('POPUP_DONE'),flush=True)
        print('RETURN_RESULT',ipc('layout mosaic scroll -880'),flush=True)
        time.sleep(.5);shot('returned')
        print('POPUP_DONE_AFTER_RETURN',logged('POPUP_DONE'),flush=True)
    # A click outside the popup is compared against the control. Capture before
    # and after separately so dismissal cannot masquerade as clipping evidence.
    inject('right',900,400)
    time.sleep(.5);shot('outside')
    print('POPUP_DONE_OUTSIDE',logged('POPUP_DONE'),'CLIENT_ALIVE',client.poll() is None,flush=True)
    if case.startswith('private_mosaic'):
        print('STANDARD_RESULT',ipc('layout splith'),flush=True)
        time.sleep(.4);shot('standard')
finally:
    for child in children:
        if child.poll() is None:os.killpg(child.pid,signal.SIGTERM)
    if compositor.poll() is None:os.killpg(compositor.pid,signal.SIGTERM)
    compositor.wait(timeout=5)
    for f in files:f.close()
