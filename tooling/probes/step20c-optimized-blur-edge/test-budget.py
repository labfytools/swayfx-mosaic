"""Offline tests use disposable ledgers; never touch campaign reservations."""
import json
import multiprocessing
import tempfile
from pathlib import Path
from budget import reserve, MODES

def denied(call):
    try:
        call()
    except (ValueError, RuntimeError, KeyError, TypeError):
        return
    raise AssertionError('accepted forbidden reservation')

def contender(root, queue):
    try:
        reserve(root, 'R0', 'run', Path(root) / 'contention.json')
        queue.put('accepted')
    except RuntimeError:
        queue.put('denied')

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / 'budget.json'
    denied(lambda: reserve(tmp, 'R0', 'capture', path))
    for mode in MODES:
        reserve(tmp, mode, 'run', path)
        denied(lambda: reserve(tmp, mode, 'run', path))
        for key, count in [('mutation', 3), ('capture', 12), ('cycle', 1),
                           ('calibration', 1 if mode in ('R2', 'R3') else 0)]:
            for _ in range(count):
                reserve(tmp, mode, key, path)
            denied(lambda: reserve(tmp, mode, key, path))
    denied(lambda: reserve(tmp + '-another', 'R0', 'run', path))
    denied(lambda: reserve(tmp, 'R4', 'run', path))
    state = json.loads(path.read_text())
    assert sum(c['capture'] for c in state['modes'].values()) == 48
    assert sum(c['mutation'] for c in state['modes'].values()) == 12
    for bad in ['', '{}', '{"campaign":"wrong"}']:
        path.write_text(bad)
        denied(lambda: reserve(tmp, 'R0', 'run', path))
    for corrupt in [True, -1, 2, 1.0]:
        state['modes']['R0']['run'] = corrupt
        path.write_text(json.dumps(state))
        denied(lambda: reserve(tmp, 'R1', 'capture', path))
with tempfile.TemporaryDirectory() as tmp:
    ctx = multiprocessing.get_context('fork')
    queue = ctx.Queue()
    children = [ctx.Process(target=contender, args=(tmp, queue)) for _ in range(2)]
    for child in children:
        child.start()
    for child in children:
        child.join(5)
        assert child.exitcode == 0
    assert sorted(queue.get(timeout=1) for _ in children) == ['accepted', 'denied']
print('PASS exact exhaustion, no fifth run, cross-LAB, corrupt schema/counters, exclusive lock')
