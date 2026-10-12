# STEP20C event-loop pending input probe

**Status: EXPERIMENTAL / INCONCLUSIVE after bounded execution.** STEP20C remains
**NEXT** and multi-output Mosaic **NOT YET SUPPORTED**. This probe changes no
production compositor, package, UX or backend scheduling policy.

## Question and historical limit

The [ordering probe](STEP20C_COMMIT_PRESENT_INPUT_ORDERING_PROBE.md) observed
20 applied input-region changes, with none between a matching native output
commit and headless present. Its runner waited for each camera IPC response,
client confirmation and pointer confirmation. Those cross-process waits can
outlast a commit-to-present interval. The old observations remain valid for
their executed order. This probe asks whether a normal Wayland request,
submitted without all those intermediate runner waits, is naturally applied
in that interval.

## Dispatch and repaint model

The pinned wlroots 0.20.2 and installed Wayland server 1.26.0 source (tag
commit `87cc8a8728a923fc57938faa81ba0e74f34ecdc7`) show that
`wl_event_loop_dispatch` runs queued idles before polling, dispatches ready
epoll sources with timers first, then dispatches idles created by those
sources. Thus a client fd already in the same returned epoll batch can run
after a repaint timer and before its newly queued present idle; a request
arriving later may encounter the idle first. The event loop does not promise
that an already written client request wins over an idle callback. A Wayland client `flush` sends
queued bytes toward its connection; it does not run a server handler. Distinct
states are **written by client**, **possibly readable at server**,
**dispatched by server**, and **applied to effective input**. The latter is
observed in the server surface-commit callback, after wlroots has committed
the new `input_region`. No readiness is inferred solely from client logs.

SwayFX's `output_repaint_timer_handler` builds scene output state and calls
`wlr_output_commit_state`. The accepted commit signal is synchronous. The
headless backend queues `output_defer_present`; wlroots adds a Wayland idle
callback for the matching native `commit_seq`. A later callback emits
`present`, but destruction or allocation failure can prevent it. A normal
surface `set_input_region` changes pending state and `wl_surface.commit`
makes it effective. SceneFX's scene hit predicate reads that effective region
through `wlr_surface_point_accepts_input`; SwayFX `node_at_coords` and seat
notifications follow. Surface input-only commits need not render a new
output buffer. Output build/commit/present and later input hit are different
identities; a later hit may legally use newer input than submitted pixels.

## Identities and clocks

Keep native `(output, commit_seq)` for accepted commits and presents; never
predict a sequence. Keep surface resource ID, observed `current.seq`,
`input_changed`, effective bounds and client command identity separately.
Private compositor callbacks use `CLOCK_MONOTONIC` nanoseconds to establish
server order. Runner and client logs have separate process order unless
their clocks are checked; a runner timestamp is not treated as a server
handler timestamp. `OUTPUT_BUILD`, `OUTPUT_COMMIT`, `OUTPUT_PRESENT`,
`SURFACE_COMMIT`, `SCENE_HIT` and `POINTER_DELIVERY` are passive existing
private trace sites. The unmodified SwayFX control supplies client events
and sampled pixels, not native output event traces.

## Fixed experiment

Two headless outputs remain HEADLESS-1 `(-800,0)` and HEADLESS-2 `(0,0)`,
both 800×600, scale 1, normal transform. The same mapped T4 client performs
normal `wl_surface.set_input_region`, `wl_surface.commit` and client flush.
Compare standard SwayFX `splith`, private `splith` and private `mosaic`, with
no popup or grab. Runs own private mode-0700 runtime directories, discovered
IPC sockets, logs and process groups. Captures sample fixed pixels only.

* **E0:** verify outputs, mapping, full-region right button receipt, empty
  region no target hit, and fixed pixels.
* **E1:** two sequential full/empty transitions using the historical waits.
  Retain runner submissions/acknowledgements and server callback order.
* **E2:** submit a camera IPC request when applicable, then a client input
  mutation without awaiting the IPC response or client confirmation. Await
  completion only after both submissions. Preserve whether application was
  before commit, between commit/present, after present, or without a new
  output commit. Up to five transitions per private mode.
* **E3:** submit a normal client region request before an ordinary rendering
  transition. Record client flush and server handler times; do not call the
  request server-ready without proof.
