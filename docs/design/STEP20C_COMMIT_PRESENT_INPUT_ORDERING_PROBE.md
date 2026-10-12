# STEP20C commit, present and input ordering probe

**Status: EXPERIMENTAL / INCONCLUSIVE.** STEP20C stays
**NEXT** and multi-output Mosaic **NOT YET SUPPORTED**. All compositor and
client changes for this probe belong to disposable private copies. No
production, packaging, ABI or UX decision follows from this protocol.

## Question and distinct states

The mutation coverage probe found T3 client pixels changing at fixed intended
geometry and T4 input hit changing while `asi_applied_epoch=12` and sampled
pixels stayed fixed. T4 is a normal possible Wayland transition, not proof of
a clipping defect. The question here is whether a real client input-region
commit can execute between one accepted output commit and that commit's
headless present, and what the actual scene hit and client delivery then do.

Keep five identities separate: client **content** buffer; effective Wayland
**input** region; applied **scene geometry** and clip; native output
**presentation** `(output, commit_seq)`; and pointer **grab/delivery** state.
A submitted output buffer is not changed retroactively when a later surface
commit changes input. A later pointer hit may legally consult newer input
than the pixels in that buffer. A mismatch alone is not a Mosaic defect.
No experimental epoch is treated as an atomic native generation.

## Source audit and scheduling hypotheses

Audited pinned inputs are SwayFX/Mosaic based on SwayFX 0.6, private SceneFX
0.5 at `37ccd723bef49e6891156ffafce8f549f01446cc`, and wlroots 0.20.2
at `d783533489e1f75d6886c2ab5c5960090ef268f8`. The frozen private
instrumentation is the Mutation Coverage chain. Wayland server API semantics
are checked against `wayland-server-core.h` and the executed callbacks.

`sway/desktop/output.c:output_repaint_timer_handler` checks
`wlr_scene_output_needs_frame`, logs private `BI_STAGE` before and after
`wlr_scene_output_build_state`, then calls `wlr_output_commit_state`.
wlroots `types/output/output.c` calls the backend commit, increments native
`commit_seq`, applies state, and emits `events.commit` synchronously on
acceptance. The private `PI_OUTPUT_COMMIT` listener runs in that callback.
The headless backend `backend/headless/output.c:output_commit` queues a
present with `commit_seq + 1` through `output_defer_present` when enabled.
`types/output/output.c` puts this on a Wayland event-loop idle source. The
idle callback calls `wlr_output_send_present`; an output destroy removes
the idle source and cancels that pending present. Allocation failure could
also prevent queuing. Thus `present` is deferred in source but not guaranteed
for every commit. A deferred idle is not evidence that a client request
actually ran between commit and present.

`types/wlr_compositor.c:surface_handle_set_input_region` changes pending
state. The subsequent `wl_surface.commit` moves it to current state,
intersects it with current surface size into `surface->input_region`, and
emits the surface commit signal. A cached/synchronized surface can delay
application; the top-level used here is not synchronized beneath a parent.
`wlr_surface_point_accepts_input` consults effective `input_region` at hit
time. wlroots `types/scene/surface.c` installs that predicate on the scene
buffer. Private SceneFX `scene_node_at_iterator` applies scene clip and
calls it. SwayFX `sway/input/cursor.c:node_at_coords` performs the scene
lookup; seat button notification follows. XDG grabs can redirect effective
delivery, so the initial scenario has none and still checks the client log.

The scene surface commit callback calls `surface_reconfigure`. It schedules
a frame only if the surface has a pending frame callback and intersects an
enabled output; an input-only commit does not itself guarantee a new output
buffer. The Wayland idle callback is documented as running before blocking
in `wl_event_loop_dispatch`; the exact order of already-ready client fd
callbacks against that idle depends on the loop's executed dispatch order.
Passive same-process timestamps, not this source inference, will decide P2.
No recursive dispatch, backend delay, compositor sleep, forged present or
direct write to `current.input` is permitted.

## Fixture, identities and lifetime

