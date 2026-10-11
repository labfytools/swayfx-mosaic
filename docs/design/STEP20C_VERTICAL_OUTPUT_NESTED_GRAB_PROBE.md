# STEP20C vertical-output nested valid-grab probe

**Status: EXPERIMENTAL / FEASIBLE for the sampled vertical matrix.** This
protocol was written before adapting the preserved fixtures; measurements
were appended as the experiments ran. It does not authorize production clipping,
an offscreen-popup UX policy, or multi-output support. The canonical
[architecture](../ARCHITECTURE.md), [UX](../UX.md), [limitations](../KNOWN_LIMITATIONS.md)
and [roadmap](../ROADMAP.md) retain authority. The horizontal
[nested-grab probe](STEP20C_NESTED_VALID_GRAB_PROBE.md) is historical evidence
and remains byte-identical.

## Hypotheses and compared systems

Unmodified SwayFX in `splith` (A) and private SceneFX/Mosaic in `splith` (B)
should render and route a truly overflowing nested popup into the lower
output. The guarded private binary in `mosaic` (C) should retain visible
popup interaction above the boundary and omit popup pixels and hits below it.
The same two real pointer-button serials must create A and B in every case.
An outside click may dismiss both under a valid grab without delivering a
button to a clipped popup. A compositor with no measured overflow cannot
qualify the clip hypothesis.

## Geometry and coordinate contract

Request HEADLESS-1 `(0,0) 800×600` and HEADLESS-2 `(0,600) 800×600`.
Workspace 1 and its tiled Mosaic owner belong to HEADLESS-1; workspace 2
hosts ordinary `wev`. Record `get_outputs` before using any coordinate.
The global logical rectangle is `[0,800) × [0,1200)` only if IPC confirms
the requested positions, resolution, scale and transform. The Mosaic
viewport is the applied workspace/output intersection on HEADLESS-1; row
`scroll_x` translates the tiled scene horizontally and does not change Y.

The virtual pointer's absolute request uses global-layout extents
`(800,1200)` vertically and `(1600,600)` for the horizontal regression.
The historical injector is hard-coded to `(1600,600)` and must remain
unchanged. The new injector validates every requested point against its
configured extents, logs request and button completion, and stays alive
through each case. An injected coordinate is a request, not proof of the
cursor's actual target: correlate it with the client's `wl_pointer.enter`,
motion and button local coordinates, the lower-output `wev` events, and
screenshots. Record a mismatch as an injection/targeting issue before making
a compositor claim.

XDG positioner anchor rectangles are relative to their parent surface:
A to the toplevel, B to A. `xdg_popup.configure` reports a popup rectangle
relative to that parent. A candidate global popup rectangle is the applied
toplevel content origin plus A's configured offset, and for B additionally
plus B's configured offset. Verify that conversion against captured pixels
and pointer-local coordinates; the IPC owner `rect` is logical and its X
coordinate alone is insufficient after Mosaic camera translation. The
root popup scene is separately positioned in the global popup layer, with
its owner-derived clip translated into local scene coordinates.

SwayFX calls `wlr_xdg_popup_unconstrain_from_box` on initial popup commit and
reposition using the owner's output box expressed in toplevel coordinates.
The preserved client's positioner sets anchor and gravity but no constraint
adjustment; XDG Shell specifies default `none`. Do not infer the final
placement from the requested anchor: retain both `ROLE_CONFIGURE` rectangles
and pixels. If an attempted crossing is flipped, slid, resized or otherwise
entirely within HEADLESS-1, classify that case **INCONCLUSIVE** and try a
bounded alternative placement or size in the private client fixture. Never
force a compositor production position.

XDG Shell also requires the positioner's anchor rectangle to remain inside
the parent's effective window geometry. A review after the first 21-run
campaign found that the copied historical toplevel buffer was only 320 px
high while the new A anchors were at `y=350` and `y=480`. No protocol error
was logged, but this violates that specification. Those initial overflow,
hidden-owner and toggle measurements are **INCONCLUSIVE as XDG compliance
evidence**. The private client was corrected to use a 575 px toplevel buffer;
the observed effective `get_tree` window geometry became `420×575`, enclosing
both A anchors at `y=350/480`. B's `y=155/80` anchors remain within A's
170 px height. The full 21-run matrix below was repeated from that corrected
source. The historical source and compositor patches remain unchanged.

