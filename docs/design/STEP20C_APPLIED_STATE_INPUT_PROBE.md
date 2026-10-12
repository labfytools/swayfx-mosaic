# STEP20C applied scene / input probe

**Status: EXPERIMENTAL / PARTIALLY_FEASIBLE.** The protocol was recorded
before the private patch and the bounded replay below. STEP20C
remains **NEXT**; production multi-output Mosaic is **NOT YET SUPPORTED**.
This protocol authorizes only disposable private instrumentation and fixed
headless geometry. It changes no production source, clipping policy, UX,
public ABI, package or installed dependency.

## Question and hypotheses

Can the scene actually applied at output-state construction be observed
alongside the scene used by a later real pointer hit test, without inventing
a native atomic transaction generation? The previous buffer probe identified
32 committed buffers and headless presents, but its global `bi_hold` released
IDs 3, 15, 21 and 27 when HEADLESS-2 repainted after HEADLESS-1 commits.
That private instrumentation defect prevents claiming those four buffers
were retained until present. The corrective patch is separate from the
historical fixture.

Hypotheses: a per-output hold survives a different output's repaint;
sampled visible/hidden/returned applied scene and clip agree with selected
buffer pixels; hit testing sees the sampled applied clip; actual pointer
delivery may differ from the scene hit because of XDG grab semantics. A
logical camera target, IPC acceptance, `wlr_scene_node_at()` result and
headless `present` are different observations.

## Ownership and scene audit boundary

`wlr_scene_output_build_state()` can install a swapchain buffer in the
pending output state. The state owns its reference until
`wlr_output_state_finish()`. A private `wlr_buffer_lock()` taken while that
state is live owns a separate reference; the matching unlock must occur on
present, same-output replacement, rejection, timeout or output destruction.
The lock prevents swapchain slot reuse while held. No event-state or pixel
pointer may outlive its callback or access scope. Use output identity plus
native `commit_seq`, not an address alone or predicted sequence. Never give
a no-buffer commit an earlier buffer fingerprint.

Sway's logical `scroll_x` is not itself an applied scene generation.
`transaction.c` applies current container/output scene positions and
visibility, including tiled translation; the private Mosaic/SceneFX
patches set tiled and owner-derived popup clips. XDG map/unmap and popup
hierarchy changes can mutate scene trees separately. Pending geometry,
current geometry, applied node position and logical camera are logged as
distinct fields. SceneFX clip propagation constrains render, damage and
`wlr_scene_node_at()` in the private build. The experimental epoch, if
used, advances only at explicitly instrumented mutations; it is **not**
a native SwayFX transaction generation. Mapping, effects, damage, direct
SceneFX mutations and uninstrumented upstream paths remain outside any
partial counter until proven otherwise.

`sway/input/cursor.c` calls `node_at_coords()` and scene hit testing for
pointer paths, while `sway/input/seat.c` relays button notifications to
wlroots. XDG grabs can filter delivery and issue `popup_done`. Record the
requested and resulting global coordinate, hit node/surface and current
applied snapshot at the actual hit call, then separate seat notification
and client-observed events. Never infer delivery solely from node-at, and
never assign an input event a fictional frame number.

## Private instrument and modes

Use a distinct correction patch after the frozen presentation and buffer
patches. A per-output, single-slot hold is bounded to one selected
HEADLESS-1 buffer in this matrix. Other-output repaint/present cannot
evict it. A same-output commit with a *new* buffer may replace it; a
configuration-only commit cannot. Release is idempotent by clearing the
slot before unlock. A two-second post-commit timer bounds waiting for an
absent present, but does not bound a stalled GPU readback. Track lock,
release, timer and output identity in logs. Paths not safely triggered are
**NOT TESTED**.

Mode 0 records scene, native commit/present and input with no new buffer
lock/read. Mode 1 reads at most three selected true buffers: visible 400,
hidden 1280, restored 400. Mode 2 additionally reads those buffers a
second time only while the owned lock remains live at matching present.
SceneFX FX texture readback can synchronize GPU/CPU internally. Compare
stage timings and event counts against mode 0; do not attribute total cost
solely to `glFinish()`.

