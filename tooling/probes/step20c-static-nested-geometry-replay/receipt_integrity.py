"""Semantic checks for the fixed, retained offline campaign; no runtime action.

WHY: self-consistent labels/hashes cannot establish observations. Reuse the
qualified replay, input correlation and AST checker instead of a second model.
CONTRACT: historical inputs are read-only; all checker output is disposable.
INVARIANT: cached replay is bound to sealed input bytes, never caller receipts.
"""
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import tempfile

from support import sha

HERE = Path(__file__).resolve().parent
SEALED = Path('/home/fy59/swayfx-mosaic-static-nested-geometry-replay-a56csvoo')
SEALS = {'source-sha256.txt': 'e1230ba1292f12d913b762f0678e638a2effb513b74eb44dd232c12aa4acea1d',
         'evidence-sha256.txt': '22b9ac035da95ba914c28d72d8aa6f019c16c2854095d81ceb62c0bd10da8dbe'}
REVIEW_ATTACKS = {'R02-A','R02-B','R02-C','root-empty','nested-empty','input-partial',
                  'render-incoherent','standard-missing','dismissal-missing',
                  'serial-contradiction','source-stale','old-review-bindings'}


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def same(actual, expected, path='receipt'):
    """Types matter: Python's True == 1 must not accept a serial or count."""
    check(type(actual) is type(expected), path + ': wrong type')
    if isinstance(expected, dict):
        check(set(actual) == set(expected), path + ': missing/unexpected fields')
        for key in expected:
            same(actual[key], expected[key], path + '.' + key)
    elif isinstance(expected, list):
        check(len(actual) == len(expected), path + ': incomplete observations')
        for index, value in enumerate(expected):
            same(actual[index], value, path + '[' + str(index) + ']')
    else:
        if isinstance(actual, float):
            check(math.isfinite(actual), path + ': nonfinite coordinate')
        check(actual == expected, path + ': contradicts original observation')


def fresh(mapping, hash_file, required=None):
    check(isinstance(mapping, dict) and bool(mapping), 'missing hash inventory')
    if required is not None:
        check(set(mapping) == set(required), 'incomplete mandatory inventory')
    for path, digest in mapping.items():
        check(isinstance(path, str) and bool(path), 'invalid input path')
        check(isinstance(digest, str) and len(digest) == 64 and
              all(c in '0123456789abcdef' for c in digest), 'missing/invalid SHA-256')
        check(hash_file(path) == digest, 'missing/stale file: ' + path)


@lru_cache(maxsize=1)
def sealed_receipts():
    """Bootstrap only the immutable historical source/provenance contracts.

    The fixed manifests authenticate the campaign used by this bounded gate.
    This does not accept derived semantics: geometry/input are replayed below.
    """
    for name, digest in SEALS.items():
        check(sha(SEALED / 'results' / name) == digest, 'historical seal changed')
        rows = (SEALED / 'results' / name).read_text().splitlines()
        check(len(rows) == (67 if name.startswith('source') else 88), 'seal inventory incomplete')
        for row in rows:
            expected, path = row.split('  ', 1)
            check(sha(path) == expected, 'sealed historical file changed: ' + path)
    return {name: json.loads((SEALED / 'results' / (name + '.json')).read_text())
            for name in ('source-audit', 'client-provenance', 'historical-replay', 'historical-evidence')}


def historical_inputs():
    from replay import NESTED, HISTORICAL
    old = sealed_receipts()
    expected = dict(old['historical-evidence']['inputs'])
    manifest = HISTORICAL / 'results/evidence-sha256.txt'
    check(sha(manifest) == '5750d1e74636c2d276800f795ed0214c3e12999908149855af0b382a2da9bfb4',
          'original geometry evidence seal changed')
    sealed_raw = {path: digest for digest,path in
                  (line.split('  ',1) for line in manifest.read_text().splitlines())}
    # Replay also reads these original IPC/calibration/reference observations.
    extra = [str(HISTORICAL / rel) for rel in (
        'results/camera-calibration.json', 'results/E1-applied-snapshot.json',
        'results/geometry-fixture-diagnostic.json', 'run/H2-reference-1.png', 'run/H2-reference-2.png')]
    for path in extra:expected[path]=sealed_raw[path]
    for row in old['historical-replay']['cases']:
        expected.update({str(NESTED / row['case'] / name): digest for name,digest in row['files'].items()})
    fresh(expected, sha)
    return dict(sorted(expected.items()))


