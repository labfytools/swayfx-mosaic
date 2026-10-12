"""Offline ledger limits and lock contention; never touches a campaign LAB."""
import json
import multiprocessing
import tempfile
from pathlib import Path
from budget import reserve

with tempfile.TemporaryDirectory() as root:
    lab = Path(root)
    reserve(lab, 'run')
    reserve(lab, 'episode')
    reserve(lab, 'camera')
    for _ in range(12):
        reserve(lab, 'capture')
    assert json.loads((lab / 'timeout-budget.json').read_text()) == {
        'run': 1, 'episode': 1, 'camera': 1, 'capture': 12}
    for resource in ('run', 'episode', 'camera', 'capture'):
        try:
            reserve(lab, resource)
            raise AssertionError(f'{resource} oversubscription accepted')
        except RuntimeError:
            pass
print('PASS one run/episode/camera and twelve captures')


def contender(path, queue):
    try:
        reserve(Path(path), 'run')
        queue.put('accepted')
    except RuntimeError:
        queue.put('rejected')

with tempfile.TemporaryDirectory() as root:
    context = multiprocessing.get_context('fork')
    queue = context.Queue()
    children = [context.Process(target=contender, args=(root, queue)) for _ in range(2)]
    for child in children:
        child.start()
    for child in children:
        child.join(5)
        assert child.exitcode == 0
    assert sorted(queue.get() for _ in children) == ['accepted', 'rejected']
print('PASS exclusive reservation')
