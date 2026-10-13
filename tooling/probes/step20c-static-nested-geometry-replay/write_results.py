#!/usr/bin/env python3
"""JSON aliases and unsealed independent-review handoff; no runtime authority."""
import argparse
import json
from pathlib import Path
from support import save,sha

HERE=Path(__file__).resolve().parent


REQUIRED=('native-shm','xdg-configure','applied','rendered','positioner',
          'historical-evidence','historical-replay','popup-root','popup-nested',
          'source-audit','client-provenance','assertion-register',
          'assertion-coverage','offline-core-coverage','test-receipts')


def aggregate(evidence,hash_file,bindings):
    """CONTRACT: READY requires complete fresh offline gates and bound review.

    WHY: no author test or successful compile can substitute for another gate.
    Bindings describe the exact final evidence/source bytes reviewed independently.
    """
    from receipt_integrity import (validate_historical, validate_source_audit,
        validate_client, validate_register, validate_tests, validate_review, historical_inputs, fresh)
    failures={}
    def need(name,ok,reason):
        if not ok:failures.setdefault(name,[]).append(reason)
    def guarded(name, validator):
        # CONTRACT: invalid/missing evidence degrades its gate, never crashes
        # the writer or becomes a compositor/SceneFX architectural failure.
        try:
            validator()
        except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError,
                AssertionError, RuntimeError, StopIteration) as error:
            need(name,False,str(error) or type(error).__name__)
    if not isinstance(evidence,dict):evidence={}
    for name in REQUIRED:
        d=evidence.get(name)
        need(name,isinstance(d,dict) and bool(d),'missing/malformed evidence')
        if not isinstance(d,dict):continue
        status=d.get('status')
        need(name,isinstance(status,str) and (status=='PASS' or status.startswith('PASS ')
             or name=='assertion-register' and status=='CLASSIFIED; execution status is per-entry'),'gate not PASS')
    input_error=None
    try:
        inputs=historical_inputs()
        fresh(inputs,hash_file)
    except (OSError,ValueError,TypeError,KeyError,AssertionError) as error:
        inputs=None;input_error=str(error) or type(error).__name__
    for name in ('native-shm','xdg-configure','applied','rendered','positioner',
                 'historical-evidence','historical-replay','popup-root','popup-nested'):
        if input_error:need(name,False,input_error)
        else:guarded(name,lambda name=name:validate_historical(name,evidence.get(name),hash_file,inputs))
    # CONTRACT: after a failed prerequisite, unchecked downstream gates are
    # INCONCLUSIVE too. This bounds work on invalid input without granting PASS.
    def downstream(name,validator):
        if failures:need(name,False,'not qualified after failed prerequisite')
        else:guarded(name,validator)
    downstream('source-audit',lambda:validate_source_audit(evidence.get('source-audit'),hash_file))
    downstream('client-provenance',lambda:validate_client(evidence.get('client-provenance'),hash_file))
    downstream('test-receipts',lambda:validate_tests(evidence.get('test-receipts'),hash_file))
    for name in ('assertion-register','assertion-coverage','offline-core-coverage'):
        downstream(name,lambda name=name:validate_register(name,evidence,hash_file))
    downstream('independent-review',lambda:validate_review(evidence,bindings,hash_file))
    groups={'STATIC_NESTED_SHM_RENDER_GEOMETRY_REPLAY':('native-shm','applied','rendered','historical-evidence'),
            'STATIC_NESTED_XDG_GEOMETRY_AUDIT':('xdg-configure','positioner','historical-replay','popup-root','popup-nested','source-audit','client-provenance'),
            'STATIC_NESTED_ASSERTION_COVERAGE':('assertion-register','assertion-coverage','offline-core-coverage'),
            'STATIC_NESTED_OFFLINE_REGRESSIONS':('test-receipts',),
            'STATIC_NESTED_INDEPENDENT_REVIEW':('independent-review',)}
    markers={key:'PASS' if not any(n in failures for n in names) else 'INCONCLUSIVE' for key,names in groups.items()}
    return dict(status='INCONCLUSIVE' if failures else 'READY_FOR_NEW_RUNTIME',markers=markers,
                marker_scope={key:list(names) for key,names in groups.items()},
                blockers=[name+': '+reason for name,reasons in failures.items() for reason in reasons],review_bindings=bindings)

