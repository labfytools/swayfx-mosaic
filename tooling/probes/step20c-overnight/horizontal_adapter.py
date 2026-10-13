"""Bounded explicit transformations of the sealed E2 runner, never a broad copy.

Generated runners are private frozen review artifacts. Reused validators retain
native/configured/assigned/applied distinctions and half-open coordinate rules.
"""
from pathlib import Path
import ast
import hashlib

BASE = Path(__file__).resolve().parent.parent / 'step20c-static-e2-completion'
BASE_SHA = '1bd67d5269b5492f5d9ac6e7b670a4db0345b0e2cd3f89930dcbd154c4473504'
REUSE = ('model.py','observations.py','ipc_predicates.py','pixels.py','predicates.py','lifecycle.py','transition.py','support.py')

def replace_one(text, old, new):
    if text.count(old) != 1:
        raise ValueError('sealed transformation occurrence mismatch: '+old[:80])
    return text.replace(old,new,1)

STANDARD_EXTERIOR = "def splith_exterior(owner, layout):\n    # Pinned sway/ipc-json.c:899-906: count=1 unless parent is stacked.\n    # This inverse is deliberately scoped to the ordinary splith controls.\n    require(layout == 'splith', 'standard-splith-only')\n    assigned = owner['rect']; deco = owner['deco_rect']['height']\n    require(type(deco) is int and deco >= 0, 'standard-decoration-height')\n    return [assigned['x'], assigned['y'] - deco,\n            assigned['width'], assigned['height'] + deco]\n\n"

STANDARD_OPEN = '''def open_standard(name):
    global stage,baseline
    reserve(lab,'chain');cmd('workspace 1')
    proc=spawn(name,[lab/'nested-client','static_cross'],debug=True)
    wait(lambda:find('org.mosaic.NestedGrabProbe',proc.pid) and 'TOPLEVEL MAP ' in log(name));time.sleep(.6)
    snap=snapshot(name+'-assigned');ws=workspace(snap['tree'],'1')
    owner=next(n for n in nodes(ws) if n.get('pid')==proc.pid)
    require(ws['layout']=='splith' and owner['visible'] and owner['focused'],'standard-owner')
    require(owner['app_id']=='org.mosaic.NestedGrabProbe' and owner['shell']=='xdg_shell','standard-owner-identity')
    refstate=validate_reference(snap,refid,ref.pid)
    inject('move',[-790,590]);first=capture('H2-reference-1','HEADLESS-2');time.sleep(.6)
    second=capture('H2-reference-2','HEADLESS-2');baseline=first
    save(lab,'reference-stability',dict(status='PASS',comparison=reference(first,second),reference=refstate))
    topim=capture(name+'-top','HEADLESS-1');bbox=paint(topim,'TOPLEVEL')['bbox'];require(bbox is not None,'standard-owner-paint')
    # C0 has no private scene trace. Current IPC assignment is explicitly named;
    # the actual painted origin and fresh pointer wire coordinates corroborate it.
    assigned=dict(owner['rect']);exterior=splith_exterior(owner,ws['layout'])
    measured=dict(id=owner['id'],workspace=ws['id'],scene=exterior,IPC=owner,
        raw='CURRENT IPC raw assignment; splith exterior inverse ipc-json.c:899-906; actual painting/input checked separately')
    applied=applied_model(measured,owner,log(name),name+'-standard-assigned-observation')
    content_rect=content(applied);origin=[content_rect.x,content_rect.y]
    require([bbox[0]-800,bbox[1]]==origin,'standard-painted-assigned-origin')
    out=output_model(snap,'HEADLESS-1',content_rect.provenance)
    verify_paint(content_rect,out,bbox,paint(topim,'TOPLEVEL')['count'])
    if CASE=='C1':
        scene=scene_from_log(log('compositor'),'HEADLESS-1');real=measure_owner(log('compositor'),owner)
        require(not scene['clip_valid'] and scene['layout_enum']==1,'standard-no-native-clip')
        require(real['scene']==measured['scene'],'standard-applied-scene-matches-assignment')
    owners[name]=dict(id=owner['id'],pid=proc.pid,workspace=ws['id'],assigned=assigned,exterior=exterior,content_origin=origin,
        native=applied.native.rectangle.values(),configured=applied.configured.values(),paint=paint(topim,'TOPLEVEL'))
    save(lab,'applied-owner-geometry',owners)
    xy=point(topim,'TOPLEVEL',-800);require(applied.native.rectangle.contains([xy[0]-origin[0],xy[1]-origin[1]]),'opening-native-bounds')
    cp=click(name+'-open-A',name,xy,True,'left');wait(lambda:'POPUP_A MAP ' in log(name));time.sleep(.25)
    correlate_pointer(name,xy,content_rect.values(),'TOPLEVEL',cp['pointer_protocol'][name])
    aim=capture(name+'-A','HEADLESS-1');xyA=point(aim,'POPUP_A',-800)
    cpB=click(name+'-open-B',name,xyA,True,'left');wait(lambda:'POPUP_B MAP ' in log(name));time.sleep(.3)
    prot=protocol(log(name));opening_pair(cp['events'][name],'TOPLEVEL',prot['grabs'][0]['serial'])
    opening_pair(cpB['events'][name],'POPUP_A',prot['grabs'][1]['serial'])
    require(not any(cp['events'][n] or cpB['events'][n] for n in ('reference','filler')),'opening-other-client')
    g=geometry(log(name),origin,content_rect.provenance);require(all(v=='EXERCISED' for v in g['crossing'].values()),'standard-root-child-crossing')
    correlate_pointer(name,xyA,g['A'],'POPUP_A',cpB['pointer_protocol'][name])
    left=capture('standard-H1','HEADLESS-1');right=capture('standard-H2','HEADLESS-2')
    rgb=popup_pixels(left,right,g,False,baseline);verify_owner_occlusion(left,right,content_rect,g,False)
    chains[name]=dict(protocol=prot,geometry=g,pixels=rgb,owner=owners[name])
    save(lab,'xdg-protocol-order',{name:prot});save(lab,'standard-popup-pixels',rgb)
    return proc,owner,g,left,right,content_rect
'''

