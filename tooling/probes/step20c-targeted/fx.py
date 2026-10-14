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


def center_roi(s, name):
    from geometry import assigned_origin, actual_origin, intersection, global_png, need
    owner=s.find(name)
    floating=owner.get('floating','auto_off').endswith('on')
    origin=actual_origin(owner,s.log('compositor'))[0] if s.spec['mode']=='mosaic' and not floating else assigned_origin(owner)
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
        p=s.spawn(name,[s.lab/'clients/fx-client',mode],True)
    finally:
        if old is None:s.env.pop('MOSAIC_FX_SHM_DIR',None)
        else:s.env['MOSAIC_FX_SHM_DIR']=old
    if mode!='background':s.wait(lambda:s.find(name));time.sleep(.25)
    return p


def source_hash(s,mode):
    rows=v.sources(s.run,s.log(mode))['rows']
    v.require(rows,'SHM source recorded')
    return rows[-1]['sha256']


def effects_campaign(s):
    from cases import init_reference, stable_reference
    from geometry import need
    need(s.spec['campaign']=='FX','explicit FX campaign')
    need(s.outputs[0]['logical']==[-800,0,800,600] and s.outputs[1]['logical']==[0,0,800,600]
        and all(o['scale']==1 and o['transform']=='normal' for o in s.outputs),'fixed FX geometry')
    s.cmd('output HEADLESS-1 bg #1e1e2e solid_color')
    init_reference(s,0);baseline=stable_reference(s)  # 2 PNG
    bg=spawn_fx(s,'background','background')
    s.wait(lambda:'BACKGROUND_CONFIGURED' in s.log('background'))
    s.client_cmd('background','A','COMMAND A DONE');time.sleep(.2)
    witness_box=[32,32,96,96]
    s.save('fx-witness-roi',dict(roi=witness_box,established_ns=time.monotonic_ns()))
    witness=s.capture('background-witness-H1','HEADLESS-1')  # 1 PNG
    witnessed=v.adjacent(witness,witness_box)>20
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
    off=s.capture('FX-off-H1','HEADLESS-1')
    s.cmd(f'[con_id={gid}] shadows enable',True);time.sleep(.25)
    shadow=s.capture('shadow-on-H1','HEADLESS-1');shadow_h2=s.capture('shadow-on-H2','HEADLESS-2')  # 3 PNG
    shadow_result=dict(status='EXERCISED' if v.diff(off,shadow)['pixels'] else 'SHADOW_NOT_EXERCISED',
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
    native=[l for l in s.log('compositor')[trace_start:].splitlines() if 'OPT_BLUR_USE ' in l and 'optimized=0' in l]
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
    opt=dict(restoration=restoration,source=source,native=v.cache(s.log('compositor')),
        source_selection='settled tiled owner -> optimized; animation path must be inspected in retained trace',
        state_ids=[st['owner']['id'] for st in states],wholeH2=[v.diff(baseline,p[1]) for p in images])
    s.save('fx-optimized',opt)
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
    result=dict(status='PARTIALLY_FEASIBLE' if all(x['status']=='PASS' for x in closes.values()) else 'INCONCLUSIVE',
        classic=classic_result,optimized=opt,wholeH1=restoration['wholeH1'],wholeH2_final=h2,
        damage=dict(status='NOT PROVEN',raw=[l for l in s.log('compositor').splitlines() if 'DAMAGE' in l],
            complete_frames='NOT PROVEN'),normalclose=closes,shadow=shadow_result,
        unknown_GPU_lifetime='NOT PROVEN',capture_count=16,
        production='NOT YET SUPPORTED; experimental fixture only')
    if not source['ABA_byte_exact'] or not h2['exact'] or not witnessed:result['status']='INCONCLUSIVE'
    s.save('effects-evidence',result)
    s.save('fx-postrun',v.validate_run(s.run))
    return result['status']
