# STEP20C optimized blur edge history and instrumentation gate

**EXPERIMENTAL / protocol recorded before new fixture development.**
The separate cache evidence freeze passed at
`e749653ccda42abad9a66a11009be6043b5b6f62`, directly verified on Forgejo
and GitHub with a clean main. The completed experimental evidence is preserved for publication. STEP20A DONE, STEP20B EXPERIMENTAL, STEP20C NEXT, STEP20D–G
PLANNED. Production multi-output Mosaic is NOT YET SUPPORTED.
No UX, production source, cumulative patch, PKGBUILD, system dependency,
shader, rendering algorithm or ABI change is authorized.

## Evidence and competing hypotheses

The [V1 cache probe](STEP20C_OPTIMIZED_BLUR_CACHE_PROBE.md) already established
actual FX/GLES 3.2, BACKGROUND cache source, optimized selection, natural
A/B/A dirty/rebuild/copy, fresh central 80,000 pixels, stable whole H2,
sampled clipping/damage/teardown. Its whole-H1 B-natural/B-explicit differences
were 36,776 private splith and 33,915 Mosaic; A-initial/A-return differences
38,308 and 35,340, maximum RGB delta 6. Common boundary ROI counts were
19,007 and 20,486. These are not excluded or dismissed as rounding.
C0 failed before captures through duplicate configure-driven initial images;
its second image was charged after observation, a reservation deviation.
The corrected client ACKs configures without drawing. Historical sources,
PNGs, logs, manifests and ledger stay intact; no V1 run is repeated.
Instrumentation neutrality and pristine graphical behavior were NOT TESTED.

| Hypothesis | Discriminating evidence | Limit |
| --- | --- | --- |
| H1 reduced-domain FBO history | Source-domain audit, spatial distributions, offline pinned-kernel predictions, identical-source repeat | Native tail content is not read; correlation cannot establish GPU causality |
| H2 new cache traces | R2/R3 same source/library/binary/client/config, OPT_TRACE alone varies | Independent timing; equality is sampled neutrality, not universal proof |
| H3 shared SceneFX property | Completed R0 pristine versus R1 private splith and R2/R3 | Private clipping and older passive traces differ from pristine |
| H4 blur command cycle state | B unchanged during one disable/enable, client events, configuration, native R3 dirty/rebuild | Cycle rearranges blur and dirties all outputs; not identical to source-only commit |
| H5 another observed rendering factor | Geometry, alpha, source colors, renderer, timing, filtering, presentation evidence | Do not invent an unobserved explanation |

## Fixed comparative matrix and binary differences

| Run | Compositor / layout | New cache traces |
| --- | --- | --- |
| R0 | pristine SwayFX 0.6 / splith + pristine SceneFX 0.5 | absent, no private patches |
| R1 | private historical compositor / splith | OPT_TRACE absent |
| R2 | same private compositor / mosaic | OPT_TRACE absent |
| R3 | identical private compositor / mosaic | OPT_TRACE=1 |

