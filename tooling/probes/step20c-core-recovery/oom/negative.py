"""Adversarial mutations of the exact extracted bodies, never historical inputs."""
import pathlib,subprocess,shutil,json,resource,argparse
p=argparse.ArgumentParser();p.add_argument('lab',type=pathlib.Path);L=p.parse_args().lab.resolve();N=L/'negative';N.mkdir(exist_ok=True);records=[]
pkg=subprocess.check_output(['pkg-config','--cflags','--libs','wayland-server','pixman-1'],text=True).split()
mutants=[('B','popup.inc','desired && admitted','desired',''),('A','setter.inc','abort();','return;','1'),('B','setter.inc','wlr_scene_node_set_enabled(&tree->node, false);','/* mutant: false without admission mask */','1'),('B','setter.inc','\treturn true;\n}\n\nbool wlr_scene_tree_get_clip','\twlr_scene_node_set_enabled(&tree->node, true);\n\treturn true;\n}\n\nbool wlr_scene_tree_get_clip','1'),('C','create.inc','struct scene_tree_clip *entry = calloc(1, sizeof(*entry));','scene_tree_init(tree, parent);\n\tstruct scene_tree_clip *entry = calloc(1, sizeof(*entry));','2'),('C','setter.inc','entry->active = clip != NULL;','entry->active = false;','')]
for i,(mode,file,old,new,arg) in enumerate(mutants):
 d=N/str(i);shutil.copytree(L/mode,d,ignore=shutil.ignore_patterns('A-*','B-*','C-*'),dirs_exist_ok=True)
 f=d/file;s=f.read_text();assert old in s;f.write_text(s.replace(old,new,1));args=['cc','-std=c17','-O1','-DMODE_'+mode,'harness-scene.c','options.c',*pkg,'-o',str(d/'mutant')]
 c=subprocess.run(args,cwd=d,capture_output=True);assert c.returncode==0,c.stderr
 def limit():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 argv=[str(d/'mutant')]+([arg] if arg else []);r=subprocess.run(argv,cwd=d,capture_output=True,preexec_fn=limit)
 (d/'stdout').write_bytes(r.stdout);(d/'stderr').write_bytes(r.stderr)
 # A must return 99 rather than expected SIGABRT; others must trip assertions.
 rejected=r.returncode==99 if mode=='A' else r.returncode==-6
 records.append(dict(mode=mode,file=file,mutation=old+' => '+new,argv=argv,returncode=r.returncode,rejected=rejected))
(N/'results.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records,indent=2));raise SystemExit(not all(r['rejected'] for r in records))
