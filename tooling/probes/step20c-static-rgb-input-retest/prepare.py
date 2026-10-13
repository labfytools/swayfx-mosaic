#!/usr/bin/env python3
"""Copy exact candidate and compile verified historical C17 clients only.

CONTRACT: exclusive campaign registration prevents another LAB/reset/retry.
WHY: historical client executable hashes were not sealed; source provenance was.
"""
import json, os, shutil, stat, subprocess, tempfile, ast, argparse
from pathlib import Path
from support import sha, command, save
OLD=Path('/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt')
OWNER=Path.home()/'swayfx-mosaic-static-rgb-input-retest-v1.owner'
p=argparse.ArgumentParser();p.add_argument('--resume-preparation',action='store_true');a=p.parse_args()
if a.resume_preparation:
    # CONTRACT: only recover pre-run preparation in the same exclusive LAB.
    # No ledger/reset, second LAB, completed preparation or executed run is allowed.
    lab=Path(OWNER.read_text().strip()).resolve()
    assert lab.is_dir() and (lab/'campaign-owner').read_text().strip()==str(OWNER)
    assert not (lab/'run').exists() and not (lab/'results/budget.json').exists()
    assert not (lab/'results/fixture-freeze-sha256.txt').exists()
else:
    fd=os.open(OWNER,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:
        lab=Path(tempfile.mkdtemp(prefix='swayfx-mosaic-static-rgb-input-retest-',dir=Path.home()))
        f.write(str(lab)+'\n');f.flush();os.fsync(f.fileno())
    for name in ['results','raw']:(lab/name).mkdir()
    (lab/'campaign-owner').write_text(str(OWNER)+'\n')
for name,digest in [('source','ed55bd418595ca977c022fa98917a899072cf3b6f0fb15457db823081046e797'),('evidence','e260ce5793ffc9a29ee4bfa2189663feeb6dc025bd46d3f5ddebccd225f3eef1')]:
    manifest=OLD/'results'/(name+'-sha256.txt');assert sha(manifest)==digest
    for line in manifest.read_text().splitlines():
        h,p=line.split('  ',1);assert sha(p)==h,p
binary=OLD/'stage-static/usr/bin/swayfx-mosaic'
expected='f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b'
assert binary.is_file() and not binary.is_symlink() and os.access(binary,os.X_OK)
assert sha(binary)==expected and stat.S_IMODE(binary.stat().st_mode)==0o755
if not (lab/'swayfx-mosaic').exists():shutil.copy2(binary,lab/'swayfx-mosaic')
assert sha(lab/'swayfx-mosaic')==expected
elf=((lab/'raw/binary-elf.log').read_text() if a.resume_preparation else
     command(lab,'binary-elf',['readelf','-hW','-nW','-dW',lab/'swayfx-mosaic']))
assert 'libscenefx' not in elf and '942db64269640778ee433e5970ba1100bc60f94c' in elf
assert 'ELF64' in elf and 'Advanced Micro Devices X86-64' in elf
# WHY: private static clip definitions are ordinary ELF symbols, not exports.
symbols=command(lab,'clip-symbols-static',['nm',lab/'swayfx-mosaic'])
assert all(' T '+s in symbols for s in ['wlr_scene_tree_set_clip','wlr_scene_tree_get_clip'])
assert '(RPATH)' not in elf and '(RUNPATH)' not in elf
loader=command(lab,'dependencies',['ldd','-r',lab/'swayfx-mosaic'])
assert 'not found' not in loader and 'undefined symbol' not in loader and 'libscenefx' not in loader
wl=Path('/usr/lib/libwlroots-0.20.so').resolve()
assert sha(wl)=='7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837'
assert str(wl) in loader
save(lab,'binary-identity',{'status':'PASS','source':str(binary),'copy':str(lab/'swayfx-mosaic'),'sha256':expected,'build_id':'942db64269640778ee433e5970ba1100bc60f94c','mode':'0755','wlroots':str(wl),'wlroots_sha256':sha(wl),'new_compositor_builds':0})
shutil.copytree(OLD/'client-source',lab/'client-source')
flags=subprocess.check_output(['pkg-config','--cflags','--libs','wayland-client'],text=True).split()
clients=[]
for name,proto in [('saved-client','xdg-shell'),('static-reference','xdg-shell'),('pointer-daemon','virtual-pointer')]:
    src=lab/'client-source';argv=['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-I'+str(src),src/(name+'.c'),src/(proto+'-protocol.c'),*flags]
    command(lab,name+'-syntax',[*argv,'-fsyntax-only'])
    command(lab,name+'-compile',[*argv,'-o',lab/name])
    clients.append({'name':name,'source_sha256':sha(src/(name+'.c')),'binary_sha256':sha(lab/name),'historical_binary_sha256_unsealed':sha(OLD/name)})
save(lab,'client-provenance',{'historical':json.loads((OLD/'results/client-provenance.json').read_text()),'source_manifest_verified':True,'clients':clients})
save(lab,'source-provenance',{'clients':clients,'historical_manifests_verified':True,
    'source_manifest_sha256':sha(OLD/'results/source-sha256.txt'),
    'evidence_manifest_sha256':sha(OLD/'results/evidence-sha256.txt'),
    'new_Mosaic_builds':0,'new_SceneFX_builds':0})
repo=Path(__file__).resolve().parents[3]
shutil.copytree(Path(__file__).parent,lab/'fixture')
(lab/'protocol-before-run.md').write_bytes((repo/'docs/design/STEP20C_STATIC_RGB_INPUT_STANDARD_RETEST.md').read_bytes())
for p in (lab/'fixture').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
with (lab/'results/fixture-freeze-sha256.txt').open('x') as f:
    for p in sorted((lab/'fixture').rglob('*')):
        if p.is_file():f.write(f'{sha(p)}  {p}\n')
    f.write(f'{sha(lab/"protocol-before-run.md")}  {lab/"protocol-before-run.md"}\n')
save(lab,'protected-before', {str(p):sha(p) for p in [Path('/usr/bin/sway'),
    Path('/usr/lib/libwlroots-0.20.so').resolve(),Path('/usr/lib/libscenefx-0.5.so').resolve(),
    repo/'PKGBUILD',repo/'patches/0001-mosaic-layout-viewport.patch',repo/'AGENTS.md',repo/'docs/UX.md']})
print('LAB='+str(lab))
