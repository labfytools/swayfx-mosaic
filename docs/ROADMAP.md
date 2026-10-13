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

**Goal:** make the single-row viewport correct at workspace and output boundaries. **Planned deliverables:** clipping or an equivalent rendering strategy, matching hit testing, adjacent-output tests, resize/migration tests, and transaction-safe camera animation. **Exit criteria:** no cross-output visual/input leakage in the tested scenarios; camera and IPC remain consistent across transactions; standard layouts still pass. **Docs first:** review the [STEP20C viewport proposal](design/STEP20C_VIEWPORT_DESIGN.md), resolve the visual/input gaps found by the [PARTIALLY FEASIBLE isolated probe](design/STEP20C_FEASIBILITY_PROBE.md) and the [PARTIALLY FEASIBLE SceneFX subtree spike](design/STEP20C_SCENEFX_CLIPPING_SPIKE.md), then settle the resulting contract in Architecture and UX and update Known Limitations before implementation. The subtree spike proves a narrow tiled path but exposes a popup visual/input leak and unresolved damage, effect and package-maintenance gates. The [PARTIALLY_FEASIBLE popup ownership probe](design/STEP20C_POPUP_OWNERSHIP_PROBE.md) closes the sampled root/nested popup leak in an isolated build. The later [PARTIALLY_FEASIBLE valid-grab and hidden-owner probe](design/STEP20C_VALID_GRAB_HIDDEN_OWNER_PROBE.md) measures a real XDG grab and exposes a hidden-owner leak in that initial private clip; a further private guard closes the sampled leak. The later nested valid-grab probe closes only its sampled horizontal matrix; the separate vertical probe covers sampled Y-crossing popups. Further output geometries, transaction/output migration, complete damage/effects and packaging remain unresolved. None of these probes authorizes production STEP20C development or general multi-output support.

The [source fixture for the valid-grab probe](../tooling/probes/step20c-valid-grab/README.md) preserves a bounded replay path. Its existence does not change STEP20C's **NEXT** status or any exit criterion.

The [nested valid-grab probe](design/STEP20C_NESTED_VALID_GRAB_PROBE.md) is
**FEASIBLE within its sampled horizontal headless matrix**: distinct valid
grabs for parent and child popups, visual/input clipping, outside dismissal,
hidden-owner camera return and standard-layout return were measured in a
disposable guarded binary. Its [source fixture](../tooling/probes/step20c-nested-grab/README.md)
is reproducible. The next bounded feasibility test should change output
geometry with the same nested grabbed hierarchy and direct control comparison.
Transaction, resize/migration, damage/effects and ABI/package gates remain
open; this result does not change STEP20C's **NEXT** status.

The [vertical-output nested-grab probe](design/STEP20C_VERTICAL_OUTPUT_NESTED_GRAB_PROBE.md)
is **FEASIBLE within its sampled stacked-headless matrix**: both standard
controls produced real Y-crossing A/B popup pixels and button targets, while
the disposable guarded Mosaic build excluded sampled lower popup pixels/hits
and preserved upper interaction, hidden-owner return and standard-layout
return. Its [source fixture](../tooling/probes/step20c-vertical-grab/README.md)
also reproduced the horizontal B-crossing control. The separate negative-origin
comparison is recorded below. Scaling, rotation,
resize/migration, transaction generations, complete damage/effects and
dependency maintenance remain open. STEP20C stays **NEXT**.

The [negative-origin nested-grab probe](design/STEP20C_NEGATIVE_ORIGIN_NESTED_GRAB_PROBE.md)
is **FEASIBLE within its sampled signed-coordinate headless matrix**:
HEADLESS-1 remained at `x=-800`, the virtual pointer reached both outputs,
standard controls proved A/B crossing pixels and buttons, and the private
guarded Mosaic build clipped sampled right-output pixels and hits. Hidden
owner and `splith` return passed. Its [source fixture](../tooling/probes/step20c-negative-origin/README.md)
preserves replay. Scaling, rotation, resize/migration, transaction
generations, complete damage/effects and dependency maintenance remain open.
STEP20C stays **NEXT**.

