#!/usr/bin/env python3
"""One newly authorized exact-byte run; no retries or implicit campaigns."""
import argparse,json
from gate import *
from engine import Session
from cases import CAMPAIGN

def main():
    p=argparse.ArgumentParser();p.add_argument('--lab',type=Path,required=True);p.add_argument('run_id',choices=RUNS);a=p.parse_args();lab=owned(a.lab)
    auth=begin(lab,a.run_id);s=None;status='INCONCLUSIVE';failure=None
    try:
        s=Session(RUNS[a.run_id],auth,lab);s.start()
        if s.spec['campaign']=='FX':
            from fx import effects_campaign
            status=effects_campaign(s)
        else:status=CAMPAIGN[s.spec['campaign']](s)
    except Exception as e:failure=dict(type=type(e).__name__,message=str(e))
    finally:
        if s is not None:status=s.cleanup(status,failure)
        observed={}
        if s:
            observed=dict(capture=sum(e['kind']=='capture' for e in s.events),spawn=sum(e['kind']=='spawn' for e in s.events),move=sum(e['kind']=='injection' for e in s.events),click=sum(e['kind']=='injection' and e['action']!='move' for e in s.events),grab=sum(e['kind']=='injection' and e.get('grab',False) for e in s.events))
        def finish(state):
            row=state['runs'][a.run_id];need(all(v<=row['reserved'][k] for k,v in observed.items()),'observed reservation reconciliation');row.update(observed=observed,outcome=status,failure=failure)
        locked(lab,finish);verify(lab)
    print(json.dumps(dict(id=a.run_id,status=status,failure=failure)));return 1 if failure else 0
if __name__=='__main__':raise SystemExit(main())
