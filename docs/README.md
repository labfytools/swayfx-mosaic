# Documentation

[Isolated EGL/FX probe](design/STEP20C_HEADLESS_EGL_FX_PROBE.md)
records the single 2026-10-17 namespace failure: EXPERIMENTAL /
EGL_FX_PROBE_BLOCKED_BEFORE_HELPER / EGL_NOT_RUN / ALLOCATOR_NOT_ATTEMPTED.
The historical READY_FOR_APPROVAL verdict preceded that consumed attempt.
The [task-limit protocol design](design/STEP20C_EGL_FX_TASK_LIMIT_PROTOCOL.md)
selects probe-local cgroup admission for future implementation;
EGL_FX_RETRY_PREP_BLOCKED, new runtime NOT_RUN. No retry is authorized.

[Gate 2 headless boot](design/STEP20C_HEADLESS_BOOT_GATE2.md) records the single
V5 native failure: EXPERIMENTAL / PRISTINE_ALLOCATOR_BLOCKED / CORE_NOT_RUN,
without private IPC or rendering proof. The [allocator triage](design/STEP20C_HEADLESS_ALLOCATOR_TRIAGE.md)
distinguishes source inference from observed failure; any new native experiment
requires separate approval. STEP20C remains NEXT; production multi-output
NOT_YET_SUPPORTED.

The [CORE-C V2 follow-up decision V4](design/STEP20C_COREC_V2_INTEGRATION_DECISION_V4.md)
records PARTIALLY_ADVANCED private evidence: five consumed runs, 32 output
captures, migration/refocus and root/nested OOM SAMPLED_ONLY / PARTIALLY_FEASIBLE.
[Fullscreen comparison](design/STEP20C_COREC_V2_FULLSCREEN_COMPARATIVE_GATE.md)
is NOT_EXERCISED, FS-C NOT_RUN; [GLES/readback G3](design/STEP20C_GLES_CONTEXT_READBACK_FOLLOWUP.md)
is INCONCLUSIVE after a fixture client exit2 before SHM, with native acquisition
NOT_EXERCISED. See the [migration report](design/STEP20C_COREC_V2_MIGRATION_REFOCUS_GATE.md)
and [native OOM completion](design/STEP20C_COREC_V2_NATIVE_OOM_COMPLETION.md).
Disposition PRIVATE_COREC_V2_NEEDS_TARGETED_EVIDENCE; production OOM policy
UNDECIDED. Separate post-campaign fixture repairs are OFFLINE_ONLY; the
[parent V2 dossier](design/STEP20C_COREC_V2_INTEGRATION_DECISION.md), 12 runs/102
captures and historical verdicts remain unchanged. STEP20C NEXT; production
multi-output NOT_YET_SUPPORTED; PRODUCTION_AUTHORIZED FALSE.

Documentation is a first-class project artifact. Architecture and UX contracts are updated before implementation when behavior changes.

The [root README](../README.md) is the public summary. For a specific topic, use the canonical document below. Within its own subject, a canonical document takes precedence over a historical STEP report. If two canonical documents disagree, resolve the conflict before implementation; do not silently choose one.

## Source-of-truth order

1. [Architecture](ARCHITECTURE.md): compositor ownership and technical invariants.
2. [UX contract](UX.md): user-visible behavior and interaction invariants.
3. [Packaging](PACKAGING.md): binary and package coexistence.
4. [Upstream maintenance](UPSTREAM.md): provenance and forward ports.
5. [Development](DEVELOPMENT.md): reproducible workflow.
6. [Known limitations](KNOWN_LIMITATIONS.md): current support boundary.
7. [Roadmap](ROADMAP.md): ordered future work, not proof of implementation.
8. [STEP20C viewport proposal](design/STEP20C_VIEWPORT_DESIGN.md): proposed design, subordinate to accepted canonical contracts.
9. [STEP20C feasibility probe](design/STEP20C_FEASIBILITY_PROBE.md): isolated technical evidence and an unresolved multi-output gate.
10. [STEP20C SceneFX subtree spike](design/STEP20C_SCENEFX_CLIPPING_SPIKE.md): isolated clipping, popup and packaging evidence; production gate remains open.
11. [STEP20C popup ownership probe](design/STEP20C_POPUP_OWNERSHIP_PROBE.md): isolated owner-derived root/nested popup evidence and remaining grab, damage and packaging gates.
12. [STEP20C valid-grab and hidden-owner probe](design/STEP20C_VALID_GRAB_HIDDEN_OWNER_PROBE.md): isolated valid-serial XDG grab comparison, fully hidden owner leak and private guard evidence; production gates remain open.
    [Preserved source fixtures](../tooling/probes/step20c-valid-grab/README.md) record exact inputs and a disposable replay procedure.
13. [STEP20C nested valid-grab probe](design/STEP20C_NESTED_VALID_GRAB_PROBE.md): two genuine nested XDG grabs and sampled clipping, dismissal, hidden-owner and standard-layout return evidence; remaining STEP20C gates stay open.
    [Nested-grab source fixture](../tooling/probes/step20c-nested-grab/README.md) reconstructs the same disposable experiment.
14. [STEP20C vertical-output nested-grab probe](design/STEP20C_VERTICAL_OUTPUT_NESTED_GRAB_PROBE.md): sampled vertical popup clipping and pointer evidence with two standard controls and private Mosaic; production gates remain open.
    [Vertical source fixture](../tooling/probes/step20c-vertical-grab/README.md) replays it in a disposable laboratory.
