#!/usr/bin/env python3
"""Seal exact final closure; independent review still required afterwards."""
import argparse,json,shutil,sys
from pathlib import Path
from gate import *
def seal(identity):
 identities=json.loads(Path(identity).read_text());need(set(identities)=={'core','pristine'},'both exact identities required')
 files={str(p):sha(p) for p in BASE.rglob('*') if p.is_file() and p.suffix in ('.py','.c','.h','.xml','.txt','.json','.conf','.md') and p.name not in ('review.json','pre-run-manifest.json') and 'runs' not in p.parts}
 files.update(json.loads((BASE/'compile.json').read_text())['files'])
 source=LAB/'audit/candidate-source-freeze.json';files[str(source)]=sha(source)
 for p,h in json.loads(source.read_text())['files'].items():
  path=LAB/p;need(sha(path)==h,'source freeze changed');files[str(path)]=h
 for name,a in identities.items():
  need(name in ('core','pristine'),'identity name');need(sha(a['binary'])==a['binary_sha256'],'exact binary');files[a['binary']]=a['binary_sha256']
  need(a['wlroots']==str(WL) and a['wlroots_sha256']==WL_SHA,'required wlroots');files[str(WL)]=WL_SHA
  if name=='pristine':
   need(a.get('source_parent')=='fd71a6bdc061bd633b488ae7b83e8a6981d22f86','pristine parent');need(a.get('pristine_scene') and a.get('source_proof'),'pristine comparability proof required');files[a['pristine_scene']]=a['pristine_scene_sha256'];proof=json.loads(Path(a['source_proof']).read_text());need(proof.get('status')=='PASS' and proof.get('pinned_parent')==a['source_parent'],'pristine source proof unproven');files[a['source_proof']]=sha(a['source_proof'])
   for row in proof['files']:
    path=Path(proof['source'])/row['path'];need(row['match'] and sha(path)==row['expected'],'pristine source changed');files[str(path)]=row['expected']
 for p in (LAB/'build-audit').glob('*.json'):files[str(p)]=sha(p)
 for t in ('swaymsg','grim','swaybg'):
  path=Path(shutil.which(t)).resolve();files[str(path)]=sha(path)
 import PIL
 for p in Path(PIL.__file__).parent.rglob('*'):
  if p.is_file() and p.suffix in ('.py','.so'):files[str(p)]=sha(p)
 files[str(Path(sys.executable).resolve())]=sha(Path(sys.executable).resolve())
 durable(BASE/'pre-run-manifest.json',dict(ticket=TICKET,lab=str(LAB),status='SEALED_REVIEW_PENDING',identities=identities,files=files),True)
 print(sha(BASE/'pre-run-manifest.json'))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('identities');seal(p.parse_args().identities)
