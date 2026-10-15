"""OFFLINE_TEST_ONLY: real final predicates; no headless spawn or real budget."""
import copy,json,os,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cases,engine,fullscreen,gate,oom,oom_handler,plans,validators
from geometry import assigned_origin,exterior_ipc,exact
from PIL import Image,ImageDraw
LAB=Path(os.environ['SMX_LAB']);KIT=Path(__file__).resolve().parents[1]

class Scientific(unittest.TestCase):
 def rejects(self,fn,*args,**kwargs):
  with self.assertRaises((ValueError,AssertionError,RuntimeError,KeyError)):fn(*args,**kwargs)
 def snapshot(self,width=800,scroll=800,output='HEADLESS-1',focus=3,count=3,gap=0):
  x=-width if output=='HEADLESS-1' else 0;cell=max(640,(width-(count-1)*gap)//count)
  return dict(tree=dict(type='workspace',layout='mosaic',name='1',id=20,output=output,rect=dict(x=x,y=0,width=width,height=600),mosaic=dict(rows=[dict(children=list(range(1,count+1)),scroll_x=scroll,focused=focus)]),nodes=[dict(id=i+1,focused=i+1==focus,rect=dict(x=x+i*(cell+gap),y=25,width=cell,height=575)) for i in range(count)]))
 def state(self):
  rect=dict(x=-800,y=0,width=800,height=600)
  owner=dict(type='con',id=40,pid=123,rect=dict(x=-800,y=0,width=400,height=600),nodes=[],floating=None)
  peer=dict(type='con',id=41,pid=124,rect=dict(x=-400,y=0,width=400,height=600),nodes=[])
  group=dict(type='con',id=30,layout='splith',fullscreen_mode=1,nodes=[owner,peer],rect=rect,floating_nodes=[])
  ws=dict(type='workspace',id=20,name='1',output='HEADLESS-1',layout='splith',nodes=[group],fullscreen_mode=1)
  return dict(owner=owner,workspace=ws,snapshot=dict(tree=ws,outputs=[dict(name='HEADLESS-1',rect=rect)]))
 def applied(self):return dict(source='post-command-xdg-configure-ack-map',group_id=30,owner_id=40,workspace_id=20)
 def test_fullscreen_exact_group(self):
  st=self.state();fullscreen.group_candidate(st,41,30,applied=self.applied())
  changes=[lambda g:g.update(fullscreen_mode=0),lambda g:g.update(nodes=g['nodes'][:1]),lambda g:g['nodes'][1].update(id=99),lambda g:g['nodes'][0]['rect'].update(width=800),lambda g:g.update(layout='splitv')]
  for change in changes:
   bad=copy.deepcopy(st);change(bad['snapshot']['tree']['nodes'][0]);self.rejects(fullscreen.group_candidate,bad,41,30,applied=self.applied())
 def test_fullscreen_peer_at_workspace(self):
  bad=self.state();g=bad['workspace']['nodes'][0];bad['workspace']['nodes'].append(g['nodes'].pop());self.rejects(fullscreen.group_candidate,bad,41,30,applied=self.applied())
 def test_pending_or_other_owner_workspace_not_applied(self):
  for mutation in ({'source':'pending'},{'owner_id':99},{'workspace_id':99},{'group_id':99}):
   a=self.applied();a.update(mutation);self.rejects(fullscreen.group_candidate,self.state(),41,30,applied=a)
  self.rejects(fullscreen.group_candidate,self.state(),41,30)
 def test_fullscreen_marker_alone_not_enough(self):
  st=self.state();st['workspace']['nodes'][0]['fullscreen_mode']=0;self.rejects(fullscreen.group_candidate,st,41,30,applied=self.applied())
 def field(self):
  baseline=Image.new('RGB',(800,600),(48,48,56));g=dict(origin=[-798,25],configured_A=[350,80,900,170],configured_B=[100,60,900,130],A=[-448,105,900,170],B=[-348,165,900,130])
  return baseline,g,plans.H[1]
 def test_whole_field_prediction_occlusion_and_A_only(self):
  b,g,o=self.field();pred=fullscreen.expected_h2(b,g,o,'logical',engine.COLORS,require_crossing=True)
  self.assertEqual(pred.getpixel((0,110)),engine.COLORS['POPUP_A']);self.assertEqual(pred.getpixel((0,170)),engine.COLORS['POPUP_B'])
  one=fullscreen.expected_h2(b,g,o,'logical',engine.COLORS,('POPUP_A',));self.assertEqual(one.getpixel((0,170)),engine.COLORS['POPUP_A'])
  for xy,color in [((799,599),(1,2,3)),((0,170),engine.COLORS['POPUP_A']),((0,110),(48,48,56))]:
   wrong=pred.copy();wrong.putpixel(xy,color);self.rejects(exact,pred,wrong)
  bad=copy.deepcopy(g);bad['A'][0]=10;self.rejects(fullscreen.expected_h2,b,bad,o,'logical',engine.COLORS,require_crossing=True)
 def test_migration_reveal_and_stale_camera(self):
  prior=cases.dynamic_geometry(self.snapshot(),expected_focus=3)
  moved=self.snapshot(scroll=1120,output='HEADLESS-2');actual=cases.dynamic_geometry(moved,prior,'migration',3);self.assertEqual(actual['expected_scroll'],1120)
  self.rejects(cases.dynamic_geometry,self.snapshot(scroll=800,output='HEADLESS-2'),prior,'migration',3)
  self.rejects(cases.dynamic_geometry,moved,prior,'resize',3)
 def test_current_geometry_varies_count_gap_and_viewport(self):
  prior=cases.dynamic_geometry(self.snapshot(scroll=500,count=4,gap=7,focus=4),expected_focus=4)
  moved=self.snapshot(width=960,scroll=4*640+3*7-960,output='HEADLESS-2',count=4,gap=7,focus=4)
  actual=cases.dynamic_geometry(moved,prior,'migration',4);self.assertEqual(actual['expected_scroll'],1621)
 def test_resize800960800_and_input_invalidation(self):
  a=cases.dynamic_geometry(self.snapshot(scroll=1100),expected_focus=3)
  b=cases.dynamic_geometry(self.snapshot(width=960,scroll=960),a,'resize',3)
  c=cases.dynamic_geometry(self.snapshot(scroll=960),b,'resize',3);self.assertEqual(c['expected_scroll'],960)
  self.rejects(cases.dynamic_geometry,self.snapshot(width=960,scroll=1100),a,'resize',3)
 def test_missing_or_other_refocus_order_bounds_pending(self):
  prior=cases.dynamic_geometry(self.snapshot(),expected_focus=3)
  for mutate in [lambda w:w['nodes'][2].update(focused=False),lambda w:w['mosaic']['rows'][0].update(focused=1),lambda w:w['mosaic']['rows'][0].update(scroll_x=9999),lambda w:w['mosaic']['rows'][0].update(children=[3,2,1]),lambda w:w['nodes'][2].update(focused=False)]:
   snap=self.snapshot(scroll=1120,output='HEADLESS-2');mutate(snap['tree']);self.rejects(cases.dynamic_geometry,snap,prior,'migration',3)
  bad=self.snapshot(scroll=0,focus=1);self.rejects(cases.dynamic_geometry,bad,prior,'migration',3)
  bad=self.snapshot(scroll=1120);bad['state_source']='pending-as-current';self.rejects(cases.dynamic_geometry,bad,prior,'migration',3)
 def close_log(self,roles=('TOPLEVEL','POPUP_A'),maps=()):
  out=[]
  for i,name in enumerate(roles):
   a=10+i*3;out.append(f'{name} CREATE wl={a} xdg={a+1} role={a+2}')
   if name in maps:out.append(name+' MAP wl='+str(a))
  out+=['CLOSE_RECEIVED','COMMAND close_owner']
  for i,name in reversed(list(enumerate(roles))):
   a=10+i*3;out += [f'{name} DESTROY role={a+2} xdg={a+1} wl={a}',f'{"xdg_toplevel" if i==0 else "xdg_popup"}#{a+2}.destroy()',f'xdg_surface#{a+1}.destroy()',f'wl_surface#{a}.destroy()']
  return '\n'.join(out+['SHM_CLOSURE created=1 released=1','EXIT error=0'])
 def test_root_only_close_is_valid_and_distinct(self):
  raw=self.close_log();validators.client_exit(raw,0,'root_failure');self.rejects(validators.client_exit,raw,0,'nested')
  self.rejects(validators.client_exit,raw+'\nPOPUP_B CREATE wl=99 xdg=98 role=97',0,'root_failure')
  self.rejects(validators.client_exit,raw.replace('CLOSE_RECEIVED',''),0,'root_failure')
 def test_nested_failure_A_mapped_B_unmapped(self):
  raw=self.close_log(('TOPLEVEL','POPUP_A','POPUP_B'),('POPUP_A',));validators.client_exit(raw,0,'nested_failure')
  self.rejects(validators.client_exit,raw+'\nPOPUP_B MAP wl=16',0,'nested_failure')
  self.rejects(validators.client_exit,raw.replace('POPUP_A MAP wl=13',''),0,'nested_failure')
 def test_close_negative_hierarchy_error_release_signal(self):
  raw=self.close_log()
  for bad in [raw.replace('POPUP_A DESTROY','TOPLEVEL DESTROY'),raw.replace('released=1','released=0'),raw.replace('error=0','error=12'),raw.replace('xdg_popup#15.destroy()',''),raw+'\nwl_display#1.error(wl_display#1, 1, "no memory")',raw+'\nPOPUP_A MAP wl=13']:
   self.rejects(validators.client_exit,bad,0,'root_failure')
  self.rejects(validators.client_exit,raw,-15,'root_failure')
 def test_wire_real_grabs_and_partial_maps(self):
  raw=(KIT/'wire-fixture.txt').read_text();validators.grab(raw)
  import re
  grab=re.search(r'POPUP_A GRAB_REQUEST[^\n]+',raw)[0];serial=re.search(r'serial=(\d+)',grab)[1]
  changes=[raw.replace('used='+serial,'used=999',1),raw.replace('POPUP_B MAP ','POPUP_B NOT_MAP ',1),re.sub(r'(POPUP_B CREATE[^\n]+parent_xdg=)\d+',r'\g<1>999',raw),re.sub(r'xdg_popup#\d+\.grab',r'xdg_popup#999.grab',raw,count=1)]
  for bad in changes:self.assertNotEqual(raw,bad);self.rejects(validators.grab,bad)
 def test_failed_popup_real_wire_no_map(self):
  raw=(KIT/'wire-fixture.txt').read_text();oom_handler.opening_before_map(raw,'POPUP_A','TOPLEVEL')
  grab=__import__('re').search(r'POPUP_A GRAB_REQUEST[^\n]+',raw)[0];serial=__import__('re').search(r'serial=(\d+)',grab)[1]
  self.rejects(oom_handler.opening_before_map,raw.replace('used='+serial,'used=999',1),'POPUP_A','TOPLEVEL')
 def test_no_memory_requires_wire(self):
  raw='wl_display#1.error(wl_display#1, 1, "no memory")\nEXIT error=12\n';oom_handler.expected_disconnect(raw,0)
  for bad in [raw.replace('.error(','.no_error('),raw.replace('error=12','error=0'),raw.replace(', 1,',', 2,')]:self.rejects(oom_handler.expected_disconnect,bad,0)
 def test_native_counter_and_NULL_association(self):
  env=dict(SMX_OOM_NONCE='a'*32,SMX_OOM_ROLE='root_popup')
  raw='SMX_OOM ENOMEM role=root_popup nonce='+env['SMX_OOM_NONCE']+' pid=123 xdg=0x10 xdg_parent=0x20 parent=0x30 tree=0x40 children=0 matched=1 failures=1 successes=0 initialized=0 listeners=0 published=0\nSMX_OOM result role=root_popup pid=123 xdg=0x10 xdg_parent=0x20 parent=0x30 tree=(nil) successes=0 failures=1'
  oom.native_failure(raw,env,123)
  for old,new in [('listeners=0','listeners=1'),('published=0','published=1'),('initialized=0','initialized=1'),('pid=123','pid=999'),('tree=(nil)','tree=0x40'),('xdg_parent=0x20','xdg_parent=0x99'),('matched=1','matched=2'),('nonce='+env['SMX_OOM_NONCE'],'nonce='+'b'*32)]:
   bad=raw.replace(old,new,1);self.rejects(oom.native_failure,bad,env,123)
 def test_B5_native_SHM_and_destination_titlebar_distinct(self):
  owner=dict(rect=dict(x=-800,y=25,width=640,height=575),window_rect=dict(x=2,y=0,width=636,height=573),deco_rect=dict(height=25))
  self.assertEqual(assigned_origin(owner),[-798,25]);self.assertEqual(exterior_ipc(owner),[-800,0,640,600])
  self.assertNotEqual([420,320],[owner['window_rect']['width'],owner['window_rect']['height']])
 def test_floating_null_tiled_and_actual_floating_rejected(self):
  st=self.state();path=[st['workspace'],st['workspace']['nodes'][0],st['owner']];st['workspace']['layout']='mosaic'
  self.assertTrue(validators.camera_eligible(path,st['workspace']) is False) # fullscreen exemption
  path[1]['fullscreen_mode']=0;self.assertTrue(validators.camera_eligible(path,st['workspace']))
  path[1]['floating_nodes']=[st['owner']];self.assertFalse(validators.camera_eligible(path,st['workspace']))

 def test_B5_terminal_raw_codes_not_rewritten(self):
  terminal=dict(ipc_exit=1,stdout='',stderr='Unable to receive IPC response')
  self.assertTrue(validators.terminal_transport(terminal,0));self.assertEqual(terminal['ipc_exit'],1)
  self.assertFalse(validators.terminal_transport(terminal,1));self.assertFalse(validators.terminal_transport(dict(ipc_exit=1),0))
  self.assertFalse(validators.terminal_transport(dict(ipc_exit=1,stdout='',stderr=''),0))
 def test_positioner_adjust_same_actual_wire_required(self):
  raw=(KIT/'wire-fixture.txt').read_text()
  import re
  adapted=re.sub(r'(xdg_wm_base#\d+\.create_positioner\(new id xdg_positioner#(\d+)\))',lambda m:m[0]+'\nxdg_positioner#'+m[2]+'.set_constraint_adjustment(0)',raw)
  self.assertEqual(fullscreen.positioner_adjust(adapted),[0,0])
  self.rejects(fullscreen.positioner_adjust,adapted.replace('set_constraint_adjustment(0)','set_constraint_adjustment(1)',1))
  self.rejects(fullscreen.positioner_adjust,raw)

 def test_native_availability_missing_identity_IPC_input_socket(self):
  expected=dict(pid=123,binary='/private/sway',binary_sha256='a'*64,build_id='b'*40,wlroots='/usr/lib/libwlroots-0.20.so')
  ident=dict(pid=123,exe=expected['binary'],sha256=expected['binary_sha256'],build_id=expected['build_id'],wlroots=[expected['wlroots']],maps='mapped '+expected['wlroots'],swaysock='/tmp/smx-offline/sway-ipc.123.sock',captured_before_cleanup=True)
  snap=dict(tree=dict(type='root',nodes=[dict(id=1)]),outputs=[dict(active=True),dict(active=True)])
  buttons=dict(reference=['BUTTON ns=100 serial=11 button=273 state=1','BUTTON ns=101 serial=12 button=273 state=0'])
  raw='wl_pointer#9.button(11, 100, 273, 1)\nwl_pointer#9.button(12, 101, 273, 0)'
  oom_handler.availability_certificate(ident,expected,snap,raw,buttons)
  for change in ({'pid':999},{'sha256':'c'*64},{'build_id':'c'*40},{'maps':'wrong'},{'captured_before_cleanup':False},{'swaysock':'/run/user/1000/sway.sock'}):
   bad=dict(ident,**change);self.rejects(oom_handler.availability_certificate,bad,expected,snap,raw,buttons)
  self.rejects(oom_handler.availability_certificate,ident,expected,dict(tree={},outputs=[]),raw,buttons)
  self.rejects(oom_handler.availability_certificate,ident,expected,snap,raw,{})
  self.rejects(oom_handler.availability_certificate,ident,expected,snap,raw.replace('273, 0','273, 1'),buttons)
 def test_predictions_precede_runtime_captures(self):
  # The real acquisition helper calls the production oracle first; a capture
  # side-effect changes the geometry to prove it cannot influence prediction.
  b,g,o=self.field();expected=fullscreen.expected_h2(b,g,o,'logical',engine.COLORS)
  from types import SimpleNamespace
  events=[]
  def capture(tag):
   events.append('capture');g['A'][0]=999;return [b,expected]
  session=SimpleNamespace(outputs=plans.H,frames={'HEADLESS-2':'logical'},record=lambda *args,**kwargs:events.append('prediction'),pair_capture=capture)
  fullscreen.measured_pair(session,'offline',b,g);self.assertEqual(events,['prediction','capture'])

class RepairPredicates(unittest.TestCase):
 rejects=Scientific.rejects
 def test_oom_pixels_both_outputs_and_final(self):
  b=Image.new('RGB',(40,40),(48,48,56));clean=[b.copy(),b.copy()]
  for failed in ('POPUP_A','POPUP_B'):
   oom_handler.popup_pixels(clean,b,failed)
   for output in (0,1):
    bad=[im.copy() for im in clean];bad[output].putpixel((7,9),engine.COLORS[failed])
    self.rejects(oom_handler.popup_pixels,bad,b,failed)
  alive=[b.copy(),b.copy()];alive[0].putpixel((7,9),engine.COLORS['POPUP_A'])
  oom_handler.popup_pixels(alive,b,'POPUP_B')
  for role in ('POPUP_A','POPUP_B'):
   for output in (0,1):
    bad=[im.copy() for im in clean];bad[output].putpixel((7,9),engine.COLORS[role])
    self.rejects(oom_handler.popup_pixels,bad,b,final=True)
  oom_handler.popup_pixels(clean,b,final=True)
 def test_root_input_real_delivery_wrong_wire_owner_point(self):
  from types import SimpleNamespace
  raw=(KIT/'wire-fixture.txt').read_text()
  # Real fixture establishes configured root identity; use its measured rectangle.
  proof=oom_handler.mapped_root(raw);x,y,w,h=proof['configure']
  origin=[-x,-y];image=Image.new('RGB',(800,600),engine.COLORS['POPUP_A'])
  def exercise(wrong=None):
   def click(name,point,action):
    self.assertEqual((name,action),('owner','right'))
    local=[point[0],point[1]]
    if wrong=='point':local[0]+=1
    target='TOPLEVEL' if wrong=='role' else 'POPUP_A'
    lines=[f'POINTER_BUTTON target={target} serial={i+10} button=273 state={v}' for i,v in enumerate((1,0))]
    tail=f'POINTER_MOTION target=POPUP_A x={local[0]} y={local[1]}\n'+'\n'.join(f'wl_pointer#9.button({i+10}, 100, 273, {v})' for i,v in enumerate((1,0)))
    if wrong=='wire':tail=tail.replace('273, 0','273, 1')
    buttons={'owner':lines,'reference':lines if wrong=='owner' else []}
    return {'owner':tail},buttons
   obj=SimpleNamespace(log=lambda name:raw,owner=lambda name:dict(origin=origin),outputs=[dict(scale=1,logical=[0,0,800,600])],frames={'HEADLESS-1':'logical'},click=click)
   obj.delivery=lambda *args:engine.Session.delivery(obj,*args)
   return oom_handler.surviving_root_input(obj,[image,image])
  self.assertEqual(exercise()['status'],'PARTIALLY_FEASIBLE')
  for wrong in ('wire','owner','point','role'):self.rejects(exercise,wrong)
 def test_git_actual_tree_inventory_and_modes(self):
  import subprocess
  top=KIT.parents[3];prefix=Path('tooling/probes/step20c-applied-state-input')
  raw=subprocess.run(['git','-C',str(top),'ls-tree','-rz','--full-tree','HEAD','--',str(prefix)],check=True,capture_output=True).stdout
  self.assertTrue(raw)
  files={};modes={}
  for row in raw.split(b'\0')[:-1]:
   meta,path=row.split(b'\t',1);rel=path[len(str(prefix).encode())+1:].decode();files[rel]=gate.sha(top/path.decode());modes[rel]='0o755' if meta.startswith(b'100755') else '0o644'
  gate.git_inventory(raw,str(prefix),files,modes)
  gate.published_sources(top,'HEAD',prefix,files,modes,gate.clean_environment(LAB))
  first=raw.split(b'\0')[0];meta,path=first.split(b'\t',1);mode,kind,oid=meta.split(b' ')
  for replacement in (b'100755' if mode==b'100644' else b'100644',b'120000'):
   bad=raw.replace(first,replacement+b' '+kind+b' '+oid+b'\t'+path,1)
   self.rejects(gate.git_inventory,bad,str(prefix),files,modes)
  self.rejects(gate.git_inventory,raw+first.replace(path,path+b'-extra')+b'\0',str(prefix),files,modes)
  self.rejects(gate.git_inventory,raw[len(first)+1:],str(prefix),files,modes)
  self.rejects(gate.git_inventory,raw,str(prefix)+'-wrong',files,modes)
  for invalid in ('0644','0o600','100644',644):
   bad=dict(modes);bad[next(iter(bad))]=invalid;self.rejects(gate.git_inventory,raw,str(prefix),files,bad)
 def test_source_modes_reject_nonportable_and_symlink(self):
  root=Path(tempfile.mkdtemp(dir=os.environ['TMPDIR']));p=root/'file';p.write_text('source');p.chmod(0o644)
  self.assertEqual(gate.source_modes(root),{'file':'0o644'})
  p.chmod(0o755);self.assertEqual(gate.source_modes(root),{'file':'0o755'})
  p.chmod(0o600);self.rejects(gate.source_modes,root)
  p.unlink();p.symlink_to('/dev/null');self.rejects(gate.source_modes,root)

class IdentityDiagnostic(unittest.TestCase):
 def test_observed_exact_identity_and_mismatch_stays_refused(self):
  pid=os.getpid();exe=Path(f'/proc/{pid}/exe');binary=exe.resolve(strict=True)
  proof=engine.client_executable_identity(pid,binary,gate.sha(exe))
  self.assertEqual(proof['status'],'OBSERVED');engine.require_client_identity(proof)
  self.assertEqual(proof['pid'],pid);self.assertEqual(proof['proc'],str(exe))
  for target,digest in ((binary,'0'*64),(Path('/wrong/binary'),gate.sha(exe))):
   proof=engine.client_executable_identity(pid,target,digest)
   with self.assertRaises(ValueError):engine.require_client_identity(proof)
 def test_EACCES_diagnostic_is_saved_and_same_final_predicate_refuses(self):
  import errno
  for phase in ('resolve','sha256'):
   failure=PermissionError(errno.EACCES,'offline actual OS error fixture','/proc/123/exe')
   if phase=='resolve':context=patch.object(Path,'resolve',side_effect=failure)
   else:context=patch.object(engine,'sha',side_effect=failure)
   with context:proof=engine.client_executable_identity(os.getpid(),Path('/expected'),'a'*64)
   self.assertEqual(proof['status'],'NOT_OBSERVABLE');self.assertFalse(proof['matches'])
   self.assertEqual(proof['errno'],errno.EACCES);self.assertEqual(proof['operation'],phase)
   self.assertIn('PermissionError',proof['error_type']);self.assertIn('offline actual OS error fixture',proof['error'])
   with self.assertRaisesRegex(ValueError,'NOT_OBSERVABLE'):engine.require_client_identity(proof)
 def test_missing_proc_preserves_errno(self):
  import errno
  proof=engine.client_executable_identity(2147483647,Path('/expected'),'a'*64)
  self.assertEqual(proof['status'],'NOT_OBSERVABLE');self.assertEqual(proof['errno'],errno.ENOENT)
  with self.assertRaises(ValueError):engine.require_client_identity(proof)

class Admission(Scientific):
 def setUp(self):
  self.root=Path(tempfile.mkdtemp(prefix='gate-',dir=os.environ.get('TMPDIR',str(LAB/'scratch'))));self.ns=self.root/'OFFLINE_TEST_ONLY';self.ns.mkdir(mode=0o700)
  self.manifest=self.ns/'manifest.json';self.review=self.ns/'review.json';self.publication=self.ns/'publication.json'
  self.files=gate.source_files();self.m=dict(ticket=gate.TICKET,schema='native-closure-source-v1',author='fixture-author',files=self.files,modes=gate.source_modes(),plans=plans.RUNS,limits=plans.LIMITS)
  gate.durable(self.manifest,self.m)
  elf=self.ns/'fake-offline-ELF';elf.write_bytes(b'OFFLINE_TEST_ONLY never executed')
  identity=dict(binary=str(elf),binary_sha256=gate.sha(elf),wlroots='/usr/lib/libwlroots-0.20.so',wlroots_sha256=gate.WL_SHA,build_review='ACCEPTED',source_qualification='ACCEPTED',build_id='offline')
  runtime=self.ns/'runtime.json';gate.durable(runtime,dict(ticket=gate.TICKET,identities={name:identity for name in ('pristine','core','oom')}))
  # Fake payloads are explicitly OFFLINE; only validation and budget state are
  # exercised. No receipt can authorize Session (offline namespace is rejected).
  self.build=LAB/'followup-work/client-build';self.generated={name:gate.sha(self.build/name) for name in ('fullscreen-client','nested-client','static-reference','pointer-daemon')}
  compile=self.ns/'compile.json';gate.durable(compile,dict(status='PASS',runtime='NOT_RUN',generated=self.generated,inputs={str(p.relative_to(KIT)):gate.sha(p) for folder in ('clients','protocols') for p in (KIT/folder).iterdir()}))
  test=self.ns/'tests.json';gate.durable(test,dict(status='PASS',tests_run=1,failures=0,source_digest=gate.digest(self.files)))
  case=dict(oom_source_review='ACCEPTED',variant_identity='COREC_V2_NATIVE_OOM_DIAGNOSTIC',source_manifest_sha256=gate.sha(self.manifest),decision='ACCEPTED',client_build_review='ACCEPTED',client_build_receipt=str(compile),client_build_receipt_sha256=gate.sha(compile))
  self.r=dict(ticket=gate.TICKET,decision='ACCEPTED',independent=True,reviewer='offline-independent-fixture',manifest_sha256=gate.sha(self.manifest),runtime_manifest=str(runtime),runtime_manifest_sha256=gate.sha(runtime),runs={rid:case for rid in plans.RUNS},gates={name:dict(decision='ACCEPTED',manifest_sha256=gate.sha(self.manifest),receipt=str(test),receipt_sha256=gate.sha(test)) for name in ('FULLSCREEN_COMPARABILITY_OFFLINE','MIGRATION_REFOCUS_OFFLINE','OOM_ROOT_NESTED_ORACLE_OFFLINE')})
  gate.durable(self.review,self.r);commit='a'*40
  self.p=dict(ticket=gate.TICKET,decision='VERIFIED',offline_test_only=True,source_commit=commit,origin_sha=commit,github_sha=commit,manifest_sha256=gate.sha(self.manifest),source_digest=gate.digest(self.files),remote_observations={name:dict(exit=0,argv=['git','ls-remote',name,'refs/heads/main'],stdout=commit+'\trefs/heads/main\n') for name in ('origin','github')});gate.durable(self.publication,self.p)
  self.ledger=gate.Ledger(LAB,self.ns/'budget.json',offline=True);self.ledger.initialize()
 def validate(self,rid='OM-ROOT'):return gate.validate_review(LAB,self.manifest,self.review,self.publication,rid,offline=True)
 def admit(self,rid='OM-ROOT'):return self.ledger.admit(rid,self.manifest,self.review,self.publication)
 def test_real_validator_offline_namespace_and_unique_reservation(self):
  self.validate();a=self.admit();self.ledger.action_debit(a,'capture','hook');self.rejects(self.admit)
  self.rejects(self.ledger.action_debit,a,'hook');self.ledger.complete(a,dict(status='INCONCLUSIVE'));self.rejects(self.ledger.action_debit,a,'capture')
  self.rejects(engine.Session,plans.RUNS['OM-ROOT'],a)
 def test_historical_ids_and_tokens(self):
  for rid in ('O1','O2','C7','P1','C8','G2'):self.rejects(self.validate,rid)
  auth=self.admit();bad=dict(auth,token='historic-token');self.rejects(self.ledger.action_debit,bad,'capture')
 def test_self_review_and_wrong_SHA_reject_before_reservation(self):
  for mutate in [lambda r:r.update(reviewer='fixture-author'),lambda r:r.update(decision='PASS'),lambda r:r.update(manifest_sha256='0'*64),lambda r:r.update(gates={})]:
   bad=copy.deepcopy(self.r);mutate(bad);gate.durable(self.review,bad);self.rejects(self.admit)
   self.assertEqual(json.loads(self.ledger.path.read_text())['runs'],[])
 def test_publication_remote_observation_and_clone_bytes_binding(self):
  for mutate in [lambda p:p.update(github_sha='b'*40),lambda p:p.update(remote_observations={}),lambda p:p.update(source_digest='0'*64),lambda p:p.update(offline_test_only=False)]:
   bad=copy.deepcopy(self.p);mutate(bad);gate.durable(self.publication,bad);self.rejects(self.admit)
 def test_stale_source_manifest_and_superficial_gate(self):
  self.m['files']['graphics/plans.py']='0'*64;gate.durable(self.manifest,self.m);self.rejects(self.admit)
  gate.durable(self.manifest,{**self.m,'files':self.files});self.r['gates']['OOM_ROOT_NESTED_ORACLE_OFFLINE']['decision']='PASS';gate.durable(self.review,self.r);self.rejects(self.admit)
 def test_root_dependency_unresolved_cannot_consume_nested(self):
  self.rejects(self.admit,'OM-NESTED');root=self.admit();self.ledger.complete(root,dict(status='INCONCLUSIVE',scientific_cleanup=True));self.rejects(self.admit,'OM-NESTED')
  self.assertEqual(len(json.loads(self.ledger.path.read_text())['runs']),1)
 def test_root_qualified_allows_one_nested(self):
  root=self.admit();self.ledger.complete(root,dict(status='PARTIALLY_FEASIBLE',scientific_cleanup=True));self.admit('OM-NESTED');self.rejects(self.admit,'OM-NESTED')
 def test_optional_gpu_never_auto_admitted(self):
  for rid in ('GPU-G3','GPU-CTRL','OM-EXTRA'):self.rejects(self.admit,rid)
 def test_caps_duration_and_failed_reservation_spent(self):
  auth=self.admit()
  for _ in range(10):self.ledger.action_debit(auth,'capture')
  self.rejects(self.ledger.action_debit,auth,'capture')
  def expire(d):d['runs'][0]['started_ns']=time.monotonic_ns()-151_000_000_000;return None,d
  self.ledger.transaction(expire);self.rejects(self.ledger.action_debit,auth,'move');self.rejects(self.admit)
 def test_mode_symlink_hardlink_lock_attacks(self):
  self.ledger.path.chmod(0o644);self.rejects(self.admit);self.ledger.path.chmod(0o600)
  alias=self.ns/'hardlink';os.link(self.ledger.path,alias);self.rejects(self.admit);alias.unlink()
  lock=self.ledger.lock;lock.unlink();lock.symlink_to(self.manifest)
  with self.assertRaises(OSError):self.admit()
 def test_clean_environment_no_daily_authority(self):
  with patch.dict(os.environ,dict(SWAYSOCK='/run/user/daily',WAYLAND_DISPLAY='daily',DISPLAY=':0',LD_PRELOAD='evil',LD_LIBRARY_PATH='daily',WLR_RENDERER='daily',SMX_OOM_NONCE='daily')):
   e=gate.clean_environment(LAB)
  self.assertFalse(set(e)&{'SWAYSOCK','WAYLAND_DISPLAY','DISPLAY','LD_PRELOAD','LD_LIBRARY_PATH','WLR_RENDERER','SMX_OOM_NONCE'})
  self.assertTrue(all(Path(e[k]).is_relative_to(LAB) for k in ('TMPDIR','TMP','TEMP','XDG_CACHE_HOME','XDG_DATA_HOME','PYTHONPYCACHEPREFIX','CCACHE_DIR')))

 def test_concurrent_reservation_single_winner(self):
  from concurrent.futures import ThreadPoolExecutor
  def attempt(_):
   try:self.admit();return 'reserved'
   except ValueError:return 'refused'
  with ThreadPoolExecutor(max_workers=2) as pool:out=list(pool.map(attempt,range(2)))
  self.assertEqual(sorted(out),['refused','reserved']);self.assertEqual(len(json.loads(self.ledger.path.read_text())['runs']),1)
 def test_source_addition_and_mutation_after_freeze(self):
  import shutil
  source=self.ns/'portable-source';shutil.copytree(gate.SOURCE_ROOT,source)
  with patch.object(gate,'SOURCE_ROOT',source):
   self.validate();(source/'unexpected.py').write_text('unreviewed=True\n');self.rejects(self.admit)
   (source/'unexpected.py').unlink();(source/'graphics/plans.py').chmod(0o755);self.rejects(self.admit);(source/'graphics/plans.py').chmod(0o644);(source/'graphics/plans.py').write_text('# mutated\n');self.rejects(self.admit)
 def test_real_watchdog_independently_kills_owned_child(self):
  import signal,subprocess,threading
  from types import SimpleNamespace
  child=subprocess.Popen(['prlimit','--core=0:0','--',sys.executable,'-B','-c','import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); print("READY",flush=True); time.sleep(20)'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True,env=gate.clean_environment(LAB))
  self.assertEqual(child.stdout.readline().strip(),'READY')
  obj=SimpleNamespace(finished=threading.Event(),started=time.monotonic()-142.9,run=self.ns,proc_lock=threading.RLock(),expired=False,proc={'offline-owned-child':child},transient={})
  obj.signal_owned=lambda sig:engine.Session.signal_owned(obj,sig)
  thread=threading.Thread(target=engine.Session.watchdog,args=(obj,));thread.start()
  try:self.assertEqual(child.wait(timeout=4),-signal.SIGKILL);thread.join(timeout=1);self.assertTrue(obj.expired);self.assertFalse(thread.is_alive())
  finally:
   if child.poll() is None:os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=1)
   obj.finished.set();thread.join(timeout=1);child.stdout.close();child.stderr.close()

 def test_GPU_environment_and_same_identity_adapter(self):
  import gpu_handler
  from types import SimpleNamespace
  calls=[];session=SimpleNamespace(lab=LAB,spec=plans.RUNS['GPU-G3'],env=gate.clean_environment(LAB),debit=lambda *args:calls.append(args))
  adapter=gpu_handler.AdapterSession(session);self.assertEqual(adapter.spec['binary'],'gpu')
  adapter.env.update(MOSAIC_G3_DIR=str(LAB/'gpu-work/acquisition'),MOSAIC_G3_NONCE='a'*64,WLR_RENDERER='gles2')
  self.assertNotIn('MOSAIC_G3_DIR',session.env);self.assertEqual(session.compositor_environment['MOSAIC_G3_NONCE'],'a'*64)
  adapter.debit('mutation');self.assertEqual(calls,[('mutation','hook')]);self.rejects(adapter.debit,'hook')
  self.rejects(adapter.env.update,MOSAIC_G3_DIR='/run/user/daily',MOSAIC_G3_NONCE='a'*64,WLR_RENDERER='gles2')
  session.spec=dict(session.spec,binary='core');self.rejects(gpu_handler.AdapterSession,session)
 def test_GPU_gate_requires_independent_B4(self):
  self.rejects(self.admit,'GPU-G3');self.assertEqual(json.loads(self.ledger.path.read_text())['runs'],[])
  self.r['gates']['B4']=dict(status='PASS');gate.durable(self.review,self.r);self.rejects(self.admit,'GPU-G3')
 def test_GPU_binding_rejects_empty_or_unreviewed(self):
  import gpu_handler
  for case in ({},{'gpu_source_review':'ACCEPTED'},{'gpu_source_review':'ACCEPTED','gl_observability_preflight':'ACCEPTED','build_review':'ACCEPTED','native_gl_status':'FEASIBLE'}):
   self.rejects(gpu_handler.validate_binding,LAB,case,{},gate.sha(self.manifest))
 def test_GPU_module_origin_attack(self):
  import gpu_handler
  from types import SimpleNamespace
  from contextlib import ExitStack
  with ExitStack() as stack:
   for name in ('protocol','scenario','validate_source'):stack.enter_context(patch.dict(sys.modules,{name:SimpleNamespace(__file__='/foreign/'+name+'.py')}))
   self.rejects(gpu_handler.modules,LAB)

if __name__=='__main__':unittest.main(verbosity=2)
