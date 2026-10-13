# STEP20C static RGB, input and standard-return retest

**EXPERIMENTAL / LOCAL / UNCOMMITTED. Protocol before fixture development.**
Phase A froze the historical failure in
`fb0293cd855a2ec917c14df3ecf3504c064499fc`, published to canonical Forgejo
and GitHub with a clean worktree. This independent phase B is never committed
or published. [Architecture](../ARCHITECTURE.md), [UX](../UX.md),
[Roadmap](../ROADMAP.md) and [Packaging](../PACKAGING.md) remain authoritative.
D1–D4 persist. STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT; STEP20D–G
PLANNED. Production multi-output remains NOT YET SUPPORTED.

## Historical error and mandatory offline gates

The [frozen follow-up](STEP20C_STATIC_RUNTIME_FOCUS_INPUT_STANDARD_PROBE.md)
stopped on an invalid `current_border_width == 0` assertion, before any PNG,
click or standard return. Its verdict remains INCONCLUSIVE / UNDECIDED and
its run/camera budget is exhausted. Neither its runner nor manifests change.

Pinned SwayFX `fd71a6bdc061bd633b488ae7b83e8a6981d22f86` border.c sets
B_NONE and only changes thickness with an optional second argument. The exact
candidate's ipc-json.c reports stored current.border_thickness; transaction.c
sets effective B_NONE border width/top to zero. Therefore width 2 is accepted
as recorded metadata under border none. A shared pure predicate validates the
actual IPC object, identity, ancestors, visibility, border mode, empty deco_rect,
full rect/window_rect and exact H2 geometry. The runner imports the same function
as the offline tests. No parallel implementation is permitted.

Read-only replay uses the sealed
`/home/fy59/swayfx-mosaic-static-followup-nhwejz6u/results/preflight-snapshot.json`,
scene traces, client logs and earlier real IPC observations. Historical IDs
7/8/9 and PIDs are used only in replay. Negative tests alter explicit copies:
wrong App ID, PID, ID, workspace, output, visibility, border, deco, absent view,
window/content/output geometry, focus, camera and clip must be rejected.
An actual earlier border-normal reference must also fail.

`STATIC_REFERENCE_IPC_REPLAY=PASS` and `STATIC_FIXTURE_PREFLIGHT_REPLAY=PASS`
are mandatory before any run reservation. Historical PNGs from the older static
runtime may validate pixel/coordinate code, clearly labelled HISTORICAL; the
failed follow-up contains no PNG. Synthetic button fixtures are explicitly
SYNTHETIC, never new input evidence. Tests check exact BTN_RIGHT=273 press/release,
positive real-format serials, timestamps/order, event count, malformed lines,
wrong recipient and absence in both other clients. No events may be silently
discarded by the button parser.

## Assertion authority and remaining measurement

| Field / assertion | Source and meaning | Offline evidence / live requirement |
| --- | --- | --- |
| outputs rect/scale/transform | ipc-json output description, logical coordinates | actual snapshots, wrong-output negatives; reread live |
| App ID/PID/con_id/ancestors | real view/node and tree ownership | actual reference/target/filler; live IDs discovered by PID |
| visible/focused/workspaces | view_is_visible and default-seat focus; not pixel coverage | actual tree plus get_workspaces; sample live |
| border/width | current border enum and stored thickness | B_NONE width 2 accepted; normal rejected |
| rect/deco_rect/window_rect | node box with title removed; decoration and content-relative box | actual full H2, empty deco; pixels still require capture |
| scroll_x | Mosaic row state, may precede applied scene | compare IPC with native PI_SCENE after settling |
| PI_OWNER scene/applied_size | wlr_scene_node_coords, animation current size | parse actual target trace; never use IPC rect as buffer y |
| PI_SCENE local/global clip | applied tiling tree, private get_clip | output origin + tiling translation + local clip equals viewport |
| client COMMIT size/color | exact C17 SHM draw, configure/ACK loop | actual logs; target horizontal width compared with IPC content |
| SHM colors | XRGB8888 target 0x2344cc/0x20d0a0; reference 0x303038 | source and historical PNG; live captures required |
| capture coordinates | scale 1/normal, local x=global x-output origin | signed-coordinate tests and measured pixels; no approximate native y |
| click point | 41×41 actual-color interior, margin 20; H2 continuation | historical image and negative sparse fixtures; recompute live |
| BUTTON log | real pointer callback, ns/serial/button/state | positive/negative parser tests; live delivery mandatory |
| splith criteria owner | layout.c uses matched container workspace; Mosaic clears parent target | exact candidate source audited; standard trace/pixels/input live |

