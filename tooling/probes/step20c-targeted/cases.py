"""Small campaign scenarios over the same reviewed Session; no historical runner copy."""
import re,time
from PIL import ImageChops
from engine import *
from geometry import *

def init_reference(s,prefix_fillers=1):
    s.cmd('workspace 2');s.launch_client('reference','static-reference');rid=s.find('reference')['id'];s.cmd(f'[con_id={rid}] border none')
    s.cmd('workspace 1')
    for i in range(prefix_fillers):s.launch_client('filler'+str(i),'static-reference')
    s.cmd('layout mosaic' if s.spec['mode']=='mosaic' else 'layout splith')
    return rid

def stable_reference(s):
    s.inject('move',[s.outputs[0]['logical'][0]+10,s.outputs[0]['logical'][1]+590]);time.sleep(.15)
    a=s.capture('H2-reference1','HEADLESS-2');time.sleep(.6);b=s.capture('H2-reference2','HEADLESS-2');exact(a,b)
    need(all(v==(48,48,56) for v in a.get_flattened_data()),'static uniform H2');s.save('reference-stability',dict(status='PASS',exact=exact(a,b)));return a

def marker_host_baseline(s):
    """D3-only pre-XDG association: source + creation timing + cardinality.

    This does not observe native owner IDs or host child count. No root is
    selected by clip/index after the owner exists.
    """
    from transition import observed_epochs
    need(s.spec.get('marker',False) and s.spec['mode']=='mosaic' and 'owner' not in s.proc,'prospective pre-owner marker baseline')
    marker=s.proc.get('marker-background');need(marker is not None and marker.poll() is None,'live marker layer client')
    start=next(e['ns'] for e in s.events if e['kind']=='spawn' and e['name']=='marker-background')
    end=time.monotonic_ns();trace=s.log('compositor')
    creations=[l for l in trace.splitlines() if 'new layer surface: namespace ' in l]
    need(len(creations)==1 and 'namespace wallpaper layer 0 ' in creations[0],'one wallpaper layer creation')
    snapshot=s.snapshot('pre-XDG-marker-host')
    need(not any(n.get('app_id')=='org.mosaic.NestedGrabProbe' for n in nodes(snapshot['tree'])),'no popup owner before baseline')
    epochs=observed_epochs(trace,'HEADLESS-1',start,end);tree=None;observed=[]
    for e in epochs:
        need(e['scene'] is not None,'complete baseline callback')
        roots=e['roots']
        if not roots:
            need(tree is None,'marker host disappeared before owner');continue
        need(len(roots)==1,'unique pre-XDG host')
        r=roots[0]
        need(r.get('local_index')=='1' and r.get('enabled')=='1' and r.get('clip_valid')=='0' and r.get('clip')=='0,0,0,0','source-backed ordinary layer host')
        if tree is None:tree=r['tree']
        need(r['tree']==tree,'stable pre-XDG host')
        observed.append(e)
    need(len(observed)>=2,'two complete pre-XDG host observations')
    baseline=dict(tree=tree,window=[start,end],epochs=epochs,layer_creation=creations[0],marker_pid=marker.pid,snapshot=snapshot,
        correlation='single layer constructor + pre-owner timing + stable cardinality; no native layer ID or child count')
    s.save('marker-host-baseline',baseline);s.marker_host=baseline
    return baseline

def associated_root(roots,baseline=None,commit_ns=None):
    if baseline is None:
        need(len(roots)==1 and roots[0].get('local_index')=='1','unique first popup root');return roots[0]
    need(commit_ns is not None and commit_ns>baseline['window'][1],'root callback after pre-XDG baseline')
    need(len(roots)==2 and len({r.get('tree') for r in roots})==2,'one known layer host plus one new XDG root')
    need([r.get('local_index') for r in roots]==['1','2'],'native host order retained')
    known=[r for r in roots if r.get('tree')==baseline['tree']]
    need(len(known)==1 and known[0].get('enabled')=='1' and known[0].get('clip_valid')=='0' and known[0].get('clip')=='0,0,0,0','same unchanged known layer host')
    return next(r for r in roots if r['tree']!=baseline['tree'])

