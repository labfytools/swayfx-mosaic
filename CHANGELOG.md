# Changelog

## Unreleased

### Added

- native Mosaic / Spatial Canvas layout foundation;
- workspace-local Mosaic state;
- real tiled Row 0 backed by the Sway tree;
- insertion/reflow/focus model tests;
- `layout mosaic` support;
- workspace-local `layout toggle mosaic`;
- logical row scrolling and first viewport translation;
- Mosaic IPC state in `get_tree`;
- headless compositor validation;
- isolated Arch packaging path for `/usr/bin/swayfx-mosaic`;
- architecture, development, upstream and roadmap documentation.

### Safety

- ordinary SwayFX remains installed separately and untouched;
- no automatic session replacement;
- no package `conflicts`, `replaces` or `provides` against SwayFX.

### Known limitations

- multi-output viewport clipping is not yet production-ready;
- multi-row Canvas behavior is not implemented;
- camera animation is not final;
- Session V2 does not yet restore Mosaic state;
- the final cell sizing/reflow policy is not frozen.
