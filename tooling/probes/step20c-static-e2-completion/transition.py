"""Observed applied transition; EXPERIMENTAL, no atomic generation claim.

WHY: an accepted layout request can precede the transaction applying it.
CONTRACT: keep the old state, then require two coherent standard observations.
INVARIANT: no first-row discard, last-row shortcut or pending-as-applied proof.
PI_POPUP has no owner field: uniqueness + exact live XDG hierarchy + IPC ancestry
provide bounded correlation only. The actual private output.c reads current.
"""
import json
import re
from model import require
from predicates import protocol
from ipc_predicates import ancestry,nodes

SOURCE_FILES = {
    'output.c': '/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/mosaic-source/sway/desktop/output.c',
    'transaction.c': '/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/mosaic-source/sway/desktop/transaction.c',
    'xdg_shell.c': '/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/mosaic-source/sway/desktop/xdg_shell.c',
}

def fields(line):
    return dict(re.findall(r'(\w+)=([^\s]+)', line))


def observed_epochs(text, output, start_ns, end_ns):
    """Group the exact commit callback's ordered SCENE/OWNER/POPUP records.

    Other output callbacks may contain the same global popup tree. We examine
    all callbacks for the selected output and never filter by desired owner.
    """
    epochs=[]; active=None; last=0
    for line in text.splitlines():
        if not re.search(r'\bPI_(?:OUTPUT_COMMIT|SCENE|OWNER|POPUP)\b',line):continue
        f=fields(line)
        if f.get('output')!=output:continue
        ns=int(f['ns'])
        if not start_ns<=ns<=end_ns:continue
        require(ns>last,'trace-monotonic-order');last=ns
        if 'PI_OUTPUT_COMMIT ' in line:
            active={'commit':f,'scene':None,'owners':[],'roots':[],'raw':[line]};epochs.append(active)
        else:
            require(active is not None,'trace-without-commit')
            active['raw'].append(line)
            if 'PI_SCENE ' in line:
                require(active['scene'] is None,'duplicate-scene');active['scene']=f
            elif 'PI_OWNER ' in line:active['owners'].append(f)
            else:active['roots'].append(f)
    require(bool(epochs),'applied-observations-missing')
    return epochs


def transition_window_start(trace,output,root_id,owner_id,workspace_id,mapped_after_ns,request_ns):
    """Select an explicitly coherent mapped A/B Mosaic callback before request.

    Earlier no-popup callbacks belong to opening evidence, not the transition.
    We require a complete commit header + current scene + owner + unique root;
    no unconditional trace-row deletion is allowed.
    """
    epochs=observed_epochs(trace,output,0,request_ns)
    candidates=[]
    for epoch in epochs:
        c,s,roots=epoch['commit'],epoch['scene'],epoch['roots']
        if int(c['ns'])<mapped_after_ns:continue
        owners=[o for o in epoch['owners'] if o.get('id')==str(owner_id)]
        if s and s.get('workspace')==str(workspace_id) and s.get('layout')=='5' and s.get('clip_valid')=='1' and \
                len(owners)==1 and owners[0].get('scene_valid')=='1' and len(roots)==1 and \
                roots[0].get('tree')==root_id and roots[0].get('enabled')=='1' and roots[0].get('clip_valid')=='1':
            candidates.append(int(c['ns']))
    require(bool(candidates),'fully-mapped-mosaic-commit-before-request')
    return min(candidates)