def root_state(s,state,origin,window_start,expect_hidden=False,previous=None,expected_tree=None):
    from transition import observed_epochs
    from ipc_predicates import ancestry
    end=time.monotonic_ns();output=state['workspace']['output']
    out=next(o['logical'] for o in s.outputs if o['name']==output)
    need(state['workspace']['layout']=='mosaic' and origin==state['origin'],'current Mosaic origin')
    path=ancestry(state['snapshot']['tree'],state['owner']['id'])
    need(path and path[-1]['id']==state['owner']['id'],'exact IPC owner ancestry')
    need([n['id'] for n in path if n.get('type')=='workspace']==[state['workspace']['id']] and
         [n['name'] for n in path if n.get('type')=='output']==[output],'exact workspace output ancestry')
    live=[n for n in nodes(state['snapshot']['tree']) if n.get('app_id')==state['owner']['app_id'] and n.get('visible')]
    need(len(live)==1 and live[0]['id']==state['owner']['id'],'unique live XDG owner')
    prot=protocol(s.log('owner'));need(len(prot['grabs'])==2,'two real grabs')
    epochs=observed_epochs(s.log('compositor'),output,window_start,end)
    rows=[];trees=set();applied=False
    for e in epochs:
        c,sc,roots=e['commit'],e['scene'],e['roots']
        need(c.get('has_buffer') in ('0','1') and sc is not None and sc.get('workspace')==str(state['workspace']['id']) and sc.get('layout')=='5','complete current callback workspace/layout')
        owners=[o for o in e['owners'] if o.get('id')==str(state['owner']['id'])]
        need(len(owners)==1 and owners[0].get('scene_valid')=='1','exact applied owner')
        r=associated_root(roots,getattr(s,'marker_host',None),int(c['ns']))
        o=owners[0];trees.add(r['tree'])
        need(len(trees)==1 and (expected_tree is None or r['tree']==expected_tree),'same live root')
        need(int(c['ns'])<int(sc['ns'])<int(o['ns'])<int(r['ns']),'callback record order')
        scene=list(map(int,o['scene'].split(',')))+list(map(int,o['applied_size'].split(',')))
        target=scene==state['scene']
        old=previous is not None and scene==previous['scene']
        need(target or (old and not applied),'unexpected or stale applied owner geometry')
        chosen=state if target else previous
        need(o['current']==','.join(str(chosen['owner']['rect'][k] if k!='y' else chosen['owner']['rect'][k]-chosen['owner']['deco_rect']['height']) for k in ('x','y','width','height')) or
             list(map(int,o['current'].split(',')))==exterior_ipc(chosen['owner']),'current owner geometry')
        win=chosen['owner']['window_rect'];actual=[scene[0]+win['x'],scene[1]+chosen['owner']['deco_rect']['height']+win['y']]
        need(actual==chosen['origin'],'applied content origin')
        box=list(map(int,r['clip'].split(',')));global_box=[box[0]+actual[0],box[1]+actual[1],*box[2:]]
        hidden=intersection(scene,out)[2]==0 or intersection(scene,out)[3]==0
        need(r['enabled']=='1' and r['clip_valid']=='1','enabled clipped root')
        need((box[2]==0 or box[3]==0) if hidden else global_box==out,'every comparable root clip')
        tile=list(map(int,sc['tile_scene'].split(',')));clip=list(map(int,sc['clip'].split(',')))
        need(sc['clip_valid']=='1' and [out[0]+tile[0]+clip[0],out[1]+tile[1]+clip[1],*clip[2:]]==out,'applied tiling viewport')
        if target:
            need(hidden==expect_hidden,'target visibility');applied=True
        rows.append(dict(state='applied-target' if target else 'old-applied',owner=o,scene=sc,root=r,commit=c,local_clip=box,global_clip=global_box,raw=e['raw'],all_roots=roots,known_layer_host=getattr(s,'marker_host',{}).get('tree')))
    need(applied,'target applied callback missing')
    return dict(tree=next(iter(trees)),states=rows,window=[window_start,end],ids=prot['ids'],marker_baseline=getattr(s,'marker_host',None),correlation='bounded unique live XDG hierarchy and exact IPC ancestry; no native parent ID or atomic generation')

