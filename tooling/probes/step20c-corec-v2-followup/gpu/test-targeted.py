"""G3 offline C17/FakeGL/protocol/client checks; no compositor build/run."""
import argparse
import ctypes
import json
import hashlib
import os
from pathlib import Path
import resource
import shlex
import subprocess
import sys

KIT = Path(__file__).resolve().parent


def main():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    assert ctypes.CDLL(None).prctl(4, 0, 0, 0, 0) == 0
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lab', required=True, type=Path)
    p.add_argument('--scene', required=True, type=Path)
    a = p.parse_args()
    lab, scene = a.lab.resolve(strict=True), a.scene.resolve(strict=True)
    assert str(lab).startswith('/var/tmp/swayfx-mosaic-step20c-native-closure-')
    assert scene.is_relative_to(lab)
    work = lab / 'g3-offline'
    work.mkdir(mode=0o700, exist_ok=True)
    env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}
    for key, name in [('TMPDIR','scratch'),('TMP','scratch'),('TEMP','scratch'),
                      ('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),
                      ('PYTHONPYCACHEPREFIX','pycache'),('CCACHE_DIR','ccache')]:
        path = work / name
        path.mkdir(mode=0o700, exist_ok=True)
        env[key] = str(path)
    flags = shlex.split(subprocess.check_output(['pkg-config','--cflags','wlroots-0.20','pixman-1','egl','glesv2','libdrm','wayland-server'],env=env,text=True))
    base = ['cc','-std=c17','-D_GNU_SOURCE','-DWLR_USE_UNSTABLE','-DWLR_PRIVATE=',
            '-DWLR_LITTLE_ENDIAN=1','-DWLR_BIG_ENDIAN=0','-Wall','-Wextra','-Werror',
            '-Wno-unused-parameter','-Wno-missing-braces','-I'+str(scene/'include')]
    root = '-DG3_ROOT="'+str(lab/'gpu-work/acquisition')+'"'
    commands = [
        ['cc','-std=c17','-Wall','-Wextra','-Werror','-I'+str(KIT),str(KIT/'test_gl.c'),'-o',str(work/'test_gl')],
        [str(work/'test_gl')],
        [sys.executable,str(KIT/'test_mutations.py')],
        [sys.executable,str(KIT/'validate_source.py')],
        [sys.executable,str(KIT/'test_protocol.py')],
        [sys.executable,str(KIT/'test_begin.py')],
        base + flags + [root,'-I'+str(KIT),'-Wno-unused-function','-ffunction-sections','-fdata-sections',str(KIT/'test_native.c'),'-Wl,--gc-sections','-o',str(work/'test_native')],
        [str(work/'test_native')],
        base + flags + [root,'-fsyntax-only',str(scene/'render/fx_renderer/fx_pass.c')],
    ]
    for xml, header in [('wlr-layer-shell-unstable-v1.xml','layer-shell-client.h'),('xdg-shell.xml','xdg-shell-client.h')]:
        commands.append(['wayland-scanner','client-header',str(KIT/'protocols'/xml),str(work/header)])
    commands.append(['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-missing-braces','-I'+str(work),'-fsyntax-only',str(KIT/'clients-g2.c')])
    rows=[]
    for i, command in enumerate(commands):
        r = subprocess.run(command, cwd=work, env=env, text=True, capture_output=True, timeout=60)
        log = work / f'test-{i}.log'
        log.write_text(r.stdout+r.stderr)
        rows.append({'command':command,'exit':r.returncode,'log':log.name})
        print(f'{i}: exit={r.returncode}\n{r.stdout}{r.stderr}',flush=True)
        if r.returncode:
            break
    passed=len(rows)==len(commands) and all(r['exit']==0 for r in rows)
    (work/'receipt.json').write_text(json.dumps({'schema':'G3-offline-v1','pass':passed,
        'review':'PENDING_INDEPENDENT','runtime':'NOT_RUN','compositor_build':'NOT_RUN',
        'environment':env,'scene':str(scene),'native_sha256':{n:hashlib.sha256((scene/'render/fx_renderer'/n).read_bytes()).hexdigest() for n in ('fx_pass.c','g2_gl.h','g2_native.h')},'headers':{n:hashlib.sha256(Path(n).read_bytes()).hexdigest() for n in ('/usr/include/EGL/egl.h','/usr/include/GLES3/gl3.h','/usr/include/libdrm/drm_fourcc.h')},'commands':rows},indent=2)+'\n')
    raise SystemExit(0 if passed else 1)


if __name__=='__main__':
    main()
