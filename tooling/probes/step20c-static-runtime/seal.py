#!/usr/bin/env python3
"""Seal this completed LAB once, or verify every immutable manifest entry.

CONTRACT: exclusive creation; source files and raw/generated evidence separate.
INVARIANT: no rewriting/refunds; report/diff stay outside sealed inventories.
"""
import argparse
from pathlib import Path
from support import REPO,sha
p=argparse.ArgumentParser();p.add_argument('lab',type=Path);p.add_argument('--verify',action='store_true');a=p.parse_args();lab=a.lab.resolve()
assert lab.is_relative_to(Path.home()) and not lab.is_relative_to(REPO)
results=lab/'results'
if not a.verify:
    assert not any((results/(n+'-sha256.txt')).exists() for n in ['source','evidence'])
    source=set(x for x in Path(__file__).parent.iterdir() if x.is_file())
    for tree in ['mosaic-source','scene-source','swayfx-source','wlroots-source','client-source','patches']:
        source.update(x for x in (lab/tree).rglob('*') if x.is_file())
    evidence=set(x for tree in ['raw','run','results','stage-static'] for x in (lab/tree).rglob('*') if x.is_file() and x.name not in ['source-sha256.txt','evidence-sha256.txt'])
    for build in ['mosaic-build','scene-build']:
        for name in ['build.ninja','compile_commands.json']:
            evidence.add(lab/build/name)
        evidence.update(x for x in (lab/build/'meson-info').glob('*.json'))
        evidence.update(x for x in (lab/build/'meson-logs').glob('*.txt'))
    evidence.add(lab/'scene-build/libscenefx-0.5.a')
    evidence.add(lab/'mosaic-build/sway/swayfx-mosaic')
    for name,files in [('source',source),('evidence',evidence)]:
        with (results/(name+'-sha256.txt')).open('x') as out:
            for path in sorted(files):out.write(f'{sha(path)}  {path.resolve()}\n')
for name in ['source','evidence']:
    path=results/(name+'-sha256.txt');lines=path.read_text().splitlines()
    for line in lines:
        digest,file=line.split('  ',1);assert sha(file)==digest,file
    print(name,len(lines),sha(path),'PASS')
