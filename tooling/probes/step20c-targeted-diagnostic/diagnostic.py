"""EXPERIMENTAL optional C3; explicit extension outside the frozen core."""
import contextlib,copy,fcntl,json,os,re,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
CORE=HERE.parent/'step20c-targeted'
sys.path.insert(0,str(CORE))
import gate,plans
from validators import held_configure,native_pairs
from geometry import need,intersection
from engine import Session,workspace,nodes
SPEC=copy.deepcopy(plans.RUNS['saved-A'])
SPEC.update(id='saved-diagnostic-A',case='saved-diagnostic',variant='diagnostic',status='EXPERIMENTAL',ceilings=['atomic generation NOT PROVEN','complete damage NOT PROVEN','GPU completion NOT PROVEN','STEP20C NEXT; production multi-output NOT YET SUPPORTED'])
SPEC['limits'].update(capture=10,click=2,camera=1)
SCOPE='STEP20C_SAVED_DIAGNOSTIC_V1'

@contextlib.contextmanager
def registration(lab,verify=True):
    """Register only in this process, after/before original byte verification.

    The persistent registration is mandatory for subsequent final validation.
    This does not transfer the original review to the new fixed fourteenth run.
    """
    lab=Path(lab)
    if verify:gate.verify(lab)
    need(SPEC['id'] not in plans.RUNS,'duplicate registration')
    persisted=gate.read(lab/'diagnostic-registration.json')
    need(persisted==dict(scope=SCOPE,spec=SPEC),'fixed persisted registration')
    plans.RUNS[SPEC['id']]=SPEC
    try:yield
    finally:
        del plans.RUNS[SPEC['id']]
        if verify:gate.verify(lab)

def final_budget(lab):
    with registration(lab):return gate.validate(gate.read(Path(lab)/'budget.json'))

def reserve_build_stage(lab,kind):
    """Durable one-way reservation, only after independent preparation review."""
    lab=gate.owned(lab);need(kind in ('build','stage'),'fixed build/stage kind')
    verify_preparation(lab)
    with registration(lab):
        state=gate.validate(gate.read(lab/'budget.json'))
        need(set(state['runs'])==set(plans.RUNS)-{SPEC['id']},'thirteen original tokens consumed before diagnostic build/stage')
    folder=lab/'diagnostic'
    with (folder/'budget.lock').open('a+') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        path=folder/'budget.json'
        state=gate.read(path) if path.exists() else dict(scope=SCOPE,events=[])
        need(state['scope']==SCOPE and all(e['kind'] in ('build','stage') for e in state['events']),'diagnostic budget schema')
        need(not any(e['kind']==kind for e in state['events']),'no build/stage retry')
        if kind=='stage':need([e['kind'] for e in state['events']]==['build'],'build before stage')
        token=folder/(kind+'.token.json')
        gate.durable(token,dict(scope=SCOPE,kind=kind,ns=time.monotonic_ns()),True)
        state['events'].append(dict(kind=kind,ns=time.monotonic_ns()))
        gate.durable(path,state,not path.exists())
    return state

def bindings(lab,binary=False):
    lab=Path(lab);diag=lab/'diagnostic'
    paths=[p for p in HERE.iterdir() if p.is_file()]
    paths += [diag/'offline.json',diag/'offline.stdout',diag/'syntax-check.json',lab/'freeze.json',lab/'review.json',lab/'diagnostic-registration.json',diag/'source-provenance.json',plans.HIST/'scene-build/libscenefx-0.5.a',plans.HIST/'scene-build/meson-uninstalled/scenefx-0.5-uninstalled.pc',plans.WLROOTS]
    paths += [p for p in (diag/'mosaic-source').rglob('*') if p.is_file()]
    paths += [p for p in (diag/'diagnostic-source').rglob('*') if p.is_file()]
    if (diag/'correction-provenance.json').exists():paths += [diag/'correction-provenance.json']
    paths += [p for p in (lab/'clients').iterdir() if p.is_file()]
    if binary:paths += [diag/'stage/usr/bin/swayfx-mosaic']
    return {str(p):gate.sha(p) for p in sorted(set(paths))}

def verify_preparation(lab):
    gate.verify(lab);diag=Path(lab)/'diagnostic'
    f=gate.read(diag/'preparation-freeze.json');r=gate.read(diag/'preparation-review.json')
    need(f.get('scope')==SCOPE and f.get('spec')==SPEC and f.get('files')==bindings(lab),'preparation exact bytes')
    need(r.get('scope')==SCOPE and r.get('status')=='ACCEPTED' and r.get('independent') is True and r.get('blockers')==[] and r.get('freeze_sha256')==gate.sha(diag/'preparation-freeze.json') and r.get('files')==f['files'] and gate.sha(r['report_file'])==r['report_sha256'],'independent preparation review')

