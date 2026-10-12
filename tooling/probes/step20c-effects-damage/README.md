# STEP20C effects and damage source fixture

**EXPERIMENTAL / PARTIALLY_FEASIBLE for the measured matrix.** This fixture
only builds and runs disposable private headless copies. It does not install
or modify SwayFX, SceneFX, wlroots, the daily IPC socket, the cumulative
Mosaic production patch or `PKGBUILD`.

## Pinned inputs and private adaptation

Start from a full clone of this repository containing commit
`542d9b9c945b22cf9134a4a643c8dc763b34607d`. `prepare.sh` delegates
to the preserved temporal-damage preparer, which pins private Mosaic
`cd550382b311efdbfe3ed892f4e1d281d852e754`, SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc` and wlroots `0.20.2`.
The preserved presentation-identity patch then observes native output
commit/present callbacks in the private Mosaic copy.
It then applies `effect-glass.patch` **only to the lab copy** of the
pre-existing nested Wayland SHM client and compiles it as C17. That patch
changes the top buffer to premultiplied ARGB `0x88442010` so the underlying
64×64 wallpaper's 8-pixel `#f5f5f5` / `#0f192d` stripes remain visible.
The opaque buffer path stays unchanged. The patch does not touch compositor
rendering or scheduling. The normal private clip and damage patches are
those preserved by the earlier fixtures.
For a separate passive-node trace, set `STEP20C_EFFECT_TRACE=1` when calling
`prepare.sh`. This applies `effect-trace.patch` only to the private SceneFX
copy and recompiles it. Its `FX_TRACE` records node type, enabled flag,
geometry, draw region and optimized dirty flag. Compare its outputs with
the default untraced run before using it as visual evidence.

## Reproduction

From the full clone, with user-local build dependencies already available:

```sh
sh tooling/probes/step20c-effects-damage/prepare.sh
python tooling/probes/step20c-effects-damage/run.py "$LAB" control --camera-pairs 0
python tooling/probes/step20c-effects-damage/run.py "$LAB" private_standard --camera-pairs 0
python tooling/probes/step20c-effects-damage/run.py "$LAB" private_mosaic --camera-pairs 1
python tooling/probes/step20c-effects-damage/analyze.py "$LAB" \
  "$LAB"/runs/control-effects-* \
  "$LAB"/runs/private_standard-effects-* \
  "$LAB"/runs/private_mosaic-effects-*
```

Read the exact `LAB=` path printed by `prepare.sh`; the code block uses it
as a shell variable for brevity. Pass only the chosen three run directories
to the analyzer when exploratory runs also exist. The runner uses the lab's
private runtime, private discovered `SWAYSOCK`, 120-second deadline,
40-capture and 35-MB limits. It uses ordinary IPC commands; it never
addresses the desktop session. `run.py` builds a local adaptation of the
preserved applied-state runner inside the lab; the generated Python file is
an artifact, not a tracked source.

The geometry is HEADLESS-1 `(-800,0)`, HEADLESS-2 `(0,0)`, both 800×600,
scale 1, normal transform. HEADLESS-2 has a floated `wev` reference. The
owner is the same nested SHM client in all three modes. `gaps inner 24`
is applied in all three modes. The standard layouts move the owner to the
right edge, so ordinary shadow overflow enters HEADLESS-2. Mosaic uses
`scroll_x 400`, then at most three `400→1280→400` camera pairs. Captures
are lossless PNG and all coordinates in them are output-local.
The reference keeps its natural floating size at `(250,250)`; an earlier
late-resize variant produced inconsistent reference rendering and is
retained as a fixture limitation. `--camera-pairs 0` allows native-event
or instrumentation controls without repeating the three camera pairs.
`--reference-resize` reproduces that retained variant, including its
known limitation. The original camera campaign used it; the final native
event supplement kept the natural reference size and used zero pairs.
The final runner counts camera pairs across the lab's retained runs and
locks the campaign against concurrent runners. A fresh lab permits at most
three pairs in total; subsequent trace/native controls must use
`--camera-pairs 0`. The executed ticket predates this guard and actually
ran 15 pairs over reproduction/trace variants, exceeding the requested
three-pair bound. All such runs are retained and manifested; this protocol
deviation limits the campaign qualification and is not hidden by selecting
a three-pair subset.

FX0 disables shadow and blur. FX1 enables shadow with `shadow_blur_radius
16`, `shadow_offset 30 0`, and `shadow_color #000000A0`. FX2 disables the
shadow and enables blur with radius 5 and three passes. FX3 additionally
enables `blur_xray`; this is **only an optimized-blur candidate** until a
dirty/cache transition is observed. FX4 enables both effects. T6 toggles
and closes the ordinary owner; T7 exits Mosaic through `layout splith`.

The analyzer records per-capture SHA-256, 800×600 dimensions, monotonic
capture windows, output-local fixed ROIs, whole-image and ROI differences,
per-transition pixel/damage comparison, and a complete raw-evidence SHA-256
manifest in `$LAB/effects-damage-results/`. A control without private
damage instrumentation records damage coverage as unknown. Its manifest
covers all files in the selected run directories plus the wallpaper PNG;
source hashes are recorded separately in the report. Old exploratory runs
are not silently substituted for selected comparable controls.
`--include-all-raw-runs` includes every retained run in the evidence
manifest while measuring only the explicitly chosen comparable runs.

## Measured result and limits

In the selected three-run matrix, both standard controls show a 27,594-pixel
shadow overflow in the first 46 columns of HEADLESS-2. Mosaic changes zero
pixels there. FX1 is invisible on the sampled Mosaic interior, even after
adding gaps, so its permitted interior rendering is **INCONCLUSIVE**.
FX2 produces 112,308 changed pixels on the standard HEADLESS-1 images and
319,734 on Mosaic; contrast of the eight-pixel stripe edges falls markedly,
establishing a real blur beyond alpha compositing. HEADLESS-2 stays
unchanged by that Mosaic blur. Three camera returns exactly reproduce the
pre-hide FX4 PNGs. Private damage extents cover the pixels changed between
selected settled captures, but are not proof of minimum damage or every
intermediate frame. The tiled FX2 path can already select optimized blur
when containers cannot overlap; FX3's `blur_xray` therefore does not
necessarily choose a different path. Optimized nodes and dirty=1/0 entries
were observed, but independent cache invalidation correctness, T3
out-of-viewport shader sampling, popup effects and saved buffers remain
**NOT TESTED**. The report
also retains an instrumentation-neutrality limitation: enabled shadow
(type 3), optimized blur (type 4) and regular blur (type 5) entries were
traced. Standard-layout PNGs matched the untraced run, but traced Mosaic
omitted the visible `wev` reference despite its mapped IPC tree entry.
The primary pixel claims use the untraced matrix. The report contains the
numerical evidence and the exact lab and manifest hashes.

## Freeze V1 independent replay

The 2026-10-12 audit rebuilt from `/tmp/step20c-effects-freeze-v1-clone`
at the pinned repository HEAD into `/tmp/swayfx-mosaic-nested-grab-xbAPurbe`.
The commands above consumed one pair total, with 18/18/24 captures and no
fixture failure. Historical evidence remains separate and nonconforming.
The reference-geometry audit found 640×480 versus 300×250 in the selected
untraced/traced Mosaic runs; instrumentation causality remains unknown.
See the report for verified historical and new manifest hashes and limits.