Pinned pristine SwayFX `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`, Mosaic
`cd550382b311efdbfe3ed892f4e1d281d852e754`, SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc`, compatible installed wlroots 0.20.
Private builds apply unchanged inherited clip/popup/guard/timing/presentation
patches and the exact V1 cache/source trace patches. R1/R2/R3 load the same
library and binary. Their old SPIKE/TEMPORAL/PI traces are always active;
"trace-off" means the new OPT cache/source logs are disabled, not all logging.
OPT_LOG tests getenv presence, so OPT_TRACE=0 is not trace-off. Only presence
changes for R2/R3. Borrowed trace-only reads outside OPT_LOG remain in both.
No neutral instrumentation claim precedes the graphics. B does not modify
those patches or add renderer instrumentation.

## Geometry, graphical inputs and parameters

Two headless outputs only: H1 HEADLESS-1 at (-800,0), H2 HEADLESS-2 at (0,0),
both 800×600 physical/logical, scale=1, transform=normal. Record actual IPC
rect/mode/scale/transform and PNG dimensions. No rotation, scaling, hotplug,
resize, migration, popup, saved-buffer episode, animation or stress test.
At most one initial Mosaic camera correction calculated from actual applied
camera and glass geometry; no hide/return pair or P1–P3 camera change.

Reuse V1 deterministic SHM patterns exactly: BACKGROUND layer on H1, opaque
8-pixel stripes A=(245,245,245)/(15,25,45), B=(32,192,224)/(176,32,64).
Same 800×600 XRGB image for each reserved commit. Glass premultiplied ARGB
0x88442010, transparent ARGB filler, static XDG SHM reference H2. No terminal
cursor or animation. XDG configure-driven size submissions are logged separately
from the three explicitly reserved background images. No background configure
may submit pixels. Require two independent whole-H2 captures equal before FX2.

Fixed blur radius=5, passes=3, noise=0, brightness=contrast=saturation=1,
xray=off, shadows=off, corners=0, compositor opacity=1. Audit pinned command
syntax/source; save applied container/tree and startup config. Acceptance is
not effect evidence: exposed stripe colors calibrate the source; FX0/FX2
central contrast reduction demonstrates actual filtering. R3 must additionally
show FX renderer, optimized node under blur_tree, BACKGROUND path, optimized=1,
selected FBO, successful rebuild and cache copies. Other runs provide config,
source and pixel evidence without fabricated absent OPT traces.

## Pre-registered regions and comparisons

All coordinates below are output-local half-open physical rectangles:

| Region | Rectangle |
| --- | --- |
| glass center | (520,100,720,500), 80,000 pixels |
| exposed source | (20,100,160,500) |
| historical right boundary | (720,50,800,550) |
| physical right diagnostic | (750,0,800,600) |
| physical bottom diagnostic | (0,550,800,600) |
| whole H1 / whole H2 | (0,0,800,600) |

No diagnostic region is an exclusion. Every full-equality comparison uses all
800×600 RGB pixels. Intra-run full images always remain reported. Inter-layout
comparisons use only actually homologous source/common glass rectangles and
explicitly retain distinct glass extents (historically splith x=400, Mosaic
x=480); R0/R1 and R2/R3 full-image equality requires matching applied geometry.
Measure changed pixels, max channel delta, mean absolute channel delta,
per-channel amplitude histogram, bounding box, changed-pixel count per column
and per row, every ROI, H2 full differences, capture hashes and timestamps.

## One deterministic sequence per reserved run

P0: connect and map background with initial bufferless commit; wait/ACK all
layer configures, assert no image submitted, reserve then command A once.
Map filler/glass/static H2, settle actual geometry/focus and initial camera.
Capture FX0 H1/H2, later independent H2. Assert source colors and stable H2.
Enable scoped glass blur, settle, capture FX2 H1/H2; verify filtering.
P1: reserve and command B exactly once, keep blur/geometry unchanged, settle,
capture H1/H2. P2: no client image; reserve one explicit cycle, scoped blur
disable then enable with ordinary commands, settle and capture H1/H2.
P3: reserve and command A once, keep all else fixed, settle, capture H1/H2;
one later H1 confirmation must match whole RGB. Total 12 PNG per run.

Settling uses client command receipt, unchanged applied IPC geometry, at least
350 ms without intentional mutation before each measured capture; last H1
has an independent 350 ms confirmation. Native R3 logs are checked for source
commit/rebuild before capture and competing events in capture windows. Earlier
states lack duplicate H1 PNGs under the finite budget; that limits claims of
stability, especially if event/capture windows disagree. No screenshot gains
a native output-buffer identity from proximity to a commit or present.

Comparisons: FX0 A/FX2 A, P0 FX2/P3 A, P1 B/P2 B, R0/R1 homologous states,
R2/R3 homologous states, and common edge regions across layouts. Inspect
source A/B/A submission order, sizes, events and frame timing before attribution.
No deliberate focus, resize, camera, alpha, radius, passes or source mutation
outside this sequence. If a second unreserved A submission appears: abort,
retain evidence, consume reservation, no rerun, dependent results INCONCLUSIVE.

## Sampling and command audit before graphics

Inspect pinned render_blur_segments/get_main_buffer_blur, blur1.frag/blur2.frag,
texture filter/wrap, FBO allocation and written/sampled regions. For each of
six passes document full framebuffer size, freshly written domain, mapping,
radius/taps, bilinear texels beyond the valid domain, possible historical value
and expected final influence. Domain sizes for 800×600 are down 400×300,
200×150,100×75 then up 200×150,400×300,800×600, inside full-size FBOs.
Full-texture GL_CLAMP_TO_EDGE is distinct from reduced valid-domain clamp.
The offline model uses ideal bilinear sampling and 8-bit rounding, not native
mediump GLES precision, and must be reported as hypothesis only.

Audit cmd_blur: scoped container blur flag and arrange_container, then dirty
all output nodes. Natural BACKGROUND commit dirties its own output. Therefore
P1 and P2 need not traverse identical scene/rebuild sequences. Preserve native
R3 evidence of H1/H2 counts and scene/damage. No shader modification, forced
FBO clearing or GPU readback is authorized. If needed, propose only a later
bounded selective-readback protocol after results; do not execute it here.

## Budgets, isolation and preflight gate

One new LAB, one persistent campaign ledger in the home directory, exclusive
flock, atomic durable replacement, exact schema validation. Four run slots
R0–R3, each once; at most 3 background images, 1 blur cycle, 12 PNG, 150 s.
Global max 12 images,4 cycles,48 PNG; one initial calibration per Mosaic run,
zero camera pairs. Reserve before every launch/action; failed reservations
remain consumed, no refund/reset/new-LAB bypass/fifth run.

Before any compositor launch: Python AST, shell syntax if applicable, offline
ledger exhaustion/corruption/concurrency/cross-LAB tests, actual layer callback
ACK/no-draw harness, explicit-command audit, SHM widths/formats/bounds/lifetimes,
Wayland globals/listeners/output naming/protocol hashes, C17 -Werror, both
SceneFX and compositor builds, Meson mosaic-model, all pinned patch checks,
private linker identities, cleanup/timeouts. Fixtures are standalone and
corrected; C0 originals and historical LAB remain untouched.

Each run has private mode-0700 XDG_RUNTIME_DIR, private WAYLAND_DISPLAY,
explicit SWAYSOCK and swaymsg -s, WLR_BACKENDS=headless. Strip inherited daily
socket/display/library/trace variables; use private SceneFX LD_LIBRARY_PATH.
Record binary/library hashes, /proc/PID/maps, renderer logs, IPC, configs,
client sources, runner exact source, PNGs, capture windows, logs and exits.
Terminate only owned process groups; controlled IPC exit first, preserve
return codes, reap clients, remove only owned runtime/socket directory.
25 MB per raw log and watchdog bound resource use. No live desktop IPC,
killall/pkill, install, sudo, dotfiles, QuickShell or Codex changes.

Stop consumed failing controls; continue other predefined independent slots
only if safe/meaningful, never relaunch to get a favorable result. Critical
fixture/budget/isolation violation stops affected dependent execution. Compiler
or offline preflight issues may be corrected before the first reserved run.

## Result evidence and classification

Keep build/renderer-identities, private-trace-comparison, pristine-control,
source-commits, graphic-states, output-geometries, blur-settings, cache-use,
dirty-events, regeneration-events, edge-pixel-analysis, column/row-distribution,
sampling-domain-audit, edge-model-comparison, damage-analysis, capture-windows,
campaign-budget, matrix, summary and source/evidence SHA-256 manifests in
LAB/results. Generated files/builds/logs/PNG/socket/bytecode never enter Git.
The source-only fixture must rebuild from the pinned versions.

FEASIBLE requires complete comparable pristine and trace controls, coherent
cache contract, absent or natively explained compatible edges, correct allowed
Mosaic pixels and no forbidden contribution/regression. PARTIALLY_FEASIBLE
means valid majority of controls but native cause or edge property remains
open. INCONCLUSIVE means controls/fixture cannot distinguish hypotheses.
BLOCKED needs a demonstrated required invariant violation, reproducible crash,
forbidden contribution or blocking standard regression; low RGB amplitude
alone is insufficient. Architecture: OPTIMIZED_EDGE_CACHE_FEASIBLE_FOR_TESTED_MATRIX,
OPTIMIZED_EDGE_CACHE_REQUIRES_REDESIGN or UNDECIDED. Distinguish a shared SceneFX
issue from Mosaic clipping. Answer Q1–Q17 from the retained evidence after
execution; recommend minimal GPU study or ABI/package gate explicitly.

## Retained execution and measured result (2026-10-13)

`SWAYFX_MOSAIC_OPTIMIZED_BLUR_EDGE_CAUSALITY_PROBE=PARTIALLY_FEASIBLE`.
Architecture: **UNDECIDED**. LAB:
`/home/fy59/swayfx-mosaic-optimized-edge-a55yjb8n/`.
All four controls completed and were comparable in their defined domains.
The old pristine failure did not recur: duplicate layer configures were ACKed
without another image. No run failed, was repeated or exceeded a budget.
The original pre-result protocol is retained as LAB/protocol-before-results.md.

| Run | Duration | A/B images | PNG | Blur cycles | Initial camera corrections | Compositor exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R0 pristine splith | 4.995 s | 3 | 12 | 1 | 0 | 0 |
| R1 private splith, OPT absent | 4.293 s | 3 | 12 | 1 | 0 | 0 |
| R2 private Mosaic, OPT absent | 4.638 s | 3 | 12 | 1 | 1 | 0 |
| R3 same private Mosaic, OPT=1 | 4.652 s | 3 | 12 | 1 | 1 | 0 |

Total 4/4 runs,12/12 images,48/48 PNG,4/4 cycles,2/2 initial corrections,
zero camera pairs. The home-directory ledger is permanently exhausted for
run slots. Every mutation/capture/cycle/calibration reservation preceded its
operation; failed-reservation tests used independent offline temporary ledgers.
Clients report Wayland EPIPE=32/code 1 after controlled compositor exit; these
teardown statuses are retained, not compositor crashes. Owned children were
reaped and all four runtime/socket directories removed.

### Actual sources, geometry and rendering

Every run uses the real FX renderer, OpenGL ES 3.2, Mesa 26.2.4-arch1.1,
AMD Radeon 780M. /proc/PID/maps establishes the private pristine SceneFX in R0
and the same private patched SceneFX in R1/R2/R3, together with installed
wlroots 0.20.2. Installed package/library series are SceneFX 0.5.0, Wayland
client 1.26.0 and wayland-protocols 1.49. The build-identity JSON records
all archive revisions, exact patch hashes, library and executable digests.
Private compositor SHA-256:
`0c87ece70aa012207de951e9d558c81c5c4b3ea78548b943477bf12543264042`;
private SceneFX:
`78daf506d9aacdd0b1a05605f73b4103ee48cd0b5900a3574671b5ec11f07fe7`.
Pristine compositor:
`8ac865481bc0487344210cd0e16d8e6c7655b29db887cd58ddc11b0ca22fe494`;
pristine SceneFX:
`7a07c1f239043f7910039670006a2f6e9bb15608bf2a840576476c5f7b1378b3`.

IPC/output records and all PNGs confirm fixed 800×600 scale-1 normal outputs
at (-800,0)/(0,0). Standard glass is 400×600, global x=-400; Mosaic source
scene glass is 640×600 at global x=-320, crossing x=0 by 320. Mosaic's initial
camera 480 receives the measured delta -320 and becomes 160. Tiled scene
translation/clip and regular blur final draw yield output-local
[480,800)×[0,600); no target regular blur draw is seen on H2 in R3. The
private scene-state traces in R2 agree. Neither P1–P3 focus, camera, geometry,
alpha nor blur parameters are deliberately changed. Stored IPC trees confirm
stable applied geometry/focus/camera during measured states.

Exposed source ROI matches every stripe pixel exactly for A/B/B/A; glass
ARGB, source image dimensions and SHM lifetime remain fixed. Container opacity
1 is source-defined (container_create alpha=1), with no opacity mutation;
ordinary IPC here does not expose an opacity/blur-parameter getter. R3 actual
regular-blur strength=1, radius=5, passes=3 and optimized=1/selected FBO=11
corroborate source/config/pixel evidence. No getter observation is fabricated.
FX0/FX2 central luminance standard deviation falls 51.165618→0.132211 and
adjacent luminance contrast 12.351341→0.015453 in every run. Actual filtering
is visible beyond alpha compositing. Source mutation changes the central
80,000 pixels and whole 480,000 H1 pixels; B's center equals explicit B exactly,
and returned A's center equals initial A exactly. Six whole-H2 captures in
each run, including two independent preflight images, are pixel-identical.
All 24 H2 PNG hashes equal the historical static-reference hash
`4471e93ccb6cf3ff4970f61fce405431a228af598d2f1f030a3b7586962ecd7a`.

### Full-image and pre-registered edge comparisons

| Comparison | R0 pristine | R1 private splith | R2 Mosaic OPT absent | R3 Mosaic OPT=1 |
| --- | ---: | ---: | ---: | ---: |
| B natural → B explicit, whole H1 | 36,776 | 36,776 | 33,915 | 33,915 |
| A initial → A returned, whole H1 | 38,308 | 38,308 | 35,340 | 35,340 |
| Maximum channel delta, both comparisons | 6 | 6 | 6 | 6 |
| Center changed pixels, both comparisons | 0 | 0 | 0 | 0 |
| H2 changed pixels, every comparison | 0 | 0 | 0 | 0 |
| Last A → independent H1 confirmation | 0 | 0 | 0 | 0 |

R0/R1 have zero whole-H1 RGB differences at all six homologous capture states.
R2/R3 likewise have zero at all six states; H2 also matches across runs.
Runner bytes, config, compiled client, private binary and loaded private library
are identical in R2/R3. New OPT logs are absent in R0/R1/R2 and present in R3;
old private logs remain active in R1/R2/R3. Thus no measured graphical effect
of activating new traces exists in this matrix. Different frame timing remains
observable, and universal instrumentation neutrality is not established.
Standard/Mosaic whole-H1 differs by 48,000 pixels at every state because glass
coverage is x=[400,800) versus [480,800). The entire common glass
[480,800)×[0,600) and exposed source are exact across layouts at every state.
This comparison does not exclude any intra-run full-image difference.

| Pre-registered edge region | B natural/explicit standard | B natural/explicit Mosaic | A initial/return standard | A initial/return Mosaic |
| --- | ---: | ---: | ---: | ---: |
| Historical boundary (720,50,800,550) | 19,007 | 19,007 | 20,486 | 20,486 |
| Physical right x=[750,800) | 23,119 | 23,119 | 22,948 | 22,948 |
| Physical bottom y=[550,600) | 15,992 | 13,139 | 15,793 | 12,825 |

Historical boundary max delta is 4 for B and 5 for A; physical bands reach 6.
Whole-H1 mean absolute channel error is 0.083278/0.083215 standard (B/A) and
0.076682/0.076858 Mosaic. Right-band means are 0.866344/0.857756; historical
boundary means 0.515933/0.524808. These small per-channel means do not erase
the tens of thousands of different pixels. Whole-image bounding boxes are
[400,800)×[0,600) standard and [480,800)×[0,600) Mosaic. Column/row arrays
and amplitude histograms retain every changed pixel. In Mosaic only 103 B
and 1,963 A differences lie outside the union of the pre-registered right
50 columns and bottom 50 rows; no pixels are discarded. Rows near the bottom
and columns near the right reach all visible glass pixels; fine quantization
also leaves sparse differences just inside the bands.

For Mosaic B, changed-pixel maximum amplitudes 1/2/3/4/5/6 occur
17,174/8,705/3,825/4,073/130/8 times. For Mosaic A return they occur
19,009/8,177/5,093/2,394/652/15 times. Channel-level histograms and standard
counts are in edge-pixel-analysis.json; this is not an assertion of ordinary
rounding as the cause. No perceptual or daily-session assessment was run.

### Natural versus explicit path, native timing and damage

R3 P1 B and P3 A each contain one mapped BACKGROUND source commit,
one H1 dirty/rebuild/result=1, two completed cache texture-copy draw calls,
one dirty clear and optimized glass use. H2 has zero reconstruction in those
windows. P2 contains no background image commit, six dirty-set observations,
two successful H1 and two successful H2 reconstructions, eight completed copy
draw calls and four dirty clears. This is consistent with scoped cmd_blur
arrangement and its unconditional all-output invalidation, not a claim that
natural and explicit updates execute the same GPU sequence. The fixed cache
objects/FBO sizes are reused; source/configuration do not change radius/passes.
Copy draw completion is not a driver fence or per-pixel intermediate readback.

All R3 relevant reconstructions finish at least 357.899 ms before H1 capture;
no source commit/reconstruction trace occurs inside the measured capture
windows. The final H1 confirmation is identical after another 350 ms.
Earlier states do not have duplicate H1 PNGs under the finite budget, and
untraced controls lack OPT quiescence evidence. Their deterministic inputs,
stable applied state, settled windows and exact cross-run pixels support the
comparisons without claiming every intervening frame.

For four stabilized R3 H1 transitions, union of available native output-state
damage extents leaves zero changed pixels uncovered. Old private scene damage
in R1/R2 is retained separately and is not promoted to equivalent output-buffer
damage proof. Pristine has no new native damage trace. Commit/present traces
keep their own IDs; no screenshot is assigned an exact native presented buffer.
No all-frame, minimum-damage, physical-presentation or input claim follows.

### Sampling domain and fixed offline model

Pinned shaders are byte-identical pristine/private. FBOs stay 800×600; the
written domains are down 400×300,200×150,100×75 and up
200×150,400×300,800×600. Down taps use 2*(p+0.5)-0.5 with ±5-pixel offsets;
up taps use (p+0.5)/2-0.5 with axial ±2.5 and diagonal ±1.25. GL_LINEAR
requires neighboring texels. First downpass sees a complete source, with
full-texture clamp; later downpasses and all upsample passes can reach past
the fresh reduced domain while remaining inside the texture. No full color
clear appears between these blur passes. Alternating full-size ping-pong FBOs
can retain earlier regions. The audited source demonstrates this possibility;
it does not identify the native value actually read there.

The exact V1 functions are reused without executing its historical writer,
with the actual eight H1 R3 rebuild timestamps and source order. No kernel,
offset or rounding fitting is performed. Model/native historical-edge mean
absolute channel error spans 0.198700–0.518242; 96.668–97.911% of channels
are within one level, maximum residual 4 in that ROI. The broader physical
right and glass-bottom domains reach model/native residual 6. For B, model
predicts 32,129 changed visible-glass pixels versus native 33,915, mask Jaccard
0.861863. For A, 37,701 versus 35,340, Jaccard 0.805086; predicted maximum
7 versus native 6. Delta residual means in visible glass are 0.049901 and
0.056941. The residual and spatial distributions are preserved, not hidden.
This is strong history compatibility, not equivalence to native mediump GLSL
or a causal measurement of intermediate FBO contents.

| Hypothesis | Result for tested matrix |
| --- | --- |
| H1 reduced-domain history | Supported by source possibility and fixed-model spatial/amplitude agreement; native causality UNDECIDED |
| H2 new trace activation causes these edge differences | Not needed to reproduce: pristine and private OPT-off show them; R2/R3 graphical effect zero; universal neutrality NOT PROVEN |
| H3 shared rendering property | Supported: pristine/private splith complete RGB identical; common glass across layouts identical |
| H4 blur cycle alters more than source cache content | Demonstrated arrangement/all-output dirty and additional reconstructions; exact RGB contribution of each side effect remains unresolved |
| H5 another observed rendering factor | Native mediump versus ideal-model residual and timing differences remain limits; geometry/source/alpha/parameters are controlled; no alternate native cause demonstrated |

### Required architectural answers

| Question | Evidence-backed answer |
| --- | --- |
| Q1 pristine edges? | Yes: R0 reproduces exact standard counts and full images of R1. |
| Q2 standard and Mosaic? | Yes: common visible glass is exact; full counts differ with coverage. |
| Q3 without new traces? | Yes: R0, R1 and R2 reproduce the edge differences. |
| Q4 measurable trace effect? | Zero RGB difference in six R2/R3 states; timing differs. Neutrality is sampled, not universal. |
| Q5 same reconstruction steps? | Same source-defined blur/copy functions, different trigger/scene/output sequence: natural 1 H1 versus explicit 2 H1+2 H2. No intermediate GPU state equivalence proved. |
| Q6 blur-command contribution? | Container blur flag/arrangement and all-output dirty, with extra reconstructions observed. Their separate pixel effects cannot be isolated here. |
| Q7 central freshness? | Yes for the predefined 80,000 pixels: changes with B, exact explicit B and exact returned A in all four runs. |
| Q8 domains localize anomalies? | Right/bottom bands contain most differences; fixed model overlaps strongly but imperfectly. Not an exact causal localization. |
| Q9 source permits stale-domain sampling? | Yes: later down and up supports cross reduced fresh bounds inside full-size textures. Actual sampled old value remains unobserved. |
| Q10 level of proof? | Source possibility plus offline prediction and native final pixels; no intermediate native causality. |
| Q11 amplitude/distribution? | Max channel 6, tens of thousands of pixels, detailed rows/columns/ROIs/histograms above and in JSON. Not dismissed as rounding. |
| Q12 Mosaic clip? | Correct for sampled final draw: H1 x=[480,800), no target draw on H2, whole H2 exact. Not a universal clipping/input proof. |
| Q13 damage? | R3 extent union covers every stabilized changed pixel in four transitions; no all-frame or screenshot/native-buffer identity claim. |
| Q14 correction justified? | Reproducible shared history-sensitive edge output warrants an upstream investigation; no Mosaic-specific correction or required invariant violation is established. No algorithm correction authorized. |
| Q15 smallest next readback? | Selected seam texels and four destination pixels per B condition at D1/D2/U2, bounded protocol below; not executed. |
| Q16 blocker or separate limitation? | Shared SceneFX edge limitation, not a demonstrated Mosaic blocker. Whole-cache/native-cause gate remains open and prevents a global FEASIBLE claim; it need not block an independent ABI audit. |
| Q17 proceed ABI/package? | Yes, an isolated read-only ABI/package feasibility audit is now justified as the next separate gate. No packaging implementation or production readiness follows. Native causal study stays a separately authorized option. |

### Proposed later minimal GPU observation — NOT EXECUTED

Only a new ticket may authorize this. Prefer one pristine fixed-geometry run
with a paired observer-off control, strict reservations, no renderer/shader
correction and no forced clearing. At H1 B natural and the last explicit B
rebuild, record source FBO identity/dimensions and actual pass ordinal.
After D1 and before D2, read only source rectangles (193,69,12,12) and
(93,143,12,12), crossing valid 200×150 right/bottom seams. After D2 and
before U2, read (96,34,7,7) and (46,71,7,7), crossing valid 100×75 seams.
These cover the ideal bilinear neighborhoods for two selected edge samples.
Read corresponding destination pixels D2 (99,37)/(49,74) and U2
(199,75)/(99,149) after their draw. Four rectangles plus four destination
pixels are 390 RGBA pixels per condition: 780 pixels / 3,120 bytes total
for the two B conditions if RGBA8 is valid. No whole-FBO read or image dump.

Observe native read format, pack state, read-FBO binding, origin and texture
transform; preserve and restore observer state. Label synchronization/timing
perturbation. Compare inside-domain versus tail texels and their change between
B rebuilds with selected destination contributions under pinned taps. This
could discriminate historical values and conversion/precision hypotheses;
readback itself still needs observer comparability and does not automatically
prove every final-pixel cause. Do not execute, create its GPU code or reserve
another run in this exhausted campaign.

### Decision and remaining scope

The missing pristine and trace controls are now qualified. The phenomenon is
shared across pristine/private rendering and layouts; no measured OPT activation
effect or forbidden Mosaic H2 contribution appears. Native edge causality is
still unresolved, so the scientific verdict is PARTIALLY_FEASIBLE and
architectural conclusion UNDECIDED. FEASIBLE would overstate the unexplained
edge property; BLOCKED would invent a required-invariant violation.
Recommend the separate SceneFX/wlroots ABI/package audit next, carrying this
explicit shared edge limitation. If selecting an upstream graphics correction
requires causal evidence, authorize the minimal observation above separately.
Neither follow-up is implemented here. No production source or policy changes.

Rotation/scaling/output changes, saved-buffer/popup/input paths, animations,
other drivers/renderers, all-frame damage and native FBO readback remain
NOT TESTED in this campaign. No saved-buffer experiment was relaunched.
STEP20C stays NEXT and production multi-output NOT YET SUPPORTED.

## Final validation and sealed inventories

PASS: shell syntax of the existing exporter (no new B shell script), AST of
all nine Python files, C17 -Wall -Wextra -Werror (unused callback parameters
explicitly exempted), duplicate-configure callback harness, final client
binary equivalence, both pristine/private SceneFX and compositor builds,
Meson mosaic-model 1/1, historical patch applicability/source equivalence,
unchanged cumulative patch forward applicability/source equivalence against
pinned pristine, loaded renderer/library identities, exact stripe calibration,
all source reservations, stable applied focus/camera/geometry, complete RGB
and edge distributions, source sampling audit, recorded R3 damage coverage,
offline/actual budgets, links/whitespace including untracked files, protected
production/V1 paths and installed /usr/bin/sway/SceneFX/wlroots hashes.
All recorded client/compositor PIDs are gone and private sockets removed.
The standalone edge-distributions.svg is an offline figure, not a 49th capture.

NOT RUN: native FBO readback/intervention, saved-buffer/popup tests, additional
geometry/driver/timing variants, ordinary headless IPC suite (no production
change; would introduce extra compositor launches), ABI/package qualification,
installation, daily-session IPC, B commit/push. The original fixture incident
is preserved only in V1; no new run or preflight build failed in this campaign.
No production behavior is claimed by compilation, screenshots or model alone.

Final source manifest: **1,020 entries**, SHA-256
`044f6ab4e0d9ced000b12daa75c7cf30f234aa32fed14dc248baa9e3e11dcdff`.
Final scientific evidence manifest: **189 entries**, SHA-256
`7554388b89fab03b5f3ad0d15c792680fcb403ee04bce8a347c55257440c73d8`.
Every entry was verified individually; sealing refuses an existing inventory.
The historical 1006/106-entry manifests remain unchanged and reverified with
the explicit pre-freeze README snapshot mapping documented by the A report.
The final result report and Git diff are captured separately from the sealed
scientific inventory to avoid self-referential digest dependencies.

Final main, origin/main and github/main remain
`e749653ccda42abad9a66a11009be6043b5b6f62`; both remotes were directly queried
again. The real index is empty; only the five synchronized tracked documents,
this new report and the source-only edge fixture are locally modified/new.
No B commit or push. The final complete Git diff, including new files, is
retained under the freeze audit directory as complete-phase-b.diff.
Production source, cumulative patch, PKGBUILD, UX, AGENTS and historical fixture
match A's published commit. Installed libraries/compositor are hash-identical.
No command targeted daily IPC/session, QuickShell, dotfiles or Codex settings.
STEP20A DONE, STEP20B EXPERIMENTAL, STEP20C NEXT, STEP20D–G PLANNED;
production multi-output NOT YET SUPPORTED.

## Independent publication freeze (2026-10-13)

The new freeze ticket reverified all 1,020 source entries and 189 evidence
entries file by file before any documentation edit; both manifest SHA-256
values above matched. Their bytes and historical evidence are preserved.
The only subsequently edited manifested source is the fixture README; its
exact historical bytes are preserved as `README.pre-freeze.md` beside it.
Use that explicit mapping when verifying the original manifest after publication.
The preceding local/uncommitted final audit describes the historical campaign,
not the publication status of this freeze. No graphical campaign, analysis
writer, model writer, seal writer or proposed GPU readback was rerun.
The verdict remains PARTIALLY_FEASIBLE and architecture UNDECIDED.
