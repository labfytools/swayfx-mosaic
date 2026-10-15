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
    s.inject('move',[s.outputs[0]['logical'][0]+10,s.outputs[0]['logical'][1]+10]);time.sleep(.15)
    a=s.capture('H2-reference1','HEADLESS-2');time.sleep(.6);b=s.capture('H2-reference2','HEADLESS-2');exact(a,b)
    need(all(v==(48,48,56) for v in a.get_flattened_data()),'static uniform H2');s.save('reference-stability',dict(status='PASS',exact=exact(a,b)));return a

def root_state(s,state,origin,window_start,expect_hidden=False,previous=None,expected_tree=None):
    # WHY/CONTRACT/INVARIANT: no PI/native scene identity exists in CORE.
    # Pixel/input evidence qualifies sampled clipping only, never generation.
    return dict(status='NOT OBSERVABLE',native_tree_identity='NOT OBSERVABLE',
                applied_generation='NOT OBSERVABLE',owner_id=state['owner']['id'],
                workspace_id=state['workspace']['id'],window=[window_start,time.monotonic_ns()])

def open_chain(s,tail_fillers=0):

    s.cmd('workspace 1');s.cmd('layout mosaic' if s.spec['mode']=='mosaic' else 'layout splith');s.expected_layout='mosaic' if s.spec['mode']=='mosaic' else 'splith'
    pre=s.snapshot('before-chain-'+str(sum(e['kind']=='spawn' and e['name']=='owner' for e in s.events)))
    validators.selected_workspace(pre,'1','HEADLESS-1',s.expected_layout)
    s.debit('chain');s.launch_client('owner',s.spec['client'],s.spec['placement'])
    s.owner('owner') # Reject wrong map before any click; never move mapped popup chains.
    for i in range(tail_fillers):s.launch_client('tail'+str(i),'static-reference')
    s.cmd(f'[con_id={s.find("owner")["id"]}] focus');state=s.calibrate('owner');baseline=s.reference if hasattr(s,'reference') else stable_reference(s);s.reference=baseline
    im=s.capture('owner-top-'+str(sum(e['kind']=='spawn' and e['name']=='owner' for e in s.events)),'HEADLESS-1');rect=[*state['origin'],state['owner']['window_rect']['width'],state['owner']['window_rect']['height']]
    xy=solid_point(im,COLORS['TOPLEVEL'],s.outputs[0],s.frames['HEADLESS-1'],rect)
    need(contains([*state['origin'],420,575 if s.spec['axis']==1 else 320],xy),'opening native bounds')
    ta,ba=s.click('owner',xy,'left',True);s.wait(lambda:'POPUP_A MAP ' in s.log('owner'));time.sleep(.2)
    aim=s.capture('popup-A-'+str(sum(e['kind']=='spawn' and e['name']=='owner' for e in s.events)),'HEADLESS-1');prov=Provenance(state['owner']['id'],state['workspace']['id'],'NOT OBSERVABLE',state['evidence'])
    xyA=solid_point(aim,COLORS['POPUP_A'],s.outputs[0],s.frames['HEADLESS-1'])
    tb,bb=s.click('owner',xyA,'left',True);s.wait(lambda:'POPUP_B MAP ' in s.log('owner'));time.sleep(.2)
    window=time.monotonic_ns();time.sleep(.15);p=validators.grab(s.log('owner'));g=geometry(s.log('owner'),state['origin'],prov)
    s.delivery('owner',rect,xy,ta,ba,'TOPLEVEL',p['grabs'][0]['serial']);s.delivery('owner',g['A'],xyA,tb,bb,'POPUP_A',p['grabs'][1]['serial'])
    [validators.crosses(g[k],s.spec['axis'],s.spec['boundary']) for k in ('A','B')]
    left,right=s.pair_capture('mapped-'+str(sum(e['kind']=='spawn' and e['name']=='owner' for e in s.events)))
    for name in ('POPUP_A','POPUP_B'):
        need(count(left,COLORS[name])>0,'permitted popup pixels missing')
        if s.spec['mode']=='pristine':need(count(right,COLORS[name])>0,'standard popup continuation missing')
    if s.spec['mode']=='mosaic':validators.rgb(baseline,right);root=root_state(s,state,state['origin'],window)
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
    return 'PARTIALLY_FEASIBLE'