def open_chain(s,tail_fillers=0):
    if s.spec.get('marker',False) and s.spec['mode']=='mosaic':marker_host_baseline(s)
    s.debit('chain');s.launch_client('owner',s.spec['client'],s.spec['placement'])
    for i in range(tail_fillers):s.launch_client('tail'+str(i),'static-reference')
    s.cmd(f'[con_id={s.find("owner")["id"]}] focus');state=s.calibrate('owner');baseline=stable_reference(s)
    im=s.capture('owner-top','HEADLESS-1');rect=[*state['origin'],state['owner']['window_rect']['width'],state['owner']['window_rect']['height']]
    xy=solid_point(im,COLORS['TOPLEVEL'],s.outputs[0],s.frames['HEADLESS-1'],rect)
    need(contains([*state['origin'],420,575 if s.spec['campaign']=='D1' else 320],xy),'opening native bounds')
    ta,ba=s.click('owner',xy,'left',True);s.wait(lambda:'POPUP_A MAP ' in s.log('owner'));time.sleep(.2)
    aim=s.capture('popup-A','HEADLESS-1');prov=Provenance(state['owner']['id'],state['workspace']['id'],'bounded-opening-window',state['evidence'])
    xyA=solid_point(aim,COLORS['POPUP_A'],s.outputs[0],s.frames['HEADLESS-1'])
    tb,bb=s.click('owner',xyA,'left',True);s.wait(lambda:'POPUP_B MAP ' in s.log('owner'));time.sleep(.2)
    window=time.monotonic_ns();time.sleep(.15);p=protocol(s.log('owner'));g=geometry(s.log('owner'),state['origin'],prov)
    s.delivery('owner',rect,xy,ta,ba,'TOPLEVEL',p['grabs'][0]['serial']);s.delivery('owner',g['A'],xyA,tb,bb,'POPUP_A',p['grabs'][1]['serial'])
    need(all(crossing(g[k],s.spec['axis'],s.spec['boundary']) for k in ('A','B')),'actual root and child crossing NOT EXERCISED')
    left,right=s.pair_capture('mapped')
    for name in ('POPUP_A','POPUP_B'):
        need(count(left,COLORS[name])>0,'permitted popup pixels missing')
        if s.spec['mode']=='pristine':need(count(right,COLORS[name])>0,'standard popup continuation missing')
    if s.spec['mode']=='mosaic':
        exact(baseline,right)
        root=root_state(s,state,state['origin'],window)
    else:root=dict(status='NOT OBSERVABLE',meaning='unmodified control has no private clip instrumentation')
    s.save('chain',dict(protocol=p,geometry=g,state=state,root=root,H2_exact=s.spec['mode']=='mosaic',color_counts={n:[count(left,c),count(right,c)] for n,c in COLORS.items()}))
    return state,baseline,p,g,left,right

