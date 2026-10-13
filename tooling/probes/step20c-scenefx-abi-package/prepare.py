#!/usr/bin/env python3
"""One-shot private source/build/stage reconstruction; never runs a compositor.

CONTRACT: empty external LAB, explicit local Git object stores at fixed commits.
INVARIANT: every command is logged; no install except stock DESTDIR staging.
WHY: a successful experimental link must never stand in for stock packaging.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tarfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('lab', type=Path)
p.add_argument('--scenefx-git', type=Path, required=True)
p.add_argument('--wlroots-git', type=Path, required=True)
p.add_argument('--pristine-binary', type=Path)
p.add_argument('--static', action='store_true')
a = p.parse_args()
lab = a.lab.resolve()
repo = Path(__file__).resolve().parents[3]
assert lab.is_dir() and lab.is_relative_to(Path.home()) and lab != Path.home()
assert not lab.is_relative_to(repo) and not (lab/'stock').exists()
assert not (lab/'prepare-started.json').exists(), 'budget consumed; inspect logs, never restart'
(lab/'prepare-started.json').write_text(json.dumps(vars(a), default=str, indent=2)+'\n')
raw = lab/'raw'; raw.mkdir(exist_ok=True)
results = lab/'results'; results.mkdir(exist_ok=True)
env = {k: v for k, v in os.environ.items() if k not in (
    'SWAYSOCK', 'I3SOCK', 'WAYLAND_DISPLAY', 'DISPLAY', 'XDG_RUNTIME_DIR',
    'LD_LIBRARY_PATH', 'LD_PRELOAD', 'PKG_CONFIG_PATH', 'OPT_TRACE')}
env['PYTHONDONTWRITEBYTECODE'] = '1'
commands = []

def run(args, cwd=None, extra=None):
    i = len(commands)
    entry = {'args': list(map(str, args)), 'cwd': str(cwd or repo), 'env_override': extra or {}}
    commands.append(entry)
    with (raw/f'build-{i:03}.log').open('wb') as out:
        proc = subprocess.Popen(entry['args'], cwd=cwd or repo, env={**env, **(extra or {})},
                                stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            proc.wait(timeout=600)
        except subprocess.TimeoutExpired:
            # Own only this command's group; compiler children must not outlive
            # a failed reproduction. No process-name or desktop-wide cleanup.
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            entry['timed_out'] = True
    entry['returncode'] = proc.returncode
    (results/'build-commands.json').write_text(json.dumps(commands, indent=2)+'\n')
    if proc.returncode:
        raise RuntimeError(f'command {i} failed; inspect {raw}/build-{i:03}.log')

def archive(git, rev, name):
    target = lab/name
    target.mkdir()
    arc = lab/(name+'.tar')
    with arc.open('wb') as out:
        subprocess.run(['git', '-C', str(git), 'archive', rev], stdout=out, check=True, env=env)
    with tarfile.open(arc) as tf:
        tf.extractall(target, filter='data')
    return target

pins = {'SwayFX': 'fd71a6bdc061bd633b488ae7b83e8a6981d22f86',
        'Mosaic': 'cd550382b311efdbfe3ed892f4e1d281d852e754',
        'SceneFX': '37ccd723bef49e6891156ffafce8f549f01446cc',
        'wlroots': 'd783533489e1f75d6886c2ab5c5960090ef268f8'}
stock = archive(repo, pins['SwayFX'], 'stock')
archive(a.scenefx_git, pins['SceneFX'], 'scene-pristine')
archive(a.scenefx_git, pins['SceneFX'], 'scene-private')
archive(a.wlroots_git, pins['wlroots'], 'wlroots-source')
archive(repo, pins['Mosaic'], 'mosaic-private')
patchdir = lab/'patches'; patchdir.mkdir()
patch = patchdir/'production.patch'; shutil.copyfile(repo/'patches/0001-mosaic-layout-viewport.patch', patch)
run(['git', 'apply', '--check', patch], stock); run(['git', 'apply', patch], stock)
for rel in ('include', 'sway', 'meson.build', 'meson_options.txt', 'tests/mosaic-model.c'):
    run(['git', 'diff', '--no-index', '--exit-code', stock/rel, repo/rel])
chains = {'scene-private': ['step20c-valid-grab/scenefx-popup-plus-base.patch',
                           'step20c-temporal-damage/scenefx-timing.patch',
                           'step20c-optimized-blur-cache/scenefx-cache-trace.patch'],
          'mosaic-private': ['step20c-valid-grab/mosaic-popup-plus-base.patch',
                            'step20c-valid-grab/hidden-guard.patch',
                            'step20c-temporal-damage/mosaic-output-timing.patch',
                            'step20c-presentation-identity/presentation-events.patch',
                            'step20c-optimized-blur-cache/sway-source-trace.patch']}
for tree, chain in chains.items():
    for rel in chain:
        dst = patchdir/Path(rel).name; shutil.copyfile(repo/'tooling/probes'/rel, dst)
        run(['git', 'apply', '--check', dst], lab/tree); run(['git', 'apply', dst], lab/tree)
flags = ['-Dwerror=false', '-Dsd-bus-provider=libsystemd', '-Dmosaic-package=true',
         '-Dswaybar=false', '-Dswaynag=false', '-Dman-pages=disabled', '-Ddefault-wallpaper=false']
run(['meson', 'setup', lab/'stock-build', stock, '--prefix=/usr', '--bindir=bin', *flags])
run(['meson', 'compile', '-C', lab/'stock-build', '-j', '8'])
run(['meson', 'test', '-C', lab/'stock-build', 'mosaic-model', '--print-errorlogs'])
run(['meson', 'install', '-C', lab/'stock-build', '--destdir', lab/'stage-current', '--no-rebuild'])
for name in ('pristine', 'private'):
    run(['meson', 'setup', lab/('scene-'+name+'-build'), lab/('scene-'+name), '-Dexamples=false', '-Dwerror=false'])
    run(['meson', 'compile', '-C', lab/('scene-'+name+'-build'), '-j', '8'])
private_env = {'PKG_CONFIG_PATH': str(lab/'scene-private-build/meson-uninstalled')}
run(['meson', 'setup', lab/'private-build', lab/'mosaic-private', *flags], extra=private_env)
run(['meson', 'compile', '-C', lab/'private-build', '-j', '8'], extra=private_env)
run(['meson', 'test', '-C', lab/'private-build', 'mosaic-model', '--print-errorlogs'])
if a.static:
    # Source inspection establishes a native Meson library() target honoring this
    # option. Only SceneFX is embedded; wlroots and other dependencies stay shared.
    run(['meson', 'setup', lab/'scene-static-build', lab/'scene-private',
         '-Ddefault_library=static', '-Dexamples=false', '-Dwerror=false'])
    run(['meson', 'compile', '-C', lab/'scene-static-build', '-j', '8'])
    static_env = {'PKG_CONFIG_PATH': str(lab/'scene-static-build/meson-uninstalled')}
    run(['meson', 'setup', lab/'static-build', lab/'mosaic-private', *flags], extra=static_env)
    run(['meson', 'compile', '-C', lab/'static-build', '-j', '8'], extra=static_env)
    run(['meson', 'test', '-C', lab/'static-build', 'mosaic-model', '--print-errorlogs'])
if a.pristine_binary:
    # Retained pristine binary is tied to the sealed A campaign identity.
    assert hashlib.sha256(a.pristine_binary.read_bytes()).hexdigest() == '8ac865481bc0487344210cd0e16d8e6c7655b29db887cd58ddc11b0ca22fe494'
    # Copy/hash only, never launch it.
    shutil.copyfile(a.pristine_binary, lab/'retained-pristine-sway')
    pins['pristine_binary_origin'] = str(a.pristine_binary.resolve())
    pins['pristine_binary_sha256'] = hashlib.sha256(a.pristine_binary.read_bytes()).hexdigest()
(results/'source-pins.json').write_text(json.dumps(pins, indent=2)+'\n')
print('PASS private builds/model tests and single stock staging; zero compositor launches')
