# Changelog

## Unreleased

### Patch export tooling

- Fixed cumulative Mosaic patch export to diff against the verified pristine SwayFX 0.6 import, preserve the real Git index, validate clean-base application and source equivalence, and replace the patch atomically only after successful checks.
- Added offline regression coverage for complete and repeatable export, working and staged edits, source additions/deletions and mode changes, index preservation, conflict refusal, and artifact preservation on failure or interruption.

### Documentation

- Established a public landing page, original source-controlled SVG banner, canonical documentation index, UX contract, packaging contract, known limitations, and documentation-first roadmap.
- Clarified the current single-row implementation, historical STEP evidence, package coexistence, and upstream forward-port policy.

### Existing implementation

- Native Mosaic layout with workspace-local state and real tiled Row 0.
- Insertion/reflow/focus model tests and `layout mosaic` command.
- Workspace-local `layout toggle mosaic`, logical scrolling, and first viewport scene translation.
- Mosaic `get_tree` IPC state and headless compositor validation.
- Isolated Arch packaging path for `/usr/bin/swayfx-mosaic`.

### Safety and limitations

- Ordinary SwayFX remains separately installed and independently updatable; no automatic session replacement.
- Multi-output clipping, multiple runtime rows, camera animation, Session V2 restore, final cell sizing, and daily-driver qualification remain open. See [known limitations](docs/KNOWN_LIMITATIONS.md).
