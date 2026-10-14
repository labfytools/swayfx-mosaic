#!/usr/bin/env python3
"""Read-only replay of immutable raw E incidents; never rewrite old verdicts."""
import json,re
from pathlib import Path
from PIL import Image
import validators as v
from saved_validators import held_configure,released_configure,rgb_exact,timeout_line
from ipc_predicates import nodes,ancestry,workspace
from gate import sha,LAB,durable
HIST=Path('/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_/graphics/runs')
CORE='29baf31aa3eeed259825c87d0799fa5d3dc83710afb967154604eb1c6657f965'

def saved_raw():
 d=HIST/'E6/run';raw=(d/'owner.log').read_text();ev=[json.loads(l) for l in (d/'events.jsonl').read_text().splitlines()]
 release=next(e['ns'] for e in ev if e['kind']=='client-request' and e.get('command')=='release_configure')
 held_serial=int(re.search(r'HELD ns=\d+ serial=(\d+)',raw)[1])
 cut=raw.index('COMMAND hold_next_configure DONE');before=raw[:cut];prior=int(re.findall(r'ACK ns=\d+ serial=(\d+)',before)[-1])
 tail=raw[cut:];wire=re.search(rf'[^\n]*xdg_surface#\d+\.ack_configure\({held_serial}\)',tail)
 holdtext=tail[:wire.start()];held=held_configure(before,holdtext,prior)
 caps=[e for e in ev if e['kind']=='capture'];post=next(e for e in caps if e['tag']=='natural-timeout-H1')['start_ns']
 live=released_configure(held,tail,release,post)
 request=next(e['ns'] for e in ev if e['kind']=='ipc-request' and e['args']==['gaps inner current set 30'])
 timeout=timeout_line((d/'compositor.log').read_text(),-1,True,request,post,release)
 for e in caps:
  v.evidence_identity(dict(binary_sha256=json.loads((d/'outcome.json').read_text())['evidence_provenance']['binary_sha256'],measurement_kind='raw'),CORE)
  assert e['sha256']==sha(e['path']) and e['output']==('HEADLESS-1' if e['tag'].endswith('H1') else 'HEADLESS-2')
  with Image.open(e['path']) as im:assert im.size==(800,600)
 ref=Image.open(d/'H2-reference1.png').convert('RGB')
 for name in ('H2-reference2','held-H2','natural-timeout-H2','restored-live-H2'):rgb_exact(ref,Image.open(d/(name+'.png')).convert('RGB'))
 assert max(e['end_ns'] for e in caps if e['tag'].startswith('held-'))<request+4_700_000_000
 assert post<release<live['ack_ns']<next(e['start_ns'] for e in caps if e['tag']=='restored-live-H1')
 return dict(held=held,live=live,timeout_native=timeout,request_ns=request,natural_capture_ns=post,capture_count=len(caps),whole_H2='EXACT',original_verdict='INCONCLUSIVE',normal_owner_close='NOT ACQUIRED',final_after_close='NOT ACQUIRED',native_saved_identity='NOT OBSERVABLE',S8_justification='Explicit normal-close, SHM releases and final restoration missing; phased ACK/live PNG already acquired')

def replay():
 result={'status':'PASS','historical_verdicts_unchanged':True,'incidents':{},'files':{}}
 for rid in ('E0-pristine','E0-core','E2-vertical'):
  d=HIST/rid/'run';candidates=[]
  for p in d.glob('*snapshot.json'):
   snap=json.loads(p.read_text());tree=snap['tree']
   for n in nodes(tree):
    if n.get('pid') and n.get('app_id')=='org.mosaic.NestedGrabProbe':
     path=ancestry(tree,n['id']);ws=next(x for x in path if x['type']=='workspace');candidates.append(dict(owner=n['id'],floating=[x.get('floating') for x in path],eligible=v.camera_eligible(path,ws)))
  # Some failed owner snapshots were overwritten; reconstruct from actual IPC
  # reply JSON rather than inventing a tree or repairing historical snapshots.
  if not candidates:
   for line in (d/'events.jsonl').read_text().splitlines():
    e=json.loads(line)
    if e['kind']=='ipc-reply' and e.get('args')==['-t','get_tree'] and e['exit']==0:
     tree=json.loads(e['stdout'])
     for n in nodes(tree):
      if n.get('app_id')=='org.mosaic.NestedGrabProbe':
       path=ancestry(tree,n['id']);ws=next(x for x in path if x['type']=='workspace');candidates.append(dict(owner=n['id'],floating=[x.get('floating') for x in path],eligible=v.camera_eligible(path,ws)))
  assert candidates,rid
  result['incidents'][rid]=dict(ancestry_replayed=candidates,original_verdict='INCONCLUSIVE',png_count=len(list(d.glob('*.png'))))
 for rid in ('E1','E4','E5'):
  d=HIST/rid/'run';events=[json.loads(l) for l in (d/'events.jsonl').read_text().splitlines()]
  result['incidents'][rid]=dict(original_verdict=json.loads((d/'outcome.json').read_text())['status'],png_count=len(list(d.glob('*.png'))))
  if rid=='E1':
   evidence=json.loads((d/'first-chain-protocol-log.json').read_text())['raw'];result['incidents'][rid]['first_chain']=v.grab(evidence[:evidence.index('POPUP_B POPUP_DONE')])
   # The surviving owner log belongs to chain2 on H2; reject its actual tree.
   maps=[json.loads(e['stdout']) for e in events if e['kind']=='ipc-reply' and e.get('args')==['-t','get_tree'] and e['exit']==0]
   tree=maps[-1];owner=next(n for n in nodes(tree) if n.get('app_id')=='org.mosaic.NestedGrabProbe');path=ancestry(tree,owner['id'])
   try:v.owner_context(owner,path,owner['pid'],'1','HEADLESS-1','mosaic')
   except ValueError:result['incidents'][rid]['wrong_second_map_rejected']=True
   else:raise AssertionError('historical wrong map accepted')
  if rid=='E4':
   state=json.loads((d/'fullscreen-current-ancestor.json').read_text());result['incidents'][rid]['actual_nonleaf']=v.fullscreen_ancestor(state['path'])['id']
  if rid=='E5':
   raw=(d/'owner.log').read_text();done=raw.index('POPUP_B POPUP_DONE');result['incidents'][rid]['dismissal_before_return']=True
   assert raw.index('POPUP_A POPUP_DONE')>done
 result['saved']=saved_raw()
 for rid in ('E0-pristine','E0-core','E2-vertical','E1','E4','E5','E6'):
  for p in (HIST/rid/'run').iterdir():
   if p.is_file():result['files'][str(p)]=sha(p)
 return result
if __name__=='__main__':
 r=replay();durable(LAB/'graphics/historical-replay.json',r);print(json.dumps({k:v for k,v in r.items() if k!='files'},indent=2))
