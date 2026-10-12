# STEP20C SceneFX effects and damage probe

**Status: EXPERIMENTAL / PARTIALLY_FEASIBLE for the sampled matrix.** STEP20C stays
**NEXT**, STEP20B **EXPERIMENTAL**, and production multi-output Mosaic
**NOT YET SUPPORTED**. This is a bounded private feasibility measurement,
not a UX, ABI, package or production decision.

## Question and current evidence

The private inherited clip and owner-derived popup guard passed sampled
tiled, nested popup, grab and negative-origin cases. The earlier SceneFX
spike accepted `shadows enable` and `blur enable` and showed a sampled shadow
boundary, but did not prove a distinct translucent blur, optimized blur
cache correctness or effect-specific damage. This probe requires an effect
to be **created and enabled, geometrically placed and measurably visible**
in both standard controls before its Mosaic clipping can pass.

The viewport is HEADLESS-1 `(-800,0,800,600)` beside HEADLESS-2
`(0,0,800,600)`, both scale 1 and normal transform. Mosaic's applied Row 0
clip should prevent tiled-owner content, including its shadow and blur draw
regions, from writing outside the workspace viewport. An effect must remain
visible in its permitted interior. The ordinary client on HEADLESS-2 must
retain its own pixels. A blur shader may sample outside its draw region;
source sampling, visible influence and a contract violation are distinct
claims. No policy forbidding a particular shader source sample has yet been
accepted, so T3 cannot be called a leak on sample reach alone.

## Source audit and working hypotheses

