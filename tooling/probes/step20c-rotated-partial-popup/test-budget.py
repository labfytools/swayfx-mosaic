"""Offline ledger tests; no compositor or campaign reservation."""
from pathlib import Path
import tempfile
from budget import Budget

with tempfile.TemporaryDirectory() as directory:
    lab = Path(directory)
    budget = Budget(lab)
    assert budget.reserve('control')['runs'] == ['control']
    try:
        budget.reserve('control')
    except ValueError:
        pass
    else:
        raise AssertionError('duplicate accepted')
    assert budget.reserve('private_standard')['runs'][-1] == 'private_standard'
    assert budget.reserve('private_mosaic')['runs'][-1] == 'private_mosaic'
    try:
        budget.reserve('control')
    except ValueError:
        pass
    else:
        raise AssertionError('exhaustion bypass')
    try:
        Budget(lab)
    except BlockingIOError:
        pass
    else:
        raise AssertionError('lock bypass')
with tempfile.TemporaryDirectory() as directory:
    lab = Path(directory)
    (lab / 'runs').mkdir()
    (lab / 'runs' / 'failed').mkdir()
    try:
        Budget(lab).read()
    except ValueError:
        pass
    else:
        raise AssertionError('missing ledger accepted')
print('PASS persistence, duplicate, exhaustion, lock, missing-ledger')