* **E4:** attempt a same-interval hit only if E2 naturally creates the
  commit/mutation/present order. Record actual scene hit and client delivery;
  no destination may be inferred for a hit that did not run.
* **E5:** restore full input on the same surface and verify client receipt,
  target hit and stable sampled pixels.

The runner offers a sequential control and an asynchronous submission mode.
It records each request and checks completion after submission; an IPC
request sent is not treated as an applied camera change. No sleep or special
idle callback is added to the compositor, headless backend, or Wayland server.
No recursive dispatch, source-priority change, direct `current.input` write,
forged `present` or output geometry change is allowed. At most five attempts
per experimental configuration; if none interleave, stop with
**INCONCLUSIVE / NOT EXERCISED**. The grabbed-popup camera variant is allowed
only after a natural E2 interleaving creates a Mosaic clipping question.

## Analysis and stop rule

Emit raw and structured `event-order.jsonl`, `client-requests.json`,
`surface-commits.json`, `output-builds.json`, `output-commits.json`,
`presentations.json`, `input-regions.json`, `scene-hits.json`,
`client-delivery.json`, `timelines.json`, `matrix.json` and `summary.json`
outside Git. Each timeline must state submitted request, observed server
application, last accepted commit, last observed and next present, actual
hit/input/client receipt, and which relations remain inferred or unknown.
Compare one minimal-trace run with a run disabling only the additional
surface log site: commit/present counts, duration, gap distribution, applied
surface mutations and button receipts. Functional agreement alone does not
prove timing neutrality. SHA-256 manifests cover all raw evidence used.

If five attempts produce no natural interleaving, close this temporal line
as **INCONCLUSIVE** for this backend and matrix. Existing ordering may be
sufficient for sampled states, but a global architectural sufficiency claim
would require more evidence. An added Mosaic transaction contract requires
a concrete required clipping/hit invariant and a real counterexample, not
merely a later input state than an already committed output buffer.

## Executed campaign and result

The source fixture rebuilt pinned private SceneFX, Mosaic and wlroots in
`/tmp/swayfx-mosaic-nested-grab-6C8kpcQB/`. The first sequential run failed
because the generated runner lacked its `sequential` constant. A later
asynchronous control run failed because an untargeted `border pixel 3` IPC
command ran after a click on an empty input region had changed focus. Both
failed runs are retained under `failed-runs/`; neither supplies temporal
evidence. The corrected fixture then ran two sequential region cycles per
mode, followed by five asynchronous cycles per mode. The standard control
remained uninstrumented. The separate trace-off comparison used two
sequential cycles per private mode.

After the five-attempt timing bound, a separate provenance check cloned
published `c1f0e3621ddfba29fde9660d044d595c00ee8610` into
`/tmp/step20c-ordering-clone-final2/`, overlaid only this uncommitted
fixture, and rebuilt both the historical and pending-input private sources
without rerunning timing attempts. Recursive source comparisons found no
differences between either clone-built private Mosaic/SceneFX tree and its
corresponding measured lab. The copied T4 client source SHA-256 matched
`2f06888fbb77d541545aa54280567b8571ef5001e6880686bc9667b4091eddeb`.
The clone-built private Meson model test passed. This establishes source
equivalence of the measured builds to reconstruction from a Git clone; it
does not make the runs byte-identical or add temporal observations.

For the evidence freeze, another fresh clone at
`c1f0e3621ddfba29fde9660d044d595c00ee8610` independently rebuilt the
same pinned chain in `/tmp/swayfx-mosaic-nested-grab-9wm8BpSJ/`. One private
Mosaic sequential cycle yielded 45 accepted output commits, 43 observed
presents and two applied target input mutations; one asynchronous cycle
yielded 48/46 and two mutations. Both runs had two positive client flushes,
two actual top-level right-button receipts, eight captures, `failure=null`
and zero commit-to-mutation-to-present intervals. The asynchronous runner
recorded two distinct client submissions before their confirmations. This
small replay verifies fixture behavior, not a new scheduling conclusion.
Its outside-Git manifest covers all 56 regular raw run files, passed every
entry check and has SHA-256
`f8b54f2ef7f9caca3837e956341ddb5a62f261d0115840d6fd8b0b3540c1e8b9`.

