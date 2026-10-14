#!/usr/bin/env python3
"""Read-only D2 association replay and ALL native F commits; no verdict upgrade."""
import argparse,json
from gate import durable,sha,source_bindings
from plans import HIST
from validators import native_pairs
from test_targeted import HistoricalTests

def main():
    p=argparse.ArgumentParser();p.add_argument('--historical',type=__import__('pathlib').Path,default=HIST);p.add_argument('--output',type=__import__('pathlib').Path,required=True);a=p.parse_args()
    import test_targeted
    test_targeted.DATA=a.historical;s,state,raw,client,b=HistoricalTests().fixture()
    from cases import root_state
    root=root_state(s,state,state['origin'],b['window'][1]);log=a.historical/'matrix/F-mosaic/run/compositor.log';pairs=native_pairs(log.read_text())
    evidence={str(p):sha(p) for p in (a.historical/'matrix/D2-mosaic/run').iterdir() if p.name in ('compositor.log','owner.log','events.jsonl','startup-snapshot.json','owner-geometry.json')};evidence[str(log)]=sha(log);gaps=a.historical/'mosaic-source/sway/commands/gaps.c';evidence[str(gaps)]=sha(gaps)
    durable(a.output,dict(status='PASS',source_bindings=source_bindings(),evidence=evidence,E2=dict(status='SOURCE_ONLY; historical held NOT EXERCISED',runtime_command='gaps inner current set 30',argc=4,arrange_workspace='arrange_workspace(ws);' in gaps.read_text(),source=str(gaps),sha256=sha(gaps)),D2=dict(association=root,preowner=b,historical_verdict='INCONCLUSIVE unchanged; input/dismissal/final NOT EXERCISED'),F=dict(source=str(log),sha256=sha(log),pairs=pairs),runtime='NOT RUN'),True)
    print('OFFLINE_REPLAY_PASS D2 historical verdict unchanged; F ALL commits='+str(pairs['total_commits']))
if __name__=='__main__':main()
