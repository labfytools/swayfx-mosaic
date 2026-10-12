# STEP20C fractional scaling and viewport probe

**Status: EXPERIMENTAL / PARTIALLY_FEASIBLE for the sampled static matrix.**
Source-only evidence preserved for the fractional freeze. STEP20A DONE, STEP20B EXPERIMENTAL, STEP20C NEXT,
STEP20D–G PLANNED; production multi-output NOT YET SUPPORTED. No UX contract
or production change is authorized. The temporal headless line stays closed
at INCONCLUSIVE; no additional transaction contract is introduced.

## Scientific question and historical baseline

Scale-1 private inherited clips excluded sampled tiled/popups pixels and hits
at negative origin. The effects report demonstrates neighboring shadow
exclusion and visible blur, but no permitted interior Mosaic shadow,
optimized-cache invalidation, saved-buffer or every-frame qualification.
Fractional conversion can expose rounding, missing boundary pixels, wrong
output damage or disagreement with logical hit testing. These are hypotheses,
not established defects. Instrumentation is passive; no algorithm, shader,
damage decision, callback order, transaction or public ABI may be changed.

## Requested geometry and acceptance gate

| Geometry | HEADLESS-1 mode/scale/origin | HEADLESS-2 mode/scale/origin |
| --- | --- | --- |
| G0 | 800×600 / 1 / (-800,0) | 800×600 / 1 / (0,0) |
| G1 | 1000×750 / 1.25 / (-800,0) | 1000×750 / 1.25 / (0,0) |
| G2 | 1000×750 / 1.25 / (-800,0) | 800×600 / 1 / (0,0) |
| G3 optional | 1200×900 / 1.5 / (-800,0) | 800×600 / 1 / (0,0) |

Expected logical rectangles are 800×600. Record actual active/name, global
rect, current physical mode, scale and transform from get_outputs, plus real
PNG dimensions. Rejected/normalized geometry is INCONCLUSIVE, not PASS or
BLOCKED. G3 is allowed only after G1/G2 calibration succeeds. G0 is a small
calibration control, not a new historical campaign.

## Coordinate contracts to audit before adapting the fixture

Global Wayland, Mosaic geometry, camera scroll and virtual-pointer points are
logical. Output-local logical = global minus output origin exactly once.
SceneFX scales logical boxes/regions into output-buffer physical coordinates;
transform is normal in this matrix. Audit actual floor/ceil/round rules,
pixman intersections, fractional conservative expansion, texture filtering,
source/destination boxes and damage conversions. Do not use arbitrary integer
truncation as the expected physical clipping rule. Never multiply scroll_x
by scale. At expected geometry, pointer injection remains sent_x=global_x+800
with logical extent 1600×600. Verify enter/motion coordinates and left/right
buttons on both outputs before scoring clipping/input.

Captures must record their real dimensions and applied output scale/origin,
logical and physical resolutions, timestamps and hashes. Predeclare logical
ROIs: left interior (300,100,700,500), left boundary (720,50,800,550), right
boundary (0,50,80,550), reference (250,250,550,500). Physical ROIs conservatively
cover floor(lower*scale)..ceil(upper*scale); retain full-image differences.
Boundary bands and adjacent columns are never removed after anomalies.
Compare equivalent logical regions, not historical pixel counts.

## Comparisons, scenarios and finite budget

Each qualified geometry compares ordinary SwayFX splith, private splith and
private Mosaic with identical deterministic clients. Controls must demonstrate
actual overflow before a clipping claim. Reuse preserved valid-anchor nested
SHM client, opaque client, deterministic background, reference and virtual
pointer. C adaptations, if needed, are private patches with pinned base/hash.

S0: IPC/mode/PNG/scene/pointer calibration gates all later input claims.
S1: inspect owner/tiled boundary pixels and logical hits.
S2: map TOPLEVEL→POPUP_A→POPUP_B using genuine button serials; retain
configure/ack/map, parent identities and anchor validity; compare visible
and clipped hits. Exterior clicks which dismiss the chain need separate runs.
S3: predeclared grid around x=0 and complete physical boundary bands.
S4: FX0/FX1/FX2, visible control shadow and filtered blur; distinguish draw
clip from sampling and cache semantics. Interior shadow remains unqualified
unless new pixels demonstrate it.
S5: one 400→1280→400 pair per G1/G2 Mosaic run with A/B mapped; no hidden
click, preserve objects and test returned hits.
S6: observed same-output damage extents compared to settled changed pixels,
with explicit physical coordinate provenance and fractional expansion.
S7: layout splith with objects open, clear clips and preserve ordinary hits.

