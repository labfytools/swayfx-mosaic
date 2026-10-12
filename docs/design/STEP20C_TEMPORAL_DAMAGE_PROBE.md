# STEP20C temporal rendering and damage probe

**Status: EXPERIMENTAL / PROTOCOL RECORDED BEFORE FIXTURE.** This probe uses
private headless binaries only. STEP20C remains **NEXT** and multi-output
Mosaic remains **NOT YET SUPPORTED**. No UX, production ABI, package or
transaction contract is changed here.

**Measured verdict: PARTIALLY_FEASIBLE for the sampled temporal matrix.**
The stabilized visual and lifecycle assertions passed in the runs below;
frame-by-frame presentation, full input/render synchronization and native
transaction generation remain unproven.

## Question and prior evidence

The [negative-origin probe](STEP20C_NEGATIVE_ORIGIN_NESTED_GRAB_PROBE.md)
found sampled popup clipping and hit testing feasible at stable positions.
It did not capture every presented frame or prove SceneFX damage sufficiency.
This probe asks whether repeated XDG lifecycle and camera transitions expose
stale pixels, wrong input targets or scene/IPC disagreement. A successful
settled screenshot cannot establish correctness during the transition.

## Fixed geometry and three configurations

HEADLESS-1 is `(-800,0,800,600)`, HEADLESS-2 is `(0,0,800,600)`, scale 1,
transform normal, global bounds `[-800,800) × [0,600)`. PNG coordinates are
output-local: HEADLESS-1 local X is global X plus 800, HEADLESS-2 local X is
global X. The virtual pointer receives `sent_x=global_x+800` with extent
`1600×600`; client enter/button events validate actual targeting.

| Mode | Binary | Layout | Camera |
| --- | --- | --- | --- |
| A | unmodified `/usr/bin/sway` | `splith` | N/A |
| B | private Mosaic with private SceneFX | `splith` | N/A |
| C | same private binary, clip and owner guard | `mosaic` | 400 ↔ 1280 |

Each run uses its own mode-0700 runtime, discovered private Wayland display,
explicit `swaymsg -s` socket, bounded children and two-output captures. The
daily session socket is excluded from the subprocess environment. The
ordinary layout controls compare common XDG creation, input and destruction;
they have no invented camera counterpart.

## Hypotheses and XDG lifecycle

H1: hiding the fully off-viewport tiled owner removes its popup pixels.
H2: camera return restores the same mapped A/B objects without old-position
pixels. H3: after B then A are destroyed, their former regions show the
underlying surfaces. H4: applied scene, clip, IPC and pointer targets agree
at observed transitions. H5: SceneFX invalidates the regions actually changed.
H6: private `splith` does not regress against unmodified SwayFX for common
XDG transitions. H7: repetition produces no crash, protocol error, surface
accumulation or ghost pixels. Each hypothesis receives its own verdict.

TOPLEVEL → POPUP_A → POPUP_B is a real parent chain with distinct `wl_surface`,
`xdg_surface` and `xdg_popup` objects. Opening A uses a fresh TOPLEVEL button
serial; opening B uses a fresh A button serial. Every popup gets role
configure, `xdg_surface` ack, then buffer map. Explicit close destroys B
first; A is destroyed after B. An outside click may deliver `popup_done`
B then A and has a different expected outcome from camera hiding without a
click. Serial values are per run, never constants.

## State and observation boundaries

The logical Mosaic `scroll_x` in IPC is distinct from Sway pending/current
container geometry and from the applied scene position. The owner applied
rectangle, clip log and sampled PNGs must corroborate scene placement. An IPC
success reply proves command acceptance, not presentation. The current
private probe exposes no native transaction generation. `SPIKE_DAMAGE`
records an output-local damage **bounding extent** before scheduling a frame
and adding to the damage ring; it is neither an exact region decomposition nor
proof of a presented frame. Any experimental counter must be labelled local.
The run preserves monotonic action/capture times, IPC trees, pointer/client
events, compositor logs and PNG hashes. `grim` produces sampled screenshots;
it cannot guarantee capture of every presented frame or a fixed achieved
frequency. Damage-to-pixel matching is **PARTIAL** unless records can be
associated with the actual presented frame and capture.

## Predefined scenarios and observations

The initial target is ten complete stable cycles per mode, bounded by a
per-run duration and capture/byte limit. Each cycle gets a unique ID and:

