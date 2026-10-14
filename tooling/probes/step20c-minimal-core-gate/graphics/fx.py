from gate import LAB
"""EXPERIMENTAL bounded FX campaign: 16 PNGs, no compositor implementation.

WHY: earlier whole-H1 equality aborted before normal client close. Differences
are evidence, never an exception preventing the lifetime measurement. Geometry
and ROIs are recorded prospectively; no anomaly-dependent mask is allowed.
"""
import hashlib
import sys
import time
from pathlib import Path
import fx_validators as v
import validators


def center_roi(s, name):
    from geometry import assigned_origin, intersection, global_png, need
    owner=s.find(name)
    floating=owner.get('floating','auto_off').endswith('on')
    origin=s.owner(name)['origin'] if s.spec['mode']=='mosaic' and not floating else assigned_origin(owner)
    win=owner['window_rect']; rect=intersection([*origin,win['width'],win['height']],s.outputs[0]['logical'])
    need(rect[2]>=80 and rect[3]>=80,'visible fixed FX center')
    p=global_png([rect[0]+rect[2]//2,rect[1]+rect[3]//2],s.outputs[0],s.frames['HEADLESS-1'])
    return [p[0]-32,p[1]-32,p[0]+32,p[1]+32]


def preset(s, name):
    # CONTRACT: edges/outside are fixed before the first relevant image; center
    # is chosen from fresh applied owner geometry, never from a pixel anomaly.
    rois=dict(center=center_roi(s,name),left=[0,0,32,600],right=[768,0,800,600],
        top=[0,0,800,32],bottom=[0,568,800,600],outside=[0,100,32,500],witness=[32,32,96,96])
    return rois


def spawn_fx(s,name,mode):
    old=s.env.get('MOSAIC_FX_SHM_DIR');s.env['MOSAIC_FX_SHM_DIR']=str(s.run)
    try:
        p=s.spawn(name,[LAB/'graphics/clients/fx-client',mode],True)
    finally:
        if old is None:s.env.pop('MOSAIC_FX_SHM_DIR',None)
        else:s.env['MOSAIC_FX_SHM_DIR']=old
    if mode!='background':s.wait(lambda:s.find(name));time.sleep(.25)
    return p


def source_hash(s,mode):
    rows=v.sources(s.run,s.log(mode))['rows']
    v.require(rows,'SHM source recorded')
    return rows[-1]['sha256']


def effects_verdict(closes, source, h2, witnessed, shadow_result):
    # WHY: measured shadow spill previously did not affect the verdict.
    # CONTRACT: the entire H2 RGB image must be exact, including shadow-on.
    # INVARIANT: call only after all normal closes; retain numeric spill evidence.
    passed=all(x['status']=='PASS' for x in closes.values())
    passed=passed and source['ABA_byte_exact'] and h2['exact'] and witnessed and shadow_result['spill']['exact']
    return 'PARTIALLY_FEASIBLE' if passed else 'INCONCLUSIVE'


def effects_campaign(s):
    from cases import init_reference, stable_reference
    from geometry import need
    need(s.spec['campaign']=='FX','explicit FX campaign')
    need(s.outputs[0]['logical']==[-800,0,800,600] and s.outputs[1]['logical']==[0,0,800,600]
        and all(o['scale']==1 and o['transform']=='normal' for o in s.outputs),'fixed FX geometry')
    s.cmd('output HEADLESS-1 bg #1e1e2e solid_color')
    init_reference(s,0);baseline=s.capture('H2-reference1','HEADLESS-2');need(all(c==(48,48,56) for c in baseline.getdata()),'whole reference uniform')
    bg=spawn_fx(s,'background','background')
    s.wait(lambda:'BACKGROUND_CONFIGURED' in s.log('background'))
    s.client_cmd('background','A','COMMAND A DONE');time.sleep(.2)
    witness_box=[32,32,96,96]
    s.save('fx-witness-roi',dict(roi=witness_box,established_ns=time.monotonic_ns()))
    witness=None  # 1 PNG
    witnessed=False
    s.save('fx-background-witness',dict(roi=witness_box,high_frequency_visible=witnessed,
        source=v.sources(s.run,s.log('background')),zorder='background layer below transparent filler and glass'))
    spawn_fx(s,'filler0','filler');s.cmd(f'[con_id={s.find("filler0")["id"]}] border none')
    spawn_fx(s,'glass','glass');gid=s.find('glass')['id'];s.cmd(f'[con_id={gid}] border none')
    s.cmd(f'[con_id={gid}] focus');s.calibrate('glass')
    for cmd in ('gaps inner 24','blur_xray disable','blur_radius 5','blur_passes 3',
        'blur_noise 0','blur_brightness 1','blur_contrast 1','blur_saturation 1',
        'shadow_offset 20 0','shadow_blur_radius 16','shadow_color #000000A0'):
        s.cmd(cmd)
    s.save('fx-shadow-rois',preset(s,'glass'));s.owner('glass')
    off=s.capture('FX-off-H1','HEADLESS-1');witnessed=v.adjacent(off,witness_box)>20
    s.cmd(f'[con_id={gid}] shadows enable',True);time.sleep(.25)
    shadow=s.capture('shadow-on-H1','HEADLESS-1');shadow_h2=s.capture('shadow-on-H2','HEADLESS-2')  # 3 PNG
    try:validators.shadow(off,shadow);shadow_status='EXERCISED'
    except ValueError:shadow_status='SHADOW_NOT_EXERCISED'
    shadow_result=dict(status=shadow_status,
        actual_RGB=v.diff(off,shadow),spill=v.diff(baseline,shadow_h2),
        meaning='pristine crossing spill control versus Mosaic sampled adjacent-output absence',
        enabled_command=True,complete_shadow_geometry='NOT PROVEN')
    s.cmd(f'[con_id={gid}] shadows disable',True)
    s.cmd(f'[con_id={gid}] floating enable',True)
    s.cmd(f'[con_id={gid}] resize set width 300 px height 200 px')
    s.cmd(f'[con_id={gid}] move absolute position -650 200');time.sleep(.25)
    classic_rois=preset(s,'glass');s.save('fx-classic-rois',classic_rois)
    floating=s.find('glass');s.save('fx-classic-state',floating)
    need(floating['rect']['x']>=-800 and floating['rect']['x']+floating['rect']['width']<=0,'classic wholly H1')
    before=source_hash(s,'glass');classic_off=s.capture('classic-off-H1','HEADLESS-1')
    trace_start=len(s.log('compositor'));s.cmd(f'[con_id={gid}] blur enable',True);time.sleep(.25)
    classic_on=s.capture('classic-blur-H1','HEADLESS-1')  # 2 PNG
    native='NOT OBSERVABLE; CORE OPT instrumentation removed'
    path=dict(selection='source floating overlap -> classic, blur_xray disabled',native=native,
        nonempty_region=bool(v.diff(classic_off,classic_on,classic_rois['center'])['pixels']),
        region_evidence='actual changed fixed interior RGB; native filter extents NOT OBSERVABLE')
    classic_result=v.classic(classic_off,classic_on,classic_rois['center'],before==source_hash(s,'glass'),path,witnessed)
    s.save('fx-classic',classic_result)
    s.cmd(f'[con_id={gid}] floating disable',True);time.sleep(.25);s.calibrate('glass')
    s.cmd(f'[con_id={gid}] blur disable',True);s.cmd(f'[con_id={gid}] blur enable',True);time.sleep(.25)
    opt_rois=preset(s,'glass');s.save('fx-rois',dict(optimized=opt_rois,classic=classic_rois,
        established_ns=time.monotonic_ns(),mask=None))
    states=[];images=[]
    for tag,command in (('optimized-A',None),('optimized-B','B'),('optimized-A-return','A')):
        if command:s.client_cmd('background',command,'COMMAND '+command+' DONE');time.sleep(.25)
        states.append(s.owner('glass'));s.save(tag+'-state',states[-1])
        images.append(s.pair_capture(tag))  # 6 PNG
    restoration=v.restoration(images[0][0],images[1][0],images[2][0],opt_rois)
    # Whole-H1 failures deliberately do not abort normal close.
    source=v.sources(s.run,s.log('background'))
    opt=dict(restoration=restoration,source=source,native=dict(status='NOT OBSERVABLE',reason='CORE OPT instrumentation removed'),
        source_selection='settled tiled owner -> optimized; animation path must be inspected in retained trace',
        state_ids=[st['owner']['id'] for st in states],wholeH2=[v.diff(baseline,p[1]) for p in images])
    s.save('fx-optimized',opt)
    for pair in images:validators.rgb(baseline,pair[1])
    close=[]
    for name in ('glass','background','filler0'):
        s.client_cmd(name,'close')
        code=s.proc[name].wait(timeout=3)
        if name!='background':s.wait(lambda:s.find(name) is None)
        alive=s.comp.poll() is None
        s.record('fx-normal-close',name=name,exit=code,compositor_alive=alive)
        close.append((name,code,alive))
    time.sleep(.2);final=s.pair_capture('final')  # 2 PNG, total 16
    h1_gone=all(c==(30,30,46) for c in final[0].getdata())
    h2=v.diff(baseline,final[1])
    closes={name:v.normalclose(s.log(name),code,alive,h1_gone) for name,code,alive in close}
    result=dict(status=effects_verdict(closes,source,h2,witnessed,shadow_result),
        classic=classic_result,optimized=opt,wholeH1=restoration['wholeH1'],wholeH2_final=h2,
        damage=dict(status='NOT PROVEN',raw=[l for l in s.log('compositor').splitlines() if 'DAMAGE' in l],
            complete_frames='NOT PROVEN'),normalclose=closes,shadow=shadow_result,
        unknown_GPU_lifetime='NOT PROVEN',capture_count=14,
        production='NOT YET SUPPORTED; experimental fixture only')
    s.save('effects-evidence',result)
    # Native OPT traces removed; no cache identity inference on CORE.
    return result['status']
