# Documentation

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
