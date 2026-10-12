# STEP20C rotated output viewport and input probe

**EXPERIMENTAL evidence; PARTIALLY_FEASIBLE.** This probe follows the
published dynamic-output evidence at `2882f7415952d7f141da85f90c0fd113a17c1665`.
STEP20C remains NEXT and production multi-output NOT YET SUPPORTED. The source
fixture is [here](../../tooling/probes/step20c-rotated-output/README.md).
No production source, installed library, package, desktop session or live IPC
was changed. The separate partial-popup experiment remains a later gate.

## Question and prior evidence

The [fractional](STEP20C_FRACTIONAL_SCALING_PROBE.md) and
[dynamic-owner](STEP20C_DYNAMIC_OUTPUT_OWNERSHIP_PROBE.md) probes sampled negative
origins, scale 1.25, nested valid XDG grabs, logical resize and workspace
migration, but every dynamic state used `transform=normal`. The dynamic probe
was PARTIALLY_FEASIBLE: two standard D5 reference calibrations failed, the
maximum camera clamp and migrated clipped-popup portion were not exercised.
This probe asks whether an output rotated 90° keeps the same **logical** Mosaic
viewport, clipping and input while pixels and damage use the changed physical
buffer coordinates. A failure is a hypothesis until measured against pristine
and private-standard controls.

## Pinned inputs and exact source path

