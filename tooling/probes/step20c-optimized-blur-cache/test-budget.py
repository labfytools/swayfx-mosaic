"""Offline exhaustion, corruption, cross-LAB refusal and lock contention."""
import json,multiprocessing,tempfile
from pathlib import Path
from budget import reserve

def denied(call):
 try:call()
 except (ValueError,RuntimeError):return
 raise AssertionError('accepted invalid reservation')
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'budget.json'
 denied(lambda:reserve(tmp,'C2','capture',p))
 for mode in ('C0','C1','C2'):
  reserve(tmp,mode,'run',p)
  denied(lambda:reserve(tmp,mode,'run',p))
  for _ in range(4):reserve(tmp,mode,'mutation',p)
  denied(lambda:reserve(tmp,mode,'mutation',p))
  for _ in range(20):reserve(tmp,mode,'capture',p)
  denied(lambda:reserve(tmp,mode,'capture',p))
  if mode!='C0':reserve(tmp,mode,'cycle',p)
  denied(lambda:reserve(tmp,mode,'cycle',p))
 reserve(tmp,'C2','camera_pair',p);denied(lambda:reserve(tmp,'C2','camera_pair',p))
 reserve(tmp,'C2','calibration',p);denied(lambda:reserve(tmp,'C2','calibration',p))
 denied(lambda:reserve(tmp+'new','C0','run',p))
 s=json.loads(p.read_text());assert sum(v['capture'] for v in s['modes'].values())==60
 p.write_text('');denied(lambda:reserve(tmp,'C0','run',p))
print('PASS exhaustion, no refunds/reset, cross-LAB protection, corruption')
def contender(root,q):
 try:reserve(root,'C0','run',Path(root)/'lock-test.json');q.put('accepted')
 except RuntimeError:q.put('denied')
with tempfile.TemporaryDirectory() as tmp:
 ctx=multiprocessing.get_context('fork');q=ctx.Queue();ps=[ctx.Process(target=contender,args=(tmp,q)) for _ in range(2)]
 for p in ps:p.start()
 for p in ps:p.join(5);assert p.exitcode==0
 assert sorted(q.get(timeout=1) for p in ps)==['accepted','denied']
print('PASS concurrent reservation')
