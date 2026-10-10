# Spatial Canvas UX contract

**Scope:** intended user experience and the current single-row implementation. `CURRENT` means present in the development tree, `EXPERIMENTAL` means present without general-use validation, `PLANNED` means not connected to runtime behavior, and `TBD` means the decision is still open.

## Mental model

```text
Workspace
└── Canvas
    ├── Row 0: ordered real tiled containers  [A][B][C][D]...
    └── Future rows: ordered real tiled containers
                         └── viewport shows only part of a row
```

Mosaic is a layout inside an ordinary Sway workspace. A row can be wider than the visible output. Logical order, container geometry, viewport position, and focus are distinct state. Moving the viewport does not reorder windows; focusing a window does not make it floating.

**CURRENT/EXPERIMENTAL:** Row 0 uses the workspace tiling list and has logical horizontal scrolling. Additional rows exist only as model helpers and tests. Their runtime tree, scene, input, and IPC behavior is **PLANNED**.

## Focus and movement

**Invariant:** Super alone never moves windows. Navigation and window movement are separate actions.

| Intended action | Desktop binding | Status |
| --- | --- | --- |
| Navigate/focus | Super + arrows | Design direction; exact mapping and row transitions TBD |
| Reorder or modify tiling within a row | Super + Ctrl + TBD | PLANNED; exact key/action mapping TBD |
| Move a container between rows | Super + Shift + Up/Down | PLANNED |

These are desktop interaction decisions, not key bindings installed by this package. Existing Sway directional focus and move commands remain available; the full Canvas mapping is not yet implemented.

## Layout toggle and applications

The intended external desktop configuration uses **Super + Alt + L** for Standard ↔ Mosaic and **Super + Alt + M** for Applications. The Mosaic compositor command is `layout toggle mosaic`. The package does not install either binding, the application launcher, or a QuickShell menu.

The previous standard layout is remembered per workspace: `splith → mosaic → splith`, `tabbed → mosaic → tabbed`, and `stacking → mosaic → stacking`. Toggling does not replace windows or launch another compositor.

## Row memory

Each row conceptually remembers `scroll_x` and its last focused container. Changing rows should restore that row's context. Row 0 memory exists in the current model; multi-row navigation and restoration are **PLANNED**. A camera change must preserve logical order.

## Insertion, closing, and reflow

**CURRENT:** A newly tiled container is inserted immediately after the active logical container in Row 0. For example, `A B C`, focus `A`, then open `X` gives `A X B C`. A grouped subtree remains one Row 0 unit. Additional-row insertion policy is **TBD**.

**CURRENT:** Removing a tiled container closes the gap in logical order: `A B C D`, close `C`, then `A B D`. Focus references must not retain removed containers. Multi-row reflow policy is **PLANNED**.

## Viewport and sizing

**CURRENT/EXPERIMENTAL:** `layout mosaic scroll <signed pixels>` changes Row 0's logical camera position. Directional focus can bring an off-screen container into view. Scene translation is immediate, with no finished camera animation. The current 640 px minimum cell width is a temporary implementation value, **not** the final UX policy. Final cell sizing, grouped-cell behavior, animation timing/curve, and row sizing remain **TBD**.

The viewport must remain aligned with rendered content and hit testing. Robust clipping across adjacent outputs is **PLANNED**.

## Floating, fullscreen, and scratchpad

These remain ordinary Sway concepts. Mosaic does not redefine them. Headless tests have exercised basic floating, fullscreen, scratchpad, insertion, and layout transitions; longer multi-output and resize interactions are not fully validated. See [known limitations](KNOWN_LIMITATIONS.md).

## Workspaces and outputs

Mosaic does **not** replace Sway workspaces. Layout activation, previous standard layout, Row 0 state, and scroll belong to each workspace. A workspace may be moved between outputs; the camera must be bounded to its new viewport.

The desired multi-output model clips each workspace's visible Mosaic content to its own output viewport and keeps pointer hit testing consistent with the visible scene. This is **PLANNED**; the present single-output proof does not establish safe adjacent-output behavior.

## Open decisions

- Final cell width and nested-group sizing.
- Exact Super + arrows and Super + Ctrl action mapping.
- Multi-row insertion, navigation, and reflow details.
- Camera animation curve and timing.
- Fullscreen, floating, scratchpad, and output-migration edge-case policy after broader validation.

No binding or animation policy should be treated as frozen merely because a temporary implementation value exists.
