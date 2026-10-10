# STEP20C viewport feasibility probe

**Status: PARTIALLY FEASIBLE; production implementation not authorized.** Starting source: `aa464f1d7691986db37ea7935885f35dfc43ab77` on clean `main`. The planning sections of this file were created before experimental source code; the measured results follow below.

## Hypothesis and decision rule

The hypothesis is that SceneFX 0.5.0 public APIs can project each real Sway tiled container into a workspace and output viewport while its logical geometry and order remain camera independent. The projection must constrain every visible node, including decorations, effects, transaction buffers and owned popups. The same presented viewport must constrain actual client pointer delivery while preserving client local coordinates. A second output must show its own ordinary content when a translated Mosaic cell geometrically overlaps it.

`FEASIBLE` requires reproducible rendering and client pointer evidence for the complete node and output matrix. `PARTIALLY FEASIBLE` means an observed subset works but explicit coverage gaps remain. `BLOCKED` means the installed public APIs cannot meet required visual and input consistency. An unexecuted case is `NOT TESTED`, never a pass.

## Available public API and provisional scene arrangement

The installed headers are SceneFX 0.5.0 and wlroots 0.20.2. `wlr_scene_tree_create` groups nodes, `wlr_scene_node_set_position` translates them, and `wlr_scene_node_at` reports the topmost hit. SceneFX declares node specific clipped regions for rect, shadow and blur; `wlr_scene_subsurface_tree_set_clip` declares a crop in root surface coordinates for descendant subsurface trees. `wlr_scene_buffer_set_source_box` crops the sampled buffer source. There is no declared generic tree clip or output build state subtree clip. Exact declarations, semantics and measured behavior will be audited below after the experiment.

The candidate scene retains Sway's workspace, container and view scene trees. A row projection would take checked logical row geometry, a viewport rectangle, camera offset and workspace/output owner as inputs. It would derive node local intersections without changing the real container order. Popups currently live in a root popup layer and must be handled with their owning view. The experiment may add instrumentation and candidate projection code only in a disposable `/tmp` checkout; production files remain unchanged.

## Required headless evidence

First use one virtual output and an oversized Row 0. Then use two adjacent virtual outputs, with Mosaic on one and normal content on the other. Translate the row until a hidden Mosaic cell geometrically overlaps the second output. Test horizontal, vertical, negative origin, mixed scale and rotated arrangements. Capture outputs independently and inspect boundary pixels; check normal content remains visible. Exercise complete and partial toplevels, subsurfaces, decorations, shadow, blur, saved buffer, popup and nested popup, and node creation/destruction.

An instrumented Wayland client must record pointer enter/leave, motion with client local coordinates, and both button codes. Inside a partial cell, events must reach its client with correct coordinates. Outside the viewport and over a fully hidden cell, no Mosaic event or focus may occur. Normal content underneath a rejected hit must still receive events. `wlr_scene_node_at` returns only one topmost node, so a proposed post filter must prove how it finds a valid underlying hit, or show a scene arrangement that makes the hidden hit absent.

Instrument scene damage, output frame/build requests, camera translation, popup create/destroy and effect edges. Check exposed and vacated regions for stale pixels and record whether an unchanged second output is unnecessarily redrawn. No frame rate or damage claim will be inferred from screenshots alone.

## Equipment and isolation

Build and run a separate checkout and build directory under `/tmp`, with a private Wayland socket, private runtime directory and headless backend. Do not install the binary or contact the active desktop IPC socket. The installed headers disclose API shape, not runtime correctness. Headless outputs may differ from physical GPU outputs in direct scanout, color, fractional scaling and effect performance. Any unsupported or unreliable test will be reported as `NOT TESTED`.

## Dependency and source audit

The isolated build used SwayFX Mosaic 0.6 at the starting SHA, SceneFX **0.5.0** (`scenefx-0.5`), wlroots **0.20.2** (`wlroots-0.20`), Wayland client **1.26.0**, Meson **1.12.1**, Ninja **1.13.2**, and GCC **16.2.1**. The candidate and pristine binaries were both built in `/tmp`; neither was installed. The local header paths were `/usr/include/scenefx-0.5/scenefx/types/wlr_scene.h` and `/usr/include/scenefx-0.5/scenefx/types/fx/clipped_region.h`.

