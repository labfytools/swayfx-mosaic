"""WHY: a new ticket cannot borrow historical reservations or source reviews.
CONTRACT: freeze + independent review + publication precede every reservation.
INVARIANT: no reset/refund; failed actions remain debited, bindings never repaired.
"""
import ctypes,fcntl,hashlib,json,os,re,resource,stat,subprocess,time,uuid
from pathlib import Path
from plans import RUNS,LIMITS
TICKET='SWAYFX_MOSAIC_STEP20C_COREC_V2_FULLSCREEN_OOM_GLES_NATIVE_CLOSURE_BATCH_V1'
WL_SHA='7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837'
SOURCE_ROOT=Path(__file__).resolve().parent.parent

def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def digest(v):return hashlib.sha256(encoded(v)).hexdigest()
def canonical_lab(lab):
 p=Path(lab);need(p.is_absolute() and p.resolve()==p and p.parent==Path('/var/tmp'),'canonical direct /var/tmp LAB required')
 s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o700,'LAB mode/owner/type');return p

def clean_environment(lab):
 lab=canonical_lab(lab)
 for name in ('scratch','cache','data','pycache'):
  p=lab/name;need(p.resolve()==p and p.is_dir() and p.stat().st_uid==os.getuid(),'owned scratch/cache/data required')
 e={k:os.environ[k] for k in ('PATH','LANG','LC_ALL','TZ') if k in os.environ}
 e.update(TMPDIR=str(lab/'scratch'),TMP=str(lab/'scratch'),TEMP=str(lab/'scratch'),SMX_LAB=str(lab),XDG_CACHE_HOME=str(lab/'cache'),XDG_DATA_HOME=str(lab/'data'),PYTHONPYCACHEPREFIX=str(lab/'pycache'),CCACHE_DIR=str(lab/'cache/ccache'))
 return e

def disable_dump():
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 need(ctypes.CDLL(None).prctl(4,0,0,0,0)==0,'PR_SET_DUMPABLE failed')

def secure_read(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 try:
  s=os.fstat(fd);need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_nlink==1 and not s.st_mode&0o077,'receipt/ledger owner/type/link/mode')
  need(s.st_size<=16*1024*1024,'receipt size bound')
  with os.fdopen(fd,'r',closefd=False) as f:return json.load(f)
 finally:os.close(fd)

def durable(path,value,exclusive=False):
 p=Path(path);need(p.parent.resolve()==p.parent and p.parent.is_dir(),'canonical output parent')
 if p.exists() or p.is_symlink():
  s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_nlink==1 and not s.st_mode&0o077,'unsafe existing output')
 tmp=p.with_name(p.name+'.tmp-'+uuid.uuid4().hex)
 fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 try:
  with os.fdopen(fd,'wb') as f:f.write(encoded(value));f.flush();os.fsync(f.fileno())
  if exclusive:os.link(tmp,p);tmp.unlink()
  else:os.replace(tmp,p)
  d=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(d)
  finally:os.close(d)
 finally:
  if tmp.exists():tmp.unlink()

def source_files(root=None):
 root=root or SOURCE_ROOT;result={}
 for p in sorted(root.rglob('*')):
  need(not p.is_symlink(),'source symlink forbidden')
  if p.is_file():
   rel=p.relative_to(root).as_posix();need('__pycache__' not in p.parts and p.suffix not in ('.pyc','.png','.o','.so','.a'),'generated source artifact')
   result[rel]=sha(p)
 need(result,'empty source kit');return result

def source_modes(root=None):
 root=root or SOURCE_ROOT
 files=source_files(root);result={}
 for rel in files:
  mode=stat.S_IMODE((root/rel).stat().st_mode)
  need(mode in (0o644,0o755),'source mode not portable Git 0644/0755')
  result[rel]=oct(mode)
 return result

def git_inventory(raw,prefix,files,modes):
 # WHY: identical blob bytes do not prove file type, mode, or full inventory.
 # CONTRACT/INVARIANT: exact Git subtree, canonical portable modes, blobs only.
 need(set(files)==set(modes),'manifest mode inventory')
 need(all(v in ('0o644','0o755') for v in modes.values()),'invalid manifest modes')
 prefix=prefix.encode()+b'/';seen={}
 need(not raw or raw.endswith(b'\0'),'truncated Git tree')
 for entry in raw.split(b'\0')[:-1]:
  meta,path=entry.split(b'\t',1);mode,kind,oid=meta.split(b' ')
  need(path.startswith(prefix),'Git tree wrong prefix')
  rel=path[len(prefix):].decode('utf-8',errors='strict')
  need(rel in files and rel not in seen,'Git tree added/duplicate path')
  need(kind==b'blob' and mode in (b'100644',b'100755'),'Git tree type/mode')
  need(mode=={'0o644':b'100644','0o755':b'100755'}[modes[rel]],'Git mode differs')
  need(re.fullmatch(b'[0-9a-f]{40}',oid),'Git object identity')
  seen[rel]=oid.decode()
 need(set(seen)==set(files),'Git tree missing path')
 return seen

