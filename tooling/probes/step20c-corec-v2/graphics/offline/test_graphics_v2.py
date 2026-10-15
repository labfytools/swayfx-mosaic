"""OFFLINE_TEST_ONLY: actual runtime modules, synthetic protocol/tree/process I/O.
No old raw evidence, client execution, compositor, IPC or real budget access.
"""
import copy,io,json,os,re,resource,shutil,sys,tempfile,threading,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
LAB=Path(os.environ["SMX_TEST_LAB"]).resolve() if "SMX_TEST_LAB" in os.environ else Path(__file__).resolve().parents[2]
KIT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(KIT))
import gate,plans,validators as v,saved_validators as sv,geometry,engine,cases,run,evidence
from ipc_predicates import ancestry

class V2(unittest.TestCase):
 def rejects(self,fn,*args,**kw):
  with self.assertRaises((ValueError,AssertionError,RuntimeError)):fn(*args,**kw)
 def setUp(self):
  root=Path(os.environ.get("SMX_OFFLINE_SCRATCH",str(LAB/"graphics-tests/OFFLINE_TEST_ONLY")));root.mkdir(parents=True,exist_ok=True)
  self.temp=tempfile.TemporaryDirectory(dir=root);self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
 def fixture(self):
  source=self.root/"source";source.mkdir();(source/"input.py").write_text("# synthetic source binding\n")
  binary=self.root/"binary";binary.write_bytes(b"OFFLINE_TEST_ONLY not executable")
  auth=dict(binary=str(binary),binary_sha256=gate.sha(binary),wlroots="/usr/lib/libwlroots-0.20.so",wlroots_sha256=gate.WL_SHA,build_review="ACCEPTED",source_qualification="ACCEPTED")
  kit_manifest=self.root/"kit-manifest.json"
  manifest=self.root/"inputs.json";review=self.root/"review.json";publication=self.root/"publication.json"
  m=dict(schema="graphics-v2-frozen-inputs",ticket=gate.TICKET,lab=str(LAB),author="offline-author",source_root=str(source),files={"input.py":gate.sha(source/"input.py")},limits=plans.LIMITS,plans=plans.RUNS,identities=dict(core=auth,pristine=auth))
  def seal():
   gate.durable(kit_manifest,dict(ticket=gate.TICKET,source_root=str(source),files=m["files"],source_commit="f"*40))
   m.update(kit_manifest=str(kit_manifest),kit_manifest_sha256=gate.sha(kit_manifest))
   gate.durable(manifest,m);gate.durable(review,dict(decision="ACCEPTED",independent=True,reviewer="offline-reviewer",manifest_sha256=gate.sha(manifest),authorized_runs=list(plans.RUNS)))
   gate.durable(publication,dict(ticket=gate.TICKET,decision="VERIFIED",source_digest=gate.digest(m["files"]),origin_sha="f"*40,github_sha="f"*40,offline_test_only=True,kit_manifest_sha256=gate.sha(kit_manifest),source_commit="f"*40))
  seal();ledger=gate.Ledger(LAB,self.root/"budget.json",offline=True);ledger.initialize()
  return ledger,manifest,review,publication,m,seal
 def tree(self):
  owner=dict(id=40,pid=100,type="con",floating=None,nodes=[],floating_nodes=[],fullscreen_mode=0)
  branch=dict(id=30,type="con",floating=None,nodes=[owner],floating_nodes=[],fullscreen_mode=0)
  ws=dict(id=20,type="workspace",name="1",output="HEADLESS-1",layout="mosaic",floating=None,nodes=[branch],floating_nodes=[])
  out=dict(id=10,type="output",name="HEADLESS-1",floating=None,nodes=[ws],floating_nodes=[])
  root=dict(id=1,type="root",nodes=[out],floating_nodes=[])
  return root,owner,ancestry(root,40)
 def test_caps_and_non_admitted(self):
  self.assertEqual(len(plans.RUNS),14);self.assertEqual(sum(plans.CAPS.values()),170)
  self.assertEqual(max(plans.CAPS.values()),18)
  l,m,r,p,_,_=self.fixture()
  for rid in ("P1","C8","O1","O2","G2","R1"):self.rejects(l.admit,rid,m,r,p)
  self.assertEqual(json.loads(l.path.read_text())["runs"],[])
 def test_real_gate_consumption_token_caps_completion(self):
  l,m,r,p,_,_=self.fixture();auth=l.admit("C1",m,r,p)
  self.rejects(l.admit,"C1",m,r,p);self.rejects(l.initialize)
  self.rejects(l.action_debit,dict(auth,token="stale"),"capture")
  for _ in range(18):l.action_debit(auth,"capture")
  before=l.path.read_bytes();self.rejects(l.action_debit,auth,"capture");self.assertEqual(before,l.path.read_bytes())
  l.complete(auth,dict(status="INCONCLUSIVE",runner_exit=1));self.rejects(l.action_debit,auth,"move");self.rejects(l.complete,auth,{})
 def test_global_and_per_action_debits_atomic(self):
  l,m,r,p,_,_=self.fixture();auth=l.admit("C2",m,r,p)
  for _ in range(plans.RUNS["C2"]["action_limits"]["grab"]):l.action_debit(auth,"grab")
  before=l.path.read_bytes();self.rejects(l.action_debit,auth,"move","grab");self.assertEqual(before,l.path.read_bytes())
  def fill(d):
   d["runs"]=[dict(id="used"+str(i),capture_limit=18) for i in range(10)];return None,d
  l.transaction(fill);self.rejects(l.admit,"C1",m,r,p)
 def test_source_review_binary_and_publication_bindings(self):
  l,m,r,p,data,seal=self.fixture();auth=l.admit("C1",m,r,p)
  source=Path(data["source_root"])/"input.py";old=source.read_bytes();source.write_bytes(b"changed")
  self.rejects(l.action_debit,auth,"move");source.write_bytes(old)
  binary=Path(auth["binary"]);old=binary.read_bytes();binary.write_bytes(b"changed");self.rejects(l.action_debit,auth,"move");binary.write_bytes(old)
  rr=json.loads(r.read_text());rr["reviewer"]="different";gate.durable(r,rr);self.rejects(l.action_debit,auth,"move");seal()
  pp=json.loads(p.read_text());pp["github_sha"]="e"*40;gate.durable(p,pp);self.rejects(l.action_debit,auth,"move");seal()
  data["ticket"]="OLD_TICKET";seal();self.rejects(l.action_debit,auth,"move")
 def test_fullkit_publication_source_binding(self):
  l,m,r,p,data,seal=self.fixture();auth=l.admit("C1",m,r,p)
  km=Path(data["kit_manifest"]);km.write_text("{}")
  self.rejects(l.action_debit,auth,"move")
  seal();pub=json.loads(p.read_text());pub["source_commit"]="a"*40;gate.durable(p,pub)
  self.rejects(l.action_debit,auth,"move")
 def test_old_lab_uid_limits_lock_symlink_and_source_addition(self):
  l,m,r,p,data,seal=self.fixture()
  data["lab"]="/var/tmp/old-lab";seal();self.rejects(l.admit,"C1",m,r,p);data["lab"]=str(LAB);seal()
  new=Path(data["source_root"])/"unreviewed.py";new.write_text("new");self.rejects(l.admit,"C1",m,r,p);new.unlink()
  data["identities"]["core"]["wlroots_sha256"]="bad";seal();self.rejects(l.admit,"C1",m,r,p)
  d=json.loads(l.path.read_text());d["limits"]["runs"]=15;gate.durable(l.path,d);self.rejects(l.admit,"C1",m,r,p)
  other=self.root/"other";other.write_text("");l.lock.unlink();l.lock.symlink_to(other)
  with self.assertRaises(OSError):l.transaction(lambda d:(None,d))
 def test_environment_and_socket_paths(self):
  with patch.dict(os.environ,{k:"daily" for k in ("DISPLAY","WAYLAND_DISPLAY","SWAYSOCK","XDG_RUNTIME_DIR","LD_PRELOAD","LD_LIBRARY_PATH","WLR_BACKENDS","EGL_PLATFORM","DBUS_SESSION_BUS_ADDRESS")}):
   env=gate.clean_environment(LAB);self.assertNotIn("SWAYSOCK",env);self.assertNotIn("LD_PRELOAD",env);self.assertEqual(env["TMPDIR"],str(LAB/"scratch"))
  s=engine.Session.__new__(engine.Session);s.runtime=Path("/tmp/smx-offline");s.sock=Path("/tmp/daily.sock");s.record=Mock();s.env={}
  with patch.object(engine.subprocess,"run") as launch:
   self.rejects(s.ipc,"exit");launch.assert_not_called()
  self.rejects(engine.Session,plans.RUNS["C1"],dict(offline=True))
 def test_spawn_wraps_argv_and_records_requested_and_actual(self):
  s=engine.Session.__new__(engine.Session);s.run=self.root;s.handles=[];s.proc={};s.expired=False;s.env={};s.debit=Mock();s.record=Mock()
  child=Mock(pid=12345);requested=[sys.executable,"-c","pass"]
  with patch.object(engine.shutil,"which",return_value="/usr/bin/prlimit"),patch.object(engine.subprocess,"Popen",return_value=child) as popen:
   self.assertIs(s.spawn("mocked",requested),child)
  argv=popen.call_args.args[0]
  self.assertEqual(argv,["/usr/bin/prlimit","--core=0:0","--",*requested])
  event=s.record.call_args
  self.assertEqual(event.kwargs["requested_argv"],requested)
  self.assertEqual(event.kwargs["actual_argv"],argv)
  self.assertEqual(event.args[0],"spawn")
 def test_spawn_real_non_graphic_child_core_limit_and_parent_unchanged(self):
  prlimit=shutil.which("prlimit")
  self.assertIsNotNone(prlimit,"util-linux prlimit required")
  parent_limit=resource.getrlimit(resource.RLIMIT_CORE)
  s=engine.Session.__new__(engine.Session);s.run=self.root;s.handles=[];s.proc={};s.expired=False;s.env={};s.debit=Mock();s.events=[]
  s.record=lambda kind,**fields:s.events.append(dict(kind=kind,**fields))
  code="import json,os,resource; print(json.dumps({'pid':os.getpid(),'core':resource.getrlimit(resource.RLIMIT_CORE)}))"
  child=s.spawn("corelimit-child",[sys.executable,"-c",code])
  self.assertEqual(child.wait(timeout=5),0)
  observed=json.loads((self.root/"corelimit-child.log").read_text())
  self.assertEqual(observed["core"],[0,0])
  self.assertEqual(observed["pid"],child.pid)
  self.assertEqual(resource.getrlimit(resource.RLIMIT_CORE),parent_limit)
  event=s.events[0]
  self.assertEqual(event["requested_argv"],[sys.executable,"-c",code])
  self.assertEqual(event["actual_argv"][:3],[prlimit,"--core=0:0","--"])
 def test_watchdog_autonomous_kill_term_resistant_private_group(self):
  import signal,subprocess
  s=engine.Session.__new__(engine.Session);s.run=self.root;s.handles=[];s.proc={};s.proc_lock=threading.RLock();s.expired=False;s.env={};s.debit=Mock();s.record=Mock();s.finished=threading.Event()
  code="import os,signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); print('READY',flush=True); time.sleep(30)"
  p=s.spawn('resistant',[sys.executable,'-c',code])
  self.addCleanup(lambda:p.poll() is None and os.killpg(p.pid,signal.SIGKILL))
  end=time.monotonic()+3
  while 'READY' not in (self.root/'resistant.log').read_text() and time.monotonic()<end:time.sleep(.01)
  self.assertIn('READY',(self.root/'resistant.log').read_text())
  self.assertEqual(os.getpgid(p.pid),p.pid)
  # Simulate the last seconds; no main cleanup is called to rescue the watchdog.
  s.started=time.monotonic()-143.1;start=time.monotonic()
  watch=threading.Thread(target=s.watchdog);watch.start();watch.join(timeout=4)
  self.assertFalse(watch.is_alive());self.assertEqual(p.wait(timeout=1),-signal.SIGKILL)
  self.assertTrue(s.expired);self.assertLess(time.monotonic()-start,3)
  self.assertLess(time.monotonic()-s.started,147)
  with self.assertRaises(ProcessLookupError):os.killpg(p.pid,0)
  p.stdin.close()
  for h in s.handles:h.close()
 def test_watchdog_expired_registration_cannot_launch(self):
  s=engine.Session.__new__(engine.Session);s.run=self.root;s.handles=[];s.proc={};s.proc_lock=threading.RLock();s.expired=False;s.env={};s.record=Mock()
  # Expiry occurs after the first check, during the debit, before atomic spawn.
  s.debit=lambda *_:setattr(s,'expired',True)
  with patch.object(engine.subprocess,'Popen') as launch:
   self.rejects(s.spawn,'late',[sys.executable,'-c','pass']);launch.assert_not_called()
 def test_close_wait_uses_absolute_deadline(self):
  s=engine.Session.__new__(engine.Session);s.started=time.monotonic()-145.5;s.proc={'owner':Mock()};s.proc['owner'].poll.return_value=None;s.closed=[];s.record=Mock();s.client_cmd=Mock()
  s.proc['owner'].wait.side_effect=engine.subprocess.TimeoutExpired('private',.5)
  with self.assertRaises(engine.subprocess.TimeoutExpired):s.close_client('owner')
  self.assertLessEqual(s.proc['owner'].wait.call_args.kwargs['timeout'],.5)
  self.assertEqual(s.closed[0]['status'],'INCONCLUSIVE')
 def dynamic_snapshot(self,width=800,scroll=1000,output='HEADLESS-1'):
  x=-width if output=='HEADLESS-1' else 0
  return dict(tree=dict(type='workspace',name='1',id=20,output=output,rect=dict(x=x,y=0,width=width,height=600),mosaic=dict(rows=[dict(children=[1,2,3],scroll_x=scroll)]),nodes=[dict(id=i+1,rect=dict(x=x+i*640,y=20,width=640,height=580)) for i in range(3)]))
 def test_dynamic_reconstructed_clamp_resize_migration_and_negatives(self):
  initial=cases.dynamic_geometry(self.dynamic_snapshot())
  resized=cases.dynamic_geometry(self.dynamic_snapshot(960,960),initial)
  self.assertEqual(resized['expected_scroll'],960);self.assertEqual(resized['minimum_width'],640)
  back=cases.dynamic_geometry(self.dynamic_snapshot(800,960),resized)
  moved=cases.dynamic_geometry(self.dynamic_snapshot(800,960,'HEADLESS-2'),back)
  self.assertEqual(moved['output'],'HEADLESS-2')
  self.rejects(cases.dynamic_geometry,self.dynamic_snapshot(960,1000),initial)
  for mutate in (lambda w:w['nodes'][0]['rect'].update(width=639),lambda w:w['nodes'][1]['rect'].update(x=123),lambda w:w['mosaic']['rows'][0].update(children=[3,2,1]),lambda w:w.update(id=21)):
   snap=self.dynamic_snapshot(960,960);mutate(snap['tree']);self.rejects(cases.dynamic_geometry,snap,initial)
 def test_dynamic_pixels_whole_h2_old_output_and_exclusion_negatives(self):
  from PIL import Image
  outputs=copy.deepcopy(plans.RUNS['C7']['outputs']);frames={o['name']:'logical' for o in outputs}
  baseline=Image.new('RGB',(800,600),(48,48,56));images=[baseline.copy(),baseline.copy()]
  images[0].putpixel((790,50),engine.COLORS['POPUP_B'])
  cases.dynamic_pixels(images,outputs,frames,[-800,0,800,600],baseline)
  images[1].putpixel((0,50),engine.COLORS['POPUP_B']);self.rejects(cases.dynamic_pixels,images,outputs,frames,[-800,0,800,600],baseline)
  images[1]=baseline.copy();images[1].putpixel((799,599),(0,0,1));self.rejects(cases.dynamic_pixels,images,outputs,frames,[-800,0,800,600],baseline)
  images[1]=baseline.copy();self.rejects(cases.dynamic_pixels,images,outputs,frames,[0,0,800,600])
  images[0]=baseline.copy();images[1].putpixel((1,50),engine.COLORS['POPUP_B']);cases.dynamic_pixels(images,outputs,frames,[0,0,800,600])

 def test_tree_tiled_branch_none_and_wrong_owner(self):
  tree,node,path=self.tree();ws=path[-3];self.assertTrue(v.camera_eligible(path,ws));v.owner_context(node,path,100,"1","HEADLESS-1","mosaic")
  self.rejects(v.owner_context,node,path,101,"1","HEADLESS-1","mosaic")
  self.rejects(v.owner_context,node,path,100,"1","HEADLESS-2","mosaic")
  self.rejects(v.owner_context,dict(node,id=999),path,100,"1","HEADLESS-1","mosaic")
  parent=path[-2];parent["nodes"].remove(node);parent["floating_nodes"].append(node)
  self.assertFalse(v.camera_eligible(path,ws));self.rejects(v.owner_context,node,path,100,"1","HEADLESS-1","mosaic")
 def test_wire_actual_button_grab_and_native_sizes(self):
  raw=(KIT/"wire-fixture.txt").read_text();proof=v.grab(raw)
  for bad in (raw.replace("origin=wl_pointer.button","origin=fake"),raw.replace("POPUP_B MAP ","BAD MAP "),raw.replace("used="+str(proof["grabs"][0]["serial"]),"used=999999"),re.sub(r"wl_pointer#\d+\.button\([^\n]+", "removed-wire-button",raw),re.sub(r"(create_buffer\(new id wl_buffer#\d+, 0, )\d+, \d+, \d+, 1\)",r"\g<1>999, 999, 3996, 1)",raw)):
   self.rejects(v.grab,bad)
  self.rejects(v.hidden_survival,raw,proof,[dict(action="left")]);v.hidden_survival(raw,proof,[dict(action="move")])
 def test_vertical_scaled_rotated_exact_rgb(self):
  v.crosses([50,505,350,170],1,600);self.rejects(v.crosses,[50,505,350,170],0,0)
  o=plans.RUNS["C2"]["outputs"][1];self.assertEqual(geometry.png_global((30,40),o,"logical"),[30,640])
  self.assertEqual(plans.RUNS["C3"]["outputs"][0]["mode"],[1000,750]);self.assertEqual(plans.RUNS["C4"]["outputs"][0]["transform"],"90")
  from PIL import Image
  a=Image.new("RGB",(20,20));b=a.copy();b.putpixel((19,19),(0,0,1));self.rejects(v.rgb,a,b);self.rejects(v.rgb,a,a,True);v.rgb(a,a)
 def test_saved_phase_actual_validator_and_closure(self):
  before="ACK ns=1 serial=10 size=640x480\nxdg_surface#1.ack_configure(10)\nwl_shm_pool#4.create_buffer(\nCOMMIT ns=2\n"
  held="HELD ns=100 serial=11\nxdg_surface#1.configure(11)\nXDG_CONFIGURE ns=100 serial=11 size=580x420 hold=1\n"
  proof=sv.held_configure(before,held,10)
  after=held+"xdg_surface#1.ack_configure(11)\nACK ns=400 serial=11\nCOMMIT ns=401 serial=11\n"
  sv.released_configure(proof,after,300,200);self.rejects(sv.held_configure,before,after,10);self.rejects(sv.released_configure,proof,after,500,200)
  good="CLOSE_RECEIVED\nSHM_CLOSURE created=2 released=2\nEXIT error=0";v.client_exit(good,0)
  for bad in (good.replace("released=2","released=1"),good.replace("error=0","error=32"),good.replace("CLOSE_RECEIVED","")):self.rejects(v.client_exit,bad,0)
 def test_no_fake_present_or_fullscreen(self):
  tree,node,path=self.tree();self.rejects(v.fullscreen_ancestor,path)
  event=dict(run="C1",output="HEADLESS-1",commit_seq=1,native_event=True,source="native-output-commit")
  present=dict(event,source="native-output-present");self.assertEqual(evidence.native_present([event],[present])["matched"],1)
  self.rejects(evidence.native_present,[event],[dict(present,native_event=False)])
  self.rejects(evidence.native_present,[event],[dict(present,run="C2")])
  path[-2]["fullscreen_mode"]=1;path[-2]["nodes"].append(dict(id=41))
  record=dict(owner_path=path,native_xdg=True,configure_ack=1,owner_id=40,configure=[800,600],child_configures=[[800,300],[800,300]],popup_A=[-10,0,350,170],popup_B=[-5,20,300,130],boundary=0)
  evidence.fullscreen_certificate(record,record)
  bad=copy.deepcopy(record);bad["popup_B"][0]=20;self.rejects(evidence.fullscreen_certificate,record,bad)
  bad=copy.deepcopy(record);bad["configure"]=[800,500];self.rejects(evidence.fullscreen_certificate,record,bad)
 def test_runner_dispatch_failures_and_no_launch_before_admission(self):
  # execute is the real dispatch/orchestration; only transport and ledger are fake.
  s=Mock();s.proc={};s.cleanup.side_effect=lambda status,failure:status
  ledger=Mock();ledger.admit.return_value={}
  with patch.object(run,"Ledger",return_value=ledger),patch.object(cases,"popup_campaign",return_value="PARTIALLY_FEASIBLE") as campaign:
   result=run.execute("C2",LAB,"m","r","p",session_factory=lambda *_:s)
   self.assertEqual(result["runner_exit"],0);campaign.assert_called_once_with(s);s.start.assert_called_once()
  s.reset_mock();s.start.side_effect=ValueError("source changed")
  with patch.object(run,"Ledger",return_value=ledger):
   result=run.execute("C2",LAB,"m","r","p",session_factory=lambda *_:s)
   self.assertEqual(result["runner_exit"],1);self.assertIn("source changed",result["failure"])
  ledger.admit.side_effect=ValueError("no review");factory=Mock()
  with patch.object(run,"Ledger",return_value=ledger):self.rejects(run.execute,"C2",LAB,"m","r","p",session_factory=factory)
  factory.assert_not_called()

 def closure_execute(self,bad=None,archived=False,exited=False,scenario_failure=False):
  good='CLOSE_RECEIVED\nSHM_CLOSURE created=2 released=2\nEXIT error=0'
  class Process:
   def __init__(self,pid,done=False):self.pid=pid;self.returncode=0 if done else None;self.stdin=io.StringIO()
   def poll(self):return self.returncode
   def wait(self,timeout=None):self.returncode=0;return 0
  s=engine.Session.__new__(engine.Session);s.spec=plans.RUNS['C2'];s.auth={};s.ledger=Mock()
  s.run=self.root/'run';s.run.mkdir();s.runtime=self.root/'runtime';s.runtime.mkdir()
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
   return 'PARTIALLY_FEASIBLE'
  def terminal(*args,**kwargs):s.comp.returncode=0;return SimpleNamespace(returncode=0,stdout='',stderr='')
  with patch.object(run,'Ledger',return_value=Mock()),patch.object(cases,'popup_campaign',side_effect=campaign),patch.object(engine.subprocess,'run',side_effect=terminal),patch.object(engine.os,'killpg',side_effect=ProcessLookupError):
   result=run.execute('C2',LAB,'m','r','p',session_factory=lambda *_:s)
  return result,json.loads((s.run/'outcome.json').read_text())
 def test_actual_session_normal_scientific_mechanical_close(self):
  result,out=self.closure_execute();self.assertEqual(result['runner_exit'],0);self.assertEqual(out['scientific_cleanup'],'PASS');self.assertEqual(out['mechanical_cleanup'],'PASS')
 def test_actual_session_shm_failure_not_laundered(self):
  result,out=self.closure_execute('CLOSE_RECEIVED\nSHM_CLOSURE created=2 released=1\nEXIT error=0')
  self.assertEqual(result['runner_exit'],1);self.assertEqual(out['scientific_cleanup'],'INCONCLUSIVE');self.assertEqual(out['mechanical_cleanup'],'PASS');self.assertIn('SHM release',out['failure'])
 def test_actual_session_archived_same_name_failure(self):
  result,out=self.closure_execute('CLOSE_RECEIVED\nSHM_CLOSURE created=2 released=1\nEXIT error=0',archived=True)
  self.assertEqual(result['runner_exit'],1);owners=[c for c in out['client_closures'] if c['name']=='owner'];self.assertEqual([c['status'] for c in owners],['INCONCLUSIVE','PASS'])
 def test_actual_session_already_exited_invalid_client(self):
  result,out=self.closure_execute('SHM_CLOSURE created=2 released=2\nEXIT error=0',exited=True)
  self.assertEqual(result['runner_exit'],1);self.assertEqual(out['scientific_cleanup'],'INCONCLUSIVE')
 def test_actual_session_scenario_failure(self):
  result,out=self.closure_execute(scenario_failure=True);self.assertEqual(result['runner_exit'],1);self.assertEqual(out['scientific_cleanup'],'PASS');self.assertIn('scenario failed',out['failure'])
 def test_open_chain_selects_and_checks_before_and_after_spawn(self):
  session=Mock();session.spec=plans.RUNS['C1'];session.events=[]
  session.owner.side_effect=ValueError('wrong mapped H2 owner');session.snapshot.return_value={}
  with patch.object(v,'selected_workspace') as selected:
   self.rejects(cases.open_chain,session)
  self.assertEqual(session.cmd.call_args_list[0].args,('workspace 1',));self.assertEqual(session.cmd.call_args_list[1].args,('layout mosaic',));selected.assert_called_once();session.owner.assert_called_once_with('owner');session.click.assert_not_called()
 def test_actual_delivery_requires_press_wire_and_grab_serial(self):
  s=engine.Session.__new__(engine.Session)
  lines={'owner':['POINTER_BUTTON target=TOPLEVEL serial=20 button=272 state=1','POINTER_BUTTON target=TOPLEVEL serial=21 button=272 state=0']}
  tail={'owner':'POINTER_MOTION target=TOPLEVEL x=5 y=6\nwl_pointer#4.button(20, 10, 272, 1)\nwl_pointer#4.button(21, 11, 272, 0)'}
  s.delivery('owner',[100,200,40,40],[105,206],tail,lines,'TOPLEVEL',20)
  self.rejects(s.delivery,'owner',[100,200,40,40],[105,206],tail,lines,'TOPLEVEL',22)
  self.rejects(s.delivery,'owner',[100,200,40,40],[105,206],{'owner':'POINTER_MOTION target=TOPLEVEL x=5 y=6'},lines,'TOPLEVEL',20)
  self.rejects(s.delivery,'owner',[100,200,40,40],[105,206],tail,{'owner':lines['owner'][1:]},'TOPLEVEL',20)

 def quota_scenario(self,rid):
  # Actual open_chain/horizontal/standard-return handlers; replace measured I/O
  # and scientific predicates, never duplicate their action/capture sequencing.
  from PIL import Image
  from collections import Counter
  from contextlib import ExitStack
  class FakeSession:
   def __init__(self):
    self.spec=plans.RUNS[rid];self.outputs=copy.deepcopy(self.spec['outputs']);self.frames={o['name']:'logical' for o in self.outputs};self.actions=Counter();self.events=[];self.proc={};self.sequence=0;self.tag='';self.closed=[];self.scroll_x=0;self.expected_output='HEADLESS-1';self.auth={};self.comp=SimpleNamespace(pid=999999995)
   def debit(self,*kinds):
    self.actions.update(kinds)
    for k in kinds:
     cap=self.spec['capture_limit'] if k=='capture' else self.spec['action_limits'][k]
     if self.actions[k]>cap:raise ValueError('actual handler quota '+k)
   def cmd(self,command,business=False):
    self.debit('mutation' if business else 'configuration')
    if command.startswith('move workspace to output '):self.expected_output=command.split()[-1]
   def launch_client(self,name,*args):
    self.debit('spawn');self.sequence+=1;self.events.append(dict(kind='spawn',name=name));self.proc[name]=SimpleNamespace(pid=self.sequence,poll=lambda:None,returncode=0)
   def find(self,name):return dict(id=self.proc[name].pid,pid=self.proc[name].pid)
   def owner(self,name):
    n=self.find(name);n.update(window_rect=dict(width=640,height=575));return dict(owner=n,origin=[-320-self.scroll_x,0],scene=[-320-self.scroll_x,0,640,575],workspace=dict(id=20,output=self.expected_output),evidence='synthetic quota only',snapshot={})
   calibrate=owner
   def snapshot(self,tag):return dict(tree=dict(type='workspace',name='1',id=20,output=self.expected_output,mosaic=dict(rows=[dict(children=[1,2,3])]),nodes=[]))
   def log(self,name):
    if rid=='C6':
     if name=='compositor':return 'Transaction 1 timed out (1 waiting)'
     return 'ACK ns=1 serial=10 size=640x480\nCOMMIT ns=2 serial=10 size=640x480 color=303038\nHELD ns=3 serial=11\nACK ns=9 serial=11'
    return (KIT/'wire-fixture.txt').read_text()
   def capture(self,tag,out):
    self.debit('capture');self.tag=tag;image=Image.new('RGB',(800,600),(48,48,56));image.info['tag']=tag;return image
   def pair_capture(self,tag):return [self.capture(tag+'-H1','HEADLESS-1'),self.capture(tag+'-H2','HEADLESS-2')]
   def inject(self,action,point,grab=False):
    self.debit('move',*(['click'] if action!='move' else []),*(['grab'] if grab else []));self.events.append(dict(kind='injection',action=action,ns=time.monotonic_ns()))
   def scroll(self,name,delta):self.debit('camera');self.cmd('synthetic scroll');self.scroll_x+=delta
   def click(self,name,point,action='right',grab=False):self.inject(action,point,grab);return {'owner':''},{'owner':[]}
   def delivery(self,*args):pass
   def wait(self,*args,**kwargs):
    if rid=='C6' and kwargs.get('seconds')==6:clock[0]+=5_000_000_000
   def save(self,*args,**kwargs):pass
   def close_client(self,*args):self.debit('configuration')
   def client_cmd(self,*args):self.debit('configuration')
  s=FakeSession();geo=dict(A=[-20,50,350,170],B=[-10,100,300,130])
  if rid=='C2':geo=dict(A=[50,570,250,170],B=[70,590,170,130])
  prot=v.grab((KIT/'wire-fixture.txt').read_text())
  def counts(image,color):
   if 'final' in image.info['tag'] or 'fully-hidden' in image.info['tag'] or image.info['tag']=='migrated-H2-H1':return 0
   if 'B-closed' in image.info['tag'] and color==engine.COLORS['POPUP_B']:return 0
   return 1
  clock=[100_000_000]
  with ExitStack() as stack:
   for module,name,value in [(cases,'geometry',lambda *_:geo),(cases,'solid_point',lambda *_:[-250,100]),(run,'solid_point',lambda *_:[-250,100]),(cases,'count',counts),(run,'count',counts),(cases,'exact',lambda *_:True),(v,'selected_workspace',lambda *_:None),(v,'crosses',lambda *_:None),(v,'standard_spill',lambda *_:None),(v,'rgb',lambda *_:True),(cases,'dismissal',lambda *_:dict(status='synthetic quota only'))]:stack.enter_context(patch.object(module,name,side_effect=value))
   import lifecycle
   for name in ('explicit_child_close','a_survival','normal_owner_close'):stack.enter_context(patch.object(lifecycle,name))
   stack.enter_context(patch.object(time,'sleep'))
   if rid=='C1':run.horizontal(s)
   elif rid=='C6':
    import saved
    def tick():clock[0]+=100_000_000;return clock[0]
    stack.enter_context(patch.object(saved.time,'monotonic_ns',side_effect=tick))
    stack.enter_context(patch.object(saved.Path,'read_bytes',return_value=b'compositor\0-Dtxn-timeout=5000\0'))
    stack.enter_context(patch.object(saved,'pending_geometry',return_value=dict(held=dict(ns=1,serial=11))))
    stack.enter_context(patch.object(saved,'held_configure',return_value=dict(ns=1,serial=11)))
    stack.enter_context(patch.object(saved,'timeout_line',return_value='synthetic quota only'))
    stack.enter_context(patch.object(saved,'released_configure',return_value=dict(status='synthetic quota only')))
    saved.run(s)
   elif rid=='C5':cases.hidden_campaign(s)
   elif rid=='C7':
    candidate=dict(workspace_id=20,output='HEADLESS-1',children=[1,2,3],viewport=[-800,0,800,600],scroll=0)
    def dynamic_candidate(*args):
     return dict(candidate,output=s.expected_output,viewport=next(o['logical'] for o in s.outputs if o['name']==s.expected_output))
    stack.enter_context(patch.object(cases,'dynamic_geometry',side_effect=dynamic_candidate))
    stack.enter_context(patch.object(cases,'dynamic_pixels',return_value=dict(status='synthetic quota only')))
    s.owner=lambda name:dict(owner=dict(id=s.find(name)['id'],window_rect=dict(width=640,height=575)),origin=[-320,0],workspace=dict(id=20,output=s.expected_output),scene=[-320,0,640,575],snapshot={},evidence='synthetic quota only')
    cases.dynamic_campaign(s)
   elif rid=='P0':
    cases.init_reference(s);state,baseline,p,g,left,right=cases.open_chain(s);run.standard_return(s,state,baseline,p,g,[left,right])
   else:cases.popup_campaign(s)
  return dict(s.actions)
 def test_actual_p0_c1_handlers_capture_and_action_caps(self):
  self.assertEqual(self.quota_scenario('P0')['capture'],10)
  self.assertEqual(self.quota_scenario('C1')['capture'],16)
 def test_actual_saved_handler_capture_caps(self):
  self.assertEqual(self.quota_scenario('C6')['capture'],10)
 def test_actual_hidden_dynamic_handlers_capture_caps(self):
  self.assertEqual(self.quota_scenario('C5')['capture'],12)
  self.assertEqual(self.quota_scenario('C7')['capture'],14)
 def test_actual_other_popup_handlers_capture_caps(self):
  self.assertEqual(self.quota_scenario('C2')['capture'],8)
  self.assertEqual(self.quota_scenario('C3')['capture'],8)
  self.assertEqual(self.quota_scenario('C4')['capture'],8)
  # Their real Session.start adds exactly one calibrated-marker screenshot.

 def test_marker_helper_is_reaped_separate_from_shm_client_closure(self):
  s=engine.Session.__new__(engine.Session);s.helper_exits=[];s.record=Mock();p=Mock();p.pid=999999996;p.poll.return_value=None;p.wait.return_value=-15;p.stdin=io.StringIO();s.proc={'marker-background':p}
  with patch.object(engine.os,'killpg') as kill:s.close_helper('marker-background')
  kill.assert_called_once_with(p.pid,engine.signal.SIGTERM);p.wait.assert_called_once_with(timeout=2)
  self.assertEqual(s.proc,{});self.assertEqual(s.helper_exits[0]['exit'],-15);self.assertFalse(s.helper_exits[0]['scientific_client'])

if __name__=="__main__":unittest.main(verbosity=2)
