"""Fail-closed independent acceptance, persistent tokens, one atomic ledger."""
import fcntl,hashlib,json,os,stat,sys,time
from pathlib import Path
from plans import *
HERE=Path(__file__).resolve().parent
SCOPE='STEP20C_TARGETED_FINAL_BYTES_V1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def need(ok,msg):
    if not ok:raise ValueError(msg)
def durable(p,data,exclusive=False):
    p=Path(p);raw=(json.dumps(data,indent=2)+'\n').encode()
    if exclusive:
        fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    else:
        tmp=p.with_name(p.name+'.new');fd=os.open(tmp,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
    fd=os.open(p.parent,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
def clean_environment():
    # Strip every inherited display/IPC and private library selection.
    from importlib.util import spec_from_file_location,module_from_spec
    spec=spec_from_file_location('targeted_environment',BASE/'support.py');m=module_from_spec(spec);spec.loader.exec_module(m)
    return m.environment()
def owned(lab):
    lab=Path(lab).resolve();need(lab==DEFAULT_LAB and lab.stat().st_uid==os.getuid() and stat.S_IMODE(lab.stat().st_mode)==0o700,'registered owned0700 lab');return lab
def initialize(lab):
    lab=owned(lab);durable(lab/'budget.json',dict(scope=SCOPE,runs={},events=[],used=dict(run=0,capture=0),campaign_used=dict.fromkeys(CAPS,0),campaign_runs=dict.fromkeys(CAPS,0)),True)
def validate(state):
    need(state.get('scope')==SCOPE,'ledger scope');events=state['events'];runs=state['runs']
    need(state['used']==dict(run=len(runs),capture=sum(e['kind']=='capture' for e in events)),'global reconciliation')
    need(len(runs)<=14 and state['used']['capture']<=174,'global cap')
    for campaign in CAPS:
        ids=[r for r,s in runs.items() if s['campaign']==campaign]
        need(state['campaign_runs'][campaign]==len(ids)<=RUN_CAPS[campaign],'campaign run reconciliation')
        captures=sum(e['kind']=='capture' and e['id'] in ids for e in events)
        need(state['campaign_used'][campaign]==captures<=CAPS[campaign],'campaign capture reconciliation')
    for rid,s in runs.items():
        need(rid in RUNS and s['campaign']==RUNS[rid]['campaign'] and s['planned']==RUNS[rid]['limits'],'run immutable plan')
        counts={k:sum(e['id']==rid and e['kind']==k for e in events) for k in s['planned']}
        need(s['reserved']==counts and all(type(v)is int and 0<=v<=s['planned'][k] for k,v in counts.items()),'local reconciliation')
        need(counts['capture']<=16,'per-run cap')
    need(all(e['sequence']==i and type(e['ns'])is int and e['ns']>0 and e['id'] in runs and e['kind'] in runs[e['id']]['planned'] for i,e in enumerate(events)),'event schema')
    return state
def locked(lab,operation):
    with (lab/'budget.lock').open('a+') as f:
        fcntl.flock(f,fcntl.LOCK_EX);state=validate(read(lab/'budget.json'));result=operation(state);validate(state);durable(lab/'budget.json',state);return result
def action_debit(lab,rid,*kinds):
    lab=owned(lab)
    def update(s):
        need(rid in s['runs'] and kinds,'consumed run token');r=s['runs'][rid]
        need(all(k in r['planned'] and r['reserved'][k]+kinds.count(k)<=r['planned'][k] for k in kinds),'local action cap')
        count=kinds.count('capture');need(s['used']['capture']+count<=174 and s['campaign_used'][r['campaign']]+count<=CAPS[r['campaign']],'global capture cap')
        for k in kinds:
            r['reserved'][k]+=1;s['events'].append(dict(id=rid,kind=k,ns=time.monotonic_ns(),sequence=len(s['events'])))
            if k=='capture':s['used']['capture']+=1;s['campaign_used'][r['campaign']]+=1
    locked(lab,update)
def frozen_paths(lab):
    # Exhaustive source closure declared at preparation; recursive fixture bytes
    # also bind new FX files and any later helper additions.
    ident=read(lab/'identity.json')
    paths=[p for p in HERE.iterdir() if p.is_file() and (p.suffix in ('.py','.c') or p.name=='README.md')]
    paths += [Path(p) for p in ident['closure']]
    paths += [lab/'identity.json',lab/'offline.json',lab/'replay.json',lab/'fx-offline.json']
    paths += [Path(read(lab/name)['raw_output']) for name in ('offline.json','fx-offline.json')]
    paths += [p for p in (lab/'clients').iterdir() if p.is_file()]
    return sorted(set(paths))
def source_bindings():
    return {str(p):sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and (p.suffix in ('.py','.c') or p.name=='README.md')}
def test_receipt(lab,name,minimum):
    r=read(lab/name);need(r.get('status')=='PASS' and type(r.get('executed'))is int and r['executed']>=minimum and r.get('exit')==0,'complete executed test receipt '+name)
    need(isinstance(r.get('command'),list) and len(r['command'])>=2 and r.get('source_bindings')==source_bindings(),'test command/exact sources '+name)
    need(Path(r['raw_output']).is_relative_to(lab) and sha(r['raw_output'])==r['raw_sha256'] and Path(r['raw_output']).stat().st_size>0,'raw test receipt '+name)
    need(not r.get('failures') and not r.get('errors'),'test failures '+name);return r
def replay_receipt(lab):
    r=read(lab/'replay.json');need(r.get('status')=='PASS' and r.get('source_bindings')==source_bindings(),'replay exact sources')
    need(isinstance(r.get('evidence'),dict) and len(r['evidence'])>=7 and all(sha(p)==h for p,h in r['evidence'].items()),'replay raw source bindings')
    d=r['D2'];need(d.get('historical_verdict')=='INCONCLUSIVE unchanged; input/dismissal/final NOT EXERCISED' and len(d['association']['states'])>=1 and len(d['preowner']['epochs'])>=2 and d['association']['tree']!=d['preowner']['tree'],'actual D2 association replay')
    f=r['F'];actual=__import__('validators').native_pairs(Path(f['source']).read_text());need(f['sha256']==sha(f['source']) and f['pairs']==actual and len(actual['analyzed'])==actual['total_commits'] and actual['total_commits']>=57,'ALL actual F commits replay')
    e=r['E2'];need(e['status']=='SOURCE_ONLY; historical held NOT EXERCISED' and e['runtime_command']=='gaps inner current set 30' and e['argc']==4 and e['arrange_workspace'] is True,'E2 source defect replay')
    need(sha(e['source'])==e['sha256'] and 'argc == 4 && !config->reading' in Path(e['source']).read_text(),'E2 actual source binding');return r
def receipts(lab):
    test_receipt(lab,'offline.json',14);test_receipt(lab,'fx-offline.json',5);replay_receipt(lab)
def seal(lab):
    lab=owned(lab);receipts(lab)
    durable(lab/'freeze.json',dict(scope=SCOPE,status='READY_FOR_REVIEW',files={str(p):sha(p) for p in frozen_paths(lab)},plans=RUNS),True)
def verify(lab,review=True):
    lab=owned(lab);receipts(lab);f=read(lab/'freeze.json');need(f['scope']==SCOPE and f['plans']==RUNS and f['files']=={str(p):sha(p) for p in frozen_paths(lab)},'frozen exact final bytes')
    if review:
        r=read(lab/'review.json');need(r.get('scope')==SCOPE and r.get('status')=='ACCEPTED' and r.get('independent') is True and r.get('read_only') is True and r.get('blockers')==[] and r.get('author')!='targeted_fixtures','independent acceptance required')
        need(r.get('freeze_sha256')==sha(lab/'freeze.json') and r.get('files')==f['files'] and sha(r['report_file'])==r['report_sha256'],'review exact-byte binding')
    return f
def begin(lab,rid):
    lab=owned(lab);need(rid in RUNS and not sys.flags.optimize,'fixed run and assertions');verify(lab)
    ident=read(lab/'identity.json');v=RUNS[rid]['variant'];binary,digest=BINARIES[v];need(sha(binary)==digest and sha(WLROOTS)==WLROOTS_SHA and sha(SCENE)==ident['scene_sha256'],'exact binary/library')
    for proc in Path('/proc').iterdir():
        if proc.name.isdigit():
            try:exe=(proc/'exe').resolve(strict=True)
            except (FileNotFoundError,PermissionError,ProcessLookupError):continue
            need(exe!=binary.resolve(),'same exact binary already running')
    folder=lab/'runs'/rid;need(not (folder/'run').exists(),'run already exists')
    # No tool ever refunds or clears this durable consumed entry.
    def update(s):
        campaign=RUNS[rid]['campaign'];need(rid not in s['runs'] and s['used']['run']<14 and s['campaign_runs'][campaign]<RUN_CAPS[campaign],'no retry; run cap')
        planned=RUNS[rid]['limits'];need(s['used']['capture']+planned['capture']<=174 and s['campaign_used'][campaign]+planned['capture']<=CAPS[campaign],'available planned capture cap')
        s['runs'][rid]=dict(campaign=campaign,planned=planned,reserved=dict.fromkeys(planned,0),consumed_ns=time.monotonic_ns(),freeze_sha256=sha(lab/'freeze.json'));s['used']['run']+=1;s['campaign_runs'][campaign]+=1
    locked(lab,update)
    return dict(binary=str(binary),binary_sha256=digest,wlroots=str(WLROOTS),wlroots_sha256=WLROOTS_SHA,pristine_scene=str(SCENE),pristine_scene_sha256=ident['scene_sha256'])
