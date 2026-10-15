"""Bounded owned headless session, usable only after the separate matrix review gate."""
import errno,json,os,re,shutil,signal,subprocess,tempfile,threading,time
from pathlib import Path
from PIL import Image,ImageDraw
from geometry import *
from gate import sha,clean_environment,Ledger,canonical_lab,disable_dump,durable

import sys

from ipc_predicates import nodes,workspace
from predicates import protocol,geometry,pair,dismissal
import validators
from lifecycle import opening_pair
from model import Provenance
COLORS={'TOPLEVEL':(35,68,204),'POPUP_A':(224,192,32),'POPUP_B':(32,208,160)}

def client_executable_identity(pid,binary,expected_sha):
    # WHY: PR_SET_DUMPABLE0 can make /proc/PID/exe inaccessible to the parent.
    # CONTRACT: preserve OS error and NOT_OBSERVABLE; identity remains mandatory.
    # INVARIANT: no fallback, self-reported identity or weakened dumpability.
    exe=Path(f'/proc/{pid}/exe');operation='resolve'
    proof=dict(pid=pid,proc=str(exe),expected_binary=str(binary),expected_sha256=expected_sha)
    try:
        actual=exe.resolve(strict=True);operation='sha256';observed=sha(exe)
    except OSError as error:
        return dict(proof,status='NOT_OBSERVABLE',matches=False,operation=operation,
                    errno=error.errno,error_type=type(error).__name__,error=str(error))
    return dict(proof,status='OBSERVED',binary=str(actual),sha256=observed,
                matches=actual==Path(binary) and observed==expected_sha)

def require_client_identity(proof):
    # The exact predicate used by launch_client remains fail-closed offline too.
    need(proof['status']=='OBSERVED' and proof['matches'],
         'actual fullscreen client executable: '+json.dumps(proof,sort_keys=True))
    return proof

def storage_guard(lab):
    # WHY/CONTRACT/INVARIANT: stop before new action at 9GiB or <20GiB free;
    # never purge old evidence to manufacture space.
    v=os.statvfs(lab);need(v.f_bavail*v.f_frsize>=20*1024**3,'SSD free space below20GiB')
    total=sum(p.lstat().st_size for p in lab.rglob('*') if p.is_file() and not p.is_symlink())
    need(total<=9*1024**3,'new LAB exceeds9GiB prudent stop')