## Planned matrix and acceptance

| Scenario | Candidate placement | Required observations | Status |
| --- | --- | --- | --- |
| Two valid grabs, both fully visible | A and B high in HEADLESS-1 | Distinct parents, button serials, configure/ack/map, A/B clicks, no lower-output pixels | PASS at sampled points |
| B crosses `y=600` | A above boundary, B near its bottom | Control A and B show B below; Mosaic shows none there and B still works above | PASS at sampled points after corrected replay |
| A and B cross `y=600` | A near toplevel bottom, B within A | Separate A/B lower pixels in controls; separate upper hits, no lower popup hits in Mosaic | PASS at sampled points after corrected replay |
| Below-boundary input | Point chosen from the actual control B/A pixels | Separate move, left and right; popup local events versus `wev` and `popup_done` | PASS at sampled points after corrected replay |
| Owner hidden and returned | `scroll_x` 400→1280→400 | Same owner and popup IDs, applied scene/clip evidence, no hidden pixels/hits, same mapped objects return | PASS at sampled points after corrected replay |
| Hidden owner clicked separately | Same, with an outside click while hidden | No hidden popup button; record dismissal and absence of return after it | PASS at sampled points after corrected replay |
| Return to `splith` with popups open | Candidate crossing still mapped | Lower pixels and popup target return without prior dismissal | PASS at sampled points after corrected replay |
| Horizontal regression | `(0,0)` and `(800,0)` with historical B crossing | Valid grabs, original left/right pixel and pointer observations | PASS at sampled points |

For each A/B/C case, save effective output and workspace IPC JSON, owner
identity/rectangle and camera, `WAYLAND_DEBUG=1` client protocol, configured
popup geometry, compositor/scene logs, injection log, `wev` events, both
output PNGs and the chosen pixel/hit points. Treat visual visibility,
pointer delivery, grab dismissal and coordinate agreement as four separate
observations. A zero runner exit alone is insufficient. The first boundary
point must come from the *actual* control popup pixels below `y=600`, never
from the old horizontal `(900,190)` point. A candidate with no lower-output
popup pixels in the control is **INCONCLUSIVE** for overflow.

**FEASIBLE** requires real vertical overflow in both standard controls,
visual and interactive exclusion at sampled lower points in Mosaic, valid
grabs, and no blocking standard-layout regression. **PARTIALLY_FEASIBLE**
records a narrower demonstrated subset. A reproducible private compositor
pixel/hit leak, protocol violation or blocking standard regression is
**BLOCKED**. **INCONCLUSIVE** means the fixture cannot establish overflow or
cannot distinguish targeting from compositor behavior. Individual unrun
cells remain **NOT TESTED**.

## Laboratory and remaining boundaries

Build from the prior pinned Mosaic and SceneFX commits, applying the same
private patches in the same order. Keep all build trees, protocol output,
short mode-0700 socket directories, captures and logs outside Git. Clear
inherited desktop Wayland/IPC variables and pass every IPC command its
discovered private socket. Load private SceneFX only in the private compositor
process. Start and terminate only identified child process groups; preserve
the log and actual exit status on startup failure. No test may use the live
desktop socket or replace installed libraries.

This vertical popup experiment does not qualify tiled-window Y overflow,
other output geometries, scaling, rotation, migration, transaction-generation
agreement, complete damage/stale-pixel coverage, effects or SceneFX ABI and
package maintenance. The previous horizontal probe is a control, not a
production precedent. STEP20C remains NEXT and cross-output Mosaic remains
NOT YET SUPPORTED regardless of a narrow positive result.

## Observations and retained evidence

The first fresh unmodified SwayFX `visible` control confirmed IPC output
rectangles `(0,0,800,600)` and `(0,600,800,600)`, scale `1.0`, transform
`normal`. A's grab used received TOPLEVEL button serial 61; B's used received
POPUP_A button serial 66. Both role configure/ack/map sequences completed,
and separate right clicks reached A and B without dismissal.