Pinned inputs: private Mosaic base
`cd550382b311efdbfe3ed892f4e1d281d852e754`, SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc`, wlroots 0.20.2.
The preserved private clip patch is layered on these bases. In SceneFX
`types/scene/wlr_scene.c`, `scene_node_intersect_clip` intersects ancestor
tree clips for each leaf. `scene_node_update_iterator` intersects
`node->visible`; `scene_node_bounds` intersects new bounds; and
`scene_node_update` damages old and new visibility. The render-list
constructor rejects empty visible intersections. `scene_entry_render`
passes `node->visible ∩ output damage` as the draw clip for buffer, rect,
shadow and blur entries. This demonstrates a route for all four node types
through the inherited **draw** clip, not proven shader sampling bounds.
`scene_output_damage` maps logical damage into the output buffer and queues
repaint. Its extents can exceed changed pixels and cannot prove every
intermediate frame or optimality.

SwayFX creates a shadow and blur under each container `scene_tree`; their
geometry and enabled state are updated in `sway/desktop/transaction.c`;
`output_configure_scene` additionally configures blur selection, strength
and corner radii using the closest container. A tiled container should inherit its tiling
tree clip. Layer-shell surfaces have their own effect nodes, with different
ownership. Root XDG popups are globally parented and receive the separate
owner-derived private guard; no popup effect is assumed without observed
node creation. Each output creates an `optimized_blur` node under staging,
outside the tiled owner's tree. `mark_dirty` sets its dirty flag only while
enabled; scene rendering clears it after a successful optimized blur pass.
SwayFX marks it dirty on selected blur/layer changes. Camera movement alone
is not yet proven to invalidate all relevant optimized caches. Thus the
ordinary inherited clip does **not** directly own the output optimized node.
The optimized cache pass itself uses its output-sized destination box;
it does not receive the tiled descendant's `render_region` draw clip.
The final ordinary blur texture draw does receive that clip. These two
operations must be audited separately.

The box-shadow node can extend by its configured sigma and offset beyond
the view's rectangle. `scene_entry_render` supplies a clipped draw region,
while shader/filter sampling may use a wider source footprint. The
`apply_blur_region` path expands damage for blur sampling; actual output
pixels and damage must be measured. Saved transaction buffers are distinct
from client SHM buffers, output buffers and optimized blur caches. No saved
buffer claim is valid without an observed controlled creation/use path.

These source answers are hypotheses until real effects are activated. A
successful IPC command, compiled shader, enabled flag or nonempty render
list alone is insufficient visual evidence. The renderer, EGL/GLES version,
headless backend, buffer formats and linked SceneFX/wlroots versions must be
recorded for each private run; `WLR_RENDERER=pixman` is a request, not proof
of the renderer actually used.

## Fixture and comparisons

Rebuild from a full Git clone into a private temporary lab. Preserve the
same deterministic SHM clients and effect settings in three modes:
unmodified SwayFX `splith`, private `splith`, private `mosaic`. Use explicit
private runtime and IPC socket, bounded process groups, timeouts and
captures; never address the daily session. The visual client will supply a
documented high-contrast striped/damier background, a translucent surface,
an opaque surface, and a stable ordinary reference on HEADLESS-2. Record
all SHM sizes, colors, alpha values, geometry and mapping. Disable dynamic
content and animations where the normal compositor allows it. Fix pixel
regions of interest before inspecting anomalies: interior effect, boundary
band on each output, unchanged reference and exposed/old-owner regions.
PNG coordinates are output-local; Wayland/Mosaic global coordinates are
signed.

Separate **FX0** (shadow/blur off), **FX1** (shadow only), **FX2** (blur on
translucent patterned background), **FX3** (optimized blur only if a real
enabled node and dirty/cache transition can be observed), and **FX4**
(combined only after independent FX1/FX2 proof). For each effect require:
accepted configuration, observed enabled node and size/position, a
preselected pixel ROI changing against FX0, and both standard controls
visibly exercising it. An unavailable effect is `NOT TESTED`; visible but
inseparable effects are `INCONCLUSIVE`.

## Bounded scenarios

* **T1 shadow boundary:** standard controls visibly draw a shadow across
  global `x=0`; Mosaic retains its permitted interior and excludes its
  forbidden right-output pixels. If controls do not overflow, no clipping
  claim follows.
* **T2 translucent blur boundary:** demonstrate blur distinct from alpha
  compositing with effect off/on ROIs, then compare the three modes.
* **T3 hidden sampling influence:** keep inside-viewport sources fixed,
  alter only an outside pattern, and test visible blurred pixels. Record
  draw clip and sampling evidence separately; classify contract legitimacy
  conservatively.
* **T4/T5 hidden owner and return:** at most three `scroll_x 400→1280→400`
  pairs, with right-output reference, enabled nodes, cache state, settled
  pixels and old/new damage checked. Do not accidentally dismiss popups.
* **T6 effect toggle and close:** disable/re-enable by normal commands,
  then close the relevant surface and compare discovered regions.
* **T7 standard-layout return:** switch to `splith` while surfaces remain
  open; ordinary effects must return without Mosaic clip leakage.

Only after main cases are valid, consider one bounded real-serial nested
popup hierarchy. First audit whether that hierarchy owns any applicable
effect node. No positive popup effect is invented. A horizontal regression
is allowed only if it distinguishes an observed anomaly. No scale, rotation,
migration or saved-buffer animation is silently added.

## Pixel, damage and classification rules

Record per capture output, dimensions, phase, monotonic capture window,
SHA-256, fixed ROIs, reference colors, pixel difference count and bounding
box, plus color-distance summaries for blur. Use lossless PNG. Compare FX1
and FX2 separately against FX0 with identical clients/geometry. Never mask
an anomalous area after seeing it. Verify actual enabled nodes and renderer
before interpreting equal pixels.

The fixed output-local ROIs for the 800×600 images are: left effect interior
`(300,100,700,500)`, left boundary `(720,50,800,550)`, right boundary
`(0,50,80,550)`, and right reference `(250,250,550,500)`. Whole-image
differences are retained as well. The striped wallpaper alternates
`#f5f5f5` and `#0f192d` every 8 pixels horizontally; the test client's
translucent top buffer is premultiplied ARGB `0x88442010`. The first FX1
capture showed no pixel difference from FX0, so shadow visibility must be
established by an amended, documented fixture before T1 can pass.

Retain `SPIKE_DAMAGE`, `TEMPORAL_DAMAGE`, accepted output commits and native
headless presents when present in the private chain. For each transition,
compare changed-pixel boxes with the union of observed damage extents on
the same output, and inspect restored/old regions. Damage coverage is a
bounded observation: it is not minimum damage, every-frame correctness, or
submitted-buffer identity. Mark cache dirty and pass events with passive
private traces only if existing logs are insufficient. Never alter the
clip algorithm, shaders, public ABI or backend scheduler to obtain a pass.

