#!/usr/bin/env python3
"""Read-only historical input replay. Writes JSON only in the new offline LAB."""
import argparse
import json
from pathlib import Path
import re
from PIL import Image
from model import *
from observations import applied_model,output_model,viewport_model
from predicates import COLORS,paint,protocol,pair,dismissal,equal,reference
from ipc_predicates import nodes,validate_reference
from support import save,sha
from pixels import color_geometry

HISTORICAL = Path('/home/fy59/swayfx-mosaic-static-nested-grab-m0a5e2qh')
NESTED = Path('/tmp/swayfx-mosaic-nested-grab-If8ofeUu')


def correlate_historical(text,injections,rects,standard=None):
    """CONTRACT: wire button times bind actions; map retarget uses the last point.

    WHY: callbacks have no injection timestamp of their own. Pre-injection seat
    events remain explicitly unpaired; software motion retains its wire time.
    """
    actions=[];stamp=1000
    for kind,x,y in re.findall(r'^INJECT (left|right|move) (-?\d+),(-?\d+)$',injections,re.M):
        action=dict(index=len(actions),kind=kind,global_point=[int(x),int(y)],motion_msec=stamp)
        stamp+=1
        if kind!='move':
            action.update(press_msec=stamp,release_msec=stamp+1,button=272 if kind=='left' else 273);stamp+=2
        actions.append(action)
    require(bool(actions),'historical-injections-present')
    bytime={a[k]:a for a in actions for k in ('motion_msec','press_msec','release_msec') if k in a}
    lines=text.splitlines();callbacks=[];events=[];current=actions[0];locations={};phase='opening';wire=None;standard_active=False;live=set()
    firstpress=next(i for i,l in enumerate(lines) if re.search(r'wl_pointer#\d+\.button\(\d+, 1001,',l))
    initialenter=max(i for i,l in enumerate(lines[:firstpress]) if l.startswith('POINTER_ENTER '))
    identities={n:int(v) for n,v in re.findall(r'^(TOPLEVEL|POPUP_A|POPUP_B) CREATE wl=(\d+)',text,re.M)}
    for i,line in enumerate(lines):
        lifecycle=re.match(r'(TOPLEVEL|POPUP_A|POPUP_B) (MAP|DESTROY) ',line)
        if lifecycle:
            if lifecycle[2]=='MAP':live.add(lifecycle[1])
            else:live.discard(lifecycle[1])
        if standard and line.startswith('TOPLEVEL ROLE_CONFIGURE ') and 'POPUP_B MAP ' in '\n'.join(lines[:i]):standard_active=True;phase='standard'
        if line.startswith('COMMAND close_b DONE'):phase='after-B-close'
        if line.startswith('POPUP_B MAP '):phase='mapped'
        debug=re.search(r'wl_pointer#\d+\.(button|motion|enter)\(([^)]+)\)',line)
        if debug:
            wire=(debug[1],[v.strip() for v in debug[2].split(',')])
            if wire[0]!='enter':
                time=int(wire[1][1] if wire[0]=='button' else wire[1][0])
                if time in bytime:current=bytime[time]
        match=re.match(r'POINTER_(ENTER|MOTION) target=(\w+) (?:wl=\d+ serial=\d+ )?x=([\d.-]+) y=([\d.-]+)',line)
        active=standard if standard_active else rects
        if match:
            kind,target,x,y=match.groups();local=[float(x),float(y)]
            record=dict(line=i+1,kind=kind,target=target,local=local,phase=phase)
            if i<initialenter:
                record.update(status='NOT AVAILABLE / NOT REPLAYED',scope='seat event before first identifiable injected enter')
                callbacks.append(record);continue
            require(target in active and target in live,'historical-pointer-recipient')
            require(wire is not None and wire[0]==kind.lower(),'historical-coordinate-wire-kind')
            offset=2 if kind=='ENTER' else 1
            require(local==list(map(float,wire[1][offset:offset+2])),'historical-coordinate-wire-local')
            if kind=='ENTER':
                require(int(re.search(r'#(\d+)',wire[1][1])[1])==identities[target],'historical-enter-surface-identity')
            if kind=='ENTER':
                # INVARIANT: a motion before the next wire button means this enter
                # belongs to the previous point (automatic mapping retarget).
                following=next((j for j in range(i+1,len(lines)) if re.search(r'wl_pointer#\d+\.(button|motion)\(',lines[j])),None)
                if following is not None and '.button(' in lines[following]:
                    t=int(re.search(r'\.button\(\d+, (\d+),',lines[following])[1]);current=bytime.get(t,current)
            pointer_local(current['global_point'],active[target],local)
            locations[target]=local
            record.update(status='PASS',action=current['index'],global_point=current['global_point'],origin=[active[target].x,active[target].y],wire=wire)
            callbacks.append(record)
        button=re.match(r'POINTER_BUTTON target=(\w+) serial=(\d+) button=(\d+) state=(\d+)',line)
        if button:
            target,serial,key,state=button.groups();serial,key,state=map(int,(serial,key,state))
            require(wire is not None and wire[0]=='button','historical-button-wire-present')
            ws,tm,wk,st=map(int,wire[1]);require((serial,key,state)==(ws,wk,st),'historical-button-wire-identity')
            require(tm in bytime,'historical-button-injection-time')
            action=bytime[tm];require(tm==action.get('press_msec' if state else 'release_msec') and key==action.get('button'),'historical-button-action-order')
            require(target in active and target in live and target in locations,'historical-pointer-recipient')
            pointer_local(action['global_point'],active[target],locations[target])
            events.append(dict(line=i+1,target=target,serial=serial,button=key,state=state,msec=tm,action=action['index'],phase=phase,raw=line))
            wire=None
    require(len(events)>=4,'historical-opening-buttons')
    require([e['target'] for e in events[:4]]==['TOPLEVEL','TOPLEVEL','POPUP_A','POPUP_A'],'historical-opening-recipients')
    times=[e['msec'] for e in events];require(times==sorted(set(times)),'historical-button-sequence')
    paired={e['action'] for e in events}
    for index in paired:
        group=[e for e in events if e['action']==index]
        require(len(group)==2 and [e['state'] for e in group]==[1,0] and group[0]['target']==group[1]['target'],'historical-button-complete-pair')
    if 'POPUP_B POPUP_DONE ' in text:
        forbidden=actions[-1]
        require(forbidden['index'] not in paired,'historical-forbidden-button-delivery')
    else:
        require(paired=={a['index'] for a in actions if a['kind']!='move'},'historical-required-visible-buttons')
    return dict(status='PASS',actions=actions,callbacks=callbacks,buttons=events,
                forbidden_buttons=[e['raw'] for e in events if e['action']==actions[-1]['index']] if 'POPUP_B POPUP_DONE ' in text else [])

