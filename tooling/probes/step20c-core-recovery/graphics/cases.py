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

    s.cmd('workspace 1');s.expected_layout='mosaic' if s.spec['mode']=='mosaic' else 'splith'
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
    aim=s.capture('popup-A-'+str(sum(e['kind']=='spawn' and e['name']=='owner' for e in s.events)),'HEADLESS-1');prov=Provenance(state['owner']['id'],state['workspace']['id'],'bounded-opening-window',state['evidence'])
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
    return 'PASS'

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
    xy=solid_point(images[0],COLORS['POPUP_B'],s.outputs[0],'logical',g['B']);tails,buttons=s.click('owner',xy);s.delivery('owner',g['B'],xy,tails,buttons,'POPUP_B')
    s.save('hidden-return',dict(status='PASS',hidden=hidden,empty_root=root,returned=restored,returned_root=returned_root,ids=p['ids']))
    s.close_client('owner');final=s.pair_capture('final');exact(baseline,final[1]);return 'PASS'

def sample_surviving(s,images,tag):
    if 'POPUP_DONE ' in s.log('owner'):
        s.save(tag+'-input',dict(status='NOT_EXERCISED',reason='legitimate popup dismissal, no new chain reserved'));return
    state=s.owner('owner');prot=validators.grab(s.log('owner'));geo=geometry(s.log('owner'),state['origin'],Provenance(state['owner']['id'],state['workspace']['id'],'NOT OBSERVABLE','mutation paint+pointer'))
    index=next(i for i,o in enumerate(s.outputs) if o['name']==state['workspace']['output'])
    try:point=solid_point(images[index],COLORS['POPUP_B'],s.outputs[index],s.frames[s.outputs[index]['name']],geo['B'])
    except ValueError:
        s.save(tag+'-input',dict(status='NOT_EXERCISED',reason='B has no measured visible interior'));return
    tails,buttons=s.click('owner',point);s.delivery('owner',geo['B'],point,tails,buttons,'POPUP_B');s.save(tag+'-input',dict(status='PASS',point=point,protocol=prot))

def dynamic_campaign(s):
    blank=s.capture('startup-vacated-H1','HEADLESS-1');init_reference(s,2);s.cmd('gaps inner 0');state,baseline,p,g,left,right=open_chain(s)
    owner_id=state['owner']['id'];ws_id=state['workspace']['id'];order=state['workspace'].get('mosaic',{}).get('rows',[{}])[0].get('children')
    s.cmd('output HEADLESS-1 resolution 960x600 position -960 0',True);s.outputs[0]={**s.outputs[0],'logical':[-960,0,960,600],'mode':[960,600]};time.sleep(.35)
    snap=s.snapshot('resized960');sample_surviving(s,s.pair_capture('resized960'),'resized960')
    clamp=dict(status='NOT EXERCISED',reason='standard control has no Mosaic camera')
    if s.spec['mode']=='mosaic':
        ws=workspace(snap['tree'],'1');row=ws['mosaic']['rows'][0];n=len(row['children']);gap=max(0,ws.get('gaps',{}).get('inner',0));cell=max(640,(960-(n-1)*gap)//n);maximum=max(0,n*cell+(n-1)*gap-960)
        request=maximum+960;before=row['scroll_x'];s.scroll('owner',request);settled=s.snapshot('clamped960');actual=workspace(settled['tree'],'1')['mosaic']['rows'][0]['scroll_x']
        need(actual==maximum,'source-derived clamp mismatch');clamp=dict(status='PASS',count=n,gap=gap,minimum_cell_width=640,source='frozen mosaic.c125-152',maximum=maximum,before=before,requested_relative=request,observed=actual)
    s.cmd('output HEADLESS-1 resolution 800x600 position -800 0',True);s.outputs[0]=dict(s.spec['outputs'][0]);time.sleep(.35);s.snapshot('resized-back');sample_surviving(s,s.pair_capture('resized-back'),'resized-back')
    stages=[]
    for out,tag in [('HEADLESS-2','migrated-H2'),('HEADLESS-1','migrated-back-H1')]:
        s.cmd('workspace 1');s.cmd(f'move workspace to output {out}',True);time.sleep(.35);snap=s.snapshot(tag);ws=workspace(snap['tree'],'1');owner=s.find('owner');need(ws['id']==ws_id and ws['output']==out and owner['id']==owner_id,'migrated exact owner/workspace')
        if order is not None:need(ws['mosaic']['rows'][0]['children']==order,'logical row order changed')
        pictures=s.pair_capture(tag);sample_surviving(s,pictures,tag);stages.append(dict(tag=tag,workspace=ws,owner=owner,popup_done=re.findall(r'(POPUP_[AB]) POPUP_DONE',s.log('owner'))))
        if out=='HEADLESS-2':need(not any(count(pictures[0],COLORS[n]) for n in ('POPUP_A','POPUP_B')),'old output retained popup pixels')
    s.save('dynamic-ownership',dict(status='PASS',clamp=clamp,stages=stages,ids_before=p['ids'],ids_after=validators.grab(s.log('owner'))['ids'] if 'POPUP_DONE ' not in s.log('owner') else 'legitimate dismissal recorded',atomic_generation='NOT PROVEN'))
    s.close_client('owner')
    for name in list(s.proc):
        if name.startswith('filler'):s.close_client(name,'close')
    time.sleep(.2);final=s.pair_capture('final');exact(baseline,final[1]);exact(blank,final[0]);return 'PASS'
