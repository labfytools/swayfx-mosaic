"""Read-only real historical replay; does not requalify historical verdicts."""
import json,re
from PIL import Image
from pathlib import Path
from plans import OLD_LAB
from ledger import need,sha,source_bindings
from runtime import engine
from saved_validators import *
def replay():
    folder=OLD_LAB/'runs/saved-diagnostic-A/run'
    paths=[folder/n for n in ('events.jsonl','compositor.log','owner.log','initial-applied.json','saved-requested-pending-snapshot.json','H2-reference1.png','H2-reference2.png')]
    events=[json.loads(l) for l in paths[0].read_text().splitlines()];requests=[e for e in events if e['kind']=='ipc-request' and e.get('args')==['gaps inner current set 30']];need(len(requests)==1,'unique actual command request')
    request=requests[0]['ns'];replies=[e for e in events if e['kind']=='ipc-reply' and e.get('args')==['gaps inner current set 30']];need(len(replies)==1 and replies[0]['exit']==0 and all(r['success'] for r in json.loads(replies[0]['stdout'])),'real accepted geometry command')
    wire=paths[2].read_text();cut=wire.index('COMMAND hold_next_configure');before=wire[:cut];after=wire[cut:];prior=int(re.findall(r'ACK ns=\d+ serial=(\d+)',before)[-1])
    initial=json.loads(paths[3].read_text())['state']['snapshot'];pending=json.loads(paths[4].read_text());ws=engine.workspace(initial['tree'],'1');owner=next(n for n in engine.nodes(ws) if n.get('app_id')=='org.mosaic.SavedBufferProbe')
    geometry=pending_geometry(initial,pending,owner['id'],ws['id'],before,after,prior,request);native=saved_identity(paths[1].read_text(),owner['id'],request,True)
    a=Image.open(paths[5]).convert('RGB');b=Image.open(paths[6]).convert('RGB');rgb_exact(a,b)
    return dict(status='PASS',source_bindings=source_bindings(),evidence={str(p):sha(p) for p in paths},geometry=geometry,native=native,observed_instances=len(lifetime_instances(paths[1].read_text())),natural_timeout='NOT EXERCISED; teardown only',gpu_completion='NOT PROVEN',historical_verdict='INCONCLUSIVE unchanged')
if __name__=='__main__':print(json.dumps(replay(),indent=2))
