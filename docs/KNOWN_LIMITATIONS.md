# Known limitations

This document describes the development tree at the documentation foundation pass. `EXPERIMENTAL` means implemented but incompletely validated; `PLANNED` means absent from runtime; `NOT YET SUPPORTED` means it must not be presented as ready for general use.

| Area | Status | Practical implication |
| --- | --- | --- |
| Adjacent-output viewport clipping | NOT YET SUPPORTED | A wider row may render beyond its workspace/output boundary on another output; pointer behavior needs matching validation. |
| Multiple runtime rows | PLANNED | Model helpers/tests exist, but only Row 0 is wired into the Sway tree, arrangement, scene, and input. |
| Camera animation | PLANNED | Camera movement is immediate; transaction-safe timing/curve is open. |
| Cell sizing and grouped containers | EXPERIMENTAL | The 640 px minimum is temporary; nested groups remain one cell. Final sizing/reflow policy is TBD. |
| Resize and output migration | EXPERIMENTAL | Scroll is clamped after arrangement, but these transitions need broader headless validation. |
| Floating, fullscreen, scratchpad edge cases | EXPERIMENTAL | Basic transitions are tested; long-running and multi-output combinations are not qualified. |
| Session V2 Mosaic restore | PLANNED | Mosaic state is not durably restored by Session V2. |
| QuickShell Mosaic visualization | PLANNED | No Mosaic-specific QuickShell display is supplied here. |
| Daily-driver deployment | NOT YET SUPPORTED | Build and headless evidence do not amount to a validated live session. |
| Forward port to a later SwayFX release | PLANNED | The patch is pinned to SwayFX 0.6; a new release requires manual review and validation. |
| Very wide logical coordinates | NOT YET SUPPORTED | Scene positions use bounded integer coordinates; extremely wide canvases are not qualified. |

The [STEP20C viewport proposal](design/STEP20C_VIEWPORT_DESIGN.md) identifies an additional **design feasibility blocker**: installed SceneFX 0.5 exposes no generic scene-tree clip. Its proposed Mosaic-only projection requires a disposable headless proof that all relevant nodes, popups, damage and pointer hits respect one viewport boundary. The proposal does not change any current support status.

The later [popup ownership probe](design/STEP20C_POPUP_OWNERSHIP_PROBE.md) is **PARTIALLY_FEASIBLE**. A private owner-derived root-popup clip kept tested root and nested GTK popup pixels and pointer hits inside the Mosaic viewport on two horizontal headless outputs. Valid-serial grabs and fully hidden owners were untested in that probe; other output arrangements, complete damage and effects also remained unqualified. This does not change the current **NOT YET SUPPORTED** multi-output status.

The [valid-grab and hidden-owner follow-up](design/STEP20C_VALID_GRAB_HIDDEN_OWNER_PROBE.md) is also **PARTIALLY_FEASIBLE**. A genuine pointer-button serial produced an interactive grabbed XDG popup in unmodified SwayFX, private standard layout and private Mosaic. The previous owner-derived viewport clip leaked popup pixels and button hits when the owner was fully hidden. A further disposable owner-visibility guard removed that sampled leak while the popup stayed mapped and returned with the camera. This earlier probe did not qualify nested valid grabs; the separate nested-grab probe below covers only a sampled horizontal matrix. Other output arrangements, transaction-generation consistency, complete damage/effect coverage and ABI/package maintenance remain unqualified. Multi-output Mosaic is still **NOT YET SUPPORTED**.

The [retained source fixture](../tooling/probes/step20c-valid-grab/README.md) permits bounded replay; it does not close these qualification gaps.

The [nested valid-grab probe](design/STEP20C_NESTED_VALID_GRAB_PROBE.md) is
**FEASIBLE for its sampled matrix only**. A separate client used real pointer
button serials to grab A and then B as A's XDG child. In the disposable
guarded compositor, both levels were visible and interactive inside the
Mosaic viewport, absent at sampled pixels and hits beyond it, and suppressed
while their tiled owner was fully hidden; the mapped surfaces returned with
the camera. Closing B left A interactive, and outside clicks dismissed B
then A. Control and private `splith` retained ordinary sampled behavior.
Other output geometries, migration/resize, transaction generations, complete
damage/effects and dependency/ABI maintenance remain **NOT TESTED**. Adjacent
output Mosaic remains **NOT YET SUPPORTED** in production.

The [vertical-output nested-grab probe](design/STEP20C_VERTICAL_OUTPUT_NESTED_GRAB_PROBE.md)
is **FEASIBLE for its measured matrix only**. On two stacked 800×600 headless
outputs, the standard controls showed real A/B XDG popup pixels and buttons
below `y=600`, while the disposable guarded Mosaic build clipped sampled
lower pixels and hits and left upper popup interaction intact. Hidden-owner
and standard-layout return cases also passed at their measured points. This
does not qualify tiled-window Y overflow, continuous or complete damage
coverage, other output geometries, migrations, transaction generations,
effects, or SceneFX ABI/package maintenance. Production adjacent-output
Mosaic remains **NOT YET SUPPORTED**.

