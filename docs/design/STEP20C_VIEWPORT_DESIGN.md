# STEP20C viewport architecture — design proposal

**Status: PROPOSED, documentation only.** Baseline: project commit `eeba4b7ac72866f9e48e6f002f39eb962fdbdd3e`, SwayFX 0.6, installed wlroots 0.20.2 and SceneFX 0.5.0 headers. No STEP20C behavior exists yet. This proposal preserves [Architecture](../ARCHITECTURE.md), [UX](../UX.md), [Packaging](../PACKAGING.md), and the [historical STEP20B evidence](../STEP20B.md). It does **not** freeze the final cell width, key bindings, or animation curve.

## 1. Design status and feasibility gate

**Recommendation: PROPOSED Approach C, a Mosaic-owned viewport projection over the existing real Sway scene nodes, with one shared viewport predicate for rendering and input.** The compositor remains the sole authority for order, geometry, camera, focus, and input. Standard layouts and the standard SwayFX binary must retain their existing paths.

**Critical unresolved feasibility:** SceneFX 0.5 has no public generic `wlr_scene_tree` clip API. It offers node-specific clip/crop operations, but their combined behavior for all Mosaic node types, damage, and hit testing has not been demonstrated. In particular, global popup scene trees and effect/saved-buffer nodes need a focused disposable headless probe before production implementation. Until that proof passes, this is a recommended architecture, **not an implementation-ready clipping contract**. If the probe fails, revisit the architecture; do not silently substitute an output-only mask or claim multi-output safety.

## 2. Existing implementation and exact call paths

The paths below were checked in this repository. References identify current functions; the change column describes **proposed future work**, not a present API.

| Source/function | Current responsibility | Required STEP20C change | Risk |
| --- | --- | --- | --- |
| `sway/tree/arrange.c:apply_mosaic_layout` | Sets Row 0 pending logical rectangles, temporary 640 px minimum, clamps scroll | Produce/retain computed row extent and viewport geometry independently of sizing policy | Overflow, changing width while scrolled |
| `sway/tree/arrange.c:arrange_children`, `arrange_workspace`, `arrange_output` | Routes Mosaic only for workspace tiling; sets workspace origin from `output->lx/ly + usable_area`; handles fullscreen/floating | Recompute viewport on usable-area/output change and bind it to workspace | Stale origin or camera after migration |
| `sway/tree/workspace.c:workspace_get_box`, `workspace_move_to_output` | Returns post-gap workspace rectangle; moves workspace between outputs | Rebind/reclamp viewport and cancel/rebase animation during move | Old-output scene/input leak |
| `sway/config/output.c:output_update_position` | Copies output layout box into `lx/ly/width/height` | Trigger viewport recomputation through existing arrangement path | Negative origins, transforms, scale |
| `sway/tree/mosaic.c:mosaic_row_max_scroll`, `mosaic_row_clamp_scroll` | Bounds row camera using count, width, gap and temporary cell width | Bound from computed logical row extent instead of duplicating sizing math | Divergent geometry/camera limit |
| `sway/commands/layout.c:cmd_layout` | `layout mosaic scroll`, toggle, state creation and arrangement | Send camera target/reveal through a single Mosaic path; preserve restore target | Target visible in IPC before scene catches up |
| `sway/input/seat.c:seat_set_workspace_focus` | Saves Row 0 focus and minimally reveals via pending rectangles | Use viewport-aware reveal for oversized/partial cells; defer visual update consistently | Reentrant arrange, focus/scene mismatch |
| `sway/desktop/transaction.c:transaction_commit_dirty`, `transaction_commit_pending`, `transaction_progress`, `transaction_apply` | Copies pending state, waits for client commits or timeout, applies current, arranges scene | Define camera target snapshot/commit boundary and invalidation on transitions | Mixed pending geometry and current scene |
| `sway/desktop/transaction.c:workspace_tiling_scene_x`, `arrange_output`, `arrange_root` | Places tiling tree at area/gap origin minus Row 0 `scroll_x`; reparents workspace/output layers | Apply visual camera and viewport projection only for active Mosaic tiling; clear it on standard/fullscreen paths | Cross-output leakage or faded old workspace |
| `sway/desktop/transaction.c:arrange_workspace_floating`, `arrange_fullscreen`, `disable_workspace`, `arrange_popups` | Floating/fullscreen/scratchpad and global popup scene handling | Preserve ordinary modes; associate Mosaic-origin popups with viewport policy | Popup bypass of clip; stale nodes |
| `sway/desktop/output.c:output_repaint_timer_handler`, `output_configure_scene`, `handle_frame` | Configures effects, calls `wlr_scene_output_build_state`, commits output and sends frame done | Verify projected clip/damage per output; avoid changing global render path for standard layouts | Redraw cost, blur/shadow spill |
| `sway/input/cursor.c:node_at_coords`, `pointer_motion`, `dispatch_cursor_button` | Walks global scene layers with `wlr_scene_node_at`; output lookup is fallback after scene hit | Reject Mosaic-owned hits outside their viewport before delivery; preserve `sx/sy` from real scene hit | Invisible target or wrong client coordinates |
| `sway/input/seatop_move_tiling.c`, `seatop_resize_tiling.c` | Use pointer/global coordinates and Sway boxes during drag/resize | Validate viewport boundary and cancellation/migration semantics | Drag target outside visible region |
| `sway/desktop/xdg_shell.c:popup_create`, `popup_unconstrain`; `transaction.c:arrange_popups` | Creates global popup scene tree, unconstrains to output, positions relative to view | Scope Mosaic-origin popup visibility/input to its owner viewport or explicitly reposition it inside | Popup can escape tiling subtree |
| `sway/ipc-json.c:ipc_json_describe_workspace` | Emits `layout: "mosaic"` and `{active_row, rows:[{children, scroll_x, focused}]}` | Keep stable target semantics; avoid publishing transient visual offset as logical order | Strict consumers, inconsistent snapshots |
| `include/sway/tree/mosaic.h` | Owns Row 0 scroll/focus and model-only future rows | Specify target/visual camera and viewport lifetime if implementation adds state | Dangling output pointer or duplicate authority |

