import pathlib, hashlib, json
ROOT=pathlib.Path(__file__).resolve().parent
LAB=ROOT.parent
bindings=[]
def extract(path,start,end,name):
    data=path.read_bytes(); a=data.index(start.encode()); b=data.index(end.encode(),a)
    piece=data[a:b]; (ROOT/name).write_bytes(piece)
    bindings.append(dict(source=str(path),source_sha256=hashlib.sha256(data).hexdigest(),start_byte=a,end_byte_exclusive=b,start_line=data[:a].count(b'\n')+1,end_line=data[:b].count(b'\n')+1,slice_sha256=hashlib.sha256(piece).hexdigest(),output=name))
s=LAB/'scene-core/types/scene/wlr_scene.c'
extract(s,'struct scene_tree_clip {','struct wlr_scene_rect *wlr_scene_rect_from_node', 'sidecar.inc')
extract(s,'static bool scene_clip_translate(', 'static bool scene_node_update_iterator(', 'clip.inc')
extract(s,'void wlr_scene_tree_set_clip(', 'struct wlr_scene_rect *wlr_scene_rect_create(', 'setter.inc')
extract(s,'struct node_at_data {','struct wlr_scene_node *wlr_scene_node_at(', 'hit.inc')
t=LAB/'mosaic-fixed/sway/desktop/transaction.c'
extract(t,'static bool probe_clip_box_intersection(', 'void arrange_popups(', 'popup.inc')
(ROOT/'bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
