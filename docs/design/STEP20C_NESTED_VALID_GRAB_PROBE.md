# STEP20C nested valid-grab probe

**Status: EXPERIMENTAL / FEASIBLE for the sampled nested-grab matrix.** This document records a bounded headless
feasibility experiment, not a production STEP20C implementation or UX decision.
The [architecture](../ARCHITECTURE.md), [UX](../UX.md), [limitations](../KNOWN_LIMITATIONS.md)
and [roadmap](../ROADMAP.md) retain authority.

## Hypothesis and protocol contract (before fixture implementation)

A real `xdg_toplevel → xdg_popup A → xdg_popup B` chain can keep both
popups mapped under two valid explicit grabs. The disposable SceneFX/Mosaic
clip should constrain **both** popup levels to the applied viewport, including
when their tiled owner is fully hidden by camera translation. The unmodified
SwayFX control establishes ordinary grab dismissal and pointer routing.

The installed `xdg-shell.xml` declares version 7; the prior fixture binds
`xdg_wm_base` at version 3. Its `xdg_popup.grab` text requires a user action
serial, a grabbing parent for nested grabbing popups, a mapped parent, grab
before mapping, and reverse destruction order. It permits a compositor to
dismiss the whole nested stack, topmost first. The initial buffer for each
popup follows `xdg_popup.configure`, `xdg_surface.configure`, and
`xdg_surface.ack_configure`. A denied grab immediately dismisses the popup.
The client must log the originating `wl_pointer.button` target, serial and
the matching `xdg_popup.grab` request for A and B separately. Nonzero serial
alone is insufficient proof.

## Fixture architecture and geometry

The toplevel has its own `wl_surface`, `xdg_surface` and `xdg_toplevel`.
Popup A has its own `wl_surface`, `xdg_surface` and `xdg_popup` with the
toplevel `xdg_surface` as parent. Popup B has distinct objects and uses A's
`xdg_surface` as its actual XDG parent. Toplevel, A and B use distinct solid
colors and explicit `TOPLEVEL`, `POPUP_A`, `POPUP_B` log labels. Surface object
identity and configure traces, rather than color alone, establish hierarchy.

A left button press on the mapped toplevel opens A with exactly that event's
serial. After A is configured, acknowledged and mapped, a **new** left press
on A opens B with that second event's serial. Each popup uses an independent
positioner anchored inside its parent window geometry. Positioner offsets
will provide a fully visible placement and one or two viewport-crossing
placements. The runner records actual configure geometry, owner IPC rectangle,
Mosaic `scroll_x`, scene clip log, output positions and injection coordinates;
it must not infer rendered position from logical IPC `rect.x` alone.

Normal lifecycle: B role → B `xdg_surface` → B `wl_surface`, then A role → A
`xdg_surface` → A `wl_surface`, then toplevel role/surface. On compositor
`popup_done`, log event order separately from client destruction order and
destroy topmost first. Explicit B closure must leave A mapped and interactive.
Owner destruction is tested separately from normal popup closure; compositor
`xdg_toplevel.close` and process teardown are distinct observations.

The probe uses two private 800×600 headless outputs at `(0,0)` and `(800,0)`.
Configuration A is unmodified `/usr/bin/sway` in `splith`; B is private
SceneFX/Mosaic in `splith`; C is the private guarded binary in `mosaic`.
Every run has private `XDG_RUNTIME_DIR`, Wayland/IPC sockets, persistent
virtual pointer, compositor log, `WAYLAND_DEBUG=1` client log, pointer log,
IPC JSON and screenshots of both outputs. Private SceneFX is loaded only by
the private compositor. No command addresses the desktop session.

## Scenario acceptance matrix

`PASS` requires matching protocol, pixels and pointer traces at named sample
points. A popup closing before a hidden-owner sample makes that sample
`INCONCLUSIVE`; a client merely surviving is never proof. `FAIL` records an
observed violated expectation. `PARTIAL` means only part of the stated
evidence exists. Unexecuted cells remain `NOT TESTED`.

