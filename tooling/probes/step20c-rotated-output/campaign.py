"""Persistent global rotation budget; one lock covers launch and cleanup."""
import fcntl
import json
import os
from pathlib import Path
import time

MODES = ('control', 'private_standard', 'private_mosaic')
ACTIONS = ('R90', 'R0', 'camera_hide', 'camera_return')


def read(lab):
    lab = Path(lab)
    path = lab / 'rotation-campaign-budget.json'
    if not path.exists():
        if any((lab / 'runs').glob('*-rotated-*')):
            raise ValueError('missing ledger with retained runs')
        return {'version': 1, 'runs': [], 'reservations': []}
    state = json.loads(path.read_text())
    if state.get('version') != 1 or len(state.get('runs', [])) != len(set(state['runs'])):
        raise ValueError('bad version or duplicate run')
    if any(mode not in MODES for mode in state['runs']):
        raise ValueError('bad mode')
    seen = set()
    for item in state.get('reservations', []):
        key = (item.get('mode'), item.get('action'))
        if key in seen or key[0] not in state['runs'] or key[1] not in ACTIONS:
            raise ValueError('bad or duplicate reservation')
        if key[1].startswith('camera') and key[0] != 'private_mosaic':
            raise ValueError('camera action outside Mosaic')
        seen.add(key)
    return state


def write(lab, state):
    # WHY: a failed command consumes its reserved global action.
    # CONTRACT: the caller holds Campaign.lock across child lifetime.
    # INVARIANT: durable replacement precedes every command launch.
    path = Path(lab) / 'rotation-campaign-budget.json'
    tmp = path.with_suffix('.tmp')
    with tmp.open('w') as output:
        output.write(json.dumps(state, indent=2) + '\n')
        output.flush()
        os.fsync(output.fileno())
    tmp.replace(path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class Campaign:
    def __init__(self, lab):
        self.lab = Path(lab)
        self.lock = (self.lab / 'rotation-campaign.lock').open('a')
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def begin(self, mode):
        state = read(self.lab)
        if mode not in MODES or mode in state['runs']:
            raise ValueError('invalid or repeated run')
        state['runs'].append(mode)
        write(self.lab, state)


def reserve(lab, mode, action):
    state = read(lab)
    if mode not in state['runs'] or action not in ACTIONS:
        raise ValueError('invalid mode/action')
    if any(x['mode'] == mode and x['action'] == action for x in state['reservations']):
        raise ValueError('duplicate action')
    if action in ('R90', 'R0'):
        if action == 'R0' and not any(x['mode'] == mode and x['action'] == 'R90' for x in state['reservations']):
            raise ValueError('return without rotation')
        if sum(x['action'] in ('R90', 'R0') for x in state['reservations']) >= 6:
            raise ValueError('global rotation budget exhausted')
    else:
        if mode != 'private_mosaic':
            raise ValueError('camera budget is Mosaic only')
        if action == 'camera_return' and not any(x['action'] == 'camera_hide' for x in state['reservations']):
            raise ValueError('camera return without hide')
        if any(x['action'] == action for x in state['reservations']):
            raise ValueError('global camera pair exhausted')
    state['reservations'].append({'mode': mode, 'action': action,
                                  'reserved_ns': time.monotonic_ns()})
    write(lab, state)
    return state
