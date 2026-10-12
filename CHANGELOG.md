# Changelog

## Unreleased

### STEP20C experimental evidence

- Preserved a private output-buffer identity fixture and protocol. In fixed headless geometry, 32 GBM buffers were read through SceneFX FX and linked to native commits and presents; three second reads matched. Four references were released early by a cross-output scope defect in the private instrumentation, not by demonstrated same-output buffer replacement. Readback changed timing, so transaction/input coherence and production readiness remain unproven. STEP20C stays NEXT and multi-output Mosaic unsupported.
- Added a source-only private presentation-identity probe at fixed negative-origin headless geometry. Native wlroots output present events paired with 470 accepted commits by output and `commit_seq`; applied scene/clip and sampled input agreed at the target states, but exact commit-buffer pixels remain unproven. STEP20C stays NEXT and production multi-output Mosaic unsupported.
- Added a source-only temporal damage fixture at the fixed negative-origin geometry. Ten XDG open/close cycles in each of three modes and sampled camera transitions restored popup regions without a detected ghost pixel; private damage/commit traces remain insufficient for a presented-frame guarantee. STEP20C remains NEXT and multi-output Mosaic unsupported.
- Added a source-only negative-origin nested-grab probe. Two outputs at `x=-800/0` verified signed pointer conversion, real standard popup crossing, sampled private Mosaic clipping, hidden-owner return, standard-layout return and a positive horizontal regression. Production STEP20C support remains open.
- Added a source-only stacked-output nested valid-grab probe. Both standard controls showed real popup overflow and pointer delivery below `y=600`; the private guarded Mosaic build clipped A/B at sampled lower points, preserved hidden-owner and standard-layout return, and reproduced the horizontal control. STEP20C production support remains open.
- Added a source-only nested XDG grab fixture and a comparative headless probe. Two real button serials produced an interactive toplevel → popup A → popup B chain; sampled guarded Mosaic clipping, child-first dismissal, hidden-owner camera return and standard-layout return were feasible. STEP20C production support remains open.
- Preserved the valid-serial XDG grab / hidden-owner probe's original C and Python sources, private patches and protocol XML with hashes and a disposable headless replay procedure. Its result remains **PARTIALLY_FEASIBLE**; no production source, package or UX policy changed.

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
