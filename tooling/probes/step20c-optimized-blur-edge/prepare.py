#!/usr/bin/env python3
"""Build-only reconstruction from fixed archives and immutable source patches.

CONTRACT: no compositor launch, system install or write to older fixtures.
INVARIANT: consumed LABs cannot be rebuilt, and prepared identities are hashed.
"""
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

fixture = Path(__file__).resolve().parent
repo = fixture.parents[2]
lab = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else Path(
    tempfile.mkdtemp(prefix='swayfx-mosaic-optimized-edge-', dir=Path.home()))
if (lab / 'runs').exists() and any((lab / 'runs').iterdir()):
    raise RuntimeError('never rebuild a consumed LAB')
(lab / 'results').mkdir(parents=True, exist_ok=True)
(lab / 'runs').mkdir(exist_ok=True)
print('LAB=' + str(lab), flush=True)

def run(args, **kwargs):
    with (lab / 'build.log').open('ab') as out:
        subprocess.run(args, check=True, stdout=out, stderr=subprocess.STDOUT, **kwargs)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def archive(git, revision, name):
    target = lab / name
    if target.exists():
        raise RuntimeError('existing source tree; continue Meson explicitly, never overwrite')
    target.mkdir()
    data = subprocess.check_output(['git', '-C', str(git), 'archive', revision])
    tarfile.open(fileobj=io.BytesIO(data)).extractall(target, filter='data')

scene_revision = '37ccd723bef49e6891156ffafce8f549f01446cc'
mosaic_revision = 'cd550382b311efdbfe3ed892f4e1d281d852e754'
pristine_revision = 'fd71a6bdc061bd633b488ae7b83e8a6981d22f86'
run(['git', 'clone', '--quiet', '--no-checkout', 'https://github.com/wlrfx/scenefx.git', str(lab / 'scenefx-git')])
for name in ('scene0', 'scenefx'):
    archive(lab / 'scenefx-git', scene_revision, name)
archive(repo, pristine_revision, 'pristine')
archive(repo, mosaic_revision, 'mosaic')
chains = {
    'scenefx': ['step20c-valid-grab/scenefx-popup-plus-base.patch',
                'step20c-temporal-damage/scenefx-timing.patch',
                'step20c-optimized-blur-cache/scenefx-cache-trace.patch'],
    'mosaic': ['step20c-valid-grab/mosaic-popup-plus-base.patch',
               'step20c-valid-grab/hidden-guard.patch',
               'step20c-temporal-damage/mosaic-output-timing.patch',
               'step20c-presentation-identity/presentation-events.patch',
               'step20c-optimized-blur-cache/sway-source-trace.patch']}
patches = []
(lab / 'patches').mkdir()
for tree, chain in chains.items():
    for name in chain:
        source = repo / 'tooling/probes' / name
        target = lab / 'patches' / source.name
        target.write_bytes(source.read_bytes())
        patches.append({'path': name, 'sha256': sha(target), 'target': tree})
        run(['git', 'apply', '--check', str(target)], cwd=lab / tree)
        run(['git', 'apply', str(target)], cwd=lab / tree)
for source, build in [('scene0', 'scene0-build'), ('scenefx', 'scenefx-build')]:
    run(['meson', 'setup', str(lab / build), str(lab / source), '-Dexamples=false', '-Dwerror=false'])
    run(['meson', 'compile', '-C', str(lab / build), '-j', '8'])
for source, build, scene in [('pristine', 'pristine-build', 'scene0-build'),
                              ('mosaic', 'mosaic-build', 'scenefx-build')]:
    env = {**os.environ, 'PKG_CONFIG_PATH': str(lab / scene / 'meson-uninstalled')}
    args = ['meson', 'setup', str(lab / build), str(lab / source),
            '-Ddefault-wallpaper=false', '-Dswaybar=false', '-Dswaynag=false',
            '-Dman-pages=disabled', '-Dsd-bus-provider=libsystemd', '-Dwerror=false']
    if source == 'mosaic':
        args.append('-Dmosaic-package=true')
    run(args, env=env)
    run(['meson', 'compile', '-C', str(lab / build), '-j', '8'], env=env)
protocols = repo / 'tooling/probes/step20c-optimized-blur-cache'
for stem, name, digest in [
    ('layer-shell', 'wlr-layer-shell-unstable-v1.xml', '996b8c66e1c2276c443336d4cb174634e8e5948823779042f244930525b79cc2'),
    ('xdg-shell', 'xdg-shell.xml', '7ba7f9c8473deee674cb1f154a18abd0bb0cc072604fc055b0c15e459fc4c7df')]:
    xml = protocols / name
    assert sha(xml) == digest
    target = lab / name
    target.write_bytes(xml.read_bytes())
    run(['wayland-scanner', 'client-header', str(target), str(lab / (stem + '-client.h'))])
    run(['wayland-scanner', 'private-code', str(target), str(lab / (stem + '-protocol.c'))])
(lab / 'client-source.c').write_bytes((fixture / 'clients.c').read_bytes())
flags = subprocess.check_output(['pkg-config', '--cflags', '--libs', 'wayland-client'], text=True).split()
run(['cc', '-std=c17', '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter',
     '-I' + str(lab), str(lab / 'client-source.c'), str(lab / 'xdg-shell-protocol.c'),
     str(lab / 'layer-shell-protocol.c'), '-o', str(lab / 'clients'), *flags])
run(['meson', 'test', '-C', str(lab / 'mosaic-build'), 'mosaic-model', '--print-errorlogs'])
versions = {package: subprocess.check_output(['pkg-config', '--modversion', package], text=True).strip()
            for package in ('wlroots-0.20', 'scenefx-0.5', 'wayland-client', 'wayland-protocols')}
binaries = {str(p.relative_to(lab)): sha(p) for p in [
    lab / 'clients', lab / 'mosaic-build/sway/swayfx-mosaic', lab / 'pristine-build/sway/sway',
    lab / 'scenefx-build/libscenefx-0.5.so', lab / 'scene0-build/libscenefx-0.5.so']}
for rel in ('mosaic-build/sway/swayfx-mosaic', 'pristine-build/sway/sway'):
    run(['ldd', str(lab / rel)])
(lab / 'results/build-identities.json').write_text(json.dumps({
    'revisions': {'SceneFX': scene_revision, 'Mosaic': mosaic_revision, 'pristine': pristine_revision},
    'packages': versions, 'patches': patches, 'binaries': binaries,
    'R2_R3': 'identical binary/library/client/config; only OPT_TRACE presence differs'}, indent=2) + '\n')
print('BUILD_PASS LAB=' + str(lab), flush=True)
