#!/usr/bin/env python3
"""Read-only historical replay and explicitly labelled synthetic negative tests.

CONTRACT: exactly the live pure functions are exercised, without compositor launch.
INVARIANT: old manifests/snapshots are never written; historical IDs stay here.
"""
import argparse
import ast
import copy
import json
from pathlib import Path
import subprocess
from PIL import Image
from support import save, sha
from ipc_predicates import (nodes, validate_reference, validate_outputs, workspace,
    measure_owner, scene_from_log, client_commit, validate_preflight, validate_camera)
from pixels import analyze, compare, interior, painted_geometry, click_points, delivery, button_pair

HIST = Path('/home/fy59/swayfx-mosaic-static-followup-nhwejz6u')
OLD = Path('/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt')


def check():
    from verify import verify_inventory
    for base,pairs in [(HIST,[('source','5f9ab2b6d1ca23ef7743623d1e544237c8b70b62fe6de8164a46f1342e5a8ee2'),('evidence','41cc5e3d305d89e83314723e67d7116c36d1503dd35647894bc898c49343e1a5')]),
                       (OLD,[('source','ed55bd418595ca977c022fa98917a899072cf3b6f0fb15457db823081046e797'),('evidence','e260ce5793ffc9a29ee4bfa2189663feeb6dc025bd46d3f5ddebccd225f3eef1')])]:
        for name,digest in pairs:
            manifest=base/'results'/(name+'-sha256.txt');assert sha(manifest)==digest
            verify_inventory(manifest)
    snap=json.loads((HIST/'results/preflight-snapshot.json').read_text())
    text=(HIST/'run/compositor.log').read_text()
    ref=next(n for n in nodes(snap['tree']) if n.get('id')==7)
    target=next(n for n in nodes(snap['tree']) if n.get('id')==9)
    results=[]
    def rejected(name,fun):
        try:fun()
        except (AssertionError,KeyError,StopIteration,TypeError):results.append({'negative':name,'status':'REJECTED'})
        else:raise AssertionError('invalid fixture accepted: '+name)
    validate_reference(snap,7,ref['pid'])
    assert ref['border']=='none' and ref['current_border_width']==2
    for field,value in [('app_id','wrong'),('pid',1),('visible',False),('shell',None),
                        ('border','normal'),('rect',dict(x=1,y=0,width=800,height=600)),
                        ('window_rect',dict(x=0,y=0,width=799,height=600)),
                        ('deco_rect',dict(x=0,y=0,width=800,height=25))]:
        s=copy.deepcopy(snap);r=next(n for n in nodes(s['tree']) if n.get('id')==7);r[field]=value
        rejected(field,lambda s=s:validate_reference(s,7,ref['pid']))
    rejected('wrong con_id',lambda:validate_reference(snap,99,ref['pid']))
    rejected('wrong workspace',lambda:validate_reference(snap,7,ref['pid'],'1'))
    rejected('wrong output',lambda:validate_reference(snap,7,ref['pid'],'2','HEADLESS-1'))
    rejected('actual H1 filler',lambda:validate_reference(snap,8,next(n for n in nodes(snap['tree']) if n.get('id')==8)['pid']))
    s=copy.deepcopy(snap);workspace(s['tree'],'2')['nodes']=[]
    rejected('absent surface',lambda:validate_reference(s,7,ref['pid']))
    for field,value in [('rect',dict(x=0,y=0,width=801,height=600)),('scale',1.25),('transform','90')]:
        s=copy.deepcopy(snap);next(o for o in s['outputs'] if o['name']=='HEADLESS-2')[field]=value
        rejected('output '+field,lambda s=s:validate_reference(s,7,ref['pid']))
    # Earlier border-normal state is an actual IPC reply, not a manufactured state.
    early=None
    for line in (HIST/'run/events.jsonl').read_text().splitlines():
        e=json.loads(line)
        if e.get('kind')=='ipc' and list(e.get('args',[]))==['-t','get_tree']:
            r=next((n for n in nodes(e['result']) if n.get('id')==7),None)
            if r and r.get('border')=='normal':early=e['result'];break
    assert early is not None, 'real earlier border-normal observation missing'
    rejected('actual earlier normal reference',lambda:validate_reference({**snap,'tree':early},7,ref['pid']))
    scene=scene_from_log(text,'HEADLESS-1');h2=scene_from_log(text,'HEADLESS-2')
    measured=measure_owner(text,target);commit=client_commit((HIST/'run/target.log').read_text())
    good=validate_preflight(snap,7,ref['pid'],9,target['pid'],scene,h2,measured,commit)
    calibration=json.loads((HIST/'results/camera-calibration.json').read_text())
    validate_camera(calibration['before'],calibration['after'],calibration['delta'],scene)
    args=[snap,7,ref['pid'],9,target['pid'],scene,h2,measured,commit]
    for name,index,field,value in [('clip global',5,'global_clip',[0,0,800,600]),
        ('clip absent',5,'clip_valid',False),('camera',5,'scroll',0),
        ('scene owner',5,'workspace',999),('H2 clip',6,'clip_valid',True),
        ('content width',8,'width',635)]:
        bad=copy.deepcopy(args);bad[index][field]=value
        rejected(name,lambda bad=bad:validate_preflight(*bad))
    for name,mutate in [('focus',lambda s:next(n for n in nodes(s['tree']) if n.get('id')==9).update(focused=False)),
                        ('layout',lambda s:workspace(s['tree'],'1').update(layout='splith'))]:
        bad=copy.deepcopy(args);mutate(bad[0]);rejected(name,lambda bad=bad:validate_preflight(*bad))
    rejected('camera correction',lambda:validate_camera(0,160,159,scene))
    historical=Image.open(OLD/'run/h1-mosaic.png').convert('RGB')
    # The older static campaign used exactly this measured content continuation.
    paint=painted_geometry(historical,measured,commit)
    fixed=Image.new('RGB',(800,600),(48,48,56))
    points=click_points(historical,fixed,measured)
    assert points['permitted']==(-159,311) and points['forbidden']==(100,311)
    assert analyze(fixed)['count']==0 and compare(fixed,fixed.copy())['equal']
    edge=fixed.copy();edge.putpixel((799,599),(48,48,57))
    diff=compare(fixed,edge);assert not diff['equal'] and diff['changed']==1
    rejected('no target paint',lambda:interior(fixed))
    sparse=historical.copy();sparse.putpixel((640,311),(0,0,0))
    rejected('sparse paint',lambda:painted_geometry(sparse,measured,commit))
    blocked=fixed.copy();blocked.putpixel((100,311),(0,0,0))
    rejected('H2 point inaccessible',lambda:click_points(historical,blocked,measured))
    # Positive and negatives below are SYNTHETIC, not new or historical delivery.
    pair=['BUTTON ns=1 serial=3 button=273 state=1','BUTTON ns=2 serial=4 button=273 state=0']
    assert delivery(dict(target=pair,reference=[],filler=[]),'target')
    for name,lines in [('none',[]),('missing release',pair[:1]),('extra',pair+pair[:1]),
                       ('malformed',pair+['BUTTON garbage']),('wrong code',[s.replace('273','272') for s in pair]),
                       ('wrong order',pair[::-1]),('zero serial',[pair[0].replace('serial=3','serial=0'),pair[1]]),
                       ('same serial',[pair[0],pair[1].replace('serial=4','serial=3')]),
                       ('backwards time',[pair[0].replace('ns=1','ns=3'),pair[1]])]:
        rejected('SYNTHETIC button '+name,lambda lines=lines:button_pair(lines))
    rejected('SYNTHETIC wrong recipient',lambda:delivery(dict(target=pair,reference=pair,filler=[]),'target'))
    src=OLD/'mosaic-source'
    # Source tokens are supporting semantic audit, not behavioral tests.
    checks=[('sway/commands/border.c',['set_border(container, B_NONE)','if (argc == 2)']),
            ('sway/ipc-json.c',['json_object_new_int(c->current.border_thickness)','c->pending.content_width','view_is_visible']),
            ('sway/commands/layout.c',['workspace && workspace->layout == L_MOSAIC','container = NULL;','workspace->layout = new_layout']),
            ('sway/desktop/transaction.c',['border_width = 0;','wlr_scene_tree_set_clip(child->layers.tiling, NULL)']),
            ('sway/desktop/output.c',['wlr_scene_node_coords','PI_SCENE output=','PI_OWNER output='])]
    sources=[]
    for name,tokens in checks:
        p=src/name;contents=p.read_text();assert all(t in contents for t in tokens),(p,tokens)
        sources.append({'file':str(p),'sha256':sha(p),'semantics_checked':tokens})
    fields=[('outputs rect/scale/transform','sway/ipc-json.c','actual IPC','PASS','live reread'),
        ('view App ID/PID/con_id/ancestors/visible','sway/ipc-json.c','actual IPC','PASS','visibility is not pixels'),
        ('workspace/focus/layout','sway/ipc-json.c; sway/commands/layout.c','actual IPC','PASS','later focus live'),
        ('border/stored width/deco/window_rect','border.c; ipc-json.c; transaction.c','actual IPC plus earlier normal','PASS','effective RGB live'),
        ('camera scroll_x/scene tree/clip local/global','transaction.c; output.c; ipc-json.c','actual traces + calibration','PASS','no atomic generation asserted'),
        ('content dimensions/SHM colors','client-source/saved-client.c','actual COMMIT + historical PNG','PASS','new pixels live'),
        ('capture coordinates/painted click selection','pixels.py; virtual pointer source','HISTORICAL H1 + SYNTHETIC H2','PASS','new accessible surface verified live'),
        ('buttons/recipient/count/order/serial','saved-client.c:pointer_button; pointer-daemon.c','SYNTHETIC labelled cases','PASS','new actual client events required'),
        ('targeted splith return','sway/commands/layout.c','exact candidate source','PASS source audit','layout/clip/render/input live; NOT TESTED offline')]
    audit=[dict(field=f,source=s,historical_data=h,replay=r,remaining_uncertainty=u,
                invariant=f+' remains required live') for f,s,h,r,u in fields]
    runtime_assertions=[]
    runner=Path(__file__).with_name('run.py').read_text()
    for node in ast.walk(ast.parse(runner)):
        if isinstance(node,ast.Assert):
            runtime_assertions.append({'line':node.lineno,'expression':ast.get_source_segment(runner,node.test),
                'authority':'see corresponding field/source table; operational assertions use owned files/processes',
                'offline':'shared predicates and historical/synthetic tests above; environment identity checked by prepare',
                'uncertainty':'live-only states require new observations; no retrospective PASS'})
    audit={'fields':audit,'runner_assertions':sorted(runtime_assertions,key=lambda x:x['line'])}
    return {'reference':{'marker':'STATIC_REFERENCE_IPC_REPLAY=PASS','snapshot_sha256':sha(HIST/'results/preflight-snapshot.json'),
                         'accepted_width':2,'reference':good['reference'],'negatives':results},
            'preflight':{'marker':'STATIC_FIXTURE_PREFLIGHT_REPLAY=PASS','actual':good,'paint_HISTORICAL':paint,
                         'points_HISTORICAL_SYNTHETIC':points,'synthetic_input_tests':'PASS'},
            'audit':audit,'source_audit':sources}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--lab',type=Path);a=p.parse_args()
    result=check()
    for path in Path(__file__).parent.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
    subprocess.run(['python',str(Path(__file__).with_name('test-budget.py'))],check=True)
    if a.lab:
        from verify import verify_inventory
        verify_inventory(a.lab/'results/fixture-freeze-sha256.txt')
        save(a.lab,'ipc-replay',result['reference']);save(a.lab,'preflight-replay',result['preflight'])
        save(a.lab,'assertion-audit',result['audit']);save(a.lab,'source-audit',result['source_audit'])
        save(a.lab,'offline-gate',{'reference':'PASS','preflight':'PASS','AST':'PASS','ledger':'PASS','source_audit':'PASS'})
    print(result['reference']['marker']);print(result['preflight']['marker'])
    print('PASS',len(result['reference']['negatives']),'negative cases; historical/synthetic evidence labelled')
