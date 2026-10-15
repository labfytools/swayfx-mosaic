"""EXPERIMENTAL comparable nonleaf fullscreen, whole-field predictions first."""
import re,time
from PIL import ImageDraw
import cases,validators
from engine import COLORS
from geometry import need,crossing,solid_point,exact,count
from ipc_predicates import ancestry
from model import Provenance
from predicates import geometry


def group_candidate(state,peer_id,group_id,fullscreen=True,applied=None):
    # WHY: IPC serializes pending.fullscreen_mode, workspace marker is always1.
    # CONTRACT: never turn that field into a direct current-state observation.
    # INVARIANT: sampled applied qualification requires post-command configure /
    # ACK / MAP plus measured geometry; native current bit remains NOT_OBSERVABLE.
    path=ancestry(state['snapshot']['tree'],state['owner']['id'])
    rows=[n for n in path[:-1] if n.get('type')=='con' and n.get('id')==group_id]
    need(len(rows)==1,'actual nonleaf group absent');group=rows[0]
    need(group.get('fullscreen_mode',0)==int(fullscreen),'group fullscreen IPC candidate mismatch')
    need(group.get('layout')=='splith' and len(group.get('nodes',[]))==2,'exact horizontal two-child group')
    need({n['id'] for n in group['nodes']}=={state['owner']['id'],peer_id},'owner/peer must be direct children')
    need(not group.get('floating_nodes') and not any((n.get('floating') or '').endswith('on') for n in group['nodes']),'floating group child')
    if fullscreen:
        out=next(o for o in state['snapshot']['outputs'] if o['name']==state['workspace']['output'])['rect']
        need(group['rect']==out,'fullscreen group does not cover output')
        need(out['width']==800 and [n['rect']['width'] for n in group['nodes']]==[400,400],'fullscreen measured400/400 required')
        need(applied and applied.get('source')=='post-command-xdg-configure-ack-map' and applied.get('group_id')==group_id and applied.get('owner_id')==state['owner']['id'] and applied.get('workspace_id')==state['workspace']['id'],'pending-only ancestor is not sampled applied evidence')
    return group


def applied_configure(raw,cut,owner_id,workspace_id,group_id):
    tail=raw[cut:]
    configs=re.findall(r'TOPLEVEL XDG_CONFIGURE serial=(\d+) ack',tail)
    need(configs and 'TOPLEVEL MAP ' in tail,'post-fullscreen configure/ACK/map absent')
    # Actual wire association and SHM mapping are independently parsed by grab().
    need(re.search(r'xdg_surface#\d+\.ack_configure\('+configs[-1]+r'\)',tail),'post-fullscreen actual ACK wire absent')
    return dict(source='post-command-xdg-configure-ack-map',group_id=group_id,owner_id=owner_id,workspace_id=workspace_id,serial=int(configs[-1]),native_current_bit='NOT_OBSERVABLE')


def positioner_adjust(raw):
    values=[]
    for popup in ('POPUP_A','POPUP_B'):
        ids=re.search(rf'{popup} CREATE wl=(\d+) xdg=(\d+) role=(\d+)',raw);need(ids is not None,'popup role absent')
        create=re.search(rf'xdg_surface#{ids[2]}\.get_popup\(new id xdg_popup#{ids[3]}, xdg_surface#\d+, xdg_positioner#(\d+)\)',raw);need(create is not None,'actual positioner absent')
        # IDs may be reused after destroy: bind the latest positioner declaration
        # and all setters before this exact get_popup request.
        before=raw[:create.start()];decl=list(re.finditer(rf'create_positioner\(new id xdg_positioner#{create[1]}\)',before));need(decl,'positioner creation wire absent')
        segment=before[decl[-1].start():]
        adjust=re.findall(rf'xdg_positioner#{create[1]}\.set_constraint_adjustment\((\d+)\)',segment)
        need(adjust==['0'],'different/unobserved positioner adjustment');values.append(int(adjust[0]))
    return values


def comparable(pristine,core):
    for r in (pristine,core):
        need(r.get('fresh') and crossing(r['popup_A'],0,0) and crossing(r['popup_B'],0,0),'actual fresh crossing not exercised')
        need(r['child_widths']==[400,400] and r['applied']['source']=='post-command-xdg-configure-ack-map','pending/noncomparable group')
    keys=('client_sha256','client_source_sha256','protocol_sha256','positioner_adjust','roles','top_configure','child_rects','child_widths','group_rect','popup_A','popup_B','configured_A','configured_B','origin','outputs')
    need(all(pristine[k]==core[k] for k in keys),'pristine/core source/role/actual geometry differs')
    return dict(status='PARTIALLY_FEASIBLE',native_current_bit='NOT_OBSERVABLE',atomic_current_state='NOT_PROVEN')


