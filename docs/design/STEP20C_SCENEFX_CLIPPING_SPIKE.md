# STEP20C SceneFX subtree clipping spike

**Final status: PARTIALLY_FEASIBLE.** Source baseline: SwayFX Mosaic `513b720750a92e02fca3cb2fea2bcf170071069b`, SceneFX tag `0.5` at `37ccd723bef49e6891156ffafce8f549f01446cc`, installed SceneFX 0.5.0 and wlroots 0.20.2. This plan was written before any experimental source edit. It does not authorize production STEP20C implementation or a permanent SceneFX fork.

## Observation and root-cause hypothesis

The [prior feasibility probe](STEP20C_FEASIBILITY_PROBE.md) captured Kitty pixels from a Mosaic workspace on a second, empty 800×600 headless output. A disposable use of `wlr_scene_subsurface_tree_set_clip` did not reliably remove the complete object, and `wlr_scene_node_at` still returned a partly visible client at global `(900,200)` outside Mosaic's x=0..799 viewport. The client received `wl_pointer.enter` at its valid local `(258,198)` coordinate. Rectangles, shadows, blur, saved buffers and root popups were not covered by that surface-only experiment.

**PROPOSED root cause:** SceneFX 0.5's tree node groups and translates descendants but carries no inherited clip. Its `_scene_nodes_in_box` traversal tests enabled descendant boxes; `scene_node_update_iterator` computes cached `node->visible` from those boxes; `scene_entry_render` consumes that visibility; `scene_node_at_iterator` independently accepts buffer hits. A surface-specific crop changes only one content path and can be superseded by normal Sway geometry updates. A correct tree clip must be part of scene traversal, visibility, rendering, damage and hit testing together. This is a hypothesis until the disposable experiment proves behavior and lifecycle transitions.

## SceneFX 0.5 source architecture already inspected

The tag's main implementation is `types/scene/wlr_scene.c`. `struct wlr_scene_tree` in `include/scenefx/types/wlr_scene.h` contains a node and ordered children, with no clip field. `_scene_nodes_in_box` recursively descends enabled trees and considers leaf node bounds. `scene_node_update_iterator` builds `node->visible`; `scene_node_visibility`, `scene_node_bounds`, `scene_update_region` and `scene_node_update` combine old/new visibility and output damage. `construct_render_list_iterator` and `wlr_scene_output_build_state` flatten visible leaves per output. `scene_entry_render` passes `node->visible` through output scale/transform and damage to the render pass for buffers, rectangles, shadows and blur. `scene_node_at_iterator` and `wlr_scene_node_at` use the same box traversal but return one topmost hit. `scene_entry_try_direct_scanout` may bypass composition for one eligible buffer. `wlr_scene_node_destroy`, `wlr_scene_node_set_enabled`, `wlr_scene_node_set_position` and `wlr_scene_node_reparent` call scene update paths. Exact function locations and the resulting minimal patch scope will be recorded after the audit.

The installed SceneFX header declares surface/subsurface clipping; the SceneFX tag's `types/scene` directory does not implement `wlr_scene_subsurface_tree_set_clip`. The installed wlroots 0.20 library exports it. That API is not a SceneFX subtree clip and must not be treated as one. This source/symbol boundary requires deliberate ABI inspection before a shared-library experiment.

## Alternatives before implementation

