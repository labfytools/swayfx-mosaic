#!/usr/bin/env python3
"""Seal completed source/evidence inventories once, or verify existing bytes.

WHY: derived reports cannot silently overwrite the evidence they cite.
CONTRACT: fixtures finalized first; report/diff are captured outside inventory.
INVARIANT: no manifest replacement, no binaries/build trees in source inventory.
"""
import argparse
import hashlib
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__);p.add_argument('lab',type=Path)
p.add_argument('--verify',action='store_true');a=p.parse_args();lab=a.lab.resolve()
fixture=Path(__file__).resolve().parent;repo=fixture.parents[2]
assert lab.is_relative_to(Path.home()) and lab!=Path.home() and not lab.is_relative_to(repo)
r=lab/'results'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
if not a.verify:
    assert not any((r/(name+'-sha256.txt')).exists() for name in ['source','evidence'])
    source=set(p for p in fixture.iterdir() if p.is_file())
    for tree in ['stock','scene-pristine','scene-private','wlroots-source','mosaic-private']:
        source.update(p for p in (lab/tree).rglob('*') if p.is_file() and 'subprojects' not in p.relative_to(lab/tree).parts)
    source.update(p for p in (lab/'patches').iterdir() if p.is_file())
    source.update(p for p in lab.iterdir() if p.is_file() and p.suffix in ['.py','.c','.md'])
    evidence=set(p for p in (lab/'raw').iterdir() if p.is_file())
    evidence.update(p for p in r.iterdir() if p.is_file() and not p.name.endswith('-sha256.txt'))
    for name,files in [('source',source),('evidence',evidence)]:
        manifest=r/(name+'-sha256.txt')
        # Exclusive creation, never truncate a prior result on interrupted runs.
        with manifest.open('x') as out:
            for path in sorted(files):out.write(f'{sha(path)}  {path}\n')
for name in ['source','evidence']:
    path=r/(name+'-sha256.txt');lines=path.read_text().splitlines()
    for line in lines:
        expected,filename=line.split('  ',1);assert sha(Path(filename))==expected,filename
    print(name,len(lines),sha(path),'PASS')