The [negative-origin nested-grab probe](design/STEP20C_NEGATIVE_ORIGIN_NESTED_GRAB_PROBE.md)
is **FEASIBLE for its sampled matrix only**. With HEADLESS-1 actually at
`x=-800`, signed global pointer requests reached both outputs, standard
controls exposed real A/B popup pixels and hits beyond `x=0`, and the
disposable guarded Mosaic build clipped those measured pixels and hits while
preserving visible interactions. Hidden-owner and standard-layout return
cases passed at measured points. This does not qualify other output
transforms, migration/resize, complete damage/effects, transaction
generations or SceneFX ABI/package maintenance. Production adjacent-output
Mosaic remains **NOT YET SUPPORTED**.

The [temporal damage probe](design/STEP20C_TEMPORAL_DAMAGE_PROBE.md) is
**PARTIALLY_FEASIBLE** at the same fixed negative-origin geometry. Ten
open/close cycles per configuration and sampled camera transitions found no
residual popup pixels or blocking standard-layout regression. The cycles also
delivered a real A button after B closed; one separate hidden-owner click
missed the popup surfaces and dismissed them in child-first order. Its timed
damage extents covered changed pixels between sampled PNGs, but screenshots
did not enumerate presented frames; broad extents and accepted output commits
cannot prove per-frame rendering, input/scene synchronization or damage
minimality. Popup effects, saved buffers and the SceneFX ABI/package gate
remain unqualified. Production multi-output Mosaic is **NOT YET SUPPORTED**.

The [presentation identity probe](design/STEP20C_PRESENTATION_IDENTITY_PROBE.md)
is **PARTIALLY_FEASIBLE** in the same fixed headless geometry. A private
listener paired 470 headless present callbacks with accepted native output
commits; 12 other accepted commits had no observed present and are not
classified as presented. Applied scene and clip snapshots at the commit
callback covered the measured target transitions, but no exact buffer
readback tied those values to the pixels of a particular commit. `grim`
captures, damage extents and pointer delivery cannot fill that missing
identity. Headless events are simulated, not evidence for physical DRM
presentation. A transient logical/applied camera lag was observed during
initial layout setup; no wrong applied clip or invisible hit was reproduced
in the targeted matrix. Production multi-output Mosaic remains
**NOT YET SUPPORTED**.

The private [output buffer identity probe](design/STEP20C_OUTPUT_BUFFER_IDENTITY_PROBE.md)
is **PARTIALLY_FEASIBLE** at the fixed negative-origin headless geometry.
Thirty-two actual output-state buffers were read through SceneFX FX texture
readback, paired with native commits and headless present events, and
released on present in 28 cases; four were released early when a
HEADLESS-2 repaint reached the probe's global release, before their later
present events. This private instrumentation scope defect is not evidence
of same-output buffer replacement. Three second
reads matched their earlier bytes.
The direct CPU access method was unavailable for the GBM buffers. Readback
added measurable GPU/CPU synchronization and file-copy delay; 29 buffers
were not read a second time at present. The observed transient logical
camera 1760 versus applied scene/clip 1120 had an identified buffer but
no demonstrated wrong pixel or hit. There is still no atomic applied
scene/input generation contract, broad effects/damage proof, physical
presentation proof or SceneFX ABI/package qualification. Production
multi-output Mosaic remains **NOT YET SUPPORTED**.


The subsequent private [applied state/input probe](design/STEP20C_APPLIED_STATE_INPUT_PROBE.md)
is **PARTIALLY_FEASIBLE** in the same fixed headless geometry. A
per-output hold survived an intervening repaint of the other output;
three selected buffers reached matching native presents and matched
visible/hidden/returned applied scene samples. Hit-test, seat-notification
and client-delivery streams were observed separately for visible, clipped
and fully hidden pointer cases. The experimental epoch covers only
instrumented popup and transaction arrangements; other scene, effect,
damage, animation, client-buffer and output mutations remain outside it.
Rejected-commit and output-destroy cleanup were not dynamically triggered.
Readback remains intrusive, and neither an atomic scene/render/input
generation nor physical presentation is proven. Production multi-output
Mosaic remains **NOT YET SUPPORTED**.

The [mutation coverage probe](design/STEP20C_MUTATION_COVERAGE_PROBE.md)
is **PARTIALLY_FEASIBLE** overall. In the fixed headless matrix, the
partial epoch missed a real input-region change that removed a scene hit,
while a client recolor changed pixels without a geometry change. Normal
private output destruction released one intentionally retained buffer
reference exactly once; rejected-commit cleanup passed only a synthetic
model and remains **NOT TESTED** on a real backend. Subsurfaces, effects,
animations, output migration and the complete cross-time build/present/hit
boundary remain unqualified. The architecture decision is **UNDECIDED**;
physical presentation and production multi-output Mosaic remain
**NOT YET SUPPORTED**.

The independently replayed [commit/present/input ordering probe](design/STEP20C_COMMIT_PRESENT_INPUT_ORDERING_PROBE.md)
is **INCONCLUSIVE** for the discriminating temporal case. The headless
backend defers `present` to an idle callback, but none of 20 bounded
input-region mutations in private standard/Mosaic fell between a native
commit and its matching present. Sampled hits and client receipt followed
the applied input state, with unchanged sampled pixels; this is not a
demonstrated Mosaic clip defect. Client input-only commits need not cause
output redraw. Popup clip changes in that window, physical presentation,
rejected backend commit cleanup and broader output/effect paths remain
**NOT TESTED**. Existing ordering sufficiency and any added-generation
contract remain **UNDECIDED**.