**FEASIBLE** requires visibly active relevant effects in both standards,
permitted interior pixels in Mosaic, no prohibited adjacent-output writes,
correct settled restoration and damage evidence supporting each claim.
**PARTIALLY_FEASIBLE** means some effects pass but other effect/cache/damage
paths remain unproven. **INCONCLUSIVE** means visibility or origin cannot be
established. **BLOCKED** requires a reproducible pixel leak, stale cache,
crash or standard-layout regression, with a minimal retained reproducer.
Stop the affected scenario on a concrete leak; do not implement an
algorithmic repair in this ticket. Even FEASIBLE here does not qualify all
renderers, scaling, rotation, migration, saved buffers or SceneFX packaging.

Keep source patches and fixture code under
`tooling/probes/step20c-effects-damage/`; keep binaries, builds, logs, PNGs,
protocol-generated files and sockets outside Git. Source and complete raw
evidence manifests must be checked separately. Synchronize canonical
Architecture, Known Limitations, Roadmap, index and Changelog to observed
results, without changing UX. This protocol is updated with actual evidence
before the final local handoff; phase B is never committed in this ticket.

## Executed matrix and evidence

Final verification amendment: reuse the preserved
`step20c-presentation-identity/presentation-events.patch` in the private
Mosaic copy to retain native commit/present identities. The neighboring
`wev` reference keeps its natural floating size rather than receiving a
late resize request; its position stays `(250,250)`. Run the supplemental
effect/native-event control with **zero camera pairs**. The three already
measured camera pairs remain the restoration evidence; do not increase
that repetition count to obtain a preferred timing result.

**Protocol deviation discovered at final audit:** the default runner
repeated three camera pairs in each exploratory/reproduction/trace Mosaic
run. Across five such runs, **15 pairs actually ran**, exceeding the
ticket's global maximum of three. The final native supplement used zero
pairs, but that does not repair the earlier excess. All 15 retained runs and 342
PNGs are retained and included in the final raw manifest. Numerical pixel
claims use named comparable runs; selecting them does not make the whole
campaign compliant. The final runner locks a lab campaign and reserves a
persisted three-pair budget before launch, including failed attempts. Its
budget rejection was verified without creating another run. No further
compositor experiment was executed after discovery of the deviation.

The independent full clone at
`/tmp/step20c-effects-clone` contains the frozen repository commit
`542d9b9c945b22cf9134a4a643c8dc763b34607d` plus the local source
fixture. The private build and all selected evidence are in
`/tmp/swayfx-mosaic-nested-grab-OIWBj9xM/`. Its headless backend actually
loaded the SceneFX FX renderer with OpenGL ES 3.2 Mesa 26.2.4-arch1.1 on
AMD Radeon 780M (radeonsi); output GBM buffers were XR24 and XB24.
`WLR_RENDERER=pixman` did not imply Pixman rendering. Output IPC confirms
HEADLESS-1 `(-800,0)` and HEADLESS-2 `(0,0)`, each 800×600, scale 1,
normal transform. The translucent client supplied a real ARGB buffer;
the wallpaper used the documented eight-pixel alternating stripes.

The comparable, **untraced** three-run matrix finished without fixture
failure: ordinary `splith` 18 captures/3.822 s, private `splith` 18
captures/3.800 s, and private Mosaic 32 captures/5.762 s. The Mosaic run
included exactly three hide/return pairs. `effects-damage-results/
pixel-analysis.json` retains every capture hash, monotonic capture window,
whole-image/ROI difference and sampled transition damage comparison.

| Mode | FX1 shadow pixels on right output | FX2 blur pixels on left output | FX2 pixels on right output |
| --- | ---: | ---: | ---: |
| Ordinary `splith` | 27,594, columns 0–45 | 112,308 | 0 |
| Private `splith` | 27,594, columns 0–45 | 112,308 | 0 |
| Private Mosaic | 0 | 319,734 | 0 |

The ordinary and private-standard shadow screenshots and differential
pixels show a genuine spill across global `x=0`. The corresponding Mosaic
right screenshot remains byte-identical to FX0, so the tested overflow is
excluded. Private passive trace later observed an enabled shadow render
entry on HEADLESS-1 with a draw region clipped at local `x=800`. However,
Mosaic FX1 changed **zero sampled pixels on HEADLESS-1** even after
`gaps inner 24`; a visible authorized interior shadow was not established.
T1 therefore proves exclusion of the sampled right-output spill but does
not fully qualify shadow rendering inside the clip.

