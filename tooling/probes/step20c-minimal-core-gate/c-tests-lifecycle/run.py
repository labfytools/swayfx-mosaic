import pathlib, subprocess, json, os, resource, hashlib
R=pathlib.Path(__file__).resolve().parent
records=[]
def run(name,args,env=None):
 def limit():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 p=subprocess.run(args,cwd=R,capture_output=True,env=env,preexec_fn=limit)
 (R/(name+'.stdout')).write_bytes(p.stdout);(R/(name+'.stderr')).write_bytes(p.stderr)
 records.append(dict(name=name,argv=args,returncode=p.returncode,core_limit=0,environment_overrides={} if env is None else {k:v for k,v in env.items() if k in ('ASAN_OPTIONS','UBSAN_OPTIONS')}))
 return p.returncode
assert run('extract',['python3','extract.py'])==0
run('compiler-version',['cc','--version'])
assert run('pkg-config',['pkg-config','--cflags','--libs','wayland-server','pixman-1'])==0
pkg=(R/'pkg-config.stdout').read_text().split()
assert run('library-versions',['pkg-config','--modversion','wayland-server','pixman-1'])==0
assert run('compile-pixman-diagnostic',['cc','-std=c17','pixman-diagnostic.c',*pkg,'-o','pixman-diagnostic'])==0
assert run('pixman-diagnostic',['./pixman-diagnostic'])==0
for variant,flags in [('normal',[]),('ubsan',['-fsanitize=undefined','-fno-sanitize-recover=all']),('asan',['-fsanitize=address'])]:
 args=['cc','-std=c17','-g','-O1','-Wall','-Wextra','-Wno-unused-function','-Wno-unused-parameter','-fno-omit-frame-pointer',*flags,'scene.c','lifecycle.c',*pkg,'-o','lifecycle-'+variant]
 rc=run('compile-'+variant,args)
 if rc==0:
  env=os.environ.copy();env.update(ASAN_OPTIONS='detect_leaks=1:abort_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
  run(variant+'-defined',['./lifecycle-'+variant],env)
  run(variant+'-allocation-unavailable',['./lifecycle-'+variant,'--allocation-unavailable'],env)
(R/'commands.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ("name","returncode")} for r in records],indent=2))
failed=[r for r in records if r["returncode"] != (-6 if r["name"].endswith("-allocation-unavailable") else 0)]
raise SystemExit(bool(failed))
