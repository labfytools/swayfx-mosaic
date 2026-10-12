# STEP20C saved target boundary crossing probe

**EXPERIMENTAL / PARTIALLY_FEASIBLE, measured 2026-10-12.** STEP20C remains NEXT and
production multi-output Mosaic is NOT YET SUPPORTED. This is a new, independent
campaign following the [saved transaction buffer freeze](STEP20C_SAVED_TRANSACTION_BUFFER_PROBE.md),
whose verdict remains INCONCLUSIVE. No Mosaic production, cumulative patch,
package, UX or SceneFX algorithm change is authorized here.

## Scientific identity and source path

The target is the XDG toplevel with `app_id=org.mosaic.SavedBufferProbe`.
Its Sway tiled container, borrowed workspace tiling row, view scene tree,
live content tree, temporary saved tree and saved scene buffer are distinct.
The source buffer of this view must be identified before the transaction.
An output buffer or optimized blur cache is never evidence for that source.

`transaction_commit` configures a changed-size visible view when
`should_configure` holds, then `view_save_buffer` creates a sibling saved tree
under `view->scene_tree`. `view_save_buffer_iterator` visits enabled live
buffers via `wlr_scene_node_for_each_buffer`, creates saved scene nodes via
`wlr_scene_buffer_create`, and calls `wlr_scene_buffer_set_buffer` with the
source buffer. Current live content is disabled and the saved tree enabled.
`transaction_progress` applies on readiness or `handle_timeout`; the normal
`apply_container_state` path calls `view_remove_saved_buffer`. SceneFX's
`scene_node_intersect_clip` intersects ancestral tree clips for visible/damage
regions and `scene_node_point_inside_clip` guards node-at; `scene_entry_render`
is the actual render-entry observation. This source path warrants a test, not
a clipping conclusion. The target node ID must be correlated from source to
saved creation to render entry and destruction. Parentage and enabled state
must be recorded. Pointer equality alone does not prove all GPU references
were released.

## Geometry gate before reservation

Use only two normal scale-1 headless outputs: H1 `(-800,0),800x600` and H2
`(0,0),800x600`. Map the deterministic C17 XDG client and ordinary reference
clients, settle focus, query actual outputs and workspace Mosaic state, and
measure the target **source scene buffer**: node pointer, source buffer
pointer, global node coordinates, destination width/height, source box,
transform, owner container/view, applied camera and tiled clip. A container
rect alone is insufficient. The previous runner issued relative
`layout mosaic scroll 400` and reached applied scroll 1760, leaving its target
outside H1. Here `desired_scroll` is computed from the measured source buffer
left/right and applied `current_scroll`; issue exactly one signed
`delta=desired_scroll-current_scroll`, then remeasure. Require
`left<0<right`, preferably at least 64 logical pixels on each side, a visible
H1 intersection and a theoretical H2 intersection. The source must be
nonempty, have a tiled Mosaic ancestor clip, and remain stable after focus.
If any gate fails, stop that run before reserving an episode. Do not scan
camera positions or create a second lab to evade the budget.

The transaction trigger may alter pending dimensions. During the hold,
remeasure the **saved** scene buffer and require all of:
`SAVED_TARGET_CREATED`, `SAVED_TARGET_ENABLED`,
`SAVED_TARGET_BUFFER_NONEMPTY`, `SAVED_TARGET_CROSSES_X0`, and
`SAVED_TARGET_RENDER_ENTRY_OBSERVED`. Correlate exact view, owner, source
buffer and saved node. If the actual saved node does not cross, classify the
episode NOT EXERCISED even if another saved node renders.

## Episodes, observations and bounds