15. [STEP20C negative-origin nested-grab probe](design/STEP20C_NEGATIVE_ORIGIN_NESTED_GRAB_PROBE.md): sampled signed-coordinate pointer, popup clipping, hidden-owner and standard-layout evidence with real `x=-800` headless origin; production gates remain open.
    [Negative-origin source fixture](../tooling/probes/step20c-negative-origin/README.md) replays it in a disposable laboratory.
16. [STEP20C temporal damage probe](design/STEP20C_TEMPORAL_DAMAGE_PROBE.md): repeated XDG cycles, camera transitions, sampled pixel restoration and timed private damage/commit traces at the same negative-origin geometry; frame presentation remains unproven.
    [Temporal source fixture](../tooling/probes/step20c-temporal-damage/README.md) rebuilds the private campaign.
17. [STEP20C presentation identity probe](design/STEP20C_PRESENTATION_IDENTITY_PROBE.md): native headless commit/present correlation and sampled applied camera/clip/input evidence; exact committed buffer content remains unproven.
    [Presentation source fixture](../tooling/probes/step20c-presentation-identity/README.md) rebuilds the private instrumentation.
18. [STEP20C output buffer identity probe](design/STEP20C_OUTPUT_BUFFER_IDENTITY_PROBE.md): private GBM/FX buffer readback tied to native commit and headless present, with measured timing perturbation and remaining temporal-coherence gate.
    [Buffer source fixture](../tooling/probes/step20c-buffer-identity/README.md) reconstructs the disposable experiment; it is not production code.
19. [STEP20C applied state/input probe](design/STEP20C_APPLIED_STATE_INPUT_PROBE.md): private per-output buffer-reference correction and partial applied-scene epoch tracing through render and pointer paths; no atomic generation is established.
    [Applied-state source fixture](../tooling/probes/step20c-applied-state-input/README.md) rebuilds the disposable experiment.
20. [STEP20C mutation coverage probe](design/STEP20C_MUTATION_COVERAGE_PROBE.md): source ownership inventory and bounded trace-only camera, popup, client-content and input-region scenarios; output-destroy cleanup sampled, rejected commit still untested.
    [Mutation source fixture](../tooling/probes/step20c-mutation-coverage/README.md) replays the disposable matrix without production integration.
21. [STEP20C commit/present/input ordering probe](design/STEP20C_COMMIT_PRESENT_INPUT_ORDERING_PROBE.md): independently replayed headless ordering evidence; 20 applied input-region mutations, no natural commit-to-present interleaving, temporal question INCONCLUSIVE.
    [Ordering source fixture](../tooling/probes/step20c-commit-present-input/README.md) rebuilds the passive private trace.
22. [STEP20C event-loop pending-input probe](design/STEP20C_EVENT_LOOP_PENDING_INPUT_PROBE.md): bounded asynchronous client submission and native callback order; no natural commit-to-present input mutation, INCONCLUSIVE.
    [Pending-input source fixture](../tooling/probes/step20c-event-loop-pending-input/README.md) replays the disposable matrix.
23. [STEP20C effects/damage probe](design/STEP20C_EFFECTS_DAMAGE_PROBE.md): real translucent blur and shadow-overflow pixels compared across standard and private Mosaic layouts; sampled damage and camera returns PARTIALLY_FEASIBLE, optimized blur cache unqualified.
    [Effects/damage source fixture](../tooling/probes/step20c-effects-damage/README.md) rebuilds the disposable matrix.
24. [STEP20C static R90 partial-popup probe](design/STEP20C_ROTATED_PARTIAL_POPUP_CLIP_PROBE.md): sampled genuine B crossing and input with a completed pristine control; broader STEP20C gates remain open.
    [R90 source fixture](../tooling/probes/step20c-rotated-partial-popup/README.md) preserves the published experimental inputs.
25. [STEP20C saved transaction buffer probe](design/STEP20C_SAVED_TRANSACTION_BUFFER_PROBE.md): real saved nodes and lifetime evidence, but target partial-overflow geometry NOT EXERCISED; result INCONCLUSIVE.
    [Saved-buffer source fixture](../tooling/probes/step20c-saved-transaction-buffer/README.md) preserves the experimental inputs.
26. [STEP20C saved target crossing probe](design/STEP20C_SAVED_BUFFER_TARGET_CROSSING_PROBE.md): measured saved target crossing and clipped H1 render; H2 reference difference and incomplete timeout/input gate keep it PARTIALLY_FEASIBLE.
    [Target-crossing source fixture](../tooling/probes/step20c-saved-buffer-target-crossing/README.md) remains local and experimental.
27. [STEP20A](STEP20A.md) and [STEP20B](STEP20B.md): historical evidence.

## Project

| Document | Role | Purpose |
| --- | --- | --- |
| [README](../README.md) | Summary | Public landing page and current status |
| [Contributing](../CONTRIBUTING.md) | Normative | Scope, docs-first flow, checks |
| [Changelog](../CHANGELOG.md) | Historical | Repository evolution |
| [Notice](../NOTICE.md) | Normative | Attribution boundary |

## Architecture and user experience

