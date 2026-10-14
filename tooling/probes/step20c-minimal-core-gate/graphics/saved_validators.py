"""Local pure CORE saved evidence; no diagnostic/historical import."""
import re
from geometry import need,intersection
from ipc_predicates import workspace,nodes
from PIL import ImageChops
def held_configure(before,after,prior_serial):
    need(type(prior_serial)is int and prior_serial>0,'prior serial required')
    need(re.search(rf'ACK ns=\d+ serial={prior_serial}\b',before) and re.search(rf'ack_configure\({prior_serial}\)',before),'initial actual ACK required')
    need('wl_shm_pool#' in before and '.create_buffer(' in before and 'COMMIT ns=' in before,'real initial SHM required')
    held=re.findall(r'HELD ns=(\d+) serial=(\d+)',after);need(len(held)==1,'unique real HELD configure')
    ns,serial=map(int,held[0]);need(serial!=prior_serial,'new held serial')
    need(re.search(rf'xdg_surface#\d+\.configure\({serial}\)',after),'received actual configure wire')
    need(re.search(rf'XDG_CONFIGURE ns=\d+ serial={serial}\b.*hold=1',after),'client received hold state')
    old=re.findall(r'ACK ns=\d+ serial='+str(prior_serial)+r' size=(\d+)x(\d+)',before);new=re.findall(r'XDG_CONFIGURE ns=\d+ serial='+str(serial)+r' size=(\d+)x(\d+)',after)
    need(old and new and old[-1]!=new[-1],'new geometry configure required')
    need(not re.search(rf'ack_configure\({serial}\)|ACK ns=\d+ serial={serial}\b',after),'held serial must remain unACKed')
    return dict(ns=ns,serial=serial,prior_serial=prior_serial,initial_size=list(map(int,old[-1])),requested_size=list(map(int,new[-1])),status='HELD_WIRE_VALIDATED',native_saved_identity='NOT OBSERVABLE')

def pending_geometry(initial,pending,owner_id,workspace_id,before,after,prior,request_ns):
    oldws=workspace(initial['tree'],'1');ws=workspace(pending['tree'],'1')
    need(oldws['id']==ws['id']==workspace_id and ws['output']==oldws['output']=='HEADLESS-1' and ws['layout']==oldws['layout']=='mosaic','same requested workspace')
    need('gaps' not in ws,'IPC gaps field is absent in audited source')
    old=next(n for n in nodes(oldws) if n['id']==owner_id)
    owners=[n for n in nodes(ws) if n['id']==owner_id];need(len(owners)==1,'same owner ancestry')
    target=owners[0];need(target['pid']==old['pid'] and target['app_id']==old['app_id']=='org.mosaic.SavedBufferProbe','same actual client')
    a=oldws['rect'];b=ws['rect'];need([b[k] for k in ('x','y','width','height')]==[a['x']+30,a['y']+30,a['width']-60,a['height']-60],'requested workspace rect changed by runtime gaps30')
    proof=held_configure(before,after,prior)
    need(proof['ns']>request_ns and proof['requested_size']==[target['window_rect']['width'],target['window_rect']['height']],'held wire after command matches requested dimensions')
    need(proof['initial_size']==[old['window_rect']['width'],old['window_rect']['height']],'initial applied dimensions')
    return dict(held=proof,workspace=ws,owner=target)

def rgb_exact(a,b):
    need(a.mode==b.mode=='RGB' and a.size==b.size,'whole RGB contract')
    need(ImageChops.difference(a,b).getbbox() is None,'whole RGB equal; no masked channel/ROI');return True

def timeout_line(text,activation_line,client_alive,request_ns,observed_ns,cleanup_ns):
    need(client_alive and request_ns+4_700_000_000<=observed_ns<cleanup_ns,'natural timeout window/client alive')
    matches=[(i,l) for i,l in enumerate(text.splitlines()) if i>activation_line and re.search(r'Transaction .*timed out \(\d*[1-9]\d* waiting\)',l)]
    need(len(matches)==1,'native natural timeout required');return matches[0]

def saved_identity(*args,**kwargs):raise ValueError("CORE native saved identity NOT OBSERVABLE")
def natural_retirement(*args,**kwargs):raise ValueError("CORE retirement NOT OBSERVABLE")
