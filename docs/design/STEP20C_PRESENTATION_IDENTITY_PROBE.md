# STEP20C presentation identity probe

**Status: EXPERIMENTAL / PARTIALLY_FEASIBLE.** STEP20C
remains **NEXT**; production multi-output Mosaic remains **NOT YET SUPPORTED**.
No production compositor, public ABI, package, patch or UX contract changes.

## Question and fixed scope

Can a private headless trace correlate an accepted output commit with its
backend `present` event, the applied Mosaic camera/clip state observed while
building that output state, and later pointer delivery? Repeat only
`scroll_x 400 → 1280 → 400` with the same mapped, genuinely grabbed nested
XDG popups A/B. HEADLESS-1 is `(-800,0,800,600)` and HEADLESS-2 is
`(0,0,800,600)`, scale 1, normal transform. Controls are unmodified SwayFX
`splith`, private SwayFX `splith`, and private Mosaic `mosaic`. Standard
controls have no synthetic camera action.

## Audited signal path

The installed `wlroots-0.20` package reports 0.20.2. Its installed
`wlr_output.h` exposes a per-output `uint32_t commit_seq`, `events.commit`,
`events.present`, and a present event with `uint32_t commit_seq`, `bool
presented`, `timespec when`, `unsigned seq`, `int refresh` in nanoseconds and
`uint32_t flags`. The sequence may wrap. The pinned upstream wlroots 0.20.2
source is tag commit `d783533489e1f75d6886c2ab5c5960090ef268f8`.
`wlr_output_commit_state` increments the native sequence only after a
successful backend commit, then emits `events.commit`. Its commit event has
a monotonic `when` and a borrowed state pointer valid during the callback.

