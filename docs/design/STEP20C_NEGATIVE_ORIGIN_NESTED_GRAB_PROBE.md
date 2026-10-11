# STEP20C negative-origin nested-grab probe

**Status: EXPERIMENTAL / FEASIBLE for the measured negative-origin matrix.** This is a
disposable feasibility test, not a production clipping change or UX decision.
The canonical [architecture](../ARCHITECTURE.md), [UX](../UX.md),
[limitations](../KNOWN_LIMITATIONS.md) and [roadmap](../ROADMAP.md) retain
authority.

## Problem and hypotheses (recorded before fixture adaptation)

An output at global `x=-800` makes global scene and pointer coordinates signed.
The virtual-pointer protocol instead transmits unsigned absolute coordinates
with unsigned extents. Passing a negative global X directly to that protocol
would wrap it. **Hypothesis H1:** with two adjacent 800×600 outputs, wlroots
maps normalized pointer X through the layout bounding box; therefore
`injected_x=global_x-min_x=global_x+800` with extent 1600 reaches the
requested global point. This must be confirmed from the pinned wlroots path
and from client pointer events on both outputs before any clipping result is
valid. A protocol-level injection acknowledgement alone is insufficient.

**Hypothesis H2:** the disposable SceneFX subtree clip, owner-derived popup
clip and hidden-owner guard use signed applied scene positions correctly when
the viewport begins at `-800`. The control layouts must first demonstrate
real pixels and button delivery beyond `x=0`; configured rectangles alone do
not prove a crossing. **Hypothesis H3:** changing Mosaic back to `splith`
removes the private clip while both XDG popups remain mapped.

## Coordinate contract and requested geometry

| Quantity | HEADLESS-1 | HEADLESS-2 |
| --- | --- | --- |
| Requested global origin | `(-800,0)` | `(0,0)` |
| Requested size, scale, transform | `800×600`, `1`, `normal` | `800×600`, `1`, `normal` |
| Global X interval | `[-800,0)` | `[0,800)` |
| Local X | `global_x+800` | `global_x` |

The requested layout bounds are `[-800,800) × [0,600)`, with border `x=0`.
`get_outputs` is authoritative. If the compositor normalizes these origins,
the negative-origin test is **INCONCLUSIVE** and the actual rectangles must
still be retained. Workspace 1 and the tiled popup owner belong to
HEADLESS-1; workspace 2 holds `wev` on HEADLESS-2.

For a requested global point `(-100,190)`, HEADLESS-1 local X is `700` and
candidate virtual-pointer coordinates are `(700,190)` with extent `1600×600`.
For `(100,190)`, HEADLESS-2 local X is `100` and the candidate transmitted X
is `900`. The runner must log requested signed global point, layout minimum,
transmitted normalized point, extents, reached output, client-local motion and
button events. It must reject out-of-bounds and nonintegral injection values.

Mosaic row order and logical owner IPC rectangle remain distinct from camera
and applied scene placement. For each sample, record logical `rect`,
`window_rect`, `scroll_x`, applied owner/popup scene positions, SceneFX clip,
XDG role configure rectangles and actual captures. The candidate applied
content X is `owner.rect.x - scroll_x + owner.window_rect.x` in Mosaic;
the compositor scene log and captured pixels must verify it. Popup A's XDG
configured rectangle is relative to the toplevel surface; B's is relative
to A's surface. Their resulting global rectangles are estimates until scene
position and pixels corroborate them. XDG anchor rectangles must lie within
their effective parent window geometry.

## Experimental method and acceptance

Reuse the historical nested client, the vertical fixture's parameterized
pointer and the same three pinned private SceneFX/Mosaic patches, including
the hidden-owner guard. Adapt only the new fixture directory. Run identical
clients in (A) unmodified SwayFX `splith`, (B) private compositor `splith`,
and (C) private compositor `mosaic`, all with verified negative output origins.
Use isolated runtimes and sockets, `swaymsg -s`, two-output captures, IPC,
`WAYLAND_DEBUG=1`, compositor logs and structured measurements. A separate
positive-origin horizontal subset checks regression. No installed library,
daily session or production source is touched.

1. Validate signed pointer targeting on both outputs, including round trip and
   left/right buttons. Failed targeting invalidates later graphics tests.
