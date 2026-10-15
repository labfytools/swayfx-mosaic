#!/usr/bin/env python3
"""WHY/CONTRACT/INVARIANT: reserve once, reviewed bytes only, no retry."""
import argparse,time,re,json
from gate import Ledger,need
from plans import RUNS
from engine import Session
import cases,validators
from geometry import *
from ipc_predicates import ancestry

def normal_remaining(s):
 for n in list(s.proc):
  if n not in ('owner','compositor','pointer') and s.proc[n].poll() is None:s.close_client(n,'close')

def standard_return(s,state,baseline,p,g,existing_images=None):
 oid=state['owner']['id'];s.expected_layout='splith'
 if existing_images is None:s.cmd(f'[con_id={oid}] layout splith',True);time.sleep(.4)
 state=s.owner('owner');prot=validators.grab(s.log('owner'));need(prot['ids']==p['ids'],'live second chain preserved')
 geo=cases.geometry(s.log('owner'),state['origin'],cases.Provenance(oid,state['workspace']['id'],'NOT OBSERVABLE','pointer+paint corroboration'))
 images=existing_images if existing_images is not None else s.pair_capture('standard-live');validators.standard_spill(images,COLORS)
 for target,key,cmd in [('POPUP_B','B','close_b'),('POPUP_A','A',None)]:
  state=s.owner('owner');geo=cases.geometry(s.log('owner'),state['origin'],cases.Provenance(oid,state['workspace']['id'],'NOT OBSERVABLE','fresh current pointer/paint candidate'));before_input=s.log('owner');im=images[1];xy=solid_point(im,COLORS[target],s.outputs[1],s.frames['HEADLESS-2'],geo[key]);tails,buttons=s.click('owner',xy);s.delivery('owner',geo[key],xy,tails,buttons,target)
  if target=='POPUP_A':
   from lifecycle import a_survival
   a_survival(images[1],before_input,s.log('owner'),p['ids'],buttons['owner'],xy,geo['A'])
  if cmd:
   before=s.log('owner');request=time.monotonic_ns();s.client_cmd('owner',cmd,'COMMAND close_b DONE');time.sleep(.2)
   from lifecycle import explicit_child_close
   explicit_child_close(before,s.log('owner'),p['ids'],request,time.monotonic_ns())
   images=s.pair_capture('B-closed-A-survives');need(count(images[1],COLORS['POPUP_A'])>0 and count(images[1],COLORS['POPUP_B'])==0,'A not alive/B residual')
 before_close=s.log('owner');s.close_client('owner')
 from lifecycle import normal_owner_close
 normal_owner_close(before_close,s.log('owner'),p['ids'],s.proc['owner'].returncode)
 final=s.pair_capture('standard-final');validators.rgb(baseline,final[1])
 return 'PARTIALLY_FEASIBLE'

def horizontal(s):
 cases.init_reference(s);state,baseline,p,g,left,right=cases.open_chain(s)
 xy=solid_point(left,COLORS['POPUP_B'],s.outputs[0],s.frames['HEADLESS-1'],g['B']);tails,buttons=s.click('owner',xy);s.delivery('owner',g['B'],xy,tails,buttons,'POPUP_B')
 forbidden=intersection(g['B'],s.outputs[1]['logical']);need(forbidden[2]>6 and forbidden[3]>6,'forbidden interior');point=[forbidden[0]+forbidden[2]//2,forbidden[1]+forbidden[3]//2]
 tails,buttons=s.click('owner',point);proof=cases.dismissal(tails['owner'],buttons['owner']);s.save('dismissal',proof);s.close_client('owner');s.save('first-chain-protocol-log',dict(raw=s.log('owner')))
 # Two independent real chains; no resurrected dismissed popup.
 old_id=state['owner']['id'];old_pid=state['owner']['pid'];state,baseline2,p,g,left,right=cases.open_chain(s);need(state['owner']['id']!=old_id and state['owner']['pid']!=old_pid,'second chain must have fresh owner/PID');return standard_return(s,state,baseline2,p,g)

COLORS=cases.COLORS
def execute(rid,lab,manifest,review,publication,session_factory=Session):
 auth=Ledger(lab).admit(rid,manifest,review,publication);s=None;status='INCONCLUSIVE';failure=None
 try:
  if rid=='G2' and session_factory is Session:
   from gpu_handler import GPUSceneSession
   s=GPUSceneSession(RUNS[rid],auth)
  else:s=session_factory(RUNS[rid],auth)
  if rid!='G2':s.start()
  if rid=='G2':
   from gpu_handler import run as gpu_run
   status=gpu_run(s)
  elif rid in ('P1','C8'):
   from fullscreen import run as fullscreen_run
   status=fullscreen_run(s)
   if rid=='C8' and status=='PARTIALLY_FEASIBLE':
    from fullscreen import comparable
    control=s.lab/'graphics-runs/P1/run/fullscreen-comparability.json'
    need(control.is_file(),'P1 actual comparability evidence missing')
    s.save('fullscreen-pair-comparison',comparable(json.loads(control.read_text()),json.loads((s.run/'fullscreen-comparability.json').read_text())))
  elif rid in ('O1','O2'):
   from oom_handler import run as oom_run
   status=oom_run(s)
  elif rid=='C1':status=horizontal(s)
  elif rid=='C5':status=cases.hidden_campaign(s)
  elif rid=='C6':
   from saved import run
   status=run(s)
  elif rid=='C7':status=cases.dynamic_campaign(s)
  elif rid=='P0':
   cases.init_reference(s);state,baseline,p,g,left,right=cases.open_chain(s)
   status=standard_return(s,state,baseline,p,g,[left,right])
  elif rid in ('C2','C3','C4'):status=cases.popup_campaign(s)
  else:raise ValueError('NOT_ADMITTED scenario')
  normal_remaining(s)
 except Exception as error:
  failure=f'{type(error).__name__}: {error}';status='INCONCLUSIVE'
  if rid in ('O1','O2') and s is not None:
   s.save('oom-partial-failure',dict(status='INCONCLUSIVE',failure=failure,critical_or_unresolved=True,blocks_O2=rid=='O1',owner_exit=s.proc['owner'].poll() if 'owner' in s.proc else None,compositor_exit=s.comp.poll() if hasattr(s,'comp') else None,events=s.events,captures_observed=sum(e['kind']=='capture' for e in s.events),captures_expected=8,missing_evidence='NOT_PROVEN; no retry',raw_owner=s.log('owner') if 'owner' in s.proc else None))
 finally:
  if s is not None:status=s.cleanup(status,failure)
  else:Ledger(lab).complete(auth,dict(status='INCONCLUSIVE',failure=failure,session_constructed=False))
 return dict(status=status,failure=failure,runner_exit=0 if status=='PARTIALLY_FEASIBLE' else 1)

def main():
 p=argparse.ArgumentParser(description='One independently admitted run; never all-cases or retry')
 p.add_argument('run_id',choices=RUNS);p.add_argument('--lab',required=True);p.add_argument('--manifest',required=True);p.add_argument('--review',required=True);p.add_argument('--publication',required=True)
 a=p.parse_args();result=execute(a.run_id,a.lab,a.manifest,a.review,a.publication);print(result);return result['runner_exit']
if __name__=='__main__':raise SystemExit(main())