**Global B budget: two pairs total, across all attempts and geometries.**
Reserve before launching under a campaign lock; failure consumes reservation.
G0/G3 and all standards use zero pairs. One persistent campaign ledger belongs
to the single new lab, never reset or bypass through another clone. Untestable
variants remain NOT TESTED. Preserve every attempted run and real exit code.

## Criteria and limits

FEASIBLE requires applied geometry, calibrated logical input and physical
captures, actual control overflow, excluded sampled forbidden pixels/hits,
correct visible interactions, active effects and observed restoration/damage.
PARTIALLY_FEASIBLE leaves effects/rounding/transitions/damage partly qualified.
INCONCLUSIVE means geometry/control/fixture cannot establish conversions.
BLOCKED requires reproducible forbidden pixels/hits, scene corruption or
blocking regression; preserve a minimal reproducer and do not repair algorithm.

Rotation, migration/resize/hotplug, full animations, all optimized caches,
saved buffers, other renderers and production ABI/package are NOT TESTED.
Sources/fixtures are local in tooling/probes/step20c-fractional-scale;
all builds, logs, PNGs, generated protocols, sockets and manifests stay outside
Git. Final analysis must answer Q1–Q11 with these evidence limits.

## Source audit before fixture adaptation

Pinned Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754`, SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc`; locally retained wlroots source
describes exactly tag 0.20.2 (the installed linked version also reports 0.20.2).
Sway output configuration sets round(scale*120)/120 after the physical mode;
1.25 and 1.5 are exactly representable protocol steps. output_update_position
copies the logical layout box. wlroots effective_resolution divides transformed
physical integer dimensions by scale with integer assignment; these test modes
yield exactly 800×600 without fractional logical extent.

SceneFX scale_box rounds both edges with round(), computing width from the
rounded far edge minus rounded origin. wlr_region_scale uses floor lower / ceil
upper. scale_region(...,true) additionally expands by one physical pixel for
fractional scales. scene_damage_outputs subtracts scene-output logical origin,
scales/expands and transforms, then scene_output_damage clips to physical
output dimensions. TEMPORAL_DAMAGE is emitted there: **already physical
buffer-local extents**, never multiply those traces by scale again.
Opaque background culling also expands one pixel at fractional scale and
reintersects damage. Buffer damage may expand for linear filtering; ordinary
buffer filter mode and bilinear blur sampling differ. Draw clips pass through
logical_to_buffer_coords; texture boxes and pixman regions need not share
identical integer bounds. An integral boundary x=0 does not exercise every
possible fractional edge offset.

The private inherited clip intersects ancestor logical rectangles; popup clips
are converted from the applied global viewport into root-popup local coordinates.
node_at uses floor(global point) for its logical query and checks inherited
point_inside_clip before surface input. Shadows/blur nodes do not accept input.
wlr_cursor_absolute_to_layout_coords uses mapping.width*normalized_x+mapping.x,
with the combined output-layout box if no explicit device mapping. The private
pointer normalizes sent integers by logical extent, so +800 is origin removal,
not physical scaling. No pointer C adaptation is needed for these 800×600
logical outputs. The runner must empirically verify both clients' local points.

## Retained fixture incidents

First G0 calibration attempt (zero camera pairs) placed the left ordinary
floating reference at x=-1550: `move position -750 300` was output-relative,
adding the -800 output origin. The bounds check rejected injection before
input scoring. The fixture now uses `move absolute position -750 300` and
continues to derive points from actual IPC content coordinates. This is a
fixture command error, not a Mosaic scaling defect. The failed run is retained.

