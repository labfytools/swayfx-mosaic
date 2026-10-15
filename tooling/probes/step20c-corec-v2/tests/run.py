#!/usr/bin/env python3
"""One serial bounded C campaign. Generated output is private /var/tmp only."""
import argparse,json,os,pathlib,resource,shlex,subprocess,sys
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
H=pathlib.Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument("--sources",type=pathlib.Path,required=True);ap.add_argument("--output",type=pathlib.Path,required=True);args=ap.parse_args()
out=args.output.absolute()
if not out.is_relative_to(pathlib.Path("/var/tmp")) or out.exists() or out.resolve()!=out:raise ValueError("Absent explicit /var/tmp output without symlink required")
out.mkdir(mode=0o700)
for key,sub in [("TMPDIR","scratch"),("TMP","scratch"),("TEMP","scratch"),("XDG_CACHE_HOME","cache"),("CCACHE_DIR","cache/ccache"),("PYTHONPYCACHEPREFIX","pycache"),("XDG_DATA_HOME","data")]:
    path=out/sub;path.mkdir(parents=True,exist_ok=True,mode=0o700);os.environ[key]=str(path)
records=[]
def call(argv,label,expected=0,env=None):
    cp=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
    (out/(label+".stdout")).write_bytes(cp.stdout);(out/(label+".stderr")).write_bytes(cp.stderr)
    records.append(dict(label=label,argv=argv,rc=cp.returncode,expected=expected,pass_expected=cp.returncode==expected))
    (out/"commands.json").write_text(json.dumps(records,indent=2)+"\n")
    return cp.returncode==expected
if not call([sys.executable,"-B",str(H.parent/"verify.py"),str(args.sources)],"verify-source"):sys.exit(1)
if not call([sys.executable,"-B",str(H/"extract.py"),"--sources",str(args.sources),"--output",str(out)],"extract"):sys.exit(1)
cflags=shlex.split(subprocess.check_output(["pkg-config","--cflags","wayland-server","pixman-1","wlroots-0.20"],text=True))
libs=shlex.split(subprocess.check_output(["pkg-config","--libs","wayland-server","pixman-1","wlroots-0.20"],text=True))
base=["cc","-std=c17","-Wall","-Wextra","-Werror","-Wno-unused-parameter","-g","-O1","-fno-omit-frame-pointer","-I"+str(args.sources/"scene/include"),"-I"+str(out),"-I"+str(H),*cflags,str(H/"core.c"),*libs,"-lm"]
status=True
for name,flags in [("normal",[]),("ubsan",["-fsanitize=undefined,float-cast-overflow,signed-integer-overflow,bounds","-fno-sanitize-recover=all"]),("asan-ubsan",["-fsanitize=address,undefined,float-cast-overflow,signed-integer-overflow,bounds","-fno-sanitize-recover=all"])]:
    binary=str(out/name)
    if not call(base+flags+["-o",binary],name+"-compile"):status=False;break
    env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:abort_on_error=1",UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1")
    status=call([binary],name+"-run",env=env) and status
    status=call([binary,"second"],name+"-second-reservation",env=env) and status
    status=call([binary,"root"],name+"-root-rejection",expected=-6,env=env) and status
result=dict(core_dump_limit=resource.getrlimit(resource.RLIMIT_CORE),status="PASS_BOUNDED" if status else "FAIL",scope="exact factory/init/destroy/reparent/coords/set/get/clip and numeric guards with native structs/signals/Pixman; rendering/damage adapters only",limitations=["IME exact refocus body exercised with reduced Sway/protocol adapters","popup current ancestor fullscreen/actual hidden-owner/standard clips exercised with reduced Sway structs; full fading/transaction engine NOT RUN","Mutation gate is separate: tests/mutations.py; independent review required","No native compositor OOM survival"],records=records)
(out/"result.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2));sys.exit(0 if status else 1)