| Scenario | A control | B private splith | C private mosaic | Required evidence |
| --- | --- | --- | --- | --- |
| 1. Both popups visible and interactive, two valid grabs | PASS | PASS | PASS | Distinct button serials; ordered XDG configure/ack/map; A/B pixels and B right-button events |
| 2. B crosses viewport | PASS | PASS | PASS | B pixels on each output in standard layouts; Mosaic B pixels left only, no B hit right; normal right-output target receives click |
| 3. A and B cross viewport | PASS | PASS | PASS | Both colors right in standard layouts, neither right in Mosaic; distinct A and B button targets left |
| 4. Explicit B close, A remains | PASS | PASS | PASS | B disappears; A receives right press/release; no B re-creation or ghost at sampled point |
| 5. Outside click | PASS | PASS | PASS | `popup_done` B then A; client destroys B then A; normal right-output client gets left press/release |
| 6. Tiled owner fully hidden, then camera return | N/A | N/A | PASS | Same owner and popup IDs, both mapped; no A/B pixels or hits while hidden; both return without recreation |
| 6b. Hidden owner with separate click | N/A | N/A | PASS | No hidden popup button; grab dismisses B then A; no return after dismissal |
| 7. Toplevel destruction with A/B open | PASS | PASS | PASS | `xdg_toplevel.close`, then client destroys B, A and toplevel; no `popup_done` required on this path |
| 8. Mosaic → splith with A/B open | N/A | N/A | PASS | Same B responds at global `(900,190)` after layout change; no prior `popup_done` |

The previously retained source fixtures and three patches must remain
byte-identical. A new private correction, if needed, is a separately named
delta with an explicit reason. Builds, sockets, generated protocol sources,
captures and logs remain outside Git. Output resize/migration, vertical,
negative-origin, scaled/rotated outputs, transaction generations, complete
damage/effects and package ABI are outside this experiment.

## Reproduction and retained artifacts

The lab is `/tmp/swayfx-mosaic-nested-grab-If8ofeUu/` (about 54 MB after all
runs). Its `artifacts-sha256.txt` lists 658 measured log, IPC and capture
files; the manifest SHA-256 is
`869f97f2ed8a7babc9db2bae49531a1c45e3aef84e6e799af87f2d8fcedb8a70`.
It was reconstructed from Mosaic
`cd550382b311efdbfe3ed892f4e1d281d852e754` and SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc`, applying the unchanged
private SceneFX patch, Mosaic patch, then hidden-owner guard in that order.
All three patch SHA-256 values match the [previous fixture](../../tooling/probes/step20c-valid-grab/README.md).
`prepare.sh` rebuilt both private libraries/compositor and generated XDG and
virtual-pointer code; `nested-client.c` and the reused `pointer-daemon.c` were
compiled with `-std=c17`. `/usr/bin/sway` provided the unmodified control.
The [new fixture README](../../tooling/probes/step20c-nested-grab/README.md)
gives clean-checkout commands. Each `run-*` directory holds client protocol,
pointer, `wev`, compositor, IPC and two-output screenshot evidence. The runner
uses short separate `/tmp/mng-*` socket directories recorded in `runtime-path`.

The client fixture SHA-256 at the measured build is
`2e40c98af72a0df8b316810589a0be8f4425a763db1de448b49a7813956b6f7d`.
The runner was corrected during the probe: its first, long runtime socket
path caused one private `splith` startup to exit before any client appeared,
with `Socket path won't fit into ipc_sockaddr->sun_path` at
`sway/ipc-server.c:142` in the compositor log. `ipc_user_sockaddr()` checks
the `snprintf` result against `sun_path`; the retained aborted directory has
only `config`, `compositor.log` and an empty `wayland-1.lock`. A `SIGSEGV`
process result was reported during the probe, but no exit-status record,
core dump or stack trace is retained to corroborate the signal or locate its
origin. Source inspection identifies a plausible error-path defect:
`sway_abort` invokes the registered `sway_terminate(EXIT_FAILURE)` callback;
with a Wayland display already present, `sway_terminate` calls
`ipc_event_shutdown`, whose listener check dereferences `ipc_client_list`.
The length check runs before `ipc_init` creates that list. This ordering could
explain a null dereference, but no retained backtrace proves that this was the
observed process exit. The overlong path is a confirmed fixture setup error;
the reported `SIGSEGV` and its precise origin remain a separate **unverified
startup incident**. A future isolated diagnostic run could preserve the exit
status and a backtrace; this probe did not do so.
Short `/tmp/mng-*` paths avoided the length failure in subsequent control,
private standard and Mosaic runs. This is a fixture workaround, not a proven
compositor bug fix. The first `close_b` runs used a left click that legitimately
reopened B; they are retained with `-initial` suffix. The revised right click
measures A's continued interaction without reopening B. No private source
patch was changed to obtain these results.

