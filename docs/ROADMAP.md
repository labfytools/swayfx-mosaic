# Roadmap

This is the canonical order of work, not proof that a feature exists. **A step is not ready for implementation until its user-visible and architectural behavior is documented in the canonical docs.** Update [UX](UX.md), [architecture](ARCHITECTURE.md), and the relevant packaging/upstream documents before changing behavior. Record validation and limitations when the step closes.

| Step | State | Goal |
| --- | --- | --- |
| STEP20A | DONE | Native compositor foundation |
| STEP20B | EXPERIMENTAL | First scrollable runtime row |
| STEP20C | NEXT | Viewport and multi-output correctness |
| STEP20D | PLANNED | Multiple runtime rows |
| STEP20E | PLANNED | Session V2 persistence |
| STEP20F | PLANNED | QuickShell visualization |
| STEP20G | PLANNED | Package and daily-use qualification |

## STEP20A — native foundation · DONE

**Deliverables:** native layout enum/parser, workspace-local state, real tiled Row 0, insertion/removal/focus model, IPC exposure, isolated build/staging, headless tests. **Exit evidence:** [historical report](STEP20A.md) and current source/tests. **Documentation before implementation:** original architecture, upstream base, and package coexistence contract; current canonical versions are [Architecture](ARCHITECTURE.md), [Upstream](UPSTREAM.md), and [Packaging](PACKAGING.md).

## STEP20B — first scrollable row · EXPERIMENTAL

**Deliverables:** logical horizontal geometry, bounded `scroll_x`, scene translation, focus visibility, workspace-local standard-layout toggle, headless visual evidence, patch export. **Exit evidence:** [historical report](STEP20B.md). The single-row proof is present, but it is not a general-use viewport guarantee. **Documentation before further implementation:** [UX](UX.md) and [Architecture](ARCHITECTURE.md) must keep the temporary sizing and scene boundaries explicit.

## STEP20C — viewport correctness · NEXT

**Goal:** make the single-row viewport correct at workspace and output boundaries. **Planned deliverables:** clipping or an equivalent rendering strategy, matching hit testing, adjacent-output tests, resize/migration tests, and transaction-safe camera animation. **Exit criteria:** no cross-output visual/input leakage in the tested scenarios; camera and IPC remain consistent across transactions; standard layouts still pass. **Docs first:** review the [STEP20C viewport proposal](design/STEP20C_VIEWPORT_DESIGN.md), prove its clipping/input feasibility on installed SceneFX, then settle the resulting contract in Architecture and UX and update Known Limitations before implementation. The proposal is not implementation approval. This documentation pass does not implement STEP20C.

## STEP20D — multi-row Spatial Canvas · PLANNED

**Goal:** connect rows to runtime tree, transactions, scene, input, and IPC. **Planned deliverables:** active-row navigation, row-local scroll/focus, deterministic insertion/reflow, in-row reorder, and between-row movement. **Exit criteria:** real tiled containers preserve identity and order across row changes; focus and camera restore correctly; headless multi-row tests pass. **Docs first:** settle exact interactions and row invariants in UX and Architecture. Unset key combinations remain TBD.

## STEP20E — Session V2 persistence · PLANNED

**Goal:** restore Mosaic workspaces across sessions without creating a second runtime authority. **Planned deliverables:** durable activation, row order/membership, active row, scroll, focus, stable identities, and restart tests. **Exit criteria:** deterministic restore and safe fallback for missing windows/older snapshots. **Docs first:** specify persistence identity, versioning, failure handling, and ownership in Architecture and UX.

## STEP20F — QuickShell visualization · PLANNED

**Goal:** expose compositor-owned Mosaic state in the desktop UI. **Planned deliverables:** workspace/row view and optional layout indication without duplicate QML layout state. **Exit criteria:** UI reflects IPC state and cannot contradict the compositor. **Docs first:** specify IPC consumer behavior and UI interactions in Architecture and UX.

## STEP20G — package and daily-use qualification · PLANNED

**Goal:** publish a validated optional session while preserving standard SwayFX fallback. **Planned deliverables:** final Arch package, optional distinct session entry, install/rollback instructions, and a forward port proven against a newer SwayFX release. **Exit criteria:** package file ownership and coexistence verified, release build and headless/live qualification recorded, standard SwayFX updates remain independent. **Docs first:** update Packaging, Upstream, Development, UX, and Known Limitations with the intended release contract.