def hidden_campaign(s):
    init_reference(s,2);state,baseline,p,g,left,right=open_chain(s,2)
    xy=solid_point(left,COLORS['POPUP_B'],s.outputs[0],'logical',g['B']);tails,buttons=s.click('owner',xy);s.delivery('owner',g['B'],xy,tails,buttons,'POPUP_B')
    delta=state['scene'][0]+state['scene'][2]-s.outputs[0]['logical'][0]+16;start=time.monotonic_ns();s.scroll('owner',delta);hidden=s.owner('owner')
    need(intersection(hidden['scene'],s.outputs[0]['logical'])[2]==0,'owner not completely hidden')
    images=s.pair_capture('fully-hidden');need(not any(count(im,COLORS[n]) for im in images for n in ('POPUP_A','POPUP_B')),'hidden popup residual');exact(baseline,images[1])
    root=root_state(s,hidden,hidden['origin'],start,True,previous=state);cut=len(s.log('owner'));s.inject('move',[-790,590]);need('target=POPUP_A ' not in s.log('owner')[cut:] and 'target=POPUP_B ' not in s.log('owner')[cut:],'hidden popup pointer enter')
    validators.hidden_survival(s.log('owner'),p,[])
    return_start=time.monotonic_ns();s.scroll('owner',-delta);restored=s.owner('owner');need(restored['origin']==state['origin'],'same owner origin restored')
    images=s.pair_capture('returned');validators.hidden_survival(s.log('owner'),p,[e for e in s.events if e['kind']=='injection' and start<=e['ns']<=return_start]);exact(baseline,images[1]);returned_root=root_state(s,restored,restored['origin'],return_start,previous=hidden,expected_tree=root.get('tree'));fresh=validators.grab(s.log('owner'));need(fresh['ids']==p['ids'] and fresh['grabs']==p['grabs'],'unchanged live chain')
    g=geometry(s.log('owner'),restored['origin'],Provenance(restored['owner']['id'],restored['workspace']['id'],'NOT OBSERVABLE','fresh return geometry'));xy=solid_point(images[0],COLORS['POPUP_B'],s.outputs[0],'logical',g['B']);tails,buttons=s.click('owner',xy);s.delivery('owner',g['B'],xy,tails,buttons,'POPUP_B')
    s.save('hidden-return',dict(status='PASS',hidden=hidden,empty_root=root,returned=restored,returned_root=returned_root,ids=p['ids']))
    s.close_client('owner');final=s.pair_capture('final');exact(baseline,final[1]);return 'PARTIALLY_FEASIBLE'

def sample_surviving(s,images,tag):
    if 'POPUP_DONE ' in s.log('owner'):
        s.save(tag+'-input',dict(status='NOT_EXERCISED',reason='legitimate popup dismissal, no new chain reserved'));return
    state=s.owner('owner');prot=validators.grab(s.log('owner'));geo=geometry(s.log('owner'),state['origin'],Provenance(state['owner']['id'],state['workspace']['id'],'NOT OBSERVABLE','mutation paint+pointer'))
    index=next(i for i,o in enumerate(s.outputs) if o['name']==state['workspace']['output'])
    try:point=solid_point(images[index],COLORS['POPUP_B'],s.outputs[index],s.frames[s.outputs[index]['name']],geo['B'])
    except ValueError:
        s.save(tag+'-input',dict(status='NOT_EXERCISED',reason='B has no measured visible interior'));return
    tails,buttons=s.click('owner',point);s.delivery('owner',geo['B'],point,tails,buttons,'POPUP_B');s.save(tag+'-input',dict(status='PASS',point=point,protocol=prot))

def dynamic_geometry(snap,previous=None):
    # WHY: scroll IPC alone does not demonstrate the resize clamp.
    # CONTRACT: pinned arrange.c105-131 / mosaic.c125-153, zero inner gap,
    # three direct tiled children; calloc row state has no minimum-width setter
    # and uses640. Corroborate that minimum with every actual IPC child width.
    # INVARIANT: this is a pending IPC candidate, never native applied geometry.
    ws=workspace(snap['tree'],'1');row=ws['mosaic']['rows'][0]
    children=ws['nodes'];ids=[c['id'] for c in children]
    need(len(children)==3 and row['children']==ids,'dynamic direct row reconstruction')
    viewport=[ws['rect'][k] for k in ('x','y','width','height')]
    width=viewport[2];need(0<width<3*640,'dynamic minimum not distinguishable from fitting')
    need(all(c['rect']['width']==640 for c in children),'actual minimum-width reconstruction')
    need([c['rect']['x'] for c in children]==[viewport[0]+i*640 for i in range(3)],'actual zero-gap row reconstruction')
    maximum=3*640-width;scroll=row['scroll_x'];need(0<=scroll<=maximum,'dynamic camera outside clamp')
    result=dict(workspace_id=ws['id'],output=ws['output'],children=ids,viewport=viewport,
                minimum_width=640,content_width=1920,max_scroll=maximum,scroll=scroll,
                geometry_status='IPC_PENDING_CANDIDATE; native generation NOT OBSERVABLE')
    if previous is not None:
        need(ws['id']==previous['workspace_id'] and ids==previous['children'],'dynamic workspace/order changed')
        expected=min(previous['scroll'],maximum)
        need(scroll==expected,'reconstructed camera clamp mismatch')
        result.update(expected_scroll=expected,clamp='PASS')
    return result

