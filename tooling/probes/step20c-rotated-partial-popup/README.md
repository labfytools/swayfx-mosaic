# Static R90 partial popup fixture

**EXPERIMENTAL / PARTIALLY_FEASIBLE.** See the
[scientific report](../../../docs/design/STEP20C_ROTATED_PARTIAL_POPUP_CLIP_PROBE.md).
The fixed placement is `rot_cross`: A (360,80), 480×170; B (210,60),
300×130; toplevel 420×320. It was fixed before the three runs.

Use a new private LAB and a locked ledger; the previous rotation laboratory
and its consumed budget are read-only. The runner must use startup R90 config,
one run per mode, explicit private sockets, at most 16 captures per run and
120 seconds. No production source, clipping algorithm, installed library or
daily session changes are permitted. Generated files remain outside Git.

The completed LAB is `/tmp/swayfx-mosaic-nested-grab-PioJ5X43`; its ledger
has consumed all three runs. **Do not run those modes again or reset the
ledger.** Source-only preparation in another authorized campaign uses:

```sh
sh tooling/probes/step20c-rotated-partial-popup/prepare.sh
```

This rebuilds pinned private sources and applies `rot-cross-client.patch`
to the [nested client](../step20c-nested-grab/nested-client.c), whose base
SHA-256 is `2e40c98af72a0df8b316810589a0be8f4425a763db1de448b49a7813956b6f7d`.
The patch preserves earlier placements and adds only `rot_cross`.
`prepare.sh` does not launch a compositor.

The completed campaign used these one-run commands, in order:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tooling/probes/step20c-rotated-partial-popup/test-budget.py
PYTHONDONTWRITEBYTECODE=1 python3 tooling/probes/step20c-rotated-partial-popup/run.py "$LAB" control
PYTHONDONTWRITEBYTECODE=1 python3 tooling/probes/step20c-rotated-partial-popup/run.py "$LAB" private_standard
PYTHONDONTWRITEBYTECODE=1 python3 tooling/probes/step20c-rotated-partial-popup/run.py "$LAB" private_mosaic
PYTHONDONTWRITEBYTECODE=1 python3 tooling/probes/step20c-rotated-partial-popup/analyze.py "$LAB"
```

`LAB/results/` contains structured analysis; `LAB/runs/` contains raw
captures, client/protocol events, applied traces and per-run exit codes.
The source manifest covers 910 files and the evidence manifest 146 files;
their final SHA-256 values are recorded in the scientific report.
Mosaic B crossed by 72 logical pixels, remained visible/clickable on H1
and was absent from H2 pixels/client delivery. Both standards visibly
crossed. Independent forbidden-side A input was not tested, so the verdict
stays PARTIALLY_FEASIBLE.