2. Open two visible popups: TOPLEVEL button serial grabs A, then A button
   serial grabs B; verify distinct actual serials, parent XDG identities,
   configure/ack/map order and interaction with each surface.
3. Test B crossing `x=0`, then A and B crossing. Both standard controls must
   show actual popup pixels and B/A button targets on HEADLESS-2. Mosaic must
   preserve visible left portions and suppress right popup pixels/hits, with
   ordinary-client events interpreted under normal XDG grab semantics.
4. In separate runs, test outside-click dismissal, fully hidden applied owner
   with no click and with a click, and `layout splith` while popups remain open.
5. Replay a horizontal positive-origin subset with the same adapted clients
   and injector. Derive samples from actual configured/scene geometry and
   capture data, never from assumed historic positions.

Each scenario retains output JSON, signed coordinate conversions, pointer
events, owner IPC/Mosaic state, XDG configuration and identities, scene clips,
two captures per stage, lifecycle events, process exit codes and a
`measurements.json`. Rendering, hit testing, XDG grab, coordinate transform
and lifecycle verdicts are separate. A screenshot alone or a protocol send
alone cannot establish a pass. Keep failures and inconclusive runs visible.

The probe is **FEASIBLE** only if negative origins and control crossing are
real, Mosaic excludes measured clipped pixels/hits while preserving visible
interaction, and private standard layout has no blocking regression. It is
**PARTIALLY_FEASIBLE** for demonstrated core behavior with matrix gaps,
**BLOCKED** for reproducible rendering/input leak, XDG violation or blocking
standard regression, and **INCONCLUSIVE** if geometry, crossing or pointer
events cannot be established. These labels apply only to this probe.

## Initial observations and correction history

The first unmodified SwayFX `pointer` run recorded `get_outputs` with active
HEADLESS-1 `(-800,0,800,600)` and HEADLESS-2 `(0,0,800,600)`, both scale `1`
and transform `normal`. Thus SwayFX did apply the requested negative origin.
The fixture transmitted `302` for global `-498` and `830` for global `30`.
The owner received `wl_pointer.enter` with surface-local X `100`, then `105`
on the return trip; `wev` received enters with local X `28`, then `33`
(its surface starts inside the container). This establishes preliminary
two-output targeting, subject to full button validation. Evidence is retained
in `run-negative-control-pointer-initial/` under the new laboratory.

The first calibration checker falsely required `POINTER_MOTION` lines. An
inter-output move produces `wl_pointer.enter` at the destination instead;
both clients logged those enters. The checker now accepts enter or motion.
That first run exited with a fixture `RuntimeError` after its captures; it is
not classified as a compositor or clipping failure.

