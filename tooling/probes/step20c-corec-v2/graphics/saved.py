"""One actual held→natural-timeout episode, exact binary, EXPERIMENTAL."""
import re,time
from pathlib import Path
import cases,engine
from geometry import need
from saved_validators import pending_geometry,held_configure,saved_identity,natural_retirement,rgb_exact,timeout_line,released_configure

def run(s):
    cases.init_reference(s,2);s.launch_client('owner','saved-client');s.cmd(f'[con_id={s.find("owner")["id"]}] focus');state=s.calibrate('owner');baseline=cases.stable_reference(s)
    initial=s.snapshot('initial-applied');before=s.log('owner');acks=re.findall(r'ACK ns=\d+ serial=(\d+)',before);need(acks,'initial actual ACK');prior=int(acks[-1])
    argv=Path(f'/proc/{s.comp.pid}/cmdline').read_bytes().split(b'\0');need(b'-Dtxn-timeout=5000' in argv,'actual startup timeout5000')
    s.client_cmd('owner','hold_next_configure','COMMAND hold_next_configure DONE');cut=len(s.log('owner'));ccut=len(s.log('compositor'));s.cmd('workspace 1');request=time.monotonic_ns();s.cmd('gaps inner current set 30',True)
    pending=s.snapshot('saved-requested-pending');s.wait(lambda:'HELD ' in s.log('owner')[cut:]);proof=pending_geometry(initial,pending,state['owner']['id'],state['workspace']['id'],before,s.log('owner')[cut:],prior,request)
    held_start=time.monotonic_ns();held=s.pair_capture('held');held_end=time.monotonic_ns();need(held_start>proof['held']['ns'] and held_end<request+4_700_000_000,'held capture before expiration')
    commits=re.findall(r'COMMIT ns=\d+ serial=\d+ size=\d+x\d+ color=([0-9a-f]+)',before);need(commits,'actual retained SHM color');value=int(commits[-1],16);color=((value>>16)&255,(value>>8)&255,value&255)
    rgb_exact(baseline,held[1]);need(any(p==color for p in held[0].getdata()),'owner retained SHM color visible H1')
    native=None
    if False:native=saved_identity(s.log('compositor'),state['owner']['id'],request)
    s.wait(lambda:re.search(r'Transaction .*timed out \(\d*[1-9]\d* waiting\)',s.log('compositor')[ccut:]),seconds=6)
    observed=time.monotonic_ns();need(s.proc['owner'].poll() is None,'owner alive natural timeout');hold=held_configure(before,s.log('owner')[cut:],prior)
    timeout=timeout_line(s.log('compositor')[ccut:],-1,True,request,observed,2**63)
    after_start=time.monotonic_ns();after=s.pair_capture('natural-timeout');rgb_exact(baseline,after[1]);release=time.monotonic_ns();s.client_cmd('owner','release_configure','COMMAND release_configure DONE');s.wait(lambda:re.search(r'ACK ns=\d+ serial='+str(proof['held']['serial'])+r'\b',s.log('owner')[cut:]));live=s.pair_capture('restored-live');rgb_exact(baseline,live[1])
    if native:
        native=saved_identity(s.log('compositor'),state['owner']['id'],request,True)
        retirement=natural_retirement(s.log('compositor'),native,after_start,time.monotonic_ns(),True,before,s.log('owner')[cut:],prior)
    else:retirement={'status':'NOT OBSERVABLE; CORE has no native saved identity'}
    # WHY CONTRACT INVARIANT: CPU destruction is measured separately from GPU
    # completion, and process exit0 alone never qualifies Wayland cleanup.
    s.save('saved-evidence',dict(request_ns=request,held_start_ns=held_start,held_end_ns=held_end,timeout_observed_ns=observed,timeout_native=timeout,geometry=proof,native=native,retirement=retirement,held_wire=hold,post_release=released_configure(hold,s.log('owner')[cut:],release,observed,s.proc['owner'].poll() is None),gpu_completion='NOT PROVEN',native_generation='NOT PROVEN',binary=s.auth))
    s.close_client('owner','close');final=s.pair_capture('final');rgb_exact(baseline,final[1]);return 'PARTIALLY_FEASIBLE'
