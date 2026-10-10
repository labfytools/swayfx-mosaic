# Roadmap

## STEP20A — compositor foundation

Status: implemented.

- identify exact SwayFX baseline;
- native Mosaic layout enum/parser;
- workspace-local state;
- real tiled containers;
- insertion/removal/focus invariants;
- IPC exposure;
- isolated build and headless tests;
- package staging without replacing SwayFX.

See [STEP20A.md](STEP20A.md).

## STEP20B — first scrollable row

Status: experimental implementation present in the development tree.

- single logical row wider than the viewport;
- workspace-local standard ↔ Mosaic toggle;
- logical `scroll_x`;
- scene translation;
- focus visibility;
- headless rendering/IPC validation;
- package patch export.

See [STEP20B.md](STEP20B.md).

## STEP20C — viewport correctness

Planned.

- robust clipping at workspace/output boundaries;
- multi-output validation;
- resize/output migration tests;
- pointer/hit-testing validation;
- camera animation without transaction divergence.

## STEP20D — multi-row Spatial Canvas

Planned.

- multiple native rows;
- active-row navigation;
- row-local scroll/focus memory;
- move/reorder within a row;
- move containers between rows;
- deterministic reflow.

Target interaction model:

```text
Super + arrows          navigation
Super + Ctrl + ...      reorder/modify within row
Super + Shift + Up/Down move between rows
```

Exact bindings remain subject to validation before they become permanent.

## STEP20E — Session V2 persistence

Planned.

Persist and restore:
- Mosaic layout state;
- ordered rows;
- active row;
- scroll positions;
- row focus;
- stable window identities.

The compositor remains the runtime source of truth.

## STEP20F — QuickShell integration

Planned.

- expose Mosaic state visually;
- adapt workspace overview;
- optional layout state indication;
- no duplicate Mosaic state in QML.

## STEP20G — packaging and daily use

Planned.

- final Arch package;
- dedicated desktop/session entry if useful;
- standard SwayFX fallback preserved;
- update/rebase procedure proven against a newer upstream SwayFX release;
- documentation for installation, rollback and troubleshooting.
