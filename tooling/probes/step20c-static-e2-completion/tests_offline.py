#!/usr/bin/env python3
"""Independent single mutations and executable receipts; never run compositor."""
import ast
import copy
import json
from pathlib import Path
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import sys
from PIL import Image,ImageDraw
from model import Invalid,require
from transition import validate_applied_standard_transition,transition_window_start
from replay import historical_inputs,replay
from predicates import COLORS,point,terminal_exchange,Defect
from lifecycle import *
from support import sha
from ledger import initial_for_offline_test,reserve,valid,LIMITS
from reusable_tests import Case as ReusableGeometry
from handoff_tests import Handoff

HERE=Path(__file__).resolve().parent
ACTIVE=None;OBSERVED={}

def trace(frame,event,arg):
    if ACTIVE and event=='return' and frame.f_code.co_name=='require' and not frame.f_locals.get('value'):
        OBSERVED.setdefault(ACTIVE,set()).add(frame.f_locals['contract'])
    if ACTIVE and event=='exception' and arg[0] is AssertionError and Path(frame.f_code.co_filename).parent==HERE:
        OBSERVED.setdefault(ACTIVE,set()).add('AssertionError:'+frame.f_code.co_name)
    return trace

class Transition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.original=historical_inputs()
    def setUp(self):self.data=copy.deepcopy(self.original)
    def reject(self,expected):
        with self.assertRaisesRegex(Invalid,'^'+re.escape(expected)+'$'):
            validate_applied_standard_transition(**self.data)
    def replace(self,old,new):
        self.assertIn(old,self.data['trace']);self.data['trace']=self.data['trace'].replace(old,new)
    def test_real_raw_replay(self):self.assertEqual(replay()['status'],'PASS')
    def test_retained_clip(self):
        self.replace('layout=1 scroll=-1 tile_scene=0,0 clip_valid=0','layout=1 scroll=-1 tile_scene=0,0 clip_valid=1');self.reject('standard-clips-absent')
    def test_no_standard_epoch(self):
        self.replace('layout=1 scroll=-1 tile_scene=0,0 clip_valid=0 clip=0,0,0,0','layout=5 scroll=-1 tile_scene=0,0 clip_valid=1 clip=0,0,800,600')
        self.data['trace']=re.sub(r'(PI_POPUP[^\n]*?)clip_valid=0 clip=0,0,0,0',r'\1clip_valid=1 clip=-402,-25,800,600',self.data['trace']);self.reject('two-standard-observations-required')
    def test_wrong_layout(self):
        self.replace('workspace=6 layout=1','workspace=6 layout=2');self.reject('unexpected-applied-layout')
    def test_wrong_owner(self):self.data['owner_id']=8;self.reject('targeted-accepted-splith')
    def test_wrong_root(self):self.data['root_id']='0x123';self.reject('unique-enabled-root')
    def test_wrong_output(self):self.data['output']='HEADLESS-2';self.reject('exact-workspace-output')
    def test_reversed_times(self):
        self.replace('ns=181923236944243','ns=181923034904617');self.reject('trace-monotonic-order')
    def test_standard_before_application(self):
        self.data['request_ns']=[181923236944244,181923236944244];self.data['ipc_response']['ns']=181923236944245
        self.reject('standard-before-request-application')
    def test_clip_reactivation(self):
        t=self.data['trace'];lines=t.splitlines();start=next(i for i,l in enumerate(lines) if 'PI_OUTPUT_COMMIT output=HEADLESS-1 commit_seq=56 ' in l)
        for i in range(start,len(lines)):
            if 'PI_SCENE output=HEADLESS-1 ' in lines[i]:lines[i]=lines[i].replace('layout=1','layout=5').replace('clip_valid=0 clip=0,0,0,0','clip_valid=1 clip=0,0,800,600')
        self.data['trace']='\n'.join(lines);self.reject('clip-reactivated-after-standard')
    def test_missing_root_traces(self):
        self.data['trace']='\n'.join(l for l in self.data['trace'].splitlines() if 'PI_POPUP output=HEADLESS-1 ' not in l);self.reject('unique-enabled-root')
    def test_multiple_roots(self):
        line=next(l for l in self.data['trace'].splitlines() if 'ns=181923236944243 ' in l)
        self.replace(line,line+'\n'+line.replace('181923236944243','181923236944244').replace('tree=0x56292fbcc170','tree=0x999').replace('local_index=1','local_index=2'));self.reject('unique-enabled-root')
    def test_wrong_capture_epoch(self):
        self.data['captures'][0]['start_ns']=181923035203193;self.reject('capture-applied-standard-epoch')
    def test_different_workspace(self):
        self.replace('workspace=6 layout=1','workspace=99 layout=1');self.reject('applied-current-scene-workspace')
    def test_popup_disappears_early(self):
        self.data['client_protocol']+='\nPOPUP_B DESTROY role=17 xdg=15 wl=13\n'
        with self.assertRaisesRegex(Invalid,'malformed-transition-evidence'):validate_applied_standard_transition(**self.data)
    def test_ipc_failure(self):self.data['ipc_response']['exit']=1;self.reject('targeted-accepted-splith')
    def test_no_root_clip_removal(self):
        self.replace('tree=0x56292fbcc170 enabled=1 clip_valid=0 clip=0,0,0,0','tree=0x56292fbcc170 enabled=1 clip_valid=1 clip=-482,-25,800,600');self.reject('standard-clips-absent')
    def test_pending_presented_applied(self):
        self.replace('scene_valid=1 scene=-400,0','scene_valid=0 scene=-400,0');self.reject('exact-applied-owner')
    def test_missing_second_observation(self):
        lines=self.data['trace'].splitlines();start=next(i for i,l in enumerate(lines) if 'PI_OUTPUT_COMMIT output=HEADLESS-1 commit_seq=56 ' in l)
        end=next((i for i in range(start+1,len(lines)) if 'PI_OUTPUT_COMMIT ' in lines[i]),len(lines))
        self.data['trace']='\n'.join(lines[:start]+lines[end:]);self.reject('two-standard-observations-required')
    def test_historical_request_omission_interval(self):
        proof=validate_applied_standard_transition(**self.data)
        self.assertEqual(proof['request_bounds'],[181922658327071,181923034516066])
        self.assertLess(proof['request_bounds'][1],181923034904618)
    def test_request_ambiguity(self):self.data['request_ns']=[181923035203193,181923035203194];self.reject('request-reply-window')
    def test_empty_captures(self):self.data['captures']=[];self.reject('two-standard-captures')
    def test_changed_xdg_identity(self):self.data['expected_ids']['POPUP_A'][1]=999;self.reject('exact-xdg-object-identities')
    def test_runtime_pre_root_epochs_window(self):
        # Real earlier callbacks contain no root before A maps. The transition
        # starts at a complete observed callback after A/B fully mapped.
        start=transition_window_start(self.data['trace'],'HEADLESS-1',self.data['root_id'],10,6,
                181922000000000,self.data['request_ns'][1])
        self.assertLess(start,self.data['request_ns'][0])
        self.data['window'][0]=start
        self.assertEqual(validate_applied_standard_transition(**self.data)['status'],'PASS')
    def test_runtime_mapped_window_missing_commit(self):
        with self.assertRaisesRegex(Invalid,'fully-mapped-mosaic-commit-before-request'):
            transition_window_start(self.data['trace'],'HEADLESS-1',self.data['root_id'],10,6,
                self.data['ipc_response']['ns'],self.data['request_ns'][1])
    def test_legitimate_missing_protocol_map_invalid(self):
        self.data['client_protocol']=self.data['client_protocol'].replace('POPUP_B MAP ','POPUP_B OMITTED ')
        with self.assertRaisesRegex(Invalid,'malformed-transition-evidence'):validate_applied_standard_transition(**self.data)
    def test_missing_reply_timestamp_invalid(self):
        del self.data['ipc_response']['ns']
        with self.assertRaisesRegex(Invalid,'malformed-transition-evidence'):validate_applied_standard_transition(**self.data)

