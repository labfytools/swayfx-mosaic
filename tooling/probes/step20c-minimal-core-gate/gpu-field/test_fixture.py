"""Offline tests importing the SAME validator/model called by the runner."""
import copy,json,struct,tempfile,unittest
from pathlib import Path
import numpy as np
import validate as v
import analysis as a

def bits(x):return struct.unpack('I',struct.pack('f',x))[0]
def obj(n,cache=False):
 return dict(fx=f'0x{n}',wlr=f'0x{n+100}',fbo=n,rbo=n+10,tex=n+20,image=f'img{n}',dimensions=[800,600],dmabuf_available=True,drm_format=v.XBGR if cache else v.ABGR,modifier='0000000000000000',dmabuf_size=[800,600],planes=[[3200,0]])

def fixture(e):
 objects=[obj(1),obj(2),obj(3),obj(2),obj(3),obj(2),obj(3),obj(4,True),obj(1)]
 rows=[dict(kind='begin',epoch=e,label='B' if e==2 else 'A',context='ctx',output='HEADLESS-1',pass_=e,scale=1,transform=0,radius=5,passes=3,strength=1,effects_neutral=True,GL_ERROR_QUEUE='UNOBSERVED',read_success='NOT_PROVEN',rows='GL_LOW_TO_HIGH',strings=['vendor','renderer','OpenGL ES 3.2','ES GLSL'],precision=[[0]*5]*6)]
 rows[0]['pass']=rows[0].pop('pass_');raw=bytearray()
 for p in range(9):
  if 1<=p<=6:
   uniforms=[dict(name=n,type=5126,value=[bits(x) for x in vals]) for n,vals in [('radius',[5]),('halfpixel',[1/800,1/600] if p<=3 else [1/3200,1/2400]),('proj',[1]*9),('tex_proj',[1]*9)]]
   rows.append(dict(kind='write',sequence=p,stage=p-1,fbo=objects[p]['fbo'],program=7,read_fbo=1,texture=objects[p-1]['tex'],context='ctx',box=[0,0,800,600],region=[[0,0,*v.FRESH[p]]],viewport=[0,0,800,600],scissor=[0,0,0,0],scissor_enabled=0,blend=0,stencil=0,dither=1,color_mask=[1]*4,src=objects[p-1],dst=objects[p],sampler=[9729,9729,33071,33071],uniforms=uniforms))
  if p==7:
   rows.append(dict(kind='write',sequence=7,stage=-1,fbo=4,region=[[0,0,800,600]]))
   rows.append(dict(kind='copy',src=objects[6],dst=objects[7],region=[[0,0,800,600]]))
  x,y,w,h=v.plan(e,p)
  yy,xx=np.mgrid[:h,:w];data=np.stack([(xx+x+p*13)%199,(yy+y+p*17)%199,(xx+yy+p*23)%199,np.full((h,w),255)],axis=2).astype('uint8').tobytes()
  rows.append(dict(kind='sample',point=p,name=v.NAMES[p],roi=[x,y,w,h],fresh=list(v.FRESH[p]),offset=len(raw),bytes=len(data),sha256=v.sha(data),object=objects[p],before=[1,2,3,4,4,0,0,0,36064],after=[1,2,3,4,4,0,0,0,36064],context_before='ctx',context_after='ctx',target_read_buffer=36064,attachment=[36161,objects[p]['rbo'],35863,9729,8,8,8,0 if p==7 else 8],renderbuffer=[800,600,32856],before_ns=e*10000+p*10+1,after_ns=e*10000+p*10+2,fbo_status=36053,sentinel_alpha_written=True,valid=True));raw.extend(data)
 rows.append(dict(kind='end',epoch=e,points=9,stages=6,writes=7,bytes=len(raw),total_bytes=sum(v.plan(k,p)[2]*v.plan(k,p)[3]*4 for k in range(1,e+1) for p in range(9)),sha256=v.sha(raw)))
 return rows,bytes(raw)