The next zero-pair standard calibration attempts retained a 25-logical-pixel
vertical discrepancy between the floating reference's IPC-derived point and
its client-local enter/motion. The intended local (60,50) was reported (60,75).
Mosaic's same calibration passed, so no scale-specific defect is inferred.
To avoid assigning frame-decoration geometry to the test surface, both ordinary
references now explicitly use `border none`; local coordinates are still checked
against the client log, not accepted from IPC alone. All failed runs remain in
the lab manifest. This fixture change is documented before further experiments.

The ordinary control is now also rebuilt from pristine pinned SwayFX 0.6,
`fd71a6bdc061bd633b488ae7b83e8a6981d22f86`, in standard-build and uses the
installed unmodified SceneFX. Preliminary installed-Sway calibrations remain
retained attempts, not the final comparative standard control.

Border none alone did not remove the standard reference's stale IPC frame
geometry (rect y=325 while surface origin is y=300). Final calibration uses
explicit absolute placement origins (-750,300) and (250,250), then requires
client enter=(20,30), motion=(60,50), and both button deliveries. IPC frame
and window geometry are recorded separately. This checks known placement
against real client surface coordinates; the IPC decoration discrepancy is
retained rather than treated as the surface-coordinate authority.

The stricter nominal-placement calibration then failed in Mosaic, where the
surface retained a different vertical placement from standard. Final S0
therefore distinguishes requested placement from measured surface origin:
first enter determines the actual surface origin, a second independent global
move of (+40,+20) must produce the identical logical local delta, and both
buttons must arrive. Initial x=20 and an interior y are asserted. Record both
origins and the IPC frame separately. This is an empirical coordinate
calibration, not a promise that a pending move command defines applied geometry.
No clipping/input scenario is scored before this two-point calibration passes.

The b_cross main runs succeeded in G1/G2, including one camera pair per
Mosaic run with A/B mapped. Their visible references and returns are identical
on both outputs. To distinguish root from nested boundary coverage, add a
zero-camera `both_cross` comparison in each of the three modes for G1/G2,
with the retained client's valid anchors A=(350,80) in TOPLEVEL 420×320 and
B=(160,60) in A 350×170. Exterior clicks stay in these distinct runs. This
uses an existing client variant, not a C or clipping algorithm adaptation.

Add two final zero-camera root-input controls: in both_cross Mosaic G1/G2,
click (20,140), the forbidden root-A portion above B's top edge. Keep them
separate from the (20,190) nested-B dismissal controls. The existing standard
runs already prove real root-A delivery at their configured visible points.
Do not spend another camera pair to qualify restored Mosaic hit testing:
the two existing S5 runs captured visual restoration, but did not inject a
new visible B button before switching to standard layout. That assertion
remains NOT TESTED under the exhausted budget.

## SWAYFX_MOSAIC_STEP20C_EFFECTS_FREEZE_AND_FRACTIONAL_SCALING_PROBE_V1

### Phase A freeze gate

Initial main/local remote references were `542d9b9c945b22cf9134a4a643c8dc763b34607d`,
with only the expected effects fixture/report and five documentation files dirty.
The historical 890-entry evidence and 29-entry source manifests verified at
`5fbe12b0312f2d82b3c5414251ae57345db8d25a83cfc018947308d40e752b42` and
`8fbd0cf927e3e2690a77aeaf2288072c183ef1dbe8f856cb63e0442454614d95`.
Historical client/trace patches retain their announced hashes, including the
separate compiled trace provenance. The report preserves 15 historical camera
pairs against a maximum of three; default repetition across five Mosaic runs
caused the excess. Selecting three pairs does not authorize the other twelve.

A fresh independent clone rebuilt the private chain; the new three-control
replay consumed one pair total and reproduced 27,594 standard shadow-spill
pixels / zero Mosaic, real filtered blur and one exact settled camera return.
New evidence/source hashes are listed in the effects report. The reservation
block passed locking, failure/interruption, exhaustion, zero-pair and retained-run
checks. Historical reference geometry differed (640×480 untraced versus 300×250
traced); missing checker causality and logging neutrality remain unqualified.
Interior shadow, optimized caches, source sampling, popups, saved buffers and
intermediate frames remain limited as documented.

