"""Offline preparation and fail-closed independent review / exact-byte runtime gate."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time
import fcntl
from horizontal_adapter import BASE,REUSE,generate
import ledger

HERE=Path(__file__).resolve().parent
DEFAULT_LAB=Path('/home/fy59/swayfx-mosaic-overnight-mcolx0gq')
OLD_CLIENTS=Path('/home/fy59/swayfx-mosaic-static-nested-runtime-pvn0osxm/client-build')
PRISTINE=Path('/home/fy59/swayfx-mosaic-optimized-edge-a55yjb8n/pristine-build/sway/sway')
PRISTINE_SHA='8ac865481bc0487344210cd0e16d8e6c7655b29db887cd58ddc11b0ca22fe494'
WLROOTS=Path('/usr/lib/libwlroots-0.20.so').resolve()
PLANS={'C0':dict(chain=1,grab=2,click=4,capture=10,camera=0,transition=0,move=5),
       'C1':dict(chain=1,grab=2,click=4,capture=10,camera=0,transition=0,move=5),
       'C2':dict(chain=2,grab=4,click=8,capture=17,camera=2,transition=1,move=10)}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def require(ok,msg):
    if not ok:raise ValueError(msg)
def exclusive(p,data):
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as f:
        json.dump(data,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def durable(p,data):
    from importlib.util import spec_from_file_location,module_from_spec
    spec=spec_from_file_location('horizontal_support',BASE/'support.py');m=module_from_spec(spec);spec.loader.exec_module(m)
    m.durable(p,data)
def env():
    spec=__import__('importlib.util',fromlist=['spec_from_file_location']).spec_from_file_location('horizontal_support',BASE/'support.py')
    m=__import__('importlib.util',fromlist=['module_from_spec']).module_from_spec(spec);spec.loader.exec_module(m)
    return m.environment()

def binding_sources(auth):
    rows=auth['trace_sources'];require(all(sha(p)==h for p,h in rows.items()),'annotated trace source changed')
    return {Path(p).name:h for p,h in rows.items()}

def prepare(lab):
    lab=Path(lab).resolve();require(lab==DEFAULT_LAB,'only registered overnight lab')
    a=read(lab/'phase-a.json');require(a['status']=='PASS' and sha(a['binary']['path'])==a['binary']['sha256'],'phase A exact binary')
    require(sha(PRISTINE)==PRISTINE_SHA,'pristine binary identity')
    work=lab/'horizontal';work.mkdir();(work/'clients').mkdir()
    rows=[]
    names=['nested-client.c','pointer-daemon.c','static-reference.c','saved-client.c','xdg-shell-client.h','xdg-shell-protocol.c','virtual-pointer-client.h','virtual-pointer-protocol.c']
    for n in names:
        target=work/'clients'/n;shutil.copyfile(OLD_CLIENTS/n,target);rows.append(dict(source=str(OLD_CLIENTS/n),path=str(target),sha256=sha(target)))
    contract=read(BASE/'client-contract.json');require(sha(work/'clients/nested-client.c')==contract['adapted_nested_sha256'],'actual static_cross')
    for n,h in contract['protocols'].items():require(sha(work/'clients'/n)==h,'actual generated protocol')
    receipts=[]
    flags=subprocess.run(['pkg-config','--cflags','--libs','wayland-client'],capture_output=True,text=True,check=True).stdout.split()
    for name,sources in [('nested-client',['nested-client.c','xdg-shell-protocol.c']),('pointer-daemon',['pointer-daemon.c','virtual-pointer-protocol.c']),('static-reference',['static-reference.c','xdg-shell-protocol.c'])]:
        argv=['cc','-std=c17','-O2','-Wall','-Wextra',*[str(work/'clients'/s) for s in sources],'-o',str(work/'clients'/name),*flags]
        p=subprocess.run(argv,env=env(),capture_output=True,text=True,timeout=30)
        receipts.append(dict(argv=argv,exit=p.returncode,stdout=p.stdout,stderr=p.stderr,binary_sha256=sha(work/'clients'/name) if p.returncode==0 else None))
        require(p.returncode==0,'C17 client compilation')
    exclusive(work/'compile.json',dict(status='PASS',transfers=rows,commands=receipts,protocol_provenance=str(BASE/'client-contract.json'),client_execution='NOT RUN'))
    for case in PLANS:
        d=work/case;d.mkdir();(d/'results').mkdir()
        for name in ('nested-client','pointer-daemon','static-reference'):(d/name).symlink_to(work/'clients'/name)
        (d/'runner.py').write_text(generate(case))
    trace={str(lab/'mosaic-source/sway/desktop'/n):sha(lab/'mosaic-source/sway/desktop'/n) for n in ('output.c','transaction.c','xdg_shell.c')}
    scene=Path('/home/fy59/swayfx-mosaic-optimized-edge-a55yjb8n/scene0-build/libscenefx-0.5.so').resolve()
    exclusive(work/'identity.json',dict(status='PREPARED',lab=str(lab),phase_a_sha256=sha(lab/'phase-a.json'),
        annotated_binary=a['binary'],pristine=dict(path=str(PRISTINE),sha256=PRISTINE_SHA,scene_path=str(scene),scene_sha256=sha(scene)),
        wlroots=dict(path=str(WLROOTS),sha256=sha(WLROOTS)),trace_sources=trace,plans=PLANS,review='PENDING',runtime='NOT RUN'))
    print('HORIZONTAL=PREPARED_CLIENTS_COMPILED_RUNTIME_NOT_RUN')

def paths(lab):
    w=lab/'horizontal';ident=read(w/'identity.json')
    out=[p for p in HERE.iterdir() if p.is_file()]+[BASE/n for n in REUSE]+[BASE/'run.py',BASE/'client-contract.json']
    out+=[p for p in (w/'clients').iterdir() if p.is_file()]
    out+=[w/'compile.json',w/'identity.json',w/'offline-tests-repair-v1.json',w/'pristine-provenance.json',lab/'phase-a.json']
    out+=[w/c/'runner.py' for c in PLANS]+[Path(p) for p in ident['trace_sources']]
    out+=[Path(ident['annotated_binary']['path']),PRISTINE,WLROOTS,Path(ident['pristine']['scene_path'])]
    provenance=read(w/'pristine-provenance.json')
    out+=[Path(provenance['historical_build_receipt']),w/'provenance_check.py']
    out+=[Path(row['path']) for check in provenance['source_equivalence'] for row in check['files']]
    out+=[Path(row['source']) for row in read(w/'compile.json')['transfers']]
    out+=[w/'protocol-scanner.json',w/'offline-tests.json']
    out+=[Path(row[k]) for row in read(w/'protocol-scanner.json')['commands'] for k in ('protocol_xml','generated')]
    retained=Path('/home/fy59/swayfx-mosaic-static-nested-runtime-pvn0osxm')
    out+=[retained/p for p in ('results/standard-snapshot.json','results/standard-offline-observation.json',
        'run/compositor.log','run/E2.log','run/standard-H1.png','run/standard-H2.png')]
    out+=[lab/'swayfx-source/sway/ipc-json.c',w/'offline-tests-repair-attempt1.json']
    out+=[Path(shutil.which(name)).resolve() for name in ('swaymsg','grim')]
    return sorted(set(out))

def seal(lab):
    require(read(lab/'horizontal/offline-tests-repair-v1.json')['status']=='PASS','executed offline tests required')
    exclusive(lab/'horizontal/freeze.json',dict(status='READY_FOR_REVIEW',files={str(p):sha(p) for p in paths(lab)},plans=PLANS))

def verify_review(lab,review=True):
    w=lab/'horizontal';f=read(w/'freeze.json')
    require(f['status']=='READY_FOR_REVIEW' and f['files']=={str(p):sha(p) for p in paths(lab)} and f['plans']==PLANS,'complete final frozen bytes')
    ident=read(w/'identity.json');a=read(lab/'phase-a.json')
    require(a['status']=='PASS' and ident['phase_a_sha256']==sha(lab/'phase-a.json') and ident['annotated_binary']==a['binary'],'exact phase A')
    require(ident['pristine']['sha256']==PRISTINE_SHA and sha(PRISTINE)==PRISTINE_SHA,'pristine bytes')
    provenance=read(w/'pristine-provenance.json');require(provenance['status']=='PASS','pristine source equivalence')
    require(all(sha(row['path'])==row['sha256'] for check in provenance['source_equivalence'] for row in check['files']),'pristine sources actual frozen equality')
    require(read(w/'offline-tests-repair-v1.json')['status']=='PASS','executed tests')
    require(read(w/'protocol-scanner.json')['status']=='PASS','scanner provenance')
    if review:
        r=read(w/'review.json')
        require(r.get('status')=='ACCEPTED' and r.get('independent') is True and r.get('read_only') is True and r.get('blockers')==[] and r.get('scope')=='OVERNIGHT_HORIZONTAL_FINAL_BYTES','genuine independent acceptance')
        require(r.get('freeze_sha256')==sha(w/'freeze.json') and r.get('files')==f['files'],'review final bindings')
        require(sha(r['report_file'])==r['report_sha256'],'review report bytes')
    return ident

def preflight(lab,case,review=True):
    require(lab==DEFAULT_LAB and case in PLANS and not sys.flags.optimize,'registered lab/case assertions')
    require(lab.stat().st_uid==os.getuid() and stat.S_IMODE(lab.stat().st_mode)==0o700,'owned lab 0700')
    ident=verify_review(lab,review)
    w=lab/'horizontal'/case
    require(not (w/'run').exists() and not (w/'consumed.json').exists(),'no retry or existing runtime')
    require(not any(stat.S_ISSOCK(p.lstat().st_mode) for p in (lab/'horizontal').rglob('*')),'no stale sockets')
    budget=read(lab/'budget.json');require(case not in budget['runs'] and budget['used']['run']<18 and budget['campaign_used']['C']<3,'unspent global run')
    require(budget['used']['capture']+PLANS[case]['capture']<=220,'available planned PNG budget')
    # Controls are scientific comparison prerequisites, not invented dispatch vetoes.
    # Shared-fixture defects must be reviewed before proceeding; no status is transferred.
    # No compositor/client process exists in this fresh per-case directory.
    for proc in Path('/proc').iterdir():
        if proc.name.isdigit():
            try:exe=(proc/'exe').resolve(strict=True)
            except (FileNotFoundError,PermissionError,ProcessLookupError):continue
            require(exe!=Path(ident['annotated_binary']['path']),'annotated binary already running')
    binary=ident['pristine'] if case=='C0' else ident['annotated_binary']
    require(sha(binary['path'])==binary['sha256'] and sha(ident['wlroots']['path'])==ident['wlroots']['sha256'],'binary/wlroots preflight')
    return dict(binary=binary['path'],binary_sha256=binary['sha256'],wlroots_sha256=ident['wlroots']['sha256'],trace_sources=ident['trace_sources'],pristine=ident['pristine'])

def begin_run():
    p=argparse.ArgumentParser();p.add_argument('lab',type=Path);p.add_argument('case',choices=PLANS);a=p.parse_args()
    lab=a.lab.resolve();case=a.case;w=lab/'horizontal'/case
    auth=preflight(lab,case)
    exclusive(w/'consumed.json',dict(case=case,freeze_sha256=sha(lab/'horizontal/freeze.json'),at_ns=time.monotonic_ns()))
    ledger.reserve(lab/'budget.json','run',campaign='C',run_id=case,duration_s=150)
    exclusive(w/'actions.json',dict(planned=PLANS[case],reserved=dict.fromkeys(PLANS[case],0),events=[]))
    return lab,case,w,auth

def debit(lab,case,w,*kinds):
    with (w/'actions.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);state=read(w/'actions.json')
        require(bool(kinds) and all(k in PLANS[case] for k in kinds),'known actions')
        require(all(state['reserved'][k]+kinds.count(k)<=state['planned'][k] for k in kinds),'local action budget exhausted')
        for k in kinds:
            if k=='capture':ledger.reserve(lab/'budget.json','capture',run_id=case)
            state['reserved'][k]+=1;state['events'].append(dict(kind=k,ns=time.monotonic_ns(),sequence=len(state['events'])))
        durable(w/'actions.json',state)

def finish_run(lab,case,w):
    verify_review(lab);state=read(w/'actions.json');events=[json.loads(s) for s in (w/'run/events.jsonl').read_text().splitlines()]
    consumed=dict(capture=sum(e['kind']=='capture' for e in events),click=sum(e['kind']=='injection' and e['action']!='move' for e in events),
        move=sum(e['kind']=='injection' for e in events),grab=sum(e['kind']=='injection' and e.get('grab',False) for e in events))
    state['consumed_observed']=consumed;durable(w/'actions.json',state)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','seal','preflight']);p.add_argument('lab',type=Path);p.add_argument('--case',choices=PLANS,default='C0');a=p.parse_args()
    if a.action=='prepare':prepare(a.lab)
    elif a.action=='seal':seal(a.lab)
    else:print(json.dumps(preflight(a.lab.resolve(),a.case),indent=2))
