# STEP20C temporal damage fixture — EXPERIMENTAL

This fixture tests repeated popup lifecycle and camera transitions only at
HEADLESS-1 `(-800,0,800,600)` and HEADLESS-2 `(0,0,800,600)`, scale 1,
normal transform. The [protocol and verdict rules](../../../docs/design/STEP20C_TEMPORAL_DAMAGE_PROBE.md)
were recorded before this fixture. It does not alter the production build,
package, session or SceneFX ABI. It produces sampled PNGs, not every
presented frame.

## Inputs and preparation

Start from a full Git clone containing Mosaic `cd550382` and the preserved
STEP20C fixtures. The wrapper invokes the negative-origin `prepare.sh`, which
clones pinned SceneFX `37ccd723bef49e6891156ffafce8f549f01446cc` and
Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754` into a new temporary
lab, applies the unchanged private SceneFX/Mosaic/hidden-owner patches,
builds both privately, generates protocol headers and compiles the pointer.
`client-cycle.patch` is the only new C adaptation: it permits explicit A
closure and fresh configure/map on later cycles. It is applied to a private
copy of the preserved nested client and compiled as C17. No installed library
or compositor is modified. The preparation output names both the lab and
build log; the lab's `temporal-source-sha256.txt` records all private patch,
client and runner inputs. Compare its hashes before a replay.
A full clone containing this fixture can run `prepare.sh` directly. The source
manifest verifies the scripts and patches used by each private lab. Do not
copy any generated lab files into Git.

The separate `scenefx-timing.patch` applies after the preserved SceneFX clip
patch and adds only monotonic damage timestamps plus a local output-commit
ordinal/result. It touches no public header, rendering buffer or clip rule.
An accepted output commit is not proof of a presented frame. The initial
uninstrumented campaign remains in its own laboratory for comparison.
SwayFX bypasses SceneFX's `wlr_scene_output_commit` in its normal repaint
path, so that SceneFX hook emits no commit records here. The independent
`mosaic-output-timing.patch` logs the actual private SwayFX
`wlr_output_commit_state` call, with the same monotonic clock and an
experimental process-local ordinal. It changes neither the decision to
commit nor the output state.

| New private patch | SHA-256 |
| --- | --- |
| `client-cycle.patch` | `119fa0b61135bb49bf84c42499799f1c75cccbf5842ea5acac9eaaba6ab7b9ca` |
| `scenefx-timing.patch` | `7a7ef1875b559f65a3240a0016592da1da6a8537929d0e96b8aaa2d20ecd46fa` |
| `mosaic-output-timing.patch` | `4419059231e038675f50a6321889f27ba981c5d8df2779ccbc4a61e02f1d6668` |

The reused SceneFX, Mosaic and hidden-owner patch hashes are recorded in the
[negative-origin fixture](../step20c-negative-origin/README.md). The fresh
lab's source manifest verifies their exact bytes again.

Dependencies are those of the [negative-origin fixture](../step20c-negative-origin/README.md),
plus Pillow for analysis. Current measured environment: SwayFX 0.6,
wlroots 0.20.2, SceneFX 0.5.0, Wayland client 1.26.0. Other versions require
separate validation.

```sh
prep=$(sh tooling/probes/step20c-temporal-damage/prepare.sh)
printf '%s\n' "$prep"
LAB=$(printf '%s\n' "$prep" | sed -n 's/^LAB=//p')
(cd "$LAB" && sha256sum -c temporal-source-sha256.txt)
```

## Bounded campaign

Every invocation creates a unique `LAB/runs/` directory. The three modes
are `control` (unmodified `/usr/bin/sway` in `splith`), `private_standard`
(private Mosaic binary in `splith`) and `private_mosaic` (same binary in
`mosaic`). Each has its own mode-0700 `/tmp/mtd-*` runtime and private sockets.
The runner removes only its own process groups and runtime, including on
failure. It never inherits the daily `SWAYSOCK` or `WAYLAND_DISPLAY`; all IPC
commands use the discovered `swaymsg -s` path.

```sh
for mode in control private_standard private_mosaic; do
  PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-temporal-damage/run.py \
    "$LAB" "$mode" cycles --cycles 10
done
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-temporal-damage/run.py \
  "$LAB" private_mosaic camera --moves 36
for mode in control private_standard private_mosaic; do
  PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-temporal-damage/run.py \
    "$LAB" "$mode" outside
done
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-temporal-damage/run.py \
  "$LAB" private_mosaic hidden_click
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-temporal-damage/run.py \
  "$LAB" private_mosaic toggle
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-temporal-damage/analyze.py "$LAB"
```

The command above requests 36 individual camera transitions per mode, or
18 complete outward/return pairs. Defaults cap one run at 900 seconds, 400
captures, 250 MB of PNGs, 30 cycles and 40 camera transitions per mode.
`--max-seconds`, `--max-captures` and `--max-bytes`
can lower the resource limits. Each run retains config, IPC snapshots, PNGs
on both outputs, monotonic action/capture records, XDG/Wayland client log,
pointer/wev/compositor logs, exit status and structured analysis. `SPIKE_DAMAGE`
lines are extracted to `damage.log`; they are output extents, not frame
identities. `TEMPORAL_DAMAGE` and `TEMPORAL_OUTPUT_COMMIT` add monotonic order without
converting sampled PNGs into presented-frame evidence. The analyzer writes
per-run `damage-analysis.json` and summaries under `LAB/results/`. Full raw
logs and captures remain under each run for independent recomputation.

`S0`/`S1`/`S2`/`S3`/`S4`/`S5`/`S6`/`S7` phase names match the protocol.
S6 includes an actual A right-button event after B is destroyed. The
`hidden_click` run is separate from camera hiding without clicks: it expects
child-first `popup_done` and no popup button at the hidden point.
Immediate and later `grim` captures are separately named. Camera mode records
settled transitions, capture-paced transitions, and a separate burst with no
capture between consecutive commands (a capture after each fourth command).
They are sampled observations; IPC acceptance and process exit zero alone do not prove render
correctness. The analyzer's fixed left ROI `(400,90,800,310)` and right ROI
`(0,90,200,310)` are output-local and were chosen before inspecting temporal
results. Dynamic `wev` text on HEADLESS-2 prevents whole-image equality there;
exact popup colors and client events are evaluated separately. No region is
masked after observing an anomaly.

## Validation and cleanup

```sh
sh -n tooling/probes/step20c-temporal-damage/prepare.sh
PYTHONDONTWRITEBYTECODE=1 python -c 'import ast,pathlib; [ast.parse(p.read_text()) for p in pathlib.Path("tooling/probes/step20c-temporal-damage").glob("*.py")]'
(cd "$LAB" && sha256sum -c temporal-source-sha256.txt)
git diff --check
```

Inspect each `analysis.json`, `exit-status.json`, raw log and sample PNG before
accepting its verdict. Keep failed cases and their exact run path. Remove a
finished laboratory only by its printed path after preserving needed proof;
never perform global `/tmp` cleanup or touch historical labs.
