#!/usr/bin/env python3
"""One optional C3. Preparation and runtime independent reviews are required."""
import argparse,re,time
from diagnostic import *
from cases import init_reference,stable_reference,exact

def campaign(s):
    init_reference(s,2);s.launch_client('owner','saved-client')
    s.cmd(f'[con_id={s.find("owner")["id"]}] focus');state=s.calibrate('owner');baseline=stable_reference(s)
    # Initial applied clip measured using native scene state; no extra PNG.
    applied=[r for r in records(s.log('compositor'),'PI_SCENE') if r['output']=='HEADLESS-1' and r['workspace']==str(state['workspace']['id'])]
    need(applied and applied[-1]['clip_valid']=='1' and applied[-1]['layout']=='5','initial applied Mosaic clip')
    clip=list(map(int,applied[-1]['clip'].split(',')));tile=list(map(int,applied[-1]['tile_scene'].split(',')))
    out=s.outputs[0]['logical'];need([out[0]+tile[0]+clip[0],out[1]+tile[1]+clip[1],*clip[2:]]==out,'initial actual applied output clip')
    s.save('initial-applied',dict(state=state,scene=applied[-1]))
    before=s.log('owner');prior=int(re.findall(r'ACK ns=\d+ serial=(\d+)',before)[-1])
    argv=Path(f'/proc/{s.comp.pid}/cmdline').read_bytes().split(b'\0');need(b'-Dtxn-timeout=2500' in argv,'real2500ms startup')
    source=(s.lab/'diagnostic/mosaic-source/sway/commands/gaps.c').read_text()
    need('argc == 4 && !config->reading' in source and 'arrange_workspace' in source,'runtime current gaps source audit')
    s.client_cmd('owner','hold_next_configure','COMMAND hold_next_configure DONE');cut=len(s.log('owner'));ccut=len(s.log('compositor'))
    s.cmd('workspace 1');request=time.monotonic_ns();s.cmd('gaps inner current set 30',True)
    pending=s.snapshot('saved-requested-pending');s.wait(lambda:'HELD ' in s.log('owner')[cut:])
    proof=pending_geometry(state['snapshot'],pending,state['owner']['id'],state['workspace']['id'],before,s.log('owner')[cut:],prior,request)
    need((time.monotonic_ns()-request)/1e9<2.1,'native held proof before timeout')
    def observed_saved():
        try:return saved_identity(s.log('compositor'),state['owner']['id'],request)
        except ValueError:return None
    native=s.wait(observed_saved,seconds=.5)
    need(all(int(row['ns'])<request+2_450_000_000 for node in native['nodes'] for row in node['samples']),'saved samples before timeout')
    held=s.pair_capture('held');need((time.monotonic_ns()-request)/1e9<2.45,'held pair before timeout');exact(baseline,held[1])
    s.wait(lambda:re.search(r'timed out \(\d*[1-9]\d* waiting\)',s.log('compositor')[ccut:]),seconds=3.5)
    timeout=time.monotonic_ns();need(timeout-request>=2_300_000_000 and s.proc['owner'].poll() is None,'natural timeout clientalive')
    held_configure(before,s.log('owner')[cut:],prior)
    def observed_removal():
        try:return saved_removal(s.log('compositor'),native,time.monotonic_ns())
        except ValueError:return None
    s.wait(observed_removal)
    live_boundary=time.monotonic_ns()
    removal=saved_removal(s.log('compositor'),native,live_boundary)
    s.record('saved-natural-removal',proof=removal,first_live_boundary_ns=live_boundary)
    live=s.owner('owner');need(live['owner']['window_rect']==proof['owner']['window_rect'],'applied requested live dimensions')
    after=s.pair_capture('natural-timeout');exact(baseline,after[1])
    time.sleep(.2);stable=s.pair_capture('stable-live');exact(after[0],stable[0]);exact(after[1],stable[1])
    # Read final passive trace after normal protocol close, never ACK held serial.
    close_request=time.monotonic_ns()
    s.record('saved-explicit-close-boundary',request_ns=close_request)
    s.close_client('owner','close');final=s.pair_capture('final');exact(baseline,final[1])
    identity=saved_identity(s.log('compositor'),state['owner']['id'],request,True)
    removal=saved_removal(s.log('compositor'),identity,min(live_boundary,close_request))
    held_configure(before,s.log('owner')[cut:],prior)
    s.save('saved-diagnostic',dict(status='PARTIALLY_FEASIBLE',request_ns=request,timeout_observed_ns=timeout,first_live_boundary_ns=live_boundary,explicit_close_request_ns=close_request,removal=removal,initial=state,pending=pending,proof=proof,native=identity,pairs=native_pairs(s.log('compositor')),argv=[v.decode() for v in argv],GPU='NOT PROVEN',complete_damage='NOT PROVEN',atomic_generation='NOT PROVEN',timing='passive logging CPU overhead; no neutrality claim'))
    return 'PARTIALLY_FEASIBLE'

def begin(lab,binary):
    need(not sys.flags.optimize,'assertions enabled')
    for p in Path('/proc').iterdir():
        if p.name.isdigit():
            try:exe=(p/'exe').resolve(strict=True)
            except (FileNotFoundError,PermissionError,ProcessLookupError):continue
            need(exe!=binary.resolve(),'diagnostic binary already running')
    folder=lab/'runs'/SPEC['id'];folder.mkdir(exist_ok=True);need(not (folder/'run').exists(),'no retry')
    def consume(state):
        need(set(state['runs'])==set(plans.RUNS)-{SPEC['id']},'all thirteen original tokens consumed first')
        need(SPEC['id'] not in state['runs'] and state['used']['run']==13 and state['campaign_runs']['saved']==2,'known fourteenth token only')
        need(state['used']['capture']+10<=174 and state['campaign_used']['saved']+10<=30,'planned caps')
        state['runs'][SPEC['id']]=dict(campaign='saved',planned=SPEC['limits'],reserved=dict.fromkeys(SPEC['limits'],0),consumed_ns=time.monotonic_ns(),freeze_sha256=gate.sha(lab/'diagnostic/runtime-freeze.json'))
        state['used']['run']+=1;state['campaign_runs']['saved']+=1
    gate.locked(lab,consume)
    ident=gate.read(lab/'identity.json')
    return dict(binary=str(binary),binary_sha256=gate.sha(binary),wlroots=str(plans.WLROOTS),wlroots_sha256=plans.WLROOTS_SHA,pristine_scene=str(plans.SCENE),pristine_scene_sha256=ident['scene_sha256'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--lab',type=Path,required=True);a=p.parse_args();lab=gate.owned(a.lab)
    binary=verify_runtime(lab)
    with registration(lab):
        auth=begin(lab,binary);s=None;status='INCONCLUSIVE';failure=None
        try:
            s=Session(SPEC,auth,lab)
            s.record('diagnostic-private-paths',run=str(s.run),runtime=str(s.runtime),compositor_log=str(s.run/'compositor.log'))
            s.env['SAVED_DIAGNOSTIC']='1';s.start()
            s.record('diagnostic-private-sockets',runtime=str(s.runtime),swaysock=str(s.sock),wayland_display=s.env['WAYLAND_DISPLAY'])
            status=campaign(s)
        except Exception as e:failure=dict(type=type(e).__name__,message=str(e))
        finally:
            if s is not None:status=s.cleanup(status,failure)
            def finish(state):state['runs'][SPEC['id']].update(outcome=status,failure=failure)
            gate.locked(lab,finish)
    print(json.dumps(dict(id=SPEC['id'],status=status,failure=failure)))
    return 1 if failure else 0
if __name__=='__main__':raise SystemExit(main())
