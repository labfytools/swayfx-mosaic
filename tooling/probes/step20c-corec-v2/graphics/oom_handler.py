"""EXPERIMENTAL prospective O1/O2 handler. No allocator or admission policy."""
import errno,re,time
from pathlib import Path
import cases,oom
from gate import sha,need
from geometry import solid_point,exact,count
from engine import COLORS

def opening_before_map(raw,popup,parent):
    # WHY: native no-memory can precede configure/MAP. CONTRACT/INVARIANT:
    # validate actual serial/grab/parent wire, never await the failed popup MAP.
    rows=re.findall(rf'{popup} CREATE wl=(\d+) xdg=(\d+) role=(\d+) parent={parent} parent_xdg=(\d+)',raw)
    need(len(rows)==1,'unique failed popup identity');wl,xdg,role,parent_xdg=map(int,rows[0])
    parent_ids=re.findall(rf'{parent} CREATE wl=(\d+) xdg=(\d+) role=(\d+)',raw)
    need(len(parent_ids)==1 and int(parent_ids[0][1])==parent_xdg,'failed popup exact parent')
    grabs=re.findall(rf'{popup} GRAB_REQUEST origin=wl_pointer.button target={parent} serial=(\d+) used=(\d+)',raw)
    need(len(grabs)==1 and grabs[0][0]==grabs[0][1] and int(grabs[0][0])>0,'failed popup real grab')
    serial=int(grabs[0][0]);button=raw.index(f'POINTER_BUTTON target={parent} serial={serial} button=272 state=1')
    wire=re.search(rf'wl_pointer#\d+\.button\({serial}, \d+, 272, 1\)',raw)
    create=re.search(rf'xdg_surface#{xdg}\.get_popup\(new id xdg_popup#{role}, xdg_surface#{parent_xdg}, xdg_positioner#\d+\)',raw)
    grab=re.search(rf'xdg_popup#{role}\.grab\(wl_seat#\d+, {serial}\)',raw)
    need(wire is not None and create is not None and grab is not None and wire.start()<button<create.start()<grab.start(),'failed grab wire association')
    return dict(popup=popup,parent=parent,serial=serial,wl=wl,xdg=xdg,role=role,parent_xdg=parent_xdg)

def mapped_root(raw):
    proof=opening_before_map(raw,'POPUP_A','TOPLEVEL')
    need(raw.count('POPUP_A MAP ')==1 and 'POPUP_A DESTROY ' not in raw and 'POPUP_A POPUP_DONE ' not in raw,'O2 same rootA mapped')
    cfg=re.findall(r'POPUP_A ROLE_CONFIGURE x=(-?\d+) y=(-?\d+) w=(\d+) h=(\d+)',raw)
    ack=re.findall(r'POPUP_A XDG_CONFIGURE serial=(\d+) ack',raw)
    need(len(cfg)==len(ack)==1,'O2 unique rootA configure/ACK')
    x,y,w,h=map(int,cfg[0]);serial=int(ack[0]);xdg=proof['xdg'];role=proof['role'];wl=proof['wl']
    rolewire=re.search(rf'xdg_popup#{role}\.configure\({x}, {y}, {w}, {h}\)',raw)
    ackwire=re.search(rf'xdg_surface#{xdg}\.ack_configure\({serial}\)',raw)
    nativecfg=re.search(rf'xdg_surface#{xdg}\.configure\({serial}\)',raw)
    attach=re.search(rf'wl_surface#{wl}\.attach\(wl_buffer#(\d+), 0, 0\)',raw)
    commits=list(re.finditer(rf'wl_surface#{wl}\.commit\(\)',raw))
    need(all((rolewire,ackwire,nativecfg,attach)) and len(commits)==2,'O2 rootA native configure/map evidence')
    buffer=attach[1]
    created=re.search(rf'create_buffer\(new id wl_buffer#{buffer}, 0, {w}, {h}, {w*4}, 1\)',raw)
    need(created is not None and commits[0].start()<rolewire.start()<nativecfg.start()<ackwire.start()<created.start()<attach.start()<commits[1].start()<raw.index('POPUP_A MAP '),'O2 rootA native ACK/SHM order')
    return dict(proof,configure=[x,y,w,h],ack=serial,buffer=int(buffer))