Current high-level paths:

```text
IPC scroll / keyboard focus -> row scroll_x -> arrange_workspace -> node_set_dirty
  -> eventual transaction_commit_dirty -> pending transaction -> client commit or timeout
  -> transaction_apply -> arrange_root -> workspace_tiling_scene_x
  -> wlr_scene_node_set_position -> SceneFX output build/commit

Pointer global lx/ly -> node_at_coords -> global scene-layer walk
  -> wlr_scene_node_at -> surface/node and sx/sy -> seat operation
```

`scroll_x` is a workspace-row model value, **not** part of copied Sway transaction state today. `cmd_layout` and focus can update it before a transaction applies; `get_tree` reads current workspace model values while ordinary rectangles may represent another transaction phase. The existing design must therefore avoid claiming that every intermediate IPC snapshot is atomic. The proposal below makes the target explicit and aligns presented scene/input with a committed geometry generation.

## 3. Coordinate spaces and transform

| Space | Meaning and owner | Used by |
| --- | --- | --- |
| Row logical | Ordered cell rectangles and extent relative to a row origin, independent of camera | Mosaic layout, clamp, reveal |
| Workspace layout | `pending`/`current` container boxes in Sway layout coordinates; `workspace_get_box` includes output origin and gaps | Arrangement, Sway transactions, IPC rectangles |
| Scene parent-local | Integer node positions relative to ancestors; output layer at `output->lx/ly`, workspace tiling layer translated by camera | `wlr_scene_node_set_position`, effects |
| Scene/root global | Sum of node transforms in output-layout logical coordinates | `wlr_scene_node_coords`, global scene hit testing |
| Output-local logical | Global coordinate minus output layout origin, before buffer scale/transform | Output viewport intersection, output IPC conversion |
| Output-buffer pixels | Output-local logical geometry transformed/scaled/rounded by wlroots/SceneFX | `wlr_scene_output_build_state`, screenshots |
| Pointer global | `wlr_cursor` layout coordinates; surface-local `sx/sy` comes from scene hit | `node_at_coords`, seat operations |

