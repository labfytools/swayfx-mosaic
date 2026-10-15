#!/usr/bin/env python3
"""Generate protocols and compile C17 clients, without executing any client."""
import argparse,json,shlex,subprocess
from pathlib import Path
from gate import canonical_lab,clean_environment,durable,sha,need,disable_dump

def prepare(lab):
 disable_dump();lab=canonical_lab(lab);src=Path(__file__).resolve().parent;build=lab/"followup-work/client-build";build.mkdir(parents=True,exist_ok=False)
 env=clean_environment(lab);commands=[]
 def invoke(argv):
  r=subprocess.run(list(map(str,argv)),env=env,capture_output=True,text=True,timeout=30)
  commands.append(dict(argv=list(map(str,argv)),exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
  durable(lab/"followup-work/client-compile.json",dict(status="PENDING" if r.returncode==0 else "FAIL",commands=commands,runtime="NOT_RUN"))
  need(r.returncode==0,"client build command failed");return r.stdout.strip()
 versions={name:invoke([name,"--version"]) for name in ("cc","wayland-scanner","pkg-config")}
 flags=shlex.split(invoke(["pkg-config","--cflags","--libs","wayland-client"]))
 for protocol,xml in (("xdg-shell","xdg-shell.xml"),("virtual-pointer","wlr-virtual-pointer-unstable-v1.xml")):
  invoke(["wayland-scanner","client-header",src/"protocols"/xml,build/(protocol+"-client.h")])
  invoke(["wayland-scanner","private-code",src/"protocols"/xml,build/(protocol+"-protocol.c")])
 for name,protocol in (("fullscreen-client","xdg-shell"),("nested-client","xdg-shell"),("vertical-client","xdg-shell"),("saved-client","xdg-shell"),("static-reference","xdg-shell"),("pointer-daemon","virtual-pointer")):
  invoke(["cc","-std=c17","-O2","-Wall","-Wextra","-I",build,src/"clients"/(name+".c"),build/(protocol+"-protocol.c"),"-o",build/name,*flags])
 durable(lab/"followup-work/client-compile.json",dict(status="PASS",commands=commands,versions=versions,inputs={str(p.relative_to(src)):sha(p) for folder in ("clients","protocols") for p in (src/folder).iterdir()},generated={str(p.relative_to(build)):sha(p) for p in build.iterdir()},runtime="NOT_RUN"))

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--lab",required=True);a=p.parse_args();prepare(a.lab)
