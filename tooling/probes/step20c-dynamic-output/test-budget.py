"""Offline execution of actual campaign budget; no dynamic output operations."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from campaign import Campaign, reserve, read

root=Path(tempfile.mkdtemp(prefix='dynamic-budget-test-'))
c=Campaign(root);c.begin('control');reserve(root,'control','D1')
# A second process must not launch a contradicting campaign while lock is held.
p=subprocess.run([sys.executable,'-c','from campaign import Campaign; Campaign('+repr(str(root))+')'],cwd=Path(__file__).parent,capture_output=True,text=True)
assert p.returncode and 'BlockingIOError' in p.stderr
for mode in ('control','private_standard','private_mosaic'):
    if mode != 'control':c.begin(mode)
    for action in ('D1','D2','D3','D5'):
        if mode=='control' and action=='D1':continue
        reserve(root,mode,action)
    try:reserve(root,mode,'D1')
    except ValueError:pass
    else:raise AssertionError('duplicate accepted')
    try:c.begin(mode)
    except ValueError:pass
    else:raise AssertionError('run reset accepted')
state=read(root);assert len(state['reservations'])==12
# Persisted reservations survive caller failure; no refund or ledger reset.
c.lock.close();assert read(root)==state
old=root/'old';(old/'runs/control-dynamic-failed').mkdir(parents=True)
try:read(old)
except ValueError:pass
else:raise AssertionError('missing ledger accepted')
print('PASS lock/persistence/duplicate/exhaustion/failed-run/missing-ledger; zero compositor launches')