For a simple untransformed row, `screen_x = logical_x - visual_camera_x + viewport_origin_x`. Here `logical_x` must be row-relative; `viewport_origin_x` is the post-gap workspace origin in global logical coordinates. In current code, container `pending.x` is already workspace/global logical, and `workspace_tiling_scene_x` subtracts `scroll_x` from the workspace tiling scene parent. **Do not subtract the output origin or camera twice.** Parent-local positions, nested trees, output negative positions, and gap offsets must be checked with `wlr_scene_node_coords`/the actual scene hierarchy. Output scale and rotation belong to the output-render conversion, not to `scroll_x`; clipping uses integer logical boxes with conservative edge rounding and test evidence at buffer pixels. Fractional scale must not be implemented by scaling camera pixels manually.

The viewport is the **workspace's tiled usable rectangle after gaps**, intersected with its active output logical box. The physical output box is a safety boundary; it is not the logical canvas extent. Scene projection and hit testing must use the same committed viewport box and owner workspace/output identity.

## 4. Clipping alternatives on installed APIs

Installed `scenefx/types/wlr_scene.h` provides `wlr_scene_node_set_position`, `wlr_scene_node_at`, `wlr_scene_subsurface_tree_set_clip` (subsurface descendants in root-surface coordinates), `wlr_scene_rect_set_clipped_region`, shadow/blur clipped-region calls, and `wlr_scene_buffer_set_source_box`. The latter crops a buffer's source; it is **not** a general workspace clip. `wlr_scene_output_build_state` options expose color transform/swapchain/timer, **no per-subtree viewport filter**. There is no declared generic tree clip. These are header observations, not a proof of all rendering behavior.

| Approach | API feasibility | Render/input correctness | Transaction/damage/performance | STEP20D/rebase/standard-layout impact |
| --- | --- | --- | --- | --- |
| **A. Generic scene-tree clip** | **Unsupported as stated** on SceneFX 0.5; no public `wlr_scene_tree` clip | Would be attractive if available, but cannot be assumed | Would rely on dependency behavior not present | Low conceptual cost, unavailable without dependency change |
| **B. Output-render restriction** | Requires custom renderer traversal or SceneFX extension; build-state options do not offer it | Could clip visual output; global `node_at_coords` still needs separate input policy | High risk to damage, effects, scanout, frame callbacks and output-specific work | Broad SceneFX/upstream maintenance; risk to standard layouts |
| **C. Mosaic viewport projection** | Node-specific public clip/crop APIs exist; complete coverage remains unproven | Proposed shared viewport predicate plus explicit scene-node projection and input guard | Medium/high compositor complexity; must test damage and transitions | Can stay Mosaic-scoped and generalize from one row to per-row regions; no standard path change intended |

**Recommend C, PROPOSED.** Keep the existing real container scene ownership, add a workspace-owned viewport descriptor and a Mosaic-scoped projection of intersected content. Use the public node-specific operations where they are valid; handle decorations, shadows, blur, saved buffers, and global popups explicitly. Do not replace real containers with copies or a second layout tree. The same committed viewport descriptor guards Mosaic scene hits. When a required node type cannot be projected safely, fail the feasibility gate and revisit B or a deliberately versioned SceneFX extension; never ship visual-only clipping.

**Focused feasibility investigation required before implementation:** in a disposable headless build/instance, clip one partly visible XDG surface including subsurfaces and popup, border, shadow/blur, and saved transaction buffer; inspect both outputs and `wlr_scene_node_at` behavior at every boundary. Instrument damage/frame callbacks. Establish that any per-node crop preserves client-local input coordinates. This probe is not authorized by this documentation-only pass.

## 5. Viewport ownership and hit testing

**PROPOSED:** a Mosaic viewport descriptor belongs to the workspace's Mosaic state. It references no output permanently: resolve the current `workspace->output` and its usable/output boxes when arranging and applying scene state. An output disconnect invalidates the descriptor and stops camera animation before scene nodes are reused. Destruction clears projection state before destroying workspace scene nodes. Future rows can each supply a region, while a workspace-level owner prevents a row from drawing on another output.

