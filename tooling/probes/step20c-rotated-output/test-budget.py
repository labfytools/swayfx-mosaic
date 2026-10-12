"""Exercise the actual ledger without launching a compositor."""
import subprocess
import sys
import tempfile
from pathlib import Path
from campaign import Campaign, read, reserve

lab = Path(tempfile.mkdtemp(prefix='rotation-budget-test-'))
campaign = Campaign(lab)
campaign.begin('control')
contender = subprocess.run([sys.executable, '-c',
    'from campaign import Campaign; Campaign(' + repr(str(lab)) + ')'],
    cwd=Path(__file__).parent, capture_output=True, text=True)
assert contender.returncode and 'BlockingIOError' in contender.stderr
for mode in ('control', 'private_standard', 'private_mosaic'):
    if mode != 'control':
        campaign.begin(mode)
    reserve(lab, mode, 'R90')
    reserve(lab, mode, 'R0')
    try:
        reserve(lab, mode, 'R90')
    except ValueError:
        pass
    else:
        raise AssertionError('duplicate transition accepted')
reserve(lab, 'private_mosaic', 'camera_hide')
reserve(lab, 'private_mosaic', 'camera_return')
state = read(lab)
assert len(state['reservations']) == 8
campaign.lock.close()
assert read(lab) == state
old = lab / 'old'
(old / 'runs/control-rotated-failed').mkdir(parents=True)
try:
    read(old)
except ValueError:
    pass
else:
    raise AssertionError('missing ledger accepted')
print('PASS lock, persistence, duplicate, exhaustion, missing ledger; no compositor launched')
