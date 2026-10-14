"""EXPERIMENTAL bounded Phase D; reviewed A/G binaries, fresh ledger only."""
import re,time
from input_validators import applied_states,wire_delivery,correlate,standard_return,require
from runtime import cases,engine
init_reference=cases.init_reference
stable_reference=cases.stable_reference
solid_point=engine.solid_point
exact=engine.exact
COLORS={"TOPLEVEL":(35,68,204)}

PROTOCOL=dict(captures=10,clicks=6,grabs=0,camera=2,moves=16,mutations=20,
              seconds_max=150,stop='missing/wrong wire identity, outside clip, budget, compositor/client error')

def measured_click(s,tag,point=None,expect_empty=False):
    # WHY: preserve asynchronous focus/camera mutation instead of sleeping it away.
    # CONTRACT: no wait inserted between selected point and actual injection.
    # INVARIANT: pre/post IPC is labelled sampled; only native PI is applied.
    s.inject('move',[-790,590])
    before=s.owner('owner');owner=before['owner'];ws=before['workspace']
    image=s.capture(tag,'HEADLESS-1')
    if point is None:
        point=solid_point(image,COLORS['TOPLEVEL'],s.outputs[0],s.frames['HEADLESS-1'],
                          [*before['origin'],owner['window_rect']['width'],owner['window_rect']['height']])
    pre=s.snapshot(tag+'-pre');cut=len(s.log('owner'));begin=time.monotonic_ns()
    tails,buttons=s.click('owner',point)
    if not expect_empty:
        s.wait(lambda: bool(re.search(r'POINTER_BUTTON .*state=0',s.log('owner')[cut:])))
        tails['owner']=s.log('owner')[cut:]
    post=s.snapshot(tag+'-post');end=time.monotonic_ns()
    require(any(n['id']==owner['id'] for n in engine.nodes(post['tree'])), 'owner destroyed during delivery')
    states=applied_states(s.log('compositor'),owner['id'],ws['output'],ws['id'],
        [owner['window_rect']['x'],owner['deco_rect']['height']+owner['window_rect']['y']],s.outputs[0]['logical'])
    receipt=dict(tag=tag,owner=owner['id'],output=ws['output'],workspace=ws['id'],
        point=point,interval=[begin,end],pre=pre,post=post,states=states,
        tails=tails,buttons=buttons,compositor_trace=s.log('compositor'),client_cut=cut)
    if expect_empty:
        require(not buttons.get('owner') and '.button(' not in tails['owner'], 'empty region delivered owner button')
        receipt['status']='PARTIALLY_FEASIBLE';receipt['meaning']='no owner wire button in bounded injection interval'
    else:
        d=wire_delivery(tails['owner']);surfaces=re.findall(r'get_xdg_surface\(new id xdg_surface#\d+, wl_surface#(\d+)\)',s.log('owner'))
        require(len(surfaces)==1,'one real owner XDG surface')
        receipt.update(delivery=d,surface=int(surfaces[0]),
            other_buttons={n:v for n,v in buttons.items() if n!='owner' and v})
        receipt['correlation']=correlate(receipt)
    s.save(tag+'-event-time',receipt)
    return point,receipt

def run(s):
    init_reference(s);s.launch_client('owner','region-client','both_cross')
    s.cmd(f'[con_id={s.find("owner")["id"]}] focus');s.calibrate('owner');baseline=stable_reference(s)
    point,full=measured_click(s,'input-full')
    s.client_cmd('owner','region_empty_top','COMMAND region_empty_top DONE')
    _,empty=measured_click(s,'input-empty',point,True)
    s.client_cmd('owner','region_full_top','COMMAND region_full_top DONE')
    _,restored=measured_click(s,'input-full-restored')
    s.cmd(f'[con_id={s.find("filler0")["id"]}] focus',True)
    s.cmd(f'[con_id={s.find("owner")["id"]}] focus',True)
    _,focus=measured_click(s,'input-focus-return')
    s.scroll('owner',20);_,camera=measured_click(s,'input-camera')
    cut=time.monotonic_ns();s.cmd(f'[con_id={s.find("owner")["id"]}] layout splith',True)
    _,standard=measured_click(s,'input-standard')
    standard_states=[r for r in standard['states'] if r['ns']>=standard['pre']['ns']]
    standard_verdict=standard_return(standard_states,standard['owner'],standard['output'],standard['workspace'])
    s.close_client('owner');log=s.log('owner')
    require(not re.search(r'wl_display[^\n]*\.error\(|protocol error|error=[1-9]',log,re.I),'normal close Wayland error')
    final=s.capture('final-H2','HEADLESS-2');exact(baseline,final)
    values=[r['correlation']['status'] for r in (full,restored,focus,camera,standard)]
    status='INCONCLUSIVE' if 'INCONCLUSIVE' in values else 'PARTIALLY_FEASIBLE'
    s.save('input-verdict',dict(INPUT_EVENT_TIME_CORRELATION=status,
        INPUT_STANDARD_RETURN=standard_verdict,INPUT_ATOMIC_GENERATION='NOT_PROVEN',
        final_H2_exact=True,normal_owner_close=True,wayland_error=0,protocol=PROTOCOL))
    return status