Every successful mode had two correctly placed 800×600 outputs, the mapped
420×320 toplevel, eight captures, six received right-button presses (initial
full region plus five restorations), five empty and five full commands in
the asynchronous campaign, and zero popup grabs. The sampled left-output
pixel `(342,175)` was `(35,68,204)` at E0, E2 empty and E5 restored in all
three modes. The control verifies pixels and client receipt; it has no
native server commit/present trace.

| Asynchronous mode | Accepted native commits | Observed presents | Applied target input mutations | Client flushes | Natural commit→mutation→present |
| --- | ---: | ---: | ---: | ---: | ---: |
| Standard SwayFX `splith` | Uninstrumented | Uninstrumented | Uninstrumented | 10 | Unobservable |
| Private `splith` | 82 | 80 | 10 | 10 | 0 |
| Private `mosaic` | 83 | 81 | 10 | 10 | 0 |

All client flush calls reported positive byte counts (40 or 64), and the
server applied the 10 corresponding input-only mutations in each private
mode. Client and server both used `CLOCK_MONOTONIC`; paired flush-to-handler
gaps were 30,176–113,331 ns in private `splith` and 15,058–111,367 ns in
private Mosaic. In E2, the runner submitted the IPC request then the client
request before waiting for either completion. In E3 it submitted the client
request before the IPC rendering request. The server traces nevertheless
place every applied target mutation outside a matching accepted
commit-to-present interval. A submitted request is still not proof that its
fd was ready in a particular epoll batch. The native counts differ from the
historical 62/60 and 84/82 because this runner also changes border state in
standard layout and overlaps normal camera requests in Mosaic. Both private
modes again have two initial sequence-2 commits with **NO PRESENT OBSERVED**;
their cause remains **UNEXPLAINED**.

E0 passed the sampled geometry, client and pixel controls. E1 passed two
sequential transitions per mode. E2 submitted five bounded overlapping
cycles per mode and found zero natural interleavings. E3 proved the client
submission and subsequent normal server application, without proving fd
readiness before repaint. E4 was **NOT TESTED**, because no E2 interval
existed in which to attempt a hit. E5 restored full input on the same
surface; actual button receipt resumed. Private scene hits after effective
empty input did not target the toplevel. Some transient full-state private
standard hits were nil during ordinary border changes, but later full-state
hits and the client deliveries succeeded; no distinct Mosaic clipping
failure was demonstrated. There was no popup/grab variant.

Trace-on two-cycle sequential controls measured private `splith` 47/45
commit/present, 4 applied target mutations, 3 buttons, 4.808 s and a
76,762 ns median commit→present gap; trace-off measured 48/46,
4 client flushes, 3 buttons, 4.799 s and 96,800.5 ns. Private Mosaic gave
59/57, 4 mutations, 3 buttons, 4.826 s and 86,591 ns trace-on; trace-off
gave 60/58, 4 client flushes, 3 buttons, 4.837 s and 86,020 ns. Applied
mutation counts cannot be observed directly with the new log site disabled;
the client and hit behavior still pass. Native counts and gap distributions
vary, so perfect timing neutrality is not claimed.

The lab contains `event-order.jsonl`, `client-requests.json`,
`surface-commits.json`, `output-builds.json`, `output-commits.json`,
`presentations.json`, `input-regions.json`, `scene-hits.json`,
`client-delivery.json`, `timelines.json`, `matrix.json` and `summary.json`.
`timelines.json` records each submitted client flush, applied server handler,
surrounding native events and executed later hit; per-hit client delivery is
left unknown where the client log has order but no same-clock event stamp.
The outside-Git `raw-evidence-sha256.txt` covers all 280 regular files in
`runs/`, `sequential-runs/`, `trace-off-runs/`, `failed-runs/` and structured
results, excluding the two source/derived manifest files and itself. All
entries passed SHA-256 verification. The manifest hash is
`6eaeee3fcd77c4f2b7682924d2ff8ebdd5b306acab715bead68ce9e655f5490a`.
Builds, binaries, generated protocol source and sockets are outside this
raw-evidence scope and outside Git.

**Verdict: INCONCLUSIVE / NOT EXERCISED** for the sought temporal order.
The request/confirmation decoupling worked, and applied mutations and later
hit/client behavior are real, but the discriminating interval was still not
exercised. No concrete Mosaic clipping invariant was violated and no added
transaction contract is established. **Architecture: UNDECIDED.** Stop this
temporal line for the headless backend and fixed matrix; STEP20C can next
examine effects/damage, scaling, or resize/migration as separate gates.