The actual wlroots 0.20.2 path confirms H1 at the source level:
[`types/wlr_virtual_pointer_v1.c`](https://gitlab.freedesktop.org/wlroots/wlroots/-/blob/0.20.2/types/wlr_virtual_pointer_v1.c)
forms normalized `x / x_extent`, while
[`types/wlr_cursor.c`](https://gitlab.freedesktop.org/wlroots/wlroots/-/blob/0.20.2/types/wlr_cursor.c)
converts that fraction to `mapping.width * x + mapping.x` using the output
layout box when no device mapping overrides it. Sway's absolute-motion path
uses the wlroots cursor. With box X `-800`, width `1600`, and transmitted X
`global_x+800`, the nominal reconstructed global point is `global_x`.
Client events remain the empirical check for device mapping and targeting.

The completed `pointer` runs in unmodified SwayFX, private `splith`, and
private Mosaic each reached both outputs on two round trips. TOPLEVEL received
right and left press/release (`button=273/272`); `wev` received left and
right press/release. In the control, requested global `(-498,150)` reached
TOPLEVEL local `(100,125)` and requested `(30,80)` reached `wev` local
`(28,55)`; the approximately 2 px X and 25 px Y differences are the client
surface inset, not an output-origin shift. Private `splith` repeated those
coordinates, and private Mosaic used global `(-458,150)` for TOPLEVEL local
`(100,125)` after its camera translation. All protocol X values were
nonnegative and inside the `1600×600` extent.

All three negative-origin `visible` runs mapped A and B and kept them open
through separate right clicks. A's role configure was `(50,80,250,170)` and
B's `(20,60,170,130)` relative to its parent. Popup pixels were confined to
HEADLESS-1 in this reference placement; HEADLESS-2 contained zero exact A
yellow or B green pixels.

The negative-origin `b_cross` controls both configured B at
`(-178,165,300,130)` after applied-owner translation and measured **15,860**
exact B-green pixels on HEADLESS-2 at the open capture. Private Mosaic
configured B at `(-138,165,300,130)` and measured **0** B-green pixels on
HEADLESS-2 while retaining **17,940** on HEADLESS-1. These are preliminary
render measurements; button traces and the remaining matrix are under review.

At the B crossing point, both standard controls delivered two B right-button
events and retained **15,860** B-green pixels beyond `x=0`; private Mosaic
delivered the left visible B button, then delivered the right-output button
to `wev`, with no right-output B button. Its legitimate outside click then
caused `popup_done` B before A. In the `both_cross` placement, both standard
controls had **6,120** A-yellow and **27,560** B-green pixels on HEADLESS-2;
private Mosaic had **0** of each there, while retaining **30,080** A-yellow
and **6,240** B-green pixels on HEADLESS-1. A separate `a_cross` run is used
for A's right-output button, since a first outside click can dismiss the
grabbed hierarchy.

## Comparative results

All three compositors used HEADLESS-1 `(-800,0,800,600)` and HEADLESS-2
`(0,0,800,600)` at scale 1, transform normal. The same nested client used
TOPLEVEL XDG object 9, A object 12 and B object 15 in each run; A named
TOPLEVEL as parent, B named A. In `b_cross`, both standard controls took real
TOPLEVEL left-button serial **69** to grab A and A left-button serial **74**
to grab B. Private Mosaic used **63** and **68**. Each `GRAB_REQUEST` used
the exact target event's serial; configure, `xdg_surface` ack and MAP followed
in order. No protocol error or immediate grab denial occurred. The anchored
rectangles stay within their effective parent geometry: the horizontal
`b_cross` A anchor X `200` is inside the standard top buffer width `420`,
and B anchor X `220` is inside A's width `300`; `both_cross` A anchor X `350`
is likewise inside `420`, B anchor X `160` inside A's width `350`.

| Scenario | Unmodified SwayFX `splith` | Private `splith` | Private Mosaic | Measured distinction |
| --- | --- | --- | --- | --- |
| Pointer reference | PASS | PASS | PASS | Signed global points reached both clients twice; left/right press and release on both outputs. |
| A/B fully visible | PASS | PASS | PASS | Two grabs, mapped distinct surfaces, A/B right clicks, no unexpected dismissal. |
| B crosses `x=0` | PASS | PASS | PASS | Standard B right pixels 15,860 and B button; Mosaic right pixels 0, B left button, `wev` right button and normal outside dismissal. |
| A and B cross `x=0` | PASS | PASS | PASS | Standard right A/B pixels 6,120/27,560; Mosaic 0/0 with separate visible A/B clicks. |
| A crossing hit in separate run | PASS | PASS | PASS | Standard right A button; Mosaic no right A button, `wev` button and normal dismissal. |
| Outside click and lifecycle | PASS | PASS | PASS | `popup_done` B then A; client destroys B then A; ordinary client receives left button. |
| Owner fully hidden, no click | N/A | N/A | PASS | Applied scene owner `(-1440,0,640,600)` does not intersect viewport `(-800,0,800,600)`; A/B pixels 0 then return with same XDG IDs. |
| Owner hidden with click | N/A | N/A | PASS | No hidden A/B button; B then A dismissed; pixels stay absent after camera return. |
| Mosaic → `splith` with A/B open | N/A | N/A | PASS | Right B pixels return to 15,860; B receives right button at `(20,195)` before any `popup_done`. |
| Positive horizontal regression | PASS | PASS | PASS | Standard B right pixels 15,860; Mosaic 0 with the same button-routing distinction as the historical horizontal probe. |

The B-crossing point was global `(20,195)` on HEADLESS-2. In standard
controls its open-capture RGB was B green `(32,208,160)` and its right click
went to B. In private Mosaic that point was ordinary background
`(238,238,238)`, and its right click went to `wev`; B received no button
there. The corresponding Mosaic visible B point `(-98,195)` was green and
delivered a B right button. For A, the separate standard crossing point
`(87,125)` was A yellow `(224,192,32)` and delivered an A button; Mosaic's
scene-adjusted point `(127,125)` was ordinary background and delivered no A
button, while visible A/B points remained interactive. Ordinary-client
delivery and popup dismissal are distinct observations; dismissal alone is
never counted as a clipped-surface hit.

The private `PROBE_POPUP_CLIP` log recorded clip local `(-242,-25,800,600)`
in the sampled Mosaic runs. Relative to viewport origin `(-800,0)`, this
gives applied root popup-tree scene origin `(-558,25)`; combining the logged
XDG configure offsets gives A `(-358,105,300,170)` and B
`(-138,165,300,130)` in `b_cross`. These match the independently calculated
owner/window/camera positions and the captured crossing colors. In
`both_cross`, A is `(-208,105,350,170)` and B
`(-48,165,300,130)`. A negative global origin is therefore present in both
the applied clip and popup surface geometry, not only in an IPC label.

For hidden owner, the compositor logged `PROBE_POPUP_HIDDEN_OWNER` with
applied `(-1440,0,640,600)` versus viewport `(-800,0,800,600)`, proving
empty intersection from applied scene state. The no-click run's left A/B
exact pixel counts were **42,200/17,940 → 0/0 → 42,200/17,940**. There
was no `popup_done` before return and no new XDG CREATE or MAP; XDG IDs
remained A 12 and B 15.
The IPC owner stayed container ID 8 and `focused=true` in open, hidden,
hidden-hover and returned snapshots; its logical rectangle stayed
`(-160,25,640,575)` while the applied scene position changed with camera.
In the separate hidden-click run, neither popup
received the right button; B then A received `popup_done`, were destroyed
child first and did not return. With both still open, switching to `splith`
restored the standard right B-green count **15,860** and a B right-button
press/release with no earlier dismissal.

The positive-origin regression used HEADLESS-1 `(0,0)` and HEADLESS-2
`(800,0)` with the same compiled clients and pointer. Both standard controls
again produced **15,860** B-green pixels on HEADLESS-2 and delivered the
right-output button to B. Private Mosaic produced **0** and delivered the
button to `wev`, followed by normal B/A dismissal. Counts happen to match
the historical horizontal probe after checking the actual applied placement;
the test did not assume their equality.

## Scope of conclusion

This negative-origin, two-output, nested-valid-grab experiment is
**FEASIBLE for the measured placements and event points**. It establishes
correct signed-to-absolute pointer conversion in the observed wlroots path,
real control crossing, sampled private clipping/hit behavior, hidden-owner
guard behavior and standard-layout restoration. It does not prove continuous
pixel coverage between samples or define universal offscreen-popup dismissal
UX. Scaling, rotation, output migration/resize, complete damage/effects,
transaction generations and ABI/package maintenance remain **NOT TESTED**.
STEP20C remains **NEXT** and production adjacent-output clipping remains
**NOT YET SUPPORTED**.

## Independent freeze replay (2026-10-11)

A fresh laboratory, `/tmp/swayfx-mosaic-nested-grab-1DzZQbcH/`, was built by
the preserved `prepare.sh` from full Git checkouts, rather than an archive.
Its build log is `/tmp/mno-prepare-ltr6sSlW`. Fourteen new run directories
cover pointer targeting on both outputs in all three configurations,
negative-origin B crossing and A+B crossing in all three, private Mosaic
hidden-owner return and `splith` return, and positive-origin B crossing in
all three. `analyze.py` decoded the new PNGs. The fresh output JSON again
reported `(-800,0,800,600)` and `(0,0,800,600)` for negative-origin runs.
In each pointer run, the owner received destination `wl_pointer.enter` at
local `(100,125)` and `(105,135)`, and `wev` received enters at `(28,55)`
and `(33,60)`; both clients also logged press/release events. These client
events, not injector acknowledgements, validate signed-global targeting.

New control and private-standard B-crossing captures each contain 15,860
B-green pixels on HEADLESS-2 and two B button presses. Private Mosaic again
contains zero B-green pixels there, preserves 17,940 on HEADLESS-1, delivers
the visible B press, and sends the clipped-side press to `wev`, followed by
normal B/A `popup_done`. For A+B crossing, both standard controls again
contain 6,120 A-yellow and 27,560 B-green right-output pixels; private
Mosaic contains zero of either there while retaining 30,080/6,240 on the
left. The fresh logs show distinct A/B XDG objects and actual A/B grab
serials (69/74 in the control B run; 63/68 in private Mosaic), with matching
button serial, configure/ack/map order and no recorded protocol error.
Serials varied in another control run, as expected; their numeric values are
run evidence, not a protocol constant.

In the new no-click hidden-owner run, `scroll_x` moved 400 → 1280 → 400,
both popup colors changed 42,200/17,940 → 0/0 → 42,200/17,940 on
HEADLESS-1, the same XDG objects remained mapped, and no `popup_done`
preceded return. In the new layout-return run, `splith` restored 15,860
B-green pixels on HEADLESS-2 and a B press without prior dismissal. The
positive-origin B-crossing subset reproduced the same control/private
distinction. These are sampled stabilized observations: the replay did not
capture every presented frame or establish complete damage coverage.

## Reproduction, provenance and validation

The retained laboratory is
`/tmp/swayfx-mosaic-nested-grab-NWy4A23x/`; its preparation log is
`/tmp/mno-prepare-4FC2ZHqF`. The source-only
[fixture](../../tooling/probes/step20c-negative-origin/README.md) documents a
fresh replay from a full Git checkout. The three unchanged private patches
applied with `git apply --check` to Mosaic
`cd550382b311efdbfe3ed892f4e1d281d852e754` and SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc`. The historical pointer
extents patch alone adapted a disposable copy of `pointer-daemon.c`; no new
private patch was needed. The historical nested client was byte-identical.
The environment used `/usr/bin/sway` 0.6, wlroots 0.20.2, SceneFX 0.5.0
and Wayland client 1.26.0. `ldd` resolved the private Mosaic executable to
the laboratory `libscenefx-0.5.so` and system `libwlroots-0.20.so`.

`artifacts-sha256.txt` lists **895** run files from the final and retained
intermediate cases; its SHA-256 is
`0f3d74cb3477aa24b5e0f6bcf84f736ffcd31280de04b08b4622a761046eb793`.
`sha256sum -c` verified **895/895**. `negative-origin-source-sha256.txt`
lists six source inputs; its SHA-256 is
`8cbf6228c0bd317442262265692f4027e41fd82c2e7c7cd22bbb0e03ddaf729d`,
and `sha256sum -c` verified **6/6**. Each run directory retains verified
output JSON, signed injections, observed client-local pointer reference,
XDG and `WAYLAND_DEBUG=1` traces, IPC trees, scene clips, two-output PNGs,
RGB/count analysis, `popup_done` order and process exit status. The
intermediate failed pointer-calibration check and its evidence remain under
`run-negative-control-pointer-initial`; earlier `both_cross` and `toggle`
attempts remain under `*-initial`. The final `both_cross` runs were replayed
with the settled runner. The first `toggle` sampled B on the left after
return; the final run explicitly sampled its right-output portion.

Private SceneFX and Mosaic builds passed; the Mosaic Meson model test passed
**1/1**. C17 syntax checks passed for both client sources against generated
protocol headers. Shell syntax, Python AST parsing without bytecode cache,
document links, `git diff --check`, source hashes and artifact hashes passed.
An independent structured matrix check passed pointer targeting, both grabs,
crossing colors/buttons, outside dismissal, hidden-owner, layout return and
positive regression. All completed case directories include actual exit
codes; normal runner teardown produced compositor/client `0` and expected
`SIGTERM` `-15` for the persistent pointer and `wev`. Their private runtime
directories were removed after reaping; no probe process remained. These
validation passes support only the measured scientific conclusion above.

No production Mosaic source, production patch, `PKGBUILD`, installed library,
historical fixture, UX policy or active session was changed; at the time of
the original experiment nothing had been committed or pushed. The smallest next bounded experiment is repeated
open/close and camera movement at this same negative-origin geometry, with
frame-by-frame stale-pixel and damage observations. It would test a currently
open gate without changing output transform or popup protocol.