def published_sources(top,commit,prefix,files,modes,env):
 tree=subprocess.run(['git','-C',str(top),'ls-tree','-rz','--full-tree',commit,'--',str(prefix)],capture_output=True,env=env,timeout=4)
 need(tree.returncode==0,'published Git tree unavailable')
 git_inventory(tree.stdout,str(prefix),files,modes)
 for rel,h in files.items():
  blob=subprocess.run(['git','-C',str(top),'show',f'{commit}:{prefix/rel}'],capture_output=True,env=env,timeout=4)
  need(blob.returncode==0 and hashlib.sha256(blob.stdout).hexdigest()==h,'commit does not contain frozen bytes')


def _receipt(lab,path,expected):
 p=Path(path);need(p.resolve()==p and p.is_relative_to(lab),'runtime receipt outside new LAB')
 value=secure_read(p);need(sha(p)==expected,'receipt SHA mismatch');return value

def validate_review(lab,manifest,review,publication,rid,offline=False,check_git=True):
 lab=canonical_lab(lab);need(rid in RUNS,'historical/unknown run ID');need(RUNS[rid]['admission']!='NOT_ADMITTED' or rid=='GPU-G3','scenario NOT_ADMITTED')
 manifest,review,publication=map(Path,(manifest,review,publication))
 need(all(p.resolve()==p and p.is_relative_to(lab) for p in (manifest,review,publication)),'external admission receipt outside new LAB')
 m=secure_read(manifest);r=secure_read(review);p=secure_read(publication)
 need(m.get('ticket')==TICKET and m.get('schema')=='native-closure-source-v1' and m.get('plans')==RUNS and m.get('limits')==LIMITS,'manifest ticket/plans/schema/limits')
 need(m.get('files')==source_files() and m.get('modes')==source_modes(),'source changed/added/removed/mode after freeze')
 need(r.get('decision')=='ACCEPTED' and r.get('independent') is True and r.get('reviewer') and r['reviewer']!=m.get('author'),'independent review absent')
 need(r.get('manifest_sha256')==sha(manifest) and r.get('ticket')==TICKET,'review stale/ticket')
 case=r.get('runs',{}).get(rid,{})
 need(case.get('decision')=='ACCEPTED' and case.get('client_build_review')=='ACCEPTED','per-run client/source review absent')
 for gate in {'FS-P':('FULLSCREEN_COMPARABILITY_OFFLINE',),'FS-C':('FULLSCREEN_COMPARABILITY_OFFLINE',),'DY-C':('MIGRATION_REFOCUS_OFFLINE',),'OM-ROOT':('OOM_ROOT_NESTED_ORACLE_OFFLINE',),'OM-NESTED':('OOM_ROOT_NESTED_ORACLE_OFFLINE',),'GPU-G3':('B4',)}[rid]:
  proof=r.get('gates',{}).get(gate,{})
  need(proof.get('decision')=='ACCEPTED' and proof.get('manifest_sha256')==sha(manifest),'required gate not independently accepted')
  receipt=_receipt(lab,proof.get('receipt',''),proof.get('receipt_sha256'))
  need(receipt.get('status')=='PASS' and receipt.get('tests_run',0)>0 and receipt.get('failures')==0 and receipt.get('source_digest')==digest(m['files']),'superficial/stale offline gate')
 need(p.get('ticket')==TICKET and p.get('decision')=='VERIFIED' and p.get('offline_test_only') is offline,'publication namespace/ticket')
 commit=p.get('source_commit','');need(re.fullmatch('[0-9a-f]{40}',commit),'publication commit')
 need(p.get('manifest_sha256')==sha(manifest) and p.get('source_digest')==digest(m['files']),'publication manifest binding')
 need(p.get('origin_sha')==p.get('github_sha')==commit,'source kit unpublished')
 for name in ('origin','github'):
  obs=p.get('remote_observations',{}).get(name,{})
  need(obs.get('exit')==0 and obs.get('argv')==['git','ls-remote',name,'refs/heads/main'] and obs.get('stdout','').split()==[commit,'refs/heads/main'],'direct remote observation absent')
 if not offline and check_git:
  # Git bytes independently bind the remote commit to this portable kit.
  repo=SOURCE_ROOT
  root=subprocess.run(['git','-C',str(repo),'rev-parse','--show-toplevel'],capture_output=True,text=True,env=clean_environment(lab),timeout=4)
  need(root.returncode==0,'published Git repository unavailable');top=Path(root.stdout.strip());prefix=SOURCE_ROOT.relative_to(top)
  published_sources(top,commit,prefix,m['files'],m['modes'],clean_environment(lab))
 runtime=_receipt(lab,r.get('runtime_manifest',''),r.get('runtime_manifest_sha256'))
 need(runtime.get('ticket')==TICKET,'runtime identity ticket')
 identity=runtime['identities'][RUNS[rid]['binary']]
 need(sha(identity['binary'])==identity['binary_sha256'],'binary changed')
 if not offline and check_git:
  elf=subprocess.run(['readelf','-n',identity['binary']],capture_output=True,text=True,env=clean_environment(lab),timeout=4)
  need(elf.returncode==0 and re.findall(r'Build ID: ([0-9a-f]+)',elf.stdout)==[identity.get('build_id')],'binary BuildID mismatch')
 need(sha(identity['wlroots'])==identity['wlroots_sha256']==WL_SHA,'wlroots changed')
 need(identity.get('build_review')=='ACCEPTED' and identity.get('source_qualification')=='ACCEPTED','identity/source build unreviewed')
 build=_receipt(lab,case.get('client_build_receipt',''),case.get('client_build_receipt_sha256'))
 need(build.get('status')=='PASS' and build.get('runtime')=='NOT_RUN','client compile receipt')
 for name in ('pointer-daemon','static-reference',RUNS[rid]['client']):
  binary=lab/'followup-work/client-build'/name
  need(sha(binary)==build['generated'][name] and build['inputs']['clients/'+name+'.c']==m['files']['graphics/clients/'+name+'.c'],'client generated/source mismatch')
 need(build['inputs']['protocols/xdg-shell.xml']==m['files']['graphics/protocols/xdg-shell.xml'] and build['inputs']['protocols/wlr-virtual-pointer-unstable-v1.xml']==m['files']['graphics/protocols/wlr-virtual-pointer-unstable-v1.xml'],'protocol source binding')
 if rid=='GPU-G3':
  need(all(identity['binary_sha256']!=other.get('binary_sha256') for name,other in runtime['identities'].items() if name!='gpu'),'GPU new distinct ELF required')
  from gpu_handler import validate_binding
  validate_binding(lab,case,identity,sha(manifest))
 if rid in ('OM-ROOT','OM-NESTED'):
  need(case.get('oom_source_review')=='ACCEPTED' and case.get('variant_identity')=='COREC_V2_NATIVE_OOM_DIAGNOSTIC' and case.get('source_manifest_sha256')==sha(manifest),'OOM native/source variant review absent')
 if rid=='OM-NESTED' and case.get('root_dependency_override'):
  v=case['root_dependency_override'];need(v.get('independent') is True and v.get('reviewer')!=m['author'] and v.get('decision')=='ACCEPTED' and v.get('manifest_sha256')==sha(manifest) and v.get('rationale') and v.get('no_common_native_fault') is True,'invalid independent nested dependency review')
 return dict(identity,prospective=case,manifest=str(manifest),review=str(review),publication=str(publication),manifest_sha256=sha(manifest),review_sha256=sha(review),publication_sha256=sha(publication),runtime_manifest_sha256=r['runtime_manifest_sha256'],source_digest=digest(m['files']),client_binary_sha256=build['generated'][RUNS[rid]['client']])