| Document | Role | Purpose |
| --- | --- | --- |
| [Architecture](ARCHITECTURE.md) | Normative | Runtime model, ownership, IPC, transactions, scene |
| [UX contract](UX.md) | Normative | Interaction rules, row behavior, undecided choices |
| [Known limitations](KNOWN_LIMITATIONS.md) | Planning/current evidence | Unsupported and unvalidated paths |

## Development, packaging, and upstream

| Document | Role | Purpose |
| --- | --- | --- |
| [Development](DEVELOPMENT.md) | Normative | Build, test, staging, patch workflow |
| [Packaging](PACKAGING.md) | Normative | File ownership, versioning, fallback |
| [Upstream maintenance](UPSTREAM.md) | Normative | SwayFX relationship, pinned base, forward ports |

## Design proposals

| Document | Role | Purpose |
| --- | --- | --- |
| [STEP20C viewport design](design/STEP20C_VIEWPORT_DESIGN.md) | Proposed, not yet accepted | Source audit, clipping alternatives, test plan, feasibility gate |
| [STEP20C feasibility probe](design/STEP20C_FEASIBILITY_PROBE.md) | Experimental evidence | PARTIALLY FEASIBLE; visual and input boundary failed in a two-output headless candidate |
| [STEP20C SceneFX subtree spike](design/STEP20C_SCENEFX_CLIPPING_SPIKE.md) | Experimental evidence | PARTIALLY FEASIBLE; tiled clip worked privately, global popup leaked pixels and input |
| [STEP20C popup ownership probe](design/STEP20C_POPUP_OWNERSHIP_PROBE.md) | Experimental evidence | PARTIALLY_FEASIBLE; owner-derived root/nested popup clipping worked in a horizontal private headless case, with grab/damage/output gates open |
| [STEP20C valid-grab and hidden-owner probe](design/STEP20C_VALID_GRAB_HIDDEN_OWNER_PROBE.md) | Experimental evidence | PARTIALLY_FEASIBLE; valid-serial popup grab measured, hidden-owner leak found and closed only in a private guard; broader STEP20C gates remain open |
| [STEP20C nested valid-grab probe](design/STEP20C_NESTED_VALID_GRAB_PROBE.md) | Experimental evidence | FEASIBLE for sampled two-level grabbed XDG popup cases on horizontal headless outputs; no production qualification |
| [STEP20C vertical-output nested-grab probe](design/STEP20C_VERTICAL_OUTPUT_NESTED_GRAB_PROBE.md) | Experimental evidence | FEASIBLE for sampled two-level grabbed XDG popup cases across the horizontal output boundary; no production qualification |
| [STEP20C negative-origin nested-grab probe](design/STEP20C_NEGATIVE_ORIGIN_NESTED_GRAB_PROBE.md) | Experimental evidence | FEASIBLE for sampled two-level grabbed XDG popup cases with HEADLESS-1 at `x=-800`; no production qualification |
| [STEP20C temporal damage probe](design/STEP20C_TEMPORAL_DAMAGE_PROBE.md) | Experimental evidence | PARTIALLY_FEASIBLE for sampled repeated lifecycle/camera states; damage-to-presented-frame and transaction/input synchronization remain open |
| [STEP20C presentation identity probe](design/STEP20C_PRESENTATION_IDENTITY_PROBE.md) | Experimental evidence | PARTIALLY_FEASIBLE; native headless events pair with commits, but buffer pixels and per-frame input identity remain unproven |
| [STEP20C output buffer identity probe](design/STEP20C_OUTPUT_BUFFER_IDENTITY_PROBE.md) | Experimental evidence | PARTIALLY_FEASIBLE; sampled true buffers were read and paired with headless presents; four early releases came from a private cross-output instrumentation defect, while readback perturbs timing and atomic scene/input coherence remains unproven |
| [STEP20C applied state/input probe](design/STEP20C_APPLIED_STATE_INPUT_PROBE.md) | Experimental evidence | PARTIALLY_FEASIBLE; per-output holds survive cross-output repaint in the sampled matrix, and applied scene/hit/client streams are observed with a partial experimental epoch |
| [STEP20C mutation coverage probe](design/STEP20C_MUTATION_COVERAGE_PROBE.md) | Experimental evidence | PARTIALLY_FEASIBLE overall; an input-region change alters the hit at unchanged partial epoch, client recolor changes pixels without geometry, and a held output reference is released on sampled output destruction; cross-time generation contract remains UNDECIDED |
| [STEP20C commit/present/input ordering probe](design/STEP20C_COMMIT_PRESENT_INPUT_ORDERING_PROBE.md) | Experimental, independently replayed evidence | INCONCLUSIVE for the discriminating temporal window; headless input-region commits and hits agree in observed states, but none of 20 applied mutations occurred between a native output commit and its present |
| [STEP20C event-loop pending-input probe](design/STEP20C_EVENT_LOOP_PENDING_INPUT_PROBE.md) | Experimental, independently replayed evidence | INCONCLUSIVE / NOT EXERCISED for natural commit→input mutation→present despite decoupled client submission; the temporal line is closed for this backend/matrix |
| [STEP20C effects/damage probe](design/STEP20C_EFFECTS_DAMAGE_PROBE.md) | Experimental, independent private replay | PARTIALLY_FEASIBLE for visible blur, excluded sampled shadow overflow, settled camera restoration and sampled damage; shadow interior, optimized cache, popup effects and saved buffers remain unqualified |
| [STEP20C static R90 partial-popup probe](design/STEP20C_ROTATED_PARTIAL_POPUP_CLIP_PROBE.md) | Experimental evidence | PARTIALLY_FEASIBLE; sampled B crossing clips under R90, independent A input remains untested |
| [STEP20C saved transaction buffer probe](design/STEP20C_SAVED_TRANSACTION_BUFFER_PROBE.md) | Experimental, local evidence | INCONCLUSIVE; real saved nodes rendered, target partial crossing not exercised |
| [STEP20C saved target crossing probe](design/STEP20C_SAVED_BUFFER_TARGET_CROSSING_PROBE.md) | Experimental, local evidence | PARTIALLY_FEASIBLE; target saved node crossed and rendered within H1, but whole-H2 reference and timeout/input evidence remain open |