The unique authorized commit is
`aefee44c636a1529eca9a082658fd80b4d17cf5f`, title
`docs(mosaic): preserve SceneFX effects and damage probe evidence`.
Normal pushes to origin/main and github/main succeeded; direct ls-remote checks
returned that SHA for both. Worktree was clean at the A→B gate.

Validation qualification: ordinary `git diff --check` passed before adding new
files, but `git diff --cached --check` flagged historical trace-patch **context**
lines (space+tab and the blank context marker). Those bytes are valid unified
patch syntax and belong to the mandated preserved SHA; they were not rewritten.
The commit/push proceeded with this explicitly classified patch-format exception.
Builds, controlled patch application, C17, model 1/1 and link checks passed.
Do not describe the unfiltered indexed whitespace check as PASS.

`SWAYFX_MOSAIC_EFFECTS_DAMAGE_FREEZE=PASS`

### Phase B laboratory and actual geometry

Independent full clone `/tmp/step20c-fractional-v1-clone` at the A commit;
private lab `/tmp/swayfx-mosaic-nested-grab-0DfvGCxn`. Private SceneFX/Mosaic
were rebuilt from the pinned preparer chain, with the historical clip, hidden
owner guard, damage and passive presentation patches. No algorithm changed.
Pristine upstream SwayFX 0.6 was separately archived and built in standard-build;
final ordinary controls use it, linked to installed unmodified SceneFX. Private
controls link only their process to the private library. wlroots 0.20.2 source
HEAD `d783533489e1f75d6886c2ab5c5960090ef268f8` is clean at tag 0.20.2.

| Geometry | Actual H1 mode / scale / logical rect | Actual H2 mode / scale / logical rect | Scope |
| --- | --- | --- | --- |
| G0 | 800×600 / 1 / (-800,0,800,600) | 800×600 / 1 / (0,0,800,600) | Small calibration only |
| G1 | 1000×750 / 1.25 / (-800,0,800,600) | 1000×750 / 1.25 / (0,0,800,600) | Three modes, b_cross + both_cross |
| G2 | 1000×750 / 1.25 / (-800,0,800,600) | 800×600 / 1 / (0,0,800,600) | Three modes, b_cross + both_cross |
| G3 | 1200×900 / 1.5 / (-800,0,800,600) | 800×600 / 1 / (0,0,800,600) | Optional three-mode b_cross, no camera |

All active, normal transform, physical modes and scales actually accepted;
PNGs match each target output's physical mode. All logical viewports remain
800×600. No requested geometry is mislabeled from a command's success alone.
SceneFX FX reports GLES 3.2 Mesa 26.2.4-arch1.1 / Radeon 780M radeonsi.

### Calibration, geometry and input

Qualified final runs pass ordinary-reference enter on each output, independent
(+40,+20) local motion, both buttons, crossing and return. Signed normalization
is sent_x=global_x+800, extent 1600×600; physical scales never enter injection.
Requested reference placement, actual measured surface origin, IPC frame and
surface-local coordinates are recorded separately. Earlier placement, frame-offset
and already-entered-pointer assumptions caused ten retained calibration failures,
all with zero reserved camera pairs. One additional calibration adapter attempt
had an escaped regular-expression defect; its failed log is among those ten.
No failed calibration is counted as clipping evidence. A forced move outside
before enter removes the already-entered-pointer ambiguity.

Both XDG grabs use actual received left-button serials unchanged; parent identities,
configure/ack/map and logs are retained. All observed grabs validate. b_cross
anchors A=(200,80) in TOPLEVEL 420×320 and B=(220,60) in A 300×170 are valid;
both_cross anchors are also inside their actual parent geometry. No invalid-anchor
campaign is reused. Visible B right buttons arrive in each main run, including
after standard-layout return; there is no popup_done in those main runs.

For b_cross Mosaic, B's applied configured global box is (-138,165,300,130).
On H1 at 1.25, local x=662 maps to rounded destination x=828; the visible
physical box ends at x=1000, y=206..369. Its 172×163 exact-color pixels fill
that retained rectangle. At 1.5, the corresponding box starts x=993 and ends
at x=1200, y=248..443 (195 rows). Conservative region floor/ceil and extra
physical expansion differ from rounded destination edges; those differences
are not automatically classified as leaks.