class Ledger:
 def __init__(self,lab,path=None,offline=False):
  self.lab=canonical_lab(lab);self.offline=offline;self.path=Path(path) if path else self.lab/'native-closure-budget.json'
  need(self.path.parent.resolve()==self.path.parent and self.path.parent.is_relative_to(self.lab),'ledger outside new LAB/canonical parent')
  need(not self.path.is_symlink(),'ledger symlink')
  if offline:need('OFFLINE_TEST_ONLY' in self.path.parts,'offline namespace')
  else:need(self.path==self.lab/'native-closure-budget.json','real ledger fixed new path')
  self.lock=self.path.with_name(self.path.name+'.lock')
 def transaction(self,fn,initialize=False):
  fd=os.open(self.lock,os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
  try:
   s=os.fstat(fd);need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_nlink==1 and not s.st_mode&0o077,'lock owner/type/link/mode')
   fcntl.flock(fd,fcntl.LOCK_EX);need(self.lock.lstat().st_ino==s.st_ino,'lock inode changed')
   if initialize:need(not self.path.exists(),'ledger already initialized');d=None
   else:
    d=secure_read(self.path);need(d.get('ticket')==TICKET and d.get('lab')==str(self.lab) and d.get('uid')==os.getuid(),'old ticket/LAB/UID')
    need(d.get('namespace')==('OFFLINE_TEST_ONLY' if self.offline else 'REAL') and d.get('limits')==LIMITS,'namespace/limits')
   result,new=fn(d);durable(self.path,new,exclusive=initialize);return result
  finally:os.close(fd)
 def initialize(self):
  return self.transaction(lambda _:(None,dict(ticket=TICKET,lab=str(self.lab),uid=os.getuid(),namespace='OFFLINE_TEST_ONLY' if self.offline else 'REAL',limits=LIMITS,runs=[])),True)
 def admit(self,rid,manifest,review,publication):
  auth=validate_review(self.lab,manifest,review,publication,rid,offline=self.offline)
  def reserve(d):
   spec=RUNS[rid];need(not any(x['id']==rid for x in d['runs']),'consumed run; no retry')
   if rid=='OM-NESTED':
    roots=[x for x in d['runs'] if x['id']=='OM-ROOT'];good=len(roots)==1 and roots[0]['status']=='COMPLETED' and roots[0].get('outcome',{}).get('status')=='PARTIALLY_FEASIBLE' and roots[0].get('outcome',{}).get('scientific_cleanup') is True
    need(good or auth['prospective'].get('root_dependency_override'),'root unresolved; independent dependency review required')
   if rid=='FS-C':
    controls=[x for x in d['runs'] if x['id']=='FS-P'];need(len(controls)==1 and controls[0]['status']=='COMPLETED' and controls[0].get('outcome',{}).get('status')=='PARTIALLY_FEASIBLE','fullscreen control incomplete')
   need(len(d['runs'])<LIMITS['runs'] and sum(x['capture_limit'] for x in d['runs'])+spec['capture_limit']<=LIMITS['captures'],'global cap')
   token=uuid.uuid4().hex;r=dict(id=rid,token=token,started_ns=time.monotonic_ns(),capture_limit=spec['capture_limit'],action_limits=spec['action_limits'],actions={},status='RESERVED',bindings=auth)
   d['runs'].append(r);return dict(auth,token=token,run_id=rid,lab=str(self.lab),offline=self.offline),d
  return self.transaction(reserve)
 def action_debit(self,auth,*kinds):
  fresh=validate_review(self.lab,auth['manifest'],auth['review'],auth['publication'],auth['run_id'],offline=self.offline,check_git=False)
  def update(d):
   rows=[x for x in d['runs'] if x['id']==auth['run_id']];need(len(rows)==1,'missing reservation');r=rows[0]
   need(r['token']==auth['token'] and r['bindings']==fresh and r['status']=='RESERVED','historical token/stale binding/completed')
   need(0<=time.monotonic_ns()-r['started_ns']<150_000_000_000,'duration exhausted')
   actions=dict(r['actions'])
   for kind in kinds:
    limit=r['capture_limit'] if kind=='capture' else r['action_limits'].get(kind,0)
    need(actions.get(kind,0)<limit,'local action exhausted: '+kind);actions[kind]=actions.get(kind,0)+1
   total=sum(x['actions'].get('capture',0) for x in d['runs'])+actions.get('capture',0)-r['actions'].get('capture',0)
   need(total<=LIMITS['captures'],'global capture cap');r['actions']=actions;return None,d
  return self.transaction(update)
 def complete(self,auth,outcome):
  def finish(d):
   rows=[x for x in d['runs'] if x['id']==auth['run_id']];need(len(rows)==1,'missing reservation');r=rows[0]
   need(r['token']==auth['token'] and r['status']=='RESERVED','historical token/completed');r.update(status='COMPLETED',finished_ns=time.monotonic_ns(),outcome=outcome);return None,d
  self.transaction(finish)