A proposal does not supersede accepted canonical contracts or assert implementation status. Its open feasibility items must be resolved before implementation.

## Roadmap and historical reports

| Document | Role | Purpose |
| --- | --- | --- |
| [Roadmap](ROADMAP.md) | Planning | Step goals, exit criteria, required documentation |
| [STEP20A](STEP20A.md) | Historical | Native foundation implementation evidence |
| [STEP20B](STEP20B.md) | Historical | First scrollable-row implementation evidence |

STEP reports record what was observed and decided at the time. They are **not** the canonical source for current behavior. When a STEP report conflicts with current canonical documentation, the canonical documentation wins. The original French reports are preserved as historical artifacts; their opening notices point here.

Preserved experimental evidence: [fractional scaling probe](design/STEP20C_FRACTIONAL_SCALING_PROBE.md)
and [source fixture](../tooling/probes/step20c-fractional-scale/README.md).
PARTIALLY_FEASIBLE for the sampled static scale matrix, independently replayed
without new camera pairs; no production qualification.

Preserved experimental evidence: [dynamic output ownership report](design/STEP20C_DYNAMIC_OUTPUT_OWNERSHIP_PROBE.md)
and [source fixture](../tooling/probes/step20c-dynamic-output/README.md).
PARTIALLY_FEASIBLE for measured stable geometry/ownership, with explicit
fixture and unexercised-input limitations. The original temporary evidence
manifest was verified before an offline analyzer rerun replaced its bytes;
the report records this provenance limit.

[Rotated-output probe](design/STEP20C_ROTATED_OUTPUT_PROBE.md) and
[fixture](../tooling/probes/step20c-rotated-output/README.md): EXPERIMENTAL /
PARTIALLY_FEASIBLE for applied geometry, logical PNG/pointer, full-owner hide,
sampled damage and return. Pristine R90 capture and a Mosaic popup portion
actually crossing the boundary were not exercised; architectural clipping
conclusion UNDECIDED. STEP20C remains NEXT; production multi-output remains
NOT YET SUPPORTED.

[Static R90 partial-popup probe](design/STEP20C_ROTATED_PARTIAL_POPUP_CLIP_PROBE.md)
and [fixture](../tooling/probes/step20c-rotated-partial-popup/README.md):
EXPERIMENTAL / PARTIALLY_FEASIBLE. Mosaic B crossed x=0 by 72 logical pixels;
its H1 pixels and real button remained, while H2 matched its reference and
delivered no B button. Both standard controls drew and handled the overflow.
Independent clipped-away A input and saved buffers remain open. STEP20C is
NEXT; production multi-output is NOT YET SUPPORTED.

[Saved transaction buffer probe](design/STEP20C_SAVED_TRANSACTION_BUFFER_PROBE.md)
and [source fixture](../tooling/probes/step20c-saved-transaction-buffer/README.md):
EXPERIMENTAL / INCONCLUSIVE. Real held XDG configures created nonempty saved
scene buffers; private render entries and ACK/timeout removal were observed.
The Mosaic target was wholly off H1 after an applied relative camera scroll,
so the partial-boundary clipping gate was NOT EXERCISED. STEP20C stays NEXT.

[Saved target crossing probe](design/STEP20C_SAVED_BUFFER_TARGET_CROSSING_PROBE.md)
and [local source fixture](../tooling/probes/step20c-saved-buffer-target-crossing/README.md):
EXPERIMENTAL / PARTIALLY_FEASIBLE. One calculated camera correction produced
a real saved target crossing x=0 with clipped render and retained H1 pixels.
H2's target color was absent, but its whole-image reference differed by 253
pixels; Mosaic target timeout and held input remain unqualified. STEP20C
stays NEXT and production multi-output remains NOT YET SUPPORTED.
The offline freeze audit found an identical filled 11×23 Kitty cursor-color
rectangle across pristine and Mosaic captures. Cursor blinking is strongly
supported, not causally proven; a static H2 reference is the next gate.

[Saved target natural timeout and input gate](design/STEP20C_SAVED_TARGET_TIMEOUT_INPUT_PROBE.md)
and [local source fixture](../tooling/probes/step20c-saved-target-timeout-input/README.md):
EXPERIMENTAL / PARTIALLY_FEASIBLE. A static SHM H2 reference stayed
pixel-identical before, during and after one held Mosaic transaction. The
crossing target saved node rendered inside H1 and was removed after a real
timeout with the XDG client alive; sampled H2 input reached the reference.
Complete damage and GPU lifetime remain open. STEP20C stays NEXT and
production multi-output remains NOT YET SUPPORTED.

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