| Option | API/source, visual/input/damage path | Effects, popup and standard behavior | Maintenance, packaging and future rows |
| --- | --- | --- | --- |
| **A. Inherited SceneFX tree clip** | Add a bounded rectangle to a tree; intersect ancestor clips during traversal and visibility; use the same effective clip for hit and render. Old/new clipped bounds must damage outputs. | Covers descendant buffers, decoration rects, shadows and blur if visibility drives all render cases. Root popups need independent owner-derived clip or ownership change. Standard trees have no clip. | General primitive can serve each future row. Smallest conceptual shared operation, but a modified library and ABI/distribution question. **Primary experimental candidate, PROPOSED.** |
| **B. Mosaic-specific organization on existing APIs** | Rearrange real scene trees and apply per-node clips/crops plus a scoped hit traversal. No generic tree clip; every leaf/lifecycle path needs coverage. | High risk of missing saved buffers, effects and root popups or losing underlying hits. Standard paths can remain separate. | No private SceneFX dependency, but a wider, version-sensitive compositor patch; future rows multiply per-node work. Must be reconsidered if A's packaging gate fails. |
| **C. Output-level clip** | Add per-output subtree filtering in SceneFX build/render; separate input filter and damage accounting. | Could keep effect output bounds, but output-level masks alone do not encode owner popups or hit traversal. Direct scanout and optimized blur need scrutiny. | Potentially broad renderer/output maintenance; future row clips still require a per-row owner map. No broad renderer replacement in this spike. |

**Selection: A, PROPOSED for a disposable test only.** It is the smallest place where the existing SceneFX visibility and render paths can share one effective region with hit testing. The choice is invalidated if the implementation must broadly replace output rendering, disable effects, duplicate buffers/containers, weaken input guarantees, or require a system SceneFX replacement to distribute.

## Ownership and invariants

Mosaic owns a viewport descriptor derived from row geometry, viewport rectangle, camera offset and current workspace/output owner. SceneFX owns only the clipping mechanism, not Sway order, row membership, focus or camera policy. A tree's clip is local to that tree; an unset clip inherits its parent, and a child clip can only narrow the inherited region. Effective coordinates must be checked in 64-bit arithmetic before narrowing to SceneFX integer/pixman bounds. A newly created descendant inherits immediately; disable, move, reparent and destroy must clear old pixels/hits and expose newly uncovered content. Rendered and hit regions must agree at fractional logical edges and after output transforms. Ordinary unclipped SwayFX scene trees must retain existing semantics.

The conceptual API name `wlr_scene_tree_set_clip(tree, box)` is only a proposed experiment. The setter would copy the rectangle (no borrowed pointer), with an explicit way to clear it; tree destruction owns its state. A null/empty distinction, clipping coordinate space, damage and child lifetime will be specified from implementation evidence. No native struct serialization or second authoritative window model is involved. Row 0, Row 1 and Row 2 could each attach this same primitive to their real row scene tree and supply independent viewport/camera values; this spike does not implement runtime extra rows.

## Minimal experimental proof plan

Use a separate SceneFX 0.5 checkout, a separate Mosaic compositor checkout and separate build trees under `/tmp`. Compile a private library; use explicit private library lookup for only the headless compositor process. First validate new clip API semantics on a small scene and pointer hit test. Then use real XDG clients on two virtual outputs. Capture output pixels and instrument client pointer enter/leave, motion, both buttons and local coordinates. Cover partial/full hidden toplevels, subsurfaces, decorations, shadow, blur, saved transaction buffers, creation/destruction, moving/nested clips, popup ownership, camera changes, workspace switches and reparenting. Record output-specific damage and direct scanout eligibility. Run negative origin, 1.25 scale, rotated and vertical arrangements when reliable; any incomplete case is **NOT TESTED**, never PASS.

The visual invariant is that no Mosaic pixel is on HEADLESS-2 while ordinary X remains visible. The input invariant is that hidden Mosaic surfaces receive no hover/button focus and X receives the event underneath; visible portions retain correct client local coordinates. Damage must clear vacated pixels and invalidate newly exposed areas without unrelated output redraws where avoidable. A screenshot cannot prove client input. A toplevel-only success cannot pass the popup/effect gate.

## Packaging gate and invalidation conditions

The current package owns only `/usr/bin/swayfx-mosaic`; normal SwayFX owns `/usr/bin/sway`. System SceneFX and wlroots must remain untouched and independently updatable with ordinary Arch/AUR SwayFX. The spike must inspect SONAME, dynamic linker resolution, symbol collisions, ABI, private runpath and static-link feasibility by an actual private build before claiming a distribution route. Upstreaming a generic primitive, a privately bundled compatible library, and a static/private link are candidates for comparison. Requiring a second system SceneFX package or replacing the system library violates the preferred architecture. No permanent dependency fork is authorized by this experiment.

