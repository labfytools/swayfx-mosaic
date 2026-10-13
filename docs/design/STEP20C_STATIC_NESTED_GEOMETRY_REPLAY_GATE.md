# STEP20C static nested geometry replay and offline fixture review

**EXPERIMENTAL / INCONCLUSIVE offline gate. Runtime NOT TESTED.** This protocol is
written before changing the corrected fixture. Phase A published the historical
INCONCLUSIVE failure in commit899c007c37beac03a337ba58ead4326ea8db8878,
verified directly on both remotes with clean worktree. This new phase stays
local, uncommitted and unpublished. **No compositor or graphical client may
be launched, no socket/PNG/input/grab/camera/run reservation created.**
Canonical [architecture](../ARCHITECTURE.md), [UX](../UX.md),
[limitations](../KNOWN_LIMITATIONS.md) and [roadmap](../ROADMAP.md) govern.
STEP20A DONE, STEP20B EXPERIMENTAL, STEP20C NEXT, STEP20D–G PLANNED;
production multi-output NOT YET SUPPORTED, architectural conclusion UNDECIDED.

## Errors and authoritative observations

The [frozen historical failure](STEP20C_STATIC_NESTED_VALID_GRAB_PROBE.md)
retains native SHM420×320, configure636×573, SceneFX destination636×573,
owner applied scene(-320,0,640,600), IPC window_rect(2,0,636,573), effective
25px titlebar and blue paint global[-318,0)×[25,598), PNG local
[482,25,800,598),182214 pixels. Applied scroll160 and global clip
[-800,0)×[0,600) pass. Runner exit1, terminal IPC1, compositor0; zero popup/grab.
Do not alter its LAB, ledgers, manifests or source fixtures. Reproduce and
reject native-height=paint-height and scene.y+window_rect.y=paint.y assumptions.

## Explicit geometry contract

Separate immutable logical structures carry provenance and coordinate-space
tags: NativeSHM (buffer identity, source pixels/format/stride), XDG configure
(role-local coordinates and ACK), AppliedContent (current assignment and
state trace), SceneGlobal (node translation and content/decor/view offsets),
PopupLocal (parent XDG geometry), ViewportGlobal (applied inherited clip),
OutputPNG (origin/scale/transform and RGB paint). Rectangles are half-open.
Conversions reject wrong spaces, origin, ownership, pending-as-applied,
unmeasured scaling/transform, identity mismatches and unchecked bounds.
The future runner and replay use the SAME conversion/validation functions.

Pinned retained source: swayfx-mosaic-static-runtime-hm5kbdkt/{mosaic-source,
scene-source,wlroots-source}. SwayFX output_configure_scene sets tiled buffer
destination from animation_state.current_content_width/height. Transaction
arrangement subtracts borders/titlebar and positions view scene by border_left/
border_top. IPC window_rect describes assigned content with titlebar-dependent
y=0; it is not a scene position or native-buffer size. Applied traces, source
arrangement, natural geometry and captured paint must agree separately. PNG
identity never substitutes for native committed-buffer identity.

Root popup scene wrapper is in root->layers.popup and placed at the applied
view content tree origin; B is beneath A's XDG scene tree. output_configure_scene
inherits closest_con only from container descriptors; globally parented popup
branches do not inherit tiled dest_size resizing. Verify this specific path,
not an assumption that all popup dimensions equal toplevel destination.
SceneFX tree-local clips intersect ancestors for render and hit testing. Root
popup clip is derived from current owning workspace's applied tiling viewport,
converted to root-local, with owner visibility guard. Standard layout clears
root/tiled clips; B's inherited boundary follows its parent. Existing traces
have limited root/owner identity: select only a bounded chain/window and require
unique correlation; ambiguity stops measurement, never arbitrary last-trace use.

## XDG positioner and protocol

