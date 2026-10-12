# STEP20C buffer identity fixture — EXPERIMENTAL

The [protocol](../../../docs/design/STEP20C_OUTPUT_BUFFER_IDENTITY_PROBE.md)
records the wlroots 0.20.2 and SceneFX 0.5 lifetime audit before this private
instrumentation. Reconstruct only in a disposable lab from the published
[presentation fixture](../step20c-presentation-identity/README.md). Its
`prepare.sh` starts from published Mosaic commit
`006adf69d7364181917cfc266863794b6d13a65b`, using pinned SwayFX
`fd71a6bdc061bd633b488ae7b83e8a6981d22f86`, private Mosaic
`cd550382b311efdbfe3ed892f4e1d281d852e754`, private SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc`, and the historical
patches. The new [`buffer-identity.patch`](buffer-identity.patch), SHA-256
`d62e8c3a166e60a6eb394de58f51da1e37c3e7ac49671a361bd106ac64e2b427`,
applies after `presentation-events.patch` to private
`sway/desktop/output.c` only. It changes no renderer, clipping decision,
public ABI or installed library.

## Rebuild and replay

Requires the presentation fixture's dependencies plus Pillow for RGB
normalization. `BI_OUTPUT_DIR` must be a new private directory. The runner
creates its own runtime, Wayland socket and explicit IPC socket. It never
uses the daily session. The buffer patch caps snapshots at 80 × 1,920,000
bytes, holds at most one extra HEADLESS-1 buffer lock, and releases it on
matching present, any subsequent repaint, rejected commit, timeout or output teardown.
The timeout is two seconds. A second read is limited to three buffers that
actually reach `present` while locked: visible, hidden and visible after
return. Four other selected buffers in the final run were released by an
instrumentation scope defect: a HEADLESS-2 repaint called global
`bi_release_hold("superseded")` while it held a HEADLESS-1 buffer. Their
later native `present` events do not establish retention or byte stability
through presentation. The historical patch and traces preserve this
negative result.

The historical five-source manifest includes the README before this
scientific rectification, SHA-256
`add56c3de06671fd14bbb504456f1339eaaa7d0209f11444a9cb940f3435aa59`.
That version is retained in the private lab as
`buffer-fixture-README-before-rectification.md`. A fresh `prepare.sh`
creates a manifest for the current corrected README; do not replace the
historical manifest or patch hash.

```sh
prep=$(sh tooling/probes/step20c-buffer-identity/prepare.sh)
printf '%s\n' "$prep"
LAB=$(printf '%s\n' "$prep" | sed -n 's/^LAB=//p')
(cd "$LAB" && sha256sum -c presentation-source-sha256.txt && \
    sha256sum -c buffer-source-sha256.txt)
mkdir "$LAB/buffers-final"
BI_OUTPUT_DIR="$LAB/buffers-final" PYTHONDONTWRITEBYTECODE=1 \
  python tooling/probes/step20c-buffer-identity/run.py \
    "$LAB" private_mosaic buffer_cycles --cycles 3
RUN=$(find "$LAB/runs" -maxdepth 1 -type d -name 'private_mosaic-buffer_cycles-*' | sort | tail -1)
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-buffer-identity/analyze.py \
  "$LAB" "$RUN" "$LAB/buffers-final"
```

For a timing control, repeat the same `buffer_cycles` invocation without
`BI_OUTPUT_DIR`, sequentially, using the same private binary. The probe
still logs stages but performs no buffer readback. For the initial
logical/applied camera lag, run a separate one-pair case with
`BI_INCLUDE_TRANSIENT=1` and a new output directory. Pointer `visible`,
`b_cross` and `hidden_click` scenarios can be run separately with the
[negative-origin fixture](../step20c-negative-origin/README.md) against this
same private lab. Standard `splith` controls use the ordinary presentation
runner, once each for `control` and `private_standard`.

The analyzer writes `LAB/results/{commits,presentations,buffer-lifetime,
buffer-fingerprints,scene-states,correlation,pixel-analysis,matrix,summary}.json`.
The raw files are XRGB8888 readback copies with stride 3200. It preserves
raw SHA-256 and a top-down RGB SHA-256. The actual output-state source is a
GBM DMA-BUF; the CPU data-pointer attempt returned false in the measured
renderer, so the successful read is through SceneFX FX texture APIs. The
pixel comparison uses the declared XRGB8888 read format and actual
source/destination defaults, not an assumed source GBM format. The private
patch's texture read calls SceneFX's internal `glFinish()`; the result is
timing-sensitive and cannot be treated as a neutral observation.

## Measured laboratory

`/tmp/swayfx-mosaic-nested-grab-QwCf4FLm/` retains the final three-pair
run, no-readback control, transient-camera run, three separate pointer runs,
two `splith` controls, private build and copied buffers. The final three-pair
run `private_mosaic-buffer_cycles-1791774958990683685` had 80 native commits,
78 native presents and two initial sequence-2 commits with no present
observed. All 32 selected true output buffers were read, confirmed in the
synchronous native commit callback and paired to a native headless present.
Twenty-eight extra locks were released on that event; four were released
early by HEADLESS-2 repaint before their later `present`. The same owner ID 8
and one A/B map persisted
through all three pairs. The three second reads (visible, hidden, visible)
matched their precommit raw bytes. The transient run separately read the
buffer for native HEADLESS-1 sequence 10 at logical 1760/applied -1120.

The [report](../../../docs/design/STEP20C_OUTPUT_BUFFER_IDENTITY_PROBE.md)
records the limited **PARTIALLY_FEASIBLE** result and measured readback
timing impact. Generated builds, logs, PNGs, sockets and copied buffers
remain outside Git. STEP20C is NEXT; multi-output Mosaic is NOT YET
SUPPORTED.
