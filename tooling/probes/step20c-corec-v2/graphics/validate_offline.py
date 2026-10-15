"""Run targeted non-GUI validation and retain its command/output receipt."""
import argparse,subprocess,sys
from pathlib import Path
from gate import canonical_lab,clean_environment,durable,sha

def validate(lab,gpu_source_manifest=None):
 lab=canonical_lab(lab);root=Path(__file__).resolve().parent;work=lab/'graphics-next-work'
 env=clean_environment(lab);env.update(SMX_TEST_LAB=str(lab),SMX_OFFLINE_SCRATCH=str(work/'OFFLINE_TEST_ONLY'))
 if gpu_source_manifest:env['SMX_GPU_SOURCE_MANIFEST']=str(Path(gpu_source_manifest).resolve())
 argv=[sys.executable,str(root/'offline/test_prospective.py')]
 result=subprocess.run(argv,env=env,capture_output=True,text=True,timeout=30)
 receipt=dict(status='PASS' if result.returncode==0 else 'FAIL',command=argv,exit=result.returncode,stdout=result.stdout,stderr=result.stderr,source_files={str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file()},runtime='NOT_RUN',new_reservations=0,new_native_captures=0,actual_GL_observability='NOT_TESTED',gpu_source_manifest=str(gpu_source_manifest) if gpu_source_manifest else None,tests='48: original32 plus prospective16',known_corrected_test_failures=['OOM quota synthetic root paint lacked color before patched fake input','G2 quota precreated raw files violated native freshness gate before corrected fake input'])
 durable(work/'offline-validation.json',receipt)
 return result.returncode
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--lab',required=True);p.add_argument('--gpu-source-manifest');a=p.parse_args();raise SystemExit(validate(a.lab,a.gpu_source_manifest))
