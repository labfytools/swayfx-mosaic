#!/usr/bin/env python3
"""Compile-only C17 clients/protocols outside Git. Never execute any client."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
from support import sha,save,environment
from model import require

HERE=Path(__file__).resolve().parent
PROBES=HERE.parent


def prepare(lab):
    dest=lab/'client-build';dest.mkdir(exist_ok=True)
    raw=lab/'raw'
    commands=[]
    def command(label,args):
        result=subprocess.run(list(map(str,args)),cwd=dest,env=environment(),text=True,capture_output=True,timeout=30)
        (raw/(label+'.stdout')).write_text(result.stdout);(raw/(label+'.stderr')).write_text(result.stderr)
        commands.append(dict(label=label,argv=list(map(str,args)),exit=result.returncode))
        require(result.returncode==0,'client-preparation-'+label)
        return result.stdout
    contract=json.loads((HERE/'client-contract.json').read_text())
    inputs={}
    for name,source in [('nested-client.c',PROBES/'step20c-nested-grab/nested-client.c'),('pointer-daemon.c',PROBES/'step20c-valid-grab/pointer-daemon.c'),('static-reference.c',PROBES/'step20c-saved-target-timeout-input/static-reference.c'),('saved-client.c',PROBES/'step20c-saved-target-timeout-input/saved-client.c')]:
        shutil.copyfile(source,dest/name);inputs[str(source)]=sha(source)
    require(inputs[str(PROBES/'step20c-nested-grab/nested-client.c')]=='2e40c98af72a0df8b316810589a0be8f4425a763db1de448b49a7813956b6f7d','frozen-nested-source')
    command('placement-check',['git','apply','--check',HERE/'placement.patch'])
    command('placement-apply',['git','apply',HERE/'placement.patch'])
    prior=PROBES/'step20c-static-nested-grab/placement.patch'
    require(sha(prior)==sha(HERE/'placement.patch'),'byte-identical-placement')
    require(sha(dest/'nested-client.c')==contract['adapted_nested_sha256'],'byte-identical-adapted-client')
    protocols={}
    for stem,xml in [('xdg-shell',Path('/usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml')),('virtual-pointer',PROBES/'step20c-valid-grab/wlr-virtual-pointer-unstable-v1.xml')]:
        for mode,suffix in [('client-header','-client.h'),('private-code','-protocol.c')]:
            path=dest/(stem+suffix);command(stem+'-'+mode,['wayland-scanner',mode,xml,path])
            require(sha(path)==contract['protocols'][path.name],'byte-identical-protocol-'+path.name)
            protocols[path.name]=sha(path)
    flags=command('wayland-flags',['pkg-config','--cflags','--libs','wayland-client']).split()
    builds=[]
    for name,stem in [('nested-client','xdg-shell'),('pointer-daemon','virtual-pointer'),('static-reference','xdg-shell')]:
        args=['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-I'+str(dest),dest/(name+'.c'),dest/(stem+'-protocol.c'),*flags]
        command(name+'-syntax',args+['-fsyntax-only']);command(name+'-compile',args+['-o',dest/name])
        builds.append(dict(client=name,source=sha(dest/(name+'.c')),binary=sha(dest/name),execution='NOT RUN'))
    save(lab,'client-provenance',dict(status='PASS C17 -Werror syntax/build; clients NOT RUN',inputs=inputs,patch=sha(HERE/'placement.patch'),adapted_nested=sha(dest/'nested-client.c'),protocols=protocols,protocol_comparison='byte-identical historical exact sources',builds=builds,commands=commands))
    print('Client-only C17 preparation PASS; no client execution')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('lab',type=Path);prepare(parser.parse_args().lab)
