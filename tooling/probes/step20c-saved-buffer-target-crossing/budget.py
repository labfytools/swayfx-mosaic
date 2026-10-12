"""One persistent, exclusive ledger for the independent target campaign."""
import fcntl
import json
import os
from pathlib import Path

MODES = ('control', 'private_standard', 'private_mosaic')


def reserve(lab: Path, mode: str, episode: str | None = None,
            *, camera: bool = False, capture: bool = False) -> dict:
    if mode not in MODES or episode not in (None, 'ack', 'timeout'):
        raise ValueError('invalid reservation')
    if int(camera) + int(capture) + int(episode is not None) > 1:
        raise ValueError('reserve one resource per call')
    path = lab / 'target-budget.json'
    with path.open('a+') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        file.seek(0)
        raw = file.read()
        state = json.loads(raw) if raw else {
            'runs': [], 'episodes': [], 'camera': [], 'captures': {m: 0 for m in MODES}}
        if camera:
            if mode != 'private_mosaic' or mode not in state['runs'] or state['camera']:
                raise RuntimeError('camera budget exhausted')
            state['camera'].append(mode)
        elif capture:
            if mode not in state['runs'] or state['captures'][mode] >= 16 or sum(state['captures'].values()) >= 48:
                raise RuntimeError('capture budget exhausted')
            state['captures'][mode] += 1
        elif episode is None:
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
