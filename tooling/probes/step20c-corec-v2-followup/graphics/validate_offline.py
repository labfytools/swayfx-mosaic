#!/usr/bin/env python3
"""Run exact offline validators; report is never an independent acceptance."""
import argparse,copy,importlib.util,json,sys,unittest
from pathlib import Path
from gate import canonical_lab,clean_environment,disable_dump,durable,source_files,digest,sha

def historical_replay(directory):
 import cases
 root=Path(directory);a=root/'resized-back-snapshot.json';b=root/'migrated-H2-snapshot.json'
 before=json.loads(a.read_text());after=json.loads(b.read_text());previous=cases.dynamic_geometry(before)
 current=cases.dynamic_geometry(after,previous,'migration',previous['focused'])
 mutant=copy.deepcopy(after)
 from ipc_predicates import workspace
 workspace(mutant['tree'],'1')['mosaic']['rows'][0]['scroll_x']=previous['scroll']
 try:cases.dynamic_geometry(mutant,previous,'migration',previous['focused'])
 except ValueError:negative=True
 else:raise AssertionError('stale historical C7 camera accepted')
 return dict(status='PASS',scope='historical IPC replay only; no runtime upgrade',inputs={str(a):sha(a),str(b):sha(b)},positive=current,negative_stale_camera_rejected=negative)

def validate(lab,historical=None):
 disable_dump();lab=canonical_lab(lab);clean_environment(lab)
 path=Path(__file__).parent/'offline/test_followup.py';spec=importlib.util.spec_from_file_location('test_followup',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 suite=unittest.defaultTestLoader.loadTestsFromModule(module);result=unittest.TextTestRunner(verbosity=2).run(suite)
 replay=historical_replay(historical) if historical else dict(status='NOT_RUN',reason='historical replay input not supplied')
 receipt=dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests_run=result.testsRun,failures=len(result.failures)+len(result.errors),skipped=len(result.skipped),source_digest=digest(source_files()),runtime='NOT_RUN',real_reservations=0,independent_review='NOT_PROVEN',historical_C7=replay)
 durable(lab/'followup-work/offline-tests.json',receipt);return result.wasSuccessful()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--lab',required=True);p.add_argument('--historical-c7');a=p.parse_args();raise SystemExit(0 if validate(a.lab,a.historical_c7) else 1)