The machine-readable assertion audit records each source location, historical
input, replay result and uncertainty. Assertions depending on new RGB/input or
standard-return observations remain explicitly live requirements; historical
or synthetic success cannot qualify them. No presentation hypothesis is an
invariant. True output/ownership/input/clip invariants remain required.

## Exact candidate, isolation and immutable runner

Reuse only
`/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/stage-static/usr/bin/swayfx-mosaic`:
SHA-256 `f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b`,
build ID `942db64269640778ee433e5970ba1100bc60f94c`.
Check regular executable, ELF64 x86-64, private clip get/set ordinary ELF definitions (not necessarily .dynsym exports), DT_NEEDED,
no SceneFX shared dependency, ldd -r and the exact system wlroots SHA-256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
Copy unchanged into one new campaign-owned laboratory outside Git. Compile
only the three historical C17 clients from manifest-verified exact C/protocol
sources; retain sources, commands and binary hashes. No SceneFX/Mosaic build.

The prepared laboratory has one exclusive owner file and persistent flock
ledger. Offline gates, source audit, AST, C17, library identity, ledger tests,
documentation and the exact runner inventory must all pass before reservation.
Freeze hashes of the executed fixture and verify them immediately before run.
Do not edit that copy afterward. Reports/collector receipts are separate.

Private runtime mode 0700, headless backend, private WAYLAND_DISPLAY and
explicit private swaymsg -s only. Strip inherited desktop sockets/library
overrides. Own process groups, bounded logs and 150-second watchdog. Retain
logs/exit codes before removing only owned sockets/runtime. No daily IPC.

## One-run ordered protocol

HEADLESS-1=(-800,0,800,600), HEADLESS-2=(0,0,800,600), scale 1, normal.
No popup, rotation, fractional scaling, resize, migration, saved-buffer scenario
or added effect. Set focus_follows_mouse no. Create H2 static reference, discover
its real PID/con_id, and apply only `[con_id=ID] border none`. H1 filler shares
its App ID; never apply a global App ID rule. Create H1 target and establish
Mosaic with target/workspace 1 focused before any H2 reference PNG.

Measure applied scene and client content width. Compute desired left=-width/2
and signed camera delta from that actual state, reserve once and apply. Do not
hard-code +160. Confirm IPC/applied scroll, owner crossing x=0, workspace identity
and global clip [-800,0,800,600]. No second adjustment if later focus moves it.

Park pointer on H1 (-790,590), stabilize and capture H2 twice at least 500 ms
apart. Require 800×600, fixed #303038 throughout and exact full RGB equality;
retain PNG hashes. No tolerance, crop or excluded ROI. Difference stops all
dependent tests and records every differing pixel.

Capture H1/H2 Mosaic. Require positive measured target paint on H1, continuation
across x=0, zero target colors on H2 and full H2 RGB equality. Client COMMIT,
painted bbox and scene-derived horizontal continuation are separate observations.
Select visible click from actual target-colored H1 pixels with 20-pixel margins.
Select H2 point in geometric continuation, within the actual full reference
surface, at least 20 pixels from borders. One right press/release to visible
target; exact client traces, no delivery to other clients. One right click to H2;
zero new target/filler events, actual reference pair, record focus and camera.
Park pointer on H1, recapture whole H2 and require exact equality after focus.

