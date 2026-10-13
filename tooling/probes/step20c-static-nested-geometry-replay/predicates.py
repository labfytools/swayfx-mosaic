"""Shared offline/live predicates: facts precede scientific classification.

CONTRACT: full RGB comparisons have no mask/tolerance; grabs require real logs.
INVARIANT: dismissal, client destruction, clipping and layout remain distinct.
"""
import re
from model import Rect,Space,Provenance,Output,popup,crossing,local_clip_to_global,require
from pixels import color_geometry,COLORS
from PIL import Image,ImageChops

class Defect(RuntimeError):
    """A directly measured scientific contract failure, distinct from fixture ambiguity."""

def paint(im,target):
    im=im.convert('RGB');assert im.size==(800,600)
    mask=Image.new('L',im.size);mask.putdata([255 if p==COLORS[target] else 0 for p in im.get_flattened_data()])
    return dict(count=sum(mask.histogram()[1:]),bbox=mask.getbbox())

def point(im,target,origin):
    box=paint(im,target)['bbox'];assert box,('no measured paint',target)
    # WHY: A may be occluded by B; bbox center alone is not a valid hit point.
    x1,y1,x2,y2=box
    for y in range(y1+10,y2-10,5):
        for x in range(x1+10,x2-10,5):
            if all(im.getpixel((xx,yy))==COLORS[target] for yy in range(y-8,y+9) for xx in range(x-8,x+9)):
                return [x+origin,y]
    raise AssertionError('no solid measured interior '+target)

