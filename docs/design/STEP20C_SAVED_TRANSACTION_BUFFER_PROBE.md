# STEP20C saved transaction buffer clipping and lifetime probe

**EXPERIMENTAL / INCONCLUSIVE, preserved after execution.** STEP20C remains NEXT and
multi-output Mosaic production is NOT YET SUPPORTED. This campaign follows
the [static R90 popup evidence](STEP20C_ROTATED_PARTIAL_POPUP_CLIP_PROBE.md)
without changing production Mosaic, SceneFX algorithms, UX or packaging.

## Source contract and ownership

Pinned inputs: SwayFX 0.6 `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`,
private Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754`, SceneFX 0.5
`37ccd723bef49e6891156ffafce8f549f01446cc`, wlroots 0.20.2. The
private source tree is disposable; installed libraries remain untouched.

`transaction_commit()` configures a visible changed-size view when
`should_configure()` sees different current/instruction content dimensions,
then calls `view_save_buffer()` for every visible view instruction without an
existing saved tree. `view_save_buffer()` creates `saved_surface_tree` under
`view->scene_tree`, places it below `output_handler`, initially disables it,
iterates enabled buffers of `content_tree`, creates new scene buffer nodes,
and calls `wlr_scene_buffer_set_buffer(sbuf, buffer->buffer)`. This reuses a
referenced source buffer; it does not copy pixels to a new SHM image.
SceneFX's setter calls `wlr_buffer_lock()` on a non-null buffer and unlocks
the previously owned buffer when replacing it; its texture conversion path
may release that lock after obtaining a texture. Node destruction releases
its owned buffer/texture through the same scene lifetime. Pointer equality at
creation is therefore evidence of reuse, not proof that one particular buffer
lock remains held throughout every rendered frame.
The live content tree is then disabled and the saved tree enabled.

The saved tree is a **sibling** of `content_tree`, not its descendant.
`apply_container_state()` normally removes it via `view_remove_saved_buffer()`:
destroy saved scene nodes and enable live content. The destroying-container
branch skips this immediate removal; close animation and container teardown
must be audited separately. XDG commit uses the actual current configure
serial to notify transaction readiness; a nonmatching commit can send frame
done to a saved view. `transaction_progress()` applies when all waiting
instructions are ready. Its timeout callback sets waiting to zero and uses
the same progress path. A new pending transaction cannot commit while a
queued transaction exists. `-Dtxn-timeout=1200` sets the private test policy;
the code default is 200 ms. No `-Dtxn-wait` or `-Dnoatomic` is permitted.

`view->scene_tree` is normally reparented under tiled container
`content_tree`. The private Mosaic clip is set on the owning workspace's
`layers.tiling`; SceneFX's `scene_node_intersect_clip()` walks all tree
ancestors for render visibility and damage, and `scene_node_point_inside_clip()`
guards node-at. Thus inheritance is plausible for the saved sibling, but
runtime parentage, enabled state, actual buffer, render contribution and pixels
must be observed. The `SWAY_SCENE_DESC_SAVED_BUFFER` descriptor marks saved
nodes. `SWAY_SCENE_DESC_VIEW` marks the view tree; container descriptors
identify ownership. `output_handler` is an input-rejecting buffer above the
saved tree and tracks output updates. A saved scene buffer is not itself a
Wayland surface: node-at, surface lookup, seat notification and client delivery
are separate observations. An output buffer and an optimized blur cache are
different objects with different lifetimes.

For destruction, XDG unmap calls `view_unmap()`, which starts container
destruction. `container_destroy()` asserts zero transaction references before
detaching the view and destroying its scene tree; `view_destroy()` also asserts
the view is unmapped, marked destroying and detached. The destroying branch
of `apply_container_state()` deliberately skips immediate saved-tree removal.
`transaction_destroy()` can defer final container deletion through a close
animation, whose completion callback removes the saved tree before destroying
the container. The observed ACK/timeout episodes did not exercise mapped-view
destruction while a transaction was waiting; that path remains NOT TESTED.

## Controlled fixture and evidence gates

Use one C17 XDG SHM client in all modes. It maps a deterministic initial
buffer, logs configure serial/size/monotonic time, keeps dispatching pings and
input, and accepts `hold_next_configure` / `release_configure` over a private
control channel. Release ACKs the latest valid serial and commits the
corresponding size; it never invents a serial. A normal geometry command
(candidate: `gaps inner` after source and IPC calibration) must create a real
visible view instruction, a nonempty saved tree, live-content disablement
and a waiting transaction. A camera change alone is insufficient. A source
trace without an active nonempty saved buffer does not pass S1.

Use H1 `800×600`, scale 1, normal, origin `(-800,0)`, and H2 `800×600`,
scale 1, normal, origin `(0,0)`. H1 hosts four tiled cells and a Mosaic camera
near 400; H2 hosts an ordinary reference surface. Recalculate owner, scene,
snapshot and viewport boxes from applied IPC and trace. The clipping gate
requires `saved_buffer_left < 0 < saved_buffer_right`; otherwise partial
exclusion is NOT EXERCISED. Capture a full H2 reference before transaction.

One run each: C0 pristine `splith`, C1 private `splith`, C2 private `mosaic`.
Controls validate ordinary snapshot/ACK/timeout/lifetime behavior, though
standard tiling need not overflow. S0 calibrates outputs, renderer, PNGs,
view/owner, viewport, pointer and ordinary input. S1 retains a real configure
and proves creation, active buffer and wait. S2 captures active snapshot,
render entries, ancestor clip, H1/H2 pixels, damage and commits/presents.
S3 samples allowed, forbidden and ordinary H2 hit points, separating node-at
from client delivery. S4 releases and observes ACK, commit, apply, saved-tree
destruction, restored content, pixels and damage. S5 holds a second configure
past the real timeout with the client alive and checks cleanup. S6 may use
one camera hide/return pair only if S1–S4 show actual saved rendering and
source/runtime prove overlap with the active snapshot. A queued camera
request alone proves nothing. Mapped-view destruction is audited; unsafe
runtime destruction remains NOT TESTED.

Passive private traces may record tree/buffer creation and destruction,
source buffer identity, parent chain, clip, enabled state, render entry,
damage, transaction wait/ready/timeout/apply, node-at and output commit/present.
Use CLOCK_MONOTONIC and ephemeral identities scoped to lifetime. Logging must
not add a buffer lock or change clipping, render, scheduler or ABI behavior.
Compare whole PNGs and measured damage in their actual coordinates. A pair of
captures cannot qualify every intermediate frame, and grim does not identify
the native presented buffer.

## Budget and classification

The single persistent locked ledger reserves before execution: at most three
main runs, one per mode; two targeted transaction episodes per mode (ACK and
natural timeout); one Mosaic camera hide/return pair; 20 captures per run,
60 overall; 150 seconds per run unless explicitly justified before launch.
Failed attempts consume reservations. No reset, refund, clone bypass or extra
run to repair placement. Historical probe ledgers remain unchanged.

FEASIBLE requires an actual rendered saved buffer crossing x=0 under Mosaic,
correct H1/H2 pixels and hits, ACK and timeout removal, no blocking standard
regression and supporting measured damage. PARTIALLY_FEASIBLE means a real
saved tree works but lifetime, input or pixels remain unqualified. INCONCLUSIVE
means the snapshot, boundary or live/saved distinction cannot be exercised.
BLOCKED requires a reproducible forbidden pixel/hit, reference defect, crash
or blocking standard regression. Stop the affected scenario for a protocol
error, uncalibrated geometry or proven leak. Do not patch algorithms to pass.

All builds, sockets, logs, PNGs and results stay outside Git under one private
LAB. Every headless run uses a private 0700 runtime, WAYLAND_DISPLAY and
explicit SWAYSOCK. The source fixture is under
[tooling/probes/step20c-saved-transaction-buffer](../../tooling/probes/step20c-saved-transaction-buffer/README.md).
Saved buffers do not qualify optimized blur, all effects/animations, all
transforms/scales/backends, complete intermediate frames, SceneFX ABI/package
or production STEP20C.

## Measured campaign

**INCONCLUSIVE / measured 2026-10-12.** One headless run was reserved per
mode. The pristine standard control completed held-configure/ACK and natural
timeout episodes with `-Dtxn-timeout=1200`. Four nonempty saved buffers were
created per target episode, with source/saved buffer pointers equal and
`content_enabled=0 saved_enabled=1`; all four trees were destroyed about
56 ms after ACK in episode one and about 1200 ms after creation in episode
two. The pristine SceneFX installation did not carry the private render-entry
trace, so its exact saved-node render contribution is unqualified. H2 stayed
identical through both held captures; the final timeout H2 capture changed
253 pixels in box `[4,35,15,58)`, not yet causally attributed; the Mosaic
timeout capture has the same count and box.

The private-standard ACK episode created four saved buffers and four of their
nodes reached `SB_RENDER`, but the fixture injected six slow pointer actions
during the 1200 ms hold. New XDG serials superseded the first retained serial;
the client correctly ACKed the latest serial after the compositor's natural
timeout. The runner then failed waiting for a post-ACK destruction that had
already occurred. Its single run and ACK reservation remain consumed; its
timeout episode is NOT EXERCISED. This is a fixture timing incident, not a
demonstrated compositor regression.

The private Mosaic run completed both episodes. Each created four saved
buffers; two saved nodes reached the private render-entry trace before each
held capture, and all four saved trees were destroyed after ACK or natural
timeout. The `layout mosaic scroll 400` command was relative to the existing
camera: applied IPC/scene state settled at scroll **1760**, with H1's tiled
scene at `-1760` and clip `(1760,0,800,600)`. The target owner's IPC rect
was `[-160,480)` and its camera-adjusted box was `[-1920,-1280)`, wholly
outside H1. Its deterministic SHM colors had zero pixels on both H1 and H2
through the Mosaic captures. Consequently, the target snapshot did not
exercise `saved_buffer_left < 0 < saved_buffer_right`, and the central partial
clipping test is **NOT EXERCISED**. Other visible saved nodes rendered; the
trace does not identify them as the target. H2 was identical to reference
through the held/ACK captures, then changed 253 pixels in the final timeout
capture, in the same `[4,35,15,58)` box as the pristine control. This is
unqualified without a full causal frame trace. No forbidden target
pixel or crash was demonstrated. Input, node-at, damage coverage, camera hide
while a target snapshot is active and mapped-view destruction remain NOT TESTED.

The campaign budget ended at 3/3 runs and 5/6 targeted episodes: control
ACK+timeout, private standard ACK attempt, Mosaic ACK+timeout. Captures were
10/20, 4/20 and 10/20 respectively, 24/60 total. No camera hide/return pair
was used. Failed reservations were not refunded. The private LAB is
`/tmp/swayfx-mosaic-nested-grab-KYJ2pj1o`; `results/` contains raw-derived
JSON and source/evidence manifests. No additional run is authorized by this
campaign. Verdict:
`SWAYFX_MOSAIC_SAVED_TRANSACTION_BUFFER_PROBE=INCONCLUSIVE` and architectural
conclusion `UNDECIDED`. The next saved-buffer gate needs a new explicitly
authorized campaign with a pre-run applied camera/owner crossing calibration;
this campaign gives no production STEP20C authorization.

The final source manifest contains **906 entries**, SHA-256
`e11a0800b84f6a7b12a383faa87d9d04bf8d53232fb83e6d12574b8569cc384c`.
The evidence manifest contains **90 entries**, SHA-256
`5c00b78b19fcffacb3922bdb600300188972e85b83fe8356aebbc65280dc7e30`.
Both passed entry-by-entry verification. The passive Sway trace patch is
`106544aade58e05e7245601ee380e763ac19521f7d51e1ada410b4e1e7a19997`;
the SceneFX trace patch is
`82ebdd4fb003be1729ecef443a92190b010f65b62ed858c546c019743998037e`.
These hashes identify the local source fixture; no phase-B commit or push
was made.

## Executed runner provenance and camera correction

The exact runner used for each run is retained in its `runs/*/fixture-source.py`,
covered by the evidence manifest. Their SHA-256 values are: pristine
`bc041eb7be89da9e198bb9ca2e25cfe86467c264e3687e6d9d3f3836e82ce40c`,
private standard `67aa3fb94901739bea0b1d0e0cf881081d2388a02256dddc45282d7a4bc86b25`,
and private Mosaic `cdece69cf956e550779bd992b0d38234629ca1e611dfb3fb0348c04841c47f59`.
The checked-in `run.py` matches only the final private Mosaic copy. The
pristine copy had no pointer injector. The private-standard copy added the
pointer daemon and six move/right actions during the retained ACK episode.
The Mosaic copy retained the daemon but removed those six actions after they
consumed the 1200 ms window in the private-standard run. The last standard
ACK used a real serial, but followed the natural timeout; the fixture then
waited for an already completed saved-tree destruction. This is a fixture
failure, not a demonstrated SwayFX regression. The corresponding raw run
source and timeline must be used for historical reconstruction.

`sway/commands/layout.c` computes `next = row->state.scroll_x + delta`.
Consequently `layout mosaic scroll 400` added 400 to the existing camera;
the observed applied `scroll_x` was 1760. The target IPC owner box
`[-160,480)` would translate to `[-1920,-1280)`, wholly outside the viewport.
This owner estimate is not a measurement of the source buffer's scene box.
A new campaign must measure that buffer, calculate one signed correction from
the applied camera, and reject the run before any transaction reservation if
the buffer itself does not cross `x=0`.

The final timeout H2 images of pristine and Mosaic both differ from their
references by 253 pixels in `[4,35,15,58)`. The common extent does not
identify the cause. A cursor or reference artifact remains a hypothesis;
the captures were not altered and no Mosaic attribution follows.

The historic ledger is exhausted at 3/3 runs, 5/6 reserved episodes,
24/60 captures and 0/1 camera pairs. The unused episode cannot replay an
old run. Saved-tree removal in completed episodes establishes node cleanup,
not exhaustive GPU texture/reference release. Transactional input, damage,
mapped-view destruction and distinct effects/caches remain NOT TESTED.
The private Mosaic trace retained 57 output commits and 55 headless presents
over the whole run; private standard retained 100/98. These are run totals,
including startup, capture and teardown activity, and do not identify the
exact native buffer content of a particular screenshot. The pristine
control lacked the private commit/present trace.
