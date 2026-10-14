"""EXPERIMENTAL shared FX predicates; no compositor or graphics launcher.

The same functions validate synthetic negative tests, retained evidence and live
captures. Whole images are authoritative: fixed ROIs explain, never mask, defects.
Client SHM object IDs are connection-local and never output/cache identities.
"""
import hashlib
import re
import struct
import sys
from pathlib import Path
from PIL import Image, ImageChops


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rgb(image):
    return Image.open(image).convert('RGB') if isinstance(image, (str, Path)) else image.convert('RGB')


def diff(a, b, roi=None, mask=None):
    require(mask is None, 'pixel masks are forbidden')
    a, b = rgb(a), rgb(b)
    require(a.size == b.size, 'different image dimensions')
    if roi is not None:
        require(len(roi) == 4 and all(type(v) is int for v in roi), 'ROI integers')
        x, y, r, t = roi
        require(0 <= x < r <= a.width and 0 <= y < t <= a.height, 'ROI outside image or empty')
        a, b = a.crop(roi), b.crop(roi)
    delta = ImageChops.difference(a, b)
    hist = [c.histogram() for c in delta.split()]
    data = delta.tobytes()
    return dict(pixels=sum(any(data[i:i+3]) for i in range(0, len(data), 3)),
        bbox=list(delta.getbbox()) if delta.getbbox() else None,
        perchannel=[dict(changed=sum(h[1:]), total_abs=sum(i*n for i,n in enumerate(h)),
            max_abs=max((i for i,n in enumerate(h) if n), default=0)) for h in hist],
        size=list(a.size), roi=roi, exact=a.tobytes() == b.tobytes())


def adjacent(image, roi):
    image = rgb(image)
    diff(image, image, roi)  # validates the prospective ROI without padding
    im = image.crop(roi)
    require(im.width > 1, 'adjacent metric ROI width')
    total = sum(sum(abs(a-b) for a,b in zip(im.getpixel((x,y)), im.getpixel((x+1,y))))
        for y in range(im.height) for x in range(im.width-1))
    return total/(im.height*(im.width-1)*3)


def classic(off, on, roi, source_same, path, witness):
    change = diff(off, on, roi)
    before, after = adjacent(off, roi), adjacent(on, roi)
    exercised = bool(source_same and path.get('nonempty_region') and witness
        and change['pixels'] and after < before)
    return dict(status='EXERCISED' if exercised else 'CLASSIC_BLUR_NOT_EXERCISED',
        difference=change, adjacent_off=before, adjacent_on=after, source_same=source_same,
        path=path, background_witness=witness,
        meaning='same-source off/on distinguishes filtering from alpha compositing')


def restoration(a, b, returned, rois):
    # CONTRACT: whole-H1 differences must survive even if center restoration passes.
    return dict(wholeH1=diff(a, returned), changed_AB=diff(a,b),
        rois={name:dict(AB=diff(a,b,box), AA=diff(a,returned,box)) for name,box in rois.items()},
        status='EXACT' if diff(a, returned)['exact'] else 'WHOLE_H1_DIFFERENT')


def cache(trace):
    rows=[l for l in trace.splitlines() if any(k in l for k in
        ('OPT_DIRTY_SET ', 'OPT_REGEN_ATTEMPT ', 'OPT_REGEN_RESULT ', 'OPT_DIRTY_CLEAR ', 'OPT_BLUR_USE '))]
    episodes=[]; dirty={}; attempts={}; regenerated={}; cleared={}
    for line in rows:
        f=dict(re.findall(r'(\w+)=([^\s]+)',line));node=f.get('node');output=f.get('output')
        if 'OPT_DIRTY_SET ' in line and f.get('enabled')=='1' and f.get('size')=='800x600':
            dirty[node]=line
        elif 'OPT_REGEN_ATTEMPT ' in line and node in dirty and f.get('dirty')=='1':
            attempts[node]=(output,line)
        elif 'OPT_REGEN_RESULT ' in line and node in attempts and f.get('result')=='1' and output==attempts[node][0]:
            regenerated[node]=(output,line)
        elif 'OPT_DIRTY_CLEAR ' in line and node in regenerated and f.get('dirty')=='0' and output==regenerated[node][0]:
            cleared[output]=dict(node=node,dirty=dirty[node],attempt=attempts[node][1],
                result=regenerated[node][1],clear=line)
        elif 'OPT_BLUR_USE ' in line and output in cleared and f.get('optimized')=='1' and f.get('chosen') not in (None,'(nil)','0x0'):
            ep={**cleared[output], 'use':line};episodes.append(ep)
    return dict(status='NATIVE_OBSERVED' if episodes else 'CACHE_NOT_EXERCISED' if rows else 'NOT OBSERVABLE',
        rows=rows, episodes=episodes,identity='node-correlated regeneration then output-correlated cache use; client IDs remain separate',
        causal_dirty_regeneration_ABA='NOT PROVEN by aggregate trace presence')