def write(lab):
    results=lab/'results'
    def read(name):
        path=results/(name+'.json')
        try:return json.loads(path.read_text()) if path.exists() else {}
        # WHY: a decoder-depth failure must not leave previous READY artifacts
        # authoritative. CONTRACT: malformed proof reaches the same aggregate
        # as missing proof, which publishes explicit INCONCLUSIVE markers.
        except (OSError,ValueError,RecursionError):return {}
    aliases={'native-shm-geometry':'native-shm','xdg-configure-geometry':'xdg-configure','applied-content-geometry':'applied','rendered-paint-geometry':'rendered','popup-positioner-audit':'positioner','historical-popup-replay':'historical-replay','root-clip-model':'popup-root','nested-clip-model':'popup-nested','positive-tests':'positive','negative-tests':'negative'}
    for name,source in aliases.items():save(lab,name,read(source))
    coverage=read('assertion-coverage');tests=read('test-receipts');core=read('offline-core-coverage')
    coverage=coverage if isinstance(coverage,dict) else {}
    tests=tests if isinstance(tests,dict) else {}
    reviewfile=results/'independent-review.json'
    review=read('independent-review') if reviewfile.exists() else {'status':'NOT RUN','independent':False}
    evidence={name:read(name) for name in REQUIRED}
    evidence['independent-review']=review
    from receipt_integrity import make_bindings
    try:
        bindings=make_bindings(evidence,{name:results/(name+'.json') for name in REQUIRED})
    except (OSError,ValueError,TypeError,KeyError,RecursionError):
        bindings={}  # Missing/malformed proof cannot carry accepted bindings.
    def safe_hash(path):
        try:return sha(path)
        except (OSError,ValueError):return None
    gates=aggregate(evidence,safe_hash,bindings)
    markers=gates['markers'];blockers=gates['blockers'];status=gates['status']
    save(lab,'popup-geometry-model',dict(status=markers['STATIC_NESTED_XDG_GEOMETRY_AUDIT'],scope='offline typed model and sampled historical replay; new runtime NOT TESTED',root=read('popup-root'),nested=read('popup-nested'),prediction=read('positioner'),source='source-audit.json',native_input='Opening click must lie in actual native surface bounds; destination scaling alone is insufficient'))
    readiness=dict(status=status,marker='SWAYFX_MOSAIC_STATIC_NESTED_GEOMETRY_OFFLINE_GATE='+status,markers=markers,marker_scope=gates['marker_scope'],review_bindings=bindings,blockers=blockers,runtime='NOT TESTED',architectural_conclusion='UNDECIDED',fixture_only=True,current_ticket_runtime_authorized=False,runtime_budget_initialized=False,independent_review=review)
    save(lab,'runner-readiness',readiness);save(lab,'offline-gate',readiness)
    def count_rows(value,key):
        rows=value.get(key) if isinstance(value,dict) else None
        return len(rows) if isinstance(rows,list) else 0
    save(lab,'summary',dict(status=status,markers=markers,tests=count_rows(tests,'tests'),coverage=coverage,core=core,historical_cases=count_rows(read('historical-replay'),'cases'),runtime_runs=0,new_popups=0,new_grabs=0,new_captures=0,new_camera_operations=0,runtime_budget_initialized=False,production_changes=False,source_delta={p.name:sha(p) for p in HERE.iterdir() if p.is_file()},manifest='UNSEALED; parent review required',next='independent review of final fixture/register/evidence; separate future authorization required for runtime',limitations=['atomic transaction-generation/native-buffer-frame identity NOT PROVEN','new static popup crossing/grab/input/standard NOT TESTED','vertical/scaled/rotated/migration/full damage NOT TESTED','production cross-output viewport NOT YET SUPPORTED']))
    (lab/'independent-review-input.md').write_text('''# Independent review input — EXPERIMENTAL

Review this final fixture against the offline gate; review E1/E2, actual
configure/ACK/map/grab, typed geometry, native input bounds, root correlation,
standard fresh origin, dismissal, terminal and owned cleanup.

Inputs: repository fixture sources, results/source-audit.json,
source-versions.json, historical-evidence.json, historical-popup-replay.json,
assertion-register.json, assertion-coverage.json, offline-core-coverage.json,
test-receipts.json, client-provenance.json and runner-readiness.json.

Write independent-review.md and results/independent-review.json with
ACCEPTED/CORRECTION_REQUIRED/NOT PROVEN findings. No author review PASS, runtime
launch, budget initialization or manifest sealing is authorized here.
''')
    print(json.dumps(readiness,indent=2))
    return readiness

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('lab',type=Path);write(parser.parse_args().lab)
