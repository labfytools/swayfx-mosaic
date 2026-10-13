"""Executed pure/isolated negative tests, no synthetic independent review."""
import argparse,ast,copy,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from PIL import Image,ImageDraw
import gate
from protocols import RUNS
from geometry import *
from cases import parse_pairs,root_state,marker_host_baseline,associated_root
from transition import observed_epochs
from types import SimpleNamespace

class Tests(unittest.TestCase):
    def test_all_source_compile(self):
        for p in Path(__file__).parent.glob('*.py'):compile(p.read_text(),str(p),'exec')
    def test_all_campaigns_exact_unique(self):
        self.assertEqual(len(RUNS),14);self.assertEqual(set(r['campaign'] for r in RUNS.values()),{'D1','D2','D3','D4','E1','E2','E3','F'})
        for key,r in RUNS.items():
            self.assertEqual(key,r['id']);self.assertTrue(r['steps'] and r['preconditions'] and r['retention'] and r['stop_criteria'])
    def test_global_planned_png_fits(self):
        total=sum(gate.PLANNED_PNG[r['campaign']] for r in RUNS.values())+37+17
        self.assertLessEqual(total,220);self.assertEqual(total,212)
    def test_limits(self):
        for r in RUNS.values():
            self.assertLessEqual(r['limits']['duration_s'],150);self.assertLessEqual(gate.PLANNED_PNG[r['campaign']],12 if r['campaign']=='F' else 20)
    def test_exact_binary_review_pending_refusal_no_action(self):
        with patch.object(gate,'verify',side_effect=ValueError('missing independent review')),patch.object(gate.ledger,'reserve') as reserve:
            for key in RUNS:
                with self.assertRaises(ValueError):gate.preflight(key)
            reserve.assert_not_called()
    def test_half_open_negative_origin(self):
        self.assertTrue(contains([-800,0,800,600],[-1,599]));self.assertFalse(contains([-800,0,800,600],[0,599]));self.assertFalse(contains([-800,0,800,600],[-1,600]))
    def test_real_crossing_axis(self):
        self.assertTrue(crossing([70,585,170,130],1,600));self.assertFalse(crossing([70,600,170,130],1,600));self.assertFalse(crossing([70,470,170,130],1,600))
    def test_splith_ipc_decoration_not_double_added(self):
        o=dict(rect=dict(x=-400,y=25,width=400,height=575),window_rect=dict(x=2,y=0,width=396,height=573),deco_rect=dict(height=25))
        self.assertEqual(assigned_origin(o),[-398,25]);self.assertEqual(exterior_ipc(o),[-400,0,400,600])
    def test_applied_origin_source_identity(self):
        o=dict(id=42,window_rect=dict(x=2,y=0),deco_rect=dict(height=25))
        origin,r,_=actual_origin(o,'PI_OWNER output=HEADLESS-1 ns=1 id=42 scene_valid=1 scene=-400,0 applied_size=400,600')
        self.assertEqual(origin,[-398,25])
        with self.assertRaises(Ambiguous):actual_origin(o,'PI_OWNER output=HEADLESS-1 ns=1 id=99 scene_valid=1 scene=-400,0 applied_size=400,600')
    def test_scale_once_pointer_roundtrip(self):
        o=RUNS['D2-mosaic']['outputs'][0]
        for p in ([-700,100],[-500,300],[-200,400]):
            self.assertEqual(png_global(global_png(p,o,'logical'),o,'logical'),p)
    def test_rotated_pointer_roundtrip(self):
        o=RUNS['D3-mosaic']['outputs'][0]
        for p in ([-700,100],[-500,300],[-200,400]):self.assertEqual(png_global(global_png(p,o,'physical90'),o,'physical90'),p)
    def test_unknown_frame_reject(self):
        with self.assertRaises(Ambiguous):png_global([3,5],RUNS['D2-mosaic']['outputs'][0],'guessed')
    def test_marker_actual_orientation_and_missing_reject(self):
        im=Image.new('RGB',(1000,750));d=ImageDraw.Draw(im)
        for k,b in [('TL',(10,10,40,40)),('TR',(950,10,980,40)),('BL',(10,700,40,730)),('BR',(950,700,980,730)),('C',(480,350,510,380))]:d.rectangle(b,fill=MARKERS[k])
        self.assertEqual(marker_frame(im,1.25,False)['frame'],'logical')
        self.assertEqual(marker_frame(im.transpose(Image.Transpose.ROTATE_270),1.25,True)['frame'],'physical90')
        im.putpixel((10,10),(0,0,0));blank=Image.new('RGB',im.size)
        with self.assertRaises(Ambiguous):marker_frame(blank,1.25,True)
    def test_exact_rgb_one_pixel_reject(self):
        a=Image.new('RGB',(800,600),(48,48,56));b=a.copy();b.putpixel((0,599),(48,48,55))
        with self.assertRaises(Ambiguous):exact(a,b)
    def test_output_physical_logical_scale_mismatch_reject(self):
        spec=RUNS['D3-mosaic']['outputs'];outputs=[]
        for o in spec:outputs.append(dict(active=True,name=o['name'],rect=dict(zip(('x','y','width','height'),o['logical'])),scale=o['scale'],transform=o['transform'],current_mode=dict(zip(('width','height'),o['mode']))))
        expected_outputs(outputs,spec)
        for key in ('scale','transform'):
            bad=copy.deepcopy(outputs);bad[0][key]=1 if key=='scale' else 90
            with self.assertRaises(Ambiguous):expected_outputs(bad,spec)
    def test_no_synthetic_saved_identity(self):
        r=RUNS['E2-mosaic'];self.assertTrue(any('saved-node' in x for x in r['ceilings']))
        code=Path(__file__).with_name('cases.py').read_text();self.assertIn("saved_node_identity='NOT OBSERVABLE'",code);self.assertNotIn('release_configure',code)
    def test_pairs_same_output_seq_only_and_missing(self):
        text='PI_OUTPUT_COMMIT output=H1 commit_seq=7 ns=1\nPI_OUTPUT_PRESENT output=H2 commit_seq=7 ns=2\n'
        a=parse_pairs(text);self.assertEqual(a['analyzed'][0]['status'],'MISSING_PRESENT')
        a=parse_pairs(text+'PI_OUTPUT_PRESENT output=H1 commit_seq=7 ns=3\n');self.assertEqual(a['analyzed'][0]['status'],'PAIRED')
    def test_duplicate_present_rejected(self):
        line='PI_OUTPUT_PRESENT output=H1 commit_seq=7 ns=2\n'
        with self.assertRaises(Ambiguous):parse_pairs(line+line)
    def test_pair_limit12(self):
        text=''.join(f'PI_OUTPUT_COMMIT output=H1 commit_seq={i} ns={i+1}\n' for i in range(30));r=parse_pairs(text)
        self.assertEqual(len(r['analyzed']),12);self.assertEqual(r['total_commits'],30)
    def test_owned_cleanup_and_explicit_IPC_source(self):
        tree=ast.parse(Path(__file__).with_name('engine.py').read_text());code=ast.unparse(tree)
        self.assertIn("['swaymsg', '-s', str(self.sock)",code);self.assertIn('start_new_session=True',code);self.assertIn('0o700',Path(__file__).with_name('engine.py').read_text())
        self.assertNotIn('shell=True',code);self.assertNotIn('os.killpg(0',code)
    def test_every_campaign_callable(self):
        from cases import CAMPAIGN
        self.assertEqual(set(CAMPAIGN),set(r['campaign'] for r in RUNS.values()))
    def test_cleanup_available_before_start(self):
        from engine import Session
        self.assertTrue(hasattr(Session,'start') and hasattr(Session,'cleanup'))
    def test_local_exhaustion_before_global(self):
        with tempfile.TemporaryDirectory() as d:
            lab=Path(d);w=lab/'matrix/D1-mosaic';w.mkdir(parents=True)
            gate.exclusive(w/'actions.json',dict(planned={'capture':1},reserved={'capture':1},events=[]))
            with patch.object(gate,'LAB',lab),patch.object(gate.ledger,'reserve') as reserve:
                with self.assertRaises(ValueError):gate.action_debit('D1-mosaic','capture')
                reserve.assert_not_called()
    def test_corrupt_local_ledger_rejected(self):
        limits=gate.action_limits('D1-mosaic');state=dict(planned=limits,reserved=dict.fromkeys(limits,0),events=[])
        gate.local_valid('D1-mosaic',state)
        for kind in ('typed','reconciliation','limits'):
            bad=copy.deepcopy(state)
            if kind=='typed':bad['reserved']['capture']=True
            elif kind=='reconciliation':bad['reserved']['capture']=1
            else:bad['planned']['capture']+=1
            with self.assertRaises(ValueError):gate.local_valid('D1-mosaic',bad)
    def test_unknown_action_before_global(self):
        with tempfile.TemporaryDirectory() as d:
            lab=Path(d);w=lab/'matrix/D1-mosaic';w.mkdir(parents=True)
            gate.exclusive(w/'actions.json',dict(planned={'capture':1},reserved={'capture':0},events=[]))
            with patch.object(gate,'LAB',lab):
                with self.assertRaises(ValueError):gate.action_debit('D1-mosaic','force_timer')

