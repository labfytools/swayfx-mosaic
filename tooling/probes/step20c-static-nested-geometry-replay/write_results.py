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
    failures={}
    def need(name,ok,reason):
        if not ok:failures.setdefault(name,[]).append(reason)
    def fresh(mapping):
        return bool(mapping) and all(hash_file(path)==digest for path,digest in mapping.items())
    for name in REQUIRED:
        d=evidence.get(name)
        need(name,isinstance(d,dict) and bool(d),'missing evidence')
        if not isinstance(d,dict):continue
        status=d.get('status','')
        need(name,status=='PASS' or status.startswith('PASS ')
             or name=='assertion-register' and status=='CLASSIFIED; execution status is per-entry','gate not PASS')
    def record(name):return evidence.get(name) or {}
    for name in ('native-shm','xdg-configure','applied','rendered','positioner'):
        fields={'native-shm':('size','buffer','stride','format'), 'xdg-configure':('toplevel','initial_ACK','assigned_ACK'),
                'applied':('owner','workspace','scene','window','titlebar','globalclip'),
                'rendered':('content','PNG_bbox','count','visible_intersection'),
                'positioner':('flags','A','B')}[name]
        need(name,all(k in record(name) for k in fields),'incomplete geometry proof')
    need('historical-evidence',fresh(record('historical-evidence').get('inputs',{})),'stale/missing historical inputs')
    cases=record('historical-replay').get('cases',[])
    expected={'run-private_mosaic-crossing-b_cross','run-private_mosaic-crossing-both_cross',
              'run-private_mosaic-toggle-b_cross','run-private_mosaic-outside-visible',
              'run-control-crossing-b_cross','run-control-crossing-both_cross','run-control-outside-visible',
              'run-private_mosaic-close_b-visible','run-control-close_b-visible'}
    need('historical-replay',len(cases)==9 and {c.get('case') for c in cases}==expected,'required nine cases incomplete')
    for c in cases:
        need('historical-replay',c.get('status')=='PASS historical sampled replay' and c.get('input_correlation',{}).get('status')=='PASS','case/input proof incomplete')
        need('historical-replay',fresh({str(__import__('replay').NESTED/c.get('case','')/n):v for n,v in c.get('files',{}).items()}),'stale case files')
    for name in ('popup-root','popup-nested'):
        need(name,len(record(name).get('cases',[]))==9,'incomplete popup proof')
    audit=record('source-audit');contracts=audit.get('contracts',[])
    need('source-audit',len(contracts)==17 and all(c.get('claim') and c.get('excerpts') and hash_file(c.get('source',''))==c.get('sha256') for c in contracts),'incomplete/stale source contracts')
    need('source-audit',bool(audit.get('pins')) and hash_file(audit.get('source_version_receipt',''))==audit.get('source_version_sha256') and bool(audit.get('source_version_sha256')),'stale pinned receipt')
    client=record('client-provenance');commands=client.get('commands',[])
    need('client-provenance',fresh(client.get('inputs',{})),'stale client sources')
    need('client-provenance',all(client.get(k) for k in ('patch','adapted_nested','protocols','protocol_comparison','builds')),'incomplete provenance')
    needed={n+'-'+mode for n in ('nested-client','pointer-daemon','static-reference') for mode in ('syntax','compile')}
    need('client-provenance',needed<={c.get('label') for c in commands} and all(c.get('exit')==0 for c in commands),'C17 commands missing/failed')
    for command in commands:
        if command.get('label') in needed:need('client-provenance','-std=c17' in command.get('argv',[]) and '-Werror' in command.get('argv',[]),'C17 flags incomplete')
    need('client-provenance',hash_file(str(HERE/'placement.patch'))==client.get('patch'),'stale placement patch')
    builds={c.get('client'):c for c in client.get('builds',[])}
    need('client-provenance',set(builds)=={'nested-client','pointer-daemon','static-reference'},'missing client builds')
    for command in commands:
        label=command.get('label','');argv=command.get('argv',[])
        if label.endswith('-compile') and label[:-8] in builds:
            build=builds[label[:-8]]
            output=argv[argv.index('-o')+1] if '-o' in argv else ''
            source=next((v for v in argv if v.endswith('/'+label[:-8]+'.c')),'')
            need('client-provenance',bool(output) and hash_file(output)==build.get('binary') and bool(source) and hash_file(source)==build.get('source'),'stale built client/source')
            directory=Path(source).parent
            need('client-provenance',all(hash_file(str(directory/n))==v for n,v in client.get('protocols',{}).items()),'stale generated protocols')
    register=record('assertion-register');inventory=register.get('source_inventory',{})
    need('assertion-register',fresh({str(HERE.parents[2]/p):v for p,v in inventory.items()}) and fresh(register.get('artifact_inventory',{})),'stale inventory')
    need('assertion-register',register.get('historical_asserts')==145 and bool(register.get('records')),'incomplete register')
    coverage=record('assertion-coverage')
    need('assertion-coverage',coverage.get('status')=='PASS' and coverage.get('historical_asserts')==145 and coverage.get('entries')==len(register.get('records',[])) and coverage.get('unresolved_pure_invariants')==[],'coverage incomplete')
    need('offline-core-coverage',record('offline-core-coverage').get('unproved')==[],'core unproved')
    tests=record('test-receipts');receipts=tests.get('tests',[])
    need('test-receipts',fresh(tests.get('source_inventory',{})),'stale test sources')
    need('test-receipts',bool(receipts) and all(t.get('status')=='PASS' for t in receipts) and len({t.get('id') for t in receipts})==len(receipts),'missing/failed test receipts')
    review=record('independent-review')
    need('independent-review',review.get('status')=='ACCEPTED' and review.get('independent') is True,'review not independently ACCEPTED')
    need('independent-review',bool(bindings.get('source_delta')) and bool(bindings.get('evidence_sha256')) and all(review.get(k)==v for k,v in bindings.items()),'review not bound to final source/evidence hashes')
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
        return json.loads(path.read_text()) if path.exists() else {}
    aliases={'native-shm-geometry':'native-shm','xdg-configure-geometry':'xdg-configure','applied-content-geometry':'applied','rendered-paint-geometry':'rendered','popup-positioner-audit':'positioner','historical-popup-replay':'historical-replay','root-clip-model':'popup-root','nested-clip-model':'popup-nested','positive-tests':'positive','negative-tests':'negative'}
    for name,source in aliases.items():save(lab,name,read(source))
    coverage=read('assertion-coverage');tests=read('test-receipts');core=read('offline-core-coverage')
    reviewfile=results/'independent-review.json'
    review=read('independent-review') if reviewfile.exists() else {'status':'NOT RUN','independent':False}
    evidence={name:read(name) for name in REQUIRED}
    evidence['independent-review']=review
    source_delta={p.name:sha(p) for p in HERE.iterdir() if p.is_file()}
    bindings=dict(source_delta=source_delta,evidence_sha256={name:sha(results/(name+'.json')) for name in REQUIRED if (results/(name+'.json')).exists()})
    def safe_hash(path):
        try:return sha(path)
        except (OSError,ValueError):return None
    gates=aggregate(evidence,safe_hash,bindings)
    markers=gates['markers'];blockers=gates['blockers'];status=gates['status']
    save(lab,'popup-geometry-model',dict(status=markers['STATIC_NESTED_XDG_GEOMETRY_AUDIT'],scope='offline typed model and sampled historical replay; new runtime NOT TESTED',root=read('popup-root'),nested=read('popup-nested'),prediction=read('positioner'),source='source-audit.json',native_input='Opening click must lie in actual native surface bounds; destination scaling alone is insufficient'))
    readiness=dict(status=status,marker='SWAYFX_MOSAIC_STATIC_NESTED_GEOMETRY_OFFLINE_GATE='+status,markers=markers,marker_scope=gates['marker_scope'],review_bindings=bindings,blockers=blockers,runtime='NOT TESTED',architectural_conclusion='UNDECIDED',fixture_only=True,current_ticket_runtime_authorized=False,runtime_budget_initialized=False,independent_review=review)
    save(lab,'runner-readiness',readiness);save(lab,'offline-gate',readiness)
    save(lab,'summary',dict(status=status,markers=markers,tests=len(tests.get('tests',[])),coverage=coverage,core=core,historical_cases=len(read('historical-replay').get('cases',[])),runtime_runs=0,new_popups=0,new_grabs=0,new_captures=0,new_camera_operations=0,runtime_budget_initialized=False,production_changes=False,source_delta={p.name:sha(p) for p in HERE.iterdir() if p.is_file()},manifest='UNSEALED; parent review required',next='independent review of final fixture/register/evidence; separate future authorization required for runtime',limitations=['atomic transaction-generation/native-buffer-frame identity NOT PROVEN','new static popup crossing/grab/input/standard NOT TESTED','vertical/scaled/rotated/migration/full damage NOT TESTED','production cross-output viewport NOT YET SUPPORTED']))
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

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('lab',type=Path);write(parser.parse_args().lab)