FX2 is a real filtered blur, not merely alpha compositing. At `y=300`,
the standard owner's stripe luminance standard deviation fell from about
50.32 (FX0) to 1.37 (FX2), and its mean adjacent-column contrast from
12.37 to 0.88. Mosaic's corresponding preselected strip fell from about
50.33 to 0.69 and 12.61 to 0.74. Enabled regular-blur render entries were
also observed in the private trace. The right output had zero FX2 changes
in all three modes. T2 is **FEASIBLE** for these sampled draw boundaries.
T3 source-sampling influence is **NOT TESTED**: no outside-only pattern
mutation with an unchanged interior was executed, and the viewport contract
does not yet prohibit a shader reading neighbors outside its draw clip.

For T4/T5, the three hidden captures were mutually pixel-identical; each
return was pixel-identical to the pre-hide FX4 reference on both outputs.
Thus no residual pixel was measured at the settled return. There is no
matched effects-off hidden-state reference, so absence of every effect
pixel in the hidden state is not established by repeat equality. T6 normal
effect disable/re-enable changed 112,308 left-output pixels after layout
return, then the owner closed and the exposed area was repainted. T7
`layout splith` succeeded while the owner remained mapped; its tree
geometry reverted to standard tiling and the subsequent enabled/disabled
effect toggles remained observable. Closure changes the exposed pixels,
but a fresh, identically arranged owner-absent reference was not captured;
complete left-output ghost exclusion after closure remains unqualified.
No grabbed XDG popup was opened, so
popup-effect ownership and dismissal remain **NOT TESTED**.

Private `TEMPORAL_DAMAGE` supplied 681 events in standard layout and 715
in Mosaic. For the sampled settled capture transitions, no changed pixel
fell outside the union of same-output damage extents between capture
windows; the uninstrumented ordinary control supplies no native damage
claim. These extents are often broad. This measurement does not prove
minimum damage, exact intermediate frames or output-buffer identity.
The initial matrix observed private output commits. A final supplemental
zero-camera-pair matrix reused the preserved native presentation listener:
private standard observed **82 commits / 80 presentations**, private Mosaic
**95 / 93**, with matching `(output, commit_seq)` identities. The two
initial commits of sequence 2 per private mode remain
**UNEXPLAINED / NO PRESENT OBSERVED**. This listener also confirms applied
tiled clip/scene geometry and removal on standard-layout return. The
supplement uses the natural-size neighboring reference and reproduces
the same shadow/blur difference counts as the original controls.

The optional `effect-trace.patch` is a passive private SceneFX patch,
base `37ccd723bef49e6891156ffafce8f549f01446cc` plus the preserved
historical patches. It records enabled shadow (type 3), optimized-blur
(type 4), and regular-blur (type 5) render entries, draw regions and the
optimized dirty flag. SHA-256:
`32056bd03177ad9b73e1f821bacd121dd39c3b8c078d96a8367f3b1ecc90bc01`.
That compiled variant is retained outside Git in
`effects-preparation-logs/effect-trace-compiled.patch`. The preserved
fixture adds WHY/CONTRACT/INVARIANT comments only, with final SHA-256
`6a89142afe2b019262033c7397d4c4593e1b7d0e63b0d620a546a2aa8ee29df7`.
The optimized entries included dirty=1 and dirty=0, but FX3 PNGs exactly
equaled FX2. Source inspection explains a limit of this comparison:
`output_configure_scene` already selects bottom-layer optimized blur for
tiled, non-overlapping containers, even with `blur_xray` disabled. The
regular blur node passes that selection through `use_optimized_blur`.
Therefore FX2 cannot be labeled a guaranteed non-optimized control, and
FX3 equality is not evidence that optimized blur was unavailable. Node
presence and dirty states were observed, but independent optimized-cache
invalidation correctness and a stale-cache test remain **NOT TESTED**.

