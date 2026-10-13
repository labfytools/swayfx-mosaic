# STEP20C static root/nested valid-grab continuity probe

**EXPERIMENTAL / INCONCLUSIVE; architecture UNDECIDED. Frozen failure evidence.** The protocol below was written before fixture implementation
and graphical launch; completed observations are appended separately.
Canonical [architecture](../ARCHITECTURE.md), [UX](../UX.md),
[limitations](../KNOWN_LIMITATIONS.md) and [roadmap](../ROADMAP.md) govern.
STEP20A DONE, STEP20B EXPERIMENTAL, STEP20C NEXT, STEP20D–G PLANNED;
production multi-output NOT YET SUPPORTED. No algorithm or UX change.

## Prior evidence and exact question

Phase A froze the [static tiled RGB/input/standard evidence](STEP20C_STATIC_RGB_INPUT_STANDARD_RETEST.md)
in commit d0fa8c5c9e6f878a0cf30c16c5ce006392838791, verified directly on
Forgejo and GitHub with clean worktree. Its scientific verdict is FEASIBLE
only for its tested tiled matrix; its runner exit 1 / runtime INCONCLUSIVE
and compositor exit 0 remain immutable. No historical run is repeated.

The [popup ownership](STEP20C_POPUP_OWNERSHIP_PROBE.md),
[valid-grab hidden-owner](STEP20C_VALID_GRAB_HIDDEN_OWNER_PROBE.md),
[nested-grab](STEP20C_NESTED_VALID_GRAB_PROBE.md),
[vertical](STEP20C_VERTICAL_OUTPUT_NESTED_GRAB_PROBE.md) and
[R90 partial-popup](STEP20C_ROTATED_PARTIAL_POPUP_CLIP_PROBE.md) reports
establish sampled shared-private behavior and controls, not static continuity.
They distinguish invisible hits from legitimate outside-grab dismissal.
No new pristine control run is authorized; comparison uses those retained
controls. Static/shared exhaustive equivalence is NOT PROVEN.

Reuse only static candidate
`/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/stage-static/usr/bin/swayfx-mosaic`,
SHA-256 `f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b`,
build ID `942db64269640778ee433e5970ba1100bc60f94c`. Verify private identical
0755 copy, ELF64 x86-64, ordinary clip definitions, no SceneFX DT_NEEDED,
no missing relocation, and actual loaded system wlroots 0.20.2 SHA-256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
No compositor/library builds, binary modifications, system install or daily IPC.

## Client and XDG contract

Historical `step20c-nested-grab/nested-client.c` must remain byte-identical,
SHA-256 `2e40c98af72a0df8b316810589a0be8f4425a763db1de448b49a7813956b6f7d`.
Retain it separately from the adapted copy and private placement patch.
Reuse the exact valid-grab pointer daemon and static-reference/saved-client
sources. Reuse manifest-verified generated protocol files; retain XML hashes
and verify regeneration byte-for-byte. Compile only clients as C17 with
-Werror (-Wno-unused-parameter for existing listener signatures).