For Mosaic tiled nodes, visual and interactive regions are the intersection of node content with the committed viewport. An entirely hidden node must be absent from visible composition and ineligible for pointer focus. A partly visible node can receive left/right click, hover, and drag only within its visible part; `sx/sy` are derived from the real scene hit, without inventing translated client coordinates. The input guard identifies the hit's owner by walking scene descriptors/ancestors, checks the current output from `wlr_output_layout_output_at`, active workspace, committed viewport and visible geometry, then rejects an out-of-viewport Mosaic hit. It must continue the normal scene-layer search below rejected content where needed, rather than return a hidden surface or swallow an unrelated layer-shell hit. `wlr_scene_node_at` returns only the topmost hit; the inspected API does not provide a generic "next hit" iterator. A scoped traversal or scene organization that avoids rejected hits is therefore another required feasibility proof, not a trivial post-filter. A bare fallback to `output_get_active_workspace` is insufficient because `node_at_coords` tests scene layers **before** output lookup.

Global popups are not children of `workspace->layers.tiling`; `arrange_popups` places them in a root popup layer. **PROPOSED:** a popup owned by a Mosaic tiled view is constrained to the owner's active output/viewport, including input, while ordinary floating/fullscreen popups keep Sway behavior. Popup reposition/unconstrain and nested popup edges require the feasibility probe. If exact clipping of popups cannot be demonstrated, multi-output support remains blocked. Pointer crossing outputs must resolve to the actually visible surface on the destination output.

Tiling drag, move indicators, resize, hover and touch/tablet paths that use `node_at_coords` or global scene nodes need the same boundary policy. An in-progress drag may cross outputs according to ordinary Sway semantics, but its **source** cannot be an invisible Mosaic hit and its drop target cannot be inferred from a clipped-away cell. Pointer constraints and popups must be rechecked when camera/output changes. No input guard should alter ordinary floating, fullscreen, scratchpad or standard-layout hit testing.

## 6. Focus and reveal

| Policy | Benefit | Cost |
| --- | --- | --- |
| Minimal movement | Stable spatial context; no motion for fully visible cell | Large cells cannot be made wholly visible |
| Center focused cell | Predictable focus position | Repeated focus causes unnecessary camera motion |
| Snap to cell/viewport | Easy coarse navigation | Jarring motion and partial visibility at odd widths |

**Recommend minimal movement, PROPOSED.** If a cell fits, reveal just enough to make it wholly visible; if already fully visible, keep camera target unchanged. If a cell is wider than the viewport, reveal its focused/entry edge or keep the visible portion stable, then allow explicit camera scroll within it; do not oscillate trying to satisfy an impossible full-visibility condition. Clamp to `[0, row_extent - viewport_width]`. Focus changes never alter row order. Tests must verify both directions and the oversized-cell rule before UX acceptance.

## 7. Transactions, camera target and animation

**PROPOSED authoritative split:** logical row order/focus and `target_scroll_x` live in workspace Mosaic state. A committed viewport/geometry generation plus `presented_scroll_x` describes what the scene and input currently show. During an in-flight Sway transaction, pending geometry may change, but the presented scene and input remain paired to the last applied geometry; target can be queued or retargeted. On `transaction_apply`, recompute the viewport from current output/current geometry, clamp target, update projection, then begin/retarget visual camera movement. IPC `scroll_x` remains the **logical target**; a future optional presented offset would need explicit naming and compatibility review. Do not serialize an interpolated pixel position as logical order.

The existing `transaction_progress` applies after client readiness or timeout and calls `arrange_root` then `cursor_rebase_all`; a timeout still applies a transaction. A failed/late client commit must not mutate order or row focus. When queued geometry is superseded, derive the next target from the latest valid logical state and do not animate toward a destroyed node. On empty/disabled output, suspend presentation and retain only valid workspace-local logical state until an output returns. The transaction generation/viewport descriptor must be an implementation detail, not another durable model.

