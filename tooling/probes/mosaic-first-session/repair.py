#!/usr/bin/env python3
"""Stage the one audited Conflicts decoding repair; never install or launch."""

import argparse
import difflib
import json
import os
from pathlib import Path
import stat

from prepare import digest, json_bytes, write_private

PREIMAGE_SHA = '556b490587af166730db686d973a63e586824b87b488e7364471228515848522'
OLD = """    conflicts = run(['/usr/bin/systemctl', '--user', 'show', SESSION_UNIT,
                     '-p', 'Conflicts', '--value']).split()
"""
NEW = """    # systemctl quotes unit names containing literal backslashes. Decode its
    # quoted word list without shell execution; preserve the unit's \\x escapes.
    conflicts = shlex.split(run([
        '/usr/bin/systemctl', '--user', 'show', SESSION_UNIT,
        '-p', 'Conflicts', '--value']))
"""


def corrected(data):
    """Refuse every source except the exact audited preimage."""
    if digest(data) != PREIMAGE_SHA:
        raise RuntimeError('Audited guard preimage changed')
    source = data.decode()
    if source.count(OLD) != 1 or source.count('import stat\n') != 1:
        raise RuntimeError('Audited repair anchors changed')
    return source.replace('import stat\n', 'import shlex\nimport stat\n').replace(
        OLD, NEW).encode()


def stage(guard_path, lab):
    """Create an exclusive repair directory in an existing private LAB.

    The installed guard authenticates all original inputs. Only the session.py
    digest changes in the manifest; no installation function is provided.
    """
    guard_path, lab = Path(guard_path).absolute(), Path(lab).absolute()
    # Authenticate bytes before importing trusted Python; do not execute an
    # arbitrary replacement supplied via the CLI.
    source_fd = os.open(guard_path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        source_info = os.fstat(source_fd)
        if (not stat.S_ISREG(source_info.st_mode) or source_info.st_nlink != 1
                or source_info.st_uid != os.getuid()
                or source_info.st_mode & 0o022 or source_info.st_size > 131072):
            raise RuntimeError('Unsafe guard preimage')
        with os.fdopen(source_fd, 'rb', closefd=False) as stream:
            authenticated = stream.read(131073)
    finally:
        os.close(source_fd)
    corrected(authenticated)
    # Compile the authenticated bytes rather than reopening a mutable source.
    import types
    guard = types.ModuleType('authenticated_installed_guard')
    exec(compile(authenticated, str(guard_path), 'exec'), guard.__dict__)
    fd = guard.secure_directory(lab)
    info = os.fstat(fd)
    os.close(fd)
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise RuntimeError('Existing LAB must be owned and mode0700')
    original = guard.read_regular(guard_path, 131072)
    candidate = corrected(original)
    guard.verify_files()
    manifest_path = guard_path.parent / 'manifest.json'
    manifest_data = guard.read_regular(manifest_path)
    manifest = json.loads(manifest_data)
    key = str(guard_path)
    if manifest['files'].get(key) != PREIMAGE_SHA:
        raise RuntimeError('Manifest does not authenticate audited guard')
    manifest['files'][key] = digest(candidate)
    # Preserve the complete manifest formatting and all other bytes.
    if manifest_data.count(PREIMAGE_SHA.encode()) != 1:
        raise RuntimeError('Manifest hash anchor is ambiguous')
    candidate_manifest = manifest_data.replace(PREIMAGE_SHA.encode(),
                                               digest(candidate).encode())
    if json.loads(candidate_manifest) != manifest:
        raise RuntimeError('Unexpected manifest change')
    destination = lab / 'guard-conflicts-repair'
    destination.mkdir(mode=0o700)  # Exclusive; never overwrite an earlier receipt.
    records = {}
    patch = ''
    for path, old, new in ((guard_path, original, candidate),
                           (manifest_path, manifest_data, candidate_manifest)):
        mode = stat.S_IMODE(path.stat().st_mode)
        write_private(destination / (path.name + '.original'), old)
        write_private(destination / path.name, new)
        records[str(path)] = {'old_sha256': digest(old), 'new_sha256': digest(new),
                              'old_mode': mode, 'deployment_mode': mode,
                              'staged_mode': 0o400}
        patch += ''.join(difflib.unified_diff(
            old.decode().splitlines(True), new.decode().splitlines(True),
            fromfile=str(path), tofile=str(path)))
    write_private(destination / 'exact.patch', patch.encode())
    write_private(destination / 'receipt.json', json_bytes({
        'status': 'SOURCE_ONLY / NOT_INSTALLED / PHYSICAL_NOT_RUN',
        'files': records, 'installation_authorized': False}))
    guard.verify_files()
    if (guard.read_regular(guard_path, 131072) != original
            or guard.read_regular(manifest_path) != manifest_data):
        raise RuntimeError('Installed inputs changed during staging')
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guard', type=Path, required=True)
    parser.add_argument('--lab', type=Path, required=True)
    args = parser.parse_args()
    print(stage(args.guard, args.lab))


if __name__ == '__main__':
    main()
