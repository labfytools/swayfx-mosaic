#!/usr/bin/env python3
"""Generate a prospective gate only from actual nonempty executed receipts.

WHY: empty PASS and historical acceptance must not grant new readiness.
CONTRACT: final source hashes + complete tests + actual raw replay + AST audit.
INVARIANT: this gate is READY_FOR_REVIEW; independent acceptance is separate.
"""
import json
from pathlib import Path
from model import require
from support import sha
HERE=Path(__file__).resolve().parent


def normalized(value):return json.loads(json.dumps(value))


def sources():return {p.name:sha(p) for p in HERE.iterdir() if p.is_file()}


def validate_test_receipts(receipt):
    from tests_offline import expected_tests
    expected=expected_tests()
    rows=receipt.get('tests')
    require(receipt.get('status')=='PASS' and isinstance(rows,list) and len(rows)==len(expected)
        and receipt.get('executed')==len(expected) and receipt.get('failures')==receipt.get('errors')==receipt.get('skips')==0,
        'complete-executed-test-receipts')
    require({r.get('id') for r in rows}==expected and all(r.get('status')=='PASS' for r in rows),'exact-test-inventory')
    require(receipt.get('sources')=={p.name:sha(p) for p in HERE.glob('*.py')},'tested-final-source-bytes')
    negative=['retained_clip','no_standard_epoch','wrong_layout','wrong_owner','wrong_root','wrong_output',
        'reversed_times','standard_before_application','clip_reactivation','missing_root_traces','multiple_roots',
        'wrong_capture_epoch','different_workspace','popup_disappears_early','ipc_failure','no_root_clip_removal','pending_presented_applied']
    indexed={r['id']:r for r in rows}
    for name in negative:
        row=indexed['tests_offline.Transition.test_'+name]
        require(bool(row.get('rejected_contracts') or row.get('rejected_exceptions')),'executed-negative-rejection:'+name)
    return receipt


def validate_gate(path):
    from replay import replay
    from audit import audit
    path=Path(path);gate=json.loads(path.read_text())
    require(gate.get('status')=='READY_FOR_REVIEW' and gate.get('marker')=='E2_COMPLETION_OFFLINE=READY_FOR_REVIEW'
            and gate.get('source_sha256')==sources() and gate.get('blockers')==[], 'prospective-gate-final-source')
    receipts={}
    for name in ('test-receipts.json','replay.json','source-audit.json'):
        p=path.parent/name
        require(sha(p)==gate['receipts_sha256'][name],'actual-file-receipt:'+name)
        receipts[name]=json.loads(p.read_text())
    validate_test_receipts(receipts['test-receipts.json'])
    require(receipts['replay.json']==normalized(replay()),'real-raw-replay-receipt')
    require(receipts['source-audit.json']==normalized(audit()),'exhaustive-current-source-audit')
    require(gate.get('test_count')==len(receipts['test-receipts.json']['tests']),'gate-test-count')
    return gate


def write(directory):
    from audit import audit
    from replay import replay
    directory=Path(directory)
    tests=json.loads((directory/'test-receipts.json').read_text());validate_test_receipts(tests)
    require(json.loads((directory/'source-audit.json').read_text())==normalized(audit()),'audit-current')
    require(json.loads((directory/'replay.json').read_text())==normalized(replay()),'real-raw-replay-before-writing')
    result=dict(status='READY_FOR_REVIEW',marker='E2_COMPLETION_OFFLINE=READY_FOR_REVIEW',source_sha256=sources(),
        receipts_sha256={n:sha(directory/n) for n in ('test-receipts.json','replay.json','source-audit.json')},
        test_count=len(tests['tests']),blockers=[],runtime='NOT RUN',independent_review='PENDING')
    path=directory/'offline-gate.json'
    with path.open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    validate_gate(path);print(result['marker'])

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();write(a.directory)
