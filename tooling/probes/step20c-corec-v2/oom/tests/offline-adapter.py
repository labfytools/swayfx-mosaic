#!/usr/bin/env python3
"""Synthetic/token tests only. No actual graphics-engine admission or process."""
import argparse,importlib.util,json,pathlib,stat
P=pathlib.Path;ap=argparse.ArgumentParser();ap.add_argument('--output',type=P,required=True);a=ap.parse_args()
o=a.output.absolute();assert o.is_relative_to(P('/var/tmp')) and not o.exists() and o.resolve()==o;o.mkdir(mode=0o700)
spec=importlib.util.spec_from_file_location('adapter',P(__file__).resolve().parents[1]/'graphics-adapter.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Session:
 spec={'id':'O1'}
 run=o/'run'
 def __init__(self):self.calls=[]
 def debit(self,k):assert k=='hook';self.calls.append(k)
 def record(self,k,**kw):self.calls.append(k)
s=Session();s.run.mkdir(mode=0o700)
e={'SMX_OOM_TOKEN_PATH':str(s.run/'oom-token'),'SMX_OOM_NONCE':'123456789abcdef0123456789abcdef0','SMX_OOM_ROLE':'root_popup'}
a=dict(decision='ACCEPTED',run='O1',oom_source_review='ACCEPTED',build_review='ACCEPTED',publication='VERIFIED',variant_identity='COREC_V2_NATIVE_OOM_DIAGNOSTIC')
stable=dict(startup=True,owner=True,neighbor=True,reference_H2_twice=True)
m.arm(s,e,a,stable);assert s.calls==['hook','oom-arm'];assert (s.run/'oom-token').read_text()=='SMXOOM1 '+e['SMX_OOM_NONCE']+' root_popup\n';assert stat.S_IMODE((s.run/'oom-token').stat().st_mode)==0o600
try:m.arm(s,e,a,stable)
except FileExistsError:pass
else:raise AssertionError('rearm unexpectedly accepted')
assert s.calls==['hook','oom-arm','hook']
log='SMX_OOM ENOMEM role=root_popup nonce='+e['SMX_OOM_NONCE']+' pid=123 xdg=0x1 xdg_parent=0x2 parent=0x3 tree=0x4 children=0 matched=1 failures=1 successes=0 initialized=0 listeners=0 published=0'
m.native_failure(log,e,123)
for bad in [log+'\n'+log,log.replace('pid=123','pid=124'),log.replace('role=root_popup','role=nested_popup')]:
 try:m.native_failure(bad,e,123)
 except AssertionError:pass
 else:raise AssertionError('bad synthetic failure accepted')
s.spec={'id':'O2'};a['run']='O2';stable.update(rootA=False,rootA_native_success=False)
prior=list(s.calls)
try:m.arm(s,e,a,stable)
except AssertionError:pass
else:raise AssertionError('O2 without stable rootA accepted')
assert s.calls==prior
result=dict(status='PASS_OFFLINE',checks=['exclusive owned token exact bytes0600','debit before write','rearm refused retaining debit','single native failure synthetic parser with nonce/PID/role','O2 no stable rootA refused before hook'],runtime='NOT_RUN')
(o/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
