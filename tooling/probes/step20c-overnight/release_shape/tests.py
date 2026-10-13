"""Offline fail-closed tests for the G smoke fixture; never launch compositor."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent)]
import adapter,gate
from horizontal_adapter import replace_one

class GOffline(unittest.TestCase):
    def test_c2_transform_unique_and_compiles(self):
        text=adapter.generate_g();compile(text,'G-smoke/runner.py','exec')
        self.assertEqual(text.count(adapter.G_IMPORT),1)
        self.assertIn("open_chain('E1')",text);self.assertIn('fresh_chain(',text)
        self.assertIn('dismissal(log',text);self.assertIn('final_restoration(baseline,final)',text)
        self.assertIn('BINARY.resolve() and sha(BINARY)==BINARY_SHA',text)
    def test_transform_rejects_missing_and_duplicate(self):
        for source in ('missing','x x'):
            with self.assertRaises(ValueError):replace_one(source,'x','y')
    def test_old_A_and_non_G_ELF_rejected(self):
        old_a=gate.LAB/'stage-static/usr/bin/swayfx-mosaic'
        with self.assertRaises(ValueError):gate.validate_binary_identity(old_a,'979dcd95ab43fa1e465d6e9d262485b73d186cedacd0f957059dd24f482ce6f4')
        with self.assertRaises(ValueError):gate.validate_binary_identity('/home/fy59/swayfx-mosaic-overnight-mcolx0gq/matrix/D4-mosaic/stage/usr/bin/swayfx-mosaic','0'*64)
        with self.assertRaises(ValueError):gate.validate_binary_identity('/usr/bin/sway','0'*64)
    def test_old_D_or_other_source_set_rejected(self):
        rows=dict(gate.TRACE_SOURCES);rows[next(iter(rows))]='0'*64
        with self.assertRaises(ValueError):gate.source_bindings({'trace_sources':rows})
    def test_wrong_wlroots_and_mutated_freeze_rejected(self):
        with self.assertRaises(ValueError):gate.validate_wlroots(gate.WLROOTS,'0'*64)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'input';p.write_bytes(b'changed')
            with self.assertRaises(ValueError):gate.validate_file_map({str(p):hashlib.sha256(b'original').hexdigest()})
    def test_quota_and_no_retry_rejected(self):
        state={'limits':{'scene_build':2,'mosaic_build':2,'stage':2,'run':18,'capture':220},
               'campaign_limits':{'C':3,'D1':2,'D2':2,'D3':2,'D4':2,'E1':1,'E2':1,'E3':2,'F':2,'G':1},
               'used':dict.fromkeys(('scene_build','mosaic_build','stage','run','capture'),0),
               'campaign_used':dict.fromkeys(('C','D1','D2','D3','D4','E1','E2','E3','F','G'),0),
               'runs':{},'events':[]}
        state['used']['capture']=204
        with patch('ledger._validate'):
            with self.assertRaises(ValueError):gate.validate_budget_room(state)
        with tempfile.TemporaryDirectory() as d:
            work=Path(d);(work/'consumed.json').write_text('{}')
            with self.assertRaises(ValueError):gate.validate_one_shot(work)
    def test_incomplete_frame_and_window_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            w=Path(d);(w/'results').mkdir();(w/'run').mkdir()
            with self.assertRaises(ValueError):gate.validate_capture_batch(w,[])
            with self.assertRaises(ValueError):gate.validate_window_results(w)
    def test_real_c2_events_satisfy_finish_predicate_and_mutations_fail(self):
        c2=gate.LAB/'horizontal/C2'
        evidence=(c2/'run/events.jsonl',c2/'actions.json',c2/'results/captures.json',
                  c2/'results/clicks.json',c2/'results/runtime.json')
        for path in evidence:
            self.assertTrue(path.is_file(),str(path))
            self.assertRegex(gate.sha(path),r'^[0-9a-f]{64}$')
        if (gate.WORK/'freeze.json').is_file():
            frozen=gate.expected_files()
            for path in evidence:self.assertEqual(frozen[str(path)],gate.sha(path),str(path))
        events=[json.loads(line) for line in evidence[0].read_text().splitlines()]
        state=json.loads(evidence[1].read_text())
        captures=json.loads(evidence[2].read_text())
        clicks=json.loads(evidence[3].read_text())
        runtime=json.loads(evidence[4].read_text())
        gate.validate_capture_batch(c2,captures)
        gate.validate_window_results(c2)
        valid=gate.finish_predicate(state,events,captures,clicks,runtime,True,True)
        self.assertTrue(valid['complete'],valid)
        self.assertEqual((valid['injections'],valid['click_injections'],
                          valid['standalone_move_injections'],valid['grabs']),(10,8,2,4))
        injections=[i for i,e in enumerate(events) if e.get('kind')=='injection']
        self.assertEqual(len(injections),10)
        missing=events[:injections[-1]]+events[injections[-1]+1:]
        extra=events+[dict(events[injections[0]])]
        wrong_action=[dict(e) for e in events]
        wrong_action[injections[1]]['action']='move'
        unknown_action=[dict(e) for e in events]
        unknown_action[injections[1]]['action']='unknown'
        for mutation in (missing,extra,wrong_action,unknown_action):
            with self.subTest(mutation=len(mutation)):
                self.assertFalse(gate.finish_predicate(
                    state,mutation,captures,clicks,runtime,True,True)['complete'])
    def test_preflight_refuses_absent_or_rejected_review_without_side_effects(self):
        if not (gate.WORK/'freeze.json').is_file():
            self.skipTest('review-gated preflight is exercised after the fresh freeze exists')
        real_root=gate.GROOT
        with tempfile.TemporaryDirectory() as d:
            review_dir=Path(d)/'reviews';review_dir.mkdir()
            absent=review_dir/'release-smoke-review.json'
            rejected=review_dir/'rejected.json'
            rejected.write_text(json.dumps({'status':'CORRECTION_REQUIRED'}))

            class RootWithIsolatedReview:
                def __truediv__(self, other):
                    if str(other)=='reviews/release-smoke-review.json':
                        return absent
                    return real_root/other

            budget=(gate.LAB/'budget.json').read_bytes()
            for path,expected in ((absent,'independent G smoke byte review missing'),
                                  (rejected,'G smoke review scope/status')):
                if path==absent:
                    self.assertFalse(absent.exists())
                else:
                    rejected.rename(absent)
                with patch.object(gate,'GROOT',RootWithIsolatedReview()):
                    with self.assertRaisesRegex(ValueError,expected):
                        gate.preflight(require_review=True)
                self.assertEqual((gate.LAB/'budget.json').read_bytes(),budget)
                self.assertFalse((gate.WORK/'consumed.json').exists())
                self.assertFalse((gate.WORK/'run').exists())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GOffline))
    data={'status':'PASS' if result.wasSuccessful() else 'FAIL','executed':result.testsRun,
          'skipped':[(str(t),reason) for t,reason in result.skipped],
          'failures':[(str(t),s) for t,s in result.failures], 'errors':[(str(t),s) for t,s in result.errors],
          'runtime':'NOT RUN','build':'NOT RUN','stage':'NOT RUN','review_acceptance_created':False}
    args.output.write_text(json.dumps(data,indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