The following are **exact public declarations** from the installed SceneFX header. A `tree` is a parent/stacking node, not a render clip. A `clipped_region` holds `struct wlr_box area` and `struct fx_corner_radii corners`; its use on rect, shadow and blur is node relative. The table separates documented behavior from behavior observed in this probe.

| Public declaration | Object, coordinates and rendering scope | Hit testing and limitation |
| --- | --- | --- |
| `struct wlr_scene_tree *wlr_scene_tree_create(struct wlr_scene_tree *parent);` | Tree of child nodes, with parent local positions. | No tree clip argument or setter. Disabling a whole node disables descendants, but cannot preserve a partly visible cell. |
| `void wlr_scene_node_set_position(struct wlr_scene_node *node, int x, int y);` | Positions a node relative to its parent. `bool wlr_scene_node_coords(struct wlr_scene_node *node, int *lx, int *ly);` reports layout coordinates for enabled ancestry. | Translation is not clipping. Integer geometry needs checked conversion. |
| `struct wlr_scene_tree *wlr_scene_subsurface_tree_create(struct wlr_scene_tree *parent, struct wlr_surface *surface);` | Creates a surface and its subsurfaces. | Does not provide an owner viewport. |
| `struct wlr_scene_tree *wlr_scene_xdg_surface_create(struct wlr_scene_tree *parent, struct wlr_xdg_surface *xdg_surface);` | Creates an XDG surface scene with its subsurfaces; returned origin matches window geometry top left. | Popup trees can be separately parented; this call alone does not constrain them to a workspace. |
| `void wlr_scene_subsurface_tree_set_clip(struct wlr_scene_node *node, const struct wlr_box *clip);` | Header: crops descendant subsurface trees in root surface coordinates; null/empty disables clipping. Used by SwayFX already for content geometry. | The probe's projected clip did **not** consistently constrain partly visible XDG pixels and did **not** remove hidden-region hits. A later Sway geometry crop can replace it. It does not clip sibling decorations/effects or saved buffers. |
| `void wlr_scene_rect_set_clipped_region(struct wlr_scene_rect *rect, struct clipped_region clipped_region);` | A single decoration rect; clip is node relative. | Hit behavior was not measured. Every title/border/text rect needs separate treatment. Existing SwayFX corner clips must be intersected, not overwritten. |
| `void wlr_scene_shadow_set_clipped_region(struct wlr_scene_shadow *shadow, struct clipped_region clipped_region);` | One SceneFX shadow, node relative. | Hit behavior and damage on clip changes were not measured. Does not constrain a view buffer. |
| `void wlr_scene_blur_set_clipped_region(struct wlr_scene_blur *blur, struct clipped_region clipped_region);` | One SceneFX blur, node relative. | Hit behavior and effect sampling across viewport edges were not measured. Optimized output blur is a separate node type. |
| `void wlr_scene_buffer_set_source_box(struct wlr_scene_buffer *scene_buffer, const struct wlr_fbox *box);` | Samples a crop of a buffer in buffer source coordinates. `void wlr_scene_buffer_set_dest_size(struct wlr_scene_buffer *scene_buffer, int width, int height);` scales that source into a destination. | This is source cropping, not an independent scene viewport clip. It requires transform/scale mapping and is unsuitable as a generic fix for complete objects. Sway's transaction saved buffers are copied `wlr_scene_buffer` nodes. |
| `struct wlr_scene_node *wlr_scene_node_at(struct wlr_scene_node *node, double lx, double ly, double *nx, double *ny);` | Returns the **topmost** node containing layout local point and node local coordinates. | No next-hit iterator. This probe observed a `WLR_SCENE_NODE_BUFFER` hit outside the Mosaic viewport even when a visual clip was attempted. A rejected hit needs an owner-aware traversal or scene organization that lets the valid underlying hit be found. |
| `bool wlr_scene_output_needs_frame(struct wlr_scene_output *scene_output);` and `bool wlr_scene_output_build_state(struct wlr_scene_output *scene_output, struct wlr_output_state *state, const struct wlr_scene_output_state_options *options);` | Output specific scene build and damage; `wlr_output_state.damage` is output buffer local. | Build options contain timer/color transform/swapchain, no subtree clip. Output rendering does not automatically define input ownership. |