Use pinned SwayFX 0.6 `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`,
private Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754`, SceneFX 0.5
`37ccd723bef49e6891156ffafce8f549f01446cc` and wlroots 0.20.2.
Reapply the preserved clipping and trace patches without changing their bytes.
Any additional passive trace is a separate hashed private patch. Build and
run only in one disposable `/tmp` laboratory, with private 0700 runtime,
Wayland and Sway IPC sockets. `-Dtxn-timeout=2500` is a lab policy only; source
parsing and equal use in comparable modes must be confirmed. Do not use
`-Dtxn-wait`, `-Dnoatomic`, direct save calls, compositor sleeps or altered
pending transaction counts.

At most one run each: C2 private Mosaic (priority), C0 pristine splith and C1
private splith. Each has at most two reserved episodes: E1 real configure
hold then latest-valid-serial ACK and commit before timeout; E2 a second real
hold until natural timeout with the client alive and pings serviced. The
ordinary `gaps inner current set` trigger is acceptable only when a changed
target configure and waiting instruction are observed. During E1 collect the
target saved node, render entry and minimal capture, then release promptly;
no six pointer injections during the hold. Observe applied transaction,
saved-tree removal and live-content return in both episodes.

Define H1 permitted and H2 forbidden regions before pixel analysis. Require
target SHM color on H1 while the saved node renders, no target color on H2,
and whole-H2 RGB equality against its reference; retain every difference.
Sample allowed and forbidden pointer points only if the hold window permits.
Distinguish `wlr_scene_node_at`, descriptor/surface association, seat notice
and client delivery; a saved scene buffer need not deliver clicks to the
held client. Record available damage around creation, activation, removal and
new live image, native commits/presents when traced, and do not infer every
intermediate frame from stabilized PNGs. Do not compare unrelated clocks.
Mapped-view destruction is NOT TESTED unless separately shown safe and within
budget. No rotation, scale, migration, resize, popup, effects or camera
hide/return pair belongs to this campaign.

The locked persistent ledger permits three runs, two episodes per mode, one
calculated camera adjustment in the Mosaic run, at most 16 captures per run
and 48 overall, and 150 seconds per run. Reserve before an episode; a failed
reservation is consumed and never refunded. Preserve the exact runner copy,
raw logs, outputs, captures, exit codes, structured JSON and SHA-256 source
and evidence manifests. Offline ledger tests precede any run. Stop early on
uncalibrated geometry, a noncrossing saved target, or an incident; preserve
the facts and do not call placement error BLOCKED.

FEASIBLE requires correct target identity/crossing/render, permitted H1 pixels,
no forbidden H2 pixels/hits, ACK and timeout cleanup and no blocking standard
regression. PARTIALLY_FEASIBLE requires crossing and rendering with limited
input, lifetime or damage evidence. INCONCLUSIVE covers absent target
crossing/render or inseparable identities. BLOCKED requires a reproduced
forbidden pixel/hit, lifetime defect, crash or blocking regression. Any
unstudied matrix cell remains NOT TESTED. Neither an experimental success nor
a compile qualifies STEP20C production.

## Measured campaign and incidents

The independent LAB is `/tmp/swayfx-mosaic-nested-grab-eVtLtpYd`. Its private
passive geometry patch is `target-geometry-trace.patch`, SHA-256
`7bbb27bc8617645e1acfd0589a410d470426363bd8a108bd43fc1006747f012e`.
The old saved-buffer Sway and SceneFX trace patches retained their published
bytes. The private build used `-Dtxn-timeout=2500` in all three modes; source
parses `txn-timeout=` into `server.txn_timeout_ms`, whose default is 200 ms.
All outputs were queried as H1 `(-800,0),800x600` and H2 `(0,0),800x600`,
scale 1, normal. The target's workspace was ID 6 on H1, container ID 8,
view `0x55997bcb85b0`; pointers identify objects only within this process.

Before correction the applied camera read **1760** and the actual source
scene buffer was `[-1918,-1282)` with 636×573 destination/source size,
normal transform and source box `(0,0,636,573)`. The fixture computed
`desired_scroll=160` and issued exactly one relative delta **−1600**.
Afterward `get_tree` read scroll **160** and the same source node/buffer at
`[-318,318)`, y=25..598. H1's applied tiled scene was `(-160,0)` with clip
`(160,0,800,600)`, equivalent to global x `[-800,0)`. No subsequent focus
action moved the camera. The 318-pixel permitted and theoretical forbidden
horizontal portions exceed the 64-pixel preflight target. This run passed
source preflight before E1 reservation.

In E1, a genuine held configure (serial 50) followed a changed target size.
The target saved tree `0x55997bcecd00` was created under its view tree,
and target saved node `0x55997bd6a560` reused source buffer
`0x55997bd4ec00`. Its measured global box was `[-318,318)×[25,598)`;
`content_enabled=0`, `saved_enabled=1`. The **same node** entered `SB_RENDER`
with global visible extent `[-318,0)×[25,598)` and damage extent in output
coordinates `[(482,25),(800,598))`. The held H1 capture contained **182,214**
pixels of the target's prior SHM color `(32,208,160)`; the H2 capture
contained **zero** of that color. The client ACKed the real serial 50 and
committed a new buffer before 2500 ms; the target saved tree was destroyed,
and the applied H1 capture contained the new target color. This is direct
partial saved-target crossing and render evidence, rather than evidence from
the other three saved nodes in the transaction.

Whole-H2 RGB comparison did **not** equal its reference during E1: 253 pixels
changed in `[4,35,15,58)`. Each changed pixel went from `(245,224,220)` in
the reference to `(48,48,56)` in the held image. The same count, box and color
transition appeared in the new pristine control after timeout and both old
pristine/Mosaic final-timeout comparisons. It is consistent with a
reference-specific disappearing shape, but its cause is **UNDECIDED**. It is
not target SHM color, and this evidence does not establish a Mosaic leak.
The whole-H2 equality requirement nevertheless remains unmet.

E2 created a new saved buffer after E1's ACK, as the ordinary client commit
changed its source pointer. The new target snapshot was observed at
`[-258,378)×[55,568)`, and its own node `0x55997bcea350` entered render
with visible extent `[-258,-30)×[55,568)`. The **executed runner** still
compared that new pointer with the pre-E1 source pointer and stopped with
`actual target saved buffer does not cross x=0`. That error is misleading:
the trace proves crossing; the failed condition was stale buffer identity.
The runner was corrected locally to remeasure before each episode, but the
exact executed copy remains in `runs/*/fixture-source.py`. No Mosaic E2
capture or natural timeout was obtained; shutdown follows the fixture
exception. Do not treat this as a compositor timeout or clipping failure.
The run was not repeated and both episode reservations remain spent.

C0 (instrumented pristine SwayFX source, unmodified SceneFX behavior) and C1
(private standard `splith`) completed their held ACK and natural 2500 ms
timeout episodes, with saved-tree cleanup. Their standard tiling geometry is
not camera-equivalent to C2. Neither had target-color pixels on H2 during its
ACK hold. No blocking standard regression was demonstrated. The new C0 final
timeout image showed the same 253-pixel H2 difference; C1's H2 remained
identical throughout. C2's target input during hold, surface/client delivery,
complete damage and native buffer/texture release remain **NOT TESTED** or
unqualified. Mapped-view destruction, output changes, effects and intermediate
frames were outside the matrix.

The persistent ledger reads **3/3 runs**, **6/6 episode reservations**,
**26/48 captures** (C0 10, C1 10, C2 6), and **1/1** calculated Mosaic
camera adjustment. All run durations were below 150 seconds. No extra run or
camera retry is authorized. The raw runs, structured results, runner copies,
exit codes, build log and SHA-256 manifests are under the LAB. The result is
`SWAYFX_MOSAIC_SAVED_BUFFER_TARGET_CROSSING_PROBE=PARTIALLY_FEASIBLE`:
target crossing/render and permitted H1 pixels are established, while whole-H2
equality, input, full damage/lifetime and Mosaic target timeout cleanup are
unqualified. Architectural conclusion: `UNDECIDED`. No SceneFX algorithm or
production Mosaic correction is justified by a reproduced counterexample.

The final source manifest covers **913** entries (including the three private
source trees and fixture), SHA-256
`816b55d94936fa32c7272845cd2f0514a55ad73b3cb04d32d442d5910e3da09b`.
The evidence manifest covers **99** raw and derived entries, SHA-256
`0ea45da93396810cf63c451f64d47101c4d4b8c7fb27900043494a0ec591096e`.
Both passed entry-by-entry verification. They exclude the report itself, whose
wording was synchronized after the measurements.

## Freeze audit: H2 reference and E2 clip (offline, no replay)

The exact executed runner is the manifest-covered `fixture-source.py` in each
run (SHA-256 `51eb1274b757701e80f54004016944b7fa23f731d194193d1baabbe25a6cdc82`).
The preserved local `run.py` differs: it remeasures `TARGET_SOURCE` before
each episode, so E2 no longer compares a post-ACK source buffer against the
pre-E1 pointer. This fixes the identified correlation condition in source;
the corrected runner was **NOT EXECUTED** in this exhausted campaign.

An offline full-RGB comparison of the old and new LABs found five nonempty
H2-reference differences: old pristine timeout-applied, old Mosaic
timeout-applied, new pristine timeout-applied, and new Mosaic ACK-held and
ACK-applied. **Each** has exactly 253 changed pixels filling the complete
rectangle `[4,15)×[35,58)` (11×23), with every pixel changing from
`#F5E0DC` `(245,224,220)` to `#303038` `(48,48,56)`. No other H2 pixel
differs in those comparisons, and none of the changed pixels is a target SHM
color. The corresponding new-reference-to-image capture-start intervals are
about 2.725 s for pristine timeout, 0.083 s for Mosaic ACK-held and 0.180 s
for Mosaic ACK-applied; the old pristine/Mosaic timeout intervals are about
1.455/1.476 s. Other sampled H2 pairs remained equal. These timings can
sample either phase of a blinking cursor; they do not prove a blink event.

The H2 reference process was Kitty with the fixture argument
`background=#303038`. The local `~/.config/kitty/kitty.conf` and included
`generated-appearance.conf` predate these runs and contain `cursor_shape
block`, a later `cursor_blink_interval 0.5`, and cursor color `#f5e0dc`.
The matching filled rectangle, exact colors and repeated pristine/Mosaic
observations strongly support a blinking Kitty block cursor as the cause.
The recorded logs do not capture Kitty's effective parsed configuration or
its cursor phase, so **causal confirmation remains open**. Whole-H2 RGB
equality remains historically unsatisfied; no pixels were masked or images
rewritten. The next lab must use a static reference.

The E2 saved target itself crossed x=0. Its render visible extent ended at
`x=-30`, matching the **applied tiled Mosaic clip after E1's 30-pixel gaps**:
H1 logged `tile_scene=-130,30`, local clip `(160,0,740,540)` and global
viewport `[-770,-30)×[30,570)`. The source in `transaction.c` derives clip
width/height from output usable area minus current gaps. Thus the measured
right bound is explained by this outer tiled clip and gap geometry; it does
not establish an additional content/view clip. E2's timeout and cleanup
remain **NOT TESTED** because the fixture stopped before expiration.
