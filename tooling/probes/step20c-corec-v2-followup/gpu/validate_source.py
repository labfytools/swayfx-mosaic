"""New G2 offline controls. Historical G1 stays HISTORICAL_REPORTED_ONLY."""
import resource,ctypes
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
assert ctypes.CDLL(None).prctl(4,0,0,0,0)==0

import hashlib,json,struct
from pathlib import Path
HEADER_SHA='992f33804acda60b0b46f1a272942c3592484ea3217d469239f1cb12249de2eb'
BPP={int.from_bytes(s,'little'):4 for s in (b'AB24',b'XB24',b'AR24',b'XR24')}
AMD='020000001046bb04'
class Rejected(ValueError):pass
def need(x,msg):
 if not x:raise Rejected(msg)
def metadata(o):
 need(type(o['width']) is int and type(o['height']) is int and 0<o['width']<=2**31-1 and 0<o['height']<=2**31-1,'dimensions')
 need(o['format'] in BPP,'unknown FOURCC')
 need(o['modifier'] in ('0000000000000000',AMD),'unknown modifier')
 planes=o['planes'];need(len(planes)==(2 if o['modifier']==AMD else 1),'plane count')
 for p in planes:
  need(all(type(p[k]) is int and 0<=p[k]<=2**32-1 for k in ('stride','offset')) and p['stride']>0,'plane uint32')
  need(p['offset']+p['stride']<=2**64-1,'overflow')
 p=planes[0];need(p['stride']>=o['width']*BPP[o['format']],'image stride')
 end=p['offset']+p['stride']*(o['height']-1)+o['width']*BPP[o['format']]
 need(end<=2**64-1,'image overflow')
 # No fabricated DCC extent or same-allocation restriction. fstat sizes are
 # recorded as descriptor metadata, not interpreted as allocation length.
 return {'image_stride':'PASS','auxiliary_stride':'NOT_AN_IMAGE_STRIDE' if len(planes)>1 else 'N/A','allocation_bounds':'NOT_PROVEN','fd_ownership':'BORROWED' if o.get('borrowed') is True else 'NOT_PROVEN','decode_support':'NOT_PROVEN'}
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def halfpixel(width,height,down,observed):
 need(width>0 and height>0 and len(observed)==2 and all(type(x)is int and 0<=x<=2**32-1 for x in observed),'uniform framing')
 divisor=f32(2.0)
 ideal=[f32(f32(.5)/f32(f32(n)/divisor if down else f32(n)*divisor)) for n in (width,height)]
 return {'observed_bits':observed,'cpu_float32_ideal_bits':[bits(x) for x in ideal],'comparison_gate':'NONE','effective_arithmetic':'NOT_PROVEN','capability_is_per_operation_precision':False}
def test():
 from copy import deepcopy
 need(hashlib.sha256(Path('/usr/include/libdrm/drm_fourcc.h').read_bytes()).hexdigest()==HEADER_SHA,'header pin')
 o={'width':800,'height':600,'format':int.from_bytes(b'AB24','little'),'modifier':AMD,'planes':[{'stride':3584,'offset':0},{'stride':1024,'offset':2293760}],'borrowed':True}
 r=metadata(o);need(r['auxiliary_stride']=='NOT_AN_IMAGE_STRIDE','AMD aux')
 # Controlled fixtures, never actual allocation evidence or historical PASS.
 for label,fn in [('unknown-format',lambda x:x.update(format=1)),('short-image',lambda x:x['planes'][0].update(stride=3199)),('plane-count',lambda x:x['planes'].pop()),('unknown-modifier',lambda x:x.update(modifier='ffffffffffffffff')),('negative-offset',lambda x:x['planes'][1].update(offset=-1)),('zero-aux',lambda x:x['planes'][1].update(stride=0))]:
  x=deepcopy(o);fn(x)
  try:metadata(x)
  except Rejected:print('PASS controlled rejection',label)
  else:raise AssertionError(label)
 u=halfpixel(800,600,True,[bits(1/800),bits(1/600)])
 v=halfpixel(800,600,True,[bits(.0012493133544921875),bits(.0016660690307617188)])
 need(u['cpu_float32_ideal_bits']==v['cpu_float32_ideal_bits'] and u['observed_bits']!=v['observed_bits'] and v['comparison_gate']=='NONE','no mediump equality or fit')
 try:halfpixel(800,600,False,[2**32,0])
 except Rejected:pass
 else:raise AssertionError('uniform framing')
 print('PASS controlled AMD/linear policy and separate halfpixel bits; HISTORICAL_REPORTED_ONLY')
if __name__=='__main__':test()