Use HEADLESS-1 `(-800,0)` and HEADLESS-2 `(0,0)`, both 800×600, scale 1,
normal transform. Compare unmodified SwayFX `splith`, private Mosaic binary
`splith`, and private Mosaic binary `mosaic`. The T4 client keeps one mapped
420×320 colored top-level and changes its input region full → empty → full
through normal Wayland requests without a new client buffer. No popup or
grab is active in P0–P5. A stable visible point is used for all hits and
actual right-button deliveries. Each run owns a mode-0700 runtime, explicit
`WAYLAND_DISPLAY` and `SWAYSOCK`, process groups and private logs.

Passive server traces record monotonic nanoseconds for surface commit,
output build, accepted output commit, headless present, executed scene hit,
and seat notification. Output identity is valid only during its lifetime;
surface IDs are temporary. Use native output `commit_seq` and an observed
surface commit sequence when available. Client events retain their own
order; client and server clocks are not merged without calibration. The
runner must stop process groups and remove sockets. The earlier private
output lock has per-output ownership, one unlock per lock, and timer cleanup;
normal P0–P5 use trace-only mode. Rejected backend commit remains
**NOT TESTED** and will not be induced unsafely.

## Bounded matrix and validity

* **P0**: verify two outputs, layout, mapped client, reference pixel, hit,
  real button receipt, and native commit/present availability where traced.
* **P1**: commit empty input before an identified later output build, if
  one occurs; observe applied region, hit, button and output timeline.
* **P2**: seek naturally `OUTPUT_COMMIT(N) → SURFACE_COMMIT(empty) →
  SCENE_HIT(P) → OUTPUT_PRESENT(N)`, retaining actual order if hit differs.
  Count only accepted native commits and a real Wayland client mutation.
* **P3**: observe a mutation after a present as temporal control.
* **P4**: restore full input on the same surface, with stable sampled pixels,
  restored hit and actual button receipt.
* **P5**: repeat at most five full/empty cycles per mode. Preserve failed
  attempts; if no P2 interleaving occurs, mark P2 **INCONCLUSIVE**.

Only after the input-only matrix, consider a private Mosaic scroll
`400 → 1280 → 400` with two valid XDG popups if source and observations show
it can distinguish a Mosaic clip invariant. An input region alone does not
exercise the Mosaic viewport clip. A clip changing after an output commit
cannot rewrite its already submitted buffer. No scaling, rotation, migration
or hotplug is part of this matrix.

## Analysis, neutral measurement and verdict

Keep raw traces and derive `event-order.jsonl`, `surface-commits.json`,
`output-commits.json`, `presentations.json`, `input-regions.json`,
`scene-hits.json`, `client-delivery.json`, `timelines.json`, `matrix.json`
and `summary.json` in the lab. Each hit must identify the effective input
region, last accepted output commit, last observed present, next present,
actual client receipt, and whether any relation is inferred. Captures are
pixel samples, not native buffer reads. Measure log volume, commit/present
counts, commit-to-present gaps and scenario duration in standard and
private runs; headless gaps are not physical display latency.

**FEASIBLE** requires sufficient observed transitions with matching hit and
client delivery inside the tested boundary. **PARTIALLY_FEASIBLE** retains
useful observations with important gaps. **INCONCLUSIVE** applies when the
natural commit-to-present window cannot be exercised or distinguished.
**BLOCKED** needs a reproducible clipping, targeting or lifetime violation;
normal input-only change without redraw is insufficient. The architecture
answer remains **UNDECIDED** unless a concrete required invariant is either
shown to hold within the tested boundary or violated by a real counterexample.

## Executed source-audit answers

1. Headless `present` is queued as a Wayland idle callback, not emitted in
   the backend commit call. The accepted `events.commit` signal is synchronous.
2. Output destruction cancels the queued idle. A failed allocation in
   `output_defer_present` could omit it. The retained private runs also lack
   the two initial sequence-2 presents per instrumented mode; the reason for
   those initial omissions is not assigned without further callback tracing.
3. For the top-level fixture, an applied `wl_surface.commit` updates
   `surface->input_region` before the SwayFX top-level commit listener logs.
   Subsequent `wlr_scene_node_at` uses that effective region.
4. An input-only commit does not necessarily schedule a frame. Scene surface
   code schedules one conditionally for pending client frame callbacks;
   camera, cursor and other activity can separately cause output commits.
5. Only callbacks actually dispatched by the Wayland event loop can occur
   between a backend commit and its idle present. Client requests, pointer
   input or other timers are candidates, not guaranteed intervening events.
