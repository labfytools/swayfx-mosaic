#!/usr/bin/env python3
"""Prepare review inputs only; never build, stage, accept, or launch."""
import argparse,json,subprocess,shutil
from diagnostic import *

def main():
    p=argparse.ArgumentParser();p.add_argument('--lab',type=Path,required=True);a=p.parse_args();lab=gate.owned(a.lab);gate.verify(lab)
    diag=lab/'diagnostic';need(diag.is_dir(),'existing same laboratory diagnostic directory')
    registration_path=lab/'diagnostic-registration.json'
    expected=dict(scope=SCOPE,spec=SPEC)
    if registration_path.exists():need(gate.read(registration_path)==expected,'unchanged fixed registration')
    else:gate.durable(registration_path,expected,True)
    # Copy only reviewed Python/README bytes; never regenerate the passive C.
    copy=diag/'diagnostic-source';copy.mkdir(exist_ok=True)
    for path in HERE.iterdir():
        if path.is_file():shutil.copy2(path,copy/path.name)
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'};cmd=[sys.executable,str(HERE/'test_diagnostic.py')]
    run=subprocess.run(cmd,env=env,capture_output=True,text=True);raw=run.stdout+run.stderr;(diag/'offline.stdout').write_text(raw)
    receipt=dict(command=cmd,exit=run.returncode,status='PASS' if run.returncode==0 else 'FAIL',executed=int(re.search(r'Ran (\d+) tests',raw)[1]),raw_sha256=gate.sha(diag/'offline.stdout'),sources={str(p):gate.sha(p) for p in HERE.iterdir() if p.is_file()})
    gate.durable(diag/'offline.json',receipt,True);need(run.returncode==0,'offline tests')
    need(gate.read(diag/'syntax-check.json')['exit']==0,'C17 syntax check')
    gate.durable(diag/'preparation-freeze.json',dict(scope=SCOPE,status='READY_FOR_INDEPENDENT_REVIEW',spec=SPEC,files=bindings(lab)),True)
    gate.verify(lab);print(json.dumps(dict(status='READY_FOR_INDEPENDENT_REVIEW',freeze_sha256=gate.sha(diag/'preparation-freeze.json'),runtime='NOT RUN',build='NOT RUN')))
if __name__=='__main__':main()