class RepairTests(unittest.TestCase):
    def fixture(self):
        run=gate.LAB/'horizontal/C2/run'
        trace=(run/'compositor.log').read_text();client=(run/'E2.log').read_text().split('POPUP_B DESTROY')[0]
        epoch=next(e for e in observed_epochs(trace,'HEADLESS-1',0,999999999999999999)
                   if e['scene'] and e['scene'].get('layout')=='5' and len(e['roots'])==1)
        o=next(o for o in epoch['owners'] if o['id']=='9');scene=list(map(int,o['scene'].split(',')))+list(map(int,o['applied_size'].split(',')))
        x,y,w,h=map(int,o['current'].split(','));owner=dict(id=9,type='con',app_id='org.mosaic.NestedGrabProbe',visible=True,rect=dict(x=x,y=y+25,width=w,height=h-25),window_rect=dict(x=2,y=0,width=w-4,height=h-27),deco_rect=dict(height=25))
        ws=dict(id=6,type='workspace',layout='mosaic',output='HEADLESS-1',nodes=[owner],floating_nodes=[])
        tree=dict(id=1,type='root',nodes=[dict(id=2,type='output',name='HEADLESS-1',nodes=[ws],floating_nodes=[])],floating_nodes=[])
        state=dict(owner=owner,workspace=ws,scene=scene,origin=[scene[0]+2,scene[1]+25],snapshot=dict(tree=tree))
        raw='\n'.join(epoch['raw']);session=SimpleNamespace(outputs=[dict(name='HEADLESS-1',logical=[-800,0,800,600])],log=lambda n:raw if n=='compositor' else client)
        return session,state,raw
    def test_real_C_callback_positive(self):
        s,state,raw=self.fixture();self.assertEqual(root_state(s,state,state['origin'],0)['states'][0]['state'],'applied-target')
    def test_malformed_callbacks_rejected(self):
        s,state,raw=self.fixture()
        mutations=[raw.replace(' id=9 ',' id=99 '), '\n'.join(l for l in raw.splitlines() if 'PI_OWNER ' not in l),raw.replace('local_index=1','local_index=2'),raw.replace('workspace=6','workspace=99'),raw.replace('output=HEADLESS-1','output=HEADLESS-2'),raw+'\n'+next(l for l in raw.splitlines() if 'PI_POPUP ' in l),raw.replace('clip=-482,-25,800,600','clip=-481,-25,800,600')]
        # Mutate the observed root x regardless of this retained callback's origin.
        import re
        mutations.append(re.sub(r'(PI_POPUP .*clip=)(-?\d+)',lambda m:m[1]+str(int(m[2])+1),raw))
        for bad in mutations:
            with self.subTest(bad=bad[-120:]),self.assertRaises((ValueError,AssertionError)):
                s.log=lambda n:bad if n=='compositor' else (gate.LAB/'horizontal/C2/run/E2.log').read_text().split('POPUP_B DESTROY')[0];root_state(s,state,state['origin'],0)
    def test_missing_ancestry_and_origin_rejected(self):
        s,state,raw=self.fixture();bad=copy.deepcopy(state);bad['origin'][0]+=1
        with self.assertRaises(ValueError):root_state(s,bad,bad['origin'],0)
        bad=copy.deepcopy(state);bad['workspace']['id']=99
        with self.assertRaises(ValueError):root_state(s,bad,bad['origin'],0)
    def test_real_hierarchy_parent_and_missing_grab_rejected(self):
        s,state,raw=self.fixture();client=(gate.LAB/'horizontal/C2/run/E2.log').read_text().split('POPUP_B DESTROY')[0]
        for bad in (client.replace('parent_xdg=12','parent_xdg=999'),client.replace('POPUP_B GRAB_REQUEST','POPUP_B OMITTED_GRAB_REQUEST')):
            s.log=lambda n:raw if n=='compositor' else bad
            with self.assertRaises((ValueError,AssertionError)):root_state(s,state,state['origin'],0)
    def test_complete_nonbuffer_callback_preserved(self):
        s,state,raw=self.fixture();client=(gate.LAB/'horizontal/C2/run/E2.log').read_text().split('POPUP_B DESTROY')[0]
        s.log=lambda n:raw.replace('has_buffer=1','has_buffer=0') if n=='compositor' else client
        self.assertEqual(len(root_state(s,state,state['origin'],0)['states']),1)

    def test_old_applied_hidden_return_and_stale_rejection(self):
        import re
        s,state,raw=self.fixture();hidden=copy.deepcopy(state)
        hidden['scene'][0]-=1600;hidden['origin'][0]-=1600;hidden['owner']['rect']['x']-=1600
        def shifted(text):
            text=re.sub(r'ns=(\d+)',lambda m:'ns='+str(int(m[1])+100000),text)
            text=re.sub(r'(PI_OWNER .*id=9 current=)(-?\d+)',lambda m:m[1]+str(int(m[2])-1600),text)
            text=re.sub(r'(PI_OWNER .*id=9 .*scene=)(-?\d+)',lambda m:m[1]+str(int(m[2])-1600),text)
            return re.sub(r'(PI_POPUP .*clip=)[^ ]+',r'\g<1>0,0,0,0',text)
        hidden_raw=shifted(raw);client=(gate.LAB/'horizontal/C2/run/E2.log').read_text().split('POPUP_B DESTROY')[0]
        s.log=lambda n:raw+'\n'+hidden_raw if n=='compositor' else client
        result=root_state(s,hidden,hidden['origin'],0,True,previous=state)
        self.assertEqual([r['state'] for r in result['states']],['old-applied','applied-target'])
        returned=re.sub(r'ns=(\d+)',lambda m:'ns='+str(int(m[1])+200000),raw)
        s.log=lambda n:hidden_raw+'\n'+returned if n=='compositor' else client
        self.assertEqual(len(root_state(s,state,state['origin'],0,previous=hidden)['states']),2)
        stale=re.sub(r'ns=(\d+)',lambda m:'ns='+str(int(m[1])+300000),hidden_raw)
        s.log=lambda n:hidden_raw+'\n'+returned+'\n'+stale if n=='compositor' else client
        with self.assertRaises(ValueError):root_state(s,state,state['origin'],0,previous=hidden)
    def test_earlier_bad_clip_then_good_rejected(self):
        import re
        s,state,raw=self.fixture();client=(gate.LAB/'horizontal/C2/run/E2.log').read_text().split('POPUP_B DESTROY')[0]
        bad=re.sub(r'(PI_POPUP .*clip=)(-?\d+)',lambda m:m[1]+str(int(m[2])+1),raw)
        good=re.sub(r'ns=(\d+)',lambda m:'ns='+str(int(m[1])+100000),raw)
        s.log=lambda n:bad+'\n'+good if n=='compositor' else client
        with self.assertRaises(ValueError):root_state(s,state,state['origin'],0)

    def test_cleanup_preserves_actual_ipc_on_wait_timeout(self):
        from engine import Session
        import subprocess,time,threading
        with tempfile.TemporaryDirectory() as d:
            s=Session.__new__(Session);s.run=Path(d);s.runtime=s.run/'runtime';s.runtime.mkdir();s.sock=Mock();s.sock.is_socket.return_value=True;s.env={};s.pointer=None;s.handles=[];s.started=time.monotonic();s.expired=False;s.finished=threading.Event();s.watch=Mock()
            comp=Mock(pid=2147483647,returncode=0,stdin=None);comp.poll.side_effect=[None,0,0];comp.wait.side_effect=subprocess.TimeoutExpired('compositor',1);s.comp=comp;s.proc={'compositor':comp}
            with patch('engine.subprocess.run',return_value=SimpleNamespace(returncode=1,stdout='actual IPC stdout',stderr='actual IPC stderr')),patch('engine.os.killpg',side_effect=ProcessLookupError):
                self.assertEqual(s.cleanup('PASS'),'INCONCLUSIVE')
            terminal=json.loads((s.run/'terminal-ipc.json').read_text());out=json.loads((s.run/'outcome.json').read_text())
            self.assertEqual(terminal['ipc_exit'],1);self.assertEqual(terminal['stdout'],'actual IPC stdout');self.assertEqual(terminal['stderr'],'actual IPC stderr');self.assertIn('wait_error',terminal);self.assertEqual(out['measurements_status'],'PASS');self.assertEqual(out['processes'][0]['exit'],0)

