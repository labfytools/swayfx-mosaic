"""G3 protocol tooling; never spawns compositor/client/GPU or grants review.
prepare-plan prints prospective framing only. arm requires an external accepted
review and runtime authorization. No retry is implemented. All files exclusive.
"""
import argparse,hashlib,json,os,stat,zlib,re
from pathlib import Path
from validate_source import need,metadata,halfpixel
CAP=256*1024*1024
FRAME=(800,600)
STAGES=['source','down0','down1','down2','up2','up1','up0','optimized-cache','no-blur-cache','composition-presubmit']
ROOT=Path(os.environ.get('MOSAIC_G3_DIR','/G3_ROOT_NOT_BOUND'))
def owned(p,mode):
 s=p.lstat();need(not stat.S_ISLNK(s.st_mode) and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode)==mode,'owned path/mode')
 return s
def bounded(p,cap):
 s=owned(p,0o600);need(stat.S_ISREG(s.st_mode) and s.st_size<=cap and s.st_nlink==1,'bounded regular exclusive file')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  after=os.fstat(fd);need((s.st_dev,s.st_ino)==(after.st_dev,after.st_ino),'path identity')
  data=os.read(fd,cap+1);need(len(data)==s.st_size and len(data)<=cap,'bounded stable framing');return data
 finally:os.close(fd)
def exclusive(p,b):
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:
  with os.fdopen(fd,'wb',closefd=False) as f:f.write(b);f.flush();os.fsync(fd)
 finally:os.close(fd)
 d=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(d)
 finally:os.close(d)
