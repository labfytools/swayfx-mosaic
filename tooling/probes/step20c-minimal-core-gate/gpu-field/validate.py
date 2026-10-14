"""EXPERIMENTAL G1 runtime validator; importable offline, no launch or writer.
WHY/CONTRACT/INVARIANT: parse actual bounded publications, never trust a PASS
field or extents for regions; rejected metadata gives no native qualification.
"""
import hashlib
import json
import struct
import os
from pathlib import Path

WIDTH, HEIGHT = 800, 600
LIMIT = 16633312
META_LIMIT = 1024 * 1024
NAMES = ('main-before-blur','down-0','down-1','down-2','up-2','up-1','up-0','cache-after-copy','output-presubmit')
FRESH = ((800,600),(400,300),(200,150),(100,75),(200,150),(400,300),(800,600),(800,600),(800,600))
BXY = ((784,292),(392,142),(192,67),(92,29),(192,67),(392,142),(784,292),(784,292),(784,292))
GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, GL_UNSIGNED_NORMALIZED = 36064, 36161, 35863
# DRM little-endian AB24/XB24; actual import formats must be recorded.
ABGR, XBGR, ARGB, XRGB = [int.from_bytes(x,'little') for x in (b'AB24',b'XB24',b'AR24',b'XR24')]

class Rejected(ValueError): pass

def need(v, msg):
    if not v: raise Rejected(msg)

def sha(data): return hashlib.sha256(data).hexdigest()

def plan(epoch, point):
    need(epoch in (1,2,3) and 0<=point<9,'epoch/point budget')
    if epoch==2 or point>=7: return (*BXY[point],16,16)
    if 3<=point<=5: return (0,0,*FRESH[point])
    return (0,0,800,600)

def read_plan():
    total=sum(plan(e,p)[2]*plan(e,p)[3]*4 for e in (1,2,3) for p in range(9))
    need(total==LIMIT and total<16*1024*1024,'planned raw budget')
    return dict(reads=27,bytes=total)

def object_identity(o):
    return tuple(o[k] if k!='dimensions' else tuple(o[k]) for k in ('fx','wlr','fbo','rbo','image','dimensions'))

def validate_object(o, role="effects"):
    need(o['dimensions']==[800,600] and all(o[k] for k in ('fx','wlr','fbo','rbo')),'existing physical object')
    need(o['dmabuf_available'] is True and o['dmabuf_size']==[800,600] and len(o['planes']) in range(1,5),'real dmabuf')
    need(o['drm_format'] in ((XBGR,) if role=='cache' else (ABGR,) if role=='effects' else (ABGR,XBGR,ARGB,XRGB)),'source compatible actual DRM format')
    need(len(o['modifier'])==16 and all(len(p)==2 and p[0]>=800*4 and p[1]>=0 for p in o['planes']),'dmabuf fields')

def validate_sample(s, raw, epoch, context, offset):
    p=s['point']; need(s['name']==NAMES[p] and s['roi']==list(plan(epoch,p)) and s['fresh']==list(FRESH[p]),'fixed ROI/fresh domain')
    x,y,w,h=s['roi'];need(x>=0 and y>=0 and w>0 and h>0 and x+w<=800 and y+h<=600,'ROI texture bounds')
    n=w*h*4;need(s['offset']==offset and s['bytes']==n and offset+n<=len(raw),'read framing/truncation')
    data=raw[offset:offset+n];need(sha(data)==s['sha256'],'sample SHA')
    need(s['before']==s['after'] and len(s['before'])==9,'READ/DRAW/RBO/PBO/pack/readbuffer restoration')
    need(s['context_before']==s['context_after']==context,'EGL context restoration')
    need(s['target_read_buffer']==GL_COLOR_ATTACHMENT0,'per-FBO readbuffer unchanged')
    a=s['attachment'];need(len(a)==8 and a[:3]==[GL_RENDERBUFFER,s['object']['rbo'],GL_UNSIGNED_NORMALIZED] and a[3]==9729 and a[4:7]==[8,8,8] and a[7] in (0,8),'actual attachment channels/type/encoding')
    need(len(s['renderbuffer'])==3 and s['renderbuffer'][:2]==[800,600] and s['renderbuffer'][2]>0,'actual RBO size/format')
    validate_object(s['object'],'cache' if p==7 else 'main' if p in (0,8) else 'effects')
    need(a[7]==(0 if s['object']['drm_format'] in (XBGR,XRGB) else 8),'alpha storage source compatibility')
    need(s['sentinel_alpha_written'] is True and 205 not in data[3::4],'sentinel incomplete read')
    need(type(s['before_ns']) is int and type(s['after_ns']) is int and 0<s['before_ns']<=s['after_ns'],'sample monotonic interval')
    need(s['valid'] is True and s['fbo_status']==36053,'C preconditions/FBO completeness failed')
    return offset+n