Historical client and new placement patch are byte-identical to frozen inputs.
A anchor(100,80),350×170; B anchor(100,60),300×130; 1×1 anchor rectangles inside
parent geometry; anchor TOP_LEFT,gravity BOTTOM_RIGHT, no explicit constraint
adjustment. Pinned wlroots allocates rules with calloc, default flags0; flip,
slide,resize each require matching nonzero bits. Unconstrain is still called
but flags0 do not enable adjustment. Read actual configure/ACK/map each time;
requested coordinates are source-backed predictions, never runtime evidence.
For applied content(-318,25), predicted A[-218,132)×[105,275),
B[-118,182)×[165,295). If either actual popup does not cross, report NOT EXERCISED.
B.parent is A.xdg_surface with grabbing mapped A. Both grabs originate from
separate real left-press serials; WAYLAND_DEBUG independently confirms requests,
bufferless commit/configure/ACK/attach/map and child-first destruction.

## Offline evidence and exhaustive assertion register

Read the historical failed LAB and, if available, the preserved nested LAB
/tmp/swayfx-mosaic-nested-grab-If8ofeUu. Replay at least b_cross, both_cross,
standard return with mapped A/B, and valid-grab dismissal. Read actual XDG
objects/serials/configures/ACK/map, IPC camera/output/layout, root clip logs,
PNG colors/occlusions/intersections and pointer button/local coordinates.
Unavailable evidence must say NOT AVAILABLE / NOT REPLAYED. Future execution
must use versioned sources and discovered IDs, never depend on temporary old LABs.

Automatically enumerate ALL assertions, Defect raises, checked validation calls,
size/geometry/identity/focus/serial/conversion conditions, terminal and cleanup
branches in the four historical modules and corrected proposed runner/model.
Each record contains file/line/function/stage/domain/invariant/source support,
replay possibility, executed positive/negative test IDs, runtime dependency and
retain/correct/replace/remove decision with justification. No unclassified
record. Operational pure-error branches may use labelled synthetic cases;
unexecuted runtime facts remain NOT TESTED. A broad synthetic test label is not
proof that each assertion has been challenged. Coverage is checked against AST
and actual test receipts; source inventory and checker freshness are required.

Required negative cases include both historical errors, wrong output/PNG origin,
assignment, workspace/owner, old camera, local/global clip, buffer identity,
pending-as-applied, scale/transform, missing/invalid serial/parent/ACK/map,
clip/occlusion errors, reused E2 identity, standard stale origin, dismissal
confused with invisible input, and terminal transport with incomplete measures.
Client-only C17 -Werror compile/syntax and generated-protocol checks are allowed;
no execution of graphical clients, compositor or new library build.

## Future ordered runner — prepared only

A future ticket must independently authorize one headless run and its durable
ledger. This ticket creates no execution budget. The runner must refuse without
explicit future authorization/readiness and fresh registered LAB; historical
budget paths cannot be used. Proposed maxima: compositor1, chains2, grabs4,
camera2(one/chain),Mosaic→splith1,clicks9,PNG16,positions24,duration150s.
Client-only preparation can compile fixtures; no Mosaic/SceneFX build.

Discover private sockets, binary/maps, actual outputs, reference ID/PID,
Mosaic owner/workspace/focus and applied geometry before measurement. Establish
H1/focus/camera and two exact full H2 references before grabs. E1 opens A/B with
real buttons, qualifies both actual crossings/colors/root inherited clipping,
visible B input then forbidden B input and normal outside dismissal. Close E1
normally. E2 is new client/IDs/serials; reopen under Mosaic, keep popups mapped
through targeted splith, remeasure owner/content/popups/root clip and H2 colors,
click standard B, explicitly close B, click surviving A, close normally and
require final exact H2. Planned8 clicks/15PNG; fail consumption never refunded.

Native SHM dimensions are correlated to rendered destination and visible
intersection, not required equal. Titlebar/content origin is derived from
applied source arrangement, independently checked by paint. Actual popup
configure and fresh owner origin drive geometry and pointer conversions;
popup painting accounts for occlusion, viewport and output. No blind reuse of
Mosaic origin for splith. No premature exterior click in E2.

Terminal IPC keeps actual stdout/stderr/code. Exception for lost transport
reply is allowed only after all measures, actual handled exit, compositor0,
no protocol/crash/timeout/rescue and all owned processes reaped. Incomplete
measurements remain failure despite clean shutdown. Capture/frame/native-buffer
identity, atomic generation and full damage cannot be established offline.

## Independent review and readiness rules