| Phase | Action and expected evidence |
| --- | --- |
| S0 | no popup, verified outputs, static reference, IPC, two PNGs |
| S1 | real TOPLEVEL click, A grab/configure/ack/map, two PNGs |
| S2 | real A click, B grab/configure/ack/map, two PNGs |
| S3 | visible A/B, configured/applied positions, interaction without dismissal |
| S4 | C only: `scroll_x` 400 → 1280, fully hidden owner, A/B still mapped, no popup hit |
| S5 | C only: 1280 → 400, same XDG objects, visible pixels restored |
| S6 | explicit B close, A retained, formerly covered region restored |
| S7 | explicit A close or controlled outside dismissal, underlying rendering restored |
| S8 | no old popup objects, owner/client alive, prepare fresh serials |

Separate runs cover controlled outside-click dismissal and Mosaic → `splith`
with open popups. After stable cycles pass, target 15–20 camera back-and-forth
transitions with A/B open, first with observed stabilization and then with
rapid IPC requests. Record both request and observed states; coalescing is
not automatically a failure. A reproducible crash stops the loop for minimal
reproduction. Failed and inconclusive cases remain in the evidence.

## Image and damage analysis protocol

Use the nested client's solid SHM A-yellow `(224,192,32)` and B-green
`(32,208,160)` surfaces as known foreground. Establish stable reference
images of the background and formerly covered A/B rectangles before scoring.
Avoid dynamic `wev` text regions when comparing full pixels; any mask must be
defined before looking at anomalies. Cursor, decorations, text, effects,
capture compression and IPC/capture timing can create unrelated differences.
Record each PNG's dimensions, monotonic capture timestamp, SHA-256, phase,
output-local region of interest, exact popup-color count, whole-region diff
count, diff bounding box and anomalous local coordinates. Compare formerly
covered regions with the appropriate uncovered reference, not just the
decrease of an exact color. Keep signed global conversion separate.

For each transition, compare observed changed regions with time-ordered
`SPIKE_DAMAGE` extents for that output, then with the rendered result. A broad
damage extent alone is not a correctness failure; missing or late invalidation
requires synchronized evidence. When frame association is absent, mark H5
**PARTIAL** even if stabilized images are correct.

## Verdict rules and limits

Each assertion is `PASS` only with the required geometry, XDG serial and
lifecycle traces, mapped identities, client events, PNG pixels and process
status. `FAIL` requires a demonstrated invariant violation. `PARTIAL` means
some required observation exists but coverage or synchronization is limited.
`INCONCLUSIVE` means the fixture cannot identify the behavior; `NOT TESTED`
means it was not run. A zero process exit alone is never `PASS`.

The aggregate is **FEASIBLE for the sampled temporal matrix** only when all
executed required visual/input transitions pass, controls have no blocking
regression, and damage traces support only the precise claims made. Positive
stabilized images with incomplete frame/damage association are
**PARTIALLY_FEASIBLE**. A reproducible leak, protocol violation, destruction
defect or crash is **BLOCKED**. Unusable fixture or captures are
**INCONCLUSIVE**. Untested cells stay **NOT TESTED**. Scaling, rotation,
resize, migration, complete effects and ABI/package maintenance are outside
this experiment. No result authorizes production STEP20C or daily use.

## Measured campaign and retained evidence

The final instrumented lab is `/tmp/swayfx-mosaic-nested-grab-RbwDblky/`
with build log `/tmp/mtd-prepare-Rv5kR9sm`. It contains ten runs: ten
complete cycles each in unmodified SwayFX `splith`, private `splith`, and
private Mosaic; one extra private Mosaic pilot cycle; one camera run; outside
click runs in all three configurations; a distinct hidden-owner click; and a
private Mosaic → `splith` return. The planned 30 cycles all completed.
There are **994 sampled PNGs**
on two outputs. None is labelled a complete presented-frame sequence.
The popup owner and A/B are solid SHM surfaces; supporting Kitty windows ran
with cursor blinking disabled. The predefined HEADLESS-1 ROI
`(400,90,800,310)` was empirically stable across S0 and post-close captures
in the completed cycles. `wev` on HEADLESS-2 can redraw its text, so its
whole image was not treated as a static underlay; right-output popup colors
and events were checked separately. The ROI and this exclusion were fixed
before scoring the campaign.