def replay_native(lab,historical=HISTORICAL):
    cal=json.loads((historical/'results/camera-calibration.json').read_text())[-1]
    snap=json.loads((historical/'results/E1-applied-snapshot.json').read_text())
    client=(historical/'run/E1.log').read_text()
    measured={**cal['after_owner'],'workspace':cal['scene']['workspace']}
    owner=measured['IPC']
    applied=applied_model(measured,owner,client,'historical-E1-applied')
    rect=content(applied);out=output_model(snap,'HEADLESS-1',rect.provenance)
    clip=viewport_model(cal['scene'],rect.provenance)
    require(measured['raw'] in (historical/'run/compositor.log').read_text(),'historical-applied-trace')
    value=paint(Image.open(historical/'run/E1-top.png'),'TOPLEVEL')
    png=verify_paint(rect,out,value['bbox'],value['count'],clip)
    require((applied.native.rectangle.width,applied.native.rectangle.height)==(420,320),'historical-shm')
    require((rect.width,rect.height)==(636,573) and (rect.x,rect.y)==(-318,25),'historical-render')
    require(value==dict(bbox=(482,25,800,598),count=182214),'historical-paint')
    require(png.height!=applied.native.rectangle.height and rect.y!=applied.scene.y+applied.window.y,'reproduce-two-invalid-assumptions')
    validate_reference(snap,cal['reference']['con_id'],cal['reference']['pid'])
    reference(Image.open(historical/'run/H2-reference-1.png').convert('RGB'),Image.open(historical/'run/H2-reference-2.png').convert('RGB'))
    records={
        'native-shm':dict(status='PASS',buffer=applied.native.buffer_id,size=applied.native.rectangle.values(),stride=applied.native.stride,format=applied.native.format,source=str(historical/'run/E1.log'),PNG_identity='NOT PROVEN'),
        'xdg-configure':dict(status='PASS',toplevel=applied.configured.values(),initial_ACK=applied.native.commit_serial,assigned_ACK=applied.configure_ack,initial_configure=[0,0],new_buffer_after_assigned_configure=False,popups='NOT EXERCISED'),
        'applied':dict(status='PASS',owner=owner['id'],pid=owner['pid'],workspace=rect.provenance.workspace,scene=applied.scene.values(),window=applied.window.values(),titlebar=applied.titlebar,scroll=cal['after'],globalclip=clip.values(),generation='atomic transaction identity NOT TESTED'),
        'rendered':dict(status='PASS',content=rect.values(),PNG_bbox=value['bbox'],count=value['count'],visible_intersection=png.values(),native_equals_dest=False),
        'historical-evidence':dict(status='PASS read-only historical replay',inputs={str(historical/'run'/n):sha(historical/'run'/n) for n in ('E1.log','E1-top.png','compositor.log')},diagnostic=str(historical/'results/geometry-fixture-diagnostic.json'),runtime='INCONCLUSIVE / no popup / no grab')}
    for name,data in records.items():save(lab,name,data)
    return records


