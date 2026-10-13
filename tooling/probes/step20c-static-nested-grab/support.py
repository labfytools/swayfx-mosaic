"""Private probe ownership, durable budgets and bounded argv execution.

WHY: an exhausted experiment must not be restarted by replacing its LAB.
CONTRACT: stable exclusive owner and lock files; fsync precedes every action.
INVARIANT: failures consume all reservations, never refund or reset counters.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

REPO = Path('/home/fy59/Documents/Development/swayfx-mosaic')
OWNER = Path.home() / 'swayfx-mosaic-static-nested-grab-v1.owner'
BINARY = Path('/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/stage-static/usr/bin/swayfx-mosaic')
BINARY_SHA = 'f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b'
WLROOTS_SHA = '7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837'
NESTED_SHA = '2e40c98af72a0df8b316810589a0be8f4425a763db1de448b49a7813956b6f7d'
LIMITS = dict(run=1, chain=2, grab=4, click=9, capture=16, camera=2, transition=1, move=24)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(lab, name, data):
    (Path(lab)/'results'/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')

def durable(path, data):
    fd,tmp=tempfile.mkstemp(prefix='.ledger-',dir=path.parent)
    with os.fdopen(fd,'w') as out:
        json.dump(data,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
    os.replace(tmp,path)
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def initial(lab):
    path=Path(lab)/'results/budget.json'
    with path.open('x') as out:
        json.dump(dict(limits=LIMITS,used=dict.fromkeys(LIMITS,0),events=[]),out,indent=2)
        out.write('\n');out.flush();os.fsync(out.fileno())
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def reserve(lab, *kinds):
    lab=Path(lab)
    with (lab/'budget.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        path=lab/'results/budget.json';state=json.loads(path.read_text())
        valid=(state.get('limits')==LIMITS and set(state.get('used',{}))==set(LIMITS)
            and all(type(state['used'][k]) is int and 0<=state['used'][k]<=LIMITS[k] for k in LIMITS)
            and len(state.get('events',[]))==sum(state['used'].values())
            and all(e.get('seq')==i and e.get('kind') in LIMITS for i,e in enumerate(state.get('events',[])))
            and all(sum(e['kind']==k for e in state['events'])==state['used'][k] for k in LIMITS))
        if not valid or not kinds or any(k not in LIMITS for k in kinds):
            raise RuntimeError('corrupt/invalid ledger')
        if any(state['used'][k]+kinds.count(k)>LIMITS[k] for k in kinds):
            raise RuntimeError('budget exhausted')
        for k in kinds:
            state['used'][k]+=1
            state['events'].append(dict(seq=len(state['events']),kind=k,ns=time.monotonic_ns()))
        durable(path,state)
        return state

def environment():
    # WHY: inherited desktop/loader settings must not select a daily socket.
    excluded={'DISPLAY','WAYLAND_DISPLAY','SWAYSOCK','I3SOCK','XDG_RUNTIME_DIR',
        'WAYLAND_DEBUG','DBUS_SESSION_BUS_ADDRESS','XDG_SESSION_ID','XDG_SEAT',
        'XDG_VTNR','XDG_SESSION_TYPE','XDG_CURRENT_DESKTOP','XDG_SESSION_DESKTOP',
        'LD_LIBRARY_PATH','LD_PRELOAD','LD_AUDIT','PKG_CONFIG_PATH','WLR_BACKENDS',
        'WLR_RENDERER','WLR_HEADLESS_OUTPUTS','WLR_DRM_DEVICES','WLR_LIBINPUT_NO_DEVICES'}
    env={k:v for k,v in os.environ.items() if k not in excluded and not k.startswith('WLR_')}
    env.update(LC_ALL='C',PYTHONDONTWRITEBYTECODE='1')
    return env

def command(lab,label,argv,cwd=None):
    result=subprocess.run(list(map(str,argv)),cwd=cwd,env=environment(),capture_output=True,text=True,timeout=30)
    (lab/'raw'/(label+'.stdout')).write_text(result.stdout)
    (lab/'raw'/(label+'.stderr')).write_text(result.stderr)
    with (lab/'raw/commands.jsonl').open('a') as out:
        out.write(json.dumps(dict(label=label,argv=list(map(str,argv)),exit=result.returncode,cwd=str(cwd)))+'\n')
    assert result.returncode==0,(label,result.returncode,result.stderr)
    return result.stdout

def verify(manifest):
    seen=set()
    for row in Path(manifest).read_text().splitlines():
        digest,p=row.split('  ',1)
        assert p not in seen and sha(p)==digest,(manifest,p)
        seen.add(p)
    assert seen
    return dict(entries=len(seen),sha256=sha(manifest))

def inventory(path, files):
    with Path(path).open('x') as out:
        for p in sorted(files):out.write(f'{sha(p)}  {p}\n')
    return verify(path)
