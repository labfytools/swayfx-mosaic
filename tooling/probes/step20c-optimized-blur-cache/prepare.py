#!/usr/bin/env python3
"""Build pinned private sources only; never launch a compositor or install."""
import hashlib,json,os,subprocess,tempfile,urllib.request,sys
from pathlib import Path
from instrument import instrument

repo=Path(__file__).resolve().parents[3]; fixture=Path(__file__).resolve().parent
lab=Path(sys.argv[1]).resolve() if len(sys.argv)==2 else Path(tempfile.mkdtemp(prefix='swayfx-mosaic-optimized-blur-',dir=Path.home()))
if (lab/'runs').exists() and any((lab/'runs').iterdir()):raise RuntimeError('never rebuild a consumed campaign')
print('LAB='+str(lab),flush=True)
(lab/'results').mkdir(exist_ok=True); (lab/'runs').mkdir(exist_ok=True)
(lab/'build.log').touch()
def run(argv,env=None,cwd=None):
 with (lab/'build.log').open('ab') as f:
  subprocess.run(argv,check=True,env=env,cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
def archive(git,rev,dst):
 if dst.exists():
  if dst.name in ('scene0','pristine'):return
  suffix=1
  while dst.with_name(dst.name+f'-preflight-failed-{suffix}').exists():suffix+=1
  dst.rename(dst.with_name(dst.name+f'-preflight-failed-{suffix}'))
 dst.mkdir()
 data=subprocess.check_output(['git','-C',str(git),'archive',rev])
 subprocess.run(['tar','-xf','-','-C',str(dst)],input=data,check=True)
def patch(dst,path):
 run(['git','apply','--check',str(path)],cwd=dst);run(['git','apply',str(path)],cwd=dst)
scene_rev='37ccd723bef49e6891156ffafce8f549f01446cc'
if not (lab/'scenefx-git').exists():run(['git','clone','--quiet','https://github.com/wlrfx/scenefx.git',str(lab/'scenefx-git')])
archive(lab/'scenefx-git',scene_rev,lab/'scene0')
archive(lab/'scenefx-git',scene_rev,lab/'scenefx')
archive(repo,'fd71a6bdc061bd633b488ae7b83e8a6981d22f86',lab/'pristine')
archive(repo,'cd550382b311efdbfe3ed892f4e1d281d852e754',lab/'mosaic')
for p in ['step20c-valid-grab/scenefx-popup-plus-base.patch','step20c-temporal-damage/scenefx-timing.patch']:
 patch(lab/'scenefx',repo/'tooling/probes'/p)
for p in ['step20c-valid-grab/mosaic-popup-plus-base.patch','step20c-valid-grab/hidden-guard.patch','step20c-temporal-damage/mosaic-output-timing.patch','step20c-presentation-identity/presentation-events.patch']:
 patch(lab/'mosaic',repo/'tooling/probes'/p)
# WHY: new passive deltas are separate from immutable historical patches.
instrument(lab/'scenefx',lab/'mosaic',fixture)
for src,build in [('scene0','scene0-build'),('scenefx','scenefx-build')]:
 run(['meson','setup',str(lab/build),str(lab/src),'-Dexamples=false','-Dwerror=false'])
 run(['meson','compile','-C',str(lab/build),'-j','8'])
for src,build,scene in [('pristine','pristine-build','scene0-build'),('mosaic','mosaic-build','scenefx-build')]:
 env={**os.environ,'PKG_CONFIG_PATH':str(lab/scene/'meson-uninstalled')}
 args=['meson','setup',str(lab/build),str(lab/src),'-Ddefault-wallpaper=false','-Dswaybar=false','-Dswaynag=false','-Dman-pages=disabled','-Dsd-bus-provider=libsystemd','-Dwerror=false']
 if src=='mosaic':args.append('-Dmosaic-package=true')
 run(args,env=env);run(['meson','compile','-C',str(lab/build),'-j','8'],env=env)
# XML is fetched at a fixed revision. Generated protocol code stays outside Git.
url='https://raw.githubusercontent.com/swaywm/wlr-protocols/b010a03648b88d143236de193bddbfea0c08bc84/unstable/wlr-layer-shell-unstable-v1.xml'
xml=urllib.request.urlopen(url,timeout=30).read();(fixture/'wlr-layer-shell-unstable-v1.xml').write_bytes(xml)
xdg=fixture/'xdg-shell.xml'
assert hashlib.sha256(xdg.read_bytes()).hexdigest()=='7ba7f9c8473deee674cb1f154a18abd0bb0cc072604fc055b0c15e459fc4c7df'
assert hashlib.sha256(xml).hexdigest()=='996b8c66e1c2276c443336d4cb174634e8e5948823779042f244930525b79cc2'
(lab/'xdg-shell.xml').write_bytes(xdg.read_bytes())
provenance={'layer':{'url':url,'commit':'b010a03648b88d143236de193bddbfea0c08bc84','sha256':hashlib.sha256(xml).hexdigest()},'xdg':{'path':str(xdg),'sha256':hashlib.sha256(xdg.read_bytes()).hexdigest(),'wayland_protocols':subprocess.check_output(['pkg-config','--modversion','wayland-protocols'],text=True).strip()}}
(fixture/'protocol-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
for name,p in [('layer-shell',fixture/'wlr-layer-shell-unstable-v1.xml'),('xdg-shell',lab/'xdg-shell.xml')]:
 run(['wayland-scanner','client-header',str(p),str(lab/(name+'-client.h'))])
 run(['wayland-scanner','private-code',str(p),str(lab/(name+'-protocol.c'))])
flags=subprocess.check_output(['pkg-config','--cflags','--libs','wayland-client'],text=True).split()
run(['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-I'+str(lab),str(fixture/'clients.c'),str(lab/'xdg-shell-protocol.c'),str(lab/'layer-shell-protocol.c'),'-o',str(lab/'clients'),*flags])
run(['meson','test','-C',str(lab/'mosaic-build'),'mosaic-model','--print-errorlogs'])
(lab/'results/versions.json').write_text(json.dumps({'SceneFX':scene_rev,'Mosaic':'cd550382b311efdbfe3ed892f4e1d281d852e754','pristine':'fd71a6bdc061bd633b488ae7b83e8a6981d22f86','wlroots':subprocess.check_output(['pkg-config','--modversion','wlroots-0.20'],text=True).strip(),'protocols':provenance},indent=2)+'\n')
print('BUILD_PASS LAB='+str(lab),flush=True)
