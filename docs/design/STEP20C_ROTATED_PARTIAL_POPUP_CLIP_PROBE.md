# STEP20C static R90 partial popup clipping probe

**EXPERIMENTAL protocol, before execution.** STEP20C is NEXT; production
multi-output Mosaic is NOT YET SUPPORTED. The preceding
[rotation probe](STEP20C_ROTATED_OUTPUT_PROBE.md) was PARTIALLY_FEASIBLE:
private standard displayed 15,860 B pixels on H2, but Mosaic B ended at
PNG x=903, short of the x=1000 boundary. Its pristine R90 fixture stopped
after applying transform `90` because it incorrectly expected IPC `270`.
This independent campaign tests only a static R90 startup, with no dynamic
transform, resize, migration, camera hide/return, effects or algorithm change.

## Fixed geometry and model

H1 starts at global (-800,0), physical 750×1000, IPC transform `90`, scale
1.25, logical 800×600. H2 starts at (0,0), physical/logical 800×600, normal
at scale 1. Read `get_outputs` before scoring. The expected `grim -s 1.25`
H1 PNG is logically oriented 1000×750 according to the earlier probe; its
actual dimensions and five distinct markers must be measured anew. The
internal Wayland transform enum `270`, physical buffer and logical PNG are
different coordinate systems. Pointer injection uses the measured logical
union (-800..800, 0..600), with sent x = global x + 800.

Use one fixed XDG placement `rot_cross`: TOPLEVEL 420×320; A 480×170 with
anchor rect (360,80,1,1); B 300×130 with anchor rect (210,60,1,1).
Both anchors fit their parent dimensions. Positioners use TOP_LEFT anchor,
BOTTOM_RIGHT gravity and no constraint adjustment requested by the client.
Actual `xdg_popup.configure` x/y/w/h, ack, map and scene placement must be
recorded; compositor unconstrain may change them. No alternate placement is
authorized in this campaign.

The prior applied Mosaic owner plus camera 640 placed B's right edge near
global -78 (PNG x=903). Moving A's anchor +160 and B's -10 predicts B's
right edge near +72, enough for a discriminating H2 portion. A's width
adds 180, predicting an A right edge near +42. These are **predictions**, not
observations. The original `(390,80)` candidate would shift B by +180: the
earlier standard B left edge near -178 would move to +2, removing its H1
portion. This single pre-run variant shifts B by +150 and predicts standard
B left near -28, retaining 28 logical pixels on H1. The owner, workspace,
applied camera and popup root scene
coordinates must be measured separately per mode. Compute each global popup
box from the applied owner/scene origin and configured XDG offsets, then
intersect with H1 [-800,0)×[0,600) and H2 [0,800)×[0,600).
Partial clipping is exercised only when left < 0 < right and both intersections
are nonempty. A crossing less than 16 logical pixels is reported with its
actual width before qualification. A box wholly within H1 is NOT EXERCISED,
even when H2 contains zero popup pixels.

## Runs, observations and decisions

One run each: C0 pristine pinned SwayFX `splith`, C1 private `splith`, C2
same private compositor `mosaic`. Static output config is applied at startup.
Each run uses one 0700 runtime and explicit private IPC socket, at most two
distinct A/B grab chains, 16 captures and 120 seconds. The entire campaign
allows at most 3 runs and 50 captures; failed reservations count. A persistent
exclusive ledger is tested offline and reserved before each launch. A single
initial Mosaic scroll to 640 is permitted before popup creation, logged once.

Capture a five-marker H1 background and stable H2 reference before popup
creation. Record capture monotonic windows, SHA-256, mode/scale/transform,
logical rect, PNG dimensions, popup boxes and clips. Compare H2's entire
forbidden intersection to its predeclared reference as well as exact A/B
colors, without post-hoc ROI exclusions. At least one standard control must
show B pixels on both outputs and a real B button on H2. Mosaic must show
its own geometric B crossing, B pixels and a delivered button inside H1,
zero B contribution and no B delivery on H2. Derive boundary y from the
applied popup box and inspect x=-3..3. Keep hover probes in one chain; use
a second chain for an exterior click that may dismiss the grab. A is evaluated
separately at points outside B when its own box crosses.

