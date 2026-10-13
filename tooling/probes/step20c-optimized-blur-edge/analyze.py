#!/usr/bin/env python3
"""Offline comparisons from retained pixels/events; no native causality invented.

CONTRACT: full RGB and pre-registered regions; traces absent remain absent.
INVARIANT: raw runs and original source manifests are not rewritten here.
"""
import hashlib
import json
import re
import sys
from pathlib import Path
import numpy as np
from PIL import Image

lab = Path(sys.argv[1]).resolve()
out = lab / 'results'
fixture = Path(__file__).resolve().parent
ROIS = {'center': (520,100,720,500), 'source': (20,100,160,500),
        'boundary': (720,50,800,550), 'physical_right': (750,0,800,600),
        'physical_bottom': (0,550,800,600)}
PAIRS = [('P0-FX0','P0-FX2'), ('P0-FX2','P1-B-natural'),
         ('P1-B-natural','P2-B-explicit'), ('P0-FX2','P3-A-natural'),
         ('P3-A-natural','P3-confirm')]
NAMES = ['OPT_NODE_CREATE','OPT_NODE_RENDER','OPT_BACKGROUND_COMMIT','OPT_DIRTY_SET',
         'OPT_DIRTY_CLEAR','OPT_REGEN_ATTEMPT','OPT_REGEN_RESULT','OPT_GPU_REBUILD',
         'OPT_GPU_RESULT','OPT_GPU_COPY','OPT_GPU_COPY_DRAWN','OPT_BLUR_USE',
         'OPT_CACHE_STATE','OPT_REGULAR_NODE','OPT_OUTPUT_BUFFER','PI_SCENE',
         'PI_OWNER','PI_OUTPUT_COMMIT','PI_OUTPUT_PRESENT','TEMPORAL_DAMAGE']

def write(name, value):
    (out / (name + '.json')).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def crop(image, box):
    left, top, right, bottom = box
    return image[top:bottom,left:right]