def verify_runtime(lab):
    gate.verify(lab);diag=Path(lab)/'diagnostic'
    f=gate.read(diag/'runtime-freeze.json');r=gate.read(diag/'runtime-review.json')
    need(f.get('scope')==SCOPE and f.get('spec')==SPEC and f.get('files')==bindings(lab,True),'runtime exact bytes')
    need(r.get('scope')==SCOPE and r.get('status')=='ACCEPTED' and r.get('independent') is True and r.get('blockers')==[] and r.get('freeze_sha256')==gate.sha(diag/'runtime-freeze.json') and r.get('files')==f['files'] and gate.sha(r['report_file'])==r['report_sha256'],'independent runtime review')
    b=gate.read(diag/'budget.json');need(b['scope']==SCOPE and [e['kind'] for e in b['events']]==['build','stage'],'exactly one build/stage')
    return diag/'stage/usr/bin/swayfx-mosaic'

def pending_geometry(initial,pending,owner_id,workspace_id,before,after,prior,request_ns):
    oldws=workspace(initial['tree'],'1');ws=workspace(pending['tree'],'1')
    need(oldws['id']==ws['id']==workspace_id and ws['output']==oldws['output']=='HEADLESS-1' and ws['layout']==oldws['layout']=='mosaic','same requested workspace')
    need('gaps' not in ws,'IPC gaps field is absent in audited source')
    old=next(n for n in nodes(oldws) if n['id']==owner_id)
    owners=[n for n in nodes(ws) if n['id']==owner_id];need(len(owners)==1,'same owner ancestry')
    target=owners[0];need(target['pid']==old['pid'] and target['app_id']==old['app_id']=='org.mosaic.SavedBufferProbe','same actual client')
    a=oldws['rect'];b=ws['rect'];need([b[k] for k in ('x','y','width','height')]==[a['x']+30,a['y']+30,a['width']-60,a['height']-60],'requested workspace rect changed by runtime gaps30')
    proof=held_configure(before,after,prior)
    need(proof['ns']>request_ns and proof['requested_size']==[target['window_rect']['width'],target['window_rect']['height']],'held wire after command matches requested dimensions')
    need(proof['initial_size']==[old['window_rect']['width'],old['window_rect']['height']],'initial applied dimensions')
    return dict(held=proof,workspace=ws,owner=target)

def records(text,tag):
    return [dict(re.findall(r'(\w+)=([^\s]+)',l),raw=l) for l in text.splitlines() if tag+' ' in l]