class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.data=historical_inputs();self.before=self.data['client_protocol'];self.ids=self.data['expected_ids']
        self.b=self.ids['POPUP_B'];self.a=self.ids['POPUP_A'];self.top=self.ids['TOPLEVEL']
        b=self.b
        self.after=self.before+f'\nPOPUP_B DESTROY role={b[2]} xdg={b[1]} wl={b[0]}\nxdg_popup#{b[2]}.destroy()\nxdg_surface#{b[1]}.destroy()\nwl_surface#{b[0]}.destroy()\nCOMMAND close_b DONE\n'
        self.image=Image.new('RGB',(800,600),(48,48,56));ImageDraw.Draw(self.image).rectangle((0,105,51,274),fill=COLORS['POPUP_A'])
        self.buttons=['POINTER_BUTTON target=POPUP_A serial=110 button=273 state=1','POINTER_BUTTON target=POPUP_A serial=111 button=273 state=0']
    def test_explicit_close(self):self.assertEqual(explicit_child_close(self.before,self.after,self.ids,1,2)['status'],'PASS')
    def test_popup_done_distinct(self):
        with self.assertRaisesRegex(Invalid,'close-must-not-be-dismissal'):explicit_child_close(self.before,self.after+'POPUP_B POPUP_DONE role=17\n',self.ids,1,2)
    def test_missing_close_command(self):
        with self.assertRaisesRegex(Invalid,'explicit-child-destroy-DONE'):explicit_child_close(self.before,self.after.replace('COMMAND close_b DONE',''),self.ids,1,2)
    def test_destroy_wrong_object(self):
        with self.assertRaisesRegex(Invalid,'child-protocol-destroy'):explicit_child_close(self.before,self.after.replace(f'xdg_popup#{self.b[2]}.destroy()','xdg_popup#999.destroy()'),self.ids,1,2)
    def test_A_destroyed(self):
        with self.assertRaisesRegex(Invalid,'same-A-remains-mapped'):explicit_child_close(self.before,self.after+'POPUP_A DESTROY role=14\n',self.ids,1,2)
    def test_A_input_and_recomputed_point(self):
        xy=point(self.image,'POPUP_A',0);self.assertEqual(a_survival(self.image,self.after,self.after,self.ids,self.buttons,xy,[-298,105,350,170])['status'],'PASS')
    def test_B_residual(self):
        self.image.putpixel((1,1),COLORS['POPUP_B'])
        with self.assertRaisesRegex(Invalid,'child-zero-residual-A-painted'):a_survival(self.image,self.after,self.after,self.ids,self.buttons,[10,120],[-298,105,350,170])
    def test_wrong_A_button(self):
        with self.assertRaises(Defect):a_survival(self.image,self.after,self.after,self.ids,[s.replace('POPUP_A','POPUP_B') for s in self.buttons],[10,120],[-298,105,350,170])
    def test_final_exact(self):
        im=Image.new('RGB',(800,600),(48,48,56));self.assertEqual(final_restoration(im,im.copy())['status'],'PASS')
    def test_final_no_tolerance(self):
        im=Image.new('RGB',(800,600),(48,48,56));b=im.copy();b.putpixel((799,599),(49,48,56))
        with self.assertRaisesRegex(Invalid,'whole-H2-final-exact'):final_restoration(im,b)
    def owner_tail(self):
        a,t=self.a,self.top
        return f'COMMAND close_owner\nPOPUP_A DESTROY role={a[2]} xdg={a[1]} wl={a[0]}\nxdg_popup#{a[2]}.destroy()\nxdg_surface#{a[1]}.destroy()\nwl_surface#{a[0]}.destroy()\nTOPLEVEL DESTROY\nxdg_toplevel#{t[2]}.destroy()\nxdg_surface#{t[1]}.destroy()\nwl_surface#{t[0]}.destroy()\n'
    def test_normal_owner_close(self):self.assertEqual(normal_owner_close(self.after,self.after+self.owner_tail(),self.ids,0)['status'],'PASS')
    def test_owner_close_without_command(self):
        with self.assertRaisesRegex(Invalid,'normal-owner-close-command'):normal_owner_close(self.after,self.after+self.owner_tail().replace('COMMAND close_owner',''),self.ids,0)
    def test_open_left_pair_real_serial(self):
        self.assertEqual(opening_pair(['POINTER_BUTTON target=TOPLEVEL serial=98 button=272 state=1','POINTER_BUTTON target=TOPLEVEL serial=99 button=272 state=0'],'TOPLEVEL',98)[0][1],98)
    def test_open_wrong_serial(self):
        with self.assertRaisesRegex(Invalid,'real-left-opening-pair'):opening_pair(['POINTER_BUTTON target=TOPLEVEL serial=98 button=272 state=1','POINTER_BUTTON target=TOPLEVEL serial=99 button=272 state=0'],'TOPLEVEL',97)

