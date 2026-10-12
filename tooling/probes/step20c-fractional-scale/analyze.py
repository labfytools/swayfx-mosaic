"""Physical PNG analysis with predeclared logical ROIs; no border exclusions."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
from PIL import Image, ImageChops, ImageDraw, ImageStat

ROIS = {'left': {'interior': (300,100,700,500), 'boundary': (720,50,800,550)},
        'right': {'boundary': (0,50,80,550), 'reference': (250,250,550,500)}}
COLORS = {'A': (224,192,32), 'B': (32,208,160)}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def nonzero(d):
    r,g,b=d.split()
    return ImageChops.lighter(ImageChops.lighter(r,g),b)

def diff(a,b):
    d=ImageChops.difference(a,b)
    return {'compared_pixels': a.width*a.height,
            'modified_pixels': a.width*a.height-nonzero(d).histogram()[0],
            'bbox': d.getbbox()}

def physical(box,scale):
    # CONTRACT: conservative ROI containment; not a substituted render-box rule.
    return [math.floor(box[0]*scale), math.floor(box[1]*scale),
            math.ceil(box[2]*scale), math.ceil(box[3]*scale)]

def analyze(run):
    events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
    geoms={(e['tag'],e['output']):e for e in events if e['kind']=='capture_geometry'}
    log=(run/'compositor.log').read_text(errors='replace')
    # WHY: source audit establishes these extents are already buffer-local.
    # INVARIANT: no second scale conversion of TEMPORAL_DAMAGE.
    damages=[(int(ns),out,list(map(int,box))) for ns,out,*box in
             re.findall(r'TEMPORAL_DAMAGE ordinal=\d+ ns=(\d+) output=(\S+) extent=(-?\d+),(-?\d+)\.\.(-?\d+),(-?\d+)',log)]
    captures=[];previous={};images={};transitions=[]
    for e in events:
        if e['kind']!='capture':continue
        path=run/e['path'];g=geoms[(e['tag'],e['output'])]
        side='left' if e['output']=='HEADLESS-1' else 'right'
        im=Image.open(path).convert('RGB');images[(side,e['tag'])]=im
        assert list(im.size)==g['dimensions']==[g['mode']['width'],g['mode']['height']]
        obs={'file':path.name,'sha256':sha(path),'geometry':g,'before_ns':e['before_ns'],
             'after_ns':e['after_ns'],'coordinate_source':'get_outputs + explicit per-output grim scale',
             'roi':{},'client_pixels':{},'edge_columns':{},
             'hit_evidence':{'client_log_sha256':sha(run/'client.log') if (run/'client.log').exists() else None,
                             'pointer_log_sha256':sha(run/'pointer.log') if (run/'pointer.log').exists() else None,
                             'scope':'ordered run events; no atomic capture/input identity'}}
        for name,box in ROIS[side].items():
            pb=physical(box,g['scale']);roi=im.crop(pb)
            obs['roi'][name]={'logical':box,'physical':pb,'pixels':roi.width*roi.height}
        for name,col in COLORS.items():
            delta=ImageChops.difference(im,Image.new('RGB',im.size,col))
            mask=nonzero(delta).point(lambda v: 255 if v == 0 else 0)
            obs['client_pixels'][name]={'exact_pixels':mask.histogram()[255], 'bbox':mask.getbbox()}
        # Entire predeclared columns, not selected after inspecting anomalies.
        cols=list(range(0,min(4,im.width))) if side=='right' else list(range(im.width-4,im.width))
        for x in cols:
            obs['edge_columns'][str(x)]={name:sum(im.getpixel((x,y))==c for y in range(im.height)) for name,c in COLORS.items()}
        if side in previous:
            older,oldim=previous[side]
            intervals=[box for ns,out,box in damages if out==e['output'] and older['after_ns']<ns<=e['after_ns']]
            mask=Image.new('1',im.size,0);draw=ImageDraw.Draw(mask)
            for box in intervals:draw.rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=1)
            delta=ImageChops.difference(oldim,im)
            changed=nonzero(delta).point(lambda v: 255 if v else 0)
            uncovered=ImageChops.subtract(changed,mask.convert('L'))
            outside=uncovered.histogram()[255]
            transitions.append({'side':side,'from':older['tag'],'to':e['tag'],**diff(oldim,im),
                'damage_coordinate_source':'TEMPORAL_DAMAGE physical buffer-local',
                'damage_extents':intervals,'changed_outside_damage':outside if damages else None})
        previous[side]=(e,im);captures.append(obs)
    comparisons=[]
    for side in ROIS:
        base=images.get((side,'FX0-off'))
        if base:
            scale=next(g['scale'] for (tag,out),g in geoms.items() if out==('HEADLESS-1' if side=='left' else 'HEADLESS-2'))
            for tag in ('FX1-shadow','FX2-blur','FX4-combined'):
                if (side,tag) not in images:continue
                im=images[(side,tag)]
                entry={'side':side,'phase':tag,'whole':diff(base,im),'rois':{}}
                for name,box in ROIS[side].items():
                    pb=physical(box,scale);aa=base.crop(pb);bb=im.crop(pb)
                    entry['rois'][name]=diff(aa,bb)
                    # Luminance and contrast measured in the predeclared ROI.
                    metrics=[]
                    for img in (aa,bb):
                        gray=img.convert('L')
                        horizontal=ImageChops.difference(gray.crop((1,0,img.width,img.height)),gray.crop((0,0,img.width-1,img.height)))
                        metrics.append({'luminance_stddev':ImageStat.Stat(gray).stddev[0],
                                        'mean_adjacent_contrast':ImageStat.Stat(horizontal).mean[0]})
                    entry['rois'][name]['filter_metrics_fx0_effect']=metrics
                comparisons.append(entry)
    for side in ROIS:
        ref_tag='S1-effects-off-reference' if (side,'S1-effects-off-reference') in images else 'S1-opaque-reference'
        if (side,ref_tag) in images and (side,'S2-chain-stable') in images:
            first=images[(side,ref_tag)];second=images[(side,'S2-chain-stable')]
            scale=next(g['scale'] for (tag,out),g in geoms.items() if out==('HEADLESS-1' if side=='left' else 'HEADLESS-2'))
            comparisons.append({'side':side,'phase':'S2-popup-vs-reference','whole':diff(first,second),
                'rois':{name:diff(first.crop(physical(box,scale)),second.crop(physical(box,scale))) for name,box in ROIS[side].items()}})
    boxes=[]
    for chain in (e for e in events if e['kind']=='chain'):
        for name,point,offset,cfg in [('A',chain['a_global'],(40,35),chain['a_configure']),('B',chain['b_global'],(35,30),chain['b_configure'])]:
            gx,gy=point[0]-offset[0],point[1]-offset[1]
            for output,ox in [('HEADLESS-1',-800),('HEADLESS-2',0)]:
                g=next(v for (tag,out),v in geoms.items() if out==output);sc=g['scale']
                def rounded(v):return math.floor(v+0.5) if v>=0 else math.ceil(v-0.5)
                edges=[rounded((gx-ox)*sc),rounded(gy*sc),rounded((gx-ox+cfg[2])*sc),rounded((gy+cfg[3])*sc)]
                boxes.append({'popup':name,'output':output,'global_logical':[gx,gy,cfg[2],cfg[3]],
                    'rounded_destination_edges':edges,'source':'configured geometry and successfully targeted local offsets; SceneFX scale_box edge rule',
                    'viewport_physical':[0,0,g['mode']['width'],g['mode']['height']]})
    returns=[]
    for side in ROIS:
        if (side,'S5-return') in images:
            returns.append({'side':side,**diff(images[(side,'S2-chain-stable')],images[(side,'S5-return')])})
    client=(run/'client.log').read_text(errors='replace') if (run/'client.log').exists() else ''
    grabs=[]
    for name,target,serial,used in re.findall(r'(POPUP_[AB]) GRAB_REQUEST origin=wl_pointer.button target=(\S+) serial=(\d+) used=(\d+)',client):
        valid=serial==used and bool(re.search(rf'POINTER_BUTTON target={target} serial={serial} button=272 state=1',client))
        grabs.append({'popup':name,'parent':target,'received_serial':int(serial),'used_serial':int(used),'valid':valid,
                      'mapped':f'{name} MAP' in client})
    return {'run':run.name,'exit_status':json.loads((run/'exit-status.json').read_text()),
            'captures':captures,'comparisons':comparisons,'transitions':transitions,'returns':returns,
            'grabs':grabs,'physical_popup_boxes':boxes,'client_events':re.findall(r'^(?:POINTER_|POPUP_)[^\n]*',client,re.M),
            'calibration':[e for e in events if e['kind']=='pointer_calibration'],
            'scenario_events':[e for e in events if e['kind'] in ('chain','exterior_click','camera_pair_complete','standard_return_hit','boundary_hover')],
            'clip_trace':[line for line in log.splitlines() if 'PROBE_POPUP_' in line or any(t in line for t in ('PI_SCENE ', 'PI_OWNER ', 'PI_POPUP '))],
            'damage_events':len(damages)}

p=argparse.ArgumentParser();p.add_argument('lab',type=Path);args=p.parse_args();lab=args.lab.resolve()
out=lab/'fractional-results';out.mkdir(exist_ok=True)
results=[analyze(r) for r in sorted((lab/'runs').iterdir()) if (r/'exit-status.json').exists()]
(out/'analysis.json').write_text(json.dumps(results,indent=2)+'\n')
proofs=[f for r in (lab/'runs').iterdir() for f in r.rglob('*') if f.is_file()]
proofs += [f for f in lab.glob('fractional-*') if f.is_file() and f.suffix!='.lock']
proofs += [f for f in out.iterdir() if f.is_file() and f.name != 'evidence-sha256.txt']
proofs += [lab/'fx-checker.png',out/'analysis.json',lab/'effects-source-sha256.txt',lab/'effects-build-log.txt']
(out/'evidence-sha256.txt').write_text(''.join(f'{sha(f)}  {f}\n' for f in sorted(set(proofs))))
print(json.dumps({'runs':len(results),'manifest_entries':len(set(proofs)),'manifest_sha256':sha(out/'evidence-sha256.txt')}))
