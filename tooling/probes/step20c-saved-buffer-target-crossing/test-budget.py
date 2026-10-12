"""Offline exclusive-ledger regression; never touches a campaign LAB."""
import json
import multiprocessing
import tempfile
from pathlib import Path
from budget import reserve

with tempfile.TemporaryDirectory() as root:
    lab = Path(root)
    reserve(lab, 'control')
    reserve(lab, 'control', 'ack')
    reserve(lab, 'control', 'timeout')
    for episode in (None, 'ack', 'timeout'):
        try:
            reserve(lab, 'control', episode)
            raise AssertionError('duplicate accepted')
        except RuntimeError:
            pass
    for mode in ('private_standard', 'private_mosaic'):
        reserve(lab, mode)
        reserve(lab, mode, 'ack')
        reserve(lab, mode, 'timeout')
    reserve(lab, 'private_mosaic', camera=True)
    try:
        reserve(lab, 'private_mosaic', camera=True)
        raise AssertionError('second camera adjustment accepted')
    except RuntimeError:
        pass
    for mode in ('control', 'private_standard', 'private_mosaic'):
        for _ in range(16):
            reserve(lab, mode, capture=True)
        try:
            reserve(lab, mode, capture=True)
            raise AssertionError('seventeenth capture accepted')
        except RuntimeError:
            pass
    state = json.loads((lab / 'target-budget.json').read_text())
    assert len(state['episodes']) == 6
    assert sum(state['captures'].values()) == 48
print('PASS persistent run/episode limits')


def contender(path, queue):
    try:
        reserve(Path(path), 'control')
        queue.put('accepted')
    except RuntimeError:
        queue.put('rejected')


with tempfile.TemporaryDirectory() as root:
    context = multiprocessing.get_context('fork')
    queue = context.Queue()
    children = [context.Process(target=contender, args=(root, queue))
                for _ in range(2)]
    for child in children:
        child.start()
    for child in children:
        child.join(5)
        assert child.exitcode == 0
    assert sorted(queue.get() for _ in children) == ['accepted', 'rejected']
print('PASS exclusive reservation')
