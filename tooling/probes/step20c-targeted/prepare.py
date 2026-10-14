#!/usr/bin/env python3
"""Offline only: copy verified retained clients, compile FX, preserve closure."""
import argparse,json,shutil,subprocess,sys
from gate import *
def prepare(lab):
    lab=owned(lab);need(not (lab/'identity.json').exists(),'preparation already completed')
    historical=read(HIST/'matrix/compile.json')['files'];dest=lab/'clients';dest.mkdir(exist_ok=True);transfers=[]
    for name in ('nested-client','pointer-daemon','region-client','saved-client','static-reference','nested-client.c','pointer-daemon.c','region-client.c','saved-client.c','static-reference.c','xdg-shell-client.h','xdg-shell-protocol.c','virtual-pointer-client.h','virtual-pointer-protocol.c','layer-shell-client.h','layer-shell-protocol.c','wlr-layer-shell-unstable-v1.xml'):
        src=HIST/'matrix/clients'/name;need(sha(src)==historical[str(src)],'historical client exact SHA '+name);target=dest/name
        need(not target.exists(),'never overwrite prepared client '+name);shutil.copy2(src,target);transfers.append(dict(source=str(src),source_sha256=sha(src),destination=str(target),sha256=sha(target)))
    for v,(binary,digest) in BINARIES.items():need(sha(binary)==digest,'exact '+v+' binary')
    need(sha(WLROOTS)==WLROOTS_SHA,'exact wlroots')
    commands=[];fx=HERE/'fx-client.c'
    need(fx.exists(),'FX source required before preparation')
    flags=subprocess.run(['pkg-config','--cflags','--libs','wayland-client'],capture_output=True,text=True,check=True,timeout=10).stdout.split()
    argv=['cc','-std=c17','-O2','-Wall','-Wextra','-I',str(dest),str(fx),str(dest/'xdg-shell-protocol.c'),str(dest/'layer-shell-protocol.c'),'-o',str(dest/'fx-client'),*flags]
    result=subprocess.run(argv,capture_output=True,text=True,timeout=30);commands.append(dict(argv=argv,exit=result.returncode,stdout=result.stdout,stderr=result.stderr));need(result.returncode==0,'FX client compilation')
    closure=set(p for p in BASE.iterdir() if p.is_file())
    closure.update(MATRIX/n for n in ('engine.py','cases.py','geometry.py','protocols.py','prepare.py','gate.py','tests.py'))
    closure.update(Path(t['source']) for t in transfers)
    closure.update([HIST/'matrix/compile.json',HIST/'matrix/freeze.json',HIST/'matrix/review.json',HIST/'matrix/executed-v2-archive/freeze.json',HIST/'matrix/executed-v2-archive/review.json',HIST/'matrix/executed-v2-archive/archive-map.json'])
    # Include all retained source files, patches and provenance that establish
    # binaries/libraries, plus all archive originals imported by old reviews.
    for folder in (HIST/'mosaic-source',HIST/'swayfx-source',HIST/'scene-source',HIST/'wlroots-source',HIST/'release-shape/mosaic-source'):
        if folder.exists():closure.update(p for p in folder.rglob('*') if p.is_file() and '.git' not in p.parts and not any(x.startswith('build') for x in p.relative_to(folder).parts))
    for receipt in (HIST/'phase-a.json',HIST/'parent/native-source-audit.json',HIST/'release-shape/build.json',lab/'parent/historical-verification.json'):
        if receipt.exists():closure.add(receipt)
    for frozen in (HIST/'matrix/freeze.json',HIST/'horizontal/freeze.json'):
        for name in read(frozen)['files']:
            p=Path(name)
            if p.exists():closure.add(p)
    closure.update(p for p,_ in BINARIES.values());closure.update([WLROOTS,SCENE,fx,Path(sys.executable).resolve()])
    import PIL
    closure.update(p for p in Path(PIL.__file__).parent.rglob('*') if p.is_file() and p.suffix in ('.py','.so'))
    closure.update(Path(shutil.which(t)).resolve() for t in ('swaymsg','grim','swaybg','cc','pkg-config','wayland-scanner'))
    for rid in RUNS:(lab/'runs'/rid).mkdir(parents=True)
    initialize(lab)
    audit={}
    for variant,source in [('A',HIST/'mosaic-source'),('G',HIST/'release-shape/mosaic-source')]:
        rows={name:(source/name).read_text() for name in ('sway/commands/gaps.c','sway/main.c','sway/server.c','sway/desktop/transaction.c','sway/desktop/layer_shell.c')}
        need('argc == 4 && !config->reading' in rows['sway/commands/gaps.c'] and 'arrange_workspace(ws);' in rows['sway/commands/gaps.c'],'runtime gaps source')
        need('server.txn_timeout_ms = atoi' in rows['sway/main.c'] and 'if (!server->txn_timeout_ms)' in rows['sway/server.c'] and 'server.txn_timeout_ms);' in rows['sway/desktop/transaction.c'],'timeout source')
        audit[variant]=dict(paths={str(source/name):sha(source/name) for name in rows},gaps='gaps inner current set 30',startup='-Dtxn-timeout=2500; applied value requires argv plus actual elapsed timeout; native value log absent',marker='layer_shell.c constructor source bound; native IDs/child count absent')
    durable(lab/'identity.json',dict(scope=SCOPE,status='PREPARED_FOR_REVIEW',runtime='NOT RUN',closure=sorted(map(str,closure)),transfers=transfers,commands=commands,scene_sha256=sha(SCENE),source_audit=audit,clients={str(p):sha(p) for p in dest.iterdir() if p.is_file()},saved_diagnostic='DISABLED; parent decision and distinct reviewed build required'),True)
    print('PREPARED offline only; compositor NOT RUN; independent review PENDING')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--lab',type=Path,required=True);a=p.parse_args();prepare(a.lab)
