"""Assemble private G3 sources, never build or launch a compositor."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import stat
import subprocess

KIT = Path(__file__).resolve().parent
PARENT = KIT.parents[1] / 'step20c-corec-v2'
PATCH_SHA = '77d7445ceaf643fd5cc708d31c3f2c77feaeb80f8130c419c55e5514ecc8a75d'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree(p):
    return {str(f.relative_to(p)): {'sha256': sha(f), 'mode': oct(stat.S_IMODE(f.stat().st_mode))}
            for f in sorted(p.rglob('*')) if f.is_file() and '.git' not in f.relative_to(p).parts}


def main():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    assert ctypes.CDLL(None).prctl(4, 0, 0, 0, 0) == 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab', type=Path, required=True)
    parser.add_argument('--core', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    a = parser.parse_args()
    lab, core, dest = a.lab.resolve(strict=True), a.core.resolve(strict=True), a.destination.resolve()
    assert str(lab).startswith('/var/tmp/swayfx-mosaic-step20c-native-closure-')
    assert lab.stat().st_uid == os.geteuid() and stat.S_IMODE(lab.stat().st_mode) == 0o700
    assert dest.is_relative_to(lab) and not dest.exists() and not dest.is_relative_to(core)
    before = tree(core)
    expected = json.loads((PARENT / 'provenance.json').read_text())['components']['scene']['files']
    assert before == expected, 'complete CORE bytes/modes differ from versioned provenance'
    patch = PARENT / 'gpu/g2-native.patch'
    assert sha(patch) == PATCH_SHA
    shutil.copytree(core, dest, ignore=shutil.ignore_patterns('.git'))
    result = subprocess.run(['patch', '--batch', '--forward', '-p1', '-i', str(patch)],
                            cwd=dest, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    # WHY: hook placement is frozen G2 instrumentation; only admission and
    # observability headers differ. CONTRACT: no shader or CORE source mutation.
    native = dest / 'render/fx_renderer'
    delta = KIT / 'g3-admission.patch'
    result = subprocess.run(['patch', '--batch', '--forward', '-p1', '-i', str(delta)],
                            cwd=dest, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    for name in ('g2_gl.h', 'g2_native.h'):
        assert sha(KIT / name) == sha(native / name), 'delta/header mismatch'
    assert sha(native / 'fx_pass.c') == 'c2886ef259fc91431dfe97841387082420ab80a0fe2f07e7dcdb71fc95731181'
    after = tree(dest)
    changed = sorted(n for n in before.keys() | after.keys() if before.get(n) != after.get(n))
    assert changed == ['render/fx_renderer/fx_pass.c', 'render/fx_renderer/g2_gl.h', 'render/fx_renderer/g2_native.h']
    assert tree(core) == before
    receipt = {'schema': 'G3-source-assembly-v1', 'status': 'EXPERIMENTAL_SOURCE_ONLY',
               'review': 'PENDING_INDEPENDENT', 'runtime': 'NOT_RUN', 'build': 'NOT_RUN',
               'core_manifest_sha256': sha(PARENT / 'provenance.json'),
               'g2_patch_sha256': sha(patch), 'g3_delta_sha256': sha(delta), 'changed': {n: after[n] for n in changed},
               'core_unchanged': True, 'acquisition_root': str(lab / 'gpu-work/acquisition'),
               'G3_ROOT_compile_definition_required': True}
    (dest.parent / (dest.name + '-receipt.json')).write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