The [pending-input event-loop follow-up](design/STEP20C_EVENT_LOOP_PENDING_INPUT_PROBE.md)
removed the runner's intermediate response waits during five bounded cycles
per private mode. It confirmed ten positive client flushes and ten applied
target input commits per mode, yet zero natural commit→mutation→present
interleavings. The sought same-interval hit and grabbed-popup variant are
**NOT TESTED**. The result remains **INCONCLUSIVE** for that temporal window;
repeat attempts on the same headless matrix are closed. Effects/damage,
scaling and resize/migration remain open STEP20C gates.

The [effects/damage follow-up](design/STEP20C_EFFECTS_DAMAGE_PROBE.md) is
**PARTIALLY_FEASIBLE** only for the sampled negative-origin private matrix.
Both standard controls showed a genuine shadow overflow into 46 neighboring
columns; the private Mosaic output showed none. A real translucent blur
changed patterned pixels inside Mosaic without changing the neighboring
output, and three settled camera returns were pixel-identical to baseline.
Sampled private damage extents covered capture-to-capture changes. The
Mosaic interior shadow was not independently visible. Optimized blur cache
correctness, source sampling outside the viewport, popup effects, saved
buffers, intermediate frames and other renderers remain **NOT TESTED**.
The optional trace changed the neighboring reference rendering in Mosaic,
so visual claims use the untraced runs. Production multi-output Mosaic
remains **NOT YET SUPPORTED**.
The final audit also found that reproduction/trace replays executed 15
camera pairs instead of the requested campaign maximum of three. This
protocol deviation is retained with all raw runs and prevents claiming
full campaign compliance; the final fixture now enforces the finite budget.

The [isolated feasibility probe](design/STEP20C_FEASIBILITY_PROBE.md) is **PARTIALLY FEASIBLE**, not a release qualification. On two horizontal headless outputs, real Mosaic content leaked visually into an empty adjacent output; that earlier disposable candidate also delivered pointer enter from a partly visible client outside its viewport. Negative-origin, scaled and rotated arrangements showed visual leakage in that candidate. Popups, effects, saved buffers and complete damage correctness remain unqualified across the full matrix. The later probes above narrow individual cases without qualifying multi-output Mosaic, which remains **NOT YET SUPPORTED**.

The later [SceneFX subtree clipping spike](design/STEP20C_SCENEFX_CLIPPING_SPIKE.md) is also **PARTIALLY FEASIBLE**. Its private inherited tree clip stopped tested tiled pixels and pointer hits from crossing the output boundary, including a fully hidden cell, but a real GTK XDG popup rendered and received input on the neighboring output because its scene tree lives in the global popup layer. Dedicated subsurface, saved-buffer, nested-popup and complete effect/damage validation remain open. The spike changed no production library or compositor source; multi-output Mosaic remains **NOT YET SUPPORTED**.

These limits are reflected in [UX](UX.md), [architecture](ARCHITECTURE.md), and [roadmap](ROADMAP.md). A future step must update those contracts before claiming support.

The preserved [fractional scaling probe](design/STEP20C_FRACTIONAL_SCALING_PROBE.md)
is **PARTIALLY_FEASIBLE** for static 1.25 uniform/mixed and 1.5 mixed headless
outputs. Actual modes/PNGs and logical pointer motion were calibrated. Sampled
root/nested popup and shadow spill disappeared on the neighboring output;
visible blur, terminal popup columns, two settled camera returns and available
physical damage were consistent. Opaque tiled-overflow controls, permitted
interior shadow, restored Mosaic hit, caches and intermediate frames remain
unqualified. Ten failed early calibrations and their source-provenance limit
are retained. The two-pair global budget was respected. The next distinct gate
should test resize/migration of owner/output clips; rotation, saved buffers and
ABI/package remain separate. This is evidence only: STEP20C stays **NEXT**,
production multi-output **NOT YET SUPPORTED**, STEP20D–G **PLANNED**.

The preserved [dynamic output ownership probe](design/STEP20C_DYNAMIC_OUTPUT_OWNERSHIP_PROBE.md)
is **PARTIALLY_FEASIBLE**: actual logical resize 800→960→800 and workspace
migration H1→H2→H1 retain workspace/tiled identities and update sampled applied
tiled/root-popup clips. Vacated outputs show exact background after stabilization.
Two standard controls fail final reference calibration through fixture occlusion;
Mosaic's corrected calibration passes. Maximum-scroll clamp, migrated clipped
popup input, independent opaque tiled spill, effects and intermediate frames
remain unqualified. Budgets are exhausted at six reconfigurations and six
migrations, with zero additional camera pairs. No production change follows.
Rotation is the next separate geometric gate; other open STEP20C gates persist.
The original temporary evidence manifest was verified before an offline
analyzer rerun replaced it; its exact historical bytes are not retained.
STEP20C stays **NEXT**, multi-output **NOT YET SUPPORTED**.

