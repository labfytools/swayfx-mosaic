#!/usr/bin/env python3
"""Read-only preparation; never start a compositor, IPC client or session unit."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True


def load_guard(path):
    """Import the audited installed guard without dispatching its CLI."""
    spec = importlib.util.spec_from_file_location('installed_mosaic_guard', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require_uwsm(guard, path):
    """Check a trusted executable as data; do not execute it, even for version."""
    path = Path(path).resolve(strict=True)
    guard.read_regular(path, 1024 * 1024, owner=0)
    if not path.stat().st_mode & 0o111:
        raise RuntimeError('UWSM is not executable')
    return path


def inventory(guard, paths):
    """Validate canonical regular files and retain link identity separately."""
    records = {}
    for path in sorted(set(map(Path, paths))):
        info = path.lstat()
        resolved = path.resolve(strict=True)
        if path.is_symlink() and info.st_uid not in (0, os.getuid()):
            raise RuntimeError('Untrusted symlink owner')
        fd = guard.secure_directory(path.parent)
        os.close(fd)
        data = guard.read_regular(resolved, 64 * 1024 * 1024,
                                  owner=resolved.stat().st_uid)
        target = resolved.stat()
        if target.st_uid not in (0, os.getuid()):
            raise RuntimeError('Untrusted file owner')
        records[str(path)] = {
            'canonical': str(resolved), 'sha256': digest(data),
            'size': len(data), 'uid': target.st_uid,
            'mode': stat.S_IMODE(target.st_mode),
            'link': os.readlink(path) if path.is_symlink() else None,
            'link_uid': info.st_uid if path.is_symlink() else None,
        }
    return records


def write_private(path, data):
    """Create a fresh, non-executable receipt or snapshot without replacement."""
    with path.open('xb') as stream:
        stream.write(data)
    path.chmod(0o400)


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def git_read(repo, *arguments):
    """Only fixed read-only Git operations are used by preparation."""
    return subprocess.run(['git', '-C', str(repo), *arguments], check=True,
                          capture_output=True).stdout


def instructions(guard):
    """Return text only: no launch or recovery execution entry point exists."""
    return f'''EXPERIMENTAL / PHYSICAL_NOT_RUN
Binary snapshot is archival, not deployed. Existing entry uses original binary.
No preference changes. Do not run arm/stable helpers.

First require one explicit conversational approval covering the reviewed
session.py and manifest.json repair and the subsequent bounded physical trial.
Install the repair only after that approval; verify its approved hashes and
loaded isolation again before the approved trial.
The original installed guard has a confirmed quoted-Conflicts refusal.
Only after that approved repair, verification and voluntary Stable logout:
Use authenticated local seat0 TTY; cancel the login menu to reach a shell.
Before launch, open and verify a second independent authenticated TTY recovery
shell; cancel if unavailable. Use TTY2 for launch and TTY3 for recovery.
After any menu cancellation, `exec /usr/bin/zsh -f` provides a clean shell.
Keep both logins alive. Inspect units (activating/deactivating must be absent):
  /usr/bin/systemctl --user list-units 'wayland-wm@*.service' --all --plain --no-pager
When all compositor WM units are inactive and inherited graphical variables
are absent, launch explicitly, leaving default-id unchanged:
  /usr/bin/uwsm start -- swayfx-mosaic-test.desktop

Normal exit or recovery without Kitty, image or IPC:
Use another authenticated TTY; cancel its login menu. Inspect the list above.
If Stable or any other WM is active/activating/deactivating, cancel recovery.
If only Mosaic remains, stop precisely this one WM instance:
  /usr/bin/systemctl --user stop '{guard.WM_UNIT}'
Inspect again and wait until ALL compositor WM units are inactive, including
Mosaic. A failed stop or lingering unit means cancel; do not force anything.
Then explicitly start Stable:
  /usr/bin/uwsm start -- sway.desktop
Read canonical default-id from manifest; it must remain sway.desktop.
No global kill, wildcard stop, uwsm stop, selection or default helper.
Actual VT/PAM/DRM/eDP-1/recovery: NOT TESTED.
'''.encode()


def prepare(guard_path, source_kit, repo, uwsm, extra):
    """Snapshot audited inputs into a fresh private LAB; source files stay intact."""
    guard_path = Path(guard_path).absolute()
    guard = load_guard(guard_path)
    guard.verify_files()
    require_uwsm(guard, uwsm)
    default = guard.Selection().validate()
    if default.strip() != b'sway.desktop':
        raise RuntimeError('Stable default must remain sway.desktop')
    installed = json.loads(guard.read_regular(guard.CONFIG / 'manifest.json'))
    fixtures = list(Path(source_kit).iterdir())
    if any(not p.is_file() or p.is_symlink() for p in fixtures):
        raise RuntimeError('Source-kit must contain only regular source fixtures')
    paths = [Path(p) for p in installed['files']]
    paths += [guard.CONFIG / 'manifest.json', guard.BINARY, guard.WLROOTS,
              guard.SELECTION_DIR / 'default-id', Path(uwsm), *fixtures,
              *map(Path, extra)]
    before = inventory(guard, paths)
    # Validate the selection alias itself using the guard's exact Stow contract.
    alias = {'path': str(guard.SELECTION_ALIAS),
             'target': os.readlink(guard.SELECTION_ALIAS),
             'uid': guard.SELECTION_ALIAS.lstat().st_uid}
    lab = Path(tempfile.mkdtemp(prefix='mosaic-first-session-', dir='/var/tmp'))
    lab.chmod(0o700)
    write_private(lab / 'before.json', json_bytes({'files': before, 'alias': alias}))
    snapshots = lab / 'snapshots'
    snapshots.mkdir(mode=0o700)
    for number, (name, record) in enumerate(before.items()):
        data = guard.read_regular(Path(record['canonical']), 64 * 1024 * 1024,
                                  owner=record['uid'])
        if digest(data) != record['sha256']:
            raise RuntimeError('Input changed during snapshot')
        destination = f'{number:03d}-{Path(name).name}'
        write_private(snapshots / destination, data)
        record['snapshot'] = destination
    write_private(lab / 'manifest.json', json_bytes({
        'status': 'EXPERIMENTAL / PHYSICAL_NOT_RUN', 'files': before,
        'default': default.decode(), 'original_binary': str(guard.BINARY),
        'snapshot_deployed': False, 'guard': str(guard_path)}))
    write_private(lab / 'MANUAL.txt', instructions(guard))
    provenance = {key: git_read(repo, *args).decode() for key, args in {
        'head': ('rev-parse', 'HEAD'),
        'origin_main': ('rev-parse', 'origin/main'),
        'status': ('status', '--short', '--branch'),
    }.items()}
    write_private(lab / 'provenance.json', json_bytes(provenance))
    write_private(lab / 'diff-to-origin.patch',
                  git_read(repo, 'diff', 'origin/main', '--'))
    guard.verify_files()
    after = inventory(guard, paths)
    comparable = {key: {k: v for k, v in value.items() if k != 'snapshot'}
                  for key, value in before.items()}
    alias_after = {'path': str(guard.SELECTION_ALIAS),
                   'target': os.readlink(guard.SELECTION_ALIAS),
                   'uid': guard.SELECTION_ALIAS.lstat().st_uid}
    unchanged = (comparable == after and alias == alias_after
                 and guard.Selection().validate() == default)
    write_private(lab / 'after.json', json_bytes({
        'files': after, 'alias': alias_after, 'unchanged': unchanged}))
    if not unchanged:
        raise RuntimeError(f'Inputs changed; inspect private receipts: {lab}')
    return lab, len(after)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guard', required=True, type=Path)
    parser.add_argument('--source-kit', required=True, type=Path)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--uwsm', type=Path, default=Path('/usr/bin/uwsm'))
    parser.add_argument('--protect', action='append', default=[], type=Path)
    args = parser.parse_args()
    lab, count = prepare(args.guard, args.source_kit, args.repo,
                         args.uwsm, args.protect)
    print(json.dumps({'lab': str(lab), 'files_unchanged': count,
                      'status': 'PHYSICAL_NOT_RUN'}))


if __name__ == '__main__':
    main()
