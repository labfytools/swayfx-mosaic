"""Controlled synthetic framing and scenario tests; NO GPU/native evidence."""
import resource,ctypes
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
assert ctypes.CDLL(None).prctl(4,0,0,0,0)==0

import json,os,shutil,tempfile,zlib,copy
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import protocol,scenario
from validate_source import Rejected
NONCE='a'*64
BASE=Path(os.environ['TMPDIR'])
def write_epoch(d,e,total):
 raw=bytes(([32,192,224,255] if e==2 else [245,245,245,255])*6);total+=len(raw)*10
 rows=[dict(kind='begin',schema='G3-followup-v1',epoch=e,nonce=NONCE,label=('A','B','A-return')[e-1],output='HEADLESS-1',intrusive_error_queue=True,error_queue_restorable=False)]
 for p,stage in enumerate(protocol.STAGES):
  if 1<=p<=6:rows.append(dict(kind='uniform',point=p,type=0x8b50,program=5,location=3,shader_default_float='mediump',varying='mediump',sampler=[9729,9729,33071,33071],precision_capability=[15,15,10],native_texture_dimensions=[2,3],actual_bits=[1,2]))
  filename=f'epoch-{e}-point-{p}.rgba';protocol.exclusive(d/filename,raw)
  rows.append(dict(kind='sample',epoch=e,point=p,stage=stage,pass_sequence=e,context='5',result='READ_SUCCESS',read_success=True,published=True,before={'pack':8},after={'pack':8},pre_errors={'exhausted':False,'codes':[]},query_errors={'exhausted':False,'codes':[]},read_errors={'exhausted':False,'codes':[]},restore_errors={'exhausted':False,'codes':[]},client_version=2,gl_major=3,gl_minor=2,glsl_hex=b'OpenGL ES GLSL ES 3.20'.hex(),version_queried=True,state_saved=True,bound=True,read_attempted=True,restore_attempted=True,version_errors={'exhausted':False,'codes':[]},capability_errors={'exhausted':False,'codes':[]},state_errors={'exhausted':False,'codes':[]},gl_version_hex=b'OpenGL ES 3.2 ControlledFake'.hex(),attachment=[0x8d41,44,0,2,3,0x8058],channels=[8,8,8,8],status=0x8cd5,read_buffer=0x8ce0,samples=0,native={'dimensions':[2,3],'fbo_rbo_tex':[11,44,22],'fx':'1','wlr':'2','image':'3'},dmabuf={'borrowed':True,'dimensions':[2,3],'format':int.from_bytes(b'AB24','little'),'modifier':'0000000000000000','planes':[{'stride':8,'offset':0,'fd':4,'fstat_ok':True,'dev':1,'ino':2}]},bytes=len(raw),file=filename,crc32=f'{zlib.crc32(raw):08x}',fresh_rectangles=[[0,0,2,3]]))
 rows.append(dict(kind='end',epoch=e,points=10,accepted=True,raw_total=total))
 protocol.exclusive(d/f'epoch-{e}.jsonl',b''.join((json.dumps(row,separators=(',',':'))+'\n').encode() for row in rows));(None if (d/f'epoch-{e}.consumed').exists() else protocol.exclusive(d/f'epoch-{e}.consumed',f'{NONCE} {e}\n'.encode()))
 return rows,total

def framing(d):
 rows,total=write_epoch(d,1,0);assert protocol.epoch(d,1,NONCE)['raw_total']==240
 tests=[('early-return',lambda x:x[1].update(read_attempted=False)),('fake-version',lambda x:x[1].update(gl_minor=1)),('unqualified-es',lambda x:x[1].update(gl_version_hex=b'OpenGL ES 3.3'.hex())),('capability-error',lambda x:x[1]['capability_errors']['codes'].append(0x500)),('read-error',lambda x:x[1]['read_errors']['codes'].append(0x502)),('restore',lambda x:x[1]['after'].update(pack=1)),('context',lambda x:x[1].update(context='0')),('path',lambda x:x[1].update(file='../escape')),('budget',lambda x:x[1].update(bytes=protocol.CAP+1)),('incomplete',lambda x:x.pop()),('stage',lambda x:x[1].update(stage='presented-buffer'))]
 p=d/'epoch-1.jsonl'
 for label,mutate in tests:
  changed=copy.deepcopy(rows);mutate(changed);p.write_text(''.join(json.dumps(x)+'\n' for x in changed));p.chmod(0o600)
  try:protocol.epoch(d,1,NONCE)
  except (Rejected,KeyError,AssertionError):print('PASS controlled framing rejection',label)
  else:raise AssertionError(label)
 p.write_text(''.join(json.dumps(x)+'\n' for x in rows));p.chmod(0o600)
 q=d/'epoch-1-point-0.rgba';q.write_bytes(b'bad')
 try:protocol.epoch(d,1,NONCE)
 except Rejected:print('PASS raw truncation/CRC rejection')
 else:raise AssertionError('truncation')
 q.unlink();q.symlink_to('/dev/null')
 try:protocol.bounded(q,10)
 except Rejected:print('PASS symlink refusal')
 else:raise AssertionError('symlink')
 try:protocol.exclusive(p,b'overwrite')
 except FileExistsError:print('PASS exclusive publication refusal')
 else:raise AssertionError('exclusive')
 assert scenario.exact_rgb(Image.new('RGB',(2,3)),Image.new('RGB',(2,3)))['equal']
 a=Image.new('RGB',(2,3));b=a.copy();b.putpixel((1,2),(1,0,0));assert not scenario.exact_rgb(a,b)['equal']
 print('PASS whole H1/H2 all-pixel zero RGB tolerance')

