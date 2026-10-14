"""WHY/CONTRACT/INVARIANT: ticket counters are durable, never refunded."""
import fcntl,hashlib,json,os,time,uuid
from pathlib import Path
LAB=Path('/home/fy59/swayfx-mosaic-core-recovery-qmhckba5')
BASE=LAB/'graphics'
TICKET='SWAYFX_MOSAIC_STEP20C_CORE_RECOVERY_OOM_AND_DCC_QUALIFICATION_BATCH_V1'
WL=Path('/usr/lib/libwlroots-0.20.so')
WL_SHA='7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def clean_environment():
 e=os.environ.copy()
 for k in list(e):
  if k in ('DISPLAY','WAYLAND_DISPLAY','SWAYSOCK','XDG_RUNTIME_DIR','LD_PRELOAD','LD_LIBRARY_PATH','DBUS_SESSION_BUS_ADDRESS','XDG_CURRENT_DESKTOP','DESKTOP_SESSION','XDG_ACTIVATION_TOKEN','DESKTOP_STARTUP_ID') or k.startswith(('WLR_','PI_','OPT_','SAVED_','XDG_SESSION_')):e.pop(k,None)
 return e

def durable(p,value,exclusive=False):
 p=Path(p);tmp=p.with_name(p.name+'.tmp-'+uuid.uuid4().hex)
 with tmp.open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 if exclusive:
  os.link(tmp,p);tmp.unlink()
 else:os.replace(tmp,p)
 fd=os.open(p.parent,os.O_DIRECTORY);os.fsync(fd);os.close(fd)

def transact(fn,path=LAB/'budget.json'):
 # Lock inode stays stable while JSON replacement is atomic.
 with Path(str(path)+'.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);d=json.loads(Path(path).read_text());need(d['ticket']==TICKET,'old ticket');r=fn(d);durable(path,d);return r

def validate_review(manifest,review):
 need(review.get('decision')=='ACCEPTED' and review.get('independent') is True,'independent review absent')
 need(review.get('manifest_sha256')==sha(manifest),'stale review')
 m=json.loads(Path(manifest).read_text());need(m['ticket']==TICKET and m['lab']==str(LAB),'wrong lab/ticket')
 for p,h in m['files'].items():need(sha(p)==h,'frozen bytes changed: '+p)
 need(sha(WL)==WL_SHA,'wlroots changed')
 return m

def begin(rid):
 from plans import RUNS
 m=validate_review(BASE/'pre-run-manifest.json',json.loads((BASE/'review.json').read_text()))
 need(rid in m.get('authorized_runs',[]),'family not reviewed/authorized')
 need(not (BASE/'runs'/rid/'run').exists(),'pre-existing run folder')
 spec=RUNS[rid];auth=m['identities'][spec['binary']];need(sha(auth['binary'])==auth['binary_sha256'],'binary changed')
 def reserve(d):
  need(d['limits']['runs']==11 and d['limits']['captures']==160 and d['limits']['captures_per_run']==18 and d['limits']['duration_s']==150,'wrong ticket limits')
  need(not any(r['id']==rid for r in d['runs']),'consumed run')
  need(len(d['runs'])<11 and sum(r.get('capture_limit',r.get('captures',0)) for r in d['runs'])+spec['capture_limit']<=160,'global budget')
  need(sum(r.get('campaign')=='S' for r in d['runs'])<9,'S run budget')
  row=dict(id=rid,campaign='S',token=uuid.uuid4().hex,started_ns=time.monotonic_ns(),capture_limit=spec['capture_limit'],actions={},status='RESERVED')
  d['runs'].append(row);return row
 row=transact(reserve);durable(BASE/'runs'/rid/'reservation.json',row,True);return auth

def action_debit(rid,*kinds):
 from plans import RUNS
 def update(d):
  rows=[r for r in d['runs'] if r['id']==rid];need(len(rows)==1,'reservation missing');r=rows[0]
  for k in kinds:
   limit=RUNS[rid]['capture_limit'] if k=='capture' else RUNS[rid]['action_limits'][k]
   need(r['actions'].get(k,0)<limit,'local '+k+' exhausted');r['actions'][k]=r['actions'].get(k,0)+1
 transact(update)
