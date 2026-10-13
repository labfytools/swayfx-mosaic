#!/usr/bin/env python3
"""Verify immutable historical manifests after publication wording changes.

WHY: documentation snapshots preserve evidence without rewriting sealed hashes.
CONTRACT: explicit mappings replace only files recorded in the source manifest.
INVARIANT: verification is read-only; every original digest must still match.
"""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('lab', type=Path)
p.add_argument('--snapshot-map', type=Path, required=True)
a = p.parse_args()
mapping = json.loads(a.snapshot_map.read_text())
seen = set()
for kind, count, expected in [
    ('source', 1892, '5ad64eaf0aec2290689c46b7754eb4563980396ba2a06e852d1c8e903086f138'),
    ('evidence', 143, '85d034f4075436bbdda302afdfa94955365aa51adcfb7e8b04ed6bb28377f649')]:
    manifest = a.lab/'results'/(kind+'-sha256.txt')
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() == expected
    lines = manifest.read_text().splitlines()
    assert len(lines) == count
    for line in lines:
        digest, name = line.split('  ', 1)
        if kind == 'source' and name in mapping:
            seen.add(name)
            name = mapping[name]
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest, name
    print(kind, count, expected, 'PASS')
assert seen == set(mapping), 'mapping must contain only sealed source entries'