@lru_cache(maxsize=1)
def rederived(input_key):
    """Bounded cache: one replay, keyed by every raw input's real SHA-256.

    Rechecking hashes before lookup prevents a stale cache from authorizing
    changed observations. No subprocess, client or compositor is executed.
    """
    from replay import replay_native, replay_nested
    with tempfile.TemporaryDirectory(prefix='mosaic-receipt-replay-') as tmp:
        root = Path(tmp)
        (root / 'results').mkdir()
        replay_native(root)
        replay_nested(root)
        values = {p.stem: json.loads(p.read_text()) for p in (root / 'results').glob('*.json')}
    # The positioner is a source prediction, separate from historical configure.
    values['positioner'] = dict(status='PASS source-backed prediction', flags=0,
        A=[100,80,350,170], B=[100,60,300,130], predicted_content_origin=[-318,25],
        predicted_A=[-218,105,350,170], predicted_B=[-118,165,300,130],
        runtime='NOT TESTED; actual configure/ACK/map required')
    return values


@lru_cache(maxsize=16)
def checked_historical(name, receipt_key, input_key):
    same(json.loads(receipt_key), rederived(input_key)[name], name)


def validate_historical(name, data, hash_file, inputs=None):
    inputs = historical_inputs() if inputs is None else inputs
    # Exact typed comparisons include all scenario-specific observations, not
    # just lists/status. Standard/null/zero-color cases follow the real replay.
    checked_historical(name, encoded(data), tuple(inputs.items()))


def validate_source_audit(data, hash_file):
    expected = sealed_receipts()['source-audit']
    same(data, expected, 'source-audit')
    for contract in data['contracts']:
        fresh({contract['source']: contract['sha256']}, hash_file)
        lines = Path(contract['source']).read_text().splitlines()
        for excerpt in contract['excerpts']:
            check(excerpt['token'] in lines[excerpt['line'] - 1], 'source excerpt token/line mismatch')
            check(excerpt['text'] in '\n'.join(lines), 'source excerpt absent')
    fresh({data['source_version_receipt']: data['source_version_sha256']}, hash_file)


def validate_client(data, hash_file):
    expected = sealed_receipts()['client-provenance']
    same(data, expected, 'client-provenance')
    fresh(data['inputs'], hash_file, expected['inputs'])
    fresh({str(HERE / 'placement.patch'): data['patch']}, hash_file)
    builds = {b['client']: b for b in data['builds']}
    for command in data['commands']:
        check(command['exit'] == 0, 'historical C17 command failed')
        label, argv = command['label'], command['argv']
        if label.endswith('-compile') and label[:-8] in builds:
            build = builds[label[:-8]]
            source = next(v for v in argv if v.endswith('/' + label[:-8] + '.c'))
            output = argv[argv.index('-o') + 1]
            fresh({source: build['source'], output: build['binary']}, hash_file)
            fresh({str(Path(source).parent / n): v for n, v in data['protocols'].items()}, hash_file)