The 0.20.2 headless backend creates a `presented=true` event with
`commit_seq = wlr_output->commit_seq + 1` for a commit leaving the output
enabled, then defers it to an event-loop idle callback. The core fills a
zero `when` with `CLOCK_MONOTONIC` at delivery. Headless initializes neither
hardware refresh sequence nor hardware presentation flags, and it has no
physical display. Allocation failure can suppress a deferred event. An
accepted commit, an idle `present`, a rendered buffer, a `grim` screenshot
and photons are distinct observations. The header alone cannot establish
buffer content or physical timing. Source references:
[`headless/output.c`](https://gitlab.freedesktop.org/wlroots/wlroots/-/blob/0.20.2/backend/headless/output.c),
[`types/output/output.c`](https://gitlab.freedesktop.org/wlroots/wlroots/-/blob/0.20.2/types/output/output.c).

SwayFX `sway/desktop/output.c` calls `output_configure_scene`, tests
`wlr_scene_output_needs_frame`, builds the output state, and calls
`wlr_output_commit_state` in `output_repaint_timer_handler`. Its existing
`present` listener updates refresh prediction but ignores unpresented
events. The private SceneFX subtree clip and owner visibility guard govern
render and hit testing; prior `TEMPORAL_DAMAGE` lines are output-local
bounding extents, not pixman region decompositions. Sway's logical
`scroll_x`, current container geometry and applied scene nodes are separate.

## Instrumentation contract

Apply a distinct, hash-checked patch only in a pinned private compositor
copy. Log native output identity and `commit_seq` from `events.commit` and
`events.present`, the monotonic callback time, present `when`, `presented`,
`seq`, `refresh`, `flags`, and the result of the repaint commit call. A
per-output listener must be removed before its output is destroyed. The
trace must not change commit, clip, damage, hit-test or transaction decisions.
Logging itself may affect timing and requires a control comparison.

At the last safely observable point before output-state build, record the
active workspace, Mosaic logical camera, owner identity and current geometry,
scene node position, and any accessible applied clip/owner visibility. Label
unavailable fields `UNOBSERVED`; never replace them with pending values.
Record a native sequence only when the callback or accepted commit provides
it. A scene snapshot taken before build is an ordered observation, not proof
of the pixels within the committed buffer. Event data and object pointers
must not be retained beyond callback/object lifetime.

Keep `TEMPORAL_DAMAGE`, `SPIKE_DAMAGE`, client XDG logs, real virtual-pointer
requests, IPC snapshots, and `grim` PNGs. The runner records capture start
and finish monotonic times, output, SHA-256, ROI and A/B color counts. Only a
native `(output, commit_seq)` match may pair commit and present; timestamp
order alone cannot do so. An accepted commit lacking present stays
unpresented in the observed trace. Multiple commands can coalesce before a
commit. Pointer enter/button and `popup_done` belong to their own timed
event stream and are never assigned a fictional frame number.

## Bounded matrix

1. Validate listener registration, native sequences, timestamps, output
   separation and removal in one private headless run before repetition.
2. Open A and B with fresh real button serials; capture settled scene, IPC,
   clips, XDG mapping, last commit/present and both output PNGs.
3. From 400, scroll +880; observe full hiding without a click. Scroll -880;
   check same owner and popup identities, applied clips and restored pixels.
4. Repeat the settled pair five times, with per-pair event and capture IDs.
5. Send twelve controlled faster alternating requests; preserve command
   times, coalesced or missing presentations and unobserved intervals.
6. In separate runs test B visible, a clipped portion, fully hidden owner
   and return without prior popup closure. An outside click may dismiss the
   grab; child-first `popup_done` is not an invisible-popup hit.
7. Compare the private standard layout with unmodified SwayFX, then compare
   private builds with and without new presentation listeners at settled
   positions. Preserve all failures, timeouts and protocol errors.

## Verdict and permanent limits

`FEASIBLE` requires real headless present events paired by native sequence
and demonstrated association of necessary applied state without a repeatable
regression. `PARTIALLY_FEASIBLE` covers partial event/state correlation with
unproven buffer identity, input relation or transitions. `BLOCKED` requires
a reproducible leak, invisible hit, lifecycle fault, crash or synchronization
violation. `INCONCLUSIVE` applies when the tested backend/instrumentation
cannot supply the needed signal or measurements cannot decide. Untested
cells remain **NOT TESTED**. Even `FEASIBLE` would not prove every presented
pixel, DRM behavior, production readiness, effects, saved buffers, scaling,
rotation, migration or SceneFX ABI maintenance.

## Measured private headless result

The private laboratory `/tmp/swayfx-mosaic-nested-grab-FQLULvot/` contains
two identity runs (the second adds a B click after camera return), one
complete A/B cycle per configuration, separate Mosaic hidden and outside
clicks, and four fixed negative-origin input controls. An earlier listener
availability pilot remains at `/tmp/swayfx-mosaic-nested-grab-TSp2JWyA/`.
The structured seven-run presentation analysis reports **482 native accepted commits**, **470 headless present
events**, **470 pairs by `(output, commit_seq)`**, **12 commits without an
observed present**, no orphan present and no rejected repaint call. All
present events have `presented=true`, `seq=0`, `refresh=0`, `flags=0`.
Every native commit callback captured a scene snapshot. The unmodified SwayFX
control has no private event listeners and is correctly **NOT TESTED** for
native event correlation. None of the 12 unpaired commits is labelled
presented. Both HEADLESS-1 and HEADLESS-2 emitted paired events; no paired
present callback or monotonic event timestamp preceded its own commit.
The 12 unpaired accepted commits are exactly native sequence 2 on both
outputs in six instrumented runs (Mosaic cycles, hidden click, outside click,
two identity runs, and private standard cycles). Each reports a new buffer and
`workspace=none` during initial output setup. Their cause is not established:
**UNEXPLAINED / NO PRESENT OBSERVED**. They are neither counted as presented
nor declared lost. The unmodified control has no native listener.

In the final identity run, ten settled transitions form five complete
400 → 1280 → 400 pairs. At the target-valued HEADLESS-1 commits, the
applied tiled scene translation is `-scroll_x` and its local clip starts at
`scroll_x` (56/56 target-valued commits, all with a paired headless present).
With A/B mapped, the root popup clip is nonempty at 400 and
empty at 1280. Nested B inherits that root clip; its own mapping identity
comes from client logs, not a separate root scene tree. All ten stable left
captures alternate zero A/B pixels when hidden and 42,200 A-yellow / 17,940
B-green pixels on return; right output has no sampled popup color. The same
owner IPC ID 8 and single A/B map each persist through the identity run.
A fresh B button after the final return was delivered to B before explicit
closure.

Each identity run issued twelve faster alternating commands. Four command
intervals in the pilot and three in the final run contained no HEADLESS-1
commit or present, while later intervals could contain more than one. This
is observable coalescence or deferral, not evidence that a command's target
was displayed. The final run had 125 commits and 123 associated presents;
the pilot had 121 and 119. Of 220 sampled captures across the seven-run
analysis, 200 overlapped one present callback during the capture call and
20 overlapped none. Even a single overlapping event does not identify the
buffer read by `grim`.

During initial Mosaic layout setup, five private Mosaic runs observed one
presented commit with logical `scroll_x=1760` while the applied scene was
translated by `-1120` and its clip began at 1120. This is a reproducible
logical-to-applied lag before the target experiment. The applied scene and
clip agreed with each other; the record does not establish a wrong rendered
pixel or hit target. No mismatch of those applied values was found in the
target 400/1280 commits. It illustrates why logical camera cannot be used
as a substitute for an applied scene snapshot.

Separate fixed-geometry input controls used real XDG button serials. Both
standard configurations delivered B buttons on the crossing portion of
HEADLESS-2 and had 15,860 B-green pixels there. Private Mosaic delivered B
inside the viewport; a click on the clipped crossing portion delivered no
B button and dismissed B then A under the grab. The separate hidden-owner
click likewise delivered no popup button and dismissed in child-first
order. Client event lines lack a common monotonic timestamp, so only runner
request times, callback times, event order and observed delivery are known;
the compositor's internal hit-test result at repaint time is **NOT TESTED**.
No pointer event is assigned to a specific frame. These clicks are not a
universal click-through UX decision.

An instrumentation-impact check compared one no-new-listener temporal cycle
with the new private cycle. Popup color counts at visible, hidden, returned
and closed sampled states, right-output absence, owner IPC ID/geometry/focus,
two valid grabs, popup mapping and absence of `popup_done` all agreed. This
does not exclude timing perturbations between samples. No crash, protocol
error, failed grab or reproducible invisible popup hit appeared in the
tested matrix.

**Verdict: PARTIALLY_FEASIBLE.** Native headless `present` is available and
can be paired with native output commits. Applied scene state can be read
at the commit callback, after output-state construction. Neither callback
proves which pixels occupy that commit's buffer; `grim` captures lack an
exact commit identity. The smallest next experiment is a private, bounded
buffer fingerprint tied to the actual output-state buffer at build/commit
and retained safely until its matching headless present callback, then
compared with a capture from that same buffer. It must establish buffer
lifetime and readback semantics first, without changing the production
renderer or SceneFX ABI.

The retained `presentation-results/presentation-artifacts-sha256.txt` lists
653 raw and derived files and has SHA-256
`d37dd26a95b895a115518c9b40b288822f71bac41dd08a2fda59cd30e0013e03`.
All 653 entries passed `sha256sum -c`. The five-input
`presentation-source-sha256.txt` has SHA-256
`40477a991f294b85c2828a8124e24379fba985695a583435a11de91a9005e92f`
and passed its five source checks. The distinct instrumentation patch has
SHA-256 `dbf1f1d11c9c741b641916d25ac22bcb13c3455ee3002e1f534aa6794cd8a538`.
The lab retains its private build log and Meson test log. Generated binaries,
PNG, sockets and logs remain outside Git.

## Protocol history

- 2026-10-12: API/backend/repaint source audit and protocol recorded before
  a new private patch or experimental run. Measurements follow below.
- 2026-10-12: private event listener and applied-scene trace passed the
  bounded headless matrix above. The result remains PARTIALLY_FEASIBLE.
- 2026-10-12: independently rebuilt the pinned private stack in
  `/tmp/swayfx-mosaic-nested-grab-tMVZBojD/` and ran one 400 → 1280 → 400
  cycle with A/B in private Mosaic, plus unmodified and private `splith`
  controls. The three-run analysis found 127 accepted native commits, 123
  matching headless presents, zero orphan presents, four initial sequence-2
  commits without observed present (two per instrumented run), 70 captures,
  and zero runner or protocol failures. The model Meson test passed. This
  bounded replay confirms event correlation and settled sampled behavior;
  it does not identify committed buffer pixels.
