"""Generate passive private deltas after the documented source audit.

WHY: dirty, regeneration return, cache copies and final use are separate facts.
CONTRACT: insert logs only, never change a render/scene/ownership decision.
INVARIANT: borrowed pointers are read synchronously; no retained GPU references.
"""
from pathlib import Path
import difflib

HEADER = r'''#ifndef OPT_PROBE_H
#define OPT_PROBE_H
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
/* WHY: correlate passive observations with the runner's CLOCK_MONOTONIC.
 * CONTRACT: no driver query/readback or retained object; opt-in logs only.
 * INVARIANT: native rendering and lifetime decisions are unchanged. */
static inline long long opt_probe_ns(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (long long)t.tv_sec * 1000000000LL + t.tv_nsec;
}
#define OPT_LOG(event, format, ...) do { if (getenv("OPT_TRACE")) \
    fprintf(stderr, event " ns=%lld " format "\n", opt_probe_ns(), __VA_ARGS__); } while (0)
#endif
'''

def instrument(scene: Path, mosaic: Path, fixture: Path):
    originals = {}
    def change(root, name, old, new):
        p=root/name
        originals.setdefault(p, p.read_text() if p.exists() else '')
        s=p.read_text()
        if s.count(old)!=1:raise RuntimeError(f'nonunique insertion {name}: {old[:60]} count={s.count(old)}')
        p.write_text(s.replace(old,new,1))
    header=scene/'include/render/opt_probe.h'; originals[header]='';header.write_text(HEADER)
    for name in ['types/scene/wlr_scene.c','render/fx_renderer/fx_pass.c','render/fx_renderer/fx_offscreen_buffers.c','render/fx_renderer/fx_framebuffer.c']:
        p=scene/name; originals[p]=p.read_text();p.write_text('#include "render/opt_probe.h"\n'+p.read_text())
    name='types/scene/wlr_scene.c'
    change(scene,name,'\tscene_blur->dirty = false;\n\n\tscene_node_update(&scene_blur->node, NULL);','\tscene_blur->dirty = false;\n\n\tscene_node_update(&scene_blur->node, NULL);\n\tOPT_LOG("OPT_NODE_CREATE", "node=%p parent=%p size=%dx%d dirty=0", (void *)scene_blur, (void *)parent, width, height);')
    change(scene,name,'\tblur_node->dirty = true;','\tOPT_LOG("OPT_DIRTY_SET", "node=%p enabled=%d before=%d size=%dx%d", (void *)blur_node, blur_node->node.enabled, blur_node->dirty, blur_node->width, blur_node->height);\n\tblur_node->dirty = true;')
    change(scene,name,'\t\t// Re-render the optimized blur buffer when needed.',r'''		OPT_LOG("OPT_NODE_RENDER", "output=%s node=%p enabled=%d dirty=%d has_blur=%d size=%dx%d visible=%d,%d,%d,%d draw=%d,%d,%d,%d radius=%.3f passes=%d",
            data->output->output->name, (void *)node, node->enabled, scene_blur->dirty, fx_pass->has_blur, scene_blur->width, scene_blur->height,
            node->visible.extents.x1, node->visible.extents.y1, node->visible.extents.x2, node->visible.extents.y2,
            render_region.extents.x1, render_region.extents.y1, render_region.extents.x2, render_region.extents.y2,
            scene->blur_data.radius, scene->blur_data.num_passes);
        // Re-render the optimized blur buffer when needed.'''.replace('\\t','\t'))
    change(scene,name,'\t\t\tbool result = fx_render_pass_add_optimized_blur(fx_pass, &blur_options);',r'''			OPT_LOG("OPT_REGEN_ATTEMPT", "output=%s node=%p dirty=%d", data->output->output->name, (void *)node, scene_blur->dirty);
            bool result = fx_render_pass_add_optimized_blur(fx_pass, &blur_options);
            OPT_LOG("OPT_REGEN_RESULT", "output=%s node=%p result=%d", data->output->output->name, (void *)node, result);'''.replace('\\t','\t'))
    change(scene,name,'\t\t\t\tscene_blur->dirty = false;','\t\t\t\tscene_blur->dirty = false;\n                OPT_LOG("OPT_DIRTY_CLEAR", "output=%s node=%p dirty=%d", data->output->output->name, (void *)node, scene_blur->dirty);')
    change(scene,name,'\t\tfx_render_pass_add_blur(fx_pass, &blur_options);',r'''		OPT_LOG("OPT_REGULAR_NODE", "output=%s node=%p parent=%p optimized=%d strength=%.3f enabled=%d global=%d,%d size=%dx%d draw=%d,%d,%d,%d mask=%p",
            data->output->output->name, (void *)node, (void *)node->parent, blur_options.use_optimized_blur, blur->strength, node->enabled,
            entry->x, entry->y, blur->width, blur->height,
            render_region.extents.x1, render_region.extents.y1, render_region.extents.x2, render_region.extents.y2, (void *)mask);
        fx_render_pass_add_blur(fx_pass, &blur_options);'''.replace('\\t','\t'))
    # Main-output buffer is the source at the optimized node, distinct from final output submission.
    change(scene,name,'\tint x = entry->x - data->logical.x;',r'''    if (node->type == WLR_SCENE_NODE_BUFFER) {
        struct wlr_scene_buffer *sb = wlr_scene_buffer_from_node(node);
        struct wlr_scene_surface *ss = wlr_scene_surface_try_from_buffer(sb);
        OPT_LOG("OPT_BUFFER_DRAW", "output=%s node=%p buffer=%p surface=%p global=%d,%d dest=%dx%d source=%dx%d draw=%d,%d,%d,%d",
            data->output->output->name, (void *)node, (void *)sb->buffer, ss ? (void *)ss->surface : NULL,
            entry->x, entry->y, sb->dst_width, sb->dst_height, sb->buffer ? sb->buffer->width : 0, sb->buffer ? sb->buffer->height : 0,
            render_region.extents.x1, render_region.extents.y1, render_region.extents.x2, render_region.extents.y2);
    }
    int x = entry->x - data->logical.x;''')
    change(scene,name,'\twlr_output_state_set_buffer(state, buffer);\n\twlr_buffer_unlock(buffer);',r'''    wlr_output_state_set_buffer(state, buffer);
    OPT_LOG("OPT_OUTPUT_BUFFER", "output=%s buffer=%p submitted=1 damage=%d,%d,%d,%d committed=%u",
        output->name, (void *)buffer, state->damage.extents.x1, state->damage.extents.y1, state->damage.extents.x2, state->damage.extents.y2, state->committed);
    wlr_buffer_unlock(buffer);''')
    name='render/fx_renderer/fx_pass.c'
    change(scene,name,'\t// Update the buffers if needed','\tstruct fx_framebuffer *opt_before = pass->fx_offscreen_buffers->optimized_blur_buffer;\n\t// Update the buffers if needed')
    change(scene,name,'\t// Bind back to the default buffer\n\tfx_framebuffer_bind(pass->buffer);\n\n\tif (failed)',r'''	OPT_LOG("OPT_CACHE_STATE", "output=%s cache=%p blur=%p plain=%p blur_fbo=%u plain_fbo=%u size=%dx%d failed=%d reuse=%d",
        output->name, (void *)pass->fx_offscreen_buffers,
        (void *)pass->fx_offscreen_buffers->optimized_blur_buffer,
        (void *)pass->fx_offscreen_buffers->optimized_no_blur_buffer,
        pass->fx_offscreen_buffers->optimized_blur_buffer ? pass->fx_offscreen_buffers->optimized_blur_buffer->fbo : 0,
        pass->fx_offscreen_buffers->optimized_no_blur_buffer ? pass->fx_offscreen_buffers->optimized_no_blur_buffer->fbo : 0,
        width, height, failed, opt_before != NULL && opt_before == pass->fx_offscreen_buffers->optimized_blur_buffer);
    // Bind back to the default buffer
    fx_framebuffer_bind(pass->buffer);

    if (failed)'''.replace('\\t','\t'))
    change(scene,name,'\tif (!buffer) {\n\t\tgoto finish;',r'''	OPT_LOG("OPT_BLUR_USE", "output=%s cache=%p chosen=%p optimized=%d strength=%.3f fbo=%u",
        ((const struct wlr_output *)pass->fx_offscreen_buffers->addon.owner)->name,
        (void *)pass->fx_offscreen_buffers, (void *)buffer, fx_options->use_optimized_blur, fx_options->blur_strength,
        buffer ? buffer->fbo : 0);
    if (!buffer) {
        goto finish;'''.replace('\\t','\t'))
    change(scene,name,'\tstruct fx_framebuffer *fx_buffer = get_main_buffer_blur(pass, &blur_options);',r'''	OPT_LOG("OPT_GPU_REBUILD", "output=%s cache=%p source=%p source_fbo=%u region=%d,%d,%d,%d",
        ((const struct wlr_output *)pass->fx_offscreen_buffers->addon.owner)->name,
        (void *)pass->fx_offscreen_buffers, (void *)pass->buffer, pass->buffer->fbo,
        clip.extents.x1, clip.extents.y1, clip.extents.x2, clip.extents.y2);
    struct fx_framebuffer *fx_buffer = get_main_buffer_blur(pass, &blur_options);'''.replace('\\t','\t'))
    change(scene,name,'\treturn fx_buffer != NULL;','\tOPT_LOG("OPT_GPU_RESULT", "output=%s cache=%p result=%d blurred=%p", ((const struct wlr_output *)pass->fx_offscreen_buffers->addon.owner)->name, (void *)pass->fx_offscreen_buffers, fx_buffer != NULL, (void *)fx_buffer);\n\treturn fx_buffer != NULL;')
    change(scene,name,'\t// Draw onto the dst_buffer',r'''	OPT_LOG("OPT_GPU_COPY", "output=%s cache=%p dst=%p src=%p dst_fbo=%u src_fbo=%u region=%d,%d,%d,%d",
        pass->fx_offscreen_buffers ? ((const struct wlr_output *)pass->fx_offscreen_buffers->addon.owner)->name : "none",
        (void *)pass->fx_offscreen_buffers, (void *)dst_buffer, (void *)src_buffer, dst_buffer->fbo, src_buffer->fbo,
        region.extents.x1, region.extents.y1, region.extents.x2, region.extents.y2);
    // Draw onto the dst_buffer'''.replace('\\t','\t'))
    change(scene,name,'\twlr_texture_destroy(src_tex);','\tOPT_LOG("OPT_GPU_COPY_DRAWN", "dst=%p src=%p", (void *)dst_buffer, (void *)src_buffer);\n\twlr_texture_destroy(src_tex);')
    name='render/fx_renderer/fx_offscreen_buffers.c'
    change(scene,name,'\t// Make sure to free the buffers','\tOPT_LOG("OPT_CACHE_DESTROY", "output=%s cache=%p blur=%p plain=%p", ((const struct wlr_output *)fbos->addon.owner)->name, (void *)fbos, (void *)fbos->optimized_blur_buffer, (void *)fbos->optimized_no_blur_buffer);\n\t// Make sure to free the buffers')
    change(scene,name,'\twl_list_insert(&renderer->offscreen_buffers, &fbos->link);','\tOPT_LOG("OPT_CACHE_ALLOC", "output=%s cache=%p", output->name, (void *)fbos);\n\twl_list_insert(&renderer->offscreen_buffers, &fbos->link);')
    name='render/fx_renderer/fx_framebuffer.c'
    change(scene,name,'\t// Release the framebuffer','\tOPT_LOG("OPT_FBO_DESTROY", "fbo_object=%p native_buffer=%p fbo=%u", (void *)fx_buffer, (void *)fx_buffer->buffer, fx_buffer->fbo);\n\t// Release the framebuffer')
    # Add a timestamped source/scene-layer trace on the existing Sway commit hook.
    name='sway/desktop/layer_shell.c'
    p=mosaic/name;originals[p]=p.read_text();p.write_text('#include <stdio.h>\n#include <time.h>\n#include "sway/tree/root.h"\n'+p.read_text())
    change(mosaic,name,'\t// Rerender the optimized blur on change',r'''	/* WHY: verify actual source ownership before interpreting cache invalidation.
     * CONTRACT: passive private trace; reads borrowed scene/surface pointers.
     * INVARIANT: no extra dirty call or change to commit/arrangement order. */
    if (getenv("OPT_TRACE")) {
        struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
        struct wlr_surface *s = layer_surface->surface;
        int x = 0, y = 0; bool valid = wlr_scene_node_coords(&surface->scene->tree->node, &x, &y);
        fprintf(stderr, "OPT_BACKGROUND_COMMIT ns=%lld output=%s surface=%p resource=%u buffer=%p seq=%u layer=%u mapped=%d coords=%d,%d valid=%d tree=%p parent=%p layer_parent=%p background=%p background_parent=%p global_background=%p bottom=%p blur_tree=%p opt_node=%p opt_parent=%p damage=%d,%d,%d,%d namespace=%s\n",
            (long long)t.tv_sec * 1000000000LL + t.tv_nsec, surface->output ? surface->output->wlr_output->name : "none",
            (void *)s, wl_resource_get_id(s->resource), (void *)s->buffer, s->current.seq, layer_surface->current.layer, s->mapped, x, y, valid,
            (void *)surface->scene->tree, (void *)surface->scene->tree->node.parent, (void *)surface->tree->node.parent,
            surface->output ? (void *)surface->output->layers.shell_background : NULL,
            surface->output ? (void *)surface->output->layers.shell_background->node.parent : NULL, (void *)root->layers.shell_background,
            surface->output ? (void *)surface->output->layers.shell_bottom : NULL,
            (void *)root->layers.blur_tree, surface->output ? (void *)surface->output->layers.blur_layer : NULL,
            surface->output ? (void *)surface->output->layers.blur_layer->node.parent : NULL,
            s->buffer_damage.extents.x1, s->buffer_damage.extents.y1, s->buffer_damage.extents.x2, s->buffer_damage.extents.y2,
            layer_surface->namespace);
    }
    // Rerender the optimized blur on change'''.replace('\\t','\t'))
    for root,name in [(scene,'scenefx-cache-trace.patch'),(mosaic,'sway-source-trace.patch')]:
        delta=''
        for p,old in originals.items():
            if not p.is_relative_to(root):continue
            rel=p.relative_to(root)
            delta+=''.join(difflib.unified_diff(old.splitlines(True),p.read_text().splitlines(True),fromfile='a/'+str(rel),tofile='b/'+str(rel)))
        (fixture/name).write_text(delta)