The [temporal damage probe](design/STEP20C_TEMPORAL_DAMAGE_PROBE.md) is
**PARTIALLY_FEASIBLE**: repeated XDG lifecycle and camera transitions restored
sampled private Mosaic pixels and standard controls, and time-ordered private
damage extents covered changed pixels between sampled captures. It did not
identify every presented frame or bind camera/clip/input to a native applied
transaction generation. Its [source fixture](../tooling/probes/step20c-temporal-damage/README.md)
remains experimental. Its proposed headless presentation-event gate was
examined by the subsequent probe below. Scaling, rotation,
resize/migration, complete effects and dependency
maintenance remain open. STEP20C stays **NEXT**.

The [presentation identity probe](design/STEP20C_PRESENTATION_IDENTITY_PROBE.md)
is **PARTIALLY_FEASIBLE**: native wlroots 0.20.2 headless present events
were paired to commits by `(output, commit_seq)` and applied scene/clip
snapshots were taken at the commit callback. Settled target states passed
sampled clipping and input checks; faster commands could coalesce or defer.
The actual buffer content of each commit and frame-specific pointer relation
remain unproven. Its [private source fixture](../tooling/probes/step20c-presentation-identity/README.md)
does not enter the production build. Its then-open buffer identity gate was
examined by the subsequent private probe below. Scaling, rotation,
migration/resize, complete effects/damage and SceneFX maintenance remain
open. STEP20C stays **NEXT**.

The [output buffer identity probe](design/STEP20C_OUTPUT_BUFFER_IDENTITY_PROBE.md)
is **PARTIALLY_FEASIBLE** in this fixed matrix: 32 real GBM output-state
buffers were read through FX texture APIs, correlated with native commits
and headless presents. Twenty-eight were released on present and four
early because HEADLESS-2 repaint reached a global release in the private
instrumentation; the latter were not retained through present. Three
second reads were byte-identical. Sampled
popup pixels matched the applied scene/clip across
three pairs with the same A/B popup objects; the initial logical/applied
camera lag also had an identified buffer but no proven visual defect.
Readback materially changed timing, and neither frame-specific pointer
identity nor an atomic scene/input generation is proven. Its
[private fixture](../tooling/probes/step20c-buffer-identity/README.md) is
preserved experimental source, not a production dependency. The smallest
next gate is a lower-impact buffer observation with an explicit applied
scene/input generation, then separate effects/damage and SceneFX maintenance
qualification. STEP20C stays **NEXT**.

The [applied state/input probe](design/STEP20C_APPLIED_STATE_INPUT_PROBE.md)
is **PARTIALLY_FEASIBLE** in its fixed headless matrix. A distinct private
patch prevented the historical cross-output buffer release; three
selected buffers were read and retained through native headless present,
while a partial experimental epoch and real pointer traces exposed
applied state at build and hit. Client delivery under grabs remained a
separate observation. Incomplete mutation coverage, untested error paths
and intrusive readback leave the temporal-consistency gate open. The
next experiment was to map the mutation boundary with lower-impact
observation before any production STEP20C decision. STEP20C
stays **NEXT**; multi-output remains **NOT YET SUPPORTED**.

The [mutation coverage probe](design/STEP20C_MUTATION_COVERAGE_PROBE.md)
is **PARTIALLY_FEASIBLE** overall. A bounded trace-only matrix separated
camera/clip, popup hierarchy, same-size client content and surface input
region changes. The input-region test changed the actual scene hit while
`asi_applied_epoch` was unchanged, so that counter is not a complete
geometry/hit identity. Output destruction released one held reference in
the real private compositor; rejected-commit cleanup is still untested on
a backend. Whether SwayFX's existing event-loop ordering suffices for
build/present/input coherence is **UNDECIDED**. The smallest next gate is
a controlled hit-geometry mutation between one known output-state build
and its deferred headless present, with hits and client delivery sampled
on both sides. This remains scientific evidence, not production STEP20C.