6. The public idle API says the callback runs before blocking in dispatch;
   it does not by itself establish the order against every ready client fd.
   The executed traces are the authority for this bounded backend run.
7. This fixture sought true client Wayland mutations without changing the
   backend. None landed in the commit-to-present interval.
8. An empty interval proves only that these 20 attempts did not exercise the
   proposed temporal case. It cannot prove that the interval is impossible.

## Replayed results

### Runner timing limit

The historical `run.py` inserts the scenario into the older runner. Each
`command()` waits for a complete `swaymsg` IPC response. Each
`client_command()` writes a line to the client and waits until its `COMMAND
... DONE` log appears. Each `inject()` writes to the virtual pointer client
and waits for `INJECT_DONE`. In Mosaic, the camera command is therefore
acknowledged before the input mutation is submitted; the next pointer action
also waits for client confirmation. The full-to-empty and empty-to-full
transitions repeat this sequential order. These are process and IPC
round trips, whereas many private commit-to-present gaps were only tens of
microseconds. This fixture can thus miss an otherwise possible pending-client
request during that narrow interval. The timing limit does not invalidate
the native callbacks, actual applied mutations, hits, pixels or client
delivery recorded in the runs. It limits the conclusion to the order that
was executed, and motivates a separately documented nonblocking runner.

The final fixture was overlaid on a new clone of published `main` at
`6fc849d172a1728a5a4b3b7fa31c7dc930736fe5`; its private SceneFX,
Mosaic, wlroots source-audit input and client were rebuilt in
`/tmp/swayfx-mosaic-nested-grab-D0AMNl62/`. The three runs used the fixed
two-output geometry and five region cycles each. All reported
`failure=null`, eight captures, five empty and five full client commands,
six actual top-level right-button presses, zero popup grabs and no retained
probe buffer. The sampled `(342,175)` left-output pixel remained
`(35,68,204)` at P0, first empty P1 and restored P4 in every mode.

| Mode | Native commits/presents | Applied target input commits | Matching commit→mutation→present | Target-point hits after known input commit | Duration |
| --- | ---: | ---: | ---: | --- | ---: |
| Unmodified SwayFX `splith` | Uninstrumented | Uninstrumented | Unobservable | Client receipt only | 8.870 s |
| Private `splith` | 62/60 | 10 | 0 | 25 empty: no target hit; 25 full: target hit | 8.906 s |
| Private `mosaic` | 84/82 | 10 | 0 | 30 empty: no target hit; 29 full: target hit; 2 full hits at a changed camera position reached another node | 8.923 s |

Both instrumented modes had 10/10 target input mutations after the last
matching observed present and before a later output build. This directly
supports P1 and P3 in their observed ordering. P0 verified output geometry,
native tracing, baseline pixels and button receipt. P4 restored the same
surface's input and receipt. P5 stopped after five cycles. P2 had **zero**
actual natural interleavings and is **INCONCLUSIVE**. The two unmatched
commits per private mode were initial sequence 2 on the two outputs. The
unmodified control's zero trace records mean no instrumentation, not zero
native commits. The client and server clocks were kept separate; server
nanoseconds establish all reported commit/present/mutation/hit ordering.

Private standard commit-to-present gaps ranged 20,779–24,620,493 ns
(median 76,131 ns); private Mosaic ranged 21,580–24,875,267 ns
(median 85,915 ns). These are headless event-loop gaps, not display
latencies. A separate same-workload comparison in an earlier private lab
disabled only the new surface-commit log site: private standard measured
62/60 commits/presents and 8.968 s with it, versus 63/61 and 8.893 s
without it; private Mosaic measured 77/75 and 8.891 s with it, versus
83/81 and 8.920 s without it. Both variants delivered six presses. Native
counts and gaps vary between runs; this pair does not isolate a causal
logging cost or establish a scheduling-neutral measurement.

The input-only test did not modify the Mosaic viewport clip. A second
`400 → 1280 → 400` popup transition could test clipping, but this campaign
did not produce the temporal window required to distinguish a newer clip
from an already submitted output buffer. Running that variant now would add
spatial coverage without answering P2, so it remains **NOT TESTED** in this
probe. No separate Mosaic clipping defect, crash or lifetime failure was
observed. Backend rejected commit remains **NOT TESTED**.