The [rotation probe](design/STEP20C_ROTATED_OUTPUT_PROBE.md) established
the applied 90° mode/transform and logical PNG/pointer orientation in two
private runs, plus sampled fully-hidden owner and damage behavior. Its global
result is **PARTIALLY_FEASIBLE**, architectural partial-clipping conclusion
**UNDECIDED**: pristine R90 capture failed through fixture assertion, and the
Mosaic popup stayed wholly inside the viewport despite standard control spill.
Scored border hits, rotated shadow/blur/cache and raw buffer readback are
**NOT TESTED**. No production support claim follows.

The subsequent [static R90 partial-popup probe](design/STEP20C_ROTATED_PARTIAL_POPUP_CLIP_PROBE.md)
closed the missing B geometry challenge for one legal XDG placement:
Mosaic B crossed by 72 logical pixels; sampled H1 visual/button input
survived and H2 matched its prior reference with no B delivery. Its
overall status is **PARTIALLY_FEASIBLE**. The A root popup also crossed,
but independent input on its forbidden portion remains **NOT TESTED**.
Saved buffers, optimized blur caches, inner shadows, intermediate frames,
atomic generation and SceneFX/wlroots ABI/package remain unqualified.
Multi-output stays **NOT YET SUPPORTED**.

The [saved transaction buffer probe](design/STEP20C_SAVED_TRANSACTION_BUFFER_PROBE.md)
is **INCONCLUSIVE** for the intended partial-overflow gate. The target
snapshot was outside H1 because its applied camera differed from the
fixture's assumed initial position. Other saved nodes rendered in the
private scene; ACK and natural timeout removed sampled trees. Target pixels,
clipped input, transaction-scoped damage, destruction while pending and
reference lifetime after texture conversion remain unqualified. One
private-standard episode failed through fixture timing. STEP20C remains
**NEXT** and production multi-output **NOT YET SUPPORTED**.

The [new target-crossing probe](design/STEP20C_SAVED_BUFFER_TARGET_CROSSING_PROBE.md)
is **PARTIALLY_FEASIBLE** for one real saved target that crossed x=0 and
rendered only its permitted H1 portion in the sampled ACK episode. H2 had no
target-color pixels but differed from its whole-image reference by 253 pixels
of unproven cause, also seen in pristine controls. A stale fixture pointer
stopped Mosaic E2 before natural timeout; target input, complete damage and
GPU reference lifetime are unqualified. STEP20C remains **NEXT** and
production multi-output **NOT YET SUPPORTED**.

Offline RGB analysis found the same filled 11×23 `#F5E0DC`→`#303038`
rectangle in pristine and Mosaic H2 comparisons. Kitty's recorded local
block-cursor color and blink setting strongly support a dynamic reference,
but no effective cursor phase was logged. Whole-H2 equality is still
unproven; the new timeout probe must use a static reference.

The subsequent [static-reference saved-target timeout gate](design/STEP20C_SAVED_TARGET_TIMEOUT_INPUT_PROBE.md)
is **PARTIALLY_FEASIBLE**. In one private horizontal Mosaic run, all four
full H2 RGB captures matched exactly; the actual crossing saved target
rendered its permitted H1 pixels, remained absent on H2 and its saved tree
was removed after a natural timeout with the configure withheld. Two pointer
points showed no invisible H2 target hit. Full frame-by-frame damage,
unmeasured input paths, seat notification for the saved node and complete
GPU/texture reference lifetime remain **NOT TESTED**. The old Kitty cursor
explanation remains strongly probable, not causally proven. STEP20C remains
**NEXT** and production multi-output Mosaic **NOT YET SUPPORTED**.

The preserved [optimized blur cache probe](design/STEP20C_OPTIMIZED_BLUR_CACHE_PROBE.md)
is **PARTIALLY_FEASIBLE**, architecture **UNDECIDED**. A real background
layer under blur_tree triggered natural output-specific cache reconstruction
and fresh central A/B/A filtered pixels in private splith and Mosaic.
Sampled final tiled drawing excluded H2, whose whole RGB remained identical;
output damage extents covered stabilized differences and sampled cache/FBO
teardown completed. Shared boundary differences up to six RGB levels remain
unresolved. Pristine C0 failed before captures through a duplicate configure
fixture; its second initial image was reserved only after observation.
No numerical budget was exceeded or run repeated. Instrumentation neutrality,
whole-cache equivalence and intermediate frames remain unqualified. A
separate pristine/untraced boundary-sampling gate should precede ABI/package
qualification. This evidence freeze changes no production or UX contract.
STEP20C stays **NEXT**, multi-output **NOT YET SUPPORTED**.

The preserved [optimized edge causality gate](design/STEP20C_OPTIMIZED_BLUR_EDGE_CAUSALITY_PROBE.md)
is **PARTIALLY_FEASIBLE**, architecture **UNDECIDED**. Four completed fixed
negative-origin runs qualify pristine/private splith and same-binary Mosaic
OPT-off/on controls. Pristine/private full images and Mosaic trace-off/on
full images are exact at six homologous states; common glass across layouts
is also exact. Historical right/bottom differences persist without new traces,
with max RGB delta 6, fresh central pixels and stable whole H2. Native FBO
history causality remains unproved despite source/model support. R3 damage
extents cover stabilized differences only. No clipping regression or required
invariant violation is established. A separate SceneFX ABI/package audit is
now justified, retaining this shared rendering limitation; optional selective
GPU observation requires a new scoped ticket. This evidence is preserved without a production change. STEP20C stays NEXT, production multi-output NOT YET SUPPORTED.

