#!/usr/bin/env python3
"""Prospective E2 handoff, derived from static-nested-runtime/handoff.py.

WHY: historical ACCEPTED cannot sign changed runner bytes.
CONTRACT: genuine independent review binds final sources, receipts and owner.
INVARIANT: preflight reads only; launch consumption is exclusive and durable.
"""
import ast
import json
import os
from pathlib import Path
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
from support import sha,verify,environment
from model import require
from ledger import LIMITS,valid
from transition import source_bindings,SOURCE_FILES

HERE=Path(__file__).resolve().parent
SOURCE_ROOT=Path('/home/fy59/Documents/Development/swayfx-mosaic/tooling/probes/step20c-static-e2-completion')
TICKET='SWAYFX_MOSAIC_STEP20C_E2_COMPLETION_AND_PRIVATE_INTEGRATION_BATCH_V1'
REGISTRY=Path('/home/fy59/swayfx-mosaic-e2-completion-v1.owner')
REGISTRATION=REGISTRY.with_suffix('.registration.json')
SPENT=REGISTRY.with_suffix('.launch-consumed.json')
OLD_LAB=Path('/home/fy59/swayfx-mosaic-static-nested-runtime-pvn0osxm')
BINARY=Path('/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/stage-static/usr/bin/swayfx-mosaic')
BINARY_SHA='f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b'
BUILD_ID='942db64269640778ee433e5970ba1100bc60f94c'
WLROOTS=Path('/usr/lib/libwlroots-0.20.so')
WLROOTS_SHA='7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837'
MARKER='E2_COMPLETION_OFFLINE=READY_FOR_REVIEW'


def read(path):return json.loads(Path(path).read_text())


def exclusive(path,data):
    path=Path(path)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as out:
        out.write(data if isinstance(data,str) else json.dumps(data,indent=2)+'\n');out.flush();os.fsync(out.fileno())
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)


def regular(path,mode=None):
    p=Path(path);s=p.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid(),'owned-regular-file:'+str(p))
    if mode is not None:require(stat.S_IMODE(s.st_mode)==mode,'file-mode:'+str(p))


def copy_exact(source,dest):
    regular(source)
    with Path(source).open('rb') as src,Path(dest).open('xb') as out:
        shutil.copyfileobj(src,out);out.flush();os.fsync(out.fileno())
    Path(dest).chmod(stat.S_IMODE(Path(source).stat().st_mode))
    require(sha(source)==sha(dest),'copy-exact')
    return dict(source=str(source),destination=str(dest),sha256=sha(source))


def source_map():return {p.name:sha(p) for p in SOURCE_ROOT.iterdir() if p.is_file()}


def immutable_paths(lab):
    paths=[p for root in ('fixture','client-source','offline') for p in (lab/root).iterdir() if p.is_file()]
    paths += [lab/n for n in ('swayfx-mosaic','nested-client','pointer-daemon','static-reference','campaign-owner')]
    paths += [lab/'results/binary-identity.json',*[lab/'raw'/(name+'.json') for name in ('ELF','symbols','relocations')],BINARY,WLROOTS.resolve(),REGISTRY]
    paths += [Path(p) for p in SOURCE_FILES.values()]
    paths += [p for p in SOURCE_ROOT.iterdir() if p.is_file()]
    require(len(paths)==len(set(paths)),'unique-manifest-paths')
    return sorted(paths)