def dynamic_pixels(images,outputs,frames,viewport,reference=None):
    # WHY/CONTRACT: each mutation must reject old-output and outside-clip paint.
    # INVARIANT: sampled RGB exclusion cannot prove complete native damage.
    for image,out in zip(images,outputs):
        for y in range(image.height):
            for x in range(image.width):
                if image.getpixel((x,y)) in (COLORS['POPUP_A'],COLORS['POPUP_B']):
                    need(contains(viewport,png_global((x,y),out,frames[out['name']])),'dynamic popup pixel outside current viewport')
    if reference is not None:exact(reference,images[1])
    return dict(exclusion='PASS',whole_H2='PASS' if reference is not None else 'NOT_APPLICABLE: current owner workspace on H2',complete_damage='NOT OBSERVABLE')

def dynamic_campaign(s):
    init_reference(s,2);s.cmd('gaps inner 0');state,baseline,p,g,left,right=open_chain(s)
    owner_id=state['owner']['id'];previous=dynamic_geometry(state['snapshot']);stages=[]
    mutations=[('output HEADLESS-1 resolution 960x600 position -960 0','resized960','HEADLESS-1'),
               ('output HEADLESS-1 resolution 800x600 position -800 0','resized-back','HEADLESS-1'),
               ('move workspace to output HEADLESS-2','migrated-H2','HEADLESS-2'),
               ('move workspace to output HEADLESS-1','migrated-back-H1','HEADLESS-1')]
    for command,tag,out in mutations:
        s.cmd('workspace 1');s.cmd(command,True);s.expected_output=out
        if tag=='resized960':s.outputs[0]={**s.outputs[0],'logical':[-960,0,960,600],'mode':[960,600]}
        elif tag=='resized-back':s.outputs[0]=dict(s.spec['outputs'][0])
        time.sleep(.35);snap=s.snapshot(tag);current=dynamic_geometry(snap,previous)
        need(current['output']==out and s.find('owner')['id']==owner_id,'dynamic exact owner/output')
        expected_viewport=next(o['logical'] for o in s.outputs if o['name']==out)
        need(current['viewport']==expected_viewport,'dynamic viewport/output reconstruction')
        pictures=s.pair_capture(tag)
        pixels=dynamic_pixels(pictures,s.outputs,s.frames,current['viewport'],baseline if out=='HEADLESS-1' else None)
        # An alive chain must supply fresh paint and local pointer input; an
        # actual XDG dismissal is recorded without injecting on destroyed popups.
        if 'POPUP_DONE ' not in s.log('owner'):
            fresh=s.owner('owner');geo=geometry(s.log('owner'),fresh['origin'],Provenance(owner_id,current['workspace_id'],'NOT OBSERVABLE','fresh mutation IPC + paint + pointer'))
            index=next(i for i,o in enumerate(s.outputs) if o['name']==out)
            point=solid_point(pictures[index],COLORS['POPUP_B'],s.outputs[index],s.frames[out],geo['B'])
            tails,buttons=s.click('owner',point);s.delivery('owner',geo['B'],point,tails,buttons,'POPUP_B')
            need(validators.grab(s.log('owner'))['ids']==p['ids'],'dynamic popup IDs changed')
            input_proof=dict(status='PASS',point=point)
        else:input_proof=dict(status='NOT_EXERCISED',reason='XDG dismissal; no injection on destroyed popup')
        stages.append(dict(tag=tag,geometry=current,pixels=pixels,input=input_proof));previous=current
    s.save('dynamic-ownership',dict(status='PASS',stages=stages,ids_before=p['ids'],atomic_generation='NOT PROVEN',complete_damage='NOT OBSERVABLE'))
    s.close_client('owner')
    for name in list(s.proc):
        if name.startswith('filler'):s.close_client(name,'close')
    s.save('dynamic-final-limit',dict(status='NOT_TESTED',reason='14 capture cap used by opening and four fresh mutation states; no post-close capture'));return 'PARTIALLY_FEASIBLE'
