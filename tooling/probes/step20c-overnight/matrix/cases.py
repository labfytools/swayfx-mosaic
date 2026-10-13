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
    need(s.spec['id']=='D3-mosaic' and 'owner' not in s.proc,'prospective pre-owner marker baseline')
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
    if s.spec['id']=='D3-mosaic':marker_host_baseline(s)
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
    if s.spec['mode']=='mosaic':exact(baseline,right);root=root_state(s,state,state['origin'],window)
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

def dynamic_campaign(s):
    blank=s.capture('startup-vacated-H1','HEADLESS-1');init_reference(s,2);s.cmd('gaps inner 0');state,baseline,p,g,left,right=open_chain(s)
    owner_id=state['owner']['id'];ws_id=state['workspace']['id'];order=state['workspace'].get('mosaic',{}).get('rows',[{}])[0].get('children')
    s.cmd('output HEADLESS-1 resolution 960x600 position -960 0',True);s.outputs[0]={**s.outputs[0],'logical':[-960,0,960,600],'mode':[960,600]};time.sleep(.35)
    snap=s.snapshot('resized960');s.pair_capture('resized960')
    clamp=dict(status='NOT EXERCISED',reason='standard control has no Mosaic camera')
    if s.spec['mode']=='mosaic':
        ws=workspace(snap['tree'],'1');row=ws['mosaic']['rows'][0];n=len(row['children']);gap=max(0,ws.get('gaps',{}).get('inner',0));cell=max(640,(960-(n-1)*gap)//n);maximum=max(0,n*cell+(n-1)*gap-960)
        request=maximum+960;before=row['scroll_x'];s.scroll('owner',request);settled=s.snapshot('clamped960');actual=workspace(settled['tree'],'1')['mosaic']['rows'][0]['scroll_x']
        need(actual==maximum,'source-derived clamp mismatch');clamp=dict(status='PASS',count=n,gap=gap,minimum_cell_width=640,source='frozen mosaic.c125-152',maximum=maximum,before=before,requested_relative=request,observed=actual)
    s.cmd('output HEADLESS-1 resolution 800x600 position -800 0',True);s.outputs[0]=dict(s.spec['outputs'][0]);time.sleep(.35);s.snapshot('resized-back');s.pair_capture('resized-back')
    stages=[]
    for out,tag in [('HEADLESS-2','migrated-H2'),('HEADLESS-1','migrated-back-H1')]:
        s.cmd('workspace 1');s.cmd(f'move workspace to output {out}',True);time.sleep(.35);snap=s.snapshot(tag);ws=workspace(snap['tree'],'1');owner=s.find('owner');need(ws['id']==ws_id and ws['output']==out and owner['id']==owner_id,'migrated exact owner/workspace')
        if order is not None:need(ws['mosaic']['rows'][0]['children']==order,'logical row order changed')
        pictures=s.pair_capture(tag);stages.append(dict(tag=tag,workspace=ws,owner=owner,popup_done=re.findall(r'(POPUP_[AB]) POPUP_DONE',s.log('owner'))))
        if out=='HEADLESS-2':need(not any(count(pictures[0],COLORS[n]) for n in ('POPUP_A','POPUP_B')),'old output retained popup pixels')
    s.save('dynamic-ownership',dict(status='PASS',clamp=clamp,stages=stages,ids_before=p['ids'],ids_after=protocol(s.log('owner'))['ids'] if 'POPUP_DONE ' not in s.log('owner') else 'legitimate dismissal recorded',atomic_generation='NOT PROVEN'))
    s.close_client('owner')
    for name in list(s.proc):
        if name.startswith('filler'):s.close_client(name,'close')
    time.sleep(.2);final=s.pair_capture('final');exact(baseline,final[1]);exact(blank,final[0]);return 'PASS'

def saved_campaign(s):
    init_reference(s,2);s.launch_client('owner','saved-client');s.cmd(f'[con_id={s.find("owner")["id"]}] focus');state=s.calibrate('owner');baseline=stable_reference(s)
    s.client_cmd('owner','hold_next_configure','COMMAND hold_next_configure DONE');cut=len(s.log('owner'));cut_comp=len(s.log('compositor'));request=time.monotonic_ns();s.cmd('gaps inner 30',True)
    s.wait(lambda:'HELD ' in s.log('owner')[cut:]);held=s.log('owner')[cut:];m=re.search(r'HELD ns=(\d+) serial=(\d+)',held);need(m is not None,'real held configure serial')
    held_serial=int(m[2]);need(re.search(rf'xdg_surface#\d+\.configure\({held_serial}\)',held) is not None,'held actual wire configure');need(f'ack_configure({held_serial})' not in held,'held serial was ACKed')
    held_images=s.pair_capture('held');held_capture_observation='NOT EXERCISED: native saved identity absent; capture may follow natural200ms timeout'
    s.wait(lambda:'timed out (' in s.log('compositor')[cut_comp:],seconds=3);need(s.proc['owner'].poll() is None,'held client alive')
    after=s.pair_capture('natural-timeout');exact(baseline,after[1]);s.save('saved-observability',dict(status='INCONCLUSIVE',request_ns=request,held_wire=held,natural_timeout=[l for l in s.log('compositor')[cut_comp:].splitlines() if 'timed out (' in l],default_timeout_ms=200,held_serial=held_serial,
        saved_node_identity='NOT OBSERVABLE',saved_render_identity='NOT PROVEN',held_capture_observation=held_capture_observation,meaning='source-backed saved path and held configure; sampled SHM/pixels do not identify a saved scene node',ping_causality='wire responses recorded if natural ping occurs; no forced ping'))
    s.close_client('owner','close');final=s.pair_capture('final');exact(baseline,final[1]);return 'INCONCLUSIVE'

def interior_roi(s,name):
    owner=s.find(name)
    if s.spec['mode']=='mosaic' and not owner.get('floating','auto_off').endswith('on'):
        origin,scene,raw=actual_origin(owner,s.log('compositor'))
    else:origin=assigned_origin(owner)
    win=owner['window_rect'];r=intersection([*origin,win['width'],win['height']],s.outputs[0]['logical'])
    need(r[2]>=80 and r[3]>=80,'effect central ROI not visible')
    center=[r[0]+r[2]//2,r[1]+r[3]//2];p=global_png(center,s.outputs[0],s.frames['HEADLESS-1'])
    return [p[0]-32,p[1]-32,p[0]+32,p[1]+32]

def adjacent_metric(image,roi):
    im=image.crop(roi);total=0
    for y in range(im.height):
        for x in range(im.width-1):total+=sum(abs(a-b) for a,b in zip(im.getpixel((x,y)),im.getpixel((x+1,y))))
    return total/(im.height*(im.width-1)*3)

def effects_campaign(s):
    init_reference(s,1);baseline=stable_reference(s);s.launch_client('glass','fx-clients','glass');s.cmd(f'[con_id={s.find("glass")["id"]}] focus');s.calibrate('glass')
    bg=s.spawn('background',[LAB/'matrix/clients/fx-clients','background'],True);s.wait(lambda:'BACKGROUND_CONFIGURED' in s.log('background'));s.client_cmd('background','A','COMMAND A DONE');time.sleep(.2)
    s.cmd('gaps inner 24');s.cmd('blur_xray disable');s.cmd('blur_radius 5');s.cmd('blur_passes 3');s.cmd('blur_noise 0');s.cmd('blur_brightness 1');s.cmd('blur_contrast 1');s.cmd('blur_saturation 1')
    off=s.pair_capture('FX-off');gid=s.find('glass')['id']
    s.cmd('shadow_offset 20 0');s.cmd('shadow_blur_radius 16');s.cmd('shadow_color #000000A0');s.cmd(f'[con_id={gid}] shadows enable',True);time.sleep(.25);shadow=s.pair_capture('shadow-on')
    shadow_exercised=ImageChops.difference(off[0],shadow[0]).getbbox() is not None
    s.cmd(f'[con_id={gid}] shadows disable',True)
    # Native source selects classic for a floating owner, optimized for settled
    # tiled owners. Keep this classic glass wholly inside H1, then retile.
    s.cmd(f'[con_id={gid}] floating enable',True);s.cmd(f'[con_id={gid}] resize set width 300 px height 200 px');s.cmd(f'[con_id={gid}] move absolute position -650 200');time.sleep(.25)
    classic_off=s.pair_capture('classic-off');classic_roi=interior_roi(s,'glass');s.cmd(f'[con_id={gid}] blur enable',True);time.sleep(.25);classic=s.pair_capture('classic-blur')
    classic_adjacent_off=adjacent_metric(classic_off[0],classic_roi);classic_adjacent_on=adjacent_metric(classic[0],classic_roi)
    classic_exercised=classic_off[0].crop(classic_roi).tobytes()!=classic[0].crop(classic_roi).tobytes() and classic_adjacent_on<classic_adjacent_off
    floating=s.find('glass');need(floating['rect']['x']>=-800 and floating['rect']['x']+floating['rect']['width']<=0,'classic floating ROI wholly H1')
    s.cmd(f'[con_id={gid}] floating disable',True);time.sleep(.25);s.calibrate('glass')
    # A real background layer below blur_tree drives the native optimized path;
    # no shader/cache call is made by the runner.
    s.cmd(f'[con_id={gid}] blur disable',True);s.cmd(f'[con_id={gid}] blur enable',True);time.sleep(.25);optA=s.pair_capture('optimized-A');optimized_roi=interior_roi(s,'glass')
    s.client_cmd('background','B','COMMAND B DONE');time.sleep(.25);optB=s.pair_capture('optimized-B')
    s.client_cmd('background','A','COMMAND A DONE');time.sleep(.25);optA2=s.pair_capture('optimized-A-return')
    need(optA[0].crop(optimized_roi).tobytes()!=optB[0].crop(optimized_roi).tobytes(),'fresh central glass A-B RGB difference');exact(optA[0],optA2[0])
    if s.spec['mode']=='mosaic':
        for imgs in (off,shadow,classic_off,classic,optA,optB,optA2):exact(baseline,imgs[1])
        log=s.log('compositor');native_optimized='OPT_REGEN_RESULT' in log and 'OPT_BLUR_USE' in log and any('optimized=1' in l and 'chosen=(nil)' not in l for l in log.splitlines() if 'OPT_BLUR_USE' in l)
    else:native_optimized='NOT OBSERVABLE on pristine'
    s.save('effects-evidence',dict(status='PARTIALLY_FEASIBLE',standard_shadow_spill='EXERCISED' if s.spec['mode']=='pristine' and ImageChops.difference(off[1],shadow[1]).getbbox() else 'NOT EXERCISED',shadow_actual_RGB='EXERCISED' if shadow_exercised else 'NOT EXERCISED',classic_blur_actual_RGB='EXERCISED' if classic_exercised else 'NOT EXERCISED',native_optimized=native_optimized,classic_filtering=dict(roi=classic_roi,adjacent_off=classic_adjacent_off,adjacent_on=classic_adjacent_on),optimized_center_roi=optimized_roi,A_B_A_actual=True,
        classic_vs_optimized_identity='source-selected classic floating wholly H1 versus settled tiled optimized; native chosen/cache observations retained, no whole-cache equivalence claim; Mosaic-tiled classic clipping NOT TESTED',edges='recorded full PNG; historical max6 not presumed',complete_damage='NOT PROVEN'))
    s.close_client('glass','close');s.close_client('background','close');time.sleep(.2);final=s.pair_capture('final');exact(baseline,final[1]);return 'PARTIALLY_FEASIBLE'

def parse_pairs(text,limit=12):
    commits=[];presents={}
    for line in text.splitlines():
        if 'PI_OUTPUT_COMMIT ' in line or 'PI_OUTPUT_PRESENT ' in line:
            fields=dict(re.findall(r'(\w+)=([^\s]+)',line));need(all(k in fields for k in ('output','commit_seq','ns')),'native pair format');key=(fields['output'],int(fields['commit_seq']))
            if 'PI_OUTPUT_COMMIT ' in line:commits.append((key,fields,line))
            else:need(key not in presents,'duplicate native present');presents[key]=(fields,line)
    rows=[]
    for key,fields,raw in commits[:limit]:
        pr=presents.get(key);rows.append(dict(output=key[0],seq=key[1],commit=raw,present=pr[1] if pr else None,status='PAIRED' if pr else 'MISSING_PRESENT'))
    return dict(analyzed=rows,limit=limit,total_commits=len(commits),unselected_retained_raw=True,buffer_identity='NOT PROVEN')

def ordering_campaign(s):
    init_reference(s);s.launch_client('owner','region-client',s.spec['placement']);s.cmd(f'[con_id={s.find("owner")["id"]}] focus');state=s.calibrate('owner');baseline=stable_reference(s)
    im=s.capture('input-full-before','HEADLESS-1');rect=[*state['origin'],state['owner']['window_rect']['width'],state['owner']['window_rect']['height']];xy=solid_point(im,COLORS['TOPLEVEL'],s.outputs[0],'logical',rect)
    tails,buttons=s.click('owner',xy);s.delivery('owner',rect,xy,tails,buttons,'TOPLEVEL')
    s.client_cmd('owner','region_empty_top','COMMAND region_empty_top DONE');tails,buttons=s.click('owner',xy);need(not buttons['owner'],'empty input region delivered owner button');s.capture('region-empty','HEADLESS-1')
    s.client_cmd('owner','region_full_top','COMMAND region_full_top DONE');tails,buttons=s.click('owner',xy);s.delivery('owner',rect,xy,tails,buttons,'TOPLEVEL')
    s.cmd(f'[con_id={s.find("filler0")["id"]}] focus',True);s.cmd(f'[con_id={s.find("owner")["id"]}] focus',True)
    s.cmd('gaps inner 30',True);s.cmd('gaps inner 0',True);time.sleep(.25);s.capture('resize-settled','HEADLESS-1')
    if s.spec['mode']=='mosaic':
        s.scroll('owner',20);s.scroll('owner',-20);s.cmd(f'[con_id={s.find("owner")["id"]}] layout splith',True);s.cmd(f'[con_id={s.find("owner")["id"]}] layout mosaic',True)
    s.capture('layout-settled','HEADLESS-1');s.close_client('owner');final=s.pair_capture('final');exact(baseline,final[1])
    pairs=parse_pairs(s.log('compositor'));s.save('ordering',dict(status='INCONCLUSIVE',pairs=pairs,
       native_atomic_epoch='NOT PROVEN',native_hit_path='NOT OBSERVABLE',buffer_reference_release='NOT PROVEN',natural_commit_mutation_present='NOT EXERCISED unless independent timestamp analysis finds a real window',
       damage=[l for l in s.log('compositor').splitlines() if 'TEMPORAL_DAMAGE' in l],client_input='actual wire/button/region commits retained separately'))
    return 'INCONCLUSIVE'

CAMPAIGN={'D1':popup_campaign,'D2':popup_campaign,'D3':popup_campaign,'D4':dynamic_campaign,'E1':hidden_campaign,'E2':saved_campaign,'E3':effects_campaign,'F':ordering_campaign}