def _validate_applied_standard_transition(request_ns, ipc_response, trace,
        owner_id, root_id, workspace_id, output, applied_layout, captures,
        client_protocol, snapshot, expected_ids, window, source_contract):
    """Return observed PASS or raise Invalid (INCONCLUSIVE).

    request_ns is an exact int in runtime. Historical replay explicitly uses a
    lower/upper interval from raw event + first trace after Handling command;
    it cannot establish the omitted syscall-start timestamp. Captures contain
    real start_ns/end_ns and must begin after first coherent applied standard.
    """
    require(source_contract==source_bindings(),'actual-private-source-contract')
    start,end=window
    bounds=[request_ns,request_ns] if type(request_ns) is int else request_ns
    require(isinstance(bounds,list) and len(bounds)==2 and all(type(v) is int for v in bounds)
            and start<=bounds[0]<=bounds[1]<ipc_response['ns']<end,'request-reply-window')
    require(ipc_response.get('args')==[f'[con_id={owner_id}] layout splith'] and
            ipc_response.get('exit')==0 and json.loads(ipc_response.get('stdout','null'))==[{'success':True}],
            'targeted-accepted-splith')
    require(applied_layout=='splith','standard-layout-required')
    path=ancestry(snapshot['tree'],owner_id)
    require(bool(path),'owner-ipc-absent')
    ws=[n for n in path if n.get('type')=='workspace'];out=[n for n in path if n.get('type')=='output']
    require(len(ws)==len(out)==1 and ws[0]['id']==workspace_id and ws[0]['layout']=='splith'
            and ws[0]['output']==output and out[0]['name']==output,'exact-workspace-output')
    require(path[-1].get('visible') is True and path[-1].get('app_id')=='org.mosaic.NestedGrabProbe',
            'mapped-owner-ipc')
    live=[n for n in nodes(snapshot['tree']) if n.get('app_id')=='org.mosaic.NestedGrabProbe' and n.get('visible')]
    require(len(live)==1 and live[0]['id']==owner_id,'one-live-popup-client-owner')
    prot=protocol(client_protocol)
    require(prot['ids']==expected_ids,'exact-xdg-object-identities')
    epochs=observed_epochs(trace,output,start,end)
    states=[];standard=[]
    for epoch in epochs:
        c,s,roots=epoch['commit'],epoch['scene'],epoch['roots']
        require(c.get('has_buffer')=='1' and s is not None and s.get('workspace')==str(workspace_id),
                'applied-current-scene-workspace')
        owners=[o for o in epoch['owners'] if o.get('id')==str(owner_id)]
        require(len(owners)==1 and owners[0].get('scene_valid')=='1','exact-applied-owner')
        require(len(roots)==1 and roots[0].get('tree')==root_id and roots[0].get('local_index')=='1'
                and roots[0].get('enabled')=='1','unique-enabled-root')
        o,r=owners[0],roots[0]
        t=int(r['ns']);layout=int(s['layout'])
        require(int(c['ns'])<int(s['ns'])<int(o['ns'])<t,'applied-trace-order')
        if layout==5:
            require(not standard,'clip-reactivated-after-standard')
            require(s['clip_valid']==r['clip_valid']=='1','old-mosaic-clips-required')
            # Signed local root box must explain the same global viewport as
            # the actual tiling tree. IPC supplies unchanged content offsets.
            win=path[-1]['window_rect'];deco=path[-1]['deco_rect']
            ox,oy=map(int,o['scene'].split(','));rx,ry,rw,rh=map(int,r['clip'].split(','))
            require([ox+win['x']+rx,oy+deco['height']+win['y']+ry,rw,rh]==[-800,0,800,600], 'old-root-global-viewport')
            tx,ty=map(int,s['tile_scene'].split(','));cx,cy,cw,ch=map(int,s['clip'].split(','))
            require([-800+tx+cx,ty+cy,cw,ch]==[-800,0,800,600],'old-tile-global-viewport')
            state='old-applied-Mosaic'
        elif layout==1:
            require(t>bounds[1],'standard-before-request-application')
            require(s['clip_valid']==r['clip_valid']=='0' and s['clip']==r['clip']=='0,0,0,0'
                    and s['tile_scene']=='0,0','standard-clips-absent')
            state='applied-standard';standard.append(epoch)
        else:require(False,'unexpected-applied-layout')
        states.append({'ns':t,'state':state,'owner':o,'scene':s,'root':r,'commit':c})
    require(states[0]['state']=='old-applied-Mosaic' and states[0]['ns']<=ipc_response['ns'],
            'old-applied-mosaic-required')
    require(len(standard)>=2,'two-standard-observations-required')
    # Coherent stabilization retains actual owner geometry and root identity.
    stable=[{k:e['owners'][next(i for i,o in enumerate(e['owners']) if o['id']==str(owner_id))][k]
             for k in ('scene','applied_size','current')} for e in standard]
    require(all(v==stable[0] for v in stable),'standard-geometry-not-stabilized')
    first_ns=int(standard[0]['roots'][0]['ns'])
    require(isinstance(captures,list) and len(captures)==2 and
            {c.get('output') for c in captures}=={'HEADLESS-1','HEADLESS-2'},'two-standard-captures')
    for capture in captures:
        require(capture.get('exit')==0 and type(capture.get('start_ns')) is int and
                first_ns<capture['start_ns']<=capture['end_ns']<=end and
                capture.get('sha256') and capture.get('file'),'capture-applied-standard-epoch')
    require(snapshot['ns']>first_ns and snapshot['ns']<=end,'snapshot-applied-epoch')
    return dict(status='PASS',states=states,request_bounds=bounds,ipc_reply_ns=ipc_response['ns'],
        first_standard_ns=first_ns,stabilized_ns=int(standard[-1]['roots'][0]['ns']),
        owner=owner_id,root=root_id,workspace=workspace_id,output=output,ids=prot['ids'],
        captures=captures,source_contract=source_contract,
        limitation='bounded unique-root correlation; independent observations, not atomic transaction generation')


EXPECTED_SOURCE = {'output.c':'b517c07655c6796a74fba731ab42d0f96ef53e104f6a9a4c0af256f26a25ded1',
 'transaction.c':'b04483d05100f57867560289d2a7db346e3e8925cec9fa4be35b23b1f6928165',
 'xdg_shell.c':'2a57ba553cacd82220bf16459debb167a3db5889c172af28d9067951f2df3610'}

def source_bindings():
    from support import sha
    observed={name:sha(path) for name,path in SOURCE_FILES.items()}
    require(observed==EXPECTED_SOURCE,'private-source-bytes-changed')
    return observed


def validate_applied_standard_transition(*args,**kwargs):
    """Malformed/omitted evidence is Invalid/INCONCLUSIVE, never accepted."""
    from model import Invalid
    try:return _validate_applied_standard_transition(*args,**kwargs)
    except Invalid:raise
    except (KeyError,IndexError,TypeError,ValueError,AttributeError,AssertionError) as exc:
        raise Invalid('malformed-transition-evidence:'+str(exc)) from exc
