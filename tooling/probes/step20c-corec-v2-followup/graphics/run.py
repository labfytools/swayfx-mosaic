#!/usr/bin/env python3
"""WHY/CONTRACT/INVARIANT: one new ID, reviewed source, no retry or auto-review."""
import argparse,json,os,time
from pathlib import Path
from gate import Ledger,need,disable_dump,validate_review
from plans import RUNS
from engine import Session,storage_guard
import cases


def normal_remaining(s):
 for name in list(s.proc):
  if name not in ('owner','compositor','pointer') and s.proc[name].poll() is None:s.close_client(name,'close')


def execute(rid,lab,manifest,review,publication):
 disable_dump();storage_guard(Path(lab))
 # WHY: missing replay inputs must not consume a run. The independent gate is
 # validated again inside admit, then before every action. Never repair a freeze.
 validate_review(lab,manifest,review,publication,rid)
 need(not (Path(lab)/'graphics-runs'/rid).exists(),'existing run directory; no overwrite/retry')
 auth=Ledger(lab).admit(rid,manifest,review,publication)
 s=None;failure=None;status='INCONCLUSIVE'
 try:
  if rid=='GPU-G3':
   from gpu_handler import GPUSceneSession,run as gpu_run
   s=GPUSceneSession(RUNS[rid],auth);status=gpu_run(s)
  else:
   s=Session(RUNS[rid],auth);s.start()
  if rid=='GPU-G3':pass
  elif rid in ('FS-P','FS-C'):
   from fullscreen import run,comparable
   status=run(s)
   if rid=='FS-C' and status=='PARTIALLY_FEASIBLE':
    control=s.lab/'graphics-runs/FS-P/run/fullscreen-comparability.json'
    need(control.is_file(),'FS-P measured comparable source missing')
    s.save('fullscreen-comparison',comparable(json.loads(control.read_text()),json.loads((s.run/'fullscreen-comparability.json').read_text())))
  elif rid=='DY-C':status=cases.dynamic_campaign(s)
  elif rid in ('OM-ROOT','OM-NESTED'):
   from oom_handler import run
   status=run(s)
  else:raise ValueError('NOT_ADMITTED: independent diagnostic adapter absent')
  normal_remaining(s)
 except Exception as exc:
  failure=f'{type(exc).__name__}: {exc}';status='INCONCLUSIVE'
  if s is not None:
   s.save('partial-failure',dict(status=status,failure=failure,events=s.events,captures_observed=sum(e['kind']=='capture' for e in s.events),compositor_exit=s.comp.poll() if hasattr(s,'comp') else None,owner_exit=s.proc['owner'].poll() if 'owner' in s.proc else None,critical_or_unresolved=True,no_retry=True))
 finally:
  if s is None:Ledger(lab).complete(auth,dict(status='INCONCLUSIVE',failure=failure,session_constructed=False))
  else:
   try:status=s.cleanup(status,failure)
   except Exception as exc:
    # Cleanup exceptions remain failures; autonomous watchdog still owns groups.
    failure=(failure or '')+f'; cleanup {type(exc).__name__}: {exc}'
    Ledger(lab).complete(auth,dict(status='INCONCLUSIVE',failure=failure,scientific_cleanup=False))
    status='INCONCLUSIVE'
 return dict(status=status,failure=failure,runner_exit=0 if status=='PARTIALLY_FEASIBLE' else 1)

if __name__=='__main__':
 p=argparse.ArgumentParser(description='One independent new-ticket run, never retry/all')
 p.add_argument('run_id',choices=RUNS)
 for name in ('lab','manifest','review','publication'):p.add_argument('--'+name,required=True)
 a=p.parse_args();result=execute(a.run_id,a.lab,a.manifest,a.review,a.publication);print(json.dumps(result));raise SystemExit(result['runner_exit'])
