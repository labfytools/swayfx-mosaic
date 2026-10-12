"""Persistent one-run target-timeout budget; every reservation is durable."""
import fcntl
import json
import os
from pathlib import Path

LIMITS = {'run': 1, 'episode': 1, 'camera': 1, 'capture': 12}


def reserve(lab: Path, resource: str) -> dict:
    if resource not in LIMITS:
        raise ValueError('unknown budget resource')
    path = lab / 'timeout-budget.json'
    with path.open('a+') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        file.seek(0)
        raw = file.read()
        state = json.loads(raw) if raw else {key: 0 for key in LIMITS}
        if state[resource] >= LIMITS[resource]:
            raise RuntimeError(f'{resource} budget exhausted')
        if resource != 'run' and state['run'] != 1:
            raise RuntimeError('run must be reserved first')
        state[resource] += 1
        file.seek(0)
        file.truncate()
        json.dump(state, file, sort_keys=True)
        file.write('\n')
        file.flush()
        os.fsync(file.fileno())
        return state
