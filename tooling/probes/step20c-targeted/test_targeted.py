"""Offline source, persistent budget and actual D2/F evidence negatives."""
import argparse,copy,json,re,sys,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
import gate
from plans import RUNS,HIST
from geometry import *
from validators import held_configure,native_pairs
from cases import marker_host_baseline,root_state,associated_root
from transition import observed_epochs
DATA=HIST
class PureTests(unittest.TestCase):
    def test_compile_sources(self):
        for p in gate.HERE.glob('*.py'):compile(p.read_text(),str(p),'exec')
    def test_fixed_allocation(self):
        self.assertEqual(len(RUNS),13);self.assertLessEqual(sum(s['limits']['capture'] for s in RUNS.values()),174)
        for campaign,cap in gate.CAPS.items():self.assertLessEqual(sum(s['limits']['capture'] for s in RUNS.values() if s['campaign']==campaign),cap)
        self.assertTrue(all(s['limits']['capture']<=16 for s in RUNS.values()))
    def test_halfopen_and_scale(self):
        o=RUNS['scale-A']['outputs'][0]
        for p in ([-700,100],[-500,300],[-200,400]):self.assertEqual(png_global(global_png(p,o,'logical'),o,'logical'),p)
        self.assertFalse(contains([-800,0,800,600],[0,300]))
    def test_stale_invalidation(self):
        from engine import Session
        s=Session.__new__(Session);s.coordinate_epoch=4;s.proofs={(1,2):dict(epoch=4)};s.record=Mock();s.invalidate('focus')
        self.assertEqual(s.coordinate_epoch,5);self.assertEqual(s.proofs,{})
    def test_held_serial(self):
        before='ACK ns=1 serial=30 size=420x320\nxdg_surface#5.ack_configure(30)\nwl_shm_pool#6.create_buffer(8)\nCOMMIT ns=2'
        after='xdg_surface#5.configure(44)\nXDG_CONFIGURE ns=4 serial=44 size=300x200 hold=1 previous=0\nHELD ns=5 serial=44'
        self.assertEqual(held_configure(before,after,30)['serial'],44)
        for b,a,p in [(before,after+'\nxdg_surface#5.ack_configure(44)',30),(before,after.replace('.configure(44)','.configure(999)'),30),(before,after.replace('serial=44','serial=30').replace('configure(44)','configure(30)'),30),(before,after.replace('HELD','ABSENT'),30),(before.replace('ACK ns=1 serial=30','ABSENT'),after,30)]:
            with self.assertRaises(ValueError):held_configure(b,a,p)
    def test_pair_all_not12(self):
        text='\n'.join(f'PI_OUTPUT_COMMIT output=H1 commit_seq={i} ns={i*10}\nPI_OUTPUT_PRESENT output=H1 commit_seq={i} ns={i*10+1} presented=1' for i in range(1,20))
        r=native_pairs(text);self.assertEqual(r['paired'],19);self.assertEqual(r['missing'],0)
        r=native_pairs(text.replace('PI_OUTPUT_PRESENT output=H1 commit_seq=19','OMITTED output=H1 commit_seq=19'));self.assertEqual(r['missing'],1)
        with self.assertRaises(ValueError):native_pairs(text+'\nPI_OUTPUT_COMMIT output=H1 commit_seq=1 ns=500')
    def test_review_refusal_no_token(self):
        with patch.object(gate,'owned',return_value=Path('/missing')),patch.object(gate,'verify',side_effect=ValueError('review absent')),patch.object(gate,'locked') as locked:
            with self.assertRaises(ValueError):gate.begin('/missing','scale-A')
            locked.assert_not_called()
    def test_ledger_atomic_no_retry_and_reconciliation(self):
        with tempfile.TemporaryDirectory() as d:
            lab=Path(d);state=dict(scope=gate.SCOPE,runs={},events=[],used=dict(run=0,capture=0),campaign_used=dict.fromkeys(gate.CAPS,0),campaign_runs=dict.fromkeys(gate.CAPS,0));gate.durable(lab/'budget.json',state,True)
            with patch.object(gate,'owned',return_value=lab):
                def consume(s):
                    p=RUNS['scale-A']['limits'];s['runs']['scale-A']=dict(campaign='scale',planned=p,reserved=dict.fromkeys(p,0));s['used']['run']=1;s['campaign_runs']['scale']=1
                gate.locked(lab,consume);gate.action_debit(lab,'scale-A','capture','configuration','click')
                s=gate.read(lab/'budget.json');self.assertEqual(s['used']['capture'],1);self.assertEqual(s['runs']['scale-A']['reserved']['click'],1)
                bad=copy.deepcopy(s);bad['events'].pop()
                with self.assertRaises(ValueError):gate.validate(bad)
                gate.action_debit(lab,'scale-A',*(['capture']*11));before=(lab/'budget.json').read_bytes()
                with self.assertRaises(ValueError):gate.action_debit(lab,'scale-A','capture')
                self.assertEqual(before,(lab/'budget.json').read_bytes())
    def test_incomplete_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            lab=Path(d);gate.durable(lab/'offline.json',{'status':'PASS'},True)
            with self.assertRaises(ValueError):gate.test_receipt(lab,'offline.json',14)
            gate.durable(lab/'replay.json',{'status':'PASS'},True)
            with self.assertRaises(ValueError):gate.replay_receipt(lab)
    def test_geometry_held_unchanged_rejected(self):
        before='ACK ns=1 serial=30 size=420x320\nxdg_surface#5.ack_configure(30)\nwl_shm_pool#6.create_buffer(8)\nCOMMIT ns=2'
        after='xdg_surface#5.configure(44)\nXDG_CONFIGURE ns=4 serial=44 size=420x320 hold=1 previous=0\nHELD ns=5 serial=44'
        with self.assertRaises(ValueError):held_configure(before,after,30)
