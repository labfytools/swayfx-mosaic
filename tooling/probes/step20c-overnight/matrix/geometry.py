"""Explicit logical global, IPC assignment, physical mode and PNG-frame adapters."""
from dataclasses import dataclass
import re
from PIL import Image

class Ambiguous(ValueError):pass
def need(ok,msg):
    if not ok:raise Ambiguous(msg)
def box_end(r):return [r[0]+r[2],r[1]+r[3]]
def contains(r,p):return r[0]<=p[0]<r[0]+r[2] and r[1]<=p[1]<r[1]+r[3]
def crossing(r,axis,boundary):return r[axis]<boundary<r[axis]+r[axis+2]
def intersection(a,b):
    x=max(a[0],b[0]);y=max(a[1],b[1]);return [x,y,max(0,min(a[0]+a[2],b[0]+b[2])-x),max(0,min(a[1]+a[3],b[1]+b[3])-y)]
def assigned_origin(owner):
    # IPC rect already excludes top decoration (ipc-json.c899–906).
    return [owner['rect']['x']+owner['window_rect']['x'],owner['rect']['y']+owner['window_rect']['y']]
def exterior_ipc(owner):
    r=owner['rect'];d=owner['deco_rect']['height'];return [r['x'],r['y']-d,r['width'],r['height']+d]
def actual_origin(owner,trace):
    rows=[s for s in trace.splitlines() if 'PI_OWNER output=' in s and f' id={owner["id"]} ' in s]
    need(rows,'applied owner trace absent');m=re.search(r'scene_valid=1 scene=(-?\d+),(-?\d+) applied_size=(\d+),(\d+)',rows[-1]);need(m is not None,'applied owner malformed')
    r=list(map(int,m.groups()));w=owner['window_rect'];return [r[0]+w['x'],r[1]+owner['deco_rect']['height']+w['y']],r,rows[-1]
MARKERS={'TL':(255,32,32),'TR':(32,255,32),'BL':(32,32,255),'BR':(255,255,32),'C':(192,32,255)}
def marker_frame(image,scale,rotated):
    positions={k:[] for k in MARKERS};lookup={v:k for k,v in MARKERS.items()}
    for y in range(image.height):
        for x in range(image.width):
            k=lookup.get(image.getpixel((x,y)))
            if k:positions[k].append((x,y))
    need(all(len(v)>=100 for v in positions.values()),'marker color missing')
    c={k:[sum(p[i] for p in v)/len(v) for i in (0,1)] for k,v in positions.items()}
    logical=image.size==(round(800*scale),round(600*scale)) and c['TL'][0]<c['TR'][0] and c['TL'][1]<c['BL'][1]
    physical=rotated and image.size==(round(600*scale),round(800*scale)) and c['TL'][0]>c['BL'][0] and c['TL'][1]<c['TR'][1]
    need(logical or physical,'PNG orientation unestablished')
    return dict(frame='logical' if logical else 'physical90',centers=c,counts={k:len(v) for k,v in positions.items()},size=list(image.size))
def png_global(px,output,frame):
    scale=output['scale'];x,y=px;ox,oy,w,h=output['logical']
    if frame=='physical90':x,y=y,round(h*scale)-1-x
    need(frame in ('logical','physical90'),'unknown PNG frame')
    # Sample integer logical centers only; resample at the chosen center later.
    return [ox+int(x/scale),oy+int(y/scale)]
def global_png(p,output,frame):
    x=(p[0]-output['logical'][0])*output['scale'];y=(p[1]-output['logical'][1])*output['scale']
    if frame=='physical90':x,y=output['logical'][3]*output['scale']-1-y,x
    return [round(x),round(y)]
def solid_point(image,color,output,frame,rectangle=None,margin=3):
    for y in range(margin,image.height-margin,3):
        for x in range(margin,image.width-margin,3):
            if image.getpixel((x,y))!=color:continue
            p=png_global((x,y),output,frame)
            if rectangle is not None and not contains(rectangle,p):continue
            pp=global_png(p,output,frame)
            if not (margin<=pp[0]<image.width-margin and margin<=pp[1]<image.height-margin):continue
            if all(image.getpixel((xx,yy))==color for yy in range(pp[1]-margin,pp[1]+margin+1) for xx in range(pp[0]-margin,pp[0]+margin+1)):
                return p
    raise Ambiguous('no measured solid logical interior')
def count(image,color):return sum(v==color for v in image.get_flattened_data())
def exact(a,b):need(a.size==b.size and a.tobytes()==b.tobytes(),'whole RGB differs');return dict(equal=True,pixels=a.width*a.height)
def expected_outputs(outputs,spec):
    active=[o for o in outputs if o['active']];need(len(active)==2,'active output count')
    for want in spec:
        rows=[o for o in active if o['name']==want['name']];need(len(rows)==1,'output identity')
        o=rows[0];need([o['rect'][k] for k in ('x','y','width','height')]==want['logical'],'logical output geometry')
        need(o['scale']==want['scale'] and o['transform']==want['transform'],'scale/IPC transform string')
        need([o['current_mode'][k] for k in ('width','height')]==want['mode'],'physical mode')
    return active