def validate_tests(data, hash_file):
    check(set(data)=={'status','source_inventory','tests'}, 'missing test receipt fields')
    files = {str(p) for p in HERE.iterdir() if p.suffix in ('.py', '.patch', '.json')}
    fresh(data['source_inventory'], hash_file, files)
    tests = data['tests']
    check(isinstance(tests, list) and bool(tests), 'missing executed tests')
    ids = set()
    # WHY: M0 must consume a genuinely completed negative suite. Excluding the
    # two positive controls avoids a circular requirement for their own PASS.
    import tests_offline
    mandatory = {'Case.' + n for n in dir(tests_offline.Case)
                 if n.startswith('test_') and n not in (
                     'test_positive_aggregate_complete_bound','test_integrity_legitimate_omissions')}
    allowed={'Case.'+n for n in dir(tests_offline.Case) if n.startswith('test_')}
    for test in tests:
        check(isinstance(test, dict), 'malformed test receipt')
        check(test['status'] == 'PASS' and test['mode'] in ('positive', 'negative'), 'failed/unclassified test')
        check(isinstance(test['id'], str) and '.Case.test_' in test['id'], 'invalid test identity')
        check(test['id'] not in ids, 'duplicate test identity')
        ids.add(test['id'])
        check(test['id'].split('.Case.')[0] in ('__main__','tests_offline') and
              test['id'][test['id'].index('Case.'):] in allowed,'unknown executed test identity')
        for field in ('executed_lines', 'failed_lines', 'contracts'):
            check(isinstance(test[field], list), 'missing test trace: ' + field)
        check(bool(test['executed_lines']) and all(isinstance(line,str) and bool(line)
              for line in test['executed_lines']), 'empty executed test trace')
        for c in test['contracts']:
            check(isinstance(c['contract'], str) and bool(c['contract']) and type(c['pass']) is bool,
                  'invalid executed contract')
    check(mandatory <= {n[n.index('Case.'):] for n in ids}, 'incomplete mandatory negative suite')


@lru_cache(maxsize=1)
def checked_register(key):
    """Use the original qualified AST checker, writing only to a temp LAB."""
    import assertions
    evidence = json.loads(key)
    with tempfile.TemporaryDirectory(prefix='mosaic-receipt-register-') as tmp:
        lab = Path(tmp)
        (lab / 'results').mkdir()
        for name, data in evidence.items():
            (lab / 'results' / (name + '.json')).write_text(json.dumps(data))
        # WHY: checking existing AST keys alone allowed null or misleading
        # derived classification/coverage fields. Regenerate every record
        # through the same classifier and executed-receipt logic as the writer
        # workflow, then compare the full caller-provided register and core.
        coverage=assertions.build(lab)
        generated=json.loads((lab/'results/assertion-register.json').read_text())
        same(evidence['assertion-register'],generated,'assertion-register effective content')
        same(evidence['offline-core-coverage'],json.loads((lab/'results/offline-core-coverage.json').read_text()),'offline-core-coverage effective content')
        return coverage


def validate_register(name, evidence, hash_file):
    import assertions
    register = evidence['assertion-register']
    check(set(register)=={'status','source_inventory','artifact_inventory','records','counts','historical_asserts'},
          'missing register receipt fields')
    same(register['historical_asserts'],145,'historical assertion count')
    same(register['status'],'CLASSIFIED; execution status is per-entry','register classification scope')
    paths = [assertions.HISTORY / n for n in assertions.HISTORICAL_FILES] + [
        p for p in sorted(HERE.glob('*.py')) if p.name != 'tests_offline.py']
    required = {str(p.relative_to(assertions.REPO)) for p in paths}
    check(set(register['source_inventory']) == required, 'incomplete AST source inventory')
    fresh({str(assertions.REPO / p): v for p,v in register['source_inventory'].items()}, hash_file)
    artifacts = {str(p) for p in HERE.iterdir() if p.suffix in ('.patch', '.json')}
    fresh(register['artifact_inventory'], hash_file, artifacts)
    selected = {n: evidence[n] for n in ('assertion-register', 'test-receipts', 'offline-core-coverage')}
    coverage = checked_register(encoded(selected))
    records = register['records']
    counts = {kind: sum(r['kind'] == kind for r in records) for kind in sorted({r['kind'] for r in records})}
    same(register['counts'], counts, 'AST counts')
    same(evidence['assertion-coverage'], coverage, 'assertion-coverage')
    core = {'model.py', 'ledger.py', 'authorization.py', 'observations.py', 'pixels.py'}
    unproved = [r['id'] for r in records if Path(r['source']).name in core and
                r['kind'] == 'checked invariant' and not
                (r['positive_executed_test_ids'] and r['negative_executed_test_ids'])]
    same(evidence['offline-core-coverage'], dict(status='PASS' if not unproved else 'FAIL NOT PROVEN', unproved=unproved), 'offline-core-coverage')
    check(not unproved and coverage['unresolved_pure_invariants'] == [], 'necessary pure coverage unproved')


