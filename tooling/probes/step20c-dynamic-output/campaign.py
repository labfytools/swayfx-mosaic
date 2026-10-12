"""Persistent finite campaign budget; only caller holding Campaign.lock may mutate."""
import fcntl
import json
import os
from pathlib import Path

MODES = ('control', 'private_standard', 'private_mosaic')
ACTIONS = {'D1': 'reconfiguration', 'D2': 'reconfiguration',
           'D3': 'migration', 'D5': 'migration'}
LIMITS = {'reconfiguration': 6, 'migration': 6, 'camera_pair': 1}


def read(lab):
    path = Path(lab) / 'dynamic-campaign-budget.json'
    if not path.exists():
        if any((Path(lab) / 'runs').glob('*-dynamic-*')):
            raise ValueError('missing ledger in existing campaign; no reset')
        return {'version': 1, 'runs': [], 'reservations': []}
    state = json.loads(path.read_text())
    if state['version'] != 1 or len(state['runs']) != len(set(state['runs'])):
        raise ValueError('invalid campaign runs/version')
    if any(m not in MODES for m in state['runs']):
        raise ValueError('invalid mode')
    seen = set()
    for r in state['reservations']:
        key = (r['mode'], r['action'])
        if key in seen or r['mode'] not in state['runs'] or r['action'] not in ACTIONS:
            raise ValueError('invalid/duplicate persisted reservation')
        seen.add(key)
    return state


def write(lab, state):
    # WHY: reservations survive launch failure and restart; never refund.
    # CONTRACT: lock is held across write, launch, cleanup; atomic replacement.
    # INVARIANT: preserve every old entry, persist before IPC is launched.
    path = Path(lab) / 'dynamic-campaign-budget.json'
    tmp = path.with_suffix('.tmp')
    with tmp.open('w') as f:
        f.write(json.dumps(state, indent=2) + '\n')
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class Campaign:
    def __init__(self, lab):
        self.lab = Path(lab)
        self.lock = (self.lab / 'dynamic-campaign.lock').open('a')
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def begin(self, mode):
        state = read(self.lab)
        if mode not in MODES or mode in state['runs']:
            raise ValueError('mode already attempted or invalid; no dynamic replay')
        state['runs'].append(mode)
        write(self.lab, state)


def reserve(lab, mode, action):
    # CONTRACT: generated child runs under its parent's exclusive campaign lock.
    state = read(lab)
    if mode not in state['runs'] or action not in ACTIONS:
        raise ValueError('unregistered mode/action')
    if any(r['mode'] == mode and r['action'] == action for r in state['reservations']):
        raise ValueError('action budget exhausted for mode')
    kind = ACTIONS[action]
    if sum(ACTIONS[r['action']] == kind for r in state['reservations']) >= LIMITS[kind]:
        raise ValueError('campaign budget exhausted')
    import time
    state['reservations'].append({'mode': mode, 'action': action,
                                  'reserved_ns': time.monotonic_ns()})
    write(lab, state)
    return state