One independent configured Astra final-reviewer receives contracts, source delta,
assertion inventory and evidence, searches the entire E1/E2/standard/cleanup
path, and writes independent-review.md with ACCEPTED, CORRECTION_REQUIRED and
NOT PROVEN findings. Author addresses every finding and runs bounded correction
validation. No reviewer availability means no ready claim. No broad re-review
loop; one bounded repair chain and delta review if required.

Markers may be PASS only after execution: STATIC_NESTED_SHM_RENDER_GEOMETRY_REPLAY,
STATIC_NESTED_XDG_GEOMETRY_AUDIT, STATIC_NESTED_ASSERTION_COVERAGE,
STATIC_NESTED_OFFLINE_REGRESSIONS, STATIC_NESTED_INDEPENDENT_REVIEW.
All PASS yields SWAYFX_MOSAIC_STATIC_NESTED_GEOMETRY_OFFLINE_GATE=
READY_FOR_NEW_RUNTIME (fixture only, no static popup success). Unresolved
necessary model/fixture evidence gives INCONCLUSIVE; proven structural invalidity
outside allowed fixture correction gives BLOCKED. Architectural conclusion
remains UNDECIDED for STEP20C.

Retain exact sources/source excerpts or hashes, client/protocol provenance,
replay receipts, register/coverage/positive/negative/review/readiness/summary
JSON and once-sealed SHA256 manifests in an offline LAB outside Git. No binary,
PNG/build/socket/large log in Git. Synchronize report/fixture README/canonical
architecture,limitations,roadmap,index,changelog; phase B never committed/pushed.


## Author validation completed before independent review

Offline LAB `/home/fy59/swayfx-mosaic-static-nested-geometry-replay-a56csvoo`.
No runtime ledger, compositor, client execution, socket, PNG capture, pointer,
grab or camera operation. Author's final suite:131 tests PASS in30.588s;
9 actual historical popup cases replayed, three client-only C17 -Werror builds
and generated protocol byte identity PASS. The initial reference syntax attempt
failed because its included saved-client.c dependency had not been copied; copy
the exact versioned dependency, change no C source, and all three checks pass.

The true failed snapshot recovers SHM420×320, configure636×573, assigned rendered
destination636×573, scene(-320,0,640,600), window(2,0,636,573), titlebar25,
origin(-318,25), visible PNG bbox[482,25,800,598),182214 pixels,scroll160,
viewport[-800,0)×[0,600). Initial configure0×0/ACK20/nativeMAP and subsequent
636×573/ACK21/no replacement buffer remain distinct. The two historical errors
are rejected by shared typed functions. PNG/native-frame identity stays NOT PROVEN.

Pinned source audit verifies1397/1397 retained source entries and658/658 old
nested artifacts. Seventeen source contract items have exact copies/hashes,
functions and excerpts in LAB. SceneFX destination and native input bounds are
separate: opening click must fit actual blue paint AND native input region.
Popup-global branches retain their own native/current configured sizes.
Default positioner flags0 disables flip/slide/resize, despite unconstrain calls.
Actual configured geometry still drives measurement; predicted static A/B are
not a runtime result. Root trace selection is restricted to the current chain,
owner origin and observation window; ambiguity is a fixture stop. Standard
origin is freshly computed. Dismissal never substitutes for invisible button.

| Actual historical case | Configured global geometry | Actual sampled RGB/input/lifecycle |
| --- | --- | --- |
| Private b_cross | origin(242,25), A(442,105,300,170), B(662,165,300,130) | grabs55/60; H1 A42200/B17940,H2 zero; visibleB65/66; exterior B→A done/destruction |
| Private both_cross | origin(242,25), A(592,105,350,170), B(752,165,300,130) | grabs55/60; H1 A30080/B6240,H2 zero; separate A/B buttons; exterior dismissal |
| Private toggle | Mosaic origin(242,25)→standard(202,25), A(402,105,300,170), B(622,165,300,130) in standard | same mapped objects, no prior popup_done; H2 B15860; B69/70 delivered |
| Private outside | A(292,105,250,170),B(312,165,170,130) | grabs55/60; outside ordinary client button, B then A popup_done, child-first destroy |
| Control b_cross | origin(202,25),A(402,105,300,170),B(622,165,300,130) | grabs61/66; H2 B15860 and actual B buttons |
| Control both_cross | origin(202,25),A(552,105,350,170),B(712,165,300,130) | grabs61/66; H2 A6120/B27560, actual A/B buttons |
| Control outside | A(252,105,250,170),B(272,165,170,130) | grabs59/64; topmost-first done and destruction |
| Private/control close_b-visible | actual source/log configure and masks replayed | explicit B destruction, A survives and receives right buttons; no erroneous left-click reopening |