def equal(a,b):
    assert a.size==b.size==(800,600)
    rows=[(i%800,i//800,x,y) for i,(x,y) in enumerate(zip(a.get_flattened_data(),b.get_flattened_data())) if x!=y]
    return dict(equal=not rows,changed=len(rows),bbox=ImageChops.difference(a,b).getbbox(),pixels=rows)

def reference(a,b):
    result=equal(a,b)
    assert result['equal'] and all(c==(48,48,56) for c in a.get_flattened_data()),'unstable reference'
    return result

def configured(text,name):
    rows=re.findall(rf'{name} ROLE_CONFIGURE x=(-?\d+) y=(-?\d+) w=(\d+) h=(\d+)',text)
    assert rows,(name,'no configure')
    return list(map(int,rows[-1]))

def geometry(text,origin,provenance=None):
    a=configured(text,'POPUP_A');b=configured(text,'POPUP_B')
    require(provenance is not None,'popup-owner-provenance-required')
    p=provenance
    top=Rect(Space.GLOBAL,*origin,0,0,p)
    ids={n:list(map(int,re.search(rf'{n} CREATE wl=(\d+) xdg=(\d+) role=(\d+)',text).groups())) for n in ('TOPLEVEL','POPUP_A','POPUP_B')}
    result={}
    parent=top
    for key,name,parent_name,c in [('A','POPUP_A','TOPLEVEL',a),('B','POPUP_B','POPUP_A',b)]:
        parent_id=int(re.search(rf'{name} CREATE .*parent_xdg=(\d+)',text)[1])
        ack=int(re.findall(rf'{name} XDG_CONFIGURE serial=(\d+) ack',text)[-1])
        parent=popup(parent,Rect(Space.POPUP,*c,p),parent_id,ids[parent_name][1],ack,name+' MAP ' in text)
        result[key]=parent.values()
    result.update(configured_A=a,configured_B=b,origin=origin,provenance=dict(owner=p.owner,workspace=p.workspace,generation=p.generation,evidence=p.evidence,state=p.state),
                  crossing={key:crossing(Rect(Space.GLOBAL,*result[key],p),0) for key in ('A','B')})
    return result

def mapped(text):
    for name in ['POPUP_A','POPUP_B']:
        assert text.count(name+' MAP ')==1 and name+' POPUP_DONE ' not in text and name+' DESTROY ' not in text,(name,'not mapped')

def protocol(text):
    assert not re.search(r'wl_display[^\n]*\.error\(|protocol error|invalid_popup_parent|not_the_topmost_popup',text,re.I),'protocol error'
    mapped(text)
    ids={}
    for name in ['TOPLEVEL','POPUP_A','POPUP_B']:
        m=re.search(rf'{name} CREATE wl=(\d+) xdg=(\d+) role=(\d+)',text);assert m
        ids[name]=list(map(int,m.groups()))
    assert len({n for v in ids.values() for n in v})==9,'object identities reused'
    grabs=[]
    for name,parent in [('POPUP_A','TOPLEVEL'),('POPUP_B','POPUP_A')]:
        create=re.search(rf'{name} CREATE .*parent={parent} parent_xdg=(\d+)',text);assert create
        assert int(create[1])==ids[parent][1], 'wrong XDG parent'
        debug_parent=re.search(rf'xdg_surface#{ids[name][1]}\.get_popup\(new id xdg_popup#{ids[name][2]}, xdg_surface#{ids[parent][1]}, xdg_positioner#\d+\)',text)
        require(debug_parent is not None,'debug-parent-request')
        m=re.search(rf'{name} GRAB_REQUEST origin=wl_pointer.button target={parent} serial=(\d+) used=(\d+)',text);assert m
        serial,used=map(int,m.groups());assert serial==used and 0<serial<=0xffffffff
        button=f'POINTER_BUTTON target={parent} serial={serial} button=272 state=1'
        assert text.index(button)<m.start(),'grab serial not from earlier button'
        debug_button=re.search(rf'wl_pointer#\d+\.button\({serial}, \d+, 272, 1\)',text)
        require(debug_button is not None and debug_button.start()<m.start(),'debug-real-button-serial')
        role=text.index(name+' ROLE_CONFIGURE ');cfg=re.search(rf'{name} XDG_CONFIGURE serial=(\d+) ack',text);assert cfg
        mp=text.index(name+' MAP ')
        assert m.start()<role<cfg.start()<mp,'configure ACK map order'
        popup_role=ids[name][2];xdg=ids[name][1];wl=ids[name][0]
        # WAYLAND_DEBUG is independent corroboration, not just fixture claims.
        request=re.search(rf'xdg_popup#{popup_role}\.grab\(wl_seat#\d+, {serial}\)',text);assert request
        ack=re.search(rf'xdg_surface#{xdg}\.ack_configure\({cfg[1]}\)',text);assert ack
        attach=re.search(rf'wl_surface#{wl}\.attach\(',text);assert attach
        commits=list(re.finditer(rf'wl_surface#{wl}\.commit\(\)',text));assert len(commits)>=2
        assert request.start()<commits[0].start()<role<ack.start()<attach.start()<commits[1].start()<mp
        actual=configured(text,name)
        require(re.search(rf'xdg_popup#{popup_role}\.configure\({actual[0]}, {actual[1]}, {actual[2]}, {actual[3]}\)',text) is not None,'debug-popup-configure')
        require(re.search(rf'xdg_surface#{xdg}\.configure\({cfg[1]}\)',text) is not None,'debug-xdg-configure')
        native_attach=re.search(rf'wl_surface#{wl}\.attach\(wl_buffer#(\d+), 0, 0\)',text[ack.start():mp])
        require(native_attach is not None,'popup-native-attach')
        native_buffer=int(native_attach[1])
        native_create=re.search(rf'create_buffer\(new id wl_buffer#{native_buffer}, 0, {actual[2]}, {actual[3]}, {actual[2]*4}, 1\)',text[role:mp])
        require(native_create is not None,'popup-native-configured-size')
        if parent=='POPUP_A':assert text.index('POPUP_A MAP ')<text.index(button)
        grabs.append(dict(popup=name,parent=parent,serial=serial,used=used,origin='wl_pointer.button',ids=ids[name],ack=int(cfg[1]),native_buffer=native_buffer,native_size=actual[2:]))
    assert grabs[0]['serial']<grabs[1]['serial'], 'distinct ordered serials'
    return dict(ids=ids,grabs=grabs,hierarchy='TOPLEVEL -> POPUP_A -> POPUP_B',status='PASS')

def pair(lines,target):
    events=[]
    for line in lines:
        m=re.fullmatch(r'POINTER_BUTTON target=(\w+) serial=(\d+) button=(\d+) state=(\d+)',line);assert m
        events.append([m[1],*map(int,m.groups()[1:])])
    if len(events)!=2 or any(e[0]!=target for e in events) or [e[2:] for e in events]!=[[273,1],[273,0]]:
        raise Defect('wrong actual button recipient/pair: '+str(events))
    assert 0<events[0][1]<events[1][1]<=0xffffffff
    return events

def dismissal(text,buttons):
    if any('target=POPUP_A ' in b or 'target=POPUP_B ' in b for b in buttons):
        raise Defect('invisible popup received actual button')
    done=re.findall(r'(POPUP_[AB]) POPUP_DONE ',text)
    destroyed=re.findall(r'(POPUP_[AB]) DESTROY ',text)
    assert done==['POPUP_B','POPUP_A'] and destroyed==['POPUP_B','POPUP_A'],('dismissal order',done,destroyed)
    return dict(done=done,destroyed=destroyed,invisible_buttons=buttons,status='PASS',meaning='outside dismissal distinct from invisible hit')

def root_clip(text,origin,mosaic,owner_id,start_ns,end_ns):
    # Traces lack popup owner IDs. Correlate the only live root in a bounded
    # owner-observed window; ambiguity is a fixture failure, never rows[-1].
    owners=[s for s in text.splitlines() if 'PI_OWNER output=HEADLESS-1 ' in s and f' id={owner_id} ' in s and start_ns<=int(re.search(r'ns=(\d+)',s)[1])<=end_ns]
    rows=[s for s in text.splitlines() if 'PI_POPUP output=HEADLESS-1 ' in s and start_ns<=int(re.search(r'ns=(\d+)',s)[1])<=end_ns]
    require(bool(owners) and bool(rows),'bounded-root-owner-observations')
    parsed=[]
    for row in rows:
        m=re.search(r'local_index=(\d+) tree=(\S+) enabled=(\d+) clip_valid=(\d+) clip=(-?\d+),(-?\d+),(\d+),(\d+)',row)
        require(m is not None,'root-trace-format')
        index,tree,enabled,valid,*box=m.groups()
        parsed.append((int(index),tree,int(enabled),bool(int(valid)),tuple(map(int,box))))
    require(len({r[1] for r in parsed})==1,'root-chain-unique')
    require(len(set(parsed))==1,'root-window-state-consistent')
    index,tree,enabled,valid,box=parsed[0]
    require(index==1 and enabled==1,'root-enabled-index')
    if valid!=mosaic:raise Defect('root clip state mismatch')
    if mosaic:
        p=Provenance(owner_id,1,'bounded-root-window','PI_OWNER + PI_POPUP')
        global_clip=local_clip_to_global(Rect(Space.CONTENT,*box,p),origin,p)
        require(global_clip.values()==[-800,0,800,600],'root-applied-global-clip')
    return dict(tree=tree,clip_valid=valid,local=list(box),origin=origin,raw=rows[0],owner=owner_id,window=[start_ns,end_ns],correlation='unique root and bounded owner observation; no atomic generation claim',child='inherited source hierarchy')

def popup_pixels(left,right,g,mosaic,baseline):
    # The runner and actual historical replay share exact typed mask conversion.
    require('provenance' in g,'popup-paint-provenance')
    p=Provenance(**g['provenance']);A=Rect(Space.GLOBAL,*g['A'],p);B=Rect(Space.GLOBAL,*g['B'],p)
    clip=Rect(Space.VIEWPORT,-800,0,800,600,p) if mosaic else None
    result={}
    for side,im,ox in [('H1',left,-800),('H2',right,0)]:
        output=Output(side,Rect(Space.GLOBAL,ox,0,800,600,p),1.0,'normal')
        result[side]={name:color_geometry(im,name,r,output,clip,(B,) if name=='POPUP_A' else ()) for name,r in [('POPUP_A',A),('POPUP_B',B)]}
    require(all(result['H1'][name]['count']>0 for name in ('POPUP_A','POPUP_B')),'permitted-popup-color')
    if mosaic:
        result['whole_H2']=equal(baseline,right)
        if not result['whole_H2']['equal']:raise Defect('whole-H2 changed under Mosaic')
    else:
        require(all(result['H2'][name]['count']>0 for name in ('POPUP_A','POPUP_B')),'standard-popup-continuation')
    return result

def terminal(measures,ipc_code,compositor_code,log,protocol_error,rescue,stdout='',stderr='',reaped=True):
    ok=bool(measures and compositor_code==0 and "Handling command 'exit'" in log
            and 'Shutting down sway' in log and not protocol_error and not rescue)
    # Reaping is completed by the runner after recording actual terminal IPC.
    require(type(ipc_code) is int and type(compositor_code) is int,'actual-terminal-codes')
    return dict(scientific_cleanup_pass=ok,ipc_exit=ipc_code,compositor_exit=compositor_code,
        stdout=stdout,stderr=stderr,all_owned_reaped=reaped,ipc_success=ipc_code==0,transport_incident=bool(ok and ipc_code!=0),
        interpretation=('compatible queued-response loss, not proven packet causality' if ok and ipc_code!=0 else 'actual recorded IPC outcome'))


def terminal_exchange(execute, wait, argv, env, measures, compositor_log,
                      protocol_error, rescue, record):
    """CONTRACT: preserve an obtained IPC reply before fallible compositor wait."""
    data=dict(scientific_cleanup_pass=False,ipc_exit=None,stdout='',stderr='',
              compositor_exit=None,measurements_completed=measures)
    try:
        reply=execute(argv,env=env,capture_output=True,text=True,timeout=3)
        data.update(ipc_exit=reply.returncode,stdout=reply.stdout,stderr=reply.stderr)
        record(reply.stdout,reply.stderr)
    except Exception as exc:
        data['ipc_error']=repr(exc)
        return data
    try:
        data['compositor_exit']=wait(timeout=3)
    except Exception as exc:
        data['compositor_error']=repr(exc)
        return data
    try:
        data.update(terminal(measures,data['ipc_exit'],data['compositor_exit'],
            compositor_log(),protocol_error(),rescue(),stdout=data['stdout'],
            stderr=data['stderr'],reaped=False))
    except Exception as exc:
        data['terminal_error']=repr(exc)
    return data
