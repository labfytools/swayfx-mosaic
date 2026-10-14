import pathlib,subprocess,json,os,resource,shutil,argparse,hashlib,re
from prepare import prepare
P=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('lab',type=pathlib.Path);L=prepare(p.parse_args().lab.resolve());records=[]
def run(name,args,cwd,expected=0):
 def limit():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 env=os.environ.copy();env.update(ASAN_OPTIONS='detect_leaks=1:abort_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
 r=subprocess.run(args,cwd=cwd,env=env,capture_output=True,preexec_fn=limit)
 (L/(name+'.stdout')).write_bytes(r.stdout);(L/(name+'.stderr')).write_bytes(r.stderr)
 records.append(dict(name=name,argv=args,cwd=str(cwd),returncode=r.returncode,expected=expected,core_limit=0,pass_expected=r.returncode==expected))
 (L/'commands.json').write_text(json.dumps(records,indent=2)+'\n')
 return r.returncode==expected
pkg=subprocess.check_output(['pkg-config','--cflags','--libs','wayland-server','pixman-1'],text=True).split()
for mode in 'ABC':
 d=L/mode
 for f in ('support.h','scene.c','options.c','lifecycle.c'):
  # Full prototype sources retain distinct filenames; harness scene is separate.
  shutil.copyfile(P/f,d/('harness-scene.c' if f=='scene.c' else f))
 if mode=='C':
  f=d/'lifecycle.c';text=f.read_text();text=re.sub(r'(init_node\(&([a-z_]+)\.node,WLR_SCENE_NODE_TREE,[^;]+;)',r'\1reserve_fixture(&\2);',text);f.write_text(text)
 for variant,flags in [('normal',[]),('ubsan',['-fsanitize=undefined','-fno-sanitize-recover=all']),('asan',['-fsanitize=address'])]:
  name=mode+'-'+variant;binary=str(d/name)
  ok=run(name+'-compile',['cc','-std=c17','-g','-O1','-Wall','-Wextra','-Wno-unused-function','-Wno-unused-parameter','-fno-omit-frame-pointer','-DMODE_'+mode,*flags,'harness-scene.c','options.c',*pkg,'-o',binary],d)
  if ok:
   run(name+'-defined',[binary],d)
   for nth in (1,2):run(name+'-oom'+str(nth),[binary,str(nth)],d,-6 if mode=='A' else 0)
for mode in ('A','C'):
 d=L/mode;shutil.copyfile(P/'memory.c',d/'memory.c')
 flags=subprocess.check_output(['pkg-config','--cflags','wlroots-0.20','wayland-server'],text=True).split()
 binary=str(d/'memory')
 if run(mode+'-memory-compile',['cc','-std=c17',*flags,'memory.c','-o',binary],d):run(mode+'-memory',[binary],d)
(L/'source-fixtures.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in P.iterdir() if f.is_file()},indent=2)+'\n')
print(json.dumps(records,indent=2));raise SystemExit(not all(r['pass_expected'] for r in records))
