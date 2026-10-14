"""Mutation tests on modules actually imported by run/engine/cases."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import run,engine,cases,gate,validators as v
from plans import RUNS
class Tests(unittest.TestCase):
 def test_imported_identity(self):
  self.assertIs(run.validators,v);self.assertIs(engine.validators,v);self.assertIs(cases.validators,v)
 def test_source_compile(self):
  for p in gate.BASE.glob('*.py'):compile(p.read_text(),str(p),'exec')
 def test_whole_h2(self):
  a=Image.new('RGB',(800,600),(48,48,56));v.rgb(a,a)
  b=a.copy();b.putpixel((799,599),(48,48,55))
  with self.assertRaises(ValueError):v.rgb(a,b)
  with self.assertRaises(ValueError):v.rgb(a,a,True)
 def test_wrong_output(self):
  spec=RUNS['E2-r90']['outputs'];rows=[dict(active=True,name=o['name'],rect=dict(zip(('x','y','width','height'),o['logical'])),scale=o['scale'],transform=o['transform'],current_mode=dict(zip(('width','height'),o['mode']))) for o in spec]
  v.expected_outputs(rows,spec);rows[0]['name']='HEADLESS-3'
  with self.assertRaises(ValueError):v.expected_outputs(rows,spec)
 def test_owner(self):
  p=[dict(type='workspace',id=4)];v.owner(dict(id=5),5,4,p)
  with self.assertRaises(ValueError):v.owner(dict(id=6),5,4,p)
  with self.assertRaises(ValueError):v.owner(dict(id=5),5,8,p)
 def test_real_grab_mutations(self):
  raw=(gate.BASE/'wire-fixture.txt').read_text();p=v.grab(raw);self.assertEqual(len(p['grabs']),2)
  for bad in (raw.replace('origin=wl_pointer.button','origin=fake'),raw.replace(' used='+str(p['grabs'][0]['serial']),' used=999999'),raw.replace('parent_xdg='+str(p['ids']['TOPLEVEL'][1]),'parent_xdg=999999'),raw.replace('wl_pointer#','fake_pointer#')):
   with self.assertRaises((ValueError,AssertionError)):v.grab(bad)
 def test_ambiguous_window(self):
  v.window(1,4,[2])
  for bad in ([0],[2,3],[]):
   with self.assertRaises(ValueError):v.window(1,4,bad)
 def test_no_crossing(self):
  v.crosses([-10,0,20,10],0,0)
  with self.assertRaises(ValueError):v.crosses([0,0,20,10],0,0)
 def test_shadow(self):
  a=Image.new('RGB',(3,3));b=a.copy();b.putpixel((0,0),(1,0,0));v.shadow(a,b)
  with self.assertRaises(ValueError):v.shadow(a,a)
 def test_wrong_binary_saved(self):
  with self.assertRaises(ValueError):v.saved_identity(dict(binary_sha256='old',native=True),'core')
  with self.assertRaises(ValueError):v.saved_identity(dict(binary_sha256='core',native=False),'core')
 def test_pending_not_applied(self):
  v.applied([1,2],[1,2],[1,2],'applied')
  with self.assertRaises(ValueError):v.applied([1,2],[1,2],[1,2],'pending')
  with self.assertRaises(ValueError):v.applied([1,2],[1,2],[2,2],'applied')
 def test_code0_error_nonzero(self):
  v.client_exit('EXIT error=0',0)
  for log,code in [('EXIT error=7',0),('EXIT error=0',2),('',0)]:
   with self.assertRaises(ValueError):v.client_exit(log,code)
 def test_stale_review(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'manifest';p.write_text('{}')
   with self.assertRaises(ValueError):gate.validate_review(p,dict(decision='ACCEPTED',independent=True,manifest_sha256='stale'))
 def test_consumed_budget_no_refund(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'budget';gate.durable(p,dict(ticket=gate.TICKET,limits={},runs=[dict(id='E1')],builds=[],stages=[]))
   def reject(b):gate.need(not any(r['id']=='E1' for r in b['runs']),'consumed')
   before=p.read_bytes()
   with self.assertRaises(ValueError):gate.transact(reject,p)
   self.assertEqual(p.read_bytes(),before)
   p.write_text(json.dumps(dict(ticket='historical',runs=[])))
   with self.assertRaises(ValueError):gate.transact(lambda b:None,p)
 def test_limits(self):
  self.assertEqual(len(RUNS),11);self.assertEqual(sum(s['capture_limit'] for s in RUNS.values()),154)
  self.assertTrue(all(s['capture_limit']<=20 for s in RUNS.values()))
if __name__=='__main__':unittest.main(verbosity=2)
