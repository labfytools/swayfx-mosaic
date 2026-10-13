"""Shared offline/live predicates: facts precede scientific classification.

CONTRACT: full RGB comparisons have no mask/tolerance; grabs require real logs.
INVARIANT: dismissal, client destruction, clipping and layout remain distinct.
"""
import re
from PIL import Image,ImageChops
COLORS=dict(TOPLEVEL=(35,68,204),POPUP_A=(224,192,32),POPUP_B=(32,208,160))

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

def geometry(text,origin):
    a=configured(text,'POPUP_A');b=configured(text,'POPUP_B')
    A=[origin[0]+a[0],origin[1]+a[1],a[2],a[3]]
    B=[A[0]+b[0],A[1]+b[1],b[2],b[3]]
    assert all(r[0]<0<r[0]+r[2] for r in [A,B]),'popup crossing NOT EXERCISED'
    return dict(A=A,B=B,configured_A=a,configured_B=b,origin=origin)

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
        m=re.search(rf'{name} GRAB_REQUEST origin=wl_pointer.button target={parent} serial=(\d+) used=(\d+)',text);assert m
        serial,used=map(int,m.groups());assert serial==used and 0<serial<=0xffffffff
        button=f'POINTER_BUTTON target={parent} serial={serial} button=272 state=1'
        assert text.index(button)<m.start(),'grab serial not from earlier button'
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
        if parent=='POPUP_A':assert text.index('POPUP_A MAP ')<text.index(button)
        grabs.append(dict(popup=name,parent=parent,serial=serial,used=used,origin='wl_pointer.button',ids=ids[name],ack=int(cfg[1])))
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

def root_clip(text,origin,mosaic):
    rows=[s for s in text.splitlines() if 'PI_POPUP output=HEADLESS-1 ' in s]
    assert rows,'no root clip trace'
    row=rows[-1]
    m=re.search(r'local_index=(\d+) tree=(\S+) enabled=(\d+) clip_valid=(\d+) clip=(-?\d+),(-?\d+),(\d+),(\d+)',row);assert m
    index,tree,enabled,valid,*box=m.groups();box=list(map(int,box))
    assert int(index)==1 and int(enabled)==1
    if bool(int(valid))!=mosaic:raise Defect('root clip state mismatch')
    if mosaic:
        assert [origin[0]+box[0],origin[1]+box[1],box[2],box[3]]==[-800,0,800,600], 'root/owner applied clip relationship'
    return dict(tree=tree,clip_valid=bool(int(valid)),local=box,origin=origin,raw=row,child='inherited; source hierarchy plus measured B render/input')

def popup_pixels(left,right,g,mosaic,baseline):
    result={side:{n:paint(im,n) for n in COLORS} for side,im in [('H1',left),('H2',right)]}
    for key,name in [('A','POPUP_A'),('B','POPUP_B')]:
        rect=g[key]
        assert result['H1'][name]['count']>0,'permitted popup color absent'
        if mosaic and result['H2'][name]['count']:
            raise Defect('forbidden popup pixels '+name)
        if not mosaic and not result['H2'][name]['count']:
            raise AssertionError('standard popup continuation absent '+name)
        # CONTRACT: compare the exact color region against configured geometry,
        # subtracting B's occlusion of A, not against a predicted painted bbox.
        for side,im,ox in [('H1',left,-800),('H2',right,0)]:
            for y in range(600):
                for x in range(800):
                    gx=x+ox
                    inside=rect[0]<=gx<rect[0]+rect[2] and rect[1]<=y<rect[1]+rect[3]
                    if key=='A':
                        B=g['B'];inside=inside and not (B[0]<=gx<B[0]+B[2] and B[1]<=y<B[1]+B[3])
                    expected=inside and (not mosaic or side=='H1')
                    if (im.getpixel((x,y))==COLORS[name])!=expected:
                        raise AssertionError(('paint/configured position mismatch',name,side,x,y))
    if mosaic:
        result['whole_H2']=equal(baseline,right)
        if not result['whole_H2']['equal']:raise Defect('whole-H2 changed under Mosaic')
    return result

def terminal(measures,ipc_code,compositor_code,log,protocol_error,rescue):
    ok=bool(measures and compositor_code==0 and "Handling command 'exit'" in log
            and 'Shutting down sway' in log and not protocol_error and not rescue)
    return dict(scientific_cleanup_pass=ok,ipc_exit=ipc_code,compositor_exit=compositor_code,
        ipc_success=ipc_code==0,transport_incident=bool(ok and ipc_code!=0),
        interpretation=('compatible queued-response loss, not proven packet causality' if ok and ipc_code!=0 else 'actual recorded IPC outcome'))
