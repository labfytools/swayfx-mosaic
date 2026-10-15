"""V2 reviewed admission and durable debit. No reset/refund or ledger CLI.

WHY: reservation failure is consumed; immutable input SHA and run token bind
all later actions. The lock inode remains stable across atomic JSON replaces.
OFFLINE_TEST_ONLY ledgers are never accepted as native-run authorizations.
"""
import fcntl,hashlib,json,os,re,stat,time,uuid
from pathlib import Path
from plans import RUNS,LIMITS
TICKET="SWAYFX_MOSAIC_STEP20C_REBUILD_FROM_GIT_COREC_OOM_GPU_NIGHT_SHIFT_V1"
WL_SHA="7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837"
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,sort_keys=True,indent=2)+"\n").encode()
def digest(value):return hashlib.sha256(encoded(value)).hexdigest()
def canonical_lab(lab):
 p=Path(lab);need(p.is_absolute() and str(p)==str(p.resolve()) and p.parent==Path("/var/tmp"),"canonical direct /var/tmp LAB required")
 st=p.stat();need(st.st_uid==os.getuid() and stat.S_ISDIR(st.st_mode),"LAB owner/type")
 return p

def clean_environment(lab):
 lab=canonical_lab(lab)
 need((lab/"scratch").resolve()==lab/"scratch" and (lab/"scratch").stat().st_uid==os.getuid(),"canonical owned scratch required")
 # Allowlist avoids inherited loader, backend, activation and desktop authority.
 e={k:os.environ[k] for k in ("PATH","LANG","LC_ALL","TZ") if k in os.environ}
 e.update(TMPDIR=str(lab/"scratch"),TMP=str(lab/"scratch"),TEMP=str(lab/"scratch"),SMX_LAB=str(lab),XDG_CACHE_HOME=str(lab/"cache"),XDG_DATA_HOME=str(lab/"data"),PYTHONPYCACHEPREFIX=str(lab/"pycache"),CCACHE_DIR=str(lab/"cache/ccache"))
 return e

def durable(path,value,exclusive=False):
 p=Path(path);tmp=p.with_name(p.name+".tmp-"+uuid.uuid4().hex)
 try:
  with tmp.open("xb") as f:f.write(encoded(value));f.flush();os.fsync(f.fileno())
  if exclusive:os.link(tmp,p);tmp.unlink()
  else:os.replace(tmp,p)
  fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if tmp.exists():tmp.unlink()

