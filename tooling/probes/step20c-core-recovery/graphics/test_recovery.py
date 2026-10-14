"""Adversarial tests import exactly the predicates used by Session/run/cases."""
import copy,json,re,unittest,os
from unittest.mock import patch
import gate
from PIL import Image
import engine,cases,run,validators as v,saved_validators as sv
from replay import saved_raw,HIST,replay
from ipc_predicates import ancestry,workspace,nodes
from plans import RUNS
from geometry import png_global,global_png,expected_outputs,solid_point

class Recovery(unittest.TestCase):
 def rejects(self,fn,*args):
  with self.assertRaises((ValueError,AssertionError,RuntimeError)):fn(*args)
 def test_desktop_environment_scrubbed(self):
  names=['DISPLAY','WAYLAND_DISPLAY','SWAYSOCK','XDG_RUNTIME_DIR','LD_PRELOAD','LD_LIBRARY_PATH','DBUS_SESSION_BUS_ADDRESS','XDG_CURRENT_DESKTOP','DESKTOP_SESSION','XDG_ACTIVATION_TOKEN','DESKTOP_STARTUP_ID','XDG_SESSION_ID','WLR_BACKENDS']
  with patch.dict(os.environ,{k:'desktop' for k in names}):
   e=gate.clean_environment();self.assertTrue(all(k not in e for k in names))
 def test_actual_gate_stale_and_consumed(self):
  import tempfile
  from pathlib import Path
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'manifest';p.write_text('{}')
   self.rejects(gate.validate_review,p,dict(decision='ACCEPTED',independent=True,manifest_sha256='stale'))
   budget=Path(d)/'budget';budget.write_text(json.dumps(dict(ticket='historical',runs=[])));before=budget.read_bytes()
   self.rejects(gate.transact,lambda x:None,budget);self.assertEqual(before,budget.read_bytes())
   rid='S0-pristine-standard';auth=dict(binary='fake',binary_sha256='sha')
   m=dict(authorized_runs=[rid],identities=dict(pristine=auth))
   limits=dict(runs=11,captures=160,captures_per_run=18,duration_s=150)
   def tx(callback):return callback(dict(limits=limits,runs=[dict(id=rid)]))
   # begin's real reserve callback, not a duplicate budget model.
   with patch.object(gate,'validate_review',return_value=m),patch.object(gate,'sha',return_value='sha'),patch.object(gate,'transact',side_effect=tx),patch.object(Path,'read_text',return_value='{}'):
    self.rejects(gate.begin,rid)
 def test_live_shared(self):
  self.assertIs(engine.validators,v);self.assertIs(run.validators,v);self.assertIs(cases.validators,v)
 def tree(self):
  t=json.loads((HIST/'E2-vertical/run/owner-owner-snapshot.json').read_text())['tree'];n=next(n for n in nodes(t) if n.get('app_id')=='org.mosaic.NestedGrabProbe');return t,n,ancestry(t,n['id'])
 def test_null_floating_actual_ancestry(self):
  t,n,p=self.tree();ws=workspace(t,'1');self.assertTrue(v.camera_eligible(p,ws));self.assertTrue(any(x.get('floating') is None for x in p))
  n['floating']='user_on';self.assertFalse(v.camera_eligible(p,ws));n['floating']='auto_off'
  parent=p[-2];parent['nodes'].remove(n);parent['floating_nodes'].append(n);self.assertFalse(v.camera_eligible(p,ws))
 def test_wrong_owner_context(self):
  t,n,p=self.tree();v.owner_context(n,p,n['pid'],'1','HEADLESS-1','mosaic')
  for args in [(n,p,0,'1','HEADLESS-1','mosaic'),(n,p[:-1],n['pid'],'1','HEADLESS-1','mosaic'),(n,p,n['pid'],'2','HEADLESS-1','mosaic'),(n,p,n['pid'],'1','HEADLESS-2','mosaic'),(n,p,n['pid'],'1','HEADLESS-1','splith')]:self.rejects(v.owner_context,*args)
 def test_fullscreen_workspace_marker_insufficient(self):
  t,n,p=self.tree();self.rejects(v.fullscreen_ancestor,p)
  q=json.loads((HIST/'E4/run/fullscreen-current-ancestor.json').read_text())['path'];v.fullscreen_ancestor(q)
  q[-2]['fullscreen_mode']=0;self.rejects(v.fullscreen_ancestor,q)
 def test_wire_grab_and_native_size(self):
  raw=(__import__('pathlib').Path(__file__).parent/'wire-fixture.txt').read_text();proof=v.grab(raw)
  for bad in (raw.replace('POPUP_B MAP ','BAD MAP '),raw.replace('origin=wl_pointer.button','origin=fake'),raw.replace('used='+str(proof['grabs'][0]['serial']),'used=999999'),raw.replace('parent_xdg='+str(proof['ids']['TOPLEVEL'][1]),'parent_xdg=999999'),re.sub(r'(create_buffer\(new id wl_buffer#\d+, 0, )\d+, \d+, \d+, 1\)',r'\g<1>999, 999, 3996, 1)',raw)):self.rejects(v.grab,bad)
 def test_vertical_axis_outputs_frame(self):
  s=RUNS['S4-core-vertical'];self.assertEqual(s['boundary'],600);v.crosses([50,505,250,170],1,600)
  self.rejects(v.crosses,[50,100,250,170],1,600);self.rejects(v.crosses,[50,505,250,170],0,0)
  o=s['outputs'][1];self.assertEqual(png_global((30,40),o,'logical'),[30,640]);self.assertEqual(global_png([30,640],o,'logical'),[30,40]);self.rejects(png_global,(1,2),o,'unknown')
  rows=[dict(active=True,name=o['name'],rect=dict(zip(('x','y','width','height'),o['logical'])),scale=1,transform='normal',current_mode=dict(width=800,height=600)) for o in s['outputs']];expected_outputs(rows,s['outputs']);rows[1]['rect']['y']=0;self.rejects(expected_outputs,rows,s['outputs'])
 def test_hidden_dismissal_rejected(self):
  raw=(__import__('pathlib').Path(__file__).parent/'wire-fixture.txt').read_text();initial=v.grab(raw);v.hidden_survival(raw,initial,[dict(action='move')]);self.rejects(v.hidden_survival,raw,initial,[dict(action='left')]);self.rejects(v.hidden_survival,raw+'POPUP_B POPUP_DONE ',initial,[])
 def test_effective_standard_clip_removal(self):
  a=Image.new('RGB',(20,20));a.putpixel((0,0),engine.COLORS['POPUP_A']);a.putpixel((1,1),engine.COLORS['POPUP_B']);v.standard_spill([a,a],engine.COLORS)
  a.putpixel((1,1),(0,0,0));self.rejects(v.standard_spill,[a,a],engine.COLORS)
 def test_rgb_sha_applied(self):
  a=Image.new('RGB',(20,20));b=a.copy();b.putpixel((19,19),(0,0,1));self.rejects(v.rgb,a,b);self.rejects(v.rgb,a,a,True)
  self.rejects(v.evidence_identity,dict(status='PASS'),'CORE');self.rejects(v.evidence_identity,dict(binary_sha256='old',measurement_kind='raw'),'CORE');self.rejects(v.applied,[0,0],[0,0],[0,0],'pending')
 def test_saved_real_temporal_phases(self):
  r=saved_raw();d=HIST/'E6/run';raw=(d/'owner.log').read_text();serial=r['held']['serial'];wire=re.search(rf'[^\n]*xdg_surface#\d+\.ack_configure\({serial}\)',raw);cut=raw.index('COMMAND hold_next_configure DONE');before=raw[:cut]
  sv.held_configure(before,raw[cut:wire.start()],30)
  self.rejects(sv.held_configure,before,raw[cut:],30)
  self.rejects(sv.released_configure,r['held'],raw,r['live']['ack_ns']+1,r['natural_capture_ns'])
  self.rejects(sv.released_configure,r['held'],raw,r['live']['release_ns'],r['live']['release_ns']+1)
  self.rejects(sv.released_configure,r['held'],raw,r['live']['release_ns'],r['natural_capture_ns'],False)
  self.rejects(sv.timeout_line,(d/'compositor.log').read_text(),-1,False,r['request_ns'],r['natural_capture_ns'],r['live']['release_ns'])
 def test_normal_closure_separate(self):
  good='CLOSE_RECEIVED\nSHM_CLOSURE created=2 released=2\nEXIT error=0';v.client_exit(good,0)
  for bad in (good.replace('released=2','released=1'),good.replace('CLOSE_RECEIVED',''),good.replace('error=0','error=32')):self.rejects(v.client_exit,bad,0)
 def closure_main(self,bad=None,archived=False,exited=False,scenario_failure=False):
  # WHY: predicate-only tests missed main's success surviving normal_remaining.
  # CONTRACT: run the real main -> normal_remaining -> Session.cleanup offline.
  # INVARIANT: fake I/O never launches a compositor or consumes a reservation.
  import tempfile,time,threading,io
  from pathlib import Path
  from types import SimpleNamespace
  from unittest.mock import Mock
  good='CLOSE_RECEIVED\nSHM_CLOSURE created=2 released=2\nEXIT error=0'
  class Process:
   def __init__(self,pid,done=False):self.pid=pid;self.returncode=0 if done else None;self.stdin=io.StringIO()
   def poll(self):return self.returncode
   def wait(self,timeout=None):self.returncode=0;return 0
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);s=engine.Session.__new__(engine.Session)
   s.spec=RUNS['S4-core-vertical'];s.auth={};s.run=root/'run';s.run.mkdir();s.runtime=root/'runtime';s.runtime.mkdir()
   s.closed=[];s.handles=[];s.events=[];s.started=time.monotonic();s.finished=threading.Event();s.expired=False;s.pointer=None;s.env={}
   s.watch=Mock();s.sock=Mock();s.sock.is_socket.return_value=True
   s.comp=Process(999999991);s.proc={'compositor':s.comp,'reference':Process(999999992,exited)}
   (s.run/'reference.log').write_text(good if archived else bad or good);s.start=Mock();s.find=Mock(return_value=None);s.debit=Mock()
   def campaign(session):
    if archived:
     old=Process(999999993);s.proc['owner']=old;(s.run/'owner.log').write_text(bad)
     try:s.close_client('owner')
     except engine.Ambiguous:pass
     s.proc['owner']=Process(999999994);(s.run/'owner.log').write_text(good)
    if scenario_failure:raise ValueError('scenario failed')
    return 'PASS'
   def terminal(*args,**kwargs):s.comp.returncode=0;return SimpleNamespace(returncode=0,stdout='',stderr='')
   with patch.object(run,'begin',return_value={}),patch.object(run,'Session',return_value=s),patch.object(run.cases,'popup_campaign',side_effect=campaign),patch('sys.argv',['run.py','S4-core-vertical']),patch.object(engine.subprocess,'run',side_effect=terminal),patch.object(engine.os,'killpg',side_effect=ProcessLookupError),patch('builtins.print'):
    result=run.main()
   return result,json.loads((s.run/'outcome.json').read_text())
 def test_main_normal_remaining_closure_failure(self):
  bad='CLOSE_RECEIVED\nSHM_CLOSURE created=2 released=1\nEXIT error=0'
  result,out=self.closure_main(bad)
  self.assertEqual(result,1);self.assertEqual(out['status'],'INCONCLUSIVE');self.assertEqual(out['scientific_cleanup'],'INCONCLUSIVE');self.assertEqual(out['mechanical_cleanup'],'PASS')
  self.assertIn('SHM release',out['failure']);self.assertEqual(out['explicit_client_closures'][0]['status'],'INCONCLUSIVE')
 def test_main_normal_close_success_control(self):
  result,out=self.closure_main();self.assertEqual(result,0);self.assertEqual(out['status'],'PASS');self.assertEqual(out['scientific_cleanup'],'PASS');self.assertEqual(out['mechanical_cleanup'],'PASS')
 def test_main_archived_same_name_failure(self):
  result,out=self.closure_main('CLOSE_RECEIVED\nSHM_CLOSURE created=2 released=1\nEXIT error=0',archived=True)
  self.assertEqual(result,1);self.assertIsNone(out['failure']);self.assertEqual(out['scientific_cleanup'],'INCONCLUSIVE');self.assertEqual(out['mechanical_cleanup'],'PASS')
  owners=[c for c in out['explicit_client_closures'] if c['name']=='owner'];self.assertEqual([c['status'] for c in owners],['INCONCLUSIVE','PASS']);self.assertNotEqual(owners[0]['pid'],owners[1]['pid'])
 def test_main_already_exited_client_validated(self):
  for bad in ('SHM_CLOSURE created=2 released=2\nEXIT error=0','CLOSE_RECEIVED\nSHM_CLOSURE created=2 released=1\nEXIT error=0'):
   result,out=self.closure_main(bad,exited=True);self.assertEqual(result,1);self.assertEqual(out['scientific_cleanup'],'INCONCLUSIVE');self.assertEqual(len(out['client_closures']),1)
 def test_main_scenario_failure_never_success(self):
  result,out=self.closure_main(scenario_failure=True);self.assertEqual(result,1);self.assertEqual(out['status'],'INCONCLUSIVE');self.assertEqual(out['scientific_cleanup'],'PASS');self.assertIn('scenario failed',out['failure'])
 def test_budgets(self):
  self.assertEqual([r['capture_limit'] for r in RUNS.values()],[12,12,18,12,12,14,14,14,12]);self.assertEqual(sum(r['capture_limit'] for r in RUNS.values()),120)
 def test_historical_raw_replay(self):self.assertEqual(replay()['status'],'PASS')
if __name__=='__main__':unittest.main(verbosity=2)
