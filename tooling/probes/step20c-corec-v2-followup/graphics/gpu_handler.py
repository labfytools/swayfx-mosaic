"""New G3 wiring only. Import never arms a hook, reserves or launches a client."""
import importlib,json,os,re,stat,sys
from pathlib import Path
import gate
from engine import Session
from gate import need,sha


def validate_binding(lab,case,identity,manifest_sha):
    # WHY: G2 qualification cannot authorize a new native G3 ELF or source.
    # CONTRACT: independent source/capability/build receipts bind final bytes.
    # INVARIANT: no ACCEPTED status is manufactured by this adapter.
    need(case.get('gpu_source_review')=='ACCEPTED' and case.get('gl_observability_preflight')=='ACCEPTED' and case.get('build_review')=='ACCEPTED' and case.get('native_gl_status')=='NOT_RUN','GPU source/capability/build review absent')
    for name in ('gpu_source_review','gl_observability_preflight','build_review'):
        receipt=gate._receipt(lab,case.get(name+'_receipt',''),case.get(name+'_receipt_sha256'))
        need(receipt.get('decision')=='ACCEPTED' and receipt.get('independent') is True and receipt.get('manifest_sha256')==manifest_sha,'GPU independent exact-byte receipt missing')
    source=gate._receipt(lab,case.get('gpu_source_manifest',''),case.get('gpu_source_manifest_sha256'))
    need(source.get('schema')=='G3-relative-source-freeze-v1' and source.get('files'),'GPU new relative freeze')
    root=gate.SOURCE_ROOT/'gpu'
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    need(actual==set(source['files']),'GPU source added/removed')
    for rel,record in source['files'].items():
        p=root/rel;need(not Path(rel).is_absolute() and p.resolve()==p and p.is_relative_to(root),'GPU source path')
        need(sha(p)==record['sha256'] and oct(stat.S_IMODE(p.stat().st_mode))==record['mode'],'GPU frozen source changed')
    binding=case.get('binding',{});client=Path(binding.get('client',''))
    need(client.resolve()==client and client.is_relative_to(lab) and sha(client)==binding.get('client_sha256'),'GPU newly built client bytes')
    need(binding.get('binary')==identity['binary'] and binding.get('source_manifest_sha256')==manifest_sha,'GPU binary/source binding')
    build=gate._receipt(lab,case.get('gpu_client_build_receipt',''),case.get('gpu_client_build_receipt_sha256'))
    need(build.get('status')=='PASS' and build.get('source_sha256')==sha(root/'clients-g2.c') and build.get('client_sha256')==sha(client),'GPU generated client/source receipt')
    gatefile=Path(case.get('gate_file',''));native=gate._receipt(lab,gatefile,case.get('gate_file_sha256'))
    acquisition=lab/'gpu-work/acquisition'
    need(acquisition.resolve()==acquisition and acquisition.is_dir() and acquisition.stat().st_uid==os.getuid() and acquisition.stat().st_mode&0o777==0o700,'GPU acquisition root/mode')
    need(native.get('source_review')=='ACCEPTED' and native.get('gl_observability')=='PASS' and native.get('runtime_authorized') is True and native.get('diagnostic')=='GPU-G3' and native.get('acquisition_root')==str(acquisition) and native.get('binary_sha256')==identity['binary_sha256'],'GPU native external authorization')
    need(binding.get('gate_file')==str(gatefile) and binding.get('reviewed_scene_sha256')==case.get('reviewed_scene_sha256') and re.fullmatch('[0-9a-f]{64}',case.get('reviewed_scene_sha256','')),'GPU final scene/binding missing')
    return binding


def modules(lab):
    path=gate.SOURCE_ROOT/'gpu';previous=os.environ.get('MOSAIC_G3_DIR');os.environ['MOSAIC_G3_DIR']=str(lab/'gpu-work/acquisition');sys.path.insert(0,str(path))
    try:
        protocol=importlib.import_module('protocol');scenario=importlib.import_module('scenario');validator=importlib.import_module('validate_source')
        need(all(Path(m.__file__).resolve()==path/(name+'.py') for m,name in ((protocol,'protocol'),(scenario,'scenario'),(validator,'validate_source'))),'GPU module origin mismatch')
        need(protocol.ROOT==lab/'gpu-work/acquisition','GPU imported wrong acquisition root')
        return scenario
    finally:
        sys.path.remove(str(path))
        if previous is None:os.environ.pop('MOSAIC_G3_DIR',None)
        else:os.environ['MOSAIC_G3_DIR']=previous

class CompositorEnvironment:
    def __init__(self,session):self.session=session
    def update(self,**fields):
        need(set(fields)=={'MOSAIC_G3_DIR','MOSAIC_G3_NONCE','WLR_RENDERER'},'GPU compositor-only environment scope')
        need(fields['MOSAIC_G3_DIR']==str(self.session.lab/'gpu-work/acquisition') and re.fullmatch('[0-9a-f]{64}',fields['MOSAIC_G3_NONCE']) and fields['WLR_RENDERER']=='gles2','GPU private acquisition environment')
        self.session.compositor_environment=fields

class AdapterSession:
    def __init__(self,session):
        need(session.spec['id']=='GPU-G3' and session.spec['binary']=='gpu','real GPU-G3 Session identity')
        self.session=session;self.spec=session.spec;self.env=CompositorEnvironment(session)
    def __getattr__(self,name):return getattr(self.session,name)
    def debit(self,*kinds):
        need(kinds==('mutation',),'GPU adapter unexpected direct debit');self.session.debit('mutation','hook')
    def spawn(self,name,argv,debug=False):
        need(name in ('g2-reference','g2-background','g2-glass'),'GPU client role');return self.session.spawn(name,argv,True)

class GPUSceneSession(Session):
    def close_client(self,name,command='close',scenario=None):
        need(name in ('g2-reference','g2-background','g2-glass') and command=='close','GPU scientific close role')
        try:
            super().close_client(name,command)
            raw=self.log(name);proof=self.closed[-1]
            mode={'g2-reference':'reference','g2-background':'background','g2-glass':'glass'}[name]
            role='zwlr_layer_surface_v1' if mode=='background' else 'xdg_toplevel'
            need(re.search(rf'EXIT ns=\d+ mode={mode} error=0 commits=\d+',raw),'GPU exact client exit role')
            need(re.search(rf'{role}#\d+\.destroy\(\)',raw) and re.search(r'wl_surface#\d+\.destroy\(\)',raw),'GPU native role wire destruction')
            proof.update(role=role,scientific_client=True,meaning='actual layer closure' if mode=='background' else 'actual GPU XDG closure')
        except Exception as exc:
            if self.closed and self.closed[-1]['pid']==self.proc[name].pid:self.closed[-1].update(status='INCONCLUSIVE',failure=str(exc))
            raise

def run(s):
    case=s.auth['prospective'];binding=validate_binding(s.lab,case,s.auth,s.auth['manifest_sha256'])
    result=modules(s.lab).run(AdapterSession(s),dict(binding,nonce=s.auth['token']*2,G3_ledger_reserved=True))
    need(result['native_source_A_Areturn_exact'] and result['whole_H1_A_Areturn']['equal'] and all(x['equal'] for x in result['whole_H2_A_B_Areturn']),'GPU measured return mismatch')
    return 'PARTIALLY_FEASIBLE'