The primary approach fails the gate if a clipped descendant remains visible or hittable, damage leaves stale pixels, effects must be disabled, popup ownership cannot be preserved, an ordinary Sway path regresses, or package isolation cannot be demonstrated. A library proof alone cannot authorize production; packaging and upstream maintenance require separate approval.

## Results and decision

**PARTIALLY_FEASIBLE.** A private SceneFX 0.5 extension clipped the real tiled XDG window, decoration, and pointer path in one- and two-output headless cases. A real GTK XDG popup from that window remained in SwayFX's global popup layer, rendered on the neighboring output, and intercepted a right click over an ordinary client. Full damage, blur, saved-buffer and nested-popup behavior were not demonstrated. The full render/input/damage/package gate is therefore **not passed**. Production STEP20C, general multi-output support, a permanent SceneFX fork and a package change are **not authorized** by this spike.

### Exact dependency and source audit

| Component | Version / provenance | Relevant source |
| --- | --- | --- |
| Mosaic | `513b720750a92e02fca3cb2fea2bcf170071069b`, clean `main` before this documentation | `sway/desktop/transaction.c`, `sway/desktop/xdg_shell.c`, `sway/input/cursor.c`, `sway/tree/view.c` |
| SceneFX | Installed Arch `0.5-1`, project `0.5.0`; isolated tag `0.5` commit `37ccd723bef49e6891156ffafce8f549f01446cc` | `include/scenefx/types/wlr_scene.h`, `types/scene/wlr_scene.c`, `render/fx_renderer/fx_pass.c` |
| wlroots | Installed `0.20.2` | `/usr/include/wlroots-0.20/wlr/types/wlr_scene.h`; `/usr/lib/libwlroots-0.20.so` |
| SceneFX development comparison | Isolated upstream checkout HEAD `0070ae510426d0e665d5785129b68f03c7264d62` on the probe date | No generic `scene_tree_set_clip` declaration or implementation was found by source search. This is not an exhaustive claim about all open proposals. |

The installed SceneFX header matches the 0.5 tag header. The tag header declares `wlr_scene_subsurface_tree_set_clip`, but `nm -D` locates its implementation in the installed wlroots library, not the SceneFX library. Both libraries expose scene functions such as `wlr_scene_node_at`; the private executable's symbol resolution and SceneFX/wlroots layout compatibility are material ABI constraints.