E1 = '''    E1,owner1,g1,im1=open_chain('E1')
    stage='E1-visible-B';xy=point(im1,'POPUP_B',-800);row=click(stage,'E1',xy)
    result=delivery(row,'E1','POPUP_B');coords=correlate_pointer('E1',xy,g1['B'],'POPUP_B',row['pointer_protocol']['E1']);mapped(log('E1'))
    save(lab,'mosaic-input',dict(status='PASS',pair=result,coordinates=coords,click=row))
    stage='E1-forbidden-B';B=g1['B'];xy=[int((max(0,B[0])+min(800,B[0]+B[2]))//2),B[1]+30]
    require(B[0]<=xy[0]<B[0]+B[2] and 8<=xy[0]<792 and B[1]<=xy[1]<B[1]+B[3],'forbidden-point-real-child-H2')
    cut=len(log('E1'));row=click(stage,'E1',xy);time.sleep(.3)
    ds=dismissal(log('E1')[cut:],row['events']['E1'])
    require(not row['events']['filler'],'forbidden-wrong-filler-recipient')
    refs=row['events']['reference'];require(len(refs) in (0,2),'outside-reference-pair')
    if refs:
        require(all('button=273 ' in s for s in refs) and ['state=1' in refs[0],'state=0' in refs[1]]==[True,True],'outside-reference-button')
    save(lab,'forbidden-input',dict(status='PASS',click=row,dismissal=ds,reference_events=refs,
        interpretation='outside dismissal; reference routing recorded, no universal click-through claim'))
    inject('move',[-790,590]);clean=capture('E1-dismissed-H2','HEADLESS-2');require(equal(baseline,clean)['equal'],'dismissal-whole-H2-residue')
    close_client(E1,'E1','close_owner')
    E2,owner2,g2,im2=open_chain('E2')
    fresh_chain(dict(owner=owner1['id'],pid=E1.pid,serials=[g['serial'] for g in chains['E1']['protocol']['grabs']]),
        dict(owner=owner2['id'],pid=E2.pid,serials=[g['serial'] for g in chains['E2']['protocol']['grabs']]))
'''