SwayFX control `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`, Mosaic base
`cd550382b311efdbfe3ed892f4e1d281d852e754`, SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc`, wlroots 0.20.2 source
`d783533489e1f75d6886c2ab5c5960090ef268f8`. Preserve prior patches
unchanged. Fresh private sources/builds, sockets and logs live under one LAB.

Source audit before fixture implementation:

- SwayFX `output_cmd_transform` accepts `90` and `270`, then swaps their
  `WL_OUTPUT_TRANSFORM_*` values: Sway command directions are clockwise while
  Wayland transform enum directions are anticlockwise. SwayFX's IPC encoder
  converts the internal enum back to the user-facing direction. The first
  pristine R90 action measured IPC `transform="90"`, physical 750×1000 and
  logical 800×600. The initial fixture erroneously expected IPC `"270"` and
  stopped before its R90 PNG; that action is consumed and is not replayed.
  The applied IPC value, not the command string alone, decides the gate. `apply_output_configs`
  prepares pending mode, transform, then scale (rounded to 1/120); scene output
  build/backend commit precedes final output-layout update, `arrange_root` and
  `transaction_commit_dirty`. It dirties optimized blur after output changes.
  Thus IPC acceptance does not establish one atomic render/input generation.
- wlroots `wlr_output_transformed_resolution` swaps width/height for odd
  transforms; `wlr_output_effective_resolution` divides those dimensions by
  scale. `wlr_output_transform_invert` exchanges unflipped 90/270;
  `wlr_output_transform_compose` combines transform values. `wlr_box_transform`
  and `wlr_region_transform` map rectangles differently at 90/270, with width
  and height arguments from the **source** coordinate space. `wlr_output_commit_state`
  applies state before `events.commit`; `events.present` is a separate callback.
- SceneFX `scene_node_intersect_clip`/`scene_node_visibility` operate on logical
  scene regions. `scene_entry_render` calls `logical_to_buffer_coords` for
  regions and `transform_output_box` for boxes; both scale first, then apply
  the inverse output transform with transformed physical dimensions.
  `scale_region` expands fractional-scale coverage by one pixel when rounding
  up. `output_to_buffer_coords` converts output damage with the inverse
  transform. `scene_output_damage` stores buffer-local physical extents;
  `wlr_scene_output_build_state` computes render damage and output commit state.
  Shadow/blur rendering has distinct paths, so effect visibility alone cannot
  validate optimized-cache invalidation or off-viewport sampling.
- Mosaic `workspace_tiling_scene_x` subtracts logical `scroll_x` from the
  applied tiled-scene position; the private tiled and root-popup clips are
  applied logical scene clips. `transaction_apply` copies pending state into
  current state, then scene arrangement and cursor rebase follow.
  `node_at_coords` and `seat_pointer_notify_button` use global logical pointer
  coordinates; wlroots `wlr_cursor_absolute_to_layout_coords` maps normalized
  pointer coordinates into the layout's logical bounding box. No physical
  scale or output rotation is applied to injected global logical points.

The source audit identifies paths, not proof that the measured buffer, PNG and
client events agree. It must be confronted with captures and event logs.

## Geometry and coordinate predictions

| State | H1 physical mode | Command transform | Expected applied logical H1 | H2 |
| --- | --- | --- | --- | --- |
| R0 | 1000×750 | normal | (-800,0,800,600), scale 1.25 | 800×600 at (0,0), normal, scale 1 |
| R90 | 750×1000 | 90 clockwise | (-800,0,800,600), scale 1.25 | unchanged |
| R270 optional | 750×1000 | 270 clockwise | (-800,0,800,600), scale 1.25 | unchanged |

R0→R90 changes both mode dimensions and transform: no single-variable causal
claim is possible from that comparison alone. The target logical viewport is
800×600 in both states; H1's physical buffer is expected to use 1000×750 then
750×1000. Actual mode, transform, scale, global rectangle, scene owner and
capture dimensions are gates read from `get_outputs`, trace and PNG. If the
command is refused or remains normal, R90 is INCONCLUSIVE.

Logical global H1 `(x,y)` becomes output-local `(x+800,y)`. The inverse
wlroots transform maps a scaled logical box into the physical buffer.
For a clockwise command `90`, the parser's applied enum is `270`; IPC reports
the user-facing `90`, while the inverse used by SceneFX is `90`. Distinguish
the two names and use the **internal enum** and actual
buffer dimensions in `wlr_box_transform`/`wlr_region_transform`, including
half-open rectangle bounds and fractional rounding. A simple hand-swapped
axis is insufficient near boundaries. Record both expected and measured
logical→buffer→PNG coordinates for every marker/ROI.

Virtual-pointer normalization is provisionally `(sent_x,sent_y)=(global_x+800,
global_y)` over a 1600×600 logical union. Empirically calibrate on each output
with an ordinary surface, (+40,+20) local motion, left/right buttons and
crossing `x=0`. Relocate **both** ordinary references before scoring either;
confirm actual client enter/motion and non-overlap. A prior D5 reference
occlusion makes frame-only geometry an insufficient calibration.

## Capture orientation gate

`grim` screencopy may expose transformed pixels in a different orientation
from SceneFX's raw framebuffer. Before any graphics assertion, capture a
deliberately asymmetric field with five distinct markers: upper-left red
square, upper-right green triangle, lower-left blue circle, lower-right yellow
stripe and purple center cross. For each, store logical point/box, predicted
physical box using observed transform, PNG box, dimensions, delta and rounding
rule. Also record capture window `CLOCK_MONOTONIC` timestamps, mode, scale,
transform, physical/logical dimensions and file hash. Do not select ROIs after
seeing anomalous pixels. If marker orientation is not identifiable, dependent
pixel, popup and damage claims are INCONCLUSIVE. The marker source and
distribution mechanism must be documented before use.

## Comparative scenarios and stop gates

Use identical deterministic SHM toplevel, valid-parent root A and child B,
virtual pointer and ordinary references in: A pristine `splith`, B private
`splith`, C private `mosaic`. Preserve `TOPLEVEL→A→B`; each grab serial must
come from its own real button press, with configure/ack/map and legal anchors.
Do not infer clipping from no spill unless standard controls visibly spill.

1. T0: R0 geometry, references, scene/clip, PNG markers and input calibration.
2. T1: one reserved R0→R90 per mode, then observed mode/transform/scale,
   logical rectangle, identities, scene/clip, marker/PNG and input gates.
3. T2/T3: A and B border-spanning cases, a logical `x=-3..3` grid at
   preselected popup y values, full adjacent physical strips, permitted and
   forbidden pixels, scene hits and separate client delivery/dismissal.
4. T4: one global Mosaic camera hide/return pair only; same XDG object identity
   and a new B button after return if no click has dismissed the stack.
5. T5: one reserved R90→R0 per mode; check restored mode, transform, scene,
   camera, clip, PNG and input. A clamp may alter camera; its measured value
   governs expected geometry.
6. T6: short shadow/blur FX0/FX2 contrasts only after geometry and PNG gates;
   optimized cache and outside-source sampling remain NOT TESTED otherwise.
7. T7: measured physical damage extents versus changed physical pixels, including
   exposed regions on both outputs. Do not double-scale physical extents or
   infer every intermediate frame from settled comparisons.
8. T8: private Mosaic `layout splith`, then no residual clip, ordinary popup,
   focus, effects and input before an exterior dismissal click.

R270 is optional, static at startup, at most one run per mode and only after
R90 capture/pointer gates pass. Transforms 180/flipped, hotplug, all saved
buffers, complete cache invalidation, all frames, ABI/package and daily-driver
support remain NOT TESTED unless directly measured.

## Strict budget, isolation and evidence

One persistent locked ledger spans the campaign. Reserve **before** each
mode/transform action, retain failed reservations, forbid repeats and refuse
more than two actions per mode / six overall. One global Mosaic camera
hide/return pair maximum. R270 adds at most three static starts, no dynamic
actions. Test lock, persistence, duplicate/exhaustion and missing-ledger
rejection offline before any run. No second lab may bypass consumed actions.

Every run has private 0700 `XDG_RUNTIME_DIR`, explicit private `SWAYSOCK`
and `swaymsg -s`, private `WAYLAND_DISPLAY`, headless backend and scoped child
cleanup. Never resolve the live IPC socket implicitly. Preserve all failure
exit codes, attempts and raw logs before owned cleanup; never kill by global
process name. Use passive patches only when prior traces are insufficient;
do not alter clipping, shaders, damage, callbacks, hit testing or ABI.

Retain source/evidence SHA-256 manifests, raw events/PNGs, output/transform,
logical-to-buffer, screenshot, owner/clip, popup, pointer/input, pixel, damage,
timeline, budget, matrix and summary JSON under LAB. The local fixture keeps
only source and passive patch files; no generated binary or capture enters Git.

Verdict: FEASIBLE only if the applied rotation, coordinate/PNG calibration,
standard spill controls, Mosaic visible/forbidden pixels and hits, valid grabs,
return clips and measured damage all pass in the tested matrix.
PARTIALLY_FEASIBLE requires valid principal measurements with named open cells.
INCONCLUSIVE covers un-applied transform or failed orientation/fixture gate.
BLOCKED requires a reproduced forbidden pixel/hit, wrong transform clip, crash
or blocking standard-layout regression. Even FEASIBLE is experimental evidence,
never production qualification. Architectural conclusion is separately
`ROTATED_OUTPUT_FEASIBLE_FOR_TESTED_MATRIX`, `ROTATED_OUTPUT_REQUIRES_REDESIGN`
or `UNDECIDED` according to measured support.

## Measured private campaign — 2026-10-12

**EXPERIMENTAL / PARTIALLY_FEASIBLE overall; architectural conclusion
UNDECIDED.** The new laboratory is
`/tmp/swayfx-mosaic-nested-grab-TJ3AhbCE`. A fresh source-only preparer built
private SceneFX/Mosaic and pristine SwayFX from the same pins and compiled
the XRGB client and virtual pointer under C17 `-Werror`. It never used the
historical dynamic campaign's consumed actions. All three modes were attempted
once under one persistent locked rotation ledger. There are 111 retained PNGs:
16 pristine, 40 private standard and 52 private Mosaic, plus the per-run marker
source PNGs. No B source, report or result was committed/pushed.

### Fixture incident and applied geometry

The pristine `splith` run completed R0, two-output pointer calibration and a
two-level grabbed popup chain. It reserved and launched R90. `get_outputs`
then showed H1 physical **750×1000**, scale **1.25**, IPC transform **`90`**,
and logical **(-800,0,800,600)**. The initial fixture asserted IPC `270` by
mistaking the internal wlroots enum for SwayFX's user-facing IPC string, so
it failed before R90 capture. Its R90 action remains consumed. Pristine R90
PNG, input and return are **NOT TESTED**; this is a fixture error, not a
demonstrated compositor rotation defect. The source assertion was corrected
before the two private runs; no pristine retry occurred.

Both private modes completed exactly one R0→R90 and one R90→R0. H2 stayed
physical/logical 800×600, scale 1, normal at (0,0). H1 remained logical
(-800,0,800,600) in all measured states while changing as follows:

| State | Physical mode | IPC transform | Internal enum trace | Scale | H1 PNG |
| --- | --- | --- | --- | --- | --- |
| R0 | 1000×750 | normal | 0 | 1.25 | 1000×750 |
| R90 | 750×1000 | 90 | 3 (`WL_OUTPUT_TRANSFORM_270`) | 1.25 | 1000×750 |
| Return R0 | 1000×750 | normal | 0 | 1.25 | 1000×750 |

The mode's orientation and the transform both changed; the equal logical
viewport does not isolate their separate causal effects. An IPC success value
alone was never used as the applied-geometry proof.

### PNG and pointer gates

`grim -s 1.25` exposed a **logical-oriented** 1000×750 PNG even with the
750×1000 physical R90 mode. All five exact-color marker centers were identical
in private R0 and R90 screenshots: TL (37,37), TR (962,37), BL (37,712),
BR (962,712), center (499.5,374.5). The pristine R0 marker matched.
This identifies the PNG repère for this screencopy path, not the raw SceneFX
framebuffer. For the internal 270 transform, SceneFX uses inverse 90 on
scaled logical rectangles. A pixel center `(x,y)` in this logical PNG maps by
source formula to physical buffer `(749-y,x)`: TL approximately (712,37),
TR (712,962), BL (37,37), BR (37,962), center approximately (375,500).
These buffer coordinates are **calculated, not directly read back**. The exact
marker equality has zero measured PNG-center deviation; raw-buffer deviation
is NOT TESTED. Fractional edges use SceneFX's region expansion and box
rounding, so the center mapping is not a claim about every filtered edge.
The actual wallpaper used five distinct exact RGB colors and five asymmetric
positions, but drew every mark as a square. This does not meet the protocol's
distinct-shape preference; the unique color/position pairs made orientation
identifiable in the retained images, and no shape-based assertion is claimed.

On each private mode, independent ordinary references received pointer
enter/motion, logical (+40,+20) local deltas and left/right buttons on H1/H2
at R0 and R90. Their first local point was (20,30), second (60,50).
The injector used the observed logical union `min_x=-800`, extent 1600×600,
`sent_x=global_x+800`, `sent_y=global_y`, without multiplying by 1.25 or
rotating injection coordinates. It traversed `x=-3..3` at y=550; those moves
were **not scored against popup client events** and do not qualify clipped
popup boundary hit testing. Both references were relocated before either
calibration, avoiding the earlier D5 overlap incident.

### Popups, clips and pixels

All measured A/B grabs used real received button serials. Pristine R0 had
two valid grabs; each private mode had four valid grabs across its first and
reopened chains. The client retained `TOPLEVEL→A→B` parentage, configure,
ack, map and distinct new role lifetimes after closure. A's anchor (200,80)
lies within the 420×320 parent buffer; B's (220,60) lies within A's 300×170
buffer. No protocol error was logged. One A/B `popup_done` pair appeared in
each private run during the explicit close/reopen sequence; the chain present
during R90 was captured before closure. This does not prove universal XDG
persistence through arbitrary transforms.

Mosaic retained workspace ID 6, tiled owner ID 8, order [7,8,9,10] and camera
640 through R0, R90 and return. `DO_STATE` records transform 0→3→0.
Pre-capture applied traces give tiled scene origin (-1440,0), local clip
(640,0,800,600), derived viewport (-800,0,800,600) at R0/R90/return.
Owner-derived root-popup clip from global root (-798,25) and local
(-2,-25,800,600) yields the same viewport. Nested popup inheritance is
visible in scene traces. These are sampled applied states, not every frame or
a shared render/input transaction generation.

The private-standard R90 screenshot has **15,860** exact B-color pixels on
H2, including 130/390/910 pixels in its first 1/3/7 physical columns.
Pristine R0 showed the same 15,860 H2 B pixels. Private Mosaic R90 has
zero A/B-color pixels on H2 and permitted A/B colors on H1. However, its
B-color box in the logical PNG is x=[528,903), y=[206,369), wholly inside
the H1 viewport x=[0,1000) in PNG coordinates. Standard B reaches x=1000
and continues on H2. **The different standard/Mosaic layout positions mean
this campaign did not challenge a partially clipped Mosaic popup at R90.**
The zero H2 count is an observed no-spill state, not proof that a forbidden
popup portion was clipped. A crossing and simultaneous A/B crossing are also
NOT EXERCISED. The fixed x=-3..3/y=550 grid did not lie in a scored popup
region; invisible hit tests there remain NOT TESTED.

The single reserved Mosaic camera hide/return pair moved scroll 640→1280→640
under R90. At 1280, owner 8's applied scene x=-1440 with width 640 ends at
the viewport's x=-800, yielding an empty intersection. Its root popup clip
became (0,0,0,0); H1 captured zero owner/A/B-color pixels. The return
restored the same scene/clip and exact R90 image hash, and a new right button
on B at global (-343,195) reached that client after return. The second camera
reservation is the return half of this one pair, not a second pair.
The second chain's sampled popup roles (A 13, B 16 in this run) remained
mapped through that pair, without a new `popup_done`; their IDs are run
observations, not fixture constants. B also received a right button while
visible under R90 before the hide.

R90→R0 restored mode, transform and clip in both private runs. Mosaic's
settled R0 popup screenshots were byte-identical to its R90 logical-oriented
popup screenshots and to its earlier R0 state. `layout splith` subsequently
removed the Mosaic clips; its left/right PNG hashes equaled the private
standard `splith` result, including the ordinary 15,860-pixel B overflow on
H2. This samples return and ordinary layout behavior, without proving all
transition frames or all focus/popup event orderings.

### Damage, effects and budget

SceneFX's traced `TEMPORAL_DAMAGE` extents are clipped to physical
buffer-local `output->width/height` after `output_to_buffer_coords` applies
the inverse transform. For equal-transform settled R90 Mosaic pairs, map
changed PNG pixels `(x,y)` to physical `(749-y,x)` before comparing extents.
The R90 visible→fully-hidden and hidden→restored H1 pairs each changed
569,789 logical-PNG pixels; 27 and 18 physical extents respectively covered
all changed pixels, **zero uncovered**. H2 changed zero in that pair. The
R0 Mosaic→standard return changed 442,712 H1 pixels; 89 available normal
extents covered them, zero uncovered. Full-output extents occurred, so neither
minimal damage nor complete intermediate-frame coverage is established.
Mode/transform transitions were not compared as equal physical buffers.
Commit/present callbacks were retained but no screenshot was tied to a native
buffer identity or atomic input generation.
Private Mosaic logged 221 native commit and 215 present callbacks; private
standard logged 188/182. The pristine control has no passive native trace.
These count differences include startup/teardown and are not themselves a
frame-loss finding.

Shadow and blur were disabled in this campaign. T6, optimized cache
invalidation, off-viewport blur source sampling and physical raw-buffer
readback are **NOT TESTED**. R270 was not run: the main negative partial-popup
challenge is already absent, so another static direction would not close it.

The durable ledger retains one failed control R90 action, private-standard
R90/R0 and private-Mosaic R90/R0: **5/6 mode/transform actions**. Mosaic used
**1/1 camera hide/return pair**; R270 static runs **0/3**. No reservation was
refunded or replayed, and no second lab was created to evade the budget.

### Structured evidence and integrity

The authoritative final analysis is `LAB/results-final/`; the prior sealed
`LAB/results/` and `LAB/results-corrected/` remain byte-for-byte preserved. The initial
analysis counted zero Mosaic spill but did not check the Mosaic B bounding
box, so its architectural conclusion was too strong. The final results
include outputs, transforms, logical-to-buffer mapping, marker coordinates,
workspace owner, scene clips, popup geometry, pointer/input, pixel/damage,
timeline, budget, matrix and summary JSON. All are recalculable from raw
events, logs and 111 retained run PNGs.

The corrected v2 1,015-entry source manifest SHA-256 was
`8fe5bdec378ca200a94c589db867fc21c80ee9fe37762c38077746e4eb2d9ce6`;
its 282-entry evidence manifest was
`77e3d60621f14e46655779d09ce53cc92e48cc50b8aa2d72c5faa64432fdba51`.
The final v3 manifests and entry counts are recorded after sealing below.
Final v3 **1,015-entry source** manifest SHA-256:
`f17ee5999edec84885997ea5dfb193859f7c1d278bf4dda22f8ab20b1c5e0b8f`.
Final v3 **284-entry evidence** manifest SHA-256:
`261ff4cb12d7be3494d43f29ce1d24f980d8f19abdc558fef42599d50070747d`.
Both verify entry by entry. The final B box is derived from pixels as
`[528,206,903,369]` against PNG width 1000; owner ID is derived from each
run's tree state. Raw captures and private logs are unchanged across analyses.
The v1 evidence manifest
`02d7f47e1be9e3fb8d867e9a2d0d8d27ee358af43d96c9b217ab5435c7e5c4b8`
also still verifies; each later evidence manifest includes the prior manifest files.
The v1 source manifest recorded earlier fixture bytes and is historical after
the analysis correction; no raw run file was modified.

An additive offline `LAB/results-roi/` annotation records fixed
logical/PNG/physical half-open boundary ROIs, exact A/B counts, comparable
previous-capture pixel changes, mode/scale/transform, hashes and monotonic
capture windows for all **108 run captures** (the three marker-source PNGs are
not run captures). At R90 the H1 PNG strip [995,1000) maps to physical-buffer
y=[995,1000), x=[0,750), while H2 uses its first four physical columns.
The private-standard R90 strip has 815 B pixels on H1 and 520 on H2;
Mosaic has zero in both strips because its B box ends at PNG x=903.
The 115-entry addendum manifest SHA-256 is
`426f40078ad6388b34219b09f576d833d99a8dec76ea286235bc34fa324f8f63`
and passed entry-by-entry verification. It chains the final analysis manifests
without changing any earlier sealed file. These strip counts are not popup
hit-delivery measurements.

### Validation and isolation closeout

The new ledger passed offline lock, durable reservations, duplicate,
exhaustion and missing-ledger tests without a compositor launch. The five
fixture modules and three generated runners passed Python AST; the inherited preparer's shell
syntax passed. The private SceneFX, Mosaic and pristine builds completed;
the Mosaic Meson model test passed 1/1. Both experimental C17 clients compiled
with `-Wall -Wextra -Werror`. The two dynamic-fixture patches retained their
published SHA-256 and reverse-applicability checks in the fresh private tree.
The forward patch sequence was exercised by the fresh preparer. A standalone
reverse check of the older SceneFX `effect-trace.patch` against the **fully
stacked** private tree failed at `wlr_scene.c:2117`; later overlapping patches
make that isolated reverse check inapplicable. No historical patch was edited;
the complete private SceneFX build passed.

Markdown links and the complete local diff, including new files through a
temporary Git index, passed checks. The real Git index remains empty.
Production Mosaic sources, the cumulative patch, `PKGBUILD`, installed
SceneFX/wlroots, `/usr/bin/sway`, QuickShell and dotfiles were untouched.
Every experimental IPC call used an explicit private socket; no live SwayFX
IPC was accessed. All three per-run 0700 runtime directories were removed,
with no retained private socket or experimental process. No install, session
restart or STEP20D work occurred. This historical laboratory and its consumed
budget are closed; the separate static-R90 partial-popup campaign requires a
new ledger and private runtime.

## Architectural answers and verdict

| Question | Evidence-backed answer |
| --- | --- |
| Q1 viewport coherence | Sampled applied R90 tiled/root-popup clips still derive (-800,0,800,600); logical owner/camera stable. |
| Q2 SceneFX physical conversion | Source scales then inverse-transforms boxes/regions. Physical damage coverage is compatible at two settled camera transitions; raw framebuffer pixels were not read, so direct physical-render proof is partial. |
| Q3 PNG frame | Yes for this `grim -s 1.25` path: 1000×750 logical orientation with all five marker centers unchanged under R90. |
| Q4 visible and forbidden pixels | Permitted Mosaic owner/A/B pixels survive R90; zero exact A/B colors on H2. Partial Mosaic popup overflow was not created, so forbidden-pixel clipping is NOT EXERCISED. |
| Q5 root/child clips | Root clip and nested inheritance trace the owner viewport; fully hidden owner reaches empty clip. Partial border challenge NOT EXERCISED. |
| Q6 grabs | Two genuine grabs per completed chain, valid serial/configure/ack/map and no protocol error. |
| Q7 pointer | Two-output logical calibration passes R0/R90 in both private modes, without scale/rotation injection; popup border hit grid unscored. |
| Q8 damage | Available physical extents cover 569,789 changed pixels on each R90 camera leg, zero uncovered; no all-frame/minimal guarantee. |
| Q9 R0→R90 stale clip/cache | No stale clip in sampled traces/screenshots; effects disabled, optimized cache NOT TESTED. |
| Q10 R90→R0 | Private modes restore physical/logical geometry and normal transform; Mosaic restores sampled scene/clip and identical logical PNG. Pristine return NOT TESTED. |
| Q11 effects | Shadow/blur disabled; NOT TESTED under rotation. |
| Q12 algorithm redesign | No reproducible leak, invisible hit or crash demonstrated. Missing challenge does not justify production or private algorithm changes. |
| Q13 applied geometry contract | A future STEP20C contract must bind applied mode, transform, scale, logical viewport and input/damage generation explicitly. This probe proposes that requirement; it does not freeze a new contract. |
| Q14 open cases | Pristine R90 PNG/input/return; partial A/B Mosaic crossing; scored popup-border hits; effects/cache; raw physical readback; saved buffers; intermediate frames; R270; ABI/package. |
| Q15 next gate | Another **rotated geometry** probe with a Mosaic popup demonstrably crossing x=0 and legal grabs, plus a completed pristine R90 control, is the smallest decisive gate. Saved buffers, optimized cache and ABI/package remain later independent gates. |

`SWAYFX_MOSAIC_ROTATED_OUTPUT_PROBE=PARTIALLY_FEASIBLE`

Architectural conclusion: **UNDECIDED** for partial popup clipping under
physical rotation. The tested logical geometry, PNG/pointer calibration,
fully-hidden guard, damage coverage and return are useful evidence, but the
central negative clipping comparison is absent. STEP20C stays **NEXT**;
multi-output Mosaic stays **NOT YET SUPPORTED**.