class TerminalLedger(unittest.TestCase):
    def test_actual_terminal_ipc_one(self):
        captured=[]
        r=terminal_exchange(lambda *a,**k:SimpleNamespace(returncode=1,stdout='raw out',stderr='raw err'),lambda **k:0,[],{},True,
            lambda:"Handling command 'exit'\nShutting down sway",lambda:False,lambda:False,lambda *a:captured.append(a))
        self.assertTrue(r['scientific_cleanup_pass']);self.assertEqual(captured,[('raw out','raw err')]);self.assertEqual(r['ipc_exit'],1)
    def test_terminal_wait_failure_retains_codes(self):
        captured=[]
        def fail(**k):raise TimeoutError('raw wait')
        r=terminal_exchange(lambda *a,**k:SimpleNamespace(returncode=1,stdout='out',stderr='err'),fail,[],{},True,lambda:'',lambda:False,lambda:False,lambda *a:captured.append(a))
        self.assertEqual(r['ipc_exit'],1);self.assertEqual(r['stdout'],'out');self.assertFalse(r['scientific_cleanup_pass'])
    def test_exact_budget_exhaustion(self):
        self.assertEqual(LIMITS,dict(run=1,chain=1,grab=2,click=4,capture=12,camera=1,transition=1,move=16))
        with tempfile.TemporaryDirectory(prefix='geometry-ledger-test-') as temp:
            p=Path(temp)/'budget.json';initial_for_offline_test(p)
            for kind,count in LIMITS.items():reserve(p,*([kind]*count))
            before=p.read_bytes()
            with self.assertRaisesRegex(Invalid,'ledger-exhausted'):reserve(p,'run')
            self.assertEqual(p.read_bytes(),before)
    def test_runner_single_chain_and_source_audit(self):
        from audit import audit
        result=audit();self.assertEqual(result['status'],'PASS');self.assertTrue(result['records'])