Send `[con_id=targetID] layout splith`, even when global focus is H2. Require
same H1 workspace, actual splith, mapped target, absent H1/H2 tiling clips,
ordinary target pixels and zero forbidden target pixels on H2. Capture both
outputs and compare whole H2. Recompute standard target interior; third right
click must deliver real target pair only. Park pointer, capture final H2 and
check focus-transition RGB. No reuse of Mosaic point without measurement.

## Budget, classification and preservation

Limits: static run 1, pristine 0, Mosaic build 0, SceneFX build 0, camera 1,
right clicks 3 (one of each named kind), movements 8, PNG 12, duration 150 s.
Every click also moves the pointer and consumes a movement reservation. Reserve
before run/capture/click/camera/move; failed work consumes reservations, no reset,
refund or second laboratory. Expected PNG 8, movement 6 including click motions.

FEASIBLE requires all exact candidate/replay/reference/Mosaic/input/standard
gates and no crash/protocol blocker in this precise matrix. PARTIALLY_FEASIBLE
retains demonstrated properties with open paths. INCONCLUSIVE denotes fixture
measurement failure. BLOCKED requires measured clipping/input/ABI/standard
defect, not an invalid fixture assertion. Architecture is respectively
STATIC_MOSAIC_RGB_INPUT_STANDARD_FEASIBLE_FOR_TESTED_MATRIX,
STATIC_MOSAIC_RGB_INPUT_STANDARD_REQUIRES_REDESIGN, or UNDECIDED.

Retain exact fixture/client/config, raw PNG/IPC/protocol/client/scene logs,
timestamps, serials, library mappings and exit codes outside Git. Produce all
requested result JSON and seal source/evidence inventories once, excluding
manifests themselves. Verify every entry read-only. Damage extents, client
damage requests and final PNGs do not prove intermediate frames or native
output-buffer identity. Wider geometry, popup/grabs, lifecycle/effects/buffers,
applied-generation consistency, complete ABI/maintenance/notices remain open.
No algorithm change or STEP20C integration follows automatically.

The [source-only fixture](../../tooling/probes/step20c-static-rgb-input-retest/README.md)
contains replay, predicates, ledger, runner, pixel analysis and collector.

## Preparation incident before run reservation

The first preparation in the single new LAB stopped because the checker used
`nm -D` for private static clip functions. The exact historical symbol receipt
qualifies ordinary executable T definitions, and `nm` confirms both. This is
a checker error, not a missing function or ABI failure. Preserve the original
checker and dynamic-symbol log; continue only that same LAB's pre-run preparation,
with no budget reservation/reset and no compositor launch. The corrected gate
uses ordinary ELF symbols. The initial checker and incident are evidence files;
the subsequently frozen/executed runner is explicitly distinct.

## Completed single campaign — 2026-10-13

`SWAYFX_MOSAIC_STATIC_RGB_INPUT_STANDARD_PROBE=FEASIBLE`

Architecture:
**STATIC_MOSAIC_RGB_INPUT_STANDARD_FEASIBLE_FOR_TESTED_MATRIX**.
This is a scientific verdict on the requested static, tiled, two-output matrix;
it does not mean the runner command exited zero, nor close STEP20C production.
LAB `/home/fy59/swayfx-mosaic-static-rgb-input-retest-hn67lnhq`.
Run duration 9.142914 seconds, one run, no retry. No pristine run, no new
SceneFX/Mosaic build, no binary/shader/algorithm/production/package/UX change.

### Candidate, clients and offline gates

The original and copied executable both retain SHA-256
`f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b`
and build ID `942db64269640778ee433e5970ba1100bc60f94c`, regular executable
mode 0755, ELF64 x86-64. Ordinary ELF clip get/set T definitions pass; these
private static definitions need not appear in .dynsym. No SceneFX DT_NEEDED,
RPATH/RUNPATH, unresolved relocation or loaded shared SceneFX exists. Actual
process maps identify the unchanged system wlroots with SHA-256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
The historical full source/evidence inventories and follow-up 24/46-entry
inventories were verified read-only. No historical manifest was rewritten.

