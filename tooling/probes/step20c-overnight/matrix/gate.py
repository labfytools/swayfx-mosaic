"""Separate exact-byte gate: no case can borrow C's review or runtime budget."""
import fcntl,json,os,stat,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;BASE=ROOT.parent/'step20c-static-e2-completion'
sys.path.insert(1,str(ROOT))
from horizontal_gate import DEFAULT_LAB as LAB,sha,env as clean_environment,exclusive,durable,PRISTINE,PRISTINE_SHA,WLROOTS
import ledger
from protocols import RUNS
PROSPECTIVE_CASES=['D3-mosaic']
REVIEW_SCOPE='OVERNIGHT_MATRIX_D3_PROSPECTIVE_V3'
PLANNED_PNG={'D1':8,'D2':9,'D3':9,'D4':17,'E1':12,'E2':8,'E3':18,'F':8}

def read(p):return json.loads(Path(p).read_text())
def need(ok,msg):
    if not ok:raise ValueError(msg)
def verify_executed_archive():
    archive=LAB/'matrix/executed-v2-archive';f=read(archive/'freeze.json');mapping=read(archive/'archive-map.json')
    need(sha(archive/'freeze.json')=='a20ccb39095ca35363119b5cfe4b5c839c1a75863bd72a097686aeac76dd7d7f','original executed v2 freeze retained')
    r=read(archive/'review.json')
    need(r.get('status')=='ACCEPTED' and r.get('independent') is True and r.get('freeze_sha256')==sha(archive/'freeze.json') and r.get('files')==f['files'],'original executed v2 acceptance retained')
    need(set(mapping)==set(f['files']),'complete original path archive binding')
    for original,digest in f['files'].items():
        p=Path(mapping[original]);need(p.is_relative_to(archive/'frozen-files') and sha(p)==digest,'archived executed bytes:'+original)
    return mapping

def frozen_paths():
    w=LAB/'matrix';archive=verify_executed_archive();out=[p for p in HERE.iterdir() if p.is_file()]
    out+=[Path(p) for p in archive.values()]+[w/'executed-v2-archive/archive-map.json']
    out+=[ROOT/'ledger.py',ROOT/'horizontal_gate.py',ROOT/'horizontal_adapter.py']
    out+=[BASE/n for n in ('model.py','predicates.py','pixels.py','lifecycle.py','ipc_predicates.py','support.py','transition.py')]
    out+=[LAB/'phase-a.json',LAB/'parent/native-source-audit.json',w/'protocols.json',w/'compile.json',w/'offline-tests-rotation-v3-frozen.json',w/'readiness.json']
    out+=[p for p in (w/'clients').iterdir() if p.is_file()]
    out+=[w/'offline-tests-rotation-v3-complete-deps.json',w/'rotation-v3-readonly-validation-attempt1.json']
    out+=[LAB/'matrix/rotation-v3-repair-report.json',LAB/'matrix/rotation-v3-source.patch',LAB/'matrix/offline-tests-rotation-v3-attempt1.json',LAB/'mosaic-source/sway/desktop/layer_shell.c']
    out+=[LAB/'reviews/matrix-first-runtime-review.md',LAB/'reviews/matrix-first-runtime-review.json',LAB/'matrix/executed-v2-archive/freeze.json',LAB/'matrix/executed-v2-archive/review.json']
    out+=[LAB/'matrix/D2-mosaic/run'/n for n in ('compositor.log','owner.log','owner-geometry.json','events.jsonl','startup-snapshot.json')]
    out+=[w/'offline-tests-initial.json',w/'offline-tests.json',w/'actual-review-refusal.json',LAB/'horizontal/C2/run/compositor.log',LAB/'horizontal/C2/run/E2.log']
    out+=[Path(r['source']) for r in read(w/'compile.json')['sources']]
    out+=[Path(read(LAB/'phase-a.json')['binary']['path']),WLROOTS,PRISTINE]
    provenance=read(LAB/'horizontal/pristine-provenance.json');out+=[LAB/'horizontal/pristine-provenance.json',Path(provenance['historical_build_receipt'])]
    out+=[Path(r['path']) for c in provenance['source_equivalence'] for r in c['files']]
    out+=[LAB/r['path'] for r in read(LAB/'parent/native-source-audit.json')['sources']]
    out+=[Path('/home/fy59/swayfx-mosaic-optimized-edge-a55yjb8n/scene0-build/libscenefx-0.5.so').resolve()]
    import shutil
    out+=[Path(shutil.which(t)).resolve() for t in ('swaymsg','grim','swaybg')]
    return sorted(set(out))
def freeze():
    need(read(LAB/'matrix/protocols.json')==RUNS,'private protocol exact source mapping')
    need(read(LAB/'matrix/offline-tests-rotation-v3-frozen.json')['status']=='PASS','executed negative tests')
    need(sum(PLANNED_PNG[g]*sum(r['campaign']==g for r in RUNS.values()) for g in PLANNED_PNG)+37+17<=220,'whole batch planned PNG allocation')
    exclusive(LAB/'matrix/freeze.json',dict(scope=REVIEW_SCOPE,status='READY_FOR_REVIEW',prospective_cases=PROSPECTIVE_CASES,previous_freeze_sha256='a20ccb39095ca35363119b5cfe4b5c839c1a75863bd72a097686aeac76dd7d7f',files={str(p):sha(p) for p in frozen_paths()},protocols=RUNS,planned_png=PLANNED_PNG,
        total_matrix_png=sum(PLANNED_PNG[r['campaign']] for r in RUNS.values()),C_allocation=37,G_allocation=17))
