# Static focus/input/standard-return fixture

EXPERIMENTAL / FROZEN HISTORICAL FAILURE. No production integration.
Read the [protocol](../../../docs/design/STEP20C_STATIC_RUNTIME_FOCUS_INPUT_STANDARD_PROBE.md).
The previous static campaign remains sealed and is never replayed.

This fixture creates one campaign-owned LAB outside Git, copies the hash-qualified
static compositor unchanged and rebuilds only three historical C17 clients from
manifest-verified source/generated protocols. The old client executables were
not manifest entries, so their observed hashes are contextual only. An exclusive
`~/swayfx-mosaic-static-followup-v1.owner` file binds the campaign to one LAB.
Never delete/reset it, its ledger, or replace the LAB to retry.

Offline checks before launch:

```sh
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-runtime-followup/test-budget.py
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-runtime-followup/test-offline.py
```

Historical commands, preserved for provenance only — DO NOT execute prepare.py
or run.py again; the historical budget is exhausted:

```sh
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-runtime-followup/prepare.py
# Use the printed LAB path; execute the retained exact fixture copy there.
PYTHONDONTWRITEBYTECODE=1 python "$LAB/fixture/run.py" "$LAB"
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-runtime-followup/collect.py "$LAB"
```

The flock ledger reserves run, PNG, named click, camera and pointer moves before
execution. No refund/reset. Runtime is private mode 0700; all swaymsg use explicit
-s, child environments discard inherited desktop sockets. Only owned process
groups are stopped. The deadline is 150 seconds, per-log bound 64 MiB. Sources,
raw protocol/client/scene logs, PNGs, IPC snapshots, timestamps, serials, exit
codes and result manifests stay external. The collector creates manifests once;
verification is read-only with `collect.py "$LAB" --verify`.

Reference border none is applied to its measured con_id, never to the shared
App ID (which also identifies the H1 filler). H2 full RGB must be identical
before input; no crop/tolerance. Clicks use measured painted interiors. The
standard-return command explicitly targets the H1 con_id after H2 gains focus.
Popup tests and native output-buffer/PNG identity remain NOT TESTED.

The protocol describes independent source reconstruction for a future authorized
campaign if historical binaries disappear. Do not silently rebuild or substitute
the compositor in this campaign. Historical LAB paths identify retained evidence,
not a permanent production dependency.

## Actual execution — no retry permitted

LAB `/home/fy59/swayfx-mosaic-static-followup-nhwejz6u`, run consumed.
Verdict INCONCLUSIVE, architecture UNDECIDED. The runner stopped before the
first PNG because it incorrectly required current_border_width=0 after border
none. Actual IPC had border none, stored width 2, empty deco_rect and 800×600
window_rect. The filler retained normal decorations; target/workspace 1 were
focused. The source confirms that border none changes the border enum, not
stored thickness. This is a fixture defect, not an observed rendered border.

The executed runner is intentionally unchanged, including the erroneous predicate.
It is historical experimental source, not a validated replay harness. A future
authorized campaign must correct that semantic check and add its regression
before a separately budgeted run; this campaign may not be resumed or repeated.
No PNG, click or splith command was executed. Camera 0→160 and applied clip were
observed. All principal RGB/input/standard gates remain NOT TESTED. The collector
records those omissions explicitly and verifies owned-process/socket cleanup.

## Freeze receipt

The preservation task verified every entry of the original 24-source and
46-evidence manifests without rewriting them. All Python files match the
sealed final-fixture; run.py matches the historical executed fixture, including
the invalid width assertion. Offline tests and --verify remain read-only
checks of this exhausted campaign. Publication preserves INCONCLUSIVE /
UNDECIDED, zero PNG and zero clicks; it does not convert the fixture into a
validated runner. A new campaign uses a separate directory and budget.