def metric(first, second):
    delta = np.abs(first.astype(np.int16) - second.astype(np.int16))
    mask = np.any(delta, axis=2)
    ys, xs = np.where(mask)
    return {'pixels': int(mask.sum()), 'total_pixels': int(mask.size),
            'max_channel': int(delta.max()), 'mean_abs_channel': float(delta.mean()),
            'bbox': [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if mask.any() else None,
            'channel_amplitude_histogram': {str(i):int(n) for i,n in enumerate(np.bincount(delta.ravel(),minlength=256)) if n},
            'changed_pixel_max_amplitude_histogram': {str(i):int(n) for i,n in enumerate(np.bincount(delta.max(axis=2).ravel(),minlength=256)) if n}}

def compare(first, second):
    return {'whole': metric(first,second),
            'ROIs': {name: metric(crop(first,box),crop(second,box)) for name,box in ROIS.items()}}

def parsed(lines, name):
    return [{'raw': line, **dict(re.findall(r'([A-Za-z_]+)=([^ ]+)',line))}
            for line in lines if re.search(r'\b' + name + r'\b',line)]

runs = {}
pixels = {}
columns = {}
rows = {}
renderers = {}
commits = {}
states = {}
geometries = {}
settings = {}
windows = {}
phase_traces = {}
damage = {}
contrast = {}
ledger = json.loads((out/'campaign-budget.json').read_text())
for mode in ('R0','R1','R2','R3'):
    run = lab/'runs'/mode
    status = json.loads((run/'exit-status.json').read_text())
    events = [json.loads(line) for line in (run/'events.jsonl').read_text().splitlines()]
    lines = (run/'compositor.log').read_text().splitlines()
    traces = {name: parsed(lines,name) for name in NAMES}
    images = {event['tag']+'-'+event['output']: np.array(Image.open(run/event['path']).convert('RGB'))
              for event in events if event['kind']=='capture'}
    runs[mode] = {'status':status,'events':events,'traces':traces,'images':images}
    renderer_event = next(e for e in events if e['kind']=='renderer_start')
    loaded = sorted(set(line.split()[-1] for line in (run/'library-maps.txt').read_text().splitlines()
                        if 'libscenefx' in line or 'libwlroots' in line))
    renderers[mode] = {'lines':[line for line in lines if any(text in line for text in
                                  ('Using OpenGL ES','GL renderer:','GL vendor:','EGL vendor:','FX RENDERER:'))],
                       'loaded_libraries':{path:sha(Path(path)) for path in loaded},
                       'binary':renderer_event['binary'],'binary_sha256':sha(Path(renderer_event['binary'])),
                       'OPT_TRACE':renderer_event['OPT_TRACE'],'native_OPT_evidence':mode=='R3'}
    client = parsed((run/'background.log').read_text().splitlines(),'CLIENT_COMMIT')
    reserves = [e for e in events if e['kind']=='mutation_reserved']
    configures = parsed((run/'background.log').read_text().splitlines(),'BACKGROUND_CONFIGURED')
    assert len(client)==ledger['modes'][mode]['mutation']==len(reserves)
    assert [c['pattern'] for c in client]==[r['pattern'] for r in reserves]
    assert all(int(c['ns'])>r['ns'] and c['size']=='800x600' for c,r in zip(client,reserves))
    assert len(status['captures'])==ledger['modes'][mode]['capture']
    assert status['duration']<150 and status['runtime_removed'] and not (run/'runtime').exists()
    commits[mode] = {'client':client,'configures':configures,'reservations':reserves,
                     'server':traces['OPT_BACKGROUND_COMMIT'],
                     'reservation_protocol':'PASS before every observed A/B image',
                     'no_configure_draw':'PASS duplicate configure ACK without autonomous image',
                     'identity_limit':'surface/buffer IDs may be reused; sequence/lifetime required'}
    states[mode] = [e for e in events if e['kind']=='graphic_state']
    geometries[mode] = {p.stem:json.loads(p.read_text()) for p in run.glob('*-outputs.json')}
    settings[mode] = {'config':(run/'config').read_text(),
                      'commands':[e for e in events if e['kind']=='ipc' and e['args'] and e['args'][0].startswith('[app_id=')],
                      'pixel_effect_gate':[e for e in events if e['kind']=='P0_gate'],
                      'setting_limit':'accepted config + source audit; filtering proves effect; no OPT parameters fabricated for untraced controls'}
    windows[mode] = status['captures']
    if status['failure']:
        pixels[mode] = {'failure':status['failure']}
        continue
    assert [c['pattern'] for c in client]==['A','B','A']
    baseline = images['P0-FX0-HEADLESS-2']
    p = {'comparisons':{},'H2_full':{},'capture_sha256':{q.name:sha(q) for q in run.glob('*.png')}}
    columns[mode] = {}; rows[mode] = {}; contrast[mode] = {}
    for first,second in PAIRS:
        key=first+' -> '+second
        a=images[first+'-HEADLESS-1']; b=images[second+'-HEADLESS-1']
        p['comparisons'][key]=compare(a,b)
        mask=np.any(a!=b,axis=2)
        columns[mode][key]=mask.sum(axis=0).astype(int).tolist()
        rows[mode][key]=mask.sum(axis=1).astype(int).tolist()
    for name,image in images.items():
        if name.endswith('HEADLESS-2'):
            p['H2_full'][name]=metric(baseline,image)
        else:
            center=crop(image,ROIS['center']).astype(float)
            luminance=center@[.2126,.7152,.0722]
            contrast[mode][name]={'luminance_std':float(luminance.std()),
                                 'adjacent_luminance':float(np.abs(np.diff(luminance,axis=1)).mean()),
                                 'mean_RGB':center.mean(axis=(0,1)).tolist()}
    # Full exposed-source calibration in every measured state, not just membership.
    x=np.arange(20,160)
    for tag,pattern in [('P0-FX0','A'),('P0-FX2','A'),('P1-B-natural','B'),('P2-B-explicit','B'),('P3-A-natural','A')]:
        colors=np.array([[245,245,245],[15,25,45]] if pattern=='A' else [[32,192,224],[176,32,64]],dtype=np.uint8)
        expected=np.broadcast_to(colors[(x//8)%2],(400,140,3))
        assert np.array_equal(expected,crop(images[tag+'-HEADLESS-1'],ROIS['source']))
    p['source_calibration']='PASS exact stripes A/B/B/A in exposed ROI'
    pixels[mode]=p
    phase_traces[mode]={}
    for tag in ('P0-FX2','P1-B-natural','P2-B-explicit','P3-A-natural'):
        capture=next(e for e in status['captures'] if e['tag']==tag and e['output']=='HEADLESS-1')
        if tag=='P0-FX2':
            start=next(e['after_ns'] for e in status['captures'] if e['tag']=='P0-reference')
        elif tag=='P2-B-explicit':
            start=next(e['ns'] for e in events if e['kind']=='explicit_cycle_start')
        else:
            start=reserves[1 if tag=='P1-B-natural' else 2]['ns']
        phase_traces[mode][tag]={'start_ns':start,'capture_before_ns':capture['before_ns'],
                                'end_ns':capture['after_ns'],
                                'trace':{name:[t for t in values if 'ns' in t and start<=int(t['ns'])<=capture['after_ns']]
                                         for name,values in traces.items()}}
    if mode!='R3':
        damage[mode]={'output_state_OPT_damage':'NOT AVAILABLE',
                      'old_scene_damage':traces['TEMPORAL_DAMAGE'],
                      'limit':'older private scene damage (if present) is not OPT output-state buffer damage; no equivalent coverage claim'}
    else:
        damage[mode]={}
        for first,second in [('P0-FX0','P0-FX2'),('P0-FX2','P1-B-natural'),('P1-B-natural','P2-B-explicit'),('P2-B-explicit','P3-A-natural')]:
            ca=next(e for e in status['captures'] if e['tag']==first and e['output']=='HEADLESS-1')
            cb=next(e for e in status['captures'] if e['tag']==second and e['output']=='HEADLESS-1')
            mask=np.any(images[first+'-HEADLESS-1']!=images[second+'-HEADLESS-1'],axis=2)
            cover=np.zeros((600,800),bool); records=[]
            for t in traces['OPT_OUTPUT_BUFFER']:
                if t['output']!='HEADLESS-1' or not ca['before_ns']<=int(t['ns'])<=cb['after_ns']:continue
                left,top,right,bottom=map(int,t['damage'].split(','));cover[max(0,top):min(600,bottom),max(0,left):min(800,right)]=True;records.append(t)
            damage[mode][first+' -> '+second]={'changed_pixels':int(mask.sum()),
                'uncovered_by_output_damage_extents':int((mask&~cover).sum()),'records':records,
                'limit':'extent union, stabilized captures only; no all-frame coverage/minimal damage/native PNG identity'}

cross={}
for first,second in [('R0','R1'),('R2','R3')]:
    key=first+' -> '+second
    a=runs[first];b=runs[second]
    comparable=not a['status']['failure'] and not b['status']['failure']
    cross[key]={'geometry_equal':states[first]==states[second], 'comparable':comparable}
    # State records contain timestamps; compare applied geometry and tags only.
    cross[key]['geometry_equal']=[(e['tag'],e['geometry']) for e in states[first]]==[(e['tag'],e['geometry']) for e in states[second]]
    if comparable and cross[key]['geometry_equal']:
        cross[key]['states']={tag:compare(a['images'][tag+'-HEADLESS-1'],b['images'][tag+'-HEADLESS-1'])
                             for tag in ('P0-FX0','P0-FX2','P1-B-natural','P2-B-explicit','P3-A-natural','P3-confirm')}
        cross[key]['H2']=metric(a['images']['P0-FX0-HEADLESS-2'],b['images']['P0-FX0-HEADLESS-2'])
    else:cross[key]['limit']='control geometry/fixture not comparable'
write('renderer-identities',renderers);write('source-commits',commits)
write('graphic-states',states);write('output-geometries',geometries);write('blur-settings',settings)
write('edge-pixel-analysis',pixels);write('column-distribution',columns);write('row-distribution',rows)
write('capture-windows',windows);write('damage-analysis',damage);write('phase-events',phase_traces)
write('filtering-analysis',contrast);write('private-trace-comparison',cross['R2 -> R3']);write('pristine-control',cross['R0 -> R1'])
for category,names in [('cache-use',['OPT_BLUR_USE','OPT_CACHE_STATE','OPT_REGULAR_NODE']),
                       ('dirty-events',['OPT_DIRTY_SET','OPT_DIRTY_CLEAR']),
                       ('regeneration-events',['OPT_REGEN_ATTEMPT','OPT_REGEN_RESULT','OPT_GPU_REBUILD','OPT_GPU_RESULT','OPT_GPU_COPY','OPT_GPU_COPY_DRAWN'])]:
    write(category,{mode:{name:data['traces'][name] for name in names} for mode,data in runs.items()})
write('matrix',{mode:{'failure':data['status']['failure'],'duration':data['status']['duration'],
                     'compositor_exit':data['status']['compositor'],'captures':len(data['status']['captures']),
                     'images':len(commits[mode]['client']),'runtime_removed':data['status']['runtime_removed']}
                for mode,data in runs.items()})
# Never infer the final scientific verdict merely from process success.
print(json.dumps({'edge_counts':{mode:{pair:value['whole'] for pair,value in data.get('comparisons',{}).items()
                                     if pair in ('P1-B-natural -> P2-B-explicit','P0-FX2 -> P3-A-natural')}
                               for mode,data in pixels.items()},
                  'cross':{key:{'geometry_equal':data['geometry_equal'],
                                'state_changed_pixels':{tag:value['whole']['pixels'] for tag,value in data.get('states',{}).items()}}
                           for key,data in cross.items()}},indent=2))