The [XDG protocol](https://raw.githubusercontent.com/wayland-mirror/wayland-protocols/main/stable/xdg-shell/xdg-shell.xml)
and installed XML require a user-action serial, mapped parent, grabbing popup
parent for B, pre-map grab, bufferless initial commit, configure/ACK before
buffer attachment, and reverse destruction. Client binds wm_base v3. A uses
the exact TOPLEVEL left press serial; B uses a new POPUP_A left press serial.
Both logs and WAYLAND_DEBUG requests must agree; nonzero serial alone fails.
A/B have distinct wl_surface, xdg_surface and popup roles, with B.parent=A.xdg.
No arbitrary serial, forced grab or protocol workaround is permitted.

The only private C delta adds placement `static_cross`: A anchor (100,80),
size 350×170; B anchor (100,60), size 300×130. Both 1×1 anchors are inside
parent effective SHM geometry (TOPLEVEL 420×320; A 350×170). Anchor top-left,
gravity bottom-right, default constraint adjustment none. No draw/grab/serial/
ACK/map/dismissal/destruction change. The toplevel keeps historical 420×320
buffer; assigned container content is measured separately. Source constants
and actual wl_surface.attach/protocol sizes qualify drawn dimensions.

For applied top content near (-318,25), predicted A=(-218,105,350,170),
B=(-118,165,300,130). Predictions are not evidence. Parse actual role configure,
measure owner scene and content offset, then independently correlate solid
paint and pointer-local coordinates. Require A.left<0<A.right and
B.left<0<B.right. Never vary anchors empirically after launch.

## Scene contract and observability

Exact candidate source parents root popup wrapper under root->layers.popup,
positions it from the applied view content tree, and derives its local clip
from current workspace's already-applied tiling clip and output intersection.
B's scene wrapper descends from A's XDG tree, retaining the same owner.
Source trace PI_OWNER distinguishes logical/current rectangle from scene;
PI_SCENE reports applied tiling clip; PI_POPUP reports root wrapper clip;
PROBE_POPUP_CLIP records owner pointer/local clip. Root wrapper origin differs
from A's configured painted origin. Correlate root local clip + applied content
origin with global [-800,0,800,600]. Child effective clip is inherited, backed
by exact source hierarchy and measured B pixels/input; no new child-node or
atomic-generation instrumentation may be claimed. Standard root clip removal
must appear in PI_POPUP, and B standard rendering/input must exercise inheritance
removal. Missing direct child trace is documented, not manufactured.

## Offline preflight and resource ledger

Before run reservation: source/protocol manifests, C17 syntax/build, binary/
loader identity, AST/shell/links, source audit (XDG hierarchy, input mapping,
configure/ACK/map, child-first destruction, clipping and shutdown), deterministic
color/coordinate/geometry/button predicates and negative cases, dismissal
classification and exit-classification tests all PASS. Live predicates are the
same functions used offline. Record `STATIC_NESTED_GRAB_FIXTURE_PREFLIGHT=PASS`.
No graphical launch to discover an offline-detectable error.

One exclusive persistent campaign owner file and one LAB outside Git. Stable
flock serializes fsync/atomic ledger updates; reservations persist before run,
chain, grab, click, pointer positioning, PNG, camera and transition. Failures
consume reservations; no refunds/reset/second LAB. Limits: run 1, pristine 0,
SceneFX/Mosaic builds 0, chains 2, grabs 4, camera 2 (at most one per chain),
Mosaic→splith 1, complete clicks 9, PNG 16, positioning/injection actions 24,
run duration 150 seconds. Planned 8 clicks and 15 PNGs; every click includes
and consumes one positioning action. No hide/return, scale/rotation/resize/
migration or additional campaign. Watchdog bounds owned process groups/logs;
all command timeouts and cleanup fit inside 150 seconds.

## Ordered runtime protocol

One headless compositor, private short runtime mode 0700, private Wayland and
explicit swaymsg -s socket. Clear inherited display/IPC/library/session overrides.
H1=(-800,0,800,600); H2=(0,0,800,600); scale1/normal. focus_follows_mouse no.
Create static H2 reference, discover PID/con_id, apply only its `[con_id=ID]
border none. Validate empty deco_rect, 800×600 content, visible XDG identity,
output/workspace; stored border width need not be zero. H1 filler may share
App ID, but never identity/PID/ancestor. Establish Mosaic, owner and H1 focus
before two H2 baselines separated by >=500 ms. Park private pointer and require
all 480,000 RGB pixels #303038 and exact equality. Stop dependents if unstable.

E1: reserve a fresh chain, map owner; compute signed relative camera delta from
actual PI_OWNER/content rectangle to center assigned content at x=0. Reserve
at most one correction; validate applied camera, same owner/workspace and clip.
Capture actual blue pixels, choose interior point, reserve grab and full left
click, open A using received press. Require configure/ACK/map; capture A, select
actual yellow interior, reserve second grab/left click to open B. Capture H1/H2;
require both crossings, positive A/B paint H1, zero A/B H2 and whole-H2 equality.
Choose B visible point from actual green pixels and inject right; require B pair,
no reference/filler event, no prior popup_done. Choose H2 point within measured
B continuation and actual reference, inject right; no invisible A/B button may
arrive. Observe reference pair and topmost-first popup_done separately; legitimate
dismissal is not an invisible hit. Verify clean H2, close E1 owner normally.

E2: new process, owner IDs and serials in the same compositor. Reserve chain,
verify Mosaic workspace, recompute sole possible camera correction, open A/B
with new actual left presses. Capture clipped state and whole H2, then send
`[con_id=E2] layout splith` without exterior click. Verify same workspace,
actual applied splith, both still mapped, no prior popup_done, tile/root clip
absent. Capture both outputs: require actual A/B crossings and positive A/B
colors H2, not empty-reference equality during intentional popup spill. Right
click actual green H2 interior must go to B. Send historical `close_b` command;
require B destruction, A survives, capture H2 and right click actual yellow
interior to A. Close owner normally; final H2 must fully equal baseline with
zero A/B residue. No stale IDs or points are reused across stages.

## Closure, classification and preservation

Record completion of all scientific gates before terminal exit. Audit
sway/commands/exit.c, ipc-server.c and main.c: termination may close socket before
queued writable reply. Keep swaymsg stdout, stderr and real code separately;
wait for compositor code and shutdown log, clients and residual groups/sockets.
Nonzero exit IPC is nonblocking transport only when all prior measures pass,
server handled exit, compositor=0, no crash/protocol error or rescue cleanup.
Never force code0 or claim IPC success when transport failed. Earlier functional
failure remains fatal to scientific qualification, regardless of shutdown.

FEASIBLE requires all listed identity/reference/XDG/grab/crossing/render/input/
dismissal/standard/cleanup gates in this matrix. PARTIALLY_FEASIBLE retains a
working main chain with missing secondary measurements; INCONCLUSIVE means
fixture attribution, geometry or protocol sequence not exercised. BLOCKED needs
actual visual/input leak, grab violation, runtime ABI/crash or standard regression.
Architecture is STATIC_NESTED_VALID_GRAB_FEASIBLE_FOR_TESTED_MATRIX,
STATIC_NESTED_VALID_GRAB_REQUIRES_REDESIGN, or UNDECIDED respectively.

Retain raw exact source/patch/runner/config, WAYLAND_DEBUG, timestamps/injections,
IPC/scene/client logs, actual codes, PNGs, dependency maps and source/evidence
SHA-256 inventories. Seal only after collection; verify every entry read-only.
Available damage extents and stabilized capture changes are partial evidence:
no intermediate-frame/minimal-damage/native-buffer/GPU-texture guarantee.
Hidden owner, scaling/rotation, migration/resize, saved buffers, effects,
complete damage/transactions and exhaustive ABI are NOT TESTED in this campaign.
Synchronize this report, fixture README, architecture, limitations, roadmap,
document index and changelog. B stays local and uncommitted, never pushed.

## Offline preparation completed before run reservation

LAB `/home/fy59/swayfx-mosaic-static-nested-grab-m0a5e2qh`, exclusive owner
`/home/fy59/swayfx-mosaic-static-nested-grab-v1.owner`. Exact candidate/0755/
ELF/build ID/ordinary symbols/ldd -r/system wlroots 0.20.2 pass. Three client-only
C17 syntax and executable builds pass with -Werror; both protocol regenerations
are byte-identical to manifest-verified inputs. Original nested SHA matches.
Private placement patch SHA-256
`e0e87fb0cb3d6e7dafb1cd59ccb50f323f2934e65247526199da1695487d3e4a`;
adapted C SHA-256
`6eafb8ad63b0b06b8297e7e72711056a6d42bdf33ccf795793eeda77f98221c7`.
Exact frozen live runner SHA-256
`e2bde767036096e4633f9dd4fe3deb1b147f6415dc550a46802a6a90c4bd6486`.

First offline check stopped on a negative with the original button deliberately
removed: the shared predicate correctly rejected it via ValueError, but the
test harness initially counted only assertion/runtime errors. Correct only
that harness in `LAB/preflight-correction/check.py`; retain immutable original
`LAB/fixture/check.py` and the incident JSON. No live predicate/runner change,
no budget reservation or graphical launch occurred. The corrected checker
then passes retained actual standard-control protocol, actual historical
border-none/stored-width2 reference, labelled synthetic geometry/paint/input,
16 negatives, ledger concurrency/exhaustion/corruption and terminal outcome
positives/five negatives. AST/shell/links and exact frozen inventory pass.
All live predicates are the same frozen functions exercised offline.

`STATIC_NESTED_GRAB_FIXTURE_PREFLIGHT=PASS`.
Runtime remains NOT TESTED at this point; reserve the sole run only afterward.


## Completed single runtime — 2026-10-13

`SWAYFX_MOSAIC_STATIC_NESTED_VALID_GRAB_PROBE=INCONCLUSIVE`.
Architecture: **UNDECIDED**. This is a fixture geometry failure before the first
popup, not a demonstrated clipping, grab, ABI or standard-layout defect.
The sole compositor run is consumed; no retry or second laboratory. The
intended two-chain experiment was **not completed** and must not be described
as popup evidence. No new Mosaic/SceneFX build, binary/algorithm/shader change,
production/UX/package change or installation occurred.

### Actual identity, output, focus and reference

Original and private executable retain SHA-256
`f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b`,
build ID `942db64269640778ee433e5970ba1100bc60f94c`, mode0755, ELF64 x86-64.
Ordinary clip definitions and ldd -r pass; no SceneFX DT_NEEDED/RPATH/RUNPATH
or loaded shared SceneFX. /proc/exe resolves to the private copy; actual /proc
maps show system wlroots 0.20.2 SHA-256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
All protected production/system/package/UX/AGENTS/binary hashes pass afterward.

Actual outputs match H1=(-800,0,800,600), H2=(0,0,800,600), scale1/normal.
Reference ID7/PID1737643 belongs to workspace2 ID5/H2; only its discovered
con_id receives border none. Stored width2 persists, deco_rect empty,
rect/window_rect 800×600, visible xdg_shell, correct app_id/PID/output.
Filler PID1737649 is distinct despite the same app_id. E1 owner ID9/PID1737655
belongs to workspace1 ID6/H1, focused and mapped. IDs were discovered, not
hard-coded. Only one chain instance was reserved/mapped.

After E1 map, applied camera was 480. PI_OWNER measured scene(-640,0,640,600),
content x=-638, assigned content636×573. Desired content x=-318 yields the
sole relative correction **-320**, resulting in camera160, applied owner
scene(-320,0,640,600), content x=-318. PI_SCENE reports local tile(-160,0),
clip(160,0,800,600); with H1 origin this gives [-800,0)×[0,600).
H2 tiling clip is absent. No popup root or child clip was measured.

Two independent 800×600 reference PNGs were captured after setup/H1 focus and
pointer parking, >=500ms apart (requested extra delay600ms). Every RGB pixel
is #303038; zero differences, no mask or tolerance. Both PNG SHA-256:
`4471e93ccb6cf3ff4970f61fce405431a228af598d2f1f030a3b7586962ecd7a`.
This establishes pre-popup reference stability only. No popup-phase whole-H2
capture exists. The third PNG, E1-top, has 182,214 actual blue pixels, box
[482,25,800,598) in H1 local coordinates, giving global visible x[-318,0),
y[25,598). It does not establish popup clipping or popup geometry.

### Runtime fixture failure and source-based diagnosis

The frozen runner stops at `E1-open-A`, **before any click/grab reservation**.
Line182 asserts painted height320 from the native SHM constants. The actual
client creates a 420×320 SHM buffer, then receives and ACKs configure636×573
without redrawing (historical client behavior). SwayFX
`output_configure_scene` in the exact candidate's sway/desktop/output.c:331
sets the tiled scene buffer destination from applied content width/height.
The captured blue height is573, consistent with this source path, not320.
The failed assertion is therefore an invalid fixture assumption.

An additional assertion at line183 was not reached: it requires painted y
= owner scene y + IPC window_rect.y. Exact sway/ipc-json.c intentionally
sets window_rect.y=0 when a titlebar is enabled; actual IPC has that0,
deco height25 and painted y25. The prior static retest already distinguished
native buffer y from window_rect.y. This source-visible error should also
have been caught before the run. No rendered-buffer/IPC equivalence contract
is invented to make the fixture pass.

The recorded preflight marker remains PASS for its actually executed tests.
Its assertion/source audit was **INSUFFICIENT / retrospective FAIL** for these
two live assertions; it did not satisfy the full intended offline gate.
No retrospective rewrite of offline-gate.json, runtime.json, frozen runner,
protocol or budget is made. Preparation's missing-origin negative-case harness
incident and this runtime geometry incident are separate. The full client
protocol buffer/configure/ACK/map, IPC, PI_OWNER/PI_SCENE and PNG are retained.
`geometry_audit.py` reproduces both invalid assumptions read-only, verifies
actual reference/camera/clip/paint/codes and confirms zero popup creation,
zero pointer button and zero grab. This offline diagnosis is not graphical
qualification. The original runner remains byte-identical and is preserved
as failed experimental evidence; it is not a ready replay fixture.

### Unexercised protocol, geometry and input

The historical nested C source remains byte-identical; the sole private delta
is the legal static_cross placement. Original C and adapted C/patch are retained
with distinct hashes. The source hierarchy and historical control/replay show
correct XDG parentage, real button serial use and child-first destruction.
In this new runtime, however, **A and B were never created**. No A/B configure,
ACK, MAP, grab request, serial, enter/button, popup_done or destruction exists.
Neither predicted crossing is a measurement. E2 was never reserved or spawned;
no standard transition, standard popup pixels/input or popup residue cleanup
sample was exercised. All those matrix cells are NOT TESTED.

### Terminal exit and owned cleanup

Runtime duration5.485246415s; actual runner exit1, runtime INCONCLUSIVE,
measurements_completed=false, watchdog=false. The finally path explicitly sends
exit on /tmp/msng-jfnc_v3o's private IPC socket; stdout empty, stderr
`Unable to receive IPC response`, actual swaymsg code1. Server log records
Handling command exit and Shutting down sway; compositor exits0. E1, filler,
reference and pointer all exit0, with normal owned cleanup and no rescue signal.
No wl_display.error/protocol-error event appears. Ordinary startup backend
errors/noise are retained; no compositor crash is observed.

The command's queued response may have been lost at socket closure, compatible
with audited source. It is **not accepted as a nonblocking scientific exception**:
the earlier geometry failure occurred before measurements completed. The
terminal classifier correctly retains scientific_cleanup_pass=false. Composite
shutdown/cleanup success does not turn this campaign into FEASIBLE.
All owned PIDs/process groups are gone; short runtime removed, no sockets left.
No daily compositor/socket/process was touched.

### Budget, damage and retained inventories

| Resource | Consumed / ceiling |
| --- | --- |
| Static compositor runs | 1/1 |
| Pristine / SceneFX build / Mosaic build | 0/0 each |
| Chain instances | 1/2; E1 toplevel only |
| Valid-grab reservations | 0/4 |
| Camera corrections | 1/2; E1 only |
| Mosaic→splith | 0/1 |
| Complete clicks | 0/9 |
| Pointer positioning | 1/24 |
| PNGs | 3/16 |
| Runtime seconds | 5.485246415/150 |

Unused chain/click/PNG counters cannot authorize another compositor run.
The durable ledger remains consumed, with no refund/reset/retry. Available
TEMPORAL_DAMAGE extents cover only setup, camera, captures and shutdown;
A/B appearance, partial popup clipping, outside dismissal/destruction, standard
return and disappearance damage are NOT TESTED. Only stabilized reference
RGB is compared. No all-frame/minimal-damage/native-PNG/GPU guarantee.

Frozen pre-run fixture and source inventories remain immutable. Collector and
read-only diagnostic are preserved separately in LAB/postrun-fixture; corrected
offline harness in LAB/preflight-correction. Both are included in source sealing.
Source:30 entries, SHA-256
`9b76aae162faa631bf1930677d484359dfc3e29ace237b9aee2daa3d5cd68dc4`.
Evidence:96 entries, SHA-256
`5750d1e74636c2d276800f795ed0214c3e12999908149855af0b382a2da9bfb4`.
Every entry is verified read-only; reports and closeout receipts live outside
the sealed inventories to avoid circular hashes. No generated binary/PNG/JSON/
protocol/build/socket/log is added to Git.

### Architectural answers for this campaign

| Question | Evidence-backed answer |
| --- | --- |
| Q1 A/B real button serial? | NOT TESTED; zero runtime buttons or grabs. Historical source/control passed offline. |
| Q2 distinct compliant grabs? | NOT TESTED; no A/B objects in the new run. |
| Q3 hierarchy correct? | Correct in exact source and retained historical control; runtime A→B NOT TESTED. |
| Q4 both really cross x=0? | NOT EXERCISED. Requested anchors and predicted boxes are not configured geometry. |
| Q5 clip from applied owner? | Tiled applied viewport measured; popup root/child NOT TESTED. |
| Q6 permitted A/B pixels? | NOT TESTED; only toplevel blue182214 measured. |
| Q7 forbidden popup pixels absent H2? | NOT TESTED; two pre-popup H2 references stable. |
| Q8 visible B input? | NOT TESTED. |
| Q9 invisible B events? | NOT TESTED; no popup/input exists, not proof of exclusion. |
| Q10 outside grab behavior? | NOT TESTED; historical controls distinguish dismissal from hit. |
| Q11 popup_done distinct from invisible button? | Yes as protocol/measurement categories; no new dismissal or button sample. |
| Q12 A/B survive splith E2? | NOT TESTED; E2 and transition not executed. |
| Q13 clips removed? | NOT TESTED for popup or standard transition. |
| Q14 standard popup colors on H2? | NOT TESTED. |
| Q15 standard A/B buttons? | NOT TESTED. |
| Q16 popup residues after closure? | NOT TESTED because none opened; process/socket cleanup PASS separately. |
| Q17 static regression versus private shared controls? | UNDECIDED for popups; no valid static comparison was obtained. |
| Q18 algorithm change justified? | No. Confirmed errors are fixture assertions; no clipping defect demonstrated. |
| Q19 matrices open? | Static hidden-owner, scale, rotation, resize/migration, saved-buffer/effects, full damage/transactions and exhaustive ABI. Historical sampled evidence is not replayed or promoted. |
| Q20 smallest next gate? | First correct and replay all geometry predicates offline against actual native/configured/painted/IPC observations, including titlebar and standard states; then a separately authorized fresh one-run static two-chain gate. Current run budget is exhausted. |

Validation PASS: original nested hash, placement-only delta, C17/client builds,
protocol byte identity, binary/loader/maps, outputs/focus/camera/tiled clip,
reference whole RGB, actual paint diagnosis, owned codes/cleanup, protected
hashes, manifests, AST/shell/links and diff. FAIL: full preflight assertion audit
and the exact runtime geometry assertion; runner code1. NOT RUN/NOT TESTED:
new pristine/compositor/library builds and all new popup/input/standard gates.
No subagent review is claimed; final local delta/source/evidence audit is by the
parent. This historical report and source fixture are now frozen for publication
in the failure-freeze phase. A separate offline geometry gate remains local
and cannot change this historical verdict or authorize another run.
STEP20C remains NEXT, production multi-output NOT YET SUPPORTED.

## Failure evidence freeze — 2026-10-13

Read-only revalidation verifies all24/30/96 entries of the historical inventories
and reproduces both invalid assertions without launching a compositor. AST,
Shell blocks, Markdown links, source-only Git content and exact distinctions
between executed, corrected-checker and postrun sources pass. The executed
runner SHA and raw runtime/terminal codes remain unchanged. The single commit
for this freeze preserves INCONCLUSIVE / UNDECIDED and all NOT TESTED cells.
No historical run, ledger, manifest, client source or binary is modified.