The compositor source confirms that a container owns blur, shadow, title and border rects and a view content tree (`sway/tree/container.c`). `view_center_and_clip_surface` and container arrangement both set content geometry clips (`sway/tree/view.c`, `sway/desktop/transaction.c`). `view_save_buffer` creates a separate saved surface tree from copied scene buffers during transactions. XDG popup creation attaches a descriptor to the popup but uses the root popup layer for its top level; `arrange_popups` positions it from its view. `node_at_coords` walks root layers and stops at the first `wlr_scene_node_at` hit **before** its output fallback (`sway/input/cursor.c`). These are concrete reasons a single content clip cannot be the complete projection.

## Isolated experiment and reproduction

The retained disposable workspace is `/tmp/swayfx-mosaic-step20c-ua1W6E`. `src-pristine` and `build-pristine` are unmodified source/build; `src` and `build` contain the disposable candidate and logging only. The scripts and images in that directory are temporary artifacts, not repository source. The protocol XML for the private virtual pointer came from `wlr-protocols/unstable/wlr-virtual-pointer-unstable-v1.xml` and has SHA-256 `3ff6d540be0bc5228195bf072bde42117ea17945a5c2061add5d3cf97d6bb524`. The injector source is `inject.c`; it uses `motion_absolute`, both Linux button codes 272/273, and `frame` on a private Wayland socket. `wev` is the actual pointer-event recording client.

Essential build/run commands, from the repository baseline:

```sh
git worktree add --detach /tmp/swayfx-mosaic-step20c-ua1W6E/src-pristine aa464f1d7691986db37ea7935885f35dfc43ab77
meson setup /tmp/swayfx-mosaic-step20c-ua1W6E/build-pristine /tmp/swayfx-mosaic-step20c-ua1W6E/src-pristine -Dwerror=false -Dsd-bus-provider=libsystemd -Dmosaic-package=true -Dprefix=/usr -Dbindir=bin -Dswaybar=false -Dswaynag=false -Dman-pages=disabled -Ddefault-wallpaper=false
meson compile -C /tmp/swayfx-mosaic-step20c-ua1W6E/build-pristine -j 8
python /tmp/swayfx-mosaic-step20c-ua1W6E/pristine.py
# Candidate patch is the two snippets below, applied only to /tmp/.../src.
meson compile -C /tmp/swayfx-mosaic-step20c-ua1W6E/build -j 8
python /tmp/swayfx-mosaic-step20c-ua1W6E/pointer.py
```

Each Python runner created a private `XDG_RUNTIME_DIR`, removed inherited `WAYLAND_DISPLAY` and `SWAYSOCK`, and started the disposable binary with `WLR_BACKENDS=headless`, `WLR_HEADLESS_OUTPUTS=2`, `WLR_RENDERER=pixman`. Its configuration set 800×600 outputs at `(0,0)` and `(800,0)`, workspace 1 on HEADLESS-1, workspace 2 on HEADLESS-2, and disabled focus follows mouse. Four differently colored real Kitty XDG clients populated the Mosaic row in the baseline. The pointer run used Kitty A and C with `wev` as B; a separate control put `wev` X on the standard workspace. The runner selected A again after client creation so camera `scroll_x` returned to zero. `grim -o HEADLESS-2` captured the right output before pointer injection. `swaymsg -t get_tree` recorded real Sway node IDs and logical rectangles.

The candidate's essential C calls were applied after `arrange_workspace_tiling` and again after the ordinary geometry clip in `view_center_and_clip_surface`:

```c
/* Experimental only: root scene coordinates must be converted to the
 * subsurface tree's root-surface clip coordinates. */
int lx, ly;
if (wlr_scene_node_coords(&view->content_tree->node, &lx, &ly)) {
    struct wlr_box clip = {
        .x = viewport.x - lx, .y = viewport.y - ly,
        .width = viewport.width, .height = viewport.height,
    };
    wlr_scene_subsurface_tree_set_clip(&view->content_tree->node, &clip);
}
```

The candidate is deliberately incomplete: it does not intersect Sway's existing geometry clip, handle nested containers, decorations, effects, saved buffers or popups, and it has no input guard. It is an API behavior probe, not a production pattern. A single placement after arrangement produced different pixels after later view updates; applying again after `view_center_and_clip_surface` improved some runs but did not establish stable complete clipping. The exact disposable diff is retained by `git diff` in `src`.

For the pointer evidence, the private injector used the following core sequence; its complete `inject.c` remains in the temporary workspace:

