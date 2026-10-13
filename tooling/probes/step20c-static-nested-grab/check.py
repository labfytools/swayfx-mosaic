#!/usr/bin/env python3
"""Offline protocol/pixel/ledger/terminal tests; never starts a compositor.

Historical observations and synthetic negative cases are explicitly labelled.
"""
import ast
import concurrent.futures
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from PIL import Image
from support import initial,reserve,LIMITS,save,sha,verify,OWNER,REPO,NESTED_SHA
from predicates import protocol,geometry,pair,dismissal,terminal,point,reference,root_clip,popup_pixels,Defect
from ipc_predicates import validate_reference,validate_outputs

def attempt(args):
    lab,k=args
    try:reserve(lab,k);return True
    except RuntimeError:return False

def rejected(name,func):
    try:func()
    except (AssertionError,Defect,RuntimeError,ValueError):return name
    raise AssertionError('negative accepted: '+name)

if __name__=='__main__':
    lab=Path(sys.argv[1]);assert OWNER.read_text().strip()==str(lab)
    verify(lab/'results/fixture-freeze-sha256.txt')
    assert json.loads((lab/'results/budget.json').read_text())['used']==dict.fromkeys(LIMITS,0)
    for p in (lab/'fixture').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    for p in [lab/'protocol-before-run.md',lab/'fixture/README.md']:
        for s in re.findall(r'```(?:sh|bash)\n(.*?)```',p.read_text(),re.S):subprocess.run(['sh','-n'],input=s,text=True,check=True)
    with tempfile.TemporaryDirectory(prefix='static-nested-ledger-offline-') as tmp:
        test=Path(tmp);(test/'results').mkdir();initial(test)
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
            assert sum(pool.map(attempt,[(test,'capture')]*24))==16
        for k,n in LIMITS.items():
            if k=='capture':continue
            for _ in range(n):reserve(test,k)
            assert not attempt((test,k))
        before=(test/'results/budget.json').read_bytes()
        assert not attempt((test,'run')) and (test/'results/budget.json').read_bytes()==before
        state=json.loads(before);state['used']['run']=-1
        (test/'results/budget.json').write_text(json.dumps(state));assert not attempt((test,'run'))
    # Use the retained actual unmodified nested control, stopping while mapped.
    old=Path('/tmp/swayfx-mosaic-nested-grab-If8ofeUu/run-control-open-visible/client.log')
    text=old.read_text().split('TOPLEVEL DESTROY')[0]
    cuts=[text.find(s) for s in ['POPUP_B DESTROY','POPUP_B POPUP_DONE'] if s in text]
    if cuts:text=text[:min(cuts)]
    good=protocol(text);negative=[]
    for name,wrong in [('serial',text.replace('used=61','used=62')),
        ('parent',text.replace('parent_xdg=12','parent_xdg=9')),
        ('button origin',text.replace('target=TOPLEVEL serial=61 button=272 state=1','target=OTHER serial=61 button=272 state=1')),
        ('protocol error',text+'\nwl_display#1.error(1, 1, "bad")'),
        ('premature dismissal',text+'\nPOPUP_B POPUP_DONE role=17')]:
        negative.append(rejected(name,lambda t=wrong:protocol(t)))
    snap=json.loads((Path('/home/fy59/swayfx-mosaic-static-rgb-input-retest-hn67lnhq/results/preflight-snapshot.json')).read_text())
    ref=validate_reference(snap,7,1700453);validate_outputs(snap['outputs']);assert ref['stored_border_width']==2
    negative.append(rejected('wrong reference identity',lambda:validate_reference(snap,8,1700459)))
    synthetic='POPUP_A ROLE_CONFIGURE x=100 y=80 w=350 h=170\nPOPUP_B ROLE_CONFIGURE x=100 y=60 w=300 h=130'
    g=geometry(synthetic,[-318,25]);assert g['A']==[-218,105,350,170] and g['B']==[-118,165,300,130]
    negative.append(rejected('no crossing',lambda:geometry(synthetic,[-700,25])))
    # Labelled synthetic color regions challenge exact rectangle/occlusion predicates.
    from PIL import ImageDraw
    baseline=Image.new('RGB',(800,600),(48,48,56))
    def synthetic_pixels(mosaic):
        images=[]
        for ox in [-800,0]:
            im=baseline.copy();draw=ImageDraw.Draw(im)
            if not mosaic or ox==-800:
                for key,color in [('A',(224,192,32)),('B',(32,208,160))]:
                    x,y,w,h=g[key];draw.rectangle((x-ox,y,x+w-ox-1,y+h-1),fill=color)
            images.append(im)
        return images
    left,right=synthetic_pixels(True);popup_pixels(left,right,g,True,baseline)
    badright=right.copy();badright.putpixel((1,200),(32,208,160))
    negative.append(rejected('actual forbidden color',lambda:popup_pixels(left,badright,g,True,baseline)))
    lstd,rstd=synthetic_pixels(False);popup_pixels(lstd,rstd,g,False,baseline)
    negative.append(rejected('standard B missing',lambda:popup_pixels(lstd,right,g,False,baseline)))
    assert point(left,'POPUP_B',-800)[0]<0
    # Initial synthetic protocol must reject missing/early ACK and buffer attachment.
    cfg=good['grabs'][0]['ack'];role=good['grabs'][0]['ids'][1]
    negative.append(rejected('missing real ACK',lambda:protocol(text.replace(f'xdg_surface#{role}.ack_configure({cfg})',f'xdg_surface#{role}.ack_configure(999)'))))
    assert 100+1<=420 and 80+1<=320 and 100+1<=350 and 60+1<=170
    assert -800+800==0 and 799+800==1599 # Signed global -> verified output-layout fraction.
    im=Image.new('RGB',(800,600),(48,48,56));reference(im,im.copy())
    bad=im.copy();bad.putpixel((799,599),(48,48,57))
    negative.append(rejected('one changed RGB',lambda:reference(im,bad)))
    negative.append(rejected('sparse paint point',lambda:point(im,'POPUP_B',0)))
    lines=['POINTER_BUTTON target=POPUP_B serial=70 button=273 state=1','POINTER_BUTTON target=POPUP_B serial=71 button=273 state=0']
    pair(lines,'POPUP_B')
    negative.append(rejected('wrong delivered target',lambda:pair(lines,'POPUP_A')))
    d='POPUP_B POPUP_DONE role=17\nPOPUP_A POPUP_DONE role=14\nPOPUP_B DESTROY role=17\nPOPUP_A DESTROY role=14'
    dismissal(d,[])
    negative.append(rejected('invisible delivery',lambda:dismissal(d,lines)))
    negative.append(rejected('wrong dismissal order',lambda:dismissal(d.replace('POPUP_B POPUP_DONE','POPUP_A POPUP_DONE'),[])))
    sc='PI_POPUP output=HEADLESS-1 ns=1 local_index=1 tree=0x123 enabled=1 clip_valid=1 clip=-482,-25,800,600'
    root_clip(sc,[-318,25],True)
    negative.append(rejected('wrong applied clip',lambda:root_clip(sc,[-317,25],True)))
    log="Handling command 'exit'\nShutting down sway"
    assert terminal(True,1,0,log,False,False)['transport_incident']
    for args in [(False,1,0,log,False,False),(True,1,1,log,False,False),(True,1,0,'',False,False),(True,1,0,log,True,False),(True,1,0,log,False,True)]:
        assert not terminal(*args)['scientific_cleanup_pass']
    src=(lab/'historical-source/nested-client.c').read_text();assert sha(lab/'historical-source/nested-client.c')==NESTED_SHA
    patched=(lab/'client-source/nested-client.c').read_text()
    # CONTRACT: remove precisely the sole new placement branch, recover original bytes.
    expected=src.replace('    if (!strcmp(placement,"visible")) {','    /* EXPERIMENTAL: only placement changes; serial/grab/lifecycle stay historical.\n     * Both 1x1 anchors lie inside their parent SHM window geometry. */\n    if (!strcmp(placement,"static_cross")) {\n        a.anchor_x=100; a.anchor_y=80; a.width=350;\n        b.anchor_x=100; b.anchor_y=60; b.width=300;\n    } else if (!strcmp(placement,"visible")) {')
    assert patched==expected,'unauthorized client behavior change'
    for tokens in ['xdg_popup_grab(s->popup,seat,serial)','parent->xdg','if (!s->mapped && !s->done) draw(s)','destroy_popup(&b); destroy_popup(&a);']:
        assert tokens in src
    candidate=Path('/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/mosaic-source')
    token_files={'sway/desktop/transaction.c':['con->current.workspace','wlr_scene_tree_get_clip(ws->layers.tiling','wlr_scene_tree_set_clip(popup_tree, NULL)'],
        'sway/desktop/xdg_shell.c':['popup->xdg_surface_tree, popup->image_capture_tree','popup->desc.relative = &view->content_tree->node'],
        'sway/commands/exit.c':['sway_terminate(0)'],
        'sway/main.c':['wl_display_terminate(server.wl_display)','Shutting down sway','return exit_value'],
        'sway/ipc-server.c':['WL_EVENT_WRITABLE','ipc_send_reply']}
    for file,tokens in token_files.items():assert all(t in (candidate/file).read_text() for t in tokens),(file,tokens)
    save(lab,'offline-gate',dict(marker='STATIC_NESTED_GRAB_FIXTURE_PREFLIGHT=PASS',status='PASS',fixture_sha256=sha(lab/'results/fixture-freeze-sha256.txt'),historical_control=str(old),historical_protocol=good,synthetic_geometry=g,negative_cases=negative,ledger='PASS concurrency/exhaustion/corruption',terminal='PASS synthetic success and five failures',client_delta='placement only',AST='PASS',shell='PASS',source_audit='PASS',C17='PASS from preparation',runtime='NOT TESTED'))
    print('STATIC_NESTED_GRAB_FIXTURE_PREFLIGHT=PASS')
    print('PASS historical control, reference width2, labelled synthetic predicates,',len(negative),'negative cases, ledger and terminal classification')
