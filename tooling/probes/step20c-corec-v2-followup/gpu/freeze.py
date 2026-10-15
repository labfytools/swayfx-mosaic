"""Write a relative G3 source manifest outside Git; grants no review."""
import argparse
import os
import json
from pathlib import Path
from reproduce import KIT, sha, tree

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lab', type=Path, required=True)
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    lab = a.lab.resolve(strict=True)
    assert str(lab).startswith('/var/tmp/swayfx-mosaic-step20c-native-closure-')
    files = tree(KIT)
    result = {'schema': 'G3-relative-source-freeze-v1', 'status': 'EXPERIMENTAL_SOURCE_ONLY',
              'review': 'PENDING_INDEPENDENT', 'build': 'NOT_RUN', 'runtime': 'NOT_RUN',
              'no_inherited_G2_qualification': True, 'files': files}
    out = a.output if a.output is not None else Path('g3-source-freeze.json')
    if not out.is_absolute():
        out = lab / out
    if out.parent.resolve(strict=True) != lab or out.name in ('', '.', '..'):
        p.error('--output must name a direct file below --lab')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(out, flags, 0o600)
    try:
        payload = (json.dumps(result, indent=2) + '\n').encode()
        with os.fdopen(fd, 'wb') as stream:
            fd = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        dirfd = os.open(lab, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        if fd >= 0:
            os.close(fd)
    print(sha(out))