```c
zwlr_virtual_pointer_v1_motion_absolute(pointer, time, x, y, 1600, 600);
zwlr_virtual_pointer_v1_frame(pointer);
zwlr_virtual_pointer_v1_button(pointer, time, BTN_LEFT, WL_POINTER_BUTTON_STATE_PRESSED);
zwlr_virtual_pointer_v1_frame(pointer);
zwlr_virtual_pointer_v1_button(pointer, time, BTN_LEFT, WL_POINTER_BUTTON_STATE_RELEASED);
zwlr_virtual_pointer_v1_frame(pointer);
/* Repeat with BTN_RIGHT. */
```

## Measured rendering and pointer evidence

On the pristine binary, the empty HEADLESS-2 capture `pristine-right-empty.png` shows Kitty B green from output local x=0 through x=477 although its workspace is on HEADLESS-1. Sample pixels: `(100,100)=srgb(0,255,0)` and `(600,100)=srgb(0,0,0)`. The normal standard workspace X remains visible when populated (`pristine-right-after.png`). Logical Row 0 rectangles remained 640 px apart; the observed spill is scene projection, not a second layout model. The exact screenshot SHA-256 is `89ed348a6b1a93156347b0aeb84396e44474db137f370734a26abdbde640cdc7`.

The experimental content clip did **not** consistently eliminate spill. In `pointer-partial-right.png`, `wev` B's checker pattern is present on HEADLESS-2 at `(100,100)=srgb(102,102,102)` even though its intended viewport ends at global x=800. Other runs briefly showed a clear content region while an adjacent title region remained; these changing observations are a coverage failure, not a pass. The retained candidate image SHA-256 is `3ae7606a25b875c80edacff480589878ed6aaefbe5a1375bfe69f5122461f7d9`.

The more decisive input observation is in `pointer-partial-compositor.log` and `pointer-partial-client.log`. Before focusing B, the instrumented `node_at_coords` call logged `global=900.0,200.0 con=8 scene_type=2 local=258.0,198.0`; `wev` B logged `wl_pointer.enter ... x,y: 258.000000,198.000000` at that point. Global x=900 is 100 logical pixels inside HEADLESS-2 and **outside** Mosaic's x=0..799 viewport. The local x is geometrically correct for B's x=642 content origin, which confirms this is the real hidden B surface rather than coordinate corruption. Later, after click focus moved the camera, B recorded both left and right press/release at global x=700 with local x=538; that is a valid visible-region control after the camera movement. The hidden-region hover alone violates the input gate. The hidden-region button path was not established as delivered to B, so no such claim is made.

With a standard `wev` X on HEADLESS-2, `X-pointer.log` recorded pointer enter at local `(98,198)` and both left and right press/release for global `(900,200)`. B also had a transient enter before X in that run, so the normal content control does **not** prove absence of hidden Mosaic focus. A separate C `wev` at global x=1300 recorded no pointer event in `C-pointer.log`; this is only one fully hidden surface/input sample, not a complete guarantee. The client trace, not a screenshot, is the pointer evidence.

The `wlr_scene_node_at` log proves it returns B as the topmost buffer in the invalid region. A simple after-the-fact rejection cannot ask that API for the next hit within the same layer. Skipping the entire Mosaic output layer would also skip valid content in a shared root layer. A valid implementation must either organize scene ownership so invalid cells are absent from hit traversal, or implement a scoped, owner-aware traversal and prove it finds the normal target underneath. Neither solution was demonstrated here.

Additional visual-only runs used the same disposable candidate, 800×600 native modes, A/B/C Kitty clients, A focused and an empty second workspace. `geometry.py` retained each configuration, `get_outputs`/`get_tree`, compositor log and HEADLESS-2 PNG. The second output layouts were: vertical `(0,600)`; negative origin with HEADLESS-1 `(-800,0)` and HEADLESS-2 `(0,0)`; scale 1.25 at `(800,0)`; and transform 90 at `(800,0)`. `get_outputs` reported logical second-output boxes 800×600, 800×600, 640×480 and 600×800 respectively. The vertical screenshot was black at output local `(100,100)` and did not exercise an effect or popup crossing Y. The negative, scaled and rotated screenshots all had Kitty B green at `(100,100)` on HEADLESS-2. Their SHA-256 values are `89ed348a6b1a93156347b0aeb84396e44474db137f370734a26abdbde640cdc7`, `2b24cfcee2e043ee6eb322b19800dc1241773da9cdbd9eb1b51cb5a0925fbbd4` and `59978ecf6dca5aedf2efa286a6bc0111b74b1f34b99577d761aa4d9ea89f25cd`. No pointer client was injected in these four runs, so none establishes a complete configuration pass.

