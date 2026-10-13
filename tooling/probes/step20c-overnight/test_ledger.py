"""WHY: validate irreversible debits and concurrent reservation bounds offline."""
import concurrent.futures
import json
from pathlib import Path
import tempfile
import unittest
from ledger import initialize, reserve

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'budget.json'
        initialize(self.path)
    def test_no_reset_and_no_refund(self):
        reserve(self.path, 'scene_build')
        with self.assertRaises(FileExistsError): initialize(self.path)
        self.assertEqual(json.loads(self.path.read_text())['used']['scene_build'], 1)
    def test_concurrent_exhaustion(self):
        def attempt(_):
            try: reserve(self.path, 'mosaic_build'); return True
            except RuntimeError: return False
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(attempt, range(16))), 2)
    def test_run_and_capture_bounds(self):
        reserve(self.path, 'run', campaign='F', run_id='f1')
        reserve(self.path, 'capture', run_id='f1', amount=12)
        with self.assertRaises(RuntimeError): reserve(self.path, 'capture', run_id='f1')
        reserve(self.path, 'run', campaign='F', run_id='f2')
        with self.assertRaises(RuntimeError): reserve(self.path, 'run', campaign='F', run_id='f3')
    def test_invalid_does_not_debit(self):
        for kwargs in ({'campaign':'C','run_id':'c','duration_s':151}, {'campaign':'C','run_id':'c','amount':2}):
            with self.assertRaises(ValueError): reserve(self.path, 'run', **kwargs)
        with self.assertRaises(ValueError): reserve(self.path, 'capture', run_id='missing')
        self.assertEqual(json.loads(self.path.read_text())['events'], [])
    def test_corrupted_persistence_fails_closed(self):
        original = self.path.read_text()
        for mutate in (
            lambda s: s['used'].update(scene_build=-1),
            lambda s: s['used'].update(scene_build=True),
            lambda s: s['used'].update(scene_build=1),
            lambda s: s['events'].append({'sequence':0,'kind':'run','amount':1,'campaign':'C','run_id':'x','reserved_at_ns':1}),
            lambda s: s['runs'].update(x={'campaign':'C','captures':0,'duration_s':150}),
        ):
            state = json.loads(original); mutate(state)
            corrupted = json.dumps(state); self.path.write_text(corrupted)
            with self.assertRaises(RuntimeError): reserve(self.path, 'stage')
            self.assertEqual(self.path.read_text(), corrupted)
if __name__ == '__main__': unittest.main()