The [preserved edge source fixture](../tooling/probes/step20c-optimized-blur-edge/README.md)
records pinned reconstruction, offline checks and the exhausted four-slot ledger.

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

The [ABI/package source fixture](../tooling/probes/step20c-scenefx-abi-package/README.md)
records build-only reconstruction and non-graphical diagnostic commands.

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

The [static-contract source fixture](../tooling/probes/step20c-scenefx-static-contract/README.md)
preserves the bounded audit/staging procedure; all generated results stay external.

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

The [static focus/input/standard follow-up](design/STEP20C_STATIC_RUNTIME_FOCUS_INPUT_STANDARD_PROBE.md)
is **EXPERIMENTAL / INCONCLUSIVE**, architecture **UNDECIDED**. One run reused
the exact static binary, verified loaded wlroots/output geometry, calculated
camera and observed the applied clip. A fixture incorrectly required stored
current_border_width=0 under border none; actual IPC retained thickness 2 with
empty decoration and full-size client rectangles. The run stopped before any
PNG, click or splith transition. Those gates are NOT TESTED; no clipping defect
or need for an algorithm change is demonstrated. No retry/build/production
change occurred. A separately authorized corrected-fixture gate is required.
STEP20C stays NEXT; production multi-output remains NOT YET SUPPORTED.

The [static RGB/input/standard retest](design/STEP20C_STATIC_RGB_INPUT_STANDARD_RETEST.md)
is **EXPERIMENTAL / FEASIBLE for the tested matrix**; its evidence is frozen
for publication.
The corrected shared IPC predicate/replay pass before the sole unchanged-static-
binary run. Two full H2 references and all later H2 RGB are exact; H1 retains
182,214 target pixels, H2 zero, actual visible/reference/standard button pairs
are delivered only to the right client. Targeted splith removes the native clip
and retains ordinary pixels/input. The runner exits 1 only on terminal exit IPC
after completed measurements and compositor exit 0; that raw failure is retained
and separately diagnosed/revalidated offline. No algorithm, build, production,
package or UX change follows. Wider static popup/effect/lifecycle, complete
damage/generation, ABI/maintenance/notices gates remain open. D1–D4 persist;
STEP20C stays NEXT and production multi-output remains NOT YET SUPPORTED.

The preserved [static nested valid-grab probe](design/STEP20C_STATIC_NESTED_VALID_GRAB_PROBE.md)
is **EXPERIMENTAL / INCONCLUSIVE**, architecture UNDECIDED. The sole unchanged-
static-binary run verified actual identity, outputs, applied camera/tiled clip
and two exact whole-H2 references, then stopped before any click or popup on
an invalid painted-height assertion (573 vs native SHM320). An additional
IPC-y/titlebar assertion was also invalid. The recorded offline test PASS had
an insufficient source-assertion audit; raw runner exit1 and all evidence remain
immutable. Root/nested grabs, geometry, popup pixels/input/dismissal and splith
are NOT TESTED in this campaign. No algorithm/production/UX/package change or
retry; budget exhausted. Correct/replay geometry predicates offline before a
separately authorized fresh static popup gate. Historical failure evidence is frozen;
STEP20C NEXT, production multi-output NOT YET SUPPORTED.

The preserved [static nested geometry replay gate](design/STEP20C_STATIC_NESTED_GEOMETRY_REPLAY_GATE.md)
is EXPERIMENTAL / INCONCLUSIVE. True SHM/configure/paint geometry and nine
historical popup cases were replayed;145 historical asserts and2288 current AST
sites are classified, with partial executed coverage explicit.195 offline tests
pass, but independent review retains CORRECTION_REQUIRED: the readiness
aggregator accepts semantically incomplete proof records. Input correlation and
terminal-code repairs are accepted; no readiness or new static popup result.
No graphical run or execution reservation occurred. Close the residual offline
receipt-validation gate before proposing runtime. Architecture UNDECIDED;
STEP20C NEXT; production multi-output NOT YET SUPPORTED.

## Local receipt semantic integrity gate — offline only

The [R02 receipt-integrity gate](design/STEP20C_STATIC_NESTED_RECEIPT_INTEGRITY_GATE.md)
is local and experimental. The real writer/aggregate share semantic validation
through the existing immutable-data replay and R01 input correlation; typed
receipt content, scenario-specific omissions, AST/test inventories and final
review bindings are checked. Historical geometry evidence remains INCONCLUSIVE;
this correction cannot retroactively qualify static popups. The final local gate
is READY_FOR_NEW_RUNTIME: 206 offline tests pass, 13478 recorded invalid mutations
are rejected, and independent review accepts the final 18-source/15-receipt
bindings after one bounded B-01 writer repair. The actual writer returns READY
with five PASS markers and no blockers. R02 is RESOLVED for this offline fixture;
partial AST coverage and runtime limitations remain explicit. Phase B is
uncommitted and unpublished, and readiness only permits requesting a separate
future authorization. No compositor/runtime authorization,
production/UX/package change or STEP20D work follows. Architecture UNDECIDED;
STEP20C NEXT; production multi-output NOT YET SUPPORTED.


## Preserved static nested runtime handoff — experimental evidence