Historical standard root clear has source/pixel/input evidence; that old binary
has no explicit clip-clear trace, so direct node-state proof is NOT PROVEN.
Future static runner must use its existing PI_POPUP trace. Old origins without
PI_OWNER are explicitly corroborated from clip + source/IPC + paint/pointer,
not presented as an independently sampled current trace. These replays validate
fixture methods; no new static popup result follows.

Register:2114 sites, including every145 historical assertions;295 sites have
executed positive+negative receipts,568 positive-only and1245 unexecuted sites
explicitly classified. This is NOT2114 runtime facts. Source/AST hashes, exact
line or named-contract receipts reject missing/stale/duplicate/unclassified or
fabricated support. Core pure model/provenance/conversion/authorization/ledger/
pixel guards are tested; runtime-only facts and retired historical code remain
identified separately. Author checker reports0 unresolved pure invariants.
The independent review must assess whether these classifications and coverage
are justified; no independent PASS or READY is claimed before that review.

Corrections cover buffer/destination/titlebar, pending/applied provenance,
output-to-PNG transforms, actual rather than requested popup configures, B
occlusion/output/inherited viewport, native input bounds, root/owner observation
window, new E2 identities/serials, fresh standard generation, lifecycle and
terminal codes. Client placement remains the exact e0e87f… patch. Future runner
requires distinct future authorization and accepted readiness before any debit,
process, runtime or socket creation; current/historical LABs are rejected.
It depends on versioned sources/protocol hashes, not old temporary evidence.

Author markers at this stage: SHM replay PASS, XDG audit PASS offline,
assertion coverage PASS inventory/classification/freshness/core guard scope,
offline regressions PASS; independent review NOT RUN. Readiness INCONCLUSIVE
pending independent review. Architecture UNDECIDED; new runtime NOT TESTED.

## Independent deep review — corrections required

The configured independent final-reviewer (GPT-6-Astra/high, isolated,
read-only) completed one deep audit. Its exact report is retained as
LAB/independent-review.md and its initial structured findings as
results/independent-review-initial.json. The reviewer independently reran131
tests PASS (8.467s, replay writes neutralized), verified all145 historical
assertions among2114 AST sites and the17 pinned contract hashes. This does not
constitute readiness acceptance: three controlled in-memory reproductions
established blocking validator defects.

- R01: callback/injection logs were retained without numerical pairing;
  x=99999 callbacks still passed all9 replays. The dismissal replay supplied an
  empty button list, accepting an injected invisible B press. Correct actual
  phase/geometry/input pairing and pass real relevant buttons, with corruption
  regressions; never modify historical logs or claim unavailable attribution.
- R02: readiness ignored failed rendered/source/coverage evidence and hardcoded
  XDG/coverage PASS. A synthetic accepted review could yield READY with a failed
  SHM marker. Aggregate all effective fresh mandatory gates and independently
  degrade each input in tests of the same production aggregator.
- R03: obtaining IPC code7 and then a compositor wait timeout lost the IPC code
  in the generic exception receipt. Preserve code/streams immediately before
  waiting, append compositor failure separately and retain scientific failure.

The reviewer accepted typed geometry/native input/occlusion, source XDG/scene
contracts, complete inventory within its stated partial execution scope and
future E1/E2/resource order. New runtime/full frame/atomic generation/wider
matrices remain NOT PROVEN/FUTURE_SCOPE, not reasons to run graphics here.
The three blockers require one bounded offline repair chain and a delta review.
No second broad final audit or new graphical campaign is authorized. All
readiness statuses remain INCONCLUSIVE until corrections are verified and
independently accepted. Earlier suite PASS and0 unresolved-core counters are
preserved as their actual results, not promoted to full protocol qualification.

