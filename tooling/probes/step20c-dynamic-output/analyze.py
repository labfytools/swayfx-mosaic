"""Offline full-image, applied ownership, clip and physical damage evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from PIL import Image, ImageChops, ImageDraw
from campaign import read, ACTIONS

COLORS={'owner':(35,68,204),'A':(224,192,32),'B':(32,208,160),'background':(30,30,46)}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def nz(im):
    r,g,b=im.split();return ImageChops.lighter(ImageChops.lighter(r,g),b)
def difference(a,b):
    if a.size!=b.size:return {'status':'DIFFERENT_PHYSICAL_BUFFERS','before':list(a.size),'after':list(b.size)}
    mask=nz(ImageChops.difference(a,b))
    return {'status':'COMPARED','changed_pixels':a.width*a.height-mask.histogram()[0],'bbox':mask.getbbox()}
def fields(line):
    # Contract: retain raw traces as well as parsed passive state, no inferred frames.
    return dict(re.findall(r'(\w+)=([^\s]+)',line))
def analyze(run):
    events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
    log=(run/'compositor.log').read_text(errors='replace')
    traces=[{'kind':k,**fields(line),'raw':line} for line in log.splitlines() for k in ('DO_STATE','DO_POPUP','PI_SCENE','PI_OWNER','PI_POPUP','PI_OUTPUT_COMMIT','PI_OUTPUT_PRESENT') if k+' ' in line]
    damages=[{'ns':int(ns),'output':out,'extent':list(map(int,box))} for ns,out,*box in re.findall(r'TEMPORAL_DAMAGE ordinal=\d+ ns=(\d+) output=(\S+) extent=(-?\d+),(-?\d+)\.\.(-?\d+),(-?\d+)',log)]
    geoms={(e['tag'],e['output']):e for e in events if e['kind']=='capture_geometry'}
    captures=[];previous={};images={};transitions=[];stable=[];clip_checks=[]
    for e in events:
        if e['kind']!='capture':continue
        g=geoms[(e['tag'],e['output'])];im=Image.open(run/e['path']).convert('RGB');images[(e['tag'],e['output'])]=im
        assert list(im.size)==g['dimensions']==[g['mode']['width'],g['mode']['height']]
        counts={name:sum(v==col for v in im.get_flattened_data()) for name,col in COLORS.items()}
        observations={k:[t for t in traces if t['kind']==k and t.get('observer',t.get('output'))==e['output'] and int(t.get('ns',0))<=e['before_ns']][-1:] for k in ('DO_STATE','PI_SCENE')}
        observation={'tag':e['tag'],'output':e['output'],'sha256':sha(run/e['path']),'geometry':g,'colors':counts,'scene':observations}
        captures.append(observation)
        state=observations['DO_STATE'];scene=observations['PI_SCENE']
        if state and scene and state[0]['workspace']==scene[0]['workspace'] and scene[0].get('clip_valid')=='1':
            sx,sy=map(int,state[0]['tile_global'].split(','));cx,cy,cw,ch=map(int,scene[0]['clip'].split(','))
            clip_checks.append({'tag':e['tag'],'output':e['output'],'workspace':scene[0]['workspace'],'applied_global_viewport':[sx+cx,sy+cy,cw,ch],'output_rect':g['rect'],'matches_output': [sx+cx,sy+cy,cw,ch]==[g['rect'][k] for k in ('x','y','width','height')],'scope':'last observed pre-capture commit callback, no atomic capture identity'})
        if e['output'] in previous:
            older,oldim=previous[e['output']];d=difference(oldim,im)
            intervals=[v for v in damages if v['output']==e['output'] and older['after_ns']<v['ns']<=e['after_ns']]
            uncovered=None
            if d['status']=='COMPARED' and damages:
                mask=Image.new('L',im.size,0);draw=ImageDraw.Draw(mask)
                for v in intervals:
                    x1,y1,x2,y2=v['extent']
                    if x2>x1 and y2>y1:draw.rectangle([x1,y1,x2-1,y2-1],fill=255)
                changed=nz(ImageChops.difference(oldim,im)).point(lambda v:255 if v else 0)
                uncovered=ImageChops.subtract(changed,mask).histogram()[255]
            resized = None
            if d['status']=='DIFFERENT_PHYSICAL_BUFFERS' and damages:
                # WHY: a resized physical buffer cannot be compared as equal-sized PNGs.
                # CONTRACT: compare common buffer-local pixels; score all new-area pixels.
                # INVARIANT: retired old-only pixels are not part of the new buffer.
                width,height=min(oldim.width,im.width),min(oldim.height,im.height)
                changed=Image.new('L',im.size,255)
                common=nz(ImageChops.difference(oldim.crop((0,0,width,height)),im.crop((0,0,width,height)))).point(lambda v:255 if v else 0)
                changed.paste(common,(0,0))
                mask=Image.new('L',im.size,0);draw=ImageDraw.Draw(mask)
                for v in intervals:
                    x1,y1,x2,y2=v['extent']
                    if x2>x1 and y2>y1:draw.rectangle([x1,y1,x2-1,y2-1],fill=255)
                resized={'common_buffer_local_pixels':width*height,
                         'new_area_pixels':im.width*im.height-width*height,
                         'changed_common_pixels':width*height-common.histogram()[0],
                         'uncovered_changed_or_new_pixels':ImageChops.subtract(changed,mask).histogram()[255],
                         'scope':'buffer-local common pixel delta and all new area, no global-world equivalence or retired-buffer claim'}
            transitions.append({'output':e['output'],'from':older['tag'],'to':e['tag'],**d,'physical_damage_extents':intervals,'uncovered_changed_pixels':uncovered,'resized_buffer_coverage':resized})
        previous[e['output']]=(e,im)
        if e['tag'].endswith('-repeat'):
            base=e['tag'][:-7]
            if (base,e['output']) in images:stable.append({'tag':base,'output':e['output'],**difference(images[(base,e['output'])],im)})
    client=(run/'client.log').read_text(errors='replace')
    grabs=[{'popup':name,'target':target,'serial':int(serial),'used':int(used),'valid':serial==used and bool(re.search(rf'POINTER_BUTTON target={target} serial={serial} button=272 state=1',client))} for name,target,serial,used in re.findall(r'(POPUP_[AB]) GRAB_REQUEST origin=wl_pointer.button target=(\S+) serial=(\d+) used=(\d+)',client)]
    popup_checks=[]
    for t in traces:
        if t['kind']=='DO_POPUP' and t.get('clip_valid')=='1' and t.get('global_valid')=='1':
            px,py=map(int,t['global'].split(','));cx,cy,cw,ch=map(int,t['clip'].split(','))
            applicable=[e for e in events if e['kind']=='state' and e['monotonic_ns']>=int(t['ns'])]
            popup_checks.append({'ns':int(t['ns']),'owner_id':t['owner_id'],'workspace':t['workspace'],'owner_output':t['owner_output'],'tree':t['tree'],'global_clip':[px+cx,py+cy,cw,ch],'local_clip':[cx,cy,cw,ch]})
    commits={(t['output'],t['commit_seq']) for t in traces if t['kind']=='PI_OUTPUT_COMMIT'}
    presents={(t['output'],t['commit_seq']) for t in traces if t['kind']=='PI_OUTPUT_PRESENT'}
    return {'run':run.name,'source_sha256':sha(run/'fixture-source.py'),'exit_status':json.loads((run/'exit-status.json').read_text()),'states':[e for e in events if e['kind']=='state'],'identities':[e for e in events if e['kind']=='identity'],'calibrations':[e for e in events if e['kind']=='pointer_calibration'],'inputs':[e for e in events if e['kind'] in ('owner_hit','forbidden_click','chain','pointer_request')],'popup_lifecycle':[e for e in events if e['kind']=='popup_lifecycle'],'grabs':grabs,'captures':captures,'stability':stable,'transitions':transitions,'tiled_clip_checks':clip_checks,'popup_clip_checks':popup_checks,'traces':traces,'damage_events':len(damages),'native_events':{'commits':len(commits),'presents':len(presents),'paired':len(commits&presents),'scope':'native private headless identity, no captured buffer identity'},'client_events':re.findall(r'^(?:POPUP_|POINTER_|TOPLEVEL)[^\n]*',client,re.M),'cleanup':[e for e in events if e['kind']=='cleanup']}

p=argparse.ArgumentParser();p.add_argument('lab',type=Path);a=p.parse_args();lab=a.lab.resolve();out=lab/'results';out.mkdir(exist_ok=True)
results=[analyze(r) for r in sorted((lab/'runs').glob('*-dynamic-*')) if (r/'exit-status.json').exists()]
state=read(lab);budget={'ledger':state,'consumed':{k:sum(ACTIONS[r['action']]==k for r in state['reservations']) for k in ('reconfiguration','migration')},'camera_pairs':0}
assert budget['consumed']['reconfiguration']<=6 and budget['consumed']['migration']<=6
mapping={'outputs-before-after':'states','workspaces':'identities','owner-identities':'identities','camera-states':'identities','popup-ownership':'popup_lifecycle','scene-clips':'tiled_clip_checks','pointer-calibration':'calibrations','input-delivery':'inputs','damage-analysis':'transitions','pixel-analysis':'captures','transition-timeline':'traces'}
(out/'analysis.json').write_text(json.dumps(results,indent=2)+'\n')
for filename,key in mapping.items():(out/(filename+'.json')).write_text(json.dumps([{'run':r['run'],'observations':r[key]} for r in results],indent=2)+'\n')
(out/'campaign-budget.json').write_text(json.dumps(budget,indent=2)+'\n')
summary={'runs':len(results),'failed_fixtures':sum(bool(r['exit_status']['failure']) for r in results),'budget':budget,'not_tested':['max-scroll clamp branch','optimized blur','all effects','clip ablation opaque overflow','every intermediate frame','atomic applied generation','rotation','saved buffers','ABI/package']}
matrix=[]
for r in results:
    geometry={}
    for tag in ('D0','D1-popup','D2-popup','D3-popup','D5-popup'):
        samples=[e for e in r['states'] if e['tag']==tag]
        if not samples:geometry[tag]='NOT TESTED';continue
        e=samples[-1];h1=next(o for o in e['outputs'] if o['name']=='HEADLESS-1')
        wanted={'x':-960,'y':0,'width':960,'height':600} if tag=='D1-popup' else {'x':-800,'y':0,'width':800,'height':600}
        geometry[tag]='PASS' if h1['rect']==wanted and h1['current_mode']['width']==(1200 if tag=='D1-popup' else 1000) else 'INCONCLUSIVE'
    matrix.append({'run':r['run'],'applied_geometry':geometry,'identities_preserved':len(set(e['workspace_id'] for e in r['identities']))==1 and len(set(e['owner_id'] for e in r['identities']))==1,
                   'settled_captures_identical':all(s.get('changed_pixels')==0 for s in r['stability']),
                   'D5_pointer_calibration':'PASS' if len([e for e in r['calibrations'] if e['tag']=='D5'])==2 else 'NOT TESTED / fixture occlusion',
                   'all_grabs_valid':all(g['valid'] for g in r['grabs']),
                   'max_scroll_clamp_branch':'NOT TESTED','newly_included_point_hit':'NOT TESTED','popup_clipped_portion_after_migration':'NOT EXERCISED: measured Mosaic camera fully contains popup rectangles',
                   'opaque_owner_visibility':'sampled XRGB pixels and owner hits; independent unclipped tiled spill control NOT TESTED',
                   'effects':'NOT TESTED: shadows and blur disabled'})
summary['result']='PARTIALLY_FEASIBLE' if len(results)==3 and all(all(v=='PASS' for v in m['applied_geometry'].values()) and m['identities_preserved'] and m['settled_captures_identical'] and m['all_grabs_valid'] for m in matrix) else 'INCONCLUSIVE'
summary['architectural_conclusion']='DYNAMIC_OUTPUT_OWNERSHIP_FEASIBLE_FOR_TESTED_MATRIX' if summary['result']=='PARTIALLY_FEASIBLE' else 'UNDECIDED'
summary['not_tested'] += ['clipped-popup portion after migration at measured camera','newly included viewport point hit','D5 standard-control calibration due reference occlusion']
(out/'matrix.json').write_text(json.dumps(matrix,indent=2)+'\n')
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
files=sorted(set([p for p in (lab/'runs').rglob('*') if p.is_file()]+[p for p in out.iterdir() if p.is_file() and p.name!='evidence-sha256.txt']+list(lab.glob('dynamic-*.py'))+[lab/'dynamic-campaign-budget.json',lab/'dynamic-build-log.txt']))
manifest=out/'evidence-sha256.txt';manifest.write_text(''.join(sha(p)+'  '+str(p)+'\n' for p in files))
print(json.dumps({'runs':len(results),'summary':summary,'entries':len(files),'manifest_sha256':sha(manifest)}))
