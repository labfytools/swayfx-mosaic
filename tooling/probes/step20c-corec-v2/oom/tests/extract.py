#!/usr/bin/env python3
"""Extract exact full C bodies and bind offsets/full-file SHA/slice SHA."""
import argparse, hashlib, json, pathlib, re
ap=argparse.ArgumentParser();ap.add_argument("--sources",type=pathlib.Path,required=True);ap.add_argument("--output",type=pathlib.Path,required=True);args=ap.parse_args()
if not args.output.absolute().is_relative_to(pathlib.Path("/var/tmp")) or args.output.absolute().resolve()!=args.output.absolute():
    raise ValueError("Explicit private /var/tmp output required")
args.output.mkdir(parents=True,exist_ok=True)
bindings=[]
def extract(component,relative,name):
    path=args.sources/component/relative;raw=path.read_bytes()
    # Definitions have their opening brace before the next semicolon.
    found=[]
    for match in re.finditer(rb"^(?:static )?(?:struct [A-Za-z_0-9]+ \*|bool |void |int )"+name.encode()+rb"\(",raw,re.M):
        a=match.start();opening=raw.index(b"{",match.end());semi=raw.find(b";",match.end())
        if semi>=0 and semi<opening:continue
        found.append((a,opening))
    assert len(found)==1,(name,found)
    a,opening=found[0];end=opening+1;depth=1
    while depth:
        if raw[end:end+1]==b"{":depth+=1
        elif raw[end:end+1]==b"}":depth-=1
        end+=1
    piece=raw[a:end]
    bindings.append(dict(component=component,path=relative,symbol=name,fullfile_sha256=hashlib.sha256(raw).hexdigest(),start_byte=a,end_byte_exclusive=end,start_line=raw[:a].count(b"\n")+1,slice_sha256=hashlib.sha256(piece).hexdigest()))
    return piece
scene="types/scene/wlr_scene.c"
raw=(args.sources/"scene"/scene).read_bytes();a=raw.index(b"struct scene_tree_clip {");b=raw.index(b"struct wlr_scene_tree *wlr_scene_tree_from_node",a)
parts=[raw[a:b]];bindings.append(dict(component="scene",path=scene,symbol="sidecar definitions",fullfile_sha256=hashlib.sha256(raw).hexdigest(),start_byte=a,end_byte_exclusive=b,start_line=raw[:a].count(b"\n")+1,slice_sha256=hashlib.sha256(raw[a:b]).hexdigest()))
for name in ["wlr_scene_tree_from_node","wlr_scene_rect_from_node","wlr_scene_buffer_from_node","wlr_scene_blur_from_node","scene_node_get_root","scene_node_init","scene_tree_init","wlr_scene_tree_create","wlr_scene_node_coords","wlr_scene_node_set_enabled","wlr_scene_node_reparent","wlr_scene_node_destroy","scene_clip_translate","scene_node_intersect_clip","scene_node_point_inside_clip","wlr_scene_tree_set_clip","wlr_scene_tree_get_clip"]:
    if name == "wlr_scene_tree_create":
        diagnostic=(args.sources/"scene/types/scene/oom-diagnostic.inc").read_bytes()
        parts.append(diagnostic)
        bindings.append(dict(component="scene",path="types/scene/oom-diagnostic.inc",symbol="complete private diagnostic",fullfile_sha256=hashlib.sha256(diagnostic).hexdigest(),start_byte=0,end_byte_exclusive=len(diagnostic),slice_sha256=hashlib.sha256(diagnostic).hexdigest()))
    parts.append(extract("scene",scene,name))
a=raw.index(b"struct node_at_data {");b=raw.index(b"struct wlr_scene_node *wlr_scene_node_at",a)
parts.append(raw[a:b]);bindings.append(dict(component="scene",path=scene,symbol="native hit iterator and data",fullfile_sha256=hashlib.sha256(raw).hexdigest(),start_byte=a,end_byte_exclusive=b,start_line=raw[:a].count(b"\n")+1,slice_sha256=hashlib.sha256(raw[a:b]).hexdigest()))
(args.output/"scene.inc").write_bytes(b"\n\n".join(parts)+b"\n")
parts=[extract("mosaic","sway/desktop/transaction.c",name) for name in ["probe_clip_box_intersection","probe_camera_scroll"]]
(args.output/"geometry.inc").write_bytes(b"\n\n".join(parts)+b"\n")
(args.output/"ime.inc").write_bytes(extract("mosaic","sway/input/text_input.c","input_popup_set_focus")+b"\n")
parts=[extract("mosaic","sway/desktop/transaction.c",name) for name in ["probe_workspace_clip","workspace_tiling_scene_x","probe_clip_popup"]]
(args.output/"transaction.inc").write_bytes(b"\n\n".join(parts)+b"\n")
(args.output/"bindings.json").write_text(json.dumps(bindings,indent=2)+"\n")

raw=(args.sources/"mosaic/sway/desktop/xdg_shell.c").read_bytes()
a=raw.index(b"struct wlr_xdg_surface *xdg_parent =");b=raw.index(b"\n\tif (!popup->scene_tree)",a)
piece=raw[a:b]
bindings.append(dict(component="mosaic",path="sway/desktop/xdg_shell.c",symbol="exact primary popup diagnostic callsite",fullfile_sha256=hashlib.sha256(raw).hexdigest(),start_byte=a,end_byte_exclusive=b,slice_sha256=hashlib.sha256(piece).hexdigest()))
(args.output/"callsite.c").write_bytes(b"#define WLR_USE_UNSTABLE\n#include <scenefx/types/wlr_scene.h>\n#include <wlr/types/wlr_xdg_shell.h>\nstruct adapter_popup {struct wlr_scene_tree *scene_tree;};\nextern struct wlr_scene_tree *smx_oom_popup_tree_create(struct wlr_scene_tree *, const char *, const void *, const void *);\nvoid test_callsite(struct adapter_popup *popup, struct wlr_scene_tree *parent, struct wlr_xdg_popup *wlr_popup, struct wlr_xdg_surface *xdg_surface) {\n"+piece+b"\n}\n")
(args.output/"bindings.json").write_text(json.dumps(bindings,indent=2)+"\n")
