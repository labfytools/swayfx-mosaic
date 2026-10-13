#!/usr/bin/env python3
"""Bounded non-graphical audit and single Meson DESTDIR stage of trusted artifacts.

WHY: source, ELF visibility and actual binding evidence answer different questions.
CONTRACT: historical LAB is read-only; only new external LAB receives results.
INVARIANT: never run the compositor; never rebuild, install live, or change symbols.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('lab', type=Path)
p.add_argument('--historical', type=Path, required=True)
p.add_argument('--historical-readme', type=Path, required=True)
p.add_argument('--stage', action='store_true')
p.add_argument('--verify', action='store_true')
a = p.parse_args()
lab, old = a.lab.resolve(), a.historical.resolve()
repo = Path(__file__).resolve().parents[3]
assert not old.is_relative_to(lab) and not lab.is_relative_to(old)
assert lab.is_dir() and old.is_dir() and lab != old
assert lab.is_relative_to(Path.home()) and not lab.is_relative_to(repo)
if a.verify:
    assert not a.stage
    for kind in ['source', 'evidence']:
        manifest = lab/'results'/(kind+'-sha256.txt')
        lines = manifest.read_text().splitlines()
        for line in lines:
            digest, filename = line.split('  ', 1)
            assert hashlib.sha256(Path(filename).read_bytes()).hexdigest() == digest, filename
        print(kind, len(lines), hashlib.sha256(manifest.read_bytes()).hexdigest(), 'PASS')
    raise SystemExit(0)
assert not (lab/'results/evidence-sha256.txt').exists(), 'sealed: verify only'
raw, results = lab/'raw', lab/'results'
raw.mkdir(exist_ok=True); results.mkdir(exist_ok=True)
env = {k: v for k, v in os.environ.items() if k not in (
    'SWAYSOCK', 'I3SOCK', 'WAYLAND_DISPLAY', 'DISPLAY', 'XDG_RUNTIME_DIR',
    'LD_LIBRARY_PATH', 'LD_PRELOAD', 'PKG_CONFIG_PATH')}
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
env.update(LC_ALL='C', PYTHONDONTWRITEBYTECODE='1', MESON_ROOT_CMD='/bin/false')
commands = json.loads((results/'commands.json').read_text()) if (results/'commands.json').exists() else []

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    (results/(name+'.json')).write_text(json.dumps(value, indent=2)+'\n')

def read(name):
    return json.loads((old/'results'/(name+'.json')).read_text())

def run(label, args, extra=None):
    # Only explicitly requested diagnostics, Meson setup/install and objcopy.
    # Command output is file-backed, with bounded execution and owned group.
    label = f'{len(commands):03}-'+label
    entry = {'args': list(map(str, args)), 'env_override': extra or {}, 'label': label}
    with (raw/(label+'.out')).open('wb') as out, (raw/(label+'.err')).open('wb') as err:
        proc = subprocess.Popen(entry['args'], env={**env, **(extra or {})},
                                stdout=out, stderr=err, start_new_session=True)
        try:
            proc.wait(timeout=120)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL); proc.wait()
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            entry['timed_out'] = True
    entry['returncode'] = proc.returncode
    commands.append(entry); save('commands', commands)
    assert proc.returncode == 0, (label, entry)
    assert (raw/(label+'.out')).stat().st_size < 32*1024*1024
    output = (raw/(label+'.out')).read_text()
    (raw/(label.split('-', 1)[1]+'.out')).write_text(output)
    return output

integrity = {}
for kind, count, digest in [
    ('source', 1463, 'a27fa33d57d3423e09f02430f04cfed643762d876099b7f88489229115c4a1e5'),
    ('evidence', 204, '86f7654c8ad962053644ce2c4c13eb9f026d6618b171e0cc3a8fc3034eb380d5')]:
    manifest = old/'results'/(kind+'-sha256.txt')
    assert sha(manifest) == digest
    lines = manifest.read_text().splitlines(); assert len(lines) == count
    for line in lines:
        expected, filename = line.split('  ', 1)
        path = Path(filename)
        if path == repo/'tooling/probes/step20c-scenefx-abi-package/README.md':
            path = a.historical_readme
        assert sha(path) == expected, filename
    integrity[kind] = {'count': count, 'sha256': digest, 'verified': True}
save('historical-integrity', integrity)
elf = read('static-binary-elf'); binary = Path(elf['path'])
assert sha(binary) == elf['sha256'] and binary.stat().st_size < 128*1024*1024
for name in ['static-binary-elf', 'experimental-binary-elf', 'system-wlroots-elf',
             'pristine-scenefx-symbols']:
    item = read(name); assert sha(Path(item['path'])) == item['sha256'], name
for tag, args in [('header', ['readelf', '-hW']), ('dynamic', ['readelf', '-dW']),
                  ('symbols', ['readelf', '-Ws']), ('relocations', ['readelf', '-rW']),
                  ('versions', ['readelf', '-VW']), ('nm', ['nm', '--format=posix'])]:
    run('static-'+tag, [*args, binary])
# Copy retained diagnostic records, do not reexecute the historical ABI campaign.
for name in ['static-bindings', 'static-relocations', 'loader-static-default']:
    shutil.copyfile(old/'raw'/(name+'.json'), raw/('historical-'+name+'.json'))
load = read('loader-resolution')
assert load['static-relocations']['returncode'] == 0
assert 'undefined symbol:' not in load['static-relocations']['stdout']
assert 'libscenefx' not in load['static-default']['stdout']
save('static-elf', {**elf, 'relocations': 'PASS historical trusted loader diagnostics',
                   'graphics': 'NOT TESTED', 'loader_records_reused': True})

# Full ELF tables distinguish local/global/default visibility from dynsym membership.
def symbols(path):
    out = {}
    for line in path.read_text().splitlines():
        f = line.split()
        if len(f) >= 8 and f[0].rstrip(':').isdigit():
            name = f[7].split('@')[0]
            rec = dict(type=f[3], bind=f[4], visibility=f[5], index=f[6],
                       version=f[7].split('@', 1)[1] if '@' in f[7] else None)
            out.setdefault(name, []).append(rec)
    return out
sym = symbols(raw/'static-symbols.out')
scene = set(read('pristine-scenefx-symbols')['defined'])
wl = set(read('system-wlroots-elf')['defined'])
shared = read('experimental-binary-elf')
clip = {'wlr_scene_tree_set_clip', 'wlr_scene_tree_get_clip'}
local_names = {n for n, records in sym.items() if any(x['bind']=='LOCAL' and x['index']!='UND' for x in records)}
scan_names = set(sym) | scene | clip
source_refs = {}
for path in sorted((old/'mosaic-private/sway').rglob('*.c')):
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        for name in set(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', line)) & scan_names:
            source_refs.setdefault(name, []).append({'file': str(path.relative_to(old)),
                                                     'line': lineno, 'text': line.strip()})
definition_refs = {}
actual_definitions = {}
for tree in ['scene-private', 'wlroots-source', 'mosaic-private']:
    for path in sorted((old/tree).rglob('*.c')):
        content = path.read_text()
        for match in re.finditer(r'(?m)^[ \t]*(?:[A-Za-z_]\w*[\s*]+)+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{', content):
            name = match[1]
            if name in scan_names:
                actual_definitions.setdefault(name, []).append({'file': str(path.relative_to(old)), 'line': content[:match.start()].count('\n')+1})
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            for name in set(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', line)) & scan_names:
                definition_refs.setdefault(name, []).append({'file': str(path.relative_to(old)),
                                                             'line': lineno, 'text': line.strip()})
bindings = {}
for mode in ['stock-bindings', 'private-bindings', 'static-bindings']:
    data = read('loader-resolution')[mode]
    for line in (data['stdout']+'\n'+data['stderr']).splitlines():
        match = re.search(r"binding file (.*?) \[0\] to (.*?) \[0\].*symbol `([^']+)'", line)
        if not match:
            continue
        rec = {'consumer': match[1], 'provider': match[2]}
        rows = bindings.setdefault(match[3], {}).setdefault(mode, [])
        if rec not in rows:
            rows.append(rec)
public = sorted((set(shared['undefined']) & scene) - clip)
common = sorted(scene & wl)
assert len(common) == 85
ownership = []
local_names = {n for n, records in sym.items() if any(x['bind']=='LOCAL' and x['index']!='UND' for x in records)}
for name in sorted(set(public) | set(common) | clip | set(elf['undefined']) | local_names):
    actual = bindings.get(name, {})
    ownership.append({'name': name, 'groups': [g for g, yes in [
        ('A', name in public), ('B', name in clip), ('C', name in common),
        ('D', name in elf['undefined']), ('E', name in local_names)] if yes],
        'definitions': actual_definitions.get(name, []),
        'definition_reference_source_candidates': definition_refs.get(name, []),
        'compositor_source_references': source_refs.get(name, []),
        'elf': sym.get(name, []), 'dynamic_export': name in elf['defined'],
        'expected_owner': 'SceneFX private clip' if name in clip else 'SceneFX scene/renderer' if name in scene else 'shared provider from retained loader graph' if name in elf['undefined'] else 'executable internal implementation',
        'observed_providers': actual,
        'selection': 'direct executable definition (non-dynsym)' if name in clip else ('MEASURED retained bindings (includes callers other than wlroots; see scene counts)' if actual else 'NOT OBSERVED at runtime; ELF definition/reference only'),
        'abi_convention': 'unversioned WLR_USE_UNSTABLE C ABI and shared scene/renderer types' if name in scene or name in clip or name.startswith('wlr_') else 'ELF table version recorded; no new ABI assertion',
        'classification': 'private prototype only; ABI not maintained' if name in clip else 'provider records retained; scene helper necessity inferred from source, not isolation experiment' if actual and name in common else 'current definition/reference characterized; full semantic ABI NOT ESTABLISHED',
        'upgrade_risk': 'any new wlroots version/build NOT QUALIFIED'})
save('scene-symbol-ownership', {'group_A_scope': 'link-required public SceneFX functions across compiled SwayFX/Mosaic; per-source references distinguish Mosaic-specific paths', 'groups': {'A': public, 'B': sorted(clip), 'C': common,
    'D': elf['undefined'], 'E': sorted(n for n, records in sym.items() if any(x['bind']=='LOCAL' and x['index']!='UND' for x in records))}, 'symbols': ownership})
save('exported-symbols', {'dynamic_definitions': elf['defined'], 'dynamic_undefined': elf['undefined'], 'full_table': sym})
save('interposition-matrix', {'observed': bindings, 'scene_wlroots_counts': read('scene-symbol-bindings'),
    'overlap': common, 'visibility_changes': 'NONE', 'new_version': 'NOT TESTED',
    'warning': 'matching names are not defects; hiding them may break wlroots helper delegation'})
transitive = read('transitive-dependencies')
stock = read('stock-binary-elf')
save('transitive-dependencies', {'static_DT_NEEDED': elf['DT_NEEDED'],
    'stock_DT_NEEDED': stock['DT_NEEDED'], 'new_direct': sorted(set(elf['DT_NEEDED'])-set(stock['DT_NEEDED'])),
    'removed_direct': sorted(set(stock['DT_NEEDED'])-set(elf['DT_NEEDED'])),
    'historical_recursive_package_owners': transitive,
    'note': 'historical union includes SceneFX for shared cases; static graph comes from historical loader-static-default.json',
    'proposal_only': 'keep existing runtime dependencies except scenefx conditionally; add libglvnd, mesa, lcms2; promote libdrm/pixman to runtime; review glib2, glibc, xcb-util-wm direct owners; no PKGBUILD change'})

# Exact root licenses plus source-level notice candidates remain external.
notices = []
for tree in ['stock', 'scene-private', 'wlroots-source']:
    for path in sorted((old/tree).rglob('*')):
        if not path.is_file() or 'subprojects' in path.relative_to(old/tree).parts:
            continue
        if path.name.upper().startswith(('LICENSE', 'COPYING', 'NOTICE')):
            notices.append({'path': str(path.relative_to(old)), 'sha256': sha(path), 'text': path.read_text(errors='replace'), 'kind': 'license_file'})
        elif path.suffix in ['.c', '.h', '.frag', '.vert', '.xml']:
            text = path.read_text(errors='replace')
            if re.search(r'copyright|SPDX-License|permission is hereby|redistribution and use', text, re.I):
                notices.append({'path': str(path.relative_to(old)), 'sha256': sha(path), 'text': text, 'kind': 'source_notice_candidate; inclusion needs link-object provenance review'})
# Link-input provenance also includes generated protocol code with its own notices.
# Root MIT files alone are insufficient for a complete distribution notice bundle.
incorporated = []
for build_name in ['static-build', 'scene-static-build']:
    build_path = old/build_name
    compile_commands = json.loads((build_path/'compile_commands.json').read_text())
    shutil.copyfile(build_path/'compile_commands.json', raw/(build_name+'-compile-commands.json'))
    shutil.copyfile(build_path/'build.ninja', raw/(build_name+'-build.ninja'))
    for command in compile_commands:
        path = (build_path/command['file']).resolve()
        if not path.is_file():
            continue
        incorporated.append({'path': str(path), 'sha256': sha(path),
                             'object': command.get('output'), 'build': build_name,
                             'note': 'compile input, final archive extraction not proven by this alone'})
        if path.is_relative_to(build_path) and path.suffix == '.c':
            text = path.read_text()
            comments = re.findall(r'/\*.*?\*/', text, re.S)
            payload = '\n'.join(c for c in comments if re.search(r'copyright|permission|redistribution', c, re.I))
            if payload:
                notices.append({'path': str(path.relative_to(old)), 'sha256': sha(path),
                                'text': payload, 'kind': 'generated_protocol_notice'})
save('incorporated-source-inventory', incorporated)
run('archive-symbols', ['nm', '-A', '--defined-only', old/'scene-static-build/libscenefx-0.5.a'])
save('license-notices', {'root_licenses': read('licenses')['source_licenses'],
    'source_notice_candidates': notices, 'system_packages': read('licenses'),
    'incorporation': 'only SceneFX archive embedded; wlroots shared; SwayFX/common/protocol code included; no static system dependency claimed',
    'compliance': 'NOT APPROVED; exact source notices retained, final object/notice closure still required'})
# Probe N1 solely on a disposable executable; never staged or executed.
notice_file = lab/'notice-candidate.txt'
notice_file.write_text('\n\n'.join(x['path']+'\n'+x['text'] for x in notices if x['kind'] in ['license_file', 'generated_protocol_notice']))
notice_bin = lab/'notice-copy'
run('notice-add', ['objcopy', '--add-section', '.mosaic_notices='+str(notice_file),
                  '--set-section-flags', '.mosaic_notices=readonly,contents', binary, notice_bin])
extracted = lab/'notice-extracted.txt'
run('notice-extract', ['objcopy', '--dump-section', '.mosaic_notices='+str(extracted), notice_bin, lab/'notice-extract-copy'])
assert extracted.read_bytes() == notice_file.read_bytes()
save('notice-distribution-options', {'N1': {'mechanics': 'PASS objcopy/extraction roundtrip on disposable copy', 'sha256': sha(extracted), 'staged': False, 'strip_retention': 'NOT TESTED', 'legal': 'NOT APPROVED', 'one_file': True, 'remaining': 'complete notice inventory, accessible extraction without executing compositor, retention through strip/sign/package, legal review'},
    'N2': {'mechanics': 'license metadata identifies license; does not contain complete notices automatically', 'one_file': True, 'risk': 'package/source separation or raw executable transfer loses notices', 'legal': 'NOT APPROVED'},
    'N3': {'mechanics': 'conventional installed notice file', 'one_file': False, 'decision': 'USER packaging contract change required', 'legal': 'complete inventory/review still required'}})

if a.stage:
    # One-shot marker persists even on failure. Historical build remains untouched.
    marker = lab/'stage-started.json'
    assert not (lab/'stage-install-started.json').exists(), 'staging attempt already consumed'
    if not marker.exists():
        with marker.open('x') as out:
            json.dump({'budget': 1, 'binary': str(binary), 'sha256': sha(binary)}, out)
    source, build = lab/'stage-source', lab/'stage-plan'
    if not source.exists():
        shutil.copytree(old/'mosaic-private', source)
    # Git archives need not contain a subprojects directory; never assume one.
    original = old/'mosaic-private'
    for path in original.rglob('*'):
        if path.is_file() and 'subprojects' not in path.relative_to(original).parts:
            assert sha(path) == sha(source/path.relative_to(original))
    flags = ['--prefix=/usr', '--bindir=bin', '-Dwerror=false', '-Dsd-bus-provider=libsystemd',
             '-Dmosaic-package=true', '-Dswaybar=false', '-Dswaynag=false', '-Dman-pages=disabled', '-Ddefault-wallpaper=false']
    run('stage-plan-setup', ['meson', 'setup', build, source, *flags],
        {'PKG_CONFIG_PATH': str(old/'scene-static-build/meson-uninstalled')})
    plan = json.loads((build/'meson-info/intro-installed.json').read_text())
    assert plan == {str(build/'sway/swayfx-mosaic'): '/usr/bin/swayfx-mosaic'}, plan
    target = build/'sway/swayfx-mosaic'; shutil.copy2(binary, target)
    assert sha(target) == elf['sha256']
    with (lab/'stage-install-started.json').open('x') as out:
        json.dump({'budget': 1}, out)
    run('stage-static', ['meson', 'install', '-C', build, '--destdir', lab/'stage-static', '--no-rebuild'])
    entries = []
    for path in sorted((lab/'stage-static').rglob('*')):
        s = path.lstat(); kind = 'symlink' if stat.S_ISLNK(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode) else 'regular' if stat.S_ISREG(s.st_mode) else 'other'
        entries.append({'path': '/'+str(path.relative_to(lab/'stage-static')), 'kind': kind,
                        'mode': oct(stat.S_IMODE(s.st_mode)), 'uid': s.st_uid, 'gid': s.st_gid,
                        'bytes': s.st_size, 'sha256': sha(path) if kind=='regular' else None,
                        'target': os.readlink(path) if kind=='symlink' else None})
    files = [x for x in entries if x['kind']!='directory']
    passed = len(files)==1 and files[0]['path']=='/usr/bin/swayfx-mosaic' and files[0]['kind']=='regular' and files[0]['sha256']==elf['sha256']
    save('static-stage-manifest', {'status': 'STATIC_STAGE_FILE_SHAPE_PASS' if passed else 'STATIC_STAGE_FILE_SHAPE_FAIL',
        'entries': entries, 'complete_non_directory_manifest': files, 'plan': plan,
        'build_options': json.loads((build/'meson-info/intro-buildoptions.json').read_text()),
        'metadata_adaptation_only': True, 'compositor_compiles': 0, 'intended_package_owner': 'swayfx-mosaic',
        'intended_install_uid_gid': 'root:root under future packaging; actual staging remains user-owned',
        'notices_present': False, 'libraries_installed': False})
    assert passed
print('PASS static analysis, retained binding verification and notice mechanics; stage executed' if a.stage else 'PASS static analysis only; no new staging')
