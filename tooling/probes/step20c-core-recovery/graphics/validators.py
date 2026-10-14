"""Imported live/offline scientific predicates, not a parallel test model."""
import re
from geometry import need,exact,crossing,expected_outputs
from predicates import protocol

def client_exit(log,code):
 if 'TOPLEVEL CREATE ' in log:
  order=re.findall(r'(POPUP_[AB]|TOPLEVEL) DESTROY',log)
  need(order in (['POPUP_B','POPUP_A','TOPLEVEL'],['TOPLEVEL']),'popup child-first destruction order')
  need(log.index('CLOSE_RECEIVED')<log.index('TOPLEVEL DESTROY'),'close precedes destruction')
 need('CLOSE_RECEIVED' in log,'explicit close receipt absent')
 releases=re.findall(r'SHM_CLOSURE created=(\d+) released=(\d+)',log)
 need(len(releases)==1 and int(releases[0][0])>0 and releases[0][0]==releases[0][1],'client SHM release incomplete/unobserved')
 need(code==0,'client nonzero');errors=re.findall(r'EXIT[^\n]*error=(\d+)',log)
 need(bool(errors) and all(e=='0' for e in errors),'client error/nonobservable exit')
 need(not re.search(r'protocol error|wl_display[^\n]*\.error\(',log,re.I),'wire error')
def window(start,end,events):
 need(start<end and len(events)==1 and start<=events[0]<=end,'ambiguous event window')
def owner(node,owner_id,workspace_id,path):
 need(node['id']==owner_id and [n['id'] for n in path if n['type']=='workspace']==[workspace_id],'wrong owner ancestry')
def rgb(reference,actual,masked=False):
 need(not masked,'H2 occlusion/mask forbidden');return exact(reference,actual)
def grab(log):return protocol(log)
def applied(geometry,paint_origin,pointer_origin,state):
 need(state=='applied' and geometry==paint_origin==pointer_origin,'pending/uncorroborated origin')
def crosses(rect,axis,boundary):need(crossing(rect,axis,boundary),'crossing not exercised')
def shadow(before,after):need(before.tobytes()!=after.tobytes(),'shadow not exercised')
def saved_identity(identity,binary_sha):
 need(identity['binary_sha256']==binary_sha,'wrong binary saved identity')
 need(identity.get('native') is True,'saved identity not observable')

def camera_eligible(path,ws):
 # Null flags are legitimate on IPC descriptors; branch membership remains
 # authoritative even when a child omits its floating flag.
 floating=any((n.get('floating') or 'auto_off').endswith('on') for n in path)
 floating |= any(c in p.get('floating_nodes',[]) for p,c in zip(path,path[1:]))
 return ws.get('layout')=='mosaic' and not floating and not any(n.get('type')=='con' and n.get('fullscreen_mode') for n in path)

def owner_context(node,path,pid,workspace_name,output,layout):
 need(path and path[-1]==node and node.get('pid')==pid,'owner path/pid mismatch')
 ws=[n for n in path if n.get('type')=='workspace'];outs=[n for n in path if n.get('type')=='output']
 need(len(ws)==len(outs)==1,'owner ancestry must include workspace/output')
 need(ws[0].get('name')==workspace_name and ws[0].get('output')==output and outs[0].get('name')==output and ws[0].get('layout')==layout,'wrong mapped workspace/output/layout')
 owner(node,node['id'],ws[0]['id'],path)
 return ws[0]

def selected_workspace(snapshot,name,output,layout):
 from ipc_predicates import workspace
 ws=workspace(snapshot['tree'],name)
 need(ws.get('output')==output and ws.get('layout')==layout,'pre-map workspace/output/layout')
 rows=[r for r in snapshot['workspaces'] if r.get('name')==name]
 need(len(rows)==1 and rows[0].get('focused') and rows[0].get('output')==output,'pre-map workspace not selected')
 return ws

def fullscreen_ancestor(path):
 rows=[n for n in path[:-1] if n.get('type')=='con' and n.get('fullscreen_mode') and n.get('nodes')]
 need(rows,'nonleaf current fullscreen ancestor NOT EXERCISED')
 return rows[-1]

def hidden_survival(log,initial,injections):
 need(not any(e.get('action')!='move' for e in injections),'hide/return contaminated by dismissal click')
 fresh=grab(log)
 need(fresh['ids']==initial['ids'] and fresh['grabs']==initial['grabs'],'same live grabbed chain required')
 return fresh

def standard_spill(images,colors):
 # Native clip identity is unavailable on CORE: demonstrate effective removal
 # through both continued popup paints, then freshly corroborated pointer input.
 need(all(any(px==colors[n] for px in images[1].get_flattened_data()) for n in ('POPUP_A','POPUP_B')),'standard continuation for both A/B NOT EXERCISED')

def evidence_identity(record,binary_sha):
 need(record.get('binary_sha256')==binary_sha and record.get('measurement_kind')=='raw','wrong SHA or superficial status')
