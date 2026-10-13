#!/usr/bin/env python3
"""Read-only post-run diagnosis of failed geometry assertions; no graphical retry.

WHY: SHM/native geometry, rendered destination and IPC window_rect differ.
CONTRACT: preserve the executed runner and diagnose against actual PNG/protocol.
INVARIANT: a successful diagnosis cannot qualify uncreated popup grabs or input.
"""
import argparse
import ast
import json
from pathlib import Path
import re
from PIL import Image
from predicates import paint,equal,reference
from ipc_predicates import validate_reference,measure_owner,scene_from_log
from support import sha,save,verify

def diagnose(lab):
    lab=Path(lab);run=lab/'run'
    runtime=json.loads((lab/'results/runtime.json').read_text());budget=json.loads((lab/'results/budget.json').read_text())
    assert runtime['status']=='INCONCLUSIVE' and runtime['stage']=='E1-open-A' and not runtime['measurements_completed']
    assert budget['used']==dict(run=1,chain=1,grab=0,click=0,capture=3,camera=1,transition=0,move=1)
    client=(run/'E1.log').read_text();assert 'GRAB_REQUEST' not in client and 'POPUP_A CREATE' not in client and 'POINTER_BUTTON' not in client
    assert 'create_buffer(new id wl_buffer#12, 0, 420, 320, 1680, 1)' in client
    assert 'TOPLEVEL ROLE_CONFIGURE w=636 h=573' in client
    assert client.index('xdg_surface#9.ack_configure(20)')<client.index('wl_surface#3.attach(')<client.index('TOPLEVEL MAP ')
    snap=json.loads((lab/'results/E1-applied-snapshot.json').read_text())
    cal=json.loads((lab/'results/camera-calibration.json').read_text())[-1];owner=cal['after_owner']['IPC']
    measure=measure_owner((run/'compositor.log').read_text(),owner)
    # Use the recorded applied sample before shutdown, never the later teardown scene.
    assert cal['after_owner']['raw'] in (run/'compositor.log').read_text()
    applied=measure_owner(cal['after_owner']['raw'],owner)
    scene=scene_from_log(cal['scene']['raw'],'HEADLESS-1')
    assert scene['global_clip']==[-800,0,800,600] and scene['clip_valid'] and scene['scroll']==160
    assert cal['before']==480 and cal['delta']==-320 and cal['after']==160
    value=paint(Image.open(run/'E1-top.png').convert('RGB'),'TOPLEVEL');assert value==dict(count=182214,bbox=(482,25,800,598))
    x1,y1,x2,y2=value['bbox'];assert x1-800==applied['horizontal_content'][0]==-318
    assert value['count']==(x2-x1)*(y2-y1) and y2-y1==owner['window_rect']['height']==573
    assert owner['geometry']==dict(x=0,y=0,width=420,height=320)
    old_height_ok=(y2-y1==320)
    old_y_ok=(y1==applied['scene'][1]+owner['window_rect']['y'])
    assert not old_height_ok and not old_y_ok, 'must reproduce both invalid assumptions'
    assert owner['window_rect']['y']==0 and owner['deco_rect']['height']==25 and applied['scene'][1]==0
    ref=json.loads((lab/'results/reference-stability.json').read_text())['reference']
    validate_reference(snap,ref['con_id'],ref['pid'])
    a=Image.open(run/'H2-reference-1.png').convert('RGB');b=Image.open(run/'H2-reference-2.png').convert('RGB');reference(a,b)
    assert paint(a,'TOPLEVEL')['count']==0 and paint(b,'TOPLEVEL')['count']==0
    events=[json.loads(s) for s in (run/'events.jsonl').read_text().splitlines()]
    cap=[e for e in events if e['kind']=='capture']
    assert len(cap)==3 and cap[1]['start_ns']-cap[0]['start_ns']>=500000000
    exact=Path('/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/mosaic-source')
    output=(exact/'sway/desktop/output.c').read_text();ipc=(exact/'sway/ipc-json.c').read_text();trans=(exact/'sway/desktop/transaction.c').read_text()
    assert 'wlr_scene_buffer_set_dest_size(buffer, MAX(content_width, 0), MAX(content_height, 0))' in output
    assert 'has_titlebar ? 0 : c->pending.content_y - c->pending.y' in ipc
    assert 'border_left, border_top' in trans
    runner=(lab/'fixture/run.py').read_text();assert 'topbox[3]-topbox[1]==320' in runner
    assert "origin[1]==after['scene'][1]+owner['window_rect']['y']" in runner
    terminal=json.loads((lab/'results/terminal-exit.json').read_text())
    assert terminal['ipc_exit']==1 and terminal['compositor_exit']==0 and not terminal['scientific_cleanup_pass']
    assert 'Unable to receive IPC response' in terminal['stderr']
    text=(run/'compositor.log').read_text();assert "Handling command 'exit'" in text and 'Shutting down sway' in text
    assert all(row['exit']==0 and not Path('/proc',str(row['pid'])).exists() for row in terminal['owned_process_codes'])
    assert not re.search(r'wl_display[^\n]*\.error\(|protocol error',client,re.I)
    return dict(status='PASS offline diagnosis; runtime remains INCONCLUSIVE',runner_sha256=sha(lab/'fixture/run.py'),
        executed_assertion_line=182,first_failure='rendered blue height 573 != immutable SHM height 320',
        additional_unreached_assertion_line=183,additional_failure='titlebar-enabled IPC window_rect.y=0 does not give painted/content y=25',
        applied_owner=applied,painted_TOPLEVEL=value,SHM_size=[420,320],assigned_content=[636,573],painted_content_origin=[-318,25],
        applied_camera=dict(before=480,relative_delta=-320,after=160),tiled_clip=scene,
        H2=dict(whole_RGB='PASS two references',color='#303038',changed_pixels=0,PNG_sha256=sha(run/'H2-reference-1.png')),
        source_locations={'destination':'sway/desktop/output.c:331','window_rect_y':'sway/ipc-json.c:712','content_origin':'sway/desktop/transaction.c:705'},
        origin_diagnosis='actual paint supplies y; IPC window_rect excludes enabled titlebar; rendered destination is separate from native SHM',
        offline_preflight_limit='recorded PASS did not audit these two live assertions against the source/available prior IPC; it was insufficient',
        popup_geometry='NOT EXERCISED',grabs='NOT TESTED',input='NOT TESTED',standard='NOT TESTED',new_runs=0,
        correction_scope='offline fixture geometry revalidation required; no clipping algorithm change justified')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('lab',type=Path);p.add_argument('--record',action='store_true');a=p.parse_args()
    verify(a.lab/'results/fixture-freeze-sha256.txt');result=diagnose(a.lab)
    if a.record:save(a.lab,'geometry-fixture-diagnostic',result)
    print('PASS reproduce failed height assertion and additional invalid IPC-y assumption; no popup evidence manufactured')
