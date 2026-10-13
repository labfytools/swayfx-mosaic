"""Adapters from independently recorded protocol/IPC/applied trace observations.

No native-buffer/frame identity is attributed to a screenshot. Generation is
an observation-window label; atomic transaction-generation is NOT TESTED.
"""
import re
from model import *


def applied_model(measured, owner, text, generation):
    require(measured['id'] == owner['id'] and measured['IPC'] == owner, 'measured-owner-identity')
    workspace = measured.get('workspace')
    require(workspace is not None, 'measured-workspace-required')
    p = Provenance(owner['id'], workspace, generation, measured['raw'])
    buffers = re.findall(r'create_buffer\(new id wl_buffer#(\d+), \d+, (\d+), (\d+), (\d+), (\d+)\)', text)
    require(bool(buffers), 'native-shm-trace-required')
    # Top's first buffer is recorded before TOPLEVEL MAP; never choose popup buffer.
    first = re.search(r'create_buffer\(new id wl_buffer#(\d+), \d+, (\d+), (\d+), (\d+), (\d+)\)', text)
    require(first.start() < text.index('TOPLEVEL MAP '), 'toplevel-buffer-before-map')
    bid,w,h,stride,fmt = map(int, first.groups())
    top_id=int(re.search(r'TOPLEVEL CREATE wl=(\d+)',text)[1])
    require(re.search(rf'wl_surface#{top_id}\.attach\(wl_buffer#{bid}, 0, 0\)',text) is not None,'native-toplevel-attach')
    cfgs = re.findall(r'TOPLEVEL ROLE_CONFIGURE w=(\d+) h=(\d+)', text)
    configured = next((list(map(int,c)) for c in reversed(cfgs) if int(c[0]) > 0 and int(c[1]) > 0), None)
    require(configured is not None, 'toplevel-configure-required')
    assigned_ack = int(re.findall(r'TOPLEVEL XDG_CONFIGURE serial=(\d+) ack', text)[-1])
    require(f'ack_configure({assigned_ack})' in text, 'assigned-ack-trace')
    serial = int(re.search(r'TOPLEVEL XDG_CONFIGURE serial=(\d+) ack', text)[1])
    natural=owner['geometry']
    require(natural==dict(x=0,y=0,width=w,height=h),'native-natural-geometry')
    win = owner['window_rect']
    return Applied(Rect(Space.GLOBAL,*measured['scene'],p),
                   Rect(Space.CONTENT,*[win[k] for k in ('x','y','width','height')],p),
                   Rect(Space.CONFIGURE,0,0,*configured,p),
                   Native(Rect(Space.NATIVE,0,0,w,h,p),bid,stride,fmt,serial),
                   win['x'], owner['deco_rect']['height'] + win['y'], owner['deco_rect']['height'],assigned_ack)


def output_model(snapshot, name, provenance):
    outputs = [o for o in snapshot['outputs'] if o['name'] == name and o['active']]
    require(len(outputs) == 1, 'unique-active-output')
    o = outputs[0]
    return Output(name,Rect(Space.GLOBAL,*[o['rect'][k] for k in ('x','y','width','height')],provenance),o['scale'],o['transform'])


def viewport_model(scene, provenance):
    require(scene['workspace'] == provenance.workspace, 'viewport-workspace')
    require(scene['clip_valid'] is True, 'viewport-applied-valid')
    return Rect(Space.VIEWPORT,*map(int,scene['global_clip']),provenance)


def verify_owner_occlusion(left,right,rect,g,mosaic):
    from pixels import color_geometry
    p=rect.provenance
    occluders=tuple(Rect(Space.GLOBAL,*g[k],p) for k in ('A','B'))
    for im,ox in ((left,-800),(right,0)):
        out=Output(str(ox),Rect(Space.GLOBAL,ox,0,800,600,p),1.0,'normal')
        clip=Rect(Space.VIEWPORT,-800,0,800,600,p) if mosaic else None
        color_geometry(im,'TOPLEVEL',rect,out,clip,occluders)