The [handoff and valid-grab report](design/STEP20C_STATIC_NESTED_RUNTIME_HANDOFF_AND_VALID_GRAB.md)
records PASS transfer/preflight and one unchanged-static-binary run, verdict
INCONCLUSIVE. Four genuine grabs and sampled E1/E2 Mosaic crossing pixels,
E1 visible/forbidden input and dismissal passed. E2 reached splith with mapped
popups and standard pixels, then a fixture root-window consistency predicate
rejected the old-to-cleared clip transition. Offline retained observations
support settled clip removal; standard A/B input, explicit child close/A survival
and final H2 restoration remain NOT TESTED. Raw runner/IPC exit1 and clean
compositor/client exits0 remain intact. No rerun or algorithm change; historical phase B
is preserved for publication by the E2 completion batch. Architecture UNDECIDED, STEP20C NEXT,
production multi-output NOT YET SUPPORTED; broader damage/generation/output/
effects/ABI/distribution gates remain open.


[Static E2 completion and private integration results](design/STEP20C_STATIC_E2_TRANSITION_AND_COMPLETION.md)
and [current fixture results](../tooling/probes/step20c-static-e2-completion/README_RESULTS.md):
EXPERIMENTAL. B 104 targeted offline tests PASS with independent acceptance;
C FEASIBLE for the sole static nested-popup standard-return/input/normal-close
matrix; D initial candidate BUILDABLE, accepted comment delta COMMENT-ONLY /
NOT REBUILT, distinct candidate graphics NOT TESTED. The original fixture
[README](../tooling/probes/step20c-static-e2-completion/README.md) is the sealed
pre-execution protocol, preserved byte-for-byte; current status is in
README_RESULTS. Historical INCONCLUSIVE verdicts remain unchanged. Final batch
audit is PASS / ACCEPTED, with publication identities recorded in Git history
and the private closeout receipt. Complete damage,
atomic generation, wider static graphics/output coverage, maintained ABI and
legal/maintenance gates remain open. STEP20C NEXT, production multi-output
NOT YET SUPPORTED; no production/UX/packaging contract change.

Preserved [overnight qualification dossier](design/STEP20C_OVERNIGHT_QUALIFICATION_AND_INTEGRATION_GATE_V1.md):
EXPERIMENTAL / PARTIALLY_ADVANCED, with a [fresh annotated rebuild and private stage](design/STEP20C_ANNOTATED_REBUILD_AND_PRIVATE_STAGE.md),
[18-run graphics matrix](design/STEP20C_ANNOTATED_GRAPHICS_MATRIX.md),
[lifecycle/effects/native-ordering limits](design/STEP20C_LIFECYCLE_EFFECTS_AND_NATIVE_ORDERING.md),
and [22-question production integration decision draft](design/STEP20C_PRODUCTION_INTEGRATION_DECISION_DRAFT.md).
The [compact source-only qualification index](../tooling/probes/step20c-overnight/qualification/README.md)
preserves exact identities, budget and private provenance references. Recommendation:
PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE; no production decision applied.
STEP20C NEXT; production multi-output NOT YET SUPPORTED. Final independent review is ACCEPTED / audit PASS for experimental evidence
fidelity. Documentary publication is prepared, not executed at this edition.

## Targeted STEP20C evidence — 2026-10-14

These new experimental reports supplement immutable historical evidence; they
do not supersede canonical contracts or qualify production. The targeted
campaign records 14 unique runs/125 PNG/520 reserved events. Raw runtime remains
INCONCLUSIVE for all terminal IPC exits, with measurement/scientific cleanup
separate. C3 observes native creation/draw/teardown partially, but stops on a
frozen predicate rejecting reused node addresses; no natural transaction timeout
or held/live PNG. Final independent review is ACCEPTED / audit PASS for experimental evidence
fidelity. Publication is authorized and prepared, not executed at this edition;
final refs belong to the private closeout and final handoff. STEP20C NEXT; production multi-output NOT YET SUPPORTED.

| Report | Scope and retained limits |
| --- | --- |
| [Targeted scale/popup gate](design/STEP20C_TARGETED_SCALE_AND_POPUP_GATE.md) | Own A/G scale1.25 grabs/pixels/input, sampled FEASIBLE; association bounded |
| [Targeted saved lifecycle](design/STEP20C_TARGETED_SAVED_BUFFER_LIFECYCLE.md) | Real held configure; C3 creation/draw/teardown partial; timeout/held PNG/GPU lifetime unqualified, INCONCLUSIVE |
| [Targeted effects/cache diagnosis](design/STEP20C_TARGETED_EFFECTS_CACHE_DIAGNOSIS.md) | Classic EXERCISED, whole-H1 FAIL, GPU attribution INCONCLUSIVE |
| [Targeted input/native ordering](design/STEP20C_TARGETED_INPUT_NATIVE_ORDERING.md) | Focus/camera mutation during click; 789/821 final paired, no atomic generation |
| [Release-shape extended matrix](design/STEP20C_RELEASE_SHAPE_EXTENDED_MATRIX.md) | Exact-G dynamic/hidden/R90, residual neutrality and ABI/package/legal limits |
| [Targeted closure decision](design/STEP20C_TARGETED_CLOSURE_DECISION.md) | Exact identities, 14-run matrix, risks and distinct lifecycle markers |
| [Production decision draft](design/STEP20C_PRODUCTION_INTEGRATION_DECISION_DRAFT.md) | Twenty current questions; PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE |

Public evidence: [results README](../tooling/probes/step20c-targeted-results/README.md),
[compact results](../tooling/probes/step20c-targeted-results/RESULTS.json) and
[artifact hashes](../tooling/probes/step20c-targeted-results/ARTIFACTS.json).
The 460 retained run artifacts include 125 output captures and three marker-source
PNGs (128 PNG files total); source PNGs are not output captures. The [review supplement](../tooling/probes/step20c-targeted-results/REVIEW.json)
is maintained separately by the parent. See the closure report for the exact private review
paths/hashes, 43 offline tests, 22 rejected mutations and finalization limits.

## Saved/input/GPU STEP20C batch — 2026-10-14

The [new gate dossier V2](design/STEP20C_GATE_CLOSURE_DECISION_V2.md) records a
separate six-run campaign:59 captures/240 reservations, 42 common and six GPU
offline tests passed; two optional runs were not exercised. The previous
14-run/125-capture/520-reservation campaign remains immutable.

Three saved runs exercise an actual native five-second transaction timeout
with client alive, held capture before deadline, normal owner close and exact
whole-H2 RGB through hold/timeout/final. C3 identifies target lifetime instance15
and natural node retirement; A/G qualify their own wire/RGB/timeout, without
native saved identity transfer. Target retirement release and GPU completion
remain NOT PROVEN. Two A/G input runs finish full/empty/full, focus/camera
mutations and targeted splith return. Temporally compatible applied state is
PARTIALLY_FEASIBLE, without proving atomic generation.

The distinct GPU diagnostic acquires108 native ROI reads and supports local
FBO history outside the fresh domain: first sampled fresh divergence is down-2,
not down-1. Whole-H1 A/B/A remains FAIL and whole-field causality INCONCLUSIVE;
no shader/cache correction follows. Native pairing is414/400/14 with unknown
missing-event causes; damage union coverage is sampled, not all-frame proof.
The bind-before-failed ordering already exists in pinned pristine SceneFX;
the old draft's contrary provenance claim is explicitly corrected in the new
[GPU report](design/STEP20C_GPU_FBO_CACHE_CAUSALITY.md), without historical rewrites.

Measurements, raw runtime exit, scientific cleanup and architecture remain
separate: all six global runtimes are INCONCLUSIVE on terminal IPC1; saved/input
helpers error32 keep scientific cleanup INCONCLUSIVE despite owner0, while GPU
clients error0 give scientific cleanup PASS. Mechanical process cleanup passes.
The private core is source-only ACCEPTED for bounded review, build/runtime/C
UBSan/OOM NOT RUN; no runtime result transfers. Whole-field GPU/lifetime,
atomic scene/input/present, full damage, instrumentation neutrality, exact-pair
maintenance, full package/notices/legal and release/security ownership remain
gates. Offscreen-popup UX and a particular atomic-counter mechanism remain
UNDECIDED. The applied rendering/input coherence contract remains required.

Recommendation PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE; scientific status
PARTIALLY_ADVANCED. Final dossier review ACCEPTED / audit PASS for experimental evidence fidelity;
documentary publication PREPARED at this edition, with actual refs in the private
post-push receipt. STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT;
STEP20D–G PLANNED; production multi-output NOT YET SUPPORTED. No production,
UX or package contract changes, and no authorization for further graphics runs.

New experimental batch reports: [saved natural timeout and epoch identity](design/STEP20C_SAVED_NATURAL_TIMEOUT_AND_EPOCH_IDENTITY.md), [input event time and applied camera](design/STEP20C_INPUT_EVENT_TIME_AND_APPLIED_CAMERA.md), [GPU FBO/cache causality](design/STEP20C_GPU_FBO_CACHE_CAUSALITY.md), [native present/damage/lifetime](design/STEP20C_NATIVE_PRESENT_DAMAGE_LIFETIME.md), [minimal private source-only core](design/STEP20C_MINIMAL_PRIVATE_INTEGRATION_CORE.md), [gate closure V2](design/STEP20C_GATE_CLOSURE_DECISION_V2.md) and [current integration draft](design/STEP20C_PRODUCTION_INTEGRATION_DECISION_DRAFT.md). The [fixture documentation](../tooling/probes/step20c-saved-input-gpu-batch/README.md) distinguishes sealed inputs from post-run results.

## Minimal private core build/runtime/GPU gate — 2026-10-14

This new campaign is EXPERIMENTAL / PARTIALLY_ADVANCED, recommendation
PRIVATE_CORE_NEEDS_TARGETED_EVIDENCE. It preserves the historical source-only
core while recording the new core 29baf31 build/C unit/local ABI/Stage1 evidence
and its own graphics. Twelve unique runs consume 88 output captures, with 90
retained PNG files including two source markers; no retry and two conditional
slots NOT EXERCISED. Fractional/R90 and resize/migration are sampled positive;
standard/vertical/fullscreen/hidden return remain incomplete. Native timeout
is observed on E6 before ACK/teardown, while its global validator fails. Core
whole-H1 return FAIL and distinct G1 rejected first epoch remain visible.