The both_cross grid records B motion x=46/47,y=25 at global x=-2/-1,y=190,
then B leave at x=0, with no new popup events at x=1,2,20. Separate right clicks
at (20,190) produce no popup button under Mosaic and dismiss both grabs.
Separate root-A clicks at (20,140), above B, likewise produce no popup button
and dismiss the chain in G1/G2 Mosaic. This is grab dismissal, not universal
click-through. The b_cross standard controls actually receive a popup button at
(20,190), without dismissal. The both_cross standard (20,190) point is outside
its differently placed popup; its dismissal is ordinary behavior, not a clip
comparison. Their configured visible A/B points still demonstrate real hits.

### Pixels, effects and rounding

| Geometry/mode | FX1 changed H2 pixels | FX2 changed H1 pixels | FX2 changed H2 pixels |
| --- | ---: | ---: | ---: |
| G1 ordinary / private splith | 43,500 each, columns 0–57 | 175,665 each | 0 |
| G1 Mosaic | 0 | 499,749 | 0 |
| G2 ordinary / private splith | 27,594 each, columns 0–45 | 175,665 each | 0 |
| G2 Mosaic | 0 | 499,749 | 0 |
| G3 ordinary / private splith | 27,594 each, columns 0–45 | 252,546 each | 0 |
| G3 Mosaic | 0 | 718,983 | 0 |

In the predeclared Mosaic interior ROI at 1.25, luminance deviation falls
51.499588→0.782573 and adjacent contrast 13.004008→0.747014. At 1.5 they fall
51.498856→0.711986 and 12.896494→0.689552. Standard 1.25 ROI contrast falls
3.350701→0.316020 (the ROI also contains non-owner pixels). The visible image
and quantitative smoothing establish filtering beyond fixed alpha compositing.
FX1 changes zero left Mosaic pixels: authorized interior shadow is still
INCONCLUSIVE, not PASS. Optimized cache and outside-only sampling remain NOT TESTED.

Main b_cross standard right images gain 127,200 popup pixels in G1 and
81,200 in G2/G3; private standards agree. Mosaic gains **zero pixels anywhere
on H2** versus its effects-off reference, not just zero exact popup colors.
both_cross standard right differences are 121,575 in G1 and 77,600 in G2;
Mosaic is again unchanged. Both root and nested permitted pixels remain visible.

Complete last four H1 columns retain B counts 163 per column at 1.25, 195 at
1.5. both_cross additionally retains 75 A pixels per last column at 1.25 above
B. First four H2 columns contain no A/B pixels under Mosaic. All predeclared
boundary ROIs and whole neighboring images remain in analysis; no anomalous
border is discarded. No forbidden antialias/filter contribution is observed.
This establishes sampled edge retention, not a universal absence of lost visible
pixels for every fractional subpixel phase.

The named historical capture `S1-opaque-reference` is actually an effects-off
reference with the ARGB owner; it is not proof of an opaque tiled spill.
Future source fixture uses `S1-effects-off-reference`; the analyzer preserves
compatibility with the old filenames. The opaque kitty is present, but the
standard tiled content itself does not demonstrate a crossing visual rectangle.
S1's independent opaque tiled-overflow prerequisite is **INCONCLUSIVE**; shadow
and popup overflow must not be substituted for that specific assertion.

### Camera, damage and standard return

Exactly two pairs ran: one in G1 Mosaic, one in G2 Mosaic, all successful.
Ledger reservations=2, completed pair events=2. All other attempts reserve zero.
No later run resets/bypasses the ledger. A third requested pair is refused with
exit 2 before creating a run. Offline real-reservation tests pass lock,
interruption, launch failure, exhaustion, zero and missing-ledger rejection.

Each main hidden state contains zero exact A/B pixels on both outputs, with a
recorded empty owner intersection and root hidden guard. Objects stay mapped,
no popup_done occurs during no-click hiding, and return PNGs exactly match the
pre-hide chain reference on both outputs. The return's Mosaic hit/button before
switching layouts is **NOT TESTED**; the budget is not increased to repair that
omission. S7 subsequently clears clips, restores standard geometry, preserves
A/B and delivers a second B right button without unexpected dismissal.

