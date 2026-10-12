# STEP20C saved target natural timeout and input probe

**EXPERIMENTAL / PARTIALLY_FEASIBLE.** STEP20C remains NEXT;
production multi-output Mosaic is NOT YET SUPPORTED. This is a new, single-run
laboratory. The prior [target crossing report](STEP20C_SAVED_BUFFER_TARGET_CROSSING_PROBE.md)
remains PARTIALLY_FEASIBLE and architecturally UNDECIDED. Its E1 established
one actual target saved node crossing `x=0`, clipped render in H1, 182,214
retained target pixels and a real ACK/cleanup. Its E2 timeout stopped through
fixture pointer correlation; it did not test Mosaic target timeout cleanup.

The old H2 Kitty reference changed one complete 11×23 rectangle from its
block-cursor color `#F5E0DC` to background `#303038` across pristine and
Mosaic runs. Blink causality is strongly supported but unproven. This probe
uses an opaque, static XDG SHM reference with app ID
`org.mosaic.StaticReference`, fixed RGB and no text cursor or animation.
The reference still handles real configure/ACK and Wayland events. Two full
H2 RGB captures separated by more than one historic Kitty blink interval
must match exactly before the target episode is reserved. No region is
masked, and reference failure stops the run.

## Source identity and geometry

Pinned inputs: SwayFX 0.6 `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`,
private Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754`, SceneFX 0.5
`37ccd723bef49e6891156ffafce8f549f01446cc`, wlroots 0.20.2.
Preserved clipping, saved-buffer and target-geometry trace patches retain
their bytes. Any further passive hit trace has its own patch and hash.
No production source, SceneFX algorithm, public ABI, package, UX or active
desktop session is changed. The private timeout policy is
`-Dtxn-timeout=2500`, parsed into `server.txn_timeout_ms`; no `-Dtxn-wait`,
`-Dnoatomic`, direct save call or scheduler change is used.

Source audit of the pinned private copies located `transaction_commit`,
`should_configure`, `transaction_progress`, `apply_container_state` and
`handle_timeout` in `sway/desktop/transaction.c`: an ordinary changed-size
instruction calls `view_save_buffer`, and timeout advances the transaction
through the normal progress path. `sway/tree/view.c` implements
`view_save_buffer_iterator`, `view_save_buffer` and
`view_remove_saved_buffer`; its iterator creates the saved scene buffer and
passes the current source buffer to `wlr_scene_buffer_set_buffer`.
The private SceneFX `types/scene/wlr_scene.c` contains
`wlr_scene_buffer_create`, `wlr_scene_buffer_set_buffer`,
`wlr_scene_node_for_each_buffer`, `scene_node_intersect_clip`,
`scene_node_point_inside_clip`, `wlr_scene_node_at` and
`scene_entry_render`. The latter two paths are separately observed by the
passive hit and render traces. A saved scene buffer is distinct from its
source Wayland buffer, output buffer, and optimized blur cache.

Only H1 `(-800,0),800×600` and H2 `(0,0),800×600`, scale 1, normal, are
allowed. Map and settle all clients first. Record H2 reference app ID,
output, geometry, two PNG hashes and full RGB equality. Then identify the
target app ID `org.mosaic.SavedBufferProbe`, workspace, output, tiled owner,
view, source scene node/buffer, destination/source dimensions, source box,
transform, applied camera, tiled clip and global source box. Compute one
signed relative scroll from the **current** camera and measured source node.
Remeasure after application. Require nonempty source and `left<0<right`,
preferably at least 64 pixels on each side. Do not substitute the IPC
container rectangle. No later focus action may silently change the camera.
Failure stops before an episode reservation; no scroll scan or retry.

## One timeout episode

Remeasure the current source immediately before reserving the sole episode.
Ask the C17 target to `hold_next_configure`, then make one normal geometry
change (`gaps inner current set 30`) and require an actual changed-size
configure. The client retains the real serial, stays alive, dispatches
Wayland events and responds to pings. It sends no ACK during the hold and
none is forged after expiration.

Correlate the target view and current source buffer to its saved tree and
saved scene node. Require a nonempty, enabled saved node whose global box
crosses `x=0`, current content disabled, ancestral tiled clip and a render
entry for **that node**. Distinguish the outer Mosaic clip, its gap-adjusted
viewport and any content clip; the old E2 `x=-30` bound matched a tiled clip
narrowed by 30-pixel gaps. Record permitted target SHM color on H1, zero
target SHM color on H2 and **full-H2 RGB equality** against the static
reference during the hold. Preserve all mismatches if equality fails.

If the remaining 2500 ms window permits, inject at most two prepared pointer
motions: one in the saved target's permitted H1 portion and one in its
geometrically forbidden H2 portion over the static reference. Record global
points, `wlr_scene_node_at` result/descriptor, surface association and
actual client events; distinguish seat notification when traceable. These
motions must not delay the natural timeout. If not safely measured, input is
NOT TESTED. A saved scene buffer need not itself deliver a Wayland click.

Wait for the real SwayFX timeout with configure held and client alive.
Observe transaction apply, target saved-tree destruction, enabled live
content, no later render entry from the destroyed saved node, final H1/H2
images and available damage extents. Node destruction does not prove all GPU
texture references were released. Stabilized PNGs do not cover all frames.
No output transition, camera hide/return, popup, scaling, rotation, effects,
animation, migration, stress test or new standard run is part of this gate.

## Budget, retention and classification

A single persistent locked ledger allows **one Mosaic run, one episode, one
calculated camera adjustment, at most 12 captures and 150 seconds**. It
reserves before each resource use; failures consume reservations. The ledger
cannot reset or be copied to justify a second laboratory. Test it offline
before the run. All builds, generated protocols, sockets, captures and logs
stay in one disposable `/tmp` LAB. The exact executed runner is copied into
its run. Source and evidence SHA-256 manifests cover the retained inputs and
observations. Private 0700 `XDG_RUNTIME_DIR`, `WAYLAND_DISPLAY` and explicit
`swaymsg -s` isolate the session; cleanup is by owned process groups only.

FEASIBLE requires stable whole-H2 RGB before/during/after, actual target
crossing/render and H1 pixels, no forbidden H2 contribution, natural timeout
with live held client, target saved-tree cleanup, and no measured invisible
hit. PARTIALLY_FEASIBLE means the timeout/clipping core succeeds with limited
input, damage or GPU lifetime qualification. INCONCLUSIVE means reference,
crossing, target rendering or natural timeout is not actually exercised.
BLOCKED requires a reproducible forbidden pixel/hit, concrete lifetime defect,
crash or blocking regression. A fixture/calibration error is documented as
such, without inventing a Mosaic defect. No result qualifies STEP20C
production or authorizes a clipping algorithm change.

## Retained execution and measured result

The single run is retained at
`/tmp/swayfx-mosaic-nested-grab-iKwhINe5/runs/timeout-mosaic-1791824080327425269`.
Its exact runner is `fixture-source.py`; the analysis in
`LAB/results/*.json` derives from the retained PNGs, logs, IPC trees and
monotonic timestamps. The private passive hit patch SHA-256 is
`25b7ffd909de3ccbab5b0ac542216b2b321fee78f7e73d80aa919c02ef829e83`.
The source manifest has 913 verified entries and SHA-256
`bcc1a921268dc1cf032aeb68824fefd27e3c1861c872920548a8db4ba33e070b`;
the evidence manifest has 46 verified entries and SHA-256
`5b085ddf58c63225a6940987b775de805543ad5711b65a6ed20d5eb9418577ac`.
There was one Mosaic run, one episode, one calculated camera delta, eight PNGs
and a 5.062-second run. The locked ledger retains these reservations. No
second run or standard control was launched.

The H2 reference had app ID `org.mosaic.StaticReference`, container ID 11,
opaque fixed RGB `#303038`, a normal XDG configure/ACK path and no cursor.
Two preflight H2 PNGs captured about 0.754 seconds apart were identical
over all 800×600 RGB pixels. The held and post-timeout H2 PNGs had the same
SHA-256 `fb69a3b1fb61484b03c41f988fba7de7b09223261b7e63c0e09d9b5cb81ddaf1`.
Each full-image difference contains zero pixels; neither target SHM color
appeared on H2. No mask or excluded region was used.

The target `org.mosaic.SavedBufferProbe` occupied tiled container ID 8,
Mosaic workspace ID 6 on H1. Its actual source node
`0x557502aff7e0` carried buffer `0x557502b652b0`, size 636×573 with
equal destination, source box 636×573 and normal transform. Before camera
calibration the global source box was `[-1918,-1282)×[25,598)` at applied
`scroll_x=1760`. One signed delta `-1600` produced applied `scroll_x=160`
and the remeasured source box `[-318,318)×[25,598)`. A second pre-episode
measurement confirmed the same source buffer; no prior episode pointer was
used. The requested `gaps inner current set 30` changed the target configure
to 636×513.

The transaction created target saved tree `0x557502b820e0` under its view,
and saved scene node `0x557502bada50` referenced that **same current source
buffer**. The node was enabled, the current content disabled, and its
effective saved box was `[-318,318)×[25,598)`. Its own `SB_RENDER` entry at
monotonic ns `123224008686383` had visible bounds
`[-318,0)×[25,598)` and damage extent `(482,25,800,598)` in H1 output
coordinates. The outer tiled Mosaic scene clip at camera 160 ended at the
global `x=0` boundary. H1 held capture retained **182,214** pixels of the
old target SHM color; H2 contained zero. After timeout, the gap-adjusted
outer clip ended at `x=-30`, matching the later live rendering limit. The
trace does not isolate a separate content clip as the cause of that limit.

The target received real XDG configure serial 50 and logged `HELD` at
monotonic ns `123224009029100` without ACK. Two prepared pointer motions
were sampled during that hold. At global `(100,100)` on H2,
`wlr_scene_node_at` returned a non-saved reference node with an associated
Wayland surface, and the static reference received `MOTION x=98,y=75`.
At global `(-159,311)` on H1, it returned the target saved scene node with
no associated Wayland surface; the held target client received no motion.
No invisible saved-target hit was observed at the sampled H2 point. The
seat notification path for the H1 saved node was not directly traced and
broader input behavior remains unqualified.

SwayFX logged `Transaction ... timed out (1 waiting)` at about 2.5 seconds
after `HELD`. The target client was still alive, continued dispatching,
and had not ACKed serial 50. The target saved tree was destroyed at
monotonic ns `123226508834753`; live source rendering and an ordinary
surface hit reappeared after application. No same-node render entry was
observed between this destruction and the controlled client exit. The
post-timeout H1 PNG contained 116,964 pixels of the old target color in the
new geometry; the full H2 PNG stayed unchanged. Additional short-lived
saved trees in the log begin during controlled client/window cleanup **after**
the measured timeout; their reused pointer values do not belong to the
timeout tree. Process exit codes and socket cleanup are retained in
`exit-status.json` and `events.jsonl`.

This establishes the target saved buffer's crossing, partial clipping,
render, H2 exclusion and natural timeout cleanup in the tested horizontal
matrix, alongside the previously preserved E1 ACK. The sampled input points
show no invisible H2 hit. Damage trace extents and stable PNGs do not cover
all intermediate frames; scene-node destruction does not prove full GPU or
texture reference release. These limits set
`SWAYFX_MOSAIC_SAVED_TARGET_TIMEOUT_INPUT_PROBE=PARTIALLY_FEASIBLE`.
The architectural conclusion for **this tested matrix** is
`SAVED_TARGET_TIMEOUT_CLIPPING_FEASIBLE_FOR_TESTED_MATRIX`; production
STEP20C remains NEXT and multi-output remains NOT YET SUPPORTED. The next
separate gates are optimized blur/cache, then SceneFX ABI/package.

## Offline evidence freeze (2026-10-12)

The freeze started on `main` at
`75f057d4717668fcec32755b79cff70b16ea355d`, also returned by direct
Forgejo and GitHub `ls-remote` queries. Only this report, its source fixture
and the five expected canonical/index/changelog additions were pending.
All 913 source entries and all 46 evidence entries were available and
matched their historical manifests; neither manifest was rewritten. The
four H2 PNG hashes and complete RGB images were independently rechecked
without a mask. Raw compositor and client lines confirm the source/saved
buffer identity, target render, held serial, natural timeout, transaction
application, tree removal and the two distinct hit/surface observations.
The historical budget remains closed at 1 run, 1 episode, 1 camera
adjustment and 8 of 12 captures. No graphical run was added.

Shell syntax, Python AST without bytecode, both C17 clients with fatal
warnings, offline ledger limits/contention, private patch applicability and
source equivalence passed. The reconstructed patch chain includes the
inherited clip, hidden-owner guard, temporal output trace, native
presentation trace, output ownership trace, saved trace, target geometry
and target hit trace. The private SceneFX chain also matched its retained
modified source. Compilation of the retained private Mosaic build and
Meson `mosaic-model` passed (1/1). The first archive extraction into `/tmp`
failed with `Disk quota exceeded`; a bounded temporary archive on the home
filesystem completed the offline reconstruction and was removed. This
recovered validation failure did not consume a graphical reservation.
Markdown local targets, generated-artifact exclusion and the complete
tracked/new-file delta were checked before publication. This freeze
preserves PARTIALLY_FEASIBLE and the limited-matrix architectural conclusion
above; it does not qualify GPU references or every transaction frame.