The isolated development checkout was searched for generic tree-clip symbols and found none. The [upstream SceneFX issue list](https://github.com/wlrfx/scenefx/issues) and [open pull-request list](https://github.com/wlrfx/scenefx/pulls) were also inspected on 2026-10-10; no clearly equivalent open generic inherited-tree clip was identified there. This is a bounded search, not proof that no proposal exists in any branch or discussion.

**Public declarations audited** (from SceneFX 0.5's `include/scenefx/types/wlr_scene.h`):

| Declaration | Scope, coordinates and hit/damage consequence |
| --- | --- |
| `struct wlr_scene_tree *wlr_scene_tree_create(struct wlr_scene_tree *parent);` | Ordered grouping/translation tree; no inherited clip in 0.5. Child positions are parent relative. |
| `void wlr_scene_node_set_position(struct wlr_scene_node *node, int x, int y);` | Parent-relative integer translation; scene update damages old/new visibility. |
| `void wlr_scene_node_set_enabled(struct wlr_scene_node *node, bool enabled);` | Node/subtree visibility and scene update; not a viewport. |
| `void wlr_scene_node_reparent(struct wlr_scene_node *node, struct wlr_scene_tree *new_parent);` | Changes ancestry/stacking and updates scene damage. The private primitive derives the effective clip from the new ancestors. |
| `struct wlr_scene_node *wlr_scene_node_at(struct wlr_scene_node *node, double lx, double ly, double *nx, double *ny);` | Layout-local topmost hit only. A clipped top hit must be rejected *inside* traversal so the ordinary hit underneath can be found; filtering the returned node afterward loses it. |
| `void wlr_scene_rect_set_clipped_region(struct wlr_scene_rect *rect, struct clipped_region clipped_region);` | One SceneFX rectangle, node-relative. Its setter cannot constrain a sibling view buffer; rect input has its own clipped-region behavior. |
| `void wlr_scene_shadow_set_clipped_region(struct wlr_scene_shadow *shadow, struct clipped_region clipped_region);` | One shadow, node-relative. No descendant inheritance. |
| `void wlr_scene_blur_set_clipped_region(struct wlr_scene_blur *blur, struct clipped_region clipped_region);` | One blur, node-relative. No descendant inheritance or popup handling. |
| `void wlr_scene_buffer_set_source_box(struct wlr_scene_buffer *scene_buffer, const struct wlr_fbox *box);` | Buffer source crop, not whole-object output clipping or a hit boundary. |
| `void wlr_scene_subsurface_tree_set_clip(struct wlr_scene_node *node, const struct wlr_box *clip);` | Root-surface-relative crop for a subsurface tree; NULL/empty clears. Implemented by wlroots 0.20 in this installation. It does not cover sibling decorations/effects/global popups. |
| `struct wlr_scene_tree *wlr_scene_xdg_surface_create(struct wlr_scene_tree *parent, struct wlr_xdg_surface *xdg_surface);` | Creates XDG surface plus subsurfaces under the supplied parent. Tiled toplevels inherit a clip if their actual parent is clipped; SwayFX root popups use another parent. |
| `void wlr_scene_node_destroy(struct wlr_scene_node *node);` | Emits a destroy signal before recursively releasing children. The experiment's private clip sidecar listens here. |

The proposed private API was `void wlr_scene_tree_set_clip(struct wlr_scene_tree *tree, const struct wlr_box *clip);`: copy a tree-local logical rectangle, clear with NULL, reject negative dimensions by assertion in the experiment. An empty non-NULL box clips everything. This is **not** an installed or approved public API. The private implementation has no allocation-error return, performs a linear sidecar lookup and does not validate coordinate-addition overflow; those are production blockers, not accepted contracts.

**Internal sites audited** in SceneFX tag `types/scene/wlr_scene.c` (tag source lines; the private patch shifts later line numbers):

| Function / location | Role and experimental change |
| --- | --- |
| `_scene_nodes_in_box` ~255 | Descends enabled trees and leaf bounds in reverse stacking order. Kept; individual leaf visibility/hit filters enforce inherited clips. It still traverses clipped-away branches, a performance limit. |
| `scene_node_update_iterator` ~676; `scene_node_opaque_region` ~323 | Builds cached `node->visible`, subtracts opaque coverage. Experiment intersects both regions with all ancestor clips. |
| `scene_node_bounds` ~735; `scene_node_visibility` ~717; `scene_node_update` ~827 | Old and new subtree bounds feed scene damage and output-enter/leave updates. Experiment intersects new bounds; old cached visible remains available for clearing. |
| `scene_damage_outputs` ~529; `scene_output_damage` ~501 | Translates/scales/transforms global damage, intersects output buffer, schedules a frame for nonempty damage. Instrumented after intersection. |
| `scene_entry_render` ~1957; `construct_render_list_iterator` ~2606; `wlr_scene_output_build_state` ~3062 | Render list uses cached visibility and output damage; buffer, rect, shadow, blur cases pass regions to SceneFX render pass. Output scale/rotation occurs after the logical clip. Visual effect coverage remains incomplete. |
| `scene_node_at_iterator` ~1883; `wlr_scene_node_at` ~1919 | Experiment rejects a leaf outside all inherited clips before accepting buffer/rect input; traversal continues to the next node. |
| `scene_entry_try_direct_scanout` ~2737 | Experiment conservatively makes a clipped descendant ineligible for direct scanout. No DRM scanout test ran on headless outputs. |
| `wlr_scene_node_destroy` ~128; `wlr_scene_node_set_enabled` ~1728; `wlr_scene_node_set_position` ~1745; `wlr_scene_node_reparent` ~1801 | Lifetime and scene-update paths. A private node-destroy listener frees the clip sidecar; nested hit/reparent behavior was tested without a Wayland client. |
| `fx_pass.c` render methods | SceneFX render options have per-node clip regions. The experiment relies on effective `node->visible` feeding those options; no shader replacement or effect disable was introduced. |

SwayFX's top-level popup creation (`sway/desktop/xdg_shell.c`, `handle_new_popup`) parents it to `root->layers.popup`; nested popups are parented to their popup's XDG tree. `arrange_popups` in `sway/desktop/transaction.c` translates the root popup from the owner's content-tree coordinates. The tiling tree's clip does not reach this global branch. Saved transaction buffers are children of the view's `saved_surface_tree` (`sway/tree/view.c`), but that path was not exercised as a distinct visual test. Container borders/title and shadow/blur are separate nodes under the real container scene tree. The compositor's cursor asks `wlr_scene_node_at` layer by layer (`sway/input/cursor.c`), so a popup hit on the global layer can intercept another output.

### Isolated implementation and reproducibility

All source, binaries, scripts, screenshots and logs remain under `/tmp/swayfx-mosaic-step20c-scenefx-aiMRk6/`. The exact private diffs are `scenefx-clip.patch` (SHA-256 `42b61025055af7552fe648dd9d8c7429f7ff670c5bacfa9f1b7b04e9eae09a91`) and `mosaic-clip.patch` (SHA-256 `341a8d9d9846c1e18a869c21d420021fe2130c89c027892c98d8d3ce04e86710`). They are retained only in `/tmp`, not the project repository. Scripts include `baseline.py`, `pointer.py`, `pointer-underlying.py`, `pointer-hidden.py`, `pointer-one.py`, `geometry.py`, `effects.py`, `nested.c`, `gtkpopup.py`, `popup-gtk-run.py`, and `popup-gtk-under.py`; the virtual pointer injector source/protocol is retained in the earlier probe at `/tmp/swayfx-mosaic-step20c-ua1W6E/`.

An initial patch appended fields to `struct wlr_scene_tree`. The first real XDG client crashed in `wlr_color_manager_v1_set_surface_preferred_image_description` during a SceneFX output-enter callback (`coredumpctl` PID 160381; `abi-crash-backtrace.log`). The appended field shifted the embedded root `struct wlr_scene` layout visible to wlroots. This **failed candidate was discarded**. The working spike preserves the public struct layout: a private, destroy-listener-owned sidecar maps each clipped tree to a copied box. A production-quality upstream design needs an ABI-safe attachment with allocation errors and bounded lookup cost.

The essential experimental algorithm is:

```c
/* For each leaf visibility/opaque/bounds region: */
for (ancestor = leaf; ancestor; ancestor = ancestor->parent) {
    if (ancestor has a tree-local clip)
        intersect(region, clip translated by ancestor scene coordinates);
}
/* For each candidate hit during topmost traversal: */
if (point is outside any ancestor clip) return false; /* keep searching */
/* On clip mutation: */
capture_old_cached_visibility(); update_new_clipped_bounds(); damage_both();
```

The disposable compositor sets the Mosaic workspace tiling-tree clip to its usable-area width/height with local x=`scroll_x`, after placing that tree at `usable_area.x - scroll_x`. Standard layout trees clear the clip. The logical Sway containers and `get_tree` order are untouched. That patch is deliberately Row-0-specific test wiring; the generic primitive itself takes any tree and can serve independent future row viewports. Future Row 0/1/2 should each have a real row-scene owner and a clip derived from `{row geometry, viewport rectangle, camera offset, workspace/output owner}`; this spike does not implement extra runtime rows.

Representative commands (run only in the disposable workspace):

```sh
R=/tmp/swayfx-mosaic-step20c-scenefx-aiMRk6
meson setup "$R/scenefx-build" "$R/scenefx-0.5" -Dexamples=false -Dwerror=false
meson compile -C "$R/scenefx-build"
PKG_CONFIG_PATH="$R/scenefx-build/meson-uninstalled" meson setup "$R/mosaic-build" "$R/mosaic" -Ddefault-wallpaper=false -Dmosaic-package=true -Dswaybar=false -Dswaynag=false -Dman-pages=disabled -Dsd-bus-provider=libsystemd -Dwerror=false
meson compile -C "$R/mosaic-build"
python3 "$R/baseline.py"
python3 "$R/pointer-underlying.py"
python3 "$R/popup-gtk-under.py"
for case in vertical negative scale rotated; do python3 "$R/geometry.py" "$case"; done
PKG_CONFIG_PATH="$R/scenefx-build/meson-uninstalled" cc -DWLR_USE_UNSTABLE -o "$R/nested" "$R/nested.c" $(PKG_CONFIG_PATH="$R/scenefx-build/meson-uninstalled" pkg-config --cflags --libs scenefx-0.5)
LD_LIBRARY_PATH="$R/scenefx-build" "$R/nested"
meson setup "$R/scenefx-static-build" "$R/scenefx-0.5" -Ddefault_library=static -Dexamples=false -Dwerror=false
meson compile -C "$R/scenefx-static-build"
PKG_CONFIG_PATH="$R/scenefx-static-build/meson-uninstalled" meson setup "$R/mosaic-static-build" "$R/mosaic" -Ddefault-wallpaper=false -Dmosaic-package=true -Dswaybar=false -Dswaynag=false -Dman-pages=disabled -Dsd-bus-provider=libsystemd -Dwerror=false
meson compile -C "$R/mosaic-static-build"
readelf -d "$R/mosaic-static-build/sway/swayfx-mosaic"
python3 "$R/baseline-static.py"
```

The Python harnesses set `XDG_RUNTIME_DIR` to distinct private directories, `WLR_BACKENDS=headless`, `WLR_RENDERER=pixman`, private `WAYLAND_DISPLAY`/`SWAYSOCK`, and `LD_LIBRARY_PATH` **only for child headless processes**. They stop those children. They did not install a compositor, replace a system library, reload Sway, or touch the daily session. Since `/tmp` is disposable, reproducing after cleanup requires checking out the pinned revisions and applying the two retained diffs first; the full patch bodies are preserved at the paths above for the current machine.

### Rendering, input, damage and category evidence

| Case | Evidence | Result |
| --- | --- | --- |
| Real toplevel, partial clip and camera translation | Four Kitty XDG clients in an 800×600 Mosaic row; `left-before.png` has red at `(100,100)` and green at `(700,200)`, then `left-after.png` has green at `(400,300)` after camera command. `right-empty.png` is black, `right-before.png`/`right-after.png` show ordinary X's magenta `(204,0,204)` at `(100,100)`, `(400,300)`, `(700,200)`. | PASS for these sampled pixels and visible scene paths. No whole-image proof of every effect pixel. |
| Fully hidden tiled cell | `pointer-hidden-run.log`: C (`wev`) at logical x=1280; injected motion, left and right buttons at global `(1300,200)` on output 2. `C-pointer.log` contains no `wl_pointer` events. | PASS for this client/point; no hidden focus observed there. |
| Partly visible cell | `B-partial-pointer.log`: `wl_pointer.enter` local `(58,198)`, motion local `(538,198)`, left button 272 and right button 273 on the visible segment. At global `(900,200)` in the underlying-window run, `B-pointer.log` has no pointer event; `X-pointer.log` has enter local `(98,198)` and both button 272/273 press/release. | PASS for these points and client-local coordinates. The hidden hit did not consume the underlying hit. |
| One output | `one-left.png`, `B-one-pointer.log`: visible B receives enter/motion and both buttons. | PASS for baseline sampled behavior. |
| Borders/title decorations | Output screenshots show SwayFX title/border at the x=799 edge with no matching decoration pixels on the empty output 2. | PASS for the observed style and boundary; alternate border modes untested. |
| Nested clips, move, reparent, destroy | Private `nested.c` creates rect/tree nodes, clips outer and inner trees, moves child, clears clip, reparents it to an unclipped branch, destroys trees. Eight asserted hits gave `1,0,0,1,0,1,0,1` at the documented coordinates in source. | PASS for scene hit semantics and listener lifetime in this bounded synthetic check. It is not rendering/client proof. |
| Shadow and blur enabled | `effects.py` explicitly set `shadows enable`, `shadow_blur_radius 10`, `shadow_offset 20 20`, `blur enable`; no cross-output pixels appeared on empty output 2. Effect commands were accepted, and SceneFX render code passes clipped visibility to render-pass options. | PARTIAL. A visible shadow boundary was exercised, but distinct translucent blur sampling, optimized blur and effect-specific damage were not isolated or proven. Effects were not disabled. |
| XDG root popup | `gtkpopup.py` uses GTK4 `Gtk.Popover`; compositor logged a third `new xdg_surface` at 2.710 s. `gtkpopup-after-right.png` shows popup text on otherwise black HEADLESS-2 (219 colors; 462,464 black pixels). | **FAIL**: root popup escapes the Mosaic viewport. |
| Popup input over ordinary client | `popup-gtk-under.py` opened that popup with `wev` on HEADLESS-2. At global `(900,190)`, GTK client log has `POPUP_POINTER_ENTER` and `POPUP_BUTTON 3`; `gtkunder-X.log` has no `wl_pointer` event. Right screenshot shows popup color `(49,50,68)` at `(100,190)` and ordinary X gray `(102,102,102)` elsewhere. | **FAIL**: popup intercepts pointer above the ordinary window. GTK-reported coordinates are widget-relative and should not be treated as toplevel surface coordinates. |
| Subsurfaces, saved transaction buffer, nested popup | Scene ownership inspected, but no dedicated client/render test completed. | **NOT TESTED**. |
| Creation/destruction | Real XDG clients were created and torn down repeatedly; no stale pixels observed in screenshots. | PARTIAL; no isolated frame-by-frame destroy test. |
| Workspace switch and reparent | Workspace changes used to place X and restore Mosaic; nested rect reparent test passed. | PARTIAL; no instrumented live tiled-view reparent event or animation transition test. |

`scene_output_damage` was instrumented with `SPIKE_DAMAGE output=<name> extent=x1,y1..x2,y2` after output bounds intersection. `damage-compositor.log` records camera clip changes from local x=400 to x=1120 and later x=480, and HEADLESS-1 damage including exposed/vacated regions and at times the full 800×600 viewport. The 4.429 s camera clip event shows HEADLESS-1 damage; later HEADLESS-2 damage also occurs during ordinary X/workspace activity, so this run does **not** isolate an output-specific frame-scheduling guarantee. Before/after screenshots showed no retained cross-output Mosaic pixels. The instrumentation does not prove optimal redraw area, frame count, popup-destroy damage or blur sampling damage. No performance number is claimed.

| Output arrangement | Rendering | Pointer / additional scope |
| --- | --- | --- |
| One 800×600 headless output | PASS at sampled visible pixels | PASS for B enter/motion/both buttons |
| Two horizontal 800×600 outputs | PASS for tiled content + ordinary X; FAIL for popup | PASS for partial/hidden tiled input and underlying X; FAIL for popup click |
| Two vertically stacked outputs | PASS: output 2 image all 480,000 pixels black | NOT TESTED for pointer/Y boundary |
| Negative origin: output 1 x=-800, output 2 x=0 | PASS: output 2 image all black | NOT TESTED for pointer |
| Output 2 scale 1.25 | PASS: output 2 screenshot all black | NOT TESTED for pointer/fractional-edge rounding |
| Output 2 rotated 90 degrees | PASS: 600×800 output 2 screenshot all black | NOT TESTED for pointer/transform edge rounding |
| Partly visible cell | PASS at sampled pixels | PASS at tested visible/hidden points |
| Fully hidden cell | PASS at sampled empty-output pixels | PASS at tested hidden point |

### Packaging feasibility and alternatives revisited

A **private shared-library run worked** with `LD_LIBRARY_PATH` confined to the headless subprocess; `readelf -d` showed `DT_NEEDED libscenefx-0.5.so` and a temporary build `RUNPATH`. That is a laboratory setup only. Installing a private `.so` would require an additional package-owned file and a robust `$ORIGIN`-relative lookup path; a same-SONAME library plus wlroots' overlapping scene symbols requires exact versioned ABI review and risks accidental interposition. It must never replace `/usr/lib/libscenefx-0.5.so` or `/usr/bin/sway`.

A **static example was actually built and run**: SceneFX with Meson `-Ddefault_library=static`, then the same private Mosaic source against `scenefx-static-build/meson-uninstalled`. `mosaic-static-build/sway/swayfx-mosaic` started headlessly and passed the two-output sampled pixel test; `static2-right-empty.png` is black, while `static2-right-before.png` and `static2-right-after.png` retain X's magenta at the three sampled coordinates above. `readelf -d` has **no** `DT_NEEDED libscenefx-0.5.so` and still has `DT_NEEDED libwlroots-0.20.so`. Thus only `/usr/bin/swayfx-mosaic` could remain the installed *application* artifact for this prototype, subject to ordinary dependency/notice files. This does not establish update safety: the SceneFX code would be embedded, its security fixes require a Mosaic rebuild, and exported/interposed `wlr_scene_*` symbols plus wlroots version changes need a full ABI/rebase test. SceneFX's MIT license text permits modification and distribution with copyright/permission notice preservation; package/legal review of the complete linked artifact is still required.

| Distribution route | Feasibility and impact |
| --- | --- |
| Generic primitive accepted upstream SceneFX | Best maintenance direction if API/ABI and popup owner behavior are designed with maintainers. Mosaic could use an ordinary versioned SceneFX dependency after adoption. Timing/acceptance unknown. |
| Privately packaged SceneFX `.so` beside Mosaic | Technically demonstrated only as a process-local headless lookup. Adds an application-private library file, symbol/SONAME/runpath and security-update burden; no architecture approval. |
| Bundled/static SceneFX in Mosaic binary | Built and headlessly run; avoids a second installed SceneFX file and system replacement. Duplicate scene symbols, wlroots ABI, license notices, reproducible build, security updates and upstream rebases remain open. No production authorization. |
| Second system SceneFX package or replacement of system libraries | Violates the coexistence architecture and risks ordinary SwayFX updates. Rejected as default. |

Option A remains the strongest **technical primitive** for tiled descendants, but the bare tiling-tree organization demonstrably fails popups. A bounded next design could attach an owner-derived clip to each Mosaic popup root and inherit it through nested popups, updating it on camera/workspace/output changes while leaving floating/fullscreen/standard-layout popup behavior untouched. That is a **proposal**, not a tested solution. Option B still avoids a dependency change but must track every buffer/rect/effect/saved-buffer/popup and input path, with greater SwayFX delta and future-row multiplication. Option C could constrain output rendering but still needs owner-aware hit traversal and popup association; it risks broader renderer/damage/direct-scanout maintenance. Neither B nor C was implemented here. An upstream SceneFX generic primitive plus narrow Mosaic popup ownership handling is the recommended next experiment, followed by a packaging/ABI decision; do not begin production STEP20C on this evidence.

This primitive's local-tree API is independent of `rows[0]`. Future row trees can each carry their own viewport clip and camera position. The temporary compositor wiring uses Row 0 because STEP20B has only that runtime row; STEP20D, final cell width, bindings, camera animation/easing and oversized-cell focus policy remain open.
