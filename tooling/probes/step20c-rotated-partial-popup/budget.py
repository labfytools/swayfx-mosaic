"""Persistent one-run-per-mode budget for the independent static-R90 campaign."""
import fcntl
import json
import os
from pathlib import Path

MODES = ('control', 'private_standard', 'private_mosaic')


class Budget:
    def __init__(self, lab):
        self.lab = Path(lab)
        self.lock = (self.lab / 'partial-campaign.lock').open('a')
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.path = self.lab / 'partial-campaign-budget.json'

    def read(self):
        if not self.path.exists():
            if (self.lab / 'runs').exists() and any((self.lab / 'runs').iterdir()):
                raise ValueError('missing ledger with retained run')
            return {'version': 1, 'runs': []}
        state = json.loads(self.path.read_text())
        runs = state.get('runs')
        if state.get('version') != 1 or not isinstance(runs, list) or len(runs) != len(set(runs)) or any(r not in MODES for r in runs):
            raise ValueError('invalid ledger')
        return state

    def reserve(self, mode):
        state = self.read()
        if mode not in MODES or mode in state['runs'] or len(state['runs']) >= 3:
            raise ValueError('run budget exhausted or duplicate mode')
        state['runs'].append(mode)
        tmp = self.path.with_suffix('.tmp')
        with tmp.open('w') as output:
            json.dump(state, output, indent=2)
            output.write('\n')
            output.flush()
            os.fsync(output.fileno())
        tmp.replace(self.path)
        fd = os.open(self.lab, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        return state