def expected_h2(baseline,g,output,frame,colors,active_roles=('POPUP_A','POPUP_B'),require_crossing=False):
    # WHY/CONTRACT/INVARIANT: predict whole RGB before acquisition. Standard /
    # fullscreen popup overflow is composed A then B, without a learned mask.
    need(frame=='logical' and output['scale']==1 and output['transform']=='normal','unsupported H2 frame')
    ox,oy,ow,oh=output['logical'];need(baseline.size==(ow,oh),'H2 baseline size')
    expected=baseline.copy();draw=ImageDraw.Draw(expected);parent=g['origin']
    for key,name in (('A','POPUP_A'),('B','POPUP_B')):
        cfg=g['configured_'+key];rect=g[key]
        need(len(cfg)==4 and cfg[2]>0 and cfg[3]>0 and rect==[parent[0]+cfg[0],parent[1]+cfg[1],cfg[2],cfg[3]],'actual configure/global rectangle differs')
        if require_crossing:need(crossing(rect,0,0),'actual popup noncrossing')
        l,t,r,b=max(rect[0],ox),max(rect[1],oy),min(rect[0]+rect[2],ox+ow),min(rect[1]+rect[3],oy+oh)
        if name in active_roles and l<r and t<b:draw.rectangle((l-ox,t-oy,r-ox-1,b-oy-1),fill=colors[name])
        parent=rect
    return expected


def measured_pair(s,tag,baseline,g,active=('POPUP_A','POPUP_B'),cross=False):
    predicted=expected_h2(baseline,g,s.outputs[1],s.frames['HEADLESS-2'],COLORS,active,cross)
    s.record('whole-H2-prediction',tag=tag,rgb_sha256=__import__('hashlib').sha256(predicted.tobytes()).hexdigest(),geometry=g,roles=active)
    images=s.pair_capture(tag);exact(predicted,images[1]);return images


def fresh_geometry(s,state):
    return geometry(s.log('owner'),state['origin'],Provenance(state['owner']['id'],state['workspace']['id'],'NOT_OBSERVABLE','fresh paint + pointer-local corroboration'))


def input_target(s,images,g,target,key):
    for index,output in enumerate(s.outputs):
        try:point=solid_point(images[index],COLORS[target],output,s.frames[output['name']],g[key]);break
        except ValueError:continue
    else:raise ValueError('no freshly painted input interior')
    tails,buttons=s.click('owner',point);s.delivery('owner',g[key],point,tails,buttons,target)


def prepare_group(s):
    # Native container_split ignores singleton H/V parents. Existing filler
    # guarantees siblings>1; peer is created on ws3, then explicitly inserted
    # in the marked nonleaf group. No post-failure empirical repair is allowed.
    s.debit('chain');s.launch_client('owner','fullscreen-client','fullscreen_cross')
    oid=s.find('owner')['id'];s.cmd(f'[con_id={oid}] focus');s.cmd(f'[con_id={oid}] split h')
    path=ancestry(s.snapshot('group-wrapper')['tree'],oid);group=path[-2]
    need(group.get('type')=='con' and [n['id'] for n in group.get('nodes',[])]==[oid],'split did not create owner wrapper')
    gid=group['id'];s.cmd(f'[con_id={gid}] mark --add smx-followup-group')
    s.cmd('workspace 3');s.launch_client('fullscreen-peer','static-reference');peer=s.find('fullscreen-peer')['id']
    s.cmd(f'[con_id={peer}] move container to mark smx-followup-group');s.cmd('workspace 1');s.cmd(f'[con_id={oid}] focus')
    snap=s.snapshot('fullscreen-before');path=ancestry(snap['tree'],oid)
    group=next(n for n in path if n.get('id')==gid)
    need({n['id'] for n in group.get('nodes',[])}=={oid,peer},'peer outside exact owner group')
    return oid,peer,gid