The first `v_b_cross` control configured A at `(50,300,250,170)` relative to
TOPLEVEL and B at `(20,155,170,130)` relative to A. With the applied owner
content origin estimated at `(202,25)`, B's candidate global rectangle was
`(272,480,170,130)`. The HEADLESS-2 `open` capture contained **1,700** exact
B-green pixels, and the requested `(312,605)` yielded a B-local pointer
motion `(40,125)` and a right press/release on B. The corresponding
HEADLESS-1 frame had **20,400** B-green pixels. Thus the standard control
really crossed `y=600`; this is not yet a Mosaic clipping result. Artifacts:
`/tmp/swayfx-mosaic-nested-grab-YNqcOBkl/run-vertical-control-{visible,b_cross}/`.
The original horizontal reports and fixtures remain unchanged.

The first A/B/C `v_b_cross` comparison found the same **1,700** lower-output
B-green pixels in unmodified and private `splith`, versus **0** in guarded
Mosaic. Above the boundary, B received a right press/release in all three.
At `(312,605)` in the unmodified control and `(352,605)` in Mosaic, the
control B received B-local `(40,125)` and right press/release; Mosaic B
received no lower button and the grab dismissed B then A. However, `wev`'s
actual IPC rectangle begins at `y=625`, so this first lower point was over
the destination workspace decoration. **Ordinary-client delivery is PARTIAL
at this point.** The initial Mosaic `visible` run also failed solely because
the runner wrote a floating-point text coordinate (`534.0`) to the integer
injector; its `INVALID_INJECTION` log is retained with suffix
`-initial-invalid`. The runner now validates and converts integral values,
and a fresh visible run delivered separate right clicks to A and B. The
next bounded placement increases B's measured overflow to place a lower
sample inside the actual `wev` rectangle. These fixture findings are not
classified as compositor defects.

In a rebuilt laboratory using the revised `v_b_cross` placement, both
standard configurations configured A `(50,350,250,170)` and B
`(20,155,170,130)`; B's estimated global rectangle was
`(272,530,170,130)`. Each standard lower-output capture contained
**10,200** B-green pixels, and each delivered the `(312,640)` right
press/release to B at local `(40,110)`. Guarded Mosaic configured the same
relative rectangles; B's estimated global rectangle was
`(312,530,170,130)`. Its lower capture contained **0** B-green pixels,
while the left capture retained **11,900**. B received the upper right
press/release but no lower button. The ordinary `wev` at `(352,640)` received
the lower right press/release; the legitimate grab subsequently emitted
`popup_done` B then A. This is a measured B-only vertical visual/input clip
at these points. Artifacts:
`/tmp/swayfx-mosaic-nested-grab-gbU3A8Mk/run-vertical-{control,private_standard,private_mosaic}-b_cross/`.

The three `v_both_cross` runs configured A `(50,480,250,170)` and B
`(20,80,170,130)`. Both standard lower frames contained **6,000** A-yellow
and **19,550** B-green pixels; private Mosaic contained **0** of either
color there while retaining **21,200** A-yellow and **2,550** B-green above.
Separate upper right clicks reached A and B in all three. At the lower B
point, standard layouts delivered right press/release to B, while Mosaic
delivered it to `wev` and dismissed B then A without a lower popup button.
This tests both levels visually and their separate *upper* hits. A separate
lower A hit is measured in the `below_a` runs described next. Artifacts:
`/tmp/swayfx-mosaic-nested-grab-gbU3A8Mk/run-vertical-{control,private_standard,private_mosaic}-both_cross/`.

Separate lower-input runs at `y=640` resolve the hit target: in standard
layouts, B received the left press/release at `x=312`, and A received the
right press/release at `x=260` outside B. In Mosaic, neither lower click
reached a popup; `wev` received left at `x=352` and right at `x=300`, and
the grab dismissed B then A. Upper B and A clicks remained delivered before
those lower samples. These are separate runs because an outside click can
legitimately dismiss the stack. Artifacts: the same laboratory's
`run-vertical-{control,private_standard,private_mosaic}-{below_left,below_a}/`
directories. The lower right B comparison is the `b_cross` run above.

