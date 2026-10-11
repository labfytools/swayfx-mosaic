# Known limitations

This document describes the development tree at the documentation foundation pass. `EXPERIMENTAL` means implemented but incompletely validated; `PLANNED` means absent from runtime; `NOT YET SUPPORTED` means it must not be presented as ready for general use.

| Area | Status | Practical implication |
| --- | --- | --- |
| Adjacent-output viewport clipping | NOT YET SUPPORTED | A wider row may render beyond its workspace/output boundary on another output; pointer behavior needs matching validation. |
| Multiple runtime rows | PLANNED | Model helpers/tests exist, but only Row 0 is wired into the Sway tree, arrangement, scene, and input. |
| Camera animation | PLANNED | Camera movement is immediate; transaction-safe timing/curve is open. |
| Cell sizing and grouped containers | EXPERIMENTAL | The 640 px minimum is temporary; nested groups remain one cell. Final sizing/reflow policy is TBD. |
| Resize and output migration | EXPERIMENTAL | Scroll is clamped after arrangement, but these transitions need broader headless validation. |
| Floating, fullscreen, scratchpad edge cases | EXPERIMENTAL | Basic transitions are tested; long-running and multi-output combinations are not qualified. |
| Session V2 Mosaic restore | PLANNED | Mosaic state is not durably restored by Session V2. |
| QuickShell Mosaic visualization | PLANNED | No Mosaic-specific QuickShell display is supplied here. |
| Daily-driver deployment | NOT YET SUPPORTED | Build and headless evidence do not amount to a validated live session. |
| Forward port to a later SwayFX release | PLANNED | The patch is pinned to SwayFX 0.6; a new release requires manual review and validation. |
| Very wide logical coordinates | NOT YET SUPPORTED | Scene positions use bounded integer coordinates; extremely wide canvases are not qualified. |

The [STEP20C viewport proposal](design/STEP20C_VIEWPORT_DESIGN.md) identifies an additional **design feasibility blocker**: installed SceneFX 0.5 exposes no generic scene-tree clip. Its proposed Mosaic-only projection requires a disposable headless proof that all relevant nodes, popups, damage and pointer hits respect one viewport boundary. The proposal does not change any current support status.

The later [popup ownership probe](design/STEP20C_POPUP_OWNERSHIP_PROBE.md) is **PARTIALLY_FEASIBLE**. A private owner-derived root-popup clip kept tested root and nested GTK popup pixels and pointer hits inside the Mosaic viewport on two horizontal headless outputs. Valid-serial grabs and fully hidden owners were untested in that probe; other output arrangements, complete damage and effects also remained unqualified. This does not change the current **NOT YET SUPPORTED** multi-output status.

The [valid-grab and hidden-owner follow-up](design/STEP20C_VALID_GRAB_HIDDEN_OWNER_PROBE.md) is also **PARTIALLY_FEASIBLE**. A genuine pointer-button serial produced an interactive grabbed XDG popup in unmodified SwayFX, private standard layout and private Mosaic. The previous owner-derived viewport clip leaked popup pixels and button hits when the owner was fully hidden. A further disposable owner-visibility guard removed that sampled leak while the popup stayed mapped and returned with the camera. This earlier probe did not qualify nested valid grabs; the separate nested-grab probe below covers only a sampled horizontal matrix. Other output arrangements, transaction-generation consistency, complete damage/effect coverage and ABI/package maintenance remain unqualified. Multi-output Mosaic is still **NOT YET SUPPORTED**.

The [retained source fixture](../tooling/probes/step20c-valid-grab/README.md) permits bounded replay; it does not close these qualification gaps.

The [nested valid-grab probe](design/STEP20C_NESTED_VALID_GRAB_PROBE.md) is
**FEASIBLE for its sampled matrix only**. A separate client used real pointer
button serials to grab A and then B as A's XDG child. In the disposable
guarded compositor, both levels were visible and interactive inside the
Mosaic viewport, absent at sampled pixels and hits beyond it, and suppressed
while their tiled owner was fully hidden; the mapped surfaces returned with
the camera. Closing B left A interactive, and outside clicks dismissed B
then A. Control and private `splith` retained ordinary sampled behavior.
Other output geometries, migration/resize, transaction generations, complete
damage/effects and dependency/ABI maintenance remain **NOT TESTED**. Adjacent
output Mosaic remains **NOT YET SUPPORTED** in production.

The [isolated feasibility probe](design/STEP20C_FEASIBILITY_PROBE.md) is **PARTIALLY FEASIBLE**, not a release qualification. On two horizontal headless outputs, real Mosaic content leaked visually into an empty adjacent output; the disposable candidate also delivered pointer enter from a partly visible client outside its viewport. Negative-origin, scaled and rotated arrangements showed visual leakage too. Popups, effects, saved buffers, vertical Y-crossing behavior, pointer behavior in those additional arrangements and complete damage correctness remain unqualified. Multi-output Mosaic remains **NOT YET SUPPORTED**.

The later [SceneFX subtree clipping spike](design/STEP20C_SCENEFX_CLIPPING_SPIKE.md) is also **PARTIALLY FEASIBLE**. Its private inherited tree clip stopped tested tiled pixels and pointer hits from crossing the output boundary, including a fully hidden cell, but a real GTK XDG popup rendered and received input on the neighboring output because its scene tree lives in the global popup layer. Dedicated subsurface, saved-buffer, nested-popup and complete effect/damage validation remain open. The spike changed no production library or compositor source; multi-output Mosaic remains **NOT YET SUPPORTED**.

These limits are reflected in [UX](UX.md), [architecture](ARCHITECTURE.md), and [roadmap](ROADMAP.md). A future step must update those contracts before claiming support.
