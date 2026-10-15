"""OFFLINE_TEST_ONLY. Real handlers with fake I/O; no compositor/IPC/client execution."""
import copy,io,json,os,sys,time,unittest
from collections import Counter
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cases,engine,fullscreen,gate,oom,oom_handler,plans,run
from test_graphics_v2 import V2,LAB,KIT
from PIL import Image

class Next(unittest.TestCase):
 setUp=V2.setUp
 fixture=V2.fixture
 rejects=V2.rejects
 dynamic_snapshot=V2.dynamic_snapshot
 def test_migration_focus_reveal_distinct_from_resize(self):
  previous=cases.dynamic_geometry(self.dynamic_snapshot(800,800))
  moved=self.dynamic_snapshot(800,1120,'HEADLESS-2');moved['tree']['nodes'][2]['focused']=True
  current=cases.dynamic_geometry(moved,previous,'migration');self.assertEqual(current['expected_scroll'],1120)
  self.rejects(cases.dynamic_geometry,moved,previous,'resize')
  wrong=copy.deepcopy(moved);wrong['tree']['mosaic']['rows'][0]['scroll_x']=800
  self.rejects(cases.dynamic_geometry,wrong,previous,'migration')
  wrong=copy.deepcopy(moved);wrong['tree']['nodes'][2]['focused']=False
  self.rejects(cases.dynamic_geometry,wrong,previous,'migration')
 def test_fullscreen_group_and_comparability_negatives(self):
  state,peer,group=self.state();fullscreen.group_candidate(state,peer,group)
  for change in (lambda g:g.update(fullscreen_mode=0),lambda g:g['nodes'][0].update(fullscreen_mode=1),lambda g:g['nodes'].pop(),lambda g:g['nodes'][0]['rect'].update(width=399)):
   bad=copy.deepcopy(state);g=bad['snapshot']['tree']['nodes'][0];change(g)
   if g.get('nodes') and g['nodes'][0].get('fullscreen_mode'):g['fullscreen_mode']=0
   self.rejects(fullscreen.group_candidate,bad,peer,group)
  exited=copy.deepcopy(state);eg=exited['snapshot']['tree']['nodes'][0];eg['fullscreen_mode']=0
  eg['nodes'][0]['rect'].update(x=-400);eg['nodes'][1]['rect'].update(x=-800)
  exited['origin']=[-398,25];exited['owner']['rect'].update(x=-400)
  fullscreen.group_candidate(exited,peer,group,fullscreen=False)
  still_full=copy.deepcopy(exited);still_full['snapshot']['tree']['nodes'][0]['fullscreen_mode']=1
  self.rejects(fullscreen.group_candidate,still_full,peer,group,fullscreen=False)
  raw=(KIT/'wire-fixture.txt').read_text();protocol=fullscreen.validators.grab(raw)
  fresh=fullscreen.fresh_geometry(SimpleNamespace(log=lambda _name:raw),exited,protocol)
  self.assertEqual(fresh['A'],[-348,505,250,170]);self.assertEqual(fresh['B'],[-328,585,170,130])
  record=dict(client_sha256='offline-client',fresh=True,crossing_A=True,crossing_B=True,roles='TOPLEVEL -> POPUP_A -> POPUP_B',top_configure=['400','575'],child_rects=[1,2],group_rect=[-800,0,800,600],popup_A=[-448,105,900,170],popup_B=[-348,165,900,130],configured_A=[350,80,900,170],configured_B=[100,60,900,130],origin=[-798,25],outputs=plans.RUNS['P1']['outputs'])
  fullscreen.comparable(record,copy.deepcopy(record))
  for key,value in [('fresh',False),('crossing_A',False),('crossing_B',False),('top_configure',['420','320']),('popup_A',[10,105,900,170]),('roles','fake')]:
   bad=copy.deepcopy(record);bad[key]=value;self.rejects(fullscreen.comparable,record,bad)
 def test_fullscreen_expected_whole_h2_field(self):
  from PIL import Image,ImageDraw
  colors=engine.COLORS;output=copy.deepcopy(plans.RUNS['P1']['outputs'][1]);baseline=Image.new('RGB',(800,600),(48,48,56))
  g=dict(origin=[-798,25],configured_A=[350,80,900,170],configured_B=[100,60,900,130],A=[-448,105,900,170],B=[-348,165,900,130],crossing=dict(A=True,B=True))
  def field(geometry=g,out=output):
   expected=baseline.copy();draw=ImageDraw.Draw(expected)
   for key,name in (('A','POPUP_A'),('B','POPUP_B')):
    x,y,w,h=geometry[key];draw.rectangle((max(0,x),max(0,y),min(799,x+w-1),min(599,y+h-1)),fill=colors[name])
   return [baseline.copy(),expected]
  good=field();fullscreen.fullscreen_h2_field(good,baseline,g,output,'logical',colors)
  wrong=field();wrong[1].putpixel((799,599),colors['POPUP_A']);wrong[1].putpixel((798,599),colors['POPUP_B']);self.rejects(fullscreen.fullscreen_h2_field,wrong,baseline,g,output,'logical',colors)
  missing=field();missing[1].putpixel((1,110),baseline.getpixel((1,110)));self.rejects(fullscreen.fullscreen_h2_field,missing,baseline,g,output,'logical',colors)
  displaced=copy.deepcopy(g);displaced['A'][0]+=1;self.rejects(fullscreen.fullscreen_h2_field,good,baseline,displaced,output,'logical',colors)
  excess=field();excess[1].putpixel((700,500),(1,2,3));self.rejects(fullscreen.fullscreen_h2_field,excess,baseline,g,output,'logical',colors)
  residual=field();residual[1].putpixel((500,200),baseline.getpixel((500,200)));self.rejects(fullscreen.fullscreen_h2_field,residual,baseline,g,output,'logical',colors)
  reverse=baseline.copy();draw=ImageDraw.Draw(reverse)
  for key,name in (('B','POPUP_B'),('A','POPUP_A')):
   x,y,w,h=g[key];draw.rectangle((max(0,x),max(0,y),min(799,x+w-1),min(599,y+h-1)),fill=colors[name])
  self.rejects(fullscreen.fullscreen_h2_field,[baseline.copy(),reverse],baseline,g,output,'logical',colors)
  badscale=copy.deepcopy(output);badscale['scale']=2;self.rejects(fullscreen.fullscreen_h2_field,good,baseline,g,badscale,'logical',colors)
  moved=dict(origin=[-398,25],configured_A=[350,80,900,170],configured_B=[100,60,900,130],A=[-48,105,900,170],B=[52,165,900,130],crossing=dict(A=False,B=False))
  def moved_field(active=('POPUP_A','POPUP_B')):
   expected=baseline.copy();draw=ImageDraw.Draw(expected)
   for key,name in (('A','POPUP_A'),('B','POPUP_B')):
    if name not in active:continue
    x,y,w,h=moved[key];draw.rectangle((max(0,x),max(0,y),min(799,x+w-1),min(599,y+h-1)),fill=colors[name])
   return [baseline.copy(),expected]
  after_exit=moved_field();fullscreen.fullscreen_h2_field(after_exit,baseline,moved,output,'logical',colors)
  a_only=moved_field(('POPUP_A',));fullscreen.fullscreen_h2_field(a_only,baseline,moved,output,'logical',colors,active_roles=('POPUP_A',))
  b_residual=moved_field()
  b_residual[1].putpixel((100,200),colors['POPUP_B']);self.rejects(fullscreen.fullscreen_h2_field,b_residual,baseline,moved,output,'logical',colors,active_roles=('POPUP_A',))
 def test_fullscreen_input_uses_visible_output_fallback(self):
  from PIL import Image,ImageDraw
  outputs=copy.deepcopy(plans.RUNS['C8']['outputs']);frames={o['name']:'logical' for o in outputs}
  h1=Image.new('RGB',(800,600),(48,48,56));h2=Image.new('RGB',(800,600),(48,48,56));ImageDraw.Draw(h2).rectangle((100,190,180,270),fill=engine.COLORS['POPUP_B'])
  s=SimpleNamespace(outputs=outputs,frames=frames,click=Mock(return_value=({'owner':''},{'owner':[]})),delivery=Mock())
  g=dict(B=[52,165,900,130]);fullscreen.input_target(s,[h1,h2],g,'POPUP_B','B')
  self.assertGreaterEqual(s.click.call_args.args[1][0],100);self.assertLessEqual(s.click.call_args.args[1][0],180)
  s.delivery.assert_called_once_with('owner',g['B'],s.click.call_args.args[1],{'owner':''},{'owner':[]},'POPUP_B')
 def state(self):
  rect=dict(x=-800,y=0,width=800,height=600)
  owner=dict(type='con',id=40,pid=100,rect=dict(x=-800,y=25,width=400,height=575),window_rect=dict(x=2,y=0,width=396,height=575),nodes=[],floating_nodes=[],fullscreen_mode=0)
  peer=dict(type='con',id=41,rect=dict(x=-400,y=25,width=400,height=575),nodes=[],fullscreen_mode=0)
  group=dict(type='con',id=30,rect=rect,layout='splith',fullscreen_mode=1,nodes=[owner,peer],floating_nodes=[])
  ws=dict(type='workspace',id=20,name='1',output='HEADLESS-1',nodes=[group],floating_nodes=[])
  state=dict(owner=owner,workspace=ws,origin=[-798,25],snapshot=dict(tree=ws,outputs=[dict(name='HEADLESS-1',rect=rect)]))
  return state,41,30
 def test_oom_native_failure_role_nonce_pid_counts(self):
  env=dict(SMX_OOM_ROLE='root_popup',SMX_OOM_NONCE='a'*32)
  line='SMX_OOM ENOMEM role=root_popup nonce='+env['SMX_OOM_NONCE']+' pid=123 xdg=0x1 xdg_parent=0x2 parent=0x3 tree=0x4 children=0 matched=1 failures=1 successes=0 initialized=0 listeners=0 published=0'
  oom.native_failure(line,env,123)
  for old,new in [('pid=123','pid=124'),('root_popup','nested_popup'),('matched=1','matched=2'),('failures=1','failures=2'),('successes=0','successes=1'),('published=0','published=1'),('nonce='+env['SMX_OOM_NONCE'],'nonce='+'b'*32),('tree=0x4','tree=(nil)')]:self.rejects(oom.native_failure,line.replace(old,new),env,123)
  self.rejects(oom.native_failure,line+'\n'+line,env,123)
 def test_real_button_before_failed_map_and_disconnect(self):
  raw=(KIT/'wire-fixture.txt').read_text();cut=raw.index('POPUP_A ROLE_CONFIGURE ')
  before=raw[:cut];proof=oom_handler.opening_before_map(before,'POPUP_A','TOPLEVEL');self.assertGreater(proof['serial'],0)
  oom_handler.mapped_root(raw)
  self.rejects(oom_handler.mapped_root,raw.replace('.ack_configure(','.wrong_ack('))
  self.rejects(oom_handler.mapped_root,raw.replace('250, 170, 1000, 1)','249, 170, 996, 1)'))
  for bad in (before.replace('origin=wl_pointer.button','origin=fake'),before.replace('.grab(','.wrong('),before.replace('parent_xdg=','parent_xdg=9')):self.rejects(oom_handler.opening_before_map,bad,'POPUP_A','TOPLEVEL')
  raw='wl_display#1.error(nil, 1, "out of memory")\nEXIT error=71'
  self.assertTrue(oom_handler.expected_disconnect(raw,0)['expected_enomem'])
  for bad,code in [(raw, None),(raw,-9),(raw,7),(raw.replace(', 1,',', 2,'),0),(raw.replace('71','32'),0),('EXIT error=0',0)]:self.rejects(oom_handler.expected_disconnect,bad,code)
  s=SimpleNamespace(comp=Mock());s.comp.poll.return_value=-9;self.rejects(oom_handler.availability,s)
 def test_compositor_only_environment_no_helpers_clients(self):
  env=oom.process_environment(LAB,'O1','a'*32)
  with patch.dict(os.environ,env):self.assertFalse(any(k.startswith('SMX_OOM_') for k in gate.clean_environment(LAB)))
  s=engine.Session.__new__(engine.Session);s.run=self.root;s.handles=[];s.proc={};s.expired=False;s.env={};s.oom_env=env;s.compositor_environment=dict(MOSAIC_G2_DIR='offline',MOSAIC_G2_NONCE='a'*64,WLR_RENDERER='gles2');s.debit=Mock();s.record=Mock()
  with patch.object(engine.shutil,'which',return_value='/usr/bin/prlimit'),patch.object(engine.subprocess,'Popen',return_value=Mock(pid=12)) as popen:
   for name in ('compositor','owner','pointer','screenshot'):
    s.spawn(name,['not-executed']);actual=popen.call_args.kwargs['env'];self.assertEqual({k:v for k,v in actual.items() if k.startswith('SMX_OOM_')},env if name=='compositor' else {});self.assertEqual(actual.get('MOSAIC_G2_DIR'),'offline' if name=='compositor' else None);self.assertEqual(actual.get('WLR_RENDERER'),'gles2' if name=='compositor' else None)
  for h in s.handles:h.close()
 def test_arm_scope_debit_before_token_and_no_reuse(self):
  folder=LAB/'graphics-runs/O1/run'
  # The real arm path is tested via an isolated OFFLINE_TEST_ONLY run directory;
  # patch process_environment path construction only, never access real run paths.
  env=dict(SMX_OOM_TOKEN_PATH=str(self.root/'oom-token'),SMX_OOM_NONCE='a'*32,SMX_OOM_ROLE='root_popup')
  admission=dict(decision='ACCEPTED',source_manifest_sha256='f',oom_source_review_sha256='a953a38b49bea11e9c19e84ed2d8218a16b2e5d980e0ba57677eeee0ddf62c6c',variant_identity='COREC_V2_NATIVE_OOM_DIAGNOSTIC')
  s=SimpleNamespace(spec=plans.RUNS['O1'],run=self.root,auth=dict(manifest_sha256='f',prospective=admission,build_review='ACCEPTED',publication_sha256='p'),record=Mock())
  debits=[]
  def debit(kind):self.assertFalse(Path(env['SMX_OOM_TOKEN_PATH']).exists());debits.append(kind)
  s.debit=debit;stable=dict(startup=True,owner=True,neighbor=True,reference_H2_twice=True)
  for key in stable:
   bad=dict(stable);bad[key]=False;self.rejects(oom.arm,s,env,admission,bad)
  self.assertEqual(debits,[]);oom.arm(s,env,admission,stable);self.assertEqual(debits,['hook'])
  self.assertEqual((self.root/'oom-token').read_text(),'SMXOOM1 '+'a'*32+' root_popup\n')
  s.debit=Mock()
  with self.assertRaises(FileExistsError):oom.arm(s,env,admission,stable)
  self.assertEqual(s.debit.call_count,1)
  s.spec=plans.RUNS['O2'];env['SMX_OOM_ROLE']='nested_popup'
  self.rejects(oom.arm,s,env,admission,dict(stable,rootA=True,rootA_native_success=False))
 def test_gate_dependency_and_prospective_review(self):
  ledger,m,r,p,_,_=self.fixture()
  for rid in ('P1','C8','O1','O2','G2','R1'):self.rejects(ledger.admit,rid,m,r,p)
  auth=dict(binary='fake')
  with patch.object(gate,'validate_review',return_value=auth):
   self.rejects(ledger.admit,'O2',m,r,p)
   a=ledger.admit('O1',m,r,p);ledger.complete(a,dict(status='INCONCLUSIVE'))
   self.rejects(ledger.admit,'O2',m,r,p)
  self.assertEqual([x['id'] for x in json.loads(ledger.path.read_text())['runs']],['O1'])
 def test_client_immutability_and_future_c2_axis(self):
  for name in ('nested-client.c','vertical-client.c','saved-client.c','static-reference.c','pointer-daemon.c'):
   self.assertEqual((KIT/'clients'/name).read_bytes(),(LAB/'graphics-kit/clients'/name).read_bytes())
  from model import Provenance
  from predicates import geometry
  g=geometry((KIT/'wire-fixture.txt').read_text(),[0,25],Provenance(40,20,'NOT OBSERVABLE','offline'),1,600)
  self.assertEqual(g['crossing_axis'],1);self.assertEqual(g['crossing_boundary'],600);self.assertTrue(all(g['crossing'].values()))
 def test_expected_enomem_actual_cleanup_keeps_raw_exit(self):
  import threading
  class Process:
   def __init__(self,pid,code):self.pid=pid;self.returncode=code;self.stdin=io.StringIO()
   def poll(self):return self.returncode
   def wait(self,timeout=None):return self.returncode
  s=engine.Session.__new__(engine.Session);s.spec=plans.RUNS['O1'];s.auth={};s.ledger=Mock();s.run=self.root/'run';s.run.mkdir();s.runtime=self.root/'runtime';s.runtime.mkdir()
  s.started=time.monotonic();s.finished=threading.Event();s.expired=False;s.pointer=None;s.env={};s.watch=Mock();s.handles=[];s.events=[];s.closed=[]
  s.sock=Mock();s.sock.is_socket.return_value=True;s.comp=Process(999999991,None)
  s.proc={'compositor':s.comp,'owner':Process(999999992,1)}
  raw='wl_display#1.error(nil, 1, "out of memory")\nEXIT error=71'
  (s.run/'owner.log').write_text(raw);s.find=lambda _:None;s.debit=Mock()
  oom_handler.retire_enomem(s)
  def terminal(*args,**kwargs):s.comp.returncode=0;return SimpleNamespace(returncode=1,stdout='',stderr='')
  with patch.object(engine.subprocess,'run',side_effect=terminal),patch.object(engine.os,'killpg',side_effect=ProcessLookupError):
   self.assertEqual(s.cleanup('PARTIALLY_FEASIBLE'),'PARTIALLY_FEASIBLE')
  out=json.loads((s.run/'outcome.json').read_text());self.assertEqual(out['scientific_cleanup'],'PASS');self.assertEqual(out['client_closures'][0]['exit'],1);self.assertTrue(out['client_closures'][0]['expected_enomem']);self.assertEqual(out['protocol_errors'],['owner'])
 def test_gpu_environment_facade_and_hook_debit(self):
  import gpu_handler
  s=SimpleNamespace(spec=plans.RUNS['G2'],lab=LAB,debit=Mock(),spawn=Mock())
  view=gpu_handler.AdapterSession(s);self.assertEqual(view.spec['binary'],'core');self.assertEqual(s.spec['binary'],'gpu')
  view.env.update(MOSAIC_G2_DIR=str(LAB/'gpu-work/acquisition'),MOSAIC_G2_NONCE='a'*64,WLR_RENDERER='gles2')
  self.assertEqual(s.compositor_environment['MOSAIC_G2_NONCE'],'a'*64)
  view.debit('mutation');s.debit.assert_called_once_with('mutation','hook')
  view.spawn('g2-background',['client']);s.spawn.assert_called_once_with('g2-background',['client'],True)
  self.rejects(view.debit,'capture');self.rejects(view.spawn,'owner',['client'])
  self.rejects(view.env.update,MOSAIC_G2_DIR='/tmp/foreign',MOSAIC_G2_NONCE='a'*64,WLR_RENDERER='gles2')
  self.rejects(gpu_handler.validate_source_binding,LAB,dict(gpu_source_review='ACCEPTED',gl_observability_preflight='NOT_RUN',native_gl_status='NOT_RUN',build_review='ACCEPTED',pair=3))
 def test_gpu_source_binding_actual_frozen_bytes_and_negative(self):
  import gpu_handler
  receipt=self.root/'external-review.json';receipt.write_text('{"decision":"ACCEPTED","offline_fixture":true,"gl_observability":"PASS","gl_observability_scope":"PREFLIGHT_CAPABILITY_ONLY","native_gl_status":"NOT_RUN"}')
  review=dict(gpu_source_review='ACCEPTED',gl_observability_preflight='ACCEPTED',native_gl_status='NOT_RUN',build_review='ACCEPTED',pair=3,gpu_source_manifest=str(Path(os.environ.get('SMX_GPU_SOURCE_MANIFEST',str(LAB/'results/gpu-source-freeze.json')))),gpu_source_manifest_sha256=gate.sha(Path(os.environ.get('SMX_GPU_SOURCE_MANIFEST',str(LAB/'results/gpu-source-freeze.json')))),gate_file=str(receipt),gate_file_sha256=gate.sha(receipt),binding=dict(client=str(receipt),client_sha256=gate.sha(receipt)))
  for key in ('gpu_source_review','gl_observability_preflight','build_review'):review[key+'_receipt']=str(receipt);review[key+'_receipt_sha256']=gate.sha(receipt)
  gpu_handler.validate_source_binding(LAB,review)
  realsha=gpu_handler.sha
  with patch.object(gpu_handler,'sha',side_effect=lambda path:'bad' if Path(path)==LAB/'gpu-kit/scenario.py' else realsha(path)):
   self.rejects(gpu_handler.validate_source_binding,LAB,review)
  for key in ('gpu_source_manifest_sha256','gate_file_sha256','gpu_source_review_receipt_sha256'):
   bad=dict(review);bad[key]='wrong';self.rejects(gpu_handler.validate_source_binding,LAB,bad)
 def test_gpu_layer_closure_does_not_require_xdg_owner(self):
  import gpu_handler
  s=gpu_handler.GPUSceneSession.__new__(gpu_handler.GPUSceneSession);s.proc={'g2-background':SimpleNamespace(pid=123)};s.closed=[]
  raw='EXIT ns=1 mode=background error=0 commits=3\nzwlr_layer_surface_v1#7.destroy()\nwl_surface#6.destroy()'
  s.log=lambda _:raw
  def close(self,name,command):self.closed.append(dict(pid=123,status='PASS'))
  with patch.object(engine.Session,'close_client',close):
   s.close_client('g2-background');self.assertEqual(s.closed[-1]['role'],'zwlr_layer_surface_v1')
   raw=raw.replace('zwlr_layer_surface_v1#7.destroy()','xdg_toplevel#7.destroy()');self.rejects(s.close_client,'g2-background');self.assertEqual(s.closed[-1]['status'],'INCONCLUSIVE')
 def test_actual_gpu_adapter_caps_and_stop_before_B_on_failed_A(self):
  import gpu_handler
  scenario=gpu_handler.modules(LAB)
  for reject in (False,True):
   with self.subTest(reject=reject):
    root=self.root/('reject' if reject else 'accepted');root.mkdir()
    client=root/'client';client.write_bytes(b'OFFLINE_CLIENT_NOT_EXECUTED')
    events=[];commands=[];actions=Counter();test=self
    class Input:
     def write(self,text):
      commands.append(text.strip());e=len(commands)
      (root/f'epoch-{e}-point-0.rgba').write_bytes(b'OFFLINE_NATIVE_SOURCE')
      (root/f'epoch-{e}.jsonl').write_text('{"kind":"rejected"}\n' if reject else '{"kind":"end"}\n')
     def flush(self):pass
    class Fake:
     def __init__(self):
      self.spec=plans.RUNS['G2'];self.auth=dict(binary='synthetic-third-binary',manifest_sha256='f');self.lab=LAB;self.proc={}
     def debit(self,*kinds):
      actions.update(kinds)
      for kind in kinds:test.assertLessEqual(actions[kind],16 if kind=='capture' else self.spec['action_limits'][kind])
     def start(self):events.append('start')
     def cmd(self,*args):self.debit('configuration')
     def spawn(self,name,*args):self.debit('spawn');self.proc[name]=SimpleNamespace(stdin=Input())
     def find(self,*args):return dict(id=40)
     def wait(self,fn):return fn()
     def log(self,name):return 'BACKGROUND_CONFIGURED '+''.join('G2_SOURCE_BYTES command='+c+' ' for c in commands)
     def capture(self,*args):self.debit('capture');return Image.new('RGB',(8,8),(48,48,56))
     def pair_capture(self,*args):return [self.capture(),self.capture()]
     def record(self,*args,**kwargs):pass
     def save(self,*args,**kwargs):pass
     def snapshot(self,*args):pass
     def close_client(self,*args):self.debit('configuration')
    fake=Fake();binding=dict(G2_ledger_reserved=True,binary='synthetic-third-binary',source_manifest_sha256='f',gate_file='synthetic-gate',client=str(client),client_sha256=gate.sha(client),nonce='a'*64)
    with patch.object(scenario,'ROOT',root),patch.object(scenario,'gate'),patch.object(scenario,'arm'),patch.object(scenario,'epoch',side_effect=lambda directory,e,nonce,prior:dict(raw_total=prior+1)),patch.object(scenario.time,'sleep'),patch.object(gpu_handler.CompositorEnvironment,'update',side_effect=lambda **fields:None):
     if reject:
      self.rejects(scenario.run,gpu_handler.AdapterSession(fake),binding);self.assertEqual(commands,['G2-A']);self.assertEqual(actions['hook'],1);self.assertEqual(actions['capture'],2)
     else:
      result=scenario.run(gpu_handler.AdapterSession(fake),binding);self.assertTrue(result['native_source_A_Areturn_exact']);self.assertEqual(actions['capture'],8);self.assertEqual(actions['hook'],3);self.assertEqual(commands,['G2-A','G2-B','G2-A-return'])
 def test_new_handler_capture_and_action_caps(self):
  for rid,cap in [('P1',10),('C8',12),('O1',8),('O2',8)]:
   with self.subTest(rid=rid):self.assertEqual(self.quota(rid)['capture'],cap)
 def quota(self,rid):
  state,peer,gid=self.state();test=self
  class Fake:
   def __init__(self):
    self.spec=copy.deepcopy(plans.RUNS[rid]);self.outputs=copy.deepcopy(self.spec['outputs']);self.frames={o['name']:'logical' for o in self.outputs};self.actions=Counter();self.proc={};self.events=[];self.run=test.root;self.auth=dict(prospective=dict(client_binary_sha256='offline-client'),manifest_sha256='offline-manifest');self.closed=[];self.oom_env=dict(SMX_OOM_ROLE='root_popup' if rid=='O1' else 'nested_popup',SMX_OOM_NONCE='a'*32);self.comp=Mock(pid=123);self.failed=False
   def debit(self,*kinds):
    for k in kinds:
     self.actions[k]+=1;limit=self.spec['capture_limit'] if k=='capture' else self.spec['action_limits'][k];test.assertLessEqual(self.actions[k],limit)
   def cmd(self,c,business=False):
    self.debit('mutation' if business else 'configuration')
    if rid=='C8' and c.endswith('fullscreen disable'):state['snapshot']['tree']['nodes'][0]['fullscreen_mode']=0
   def launch_client(self,n,*args):self.debit('spawn');self.proc[n]=Mock(pid=100 if n=='owner' else 101);self.proc[n].poll.return_value=None
   def find(self,n):return dict(id=40 if n=='owner' else 41)
   def owner(self,*args):return state
   def calibrate(self,*args):return state
   def snapshot(self,*args):return state['snapshot']
   def capture(self,tag,out):self.debit('capture');return Image.new('RGB',(800,600),(48,48,56))
   def pair_capture(self,tag):return [self.capture(tag+'-H1','HEADLESS-1'),self.capture(tag+'-H2','HEADLESS-2')]
   def click(self,n,xy,action='right',grab=False):
    self.debit('move','click',*(['grab'] if grab else []))
    if n=='reference':return {'reference':'wl_pointer#3.button(1, 1, 273, 1)\nwl_pointer#3.button(2, 1, 273, 0)'},{'reference':['BUTTON ns=1 serial=1 button=273 state=1','BUTTON ns=2 serial=2 button=273 state=0']}
    return {'owner':''},{'owner':[]}
   def inject(self,*args):self.debit('move')
   def delivery(self,*args):pass
   def wait(self,*args):pass
   def save(self,*args):pass
   def client_cmd(self,*args):self.debit('configuration')
   def close_client(self,*args):self.debit('configuration')
   def log(self,n):
    if rid in ('P1','C8'):return (KIT/'wire-fixture.txt').read_text()
    if n=='compositor':return 'SMX_OOM ENOMEM role='+self.oom_env['SMX_OOM_ROLE']+'\nSMX_OOM result role='+self.oom_env['SMX_OOM_ROLE']+' tree=(nil) failures=1'
    raw=(KIT/'wire-fixture.txt').read_text();return raw[:raw.index(('POPUP_A' if rid=='O1' else 'POPUP_B')+' ROLE_CONFIGURE ')]
  s=Fake();geo=dict(A=[-448,105,900,170],B=[-348,165,900,130],configured_A=[350,80,900,170],configured_B=[100,60,900,130],origin=[-798,25]);proto=cases.validators.grab((KIT/'wire-fixture.txt').read_text())
  with ExitStack() as stack:
   stack.enter_context(patch.object(time,'sleep'))
   stack.enter_context(patch.object(cases,'stable_reference',side_effect=lambda session:(session.capture('ref1','HEADLESS-2'),session.capture('ref2','HEADLESS-2'))[0]))
   if rid in ('P1','C8'):
    for name,value in [('solid_point',[-700,100]),('fresh_geometry',geo),('count',0)]:stack.enter_context(patch.object(fullscreen,name,return_value=value))
    stack.enter_context(patch.object(fullscreen.validators,'standard_spill'))
    stack.enter_context(patch.object(fullscreen,'fullscreen_h2_field'))
    import lifecycle
    stack.enter_context(patch.object(lifecycle,'explicit_child_close'))
    fullscreen.run(s)
   else:
    stack.enter_context(patch.object(oom_handler,'solid_point',return_value=[-700,100]))
    stack.enter_context(patch.object(oom_handler,'native_root_success',return_value=dict(tree='0x1')))
    stack.enter_context(patch.object(oom_handler,'availability',return_value=dict(pid=123)))
    stack.enter_context(patch.object(oom_handler,'count',side_effect=[1,0]))
    stack.enter_context(patch.object(oom,'native_failure',return_value=dict(failures='1')))
    stack.enter_context(patch.object(oom,'arm',side_effect=lambda session,*_:session.debit('hook')))
    s.auth['prospective']={}
    oom_handler.run(s);test.assertEqual(s.actions['hook'],1)
  test.assertEqual(s.actions['camera'],0)
  return s.actions

if __name__=='__main__':unittest.main(verbosity=2)