The preserved [SceneFX ABI/package audit](design/STEP20C_SCENEFX_ABI_PACKAGE_FEASIBILITY.md)
is **PARTIALLY_FEASIBLE**, architecture
**SCENEFX_ABI_PACKAGE_REQUIRES_ARCHITECTURAL_DECISION**. The unchanged current
package builds with stock SceneFX and stages exactly /usr/bin/swayfx-mosaic.
The shared experimental binary needs two clip exports absent from stock
despite the same SONAME. Static embedding builds and resolves without a
SceneFX shared dependency, but shared wlroots interposition, updates, security
maintenance and license notices remain gates. A distinct private shared library
would require a new file-ownership decision; upstream API acceptance is unknown.
No integration or packaging contract is approved. The historical audit is frozen as evidence; STEP20C stays NEXT, production multi-output NOT YET SUPPORTED.

The preserved [static distribution contract dossier](design/STEP20C_SCENEFX_STATIC_DISTRIBUTION_CONTRACT.md)
is **EXPERIMENTAL / PARTIALLY_FEASIBLE**, conclusion
**STATIC_DISTRIBUTION_REQUIRES_CONTRACT_DECISION**. One private Meson DESTDIR
stage of the hash-qualified static executable contains exactly
`/usr/bin/swayfx-mosaic`; this proves file shape only. The 85 overlapping
exports and 31/34 wlroots scene bindings into the executable remain explicit
paired-version constraints, not automatically defects. Only the pinned
SceneFX 0.5 / observed wlroots 0.20.2 pair has non-graphical evidence.
Notices (including generated protocols), security ownership, upgrades, rollback
and graphical semantics remain gates. A disposable notice-section extraction
passes mechanically; legal distribution compliance is not approved.
The upstream API dossier is preserved and not submitted. Production strategy:
**NONE — USER DECISION REQUIRED**. Packaging/UX contracts are unchanged;
STEP20C stays NEXT and production multi-output NOT YET SUPPORTED.

## Approved private STEP20C static candidate — 2026-10-13

The user approved four decisions for documentation and private prototypes only:
private static SceneFX; separate complete notices under
`/usr/share/licenses/swayfx-mosaic/`; project responsibility for embedded
SceneFX maintenance; and qualification of each exact SceneFX/wlroots pair.
See the [decision register and bounded runtime gate](design/STEP20C_STATIC_RUNTIME_AND_PACKAGE_CONTRACT.md).
The current PKGBUILD, system SceneFX dependency, one-binary package, production
sources and cumulative patch remain unchanged. The future private stage may
contain only `/usr/bin/swayfx-mosaic` and justified regular notice files below
the license directory. No private shared library, session, service, config or
Sway symlink is allowed. No real installation is authorized.

Mosaic owns monitoring, impact review, rebuild and requalification of embedded
SceneFX fixes, including renderer/shaders/dependencies/ABI/buffer lifetime/clip/
damage changes. Before public distribution, a release maintainer and security
reviewer must be designated; no names or SLA are assigned. Preserve exact source,
patch, compiler/options/dependency, notice, test and artifact manifests.
A new relevant dependency build requires header/symbol/shared-layout inspection,
rebuild, relocation/model/staging/headless checks and graphical requalification
of relevant paths, then a separate publication decision. No automatic update
subsystem is added. Ordinary SwayFX upgrades remain independent and standard
SwayFX remains the fallback. All other pairs are NOT QUALIFIED.

These decisions do not settle popup UX or close STEP20C production gates.
STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT; STEP20D–G PLANNED.
Production multi-output remains NOT YET SUPPORTED.

The [private static runtime gate](design/STEP20C_STATIC_RUNTIME_AND_PACKAGE_CONTRACT.md)
is **EXPERIMENTAL / PARTIALLY_FEASIBLE**, architecture **UNDECIDED**. Real `/usr`
static build/model/stage/notices/loaded-library identity/headless startup pass.
Sampled H1 target pixels survive with zero target colors on H2, but whole-H2
reference equality fails through a focus/decor mismatch; input and splith return
are NOT TESTED after the single run stopped. No rerun or algorithm modification
occurred. Distribution notice closure, named release/security roles and broader
ABI/graphics gates remain open. STEP20C NEXT, multi-output NOT YET SUPPORTED.

The [static focus/input/standard follow-up](design/STEP20C_STATIC_RUNTIME_FOCUS_INPUT_STANDARD_PROBE.md)
is **EXPERIMENTAL / INCONCLUSIVE**, architecture **UNDECIDED**. One run reused
the exact static binary, verified loaded wlroots/output geometry, calculated
camera and observed the applied clip. A fixture incorrectly required stored
current_border_width=0 under border none; actual IPC retained thickness 2 with
empty decoration and full-size client rectangles. The run stopped before any
PNG, click or splith transition. Those gates are NOT TESTED; no clipping defect
or need for an algorithm change is demonstrated. No retry/build/production
change occurred. A separately authorized corrected-fixture gate is required.
STEP20C stays NEXT; production multi-output remains NOT YET SUPPORTED.