## Fixed matrix and correlation

HEADLESS-1 `(-800,0)` and HEADLESS-2 `(0,0)` are each 800×600, scale 1,
normal transform. The client hierarchy is TOPLEVEL → POPUP_A → POPUP_B,
with real pointer-button serials for both grabs. Confirm outputs and
native commit/present events. Run stable 400 with a real B hit; 1280 with
the owner fully hidden; return to 400 with the same mapped A/B; then at
most three hide/return pairs. In distinct runs, click visible B, clipped
B on HEADLESS-2 and hidden owner; send six close alternating commands;
compare unmodified SwayFX and private `splith` controls without inventing
a Mosaic camera for them.

Each record uses a monotonic timestamp where available. Preserve
PRE_BUILD, POST_BUILD, COMMIT_ACCEPTED and PRESENT_CALLBACK applied
snapshots and the native `(output, commit_seq)` link. Separately preserve
the applied snapshot at hit test, the wlroots seat notification and the
client delivery. A matching experimental epoch across observations is
limited evidence only for mutations covered by its increments; time
ordering is not an atomic identity. Preserve coalesced commands and
commits without observed present as such.

## Acceptance and stop rules

**FEASIBLE** requires same-output buffer lifetime through present in the
tested paths, observed applied scene at build and hit, actual pointer
delivery agreement, bounded cleanup and no blocking regression.
**PARTIALLY_FEASIBLE** covers useful scene/render/input observations with
incomplete mutation coverage, temporal identity or error-path tests.
**INCONCLUSIVE** applies when safe observability is unavailable.
**BLOCKED** requires a reproduced memory violation, crash, visual leak,
invisible hit or blocking regression. A clean unsupported readback is not
a compositor defect. Stop on a reproducible crash and retain evidence.

Caps: three transition pairs, three selected readback buffers per run,
one held slot per tested output, 8 MiB per copied buffer, two-second
post-commit hold timeout, bounded captures/logs and explicit process
cleanup. No scaling, rotation, migration or hotplug is tested. Even a
successful fixed headless matrix does not authorize production STEP20C.

## Measurements

The primary private laboratory is
`/tmp/swayfx-mosaic-nested-grab-l2HvAkRe/`, rebuilt from the frozen buffer
fixture. Its corrected output, transaction, cursor and seat sources were
byte-identical to the independent rebuild in
`/tmp/swayfx-mosaic-nested-grab-8CiDjoij/`. The corrective patch has
SHA-256 `8a0766536fa728a6be6ef29aea3be67abbfad107f2fcd6048718097499a4d88f`.
Only these disposable copies were changed. The final-patch independent
one-pair run `private_mosaic-buffer_cycles-asi2-1791782683026614149`
again read three buffers and matched all three native commits and headless
presents, with three byte-identical second reads and one unlock per hold.
Its separate visible, clipped and hidden pointer runs repeated the
client-delivery results. The fixed geometry was confirmed by IPC in the
run snapshots; each A/B chain used two real pointer-button serials
(the three-pair run requested A=55 and B=60, each used unchanged). All
named runs exited without runner or XDG protocol failure.

### Buffer ownership and pixels

Mode 0 (`private_mosaic-buffer_cycles-asi0-1791781864140604493`) recorded
95 accepted native commits and 93 headless presents, with no probe lock or
read. Mode 1 (`...asi1-1791781908846694616`) recorded 87/85 and read three
selected buffers. Mode 2 (`...asi2-1791781917161051239`) recorded 88/86,
read those three selected states and read each again at its matching
present. The two unpaired accepted commits in each run were initial output
sequence 2, one per output: **UNEXPLAINED / NO PRESENT OBSERVED**.

