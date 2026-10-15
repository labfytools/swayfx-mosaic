#!/usr/bin/env python3
"""Ten executable wrong variants. Compile failure is not a killed mutant."""
import argparse,json,os,pathlib,resource,shlex,subprocess,sys
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
H=pathlib.Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument("--sources",type=pathlib.Path,required=True);ap.add_argument("--output",type=pathlib.Path,required=True);a=ap.parse_args();out=a.output.absolute()
if out.exists() or not out.is_relative_to(pathlib.Path("/var/tmp")) or out.resolve()!=out:raise ValueError("Absent private /var/tmp output required")
out.mkdir(mode=0o700)
for key,sub in [("TMPDIR","scratch"),("TMP","scratch"),("TEMP","scratch"),("XDG_CACHE_HOME","cache"),("CCACHE_DIR","cache/ccache"),("PYTHONPYCACHEPREFIX","pycache"),("XDG_DATA_HOME","data")]:
    path=out/sub;path.mkdir(parents=True,exist_ok=True,mode=0o700);os.environ[key]=str(path)
subprocess.run([sys.executable,"-B",str(H.parent/"verify.py"),str(a.sources)],check=True,stdout=subprocess.DEVNULL)
base=out/"baseline";subprocess.run([sys.executable,"-B",str(H/"extract.py"),"--sources",str(a.sources),"--output",str(base)],check=True)
def replacement(text,old,new):
    assert text.count(old)==1,(old,text.count(old));return text.replace(old,new,1)
def before_alloc(text):
    text=replacement(text,"struct scene_tree_clip *entry = calloc(1, sizeof(*entry));","scene_tree_init(tree, parent);\n\tstruct scene_tree_clip *entry = calloc(1, sizeof(*entry));")
    return replacement(text,"\tscene_tree_init(tree, parent);\n\tentry->tree = tree;","\tentry->tree = tree;")
def unsafe_box(text):
    start=text.index("static bool probe_clip_box_intersection(");end=text.index("\n}",start)+2
    return text[:start]+"""static bool probe_clip_box_intersection(struct wlr_box *dest,const struct wlr_box *a,const struct wlr_box *b) {
    int x1=a->x>b->x?a->x:b->x,y1=a->y>b->y?a->y:b->y;
    int x2=a->x+a->width<b->x+b->width?a->x+a->width:b->x+b->width;
    int y2=a->y+a->height<b->y+b->height?a->y+a->height:b->y+b->height;
    *dest=(struct wlr_box){x1,y1,x2-x1,y2-y1};return dest->width>0&&dest->height>0;
}"""+text[end:]
def caller_null(text):
    start=text.index("\tif (relative == NULL) {");end=text.index("\n\t}\n",start)+4
    return text[:start]+text[end:]
mutants=[
("publish_before_reserve","scene.inc",before_alloc,[],0),
("setter_allocates","scene.inc",lambda t:replacement(t,"\tentry->active = clip != NULL;","\tvoid *extra = calloc(1, 1); free(extra);\n\tentry->active = clip != NULL;"),[],0),
("inactive_visible","scene.inc",lambda t:replacement(t,"return entry && entry->active ? entry : NULL;","return entry;"),[],0),
("null_frees_reservation","scene.inc",lambda t:replacement(t,"\tif (!clip && !entry->active) return;","\tif (!clip) {scene_tree_clip_remove(entry); return;}"),[],0),
("root_accepted","scene.inc",lambda t:replacement(t,"\t\tabort();","\t\treturn;"),["root"],-6),
("caller_null_dereference","ime.inc",caller_null,[],0),
("zero_allows_hit","scene.inc",lambda t:replacement(t,"\t\tstruct wlr_box clip;","\t\tif (entry->box.width == 0 || entry->box.height == 0) continue;\n\t\tstruct wlr_box clip;"),[],0),
("doublefree_listener","scene.inc",lambda t:replacement(t,"\tscene_tree_clip_remove(clip);","\tscene_tree_clip_remove(clip);\n\tscene_tree_clip_remove(clip);"),[],0),
("unsafe_intersection","geometry.inc",unsafe_box,[],0),
("unchecked_float_conversion","geometry.inc",lambda t:replacement(t,"\tif (!isfinite(scroll) || scroll < 0) return 0;","\tvolatile int unchecked = (int)scroll; (void)unchecked;\n\tif (!isfinite(scroll) || scroll < 0) return 0;"),[],0),
]
cflags=shlex.split(subprocess.check_output(["pkg-config","--cflags","wayland-server","pixman-1","wlroots-0.20"],text=True));libs=shlex.split(subprocess.check_output(["pkg-config","--libs","wayland-server","pixman-1","wlroots-0.20"],text=True));results=[]
for name,file,change,argv,correct_rc in mutants:
    d=out/name;d.mkdir(mode=0o700)
    for inc in base.glob("*.inc"):(d/inc.name).write_bytes(inc.read_bytes())
    p=d/file;p.write_text(change(p.read_text()));binary=d/"test"
    cmd=["cc","-std=c17","-Wall","-Wextra","-Werror","-Wno-unused-parameter","-g","-O1","-fno-omit-frame-pointer","-fsanitize=address,undefined,float-cast-overflow,signed-integer-overflow,bounds","-fno-sanitize-recover=all","-I"+str(a.sources/"scene/include"),"-I"+str(d),"-I"+str(H),*cflags,str(H/"core.c"),*libs,"-lm","-o",str(binary)]
    cp=subprocess.run(cmd,capture_output=True);(d/"compile.stdout").write_bytes(cp.stdout);(d/"compile.stderr").write_bytes(cp.stderr)
    result=dict(name=name,compile_argv=cmd,compile_rc=cp.returncode,mutant_exercised=False,killed=False,correct_rc=correct_rc)
    if cp.returncode==0:
        env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:abort_on_error=1",UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1")
        cp=subprocess.run([str(binary),*argv],capture_output=True,env=env);(d/"run.stdout").write_bytes(cp.stdout);(d/"run.stderr").write_bytes(cp.stderr)
        result.update(run_argv=[str(binary),*argv],run_rc=cp.returncode,mutant_exercised=True,killed=cp.returncode!=correct_rc)
    results.append(result)
result=dict(status="PASS" if all(r["killed"] for r in results) else "FAIL",variants=results,scope="Mutated generated exact-body slices; wrong variants intentionally violate bound source; no native compositor survival claim")
(out/"mutations.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps({"status":result["status"],"variants":[{k:r.get(k) for k in ["name","compile_rc","run_rc","killed"]}for r in results]},indent=2));sys.exit(result["status"]!="PASS")