## Coverage, effects, popups and damage

| Node or behavior | Evidence and status |
| --- | --- |
| Real XDG toplevel, partly visible | **FAIL:** Kitty/`wev` spill and hidden-region `wev` enter at x=900 in the candidate. |
| Fully hidden XDG toplevel | One `wev` C input sample at x=1300 had no event; visual and full interaction matrix **NOT TESTED**. |
| Subsurfaces | Public helper includes them; no dedicated subsurface client, **NOT TESTED**. |
| Borders, title text and decoration rects | Separate scene nodes shown by source audit; no complete per-node projection, **NOT TESTED** as a working clip. |
| SceneFX shadow and blur | Clipped-region setters exist, but rendering, sampling, damage and interaction **NOT TESTED**. Effects were not disabled to obtain a pass. |
| Saved transaction buffer | Separate `wlr_scene_buffer` tree in source; forced saved-buffer frame **NOT TESTED**. A source box is not a proven viewport clip. |
| XDG popup and nested popup | Root popup ownership confirmed in source; no popup client or viewport test, **NOT TESTED**. Floating/fullscreen/standard popup regression also **NOT TESTED**. |
| Node creation/destruction | Clients were created/stopped; boundary pixels and stale focus across lifecycle **NOT TESTED** systematically. |
| Camera translation and damage | Instrumented `wlr_scene_output_build_state` logged damage on both outputs during camera changes. At one x=400 transition, both outputs recorded full 800×600 damage. HEADLESS-2 also received damage extent `0,25..78,598` from leaked geometry. This is correctness evidence of affected output scheduling in the failing candidate, **not** a performance benchmark. Exposed/vacated pixel cleanliness, popup/effect damage and excessive redraw rate remain **NOT TESTED**. |

The exact output damage was taken from `struct wlr_output_state.damage` after `wlr_scene_output_build_state`, in output buffer local coordinates. The instrumented log line records output name, committed damage flag, rectangle count and region extents. A full damage region after camera movement may be justified by existing animations or other scene work; this probe cannot attribute all work to the new clip.

| Configuration | Objective | Result |
| --- | --- | --- |
| One headless output | Baseline camera/row behavior | Existing headless IPC/render test **PASS** for scrolling and real scene translation; complete clipping **NOT TESTED**. |
| Two horizontal outputs, 800×600 each | No cross-output visual/input leak | **FAIL** on empty HEADLESS-2: visual B spill and hidden B pointer enter. Standard X remained visible in control. |
| Two vertically stacked outputs | Y boundary | Visual diagnostic: second output black at sampled point; Y-crossing effects/popups and pointer **NOT TESTED**. |
| Negative output origin | Global coordinate handling | **FAIL visually:** green Mosaic B pixels on HEADLESS-2; input **NOT TESTED**. |
| Different output scales | Logical/pixel rounding | **FAIL visually:** green Mosaic B pixels at scale 1.25; input/edge rounding **NOT TESTED**. |
| Rotated output | Transform behavior | **FAIL visually:** green Mosaic B pixels at transform 90; input/edge rounding **NOT TESTED**. |
| Partly visible cell | Rendering and input agree | **FAIL** at x=900 for B. |
| Fully hidden cell | No invisible interaction | One x=1300 input sample only; **NOT TESTED** as a complete case. |

`meson test` passed its one Mosaic model test in the disposable candidate build. The existing one-output `tests/headless-ipc.py` also passed against the candidate and reported 69,335 changed color components after a scroll; that number is its test diagnostic, **not** a performance measurement or clip proof. The build and both runs used the isolated binary and socket.

## Feasibility decision and next architecture

**PARTIALLY FEASIBLE.** The installed APIs can create and translate real Sway scene trees, perform some node-specific clipping, render normal content on a second output, and report actual client pointer coordinates. The candidate did not establish a complete visual boundary; it definitely did not establish an input boundary. Generic scene-tree clipping is absent from the installed public header. Therefore Approach C remains an architectural hypothesis and **general multi-output Mosaic support is not authorized**.