```text
Normal camera move:
IPC delta -> validate/clamp target -> no order change -> dirty/commit path
-> scene generation applies -> projection updates -> visual camera reaches target
-> cursor rebase; IPC continues to describe target

Focus reveal:
seat focus -> remember real tiled cell -> calculate minimal target from pending geometry
-> transaction applies current geometry -> re-evaluate/clamp target
-> project scene and input together -> animate or jump per motion setting

Output resize/migration:
output config/move -> invalidate old viewport and stop/retarget animation
-> arrange pending geometry and new output box -> transaction applies
-> clamp target to new row extent -> project on new output -> rebase pointer

Standard -> Mosaic -> Standard:
remember standard layout -> create/reuse Mosaic state -> arrange real nodes
-> apply Mosaic viewport/projection -> toggle back -> clear Mosaic projection
-> restore standard layout on same workspace -> preserve node identities
```

### Animation approaches

| Approach | Assessment |
| --- | --- |
| Move scene tree directly on a timer | Simple but risks bypassing transaction and input/projection updates |
| Store visual camera separately from target | Clear authority; every frame can derive scene translation, clip and hit boundary from one presented state |
| Use existing SwayFX animation manager | Reuses scheduling/easing infrastructure, but needs a Mosaic-specific state callback and lifecycle/cancel rules |

**Recommend a separate visual camera value driven by the existing animation manager, PROPOSED.** Keep target and presented offset distinct. At each tick, interpolate from current presented position toward the latest valid target; update scene translation, projected clip/input region and damage together; schedule only affected output frames. Rapid repeated focus/navigation retargets from the **currently presented** position, never from the stale original start. Cancel/snap on layout exit, workspace destruction, output loss, fullscreen entry, or geometry generation change that invalidates the path. Recompute from current geometry on output resize/migration. Avoid extra redraws when target equals presented or workspace is inactive. Measure CPU/GPU/damage behavior before choosing a duration or easing. **Reduced-motion proposal:** snap immediately when compositor animation is disabled or a future explicit reduced-motion setting is active. Duration and curve remain **TBD**, not permanent constants.

## 8. Output isolation and transitions

The output box and workspace viewport are distinct. The projection uses their intersection so a row on eDP-1 cannot paint or hit HDMI-A-1. Horizontal adjacency, vertical stacking and negative global origins share the same logical-box intersection rule. Differing scales/transforms are handled only after verifying SceneFX conversion from global logical coordinates to buffer pixels; tests must include boundary pixels and transformed input. These scenarios are **target acceptance cases**, not currently supported.

On workspace switch, old workspace fade animation may keep its tiling scene enabled in `transaction.c:arrange_output`; its Mosaic projection must remain bound to the old output viewport until disabled. On output move, bind to the new output only after the transaction has consistent current geometry; never display old-output content on the destination by stale projection. On disconnect, disable visible projection and animation; on reconnect, recompute from the new output. Empty workspace has extent zero and camera zero. One-cell workspace cannot scroll unless that cell is wider than the viewport. Closing the focused/first/last cell clears stale focus, reflows and reclamps. Inserting while scrolled keeps logical insertion after active cell and reveals only as focus policy requires. Resizing at the end clamps the target and presented position to the new range.

Fullscreen disables Mosaic tiling projection while the standard fullscreen tree is active, then restores/reclamps it on exit. Floating and scratchpad nodes remain in their ordinary Sway/root scene paths; converting floating to tiled re-enters Row 0 through normal tree mutation. Layout toggle preserves identities and workspace-local previous layout. None of these paths may leave a hidden interactive tiling node.

## 9. Cell sizing and future rows

STEP20C needs **computed cell rectangles**, their checked logical row extent, the viewport rectangle, and a camera target. It must not read a hard-coded cell width to clip or hit-test. `mosaic_row_max_scroll` currently repeats the temporary sizing calculation; STEP20C should derive the clamp from the same arranged geometry/extent used for scene placement. Future sizing discussions may compare equal-width cells, content-informed widths, and user-set width classes; no choice is frozen here. A policy change should alter layout geometry, not the clipping architecture.