def popup_campaign(s):
    init_reference(s);state,baseline,p,g,left,right=open_chain(s)
    xy=solid_point(left,COLORS['POPUP_B'],s.outputs[0],s.frames['HEADLESS-1'],g['B']);tails,buttons=s.click('owner',xy);s.delivery('owner',g['B'],xy,tails,buttons,'POPUP_B')
    forbidden=intersection(g['B'],s.outputs[1]['logical']);need(forbidden[2]>6 and forbidden[3]>6,'H2 crossing interior missing')
    xy=[forbidden[0]+forbidden[2]//2,forbidden[1]+forbidden[3]//2]
    if s.spec['mode']=='pristine':
        # The point must be real standard paint, not just a requested extent.
        xy=solid_point(right,COLORS['POPUP_B'],s.outputs[1],s.frames['HEADLESS-2'],g['B']);tails,buttons=s.click('owner',xy);s.delivery('owner',g['B'],xy,tails,buttons,'POPUP_B')
    else:
        tails,buttons=s.click('owner',xy);ds=dismissal(tails['owner'],buttons['owner']);s.save('dismissal',dict(proof=ds,reference_buttons=buttons.get('reference'),interpretation='outside grab dismissal; no universal click-through claim'))
        need(not any('target=POPUP_A ' in l or 'target=POPUP_B ' in l for v in buttons.values() for l in v),'forbidden popup delivery')
    s.close_client('owner');time.sleep(.2);final=s.pair_capture('final');exact(baseline,final[1]);need(not any(count(im,COLORS[n]) for im in final for n in ('POPUP_A','POPUP_B')),'popup residual')
    return 'PASS'

def hidden_campaign(s):
    init_reference(s,2);state,baseline,p,g,left,right=open_chain(s,2)
    xy=solid_point(left,COLORS['POPUP_B'],s.outputs[0],'logical',g['B']);tails,buttons=s.click('owner',xy);s.delivery('owner',g['B'],xy,tails,buttons,'POPUP_B')
    delta=state['scene'][0]+state['scene'][2]-s.outputs[0]['logical'][0]+16;start=time.monotonic_ns();s.scroll('owner',delta);hidden=s.owner('owner')
    need(intersection(hidden['scene'],s.outputs[0]['logical'])[2]==0,'owner not completely hidden')
    images=s.pair_capture('fully-hidden');need(not any(count(im,COLORS[n]) for im in images for n in ('POPUP_A','POPUP_B')),'hidden popup residual');exact(baseline,images[1])
    root=root_state(s,hidden,hidden['origin'],start,True,previous=state);cut=len(s.log('owner'));s.inject('move',[-790,590]);need('target=POPUP_A ' not in s.log('owner')[cut:] and 'target=POPUP_B ' not in s.log('owner')[cut:],'hidden popup pointer enter')
    return_start=time.monotonic_ns();s.scroll('owner',-delta);restored=s.owner('owner');need(restored['origin']==state['origin'],'same owner origin restored')
    images=s.pair_capture('returned');exact(baseline,images[1]);returned_root=root_state(s,restored,restored['origin'],return_start,previous=hidden,expected_tree=root['tree']);fresh=protocol(s.log('owner'));need(fresh['ids']==p['ids'] and fresh['grabs']==p['grabs'],'unchanged live chain')
    xy=solid_point(images[0],COLORS['POPUP_B'],s.outputs[0],'logical',g['B']);tails,buttons=s.click('owner',xy);s.delivery('owner',g['B'],xy,tails,buttons,'POPUP_B')
    s.save('hidden-return',dict(status='PASS',hidden=hidden,empty_root=root,returned=restored,returned_root=returned_root,ids=p['ids']))
    s.close_client('owner');final=s.pair_capture('final');exact(baseline,final[1]);return 'PASS'


def saved_campaign(s):
    from validators import held_configure
    init_reference(s,2);s.launch_client('owner','saved-client');s.cmd(f'[con_id={s.find("owner")["id"]}] focus');state=s.calibrate('owner');baseline=stable_reference(s)
    before=s.log('owner');serials=re.findall(r'ACK ns=\d+ serial=(\d+)',before);need(serials,'initial ACK');prior=int(serials[-1]);need('COMMIT ns=' in before,'initial mapped SHM')
    # Parse source contract + /proc argv; observed elapsed timeout corroborates
    # the assigned 2500ms value, without inventing a native saved-node record.
    argv=Path(f'/proc/{s.comp.pid}/cmdline').read_bytes().split(b'\0');need(b'-Dtxn-timeout=2500' in argv,'actual startup timeout option')
    s.client_cmd('owner','hold_next_configure','COMMAND hold_next_configure DONE');cut=len(s.log('owner'));ccut=len(s.log('compositor'));request=time.monotonic_ns()
    s.cmd('workspace 1');request=time.monotonic_ns();s.cmd('gaps inner current set 30',True);pending=s.snapshot('saved-requested-pending');pending_owner=s.find('owner');pending_ws=workspace(pending['tree'],'1');need(pending_owner['id']==state['owner']['id'] and pending_ws['id']==state['workspace']['id'] and pending_ws.get('gaps',{}).get('inner')==30,'same ws1 owner and requested runtime gaps')
    s.wait(lambda:'HELD ' in s.log('owner')[cut:]);proof=held_configure(before,s.log('owner')[cut:],prior);need(proof['ns']>request,'held configure after runtime geometry command');need(proof['requested_size']==[pending_owner['window_rect']['width'],pending_owner['window_rect']['height']],'wire requested size matches pending IPC geometry')
    elapsed=(time.monotonic_ns()-request)/1e9;need(elapsed<2.1,'held observation must precede natural timeout')
    held=s.pair_capture('held');need((time.monotonic_ns()-request)/1e9<2.45,'held capture finished before deadline')
    s.wait(lambda:'timed out (' in s.log('compositor')[ccut:],seconds=3.5)
    timeout_ns=time.monotonic_ns();need(re.search(r'timed out \(\d*[1-9]\d* waiting\)',s.log('compositor')[ccut:]),'transaction actually waiting at natural timeout');need(timeout_ns-request>=2_300_000_000,'observed timeout consistent with2500ms');need(s.proc['owner'].poll() is None,'client alive at natural timeout')
    proof=held_configure(before,s.log('owner')[cut:],prior);after=s.pair_capture('natural-timeout');exact(baseline,held[1]);exact(baseline,after[1])
    s.save('saved-observability',dict(status='INCONCLUSIVE',request_ns=request,timeout_observed_ns=timeout_ns,held=proof,startup_argv=[v.decode() for v in argv],initial_state=state,pending_snapshot=pending,pending_owner=pending_owner,requested_workspace=pending_ws,
        source_timeout_ms=2500,natural_timeout=[l for l in s.log('compositor')[ccut:].splitlines() if 'timed out (' in l],saved_node_identity='NOT OBSERVABLE',saved_render_identity='NOT PROVEN',saved_clipping='SOURCE_ONLY; SHM not a native saved-node identity'))
    s.close_client('owner','close');final=s.pair_capture('final');exact(baseline,final[1]);return 'INCONCLUSIVE'

def input_campaign(s):
    from validators import native_pairs
    init_reference(s);s.launch_client('owner','region-client','both_cross');s.cmd(f'[con_id={s.find("owner")["id"]}] focus');s.calibrate('owner');baseline=stable_reference(s)
    point=s.fresh_delivery('owner','input-full')
    s.client_cmd('owner','region_empty_top','COMMAND region_empty_top DONE');time.sleep(.15)
    empty_state=s.owner('owner');empty=s.capture('input-empty','HEADLESS-1')
    # Deliberately unchanged global point is the empty-region comparison.
    tails,buttons=s.click('owner',point);need(not buttons.get('owner'),'empty region owner button');s.save('input-empty-hit',dict(point=point,state=empty_state,buttons=buttons,tails=tails))
    s.client_cmd('owner','region_full_top','COMMAND region_full_top DONE');time.sleep(.15);s.fresh_delivery('owner','input-full-restored')
    s.cmd(f'[con_id={s.find("filler0")["id"]}] focus',True);s.cmd(f'[con_id={s.find("owner")["id"]}] focus',True);time.sleep(.2);s.fresh_delivery('owner','input-focus-return')
    if s.spec['mode']=='mosaic':
        s.scroll('owner',20);s.fresh_delivery('owner','input-camera')
        s.cmd(f'[con_id={s.find("owner")["id"]}] layout splith',True);time.sleep(.35);s.fresh_delivery('owner','input-standard')
    else:
        s.save('input-camera-standard',dict(camera='NOT APPLICABLE: unmodified pristine control',standard='already splith'))
    s.close_client('owner');final=s.pair_capture('final');exact(baseline,final[1]);s.save('ordering',dict(status='INCONCLUSIVE',pairs=native_pairs(s.log('compositor')),native_hit='NOT OBSERVABLE',atomic_generation='NOT PROVEN',buffer_lifetime='NOT PROVEN'))
    return 'INCONCLUSIVE'

def dynamic_campaign(s):
    init_reference(s,2);state,baseline,p,g,left,right=open_chain(s);owner_id=state['owner']['id'];ws_id=state['workspace']['id'];order=state['workspace']['mosaic']['rows'][0]['children'];stages=[]
    for out,tag,mode in [('HEADLESS-1','resize960',960),('HEADLESS-1','resize800',800),('HEADLESS-2','migrationH2',None),('HEADLESS-1','migrationH1',None)]:
        if mode:
            s.cmd(f'output HEADLESS-1 resolution {mode}x600 position {-mode} 0',True);s.outputs[0]={**s.outputs[0],'logical':[-mode,0,mode,600],'mode':[mode,600]}
        else:s.cmd('workspace 1');s.cmd(f'move workspace to output {out}',True)
        start=time.monotonic_ns();time.sleep(.35);current=s.owner('owner');need(current['owner']['id']==owner_id and current['workspace']['id']==ws_id and current['workspace']['output']==out,'exact migrated identity/output')
        need(current['workspace']['mosaic']['rows'][0]['children']==order,'logical order retained');image=s.capture(tag,out)
        done=re.findall(r'POPUP_[AB] POPUP_DONE',s.log('owner'))
        if done:
            win=current['owner']['window_rect'];rect=[*current['origin'],min(win['width'],420),min(win['height'],320)];output=next(o for o in s.outputs if o['name']==out);point=solid_point(image,COLORS['TOPLEVEL'],output,s.frames[out],rect);tails,buttons=s.click('owner',point);delivery=s.delivery('owner',rect,point,tails,buttons,'TOPLEVEL');live=dict(status='POPUP NOT EXERCISED; TOPLEVEL SAMPLED',reason='legitimate popup_done; no chain recreation',done=done,point=point)
        else:
            fresh=protocol(s.log('owner'));need(fresh['ids']==p['ids'] and fresh['grabs']==p['grabs'],'same live chain')
            prov=Provenance(owner_id,ws_id,'fresh-stage',current['evidence']);geo=geometry(s.log('owner'),current['origin'],prov)
            output=next(o for o in s.outputs if o['name']==out);point=solid_point(image,COLORS['POPUP_B'],output,s.frames[out],geo['B']);tails,buttons=s.click('owner',point);delivery=s.delivery('owner',geo['B'],point,tails,buttons,'POPUP_B')
            root=root_state(s,current,current['origin'],start);live=dict(status='SAMPLED',geometry=geo,point=point,delivery=delivery,root_clip=root)
        if mode is None:
            other=next(o for o in s.outputs if o['name']!=out);vacated=s.capture(tag+'-other',other['name']);need(not any(count(vacated,COLORS[n]) for n in ('POPUP_A','POPUP_B')),'old output popup residual')
        stages.append(dict(tag=tag,state=current,live=live))
    s.save('dynamic-ownership',dict(status='PARTIALLY_FEASIBLE',stages=stages,atomic_generation='NOT PROVEN'))
    s.close_client('owner');final=s.pair_capture('final');exact(baseline,final[1]);return 'PASS'

CAMPAIGN={'scale':popup_campaign,'saved':saved_campaign,'input':input_campaign,'G':lambda s: {'dynamic':dynamic_campaign,'hidden':hidden_campaign,'R90':popup_campaign}[s.spec['case']](s)}