class HistoricalTests(unittest.TestCase):
    def fixture(self):
        run=DATA/'matrix/D2-mosaic/run';events=[json.loads(l) for l in (run/'events.jsonl').read_text().splitlines()];owner_start=next(e['ns'] for e in events if e['kind']=='spawn' and e['name']=='owner');trace=(run/'compositor.log').read_text()
        before=[]
        for l in trace.splitlines():
            m=re.search(r'\bns=(\d+)',l)
            if m and int(m[1])>=owner_start:break
            before.append(l)
        session=SimpleNamespace(spec={'marker':True,'mode':'mosaic'},proc={'marker-background':Mock(pid=77)},events=[e for e in events if e['ns']<owner_start],log=lambda n:'\n'.join(before),snapshot=lambda tag:json.loads((run/'startup-snapshot.json').read_text()),save=Mock());session.proc['marker-background'].poll.return_value=None
        with patch('cases.time.monotonic_ns',return_value=owner_start-1):baseline=marker_host_baseline(session)
        state=json.loads((run/'owner-geometry.json').read_text())
        epoch=next(e for e in observed_epochs(trace,'HEADLESS-1',0,999999999999999999) if e['scene'] and e['scene'].get('layout')=='5' and len(e['roots'])==2 and any(o.get('id')=='9' and list(map(int,o['scene'].split(',')))==state['scene'][:2] for o in e['owners']))
        raw='\n'.join(epoch['raw']);client=(run/'owner.log').read_text().split('POPUP_B DESTROY')[0].split('POPUP_B POPUP_DONE')[0];session.outputs=[dict(name='HEADLESS-1',logical=[-800,0,800,600])];session.log=lambda n:raw if n=='compositor' else client
        return session,state,raw,client,baseline
    def test_actual_D2_association(self):
        s,state,raw,client,b=self.fixture();r=root_state(s,state,state['origin'],b['window'][1]);self.assertNotEqual(r['tree'],b['tree']);self.assertEqual(len(r['states'][0]['all_roots']),2)
    def test_host_membership_negatives(self):
        s,state,raw,client,b=self.fixture();roots=observed_epochs(raw,'HEADLESS-1',0,999999999999999999)[0]['roots']
        for bad in ([roots[1]],roots+[dict(roots[1],tree='unknown')],[dict(roots[0],tree='unknown'),roots[1]],[dict(roots[0],clip_valid='1'),roots[1]],[roots[0],dict(roots[1],tree=roots[0]['tree'])],list(reversed(roots))):
            with self.assertRaises(ValueError):associated_root(bad,b,b['window'][1]+1)
        with self.assertRaises(ValueError):associated_root(roots,b,b['window'][1])
    def test_clip_owner_ancestry_negatives(self):
        s,state,raw,client,b=self.fixture();root=observed_epochs(raw,'HEADLESS-1',0,999999999999999999)[0]['roots'][1];clip=root['clip'].split(',');clip[0]=str(int(clip[0])+1);badclip=raw.replace('clip='+root['clip'],'clip='+','.join(clip));later=re.sub(r'ns=(\d+)',lambda m:'ns='+str(int(m[1])+100000),raw)
        for bad in (raw.replace(' id=9 ',' id=99 '),raw.replace('workspace=6','workspace=99'),badclip+'\n'+later):
            s.log=lambda n:bad if n=='compositor' else client
            with self.assertRaises(ValueError):root_state(s,state,state['origin'],b['window'][1])
        state=copy.deepcopy(state);state['workspace']['output']='HEADLESS-2'
        with self.assertRaises((ValueError,StopIteration)):root_state(s,state,state['origin'],b['window'][1])
    def test_all_historical_F_commits(self):
        raw=(DATA/'matrix/F-mosaic/run/compositor.log').read_text();r=native_pairs(raw);self.assertEqual(r['total_commits'],raw.count('PI_OUTPUT_COMMIT '));self.assertGreater(r['total_commits'],12);self.assertEqual(len(r['analyzed']),r['total_commits']);self.assertGreaterEqual(r['missing'],2)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--historical',type=Path,default=HIST);p.add_argument('--output',type=Path,required=True);a=p.parse_args();DATA=a.historical
    import io
    raw=io.StringIO();suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in (PureTests,HistoricalTests));result=unittest.TextTestRunner(stream=raw,verbosity=2).run(suite);log=a.output.with_suffix('.log');log.write_text(raw.getvalue());print(raw.getvalue())
    gate.durable(a.output,dict(status='PASS' if result.wasSuccessful() else 'FAIL',executed=result.testsRun,exit=0 if result.wasSuccessful() else 1,command=[sys.executable,*sys.argv],source_bindings=gate.source_bindings(),raw_output=str(log),raw_sha256=gate.sha(log),failures=[(str(t),e) for t,e in result.failures],errors=[(str(t),e) for t,e in result.errors],runtime='NOT RUN'),True);raise SystemExit(not result.wasSuccessful())