The [static RGB/input/standard retest](design/STEP20C_STATIC_RGB_INPUT_STANDARD_RETEST.md)
is **EXPERIMENTAL / FEASIBLE for the tested matrix**; its evidence is frozen
for publication.
The corrected shared IPC predicate/replay pass before the sole unchanged-static-
binary run. Two full H2 references and all later H2 RGB are exact; H1 retains
182,214 target pixels, H2 zero, actual visible/reference/standard button pairs
are delivered only to the right client. Targeted splith removes the native clip
and retains ordinary pixels/input. The runner exits 1 only on terminal exit IPC
after completed measurements and compositor exit 0; that raw failure is retained
and separately diagnosed/revalidated offline. No algorithm, build, production,
package or UX change follows. Wider static popup/effect/lifecycle, complete
damage/generation, ABI/maintenance/notices gates remain open. D1–D4 persist;
STEP20C stays NEXT and production multi-output remains NOT YET SUPPORTED.

The preserved [static nested valid-grab probe](design/STEP20C_STATIC_NESTED_VALID_GRAB_PROBE.md)
is **EXPERIMENTAL / INCONCLUSIVE**, architecture UNDECIDED. The sole unchanged-
static-binary run verified actual identity, outputs, applied camera/tiled clip
and two exact whole-H2 references, then stopped before any click or popup on
an invalid painted-height assertion (573 vs native SHM320). An additional
IPC-y/titlebar assertion was also invalid. The recorded offline test PASS had
an insufficient source-assertion audit; raw runner exit1 and all evidence remain
immutable. Root/nested grabs, geometry, popup pixels/input/dismissal and splith
are NOT TESTED in this campaign. No algorithm/production/UX/package change or
retry; budget exhausted. Correct/replay geometry predicates offline before a
separately authorized fresh static popup gate. Historical failure evidence is frozen;
STEP20C NEXT, production multi-output NOT YET SUPPORTED.

The preserved [static nested geometry replay gate](design/STEP20C_STATIC_NESTED_GEOMETRY_REPLAY_GATE.md)
is EXPERIMENTAL / INCONCLUSIVE. True SHM/configure/paint geometry and nine
historical popup cases were replayed;145 historical asserts and2288 current AST
sites are classified, with partial executed coverage explicit.195 offline tests
pass, but independent review retains CORRECTION_REQUIRED: the readiness
aggregator accepts semantically incomplete proof records. Input correlation and
terminal-code repairs are accepted; no readiness or new static popup result.
No graphical run or execution reservation occurred. Close the residual offline
receipt-validation gate before proposing runtime. Architecture UNDECIDED;
STEP20C NEXT; production multi-output NOT YET SUPPORTED.

## Local receipt semantic integrity gate — offline only

The [R02 receipt-integrity gate](design/STEP20C_STATIC_NESTED_RECEIPT_INTEGRITY_GATE.md)
is local and experimental. The real writer/aggregate share semantic validation
through the existing immutable-data replay and R01 input correlation; typed
receipt content, scenario-specific omissions, AST/test inventories and final
review bindings are checked. Historical geometry evidence remains INCONCLUSIVE;
this correction cannot retroactively qualify static popups. The final local gate
is READY_FOR_NEW_RUNTIME: 206 offline tests pass, 13478 recorded invalid mutations
are rejected, and independent review accepts the final 18-source/15-receipt
bindings after one bounded B-01 writer repair. The actual writer returns READY
with five PASS markers and no blockers. R02 is RESOLVED for this offline fixture;
partial AST coverage and runtime limitations remain explicit. Phase B is
uncommitted and unpublished, and readiness only permits requesting a separate
future authorization. No compositor/runtime authorization,
production/UX/package change or STEP20D work follows. Architecture UNDECIDED;
STEP20C NEXT; production multi-output NOT YET SUPPORTED.


## Preserved static nested runtime handoff — experimental evidence

The [handoff and valid-grab report](design/STEP20C_STATIC_NESTED_RUNTIME_HANDOFF_AND_VALID_GRAB.md)
records PASS transfer/preflight and one unchanged-static-binary run, verdict
INCONCLUSIVE. Four genuine grabs and sampled E1/E2 Mosaic crossing pixels,
E1 visible/forbidden input and dismissal passed. E2 reached splith with mapped
popups and standard pixels, then a fixture root-window consistency predicate
rejected the old-to-cleared clip transition. Offline retained observations
support settled clip removal; standard A/B input, explicit child close/A survival
and final H2 restoration remain NOT TESTED. Raw runner/IPC exit1 and clean
compositor/client exits0 remain intact. No rerun or algorithm change; historical phase B
is preserved for publication by the E2 completion batch. Architecture UNDECIDED, STEP20C NEXT,
production multi-output NOT YET SUPPORTED; broader damage/generation/output/
effects/ABI/distribution gates remain open.


## Static E2 completion support boundary — 2026-10-13