The independently replayed [commit/present/input ordering probe](design/STEP20C_COMMIT_PRESENT_INPUT_ORDERING_PROBE.md)
tested that gate without changing backend scheduling. Twenty real input
region mutations applied in two private modes, but none occurred between
an accepted output commit and its matching headless present; P2 is
**INCONCLUSIVE**. The sampled hit and client delivery matched effective
input state, and no distinct Mosaic clipping defect was reproduced. The
subsequent pending-input event-loop follow-up below addressed that bounded
timing question without observing the target interval. STEP20C remains
**NEXT** and multi-output **NOT YET SUPPORTED**.

The bounded [event-loop pending-input probe](design/STEP20C_EVENT_LOOP_PENDING_INPUT_PROBE.md)
decoupled normal client submission from IPC/client acknowledgements, then
stopped after five attempts in each private mode. All 20 target mutations
applied, with no matching commit-to-present interleaving. Close this
particular temporal line as **INCONCLUSIVE / NOT EXERCISED** for the tested
headless backend and fixed geometry. Do not infer an extra generation
contract or production readiness. The next separate STEP20C gate should
address complete effects/damage, scaling, or resize/migration. STEP20C stays
**NEXT** and multi-output Mosaic **NOT YET SUPPORTED**.

The [effects/damage probe](design/STEP20C_EFFECTS_DAMAGE_PROBE.md) then
demonstrated genuine shadow spill in both standard controls, excluded the
sampled spill under private Mosaic, and measured a visibly active
translucent blur, sampled damage coverage and three exact settled camera
returns. Its result is **PARTIALLY_FEASIBLE**: interior Mosaic shadow,
optimized blur cache correctness, outside-viewport shader sampling, popup
effects and saved buffers remain unqualified. The next distinct gate should
test scaling first for the inherited clip and effect draw regions;
rotation, resize/migration, saved buffers and ABI/package maintenance remain open.
This does not authorize STEP20C production work or STEP20D. STEP20C stays
**NEXT** and production multi-output Mosaic **NOT YET SUPPORTED**.

## STEP20D — multi-row Spatial Canvas · PLANNED

**Goal:** connect rows to runtime tree, transactions, scene, input, and IPC. **Planned deliverables:** active-row navigation, row-local scroll/focus, deterministic insertion/reflow, in-row reorder, and between-row movement. **Exit criteria:** real tiled containers preserve identity and order across row changes; focus and camera restore correctly; headless multi-row tests pass. **Docs first:** settle exact interactions and row invariants in UX and Architecture. Unset key combinations remain TBD.

## STEP20E — Session V2 persistence · PLANNED

**Goal:** restore Mosaic workspaces across sessions without creating a second runtime authority. **Planned deliverables:** durable activation, row order/membership, active row, scroll, focus, stable identities, and restart tests. **Exit criteria:** deterministic restore and safe fallback for missing windows/older snapshots. **Docs first:** specify persistence identity, versioning, failure handling, and ownership in Architecture and UX.

## STEP20F — QuickShell visualization · PLANNED

**Goal:** expose compositor-owned Mosaic state in the desktop UI. **Planned deliverables:** workspace/row view and optional layout indication without duplicate QML layout state. **Exit criteria:** UI reflects IPC state and cannot contradict the compositor. **Docs first:** specify IPC consumer behavior and UI interactions in Architecture and UX.

## STEP20G — package and daily-use qualification · PLANNED

**Goal:** publish a validated optional session while preserving standard SwayFX fallback. **Planned deliverables:** final Arch package, optional distinct session entry, install/rollback instructions, and a forward port proven against a newer SwayFX release. **Exit criteria:** package file ownership and coexistence verified, release build and headless/live qualification recorded, standard SwayFX updates remain independent. **Docs first:** update Packaging, Upstream, Development, UX, and Known Limitations with the intended release contract.

