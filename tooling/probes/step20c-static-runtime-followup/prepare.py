#!/usr/bin/env python3
"""Copy exact candidate and compile verified historical C17 clients only.

CONTRACT: exclusive campaign registration prevents another LAB/reset/retry.
WHY: historical client executable hashes were not sealed; source provenance was.
"""
import json, os, shutil, stat, subprocess, tempfile
from pathlib import Path
from support import sha, command, save
OLD=Path('/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt')
OWNER=Path.home()/'swayfx-mosaic-static-followup-v1.owner'
# Reserve campaign ownership before creating the only LAB, even on failure.
fd=os.open(OWNER,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f:
    lab=Path(tempfile.mkdtemp(prefix='swayfx-mosaic-static-followup-',dir=Path.home()))
    f.write(str(lab)+'\n');f.flush();os.fsync(f.fileno())
for name in ['results','raw']:(lab/name).mkdir()
(lab/'campaign-owner').write_text(str(OWNER)+'\n')
for name,digest in [('source','ed55bd418595ca977c022fa98917a899072cf3b6f0fb15457db823081046e797'),('evidence','e260ce5793ffc9a29ee4bfa2189663feeb6dc025bd46d3f5ddebccd225f3eef1')]:
    manifest=OLD/'results'/(name+'-sha256.txt');assert sha(manifest)==digest
    for line in manifest.read_text().splitlines():
        h,p=line.split('  ',1);assert sha(p)==h,p
binary=OLD/'stage-static/usr/bin/swayfx-mosaic'
expected='f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b'
assert sha(binary)==expected and stat.S_IMODE(binary.stat().st_mode)==0o755
shutil.copy2(binary,lab/'swayfx-mosaic');assert sha(lab/'swayfx-mosaic')==expected
elf=command(lab,'binary-elf',['readelf','-hW','-nW','-dW',lab/'swayfx-mosaic'])
assert 'libscenefx' not in elf and '942db64269640778ee433e5970ba1100bc60f94c' in elf
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
shutil.copytree(Path(__file__).parent,lab/'fixture')
print('LAB='+str(lab))
