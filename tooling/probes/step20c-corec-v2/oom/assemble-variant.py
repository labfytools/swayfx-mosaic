#!/usr/bin/env python3
"""Apply private OOM deltas to exact reviewed CORE trees; no build/runtime."""
import argparse,hashlib,json,os,pathlib,shutil,subprocess
P=pathlib.Path;H=P(__file__).resolve().parent

def manifest(root):
 result={}
 for p in sorted(root.rglob('*')):
  if p.is_symlink():raise ValueError('symlink source')
  if p.is_file():result[str(p.relative_to(root))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':oct(p.stat().st_mode&0o777)}
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--core',type=P,required=True);ap.add_argument('--destination',type=P,required=True);a=ap.parse_args()
 d=a.destination.absolute();assert d.is_relative_to(P('/var/tmp')) and d!=P('/var/tmp') and d.resolve()==d and not d.exists()
 os.umask(0o077);d.mkdir(mode=0o700);p=json.loads((H/'provenance.json').read_text());receipt={}
 for c,e in p['components'].items():
  assert manifest(a.core/c)==e['parent_files'],c+' exact reviewed parent mismatch'
  patch=H/e['patch'];assert hashlib.sha256(patch.read_bytes()).hexdigest()==e['patch_sha256']
  dst=d/c;shutil.copytree(a.core/c,dst)
  env=dict(os.environ,GIT_CEILING_DIRECTORIES=str(d))
  subprocess.run(['git','apply','--check',str(patch)],cwd=dst,env=env,check=True)
  subprocess.run(['git','apply',str(patch)],cwd=dst,env=env,check=True)
  for r in e['changed_files']:(dst/r).chmod(int(e['files'][r]['mode'],8))
  assert manifest(dst)==e['files'],c+' variant mismatch'
  receipt[c]={'forward_apply':True,'manifest_sha256':hashlib.sha256(json.dumps(e['files'],sort_keys=True).encode()).hexdigest()}
 (d/'assembly-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
