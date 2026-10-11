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
15. [STEP20A](STEP20A.md) and [STEP20B](STEP20B.md): historical evidence.

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

A proposal does not supersede accepted canonical contracts or assert implementation status. Its open feasibility items must be resolved before implementation.

## Roadmap and historical reports

| Document | Role | Purpose |
| --- | --- | --- |
| [Roadmap](ROADMAP.md) | Planning | Step goals, exit criteria, required documentation |
| [STEP20A](STEP20A.md) | Historical | Native foundation implementation evidence |
| [STEP20B](STEP20B.md) | Historical | First scrollable-row implementation evidence |

STEP reports record what was observed and decided at the time. They are **not** the canonical source for current behavior. When a STEP report conflicts with current canonical documentation, the canonical documentation wins. The original French reports are preserved as historical artifacts; their opening notices point here.