class Receipt(unittest.TestCase):
    def test_empty_PASS_rejected(self):
        from gate import validate_test_receipts
        with self.assertRaises(Invalid):validate_test_receipts({'status':'PASS','tests':[]})
    def test_skipped_rejected(self):
        from gate import validate_test_receipts
        with self.assertRaises(Invalid):validate_test_receipts({'status':'PASS','tests':[{'id':'test','status':'SKIP'}]})
    def test_incomplete_temporal_PASS_records_rejected(self):
        from gate import validate_test_receipts
        receipt=dict(status='PASS',tests=[dict(id=n,status='PASS',rejected_contracts=[]) for n in expected_tests()],
            executed=len(expected_tests()),failures=0,errors=0,skips=0,sources={p.name:sha(p) for p in HERE.glob('*.py')})
        with self.assertRaisesRegex(Invalid,'executed-negative-rejection'):
            validate_test_receipts(receipt)

class Result(unittest.TextTestResult):
    def startTest(self,test):
        global ACTIVE
        ACTIVE=test.id();super().startTest(test)
    def stopTest(self,test):
        global ACTIVE
        ACTIVE=None;super().stopTest(test)
    def addSuccess(self,test):
        super().addSuccess(test);self.receipts.append(dict(id=test.id(),status='PASS',rejected_contracts=sorted(OBSERVED.get(test.id(),[]))))
    def __init__(self,*a,**k):super().__init__(*a,**k);self.receipts=[]


def expected_tests():
    suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    def flatten(s):
        for item in s:
            if isinstance(item,unittest.TestSuite):yield from flatten(item)
            else:yield item
    return {test.id().replace('__main__.','tests_offline.') for test in flatten(suite)}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
    sys.settrace(trace)
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    sys.settrace(None)
    # Module identity is normalized so direct CLI and imported inventory agree.
    receipts=[{**r,'id':r['id'].replace('__main__.','tests_offline.')} for r in result.receipts]
    if a.output:
        with a.output.open('x') as out:json.dump(dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests=receipts,
          executed=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),
          sources={p.name:sha(p) for p in HERE.glob('*.py')}),out,indent=2);out.write('\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