With B crossing in guarded Mosaic, `hidden` kept IPC owner ID **8** and
`scroll_x` **400→1280→400**. The private scene log reported applied owner
`(-640,0,640,600)` and viewport `(0,0,800,600)`. A/B exact left-output
pixel counts were **39,950/11,900** at open, **0/0** while hidden and on
hidden hover, then **39,950/11,900** after return. Each popup mapped once;
neither received `popup_done` before return. In the separate `hidden_click`
run, no hidden popup button was delivered, `popup_done` occurred B then A,
and neither popup returned after camera restoration. The `toggle` run kept
both mapped through `layout splith`; B-green pixels on HEADLESS-2 changed
from **0** to **10,200**, and B received a right press/release at
`(312,640)` without prior dismissal. Artifacts:
`/tmp/swayfx-mosaic-nested-grab-gbU3A8Mk/run-vertical-private_mosaic-{hidden,hidden_click,toggle}/`.

The adapted pointer also replayed the historical horizontal `b_cross`
geometry in all three configurations using `(1600,600)` extents. The two
standard lower-output captures had **15,860** B-green pixels and B received
the right-output right press/release. Guarded Mosaic had **0** B-green pixels
there, **17,940** on HEADLESS-1, no lower B button, and a right press/release
on `wev`; B then A were dismissed. All three used two distinct real grab
serials and mapped both popups. This matches the preserved horizontal result
at the historical points. Artifacts:
`/tmp/swayfx-mosaic-nested-grab-gbU3A8Mk/run-horizontal-{control,private_standard,private_mosaic}-b_cross/`.

The main fresh laboratory contains **18 validated vertical** and **3
horizontal** run directories. Its `artifacts-sha256.txt` lists **669** files;
the manifest SHA-256 is
`91830d91906039a5c9205f5b05e14f347969d516e2a5f13313969c9a78bf14a9`
and `sha256sum -c` returned **669 OK, 0 failures**. These are temporary
artifacts outside Git; the exact measured observations remain in this report
if that laboratory is later removed. The retained first shallow crossing
and rejected floating-coordinate injection are in the earlier temporary lab
`/tmp/swayfx-mosaic-nested-grab-YNqcOBkl/`, not included in this manifest.
The first full 21-run laboratory
`/tmp/swayfx-mosaic-nested-grab-yCtCIiUB/` is also excluded from the
corrected verdict and manifest: its 320 px toplevel left the vertical A
anchors outside the parent's effective window geometry.
The corrected fixture's SHA-256 values and rebuild commands are in its
[README](../../tooling/probes/step20c-vertical-grab/README.md).

The sampled result is **FEASIBLE** for the vertical nested-grab matrix above.
The standard controls establish actual Y overflow; the private Mosaic build
clips measured A/B pixels and input below `y=600` while preserving upper
interaction, hidden-owner camera return and standard-layout behavior. This
is not complete damage correctness, continuous clip coverage between samples,
all tiled-content Y overflow, a transaction-generation proof, or a SceneFX
ABI/package decision. Output scaling, rotation, negative origins,
resize/migration, decoration/shadow/blur/saved-buffer coverage and live
deployment remain **NOT TESTED** here. The next smallest distinct gate is a
separate negative-origin output geometry comparison with the same hierarchy
and direct unmodified/standard controls; it was not started in this probe.
STEP20C remains NEXT and multi-output Mosaic remains NOT YET SUPPORTED.

## Validation and provenance

### Independent freeze replay

A fresh local Git clone at `/tmp/mvg-freeze-clone-37QJ9Bq3/` received only
the five reviewed vertical fixture source files from this worktree. Its
`prepare.sh` reconstructed the pinned SceneFX and Mosaic sources, applied
the three unchanged private compositor/library patches in their documented
order and the two client-only patches to temporary copies, regenerated both
Wayland protocols, and rebuilt the private libraries, compositor and C17
clients. The new laboratory is
`/tmp/swayfx-mosaic-nested-grab-5MXNLRED/`; its build log is
`/tmp/mvg-prepare-DCyxEBUY`. `vertical-source-sha256.txt` verifies all six
new patch/script and patched-client entries against those sources.

