"""Imported live/offline scientific predicates, not a parallel test model."""
import re
from geometry import need,exact,crossing,expected_outputs
from predicates import protocol

def client_exit(log,code):
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
