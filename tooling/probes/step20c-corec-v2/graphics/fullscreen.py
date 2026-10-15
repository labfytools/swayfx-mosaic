"""Prospective equal-child nonleaf fullscreen handler; applied evidence is sampled."""
import re,time
import cases,validators
from engine import COLORS
from geometry import *
from ipc_predicates import ancestry
from model import Provenance
from PIL import Image,ImageChops,ImageDraw
from predicates import geometry

def group_candidate(state,peer_id,group_id=None,fullscreen=True):
    path=ancestry(state['snapshot']['tree'],state['owner']['id'])
    if fullscreen:
        group=validators.fullscreen_ancestor(path)
        need(group['type']=='con' and group.get('fullscreen_mode')==1 and len(group['nodes'])==2,'exact nonleaf fullscreen group')
    else:
        rows=[n for n in path[:-1] if n.get('type')=='con' and n.get('id')==group_id]
        need(len(rows)==1,'current two-child group absent after fullscreen exit');group=rows[0]
        need(group.get('fullscreen_mode',0)==0 and len(group.get('nodes',[]))==2,'group still fullscreen or child count changed')
    need(group_id is None or group['id']==group_id,'fullscreen group identity changed')
    need({n['id'] for n in group['nodes']}=={state['owner']['id'],peer_id},'fullscreen exact owner/peer children')
    need(group.get('layout')=='splith','fullscreen group split orientation')
    rect=group['rect'];out=next(o for o in state['snapshot']['outputs'] if o['name']==state['workspace']['output'])['rect']
    if fullscreen:need(rect==out,'fullscreen group does not cover output')
    else:need(rect==out,'current split group does not cover output after fullscreen exit')
    widths=[n['rect']['width'] for n in group['nodes']]
    need(widths[0]==widths[1] and sum(widths)==rect['width'],'fullscreen equal child widths')
    return group

def comparable(pristine,core):
    # WHY/CONTRACT/INVARIANT: compare actual roles, configures and geometry
    # measured for these binaries; matching requested placement is insufficient.
    for r in (pristine,core):
        need(r['fresh'] and r['crossing_A'] and r['crossing_B'] and crossing(r['popup_A'],0,0) and crossing(r['popup_B'],0,0),'stale/noncrossing fullscreen evidence')
    keys=('client_sha256','roles','top_configure','child_rects','group_rect','popup_A','popup_B','configured_A','configured_B','origin','outputs')
    need(all(pristine[k]==core[k] for k in keys),'noncomparable pristine/core fullscreen evidence')
    return dict(status='PARTIALLY_FEASIBLE',atomic_current_state='NOT_PROVEN')

def fresh_geometry(s,state,p):
    return geometry(s.log('owner'),state['origin'],Provenance(state['owner']['id'],state['workspace']['id'],'NOT OBSERVABLE','fresh native paint + pointer-local corroboration'))

def fullscreen_h2_field(images,baseline,g,output,frame,colors,active_roles=('POPUP_A','POPUP_B'),require_crossing=False):
    # WHY/CONTRACT/INVARIANT: fullscreen standard overflow must reproduce the
    # complete measured H2 field. P1/C8 are scale-1, normal, logical captures;
    # configured global rectangles are clipped with half-open output bounds.
    need(frame=='logical' and output['scale']==1 and output['transform']=='normal','fullscreen H2 frame/scale/transform unsupported')
    ox,oy,ow,oh=output['logical'];need(baseline.size==(ow,oh) and images[1].size==baseline.size,'fullscreen H2 image dimensions')
    expected=baseline.copy();draw=ImageDraw.Draw(expected)
    parent=g['origin']
    for key,name in (('A','POPUP_A'),('B','POPUP_B')):
        configured=g['configured_'+key];rect=g[key]
        need(len(configured)==len(rect)==4 and configured[2]>0 and configured[3]>0,'fullscreen popup configured extent')
        need(rect==[parent[0]+configured[0],parent[1]+configured[1],configured[2],configured[3]],'fullscreen popup geometry/configure mismatch')
        if require_crossing:need(g.get('crossing',{}).get(key) is True,'fullscreen popup crossing not traversed')
        left=max(rect[0],ox);top=max(rect[1],oy);right=min(rect[0]+rect[2],ox+ow);bottom=min(rect[1]+rect[3],oy+oh)
        if name in active_roles and left<right and top<bottom:
            # Pillow endpoints are inclusive; convert our half-open rectangle.
            draw.rectangle((left-ox,top-oy,right-ox-1,bottom-oy-1),fill=colors[name])
        parent=rect
    need(ImageChops.difference(expected,images[1]).getbbox() is None,'fullscreen whole H2 RGB field differs')

def input_target(s,images,g,target,key):
    point=None
    for index,output in enumerate(s.outputs):
        try:point=solid_point(images[index],COLORS[target],output,s.frames[output['name']],g[key]);break
        except Ambiguous:continue
    need(point is not None,'popup has no visible solid input region on either output')
    tails,buttons=s.click('owner',point);s.delivery('owner',g[key],point,tails,buttons,target)

