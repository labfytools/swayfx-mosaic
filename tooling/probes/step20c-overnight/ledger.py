"""EXPERIMENTAL persistent overnight budget.
WHY: failures consume the same budget as successes.
CONTRACT: reserve before action; no refunds or reset operation.
INVARIANT: exclusive flock covers validation and durable atomic replacement.
"""
import fcntl
import json
import os
from pathlib import Path
import tempfile
import time

LIMITS = {'scene_build': 2, 'mosaic_build': 2, 'stage': 2, 'run': 18, 'capture': 220}
CAMPAIGNS = {'C': 3, 'D1': 2, 'D2': 2, 'D3': 2, 'D4': 2, 'E1': 1, 'E2': 1, 'E3': 2, 'F': 2, 'G': 1}

def _sync_dir(parent):
    fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

def initialize(path):
    path = Path(path)
    with path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = {'limits': LIMITS, 'campaign_limits': CAMPAIGNS,
                 'used': dict.fromkeys(LIMITS, 0), 'campaign_used': dict.fromkeys(CAMPAIGNS, 0),
                 'runs': {}, 'events': []}
        # O_EXCL makes reinitialization an error, never an implicit reset.
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as out:
            json.dump(state, out, indent=2); out.write('\n'); out.flush(); os.fsync(out.fileno())
        _sync_dir(path.parent)
    return state

def _validate(state):
    """WHY: corrupted persisted counters must fail closed before any action."""
    if not isinstance(state, dict) or state.get('limits') != LIMITS or state.get('campaign_limits') != CAMPAIGNS:
        raise RuntimeError('budget contract changed or corrupt')
    for key, limits in [('used', LIMITS), ('campaign_used', CAMPAIGNS)]:
        values = state.get(key)
        if not isinstance(values, dict) or set(values) != set(limits):
            raise RuntimeError('corrupt counter keys')
        if any(type(values[k]) is not int or not 0 <= values[k] <= limits[k] for k in limits):
            raise RuntimeError('corrupt counter values')
    events, runs = state.get('events'), state.get('runs')
    if not isinstance(events, list) or not isinstance(runs, dict):
        raise RuntimeError('corrupt event/run data')
    counted = dict.fromkeys(LIMITS, 0)
    campaigns = dict.fromkeys(CAMPAIGNS, 0)
    replay = {}
    for i, event in enumerate(events):
        if not isinstance(event, dict) or type(event.get('sequence')) is not int or event['sequence'] != i:
            raise RuntimeError('corrupt event sequence')
        kind, amount = event.get('kind'), event.get('amount')
        if kind not in LIMITS or type(amount) is not int or amount <= 0 or type(event.get('reserved_at_ns')) is not int or event['reserved_at_ns'] <= 0:
            raise RuntimeError('corrupt reservation event')
        counted[kind] += amount
        campaign, run_id = event.get('campaign'), event.get('run_id')
        if kind == 'run':
            if amount != 1 or campaign not in CAMPAIGNS or not isinstance(run_id, str) or not run_id or run_id in replay:
                raise RuntimeError('corrupt run event')
            replay[run_id] = {'campaign': campaign, 'captures': 0}
            campaigns[campaign] += 1
        elif kind == 'capture':
            if run_id not in replay or campaign is not None:
                raise RuntimeError('corrupt capture event')
            replay[run_id]['captures'] += amount
        elif campaign is not None or run_id is not None:
            raise RuntimeError('unexpected build event association')
    if counted != state['used'] or campaigns != state['campaign_used'] or set(replay) != set(runs):
        raise RuntimeError('events do not reconcile counters')
    for run_id, expected in replay.items():
        run = runs[run_id]
        if not isinstance(run, dict) or set(run) != {'campaign', 'captures', 'duration_s'} or run.get('campaign') != expected['campaign'] or type(run.get('captures')) is not int or run['captures'] != expected['captures']:
            raise RuntimeError('corrupt run record')
        if not 0 <= run['captures'] <= (12 if run['campaign'] == 'F' else 20) or type(run.get('duration_s')) not in (int, float) or not 0 < run['duration_s'] <= 150:
            raise RuntimeError('corrupt run bounds')

def reserve(path, kind, *, campaign=None, run_id=None, amount=1, duration_s=150):
    path = Path(path)
    if kind not in LIMITS or type(amount) is not int or amount <= 0:
        raise ValueError('invalid reservation')
    with path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = json.loads(path.read_text())
        _validate(state)
        if state['used'][kind] + amount > LIMITS[kind]:
            raise RuntimeError('global budget exhausted: ' + kind)
        if kind == 'run':
            if amount != 1 or campaign not in CAMPAIGNS or not isinstance(run_id, str) or not run_id or run_id in state['runs']:
                raise ValueError('unique run and known campaign required')
            if type(duration_s) not in (int, float) or not 0 < duration_s <= 150:
                raise ValueError('run duration exceeds 150 seconds')
            if state['campaign_used'][campaign] >= CAMPAIGNS[campaign]:
                raise RuntimeError('campaign budget exhausted')
            state['campaign_used'][campaign] += 1
            state['runs'][run_id] = {'campaign': campaign, 'captures': 0, 'duration_s': duration_s}
        elif kind == 'capture':
            if campaign is not None or run_id not in state['runs']:
                raise ValueError('capture requires reserved run')
            run = state['runs'][run_id]
            if run['captures'] + amount > (12 if run['campaign'] == 'F' else 20):
                raise RuntimeError('run capture budget exhausted')
            run['captures'] += amount
        elif campaign is not None or run_id is not None:
            raise ValueError('build cannot associate run')
        state['used'][kind] += amount
        event = {'sequence': len(state['events']), 'kind': kind, 'amount': amount,
                 'campaign': campaign, 'run_id': run_id, 'reserved_at_ns': time.time_ns()}
        state['events'].append(event)
        fd, temporary = tempfile.mkstemp(prefix='.budget-', dir=path.parent)
        try:
            with os.fdopen(fd, 'w') as out:
                json.dump(state, out, indent=2); out.write('\n'); out.flush(); os.fsync(out.fileno())
            os.replace(temporary, path)
            _sync_dir(path.parent)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return event
