#!/usr/bin/env python3
"""Exactly one reviewed matrix case, with preserved failures and owned cleanup."""
import argparse,json,time
from pathlib import Path
from gate import begin,LAB,verify,read,durable
from protocols import RUNS
from engine import Session
from cases import CAMPAIGN
p=argparse.ArgumentParser();p.add_argument('run_id',choices=RUNS);a=p.parse_args()
auth=begin(a.run_id);s=None;status='INCONCLUSIVE';failure=None
try:
    s=Session(RUNS[a.run_id],auth);s.start();status=CAMPAIGN[RUNS[a.run_id]['campaign']](s)
except Exception as e:
    failure=dict(type=type(e).__name__,message=str(e));status='INCONCLUSIVE'
finally:
    if s is not None:status=s.cleanup(status,failure)
    state=read(LAB/'matrix'/a.run_id/'actions.json')
    if s is not None:
        state['consumed_observed']=dict(capture=sum(e['kind']=='capture' for e in s.events),
            click=sum(e['kind']=='injection' and e['action']!='move' for e in s.events),
            move=sum(e['kind']=='injection' for e in s.events),grab=sum(e['kind']=='injection' and e.get('grab',False) for e in s.events))
    durable(LAB/'matrix'/a.run_id/'actions.json',state);verify()
print(json.dumps(dict(id=a.run_id,status=status,failure=failure)))
raise SystemExit(1 if failure else 0)