## Bounded offline repairs implemented — acceptance pending

The resolver changed only new replay/write_results/run/predicates/tests/assertions
and fixture README. Initial independent report and initial structured findings
remain byte-identical; final-review-repair.json records root causes, repairs and
actual test outcomes. No historical evidence, production, contract or runtime
budget is modified.

R01 now pairs wire and callback coordinates with action identity/time, real
surface/parent, lifecycle phase and actual configured rectangles, using the
same pointer_local function as future runtime. It handles A's automatic map
retarget, unchanged-position clicks, software motion after layout and fresh
standard origin. Relevant actual forbidden-action buttons reach dismissal;
legitimate earlier visible popup buttons are retained separately. Unidentifiable
old events are labelled NOT AVAILABLE / NOT REPLAYED, never silently promoted.
Corrupted callback/wire coordinates, recipient, extra invisible button and order
are rejected against unmodified archive inputs.

R02 uses one shared aggregator for real results and tests. The repair intended
to require all mandatory geometry/XDG/source/provenance/C17/replay/register/core/
test evidence complete and fresh; the final delta review below proves the
semantic-completeness requirement remains unsatisfied; source_delta/evidence_sha256 bindings must match independent
acceptance. Missing/failed/stale inputs or stale acceptance block readiness.
All marker values are exact PASS/INCONCLUSIVE with separate marker_scope.
Synthetic accepted review in negative/positive tests is memory-only; real
initial review remains CORRECTION_REQUIRED.

R03 uses terminal_exchange in runner and mocks: IPC code/stdout/stderr are stored
before compositor wait. IPC7 then TimeoutExpired retains7 and streams plus a
separate compositor error; scientific result remains false. No obtained code on
invocation error stays explicit null. IPC1 may be separately qualified only
with completed measures, handled clean compositor0 and no crash/protocol/rescue.

Author repair validation:195 tests PASS,32.276s; nine historical replays PASS;
register2288 sites including145 historical assertions,361 positive+negative,
676 positive-only,6 negative-only,1245 unexecuted, core PASS. These are execution
receipts for their limited offline scope, not2288 graphical observations.
A first expanded suite failed because its synthetic positive aggregation
snapshot read stale receipts during editing; snapshot isolation was corrected
and final tests pass. Compilation dependency and AST-key preparation incidents
are likewise preserved. An independent tester and bounded reviewer must still
verify this final delta before READY; no second broad deep audit is performed.


## Final bounded review and disposition — INCONCLUSIVE

Independent tester (GPT-6-Luna/low, isolated) reran the actual offline sequence:
replay,195 tests with0 failures,register generation,register --check,writer.
All commands exit0. AST14 Python files, README shell syntax, diff check,
310 protected paths, immutable24/30/96 historical manifest entries and original
review hashes pass. No new PNG/socket/runtime budget exists.

Independent delta reviewer (GPT-6.1-Sol/medium, isolated, read-only) examined
R01–R03, ran65 targeted tests PASS (4.299s), replayed9 cases with writes disabled
and verified17 source/15 proof bindings. R01 and R03 are RESOLVED. **R02 remains
CORRECTION_REQUIRED / BLOCKING for readiness**, not a demonstrated compositor
or architectural defect. LAB/bounded-review.md and results/bounded-review.json
retain the finding; original Astra report/JSON remain immutable. The parent
independently reproduced all three principal counterexamples with the actual
aggregate and in-memory snapshots, results/parent-R02-reproduction.json:

| Effective mandatory evidence removed | Actual wrong synthetic decision |
| --- | --- |
| Historical input correlation reduced to a bare PASS label | READY, no blocker |
| Rendered content/bbox/count/intersection set to null | READY, no blocker |
| Root popup records replaced by nine empty objects | READY, no blocker |

The reviewer additionally removed protocol/configured/button/callback/injection
and available standard/close/dismissal facts in b_cross,toggle,close_b cases;
all still produced synthetic READY. No acceptance was signed or persisted.
The true LAB remains INCONCLUSIVE because its review is not ACCEPTED.
The existing writer's four technical PASS labels are retained as **raw calculated
results with limited scope**. Their ability to certify complete proof is not
accepted. Counting an AST site or passing195 existing tests cannot override
these executed negative counterexamples.