The [completion report](design/STEP20C_STATIC_E2_TRANSITION_AND_COMPLETION.md)
and [current fixture results](../tooling/probes/step20c-static-e2-completion/README_RESULTS.md)
record B offline PASS, C **FEASIBLE for the tested E2 matrix** and D initial
**BUILDABLE** with an accepted **COMMENT-ONLY / NOT REBUILT** delta. C closes
its own sampled standard-return B/A input, explicit B-close/A-survival and normal
owner-close/full-H2 restoration gates. It does not rewrite the historical
INCONCLUSIVE campaign, whose corresponding gates remain NOT TESTED.

C ran once on normal scale1 outputs at x=-800/0 with the unchanged static binary.
New static hidden-owner, saved-buffer/effects, vertical/scaled/rotated and
migration/resize matrices remain unqualified; historical private evidence retains
its own limits. Settled full-H2 equality and 256 sampled damage traces do not
qualify every intermediate frame, complete damage/stale pixels or atomic
transaction/render/input generation. Universal click-through and final offscreen
popup UX remain UNDECIDED.

D's new binary has **NOT TESTED** graphics. Initial builds/model/ELF/stage pass;
annotated sources are NOT REBUILT and the future recipe is syntax-only, NOT RUN.
The exact five-file private stage includes the binary and four license notices;
semantic ABI maintenance is NOT ESTABLISHED, legal compliance NOT APPROVED,
and release/security names remain required. Raw terminal IPC1 and startup
EGL_BAD_ALLOC entries remain preserved despite runner/compositor/client0 and
completed C observations. A fresh old 206-suite setup retained 145 PASS/61 setup
errors, separate from B's accepted104 tests and the historical206 result.
Final batch audit is PASS / ACCEPTED. Publication identities are recorded in
Git history and the private closeout receipt. STEP20C remains NEXT, production
multi-output NOT YET SUPPORTED; no daily-driver qualification follows.

## Preserved overnight STEP20C qualification — 2026-10-14

The [overnight qualification dossier](design/STEP20C_OVERNIGHT_QUALIFICATION_AND_INTEGRATION_GATE_V1.md)
records a fresh annotated private rebuild and its own bounded graphics evidence,
plus a separately built release-shape candidate with its own horizontal smoke.
The [exact matrix](design/STEP20C_ANNOTATED_GRAPHICS_MATRIX.md) contains 18 unique
runs and 196 captures, without retries. Horizontal C is FEASIBLE for sampled
cases; the overall result is PARTIALLY_ADVANCED and the integration recommendation
is PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE, a draft decision, not adoption.

Vertical, scaled, R90 and resize/migration observations remain bounded. D2's
fixture root association stopped before input/final qualification; saved-buffer
E2 was NOT EXERCISED; whole-H1 effects restoration failed in both controls;
F's stale-coordinate assertion stopped its remaining mutations. Atomic
transaction/input/present identity, complete damage and GPU buffer lifetime
remain NOT PROVEN. G is SMOKE_FEASIBLE horizontally, without inheriting A's
matrix or establishing instrumentation neutrality. Exact local ABI/staging
checks and future recipe syntax/input checks do not qualify future pairs,
complete makepkg reproduction, actual notice incorporation or legal distribution.

STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT; STEP20D–G PLANNED.
Production multi-output remains NOT YET SUPPORTED. No production, UX or current
package contract is changed. Final independent review is ACCEPTED / audit PASS for experimental evidence
fidelity. Documentary publication is prepared, not executed at this edition;
production integration remains undecided.

## Targeted STEP20C limits — 2026-10-14

The [targeted dossier](design/STEP20C_TARGETED_CLOSURE_DECISION.md) adds exact-SHA
scale and G dynamic/hidden/R90 observations. It retains 14 raw INCONCLUSIVE
runtime outcomes (terminal IPC exit 1), distinct from positive measurements and
process codes 0. Saved A/G show a real held configure, but no natural timeout,
held image/native saved identity or normal close; error 32 during compositor
teardown keeps scientific cleanup INCONCLUSIVE. The distinct C3 run also stops:
its frozen unique-address predicate rejects actual node-address reuse. C3
creation/H1 draw/teardown and lock 3 to 4 are partially observed, but the bounded
wait failure is not a natural transaction timeout. Held/live PNG, H2 held
clipping, normal owner close and GPU completion remain unqualified; no result
transfers to A/G.

Classic blur is genuinely exercised in pristine/A/G. Whole-H1 optimized return
still fails by 37,252 pristine and 34,323 A/G pixels, maximum channel delta 6,
without masks. A/G's 16 homologous RGB frames are exact; a deterministic source
kernel model does not reproduce the native signed deltas, so GPU causality and
neutrality remain INCONCLUSIVE. Permitted interior shadow is NOT EXERCISED.
Input A/G stops at a focus/camera mutation during delivery; observed local
coordinates agree with the latest native origin, but remaining camera/layout
coverage and atomic generation are unqualified. Native replay pairs 789 of 821
final commits (13 initial runs: 758/788; C3: 31/33); buffer identity, complete damage and lifetime remain NOT PROVEN.

Private recipe metadata/source verification and five-file stages are validated;
full package build is NOT RUN. Exact incorporation/legal notices, named
release/security ownership and all other SceneFX/wlroots pairs remain open.
Final independent review is ACCEPTED / audit PASS for experimental evidence
fidelity. Documentary publication is authorized and prepared, not executed at
this edition; final refs belong to the private closeout and final handoff.
STEP20C remains NEXT; production multi-output remains NOT YET SUPPORTED.

