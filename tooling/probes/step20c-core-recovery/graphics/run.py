#!/usr/bin/env python3
"""WHY/CONTRACT/INVARIANT: reserve once, reviewed bytes only, no retry."""
import argparse,time,re
from gate import LAB,begin,durable,BASE,need
from plans import RUNS
from engine import Session
import cases,validators
from geometry import *
from ipc_predicates import ancestry

def normal_remaining(s):
 for n in list(s.proc):
  if n not in ('owner','compositor','pointer') and s.proc[n].poll() is None:s.close_client(n,'close')

def standard_return(s,state,baseline,p,g):
 oid=state['owner']['id'];s.expected_layout='splith';s.cmd(f'[con_id={oid}] layout splith',True);time.sleep(.4)
 state=s.owner('owner');prot=validators.grab(s.log('owner'));need(prot['ids']==p['ids'],'live second chain preserved')
 geo=cases.geometry(s.log('owner'),state['origin'],cases.Provenance(oid,state['workspace']['id'],'NOT OBSERVABLE','pointer+paint corroboration'))
 images=s.pair_capture('standard-live');validators.standard_spill(images,COLORS)
 for target,key,cmd in [('POPUP_B','B','close_b'),('POPUP_A','A',None)]:
  im=images[1];xy=solid_point(im,COLORS[target],s.outputs[1],s.frames['HEADLESS-2'],geo[key]);tails,buttons=s.click('owner',xy);s.delivery('owner',geo[key],xy,tails,buttons,target)
  if cmd:
   before=s.log('owner');request=time.monotonic_ns();s.client_cmd('owner',cmd,'COMMAND close_b DONE');time.sleep(.2)
   from lifecycle import explicit_child_close
   explicit_child_close(before,s.log('owner'),p['ids'],request,time.monotonic_ns())
   images=s.pair_capture('B-closed-A-survives');need(count(images[1],COLORS['POPUP_A'])>0 and count(images[1],COLORS['POPUP_B'])==0,'A not alive/B residual')
 s.close_client('owner');final=s.pair_capture('standard-final');validators.rgb(baseline,final[1])
 return 'PARTIALLY_FEASIBLE'

def horizontal(s):
 cases.init_reference(s);state,baseline,p,g,left,right=cases.open_chain(s)
 xy=solid_point(left,COLORS['POPUP_B'],s.outputs[0],s.frames['HEADLESS-1'],g['B']);tails,buttons=s.click('owner',xy);s.delivery('owner',g['B'],xy,tails,buttons,'POPUP_B')
 forbidden=intersection(g['B'],s.outputs[1]['logical']);need(forbidden[2]>6 and forbidden[3]>6,'forbidden interior');point=[forbidden[0]+forbidden[2]//2,forbidden[1]+forbidden[3]//2]
 tails,buttons=s.click('owner',point);proof=cases.dismissal(tails['owner'],buttons['owner']);s.save('dismissal',proof);s.close_client('owner');s.save('first-chain-protocol-log',dict(raw=s.log('owner')))
 # Two independent real chains; no resurrected dismissed popup.
 state,baseline2,p,g,left,right=cases.open_chain(s);return standard_return(s,state,baseline2,p,g)

def fullscreen(s):
 # WHY/CONTRACT/INVARIANT: fullscreen the actual nonleaf parent containing owner.
 cases.init_reference(s);s.debit('chain');s.launch_client('owner','nested-client','static_cross');oid=s.find('owner')['id']
 s.cmd(f'[con_id={oid}] focus');s.cmd('splitv');s.launch_client('nested-filler','static-reference');s.cmd(f'[con_id={oid}] focus')
 before=s.owner('owner');baseline=cases.stable_reference(s);s.cmd('focus parent');s.cmd('fullscreen enable',True);time.sleep(.4)
 state=s.owner('owner');path=ancestry(state['snapshot']['tree'],oid);ancestor=validators.fullscreen_ancestor(path);anc=[ancestor]
 s.save('fullscreen-current-ancestor',dict(before=before,path=path,ancestor_ids=[n['id'] for n in anc]))
 if not anc:raise ValueError('current fullscreen ancestor NOT EXERCISED')
 image=s.capture('fullscreen-owner','HEADLESS-1');xy=solid_point(image,COLORS['TOPLEVEL'],s.outputs[0],s.frames['HEADLESS-1'])
 tails,buttons=s.click('owner',xy,'left',True);s.wait(lambda:'POPUP_A MAP ' in s.log('owner'));time.sleep(.2)
 image=s.capture('fullscreen-A','HEADLESS-1');xyA=solid_point(image,COLORS['POPUP_A'],s.outputs[0],s.frames['HEADLESS-1'])
 tailsA,buttonsA=s.click('owner',xyA,'left',True);s.wait(lambda:'POPUP_B MAP ' in s.log('owner'));time.sleep(.2)
 prot=validators.grab(s.log('owner'));geo=cases.geometry(s.log('owner'),state['origin'],cases.Provenance(oid,state['workspace']['id'],'NOT OBSERVABLE','fullscreen paint+pointer'))
 s.delivery('owner',[*state['origin'],state['owner']['window_rect']['width'],state['owner']['window_rect']['height']],xy,tails,buttons,'TOPLEVEL',prot['grabs'][0]['serial'])
 s.delivery('owner',geo['A'],xyA,tailsA,buttonsA,'POPUP_A',prot['grabs'][1]['serial'])
 images=s.pair_capture('fullscreen-nested');point=solid_point(images[0],COLORS['POPUP_B'],s.outputs[0],s.frames['HEADLESS-1'],geo['B']);tails,buttons=s.click('owner',point);s.delivery('owner',geo['B'],point,tails,buttons,'POPUP_B')
 s.cmd(f'[con_id={anc[-1]["id"]}] fullscreen disable',True);time.sleep(.4);s.pair_capture('fullscreen-left')
 s.expected_layout='splith';s.cmd(f'[con_id={oid}] layout splith',True);time.sleep(.4);s.pair_capture('fullscreen-standard');s.close_client('owner');final=s.pair_capture('fullscreen-final');validators.rgb(baseline,final[1])
 s.save('fullscreen-policy',dict(status='INCONCLUSIVE',reason='paired pristine/core raw observations; cross-run comparison required, no UX policy inferred',atomic_generation='NOT OBSERVABLE'))
 return 'PARTIALLY_FEASIBLE'

COLORS=cases.COLORS
def main():
 p=argparse.ArgumentParser();p.add_argument('run_id',choices=RUNS);rid=p.parse_args().run_id
 auth=begin(rid);s=None;status='INCONCLUSIVE';failure=None
 try:
  s=Session(RUNS[rid],auth);s.start()
  if rid=='S2-core-horizontal':status=horizontal(s)
  elif 'fullscreen' in rid:status=fullscreen(s)
  elif rid=='S7-core-hidden-return':status=cases.hidden_campaign(s)
  elif rid=='S8-core-saved':
   from saved import run
   status=run(s)
  elif 'standard' in rid:
   cases.init_reference(s);state,baseline,p,g,left,right=cases.open_chain(s);status=standard_return(s,state,baseline,p,g)
  else:status=cases.popup_campaign(s)
  normal_remaining(s)
 except Exception as e:
  # WHY/CONTRACT/INVARIANT: successful measurements do not qualify a failed run.
  failure=f'{type(e).__name__}: {e}';status='INCONCLUSIVE'
 finally:
  if s is not None:status=s.cleanup(status,failure)
 print(status,failure or '');return 0 if status in ('PASS','PARTIALLY_FEASIBLE') else 1
if __name__=='__main__':raise SystemExit(main())