The trace had a measurable fixture limitation. All 18 private-standard
PNGs matched the untraced run; 17/32 private-Mosaic PNGs matched. The
remaining 15 differed only in the right reference rectangle, where the
traced run's `wev` tree node was mapped but its checker did not appear.
Durations were 3.825 versus 3.800 seconds and 5.772 versus 5.762 seconds;
output commit counts were 80 versus 78 and 113 versus 112. Thus perfect
instrumentation neutrality is **not claimed**. The untraced matrix is
authoritative for pixel conclusions; the trace establishes node-path
presence only. No rendering algorithm, shader, scheduler or ABI changed.

The final raw manifest covers **890 files / 342 PNGs**, totaling
26,817,110 bytes: all contents of the **15 retained runs**, including
exploratory and excluded reference variants (configs, IPC, client/compositor logs,
captures, output states, exits and events), the wallpaper, generated runner,
preparation logs, compiled trace patch, source manifest, library metadata
and structured pixel analysis. Its SHA-256 is
`5fbe12b0312f2d82b3c5414251ae57345db8d25a83cfc018947308d40e752b42`;
all 890 entries verified. The structured analysis measures 174 PNGs in
eight named comparable/control runs; metadata identifies each role. The
separate 29-entry source manifest, including
the preparer chain, pinned patches, protocol inputs, clients and private
SceneFX/Mosaic sources, has SHA-256
`8fbd0cf927e3e2690a77aeaf2288072c183ef1dbe8f856cb63e0442454614d95`;
all 29 entries verified. The client patch SHA-256 is
`49070bb13ffc96a58e35693b34f1d25c60f824aba69507061211a44ecaeb8087`.
Exploratory runs remain excluded from selected numerical claims while
included in the complete raw manifest and the campaign repetition count.

**Verdict: PARTIALLY_FEASIBLE.** The tested inherited draw clip excludes
the demonstrated ordinary shadow spill, and the genuinely visible blur
stays within the sampled Mosaic output with exact settled camera returns.
Authorized interior shadow pixels, optimized cache behavior, outside-only
shader sampling, popup effects, saved buffers and intermediate frames are
unqualified. No concrete leak or standard-layout regression requires a
SceneFX redesign on these observations. The next independent STEP20C gate
should test scaling first, since this entire effects matrix uses scale 1
and normal transform; rotation, resize/migration, saved buffers and ABI/package
maintenance remain subsequent gates. STEP20C stays **NEXT** and production
multi-output Mosaic stays **NOT YET SUPPORTED**.

## Final technical validation and retained incidents

Shell syntax, Python AST, C17 client compilation, patch applicability,
private SceneFX/Mosaic builds, the Meson `mosaic-model` test (1/1), local
Markdown links and `git diff --check` passed. Native presentation callbacks
were later than their matching commit callbacks and reported presented
buffers; no relation is assigned to the two unmatched startup commits.
The actual private library linkage resolves `libscenefx-0.5.so` inside the
lab, wlroots 0.20.2 and Wayland 1.26.0 system libraries without replacement.
The preparer creates source hashes automatically; the analyzer creates the
complete chosen-run evidence manifest. No build/binary/capture is tracked.

Retained fixture incidents: the initial hand-written client patch failed
applicability before any experiment and the preparation trap removed only
its own failed lab; the corrected patch subsequently applied and compiled.
The late-resize neighboring-reference variant differed between untraced
and traced Mosaic and is excluded from perfect-neutrality claims. A source
manifest made during edits became stale when the analyzer was updated;
the final manifest was regenerated and every entry now passes. None is
silently converted into a compositor defect. The private build also retains
the existing upstream libinput enumeration warning; it compiled successfully.

All 15 run-specific runtimes created in this lab were removed. No lab
process or socket remained at validation. Production source, historical
patches, cumulative patch, `PKGBUILD` and UX are unchanged; phase B remains
local and uncommitted. The overall architectural conclusion is **UNDECIDED**:
the tested blur draw boundary is viable, but unexercised cache/sampling,
interior-shadow and buffer paths prevent a complete effects contract.

## Effects freeze V1 audit plan (2026-10-12)

Reverify the historical 890-entry evidence and 29-entry source manifests
without rewriting them. Audit the eight budget cases offline, including
launch failure, concurrency and interruption. Rebuild in a new full clone
with the pinned inputs and replay the three controls: zero camera pairs in
ordinary/private standard, one pair in Mosaic. The new reproduction has a
single three-pair campaign ceiling; no second lab is used to reset it.
Keep its manifest and results separate from the nonconforming historical
campaign. Audit mapped reference geometry and client events before assigning
any cause to the traced `wev` anomaly. No production or UX change is authorized.