def run(s):
    cases.init_reference(s,1);s.debit('chain');s.launch_client('owner','fullscreen-client','fullscreen_cross')
    owner_id=s.find('owner')['id'];s.cmd(f'[con_id={owner_id}] split h');s.launch_client('fullscreen-peer','static-reference')
    peer_id=s.find('fullscreen-peer')['id'];tree=s.snapshot('fullscreen-before')['tree'];path=ancestry(tree,owner_id)
    group=path[-2];need(group.get('type')=='con' and {n['id'] for n in group.get('nodes',[])}=={owner_id,peer_id},'exact two-child group preparation')
    gid=group['id'];cut=len(s.log('owner'));s.cmd(f'[con_id={gid}] fullscreen enable');s.cmd(f'[con_id={owner_id}] focus')
    s.wait(lambda:'TOPLEVEL XDG_CONFIGURE ' in s.log('owner')[cut:] and 'TOPLEVEL MAP ' in s.log('owner')[cut:]);time.sleep(.2)
    state=s.owner('owner');group=group_candidate(state,peer_id,gid);baseline=cases.stable_reference(s)
    top=s.capture('fullscreen-owner','HEADLESS-1');xy=solid_point(top,COLORS['TOPLEVEL'],s.outputs[0],s.frames['HEADLESS-1'],[*state['origin'],420,320])
    ta,ba=s.click('owner',xy,'left',True);s.wait(lambda:'POPUP_A MAP ' in s.log('owner'))
    root=s.capture('fullscreen-rootA','HEADLESS-1');xyA=solid_point(root,COLORS['POPUP_A'],s.outputs[0],s.frames['HEADLESS-1'])
    tb,bb=s.click('owner',xyA,'left',True);s.wait(lambda:'POPUP_B MAP ' in s.log('owner'));time.sleep(.2)
    p=validators.grab(s.log('owner'));g=fresh_geometry(s,state,p)
    s.delivery('owner',[*state['origin'],420,320],xy,ta,ba,'TOPLEVEL',p['grabs'][0]['serial'])
    s.delivery('owner',g['A'],xyA,tb,bb,'POPUP_A',p['grabs'][1]['serial'])
    images=s.pair_capture('fullscreen-mapped')
    if not all(crossing(g[k],0,0) for k in ('A','B')):
        s.save('fullscreen-not-exercised',dict(status='NOT_EXERCISED',geometry=g,reason='actual configured popup crossing absent'))
        return 'NOT_EXERCISED'
    validators.standard_spill(images,COLORS)
    fullscreen_h2_field(images,baseline,g,s.outputs[1],s.frames['HEADLESS-2'],COLORS,require_crossing=True)
    fresh=s.owner('owner');group_candidate(fresh,peer_id,gid);need(fresh['origin']==state['origin'],'stale fullscreen geometry')
    record=dict(client_sha256=s.auth['prospective']['client_binary_sha256'],source_manifest_sha256=s.auth['manifest_sha256'],fresh=True,crossing_A=True,crossing_B=True,roles=p['hierarchy'],top_configure=re.findall(r'TOPLEVEL ROLE_CONFIGURE w=(\d+) h=(\d+)',s.log('owner'))[-1],child_rects=[c['rect'] for c in group['nodes']],group_rect=group['rect'],popup_A=g['A'],popup_B=g['B'],configured_A=g['configured_A'],configured_B=g['configured_B'],origin=g['origin'],outputs=s.outputs,owner_id=owner_id,group_id=gid,peer_id=peer_id,protocol=p,atomic_current_state='NOT_PROVEN')
    s.save('fullscreen-comparability',record)
    input_target(s,images,g,'POPUP_B','B');input_target(s,images,g,'POPUP_A','A')
    if s.spec['id']=='C8':
        s.cmd(f'[con_id={gid}] fullscreen disable',True);s.cmd(f'[con_id={state["workspace"]["id"]}] layout splith',True);s.expected_layout='splith';time.sleep(.35)
        state=s.owner('owner');need(state['owner']['id']==owner_id,'C8 owner identity changed')
        p2=validators.grab(s.log('owner'));need(p2['ids']==p['ids'],'C8 popup chain changed')
        state=s.owner('owner');need(state['owner']['id']==owner_id,'C8 owner identity changed after fullscreen exit')
        group_candidate(state,peer_id,gid,fullscreen=False)
        g=fresh_geometry(s,state,p)
        images=s.pair_capture('fullscreen-exited-standard')
        fullscreen_h2_field(images,baseline,g,s.outputs[1],s.frames['HEADLESS-2'],COLORS);input_target(s,images,g,'POPUP_B','B')
    before=s.log('owner');start=time.monotonic_ns();s.client_cmd('owner','close_b','COMMAND close_b DONE');time.sleep(.2)
    from lifecycle import explicit_child_close
    explicit_child_close(before,s.log('owner'),p['ids'],start,time.monotonic_ns())
    state=s.owner('owner');need(state['owner']['id']==owner_id,'owner identity changed after B close')
    group_candidate(state,peer_id,gid,fullscreen=s.spec['id']=='P1');g=fresh_geometry(s,state,p)
    images=s.pair_capture('fullscreen-B-closed');need(not any(count(image,COLORS['POPUP_B']) for image in images),'B residual')
    fullscreen_h2_field(images,baseline,g,s.outputs[1],s.frames['HEADLESS-2'],COLORS,active_roles=('POPUP_A',));input_target(s,images,g,'POPUP_A','A')
    s.close_client('owner')
    if s.spec['id']=='P1' and any(n.get('id')==gid for n in cases.nodes(s.snapshot('fullscreen-after-owner')['tree'])):s.cmd(f'[con_id={gid}] fullscreen disable',True)
    final=s.pair_capture('fullscreen-final');exact(baseline,final[1])
    return 'PARTIALLY_FEASIBLE'
