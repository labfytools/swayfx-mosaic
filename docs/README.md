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
11. [STEP20A](STEP20A.md) and [STEP20B](STEP20B.md): historical evidence.

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

A proposal does not supersede accepted canonical contracts or assert implementation status. Its open feasibility items must be resolved before implementation.

## Roadmap and historical reports

| Document | Role | Purpose |
| --- | --- | --- |
| [Roadmap](ROADMAP.md) | Planning | Step goals, exit criteria, required documentation |
| [STEP20A](STEP20A.md) | Historical | Native foundation implementation evidence |
| [STEP20B](STEP20B.md) | Historical | First scrollable-row implementation evidence |

STEP reports record what was observed and decided at the time. They are **not** the canonical source for current behavior. When a STEP report conflicts with current canonical documentation, the canonical documentation wins. The original French reports are preserved as historical artifacts; their opening notices point here.
