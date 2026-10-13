"""Offline exhaustion and cross-process reservation tests, outside campaign LAB."""
import concurrent.futures
import json
from pathlib import Path
import tempfile
from support import LIMITS, reserve

def attempt(args):
    lab, kind = args
    try: reserve(lab,kind); return True
    except RuntimeError: return False

if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='static-budget-test-') as tmp:
        lab=Path(tmp);(lab/'results').mkdir()
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
            assert sum(pool.map(attempt,[(lab,'capture')]*20))==8
        for kind,limit in LIMITS.items():
            if kind=='capture':continue
            for _ in range(limit):assert attempt((lab,kind))
            assert not attempt((lab,kind))
        state=json.loads((lab/'results/budget.json').read_text())
        assert state['used']==LIMITS
        assert not attempt((lab,'run'))
    print('PASS offline ledger: concurrent reservations, exhaustion, durable failures, no refund')