def validate_writes(rows, samples, context):
    writes=[r for r in rows if r['kind']=='write'];blur=[r for r in writes if r['stage']>=0]
    need(len(blur)==6 and [r['stage'] for r in blur]==list(range(6)),'six draws strict order')
    need([r['sequence'] for r in writes]==list(range(1,len(writes)+1)),'all writes ordered')
    objs=[samples[p]['object'] for p in range(7)]
    ping,pong=object_identity(objs[1]),object_identity(objs[2])
    need(ping!=pong and objs[1]['wlr']!=objs[2]['wlr'] and objs[1]['fbo']!=objs[2]['fbo'],'distinct ping/pong alias')
    need([object_identity(o) for o in objs[1:]]==[ping,pong,ping,pong,ping,pong],'same physical buffers within pass')
    for i,r in enumerate(blur):
        need(r['region']==[[0,0,*FRESH[i+1]]] and r['box']==[0,0,800,600],'exact domain union, no holes')
        need(object_identity(r['src'])==object_identity(objs[i]) and object_identity(r['dst'])==object_identity(objs[i+1]),'source/destination continuity')
        need(r['texture']==r['src']['tex'] and r['src']['tex']>0,'actual source texture mapping')
        for seen,draw_obj in ((objs[i],r['src']),(objs[i+1],r['dst'])):
            need(seen['tex']==0 or seen['tex']==draw_obj['tex'],'existing texture replaced')
        need(r['src']['wlr']!=r['dst']['wlr'] and r['src']['fbo']!=r['dst']['fbo'],'feedback alias')
        need(r['fbo']==r['dst']['fbo'] and r['context']==context and r['viewport']==[0,0,800,600],'draw FBO/context/viewport')
        need(r['blend']==r['stencil']==r['scissor_enabled']==0 and r['color_mask']==[1,1,1,1],'unmasked raster write')
        need(r['sampler']==[9729,9729,33071,33071] and r['program']>0 and r['texture']>0,'effective sampler/program')
        u={x['name']:x for x in r['uniforms']}
        need(all(k in u for k in ('radius','halfpixel','proj','tex_proj')),'effective blur uniforms/matrices')
        floats=lambda n: [struct.unpack('f',struct.pack('I',b))[0] for b in u[n]['value']]
        need(floats('radius')==[5.0] and len(floats('proj'))==len(floats('tex_proj'))==9,'uniform radius/matrix')
        expected=(1/800,1/600) if i<3 else (1/3200,1/2400)
        need(floats('halfpixel')==[struct.unpack('f',struct.pack('f',x))[0] for x in expected],'effective halfpixel')
    fbo_ids={objs[1]['fbo'],objs[2]['fbo']}
    need(not any(r['stage']<0 and r['fbo'] in fbo_ids for r in writes),'external ping/pong write')
    need(not any(r['kind']=='clear' and r['mask']&16384 for r in rows),'color clear')
    need(not any(r['kind'] in ('destroy','replace','resize','migration') for r in rows),'object lifetime/layout change')
    copies=[r for r in rows if r['kind']=='copy']
    cache=[r for r in copies if r['dst']['fbo']==samples[7]['object']['fbo']]
    need(len(cache)==1 and object_identity(cache[0]['src'])==pong and cache[0]['region']==[[0,0,800,600]],'cache copy exact source/domain')
    # Every copy includes its corresponding render write, not just a declaration.
    for c in copies:
        need(any(w['stage']==-1 and w['fbo']==c['dst']['fbo'] and w['region']==c['region'] for w in writes),'copy actual raster write missing')
    # Stages and reads alternate; no unseen color draw between output and sample.
    positions={id(r):i for i,r in enumerate(rows)}
    for i,r in enumerate(blur):
        begin=positions[id(samples[i])];end=positions[id(samples[i+1])]
        between=[w for w in writes if begin<positions[id(w)]<end]
        need(between==[r],'additional/missing write in native interval')
    return True