### Independent audit of the historical reference incident

The retained FX0 IPC trees show `wev` as `floating_con`, visible=true,
at global (250,250) in each selected run. The untraced Mosaic reference
is actually 640×480; the traced Mosaic reference is 300×250. Both event
streams include floating enable, resize 300×250 and move 250,250, but the
client logs differ: only the traced variant receives the later 300×250
configure (serials 59/60); the untraced variant retains 640×480 (57/58).
The common runner maps `wev` on workspace 2 before mapping the owner on
workspace 1, then applies the floating/resize adaptation. `FX_TRACE` is
present in the traced compositor log. Mapping/IPC visibility is insufficient
to prove the checker was rendered. The anomalous 15 captures remain in the
historical manifest; no screenshot was removed. Geometry/configure timing
is a demonstrated confounder, not a proven cause. Logging causality and
perfect instrumentation neutrality remain unqualified. Main pixel claims
retain the untraced matrix as their reference.

The reservation block passed isolated executable tests of reservation
before launch, nonblocking exclusive flock, a launch returning failure,
SIGINT interruption, refusal after exhaustion, zero-pair operation with an
exhausted budget, and historical retained captures exceeding the limit.
The JSON reservation survives failure/interruption. Existing capture counts
are combined with the persisted count using max, not reset. These are local
process interruption tests, not a power-loss durability guarantee. An initial
audit harness failed before executing the reservation block because its
synthetic script path had insufficient parent components; the corrected
harness passed. No compositor or camera pair ran in that harness.

### Freeze V1 independent replay result

New full clone: `/tmp/step20c-effects-freeze-v1-clone`, HEAD
`542d9b9c945b22cf9134a4a643c8dc763b34607d`, with the source-only fixture
copied in before preparation. New lab:
`/tmp/swayfx-mosaic-nested-grab-xbAPurbe`. Preparation reconstructed pinned
SceneFX/Mosaic, checked each historical patch before application, rebuilt
private libraries/compositor and compiled the adapted C17 client. No
historical lab or binary was used as the reproduction source. The ordinary
control uses installed unmodified `/usr/bin/sway`, as the historical
fixture does; exact package-source byte identity is not claimed.

The three runs used `--camera-pairs 0`, `0`, `1` respectively; 18/18/24
captures, failure=null, compositor exit 0 and client exit 0. Helpers were
terminated by the runner (SIGTERM where recorded). FX1 right-output counts
are again 27,594 / 27,594 / 0; FX2 left counts 112,308 / 112,308 / 319,734,
with zero right changes in all modes. Mosaic's FX1 left remains zero;
interior shadow is still INCONCLUSIVE. The single camera return is
pixel-identical to FX4 on both outputs. Available sampled private damage
contains no changed pixel outside the recorded union; ordinary control
has no such native damage claim. Renderer again reports SceneFX FX,
GLES 3.2 Mesa 26.2.4-arch1.1, AMD Radeon 780M/radeonsi, wlroots 0.20.2.

The separate new 164-entry evidence manifest SHA-256 is
`46ac42d414a63ccf5f6f02e6d616fadb72b5533fa8a1b8f56687fdb9600e36c6`;
new 29-entry build-source manifest:
`3693b3be887a8781b3010f330ddeed2c1b69228228f0d579b13b847ccded0bde`.
Every entry verifies. The persisted budget is consumed=1; actual captured
pairs=1. Historical manifests separately verify 890/890 and 29/29 at their
original announced hashes. Historical patches, including the distinct
compiled trace provenance, are unchanged. The new source manifest records
the build inputs before subsequent documentation amendments; it is not
represented as a final-publication source manifest.

Shell syntax, Python AST, controlled patch application, C17 compilation,
private builds, model test 1/1, local links, unchanged production paths
and `git diff --check` pass. A Pillow getdata deprecation warning is
retained; it did not invalidate current analysis. No runtime was left by
the three runs. Verdict remains PARTIALLY_FEASIBLE. The historical 15
pairs remain supplementary measurements outside the authorized original
protocol; this new conforming reproduction does not retroactively authorize
them or erase the instrumentation-neutrality limitation.
