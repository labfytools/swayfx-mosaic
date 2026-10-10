# Architecture

## Scope

Mosaic / Spatial Canvas is an additional native SwayFX layout. It is not a separate window manager model layered above IPC and it is not a QuickShell feature.

The compositor owns:
- container order;
- row membership;
- logical geometry;
- active row;
- per-row scroll position;
- per-row focus memory;
- scene translation;
- hit testing consistency.

QuickShell may display this state later, but must not duplicate or authoritatively store it.

## Logical model

```text
MosaicWorkspaceState
├── active_row
├── previous_standard_layout
└── rows[]
    ├── ordered children
    ├── scroll_x
    └── focused child
```

The first row directly borrows `workspace->tiling`, keeping the existing Sway tree authoritative.

Four concepts must remain separate:

1. logical order;
2. calculated geometry;
3. viewport/camera;
4. focus.

Changing the camera must not reorder containers. Changing focus must not change logical order.

## Layout semantics

Mosaic is opt-in per workspace through:

```text
layout mosaic
```

The bidirectional UX command is:

```text
layout toggle mosaic
```

Entering Mosaic records the current standard layout. Leaving Mosaic restores that layout for the same workspace.

Standard layouts continue to work inside `swayfx-mosaic`; changing process or restarting the compositor is not part of layout switching.

## Tiling invariants

- containers remain Sway tiled nodes;
- no overlaps in the logical tiling geometry;
- no internal holes after insertion/removal;
- insertion occurs next to the active logical container;
- deletion triggers reflow;
- a row can extend beyond the physical viewport;
- `scroll_x` is bounded to the logical row extent;
- focusing an off-screen cell may bring it into view;
- floating, fullscreen and scratchpad use normal Sway paths and are not reimplemented as Mosaic concepts.

## Scene and viewport

The logical row may be wider than the output. Mosaic therefore needs a camera transform between logical tiled geometry and visible scene coordinates.

The output viewport is not the layout itself.

STEP20B currently proves the single-row translation path. Multi-output correctness still requires explicit clipping or an equivalent SceneFX/wlroots strategy so content from one workspace viewport cannot leak onto an adjacent output.

Hit testing must remain aligned with the translated scene.

## IPC

Existing Sway IPC contracts remain primary:
- `get_tree`;
- `get_workspaces`;
- window events;
- workspace events.

A Mosaic workspace exposes `layout: "mosaic"` and may expose an additional Mosaic object describing rows, focus and scroll state.

Consumers that treat layouts as a closed enum must explicitly add Mosaic support.

## Package isolation

The normal package owns the normal compositor:

```text
swayfx → /usr/bin/sway
```

This project owns only the alternate binary and project-specific files:

```text
swayfx-mosaic → /usr/bin/swayfx-mosaic
```

No file owned by `swayfx` may be overwritten.

The package must not declare itself a replacement for SwayFX.

## Patch maintenance

The installed Mosaic build is produced from:
1. a pinned, known SwayFX upstream commit;
2. the Mosaic patch set;
3. Mosaic tests;
4. a package recipe that checks the expected upstream commit.

A new SwayFX version is never accepted implicitly. The patch must be rebased/reviewed and all standard-layout plus Mosaic tests rerun.

## Session restore

The existing external Session V2 system will eventually need to persist:
- Mosaic activation;
- ordered rows;
- row membership;
- active row;
- each row's `scroll_x`;
- each row's remembered focus;
- stable window identities.

That integration belongs to a later step and must not turn Session V2 into the runtime source of truth.
