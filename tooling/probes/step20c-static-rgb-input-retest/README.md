# Static RGB, input and standard-return retest fixture

EXPERIMENTAL / FROZEN EVIDENCE. No production integration.
Read the [protocol](../../../docs/design/STEP20C_STATIC_RGB_INPUT_STANDARD_RETEST.md).
The historical failed campaign is frozen and must never be rerun.

`ipc_predicates.py` supplies pure validators shared by replay and the real runner.
`replay.py` uses actual sealed historical IPC/scene/client observations and
clearly labelled historical PNGs or synthetic input fixtures. Negative tests
must reject wrong identities/ownership/geometry/focus/clip and malformed input.
`pixels.py` compares every RGB pixel, preserves differences, measures actual
paint and selects points with a 20-pixel interior margin. `support.py` and
`test-budget.py` implement/test durable exclusive no-refund reservations.

Offline preparation, client-only C17 checks and gates:

```sh
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-rgb-input-retest/test-budget.py
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-rgb-input-retest/prepare.py
# LAB is the one newly printed path, registered in the exclusive owner file.
PYTHONDONTWRITEBYTECODE=1 python "$LAB/fixture/replay.py" --lab "$LAB"
```

Preparation copies the exact qualified static binary, verifies the unchanged
historical manifests, builds only exact historical clients and freezes the
fixture inventory. No Mosaic or SceneFX build is allowed. `replay.py` verifies
source authority, syntax and ledger tests and records the two mandatory PASS
markers. `run.py` verifies the immutable inventory and all gates before its
first run reservation. Never replace the owner file, reset the ledger, modify
the executed fixture or create a second lab to retry.

Only after every gate passes, execute the single retained runner:

```sh
PYTHONDONTWRITEBYTECODE=1 python "$LAB/fixture/run.py" "$LAB"
PYTHONDONTWRITEBYTECODE=1 python "$LAB/fixture/collect.py" "$LAB"
PYTHONDONTWRITEBYTECODE=1 python "$LAB/fixture/verify.py" "$LAB"
```

One static run, zero pristine runs/builds, one camera correction, three named
right clicks, eight movements including click positioning, twelve PNGs and
150 seconds. Reservations precede work and remain consumed on failure.
Headless/private mode-0700 runtime only, explicit swaymsg -s, owned process
groups, bounded logs and cleanup. No inherited daily IPC or library override.
The collector seals source/evidence once, verification never rewrites them.
Generated C protocols, clients/binaries/builds/logs/PNG/sockets stay outside Git.
Actual observations and final verdict are recorded below after collection.

## Post-run collection distinction

The exact executed fixture remains immutable in LAB/fixture. The measurements
completed, but its final `swaymsg exit` returned 1 after normal compositor exit.
Raw runtime.json and runner code/status are preserved. `validate_results.py`
independently rechecks actual PNG, IPC/scene, real recipient events, focus,
layout/clip and cleanup, and rejects changed RGB, invisible delivery, retained
clip or abnormal compositor exit. It accepts terminal transport only after all
scientific measurements, explicit exit, compositor code 0 and terminal EPIPE.
The post-run collector is retained separately in LAB/postrun-fixture, with its
own source inventory. Run that collector/validator for this completed campaign;
do not substitute it for the historical executed fixture or rerun the compositor.

## Measured result (one run, no retry)

LAB `/home/fy59/swayfx-mosaic-static-rgb-input-retest-hn67lnhq`.
Scientific FEASIBLE for the exact matrix, architecture
STATIC_MOSAIC_RGB_INPUT_STANDARD_FEASIBLE_FOR_TESTED_MATRIX. The executed runner
exited 1 only on final exit IPC; compositor exited 0 after every measured gate.
Raw failure is retained, never rewritten as a successful runner execution.
271 damage traces are partial evidence, not every-frame qualification.

H2 six PNGs are whole-RGB identical; 182,214 target pixels on H1, zero H2.
Actual target visible serials 35/36, reference 48/49, standard target 67/68;
wrong clients have no button delivery. Real H1 splith/clip removal measured,
standard H1 paint 226,908 pixels. Budget run 1, camera 1, PNG 8, clicks 3,
movements 6 including click positioning, duration 9.142914 seconds. No second run.

Source manifest 31 entries SHA-256
`cb812ae3a27c9715efce2e1b2cfd36f315ea897d003c77944f688bc931861f1e`;
evidence 93 entries SHA-256
`209196b2857381db7a856347dcce45cd3ee33c48c2db0c73777fc982d01ad568`.
Every entry verifies; runner/pre-run inventory and post-run collector are
separate retained sources. Result additions here are later documentation.

Read-only final validation (no recording into sealed results):

```sh
PYTHONDONTWRITEBYTECODE=1 python "$LAB/postrun-fixture/validate_results.py" "$LAB"
PYTHONDONTWRITEBYTECODE=1 python "$LAB/postrun-fixture/verify.py" "$LAB"
```

No production readiness, broad static/shared equivalence, popup/effect/buffer
qualification, full damage/generation or exhaustive ABI approval. STEP20C NEXT,
production multi-output NOT YET SUPPORTED. The completed retest sources and report are preserved for publication.
Any later static nested-grab campaign is separate and remains local, uncommitted
and unpublished. No installation or system/session change.