The narrowest next experiment is a versioned SceneFX scene subtree clip whose contract explicitly covers buffers, decorations, blur, shadows, saved buffers, nested scene descendants, output damage and hit testing. SceneFX is the natural owner of the scene traversal/render/damage primitive; Mosaic should own only the viewport descriptor, workspace/output identity, logical camera, popup association and policy for ordinary versus Mosaic views. A versioned dependency extension would increase upstream maintenance and forward-port cost. It should be considered only after checking SceneFX internals and proving a minimal patch, not started automatically by this probe. An alternate Mosaic scene organization may avoid some hit leakage but still needs a demonstrated visual primitive for all node types. Output-renderer-level filtering is technically possible but has wider damage, effects, scanout and input consistency risk; no renderer replacement was attempted.

For future rows, the clipping contract must accept `(row geometry, viewport rectangle, camera offset, workspace/output owner)` and a scene subtree/owner identity. Row 0 supplies those inputs today, but `rows[0]` must not become the clip primitive's ownership model. No STEP20D behavior or UX decision was implemented. Final cell width, bindings, animation timing/easing and oversized-cell reveal policy remain open.

**Implementation authorization status:** STEP20C production source changes are **not authorized** by this result. Before reconsidering, prove a complete visual and client input boundary on two outputs, including partial/hidden surfaces, decorations/effects, saved buffers, root and nested popups, and the remaining output matrix. The failed and unexecuted cases above must remain visible in the next review.

## Minimal independent reproduction recipe

The following recreates the decisive pristine visual and client input checks without relying on the temporary Python runners. Run in a fresh disposable checkout/build. Use a private runtime directory and **the absolute private IPC socket** on every command; never fall back to the active desktop socket. `wev` writes one log per client. The initial `sleep` calls only let clients map and transactions settle; IPC tree inspection confirms the actual state.

```sh
probe_dir=$(mktemp -d /tmp/step20c-repro-XXXXXX)
git worktree add --detach "$probe_dir/src" aa464f1d7691986db37ea7935885f35dfc43ab77
meson setup "$probe_dir/build" "$probe_dir/src" -Dwerror=false -Dsd-bus-provider=libsystemd -Dmosaic-package=true -Dprefix=/usr -Dbindir=bin -Dswaybar=false -Dswaynag=false -Dman-pages=disabled -Ddefault-wallpaper=false
meson compile -C "$probe_dir/build" -j 8
mkdir "$probe_dir/run"
cat > "$probe_dir/run/config" <<'CONF'
output HEADLESS-1 resolution 800x600 position 0 0
output HEADLESS-2 resolution 800x600 position 800 0
workspace 1 output HEADLESS-1
workspace 2 output HEADLESS-2
focus_follows_mouse no
CONF
env -u WAYLAND_DISPLAY -u SWAYSOCK XDG_RUNTIME_DIR="$probe_dir/run" WLR_BACKENDS=headless WLR_HEADLESS_OUTPUTS=2 WLR_RENDERER=pixman "$probe_dir/build/sway/swayfx-mosaic" -d -c "$probe_dir/run/config" > "$probe_dir/compositor.log" 2>&1 &
probe_pid=$!
# Wait for both private sway-ipc.*.sock and wayland-* sockets in $probe_dir/run.
export XDG_RUNTIME_DIR="$probe_dir/run"
export SWAYSOCK=$(find "$probe_dir/run" -maxdepth 1 -name 'sway-ipc.*.sock' -print -quit)
export WAYLAND_DISPLAY=$(find "$probe_dir/run" -maxdepth 1 -type s -name 'wayland-*' -printf '%f\n' -quit)
swaymsg -s "$SWAYSOCK" 'workspace 1'
swaymsg -s "$SWAYSOCK" 'layout mosaic'
kitty --class A -o background='#ff0000' /usr/bin/sleep 60 &
sleep 0.5
stdbuf -oL wev > "$probe_dir/B-pointer.log" 2>&1 &
sleep 0.8
kitty --class C -o background='#0000ff' /usr/bin/sleep 60 &
sleep 0.8
swaymsg -s "$SWAYSOCK" -t get_tree > "$probe_dir/tree.json"
a_id=$(jq -r '[.. | objects | select(.type? == "workspace" and .name? == "1")][0].nodes[0].id' "$probe_dir/tree.json")
swaymsg -s "$SWAYSOCK" "[con_id=$a_id] focus"
# Verify Row 0 camera is 0 in a fresh get_tree response.
sleep 2
grim -o HEADLESS-2 "$probe_dir/right-empty.png"
# Build the injector below, then send x=900 before any visible B click.
"$probe_dir/inject" 1600 600 900 200
```

