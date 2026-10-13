#!/usr/bin/env python3
"""Create one exclusive LAB; copy an immutable compositor and build clients only.

CONTRACT: never launch a graphical process from preparation. No LAB retry/reset.
INVARIANT: retained historical source and manifests are read-only.
"""
import ast
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
from support import REPO,OWNER,BINARY,BINARY_SHA,WLROOTS_SHA,NESTED_SHA,sha,save,command,initial,inventory,verify

fd=os.open(OWNER,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as out:
    lab=Path(tempfile.mkdtemp(prefix='swayfx-mosaic-static-nested-grab-',dir=Path.home()))
    out.write(str(lab)+'\n');out.flush();os.fsync(out.fileno())
for n in ['raw','results','client-source','historical-source','fixture']:(lab/n).mkdir()
(lab/'campaign-owner').write_text(str(OWNER)+'\n');initial(lab)
prior=Path('/home/fy59/swayfx-mosaic-static-rgb-input-retest-hn67lnhq')
receipts={n:verify(prior/'results'/(n+'-sha256.txt')) for n in ['fixture-freeze','source','evidence']}
assert sha(BINARY)==BINARY_SHA and not BINARY.is_symlink() and stat.S_IMODE(BINARY.stat().st_mode)==0o755
shutil.copy2(BINARY,lab/'swayfx-mosaic');assert sha(lab/'swayfx-mosaic')==BINARY_SHA
elf=command(lab,'ELF',['readelf','-hW','-nW','-dW',lab/'swayfx-mosaic'])
assert 'ELF64' in elf and 'Advanced Micro Devices X86-64' in elf and '942db64269640778ee433e5970ba1100bc60f94c' in elf
assert 'libscenefx' not in elf and '(RPATH)' not in elf and '(RUNPATH)' not in elf
symbols=command(lab,'symbols',['nm',lab/'swayfx-mosaic'])
assert all(' T '+s in symbols for s in ['wlr_scene_tree_set_clip','wlr_scene_tree_get_clip'])
loader=command(lab,'loader',['ldd','-r',lab/'swayfx-mosaic'])
assert not any(s in loader for s in ['undefined symbol','not found','libscenefx'])
wl=Path('/usr/lib/libwlroots-0.20.so').resolve();assert sha(wl)==WLROOTS_SHA and str(wl) in loader
version=command(lab,'wlroots-version',['pkg-config','--modversion','wlroots-0.20']).strip();assert version=='0.20.2'
save(lab,'binary-identity',dict(status='PASS',sha256=BINARY_SHA,build_id='942db64269640778ee433e5970ba1100bc60f94c',mode='0755',ELF='ELF64 x86-64',SceneFX_dynamic=False,wlroots_sha256=WLROOTS_SHA,wlroots_version=version,source=str(BINARY),copy=str(lab/'swayfx-mosaic')))
src=lab/'client-source';inputs=[]
for name,rel in [('nested-client.c','step20c-nested-grab/nested-client.c'),('pointer-daemon.c','step20c-valid-grab/pointer-daemon.c'),('static-reference.c','step20c-saved-target-timeout-input/static-reference.c'),('saved-client.c','step20c-saved-target-timeout-input/saved-client.c')]:
    p=REPO/'tooling/probes'/rel;shutil.copy2(p,src/name);shutil.copy2(p,lab/'historical-source'/name)
    inputs.append(dict(source=str(p),sha256=sha(p),copy=str(src/name)))
assert sha(src/'nested-client.c')==NESTED_SHA
patch=REPO/'tooling/probes/step20c-static-nested-grab/placement.patch'
command(lab,'placement-check',['git','apply','--check',patch],cwd=src)
command(lab,'placement-apply',['git','apply',patch],cwd=src)
# Protocol byte identity is independently checked by regeneration, outside Git.
for name in ['xdg-shell-client.h','xdg-shell-protocol.c','virtual-pointer-client.h','virtual-pointer-protocol.c']:
    shutil.copy2(prior/'client-source'/name,src/name)
xml=Path('/usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml');shutil.copy2(xml,src/'xdg-shell.xml')
vxml=REPO/'tooling/probes/step20c-valid-grab/wlr-virtual-pointer-unstable-v1.xml';shutil.copy2(vxml,src/'virtual-pointer.xml')
assert sha(vxml)=='3ff6d540be0bc5228195bf072bde42117ea17945a5c2061add5d3cf97d6bb524'
for stem in ['xdg-shell','virtual-pointer']:
    for mode,suffix in [('client-header','-client.h'),('private-code','-protocol.c')]:
        dest=lab/'raw'/(stem+suffix)
        command(lab,stem+'-'+mode,['wayland-scanner',mode,src/(stem+'.xml'),dest])
        assert dest.read_bytes()==(src/(stem+suffix)).read_bytes(),'generated protocol differs'
flags=command(lab,'wayland-flags',['pkg-config','--cflags','--libs','wayland-client']).split()
builds=[]
for name,proto in [('nested-client','xdg-shell'),('static-reference','xdg-shell'),('pointer-daemon','virtual-pointer')]:
    args=['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-I'+str(src),src/(name+'.c'),src/(proto+'-protocol.c'),*flags]
    command(lab,name+'-syntax',args+['-fsyntax-only']);command(lab,name+'-build',args+['-o',lab/name])
    builds.append(dict(name=name,source_sha256=sha(src/(name+'.c')),binary_sha256=sha(lab/name)))
save(lab,'client-provenance',dict(inputs=inputs,historical_nested_sha256=NESTED_SHA,adapted_nested_sha256=sha(src/'nested-client.c'),patch_sha256=sha(patch),protocol_regeneration='byte-identical',protocols={p.name:sha(p) for p in src.glob('*') if p.suffix in ['.h','.xml'] or p.name.endswith('-protocol.c')},C17='PASS',builds=builds,prior_manifests=receipts))
for p in Path(__file__).parent.iterdir():
    assert p.suffix in ['.py','.md','.patch'],('generated repository file',p)
    shutil.copy2(p,lab/'fixture'/p.name)
    if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
shutil.copy2(REPO/'docs/design/STEP20C_STATIC_NESTED_VALID_GRAB_PROBE.md',lab/'protocol-before-run.md')
protected=[REPO/p for p in ['AGENTS.md','docs/UX.md','docs/PACKAGING.md','PKGBUILD','patches/0001-mosaic-layout-viewport.patch']]
protected+=[Path('/usr/bin/sway'),wl,Path('/usr/lib/libscenefx-0.5.so').resolve(),BINARY]
protected+=list((REPO/'sway').rglob('*.c'))+list((REPO/'include').rglob('*.h'))
save(lab,'protected-before',{str(p):sha(p) for p in protected})
source=Path('/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/mosaic-source')
files=['sway/desktop/transaction.c','sway/desktop/xdg_shell.c','sway/desktop/output.c','sway/tree/view.c','sway/commands/exit.c','sway/ipc-server.c','sway/main.c','sway/commands/layout.c']
save(lab,'candidate-source-audit',{str(source/p):sha(source/p) for p in files})
freeze=[p for root in ['fixture','client-source','historical-source'] for p in (lab/root).rglob('*') if p.is_file()]+[lab/'protocol-before-run.md']
save(lab,'fixture-inventory',inventory(lab/'results/fixture-freeze-sha256.txt',freeze))
print('LAB='+str(lab))