| Final assessed gate | Result and scope |
| --- | --- |
| STATIC_NESTED_SHM_RENDER_GEOMETRY_REPLAY | PASS — true snapshot/PNG/SHM/destination replay |
| STATIC_NESTED_XDG_GEOMETRY_AUDIT | PASS — pinned source and sampled historical protocol/geometry only |
| STATIC_NESTED_ASSERTION_COVERAGE | PASS — current exhaustive inventory/classification/freshness; partial executed semantic coverage |
| STATIC_NESTED_OFFLINE_REGRESSIONS | INCONCLUSIVE —195 existing tests PASS, semantic deletion/null counterexamples expose an uncovered validator defect |
| STATIC_NESTED_INDEPENDENT_REVIEW | INCONCLUSIVE — CORRECTION_REQUIRED, no acceptance |

`SWAYFX_MOSAIC_STATIC_NESTED_GEOMETRY_OFFLINE_GATE=INCONCLUSIVE`.
Architecture UNDECIDED; no new static popup is qualified. All historical static
popup/grab/input/standard cells remain NOT TESTED. Runtime runner is prepared
but unexecuted and **NOT READY**. Its authorization guard refuses this ticket,
current/historical LABs and unaccepted readiness. No runtime ledger is created.

The single deep final review and its bounded repair/delta review chain are
complete. A material readiness defect survives that chain. Stop repair here,
retain the failure, and request a separately scoped **offline-only** follow-up
for aggregate's effective receipt-content validation and shared-function negative
regressions. This is smaller than any graphical gate. Only after an independently
accepted offline gate could a later distinct ticket authorize one run; nothing
in this report authorizes execution or makes a reservation.

## Required geometry and protocol answers

1. SHM420×320 remains the client's native submission. SwayFX configures636×573
   from the tiled content assignment and SceneFX dest_size scales rendering;
   the client ACKs but does not replace its original buffer. Native input bounds
   are distinct from destination rendering.
2. Applied owner scene(-320,0), left border2 and effective top titlebar25 place
   content at(-318,25). IPC window_rect.y=0 alone omits that translation.
3. IPC window_rect/content assignment derives from pending fields; natural
   geometry describes native XDG size. Applied PI_OWNER/PI_MOSAIC traces, snapshot
   timing and paint correlate actual state; do not label pending rects applied.
4. Translate content/root/global scene explicitly, intersect global viewport
   and output, then subtract output origin(-800,0) at measured scale1/normal.
   Global(-318,25) becomes PNG(482,25); clipped right edge0 becomes PNG800.
5. Both erroneous assumptions are reproduced and rejected in shared model
   negatives using true geometry. The additional aggregator defect is also
   reproduced; it is not a geometry failure.
6. All145 historical asserts and current runner/helper sites are inventoried:
   2288 sites,361 positive+negative,676 positive-only,6 negative-only,1245
   unexecuted explicitly classified. Inventory is not complete branch proof.
7. New applied output/focus/owner/camera/buffer/clip/actual popup configure/map/
   crossing/input/dismissal/standard/cleanup and exact rendering remain runtime
   observations. Native frame identity and atomic generation are NOT PROVEN.
8. Pinned calloc default constraint flags0 disables flip/slide/resize adjustment
   in this client despite popup_unconstrain. Parent geometry and actual configure
   must still be measured; different flags/geometry would change the contract.
9. Predicted A[-218,132)×[105,275),B[-118,182)×[165,295) cross0 for the last
   content origin(-318,25). These are predictions, not static popup measurements.
10. Actual xdg_popup.configure,xdg_surface.configure/ACK/map,applied owner/root/
    child scene positions and capture masks must establish both real crossings.
    Missing crossing is NOT EXERCISED, never clipping PASS.
11. Root selection uses owner,chain and bounded observation window; ambiguous
    roots stop. No arbitrary last trace. Historical indirect origin evidence is
    identified; future direct PI_POPUP state must correlate the current owner.