def verify(review=True):
    w=LAB/'matrix';f=read(w/'freeze.json');need(f['files']=={str(p):sha(p) for p in frozen_paths()} and f['protocols']==RUNS and f.get('scope')==REVIEW_SCOPE and f.get('prospective_cases')==PROSPECTIVE_CASES,'final frozen bytes/schema')
    need(read(w/'readiness.json')['status']=='PREPARED_FOR_REVIEW','readiness')
    if review:
        r=read(w/'review.json');need(r.get('status')=='ACCEPTED' and r.get('independent') is True and r.get('read_only') is True and r.get('scope')==REVIEW_SCOPE and r.get('blockers')==[],'genuine independent matrix review')
        need(r.get('freeze_sha256')==sha(w/'freeze.json') and r.get('files')==f['files'],'review binding')
        need(sha(r['report_file'])==r['report_sha256'],'review report bytes')
    return f

def preflight(run_id,review=True):
    need(run_id in RUNS and not sys.flags.optimize,'known immutable case and assertions')
    verify(review);need(run_id in PROSPECTIVE_CASES,'only unused D3-mosaic prospective v3');w=LAB/'matrix'/run_id
    need(not (w/'consumed.json').exists() and not (w/'run').exists(),'no retry')
    need(stat.S_IMODE(LAB.stat().st_mode)==0o700 and LAB.stat().st_uid==os.getuid(),'owned0700 LAB')
    need(not any(stat.S_ISSOCK(p.lstat().st_mode) for p in w.rglob('*')),'stale case socket')
    a=read(LAB/'phase-a.json');need(a['status']=='PASS','phase A')
    need(read(LAB/'matrix/compile.json')['status']=='PASS','C17 clients')
    budget=read(LAB/'budget.json');ledger._validate(budget);spec=RUNS[run_id]
    need(run_id not in budget['runs'] and budget['used']['run']<18 and budget['campaign_used'][spec['campaign']]<ledger.CAMPAIGNS[spec['campaign']],'global run budget')
    need(budget['used']['capture']+PLANNED_PNG[spec['campaign']]<=220,'planned PNG availability')
    mode=spec['mode'];binary=a['binary']['path'] if mode=='mosaic' else str(PRISTINE);digest=a['binary']['sha256'] if mode=='mosaic' else PRISTINE_SHA
    need(sha(binary)==digest and sha(WLROOTS)=='7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837','exact candidate/pristine/wlroots')
    for p in Path('/proc').iterdir():
        if p.name.isdigit():
            try:exe=(p/'exe').resolve(strict=True)
            except (FileNotFoundError,PermissionError,ProcessLookupError):continue
            need(exe!=Path(binary).resolve(),'same binary already running')
    scene=Path('/home/fy59/swayfx-mosaic-optimized-edge-a55yjb8n/scene0-build/libscenefx-0.5.so').resolve()
    return dict(binary=binary,binary_sha256=digest,wlroots=str(WLROOTS),wlroots_sha256=sha(WLROOTS),pristine_scene=str(scene),pristine_scene_sha256=sha(scene))
def begin(run_id):
    auth=preflight(run_id);w=LAB/'matrix'/run_id;exclusive(w/'consumed.json',dict(id=run_id,freeze_sha256=sha(LAB/'matrix/freeze.json'),ns=time.monotonic_ns()))
    ledger.reserve(LAB/'budget.json','run',campaign=RUNS[run_id]['campaign'],run_id=run_id,duration_s=150)
    limits=action_limits(run_id)
    exclusive(w/'actions.json',dict(planned=limits,reserved=dict.fromkeys(limits,0),events=[]));return auth
def action_limits(run_id):
    limits={k:v for k,v in RUNS[run_id]['limits'].items() if k not in ('duration_s','active_watchdog_s')}
    limits['capture']=PLANNED_PNG[RUNS[run_id]['campaign']];limits['configuration']=48;return limits

def local_valid(run_id,state):
    limits=action_limits(run_id);need(state.get('planned')==limits,'immutable planned action limits')
    values=state.get('reserved');events=state.get('events');need(isinstance(values,dict) and set(values)==set(limits) and isinstance(events,list),'local schema')
    need(all(type(values[k]) is int and 0<=values[k]<=limits[k] for k in limits),'local typed counters')
    need(len(events)==sum(values.values()),'local event total')
    need(all(isinstance(e,dict) and e.get('sequence')==i and e.get('kind') in limits and type(e.get('ns')) is int and e['ns']>0 for i,e in enumerate(events)),'local event sequence')
    need(all(sum(e['kind']==k for e in events)==values[k] for k in limits),'local reconciliation')
    return state

def action_debit(run_id,*kinds):
    w=LAB/'matrix'/run_id
    with (w/'actions.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);state=local_valid(run_id,read(w/'actions.json'))
        need(kinds and all(k in state['planned'] for k in kinds),'known actions')
        need(all(state['reserved'][k]+kinds.count(k)<=state['planned'][k] for k in kinds),'planned local action exhausted')
        for k in kinds:
            if k=='capture':ledger.reserve(LAB/'budget.json','capture',run_id=run_id)
            state['reserved'][k]+=1;state['events'].append(dict(kind=k,ns=time.monotonic_ns(),sequence=len(state['events'])))
        durable(w/'actions.json',state)
