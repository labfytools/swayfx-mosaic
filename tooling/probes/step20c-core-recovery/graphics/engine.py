"""Bounded owned headless session, usable only after the separate matrix review gate."""
import json,os,re,shutil,signal,subprocess,tempfile,threading,time
from pathlib import Path
from PIL import Image,ImageDraw
from geometry import *
from gate import LAB,sha,clean_environment,action_debit,BASE
ROOT=LAB
import sys

from ipc_predicates import nodes,workspace
from predicates import protocol,geometry,pair,dismissal
import validators
from lifecycle import opening_pair
from model import Provenance
COLORS={'TOPLEVEL':(35,68,204),'POPUP_A':(224,192,32),'POPUP_B':(32,208,160)}

class Session:
    def __init__(self,spec,auth):
        self.spec=spec;self.auth=auth;self.folder=LAB/'graphics/runs'/spec['id'];self.run=self.folder/'run';self.run.mkdir(parents=True)
        self.runtime=Path(tempfile.mkdtemp(prefix='m20-',dir='/tmp'));self.runtime.chmod(0o700)
        self.env=clean_environment();self.env.update(XDG_RUNTIME_DIR=str(self.runtime),WLR_BACKENDS='headless',WLR_HEADLESS_OUTPUTS='2')
        self.outputs=[dict(o) for o in spec['outputs']];self.frames={o['name']:'logical' for o in self.outputs}
        self.proc={};self.closed=[];self.handles=[];self.started=time.monotonic();self.finished=threading.Event();self.expired=False;self.events=[];self.pointer=None
    def start(self):
        spec=self.spec;auth=self.auth
        cfg='\n'.join(f"output {o['name']} resolution {o['mode'][0]}x{o['mode'][1]} scale {o['scale']} transform {o['transform']} position {o['logical'][0]} {o['logical'][1]}" for o in self.outputs)
        cfg+='\nworkspace 1 output HEADLESS-1\nworkspace 2 output HEADLESS-2\nfocus_follows_mouse no\nseat seat0 hide_cursor 100\nshadows disable\nblur disable\n'
        if spec['id'] in ('E2-fractional','E2-r90'):
            marker=Image.new('RGB',(800,600),(30,30,46));draw=ImageDraw.Draw(marker)
            for k,box in [('TL',(15,15,44,44)),('TR',(755,15,784,44)),('BL',(15,555,44,584)),('BR',(755,555,784,584)),('C',(385,285,414,314))]:draw.rectangle(box,fill=MARKERS[k])
            marker.save(self.run/'marker-source.png');self.marker_source=self.run/'marker-source.png';self.record('generated-content-PNG',path=str(self.marker_source),counts_as_capture=False)
        need(cfg==(BASE/'configs'/(spec['id']+'.conf')).read_text(),'sealed config bytes');(self.run/'config').write_text(cfg);self.watch=threading.Thread(target=self.watchdog,daemon=True);self.watch.start()
        self.comp=self.spawn('compositor',[auth['binary'],'-d',*(['-Dtxn-timeout=5000'] if spec['id']=='S8-core-saved' else []),'-c',self.run/'config'])
        self.sock=self.wait(lambda:next(iter(self.runtime.glob('sway-ipc.*.sock')),None));display=self.wait(lambda:next((p for p in self.runtime.glob('wayland-*') if p.is_socket()),None))
        self.env.update(WAYLAND_DISPLAY=display.name,SWAYSOCK=str(self.sock));need(Path(f'/proc/{self.comp.pid}/exe').resolve()==Path(auth['binary']).resolve() and sha(Path(f'/proc/{self.comp.pid}/exe'))==auth['binary_sha256'],'actual executable')
        maps=Path(f'/proc/{self.comp.pid}/maps').read_text();(self.run/'proc-maps.txt').write_text(maps)
        paths={s.split()[-1] for s in maps.splitlines() if len(s.split())>=6 and s.split()[-1].startswith('/')}
        wl=[Path(p).resolve() for p in paths if 'libwlroots' in p];need(wl==[Path(auth['wlroots'])] and sha(wl[0])==auth['wlroots_sha256'],'mapped wlroots')
        scene=[Path(p).resolve() for p in paths if 'libscenefx' in p]
        if spec['binary']=='core':need(not scene,'static SceneFX')
        else:need(scene==[Path(auth['pristine_scene'])] and sha(scene[0])==auth['pristine_scene_sha256'],'mapped pristine SceneFX')
        render=[s for s in self.log('compositor').splitlines() if any(x in s for x in ('Creating scenefx FX renderer','GL renderer:','GL vendor:','Using OpenGL ES'))]
        need(any('Creating scenefx FX renderer' in s for s in render) and any('GL renderer:' in s for s in render),'actual renderer')
        self.record('actual-renderer',lines=render);self.snapshot('startup')
        if spec['id'] in ('E2-fractional','E2-r90'):
            self.spawn('marker-background',['swaybg','-o','HEADLESS-1','-i',self.marker_source,'-m','fill']);time.sleep(.35)
            im=self.capture('marker-H1','HEADLESS-1',orientation_pending=True);m=marker_frame(im,self.outputs[0]['scale'],self.outputs[0]['transform']=='90');self.frames['HEADLESS-1']=m['frame'];self.record('marker-frame',**m)
        self.pointer=self.spawn('pointer',[LAB/'graphics/clients/pointer-daemon']);self.wait(lambda:'POINTER_READY' in self.log('pointer'))
    def record(self,kind,**fields):
        e=dict(kind=kind,ns=time.monotonic_ns(),**fields);self.events.append(e)
        with (self.run/'events.jsonl').open('a') as f:f.write(json.dumps(e)+'\n')
    def save(self,name,value):
        (self.run/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    def debit(self,*kinds):action_debit(self.spec['id'],*kinds)
    def spawn(self,name,argv,debug=False):
        need(not self.expired,'expired before spawn');f=(self.run/(name+'.log')).open('w');self.handles.append(f)
        p=subprocess.Popen(list(map(str,argv)),stdin=subprocess.PIPE,stdout=f,stderr=subprocess.STDOUT,text=True,start_new_session=True,env={**self.env,**({'WAYLAND_DEBUG':'1'} if debug else {})})
        self.proc[name]=p;self.record('spawn',name=name,pid=p.pid,argv=list(map(str,argv)));return p
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
    def watchdog(self):
        while not self.finished.wait(.1):
            if time.monotonic()-self.started>143 or any(p.stat().st_size>32*1024*1024 for p in self.run.glob('*.log')):
                self.expired=True
                for p in list(self.proc.values()):
                    try:os.killpg(p.pid,signal.SIGTERM)
                    except ProcessLookupError:pass
                return
    def ipc(self,*args,strict=True):
        need(self.sock.is_relative_to(self.runtime) and self.sock.is_socket(),'private socket')
        self.record('ipc-request',args=args)
        p=subprocess.run(['swaymsg','-s',str(self.sock),*args],env=self.env,capture_output=True,text=True,timeout=4)
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
        p=self.spawn(name,[LAB/'graphics/clients'/client,*args],True);self.wait(lambda:self.find(name));time.sleep(.25);return p
    def capture(self,tag,out,orientation_pending=False):
        self.debit('capture');spec=next(o for o in self.outputs if o['name']==out);p=self.run/(tag+'.png');need(not p.exists(),'capture unique')
        t=time.monotonic_ns();r=subprocess.run(['grim','-s',str(spec['scale']),'-o',out,str(p)],env=self.env,capture_output=True,text=True,timeout=4)
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
        validators.owner_context(owner,path,self.proc[name].pid,'1','HEADLESS-1',getattr(self,'expected_layout','mosaic' if self.spec['mode']=='mosaic' else 'splith'))
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
    def close_client(self,name,command='close_owner'):
        # WHY: exit0 alone cannot prove SHM release or an explicit normal close.
        # CONTRACT: retain each PID's validation, including retired same-name owners.
        # INVARIANT: a failed closure is durable evidence, never laundered by cleanup.
        p=self.proc[name];proof=dict(name=name,pid=p.pid,status='INCONCLUSIVE',failure=None)
        try:
            if p.poll() is None:self.client_cmd(name,command)
            code=p.wait(timeout=3);raw=self.log(name)
            archive=self.run/f'{name}-closed-{p.pid}.log';archive.write_text(raw)
            proof.update(exit=code,log=str(archive),sha256=sha(archive),close_received='CLOSE_RECEIVED' in raw,shm_closure=re.findall(r'SHM_CLOSURE created=(\d+) released=(\d+)',raw),wayland_errors=re.findall(r'EXIT[^\n]*error=(\d+)',raw))
            validators.client_exit(raw,code);self.wait(lambda:self.find(name) is None)
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
            try:
                self.close_client(name,'close_owner' if name=='owner' and self.spec['client']!='saved-client' and self.spec['id']!='S8-core-saved' else 'close')
            except Exception:pass # close_client retains the explicit validation failure.
        # WHY/CONTRACT/INVARIANT: archived and already-exited clients count equally;
        # an empty list of newly closed processes must not erase prior failures.
        closures=[dict(c) for c in self.closed]
        tracked=[p.pid for n,p in self.proc.items() if n not in ('compositor','pointer')]
        closure_coverage=all(any(c['pid']==pid for c in closures) for pid in tracked)

        if hasattr(self,'comp') and self.comp.poll() is None and hasattr(self,'sock') and self.sock.is_socket():
            try:
                p=subprocess.run(['swaymsg','-s',str(self.sock),'exit'],env=self.env,capture_output=True,text=True,timeout=2)
                terminal=dict(ipc_exit=p.returncode,stdout=p.stdout,stderr=p.stderr)
                self.save('terminal-ipc',terminal)
            except Exception as e:
                terminal=dict(ipc_error=str(e));self.save('terminal-ipc',terminal)
            if terminal is not None and 'ipc_exit' in terminal:
                try:self.comp.wait(timeout=1)
                except Exception as e:
                    terminal['wait_error']=str(e);self.save('terminal-ipc',terminal)
        codes=[dict(name=c['name'],pid=c['pid'],exit=c['exit']) for c in self.closed if not any(p.pid==c['pid'] for p in self.proc.values())]
        # One shared cleanup deadline prevents N owned clients multiplying waits.
        cleanup_end=time.monotonic()+2
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
            kill_end=time.monotonic()+1
            for p in residual:p.wait(timeout=max(.01,kill_end-time.monotonic()))
        for name,p in self.proc.items():
            codes.append(dict(name=name,pid=p.pid,exit=p.returncode))
            if p.stdin and not p.stdin.closed:p.stdin.close()
        self.finished.set();self.watch.join(timeout=1)
        for h in self.handles:h.close()
        for p in self.proc.values():
            try:os.killpg(p.pid,0)
            except ProcessLookupError:pass
            else:rescue=True;os.killpg(p.pid,signal.SIGKILL)
        reaped=all(not Path('/proc',str(p.pid)).exists() for p in self.proc.values());need(reaped,'owned process residual');shutil.rmtree(self.runtime)
        seconds=time.monotonic()-self.started
        protocol_errors=[n for n in self.proc if n not in ('compositor','pointer') and re.search(r'wl_display[^\n]*\.error\(|protocol error|invalid_popup_parent|not_the_topmost_popup',self.log(n),re.I)]
        cleanup_pass=bool(closure_coverage and all(c['status']=='PASS' for c in closures) and not rescue and reaped and seconds<=150 and not self.expired and not protocol_errors and all(p['exit']==0 for p in codes))
        transport_pass=terminal is not None and terminal.get('ipc_exit') in (0,1) and 'wait_error' not in terminal and 'ipc_error' not in terminal
        final_status=measurement_status if failure is None and cleanup_pass and transport_pass else 'INCONCLUSIVE'
        self.save('outcome',dict(status=final_status,measurements_pass=measurement_status,architecture_verdict='INCONCLUSIVE',evidence_provenance=self.auth,untested_matrix_cells=['ATOMIC_GENERATION','COMPLETE_DAMAGE','NATIVE_BUFFER_IDENTITY','GPU_LIFETIME'],scientific_cleanup='PASS' if cleanup_pass else 'INCONCLUSIVE',runtime_exit=codes,measurements_status=measurement_status,failure=failure,terminal=terminal,explicit_client_closures=self.closed,mechanical_cleanup='PASS' if reaped and not rescue and not self.runtime.exists() else 'INCONCLUSIVE',client_closures=closures,processes=codes,rescue=rescue,reaped=reaped,runtime_removed=not self.runtime.exists(),seconds=seconds,watchdog=self.expired,protocol_errors=protocol_errors,cleanup_pass=cleanup_pass,transport_status='PASS' if transport_pass else 'INCONCLUSIVE'))
        return final_status
