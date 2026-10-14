#!/usr/bin/env python3
"""EXPERIMENTAL read-only historical audit; receipts go to a new private LAB.

WHY: source hashes and native event keys must survive a new interpretation.
CONTRACT: never launch a compositor, rewrite historical evidence, or infer a
present, buffer identity or missing-event cause from a screenshot or teardown.
INVARIANT: each native key is scoped by LAB, run and output before aggregation.
"""
import argparse
import hashlib
import json
import stat
import sys
from pathlib import Path

OLD = Path('/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_')
EXPECTED = {
    'closeout.json': '5166d6442aae8dfa2a5e939eb5e83141f83c55e7be89f93670eb381e9956df0a',
    'closeout-manifest.json': '4fd7ccedf00a59754db447d015fdca35fbcdda5b7de3820c3655b6e433765ce8',
    'publication-receipt.json': '45396f706af9374547bda0d76edcb704298bca10a4ea300ae69b4fdb076de655',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def historical():
    failures = []
    for name, expected in EXPECTED.items():
        if sha(OLD / name) != expected:
            failures.append(name + ': identity')
    manifest = json.loads((OLD / 'closeout-manifest.json').read_text())
    for row in manifest['entries']:
        p = OLD / row['path']
        s = p.lstat()
        if oct(stat.S_IMODE(s.st_mode)) != row['mode']:
            failures.append(row['path'] + ': mode')
        if row['type'] == 'file':
            if not stat.S_ISREG(s.st_mode) or s.st_size != row['bytes'] or sha(p) != row['sha256']:
                failures.append(row['path'] + ': file')
        elif row['type'] != 'directory' or not stat.S_ISDIR(s.st_mode):
            failures.append(row['path'] + ': type')
    actual = {str(p.relative_to(OLD)) for p in OLD.rglob('*')}
    expected = {r['path'] for r in manifest['entries']}
    actual -= set(manifest['excluded_self_reference_outputs'])
    if actual != expected:
        failures.append({'added': sorted(actual - expected), 'missing': sorted(expected - actual)})
    return dict(status='PASS' if not failures else 'FAIL', entries=len(expected),
                files=sum(r['type'] == 'file' for r in manifest['entries']),
                checks='all file bytes/modes/types and complete path set; directory content digests not recomputed',
                identities=EXPECTED, failures=failures)


def native():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'step20c-saved-input-gpu-batch'))
    from native_replay import replay
    groups = {
        'initial': [Path('/home/fy59/swayfx-mosaic-overnight-mcolx0gq/matrix/F-mosaic/run/compositor.log')],
        'targeted': sorted(Path('/home/fy59/swayfx-mosaic-targeted-7gge6h8b/runs').glob('*/run/compositor.log')),
        'saved-input-gpu': sorted(Path('/home/fy59/swayfx-mosaic-saved-input-gpu-pz4z428f/runs').glob('*/run/compositor.log')),
        'historical-core': sorted((OLD / 'graphics/runs').glob('*/run/compositor.log')),
    }
    result = {}
    for group, paths in groups.items():
        rows = []
        for p in paths:
            r = replay(p.read_text(errors='replace'))
            by_output = {}
            for item in r['rows']:
                o = by_output.setdefault(item['output'], dict(commits=0, paired=0, missing=[]))
                o['commits'] += 1
                o['paired'] += item['present'] is not None
                if item['present'] is None:
                    o['missing'].append(dict(commit_seq=item['commit_seq'], cause='UNKNOWN'))
            rows.append(dict(path=str(p), sha256=sha(p), by_output=by_output,
                             counts=[r[k] for k in ('total_commits', 'paired', 'missing')],
                             unmatched_presents=r['unmatched_presents']))
        result[group] = dict(logs=rows, counts=[sum(r['counts'][i] for r in rows) for i in range(3)])
    for name, expected in [('initial', [57, 55, 2]), ('targeted', [821, 789, 32]), ('saved-input-gpu', [414, 400, 14])]:
        if result[name]['counts'] != expected:
            raise ValueError('historical count mismatch: ' + name)
    return dict(groups=result, missing_causes='UNKNOWN: no exact-key cause trace',
                CORE_BUFFER_IDENTITY='NOT_PROVEN', CORE_ATOMIC_GENERATION='NOT_PROVEN',
                CORE_NATIVE_ORDERING='NOT_EXERCISED',
                limitation='CORE lacks PI hooks; zero parsed events means NOT OBSERVABLE, not zero native commits. No new run without a discriminant.')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = dict(historical=historical(), native=native())
    with args.output.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps(dict(historical=result['historical'], native={k: v['counts'] for k, v in result['native']['groups'].items()}), indent=2))
    return int(result['historical']['status'] != 'PASS')


if __name__ == '__main__':
    raise SystemExit(main())