def prepare(offline):
    from gate import validate_gate
    offline=Path(offline).resolve();gate=validate_gate(offline/'offline-gate.json')
    require(not any(p.exists() for p in (REGISTRY,REGISTRATION,SPENT)),'ticket-already-registered')
    require(sha(BINARY)==BINARY_SHA and sha(WLROOTS)==WLROOTS_SHA,'binary-wlroots-identities')
    lab=Path(tempfile.mkdtemp(prefix='swayfx-mosaic-e2-completion-',dir='/home/fy59'));lab.chmod(0o700)
    for n in ('results','raw','fixture','client-source','offline'):(lab/n).mkdir()
    token=secrets.token_hex(32)
    exclusive(REGISTRY,str(lab)+'\n');exclusive(lab/'campaign-owner',str(REGISTRY)+'\n')
    transfers=[]
    for p in sorted(HERE.iterdir()):
        if p.is_file():transfers.append(copy_exact(p,lab/'fixture'/p.name))
    for name in ('offline-gate.json','test-receipts.json','replay.json','source-audit.json'):
        transfers.append(copy_exact(offline/name,lab/'offline'/name))
    for n in ('swayfx-mosaic','nested-client','pointer-daemon','static-reference'):
        transfers.append(copy_exact(BINARY if n=='swayfx-mosaic' else OLD_LAB/n,lab/n));regular(lab/n,0o755)
    # Actual prepared static_cross sources and generated protocols, not rebuilt.
    for p in sorted((OLD_LAB/'client-build').iterdir()):
        if p.suffix in ('.c','.h'):transfers.append(copy_exact(p,lab/'client-source'/p.name))
    contract=read(HERE/'client-contract.json')
    require(sha(lab/'client-source/nested-client.c')==contract['adapted_nested_sha256'],'actual-static-cross-source')
    for name,digest in contract['protocols'].items():require(sha(lab/'client-source'/name)==digest,'actual-protocol-source')
    identity={}
    for label,argv in [('ELF',['readelf','-hW','-nW','-dW',str(lab/'swayfx-mosaic')]),
                       ('symbols',['nm',str(lab/'swayfx-mosaic')]),('relocations',['ldd','-r',str(lab/'swayfx-mosaic')])]:
        r=subprocess.run(argv,env=environment(),capture_output=True,text=True,timeout=30)
        exclusive(lab/'raw'/(label+'.json'),dict(argv=argv,exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
        require(r.returncode==0,'identity-command');identity[label]=r.stdout
    require(BUILD_ID in identity['ELF'] and 'ELF64' in identity['ELF'] and
            all(s not in identity['ELF'] for s in ('libscenefx','(RPATH)','(RUNPATH)')),'ELF-static-contract')
    require(all(' T '+n in identity['symbols'] for n in ('wlr_scene_tree_set_clip','wlr_scene_tree_get_clip')),'clip-symbols')
    require(str(WLROOTS.resolve()) in identity['relocations'] and
            all(s not in identity['relocations'] for s in ('libscenefx','undefined symbol','not found')),'resolved-libraries')
    exclusive(lab/'results/binary-identity.json',dict(status='PASS',build_id=BUILD_ID,binary_sha256=BINARY_SHA,
        wlroots_sha256=WLROOTS_SHA,raw={n:sha(lab/'raw'/(n+'.json')) for n in identity}))
    exclusive(lab/'results/fixture-freeze-sha256.txt',''.join(sha(p)+'  '+str(p)+'\n' for p in immutable_paths(lab)))
    frozen=verify(lab/'results/fixture-freeze-sha256.txt')
    registration=dict(ticket=TICKET,lab=str(lab),owner_registry=str(REGISTRY),uid=os.getuid(),token=token,
        fixture_sha256=frozen['sha256'],binary=str(BINARY),binary_sha256=BINARY_SHA,wlroots_sha256=WLROOTS_SHA)
    exclusive(REGISTRATION,registration);exclusive(lab/'results/registration.json',registration)
    auth={**registration,'registered_lab':str(lab),'scope':'one-new-static-e2-completion-headless-run','explicit_user_authorization':True}
    exclusive(lab/'results/authorization.json',auth)
    exclusive(lab/'results/budget.json',dict(limits=LIMITS,used=dict.fromkeys(LIMITS,0),events=[]))
    exclusive(lab/'results/offline-gate.json',dict(marker=MARKER,status='READY_FOR_REVIEW',fixture_sha256=frozen['sha256'],
        offline_gate_sha256=sha(lab/'offline/offline-gate.json')))
    exclusive(lab/'results/runtime-handoff.json',dict(status='PREPARED_FOR_INDEPENDENT_REVIEW',ticket=TICKET,
        lab=str(lab),fixture=frozen,transfers=transfers,source_sha256=source_map(),source_contract=source_bindings(),
        gate_sha256=sha(lab/'offline/offline-gate.json'),authorization_sha256=sha(lab/'results/authorization.json'),
        registration_sha256=sha(REGISTRATION),historical_review='does not accept changed runner',run_reserved=False))
    print('LAB='+str(lab));return lab


def preflight(lab,authorization,review=True,consumed=False):
    """Read-only. review=False is prospective preparation, never dispatch."""
    from gate import validate_gate
    lab=Path(lab).resolve();authorization=Path(authorization)
    require(not sys.flags.optimize,'assertions-required')
    require(lab!=OLD_LAB and lab.name.startswith('swayfx-mosaic-e2-completion-'),'fresh-ticket-lab')
    require(lab.stat().st_uid==os.getuid() and stat.S_IMODE(lab.stat().st_mode)==0o700,'lab-owner-mode')
    for p in (REGISTRY,REGISTRATION,lab/'campaign-owner',authorization):regular(p,0o600)
    require(REGISTRY.read_text().strip()==str(lab) and (lab/'campaign-owner').read_text().strip()==str(REGISTRY),'exclusive-owner')
    auth=read(authorization);registration=read(REGISTRATION)
    require(registration==read(lab/'results/registration.json'),'durable-registration-copy')
    require(auth=={**registration,'registered_lab':str(lab),'scope':'one-new-static-e2-completion-headless-run',
                   'explicit_user_authorization':True},'exact-authorization')
    require(auth['ticket']==TICKET and auth['lab']==str(lab) and auth['owner_registry']==str(REGISTRY)
        and auth['uid']==os.getuid() and len(auth['token'])==64,'ticket-lab-token')
    require(auth['binary']==str(BINARY) and auth['binary_sha256']==BINARY_SHA and auth['wlroots_sha256']==WLROOTS_SHA,
            'authorized-identities')
    require(sha(BINARY)==sha(lab/'swayfx-mosaic')==BINARY_SHA and sha(WLROOTS)==WLROOTS_SHA,'actual-identities')
    require(not (lab/'run').exists() and not (lab/'run.lock').exists(),'unconsumed-runtime')
    require(not any(stat.S_ISSOCK(p.lstat().st_mode) for p in lab.rglob('*')),'no-existing-sockets')
    manifest=lab/'results/fixture-freeze-sha256.txt'
    frozen=verify(manifest)
    require(manifest.read_text()==''.join(sha(p)+'  '+str(p)+'\n' for p in immutable_paths(lab)),'complete-exact-manifest')
    require({p.name:sha(p) for p in (lab/'fixture').iterdir() if p.is_file()}==source_map(),'installed-final-fixture')
    require(auth['fixture_sha256']==frozen['sha256'],'authorization-manifest')
    handoff=read(lab/'results/runtime-handoff.json')
    require(handoff['ticket']==TICKET and handoff['lab']==str(lab) and handoff['fixture']==frozen and
            handoff['source_sha256']==source_map() and handoff['source_contract']==source_bindings() and
            handoff['authorization_sha256']==sha(authorization) and handoff['registration_sha256']==sha(REGISTRATION),
            'handoff-final-bindings')
    require(bool(handoff['transfers']) and len({row['destination'] for row in handoff['transfers']})==len(handoff['transfers']),'nonempty-unique-transfers')
    for row in handoff['transfers']:require(sha(row['source'])==sha(row['destination'])==row['sha256'],'transfer-changed')
    gate=validate_gate(lab/'offline/offline-gate.json')
    require(handoff['gate_sha256']==sha(lab/'offline/offline-gate.json'),'handoff-gate-binding')
    require(read(lab/'results/offline-gate.json')==dict(marker=MARKER,status='READY_FOR_REVIEW',fixture_sha256=frozen['sha256'],
        offline_gate_sha256=sha(lab/'offline/offline-gate.json')),'derived-gate')
    budget=valid(read(lab/'results/budget.json'));require(not any(budget['used'].values()) and not budget['events'],'ledger-unreserved')
    identity=read(lab/'results/binary-identity.json')
    require(identity['status']=='PASS' and identity['build_id']==BUILD_ID and identity['binary_sha256']==BINARY_SHA
            and identity['wlroots_sha256']==WLROOTS_SHA,'identity-receipt')
    for n,digest in identity['raw'].items():require(sha(lab/'raw'/(n+'.json'))==digest,'raw-identity-binding')
    expected_spent=dict(ticket=TICKET,lab=str(lab),token=auth['token'],fixture_sha256=frozen['sha256'],authorization_sha256=sha(authorization))
    if consumed:require(SPENT.exists() and read(SPENT)==expected_spent,'runner-exact-consumption')
    else:require(not SPENT.exists(),'ticket-launch-already-consumed')
    if review:
        reviewed=read(lab/'results/handoff-review.json')
        require(reviewed.get('status')=='ACCEPTED' and reviewed.get('independent') is True and reviewed.get('read_only') is True
                and reviewed.get('scope')=='STATIC_E2_COMPLETION_FINAL_BYTES' and reviewed.get('blockers')==[],
                'genuine-independent-review-required')
        require(reviewed['fixture_sha256']==frozen['sha256'] and reviewed['source_sha256']==source_map()
                and reviewed['runtime_handoff_sha256']==sha(lab/'results/runtime-handoff.json')
                and reviewed['authorization_sha256']==sha(authorization) and reviewed['registration_sha256']==sha(REGISTRATION)
                and reviewed['gate_sha256']==sha(lab/'offline/offline-gate.json'),'review-final-bindings')
        regular(reviewed['report_file']);require(sha(reviewed['report_file'])==reviewed['report_sha256'],'review-report-bytes')
    return dict(status='PASS',ticket=TICKET,lab=str(lab),fixture=frozen,token=auth['token'],
                review='ACCEPTED' if review else 'PENDING_INDEPENDENT_REVIEW',run_reserved=False)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','preflight']);p.add_argument('path',type=Path);a=p.parse_args()
    if a.action=='prepare':prepare(a.path)
    else:
        result=preflight(a.path,a.path/'results/authorization.json');exclusive(a.path/'results/preflight.json',result)
        print('E2_COMPLETION_PREFLIGHT=PASS')