STEP20C projects Row 0 only. STEP20D may supply separate row geometry/regions and `scroll_x` values (for example 1200, 400, 0), plus each row's order and focus memory. The viewport owner should accept row-scoped regions/camera values rather than embed `rows[0]` in the clip primitive. STEP20D, not this step, wires additional rows into Sway runtime tree, transactions, input and IPC.

## 10. Headless test design

Use isolated headless compositor instances, temporary config/runtime directories and separate IPC sockets. Place colored test clients with identifiable IDs; capture each output independently (for example with `grim`), compare expected pixel regions, query `get_tree`, and inject pointer events through a headless input device/test harness. **Screenshots prove pixels, not click routing.** Log target surface/seat focus and client-received button/hover coordinates. Assertions use both IPC and observed input. No test runs against the normal desktop session.

In the matrix, `IDs` means Sway node IDs and ordered `mosaic.rows[0].children`; `hit` means observed client/seat target, including button side and local coordinates. Each case also checks no compositor crash and no unexpected window migration.

| Scenario and initial state | Action | Expected IPC | Expected rendering | Expected hit result / regression condition |
| --- | --- | --- | --- | --- |
| One output, 4 cells | Scroll to middle | IDs/order fixed; bounded target | Only viewport intersection appears | Hidden side has no hit; any spill fails |
| Two horizontal outputs: Mosaic left, standard right | Scroll past left edge of right output | Both workspace IDs fixed | Right output shows only its workspace | Click/right-click right output reaches right surface; Mosaic hit fails |
| Two vertically stacked outputs | Scroll and move pointer across boundary | Output/workspace ownership fixed | No vertical spill, including shadows/popups | Destination hit correct; hidden Mosaic target fails |
| Negative output origin | Put Mosaic output left/up of origin, scroll | Same IDs and valid target | Clip follows negative box | Correct target across zero boundary; offset error fails |
| Different scales and rotated output | Scroll across boundary | Logical target unchanged by scale | Boundary pixels confined after transform | Hit maps to visible client-local coordinates; off-by-one fails |
| Partly visible cell, popup and border | Open context menu; left/right click visible and clipped sides | Same cell ID; focus as expected | Visible fraction only; popup bounded/repositioned | Only visible fraction/menu receives input; wrong `sx/sy` fails |
| Entirely hidden cell | Move/click/hover over where its translated geometry crosses neighbor | Same focus unless explicit keyboard action | No pixels/effects on neighbor | No hover/button/focus to hidden client; any hit fails |
| Scroll left/right repeatedly | Explicit scroll commands | IDs/order/geometry fixed; target clamped | Camera changes only | Visible target matches frame; reordered ID fails |
| Focus off-screen, then fully visible cell | Directional focus | Focused ID and target update only when needed | First reveals; second does not pan | Keyboard focus correct; needless camera move fails |
| Rapid camera moves | Alternate focus/scroll before animation ends | Latest target wins | Continuous path, final frame at target | Hits follow presented scene; stale final position fails |
| Resize output while at row end | Change headless mode/usable area | Target bounded to new extent | No void/excess content | Boundary hit correct; overscroll fails |
| Move workspace to another output, then hotplug | IPC workspace move/disconnect/reconnect | Same workspace/container IDs | Only new active output shows it | No old-output hit; stale viewport fails |
| `splith/tabbed/stacking -> mosaic -> prior` | Toggle each populated workspace | Same IDs/order; previous layout restored | Standard scene returns without Mosaic clip | Standard hit path unchanged; identity loss fails |
| Floating/fullscreen/scratchpad | Toggle each mode while scrolled | Ordinary mode and IDs | Standard scene ownership; tiling hidden under fullscreen | Expected mode receives input; clipped floating fails |
| Close focused/first/last; insert while scrolled | Close/open test clients | No stale focus ID; contiguous order | Reflow and bounded camera | New visible cell hit correct; ghost node fails |
| Client stalls during resize | Delay commit past transaction timeout | Final target/IDs coherent | No permanent mixed geometry or leak | Input follows applied scene; stuck transaction fails |
| Drag/resize at clipped edge | Tiling drag and resize from visible part | Order changes only on valid operation | Indicator bounded; no neighbor spill | Hidden edge cannot initiate drag; wrong target fails |

