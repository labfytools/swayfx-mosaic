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

The [isolated feasibility probe](design/STEP20C_FEASIBILITY_PROBE.md) is **PARTIALLY FEASIBLE**, not a release qualification. On two horizontal headless outputs, real Mosaic content leaked visually into an empty adjacent output; the disposable candidate also delivered pointer enter from a partly visible client outside its viewport. Negative-origin, scaled and rotated arrangements showed visual leakage too. Popups, effects, saved buffers, vertical Y-crossing behavior, pointer behavior in those additional arrangements and complete damage correctness remain unqualified. Multi-output Mosaic remains **NOT YET SUPPORTED**.

These limits are reflected in [UX](UX.md), [architecture](ARCHITECTURE.md), and [roadmap](ROADMAP.md). A future step must update those contracts before claiming support.