def make_bindings(evidence, evidence_files=None):
    """Canonical content digest supports M0 in memory and binds real receipts.

    WHY: raw file hashes alone cannot bind a caller's mutated parsed object.
    File hashes remain separate; formatting changes after review also expire it.
    """
    from write_results import REQUIRED
    result = dict(source_delta={p.name: sha(p) for p in HERE.iterdir() if p.is_file()},
                  evidence_content={n: hashlib.sha256(encoded(evidence[n]).encode()).hexdigest() for n in REQUIRED})
    if evidence_files is not None:
        result['evidence_files'] = {n: str(p) for n,p in evidence_files.items()}
        result['evidence_sha256'] = {n: sha(p) for n,p in evidence_files.items()}
    else:
        # Memory-only tests bind canonical bytes, not imaginary evidence files.
        result['evidence_sha256'] = dict(result['evidence_content'])
    return result


def validate_review(evidence, bindings, hash_file):
    from write_results import REQUIRED
    check(isinstance(bindings, dict), 'missing final bindings')
    current = make_bindings(evidence)
    same(bindings['source_delta'], current['source_delta'], 'review final sources')
    fresh({str(HERE / n): v for n,v in bindings['source_delta'].items()}, hash_file)
    same(bindings['evidence_content'], current['evidence_content'], 'review final receipt content')
    check(set(bindings['evidence_sha256']) == set(REQUIRED), 'missing evidence bindings')
    if 'evidence_files' in bindings:
        check(set(bindings['evidence_files']) == set(REQUIRED), 'missing evidence paths')
        for name in REQUIRED:
            path = bindings['evidence_files'][name]
            fresh({path: bindings['evidence_sha256'][name]}, hash_file)
            same(json.loads(Path(path).read_text()), evidence[name], 'loaded proof ' + name)
    else:
        same(bindings['evidence_sha256'], current['evidence_content'], 'memory evidence hashes')
    review = evidence['independent-review']
    check(review['status'] == 'ACCEPTED' and review['independent'] is True, 'review not independently ACCEPTED')
    for key, value in bindings.items():
        same(review[key], value, 'review not bound to final source/evidence hashes: ' + key)
    if 'evidence_files' not in bindings:
        # CONTRACT: only the in-memory positive control may use synthetic
        # acceptance. The writer always supplies evidence_files and cannot
        # turn this test receipt into independent publication authority.
        check(review['scope']=='SYNTHETIC_IN_MEMORY_ONLY','unqualified memory review')
        return
    check(review['scope']=='FINAL_OFFLINE_RECEIPT_INTEGRITY','synthetic/incorrect persisted review scope')
    check(review['reviewer_role'] in ('final-reviewer','reviewer') and
          isinstance(review['reviewer_agent'],str) and bool(review['reviewer_agent']) and
          review['read_only'] is True,'missing independent reviewer provenance')
    fresh({review['report_file']:review['report_sha256']},hash_file)
    report=Path(review['report_file']).read_text()
    check('RECEIPT_INTEGRITY_REVIEW=ACCEPTED' in report,'report does not accept final version')
    commands=review['commands']
    check(isinstance(commands,list) and bool(commands),'missing executed review commands')
    for command in commands:
        check(isinstance(command['argv'],list) and bool(command['argv']) and
              all(isinstance(a,str) and bool(a) for a in command['argv']) and
              type(command['exit_code']) is int and command['exit_code']==0,
              'review command absent/failed')
    mutations=review['mutations']
    check(isinstance(mutations,dict) and REVIEW_ATTACKS<=set(mutations),'incomplete independent mutation set')
    for name in REVIEW_ATTACKS:
        result=mutations[name]
        check(result['status']=='INCONCLUSIVE' and isinstance(result['blockers'],list) and
              bool(result['blockers']) and all(isinstance(b,str) and bool(b) for b in result['blockers']),
              'independent attack not rejected: '+name)
    check(isinstance(review['findings'],list) and
          all(isinstance(f,dict) and f.get('severity') in ('NON_BLOCKING','FUTURE_SCOPE') for f in review['findings']),
          'material independent finding unresolved')
    check(isinstance(review['limitations'],list) and bool(review['limitations']) and
          all(isinstance(s,str) and bool(s) for s in review['limitations']), 'review scope absent')