def run(s):
    cases.init_reference(s,1)
    try:oid,peer,gid=prepare_group(s)
    except ValueError as exc:
        s.save('fullscreen-not-exercised',dict(status='NOT_EXERCISED',reason=str(exc)));return 'NOT_EXERCISED'
    baseline=cases.stable_reference(s);cut=len(s.log('owner'))
    s.cmd(f'[con_id={gid}] fullscreen enable');s.cmd(f'[con_id={oid}] focus')
    s.wait(lambda:'TOPLEVEL XDG_CONFIGURE ' in s.log('owner')[cut:] and 'TOPLEVEL MAP ' in s.log('owner')[cut:]);time.sleep(.2)
    state=s.owner('owner');applied=applied_configure(s.log('owner'),cut,oid,state['workspace']['id'],gid)
    group=group_candidate(state,peer,gid,applied=applied)
    top=s.capture('fullscreen-owner','HEADLESS-1');xy=solid_point(top,COLORS['TOPLEVEL'],s.outputs[0],'logical',[*state['origin'],420,320])
    ta,ba=s.click('owner',xy,'left',True);s.wait(lambda:'POPUP_A MAP ' in s.log('owner'))
    root=s.capture('fullscreen-A','HEADLESS-1');xyA=solid_point(root,COLORS['POPUP_A'],s.outputs[0],'logical')
    tb,bb=s.click('owner',xyA,'left',True);s.wait(lambda:'POPUP_B MAP ' in s.log('owner'));time.sleep(.2)
    p=validators.grab(s.log('owner'));adjust=positioner_adjust(s.log('owner'));g=fresh_geometry(s,state)
    s.delivery('owner',[*state['origin'],420,320],xy,ta,ba,'TOPLEVEL',p['grabs'][0]['serial']);s.delivery('owner',g['A'],xyA,tb,bb,'POPUP_A',p['grabs'][1]['serial'])
    if not all(crossing(g[k],0,0) for k in ('A','B')):
        s.save('fullscreen-not-exercised',dict(status='NOT_EXERCISED',geometry=g));return 'NOT_EXERCISED'
    images=measured_pair(s,'fullscreen-mapped',baseline,g,cross=True);input_target(s,images,g,'POPUP_B','B')
    m=__import__('json').loads(__import__('pathlib').Path(s.auth['manifest']).read_text())
    record=dict(client_sha256=s.auth['client_binary_sha256'],client_source_sha256=m['files']['graphics/clients/fullscreen-client.c'],protocol_sha256=m['files']['graphics/protocols/xdg-shell.xml'],positioner_adjust=adjust,fresh=True,applied=applied,roles=p['hierarchy'],top_configure=re.findall(r'TOPLEVEL ROLE_CONFIGURE w=(\d+) h=(\d+)',s.log('owner'))[-1],child_rects=[c['rect'] for c in group['nodes']],child_widths=[c['rect']['width'] for c in group['nodes']],group_rect=group['rect'],popup_A=g['A'],popup_B=g['B'],configured_A=g['configured_A'],configured_B=g['configured_B'],origin=g['origin'],outputs=s.outputs,owner_id=oid,group_id=gid,peer_id=peer,protocol=p)
    s.save('fullscreen-comparability',record)
    before=s.log('owner');start=time.monotonic_ns();s.client_cmd('owner','close_b','COMMAND close_b DONE')
    from lifecycle import explicit_child_close
    explicit_child_close(before,s.log('owner'),p['ids'],start,time.monotonic_ns());time.sleep(.15)
    state=s.owner('owner');group_candidate(state,peer,gid,applied=applied);g=fresh_geometry(s,state)
    images=measured_pair(s,'fullscreen-B-closed',baseline,g,('POPUP_A',));need(not any(count(im,COLORS['POPUP_B']) for im in images),'B residual');input_target(s,images,g,'POPUP_A','A')
    s.cmd(f'[con_id={gid}] fullscreen disable',True);s.cmd(f'[con_id={state["workspace"]["id"]}] layout splith',True);s.expected_layout='splith';time.sleep(.35)
    state=s.owner('owner');need(state['owner']['id']==oid,'owner changed on standard return');group_candidate(state,peer,gid,fullscreen=False)
    g=fresh_geometry(s,state);images=measured_pair(s,'fullscreen-standard-A',baseline,g,('POPUP_A',));input_target(s,images,g,'POPUP_A','A')
    s.close_client('owner',scenario='nested');final=s.pair_capture('fullscreen-final');exact(baseline,final[1])
    return 'PARTIALLY_FEASIBLE'