## Independent post-audit replay

A fresh disposable laboratory was rebuilt from the pinned commits and the
same three private patches. The reconstructed SceneFX and Mosaic builds,
generated protocol code and both C17 clients succeeded; the Mosaic Meson
model test passed. Twelve representative isolated runs plus one final `open`
smoke run returned successfully. Direct log,
pointer and screenshot checks confirmed both genuine grabs in all three
`visible_click` configurations. With `b_cross`, unmodified SwayFX and private
`splith` each showed **15,860** B-green pixels on HEADLESS-2; private Mosaic
showed **0** there and **17,940** on HEADLESS-1. Mosaic's `(900,190)` click
went to `wev`, not B, while standard controls delivered it to B. With
`both_cross`, Mosaic showed **0** A-yellow and B-green pixels on HEADLESS-2
and delivered separate left-output right clicks to A and B. In `hidden`, both
colors fell to **0** and returned to their prior counts with one A/B map each;
`hidden_click` dismissed B then A without a hidden popup button. `close_b`
left A receiving right press/release, `outside` logged B then A `popup_done`
and child-first destruction, and `toggle` restored B-green pixels and B's
button delivery on HEADLESS-2 in `splith`. These are fresh confirmations of
named samples, not a broader qualification. The original 658-artifact
manifest was also rechecked with **658 OK, 0 failures**. Its historical
measurements remain described here even if the temporary laboratory is later
removed. The post-audit runner changes affect socket isolation and cleanup,
not popup actions or the private compositor patches.

## Protocol and hierarchy evidence

In `run-control-open-visible/client.log`, A used button serial **61** from
TOPLEVEL and B used **66** from POPUP_A. Both respective `GRAB_REQUEST`
entries show `used=61` and `used=66`. `POPUP_A CREATE` records
`parent_xdg=9` (TOPLEVEL); `POPUP_B CREATE` records `parent_xdg=12`, exactly
A's XDG object. The two role configure events were `(50,80,250,170)` and
`(20,60,170,130)`; their `xdg_surface.configure` serials 62 and 67 were
acknowledged before each MAP. Private standard repeated 61→66 in the first
visible run; private Mosaic used distinct real serials **55** and **60**.
`WAYLAND_DEBUG=1` logs corroborate client request order. No protocol error,
immediate grab denial or pre-configure dismissal was observed in the successful
runs. A later right click on B was delivered in all three configurations
(control/private standard button serial 71; Mosaic 65, with releases).

These are real nested XDG grabs, not merely two transient surfaces: B's parent
is A's `xdg_surface`, A was mapped before B was created, both were mapped
at the `open` capture, and each received pointer interaction. Source colors
are blue TOPLEVEL `(35,68,204)`, yellow A `(224,192,32)` and green B
`(32,208,160)` in the captured RGB images. Surface IDs and event targets are
the primary identity evidence.

## Visual and pointer observations