Effects freeze audit: the historical campaign exceeded its three-pair budget
(15 pairs in five Mosaic runs); all evidence is retained. A separate fresh
rebuild reproduced the main counts with one pair under the corrected
campaign guard. The traced reference had a different effective size, so
instrumentation neutrality and its cause remain unqualified. See the
[effects report](design/STEP20C_EFFECTS_DAMAGE_PROBE.md). This adds no contract.

The preserved [fractional scaling probe](design/STEP20C_FRACTIONAL_SCALING_PROBE.md)
is **PARTIALLY_FEASIBLE** for static 1.25 uniform/mixed and 1.5 mixed headless
outputs. Actual modes/PNGs and logical pointer motion were calibrated. Sampled
root/nested popup and shadow spill disappeared on the neighboring output;
visible blur, terminal popup columns, two settled camera returns and available
physical damage were consistent. Opaque tiled-overflow controls, permitted
interior shadow, restored Mosaic hit, caches and intermediate frames remain
unqualified. Ten failed early calibrations and their source-provenance limit
are retained. The two-pair global budget was respected. The next distinct gate
should test resize/migration of owner/output clips; rotation, saved buffers and
ABI/package remain separate. This is evidence only: STEP20C stays **NEXT**,
production multi-output **NOT YET SUPPORTED**, STEP20D–G **PLANNED**.

The preserved [dynamic output ownership probe](design/STEP20C_DYNAMIC_OUTPUT_OWNERSHIP_PROBE.md)
is **PARTIALLY_FEASIBLE**: actual logical resize 800→960→800 and workspace
migration H1→H2→H1 retain workspace/tiled identities and update sampled applied
tiled/root-popup clips. Vacated outputs show exact background after stabilization.
Two standard controls fail final reference calibration through fixture occlusion;
Mosaic's corrected calibration passes. Maximum-scroll clamp, migrated clipped
popup input, independent opaque tiled spill, effects and intermediate frames
remain unqualified. Budgets are exhausted at six reconfigurations and six
migrations, with zero additional camera pairs. No production change follows.
Rotation is the next separate geometric gate; other open STEP20C gates persist.
The original temporary evidence manifest passed verification before an
offline analyzer rerun replaced its bytes; see the report for provenance.
STEP20C stays **NEXT**, multi-output **NOT YET SUPPORTED**.

The [rotated-output probe](design/STEP20C_ROTATED_OUTPUT_PROBE.md) is
**PARTIALLY_FEASIBLE** for sampled applied geometry, PNG/pointer calibration,
hidden-owner return and physical damage. Its partial-popup clipping conclusion
is **UNDECIDED** because the Mosaic popup never crossed the R90 boundary and
the pristine R90 capture was lost to a fixture assertion. The next distinct
geometric gate should force a legal grabbed Mosaic popup portion across that
boundary with a completed pristine control. STEP20C remains **NEXT**.

The [static R90 partial-popup gate](design/STEP20C_ROTATED_PARTIAL_POPUP_CLIP_PROBE.md)
then measured exactly that B crossing and completed the pristine control.
The bounded result is **PARTIALLY_FEASIBLE**: B's sampled pixels/input obeyed
the owner clip, while the independent clipped-away A input point and broader
temporal/effect cases remain open. Next prioritize saved transaction buffers
against the same owner-derived viewport before optimized blur cache,
interior shadow and ABI/package maintenance. STEP20C remains **NEXT**;
production multi-output remains **NOT YET SUPPORTED**.

The subsequent [saved transaction buffer campaign](design/STEP20C_SAVED_TRANSACTION_BUFFER_PROBE.md)
observed real held XDG configure transactions, reused saved buffers, private
render entries and sampled ACK/timeout removal. Its target never crossed the
H1/H2 boundary after the applied Mosaic camera settled at 1760. Overall
**INCONCLUSIVE**; all three run reservations are consumed. A new, separately
authorized saved-buffer experiment must calibrate the applied camera and
target crossing before the first transaction. Optimized blur/cache and
SceneFX ABI/package remain separate unqualified gates. STEP20C stays
**NEXT**, multi-output **NOT YET SUPPORTED**.