def saved_identity(text,owner,creation_after,require_destroy=False):
    trees=[r for r in records(text,'SD_TREE') if r['owner']==str(owner) and int(r['ns'])>creation_after]
    need(len(trees)==1 and trees[0]['saved_enabled']=='1' and trees[0]['content_enabled']=='0','unique actual saved owner tree')
    tree=trees[0]['tree']
    # WHY CONTRACT INVARIANT: addresses are labels, so reused/old trees or nodes
    # cannot prove this command's saved copies or this owner's activation.
    need(len([r for r in records(text,'SD_TREE') if r['tree']==tree])==1,'unique owner/tree activation')
    created=[r for r in records(text,'SD_CREATE') if r['tree']==tree]
    need(created,'actual saved copies')
    rows=[]
    for c in created:
        node=c['node']
        need(creation_after<int(c['ns'])<int(trees[0]['ns']),'actual creation after command before activation')
        need(len([r for r in records(text,'SD_CREATE') if r['node']==node])==1,'unique unreused saved node')
        need(node!=c['source_node'] and c['source'] not in ('(nil)','0x0'),'distinct saved/source scene identities')
        need(c['parent']==trees[0]['parent'],'actual saved parent')
        samples=[r for r in records(text,'SD_SAMPLE') if r['node']==node]
        draws=[r for r in records(text,'OPT_BUFFER_DRAW') if r['node']==node]
        need(samples and draws,'actual saved sample and native draw')
        dead=[r for r in records(text,'SD_NODE_DESTROY') if r['node']==node]
        need(len(dead)<=1,'unique saved node destruction')
        if require_destroy:need(len(dead)==1,'saved node removed naturally')
        for s in samples:
            need(s['source']==c['source'] and s['enabled']=='1' and s['node_enabled']=='1' and int(s['ns'])>int(trees[0]['ns']),'same live saved source after activation')
            need(not dead or int(s['ns'])<int(dead[0]['ns']),'sample after node destruction')
            same=[d for d in draws if d['output']==s['output'] and int(trees[0]['ns'])<int(d['ns'])<=int(s['ns'])]
            need(same,'same native node/output draw before sample')
            draw=same[-1]
            need(draw['global']==s['global'] and list(map(int,draw['dest'].split('x')))==list(map(int,s['dest'].split(','))),'native draw and saved sample geometry agree')
            need(draw['buffer'] in (c['source'],'(nil)'),'native draw source buffer identity or cleared texture source')
            ancestors=[a for a in records(text,'SD_ANCESTOR') if a['node']==node and a['output']==s['output'] and a.get('sample_ns')==s['ns']]
            need(ancestors,'applied ancestor clip sample')
            xy=list(map(int,s['global'].split(',')));dest=list(map(int,s['dest'].split(',')));bbox=[*xy,*dest]
            viewport=list(map(int,s['viewport'].split(',')));visible=intersection(bbox,viewport)
            for a in ancestors:
                if a['clip_valid']=='1':
                    pos=list(map(int,a['global'].split(',')));clip=list(map(int,a['clip'].split(',')));visible=intersection(visible,[pos[0]+clip[0],pos[1]+clip[1],*clip[2:]])
            dbox=list(map(int,draw['draw'].split(',')))
            # SceneFX native draw extents are output-buffer coordinates. Fixed
            # C3 normal scale1 maps these directly to logical viewport space.
            drawn=[dbox[0]+viewport[0],dbox[1]+viewport[1],dbox[2]-dbox[0],dbox[3]-dbox[1]]
            need(intersection(drawn,visible)==drawn and drawn[2]>0 and drawn[3]>0,'native saved draw contained by measured applied intersection')
            need(s['output']=='HEADLESS-1' and visible[2]>0 and visible[3]>0 and bbox[0]<0<bbox[0]+bbox[2],'actual saved target crossing and H1 intersection')
        for d in draws:need(not dead or int(d['ns'])<int(dead[0]['ns']),'native draw after node destruction')
        releases=[r for r in records(text,'SD_RELEASE') if r['node']==node];destroyed=[r for r in records(text,'SD_BUFFER_DESTROY') if r['node']==node]
        need(len(destroyed)<=1,'unique source destruction')
        need(all(int(r['ns'])>int(c['ns']) for r in releases+destroyed),'source lifecycle after saved creation')
        need(not destroyed or all(int(r['ns'])<int(destroyed[0]['ns']) for r in releases),'release after source destroy')
        for sample in samples:
            gone=destroyed and int(destroyed[0]['ns'])<int(sample['ns'])
            need(sample['live_source'] in ('(nil)','0x0') if gone else sample['live_source']==c['source'],'source pointer cleared after buffer destruction')
        need(all(r['source']==c['source'] and r.get('gpu_complete')=='NOT_PROVEN' for r in releases+destroyed),'native release is not GPU proof')
        rows.append(dict(create=c,samples=samples,draws=draws,node_destroy=dead,release=releases,buffer_destroy=destroyed))
    return dict(tree=trees[0],nodes=rows,gpu_completion='NOT PROVEN',cpu_lifetime='signal observations only; no retained references')


def saved_removal(text,identity,before_ns):
    """Exact natural-timeout removal; also used on final/post-close logs.

    before_ns is the first live-capture boundary, never the runner's timeout
    observation. The native timeout callback destroys nodes synchronously.
    """
    lines=text.splitlines();tree=identity['tree'];created=identity['nodes']
    def position(row):
        hits=[i for i,l in enumerate(lines) if l==row['raw']]
        need(len(hits)==1,'unique raw native record position')
        return hits[0]
    activation=position(tree)
    # WHY CONTRACT INVARIANT: the audited single queued transaction emits its
    # unmodified timeout line before applying/removing saved buffers. No native
    # ns exists on that line; raw order proves causality, not GPU completion.
    timeouts=[i for i,l in enumerate(lines) if i>activation and re.search(r'Transaction .*timed out \(\d*[1-9]\d* waiting\)',l)]
    need(len(timeouts)==1,'unique natural timeout after target activation')
    removes=[r for r in records(text,'SD_REMOVE') if r['tree']==tree['tree']]
    need(len(removes)==1,'exact saved tree removal')
    remove=removes[0]
    need(remove['owner']==tree['owner'] and remove['content']==tree['content'],'exact removed owner/content')
    need(timeouts[0]<position(remove),'tree removal after native timeout')
    need(int(tree['ns'])<int(remove['ns'])<before_ns,'tree removed before first live capture/close')
    dead=[]
    for node in created:
        c=node['create'];matches=[r for r in records(text,'SD_NODE_DESTROY') if r['node']==c['node']]
        need(len(matches)==1,'exact measured saved node destroyed')
        r=matches[0]
        need(r['source']==c['source'],'destroyed saved source identity')
        need(position(remove)<position(r),'SD_REMOVE precedes synchronous node destruction')
        need(int(c['ns'])<int(remove['ns'])<=int(r['ns'])<before_ns,'target destruction in natural removal window')
        dead.append(r)
    return dict(timeout_raw=lines[timeouts[0]],timeout_line=timeouts[0],remove=remove,nodes=dead,before_ns=before_ns,gpu_completion='NOT PROVEN')
