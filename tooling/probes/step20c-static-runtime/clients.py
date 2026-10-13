#!/usr/bin/env python3
"""Compile byte-verified historical clients and the preserved pointer adaptation.

CONTRACT: no held transaction or new popup behavior is added to these fixtures.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
from support import REPO,command,save,sha
p=argparse.ArgumentParser();p.add_argument('lab',type=Path);a=p.parse_args();lab=a.lab.resolve();src=lab/'client-source';src.mkdir()
paths={'saved-client.c':'step20c-saved-target-timeout-input/saved-client.c','static-reference.c':'step20c-saved-target-timeout-input/static-reference.c','pointer-daemon.c':'step20c-valid-grab/pointer-daemon.c','virtual-pointer.xml':'step20c-valid-grab/wlr-virtual-pointer-unstable-v1.xml'}
inventory=[]
for name,rel in paths.items():
    origin=REPO/'tooling/probes'/rel;shutil.copy2(origin,src/name);assert sha(origin)==sha(src/name)
    inventory.append({'source':str(origin),'sha256':sha(origin),'destination':str(src/name)})
patch=REPO/'tooling/probes/step20c-vertical-grab/pointer-extents.patch'
command(lab,'pointer-check',['git','apply','--check',patch],src);command(lab,'pointer-apply',['git','apply',patch],src)
for stem,xml in [('xdg-shell',Path('/usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml')),('virtual-pointer',src/'virtual-pointer.xml')]:
    command(lab,stem+'-header',['wayland-scanner','client-header',xml,src/(stem+'-client.h')])
    command(lab,stem+'-code',['wayland-scanner','private-code',xml,src/(stem+'-protocol.c')])
# The historical pointer include uses its original generated filename.
shutil.copy2(src/'virtual-pointer-client.h',src/'virtual-pointer.h')
flags=subprocess.check_output(['pkg-config','--cflags','--libs','wayland-client'],text=True).split()
for name,proto in [('saved-client','xdg-shell'),('static-reference','xdg-shell'),('pointer-daemon','virtual-pointer')]:
    argv=['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-I'+str(src),src/(name+'.c'),src/(proto+'-protocol.c'),*flags]
    command(lab,name+'-syntax',[*argv,'-fsyntax-only'])
    command(lab,name+'-compile',[*argv,'-o',lab/name])
save(lab,'client-provenance',{'inputs':inventory,'pointer_patch':{'source':str(patch),'sha256':sha(patch)},'adapted_pointer_sha256':sha(src/'pointer-daemon.c'),'C17':'PASS'})