| Observation | Unmodified `splith` | Private `splith` | Private Mosaic |
| --- | --- | --- | --- |
| Ten A/B open → close B → click A → close A cycles | PASS sampled | PASS sampled | PASS sampled |
| A right-button delivery after B destruction | 10/10 | 10/10 | 10/10 |
| Former A/B left-output ROI restored | 10/10 exact equalities | 10/10 | 10/10 |
| B crossing color at right, cycles 1 and 10 | 15,860 green | 15,860 green | 0 green |
| Fully hidden A/B colors and camera return | N/A | N/A | 10/10 sampled: 0/0 hidden, A/B restored with equal ROI |
| Outside-click `popup_done` and child-first destruction | PASS | PASS | PASS |
| Hidden-owner click: no popup button, B/A dismissal | N/A | N/A | PASS sampled |
| Stable `splith` return with B open | N/A | N/A | 15,860 B pixels and actual B button |
| Damage/frame presentation proof | NOT TESTED | PARTIAL | PARTIAL |

The camera run requested 18 outward/return pairs in each of three pacing
modes: stabilization after every change, capture between accepted commands,
and a four-command burst without intervening captures. The owner stayed IPC
ID 8, A/B were created once each, no `popup_done` occurred before explicit
closure, and the sampled hidden/visible colors followed the observed target
values. All 109 `camera_observed` records, including initial positioning,
reported targets 400 or 1280. No sampled right-output A/B color appeared.
The runner's IPC checks do not prove which intermediate target values were
actually presented. The burst may coalesce them. Input/render consistency
during an unobserved frame is therefore **PARTIAL**, even though the sampled
pointer and pixel outcomes show no reproducible divergence.

The separate hidden-click run sent a right button to a point on HEADLESS-1
after `scroll_x=1280`. The count of popup button presses did not increase;
`popup_done` arrived B then A, and neither popup reappeared after return to
400. This is one controlled hidden point, not a universal input claim.

The private SceneFX `TEMPORAL_DAMAGE` log recorded **4,361** output-local
damage extents across the eight private runs, and the actual SwayFX repaint
path logged **1,432** accepted output commits (zero rejected). The analyzer
compared each pair of sampled captures per output against extents whose
monotonic timestamps fell in that capture interval. It found **zero changed
pixels outside their union** and zero changed intervals without an overlapping
extent. This is interval evidence only: broad bounding extents may hide
over-invalidation, and no screenshot is tied to a unique presented frame.
H5 is **PARTIAL**. The unmodified control has no private damage trace and is
**NOT TESTED** for H5.

An independent audit of the retained PNGs compared all three RGB channels,
rather than relying on the analyzer's grayscale difference. Across 784
private same-output capture intervals, 237 contained changed pixels
(57,451,528 changed pixel positions in total); zero changed positions fell
outside the union of their time-bounded logged damage extents. This confirms
the narrowly stated interval observation despite the grayscale conversion
used by the fixture analyzer. It does not establish minimal damage, exact
pixman regions, a damage-to-commit mapping or intermediate frame correctness.

`results/artifacts-sha256.txt` lists **2,133** raw and derived files, with
manifest SHA-256
`362ba5dc399383ecd7c071b56c144b8bdf9f4dc17fad53b60238a14c750bdf7c`.
The final 12-input source manifest is `temporal-source-sha256.txt`, SHA-256
`ef5596c587372388efedd9319ee0062cf1143e2a7c203ed4c579fc6346753702`.
The preceding instrumented lab
`/tmp/swayfx-mosaic-nested-grab-1u4Q8mE9/` retains its original
`temporal-source-sha256-initial.txt`: after those runs, its analyzer gained
a pixel-wise union check and final matrix. The final lab was rebuilt after
the A-input and hidden-click refinement and carries a single matching source
manifest. `sha256sum -c` passed for all 2,133
listed artifacts and all 12 final source inputs.

A fresh private lab at `/tmp/swayfx-mosaic-nested-grab-u5ZlcX0A/` rebuilt
the pinned source and patches and passed its 12-input source manifest. A
targeted replay completed one A/B open → explicit B/A close cycle in each of
the three configurations, plus private Mosaic hide/click/return, one
two-move camera run and a separate outside-click dismissal. All six runs had
no runner failure, valid XDG button serials and no failing targeted
assertions. Their 124 sampled PNGs, 1,457 private timed damage extents and
289 accepted private output commits reproduce the sampled outcome; they do
not add frame identity. This fresh lab is retained outside Git.

