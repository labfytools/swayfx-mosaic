#!/usr/bin/env python3
"""Seal retained source and evidence inventories once, without overwriting.

CONTRACT: raw observations and completed source fixtures precede this seal.
INVARIANT: existing manifests are refused; verification never regenerates them.
"""
import hashlib
import sys
from pathlib import Path

lab=Path(sys.argv[1]).resolve()
fixture=Path(__file__).resolve().parent
out=lab/'results'
if any((out/name).exists() for name in ('source-sha256.txt','evidence-sha256.txt')):
    raise RuntimeError('sealed inventories already exist; verify, never overwrite')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

sources=set(p for p in fixture.iterdir() if p.is_file())
sources.add(fixture.parent/'step20c-optimized-blur-cache/edge-model.py')
for name in ('scene0','scenefx','mosaic','pristine'):
    sources.update(p for p in (lab/name).rglob('*')
                   if p.is_file() and 'subprojects' not in p.relative_to(lab/name).parts)
sources.update(p for p in (lab/'patches').iterdir() if p.is_file())
sources.update(p for p in lab.iterdir() if p.is_file() and p.suffix in ('.c','.h','.xml'))
sources.add(lab/'protocol-before-results.md')
for run in (lab/'runs').iterdir():
    sources.update(run/name for name in ('fixture-source.py','client-source.c','config'))
source_manifest=out/'source-sha256.txt'
source_manifest.write_text(''.join(f'{sha(p)}  {p}\n' for p in sorted(sources)))
# Evidence includes all run files, result categories and build/analysis/model/final
# validation logs. Build binaries are identified by digests in build-identities.
evidence=set(p for p in (lab/'runs').rglob('*') if p.is_file())
evidence.update(p for p in out.iterdir() if p.is_file() and not p.name.endswith('-sha256.txt'))
evidence.update(p for p in lab.glob('*.log') if p.is_file())
evidence_manifest=out/'evidence-sha256.txt'
evidence_manifest.write_text(''.join(f'{sha(p)}  {p}\n' for p in sorted(evidence)))
for manifest in (source_manifest,evidence_manifest):
    for line in manifest.read_text().splitlines():
        digest,path=line.split('  ',1)
        assert sha(Path(path))==digest,path
    print(manifest.name,len(manifest.read_text().splitlines()),sha(manifest))
