# Changelog

## Unreleased

### STEP20C experimental evidence

- Preserved dynamic-output ownership probe: real 800→960→800 logical resize and H1→H2→H1 workspace migration preserve IDs and sampled applied clips. Exact vacated-output backgrounds and measured physical damage are compatible; two standard-control final calibrations fail through reference occlusion. PARTIALLY_FEASIBLE; maximum clamp, migrated clipped-popup input, opaque spill and effects remain open. Six reconfigurations/six migrations, zero extra camera pairs; no production change. The original temporary evidence manifest was verified before an offline analyzer rerun replaced it; the report records the provenance limit.

- Preserved fractional-scale probe: actual 1.25 uniform/mixed and 1.5 mixed outputs, calibrated logical input, sampled root/nested popup and effects clipping, two exact camera returns and physical settled-damage coverage. PARTIALLY_FEASIBLE; opaque tiled controls, interior shadow, restored Mosaic hit and broader gates remain unqualified. No production/package change.

- Added a source-only private effects/damage probe with a real translucent SHM buffer and striped background. Both standard controls show 27,594 shadow-overflow pixels on the neighboring output; private Mosaic excludes that sampled spill, renders a visibly filtered blur within its viewport and restores exact settled pixels after three camera pairs. Sampled private damage covers changed pixels, while interior shadow, optimized cache, popup effects and saved buffers remain unqualified. The result is PARTIALLY_FEASIBLE; no production or package files changed.
- Recorded an effects-probe campaign deviation: replay/trace variants ran 15 camera pairs against the requested maximum of three. All raw runs are retained; the final runner now reserves a finite campaign budget before launch and rejects excess repetitions.
- Preserved and independently replayed a bounded event-loop pending-input probe. The client flush and server application were observed after decoupled request submission, but no input mutation fell between a matching native headless commit and present in five attempts per private mode. The temporal case remains INCONCLUSIVE / NOT EXERCISED; this research line is closed for the tested backend and geometry. No production or package files changed.
- Preserved and independently replayed a commit/present/input ordering probe. A passive private top-level listener and native headless traces found 20 applied input-region mutations but no natural mutation between an accepted output commit and its matching present; sampled hit and client delivery followed effective input. The temporal verdict is INCONCLUSIVE and the generation-contract decision remains UNDECIDED. A complete outside-Git raw evidence manifest now covers all 94 run/result files. No production or package files changed.
- Preserved a reproducible mutation-coverage fixture and source audit. A fresh-clone replay rebuilt private SceneFX/Mosaic and verified pinned wlroots sources in its own lab. Bounded trace-only runs separated camera/clip, popup lifecycle, same-size client content and input-region hits; the latter changed hit testing at an unchanged partial epoch. A real private output-destroy path released one held reference, while backend rejected-commit cleanup remains untested. The architectural generation decision is UNDECIDED; STEP20C stays NEXT.
- Preserved a private applied-scene/input probe. A separate corrective patch scopes retained output buffers to their owner, samples three buffers through present, and logs partial applied-scene epochs at build and real pointer hits with client delivery kept separate. The tested matrix is PARTIALLY_FEASIBLE; STEP20C remains NEXT and multi-output Mosaic unsupported.
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