The independent uninstrumented lab
`/tmp/swayfx-mosaic-nested-grab-36Cbn4JP/` had the same ten-cycle sampled
outcomes in each configuration. The first instrumented lab
`/tmp/swayfx-mosaic-nested-grab-M5uSSO6U/` and the later
`/tmp/swayfx-mosaic-nested-grab-1u4Q8mE9/` also repeated them. No
probe-induced visual difference was observed in these sampled runs; timing
perturbation outside them remains possible. No compositor crash, Wayland
protocol error, failed grab, stale popup object or residual popup-colored
pixel was detected in the completed final matrix. The initial toggle
sampling failure and its correction are recorded in the history below.

This result does not settle popup UX while an owner is hidden, full
transaction-generation consistency, all presented frames, effects/decorations,
saved buffers, scaling/rotation, output migration/resize or SceneFX ABI/package
maintenance. The next bounded STEP20C experiment should instrument an actual
headless output presentation event together with applied camera/clip state
and pointer target for one repeated hide/return transition. It should test
the unobserved interval directly; it does not authorize a production fix.

## Protocol history

- 2026-10-11: protocol written before the temporal fixture; targets and
  verdict rules above are prospective. Subsequent changes and measured
  results must be recorded here with their date and run paths.
- 2026-10-11: first private campaign in
  `/tmp/swayfx-mosaic-nested-grab-36Cbn4JP/` completed ten cycles in each
  configuration, plus 18 camera transitions per mode, outside clicks and a
  layout-return pilot. The original runner/analyzer sources are retained in
  that lab's `source-snapshot-v1/`. Its immediate `layout splith` capture
  contained no right-output B pixels; the protocol now adds a stabilized
  capture and B click before classification. The camera runner also adds a
  separate command burst without captures between every accepted scroll.
  These changes affect measurement timing, not the private clip algorithm.
- 2026-10-11: `SPIKE_DAMAGE` lacks monotonic timestamps and an output commit
  marker. A separate private SceneFX logging patch is therefore planned for
  the next lab. It may log `CLOCK_MONOTONIC` nanoseconds, the damage extent,
  and a **local experimental** output-commit ordinal/result. It will not
  expose a native transaction generation, alter public headers or prove
  presentation by itself. Compare the instrumented result with the
  uninstrumented campaign for probe-induced changes.
- 2026-10-11: the first instrumented lab
  `/tmp/swayfx-mosaic-nested-grab-M5uSSO6U/` retained 10 cycles per mode,
  18 camera round trips in each of three pacing modes, outside clicks and a
  successful stable layout-return check. It logged damage but zero SceneFX
  commit-hook calls. Source audit found the actual call in private SwayFX
  `sway/desktop/output.c`; a separate logging-only Mosaic patch is now added
  to the next private lab. The initial toggle runner failure in
  `/tmp/swayfx-mosaic-nested-grab-pX0BTADM/` was a left-side fixture sample
  after stable right-side pixels had already been captured; it was not a
  compositor or XDG failure. Its logs and exit code are retained.
- 2026-10-11: the private SwayFX commit-hook patch logged the repaint path
  actually used. Pixel-wise unions and `matrix.json` were added to the
  analyzer after the first complete instrumented campaign; its original
  analyzer hash was retained in `temporal-source-sha256-initial.txt` under
  that lab. Its own source and artifact manifests remain available.
- 2026-10-11: a final protocol refinement adds an explicit A right-button
  interaction after B's destruction in each cycle, and a separate hidden-owner
  outside-click run. Earlier cycles demonstrated A mapping and B creation via
  an A click, but did not directly recheck A input after B closed. The new
  run must not erase or relabel earlier evidence; its own manifest and run IDs
  will distinguish this stronger input check from the previous matrix.
- 2026-10-11: the refined campaign in
  `/tmp/swayfx-mosaic-nested-grab-RbwDblky/` completed the 30-cycle matrix,
  camera modes and both outside-click contexts. Ten post-B A interactions per
  configuration and the separate hidden-click non-hit assertion passed. Its
  final source and artifact manifests validate the finished analysis. The
  verdict remains **PARTIALLY_FEASIBLE** because frames and native transaction
  generations remain unobserved.
