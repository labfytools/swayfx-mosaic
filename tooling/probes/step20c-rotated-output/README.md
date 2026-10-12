# Rotated-output source fixture

**EXPERIMENTAL / PARTIALLY_FEASIBLE evidence fixture.** The
[protocol](../../../docs/design/STEP20C_ROTATED_OUTPUT_PROBE.md) records the
scientific question, pinned source audit, geometry/capture gates, strict global
action budget and stopping criteria before dynamic execution. All generated
sources, builds, clients, sockets, captures, logs and manifests belong in one
private temporary LAB, never in Git or the running desktop session.

The fixture must reuse the published source-only private patches unchanged.
The pristine SwayFX control remains free of Mosaic changes. No live IPC,
installed library, package or production algorithm may be modified.

## Measured campaign and replay boundary

Laboratory: `/tmp/swayfx-mosaic-nested-grab-TJ3AhbCE`. The source-only
preparer was the preserved `step20c-dynamic-output/prepare.sh`; it rebuilt
pristine SwayFX, private Mosaic/SceneFX and strict C17 clients in a new LAB.
The rotation runner generates a bounded child from the published applied-state
runner, with the corrected two-reference calibration and a five-marker
asymmetric wallpaper. `--source-only` checks generated Python without launch.
`test-budget.py` exercises the real lock/ledger offline.

```sh
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-rotated-output/test-budget.py
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-rotated-output/run.py "$LAB" control --source-only
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-rotated-output/run.py "$LAB" private_standard --source-only
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-rotated-output/run.py "$LAB" private_mosaic --source-only
```

The actual three modes have already been attempted in this LAB. **Do not run
those mode commands again.** The pristine control's R90 reservation was
consumed before a fixture assertion incorrectly expected IPC `270`; the
applied output actually reported user-facing `90`, physical 750×1000 and
logical 800×600. No pristine R90 PNG or R0 return is available. The two
private modes completed R0→R90→R0. Their five-marker captures establish
that `grim -s 1.25` returns a logical-oriented 1000×750 PNG even while the
physical buffer is 750×1000. Private `splith` has 15,860 B-color overflow
pixels on H2; private Mosaic has zero A/B-color pixels there in the sampled
R90 states. The Mosaic B box ends at logical-PNG `x=903`, before the
`x=1000` boundary: the zero H2 count is **not** a partial-clip challenge.
One Mosaic camera hide/return pair and a subsequent B button delivery were
observed. The global result is PARTIALLY_FEASIBLE and the architectural
partial-clipping conclusion is UNDECIDED.

The complete measured evidence and result caveats are in the report. The
analyzer reads raw events, screenshots and private logs offline. An initial
sealed `results/` analysis counted spill but missed the Mosaic-box geometry
confound. The second sealed `results-corrected/` analysis identified that
confound; a final `results-final/` analysis derives the owner ID and B box from
each run rather than using historical ID/box constants. Earlier directories
remain byte-for-byte preserved and chained by manifests. The analyzer refuses
to overwrite any sealed directory.
Original dynamic, fractional, SceneFX and other earlier fixture patches are
unchanged. No new passive instrumentation patch was needed.