def sources(run, log):
    rows=[]
    for line in log.splitlines():
        if not line.startswith('SHM_SOURCE '):
            continue
        fields=dict(re.findall(r'(\w+)=([^\s]+)',line))
        p=Path(fields['path'])
        require(p.resolve().parent == Path(run).resolve(), 'SHM outside owned run')
        raw=p.read_bytes()
        require(len(raw)==int(fields['bytes']), 'SHM byte count')
        stride=int(fields['stride'])
        require(stride>0 and stride%4==0 and len(raw)%stride==0, 'SHM stride/size')
        width,height=stride//4,len(raw)//stride
        endian='<' if sys.byteorder=='little' else '>'
        if fields['mode']=='background':
            require(width==800 and height==600 and fields['format']=='XRGB8888', 'background format/geometry')
            colors=[int(x,16) for x in fields['colors'].split(',')]
            require(len(colors)==2, 'background palette')
            row=b''.join(struct.pack(endian+'I',colors[x//8%2]) for x in range(width))
            require(raw==row*height, 'background high-frequency source bytes')
        elif fields['mode'] in ('glass','filler'):
            color=0x88442010 if fields['mode']=='glass' else 0
            require(fields['format']=='ARGB8888' and raw==struct.pack(endian+'I',color)*(width*height),
                'glass/filler premultiplied source bytes')
        fields.update(sha256=hashlib.sha256(raw).hexdigest(), actual_bytes=len(raw),
            width=width,height=height,byteorder=sys.byteorder)
        rows.append(fields)
    bg=[r for r in rows if r['mode']=='background']
    valid=(len(bg)==3 and bg[0]['sha256']==bg[2]['sha256'] and bg[0]['sha256']!=bg[1]['sha256'])
    return dict(rows=rows, ABA_byte_exact=valid, format_endianness='native uint32_t; little-endian expected and separately recorded')


def normalclose(log, code, compositor_alive, gone):
    lines=log.splitlines(); close=[(i,l) for i,l in enumerate(lines) if l.startswith('CLOSE_RECEIVED ')]
    destroy=[(i,l) for i,l in enumerate(lines) if l.startswith('OBJECTS_DESTROYED ')]
    exits=[(i,l) for i,l in enumerate(lines) if l.startswith('EXIT ')]
    releases=[l for l in lines if l.startswith('RELEASE ')]
    commit_after=bool(close and any(l.startswith('CLIENT_COMMIT ') for l in lines[close[0][0]+1:]))
    ok=(code==0 and compositor_alive and gone and len(close)==len(destroy)==len(exits)==1
        and close[0][0]<destroy[0][0]<exits[0][0] and 'error=0 ' in exits[0][1]
        and 'normalclose=1 ' in exits[0][1] and bool(releases) and not commit_after)
    return dict(status='PASS' if ok else 'FAIL', code=code, compositor_alive=compositor_alive,
        pixels_gone=gone, command_received=[l for _,l in close], objects_destroyed=[l for _,l in destroy],
        exits=[l for _,l in exits], release_callbacks=releases, commit_after_close=commit_after,
        GPU_lifetime='NOT PROVEN; SHM releases and normal object teardown are separate observations')


def validate_run(run):
    """Post-run entry also usable on retained old runs; missing proof stays absent."""
    import json
    run=Path(run)
    names=('optimized-A','optimized-B','optimized-A-return')
    result={'schema':'experimental-fx-v1','historical':not (run/'fx-rois.json').exists()}
    rois=json.loads((run/'fx-rois.json').read_text())['optimized'] if (run/'fx-rois.json').exists() else {'center':[300,250,364,314]}
    if all((run/(name+'-H1.png')).exists() for name in names):
        result['optimized']=restoration(*(run/(name+'-H1.png') for name in names),rois)
    for output in ('H1','H2'):
        a,b=run/('classic-off-'+output+'.png'),run/('classic-blur-'+output+'.png')
        if a.exists() and b.exists():result['classic_'+output]=diff(a,b)
    ref=run/'H2-reference1.png'
    if ref.exists():result['wholeH2']={p.name:diff(ref,p) for p in sorted(run.glob('*-H2.png'))}
    trace=(run/'compositor.log').read_text(errors='replace')
    result['cache']=cache(trace)
    result['clients']={name:normalclose((run/(name+'.log')).read_text(errors='replace'),
        None,False,False) for name in ('glass','background') if (run/(name+'.log')).exists()}
    result['normalclose']='NOT PROVEN offline without explicit recorded live-compositor/pixel proof'
    if (run/'effects-evidence.json').exists() and (run/'events.jsonl').exists() and (run/'final-H1.png').exists():
        events=[json.loads(l) for l in (run/'events.jsonl').read_text().splitlines()]
        close={e['name']:e for e in events if e['kind']=='fx-normal-close'}
        final=rgb(run/'final-H1.png');gone=all(c==(30,30,46) for c in final.getdata())
        result['clients']={name:normalclose((run/(name+'.log')).read_text(errors='replace'),
            e['exit'],e['compositor_alive'],gone) for name,e in close.items()}
        result['normalclose']='PASS' if set(close)=={'glass','background','filler0'} and all(
            r['status']=='PASS' for r in result['clients'].values()) else 'FAIL'
        evidence=json.loads((run/'effects-evidence.json').read_text())
        result['classic']=classic(run/'classic-off-H1.png',run/'classic-blur-H1.png',
            json.loads((run/'fx-rois.json').read_text())['classic']['center'],
            evidence['classic']['source_same'],evidence['classic']['path'],evidence['classic']['background_witness'])
        result['sources']=sources(run,(run/'background.log').read_text(errors='replace'))
    return result
