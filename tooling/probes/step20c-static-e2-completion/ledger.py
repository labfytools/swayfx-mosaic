"""Durable debits. Offline tests initialize temporary ledgers only.

The offline LAB never has a runtime ledger. Future registration is a separate
explicitly authorized ticket; failed reservations/actions are never refunded.
"""
import fcntl
import json
import os
from pathlib import Path
import tempfile
import time
from model import require

LIMITS = dict(run=1, chain=1, grab=2, click=4, capture=12, camera=1, transition=1, move=16)


def durable(path, state):
    fd, tmp = tempfile.mkstemp(prefix='.debit-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as out:
            json.dump(state, out); out.flush(); os.fsync(out.fileno())
        os.replace(tmp, path)
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def initial_for_offline_test(path):
    """No production initialization API: the caller proves isolated test storage."""
    path = Path(path)
    require(path.parent.name.startswith('geometry-ledger-test-'), 'test-ledger-only')
    with path.open('x') as out:
        json.dump(dict(limits=LIMITS, used=dict.fromkeys(LIMITS, 0), events=[]), out)
        out.flush(); os.fsync(out.fileno())


def valid(state):
    require(state.get('limits') == LIMITS and set(state.get('used', {})) == set(LIMITS), 'ledger-schema')
    require(all(type(state['used'][k]) is int and 0 <= state['used'][k] <= LIMITS[k] for k in LIMITS), 'ledger-counts')
    events = state.get('events')
    require(isinstance(events, list) and len(events) == sum(state['used'].values()), 'ledger-events')
    require(all(isinstance(e, dict) and e.get('seq') == i and e.get('kind') in LIMITS and
                type(e.get('ns')) is int and e['ns'] > 0 for i, e in enumerate(events)), 'ledger-sequences')
    require(all(sum(e['kind'] == k for e in events) == state['used'][k] for k in LIMITS), 'ledger-accounting')
    return state


def reserve(path, *kinds):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'existing-ledger-required')
    with path.with_suffix('.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = valid(json.loads(path.read_text()))
        require(bool(kinds) and all(k in LIMITS for k in kinds), 'ledger-debit-kinds')
        require(all(state['used'][k] + kinds.count(k) <= LIMITS[k] for k in kinds), 'ledger-exhausted')
        for k in kinds:
            state['used'][k] += 1
            state['events'].append(dict(seq=len(state['events']), kind=k, ns=time.monotonic_ns()))
        durable(path, state)
        return state