The client must log a real button serial on TOPLEVEL before A's grab and on
A before B's grab, each configure/ack/map and protocol error. The runner
records applied tiled/root/child clips, owner output, damage in buffer-local
physical coordinates, commits/presents and actual client delivery. Damage
from the inherited `TEMPORAL_DAMAGE` path is already physical: do not apply
scale twice. Settled PNG differences do not prove every intermediate frame
or an atomic render/input generation.

FEASIBLE requires valid crossing B in Mosaic, standard overflow controls,
retained H1 pixels/input, excluded H2 pixels/input, correct owner clips and
completed pristine R90. PARTIALLY_FEASIBLE preserves a crossing with missing
secondary proof. INCONCLUSIVE covers absent crossing, invalid fixture or
incomparable controls. BLOCKED requires a reproducible forbidden pixel/hit,
wrong owner clip, crash or standard regression. A confirmed leak stops the
affected campaign; no clipping algorithm is changed to obtain a pass.
R270, saved buffers, optimized blur cache, inner shadow, raw framebuffer,
all intermediate frames and ABI/package maintenance remain NOT TESTED.

The [source fixture](../../tooling/probes/step20c-rotated-partial-popup/README.md)
retains only reviewed scripts and the client placement patch. Generated
builds, binaries, captures, sockets, logs and structured results stay in a
private LAB.

## Measured static-R90 campaign — 2026-10-12

**EXPERIMENTAL / PARTIALLY_FEASIBLE.** LAB:
`/tmp/swayfx-mosaic-nested-grab-PioJ5X43`. The new preparer rebuilt the pinned
pristine SwayFX, private Mosaic/SceneFX and strict C17 clients from the prior
published source chain, then applied only the dedicated `rot_cross` client
patch. The clipping algorithm and installed libraries were untouched. One
main run each of pristine `splith`, private `splith` and private `mosaic`
completed normally, with 14 captures and about 14.6 seconds per run. The
new locked ledger consumed **3/3** runs; dynamic transitions, migrations,
resize, camera hide/return and R270 each consumed **0**. Mosaic made one
pre-popup static camera placement to scroll 640, recorded in the raw events.

All three `get_outputs` states reported H1 physical 750×1000, IPC transform
`90`, scale 1.25 and logical (-800,0,800,600). H2 remained 800×600,
normal/scale 1 at (0,0). Every H1 `grim -s 1.25` PNG was 1000×750 and the
five marker centers established the logical PNG orientation. The control
pristine therefore completed the R90 capture and input matrix missed by the
historical fixture; no dynamic R90→R0 action occurred. Its two grabs used
real button serials 121/126, configured, acked, mapped, and exited without
protocol error. Private standard used 123/128; Mosaic used 105/110. The
configured XDG offsets were A (360,80,480,170) and B (210,60,300,130)
in all modes, matching the fixed legal 1×1 anchors. The actual source scene
and owner positions produced these global half-open boxes:

| Mode | Applied owner x / camera | A global | A∩H1 / A∩H2 widths | B global | B∩H1 / B∩H2 widths |
| --- | --- | --- | --- | --- | --- |
| Pristine `splith` | -600 / 0 | [-238,242)×[105,275) | 238 / 242 | [-28,272)×[165,295) | 28 / 272 |
| Private `splith` | -600 / 0 | [-238,242)×[105,275) | 238 / 242 | [-28,272)×[165,295) | 28 / 272 |
| Private Mosaic | -160 / 640 | [-438,42)×[105,275) | 438 / 42 | [-228,72)×[165,295) | 228 / 72 |

The Mosaic owner current rect was x=-160 with width 640, while its applied
scene origin was x=-800 after scroll 640. Its content/window x offset was 2,
giving root-popup global (-798,25). A starts there plus configured (360,80),
B starts at A plus configured (210,60). The sampled `DO_STATE` reported
internal transform 3 (`WL_OUTPUT_TRANSFORM_270`), physical 750×1000 and
logical 800×600. `PI_SCENE` held tile global -1440 and local clip
(640,0,800,600), hence viewport [-800,0)×[0,600). `DO_POPUP` identified
owner 8 on H1 and local root clip (-2,-25,800,600), which yields the same
global viewport. B remained a scene descendant of A and inherited that
root clip. The scene and configured XDG offsets agree at the sampled applied
state; this does not establish an atomic generation over all frames.