class Ledger:
 def __init__(self,lab,path=None,offline=False):
  self.lab=canonical_lab(lab);self.offline=offline
  self.path=Path(path) if path else self.lab/"budget.json"
  need(self.path.parent.resolve().is_relative_to(self.lab),"ledger outside LAB")
  need(not self.path.is_symlink(),"ledger symlink")
  if offline:need("OFFLINE_TEST_ONLY" in self.path.parts,"offline fixture namespace required")
  else:need(self.path==self.lab/"budget.json","real ledger fixed path")
  self.lock=self.path.with_name(self.path.name+".lock")
 def transaction(self,fn,initialize=False):
  fd=os.open(self.lock,os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
  try:
   st=os.fstat(fd);need(st.st_uid==os.getuid() and stat.S_ISREG(st.st_mode) and st.st_nlink==1 and not st.st_mode&0o077,"stable lock owner/type/link")
   fcntl.flock(fd,fcntl.LOCK_EX)
   need(os.stat(self.lock,follow_symlinks=False).st_ino==st.st_ino,"lock inode changed")
   if initialize:need(not self.path.exists(),"ledger already initialized");d=None
   else:
    s=self.path.lstat();need(s.st_uid==os.getuid() and stat.S_ISREG(s.st_mode) and s.st_nlink==1,"ledger owner/type/link")
    d=json.loads(self.path.read_text());need(d["ticket"]==TICKET and d["lab"]==str(self.lab) and d["uid"]==os.getuid(),"old ticket/LAB/UID")
    need(d["namespace"]==("OFFLINE_TEST_ONLY" if self.offline else "REAL") and d["limits"]==LIMITS,"namespace/limits")
   value,new=fn(d);durable(self.path,new,exclusive=initialize);return value
  finally:os.close(fd)
 def initialize(self):
  return self.transaction(lambda _: (None,dict(ticket=TICKET,lab=str(self.lab),uid=os.getuid(),namespace="OFFLINE_TEST_ONLY" if self.offline else "REAL",limits=LIMITS,runs=[])),True)
 def admit(self,rid,manifest,review,publication):
  auth=validate_review(self.lab,manifest,review,publication,rid,offline=self.offline)
  def reserve(d):
   spec=RUNS[rid]
   # WHY/CONTRACT/INVARIANT: O2 is dependent evidence, never a retry after O1
   # availability or invariant failure. Missing/unfinished O1 blocks admission.
   if rid=='O2':
    prior=[r for r in d['runs'] if r['id']=='O1']
    need(len(prior)==1 and prior[0]['status']=='COMPLETED' and prior[0].get('outcome',{}).get('status')=='PARTIALLY_FEASIBLE',"O1 critical/unresolved failure blocks O2")
   need(not any(r["id"]==rid for r in d["runs"]),"consumed run")
   need(len(d["runs"])<14 and sum(r["capture_limit"] for r in d["runs"])+spec["capture_limit"]<=180,"global budget")
   token=uuid.uuid4().hex;r=dict(id=rid,token=token,started_ns=time.monotonic_ns(),capture_limit=spec["capture_limit"],action_limits=spec["action_limits"],actions={},status="RESERVED",bindings=auth)
   d["runs"].append(r);return dict(auth,token=token,run_id=rid,lab=str(self.lab),offline=self.offline),d
  return self.transaction(reserve)
 def action_debit(self,auth,*kinds):
  # Revalidate all frozen source/review/publication/binary bytes before each action.
  fresh=validate_review(self.lab,auth["manifest"],auth["review"],auth["publication"],auth["run_id"],offline=self.offline)
  def update(d):
   rows=[r for r in d["runs"] if r["id"]==auth["run_id"]];need(len(rows)==1,"missing reservation");r=rows[0]
   need(r["token"]==auth["token"] and r["bindings"]==fresh and r["status"]=="RESERVED","token/stale bindings/completed")
   need(time.monotonic_ns()-r["started_ns"]<150_000_000_000,"duration exhausted")
   actions=dict(r["actions"])
   for kind in kinds:
    limit=r["capture_limit"] if kind=="capture" else r["action_limits"].get(kind,0)
    need(actions.get(kind,0)<limit,"local "+kind+" exhausted");actions[kind]=actions.get(kind,0)+1
   r["actions"]=actions;return None,d
  return self.transaction(update)
 def complete(self,auth,outcome):
  def finish(d):
   rows=[r for r in d["runs"] if r["id"]==auth["run_id"]];need(len(rows)==1,"missing reservation");r=rows[0]
   need(r["token"]==auth["token"] and r["status"]=="RESERVED","token/completed")
   r.update(status="COMPLETED",finished_ns=time.monotonic_ns(),outcome=outcome);return None,d
  self.transaction(finish)

def validate_review(lab,manifest,review,publication,rid,offline=False):
 lab=canonical_lab(lab);manifest=Path(manifest);review=Path(review);publication=Path(publication)
 m=json.loads(manifest.read_text());r=json.loads(review.read_text());p=json.loads(publication.read_text())
 need(m.get("ticket")==TICKET and m.get("lab")==str(lab),"old ticket/LAB manifest")
 need(m.get("schema")=="graphics-v2-frozen-inputs" and m.get("limits")==LIMITS and m.get("plans")==RUNS,"manifest schema/plans/caps")
 need(r.get("decision")=="ACCEPTED" and r.get("independent") is True and r.get("reviewer")!=m.get("author") and r.get("reviewer"),"independent review absent")
 need(r.get("manifest_sha256")==sha(manifest) and rid in r.get("authorized_runs",[]),"stale review/case not admitted")
 if RUNS[rid]["admission"]=="NOT_ADMITTED":
  need(rid in ('P1','C8','O1','O2','G2'),"scenario NOT_ADMITTED")
  prospective=r.get('prospective',{}).get(rid,{})
  need(prospective.get('decision')=='ACCEPTED' and prospective.get('source_manifest_sha256')==sha(manifest),"prospective case review absent/stale")
  need(prospective.get('client_build_review')=='ACCEPTED',"new client/build review absent")
  if rid in ('P1','C8'):
   cb=Path(prospective.get('client_binary',''));cr=Path(prospective.get('client_build_receipt',''))
   need(cb==lab/'graphics-next-work/client-build/fullscreen-client' and sha(cb)==prospective.get('client_binary_sha256'),"new fullscreen client bytes")
   need(cr.resolve().is_relative_to(lab) and sha(cr)==prospective.get('client_build_receipt_sha256'),"new client build receipt bytes")
   compile_receipt=json.loads(cr.read_text())
   need(compile_receipt.get('status')=='PASS' and compile_receipt['generated']['fullscreen-client']==sha(cb) and compile_receipt['inputs']['clients/fullscreen-client.c']==m['files']['clients/fullscreen-client.c'],"client compile/source binding")
  if rid in ('O1','O2'):
   need(prospective.get('oom_source_review_sha256')=='a953a38b49bea11e9c19e84ed2d8218a16b2e5d980e0ba57677eeee0ddf62c6c',"OOM source review binding")
   need(sha(lab/'review-oom-runtime/oom-source-receipt.json')==prospective['oom_source_review_sha256'],"OOM source review bytes changed")
   need(prospective.get('variant_identity')=='COREC_V2_NATIVE_OOM_DIAGNOSTIC',"OOM variant identity")
 root=Path(m["source_root"]);need(root.resolve()==root and root.is_relative_to(lab),"source root outside LAB")
 need(m.get("files"),"empty inputs")
 for rel,h in m["files"].items():
  path=root/rel;need(not Path(rel).is_absolute() and path.resolve().is_relative_to(root) and path.is_file(),"input path")
  need(not any(v in path.parts for v in ("runs","results","logs","build","__pycache__")) and path not in (manifest,review,publication),"mutable/self input")
  need(sha(path)==h,"frozen source changed: "+rel)
 actual={str(x.relative_to(root)) for x in root.rglob("*") if x.is_file()}
 need(actual==set(m["files"]),"unfrozen source addition/removal")
 # Full source-only kit (including core recipes/patches/tests) has a separate,
 # immutable manifest outside the source tree. Parent records remote observation;
 # matching hex strings alone do not bind source bytes to that observation.
 kit_manifest=Path(m["kit_manifest"])
 need(sha(kit_manifest)==m["kit_manifest_sha256"],"full kit manifest changed")
 kit=json.loads(kit_manifest.read_text());kit_root=Path(kit["source_root"])
 need(kit_root.resolve()==kit_root and kit_root.is_relative_to(lab) and kit.get("ticket")==TICKET,"full kit root/ticket")
 need(root.is_relative_to(kit_root),"graphics outside full kit")
 need(not kit_manifest.is_relative_to(kit_root),"full kit manifest self-cycle")
 need(kit.get("files"),"empty full kit")
 for rel,h in kit["files"].items():
  file=kit_root/rel
  need(not Path(rel).is_absolute() and file.resolve().is_relative_to(kit_root) and sha(file)==h,"full kit source changed")
 need({str(x.relative_to(kit_root)) for x in kit_root.rglob("*") if x.is_file()}==set(kit["files"]),"full kit added/removed source")
 need(p.get("kit_manifest_sha256")==sha(kit_manifest) and p.get("source_commit")==kit.get("source_commit")==p.get("origin_sha"),"publication not bound to full source kit")
 source_digest=digest(m["files"])
 need(p.get("ticket")==TICKET and p.get("source_digest")==source_digest and p.get("decision")=="VERIFIED" and p.get("origin_sha")==p.get("github_sha") and re.fullmatch(r"[0-9a-f]{40}",p.get("origin_sha","")),"source kit unpublished")
 need(p.get("offline_test_only",False)==offline,"publication namespace")
 if rid=='G2':
  from gpu_handler import validate_source_binding
  validate_source_binding(lab,r.get('prospective',{}).get(rid,{}))
 auth=m["identities"][RUNS[rid]["binary"]]
 need(sha(auth["binary"])==auth["binary_sha256"],"binary changed")
 if rid in ('O1','O2','G2'):
  need(auth['binary_sha256'] not in (m['identities']['core']['binary_sha256'],m['identities']['pristine']['binary_sha256']),"distinct diagnostic ELF required")
 need(sha(auth["wlroots"])==auth["wlroots_sha256"]==WL_SHA,"wlroots changed")
 if rid=='G2':need(all(other.get('binary_sha256')!=auth['binary_sha256'] for name,other in m['identities'].items() if name!='gpu'),'GPU pair3 must differ from every other ELF')
 need(auth.get("build_review")=="ACCEPTED" and auth.get("source_qualification")=="ACCEPTED","binary/source qualification pending")
 return dict(auth,prospective=r.get('prospective',{}).get(rid,{}),manifest=str(manifest),review=str(review),publication=str(publication),manifest_sha256=sha(manifest),review_sha256=sha(review),publication_sha256=sha(publication),source_digest=source_digest)