def replay_nested(lab,root=NESTED):
    results=[]
    dirs=('run-private_mosaic-crossing-b_cross','run-private_mosaic-crossing-both_cross',
          'run-private_mosaic-toggle-b_cross','run-private_mosaic-outside-visible',
          'run-control-crossing-b_cross','run-control-crossing-both_cross','run-control-outside-visible',
          'run-private_mosaic-close_b-visible','run-control-close_b-visible')
    for dirname in dirs:
        directory=root/dirname
        if not directory.is_dir():
            results.append(dict(case=dirname,status='NOT AVAILABLE'));continue
        text=(directory/'client.log').read_text()
        stop=min([m.start() for m in re.finditer(r'POPUP_[AB] (?:POPUP_DONE|DESTROY)',text)] or [len(text)])
        opened=text[:stop]
        prot=protocol(opened)
        tree=json.loads((directory/'tree-open.json').read_text())
        ws=next(n for n in nodes(tree) if n.get('type')=='workspace' and n.get('name')=='1')
        owner=next(n for n in nodes(ws) if n.get('app_id')=='org.mosaic.NestedGrabProbe')
        prov=Provenance(owner['id'],ws['id'],dirname+'-open','IPC + clip + RGB; no atomic generation')
        comp=(directory/'compositor.log').read_text()
        clips=re.findall(r'PROBE_POPUP_CLIP owner=(\S+) local=(-?\d+),(-?\d+) (\d+)x(\d+)',comp)
        private='private_mosaic' in dirname
        if private:
            require(bool(clips),'historical-popup-root-clip')
            require(len({c[0] for c in clips})==1,'historical-unique-owner-pointer')
            _,cx,cy,cw,ch=clips[0];origin=(-int(cx),-int(cy))
            clip=Rect(Space.VIEWPORT,0,0,int(cw),int(ch),prov)
            require(origin==(owner['rect']['x']-int(ws['mosaic']['rows'][0]['scroll_x'])+owner['window_rect']['x'],owner['deco_rect']['height']+owner['window_rect']['y']),'historical-origin-corroboration')
        else:
            origin=(owner['rect']['x']+owner['window_rect']['x'],owner['deco_rect']['height']+owner['window_rect']['y']);clip=None
        top=Rect(Space.GLOBAL,*origin,owner['window_rect']['width'],owner['window_rect']['height'],prov)
        configs={n:list(map(int,re.findall(rf'{n} ROLE_CONFIGURE x=(-?\d+) y=(-?\d+) w=(\d+) h=(\d+)',opened)[-1])) for n in ('POPUP_A','POPUP_B')}
        A=popup(top,Rect(Space.POPUP,*configs['POPUP_A'],prov),prot['ids']['TOPLEVEL'][1],prot['ids']['TOPLEVEL'][1],prot['grabs'][0]['ack'],True)
        B=popup(A,Rect(Space.POPUP,*configs['POPUP_B'],prov),prot['ids']['POPUP_A'][1],prot['ids']['POPUP_A'][1],prot['grabs'][1]['ack'],True)
        outputs=json.loads((directory/'outputs-open.json').read_text())
        colors={}
        for side,name in (('left','HEADLESS-1'),('right','HEADLESS-2')):
            out=output_model({'outputs':outputs},name,prov)
            im=Image.open(directory/(side+'-open.png')).convert('RGB')
            colors[side]={n:color_geometry(im,n,r,out,clip,(B,) if n=='POPUP_A' else ()) for n,r in (('POPUP_A',A),('POPUP_B',B))}
        pointers=re.findall(r'POINTER_(ENTER|MOTION) target=(\w+) (?:wl=\d+ serial=\d+ )?x=([\d.-]+) y=([\d.-]+)',text)
        injections=(directory/'pointer.log').read_text()
        buttons=[line for line in text.splitlines() if line.startswith('POINTER_BUTTON ')]
        done=re.findall(r'(POPUP_[AB]) POPUP_DONE ',text)
        destroyed=re.findall(r'(POPUP_[AB]) DESTROY ',text)
        row=dict(case=dirname,status='PASS historical sampled replay',owner=owner['id'],pid=owner['pid'],workspace=ws['id'],scroll=ws.get('mosaic',{}).get('rows',[{}])[0].get('scroll_x'),origin=origin,A=A.values(),B=B.values(),configured=configs,protocol=prot,clip=clip.values() if clip else None,colors=colors,pointer_callbacks=pointers,pointer_injections=injections.splitlines(),buttons=buttons,done=done,destroyed=destroyed,files={p.name:sha(p) for p in directory.iterdir() if p.is_file()},native_frame_identity='NOT PROVEN')
        require(destroyed==['POPUP_B','POPUP_A'],'historical-child-first-destruction')
        if 'toggle' in dirname:
            stdtree=json.loads((directory/'tree-standard.json').read_text());stdws=next(n for n in nodes(stdtree) if n.get('id')==ws['id']);stdowner=next(n for n in nodes(stdws) if n.get('id')==owner['id'])
            require(stdws['layout']=='splith' and not done,'historical-standard-mapped')
            sp=Provenance(owner['id'],ws['id'],dirname+'-standard','fresh standard IPC + paint')
            so=(stdowner['rect']['x']+stdowner['window_rect']['x'],stdowner['deco_rect']['height']+stdowner['window_rect']['y'])
            stdtop=Rect(Space.GLOBAL,*so,stdowner['window_rect']['width'],stdowner['window_rect']['height'],sp)
            stdA=Rect(Space.GLOBAL,so[0]+configs['POPUP_A'][0],so[1]+configs['POPUP_A'][1],*configs['POPUP_A'][2:],sp)
            stdB=Rect(Space.GLOBAL,stdA.x+configs['POPUP_B'][0],stdA.y+configs['POPUP_B'][1],*configs['POPUP_B'][2:],sp)
            fresh_standard(top,stdtop)
            stdcolors={}
            stdoutputs=json.loads((directory/'outputs-standard.json').read_text())
            for side,name in (('left','HEADLESS-1'),('right','HEADLESS-2')):
                im=Image.open(directory/(side+'-standard.png')).convert('RGB');out=output_model({'outputs':stdoutputs},name,sp)
                stdcolors[side]={n:color_geometry(im,n,r,out,None,(stdB,) if n=='POPUP_A' else ()) for n,r in (('POPUP_A',stdA),('POPUP_B',stdB))}
            row['standard']=dict(origin=so,A=stdA.values(),B=stdB.values(),colors=stdcolors,buttons=pair([b for b in buttons if 'target=POPUP_B ' in b],'POPUP_B'),root_clip_clear='source + pixels; no explicit clear trace NOT PROVEN',A_survived_explicit_B_close='NOT REPLAYED')
            standard_rects={'TOPLEVEL':stdtop,'POPUP_A':stdA,'POPUP_B':stdB}
        elif 'close_b' in dirname:
            require('COMMAND close_b DONE' in text and not done,'historical-explicit-B-close')
            closepos=text.index('COMMAND close_b DONE')
            require(text.index('POPUP_B DESTROY ')<closepos<text.index('POPUP_A DESTROY '),'historical-A-survives-B-close')
            Aevents=[b for b in text[closepos:].splitlines() if b.startswith('POINTER_BUTTON ')]
            row['explicit_B_close']=dict(status='PASS historical',A_buttons=pair(Aevents,'POPUP_A'),A_mapped_until_owner_close=True,B_reopened=False)
            require(text.count('POPUP_B MAP ')==1,'historical-no-B-reopen')
            closecolors={}
            for side,name in (('left','HEADLESS-1'),('right','HEADLESS-2')):
                im=Image.open(directory/(side+'-closed-b.png')).convert('RGB');out=output_model({'outputs':outputs},name,prov)
                closecolors[side]=color_geometry(im,'POPUP_A',A,out,clip)
                require(paint(im,'POPUP_B')['count']==0,'historical-B-color-removed')
            row['explicit_B_close']['colors']=closecolors
        elif done:
            start=text.index('POPUP_B POPUP_DONE ')
            # CONTRACT: earlier visible buttons are distinct from the final
            # forbidden action; all observed events remain in the correlation.
            correlation=correlate_historical(text,injections,{'TOPLEVEL':top,'POPUP_A':A,'POPUP_B':B})
            row['dismissal']=dismissal(text[start:],correlation['forbidden_buttons'])
            row['visible_buttons_before_forbidden_action']=[e for e in correlation['buttons'] if e['action']<correlation['actions'][-1]['index']]
        row['input_correlation']=correlate_historical(text,injections,{'TOPLEVEL':top,'POPUP_A':A,'POPUP_B':B},standard_rects if 'toggle' in dirname else None)
        results.append(row)
    save(lab,'historical-replay',dict(status='PASS sampled historical facts',cases=results,missing={'new-static-popups':'NOT REPLAYED','atomic-generation':'NOT TESTED','new-standard-A-after-B-close':'NOT REPLAYED'}))
    save(lab,'popup-root',{'status':'PASS historical replay','cases':[{k:r.get(k) for k in ('case','origin','A','clip')} for r in results]})
    save(lab,'popup-nested',{'status':'PASS historical replay','cases':[{k:r.get(k) for k in ('case','B','protocol','standard','dismissal')} for r in results]})
    return results


def main():
    p=argparse.ArgumentParser();p.add_argument('lab',type=Path);args=p.parse_args()
    replay_native(args.lab);replay_nested(args.lab)
    save(args.lab,'positioner',dict(status='PASS source-backed prediction',flags=0,A=[100,80,350,170],B=[100,60,300,130],predicted_content_origin=[-318,25],predicted_A=[-218,105,350,170],predicted_B=[-118,165,300,130],runtime='NOT TESTED; actual configure/ACK/map required'))
    print('Historical geometry replays PASS; new runtime NOT TESTED')

if __name__=='__main__':main()