The predefined reference was each mode's `right-reference.png`, captured
before A/B creation. At the mapped-B capture, pristine and private standard
each had **5,705 exact B pixels on H1** and **35,360 on H2**; their H2
full-image difference from reference contained **49,880 pixels**, with box
[0,105,272,295). Mosaic retained **46,455 B pixels on H1**, including
163/489/815 pixels in its last 1/3/5 PNG columns, and **zero B pixels on
H2**. Its H2 whole PNG was **pixel-identical** to the
predeclared reference: zero differing pixels, not merely zero exact SHM
colors. A itself also crossed: Mosaic showed 77,181 A pixels on H1 and
zero on H2; the standards showed 58,431 on H1 and 14,520 on H2. The A
count includes occlusion by B where their rectangles overlap; it is not a
full theoretical A-area count. The measured B geometry, unlike the old
probe, genuinely challenged the clip by 72 logical pixels on H2.

For B's y=230 boundary grid, the pristine and private-standard clients
reported B local motions x=25..31 for global x=-3..3 and delivered right
buttons on B at (-14,230) and (30,230). The Mosaic client reported B local
motions x=225,226,227 at global x=-3,-2,-1, then a B leave at x=0; no
B enter/motion followed for x=0..3. A right button at (-30,230) was delivered
to B with serial 119. At forbidden (30,230), B received **no button**;
the valid grab produced `popup_done` for B and A. The button on visible A
that created B was genuinely delivered (serial 110). An independent click
on the clipped-away portion of **A** was not made; P2 root-popup input is
therefore PARTIAL even though A's geometry and pixels cross. No universal
click-through contract is inferred from the dismissal.

Available `TEMPORAL_DAMAGE` extents for the settled reference→mapped-B
Mosaic H1 pair covered all **123,636 changed logical-PNG pixels** after
mapping `(x,y)` to physical `(749-y,x)`: 10 physical extents, zero uncovered.
H2 changed zero pixels. The private-standard pair likewise had zero
uncovered changed pixels on both outputs (10 H1 and 6 H2 extents). The
pristine control had no passive damage trace; its nonzero screenshot diff
cannot be scored against absent extents. These broad damage observations
cover only the settled pair, not minimal invalidation, all intermediate
frames, saved buffers or render/input generation identity. Private Mosaic
logged 126 native commits and 124 presents during the whole run; private
standard logged 119/117. Startup, pointer and teardown activity are included.

`LAB/results/` retains geometry, positions/intersections, output transform,
grab, applied clip, input, pixels, damage, matrix and summary JSON. Raw
client/protocol, compositor, pointer, `get_outputs`/tree, PNG and capture
windows remain under each `LAB/runs/` directory. The final source and
evidence manifest entry counts and SHA-256 values are recorded below after
documentation synchronization: **910 source entries**,
`3e6930c46dd9abf50aa2720357ccbdd47ac3fdd0f1106a47734383cb281b41a5`;
**146 evidence entries**,
`e3c13e4fc02f6b66b59b87407ef7b91f5b7cd67430cc1142252098ef3885a949`.
The dedicated placement patch SHA-256 is
`0f45d48625c062ca05f36849068aedecd02e4480a98f3e0bafe98c1f1c529089`,
based on nested client SHA-256
`2e40c98af72a0df8b316810589a0be8f4425a763db1de448b49a7813956b6f7d`.
Both manifest files passed entry-by-entry verification after the fixture
README was synchronized and the CLI limits were made non-overridable above
120 seconds / 16 captures / 30 MB. Each run retains its executed
`fixture-source.py`; that exact source precedes this post-run limit hardening.
The hardening was tested offline with an over-limit argument and caused no
fourth run or ledger change. The ledger is separate
from the historical 5/6 rotation and 1/1 camera budget, which were not
reopened. Every run used a private 0700 runtime and explicit private IPC;
exit status and cleanup were retained. No production, package or UX change
was made.

**Verdict:** `SWAYFX_MOSAIC_ROTATED_PARTIAL_POPUP_CLIP_PROBE=PARTIALLY_FEASIBLE`.
The central B crossing/visible/clipped/input distinction passed this one
static-R90 matrix, including a complete pristine control. The scored
clipped-away A input point, all-frame damage and applied generation are
still open. Architectural conclusion:
`ROTATED_PARTIAL_POPUP_CLIP_FEASIBLE_FOR_TESTED_MATRIX`, without production
STEP20C qualification. Saved transaction buffers are the next priority:
they can reintroduce pixels from an earlier scene at the same viewport even
when the live popup tree clips correctly. Optimized blur cache, interior
shadow and SceneFX/wlroots ABI/package maintenance remain separate gates.