Main private damage events: G1 standard 981 / Mosaic 936; G2 924 / 818;
G3 918 / 761. Available physical buffer-local extents cover every changed pixel
between the analyzed settled capture windows; no uncovered changed pixel is
measured. Ordinary controls have no native damage instrumentation. Extents
can be broad; fractional expansions are source-audited but their minimum extent
and every intermediate frame are not qualified. Native commit/present logs are
retained as passive context, not a reopened temporal campaign or atomic input
identity proof.

### Reproducibility, validation and remaining limits

42 attempted runs / 32 without fixture failure / 10 failed early calibrations;
680 PNGs. All retained in the complete manifest, including excluded attempts.
Early reusable generated calibration filenames were overwritten; exact generated
source for every failed early attempt is not available. Their logs/configs/PNGs
and documented defects remain. Final attempts save unique generated source and
per-run source copies; main sources are retained. This provenance limitation is
explicit and does not make the final reproducer depend on a historical lab.

Evidence manifest (1,986 entries) and separate source manifest (39 entries)
verify; exact final hashes are recorded below after final synchronization.
The manifests include the final analysis, metadata, budget, retained run artifacts,
private source inputs and fixture sources. Builds/binaries/logs/images/manifests
remain outside Git. Final fixture contains prepare.sh, run.py, analyze.py,
test-budget.py and README.md; no new C adaptation or algorithmic patch was added.

Shell syntax, Python AST including generated runners, standalone C17 clients
with warnings as errors, pinned controlled patch application, fresh private
SceneFX/Mosaic and pristine-standard builds, model 1/1, actual scale/PNG checks,
pointer calibration, grabs, clip traces, pixel/damage analysis and manifest
verification pass. Final production paths, historical patches, cumulative patch,
PKGBUILD and UX are unchanged against initial HEAD. Each runtime is removed;
no lab process or private socket remains. No installation, live IPC, daily-session
operation or STEP20D work was performed. Phase B remains uncommitted/unpublished.

Remaining NOT TESTED or limited: rotation, resize/migration/hotplug, full animations,
all optimized caches, saved buffers, other renderers, source-sampling influence,
intermediate frames, all subpixel edge phases and production ABI/package. No new
reproducible clipping leak or scene corruption was demonstrated.

### Architectural answers

| Question | Evidence-backed answer |
| --- | --- |
| Q1 viewport coherence | Yes in sampled applied static G1/G2/G3: 800×600 logical viewport, independent physical scaling, camera remains logical. |
| Q2 forbidden rounding pixels | None observed in whole H2 popup/effect comparisons and retained boundary bands. |
| Q3 missing visible pixels | None in sampled final columns/known popup boxes; all fractional phases and opaque tiled boundary are not qualified. |
| Q4 hit/render agreement | Yes at calibrated points and x=-2,-1,0,1,2,20 grid; no same-frame atomic identity claim. |
| Q5 nested XDG clipping | Root and child both_cross/b_cross clips exclude sampled H2 pixels and forbidden buttons while preserving visible interactions. |
| Q6 true grabs | Both real serials unchanged, configure/ack/map and visible buttons succeed; outside dismissal remains normal. |
| Q7 shadow/blur | Shadow-spill exclusion and real blur persist; interior shadow/cache/sampling limits persist. |
| Q8 uniform versus mixed | No clipping/input divergence found; physical counts differ as expected with each output's scale. |
| Q9 damage conversion | Source-audited physical extents cover settled measured changes; no minimal/every-frame proof. |
| Q10 redesign required | No reproduced defect here forces a private algorithm change; production gates remain open. |
| Q11 next gate | Resize/migration: these results use fixed logical boxes, while the calibration exposed frame/applied-placement distinctions; verify owner/output/clip updates as geometry actually changes. Rotation, saved buffers and ABI/package remain separate subsequent gates. |

`SWAYFX_MOSAIC_FRACTIONAL_SCALING_PROBE=PARTIALLY_FEASIBLE`