The independent [saved target crossing campaign](design/STEP20C_SAVED_BUFFER_TARGET_CROSSING_PROBE.md)
used one measured signed camera correction and observed the actual target
saved node cross x=0, render inside H1 and retain permitted pixels. H2 showed
no target color, but whole-image equality failed by a repeated 253-pixel
reference difference. Mosaic timeout cleanup and held input remain untested
after an E2 fixture pointer error. Result **PARTIALLY_FEASIBLE**, architecture
**UNDECIDED**. The next narrow gate should first resolve the H2 reference
artifact and complete a fresh target timeout/input observation; optimized
blur/cache and SceneFX ABI/package remain later separate gates. STEP20C is
still **NEXT** and multi-output **NOT YET SUPPORTED**.

The saved-target freeze audit identifies the repeated 253-pixel H2 difference
as strongly compatible with Kitty's blinking block cursor, not causally
proven. A separate static-reference Mosaic timeout/input gate is authorized
before optimized blur/cache and SceneFX ABI/package work. No production
readiness or changed UX contract follows.

The completed [static-reference saved-target natural timeout gate](design/STEP20C_SAVED_TARGET_TIMEOUT_INPUT_PROBE.md)
then measured a real crossing target saved node, clipped H1 rendering,
stable full-image H2 RGB, two targeted pointer hits and natural timeout
cleanup with the XDG client alive and serial 50 withheld. Combined with the
earlier E1 ACK, the tested saved-target clipping matrix is viable, while
damage across every frame, broader input and GPU/texture lifetime remain
unqualified. Its verdict is **PARTIALLY_FEASIBLE**; the earlier probe's own
UNDECIDED conclusion is preserved. The next separate STEP20C gate is
optimized blur/cache, followed by SceneFX ABI/package. STEP20C is still
**NEXT**, production multi-output **NOT YET SUPPORTED**.

The preserved [optimized blur cache probe](design/STEP20C_OPTIMIZED_BLUR_CACHE_PROBE.md)
is **PARTIALLY_FEASIBLE**, architecture **UNDECIDED**. A real background
layer under blur_tree triggered natural output-specific cache reconstruction
and fresh central A/B/A filtered pixels in private splith and Mosaic.
Sampled final tiled drawing excluded H2, whose whole RGB remained identical;
output damage extents covered stabilized differences and sampled cache/FBO
teardown completed. Shared boundary differences up to six RGB levels remain
unresolved. Pristine C0 failed before captures through a duplicate configure
fixture; its second initial image was reserved only after observation.
No numerical budget was exceeded or run repeated. Instrumentation neutrality,
whole-cache equivalence and intermediate frames remain unqualified. A
separate pristine/untraced boundary-sampling gate should precede ABI/package
qualification. This evidence freeze changes no production or UX contract.
STEP20C stays **NEXT**, multi-output **NOT YET SUPPORTED**.

The preserved [optimized edge causality gate](design/STEP20C_OPTIMIZED_BLUR_EDGE_CAUSALITY_PROBE.md)
is **PARTIALLY_FEASIBLE**, architecture **UNDECIDED**. Four completed fixed
negative-origin runs qualify pristine/private splith and same-binary Mosaic
OPT-off/on controls. Pristine/private full images and Mosaic trace-off/on
full images are exact at six homologous states; common glass across layouts
is also exact. Historical right/bottom differences persist without new traces,
with max RGB delta 6, fresh central pixels and stable whole H2. Native FBO
history causality remains unproved despite source/model support. R3 damage
extents cover stabilized differences only. No clipping regression or required
invariant violation is established. A separate SceneFX ABI/package audit is
now justified, retaining this shared rendering limitation; optional selective
GPU observation requires a new scoped ticket. This evidence is preserved without a production change. STEP20C stays NEXT, production multi-output NOT YET SUPPORTED.

