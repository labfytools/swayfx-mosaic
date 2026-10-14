#!/usr/bin/env python3
"""C17 builds only; no Wayland connections or compositor launches."""
import json,subprocess
from pathlib import Path
from gate import BASE,LAB,sha,durable,clean_environment,need

def prepare():
 dest=BASE/'clients';commands=[]
 flags=subprocess.run(['pkg-config','--cflags','--libs','wayland-client'],capture_output=True,text=True,timeout=10,check=True).stdout.split()
 for n,proto in [('nested-client','xdg-shell'),('vertical-client','xdg-shell'),('saved-client','xdg-shell'),('static-reference','xdg-shell'),('pointer-daemon','virtual-pointer'),('fx-client','xdg-shell')]:
  argv=['cc','-std=c17','-O2','-Wall','-Wextra',str(dest/(n+'.c')),str(dest/(proto+'-protocol.c')),*([str(dest/'layer-shell-protocol.c')] if n=='fx-client' else []),'-o',str(dest/n),*flags]
  r=subprocess.run(argv,env=clean_environment(),capture_output=True,text=True,timeout=30);commands.append(dict(argv=argv,exit=r.returncode,stdout=r.stdout,stderr=r.stderr));need(r.returncode==0,'client compile '+n)
 for rid in __import__('plans').RUNS:(BASE/'runs'/rid).mkdir(parents=True,exist_ok=True)
 durable(BASE/'compile.json',dict(commands=commands,files={str(p):sha(p) for p in dest.iterdir() if p.is_file()},runtime='NOT RUN'),True)

if __name__=='__main__':prepare()