Automate exact pixel-color masks and event logs where possible; use screenshots for corroboration. Run standard-layout controls on the same isolated binary. Stress with long rows, many windows, rapid retargets, output hotplug, popup creation/destruction and client stalls. A single-output screenshot or IPC-only test cannot qualify multi-output correctness.

## 11. Performance and safety

A projection layer or per-node clipping can increase scene traversal, clip recomputation and scene graph depth; measure them. Camera movement damages old and new visible regions and may trigger more frequent output composition, blur, shadows and saved-buffer work. Restrict redraw to affected outputs where SceneFX permits, and verify damage rather than promising a frame rate. Long rows should not allocate one output-sized buffer per cell. Check 64-bit extent calculations before converting to SceneFX integer node positions; reject or safely bound extreme widths and non-finite camera values. Test output hotplug, negative origins, fractional scale, transforms, many logical pixels, hundreds of containers, popups and transaction timeouts. Do not compare only total process RSS to a camera-state estimate. Keep the future production patch small and reviewable; preserve standard-layout code paths and package isolation.

## 12. Implementation decomposition and acceptance

This is a **future work plan**, not authorization to edit source in this pass.

1. **Feasibility probe:** prove complete render/input behavior of node-specific clipping on installed SceneFX 0.5 with two headless outputs, partial surface, effects, saved buffer and popup. Record API behavior and damage. **Block implementation** if it fails.
2. **Geometry contract:** expose checked row extent and committed viewport intersection independently of cell sizing; define workspace ownership/lifetime and output invalidation.
3. **Scene projection:** Mosaic-only clip/crop for all relevant scene node types and output boundaries; preserve standard/floating/fullscreen paths.
4. **Input guard:** use the same committed viewport predicate in `node_at_coords` and related pointer/drag paths; test local coordinates and popup routing.
5. **Transaction/camera path:** separate target from presented camera; align scene/input with applied geometry, handle timeout/rebase/cancel.
6. **Animation:** reuse existing manager only after static clipping passes; implement retarget/reduced-motion behavior without hard-coded UX duration.
7. **Headless matrix:** qualify horizontal/vertical/negative/scaled/transformed outputs, transitions, special modes and stress; update canonical docs and limitations from evidence.

**Acceptance criteria:** no Mosaic pixels or input leak outside its viewport on qualified output arrangements; partial cells and popups have matching visible/interactive regions; target and presented camera converge without changing order; scene and IPC recover after transaction timeout/output change; standard layouts and ordinary SwayFX paths remain unaffected; tests are reproducible and report actual client input, not screenshots alone. Until feasibility and these tests pass, multi-output Mosaic remains unsupported.

## 13. Decision register

| Decision | Options | Recommendation | Status |
| --- | --- | --- | --- |
| Viewport clipping | A generic tree / B output renderer / C Mosaic projection | C, conditional on node-coverage probe | **PROPOSED; feasibility open** |
| Hit testing | Trust scene alone / separate guard | Shared committed viewport predicate and explicit input guard | **PROPOSED** |
| Focus reveal | Minimal / center / snap | Minimal; special rule for oversized cell | **PROPOSED** |
| Camera animation | Direct scene timer / separate visual state / existing manager | Separate visual value driven by existing manager | **PROPOSED** |
| Reduced motion | Animate / snap | Snap when animations disabled; explicit setting later | **PROPOSED** |
| Cell sizing | Equal/content-based/user classes | Defer final choice | **TBD** |
| Exact navigation keys, duration, curve | Multiple valid UX choices | Resolve in UX review after feasibility | **TBD** |

The only material architectural approval requested before implementation is the clipping strategy after its feasibility probe. UX review can settle motion and oversized-cell details without changing real-container ownership. This design does not authorize STEP20D or a SwayFX/SceneFX dependency fork.