The preserved [SceneFX ABI/package audit](design/STEP20C_SCENEFX_ABI_PACKAGE_FEASIBILITY.md)
is **PARTIALLY_FEASIBLE**, architecture
**SCENEFX_ABI_PACKAGE_REQUIRES_ARCHITECTURAL_DECISION**. The unchanged current
package builds with stock SceneFX and stages exactly /usr/bin/swayfx-mosaic.
The shared experimental binary needs two clip exports absent from stock
despite the same SONAME. Static embedding builds and resolves without a
SceneFX shared dependency, but shared wlroots interposition, updates, security
maintenance and license notices remain gates. A distinct private shared library
would require a new file-ownership decision; upstream API acceptance is unknown.
No integration or packaging contract is approved. The historical audit is frozen as evidence; STEP20C stays NEXT, production multi-output NOT YET SUPPORTED.

The preserved [static distribution contract dossier](design/STEP20C_SCENEFX_STATIC_DISTRIBUTION_CONTRACT.md)
is **EXPERIMENTAL / PARTIALLY_FEASIBLE**, conclusion
**STATIC_DISTRIBUTION_REQUIRES_CONTRACT_DECISION**. One private Meson DESTDIR
stage of the hash-qualified static executable contains exactly
`/usr/bin/swayfx-mosaic`; this proves file shape only. The 85 overlapping
exports and 31/34 wlroots scene bindings into the executable remain explicit
paired-version constraints, not automatically defects. Only the pinned
SceneFX 0.5 / observed wlroots 0.20.2 pair has non-graphical evidence.
Notices (including generated protocols), security ownership, upgrades, rollback
and graphical semantics remain gates. A disposable notice-section extraction
passes mechanically; legal distribution compliance is not approved.
The upstream API dossier is preserved and not submitted. Production strategy:
**NONE — USER DECISION REQUIRED**. Packaging/UX contracts are unchanged;
STEP20C stays NEXT and production multi-output NOT YET SUPPORTED.

## Approved private STEP20C static candidate — 2026-10-13

The user approved four decisions for documentation and private prototypes only:
private static SceneFX; separate complete notices under
`/usr/share/licenses/swayfx-mosaic/`; project responsibility for embedded
SceneFX maintenance; and qualification of each exact SceneFX/wlroots pair.
See the [decision register and bounded runtime gate](design/STEP20C_STATIC_RUNTIME_AND_PACKAGE_CONTRACT.md).
The current PKGBUILD, system SceneFX dependency, one-binary package, production
sources and cumulative patch remain unchanged. The future private stage may
contain only `/usr/bin/swayfx-mosaic` and justified regular notice files below
the license directory. No private shared library, session, service, config or
Sway symlink is allowed. No real installation is authorized.

Mosaic owns monitoring, impact review, rebuild and requalification of embedded
SceneFX fixes, including renderer/shaders/dependencies/ABI/buffer lifetime/clip/
damage changes. Before public distribution, a release maintainer and security
reviewer must be designated; no names or SLA are assigned. Preserve exact source,
patch, compiler/options/dependency, notice, test and artifact manifests.
A new relevant dependency build requires header/symbol/shared-layout inspection,
rebuild, relocation/model/staging/headless checks and graphical requalification
of relevant paths, then a separate publication decision. No automatic update
subsystem is added. Ordinary SwayFX upgrades remain independent and standard
SwayFX remains the fallback. All other pairs are NOT QUALIFIED.

These decisions do not settle popup UX or close STEP20C production gates.
STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT; STEP20D–G PLANNED.
Production multi-output remains NOT YET SUPPORTED.

The [private static runtime gate](design/STEP20C_STATIC_RUNTIME_AND_PACKAGE_CONTRACT.md)
is **EXPERIMENTAL / PARTIALLY_FEASIBLE**, architecture **UNDECIDED**. Real `/usr`
static build/model/stage/notices/loaded-library identity/headless startup pass.
Sampled H1 target pixels survive with zero target colors on H2, but whole-H2
reference equality fails through a focus/decor mismatch; input and splith return
are NOT TESTED after the single run stopped. No rerun or algorithm modification
occurred. Distribution notice closure, named release/security roles and broader
ABI/graphics gates remain open. STEP20C NEXT, multi-output NOT YET SUPPORTED.