Overall architectural conclusion: **UNDECIDED**. Observed static fractional
clip behavior is viable, but S1 prerequisite, interior shadow and restored
Mosaic hit are insufficient for complete requested-matrix qualification.
No production qualification or new transaction/UX contract follows.

`SWAYFX_MOSAIC_STEP20C_EFFECTS_FREEZE_AND_FRACTIONAL_SCALING_PROBE_V1=PARTIALLY_FEASIBLE`

Final source manifest SHA-256 (39 entries): `a553a1106297ae21819a6f00ffea681cba88996135e28feea393b1b37a1f1c5d`.

Final evidence manifest SHA-256 (1,986 entries): `b47ddab0be8f60b1fd43576fcdc2ca0dbcc5fee19b4c8faf343b648c3ed36fdd`.
Both verified entry by entry after final fixture synchronization. The final
ordinary/private standard FX0/FX1/FX2/popup PNGs are pixel-identical in G1/G2/G3.

## Fractional evidence freeze — 2026-10-12

The initial main/local origin/main/github/main references all matched
`aefee44c636a1529eca9a082658fd80b4d17cf5f`; only this fixture/report and the
five expected documentation files were dirty. No unrelated changes were found.
Both historical manifests matched their announced hashes and every one of
39 source / 1,986 evidence entries verified before documentation edits.
The 42 attempts, 32 successful fixtures, ten calibration failures and 680 PNGs
were independently counted. All observed grab serials matched their received
buttons. Both historical camera returns changed zero pixels on both outputs;
the ledger consumed exactly two pairs. The ten exclusions remain fixture
failures, with the overwritten early-source limitation retained above.

A new full clone `/tmp/step20c-fractional-freeze-clone-v1` reconstructed private
SceneFX/Mosaic, pristine pinned SwayFX and the C17 clients. Its disposable lab
is `/tmp/swayfx-mosaic-nested-grab-UZe5sYFr`. Seven runs passed: G1 ordinary
calibration, then b_cross outside scenarios in all three modes for G1 and G2.
Each run calibrated both logical references; all twelve popup grabs used real
unchanged serials and mapped. Ordinary/private splith added 127,200 H2 popup
pixels in G1 and 81,200 in G2. Mosaic added zero H2 pixels, retained visible
popup pixels, and delivered no popup button for the exterior click; both
popup_done events followed the exterior grab dismissal. Real modes, normal
transforms, scales and per-output physical PNG dimensions matched G1/G2.
Boundary hover records and passive clip logs are retained. The actual FX
renderer reports GLES 3.2 Mesa 26.2.4-arch1.1 / Radeon 780M radeonsi.
Available private physical damage extents covered all measured settled changed
pixels; ordinary SwayFX has no such native instrumentation.

The replay reserved **zero new camera pairs**, retaining the historical 2/2
budget as the sole camera evidence. No restored-Mosaic hit assertion was added.
Shell syntax, fixture/generated Python AST, C17 -Werror clients, controlled
patch application and all three builds passed; Meson model passed 1/1.
Offline reservation tests passed. Documentation links and git diff --check
passed. Production sources, historical patches, cumulative patch, PKGBUILD
and UX remained unchanged. Per-run runtime cleanup removed private sockets
and terminated owned children. No system installation or live IPC was used.

New source manifest: 974 entries, SHA-256
`c527db9988223fc51d056fdfe8d155ea293c25d1f7361b0aaf93b72be1f06869`.
New complete freeze evidence manifest: 443 entries, SHA-256
`54968808f6df7d23b142d3d9decf975eb2378c1c3e07649332120f66fcfd2722`.
Both live under the new lab's fractional-results directory; historical
manifests were not rewritten. Sources in the new manifest reflect the exact
pre-publication replay fixture, including its then-local documentation.

Verdict remains **PARTIALLY_FEASIBLE**, architectural conclusion **UNDECIDED**.
Opaque tiled overflow remains INCONCLUSIVE, permitted interior shadow remains
INCONCLUSIVE, and a new Mosaic hit after historical camera return remains
NOT TESTED. Rotation, dynamic geometry/ownership, optimized caches, sampling,
saved buffers, intermediate frames, subpixel phases and ABI/package remain
open gates. This freeze adds source-only evidence, not a production contract.