def validate_epoch(directory, epoch):
    d=Path(directory);need(epoch in (1,2,3),'fourth epoch')
    mp=d/f'epoch-{epoch}.meta';rp=d/f'epoch-{epoch}.rgba';arm=d/f'epoch-{epoch}.arm'
    need(arm.is_file() and not arm.is_symlink() and arm.read_bytes()==(('B' if epoch==2 else 'A')+'\n').encode(),'arm absent/invalid')
    for file in (mp,rp,arm):
        need(file.is_file() and file.stat().st_uid==os.geteuid() and file.stat().st_mode&0o777==0o600,'exclusive mode/ownership')
    need(mp.is_file() and rp.is_file() and not mp.is_symlink() and not rp.is_symlink(),'complete exclusive publication')
    need(mp.stat().st_size<=META_LIMIT and rp.stat().st_size<=8312048,'bounded publications')
    text=mp.read_bytes();need(text.endswith(b'\n'),'metadata framing')
    try: rows=[json.loads(line) for line in text.splitlines()]
    except (ValueError,UnicodeError) as e: raise Rejected('malformed metadata') from e
    need(rows and rows[0]['kind']=='begin' and rows[-1]['kind']=='end','begin/end framing')
    b,e=rows[0],rows[-1];need(b['epoch']==e['epoch']==epoch and b['label']==('B' if epoch==2 else 'A'),'epoch order/label')
    need(b['output']=='HEADLESS-1' and b['scale']==1 and b['transform']==0 and b['radius']==5 and b['passes']==3 and b['strength']==1 and b['effects_neutral'] is True,'acquisition admissibility')
    need(b['GL_ERROR_QUEUE']=='UNOBSERVED' and b['read_success']=='NOT_PROVEN' and b['rows']=='GL_LOW_TO_HIGH','observability limits retained')
    need(len(b['strings'])==4 and b['strings'][2].startswith('OpenGL ES 3.') and len(b['precision'])==6,'actual API capabilities')
    need(all(r['kind'] in ('begin','write','clear','copy','sample','end') for r in rows),'unknown write/event')
    samples=[r for r in rows if r['kind']=='sample'];need([s['point'] for s in samples]==list(range(9)),'nine reads ordered')
    raw=rp.read_bytes();offset=0
    for s in samples: offset=validate_sample(s,raw,epoch,b['context'],offset)
    need(all(samples[p]['after_ns']<=samples[p+1]['before_ns'] for p in range(8)),'native sample temporal order')
    need(offset==len(raw)==e['bytes']==(9216 if epoch==2 else 8312048) and sha(raw)==e['sha256'],'epoch size/whole SHA')
    need(e['points']==9 and e['stages']==6 and e['writes']==sum(r['kind']=='write' for r in rows),'end counts')
    need(e['total_bytes']==sum(plan(k,p)[2]*plan(k,p)[3]*4 for k in range(1,epoch+1) for p in range(9)),'total read budget')
    validate_writes(rows,samples,b['context'])
    return dict(rows=rows,samples=samples,raw=raw)

def validate(directory):
    d=Path(directory);need(not any(d.glob('epoch-4.*')),'fourth epoch forbidden')
    epochs=[validate_epoch(d,e) for e in (1,2,3)]
    need(len({x['rows'][0]['pass'] for x in epochs})==3,'different local acquisition pass')
    return epochs

def reconstruct(epoch):
    need(epoch['rows'][0]['epoch'] in (1,3),'B partial fields cannot reconstruct')
    validate_writes(epoch['rows'],epoch['samples'],epoch['rows'][0]['context'])
    def data(p):
        s=epoch['samples'][p];return epoch['raw'][s['offset']:s['offset']+s['bytes']]
    def replace(base, patch, w,h):
        need(len(base)==800*600*4 and len(patch)==w*h*4,'reconstruction dimensions')
        out=bytearray(base)
        for y in range(h):out[y*800*4:(y*800+w)*4]=patch[y*w*4:(y+1)*w*4]
        return bytes(out)
    p2=replace(data(1),data(3),100,75);q2=replace(data(2),data(4),200,150);p1=replace(p2,data(5),400,300)
    return dict(P2=p2,Q2=q2,P1=p1,U0=data(6),status='SOURCE_DERIVED_RECONSTRUCTION')
