#!/usr/bin/env python3
"""Reconstruct only the approved static chain in the one external LAB.

CONTRACT: unchanged historical patches, real /usr prefix, no live install.
INVARIANT: reserve before each build/stage; failures are never retried.
WHY: a staged historical /usr/local binary cannot qualify compiled /usr paths.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
from support import REPO,command,environment,reserve,save,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('lab',type=Path);p.add_argument('--scenefx-git',type=Path,required=True)
p.add_argument('--historical',type=Path,required=True)
a=p.parse_args();lab=a.lab.resolve();old=a.historical.resolve()
assert lab.is_relative_to(Path.home()) and not lab.is_relative_to(REPO)
assert not (lab/'prepare-started.json').exists()
(lab/'prepare-started.json').write_text(json.dumps({'historical':str(old),'scene_store':str(a.scenefx_git)})+'\n')
pins={'SwayFX':'fd71a6bdc061bd633b488ae7b83e8a6981d22f86',
      'Mosaic':'cd550382b311efdbfe3ed892f4e1d281d852e754',
      'SceneFX':'37ccd723bef49e6891156ffafce8f549f01446cc',
      'wlroots':'d783533489e1f75d6886c2ab5c5960090ef268f8'}
for name,store,rev in [('mosaic-source',REPO,pins['Mosaic']),('scene-source',a.scenefx_git,pins['SceneFX']),('swayfx-source',REPO,pins['SwayFX'])]:
    arc=lab/(name+'.tar')
    with arc.open('wb') as out:subprocess.run(['git','-C',str(store),'archive',rev],stdout=out,check=True,env=environment())
    (lab/name).mkdir()
    with tarfile.open(arc) as tf:tf.extractall(lab/name,filter='data')
# The sealed wlroots archive was hash-verified at A; copying never changes it.
shutil.copy2(old/'wlroots-source.tar',lab/'wlroots-source.tar')
(lab/'wlroots-source').mkdir()
with tarfile.open(lab/'wlroots-source.tar') as tf:tf.extractall(lab/'wlroots-source',filter='data')
chains={'scene-source':['step20c-valid-grab/scenefx-popup-plus-base.patch','step20c-temporal-damage/scenefx-timing.patch','step20c-optimized-blur-cache/scenefx-cache-trace.patch'],
        'mosaic-source':['step20c-valid-grab/mosaic-popup-plus-base.patch','step20c-valid-grab/hidden-guard.patch','step20c-temporal-damage/mosaic-output-timing.patch','step20c-presentation-identity/presentation-events.patch','step20c-optimized-blur-cache/sway-source-trace.patch']}
(lab/'patches').mkdir();inventory=[]
for tree,chain in chains.items():
    for i,rel in enumerate(chain):
        src=REPO/'tooling/probes'/rel;dst=lab/'patches'/src.name
        assert sha(src)==sha(old/'patches'/src.name)
        shutil.copy2(src,dst);inventory.append({'source':str(src),'sha256':sha(src),'tree':tree,'order':i})
        command(lab,f'{tree}-patch-{i}-check',['git','apply','--check',dst],lab/tree)
        command(lab,f'{tree}-patch-{i}-apply',['git','apply',dst],lab/tree)
    historical=old/('scene-private' if tree=='scene-source' else 'mosaic-private')
    files={str(x.relative_to(historical)):sha(x) for x in historical.rglob('*') if x.is_file()}
    reconstructed={str(x.relative_to(lab/tree)):sha(x) for x in (lab/tree).rglob('*') if x.is_file()}
    assert files==reconstructed, 'historical source equivalence'
save(lab,'source-versions',{'pins':pins,'patches':inventory,'source_equivalence':'PASS','archives':{x.name:sha(x) for x in lab.glob('*.tar')}})
command(lab,'compiler',['cc','--version']);command(lab,'meson-version',['meson','--version'])
command(lab,'dependencies',['pkg-config','--modversion','wlroots-0.20','scenefx-0.5','wayland-server','wayland-client','wayland-protocols','libdrm','xkbcommon','pixman-1'])
reserve(lab,'scene_build')
command(lab,'scene-setup',['meson','setup',lab/'scene-build',lab/'scene-source','-Ddefault_library=static','-Dexamples=false','-Dwerror=false'])
command(lab,'scene-build',['meson','compile','-C',lab/'scene-build','-j','8'])
reserve(lab,'mosaic_build')
extra={'PKG_CONFIG_PATH':str(lab/'scene-build/meson-uninstalled')}
flags=['--prefix=/usr','--bindir=bin','-Dwerror=false','-Dsd-bus-provider=libsystemd','-Dmosaic-package=true','-Dswaybar=false','-Dswaynag=false','-Dman-pages=disabled','-Ddefault-wallpaper=false']
command(lab,'mosaic-setup',['meson','setup',lab/'mosaic-build',lab/'mosaic-source',*flags],extra=extra)
command(lab,'mosaic-build',['meson','compile','-C',lab/'mosaic-build','-j','8'],extra=extra)
command(lab,'mosaic-model',['meson','test','-C',lab/'mosaic-build','mosaic-model','--print-errorlogs'])
options=json.loads((lab/'mosaic-build/meson-info/intro-buildoptions.json').read_text())
values={x['name']:x['value'] for x in options};assert values['prefix']=='/usr' and values['bindir']=='bin'
save(lab,'static-build',{'status':'PASS','flags':flags,'options':options,'archive_sha256':sha(lab/'scene-build/libscenefx-0.5.a'),'binary_sha256':sha(lab/'mosaic-build/sway/swayfx-mosaic'),'bit_reproducibility':'NOT TESTED; one build per contract'})
reserve(lab,'stage')
command(lab,'meson-stage',['meson','install','-C',lab/'mosaic-build','--no-rebuild','--destdir',lab/'stage-static'])
assert sha(lab/'stage-static/usr/bin/swayfx-mosaic')==sha(lab/'mosaic-build/sway/swayfx-mosaic')
save(lab,'meson-stage',{'files':[str(x.relative_to(lab/'stage-static')) for x in (lab/'stage-static').rglob('*') if not x.is_dir()]})
print('PASS static builds, exact source equivalence, /usr prefix, model and single stage')
