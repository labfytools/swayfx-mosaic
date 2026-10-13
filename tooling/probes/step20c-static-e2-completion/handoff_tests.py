"""Isolated preflight mutations. No real owner/review/token is created.

All simulated accepted records are confined to TemporaryDirectory; mocked gate
validation avoids claiming historical or prospective runtime acceptance.
"""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from contextlib import ExitStack
import handoff as h
from model import Invalid
from ledger import LIMITS
from support import sha

class Handoff(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='e2-handoff-tests-');self.root=Path(self.tmp.name)
        self.lab=self.root/'swayfx-mosaic-e2-completion-synthetic';self.lab.mkdir(mode=0o700)
        for n in ('results','raw','fixture','client-source','offline'):(self.lab/n).mkdir()
        self.stack=ExitStack()
        for name,value in [('REGISTRY',self.root/'owner'),('REGISTRATION',self.root/'registration.json'),('SPENT',self.root/'spent.json'),
                           ('BINARY',self.root/'binary'),('WLROOTS',self.root/'wlroots'),('SOURCE_FILES',{})]:
            self.stack.enter_context(patch.object(h,name,value))
        h.BINARY.write_bytes(b'synthetic binary');h.WLROOTS.write_bytes(b'synthetic wlroots')
        self.stack.enter_context(patch.object(h,'BINARY_SHA',sha(h.BINARY)));self.stack.enter_context(patch.object(h,'WLROOTS_SHA',sha(h.WLROOTS)))
        self.stack.enter_context(patch('gate.validate_gate',return_value={'status':'SYNTHETIC_TEST_ONLY'}))
        for p in h.HERE.iterdir():
            if p.is_file():(self.lab/'fixture'/p.name).write_bytes(p.read_bytes())
        for n in ('nested-client','pointer-daemon','static-reference'):(self.lab/n).write_bytes(b'synthetic client')
        (self.lab/'swayfx-mosaic').write_bytes(h.BINARY.read_bytes())
        for n in ('offline-gate.json','test-receipts.json','replay.json','source-audit.json'):(self.lab/'offline'/n).write_text('{}')
        h.exclusive(h.REGISTRY,str(self.lab)+'\n');h.exclusive(self.lab/'campaign-owner',str(h.REGISTRY)+'\n')
        for n in ('ELF','symbols','relocations'):(self.lab/'raw'/(n+'.json')).write_text('{}')
        self.write('binary-identity',dict(status='PASS',build_id=h.BUILD_ID,binary_sha256=h.BINARY_SHA,wlroots_sha256=h.WLROOTS_SHA,raw={}))
        manifest=self.lab/'results/fixture-freeze-sha256.txt'
        manifest.write_text(''.join(sha(p)+'  '+str(p)+'\n' for p in h.immutable_paths(self.lab)))
        frozen=h.verify(manifest)
        reg=dict(ticket=h.TICKET,lab=str(self.lab),owner_registry=str(h.REGISTRY),uid=os.getuid(),token='a'*64,
            fixture_sha256=frozen['sha256'],binary=str(h.BINARY),binary_sha256=h.BINARY_SHA,wlroots_sha256=h.WLROOTS_SHA)
        h.exclusive(h.REGISTRATION,reg);self.write('registration',reg)
        self.auth={**reg,'registered_lab':str(self.lab),'scope':'one-new-static-e2-completion-headless-run','explicit_user_authorization':True}
        h.exclusive(self.lab/'results/authorization.json',self.auth)
        self.write('budget',dict(limits=LIMITS,used=dict.fromkeys(LIMITS,0),events=[]))
        self.write('offline-gate',dict(marker=h.MARKER,status='READY_FOR_REVIEW',fixture_sha256=frozen['sha256'],offline_gate_sha256=sha(self.lab/'offline/offline-gate.json')))
        self.write('runtime-handoff',dict(status='PREPARED_FOR_INDEPENDENT_REVIEW',ticket=h.TICKET,lab=str(self.lab),fixture=frozen,
            source_sha256=h.source_map(),source_contract=h.source_bindings(),authorization_sha256=sha(self.lab/'results/authorization.json'),
            registration_sha256=sha(h.REGISTRATION),gate_sha256=sha(self.lab/'offline/offline-gate.json'),
            transfers=[dict(source=str(h.BINARY),destination=str(self.lab/'swayfx-mosaic'),sha256=h.BINARY_SHA)]))
        self.report=self.root/'synthetic-review.md';self.report.write_text('SYNTHETIC TEST ONLY, not a genuine independent review')
        self.review=dict(status='ACCEPTED',independent=True,read_only=True,scope='STATIC_E2_COMPLETION_FINAL_BYTES',blockers=[],
            fixture_sha256=frozen['sha256'],source_sha256=h.source_map(),runtime_handoff_sha256=sha(self.lab/'results/runtime-handoff.json'),
            authorization_sha256=sha(self.lab/'results/authorization.json'),registration_sha256=sha(h.REGISTRATION),
            gate_sha256=sha(self.lab/'offline/offline-gate.json'),report_file=str(self.report),report_sha256=sha(self.report))
        self.write('handoff-review',self.review)
    def tearDown(self):self.stack.close();self.tmp.cleanup()
    def write(self,name,data):
        p=self.lab/'results'/(name+'.json');p.write_text(json.dumps(data));p.chmod(0o600)
    def mutate_auth(self,**updates):self.write('authorization',{**self.auth,**updates})
    def call(self,review=True):return h.preflight(self.lab,self.lab/'results/authorization.json',review=review)
    def test_prospective_no_review_pure(self):
        before={str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(self.call(review=False)['review'],'PENDING_INDEPENDENT_REVIEW')
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_wrong_lab(self):
        with self.assertRaises(Invalid):h.preflight(h.OLD_LAB,self.lab/'results/authorization.json')
    def test_wrong_token(self):
        self.mutate_auth(token='b'*64)
        with self.assertRaisesRegex(Invalid,'exact-authorization'):self.call()
    def test_wrong_ticket(self):
        self.mutate_auth(ticket='old-ticket')
        with self.assertRaises(Invalid):self.call()
    def test_wrong_binary(self):
        (self.lab/'swayfx-mosaic').write_bytes(b'changed')
        with self.assertRaisesRegex(Invalid,'actual-identities'):self.call()
    def test_wrong_wlroots(self):
        h.WLROOTS.write_bytes(b'changed')
        with self.assertRaisesRegex(Invalid,'actual-identities'):self.call()
    def test_missing_review(self):
        (self.lab/'results/handoff-review.json').unlink()
        with self.assertRaises(FileNotFoundError):self.call()
    def test_historical_review_rejected(self):
        self.write('handoff-review',{**self.review,'scope':'STATIC_NESTED_RUNTIME_HANDOFF'})
        with self.assertRaisesRegex(Invalid,'genuine-independent-review-required'):self.call()
    def test_stale_review(self):
        self.write('handoff-review',{**self.review,'fixture_sha256':'0'*64})
        with self.assertRaisesRegex(Invalid,'review-final-bindings'):self.call()
    def test_changed_manifest(self):
        (self.lab/'results/fixture-freeze-sha256.txt').write_text(sha(h.BINARY)+'  '+str(h.BINARY)+'\n')
        with self.assertRaisesRegex(Invalid,'complete-exact-manifest'):self.call()
    def test_changed_runner(self):
        (self.lab/'fixture/run.py').write_text('changed runner')
        with self.assertRaises(AssertionError):self.call()
    def test_consumed_run(self):
        h.exclusive(h.SPENT,{'synthetic':'spent'})
        with self.assertRaisesRegex(Invalid,'ticket-launch-already-consumed'):self.call()
    def test_existing_run(self):
        (self.lab/'run').mkdir()
        with self.assertRaisesRegex(Invalid,'unconsumed-runtime'):self.call()
    def test_review_report_changed(self):
        self.report.write_text('changed synthetic report')
        with self.assertRaisesRegex(Invalid,'review-report-bytes'):self.call()
    def test_consumed_runner_wrong_token(self):
        h.exclusive(h.SPENT,dict(ticket=h.TICKET,lab=str(self.lab),token='wrong',fixture_sha256=self.auth['fixture_sha256'],authorization_sha256=sha(self.lab/'results/authorization.json')))
        with self.assertRaisesRegex(Invalid,'runner-exact-consumption'):h.preflight(self.lab,self.lab/'results/authorization.json',consumed=True)
