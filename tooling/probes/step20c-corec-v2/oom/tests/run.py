#!/usr/bin/env python3
"""Bounded H1 extension only. No compositor, runtime budget or new campaign."""
import argparse,json,os,pathlib,resource,shlex,subprocess,sys
P=pathlib.Path
H=P(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--sources',type=P,required=True);ap.add_argument('--output',type=P,required=True);a=ap.parse_args()
o=a.output.absolute()
assert str(o).startswith('/var/tmp/') and o.resolve()==o and not o.exists()
o.mkdir(mode=0o700);resource.setrlimit(resource.RLIMIT_CORE,(0,0));records=[]
def call(argv,label,env=None,negative=False):
 r=subprocess.run(list(map(str,argv)),capture_output=True,env=env)
 (o/(label+'.stdout')).write_bytes(r.stdout);(o/(label+'.stderr')).write_bytes(r.stderr)
 passed=r.returncode!=0 if negative else r.returncode==0
 records.append(dict(label=label,argv=list(map(str,argv)),rc=r.returncode,expected='nonzero runtime assertion/sanitizer' if negative else 0,passed=passed))
 (o/'commands.json').write_text(json.dumps(records,indent=2)+'\n');return passed
assert call([sys.executable,H/'extract.py','--sources',a.sources,'--output',o],'extract')
cflags=shlex.split(subprocess.check_output(['pkg-config','--cflags','wayland-server','pixman-1','wlroots-0.20'],text=True))
libs=shlex.split(subprocess.check_output(['pkg-config','--libs','wayland-server','pixman-1','wlroots-0.20'],text=True))
base=['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-unused-function','-g','-O1','-fno-omit-frame-pointer','-I'+str(a.sources/'scene/include'),'-I'+str(o),'-I'+str(H),*cflags,str(H/'oom.c'),*libs,'-lm']
cases=['root','nested','unarmed','wrongrole','malformed','nonce','mode','symlink','invalidenv']
def env_for(label,case):
 return dict(os.environ,SMX_OOM_TOKEN_PATH=str(o/(label+'.token')),SMX_OOM_NONCE='bad' if case=='invalidenv' else '123456789abcdef0123456789abcdef0',SMX_OOM_ROLE='nested_popup' if case=='nested' else 'root_popup',ASAN_OPTIONS='detect_leaks=1:abort_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
ok=call(['cc','-std=c17','-Wall','-Wextra','-Werror','-fsyntax-only','-I'+str(a.sources/'scene/include'),*cflags,str(o/'callsite.c')],'native-header-callsite-syntax')
for name,flags in [('normal',[]),('ubsan',['-fsanitize=undefined','-fno-sanitize-recover=all']),('asan-ubsan',['-fsanitize=address,undefined','-fno-sanitize-recover=all'])]:
 binary=o/name
 if not call(base+flags+['-o',str(binary)],name+'-compile'):ok=False;break
 for case in cases:
  label=name+'-'+case;ok=call([binary,case],label,env_for(label,case)) and ok
original=(o/'scene.inc').read_text()
mutants={
 'global_scope':('oom_diag.scoped && oom_diag.configured && !oom_diag.consumed &&\n\t\t\t!strcmp(oom_diag.call_role, oom_diag.role) && oom_diag_token()', 'oom_diag.configured && !oom_diag.consumed && oom_diag_token()'),
 'after_publication':('struct scene_tree_clip *entry = oom_diag_reserve(parent, tree, sizeof(*entry));','scene_tree_init(tree, parent);\nstruct scene_tree_clip *entry = oom_diag_reserve(parent, tree, sizeof(*entry));'),
 'wrong_role':('!strcmp(oom_diag.call_role, oom_diag.role) && oom_diag_token()','oom_diag_token()'),
 'token_reuse':('&& !oom_diag.consumed &&','&&'),
 'malformed_accepted':('return valid && got == length && !memcmp(token, expected, (size_t)length);','return true;'),
 'nonce_ignored':('!memcmp(token, expected, (size_t)length)','!memcmp(token + 41, expected + 41, (size_t)length - 41)'),
}
for name,(old,new) in mutants.items():
 assert original.count(old)==1,(name,original.count(old))
 changed=original.replace(old,new)
 if name=='after_publication':
  marker='scene_tree_init(tree, parent);'
  i=changed.index(marker,changed.index(marker)+len(marker))
  changed=changed[:i]+changed[i:].replace(marker,'/* moved, not duplicated */',1)
 (o/'scene.inc').write_text(changed)
 binary=o/('mutant-'+name)
 if not call(base+['-Wno-unused-variable','-o',str(binary)],name+'-compile'):ok=False;continue
 case={'wrong_role':'wrongrole','malformed_accepted':'malformed','nonce_ignored':'nonce'}.get(name,'root')
 label='mutant-'+name;ok=call([binary,case],label,env_for(label,case),negative=True) and ok
(o/'scene.inc').write_text(original)
result=dict(status='PASS_BOUNDED' if ok else 'FAIL',campaign='existing H1 source-corpus extension; no native runtime reservation',cases=cases,mutants=list(mutants),records=records,limits=['native compositor survival NOT_RUN','popup C callsite source binding only; no complete Sway build','damage/render use inherited reduced adapters; complete damage NOT_PROVEN'],core_limit=resource.getrlimit(resource.RLIMIT_CORE),dumpability='PR_SET_DUMPABLE0 and PR_GET_DUMPABLE0 asserted in each executable before test assertions')
(o/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status']);sys.exit(0 if ok else 1)
