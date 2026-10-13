"""Private probe support; no desktop environment or global process ownership.

WHY: failures must consume the same persistent experiment budget as successes.
CONTRACT: a stable flock file serializes durable atomic ledger updates.
INVARIANT: no reset/refund; only argv execution and owned process groups.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

REPO = Path(__file__).resolve().parents[3]
LIMITS = {'run': 1, 'capture': 12, 'camera': 1, 'visible_click': 1,
          'forbidden_click': 1, 'standard_click': 1, 'move': 8}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(lab, name, value):
    (Path(lab)/'results'/(name+'.json')).write_text(json.dumps(value, indent=2)+'\n')

def reserve(lab, kind):
    lab = Path(lab)
    if kind not in LIMITS:
        raise ValueError(kind)
    with (lab/'budget.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = lab/'results/budget.json'
        state = json.loads(path.read_text()) if path.exists() else {
            'limits': LIMITS, 'used': dict.fromkeys(LIMITS, 0), 'events': []}
        # CONTRACT: corruption cannot create negative/extra capacity or erase history.
        valid = (state.get('limits') == LIMITS and set(state.get('used', {})) == set(LIMITS)
                 and all(type(state['used'][k]) is int and 0 <= state['used'][k] <= LIMITS[k] for k in LIMITS)
                 and len(state.get('events', [])) == sum(state['used'].values())
                 and all(e.get('sequence') == i and e.get('kind') in LIMITS for i,e in enumerate(state.get('events', [])))
                 and all(sum(e['kind'] == k for e in state['events']) == state['used'][k] for k in LIMITS))
        if not valid or state['used'][kind] >= LIMITS[kind]:
            raise RuntimeError('budget exhausted or changed: '+kind)
        state['used'][kind] += 1
        state['events'].append({'sequence': len(state['events']), 'kind': kind})
        fd, temporary = tempfile.mkstemp(prefix='.budget-', dir=path.parent)
        with os.fdopen(fd, 'w') as out:
            json.dump(state, out, indent=2); out.write('\n'); out.flush(); os.fsync(out.fileno())
        os.replace(temporary, path)
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        return state

def environment():
    env = {k:v for k,v in os.environ.items() if k not in (
        'SWAYSOCK','I3SOCK','WAYLAND_DISPLAY','DISPLAY','XDG_RUNTIME_DIR',
        'LD_LIBRARY_PATH','LD_PRELOAD','PKG_CONFIG_PATH')}
    env.update(LC_ALL='C', PYTHONDONTWRITEBYTECODE='1', MESON_ROOT_CMD='/bin/false')
    return env

def command(lab, label, argv, cwd=None, extra=None, timeout=600, allow_failure=False):
    lab=Path(lab); path=lab/'raw'/(label+'.log')
    assert not path.exists(), 'diagnostic already recorded: '+label
    with path.open('wb') as out:
        proc=subprocess.Popen(list(map(str,argv)),cwd=cwd,env={**environment(),**(extra or {})},
                              stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            deadline=time.monotonic()+timeout
            while proc.poll() is None:
                if time.monotonic()>=deadline or path.stat().st_size>64*1024*1024:
                    raise subprocess.TimeoutExpired(argv,timeout)
                time.sleep(.1)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGTERM)
            try: proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            try: os.killpg(proc.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            raise
    with (lab/'raw/commands.jsonl').open('a') as out:
        out.write(json.dumps({'label':label,'argv':list(map(str,argv)), 'cwd':str(cwd),
                              'env':extra or {},'exit':proc.returncode})+'\n')
    assert path.stat().st_size < 64*1024*1024, 'output bound exceeded'
    if not allow_failure and proc.returncode:
        raise RuntimeError(f'{label} exit={proc.returncode}; inspect {path}')
    return path.read_text(errors='replace')
