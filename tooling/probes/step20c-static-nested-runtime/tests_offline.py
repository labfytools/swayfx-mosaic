#!/usr/bin/env python3
"""File-backed authorization attacks and real ledger tests, never runtime.

CONTRACT: immutable LAB/historical files are never edited by negative tests.
Alternate records model received corrupt inputs; actual verification functions
still execute. Manifest attacks use real disposable files and real SHA checks.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import handoff as h

LAB = None


class Gate(unittest.TestCase):
    def auth_attack(self, key, value):
        auth = h.read(LAB / 'results/authorization.json')
        auth[key] = value
        with tempfile.TemporaryDirectory(prefix='nested-auth-negative-') as tmp:
            p = Path(tmp) / 'authorization.json'
            p.write_text(json.dumps(auth))
            with self.assertRaises((ValueError, AssertionError, OSError, KeyError)):
                h.preflight(LAB, p, review=False)

    def record_attack(self, name, change):
        actual = h.read
        def read(path):
            value = actual(path)
            if Path(path) == LAB / 'results' / name:
                value = copy.deepcopy(value)
                change(value)
            return value
        with patch.object(h, 'read', read):
            with self.assertRaises((ValueError, AssertionError, OSError, KeyError)):
                h.preflight(LAB, LAB / 'results/authorization.json', review=False)

    def test_positive_real_preflight_without_review(self):
        r = h.preflight(LAB, LAB / 'results/authorization.json', review=False)
        self.assertEqual(r['handoff'], 'PENDING_INDEPENDENT_REVIEW')
        self.assertFalse(r['run_reserved'])

    def test_no_authorization(self):
        with self.assertRaises(ValueError):
            h.preflight(LAB, None, review=False)

    def test_old_ticket(self):
        self.auth_attack('ticket', 'SWAYFX_MOSAIC_STEP20C_NESTED_OFFLINE_FREEZE_AND_RECEIPT_INTEGRITY_V1')

    def test_wrong_lab(self):
        self.auth_attack('registered_lab', str(h.OLD_LAB))

    def test_exhausted_historical_lab(self):
        auth = h.read(LAB / 'results/authorization.json')
        old = Path('/home/fy59/swayfx-mosaic-static-nested-grab-m0a5e2qh')
        auth['registered_lab'] = str(old)
        with tempfile.TemporaryDirectory(prefix='nested-old-lab-negative-') as tmp:
            p = Path(tmp) / 'authorization.json'
            p.write_text(json.dumps(auth))
            with self.assertRaises(ValueError):
                h.preflight(old, p, review=False)

    def test_wrong_owner(self):
        self.auth_attack('owner_registry', '/tmp/nonexistent-old-campaign-owner')

    def test_wrong_uid(self):
        self.auth_attack('uid', h.os.getuid() + 1)

    def test_wrong_binary(self):
        self.auth_attack('binary', '/usr/bin/sway')

    def test_wrong_binary_hash(self):
        self.auth_attack('binary_sha256', '0' * 64)

    def test_wrong_wlroots(self):
        self.auth_attack('wlroots_sha256', '0' * 64)

    def test_wrong_fixture_hash(self):
        self.auth_attack('fixture_sha256', '0' * 64)

    def test_review_not_accepted_original_gate(self):
        # The unchanged authorize() reads the actual file-backed gate/review.
        # Preserve original accepted bytes in an isolated negative-test LAB,
        # then downgrade its review; no accepted review is invented.
        with tempfile.TemporaryDirectory(prefix='nested-review-negative-') as tmp:
            lab = Path(tmp)
            (lab / 'results').mkdir()
            auth = h.read(LAB / 'results/authorization.json')
            auth['registered_lab'] = str(lab)
            (lab / 'auth.json').write_text(json.dumps(auth))
            (lab / 'results/offline-gate.json').write_bytes((LAB / 'results/offline-gate.json').read_bytes())
            review = h.read(LAB / 'results/independent-review.json')
            review['status'] = 'CORRECTION_REQUIRED'
            (lab / 'results/independent-review.json').write_text(json.dumps(review))
            with self.assertRaises(ValueError):
                h.authorize(lab, lab / 'auth.json')

    def test_offline_gate_not_ready_original_gate(self):
        with tempfile.TemporaryDirectory(prefix='nested-ready-negative-') as tmp:
            lab = Path(tmp)
            (lab / 'results').mkdir()
            auth = h.read(LAB / 'results/authorization.json')
            auth['registered_lab'] = str(lab)
            (lab / 'auth.json').write_text(json.dumps(auth))
            gate = h.read(LAB / 'results/offline-gate.json')
            gate['marker'] = 'INCONCLUSIVE'
            (lab / 'results/offline-gate.json').write_text(json.dumps(gate))
            (lab / 'results/independent-review.json').write_bytes((LAB / 'results/independent-review.json').read_bytes())
            with self.assertRaises(ValueError):
                h.authorize(lab, lab / 'auth.json')

    def test_missing_manifest(self):
        actual = h.verify
        with tempfile.TemporaryDirectory(prefix='nested-manifest-negative-') as tmp:
            missing = Path(tmp) / 'absent'
            def verify(path):
                return actual(missing if Path(path) == LAB / 'results/fixture-freeze-sha256.txt' else path)
            with patch.object(h, 'verify', verify), self.assertRaises(OSError):
                h.preflight(LAB, LAB / 'results/authorization.json', review=False)

    def test_changed_manifest_entry(self):
        actual = h.verify
        with tempfile.TemporaryDirectory(prefix='nested-manifest-negative-') as tmp:
            manifest = Path(tmp) / 'fixture-freeze-sha256.txt'
            rows = (LAB / 'results/fixture-freeze-sha256.txt').read_text().splitlines(True)
            rows[0] = '0' * 64 + rows[0][64:]
            manifest.write_text(''.join(rows))
            def verify(path):
                return actual(manifest if Path(path) == LAB / 'results/fixture-freeze-sha256.txt' else path)
            with patch.object(h, 'verify', verify), self.assertRaises(AssertionError):
                h.preflight(LAB, LAB / 'results/authorization.json', review=False)

    def test_run_already_consumed(self):
        def consume(b):
            b['used']['run'] = 1
            b['events'] = [dict(seq=0, kind='run', ns=1)]
        self.record_attack('budget.json', consume)

    def test_dispatch_already_consumed(self):
        with tempfile.TemporaryDirectory(prefix='nested-consumed-negative-') as tmp:
            p = Path(tmp) / 'spent'
            p.write_text('consumed')
            with patch.object(h, 'SPENT', p), self.assertRaises(ValueError):
                h.preflight(LAB, LAB / 'results/authorization.json', review=False)

    def test_durable_exclusive_consumption(self):
        with tempfile.TemporaryDirectory(prefix='nested-exclusive-test-') as tmp:
            p = Path(tmp) / 'spent'
            h.exclusive(p, dict(ticket=h.TICKET))
            before = p.read_bytes()
            with self.assertRaises(FileExistsError):
                h.exclusive(p, dict(ticket='second'))
            self.assertEqual(p.read_bytes(), before)

    def test_ledger_exhaustion_and_atomic_bundle(self):
        from ledger import initial_for_offline_test, reserve
        with tempfile.TemporaryDirectory(prefix='geometry-ledger-test-') as tmp:
            p = Path(tmp) / 'budget.json'
            initial_for_offline_test(p)
            reserve(p, 'run')
            before = p.read_bytes()
            with self.assertRaises(ValueError):
                reserve(p, 'run', 'click')
            self.assertEqual(p.read_bytes(), before)
            self.assertEqual(h.valid(h.read(p))['used']['run'], 1)


if __name__ == '__main__':
    import sys
    LAB = Path(sys.argv[1]).resolve()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Gate))
    h.exclusive(LAB / 'results/preflight-tests.json', dict(status='PASS' if result.wasSuccessful() else 'FAIL',
                tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                source_sha256=h.sha(Path(__file__)), run_reserved=False, runtime_runs=0))
    raise SystemExit(0 if result.wasSuccessful() else 1)
