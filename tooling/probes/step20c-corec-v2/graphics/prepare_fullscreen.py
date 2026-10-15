"""C17 build of the prospective client only. Never executes it."""
import json,shlex,subprocess
from pathlib import Path
from gate import canonical_lab,clean_environment,durable,sha,need

def prepare(lab):
 lab=canonical_lab(lab);src=Path(__file__).resolve().parent;build=lab/'graphics-next-work/client-build';build.mkdir(exist_ok=False)
 env=clean_environment(lab);commands=[]
 def invoke(argv):
  r=subprocess.run(list(map(str,argv)),env=env,capture_output=True,text=True,timeout=30)
  commands.append(dict(argv=list(map(str,argv)),exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
  durable(lab/'graphics-next-work/client-compile.json',dict(status='PENDING' if r.returncode==0 else 'FAIL',commands=commands,runtime='NOT_RUN'))
  need(r.returncode==0,'fullscreen client build failed');return r.stdout.strip()
 flags=shlex.split(invoke(['pkg-config','--cflags','--libs','wayland-client']))
 for mode,suffix in [('client-header','client.h'),('private-code','protocol.c')]:invoke(['wayland-scanner',mode,src/'protocols/xdg-shell.xml',build/('xdg-shell-'+suffix)])
 invoke(['cc','-std=c17','-O2','-Wall','-Wextra','-I',build,src/'clients/fullscreen-client.c',build/'xdg-shell-protocol.c','-o',build/'fullscreen-client',*flags])
 durable(lab/'graphics-next-work/client-compile.json',dict(status='PASS',commands=commands,inputs={name:sha(src/name) for name in ('clients/fullscreen-client.c','protocols/xdg-shell.xml')},generated={p.name:sha(p) for p in build.iterdir()},runtime='NOT_RUN'))
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--lab',required=True);prepare(p.parse_args().lab)