The replay executed **17** scenarios: `b_cross`, `both_cross`, `below_left`
and `below_a` in each of unmodified SwayFX `splith`, private `splith` and
private `mosaic`; private Mosaic `hidden` and `toggle`; and `b_cross` in all
three configurations with the original horizontal output arrangement. All
17 runners exited zero, but the verdict also checks their client protocol,
pointer and `wev` logs, effective IPC geometry, scene log and both captures.
Every vertical run reported outputs `(0,0,800,600)` and
`(0,600,800,600)` with scale 1 and normal transform; the pointer extent was
`800×1200`. The effective toplevel `get_tree` geometry was `420×575`.
For B-only crossing, A configured `(50,350,250,170)` and B
`(20,155,170,130)`; for both-level crossing, A configured
`(50,480,250,170)` and B `(20,80,170,130)`. Each A anchor lies within the
575-pixel toplevel and each B anchor within A's 170-pixel height. Two
distinct received `wl_pointer.button` press serials matched the A and B
`GRAB_REQUEST` serials, and both configure/ack/map chains completed without
logged XDG protocol error.

At `open`, both new standard B-crossing runs again contained **10,200**
B-green pixels on HEADLESS-2, versus **0** in private Mosaic. Both-level
crossing again contained **6,000** A-yellow and **19,550** B-green pixels
on HEADLESS-2 in each standard control, versus **0/0** in Mosaic. The
controls delivered the measured lower B and A presses to the corresponding
popup; Mosaic delivered those presses to `wev`, with no lower popup press,
after upper popup interaction. `popup_done` followed B then A in the
outside-click cases. This dismissal is distinct from a hit on a clipped
popup. In the new `hidden` run, owner ID 8 and its logical rectangle stayed
fixed while `scroll_x` changed **400→1280→400**; one mapped A and B each
remained the same XDG objects, with no `popup_done`. Their left-output
color counts were **39,950/11,900 → 0/0 → 39,950/11,900**. The scene log
recorded applied owner `(-640,0,640,600)` against viewport
`(0,0,800,600)`. With both still open, `toggle` restored **10,200** B-green
pixels below the boundary and a button on B after `layout splith`. The
three horizontal runs repeated the historical standard **15,860**
B-green pixels on HEADLESS-2 versus **0** in private Mosaic, with the
same popup-versus-`wev` button distinction. No measured divergence was
found between this replay and the corrected historical campaign.

The new lab's `freeze-artifacts-sha256.txt` contains **574** run/command
evidence files. Its SHA-256 is
`c5666bc236dbfff52996295fee15c378af0baa2d657ec76ed4c7df172889337d`;
`sha256sum -c` verified **574/574** entries. The files remain temporary
and outside Git. An initial attempt using a source-only `git archive`
failed before any client or scientific scenario because the reused
preparation needs the pinned commit in a Git object database; its failed
build log is `/tmp/mvg-prepare-tZOrcirM`, and no completed `LAB=` was
reported. The full local clone resolved that fixture setup error. The
README now states this prerequisite. No scientific fixture or private
compositor patch was changed during freeze.

### Original corrected campaign

The final 21-case replay used one immutable set of private compositor/client
sources and the fixture `run.py` SHA-256
`b7dc778c01d9e8e1f058c1aa2bb0e3e0e8dfa6ad1ba8e5af122a0503cd7eef96`.
All 21 runs exited normally; independent checks of `client.log`, `wev.log`,
`pointer.log`, IPC, exact-color masks and ordered XDG events passed. Their
`measurements.json` records configured rectangles and sampling points;
`exit-status.json` records the actual compositor/child results. Each output
geometry was verified by IPC before injecting input. All 21 short private
runtime directories were removed and no probe process remained.

The private build used SceneFX `37ccd723bef49e6891156ffafce8f549f01446cc`
(`0.5.0`), Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754`,
wlroots `0.20.2`, Wayland client `1.26.0` and system control SwayFX `0.6`.
`ldd` resolved the private Mosaic binary to the laboratory
`libscenefx-0.5.so` and system `libwlroots-0.20.so`. The three unchanged
private compositor/library patches and two new client-only patches applied
with `git apply --check`; `vertical-source-sha256.txt` verified **6/6**
source entries. Private SceneFX/Mosaic builds and generated protocol files
succeeded. Shell and Python syntax checks, C17 syntax checks for both
clients, the Mosaic Meson model test (**1/1**), documentation links,
`git diff --check` and the 669-artifact manifest passed. An initial version
query used the wrong `pkg-config` name (`scenefx`); the corrected
`scenefx-0.5-uninstalled` query returned `0.5.0`. This command error did not
affect a build or run.

No production Mosaic source, production patch, `PKGBUILD`, installed library,
UX contract or historical fixture was changed. No commit or push belongs to
this experiment.
