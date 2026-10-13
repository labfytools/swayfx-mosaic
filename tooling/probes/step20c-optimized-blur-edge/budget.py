"""Durable fail-closed reservations, bound to one LAB for this ticket.

WHY: a failed graphical attempt must never create capacity for a rerun.
CONTRACT: exclusive flock; fsync file then atomic replace and directory fsync.
INVARIANT: exact schema, bounded counters, no reset/refund or alternate LAB.
"""
import fcntl
import json
import os
import tempfile
from pathlib import Path

MODES = ('R0', 'R1', 'R2', 'R3')
KEYS = ('run', 'mutation', 'capture', 'cycle', 'calibration')
CAMPAIGN = 'SWAYFX_MOSAIC_STEP20C_OPTIMIZED_CACHE_FREEZE_AND_EDGE_CAUSALITY_GATE_V1'
DEFAULT = Path.home() / 'swayfx-mosaic-optimized-edge-v1-budget.json'

def limits(mode):
    return dict(run=1, mutation=3, capture=12, cycle=1,
                calibration=1 if mode in ('R2', 'R3') else 0)

def validate(state, lab):
    if set(state) != {'campaign', 'lab', 'modes'} or state['campaign'] != CAMPAIGN or state['lab'] != lab:
        raise RuntimeError('wrong campaign/LAB or corrupt schema')
    if set(state['modes']) != set(MODES):
        raise RuntimeError('corrupt modes')
    for mode, counts in state['modes'].items():
        if set(counts) != set(KEYS):
            raise RuntimeError('corrupt resource schema')
        for key, value in counts.items():
            if type(value) is not int or not 0 <= value <= limits(mode)[key]:
                raise RuntimeError('corrupt/out-of-bounds counter')
        if any(counts[k] for k in KEYS if k != 'run') and counts['run'] != 1:
            raise RuntimeError('action before run')

def reserve(lab, mode, resource, path=DEFAULT):
    if mode not in MODES or resource not in KEYS:
        raise ValueError('unknown reservation')
    lab = str(Path(lab).resolve())
    path = Path(path)
    with path.with_suffix('.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = json.loads(path.read_text()) if path.exists() else {
            'campaign': CAMPAIGN, 'lab': lab,
            'modes': {m: {k: 0 for k in KEYS} for m in MODES}}
        validate(state, lab)
        counts = state['modes'][mode]
        if resource != 'run' and counts['run'] != 1:
            raise RuntimeError('reserve run first')
        if counts[resource] >= limits(mode)[resource]:
            raise RuntimeError('budget exhausted: ' + resource)
        counts[resource] += 1
        fd, tmp = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
        try:
            with os.fdopen(fd, 'w') as out:
                json.dump(state, out, sort_keys=True)
                out.write('\n')
                out.flush()
                os.fsync(out.fileno())
            os.replace(tmp, path)
            directory = os.open(path.parent, os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        return state