Three C17 client-only syntax checks and builds passed from exact verified
historical C/generated-protocol inputs; commands are in raw/commands.jsonl:

| Client | Result executable SHA-256 |
| --- | --- |
| saved-client | `3d5d0c5e446b995c210006a5bafe0d86dd5f32a228e1b7137d12af6ec9e217da` |
| static-reference | `11166ea1bb7cb3bb08f10ab93e091c5c5ea8687649b5fb0705288c7ca91680e8` |
| pointer-daemon | `76ad0f093f2b7a97359920b7bd456cfa93a1581c73875547a86eb911f2ed2d7a` |

The corrected shared predicate accepted the actual historical H2 node with
border none / stored width 2, full window_rect and zero deco_rect. Thirty-nine
negative cases rejected wrong identities/ownership/geometry/focus/clip, the
actual filler, an actual earlier normal-border reference, sparse/inaccessible
pixel fixtures and invalid synthetic button sequences/recipients. Historical
PNG and synthetic input observations remain explicitly labelled. Both required
replay markers passed, with AST, shell recipes, links and durable concurrent/
exhausted/corrupt-ledger tests before reservation.

The exact runner SHA-256 is
`07ce1f98c9cb35ddb5219aff3991f19321759ac4edb26ab6d354096a853979d6`.
The pre-run fixture inventory (10 source files plus protocol) has 11 entries,
SHA-256 `294c001b5e88d7759255afb59646a386a59e2273f21e19c5a29512a4230f56a2`.
The executed copy remains immutable. The live runner imports the same validators
as replay. No width-zero assertion was relaxed after launching the compositor.

### Applied ownership, border, camera and clip

Both real outputs match (-800,0,800,600) / (0,0,800,600), scale 1, normal.
Reference con_id 7/PID 1700453 belonged to workspace 2 (ID 5), H2. Filler ID 8/
PID 1700459 kept normal border; target ID 9/PID 1700462 belonged to workspace 1
(ID 6), H1. These IDs were discovered at runtime, never hard-coded in the runner.
Target/workspace 1 initially focused; reference unfocused. Only `[con_id=7]
border none` affected H2. IPC retained width 2, rect/window_rect 800×600 and
zero deco_rect; full RGB then independently established absent rendered decoration.

Applied scroll initially 0. Actual target horizontal content left -158, width
636, desired left -318 gave the sole signed correction +160. This was computed
again from actual state, not borrowed as a constant. IPC and scene both read
160. Owner scene (-320,0,640,600), content continuation [-318,318), actual client
COMMIT 636×573. Tile-local translation (-160,0), local clip (160,0,800,600), H1
origin (-800,0) yield global clip (-800,0,800,600). H2 tiling clip is absent.
Native buffer y was never inferred from window_rect.y.

### Whole RGB and measured input

The two 800×600 H2 references, captured 600 ms apart after H1 focus/setup and
pointer parking, are entirely #303038 and exact RGB equals. Every subsequent
H2 PNG is also entirely equal: Mosaic, after H2 click/focus, standard layout,
and after standard target click/focus. Six H2 PNGs share SHA-256
`4471e93ccb6cf3ff4970f61fce405431a228af598d2f1f030a3b7586962ecd7a`.
Five independent whole-frame comparisons each have zero changed pixels; no
crop, excluded ROI, RGB tolerance or focus compensation.

H1 Mosaic contains 182,214 target-colored pixels, solid painted box local
[482,25,800,598), global x [-318,0), against continuation [-318,318).
H2 has zero target-colored pixels plus independently exact whole RGB.
H1 Mosaic PNG SHA-256:
`1ca64ee4aac80dd8377609528598608a412c1169d75bd4bce93b394292919ab8`.