def expected_disconnect(raw,code):
    # WHY/CONTRACT/INVARIANT: retain raw no_memory code1 and client errno;
    # arbitrary errors, server death and missing EXIT never become normal close.
    errors=re.findall(r'wl_display#\d+\.error\([^\n]*?, (\d+), [^\n]*\)',raw)
    exits=re.findall(r'EXIT error=(\d+)',raw)
    need(code in (0,1) and errors==['1'] and len(exits)==1 and int(exits[0]) in (errno.ENOMEM,errno.EPROTO),'expected no-memory disconnect not established')
    return dict(exit=code,wire_error=errors,display_errno=exits,expected_enomem=True)

def retire_enomem(s):
    p=s.proc['owner'];raw=s.log('owner');proof=expected_disconnect(raw,p.poll())
    need(s.find('owner') is None,'disconnected owner remains in IPC')
    proof.update(name='owner',pid=p.pid,status='PASS',meaning='EXPECTED_ENOMEM_DISCONNECT; not ordinary close',raw_log=raw)
    s.closed.append(proof);s.record('owner-enomem-disconnect',**proof);return proof

def availability(s):
    need(s.comp.poll() is None,'critical compositor death')
    exe=Path(f'/proc/{s.comp.pid}/exe')
    need(exe.resolve()==Path(s.auth['binary']).resolve() and sha(exe)==s.auth['binary_sha256'],'critical compositor PID/executable changed')
    maps=Path(f'/proc/{s.comp.pid}/maps').read_text()
    paths={str(Path(line.split()[-1]).resolve()) for line in maps.splitlines() if len(line.split())>=6 and line.split()[-1].startswith('/') and 'libwlroots' in line.split()[-1]}
    need(paths=={s.auth['wlroots']} and sha(s.auth['wlroots'])==s.auth['wlroots_sha256'],'critical mapped wlroots changed')
    return dict(pid=s.comp.pid,exe=str(exe.resolve()),sha256=sha(exe),wlroots=list(paths),maps=maps)

def native_root_success(raw,pid):
    lines=[line for line in raw.splitlines() if 'SMX_OOM result ' in line and 'role=root_popup' in line and 'tree=' in line and 'failures=0' in line]
    need(len(lines)==1,'O2 rootA native success identity missing/ambiguous')
    fields=dict(re.findall(r'([a-z_]+)=([^ ]+)',lines[0]))
    need(fields.get('pid')==str(pid) and fields.get('tree') not in (None,'(nil)','0x0'),'O2 native rootA success')
    return fields

