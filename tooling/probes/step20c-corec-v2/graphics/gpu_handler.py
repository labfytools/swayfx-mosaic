"""Narrow wiring of frozen G2 adapter to graphics Session. No native execution at import."""
import importlib,sys,json,re
from pathlib import Path
from engine import Session
from gate import need,sha

def validate_source_binding(lab,review):
    need(review.get('gpu_source_review')=='ACCEPTED' and review.get('gl_observability_preflight')=='ACCEPTED' and review.get('native_gl_status')=='NOT_RUN' and review.get('build_review')=='ACCEPTED' and review.get('pair')==3,'G2 independent source/GL/build3 acceptance missing')
    manifest=Path(review.get('gpu_source_manifest',''));need(manifest.is_absolute() and manifest.resolve()==manifest and manifest.is_relative_to(lab),'G2 canonical reviewed source manifest path')
    expected=review.get('gpu_source_manifest_sha256','')
    need(re.fullmatch('[0-9a-f]{64}',expected) and expected==sha(manifest),'G2 exact reviewed source freeze')
    m=json.loads(manifest.read_text());root=lab/'gpu-kit'
    # WHY/CONTRACT/INVARIANT: external source remains frozen; its adapter is
    # imported only after actual byte validation, never by a status string alone.
    files=m['files']
    for rel,h in files.items():
        p=lab/rel;need(not Path(rel).is_absolute() and p.resolve().is_relative_to(lab) and sha(p)==h['sha256'] and p.stat().st_size==h['bytes'],'G2 frozen source changed')
    need({str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}=={str(Path(rel).relative_to('gpu-kit')) for rel in files if Path(rel).parts[0]=='gpu-kit'},'G2 source addition/removal')
    for key in ('gpu_source_review','gl_observability_preflight','build_review'):
        path=Path(review[key+'_receipt']);need(path.resolve().is_relative_to(lab) and sha(path)==review[key+'_receipt_sha256'],'G2 review receipt bytes')
    binding=review['binding'];client=Path(binding['client']);need(client.resolve().is_relative_to(lab) and sha(client)==binding['client_sha256'],'G2 reviewed client bytes')
    gatefile=Path(review['gate_file']);need(gatefile.resolve().is_relative_to(lab) and sha(gatefile)==review['gate_file_sha256'],'G2 native external gate bytes')
    # WHY: the frozen adapter's legacy PASS admits instrumentation capability,
    # not an observation made before its first native epoch. CONTRACT/INVARIANT:
    # require explicit scope and retain native NOT_RUN until measured metadata.
    native_gate=json.loads(gatefile.read_text())
    need(native_gate.get('gl_observability')=='PASS' and native_gate.get('gl_observability_scope')=='PREFLIGHT_CAPABILITY_ONLY' and native_gate.get('native_gl_status')=='NOT_RUN','G2 legacy PASS must be scoped preflight only')

def modules(lab):
    path=str(lab/'gpu-kit');sys.path.insert(0,path)
    try:
        # These names have no graphics-kit peer; source freeze includes both.
        protocol=importlib.import_module('protocol');scenario=importlib.import_module('scenario')
        need(Path(protocol.__file__).resolve()==lab/'gpu-kit/protocol.py' and Path(scenario.__file__).resolve()==lab/'gpu-kit/scenario.py','G2 module origin')
        return scenario
    finally:sys.path.remove(path)

class CompositorEnvironment:
    def __init__(self,session):self.session=session
    def update(self,**fields):
        need(set(fields)=={'MOSAIC_G2_DIR','MOSAIC_G2_NONCE','WLR_RENDERER'},'G2 compositor environment scope')
        need(fields['MOSAIC_G2_DIR']==str(self.session.lab/'gpu-work/acquisition') and re.fullmatch('[0-9a-f]{64}',fields['MOSAIC_G2_NONCE']) and fields['WLR_RENDERER']=='gles2','G2 acquisition environment')
        self.session.compositor_environment=fields

class AdapterSession:
    """Compatibility view of pair#3, without changing the actual Session spec.
    WHY: frozen adapter calls its static SceneFX branch 'core'. CONTRACT: real
    identity/admission remain gpu; no other binary or environment is translated.
    """
    def __init__(self,session):
        need(session.spec['id']=='G2' and session.spec['binary']=='gpu','G2 real Session identity')
        self.session=session;self.spec=dict(session.spec,binary='core');self.env=CompositorEnvironment(session)
    def __getattr__(self,name):return getattr(self.session,name)
    def debit(self,*kinds):
        need(kinds==('mutation',),'unexpected direct G2 adapter debit')
        # Each explicit epoch reservation precedes arm, without retry/refund.
        self.session.debit('mutation','hook')
    def spawn(self,name,argv,debug=False):
        need(name in ('g2-reference','g2-background','g2-glass'),'G2 client role')
        return self.session.spawn(name,argv,True)

class GPUSceneSession(Session):
    def close_client(self,name,command='close'):
        need(name in ('g2-reference','g2-background','g2-glass') and command=='close','G2 scientific closure role')
        try:
            super().close_client(name,command)
            proof=self.closed[-1];raw=self.log(name)
            mode='background' if name=='g2-background' else 'glass' if name=='g2-glass' else 'reference'
            need(re.search(rf'EXIT ns=\d+ mode={mode} error=0 commits=\d+',raw),'G2 exact client role/raw error')
            role='zwlr_layer_surface_v1' if mode=='background' else 'xdg_toplevel'
            need(re.search(rf'{role}#\d+\.destroy\(\)',raw) and re.search(r'wl_surface#\d+\.destroy\(\)',raw),'G2 native role destruction')
            proof.update(role=role,scientific_client=True,meaning='layer closure without invented XDG ownership' if mode=='background' else 'G2 XDG closure')
        except Exception as error:
            if self.closed and self.closed[-1]['pid']==self.proc[name].pid:self.closed[-1].update(status='INCONCLUSIVE',failure=str(error))
            raise

def run(s):
    review=s.auth['prospective'];validate_source_binding(s.lab,review)
    binding=dict(review['binding'],nonce=s.auth['token']*2)
    need(binding['source_manifest_sha256']==s.auth['manifest_sha256'] and binding['binary']==s.auth['binary'] and binding['gate_file']==review['gate_file'],'G2 exact reviewed reservation/binary/gate binding')
    result=modules(s.lab).run(AdapterSession(s),dict(binding,G2_ledger_reserved=True))
    need(result['native_source_A_Areturn_exact'] and result['whole_H1_A_Areturn']['equal'] and all(v['equal'] for v in result['whole_H2_A_B_Areturn']),'G2 measured return mismatch')
    return 'PARTIALLY_FEASIBLE'