def private_runtime():
    # WHY: tmpfs may have user quota exhaustion despite statvfs free space.
    # CONTRACT: probe an owned 0700 directory by writing, then fall back only
    # on EDQUOT/ENOSPC. INVARIANT: socket-only path stays UNIX-length-safe.
    for base in ('/tmp','/var/tmp'):
        runtime=None
        try:
            v=os.statvfs(base)
            if v.f_bavail*v.f_frsize<1024*1024:raise OSError(errno.ENOSPC,'runtime free space')
            runtime=Path(tempfile.mkdtemp(prefix='smx-',dir=base));runtime.chmod(0o700)
            need(len(os.fsencode(runtime/'sway-ipc.4294967295.4294967295.sock'))<108,'UNIX socket path too long')
            fd=os.open(runtime/'quota-probe',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            try:os.write(fd,b'X'*4096);os.fsync(fd)
            finally:os.close(fd)
            (runtime/'quota-probe').unlink();return runtime
        except OSError as exc:
            if runtime is not None:
                p=runtime/'quota-probe'
                if p.exists():p.unlink()
                runtime.rmdir()
            if exc.errno not in (errno.EDQUOT,errno.ENOSPC):raise
            if base=='/var/tmp':raise
    raise ValueError('no safe private runtime')

class Session:
    def __init__(self,spec,auth):
        need(not auth.get('offline'), 'OFFLINE_TEST_ONLY cannot launch');self.spec=spec;self.auth=auth;self.lab=canonical_lab(auth['lab']);self.ledger=Ledger(self.lab);self.folder=self.lab/'graphics-runs'/spec['id'];self.run=self.folder/'run';self.run.mkdir(parents=True)
        disable_dump();self.runtime=private_runtime()
        self.env=clean_environment(self.lab);self.env.update(XDG_RUNTIME_DIR=str(self.runtime),WLR_BACKENDS='headless',WLR_HEADLESS_OUTPUTS='2')
        self.outputs=[dict(o) for o in spec['outputs']];self.frames={o['name']:'logical' for o in self.outputs}
        self.proc_lock=threading.RLock();self.proc={};self.transient={};self.tool_serial=0;self.closed=[];self.helper_exits=[];self.handles=[];self.started=time.monotonic();self.finished=threading.Event();self.expired=False;self.events=[];self.pointer=None
    def start(self):
        spec=self.spec;auth=self.auth
        cfg='\n'.join(f"output {o['name']} resolution {o['mode'][0]}x{o['mode'][1]} scale {o['scale']} transform {o['transform']} position {o['logical'][0]} {o['logical'][1]}" for o in self.outputs)
        cfg+='\nworkspace 1 output HEADLESS-1\nworkspace 2 output HEADLESS-2\nfocus_follows_mouse no\nseat seat0 hide_cursor 100\nshadows disable\nblur disable\n'
        if spec['id'] in ('C3','C4'):
            marker=Image.new('RGB',(800,600),(30,30,46));draw=ImageDraw.Draw(marker)
            for k,box in [('TL',(15,15,44,44)),('TR',(755,15,784,44)),('BL',(15,555,44,584)),('BR',(755,555,784,584)),('C',(385,285,414,314))]:draw.rectangle(box,fill=MARKERS[k])
            marker.save(self.run/'marker-source.png');self.marker_source=self.run/'marker-source.png';self.record('generated-content-PNG',path=str(self.marker_source),counts_as_capture=False)
        need(cfg==self.spec['config'],'sealed config bytes');(self.run/'config').write_text(cfg);self.watch=threading.Thread(target=self.watchdog,daemon=True);self.watch.start()
        if spec['id'] in ('OM-ROOT','OM-NESTED'):
            from oom import process_environment
            self.oom_env=process_environment(self.lab,spec['id'],auth['token'])
        self.comp=self.spawn('compositor',[auth['binary'],'-d',*(['-Dtxn-timeout=5000'] if spec['id']=='C6' else []),'-c',self.run/'config'])
        self.sock=self.wait(lambda:next(iter(self.runtime.glob('sway-ipc.*.sock')),None));display=self.wait(lambda:next((p for p in self.runtime.glob('wayland-*') if p.is_socket()),None))
        self.env.update(WAYLAND_DISPLAY=display.name,SWAYSOCK=str(self.sock));need(Path(f'/proc/{self.comp.pid}/exe').resolve()==Path(auth['binary']).resolve() and sha(Path(f'/proc/{self.comp.pid}/exe'))==auth['binary_sha256'],'actual executable')
        maps=Path(f'/proc/{self.comp.pid}/maps').read_text();(self.run/'proc-maps.txt').write_text(maps)
        paths={s.split()[-1] for s in maps.splitlines() if len(s.split())>=6 and s.split()[-1].startswith('/')}
        wl=[Path(p).resolve() for p in paths if 'libwlroots' in p];need(wl==[Path(auth['wlroots'])] and sha(wl[0])==auth['wlroots_sha256'],'mapped wlroots')
        scene=[Path(p).resolve() for p in paths if 'libscenefx' in p]
        if spec['binary'] in ('core','oom','gpu'):need(not scene,'static SceneFX')
        else:need(scene==[Path(auth['pristine_scene'])] and sha(scene[0])==auth['pristine_scene_sha256'],'mapped pristine SceneFX')
        render=[s for s in self.log('compositor').splitlines() if any(x in s for x in ('Creating scenefx FX renderer','GL renderer:','GL vendor:','Using OpenGL ES'))]
        need(any('Creating scenefx FX renderer' in s for s in render) and any('GL renderer:' in s for s in render),'actual renderer')
        self.save('runtime-identity',dict(pid=self.comp.pid,executable=str(Path(f'/proc/{self.comp.pid}/exe').resolve()),binary_sha256=sha(Path(f'/proc/{self.comp.pid}/exe')),wlroots=[dict(path=str(p),sha256=sha(p)) for p in wl],renderer=render,egl=[line for line in self.log('compositor').splitlines() if 'EGL' in line],egl_source='compositor startup log; NOT_OBSERVABLE if empty',source_manifest=self.auth['manifest_sha256']));self.record('actual-renderer',lines=render);self.snapshot('startup')
        if spec['id'] in ('C3','C4'):
            self.spawn('marker-background',['swaybg','-o','HEADLESS-1','-i',self.marker_source,'-m','fill']);time.sleep(.35)
            im=self.capture('marker-H1','HEADLESS-1',orientation_pending=True);m=marker_frame(im,self.outputs[0]['scale'],self.outputs[0]['transform']=='90');self.frames['HEADLESS-1']=m['frame'];self.record('marker-frame',**m);self.close_helper('marker-background')
        self.pointer=self.spawn('pointer',[self.lab/'followup-work/client-build/pointer-daemon']);self.wait(lambda:'POINTER_READY' in self.log('pointer'))
    def close_helper(self,name):
        # WHY: swaybg is a calibration helper, not an XDG SHM test client.
        # CONTRACT: retire its owned group after the marker screenshot; retain
        # raw status separately. Never reinterpret SIGTERM as scientific close.
        need(name=='marker-background','unknown helper role');p=self.proc[name]
        if p.poll() is None:
            try:os.killpg(p.pid,signal.SIGTERM)
            except ProcessLookupError:pass
        code=p.wait(timeout=2)
        proof=dict(name=name,pid=p.pid,exit=code,expected_termination='owned helper SIGTERM after calibration',scientific_client=False)
        self.helper_exits.append(proof);self.record('helper-exit',**proof)
        need(code in (0,-signal.SIGTERM),'unexpected calibration helper exit')
        need(not Path('/proc',str(p.pid)).exists(),'calibration helper residual')
        if p.stdin and not p.stdin.closed:p.stdin.close()
        del self.proc[name]

    def record(self,kind,**fields):
        e=dict(kind=kind,ns=time.monotonic_ns(),**fields);self.events.append(e)
        with (self.run/'events.jsonl').open('a') as f:f.write(json.dumps(e)+'\n')
    def save(self,name,value):
        durable(self.run/(name+'.json'),value)
    def debit(self,*kinds):
        storage_guard(self.lab);self.ledger.action_debit(self.auth,*kinds)
    def spawn(self,name,argv,debug=False):
        self.debit('spawn');need(not self.expired,'expired before spawn');f=(self.run/(name+'.log')).open('w');self.handles.append(f)
        requested_argv=list(map(str,argv));prlimit=shutil.which('prlimit')
        need(prlimit is not None,'util-linux prlimit unavailable; refusing unbounded child')
        # WHY: a child core dump can exhaust the bounded graphics LAB.
        # CONTRACT: every owned child starts with a zero soft and hard core limit.
        # INVARIANT: exec keeps the child PID stable for /proc identity checks.
        actual_argv=[prlimit,'--core=0:0','--',*requested_argv]
        # WHY/CONTRACT/INVARIANT: registration and expiry are atomic: no child
        # can escape the watchdog's owned-group snapshot by racing its deadline.
        with getattr(self,'proc_lock',threading.RLock()):
            need(not self.expired,'expired before process creation')
            # WHY/CONTRACT/INVARIANT: diagnostics are compositor-private and
            # never enter the environment shared with capture, IPC or clients.
            child_env={**self.env,**({'WAYLAND_DEBUG':'1'} if debug else {})}
            need(not any(k.startswith(('SMX_OOM_','MOSAIC_G2_','MOSAIC_G3_')) for k in child_env),'diagnostic environment leaked into common environment')
            if name=='compositor':
                child_env.update(getattr(self,'oom_env',{}));child_env.update(getattr(self,'compositor_environment',{}))
            p=subprocess.Popen(actual_argv,stdin=subprocess.PIPE,stdout=f,stderr=subprocess.STDOUT,text=True,start_new_session=True,env=child_env)
            self.proc[name]=p
        self.record('spawn',name=name,pid=p.pid,requested_argv=requested_argv,actual_argv=actual_argv);return p
    def log(self,name):return (self.run/(name+'.log')).read_text(errors='replace')
    def wait(self,fn,seconds=5):
        end=min(self.started+143,time.monotonic()+seconds)
        while time.monotonic()<end:
            need(not self.expired,'watchdog')
            if hasattr(self,'comp'):need(self.comp.poll() is None,'unexpected compositor exit')
            v=fn()
            if v:return v
            time.sleep(.02)
        raise Ambiguous('bounded wait timeout')
    def remaining(self,deadline=146):
        return max(.001,self.started+deadline-time.monotonic())
    def signal_owned(self,sig):
        with getattr(self,'proc_lock',threading.RLock()):
            for p in [*self.proc.values(),*self.transient.values()]:
                try:os.killpg(p.pid,sig)
                except ProcessLookupError:pass
    def watchdog(self):
        # WHY: main-thread protocol closure may block or fail.
        # CONTRACT: autonomous TERM at143, KILL by146, below150s/run.
        # INVARIANT: only registered private session groups are signalled;
        # the main cleanup shares this absolute deadline, never N grace periods.
        while not self.finished.wait(.02):
            if time.monotonic()>=self.started+143 or any(p.stat().st_size>32*1024*1024 for p in self.run.glob('*.log')):
                with getattr(self,'proc_lock',threading.RLock()):self.expired=True
                self.signal_owned(signal.SIGTERM)
                grace_end=min(self.started+146,time.monotonic()+2)
                if not self.finished.wait(max(0,grace_end-time.monotonic())):
                    self.signal_owned(signal.SIGKILL)
                return
    def command_process(self,argv,timeout=4):
        # WHY: capture/IPC helpers also belong to the autonomous watchdog.
        # CONTRACT: bounded file output and owned session groups for every tool.
        # INVARIANT: debit precedes spawn; raw tool status remains independent.
        self.debit('tool');self.tool_serial+=1;tag='tool-'+str(self.tool_serial)
        outpath=self.run/(tag+'.stdout.log');errpath=self.run/(tag+'.stderr.log')
        with outpath.open('w') as stdout,errpath.open('w') as stderr:
            with self.proc_lock:
                need(not self.expired,'expired before helper spawn')
                argv=list(map(str,argv));actual=['prlimit','--core=0:0','--',*argv]
                p=subprocess.Popen(actual,env=self.env,stdout=stdout,stderr=stderr,start_new_session=True)
                self.transient[p.pid]=p
            try:
                try:p.wait(timeout=min(timeout,self.remaining()))
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=1);raise
            finally:
                with self.proc_lock:self.transient.pop(p.pid,None)
        need(outpath.stat().st_size<=32*1024*1024 and errpath.stat().st_size<=32*1024*1024,'helper log bound')
        result=subprocess.CompletedProcess(argv,p.returncode,outpath.read_text(errors='replace'),errpath.read_text(errors='replace'))
        self.record('tool-exit',argv=argv,pid=p.pid,exit=p.returncode,stdout_path=str(outpath),stderr_path=str(errpath))
        return result

    def ipc(self,*args,strict=True):
        need(self.sock.is_relative_to(self.runtime) and self.sock.is_socket(),'private socket')
        self.record('ipc-request',args=args)
        p=self.command_process(['swaymsg','-s',str(self.sock),*args])
        self.record('ipc-reply',args=args,exit=p.returncode,stdout=p.stdout,stderr=p.stderr)
        if strict:need(p.returncode==0,'IPC command failure')
        return json.loads(p.stdout) if p.returncode==0 else None
    def cmd(self,command,business=False):
        self.debit('mutation' if business else 'configuration');reply=self.ipc(command);need(all(r['success'] for r in reply),'command rejected')
    def snapshot(self,tag,validate=True):
        snap=dict(tree=self.ipc('-t','get_tree'),outputs=self.ipc('-t','get_outputs'),workspaces=self.ipc('-t','get_workspaces'),ns=time.monotonic_ns())
        if validate:expected_outputs(snap['outputs'],self.outputs)
        self.save(tag+'-snapshot',snap);return snap
    def find(self,name):
        pid=self.proc[name].pid;rows=[n for n in nodes(self.ipc('-t','get_tree')) if n.get('pid')==pid];need(len(rows)<=1,'client owner ambiguity');return rows[0] if rows else None
    def launch_client(self,name,client,*args):
        build=self.lab/'followup-work/client-build'
        p=self.spawn(name,[build/client,*args],True);self.wait(lambda:self.find(name));time.sleep(.25)
        if client=='fullscreen-client':
            proof=client_executable_identity(p.pid,build/client,self.auth['client_binary_sha256'])
            self.save('fullscreen-client-identity',proof)
            self.record('fullscreen-client-identity',**proof)
            require_client_identity(proof)
        return p
    def capture(self,tag,out,orientation_pending=False):
        self.debit('capture');spec=next(o for o in self.outputs if o['name']==out);p=self.run/(tag+'.png');need(not p.exists(),'capture unique')
        t=time.monotonic_ns();r=self.command_process(['grim','-s',str(spec['scale']),'-o',out,str(p)])
        self.record('capture',tag=tag,output=out,start_ns=t,end_ns=time.monotonic_ns(),exit=r.returncode,path=str(p),sha256=sha(p) if p.exists() else None)
        need(r.returncode==0,'capture failure');im=Image.open(p).convert('RGB')
        logical=tuple(round(v*spec['scale']) for v in spec['logical'][2:]);physical=tuple(spec['mode'])
        need(im.size==logical or (orientation_pending and im.size==physical) or (self.frames[out]=='physical90' and im.size==physical),'PNG size')
        return im
    def pair_capture(self,tag):return [self.capture(tag+'-H1','HEADLESS-1'),self.capture(tag+'-H2','HEADLESS-2')]
    def inject(self,action,point,grab=False):
        need(action in ('move','left','right'),'injection action');outs=self.ipc('-t','get_outputs');active=[o for o in outs if o['active']]
        rects=[[o['rect'][k] for k in ('x','y','width','height')] for o in active];need(any(contains(r,point) for r in rects),'logical point outside output')
        minx=min(r[0] for r in rects);miny=min(r[1] for r in rects);w=max(r[0]+r[2] for r in rects)-minx;h=max(r[1]+r[3] for r in rects)-miny
        self.debit('move',*(['click'] if action!='move' else []),*(['grab'] if grab else []))
        sent=[point[0]-minx,point[1]-miny];marker=f'INJECT_DONE {action} {sent[0]},{sent[1]}';before=self.log('pointer').count(marker)
        self.pointer.stdin.write(f'{action} {sent[0]} {sent[1]} {w} {h}\n');self.pointer.stdin.flush();self.wait(lambda:self.log('pointer').count(marker)>before)
        self.record('injection',action=action,global_logical=point,sent=sent,logical_extent=[w,h],grab=grab);time.sleep(.12)
    def click(self,name,point,action='right',grab=False):
        before={n:len(self.log(n)) for n in self.proc if n not in ('compositor','pointer','background')};t=time.monotonic_ns();self.inject(action,point,grab)
        validators.window(t,time.monotonic_ns(),[e['ns'] for e in self.events if e['kind']=='injection' and e['ns']>=t]);tails={n:self.log(n)[i:] for n,i in before.items()};lines={n:[s for s in v.splitlines() if s.startswith(('POINTER_BUTTON ','BUTTON '))] for n,v in tails.items()}
        self.record('click-observation',name=name,point=point,start_ns=t,tails=tails,buttons=lines)
        return tails,lines
    def delivery(self,name,rect,point,tails,lines,target,opening_serial=None):
        need(not any(v for n,v in lines.items() if n!=name),'wrong client received popup button')
        proof=opening_pair(lines[name],target,opening_serial) if opening_serial else pair(lines[name],target)
        rows=re.findall(rf'POINTER_(?:ENTER|MOTION) target={target} .*?x=([\d.-]+) y=([\d.-]+)',tails[name]);need(rows,'fresh pointer local coordinates')
        local=list(map(float,rows[-1]));validators.applied(rect[:2],rect[:2],[point[0]-local[0],point[1]-local[1]],'applied')
        for e in proof:need(re.search(rf'wl_pointer#\d+\.button\({e[1]}, \d+, {e[2]}, {e[3]}\)',tails[name]) is not None,'button actual wire')
        return proof
    def owner(self,name):
        snap=self.snapshot(name+'-owner')
        rows=[n for n in nodes(snap['tree']) if n.get('pid')==self.proc[name].pid]
        need(len(rows)==1,'owner identity/ambiguity');owner=rows[0]
        ws=workspace(snap['tree'],'1')
        path=__import__('ipc_predicates').ancestry(snap['tree'],owner['id'])
        validators.owner_context(owner,path,self.proc[name].pid,'1',getattr(self,'expected_output','HEADLESS-1'),getattr(self,'expected_layout','mosaic' if self.spec['mode']=='mosaic' else 'splith'))
        # WHY: standard_return changes layout after the initial campaign mode.
        # CONTRACT: camera applies only to current Mosaic tiled descendants;
        # floating branches and fullscreen group ancestry remain exempt.
        # WHY/CONTRACT: root/output/workspace IPC descriptors may have floating=null.
        # INVARIANT: null means no floating flag; branch membership still counts,
        # and this geometry remains a pending candidate, never native-applied.
        eligible=validators.camera_eligible(path,ws)
        origin=assigned_origin(owner);scene=exterior_ipc(owner)
        if eligible:
            scroll=int(ws['mosaic']['rows'][0]['scroll_x']);origin[0]-=scroll;scene[0]-=scroll
        # INVARIANT: IPC never becomes native-applied without fresh paint and pointer corroboration.
        raw='current-layout IPC candidate; native paint and fresh pointer-local corroboration required, generation NOT OBSERVABLE'
        data=dict(geometry_status='IPC_PENDING_CANDIDATE; requires fresh paint/pointer after every mutation',owner=owner,workspace=ws,origin=origin,scene=scene,evidence=raw,snapshot=snap);self.save(name+'-geometry',data);return data
    def calibrate(self,name):
        state=self.owner(name)
        if self.spec['mode']=='mosaic' and self.spec['axis']==0:
            delta=int(state['origin'][0]+state['owner']['window_rect']['width']//2)
            if delta:self.scroll(name,delta)
            state=self.owner(name);need(crossing([*state['origin'],state['owner']['window_rect']['width'],state['owner']['window_rect']['height']],0,0),'owner real x0 crossing')
        return state
    def scroll(self,name,delta):
        self.debit('camera');self.cmd(f'[con_id={self.find(name)["id"]}] layout mosaic scroll {int(delta)}');time.sleep(.35)
        self.record('camera',owner=self.find(name)['id'],delta=int(delta))
    def client_cmd(self,name,cmd,marker=None):
        self.debit('configuration' if cmd.startswith('close') else 'mutation');before=len(self.log(name));self.record('client-request',name=name,command=cmd)
        self.proc[name].stdin.write(cmd+'\n');self.proc[name].stdin.flush()
        if marker:self.wait(lambda:marker in self.log(name)[before:])
    def close_client(self,name,command='close_owner',scenario=None):
        # WHY: exit0 alone cannot prove SHM release or an explicit normal close.
        # CONTRACT: retain each PID's validation, including retired same-name owners.
        # INVARIANT: a failed closure is durable evidence, never laundered by cleanup.
        p=self.proc[name];proof=dict(name=name,pid=p.pid,status='INCONCLUSIVE',failure=None)
        try:
            if p.poll() is None:self.client_cmd(name,command)
            code=p.wait(timeout=min(3,self.remaining()));raw=self.log(name)
            archive=self.run/f'{name}-closed-{p.pid}.log';archive.write_text(raw)
            proof.update(exit=code,log=str(archive),sha256=sha(archive),close_received='CLOSE_RECEIVED' in raw,shm_closure=re.findall(r'SHM_CLOSURE created=(\d+) released=(\d+)',raw),wayland_errors=re.findall(r'EXIT[^\n]*error=(\d+)',raw))
            validators.client_exit(raw,code,scenario or getattr(self,'closure_scenarios',{}).get(name,'observed'));self.wait(lambda:self.find(name) is None)
            proof['status']='PASS'
        except Exception as error:
            proof['failure']=f'{type(error).__name__}: {error}'
            proof.setdefault('exit',p.poll())
            raise
        finally:
            self.closed.append(proof);self.record('client-closed',**proof)

    def cleanup(self,measurement_status,failure=None):
        terminal=None;rescue=False;closures=[]
        # Close test clients while their Wayland server still exists. Mechanical
        # rescue and terminal IPC can never substitute for scientific closure.
        for name in reversed(list(self.proc)):
            if name in ('compositor','pointer') or any(c['pid']==self.proc[name].pid for c in self.closed):continue
            if self.expired or time.monotonic()>=self.started+143:break
            try:
                self.close_client(name,'close_owner' if name=='owner' and self.spec['client']!='saved-client' and self.spec['id']!='C6' else 'close')
            except Exception:pass # close_client retains the explicit validation failure.
        # WHY/CONTRACT/INVARIANT: archived and already-exited clients count equally;
        # an empty list of newly closed processes must not erase prior failures.
        closures=[dict(c) for c in self.closed]
        tracked=[p.pid for n,p in self.proc.items() if n not in ('compositor','pointer')]
        closure_coverage=all(any(c['pid']==pid for c in closures) for pid in tracked)

        if hasattr(self,'comp') and self.comp.poll() is None and hasattr(self,'sock') and self.sock.is_socket() and not self.expired and time.monotonic()<self.started+145:
            try:
                self.debit('configuration')
                p=self.command_process(['swaymsg','-s',str(self.sock),'exit'],timeout=2)
                terminal=dict(ipc_exit=p.returncode,stdout=p.stdout,stderr=p.stderr)
                self.save('terminal-ipc',terminal)
            except Exception as e:
                terminal=dict(ipc_error=str(e));self.save('terminal-ipc',terminal)
            if terminal is not None and 'ipc_exit' in terminal:
                try:self.comp.wait(timeout=min(1,self.remaining()))
                except Exception as e:
                    terminal['wait_error']=str(e);self.save('terminal-ipc',terminal)
        codes=[dict(name=c['name'],pid=c['pid'],exit=c['exit']) for c in self.closed if not any(p.pid==c['pid'] for p in self.proc.values())]
        # One shared cleanup deadline prevents N owned clients multiplying waits.
        cleanup_end=min(self.started+146,time.monotonic()+2)
        if self.pointer and self.pointer.poll() is None and self.pointer.stdin and not self.pointer.stdin.closed:self.pointer.stdin.close()
        for name,p in reversed(list(self.proc.items())):
            if p.poll() is None:
                try:p.wait(timeout=max(.01,cleanup_end-time.monotonic()))
                except subprocess.TimeoutExpired:pass
        residual=[p for p in self.proc.values() if p.poll() is None]
        if residual:
            rescue=True
            for p in residual:
                try:os.killpg(p.pid,signal.SIGKILL)
                except ProcessLookupError:pass
            kill_end=min(self.started+147,time.monotonic()+1)
            for p in residual:p.wait(timeout=max(.01,kill_end-time.monotonic()))
        for name,p in self.proc.items():
            codes.append(dict(name=name,pid=p.pid,exit=p.returncode))
            if p.stdin and not p.stdin.closed:p.stdin.close()
        self.finished.set();
        if hasattr(self,'watch'):self.watch.join(timeout=1)
        for h in self.handles:h.close()
        for p in self.proc.values():
            try:os.killpg(p.pid,0)
            except ProcessLookupError:pass
            else:rescue=True;os.killpg(p.pid,signal.SIGKILL)
        reaped=all(not Path('/proc',str(p.pid)).exists() for p in self.proc.values());need(reaped,'owned process residual');shutil.rmtree(self.runtime)
        seconds=time.monotonic()-self.started
        protocol_errors=[n for n in self.proc if n not in ('compositor','pointer') and re.search(r'wl_display[^\n]*\.error\(|protocol error|invalid_popup_parent|not_the_topmost_popup',self.log(n),re.I)]
        cleanup_pass=bool(closure_coverage and all(c['status']=='PASS' for c in closures) and not rescue and reaped and seconds<=150 and not self.expired and all(any(c['name']==n and c.get('expected_enomem') for c in closures) for n in protocol_errors) and all(p['exit']==0 or any(c['pid']==p['pid'] and c.get('expected_enomem') for c in closures) for p in codes))
        transport_pass=validators.terminal_transport(terminal,self.comp.returncode if hasattr(self,'comp') else None)
        final_status=measurement_status if failure is None and cleanup_pass and transport_pass else 'INCONCLUSIVE'
        self.save('outcome',dict(status=final_status,measurements_pass=measurement_status,architecture_verdict='INCONCLUSIVE',evidence_provenance=self.auth,untested_matrix_cells=['ATOMIC_GENERATION','COMPLETE_DAMAGE','NATIVE_BUFFER_IDENTITY','GPU_LIFETIME'],scientific_cleanup='PASS' if cleanup_pass else 'INCONCLUSIVE',runtime_exit=codes,measurements_status=measurement_status,failure=failure,terminal=terminal,helper_exits=getattr(self,'helper_exits',[]),explicit_client_closures=self.closed,mechanical_cleanup='PASS' if reaped and not rescue and not self.runtime.exists() else 'INCONCLUSIVE',client_closures=closures,processes=codes,rescue=rescue,reaped=reaped,runtime_removed=not self.runtime.exists(),seconds=seconds,watchdog=self.expired,protocol_errors=protocol_errors,cleanup_pass=cleanup_pass,transport_status='PASS' if transport_pass else 'INCONCLUSIVE'))
        self.ledger.complete(self.auth,dict(status=final_status,runner_failure=failure,terminal=terminal,processes=codes,scientific_cleanup=cleanup_pass,mechanical_rescue=rescue));return final_status