The private virtual pointer protocol can be obtained from `https://raw.githubusercontent.com/swaywm/wlr-protocols/master/unstable/wlr-virtual-pointer-unstable-v1.xml`; verify the SHA-256 above before generating code. Then:

```sh
wayland-scanner client-header "$probe_dir/wlr-virtual-pointer.xml" "$probe_dir/virtual-pointer-client.h"
wayland-scanner private-code "$probe_dir/wlr-virtual-pointer.xml" "$probe_dir/virtual-pointer-protocol.c"
cc -std=c17 -D_DEFAULT_SOURCE -I"$probe_dir" "$probe_dir/inject.c" "$probe_dir/virtual-pointer-protocol.c" -o "$probe_dir/inject" $(pkg-config --cflags --libs wayland-client)
```

The following is the essential complete injector used for the event check (save as `$probe_dir/inject.c`). It binds only the private compositor connection selected by `WAYLAND_DISPLAY` and sends both buttons at each requested point:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <linux/input-event-codes.h>
#include <wayland-client.h>
#include "virtual-pointer-client.h"

static struct zwlr_virtual_pointer_manager_v1 *manager;
static void global(void *data, struct wl_registry *registry, uint32_t name,
        const char *interface, uint32_t version) {
    if (strcmp(interface, zwlr_virtual_pointer_manager_v1_interface.name) == 0)
        manager = wl_registry_bind(registry, name,
            &zwlr_virtual_pointer_manager_v1_interface, version < 2 ? version : 2);
}
static void removed(void *data, struct wl_registry *registry, uint32_t name) {}

int main(int argc, char **argv) {
    if (argc < 5 || (argc - 3) % 2) return 2;
    struct wl_display *display = wl_display_connect(NULL);
    if (!display) return 1;
    struct wl_registry *registry = wl_display_get_registry(display);
    struct wl_registry_listener listener = {global, removed};
    wl_registry_add_listener(registry, &listener, NULL);
    wl_display_roundtrip(display);
    if (!manager) return 1;
    struct zwlr_virtual_pointer_v1 *pointer =
        zwlr_virtual_pointer_manager_v1_create_virtual_pointer(manager, NULL);
    wl_display_roundtrip(display);
    for (int i = 3; i + 1 < argc; i += 2) {
        int x = atoi(argv[i]), y = atoi(argv[i + 1]);
        zwlr_virtual_pointer_v1_motion_absolute(pointer, 100 + i,
            x, y, atoi(argv[1]), atoi(argv[2]));
        zwlr_virtual_pointer_v1_frame(pointer);
        wl_display_flush(display);
        usleep(200000);
        int buttons[] = {BTN_LEFT, BTN_RIGHT};
        for (int b = 0; b < 2; ++b) {
            zwlr_virtual_pointer_v1_button(pointer, 110 + i, buttons[b],
                WL_POINTER_BUTTON_STATE_PRESSED);
            zwlr_virtual_pointer_v1_frame(pointer);
            zwlr_virtual_pointer_v1_button(pointer, 120 + i, buttons[b],
                WL_POINTER_BUTTON_STATE_RELEASED);
            zwlr_virtual_pointer_v1_frame(pointer);
            wl_display_flush(display);
            usleep(100000);
        }
    }
    wl_display_roundtrip(display);
    zwlr_virtual_pointer_v1_destroy(pointer);
    zwlr_virtual_pointer_manager_v1_destroy(manager);
    wl_registry_destroy(registry);
    wl_display_disconnect(display);
    return 0;
}
```

The manual recipe starts disposable processes that must be stopped after capture (`kill "$probe_pid"` and stop the three private clients). It does not remove the temporary files, so another developer can inspect logs. To reproduce the experimental candidate specifically, add the content clip snippet above after `arrange_workspace_tiling` and after Sway's ordinary geometry crop in the disposable checkout, then rebuild. The separate `wlr_scene_node_at` log line was inserted immediately before `node_at_coords` returned a container; the output-frame log line read `pending.damage` after `wlr_scene_output_build_state`.