The selected HEADLESS-1 buffers in mode 2 have actual native sequences
23, 27 and 30, with experimental applied epochs 13, 15 and 17. All three
are 800×600 GBM XB24 source buffers, read as XRGB8888 with stride 3200 and
1,920,000 bytes per copy. The SHA-256 sequence is
`9e6d2f7b094fd5124c0207a30cb294acec3a01da15b90008d7f7449d27e1ee7c`,
`03e815da50d0f04b16660340db19c1a03225f31bac0824d490c2ffbab0ee165c`,
then the first hash again. A/B exact-color counts are 42,200/17,940 at
400, 0/0 at 1280, then 42,200/17,940 after return. Each second read is
byte-identical. Every selected buffer matched its synchronous commit
callback, accepted native sequence and `presented=true` headless event;
each extra lock was released **once**, on that event. No cross-output
release occurred. A HEADLESS-2 `POST_BUILD` and commit intervened between
the lock of buffer ID 3 and its matching HEADLESS-1 present; the buffer
remained locked through that interval. This is the direct positive test
against the historical scope defect.

In one-pair private fault injection
`private_mosaic-buffer_cycles-asi1-1791781965826777786`, ID 1 was
intentionally retained after its present and released once when a later
accepted HEADLESS-1 buffer commit replaced it. The other two selected
buffers released on present. In separate run
`private_mosaic-buffer_cycles-asi1-1791781980485708932`, ID 1 released
once by the two-second timer (logged age 2,000,030,155 ns); the other
two released on present. The timer and slot were cleaned in both paths.
The rejected-commit and output-destroy branches compile but were **NOT
TESTED** by a controlled runtime trigger. A same-output configuration
commit without a selected new buffer was not a controlled lifetime test;
the code condition excludes eviction, but runtime qualification is
**NOT TESTED**.

The historical 32-buffer readback used 61.44 MB of first copies; this
selective run used 5.76 MB, a **90.6% reduction in copied bytes and first
readback count**. Mode 2 adds 5.76 MB for its three second reads. Sequential
runs are not a controlled latency benchmark: median HEADLESS-1
POST_BUILD→COMMIT_ACCEPTED over all frames was 0.083, 0.109 and 0.112 ms
in modes 0, 1 and 2, while the three selected readback commits alone took
about 4.255/1.621/1.082 ms in mode 1 and 3.287/1.004/1.025 ms in mode
2. Host scheduling, renderer work, copies and logs were not separated.
The readback is therefore still materially intrusive on sampled commits;
no reliable wall-clock speedup is claimed.

### Applied scene and pointer

The experimental epoch increments after `arrange_popups()` handles a
popup and after `transaction_progress()` completes `arrange_root()`.
It is visible in PRE_BUILD, POST_BUILD and COMMIT_ACCEPTED stage logs,
and at `node_at_coords()` hits and wlroots seat button notification.
The final patch also records the root-popup applied clip and logical camera
at each hit. The visible B hit had logical 400, applied tiled scene -400,
clip x=400 and a nonempty root-popup clip. With the owner hidden at 1280,
the root-popup clip was explicitly empty at the hit; the observed surface
under the pointer was an ordinary surface, not a popup. The clipped
HEADLESS-2 hit also found the ordinary surface while the root-popup clip
remained bounded to HEADLESS-1. Nested-popup mapping remains verified in
the client log, not atomically exported with the hit record.
The three selected buffers carried applied tiled scene/clip `-400/400`,
`-1280/1280`, `-400/400`, consistent with their decoded pixels. This is
an ordered observation, not an atomic frame/scene identity.

In the three-pair mode-2 run, the same owner IPC ID 8 and one A/B map
persisted through all three hide/return pairs. Six further alternating
IPC camera requests were accepted and returned to 400; they are not
counted as six presented images. Before the final visible B button, the
last observed HEADLESS-1 headless present was native sequence 48, whose
COMMIT_ACCEPTED stage and subsequent scene hit both recorded epoch 37,
applied scene `-400` and clip x=400. No *instrumented* mutation occurred
between these observations. Buffer 48 was **not** among the three copied
buffers, and the partial epoch cannot exclude uninstrumented mutations.
It does not prove atomic frame-specific input agreement.

