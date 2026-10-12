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
24. [STEP20A](STEP20A.md) and [STEP20B](STEP20B.md): historical evidence.

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
