#!/usr/bin/env python3
"""Offline requalification of actual RGB/input/return artifacts after the sole run.

WHY: shutdown IPC may lose its reply after cmd_exit terminates the compositor.
CONTRACT: never rewrite runtime.json or claim the executed runner exited zero.
INVARIANT: all scientific gates must independently pass; terminal transport is
accepted only with completed measurements, explicit exit and compositor code 0.
"""
import argparse
import copy
import json
from pathlib import Path
import re
from PIL import Image
from support import sha,save
from ipc_predicates import (nodes,workspace,validate_preflight,measure_owner,
    scene_from_log,client_commit,validate_reference,validate_outputs,validate_camera)
from pixels import compare,analyze,painted_geometry,click_points,delivery,button_pair,interior


def check(lab,overrides=None):
    lab=Path(lab);overrides=overrides or {}
    def read(name):return overrides.get(name,json.loads((lab/'results'/(name+'.json')).read_text()))
    def image(name):return overrides.get(name,Image.open(lab/'run'/name).convert('RGB'))
    text=(lab/'run/compositor.log').read_text()
    snap=read('preflight-snapshot');cal=read('camera-calibration');measured=read('owner-geometry')['after']
    ref=read('reference-state');tid=measured['id'];rid=ref['con_id']
    owner=next(n for n in nodes(snap['tree']) if n['id']==tid)
    assert measured['raw'] in text and cal['after_scene']['raw'] in text
    measured=measure_owner(measured['raw'],owner)
    scene=scene_from_log(cal['after_scene']['raw'],'HEADLESS-1')
    clips=read('scene-clips');assert clips['H2']['raw'] in text
    h2=scene_from_log(clips['H2']['raw'],'HEADLESS-2')
    commit=read('live-preflight')['commit'];assert commit['raw'] in (lab/'run/target.log').read_text()
    commit=client_commit(commit['raw'])
    validate_preflight(snap,rid,ref['pid'],tid,owner['pid'],scene,h2,measured,commit)
    validate_camera(cal['before'],cal['after'],cal['delta'],scene)
    baseline=image('h2-reference-1.png');assert baseline.size==(800,600)
    assert all(p==(48,48,56) for p in baseline.get_flattened_data())
    rgb={}
    for name in ['h2-reference-2.png','h2-mosaic.png','h2-after-clicks.png','h2-standard.png','h2-standard-after-click.png']:
        im=image(name);assert im.size==(800,600)
        value=compare(baseline,im);assert value['equal'], ('whole H2 RGB',name)
        assert analyze(im)['count']==0
        rgb[name]={'changed':0,'PNG_sha256':sha(lab/'run'/name)}
    paint=painted_geometry(image('h1-mosaic.png'),measured,commit)
    points=click_points(image('h1-mosaic.png'),image('h2-mosaic.png'),measured)
    logs={n:(lab/'run'/(n+'.log')).read_text() for n in ['target','reference','filler']}
    button_lines={n:[s for s in t.splitlines() if s.startswith('BUTTON ')] for n,t in logs.items()}
    pairs={}
    for name,recipient,point in [('visible_click','target',points['permitted']),
                                 ('forbidden_click','reference',points['forbidden']),
                                 ('standard_click','target',None)]:
        click=read(name);pairs[name]=delivery(click['events'],recipient)
        assert all(row in button_lines[recipient] for row in click['events'][recipient]), 'event not in actual log'
        if point:assert tuple(click['global_point'])==point
    assert button_lines['target']==read('visible_click')['events']['target']+read('standard_click')['events']['target']
    assert button_lines['reference']==read('forbidden_click')['events']['reference'] and not button_lines['filler']
    focus={}
    for name,expected in [('after-visible',tid),('after-reference',rid),('standard',rid),('after-standard-click',tid)]:
        s=read(name+'-snapshot');assert s['focused']==[expected]
        validate_reference(s,rid,ref['pid']);validate_outputs(s['outputs'])
        if name in ['after-visible','after-reference']:
            assert workspace(s['tree'],'1')['mosaic']['rows'][0]['scroll_x']==cal['after']
        focus[name]=expected
    standard=read('standard-return');assert standard['status']=='STATIC_STANDARD_RETURN=PASS'
    stdsnap=read('standard-snapshot');ws=workspace(stdsnap['tree'],'1')
    assert ws['id']==workspace(snap['tree'],'1')['id'] and ws['layout']=='splith'
    stdowner=next(n for n in nodes(ws) if n['id']==tid)
    assert stdowner['visible'] and stdowner['pid']==owner['pid']
    for output,key in [('HEADLESS-1','scene'),('HEADLESS-2','H2_scene')]:
        sc=standard[key];assert sc['raw'] in text
        parsed=scene_from_log(sc['raw'],output);assert not parsed['clip_valid'] and parsed['layout_enum']==1
    std=image('h1-standard.png');paint_std=analyze(std);assert paint_std['count']>0
    x1,y1,x2,y2=paint_std['bbox'];assert paint_std['count']==(x2-x1)*(y2-y1)
    stdpoint=interior(std);assert read('standard_click')['global_point']==[stdpoint[0]-800,stdpoint[1]]
    assert analyze(image('h2-standard.png'))['count']==0
    runtime=read('runtime');assert runtime['duration_seconds']<150
    assert [r['exit'] for r in runtime['process_exit_codes']]==[0,-15,0,0,0], 'unexpected owned process exit'
    assert not Path(runtime['runtime_removed']).exists()
    for row in runtime['process_exit_codes']:
        assert not Path('/proc',str(row['pid'])).exists(), 'owned process remains'
    budget=read('budget');assert budget['used']==dict(run=1,capture=8,camera=1,visible_click=1,forbidden_click=1,standard_click=1,move=6)
    assert len(list((lab/'run').glob('*.png')))==8
    injections=[s for s in (lab/'run/pointer.log').read_text().splitlines() if s.startswith('INJECT ')]
    assert len(injections)==6 and sum('INJECT right ' in s for s in injections)==3
    events=[json.loads(s) for s in (lab/'run/events.jsonl').read_text().splitlines()]
    adjustments=[e for e in events if e['kind']=='ipc' and e['args']==['layout mosaic scroll '+str(cal['delta'])]]
    assert len(adjustments)==1
    assert 'wl_display' not in '\n'.join(s for t in logs.values() for s in t.splitlines() if '.error(' in s)
    assert not re.search(r'protocol error|INVALID_|MISSING_GLOBAL', '\n'.join(logs.values()), re.I)
    shutdown_ns=min(int(re.search(r'EXIT ns=(\d+)',t)[1]) for t in logs.values())
    last_capture=max(e['ns'] for e in events if e['kind']=='capture')
    assert shutdown_ns>last_capture, 'client transport failure before final measurements'
    terminal=False
    if runtime['status']!='PASS':
        assert runtime['stopping_stage']=='completed'
        assert runtime['failure'].startswith('CalledProcessError: Command') and "'exit']' returned non-zero exit status 1." in runtime['failure']
        assert "Handling command 'exit'" in text and 'Shutting down sway' in text
        assert all('error=32' in t.splitlines()[-1] for t in logs.values()), 'different terminal transport error'
        terminal=True
    return {'status':'PASS','scientific_gates':'ALL PASS','verdict':'FEASIBLE',
            'architecture':'STATIC_MOSAIC_RGB_INPUT_STANDARD_FEASIBLE_FOR_TESTED_MATRIX',
            'RGB':rgb,'H1':paint,'standard_H1':paint_std,'pairs':pairs,'focus':focus,
            'terminal_transport_incident':terminal,'runner_exit':1 if terminal else 0,
            'original_runtime_status_preserved':runtime['status'],
            'terminal_diagnosis':'completed measurements precede explicit compositor exit 0; client errno 32 is terminal EPIPE, not a wl_display protocol error'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('lab',type=Path);p.add_argument('--record',action='store_true');a=p.parse_args()
    result=check(a.lab)
    # Negative post-run classification tests do not write any original observation.
    negatives=[]
    for name in ['runtime','standard-return','forbidden_click']:
        value=json.loads((a.lab/'results'/(name+'.json')).read_text());bad=copy.deepcopy(value)
        if name=='runtime':bad['process_exit_codes'][0]['exit']=1
        elif name=='standard-return':bad['scene']['clip_valid']=True;bad['scene']['raw']=bad['scene']['raw'].replace('clip_valid=0','clip_valid=1')
        else:bad['events']['target']=['BUTTON ns=1 serial=3 button=273 state=1']
        try:check(a.lab,{name:bad})
        except AssertionError:negatives.append(name+' REJECTED')
        else:raise AssertionError('postrun bad state accepted: '+name)
    changed=Image.open(a.lab/'run/h2-mosaic.png').convert('RGB');changed.putpixel((799,599),(48,48,57))
    try:check(a.lab,{'h2-mosaic.png':changed})
    except AssertionError:negatives.append('whole H2 RGB REJECTED')
    else:raise AssertionError('postrun changed H2 accepted')
    result['negative_tests']=negatives
    if a.record:save(a.lab,'postrun-validation',result)
    print('PASS actual RGB, scene, all real buttons/focus, standard return, budget and terminal diagnosis')
    print('PASS negative postrun classification',negatives)