Separate `run-negative-private_mosaic-{visible,b_cross,hidden_click}`
controls logged actual requested and obtained global coordinates,
`wlr_scene_node_at()` result, applied clip, seat notification and client
events. Visible B received its button. On HEADLESS-2's clipped B portion,
the hit and seat focus were the ordinary client, whose button was logged;
B received no button from that point and `popup_done` occurred B then A
under the XDG grab. With the owner fully hidden at 1280, the hit was an
ordinary surface under the pointer, no popup button was delivered, and
`popup_done` again occurred B then A. The private and unmodified `splith`
controls retained the ordinary crossing B button behavior. A seat's
focused-surface value is logged before wlroots notification; client logs
are the separate evidence of actual delivery. No pointer event is
assigned a native frame ID.

The counter does **not** cover every SceneFX node mutation, client buffer
commit, damage, animation, effect/saved-buffer change, direct XDG scene
change, output configuration or internal grab decision. It also increments
for some arrangements that may leave sampled state unchanged. Consequently
matching epoch values provide only bounded negative evidence about the
instrumented sites. No visual leak, invisible popup hit, memory-lifetime
anomaly, crash or blocking standard-layout regression was reproduced in
the tested matrix. Scaling, rotation, migration, full effects/damage and
physical presentation remain **NOT TESTED**.

**Verdict: PARTIALLY_FEASIBLE.** Per-output reference ownership fixes the
historical cross-output release in the tested path, and applied scene,
buffer, native present, scene hit and actual client delivery can be
observed separately. The partial epoch and intrusive readback cannot yet
establish a complete temporal scene/render/input generation. The next
minimal gate is to instrument or formally bound every applied scene and
hit-affecting mutation, then repeat a low-impact selected-buffer/input
test against that complete boundary. This is no production decision.

## Proof manifests and validation

A further fresh, bounded replay in
`/tmp/swayfx-mosaic-nested-grab-OWIvboDB/` rebuilt private SceneFX and
Mosaic from the preserved fixture chain. One visible/hidden/returned pair
produced 65 accepted commits and 63 headless presents in trace-only mode,
with no buffer lock, then 65/63 in second-read mode. All three selected
HEADLESS-1 buffers matched native presents, had byte-identical second
reads, and were unlocked once at their matching present. A HEADLESS-2
build/commit occurred while the first HEADLESS-1 reference was retained.
The three states repeated clip x=400/1280/400 and the visible/hidden/
visible color counts. Fresh visible, clipped and hidden pointer runs
reproduced the B delivery and XDG dismissal distinction; unmodified and
private standard `splith` controls delivered the crossing B button.
This is a targeted replay, not a new matrix qualification.

The primary and independent labs retain structured `results-asi/`, raw
buffers, captures, event logs and source/artifact SHA-256 manifests. The
rebuild starts from published Mosaic `11c80a40f20240a2ca137d412f6e3b711c5d5f80`,
inherits private Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754`
and SceneFX `37ccd723bef49e6891156ffafce8f549f01446cc` through the
frozen fixture chain, and uses pinned SwayFX
`fd71a6bdc061bd633b488ae7b83e8a6981d22f86` with wlroots 0.20.2.
The five-source manifest in each
lab has SHA-256
`0ef45e3e4d7623498d20db8a290ca1dd7bc6cdd6e69a2276e96a01ad1ae475cb`
and all five source checks pass. The primary lab's 729-artifact manifest
has SHA-256
`f7cdefe8d90e2548c927951341b37f8c72b2ad3e64dee53fda6f43438f2b8ef9`;
the final-patch independent lab's 189-artifact manifest has SHA-256
`d3f3782538646e37444fde3fd68a7cb494c50dfa190e6df60f176d5ddd1e47ce`.
All listed available artifacts passed `sha256sum -c`. The older main-lab
intermediate runs remain in the primary manifest as negative development
evidence; final-patch reproduction is distinguished by the independent
lab path and source-equivalence check.