| Actual injection | Recipient and real serials | Other client buttons | Focus afterward |
| --- | --- | --- | --- |
| Mosaic visible (-159,311) | target, BTN_RIGHT 273 press 35/release 36 | reference/filler none | target 9, workspace 1 |
| Mosaic continuation on H2 (100,311) | reference, press 48/release 49 | target/filler none | reference 7, workspace 2 |
| Standard recomputed (-200,311) | target, press 67/release 68 | reference/filler none | target 9, workspace 1 |

Each point uses measured captured pixels and a 41×41 interior neighborhood;
H2 also lies within the un-clipped target's measured horizontal continuation.
Client logs retain ns timestamps, real serials, enter/motion and protocol traces.
All target logs contain exactly four button lines (visible + standard pairs),
reference exactly two, filler zero. Camera remains 160 after both Mosaic clicks.
Reference focus changes without any H2 RGB difference.

After reference focus, `[con_id=9] layout splith` keeps H1 workspace ID 6,
changes its actual layout to splith and leaves the target mapped. commands.c
binds handler context to matched container.pending.workspace; layout.c clears
container targeting when that workspace is Mosaic. This source audit preceded
execution. Native PI_SCENE reports layout enum 1, tile translation (0,0),
clip_valid=0 on both H1 and H2. H1 standard has 226,908 target pixels, local
[402,25,798,598), configured 396×573, with zero target pixels on H2. H1 standard
PNG SHA-256 `195c4faea3020af31819214346772339f62a34c8a82386afb3176ddb9391ee1a`.
The standard click point was recalculated from this image. Actual standard input,
clip removal, layout, ownership and rendered pixels pass together.

### Terminal fixture incident, preserved raw status

The executed runner's final `swaymsg -s PRIVATE exit` returned 1 after all
measurements and `standard-return.json` had been written. It therefore exited
1 and wrote runtime.status=INCONCLUSIVE. Those bytes/statuses are preserved,
not changed to PASS. The compositor log shows Handling command exit, orderly
shutdown and compositor code 0. All three clients exited 0, logging errno 32
(EPIPE) only after the final capture; pointer was owned and terminated -15.
No wl_display.error protocol event or pre-measurement transport failure occurs.

Exact source is compatible with the terminal observation: cmd_exit invokes
sway_terminate(0), which terminates the display event loop; ipc_send_reply queues
its write for a later writable callback. Closing the compositor may remove the
socket before swaymsg reads that reply. This is an observed terminal fixture
incident, not a clipping/input/standard-layout failure. Loss of the queued IPC
response is a compatible explanation, not an independently observed packet
trace or a universal assertion about every exit command. Its exact response error
text was not retained separately because subprocess.check=True raised; the
CalledProcessError, command/code and compositor/client logs remain available.

A separate post-run validator rechecks actual PNGs, IPC/scene, recipient event
lists, focus, clip absence, budget, library identity and cleanup without any
runtime invocation. Negative post-run cases reject abnormal compositor exit,
retained standard clip, invisible-target delivery and even one changed H2 pixel.
Only all measured gates plus this narrow terminal-source/log diagnosis permit
scientific FEASIBLE. The collector and validator are retained under postrun-fixture,
separate from immutable fixture. No new run, workaround or budget refund.

### Budget, damage, integrity and validation

| Resource | Consumed / maximum |
| --- | --- |
| Static runs | 1/1 |
| Pristine runs | 0/0 |
| SceneFX / Mosaic builds | 0/0 each |
| Camera correction | 1/1 |
| Right clicks | 3/3, one per named kind |
| Pointer motions, including click positioning | 6/8 |
| PNGs | 8/12 |
| Duration | 9.142914 / 150 seconds |

Persistent ledger remains consumed. Unused moves/PNGs never authorize another
run. The single runtime `/tmp/msr-26spytfz` is removed; all owned process groups
are reaped and PIDs absent. No private socket remains. Protected system binary,
wlroots/SceneFX libraries, AGENTS/UX/package/patch hashes remain unchanged.
No daily IPC/session/QuickShell/dotfile/Codex change or STEP20D work.

