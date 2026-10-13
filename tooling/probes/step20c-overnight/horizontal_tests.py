"""Executed offline negative tests; never mint an independent acceptance."""
import argparse
import ast
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from horizontal_adapter import BASE,STANDARD_EXTERIOR,generate,replace_one
import horizontal_gate as gate
sys.path.insert(1,str(BASE))
from model import Rect,Space,Provenance,Invalid,pointer_local,popup,require
from predicates import dismissal,reference,protocol
from PIL import Image
from observations import applied_model,verify_owner_occlusion
from ipc_predicates import nodes,workspace,measure_owner
from model import content
from dataclasses import replace
import copy

class Offline(unittest.TestCase):
    def test_generated_all_compile(self):
        for c in gate.PLANS:
            code=generate(c);compile(code,c,'exec')
            self.assertIn('begin_run()',code);self.assertNotIn("reserve(lab,'run')",code)
            self.assertLess(code.index('begin_run()'),code.index('tempfile.mkdtemp'))
            self.assertIn("['swaymsg','-s',str(sock)",code)
    def test_repository_import_closure_matches_frozen_paths(self):
        frozen = set(gate.paths(gate.DEFAULT_LAB))
        roots = (gate.HERE, BASE)
        pending = [ast.parse(generate(c)) for c in gate.PLANS]
        seen = set()
        while pending:
            tree = pending.pop()
            for node in ast.walk(tree):
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
                for name in names:
                    matches = [root / (name.split('.')[0] + '.py') for root in roots]
                    local = next((p for p in matches if p.is_file()), None)
                    if local is None:
                        continue
                    self.assertIn(local, frozen, 'executed repository import absent: ' + name)
                    if local not in seen:
                        seen.add(local);pending.append(ast.parse(local.read_text()))
        self.assertNotIn(BASE / 'authorization.py', seen)

    def retained_standard(self):
        old = Path('/home/fy59/swayfx-mosaic-static-nested-runtime-pvn0osxm')
        snap = json.loads((old/'results/standard-snapshot.json').read_text())
        ws = workspace(snap['tree'], '1')
        owner = next(n for n in nodes(ws) if n['id'] == 10)
        env = {'require': require};exec(STANDARD_EXTERIOR, env)
        scene = env['splith_exterior'](owner, ws['layout'])
        measured = measure_owner((old/'run/compositor.log').read_text(), owner)
        self.assertEqual(scene, measured['scene'])
        measured['workspace'] = ws['id']
        applied = applied_model(measured, owner, (old/'run/E2.log').read_text(), 'repair-retained-offline')
        return old, owner, applied, env['splith_exterior']

    def test_retained_standard_exterior_content_and_actual_png(self):
        old, owner, applied, inverse = self.retained_standard()
        self.assertEqual(owner['rect'], dict(x=-400,y=25,width=400,height=575))
        self.assertEqual(inverse(owner,'splith'), [-400,0,400,600])
        rect = content(applied);self.assertEqual(rect.values(), [-398,25,396,573])
        obs = json.loads((old/'results/standard-offline-observation.json').read_text())
        verify_owner_occlusion(Image.open(old/'run/standard-H1.png').convert('RGB'),
                               Image.open(old/'run/standard-H2.png').convert('RGB'), rect, obs['geometry'], False)

    def test_retained_standard_invalid_decoration_model_destination(self):
        old, owner, applied, inverse = self.retained_standard()
        with self.assertRaises(Invalid):inverse(owner,'stacked')
        altered=copy.deepcopy(owner);altered['deco_rect']['height']=-1
        with self.assertRaises(Invalid):inverse(altered,'splith')
        for bad in (replace(applied, titlebar=26),
                    replace(applied, scene=replace(applied.scene,y=25,height=575)),
                    replace(applied, window=replace(applied.window,height=572))):
            with self.assertRaises(Invalid):content(bad)
        altered=copy.deepcopy(owner);altered['deco_rect']['height']=26
        with self.assertRaises(Invalid):
            require(inverse(altered,'splith') == applied.scene.values(), 'standard-applied-scene-matches-assignment')

    def test_unique_transform_rejects(self):
        for s in ('missing','x x'):
            with self.assertRaises(ValueError):replace_one(s,'x','y')
    def test_standard_has_no_camera_or_mosaic_command(self):
        for c in ('C0','C1'):
            code=generate(c);self.assertNotIn('open_chain(',code);self.assertNotIn('layout mosaic scroll',code)
            self.assertNotIn('layout mosaic\')',code)
            self.assertNotIn('validate_applied_standard_transition(request',code)
    def test_C2_contract_actions(self):
        code=generate('C2');self.assertIn("open_chain('E1')",code);self.assertIn('fresh_chain(',code)
        self.assertIn('dismissal(log',code);self.assertIn('validate_applied_standard_transition(request',code)
        self.assertIn("layout splith",code);self.assertIn('final_restoration(baseline,final)',code)
    def test_half_open_and_wrong_pointer_reject(self):
        p=Provenance(1,2,'window','actual');r=Rect(Space.GLOBAL,-200,20,300,130,p)
        self.assertTrue(r.contains((99,149)));self.assertFalse(r.contains((100,149)))
        for xy,local in [((100,20),(300,0)),((0,20),(0,0))]:
            with self.assertRaises(Invalid):pointer_local(xy,r,local)
    def test_parent_identity_and_ack_reject(self):
        p=Provenance(1,2,'window','actual');r=Rect(Space.GLOBAL,-200,20,300,130,p);c=Rect(Space.POPUP,10,10,30,30,p)
        for parent,ack,mapped in [(22,3,True),(11,0,True),(11,3,False)]:
            with self.assertRaises(Invalid):popup(r,c,parent,11,ack,mapped)
    def test_reference_unmasked_single_pixel_reject(self):
        a=Image.new('RGB',(800,600),(48,48,56));b=a.copy();b.putpixel((799,599),(48,48,57))
        with self.assertRaises(AssertionError):reference(a,b)
    def test_forbidden_button_rejects(self):
        with self.assertRaises(RuntimeError):dismissal('POPUP_B POPUP_DONE \nPOPUP_A POPUP_DONE \nPOPUP_B DESTROY \nPOPUP_A DESTROY \n',['POINTER_BUTTON target=POPUP_B serial=2 button=273 state=1'])
    def test_dismissal_missing_wrong_order_reject(self):
        for text in ('','POPUP_A POPUP_DONE \nPOPUP_B POPUP_DONE \nPOPUP_B DESTROY \nPOPUP_A DESTROY \n'):
            with self.assertRaises(AssertionError):dismissal(text,[])
    def test_protocol_missing_real_wire_reject(self):
        text=Path('/home/fy59/swayfx-mosaic-e2-completion-dk1hq9an/run/E2.log').read_text()
        # Retained full log ends with explicit destruction; cut before actual close.
        text=text[:text.index('POPUP_B DESTROY ')];protocol(text)
        with self.assertRaises((AssertionError,Invalid)):protocol(text.replace('.grab(wl_seat#','.fake_grab(wl_seat#'))
    def test_review_pending_rejected_before_effect(self):
        with patch.object(gate,'verify_review',side_effect=ValueError('review pending')),patch.object(gate.ledger,'reserve') as debit:
            with self.assertRaises(ValueError):gate.preflight(gate.DEFAULT_LAB,'C0')
            debit.assert_not_called()
    def test_local_budget_reject_no_global_capture(self):
        with tempfile.TemporaryDirectory() as d:
            w=Path(d);gate.exclusive(w/'actions.json',dict(planned=gate.PLANS['C0'],reserved={**dict.fromkeys(gate.PLANS['C0'],0),'capture':10},events=[]))
            with patch.object(gate.ledger,'reserve') as debit:
                with self.assertRaises(ValueError):gate.debit(w,'C0',w,'capture')
                debit.assert_not_called()
    def test_unknown_action_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            w=Path(d);gate.exclusive(w/'actions.json',dict(planned=gate.PLANS['C0'],reserved=dict.fromkeys(gate.PLANS['C0'],0),events=[]))
            with self.assertRaises(ValueError):gate.debit(w,'C0',w,'retry')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Offline);names=[t.id() for t in suite]
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    gate.exclusive(a.output,dict(status='PASS' if result.wasSuccessful() else 'FAIL',executed=result.testsRun,
        tests=names,failures=[(str(t),s) for t,s in result.failures],errors=[(str(t),s) for t,s in result.errors],
        runtime='NOT RUN',review_acceptance_created=False))
    raise SystemExit(not result.wasSuccessful())
