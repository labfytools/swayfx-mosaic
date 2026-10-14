"""Durable new-ticket accounting and exact-byte independent launch gate."""
import fcntl,hashlib,json,os,stat,time
from pathlib import Path
from plans import *
def need(ok,message):
    if not ok: raise ValueError(message)
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def durable(path,value,exclusive=False):
    path=Path(path);tmp=path if exclusive else path.with_name(path.name+'.new')
    fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as f:
        json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    if not exclusive: os.replace(tmp,path)
    fd=os.open(path.parent,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
def owned(lab):
    p=Path(lab).resolve();need(p==DEFAULT_LAB and p.stat().st_uid==os.getuid() and stat.S_IMODE(p.stat().st_mode)==0o700,'registered lab 0700');return p
def initialize(lab): durable(owned(lab)/'budget.json',dict(scope=SCOPE,runs={},events=[]),True)
def validate(s):
    need(s.get('scope')==SCOPE and len(s['runs'])<=8,'ticket/run cap')
    events=s['events'];need(len([e for e in events if e['kind']=='capture'])<=96,'capture total')
    for category,cap in CAPS.items():need(sum(e['kind']=='capture' and RUNS[e['id']]['campaign']==category for e in events)<=cap,'category cap')
    for rid,r in s['runs'].items():
        need(rid in RUNS and r['planned']==RUNS[rid]['limits'],'immutable run plan')
        counts={k:sum(e['id']==rid and e['kind']==k for e in events) for k in r['planned']}
        need(r['reserved']==counts and all(0<=v<=r['planned'][k] for k,v in counts.items()) and counts['capture']<=16,'local action reconciliation')
    need(all(e['sequence']==i and e['id'] in s['runs'] and e['kind'] in s['runs'][e['id']]['planned'] and type(e['ns']) is int for i,e in enumerate(events)),'event schema')
    return s
def locked(lab,operation):
    lab=owned(lab)
    with (lab/'budget.lock').open('a+') as f:
        fcntl.flock(f,fcntl.LOCK_EX);s=validate(read(lab/'budget.json'));result=operation(s);validate(s);durable(lab/'budget.json',s);return result
def action_debit(lab,rid,*kinds):
    # WHY CONTRACT INVARIANT: reservation precedes the attempted side effect;
    # failure consumes capacity, and no refund or reset operation exists.
    def op(s):
        need(rid in s['runs'] and kinds,'consumed one-shot token');r=s['runs'][rid]
        need(all(k in r['planned'] and r['reserved'][k]+kinds.count(k)<=r['planned'][k] for k in kinds),'action cap')
        for k in kinds:r['reserved'][k]+=1;s['events'].append(dict(id=rid,kind=k,ns=time.monotonic_ns(),sequence=len(s['events'])))
    locked(lab,op)
def source_bindings():
    return {str(p):sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
def seal(lab,closure):
    lab=owned(lab);paths=set(map(Path,closure))|set(map(Path,source_bindings()))
    # Bind every historical helper that the retained engine can import.
    for folder in (HIST,BASE,HERE.parent/'step20c-targeted-diagnostic'):
        paths.update(p for p in folder.iterdir() if p.is_file())
    paths.update(p for p in (lab/'clients').iterdir() if p.is_file())
    paths.update([WLROOTS,OLD_LAB/'diagnostic/build-stage.json'])
    paths.update(p for p,_ in BINARIES.values())
    m=read(OLD_LAB/'diagnostic/build-stage.json');paths.add(Path(m['staging']['destdir'])/m['staging']['manifest'][0])
    durable(lab/'freeze.json',dict(scope=SCOPE,status='READY_FOR_REVIEW',plans=RUNS,files={str(p):sha(p) for p in sorted(paths)}),True)
def verify(lab):
    lab=owned(lab);f=read(lab/'freeze.json');r=read(lab/'review.json')
    need(f.get('scope')==SCOPE and f.get('plans')==RUNS and f.get('files') and all(sha(p)==h for p,h in f['files'].items()),'frozen exact bytes')
    need(all(f['files'].get(p)==h for p,h in source_bindings().items()),'new source closure')
    need(r.get('scope')==SCOPE and r.get('status')=='ACCEPTED' and r.get('independent') is True and r.get('read_only') is True and r.get('blockers')==[] and r.get('freeze_sha256')==sha(lab/'freeze.json') and r.get('files')==f['files'] and sha(r['report_file'])==r['report_sha256'],'independent exact byte review')
    return f
def begin(lab,rid):
    lab=owned(lab);need(rid in RUNS,'fixed run');verify(lab)
    # The token is consumed before preflight, including preflight failures.
    def op(s):
        need(rid not in s['runs'],'one-shot; no retry');limits=RUNS[rid]['limits']
        s['runs'][rid]=dict(planned=limits,reserved=dict.fromkeys(limits,0),consumed_ns=time.monotonic_ns(),freeze_sha256=sha(lab/'freeze.json'))
    locked(lab,op)
    p=read(lab/'preflight.json');need(p.get('scope')==SCOPE and p.get('freeze_sha256')==sha(lab/'freeze.json') and rid in p.get('authorized_runs',[]) and p.get('status')=='PASS' and p.get('evidence') and all(sha(x)==h for x,h in p['evidence'].items()),'durable bound preflight')
    v=RUNS[rid]['variant']
    if v=='C3':
        m=read(OLD_LAB/'diagnostic/build-stage.json');need(m['staging']['manifest']==['usr/bin/swayfx-mosaic'] and m['staging']['sha256']==C3_SHA,'C3 authoritative build-stage')
        binary=Path(m['staging']['destdir'])/m['staging']['manifest'][0];digest=C3_SHA
    else:need(v in BINARIES,'conditional diagnostics require separate reviewed identity');binary,digest=BINARIES[v]
    need(sha(binary)==digest and sha(WLROOTS)==WLROOTS_SHA,'exact binary/pair')
    for proc in Path('/proc').iterdir():
        if proc.name.isdigit():
            try:exe=(proc/'exe').resolve(strict=True)
            except (FileNotFoundError,PermissionError,ProcessLookupError):continue
            need(exe!=binary.resolve(),'same binary already running')
    (lab/'runs'/rid).mkdir(parents=True,exist_ok=False)
    return dict(binary=str(binary),binary_sha256=digest,wlroots=str(WLROOTS),wlroots_sha256=WLROOTS_SHA)
