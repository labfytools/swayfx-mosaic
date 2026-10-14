"""Private full-file prototypes followed by exact byte extraction; no build of a compositor."""
import argparse, pathlib, hashlib, json, difflib, shutil
P=pathlib.Path(__file__).resolve().parent
H=pathlib.Path('/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_')
def sha(b): return hashlib.sha256(b).hexdigest()
def replace(s,a,b):
    assert a in s,a
    return s.replace(a,b)
def prepare(lab):
    lab.mkdir(parents=True,exist_ok=True); bindings=[]; sources=[]
    original=(H/'scene-core/types/scene/wlr_scene.c').read_text()
    txn=(H/'mosaic-fixed/sway/desktop/transaction.c').read_text()
    assert sha(original.encode())=='99992429f9a1d2754042989d89904fb6d705f963d74f4456d737fc9da3e0927d'
    assert sha(txn.encode())=='0b1d31bb8458dceaff34cc2a2987044b3096e6ebc96e68b522c0ac3540bc8ecd'
    for mode in 'ABC':
        d=lab/mode;d.mkdir(exist_ok=True);s=original;t=txn
        if mode=='B':
            s=replace(s,'void wlr_scene_tree_set_clip(', 'bool wlr_scene_tree_set_clip(')
            s=replace(s,'if (!clip && !entry) return;', 'if (!clip && !entry) return true;')
            s=replace(s,'sizeof(*clip)) == 0) return;', 'sizeof(*clip)) == 0) return true;')
            s=replace(s,'\t\t\tabort();', '''\t\t\t// WHY: a mandatory clip must not fail open even if callers ignore false.
\t\t\t// CONTRACT: mask synchronously; caller owns future visibility admission.
\t\t\t// INVARIANT: never automatically re-enable an intentionally hidden tree.
\t\t\twlr_scene_node_set_enabled(&tree->node, false);
\t\t\treturn false;''')
            s=replace(s,'scene_node_update(&tree->node, NULL);\n}\n\nbool wlr_scene_tree_get_clip', 'scene_node_update(&tree->node, NULL);\n\treturn true;\n}\n\nbool wlr_scene_tree_get_clip')
            import re
            t=re.sub(r'(?m)^(\s*)wlr_scene_tree_set_clip\(([^;]+)\);',r'\1if (!wlr_scene_tree_set_clip(\2)) return;',t)
            # Admission has no heap state: current Mosaic plus applied clip is the gate.
            helper="""// WHY: fading-out also enables tiling without retrying clip installation.
// CONTRACT: upstream decides desired visibility; absent mandatory clip vetoes it.
// INVARIANT: false desired never becomes true; no OOM latch allocation is needed.
static void probe_clip_enable_tiling(struct sway_workspace *ws, bool desired) {
	struct wlr_box clip;
	bool admitted = ws->current.layout != L_MOSAIC || !ws->mosaic ||
		wlr_scene_tree_get_clip(ws->layers.tiling, &clip);
	wlr_scene_node_set_enabled(&ws->layers.tiling->node, desired && admitted);
}

"""
            # Declaration precedes arrange_output; implementation precedes popup helpers.
            t=t.replace('// WHY: int endpoint subtraction',helper+'// WHY: int endpoint subtraction',1)
            pos=t.index('static void arrange_output(')
            t=t[:pos]+'static void probe_clip_enable_tiling(struct sway_workspace *ws, bool desired);\n\n'+t[pos:]
            t=t.replace('wlr_scene_node_set_enabled(&child->layers.tiling->node, !fs);','probe_clip_enable_tiling(child, !fs);')
            t=t.replace('wlr_scene_node_set_enabled(&child->layers.tiling->node, true);','probe_clip_enable_tiling(child, true);')
            t=t.replace('wlr_scene_node_set_enabled(&child->layers.tiling->node, false);','probe_clip_enable_tiling(child, false);')
            t=t.replace('\n\t\t\t\tarrange_workspace_tiling(child,','\n\t\t\t\tprobe_clip_enable_tiling(child, true);\n\t\t\t\tarrange_workspace_tiling(child,',1)

        if mode=='C':
            s=replace(s,'struct wlr_box box;\n\tstruct wl_listener destroy;', 'struct wlr_box box;\n\tbool active; // Private sidecar only: no installed tree/node ABI change.\n\tstruct wl_listener destroy;')
            s=replace(s,'static struct scene_tree_clip *scene_tree_clip_find(', 'static struct scene_tree_clip *scene_tree_clip_storage(')
            marker='static void scene_tree_clip_remove('
            i=s.index(marker)
            s=s[:i]+'''// WHY: reservation must survive clip removal to make later admission allocation-free.
// CONTRACT: inactive reservations are absent to render/hit/get callers.
// INVARIANT: lookup never exposes an uninitialized clip rectangle.
static struct scene_tree_clip *scene_tree_clip_find(struct wlr_scene_tree *tree) {
\tstruct scene_tree_clip *entry = scene_tree_clip_storage(tree);
\treturn entry && entry->active ? entry : NULL;
}

'''+s[i:]
            s=replace(s,'\tscene_tree_init(tree, parent);\n\treturn tree;', '''\t// WHY: failure must occur before tree publication to parent scene children.
\t// CONTRACT: both tree and reservation are acquired before scene_tree_init.
\t// INVARIANT: failed reservation frees unpublished tree, no listener attached.
\tstruct scene_tree_clip *entry = calloc(1, sizeof(*entry));
\tif (!entry) { free(tree); return NULL; }
\tscene_tree_init(tree, parent);
\tentry->tree = tree;
\tentry->destroy.notify = scene_tree_clip_destroy;
\twl_signal_add(&tree->node.events.destroy, &entry->destroy);
\tentry->next = scene_tree_clips;
\tscene_tree_clips = entry;
\treturn tree;''')
            a=s.index('void wlr_scene_tree_set_clip(');b=s.index('bool wlr_scene_tree_get_clip(',a)
            s=s[:a]+'''void wlr_scene_tree_set_clip(struct wlr_scene_tree *tree, const struct wlr_box *clip) {
\t// WHY: no heap allocation may occur when exposing an existing tree.
\t// CONTRACT: trees must come from the private reservation-aware create path.
\t// INVARIANT: NULL deactivates but never releases the reservation.
\tassert(tree && (!clip || (clip->width >= 0 && clip->height >= 0)));
\tstruct scene_tree_clip *entry = scene_tree_clip_storage(tree);
\tassert(entry);
\tif (!clip && !entry->active) return;
\tif (clip && entry->active && memcmp(&entry->box, clip, sizeof(*clip)) == 0) return;
\tentry->active = clip != NULL;
\tif (clip) entry->box = *clip;
\tscene_node_update(&tree->node, NULL);
}

'''+s[b:]
        header=(H/'scene-core/include/scenefx/types/wlr_scene.h').read_text()
        private_header=header.replace('void wlr_scene_tree_set_clip(', 'bool wlr_scene_tree_set_clip(') if mode=='B' else header
        for name,parent,body in [('scene.c',original,s),('transaction.c',txn,t),('scene.h',header,private_header)]:
            (d/name).write_text(body)
            patch=''.join(difflib.unified_diff(parent.splitlines(True),body.splitlines(True),fromfile='a/'+name,tofile='b/'+name,n=0))
            (lab/(mode+'-'+name+'.patch')).write_text(patch)
            sources.append(dict(mode=mode,file=name,parent_sha256=sha(parent.encode()),prototype_sha256=sha(body.encode()),patch_sha256=sha(patch.encode())))
        ranges=[('scene.c','struct scene_tree_clip {','static struct scene_tree_clip *scene_tree_clips;','size-struct.inc'),('scene.c','void wlr_scene_node_set_enabled(','void wlr_scene_node_set_position(','enabled.inc'),('scene.c','struct scene_tree_clip {','struct wlr_scene_rect *wlr_scene_rect_from_node','sidecar.inc'),('scene.c','static bool scene_clip_translate(','static bool scene_node_update_iterator(','clip.inc'),('scene.c',('bool' if mode=='B' else 'void')+' wlr_scene_tree_set_clip(','struct wlr_scene_rect *wlr_scene_rect_create(','setter.inc'),('scene.c','struct node_at_data {','struct wlr_scene_node *wlr_scene_node_at(','hit.inc'),('scene.c','struct wlr_scene_tree *wlr_scene_tree_create(','typedef bool (*scene_node_box_iterator_func_t)','create.inc'),('transaction.c','static void probe_clip_enable_tiling(struct sway_workspace *ws, bool desired) {' if mode=='B' else 'static bool probe_clip_box_intersection(','void arrange_popups(','popup.inc')]
        if mode=='B': ranges.append(('transaction.c','\n\t\t\tprobe_clip_enable_tiling(child, true);','\n\t\t\twlr_scene_node_set_enabled(&child->layers.fullscreen->node, false);','fading.inc'))
        for source,start,end,out in ranges:
            data=(d/source).read_bytes();a=data.index(start.encode());b=data.index(end.encode(),a);piece=data[a:b];(d/out).write_bytes(piece)
            bindings.append(dict(mode=mode,source=str(d/source),source_sha256=sha(data),start_byte=a,end_byte_exclusive=b,start_line=data[:a].count(b'\n')+1,slice_sha256=sha(piece),output=out))
    (lab/'bindings.json').write_text(json.dumps(bindings,indent=2)+'\n');(lab/'sources.json').write_text(json.dumps(sources,indent=2)+'\n')
    return lab
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('lab',type=pathlib.Path);prepare(p.parse_args().lab)