12. Private root wrapper is globally parented; B is under A.xdg_surface_tree.
    SceneFX ancestor clip traversal covers render and hit. This is source and
    historical evidence, not new static applied-child measurement.
13. Shared RGB comparators intersect output and inherited viewport, subtract
    B's occlusion from A, use actual configured rectangles and lifecycle.
14. Standard transition remeasures owner/content/root and recomputes A/B from
    fresh origin; it never reuses Mosaic origin. Historical standard B local
    (278,25) at global(900,190) is replayed.
15. Actual wl_pointer.button callbacks and WAYLAND_DEBUG requests bind distinct
    press serials to each grab; synthetic tests have explicit labels. Runtime
    errors/unaccepted grabs cannot be inferred away by source inspection.
16. Shared terminal_exchange preserves obtained IPC code/streams before wait;
    scientific completeness, handled exit, compositor0 and protocol/cleanup gates
    separately determine transport qualification. IPC7+timeout remains failed.
17. Independent review does not accept readiness: R02 survives. R01/R03 are
    accepted repairs; initial accepted geometry/source scope remains unchanged.
18. Fixture is NOT READY for a new run. Smallest next gate is offline receipt
    semantic completeness, not another compositor reservation.

## Final scope and retained evidence

Phase A was committed/pushed to both remotes at899c007c37beac03a337ba58ead4326ea8db8878
with a clean gate worktree. Phase B remains local, unstaged, uncommitted and
unpublished: report,17 source-only fixture files and five synchronized docs.
LAB results include all requested geometry/model/register/replay/test/review/
readiness/summary JSON, exact clients/protocols/private placement patch, source
contract copies, offline command receipts and review reports. New source and
evidence manifests are sealed once after finalization, with separate seal
receipt; historical manifests and ledgers remain immutable.

New runs/pristine runs/Mosaic builds/SceneFX builds/captures/pointer actions/grabs/
camera operations/installations/runtime reservations: **all0**. Client C17 builds
only, never executed. Static binary and310 protected source/system paths remain
unchanged. No production/patch/PKGBUILD/AGENTS/UX/PACKAGING/system/desktop IPC/
QuickShell/dotfiles/Codex/STEP20D operation. No experimental process/socket was
created by phase B. STEP20A DONE,STEP20B EXPERIMENTAL,STEP20C NEXT,STEP20D–G
PLANNED; production multi-output NOT YET SUPPORTED.

## Historical offline evidence freeze — 2026-10-13

This report and source fixture are preserved for publication by ticket
`SWAYFX_MOSAIC_STEP20C_NESTED_OFFLINE_FREEZE_AND_RECEIPT_INTEGRITY_V1`,
phase A. Statements about a local/unpublished phase above describe the prior
campaign, not the publication state of this historical freeze. No historical
receipt, review, manifest or fixture source was rewritten.

All 67 source and 88 evidence entries were verified individually against the
sealed manifests in `/home/fy59/swayfx-mosaic-static-nested-geometry-replay-a56csvoo/`.
Their SHA-256 values are respectively
`e1230ba1292f12d913b762f0678e638a2effb513b74eb44dd232c12aa4acea1d` and
`22b9ac035da95ba914c28d72d8aa6f019c16c2854095d81ceb62c0bd10da8dbe`.
The preserved writer SHA-256 is
`94ddab595dd9765d3edaa7158a6a98319f3be6b15a62842e4b10eeacfb530cfa`.
R01/R03 remain RESOLVED; R02 remains NOT_RESOLVED / CORRECTION_REQUIRED.
The three in-memory counterexamples in `results/parent-R02-reproduction.json`
are evidence of a validator defect, never compositor operation.

`SWAYFX_MOSAIC_STATIC_NESTED_GEOMETRY_OFFLINE_GATE=INCONCLUSIVE`.
Architecture UNDECIDED. The 195 passing historical tests and 65 passing
independent targeted tests do not detect these semantic omissions. New static
popup runtime, serials, pixels, clicks, dismissal, standard return, atomic
generation and complete GPU-reference qualification remain NOT TESTED.
This freeze runs only static checks: no builds, graphical execution, runtime
budget or reservation. A separate local phase may repair R02; it cannot
retroactively change this historical verdict.
