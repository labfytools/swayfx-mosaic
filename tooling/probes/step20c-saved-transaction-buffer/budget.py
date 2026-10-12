"""Persistent campaign reservations. Failed attempts are never refunded."""
import fcntl
import json
import os
from pathlib import Path

MODES = ('control', 'private_standard', 'private_mosaic')


def reserve(lab: Path, mode: str, episode: str | None = None) -> dict:
    if mode not in MODES or episode not in (None, 'ack', 'timeout'):
        raise ValueError('invalid reservation')
    path = lab / 'saved-budget.json'
    with path.open('a+') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        file.seek(0)
        raw = file.read()
        state = json.loads(raw) if raw else {'runs': [], 'episodes': []}
        file.seek(0)
        if episode is None:
            if mode in state['runs'] or len(state['runs']) >= 3:
                raise RuntimeError('run budget exhausted')
            state['runs'].append(mode)
        else:
            key = [mode, episode]
            if mode not in state['runs'] or key in state['episodes'] or len(state['episodes']) >= 6:
                raise RuntimeError('episode budget exhausted')
            state['episodes'].append(key)
        file.seek(0)
        file.truncate()
        json.dump(state, file, sort_keys=True)
        file.write('\n')
        file.flush()
        os.fsync(file.fileno())
        return state