def run(s):
    cases.init_reference(s);s.debit('chain');s.launch_client('owner',s.spec['client'],s.spec['placement']);s.owner('owner')
    s.cmd(f'[con_id={s.find("owner")["id"]}] focus');state=s.calibrate('owner')
    baseline=cases.stable_reference(s);root_success=None
    if s.spec['id']=='O2':
        # Owner origin is corroborated below by actual pointer-local delivery.
        origin=state['origin'];xy=[origin[0]+10,origin[1]+100]
        tails,buttons=s.click('owner',xy,'left',True)
        s.wait(lambda:'POPUP_A MAP ' in s.log('owner'));time.sleep(.15)
        root_success=native_root_success(s.log('compositor'),s.comp.pid)
        proof=mapped_root(s.log('owner'))
        s.delivery('owner',[*origin,420,320],xy,tails,buttons,'TOPLEVEL',proof['serial'])
    pre=s.pair_capture('oom-pre');exact(baseline,pre[1]);before=s.snapshot('oom-before')
    target='TOPLEVEL' if s.spec['id']=='O1' else 'POPUP_A';popup='POPUP_A' if target=='TOPLEVEL' else 'POPUP_B'
    xy=solid_point(pre[0],COLORS[target],s.outputs[0],s.frames['HEADLESS-1'])
    stable=dict(startup=True,owner=True,neighbor=s.find('reference') is not None,reference_H2_twice=True,rootA=root_success is not None,rootA_native_success=root_success is not None)
    oom.arm(s,s.oom_env,s.auth['prospective'],stable)
    tails,buttons=s.click('owner',xy,'left',True)
    s.wait(lambda:'SMX_OOM ENOMEM ' in s.log('compositor'))
    wire=opening_before_map(s.log('owner'),popup,target)
    native=oom.native_failure(s.log('compositor'),s.oom_env,s.comp.pid)
    results=[line for line in s.log('compositor').splitlines() if 'SMX_OOM result ' in line and 'role='+s.oom_env['SMX_OOM_ROLE']+' ' in line]
    need(len(results)==1 and 'tree=(nil)' in results[0] and 'failures=1' in results[0],'native NULL caller outcome absent')
    ident=availability(s);after=s.snapshot('oom-after')
    need(popup+' MAP ' not in s.log('owner'),'failed popup unexpectedly mapped')
    owner_raw_exit=s.proc['owner'].poll();disconnected=None
    if owner_raw_exit is None:
        time.sleep(.15);owner_raw_exit=s.proc['owner'].poll()
    if owner_raw_exit is not None:disconnected=retire_enomem(s)
    post=s.pair_capture('oom-post');exact(baseline,post[1])
    old_root=dict(status='NOT_EXERCISED',reason='O1 has no old rootA' if root_success is None else 'owner disconnected or rootA dismissed')
    if root_success is not None and disconnected is None and 'POPUP_A DESTROY ' not in s.log('owner') and 'POPUP_A POPUP_DONE ' not in s.log('owner'):
        need(count(post[0],COLORS['POPUP_A'])>0 and count(post[1],COLORS['POPUP_A'])==0,'surviving rootA sampled clipping')
        old_root=dict(status='PARTIALLY_FEASIBLE',native_success=root_success)
    neighbor=s.find('reference');need(neighbor is not None,'surviving neighbor absent')
    xy=solid_point(post[1],(48,48,56),s.outputs[1],s.frames['HEADLESS-2'])
    tails,buttons=s.click('reference',xy)
    # WHY/CONTRACT/INVARIANT: a surviving real popup grab may consume the
    # outside click to dismiss; only a measured dismissal permits a fresh
    # neighbor click. This does not claim universal click-through.
    if not buttons.get('reference'):
        need('POPUP_DONE ' in tails.get('owner',''),'neighbor input missing without measured outside dismissal')
        s.save('oom-neighbor-outside-dismissal',dict(tails=tails,buttons=buttons))
        tails,buttons=s.click('reference',xy)
    lines=buttons.get('reference',[])
    events=[re.search(r'BUTTON ns=\d+ serial=(\d+) button=(\d+) state=(\d+)',line) for line in lines]
    need(len(events)==2 and all(events) and [list(map(int,e.groups()[1:])) for e in events]==[[273,1],[273,0]],'fresh neighbor button pair')
    for e in events:need(re.search(rf'wl_pointer#\d+\.button\({e[1]}, \d+, 273, {e[3]}\)',tails['reference']) is not None,'neighbor real wire')
    need(not any(v for k,v in buttons.items() if k!='reference'),'neighbor button not exclusive')
    if disconnected is None:s.close_client('owner')
    final=s.pair_capture('oom-final');exact(baseline,final[1])
    s.save('oom-measurements',dict(native=native,wire=wire,rootA_success=root_success,old_rootA=old_root,before=before,after=after,availability=ident,owner_raw_exit=owner_raw_exit,owner_disconnect=disconnected,neighbor_buttons=buttons,H2_pre_post_final='EXACT',captures=8,complete_damage='NOT_PROVEN',native_stale_listeners='NOT_PROVEN',native_no_partial_popup='NOT_PROVEN; IPC has no popup-node schema',atomic_generation='NOT_PROVEN'))
    return 'PARTIALLY_FEASIBLE'