class RuntimeValidator(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();cls.d=Path(cls.temp.name);cls.base={}
  for e in (1,2,3):
   rows,raw=fixture(e);cls.base[e]=rows;(cls.d/f'epoch-{e}.rgba').write_bytes(raw);(cls.d/f'epoch-{e}.rgba').chmod(0o600)
   (cls.d/f'epoch-{e}.arm').write_text(('B' if e==2 else 'A')+'\n');(cls.d/f'epoch-{e}.arm').chmod(0o600)
  cls.reset()
 @classmethod
 def reset(cls):
  for e,rows in cls.base.items():
   (cls.d/f'epoch-{e}.meta').write_text(''.join(json.dumps(r)+'\n' for r in rows));(cls.d/f'epoch-{e}.meta').chmod(0o600)
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def tearDown(self):self.reset()
 def mutate(self,fn):
  rows=copy.deepcopy(self.base[1]);fn(rows);(self.d/'epoch-1.meta').write_text(''.join(json.dumps(r)+'\n' for r in rows))
  with self.assertRaises((v.Rejected,KeyError,IndexError)):v.validate_epoch(self.d,1)
 def test_real_validator_accepts(self):self.assertEqual(len(v.validate(self.d)),3)
 def test_arm_missing_invalid(self):
  p=self.d/'epoch-1.arm';data=p.read_bytes()
  try:
   for bad in (b'',b'B\n',b'A\nextra'):
    p.write_bytes(bad)
    with self.assertRaises(v.Rejected):v.validate_epoch(self.d,1)
  finally:p.write_bytes(data)
 def test_metadata_mode(self):
  p=self.d/'epoch-1.meta';p.chmod(0o644)
  with self.assertRaises(v.Rejected):v.validate_epoch(self.d,1)
 def test_budget(self):self.assertEqual(v.read_plan(),dict(reads=27,bytes=16633312))
 def test_invalid_fourth(self):
  with self.assertRaises(v.Rejected):v.plan(4,0)
 def test_restore_each_field(self):
  for k in range(9):
   with self.subTest(k=k):self.mutate(lambda r,k=k:r[1]['after'].__setitem__(k,777))
 def test_context(self):self.mutate(lambda r:r[1].update(context_after='other'))
 def test_bad_format_channels(self):
  for k,value in ((0,5890),(1,99),(2,5126),(3,35904),(4,10),(5,0),(6,5),(7,0)):
   with self.subTest(k=k):self.mutate(lambda r,k=k,value=value:r[1]['attachment'].__setitem__(k,value))
 def test_bad_dmabuf(self):self.mutate(lambda r:r[1]['object'].update(drm_format=0))
 def test_rbo_size(self):self.mutate(lambda r:r[1]['renderbuffer'].__setitem__(0,799))
 def test_readbuffer(self):self.mutate(lambda r:r[1].update(target_read_buffer=0))
 def test_truncated_and_corrupt(self):
  rp=self.d/'epoch-1.rgba';old=rp.read_bytes()
  try:
   for bad in (old[:-1],bytes([old[0]^1])+old[1:]):
    rp.write_bytes(bad)
    with self.assertRaises(v.Rejected):v.validate_epoch(self.d,1)
  finally:rp.write_bytes(old)
 def test_incomplete_reordered_extra(self):
  for fn in (lambda r:r.pop(),lambda r:r.__setitem__(1,r[3]),lambda r:r.insert(3,copy.deepcopy(r[2]))):self.mutate(fn)
 def test_admissibility(self):
  for k,val in [('epoch',4),('label','B'),('output','HEADLESS-2'),('scale',1.25),('transform',1),('radius',4),('strength',.5),('effects_neutral',False)]:
   with self.subTest(k=k):self.mutate(lambda r,k=k,val=val:r[0].__setitem__(k,val))
 def test_sentinel(self):self.mutate(lambda r:r[1].update(sentinel_alpha_written=False))
 def test_roi_outside(self):self.mutate(lambda r:r[1]['roi'].__setitem__(0,800))
 def test_budget_offset(self):self.mutate(lambda r:r[-1].update(total_bytes=v.LIMIT+1))
 def test_region_hole_same_extents(self):self.mutate(lambda r:r[2].update(region=[[0,0,400,149],[0,150,400,300]]))
 def test_alias_source_fbo(self):self.mutate(lambda r:r[2]['src'].update(fbo=r[2]['dst']['fbo']))
 def test_replaced_buffer(self):self.mutate(lambda r:r[3]['object'].update(wlr='replaced'))
 def test_color_clear(self):self.mutate(lambda r:r.insert(-1,dict(kind='clear',mask=16384,fbo=2)))
 def test_external_write(self):
  def fn(r):r.insert(-1,dict(kind='write',stage=-1,sequence=8,fbo=2,region=[[0,0,1,1]]));r[-1]['writes']=8
  self.mutate(fn)
 def test_unknown_destroy(self):self.mutate(lambda r:r.insert(-1,dict(kind='destroy',fbo=2)))
 def test_missing_draw(self):self.mutate(lambda r:r.pop(2))
 def test_exact_reconstruction(self):
  e=v.validate_epoch(self.d,1);r=v.reconstruct(e)
  p2=np.frombuffer(r['P2'],dtype='uint8').reshape(600,800,4);q2=np.frombuffer(r['Q2'],dtype='uint8').reshape(600,800,4);p1=np.frombuffer(r['P1'],dtype='uint8').reshape(600,800,4)
  np.testing.assert_array_equal(p2[:75,:100],a.field(e,3));np.testing.assert_array_equal(p2[75:],a.field(e,1)[75:]);np.testing.assert_array_equal(p2[:75,100:],a.field(e,1)[:75,100:])
  np.testing.assert_array_equal(q2[:150,:200],a.field(e,4));np.testing.assert_array_equal(q2[150:],a.field(e,2)[150:]);np.testing.assert_array_equal(p1[:300,:400],a.field(e,5));np.testing.assert_array_equal(p1[300:],p2[300:]);np.testing.assert_array_equal(p1[:300,400:],p2[:300,400:])
 def test_B_cannot_reconstruct(self):
  with self.assertRaises(v.Rejected):v.reconstruct(v.validate_epoch(self.d,2))
 def test_exact_predictions_mutated(self):
  epochs=v.validate(self.d)
  for p in (0,1,2):
   e=copy.deepcopy(epochs);s=e[2]['samples'][p];raw=bytearray(e[2]['raw']);raw[s['offset']]^=1;e[2]['raw']=bytes(raw)
   self.assertEqual(a.whole_hypothesis(e)['H_FRONTIERE_CHAMP_ENTIER'],'REFUTED')

class Controller(unittest.TestCase):
 def test_durable_one_shot_arm(self):
  import runner
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp)
   runner.arm(d,1,'A');self.assertEqual((d/'epoch-1.arm').read_bytes(),b'A\n')
   with self.assertRaises(v.Rejected):runner.arm(d,1,'A')
   with self.assertRaises(v.Rejected):runner.arm(d,2,'B')
   with self.assertRaises(v.Rejected):runner.arm(d,4,'A')
   with self.assertRaises(v.Rejected):runner.arm(d,2,'A')
 def test_real_SHM_validator_mismatch(self):
  import runner
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);log=[]
   for i,colors in enumerate(('00101010,00202020','00303030,00404040','00101010,00202020'),1):
    cs=[int(x,16) for x in colors.split(',')];raw=b''.join(struct.pack('<I',cs[x//8%2]) for x in range(800))*600
    p=d/f'background-{i}.shm';p.write_bytes(raw)
    log.append(f'SHM_SOURCE mode=background path={p} bytes={len(raw)} stride=3200 format=XRGB8888 colors={colors}')
   self.assertTrue(runner.fx_validators.sources(d,'\n'.join(log))['ABA_byte_exact'])
   p=d/'background-3.shm';bad=bytearray(p.read_bytes());bad[0]^=1;p.write_bytes(bad)
   with self.assertRaises(ValueError):runner.fx_validators.sources(d,'\n'.join(log))

class Model(unittest.TestCase):
 def test_constant_and_partition(self):
  src=np.full((80,100,4),64,dtype='uint8')
  for down in (False,True):
   pred,fresh,tail=a.ideal(src,20,15,down,(10,10));np.testing.assert_allclose(pred,64,rtol=0,atol=1e-13);np.testing.assert_array_equal(pred,fresh+tail)
 def test_linear_ramp_bilinear(self):
  yy,xx=np.mgrid[:100,:100];src=np.repeat((xx+yy)[:,:,None],4,axis=2).astype(float)
  np.testing.assert_array_equal(a.bilinear(src,np.array([[10.5]]),np.array([[20.25]])),np.full((1,1,4),30.75))
 def test_tap_weights_ramp(self):
  yy,xx=np.mgrid[:100,:100];src=np.repeat((xx+yy)[:,:,None],4,axis=2).astype(float)
  down,_,_=a.ideal(src,30,30,True,(100,100));self.assertEqual(down[10,10,0],41)
  up,_,_=a.ideal(src,50,50,False,(100,100));self.assertAlmostEqual(up[20,20,0],19.5)
 def test_composition(self):
  src=np.full((1,1,4),255);np.testing.assert_array_equal(a.composition(src),[[[187,151,135]]])
  with self.assertRaises(v.Rejected):a.composition(src,136)

if __name__=='__main__':unittest.main(verbosity=2)
