#!/usr/bin/env python3
"""Private C17 client preparation; never reserves or launches a compositor."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;REPO=ROOT.parents[2]
sys.path.insert(0,str(ROOT));from horizontal_gate import DEFAULT_LAB,BASE,sha,env,exclusive,OLD_CLIENTS
from protocols import RUNS
lab=DEFAULT_LAB/'matrix';lab.mkdir();dest=lab/'clients';dest.mkdir();commands=[];sources=[]
def command(argv,cwd=None):
    r=subprocess.run(list(map(str,argv)),cwd=cwd,env=env(),capture_output=True,text=True,timeout=30)
    commands.append(dict(argv=list(map(str,argv)),cwd=str(cwd),exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if r.returncode:raise RuntimeError('private client preparation failed')
    return r.stdout
def copy(src,name):
    p=dest/name;shutil.copyfile(src,p);sources.append(dict(source=str(src),sha256=sha(src),destination=str(p)));return p
for n in ('nested-client.c','pointer-daemon.c','saved-client.c','static-reference.c','xdg-shell-client.h','xdg-shell-protocol.c','virtual-pointer-client.h','virtual-pointer-protocol.c'):copy(OLD_CLIENTS/n,n)
# An independent base is patched privately; original repository/historical bytes stay read only.
copy(REPO/'tooling/probes/step20c-nested-grab/nested-client.c','vertical-client.c')
patch=REPO/'tooling/probes/step20c-vertical-grab/client-vertical.patch'
p=dest/'vertical-patch';p.write_text(patch.read_text().replace('nested-client.c','vertical-client.c'))
command(['patch','--batch','--forward','--fuzz=0','-p1','-i',p],cwd=dest);sources.append(dict(source=str(patch),sha256=sha(patch),destination=str(p)))
# Extents are supplied for every injection so resized output unions remain explicit.
pointer=dest/'pointer-daemon.c';old='if (sscanf(line,"%15s %d %d",action,&x,&y)!=3) continue;'
new='unsigned width,height;\n        if (sscanf(line,"%15s %d %d %u %u",action,&x,&y,&width,&height)!=5 || !width || !height || x<0 || y<0 || (unsigned)x>=width || (unsigned)y>=height || (strcmp(action,"move") && strcmp(action,"left") && strcmp(action,"right"))) return 3;'
s=pointer.read_text();assert s.count(old)==1;s=s.replace(old,new).replace('x,y,1600,600','x,y,width,height');pointer.write_text(s)
copy(REPO/'tooling/probes/step20c-nested-grab/nested-client.c','region-client.c')
patch=REPO/'tooling/probes/step20c-mutation-coverage/mutation-client.patch';p=dest/'region-patch';p.write_text(patch.read_text().replace('nested-client.c','region-client.c'))
# Reuse only the exact added command branch; historical close_a context is absent.
minus=[line[1:] for line in patch.read_text().splitlines() if line.startswith('-') and not line.startswith('---')]
plus=[line[1:] for line in patch.read_text().splitlines() if line.startswith('+') and not line.startswith('+++')]
r=dest/'region-client.c';text=r.read_text();assert len(minus)==1 and text.count(minus[0])==1
r.write_text(text.replace(minus[0],'\n'.join(plus),1));sources.append(dict(source=str(patch),sha256=sha(patch),destination=str(p)))
copy(REPO/'tooling/probes/step20c-optimized-blur-edge/clients.c','fx-clients.c')
xml=REPO/'tooling/probes/step20c-optimized-blur-cache/wlr-layer-shell-unstable-v1.xml'
copy(xml,'wlr-layer-shell-unstable-v1.xml')
for mode,suffix in [('client-header','-client.h'),('private-code','-protocol.c')]:command(['wayland-scanner',mode,xml,dest/('layer-shell'+suffix)])
# XDG/virtual-pointer regeneration must equal the retained compiled client's wire API.
for stem,xml in [('xdg-shell',Path('/usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml')),('virtual-pointer',REPO/'tooling/probes/step20c-valid-grab/wlr-virtual-pointer-unstable-v1.xml')]:
    for mode,suffix in [('client-header','-client.h'),('private-code','-protocol.c')]:
        p=dest/(stem+suffix+'.regenerated');command(['wayland-scanner',mode,xml,p]);assert p.read_bytes()==(dest/(stem+suffix)).read_bytes()
    sources.append(dict(source=str(xml),sha256=sha(xml),destination=None))
flags=command(['pkg-config','--cflags','--libs','wayland-client']).split()
for name,protocol in [('nested-client','xdg-shell'),('vertical-client','xdg-shell'),('region-client','xdg-shell'),('saved-client','xdg-shell'),('static-reference','xdg-shell'),('pointer-daemon','virtual-pointer'),('fx-clients','xdg-shell')]:
    command(['cc','-std=c17','-O2','-Wall','-Wextra',dest/(name+'.c'),dest/(protocol+'-protocol.c'),*([dest/'layer-shell-protocol.c'] if name=='fx-clients' else []),'-o',dest/name,*flags])
exclusive(lab/'compile.json',dict(status='PASS',sources=sources,commands=commands,files={str(p):sha(p) for p in sorted(dest.iterdir()) if p.is_file()},runtime='NOT RUN'))
exclusive(lab/'protocols.json',RUNS)
for run_id in RUNS:(lab/run_id).mkdir()
print('MATRIX_CLIENTS_C17=PASS RUNS=NOT_RUN')