271 TEMPORAL_DAMAGE lines cover setup, transitions and cleanup. Actual clients
request full SHM damage on commits, and stabilized PNGs are consistent. This
is PARTIAL damage evidence: no complete intermediate-frame coverage, native
output-buffer/PNG identity or atomic transaction/input generation is proved.
Popups/grabs, scaling/rotation, resize/migration, extra effects and saved-buffer
scenarios are NOT TESTED in this new campaign. Exhaustive semantic ABI, other
library pairs, notice/legal closure and named release/security roles remain open.

Final source inventory: 31 entries, SHA-256
`cb812ae3a27c9715efce2e1b2cfd36f315ea897d003c77944f688bc931861f1e`.
Final evidence inventory: 93 entries, SHA-256
`209196b2857381db7a856347dcce45cd3ee33c48c2db0c73777fc982d01ad568`.
Both sealed once and every entry verified. Final report/documentation/Git diff
receipts are outside those inventories to avoid circular digests. Repository
README result additions are later documentation, not the executed source copy.

Validation: AST, shell, Markdown links, historical manifests, IPC reference/
preflight replay, 39 negatives, ledger concurrency/exhaustion/corruption, C17
sources/builds, exact binary/loader/maps, actual outputs/camera/clip/pixels/buttons/
focus/splith, protected hashes and residual-process/socket checks PASS. Run
command FAIL at terminal exit IPC only; scientific gates PASS after independent
artifact revalidation. Meson compile/test, ordinary headless suite and pristine
run NOT RUN (outside this ticket and prohibited new builds/runs). Parent source,
contract and final-delta audit performed; no independent subagent review claimed.

### Architectural answers and next bounded gate

| Question | Evidence-backed answer |
| --- | --- |
| Q1 corrected none/width 2? | Yes, accepted in actual historical and live snapshots; mode/deco/content still checked. |
| Q2 other assertions replayed? | Yes for available IPC/scene/COMMIT; pixel selector uses historical PNG; buttons synthetic negatives; live-only states then actually measured. |
| Q3 two whole references identical? | Yes, 480,000 RGB pixels, zero differences and same PNG SHA. |
| Q4 H2 unchanged during Mosaic? | Yes, whole RGB exact. |
| Q5 permitted H1 pixels retained? | Yes, 182,214 actual target pixels. |
| Q6 forbidden H2 pixels absent? | Yes, zero target colors and full reference equality. |
| Q7 visible click correct? | Yes, actual target serials 35/36 only. |
| Q8 invisible portion excluded? | Yes, no new target/filler event on the H2 click. |
| Q9 H2 receives click? | Yes, reference serials 48/49. |
| Q10 focus graphical change? | No H2 change across both actual focus transitions; no claim about all compositor decorations. |
| Q11 splith removes clip? | Yes, actual H1 workspace splith and native H1/H2 clip_valid=0. |
| Q12 standard input? | Yes, recalculated target point, actual serials 67/68 only. |
| Q13 static retains shared-private behavior? | Tested tiled/render/input/standard continuity is supported; exhaustive static/shared equivalence and broader effects/popups are not proved. |
| Q14 algorithm change justified? | No reproduced clipping defect; both incidents belong to fixture checks/terminal handling. |
| Q15 remaining integration limits? | Static popup/grab/effects/buffer continuity, wider geometry/lifecycle, complete damage/generation, exhaustive ABI/maintenance/notices/release ownership. |

Smallest next justified experiment: a separately authorized same-static-binary
root/nested valid-grab popup RGB/input/standard-return continuity gate. Do not
extend this exhausted campaign or integrate clipping in production. STEP20C
remains NEXT and production multi-output NOT YET SUPPORTED. At the start of the evidence-freeze ticket, local main, Forgejo and GitHub
all pointed to fb0293cd855a2ec917c14df3ecf3504c064499fc. This report and the
source-only fixture are frozen for a single evidence-publication commit. The
separate new static nested-grab campaign may start only after that commit is
verified on both remotes with a clean worktree, and remains uncommitted and
unpublished. The historical runtime and three sealed inventories are immutable.