def token_test(d):
 with patch.object(protocol,'gate',lambda *args:None):
  protocol.arm(d,1,NONCE,d/'gate',d/'binary')
  assert protocol.bounded(d/'epoch-1.arm',80)==f'{NONCE} 1\n'.encode()
  for e in (1,2):
   try:protocol.arm(d,e,NONCE,d/'gate',d/'binary')
   except (Rejected,FileNotFoundError):pass
   else:raise AssertionError('retry or B before complete A')
  os.link(d/'epoch-1.arm',d/'epoch-1.consumed');(d/'epoch-1.arm').unlink()
  write_epoch(d,1,0)
  protocol.arm(d,2,NONCE,d/'gate',d/'binary')
  try:protocol.arm(d,3,NONCE,d/'gate',d/'binary')
  except (Rejected,FileNotFoundError):pass
  else:raise AssertionError('return before complete B')
  print('PASS exact arm token nonce/exclusive/replay and first A completion gate, controlled directory')

class Session:
 def __init__(self,d,fail=False):
  self.d=d;self.fail=fail;self.commands=[];self.captures=0;self.total=0;self.env={};self.spec={'id':'GPU-G3','binary':'gpu'};self.auth={'binary':str(d/'fake-binary'),'manifest_sha256':'controlled'};self.proc={};self.data={};self.saved={}
 def start(self):self.data['started']=True
 def cmd(self,*a,**kw):pass
 def spawn(self,name,argv):
  parent=self
  class Input:
   def write(self,text):
    parent.commands.append(text.strip());e=len(parent.commands)
    if parent.fail:protocol.exclusive(parent.d/f'epoch-{e}.jsonl',b'{"kind":"rejected"}\n')
    else:_,parent.total=write_epoch(parent.d,e,parent.total)
   def flush(self):pass
  self.proc[name]=type('Process',(),{'stdin':Input()})()
 def wait(self,fn):assert fn()
 def find(self,name):return {'id':1}
 def log(self,name):return 'BACKGROUND_CONFIGURED '+' '.join('G3_SOURCE_BYTES command='+x+' ' for x in self.commands)
 def debit(self,*a):pass
 def record(self,*a,**kw):pass
 def capture(self,*a):self.captures+=1;return Image.new('RGB',(2,3))
 def pair_capture(self,*a):self.captures+=2;return [Image.new('RGB',(2,3)),Image.new('RGB',(2,3))]
 def snapshot(self,*a):pass
 def save(self,name,result):self.saved[name]=result
 def close_client(self,*a):pass

def scenario_test(d,fail):
 s=Session(d,fail);binary=d/'fake-binary';binary.write_bytes(b'controlled')
 binding=dict(G3_ledger_reserved=True,binary=str(binary),source_manifest_sha256='controlled',gate_file=str(d/'gate'),client=str(binary),client_sha256=__import__('hashlib').sha256(binary.read_bytes()).hexdigest(),nonce=NONCE)
 armed=[]
 with patch.object(scenario,'ROOT',d),patch.object(scenario,'gate',lambda *args:None),patch.object(scenario,'arm',lambda root,e,*args:armed.append(e)),patch.object(scenario.time,'sleep',lambda seconds:None):
  if fail:
   try:scenario.run(s,binding)
   except RuntimeError:pass
   else:raise AssertionError('rejected A continued')
   assert s.commands==['G3-A'] and armed==[1] and s.captures==2
   print('PASS rejected first A stops B/A-return: exact executable adapter, fake Session only')
  else:
   r=scenario.run(s,binding);assert s.commands==['G3-A','G3-B','G3-A-return'] and armed==[1,2,3] and s.captures==8 and r['whole_H1_A_Areturn']['equal']
   print('PASS one-shot A/B/A adapter flow, eight captures with whole H1/H2 and H2 baseline, controlled framing')
if __name__=='__main__':
 with tempfile.TemporaryDirectory(prefix='protocol-controlled-',dir=BASE) as temp:
  p=Path(temp);p.chmod(0o700)
  for name in ('framing','accepted','rejected','token'):(p/name).mkdir(mode=0o700)
  with patch.object(protocol,'FRAME',(2,3)):
   framing(p/'framing');token_test(p/'token');scenario_test(p/'accepted',False);scenario_test(p/'rejected',True)
