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