## Saved/input/GPU STEP20C batch — 2026-10-14

The [new gate dossier V2](design/STEP20C_GATE_CLOSURE_DECISION_V2.md) records a
separate six-run campaign:59 captures/240 reservations, 42 common and six GPU
offline tests passed; two optional runs were not exercised. The previous
14-run/125-capture/520-reservation campaign remains immutable.

Three saved runs exercise an actual native five-second transaction timeout
with client alive, held capture before deadline, normal owner close and exact
whole-H2 RGB through hold/timeout/final. C3 identifies target lifetime instance15
and natural node retirement; A/G qualify their own wire/RGB/timeout, without
native saved identity transfer. Target retirement release and GPU completion
remain NOT PROVEN. Two A/G input runs finish full/empty/full, focus/camera
mutations and targeted splith return. Temporally compatible applied state is
PARTIALLY_FEASIBLE, without proving atomic generation.

The distinct GPU diagnostic acquires108 native ROI reads and supports local
FBO history outside the fresh domain: first sampled fresh divergence is down-2,
not down-1. Whole-H1 A/B/A remains FAIL and whole-field causality INCONCLUSIVE;
no shader/cache correction follows. Native pairing is414/400/14 with unknown
missing-event causes; damage union coverage is sampled, not all-frame proof.
The bind-before-failed ordering already exists in pinned pristine SceneFX;
the old draft's contrary provenance claim is explicitly corrected in the new
[GPU report](design/STEP20C_GPU_FBO_CACHE_CAUSALITY.md), without historical rewrites.

Measurements, raw runtime exit, scientific cleanup and architecture remain
separate: all six global runtimes are INCONCLUSIVE on terminal IPC1; saved/input
helpers error32 keep scientific cleanup INCONCLUSIVE despite owner0, while GPU
clients error0 give scientific cleanup PASS. Mechanical process cleanup passes.
The private core is source-only ACCEPTED for bounded review, build/runtime/C
UBSan/OOM NOT RUN; no runtime result transfers. Whole-field GPU/lifetime,
atomic scene/input/present, full damage, instrumentation neutrality, exact-pair
maintenance, full package/notices/legal and release/security ownership remain
gates. Offscreen-popup UX and a particular atomic-counter mechanism remain
UNDECIDED. The applied rendering/input coherence contract remains required.

Recommendation PRIVATE_CANDIDATE_NEEDS_TARGETED_EVIDENCE; scientific status
PARTIALLY_ADVANCED. Final dossier review ACCEPTED / audit PASS for experimental evidence fidelity;
documentary publication PREPARED at this edition, with actual refs in the private
post-push receipt. STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT;
STEP20D–G PLANNED; production multi-output NOT YET SUPPORTED. No production,
UX or package contract changes, and no authorization for further graphics runs.

## Minimal private core limits — 2026-10-14

The [new exact-core campaign](design/STEP20C_MINIMAL_CORE_ABI_PACKAGE_AND_INTEGRATION_DECISION.md)
is separate from the historical source-only core: build and extracted C unit
normal/UBSan/ASan gates now pass on their own sources. Compositor sanitizer
remains NOT RUN; OOM sidecar allocation abort remains experimental/P1 and does
not qualify production availability. Local ELF/relocations/layout/provider
checks and five-file Stage1 pass, but future pairs, maintained interposition,
full package reproduction and notices/legal review remain open.

Twelve runs consume 88 captures without retries. E0-pristine/E0-core/vertical
fail before images, leaving no comparable new standard control. E1's first
grabbed chain is sampled but second-owner ancestry stops standard return.
Fractional/R90 and resize/migration pass their bounded measurements; E4 has an
actual non-leaf fullscreen ancestor without comparable standard policy control.
E5 dismissal prevents same-chain hidden-owner return. E6 has a real native
five-second timeout before ACK/teardown, but retains its frozen-validator FAIL,
normal-close limit and unobserved native saved identity. Runner process cleanup
PASS is not universal Wayland error 0 closure; E2 helpers error 32/marker timeout,
E1/E6 closure gaps and G1 client exit 1 remain visible.

Core classic blur is exercised. Whole-H1 A/A-return remains FAIL 33,789 pixels,
max RGB 6/5/1, with H2 sampled exact; shadow contribution is NOT EXERCISED.
G1's sole first epoch is rejected: the fixture's all-plane image-stride predicate
is inappropriate for the observed AMD DCC modifier. Raw GPU read_success stays
NOT PROVEN, GL error queue UNOBSERVED and whole-field causality INCONCLUSIVE.
Native buffer/GPU lifetime, atomic generation and complete damage remain
NOT PROVEN; damage-ring extents do not prove frame presentation.

Recommendation PRIVATE_CORE_NEEDS_TARGETED_EVIDENCE, scientific status
PARTIALLY_ADVANCED. Evidence delta review ACCEPTED; final dossier review pending,
publication PREPARED at this edition. Production multi-output NOT YET SUPPORTED;
STEP20C NEXT. No production, UX, package or historical evidence change.