def generate(case):
    if case not in ('C0','C1','C2'):raise ValueError('unknown C case')
    text=(BASE/'run.py').read_text()
    if hashlib.sha256(text.encode()).hexdigest()!=BASE_SHA:raise ValueError('sealed base changed')
    text=replace_one(text,'from authorization import authorize\n','')
    begin=text.index('p=argparse.ArgumentParser()');end=text.index("run=lab/'run';run.mkdir()")
    text=text[:begin]+'''# Gate, unique consumption and run reservation precede even runtime directory creation.
from horizontal_gate import begin_run, debit, binding_sources, finish_run
LAB,CASE,lab,auth=begin_run()
BINARY=Path(auth['binary']);BINARY_SHA=auth['binary_sha256'];WLROOTS_SHA=auth['wlroots_sha256']
def reserve(unused,*kinds):return debit(LAB,CASE,lab,*kinds)
def source_bindings():return binding_sources(auth)
import transition
transition.source_bindings=source_bindings
'''+text[end:]
    text=replace_one(text,"reserve(lab,'capture');time.sleep(.20)","reserve(lab,'capture');time.sleep(.20)")
    text=replace_one(text,"assert Path(f'/proc/{comp.pid}/exe').resolve()==lab/'swayfx-mosaic'","assert Path(f'/proc/{comp.pid}/exe').resolve()==BINARY.resolve() and sha(BINARY)==BINARY_SHA")
    text=replace_one(text,"assert not any('libscenefx' in x for x in paths)","assert CASE=='C0' or not any('libscenefx' in x for x in paths)")
    text=replace_one(text,"    save(lab,'dependency-mappings',","    if CASE=='C0':\n        scene_paths=[Path(x).resolve() for x in paths if 'libscenefx' in x]\n        require(scene_paths==[Path(auth['pristine']['scene_path'])] and sha(scene_paths[0])==auth['pristine']['scene_sha256'],'pristine mapped SceneFX identity')\n    save(lab,'dependency-mappings',")
    text=replace_one(text,"SceneFX_shared=False","SceneFX_shared=any('libscenefx' in x for x in paths)")
    marker="    outputs=ipc('-t','get_outputs');validate_outputs(outputs);save(lab,'output-geometry',outputs)"
    text=replace_one(text,marker,"""    actual=[s for s in log('compositor').splitlines() if any(k in s for k in ('Creating scenefx FX renderer','GL renderer:','Using OpenGL ES','GL vendor:'))]
    require(any('Creating scenefx FX renderer' in s for s in actual) and any('GL renderer:' in s for s in actual),'actual-renderer-log-required')
    save(lab,'actual-renderer',dict(status='PASS',source='actual compositor startup log',lines=actual,requested_env_renderer=env.get('WLR_RENDERER')))
"""+marker)
    text=replace_one(text,"    comp=spawn('compositor',[lab/'swayfx-mosaic','-d','-c',run/'config'])","    comp=spawn('compositor',[BINARY,'-d','-c',run/'config'])")
    text=replace_one(text,"    verify(lab/'results/fixture-freeze-sha256.txt')","    finish_run(LAB,CASE,lab)")
    if case=='C2':
        text=replace_one(text,"    if name=='E2':","    if name=='E1':")
        text=replace_one(text,"    content_rect=content(applied);origin=[content_rect.x,content_rect.y]","    content_rect=content(applied);origin=[content_rect.x,content_rect.y]\n    require(content_rect.x < 0 < content_rect.end[0],'real-owner-crossing')")
        text=replace_one(text,"    E2,owner2,g2,im2=open_chain('E2')\n",E1)
    else:
        text=text[:text.index('\ndef open_chain(name):')]+ '\n'+STANDARD_EXTERIOR+STANDARD_OPEN+text[text.index('\ntry:\n    comp='):]
        text=replace_one(text,";cmd('layout mosaic')",";cmd('layout splith')")
        start=text.index("    E2,owner2,g2,im2=open_chain('E2')")
        end=text.index("    stage='E2-standard-B';")
        text=text[:start]+"    E2,owner2,stdg,stdleft,stdright,stdcontent=open_standard('E2')\n"+text[end:]
        start=text.index('    # Re-examine every trace through the B input')
        end=text.index("    before_close=log('E2');",start)
        text=text[:start]+text[end:]
    ast.parse(text)
    return text
