#!/usr/bin/env python3
"""EXPERIMENTAL read-only collection of this ticket's completed S observations.

WHY: raw exits, measured pixels, scientific closure and architectural claims
have different meanings. CONTRACT: no launch, retry, image mask, tolerance or
inference of native identity. INVARIANT: every claim retains its input hashes;
comparisons use entire RGB images with matching prospective state names.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def pixels(a, b):
    aa = np.asarray(Image.open(a).convert('RGB'), dtype=np.int16)
    bb = np.asarray(Image.open(b).convert('RGB'), dtype=np.int16)
    if aa.shape != bb.shape:
        return dict(result='INCONCLUSIVE', reason='different full image dimensions')
    diff = bb - aa
    changed = np.any(diff != 0, axis=2)
    return dict(result='EXACT' if not changed.any() else 'DIFFERENT',
                pixels=int(changed.sum()), total_pixels=int(changed.size),
                max_abs_RGB=np.abs(diff).max(axis=(0, 1)).tolist(),
                input_sha256=[sha(a), sha(b)])


def collect(lab):
    runs = []
    for execution in sorted((lab / 'runtime-execution').glob('*/execution.json')):
        rid = execution.parent.name
        folder = lab / 'graphics/runs' / rid / 'run'
        outcome = load(folder / 'outcome.json')
        events = [json.loads(line) for line in (folder / 'events.jsonl').read_text().splitlines()]
        pictures = [e for e in events if e['kind'] == 'capture']
        for e in pictures:
            if sha(Path(e['path'])) != e['sha256']:
                raise ValueError('capture integrity: ' + e['path'])
        chains = []
        for p in sorted(folder.glob('*chain*.json')):
            data = load(p)
            if 'protocol' in data:
                chains.append(dict(path=str(p), sha256=sha(p), evidence=data))
        log = (folder / 'compositor.log').read_text(errors='replace')
        damage = {}
        for line in log.splitlines():
            m = re.search(r'SPIKE_DAMAGE output=(\S+) extent=(-?\d+),(-?\d+)\.\.(-?\d+),(-?\d+)', line)
            if m:
                d = damage.setdefault(m[1], dict(records=0, extents=[]))
                d['records'] += 1
                box = list(map(int, m.groups()[1:]))
                if box not in d['extents']:
                    d['extents'].append(box)
        runs.append(dict(id=rid, execution=load(execution), execution_sha256=sha(execution),
                         outcome=outcome, outcome_sha256=sha(folder / 'outcome.json'),
                         captures=pictures, capture_count=len(pictures), chains=chains,
                         damage=damage,
                         native_PI_events=sum('PI_OUTPUT_COMMIT ' in s or 'PI_OUTPUT_PRESENT ' in s for s in log.splitlines()),
                         damage_limit='Recorded extents added to rings; includes startup modes before config. No exact region/frame/content coverage or present is inferred.'))
    comparisons = {}
    for name, ids in {
        'horizontal-standard': ('S0-pristine-standard', 'S1-core-standard'),
        'vertical': ('S3-pristine-vertical', 'S4-core-vertical'),
        'fullscreen': ('S5-pristine-fullscreen', 'S6-core-fullscreen'),
    }.items():
        a, b = [lab / 'graphics/runs' / i / 'run' for i in ids]
        if not (a / 'outcome.json').exists() or not (b / 'outcome.json').exists():
            comparisons[name] = dict(result='NOT_RUN', ids=ids)
            continue
        # Identical prospective names permit a raw comparison, not a claim of
        # equivalent geometry or identical transaction time across processes.
        common = sorted({p.name for p in a.glob('*.png')} & {p.name for p in b.glob('*.png')})
        comparisons[name] = dict(ids=ids, whole_RGB={n: pixels(a / n, b / n) for n in common},
                                 limitation='Raw same-named sampled states; review owner/configure/output geometry before semantic equivalence. Vertical Mosaic intentionally differs from pristine where clipped.')
    return dict(status='EXPERIMENTAL_DERIVED_OBSERVATIONS', lab=str(lab), runs=runs,
                comparisons=comparisons, new_runs=len(runs),
                output_PNG=sum(r['capture_count'] for r in runs),
                CORE_BUFFER_IDENTITY='NOT_PROVEN', CORE_ATOMIC_GENERATION='NOT_PROVEN')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--lab', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    result = collect(args.lab)
    with args.output.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps(dict(new_runs=result['new_runs'], output_PNG=result['output_PNG'])))


if __name__ == '__main__':
    main()
