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

REPO = Path(__file__).resolve().parents[3]
# No immutable compositor is built/copied and no runtime budget is initialized.

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

def reserve(lab, *kinds):
    from ledger import reserve as debit
    return debit(Path(lab)/'results/budget.json', *kinds)

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