def epoch(directory,e,nonce,prior=0):
 need(e in (1,2,3),'epoch')
 raw=bounded(directory/f'epoch-{e}.jsonl',1024*1024);need(raw.endswith(b'\n'),'metadata line framing')
 rows=[json.loads(x) for x in raw.splitlines()];need(len(rows)==18,'bounded exact event count')
 begin,end=rows[0],rows[-1]
 need(begin['kind']=='begin' and begin['schema']=='G3-followup-v1' and begin['epoch']==e and begin['nonce']==nonce and begin['label']==('A','B','A-return')[e-1],'begin identity')
 need(begin['output']=='HEADLESS-1' and begin['intrusive_error_queue'] is True and begin['error_queue_restorable'] is False,'intrusion/output')
 need(end['kind']=='end' and end['epoch']==e and end['points']==10 and end['accepted'] is True,'complete accepted epoch; rejection or incomplete A stops all')
 # Consumed files intentionally had one hard link during atomic consumption;
 # publication is accepted only after arm unlink gives a single link again.
 need(bounded(directory/f'epoch-{e}.consumed',80)==f'{nonce} {e}\n'.encode(),'consumed token')
 samples=[x for x in rows if x['kind']=='sample'];uniforms=[x for x in rows if x['kind']=='uniform']
 need(len(samples)==10 and len(uniforms)==6,'stage/uniform count')
 need([x['point'] for x in samples]==list(range(10)) and [x['point'] for x in uniforms]==list(range(1,7)),'strict point order')
 need([x['kind'] for x in rows[1:-1]]==['sample']+['uniform','sample']*6+['sample']*3,'query/draw/read sequence')
 total=prior;context=samples[0]['context'];source_analysis=[]
 for p,s in enumerate(samples):
  need(s['point']==p and s['stage']==STAGES[p] and s['epoch']==e and s['pass_sequence']==e and s['context']==context and context!='0','pass/context identity')
  need(s['result']=='READ_SUCCESS' and s['read_success'] is True and s['published'] is True and s['before']==s['after'],'GL/read/state acceptance')
  for key in ('pre_errors','query_errors','read_errors','restore_errors'):need(s[key]=={'exhausted':False,'codes':[]},'error queue ambiguity')
  need(s['client_version'] in (2,3) and re.fullmatch(rb'OpenGL ES 3\.([0-2])(?: [ -~]*)?',bytes.fromhex(s['gl_version_hex'])) is not None,'bounded actual GLES3 version')
  need(s['gl_major']==3 and s['gl_minor']==int(bytes.fromhex(s['gl_version_hex'])[12:13]) and bool(bytes.fromhex(s['glsl_hex'])),'consistent native GL version/GLSL')
  need(all(s.get(k) is True for k in ('version_queried','state_saved','bound','read_attempted','restore_attempted')),'observable exact read lifecycle')
  for key in ('version_errors','capability_errors','state_errors'):need(s[key]=={'exhausted':False,'codes':[]},'capability/state error attribution')
  a=s['attachment'];need(a[0]==0x8d41 and a[1]>0 and a[2]==0 and a[3:5]==s['native']['dimensions'] and s['status']==0x8cd5 and s['read_buffer']==0x8ce0 and s['samples']==0,'supported RBO attachment')
  need(s['channels'][:3]==[8,8,8] and s['channels'][3] in (0,8),'actual alpha storage')
  native=s['native'];need(native['fbo_rbo_tex'][1]==a[1] and all(int(native[key],16)>0 for key in ('fx','wlr','image')),'native attachment identity')
  d=s['dmabuf'];need(d is not None and d['borrowed'] is True and d['dimensions']==native['dimensions'],'actual borrowed dmabuf')
  metadata(dict(d,width=d['dimensions'][0],height=d['dimensions'][1]))
  need(all(p.get('fstat_ok') is True and all(type(p.get(k)) is int and p[k]>=0 for k in ('fd','dev','ino')) for p in d['planes']),'borrowed FD fstat identity observed')
  w,h=native['dimensions'];need((w,h)==FRAME,'prospective physical full-frame dimensions');n=w*h*4;need(0<n<=CAP-total and s['bytes']==n,'checked full-frame raw budget');total+=n
  need(s['file']==f'epoch-{e}-point-{p}.rgba','fixed exclusive raw filename')
  b=bounded(directory/s['file'],CAP);need(len(b)==n and f'{zlib.crc32(b):08x}'==s['crc32'],'raw framing/CRC')
  if p==0:
   colors=((32,192,224),(176,32,64)) if e==2 else ((245,245,245),(15,25,45))
   for y in range(h):
    for x in range(w):need(tuple(b[(y*w+x)*4:(y*w+x)*4+3])==colors[(x//8)%2],'native RGB source does not belong to current epoch')
  need(s.get('fresh_region_overflow') is not True and len(s['fresh_rectangles'])<=256 and all(len(r)==4 and 0<=r[0]<=r[2]<=w and 0<=r[1]<=r[3]<=h for r in s['fresh_rectangles']),'actual fresh region rectangles')
 for u in uniforms:
  need(u['type']==0x8b50 and u['program']>0 and u['location']>=0 and u['shader_default_float']=='mediump' and u['varying']=='mediump','uniform native program/type/qualifier')
  need(u['sampler']==[9729,9729,33071,33071] and len(u['precision_capability'])==3,'actual sampler/capability')
  source_analysis.append(halfpixel(*u['native_texture_dimensions'],u['point']<=3,u['actual_bits']))
 need(end['raw_total']==total,'cumulative raw budget')
 return {'epoch':e,'raw_total':total,'context':context,'observed_versions':[dict(egl_client_version=s['client_version'],gl_version=bytes.fromhex(s['gl_version_hex']).decode('ascii'),gl_major=s['gl_major'],gl_minor=s['gl_minor'],egl_gl_divergence=s['client_version']!=s['gl_major']) for s in samples],'uniform_comparison':source_analysis,'whole_field_causality':'NOT_PROVEN','native_present_buffer':'NOT_PROVEN','gpu_completion':'NOT_PROVEN'}
def gate(directory,gatefile,binary):
 need(directory==ROOT and directory.resolve(strict=True)==ROOT,'fixed real acquisition path')
 need(str(ROOT).startswith('/var/tmp/swayfx-mosaic-step20c-native-closure-') and ROOT.name=='acquisition','new LAB acquisition only')
 owned(directory,0o700)
 g=json.loads(bounded(gatefile,65536));need(g['source_review']=='ACCEPTED' and g['gl_observability']=='PASS' and g['runtime_authorized'] is True and g['diagnostic']=='GPU-G3' and g['acquisition_root']==str(ROOT),'independent external review/authorization gate')
 need(hashlib.sha256(binary.read_bytes()).hexdigest()==g['binary_sha256'],'distinct reviewed binary identity')
 return g

def arm(directory,e,nonce,gatefile,binary):
 gate(directory,gatefile,binary);need(len(nonce)==64 and all(x in '0123456789abcdef' for x in nonce),'nonce')
 # Prior complete success is mandatory. An existing consumed/current epoch,
 # failed A, or any unexpected future epoch prevents every subsequent arm.
 total=0
 for prior in range(1,e):total=epoch(directory,prior,nonce,total)['raw_total']
 need(e in (1,2,3),'one-shot three epochs')
 for future in range(e,5):need(not any(directory.glob(f'epoch-{future}.*')),'no retry/future token')
 exclusive(directory/f'epoch-{e}.arm',f'{nonce} {e}\n'.encode())

def plan():
 return {'schema':'G3-followup-v1','status':'EXPERIMENTAL_SOURCE_ONLY_REVIEW_REQUIRED','diagnostic':'GPU-G3','max_raw_bytes':CAP,'epochs':['A','B','A-return'],'points':STAGES,'full_field':[0,0,800,600],'ROI':[0,0,800,600],'ROI_policy':'FULL_FIELD_NO_POSTHOC_MASK','requirements':['Independent R-GPU exact-source acceptance','GL observability acceptance','Explicit new pair and distinct binary identity','External one-shot ledger reservation before compositor spawn','Explicit source A/B/A client commands with original A byte identity','If A incomplete/rejected STOP; preserve bytes, no B, no retry'],'intrusive':['glGetError consumes nonrestorable queue','glReadPixels may synchronize timing'],'unobserved':['native presented physical buffer','GPU completion','GPU object lifetime','atomic generation'],'launches_gpu':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['prepare-plan','verify-epoch','arm']);p.add_argument('--epoch',type=int);p.add_argument('--nonce');p.add_argument('--gate',type=Path);p.add_argument('--binary',type=Path);a=p.parse_args()
 if a.operation=='prepare-plan':print(json.dumps(plan(),indent=2))
 elif a.operation=='verify-epoch':print(json.dumps(epoch(ROOT,a.epoch,a.nonce),indent=2))
 else:arm(ROOT,a.epoch,a.nonce,a.gate,a.binary)
