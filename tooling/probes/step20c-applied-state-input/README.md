# STEP20C applied state / input fixture — EXPERIMENTAL

The [protocol](../../../docs/design/STEP20C_APPLIED_STATE_INPUT_PROBE.md)
was written before this fixture. This directory will retain only source
patches, preparation, runner and analysis code needed to reconstruct a
disposable private headless laboratory. Its inputs are the frozen
[buffer fixture](../step20c-buffer-identity/README.md), not production
Mosaic or installed SceneFX. Generated builds, buffers, PNGs, logs,
sockets and manifests remain in a named private `/tmp` laboratory.

**Status: EXPERIMENTAL / PARTIALLY_FEASIBLE.** The distinct
[`applied-state-input.patch`](applied-state-input.patch) applies after the
frozen buffer patch and changes only private `output.c`, `transaction.c`,
`cursor.c` and `seat.c`. It leaves clipping and hit decisions untouched.
The patch's SHA-256 is
`8a0766536fa728a6be6ef29aea3be67abbfad107f2fcd6048718097499a4d88f`.

## Rebuild and bounded replay

```sh
prep=$(sh tooling/probes/step20c-applied-state-input/prepare.sh)
printf '%s\n' "$prep"
LAB=$(printf '%s\n' "$prep" | sed -n 's/^LAB=//p')
(cd "$LAB" && sha256sum -c asi-source-sha256.txt)
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-applied-state-input/run.py \
  "$LAB" private_mosaic buffer_cycles --cycles 3 --asi-mode 0 \
  --max-seconds 120 --max-captures 100
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-applied-state-input/run.py \
  "$LAB" private_mosaic buffer_cycles --cycles 3 --asi-mode 1 \
  --max-seconds 120 --max-captures 100
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-applied-state-input/run.py \
  "$LAB" private_mosaic buffer_cycles --cycles 3 --asi-mode 2 \
  --max-seconds 120 --max-captures 100
```

Mode 0 logs without a probe lock/read. Mode 1 samples only three buffers
after both A/B have mapped, in order visible 400, hidden 1280, returned
400. Mode 2 reads these again only during their matching headless present
while the owned reference remains. The runner creates a private runtime,
Wayland display and IPC socket, bounds captures, then stops its process
groups. Standard and pointer controls reuse the frozen negative-origin
runner against the same private binary, with scenario `visible`, `b_cross`
or `hidden_click` and geometry `negative`. Use
`analyze.py LAB RUN` for each run; outputs go to `LAB/results-asi/RUN/`.

For controlled lifetime paths, run one pair with mode 1 and `--test-hold`:
the first already-presented buffer stays held until a subsequent real
HEADLESS-1 buffer commit. Use `--test-timeout` instead to pause 2.3 seconds
and observe the two-second post-commit timer. These switches are private
fault injections; normal mode does neither. Rejected commits and output
destruction were not injected in the measured campaign.

## Interpretation

`asi_applied_epoch` is an experimental counter incremented after private
popup position/clip arrangement and after a transaction's root arrangement.
It can increment even if the sampled state does not change and misses
direct client-buffer, effect, animation, damage, output and other SceneFX
mutations. Matching values show only that these instrumented sites did not
run between observations; they are not a native atomic scene/input
generation. `ASI_HIT` records the executed scene node-at result;
`ASI_DELIVERY` records the seat's focused surface before wlroots button
notification. XDG grabs may alter delivery, so the client log is the
separate final observation. No input event is assigned a frame ID.

The selected source buffer is GBM XB24. The successful read path uses FX
texture readback to XRGB8888; it can synchronize GPU/CPU. Each selected
copy is 1,920,000 bytes. The private hold is keyed by output and native
commit sequence. HEADLESS-2 repaint cannot release a HEADLESS-1 hold;
configuration-only commits do not replace it. The one-slot-per-output
model releases on matching present, accepted same-output replacement,
timeout or output destruction. Its two-second timer begins after readback
and commit; it cannot bound a stalled GPU readback call.

## Measured lab

`/tmp/swayfx-mosaic-nested-grab-l2HvAkRe/` contains trace-only, three-
buffer selective and second-read modes, one-pair replacement and timeout
injections, three Mosaic pointer scenarios and two `splith` controls.
The [report](../../../docs/design/STEP20C_APPLIED_STATE_INPUT_PROBE.md)
records exact runs, counts, hashes, limits and status. Generated evidence
is outside Git. STEP20C stays NEXT; multi-output Mosaic remains NOT YET
SUPPORTED.