## Structured evidence and verdict

The [source fixture](../../tooling/probes/step20c-commit-present-input/README.md)
produces `event-order.jsonl`, `surface-commits.json`,
`output-commits.json`, `presentations.json`, `input-regions.json`,
`scene-hits.json`, `client-delivery.json`, `timelines.json`, `matrix.json`
and `summary.json` outside Git. Scene-hit records carry the last known
target input mutation, last accepted native commit and surrounding present
sequences; a nil hit's target identity is explicitly an inference from the
fixed test point. Captures are sampled pixels, not exact submitted buffers.

The final patch SHA-256 is
`0abdd61a45dc5cc63a59b5279fcd3d94a01b52ed394048259270edcc6ca582fc`.
The final source and artifact manifests hash to
`767755b02b505af2467ea9b40f67c250f9406ee720a29237d877f9c69dc2f3c2`
and `7835941aaae98ca3e5a3484defdfe0e14f246ac4693bdb13ff437c1fa29ffbd1`;
every manifest entry passed `sha256sum -c`. The matrix, summary and event
order hashes are `347f74ec86fb54691660dde6098effde2ee2a90d4055df3613f8e7810aebd9d1`,
`8202008e649c3b5782ebac2ae32e9e80875f5763ec76936ae6849c2c37598a39`
and `399c9e52087e426d2c6448dfa2bbc761f23a348ace4275b0d6472cf409993100`.

The historical artifact manifest contains 11 derived files and omits raw
run logs and captures. It remains unchanged. A second, outside-Git manifest
at `commit-present-input-results/raw-evidence-sha256.txt` in that lab
covers all 84 regular files under the three `runs/` directories and the 10
structured result files, excluding the two historical manifests themselves.
This includes configs, IPC output, compositor/client/pointer logs, captures,
output states and exit codes. It has 94 entries, all verified, and SHA-256
`9b74584936d44be5accb1f3882482fbd1eb85bc5c696b4551d45076b76ff4f8d`.
It does not cover build trees, binaries or sockets.

### Independent freeze replay

On 2026-10-12 the preserved fixture was reconstructed again in a new
disposable lab, `/tmp/swayfx-mosaic-nested-grab-a7AsuMuV/`, from the pinned
source preparation chain, not from the historical build. Pinned SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc` and wlroots
`d783533489e1f75d6886c2ab5c5960090ef268f8` were checked out in the
new lab. The three five-cycle runs all had `failure=null`, eight captures,
six real top-level right-button receipts and the same sampled pixel at P0,
P1 and P4. The standard control remains uninstrumented. Private `splith`
again gave 62 commits, 60 presents and 10 applied target mutations; private
Mosaic gave 84, 82 and 10. Both had zero target mutation between matched
commit and present. The two sequence-2 commits without observed presents
remain **UNEXPLAINED / NO PRESENT OBSERVED**. Timing values and exact event
stream hashes differed from the historical run, as normal scheduling can
vary; the measured counts and classification did not. Meson `mosaic-model`
passed in the new private build.

The independent lab's outside-Git raw evidence manifest uses the same
94-file scope and passed every hash check. Its SHA-256 is
`7d4e5c3860cc5ea3b63668441efa58bf31ef3197c6d22890cbaccee70543d41a`.
The independent matrix and event stream SHA-256 values are
`00a70483bd8ad1f30fd9e544f8253d516f4b571f4cb876dc2a960a474ee532dc`
and `71cab46cac1e41d1a08ab0d1460599074a1a0924c27e64af6c98e1afa6180ef9`.

**Probe verdict: INCONCLUSIVE** for the commit/present/input ordering
question. The sampled steady-state transitions and delivery passed, but the
discriminating temporal window was never exercised. **Architecture:
UNDECIDED.** No observed invariant requires an added applied-generation
contract, and these samples cannot prove existing ordering sufficient for
all clipping mutations. The smallest follow-up is a passive event-loop
phase trace with a client input request already pending during ordinary
repaint, preserving the native backend and five-attempt bound, to determine
whether fd dispatch can naturally precede the queued present. If that is
observed, execute a hit and client receipt in the same interval; only then
consider an owner-popup clip transition at the same output geometry.