All screenshots are 800×600 for HEADLESS-1 and HEADLESS-2. For `b_cross`,
the compositor configured A at `(200,80,300,170)` relative to TOPLEVEL and B
at `(220,60,300,130)` relative to A. At `open`, both standard configurations
had **15,860** exact B-green pixels on HEADLESS-2; Mosaic had **0** while
retaining **17,940** B-green pixels on HEADLESS-1. At global `(700,190)`, B
received right press/release in all three cases. In the control, moving to
global `(900,190)` yielded B-local `(278,25)` and a further right press/release.
The private standard case matched it. In Mosaic, B received a leave, no
right-output B enter/button, and the ordinary `wev` on HEADLESS-2 received
the right press/release. The Mosaic grab then dismissed B and A. Thus a
legitimate grab's dismissal is separated from a hit on an invisible B.

For `both_cross`, A was configured `(350,80,350,170)` and B
`(160,60,300,130)`. At `open`, both standard configurations had **6,120**
A-yellow and **27,560** B-green pixels on HEADLESS-2. Mosaic had **0** of
both colors there, while retaining **30,080** A-yellow and **6,240** B-green
pixels on HEADLESS-1. A right click at global `(700,190)` targeted A and
one at `(780,190)` targeted B in Mosaic, confirmed by separate surface logs;
the control and private standard also targeted A then B. At `(900,190)`,
only the standard layouts delivered the button to B; Mosaic's ordinary
right-output client received it and B/A were dismissed. These points test
two hierarchy levels rather than treating the whole menu as one colored area.

On explicit `close_b`, the `POPUP_B DESTROY` entry preceded a right click on
A in all three configurations. A received press and release and B did not
reappear. The sampled pixel at B's former overlap changed from green to A's
yellow. On the outside click `(900,400)`, every configuration logged
`POPUP_B POPUP_DONE`, then `POPUP_A POPUP_DONE`, then client destruction B,
then A. `wev` got the left press/release. On compositor IPC `kill` of the
toplevel, the client logged `TOPLEVEL CLOSE_REQUEST`, destroyed B and A, then
destroyed TOPLEVEL; no `popup_done` preceded this normal owner teardown.

## Hidden owner and standard-layout return

The Mosaic owner remained IPC container ID **8**, logical rectangle
`(640,25,640,575)`, with `scroll_x` **400→1280→400**. Private compositor log
`PROBE_POPUP_HIDDEN_OWNER` recorded applied owner `(-640,0,640,600)` against
viewport `(0,0,800,600)`, an empty intersection. During `hidden` and
`hidden-hover`, both A-yellow and B-green exact pixel counts on HEADLESS-1
were **0**, down from **42,200** and **17,940** at `open`. No popup enter,
button, `popup_done`, reconfigure, object re-creation or client exit occurred
before the hidden measurement. After camera return, both counts returned
to **42,200** and **17,940** with the same XDG object IDs. In the separate
`hidden_click` case, right click at `(100,190)` produced no A/B button but
did produce `popup_done` B then A; the returned frame correctly did not
restore them after dismissal. This is sampled guard and grab behavior, not
a universal offscreen-popup policy.

The `toggle` run left Mosaic with B still mapped. HEADLESS-2 local
`(100,190)` changed from ordinary `(102,102,102)` to B-green
`(32,208,160)` in `splith`, and B then received right press/release at global
`(900,190)` without a prior `popup_done`. The private guard did not persist
into the sampled standard-layout path.

## Classification and remaining gates

The specified horizontal, two-output nested-grab experiment is **FEASIBLE**
at its measured placements and event points. This does **not** establish
continuous clipping between sample points or a general popup dismissal policy.
The startup incident above does not affect the later runs, which started their
clients, mapped both popups and produced protocol, pointer and pixel evidence.
No architectural guarantee is established for
universal grab behavior, complete damage/stale-pixel coverage, decorations,
shadows/blur/saved buffers, vertical/negative/scaled/rotated outputs,
output resize/migration, transaction-generation agreement, SceneFX ABI or
package maintenance. Each of those remains **NOT TESTED** in this probe.
The private SceneFX symbols and owner guard remain disposable; no source
or patch enters production. STEP20C remains NEXT and cross-output Mosaic
remains NOT YET SUPPORTED. The smallest next bounded experiment should
exercise a changed output geometry with these same nested grabbed surfaces
and compare the control, private standard and private Mosaic paths before any
production integration decision.