class RotationTests(unittest.TestCase):
    def fixture(self):
        run=gate.LAB/'matrix/D2-mosaic/run';events=[json.loads(l) for l in (run/'events.jsonl').read_text().splitlines()]
        owner_start=next(e['ns'] for e in events if e['kind']=='spawn' and e['name']=='owner')
        trace=(run/'compositor.log').read_text()
        # Retain only the complete pre-owner native prefix for baseline. The
        # selected mapped epoch is from actual D2; it does not reclassify D2.
        # Later textual lines without ns could include cleanup: preserve the
        # prefix only, as live observation would do before owner creation.
        first_owner_line=next(i for i,l in enumerate(trace.splitlines()) if 'PI_OWNER ' in l and ' id=9 ' in l)
        before='\n'.join(trace.splitlines()[:first_owner_line])
        first_after=next(i for i,l in enumerate(before.splitlines()) if 'ns=' in l and int(__import__('re').search(r'ns=(\d+)',l)[1])>=owner_start)
        before='\n'.join(before.splitlines()[:first_after])
        session=SimpleNamespace(spec={'id':'D3-mosaic'},proc={'marker-background':Mock(pid=77)},events=[e for e in events if e['ns']<owner_start],log=lambda n:before,
            snapshot=lambda tag:json.loads((run/'startup-snapshot.json').read_text()),save=Mock())
        session.proc['marker-background'].poll.return_value=None
        with patch('cases.time.monotonic_ns',return_value=owner_start-1):baseline=marker_host_baseline(session)
        state=json.loads((run/'owner-geometry.json').read_text())
        epoch=next(e for e in observed_epochs(trace,'HEADLESS-1',0,999999999999999999) if e['scene'] and e['scene'].get('layout')=='5' and len(e['roots'])==2 and any(o.get('id')=='9' and list(map(int,o['scene'].split(',')))==state['scene'][:2] for o in e['owners']))
        raw='\n'.join(epoch['raw']);client=(run/'owner.log').read_text().split('POPUP_B DESTROY')[0].split('POPUP_B POPUP_DONE')[0]
        session.outputs=[dict(name='HEADLESS-1',logical=[-800,0,800,600])];session.log=lambda n:raw if n=='compositor' else client
        return session,state,raw,client,baseline
    def test_actual_D2_known_preowner_host_and_new_root(self):
        s,state,raw,client,baseline=self.fixture();result=root_state(s,state,state['origin'],baseline['window'][1])
        self.assertNotEqual(result['tree'],baseline['tree']);self.assertEqual(len(result['states'][0]['all_roots']),2)
        self.assertEqual(result['states'][0]['root']['local_index'],'2')
    def test_unknown_host_multiple_new_and_missing_known_rejected(self):
        s,state,raw,client,baseline=self.fixture();roots=observed_epochs(raw,'HEADLESS-1',0,999999999999999999)[0]['roots']
        for bad in ([roots[1]],roots+[dict(roots[1],tree='0xunknown',local_index='3')], [dict(roots[0],tree='0xunknown'),roots[1]], [dict(roots[0],clip_valid='1'),roots[1]], [roots[0],dict(roots[1],tree=roots[0]['tree'])]):
            with self.assertRaises(ValueError):associated_root(bad,baseline,baseline['window'][1]+1)
        with self.assertRaises(ValueError):associated_root(roots,baseline,baseline['window'][1])
    def test_wrong_owner_workspace_and_earlier_clip_rejected(self):
        import re
        s,state,raw,client,baseline=self.fixture()
        root=observed_epochs(raw,'HEADLESS-1',0,999999999999999999)[0]['roots'][1]
        badclip=raw.replace('clip='+root['clip'],'clip='+str(int(root['clip'].split(',')[0])+1)+','+','.join(root['clip'].split(',')[1:]))
        later=re.sub(r'ns=(\d+)',lambda m:'ns='+str(int(m[1])+100000),raw)
        for bad in (raw.replace(' id=9 ',' id=99 '),raw.replace('workspace=6','workspace=99'),badclip+'\n'+later):
            s.log=lambda n:bad if n=='compositor' else client
            with self.assertRaises(ValueError):root_state(s,state,state['origin'],baseline['window'][1])
    def test_v3_gate_disallows_every_old_case_before_debit(self):
        with patch.object(gate,'verify',return_value={}),patch.object(gate.ledger,'reserve') as reserve:
            for key in gate.RUNS:
                if key!='D3-mosaic':
                    with self.assertRaisesRegex(ValueError,'only unused D3'):gate.preflight(key)
            reserve.assert_not_called()
    def test_executed_v2_archive_exact(self):
        archive=gate.LAB/'matrix/executed-v2-archive';f=gate.read(archive/'freeze.json');mapping=gate.read(archive/'archive-map.json')
        self.assertEqual(gate.sha(archive/'freeze.json'),'a20ccb39095ca35363119b5cfe4b5c839c1a75863bd72a097686aeac76dd7d7f')
        self.assertEqual(set(mapping),set(f['files']))
        for original,digest in f['files'].items():self.assertEqual(gate.sha(mapping[original]),digest,original)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in (Tests,RepairTests,RotationTests)]);names=[t.id() for group in suite for t in group];r=unittest.TextTestRunner(verbosity=2).run(suite)
    gate.exclusive(a.output,dict(status='PASS' if r.wasSuccessful() else 'FAIL',executed=r.testsRun,tests=names,failures=[(str(t),e) for t,e in r.failures],errors=[(str(t),e) for t,e in r.errors],runtime='NOT RUN',acceptance_created=False))
    raise SystemExit(not r.wasSuccessful())