| Report | Scope and limits |
| --- | --- |
| [Build and C failure paths](design/STEP20C_MINIMAL_CORE_BUILD_AND_C_FAILURE_PATHS.md) | Exact parents/replay, six original UB reproductions, private camera guard, real C unit sanitizers, OOM abort/P1, ELF and Stage1 |
| [Core graphics qualification](design/STEP20C_MINIMAL_CORE_GRAPHICS_QUALIFICATION.md) | Eleven E runs, per-case measurements/exits/normal-client closure and missing controls |
| [Lifetime, damage and transactions](design/STEP20C_MINIMAL_CORE_LIFETIME_DAMAGE_AND_TXN.md) | Real timeout despite rejected receipt, sampled input/damage, native identity/GPU/atomic/complete-damage NOT PROVEN |
| [GPU full-field freshness follow-up](design/STEP20C_GPU_FULL_FIELD_FRESHNESS_FOLLOWUP.md) | Separate GPU 1905a20, one rejected epoch, modifier-aware fixture diagnosis without accepting raw readback |
| [ABI/package and integration decision](design/STEP20C_MINIMAL_CORE_ABI_PACKAGE_AND_INTEGRATION_DECISION.md) | Budget/identity/marker ledger, exact-pair/local stage limits, P0–P3 and human decisions |

The [compact source/provenance fixture](../tooling/probes/step20c-minimal-core-gate/README.md)
preserves reviewed fixture inputs and small evidence metadata; core bodies,
functional core patches, GPU hook, binaries, raw data and build trees stay in
the private LAB. Existing commands are provenance, not permission to replay
spent reservations. Scoped evidence delta review ACCEPTED; final independent
dossier review pending and documentary publication PREPARED at this edition.
Actual publication refs belong to the private post-push receipt/final handoff.
STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT; STEP20D–G PLANNED;
production multi-output NOT YET SUPPORTED. No production/UX/package change.

## Private CORE recovery, OOM and DCC gate — 2026-10-14

The new EXPERIMENTAL campaign is PARTIALLY_ADVANCED, recommendation
PRIVATE_CORE_NEEDS_TARGETED_EVIDENCE. Nine new runs consume102 output PNG and
120 reserved capture slots, no retry/compositor build/GPU build/stage. Targeted
standard/return/vertical/hidden/saved evidence is PARTIALLY_FEASIBLE; fullscreen
comparison and GPU whole-field remain INCONCLUSIVE. OOM production policy is
UNDECIDED; no production, UX or package contract is adopted.

| Report | Scope and limits |
| --- | --- |
| [Standard, vertical and fullscreen recovery](design/STEP20C_CORE_STANDARD_VERTICAL_FULLSCREEN_RECOVERY.md) |12 homologous standard RGB exact, two-chain return and Y600 crossing; fullscreen NOT_EXERCISED/non-equivalent |
| [Hidden and saved lifecycle recovery](design/STEP20C_CORE_HIDDEN_SAVED_LIFECYCLE_RECOVERY.md) | Same-chain hidden return and phased timeout/ACK/SHM closure; native identity NOT_OBSERVABLE |
| [Modifier-aware GPU validation](design/STEP20C_GPU_DCC_MODIFIER_AWARE_VALIDATION.md) | Per-plane repair, full epoch effective halfpixel rejection, GL/read limits, G2 NOT_RUN |
| [Mandatory clip OOM options](design/STEP20C_MANDATORY_CLIP_OOM_POLICY_OPTIONS.md) | A abort/P1, private B/C studies,40 expected commands/six mutants; production policy UNDECIDED |
| [Qualification decision V3](design/STEP20C_CORE_QUALIFICATION_DECISION_V3.md) | Identities, budget, raw exits versus targeted verdicts, native/ELF/stage gates, prepublication markers |
| [Current integration draft](design/STEP20C_PRODUCTION_INTEGRATION_DECISION_DRAFT.md) | CORE-specific matrix, OOM/coherence/UX/maintenance/legal decisions and rollback boundary |

The [new source fixture](../tooling/probes/step20c-core-recovery/README.md)
links provenance, scoped reviews and compact results. Nested submission
editions remain frozen; later review receipts clarify their limited acceptance.
Public EOF-only normalization is explicitly reversible; executed LAB sources
and historical archives remain unchanged. Final deep audit/publication pending
at this edition; actual postpublication identities belong to the private receipt.
STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT; STEP20D–G PLANNED;
PRODUCTION_MULTI_OUTPUT NOT_YET_SUPPORTED; PRODUCTION_AUTHORIZED FALSE.

[CORE-C preallocation/native/GPU precision dossier](design/STEP20C_COREC_PREALLOCATION_NATIVE_AND_GPU_PRECISION.md)
and [evidence-only receipts](../tooling/probes/step20c-corec-prealloc-gate/README.md):
EXPERIMENTAL / **BLOCKED**, recommendation and OOM policy **UNDECIDED**.
Historical LAB deletion prevents mandatory seal/exact-source/GPU-hook
verification; 0/979 entries and 0/916 files reverified. Five offline commands
exit 1 with explicit missing-input/EDQUOT limits. No new native tests, builds,
stages, runs or captures; no CORE-C identity or GPU observation contract
qualified. Historical reports remain unchanged. Next step is a separately
scoped provenance-gate instruction or exact authoritative inputs restored
from an existing backup. STEP20C NEXT; production multi-output
NOT_YET_SUPPORTED; PRODUCTION_AUTHORIZED FALSE.
