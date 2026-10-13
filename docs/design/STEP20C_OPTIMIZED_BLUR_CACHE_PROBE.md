# STEP20C optimized blur cache invalidation probe

**EXPERIMENTAL / PARTIALLY_FEASIBLE; architecture UNDECIDED.**
The protocol below preceded the graphical runs; actual evidence follows. The
previous ticket published its saved-timeout phase at
`6fd8945d10d1072871bf66f639153a717d7ca758`. Its optimized-cache phase
was local until this separate evidence-freeze ticket. No graphical run is
authorized in the closed historical laboratory. STEP20A DONE, STEP20B EXPERIMENTAL, STEP20C NEXT, STEP20D–G
PLANNED; production multi-output Mosaic NOT YET SUPPORTED. No UX change.

## Question, historical evidence and source contract

Does a normal same-size commit from the actual background source update the
optimized cache and the final visibly filtered translucent pixels? Separate
logical dirty state, reconstruction attempt/result, GPU cache copies,
regular blur selection, final drawing clip and output damage. The
[effects/damage probe](STEP20C_EFFECTS_DAMAGE_PROBE.md) established visible
blur and sampled clipping, but did not qualify cache invalidation. Its
FX2 tiled path could already select optimized blur, so FX3 is not an
independent non-optimized control. Its reference/trace difference had
unproven causality. This campaign uses no animated reference.

Pinned inputs: SwayFX 0.6 `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`,
private Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754`, SceneFX 0.5
`37ccd723bef49e6891156ffafce8f549f01446cc`, installed wlroots 0.20.2
(previous audited source `d783533489e1f75d6886c2ab5c5960090ef268f8`).
Reconstruct archives from these commits and the unchanged preserved clip,
owner guard and passive timing/native-presentation patches. New passive
patches record borrowed identities only. No algorithm, shader, public ABI,
installed library, package or production source changes.

Source audit before instrumentation (pinned SceneFX and SwayFX):

1. `sway/tree/output.c:output_create` creates one optimized node under
   staging, initially sized zero. `arrange_root` reparents it to global
   `root->layers.blur_tree`, at its own output origin. `arrange_output`
   controls its size and enabled state; fullscreen disables it.
2. `root_create` orders shell background, shell bottom, optimized blur,
   tiling, floating, shell top, fullscreen, overlay, popup, seat and lock.
   Render-list traversal reverses its top-to-bottom list for drawing.
   The optimized source is the main output framebuffer at this stage,
   containing lower background/bottom composition, not arbitrary tiled
   content above the cache node.
3. `handle_surface_commit` in `sway/desktop/layer_shell.c` explicitly marks
   the output cache dirty on EVERY background/bottom surface commit,
   including ordinary pixel commits without layer-state changes. The
   existing comment says “Rerender the optimized blur on change”. Destroy
   of those layers also invalidates. This is the tested correctness intent.
4. `cmd_blur` and `cmd_blur_xray` mark all output optimized nodes dirty.
   Blur radius/passes/noise/brightness/contrast/saturation setters traverse
   and invalidate optimized nodes when their parameter actually changes.
   Output reconfiguration directly sets dirty for FBO-dependent changes.
5. `wlr_scene_optimized_blur_mark_dirty` skips disabled nodes, otherwise
   sets dirty and calls `scene_node_update`. `set_size` invalidates on a
   size change. Generic `scene_node_update` recomputes visibility and damages
   old/new regions; it does not universally invalidate optimized caches.
   Generic geometry/visibility/buffer mutations are not interchangeable
   with the Sway layer-shell commit hook. Other source owners need separate
   audit; absent mark calls alone are not proof of stale rendering.
6. `scene_node_visibility` ignores disabled nodes. The inherited private
   `scene_node_intersect_clip` restricts tiled leaves. Optimized nodes have
   a different global parent and do not inherit the tiled clip.
7. `wlr_scene_output_build_state` initializes FX offscreen buffers before
   blur damage expansion. `should_blur_node_extend_damage` sets `has_blur`
   for optimized regular blur at full strength; dirty optimized nodes,
   full damage and `apply_blur_region` intersections provide other routes.
8. `scene_entry_render` first requires a nonempty visible/damage intersection.
   An optimized regeneration then requires `has_blur`, enabled blur data and
   dirty. `fx_render_pass_add_optimized_blur` calls `get_main_buffer_blur`
   with the current main framebuffer, and copies blurred and unblurred
   results into the two output caches. It returns false with no offscreen
   buffers or no blur result; dirty is cleared only on true and otherwise
   retained for a later visible blur. A true return is not itself pixel proof.
9. `fx_render_pass_read_to_buffer` performs a GPU texture draw/copy, not CPU
   readback. It returns void and can skip a copy if texture import fails;
   trace attempted and completed draw calls separately from regeneration.
   No mass GPU readback is planned.
10. `fx_render_pass_add_blur` selects `optimized_blur_buffer` when optimized
    and strength 1; a lower strength reblurs `optimized_no_blur_buffer`.
    Ordinary nonoptimized blur instead uses the current main framebuffer.
    Sway's `config->blur_xray || !could_container_overlap(con)` explains
    optimized selection with xray disabled. Keep opacity 1 and SHM alpha
    partial, so buffer alpha and compositor blur strength remain distinct.
11. `fx_offscreen_buffers_try_get` finds/creates an output-owned addon.
    `fx_render_pass_init_offscreen_buffers` obtains output-size framebuffers.
    `fx_framebuffer_get_or_create_custom` reuses equal sizes, drops/resizes
    different sizes and reports allocation failures; failure destroys the
    offscreen set. No output resize is exercised here.
12. Framebuffers use allocator buffers, EGL images and GLES FBOs/stencils.
    The output addon destructor drops all five buffers, finishes the addon
    and frees the set; renderer teardown also owns cleanup. Observed object
    destruction is not proof of every driver/GPU reference lifetime.
13. Optimized regeneration copies the output-sized destination region.
    Final regular blur receives visible intersect damage and ancestor clip.
    Shader sampling expands/clamps to output framebuffer bounds and can
    read beyond a tiled draw clip. Such reads are not automatically leaks;
    the decisive contract is absence of forbidden final contributions.
14. `apply_blur_region` expands damage for sampling/artifact prevention and
    includes it in output-state damage. Client buffer damage, scene damage,
    cache copy regions and output damage are separate. Captures and extent
    coverage cannot enumerate intermediate frames or native PNG identities.

## Fixed geometry, clients and comparators

H1 `(-800,0)`, H2 `(0,0)`, both physical/logical 800×600, scale 1, normal.
C0: pinned pristine SwayFX splith, pristine private SceneFX without new logs.
C1: private SwayFX splith with inherited clip/guard, private SceneFX plus
passive logs. C2: same private compositor/renderer with Mosaic enabled.
C0/C1 provide a bounded visual instrumentation comparison; source/library
clip differences prevent claiming perfect log-only causal isolation.
Each configuration has exactly one reserved run, with identical client
sources and blur settings. No installed `/usr/bin/sway` is executed.

A background layer-shell SHM client explicitly binds HEADLESS-1, uses layer
BACKGROUND, all four anchors, exclusive zone -1 and no keyboard input. It
remains mapped and submits opaque 8-pixel vertical stripes A (#f5f5f5 /
#0f192d) and B (#20c0e0 / #b02040), same dimensions, by normal attach,
damage_buffer and commit. Generated layer-shell protocol comes from pinned
wlr-protocols `b010a03648b88d143236de193bddbfea0c08bc84`, with its XML hash
and URL retained before code generation. XDG XML is recorded and hashed.
The glass client uses premultiplied ARGB `0x88442010`, no opaque region,
normal XDG configure/ACK and no animation; the H2 XDG static reference
`org.mosaic.StaticReference` uses fixed XRGB #303038. A separate transparent ARGB
filler with blur disabled provides a second tiled cell without occluding
the exposed source ROI. Only the glass receives scoped blur commands. All identities are discovered by app ID.

Before scoring, verify background surface/buffer, output, layer, scene parent
under shell_background below blur_tree, real client and compositor commits,
source pattern visible outside glass and within FX0 alpha blending. Correlate
renderer/FBO/cache identities, actual optimized regular use and reconstruction.
A node alone cannot pass the gate. FX0 blur disabled; FX2 blur enabled,
radius 5, passes 3, noise 0, brightness/contrast/saturation 1, shadows off,
corner radius 0, xray off, opacity 1. Log real renderer (not environment hint).

ROIs predefined in output-local pixels: glass interior `(520,100,720,500)`,
exposed source `(20,100,160,500)`, H1 boundary `(720,50,800,550)` and H2
whole image `(0,0,800,600)`. Record full RGB diffs/bboxes/counts, ROI luminance
standard deviation and mean absolute horizontal adjacent-pixel contrast.
FX0/FX2 must show filtering beyond simple alpha. Geometry is recorded from
IPC and actual scene buffer draw positions; Mosaic camera is calibrated once
from current IPC camera and logical cell geometry to put glass across x=0.
Calibration is not P5 and occurs before P1. No focus or camera change during
P1–P3. Standard cells use the same splith/tiled identities without camera.

## Ordered protocol and gates

P0 map A, filler, glass, H2 reference; settle outputs/geometries. Capture
both outputs FX0, capture H2 a second time >=0.7s later and require complete
RGB equality. Enable FX2, capture both. Stop dependent cases if renderer,
source or visibly optimized filtering gate fails. Reserve capture before grim.

P1 submit B once with a normal same-size background pixel commit. Keep
position, geometry, alpha, focus, camera, output, clip and parameters fixed.
Capture both after stabilization. Observe dirty, attempt, return, copies,
regular use, damage and final pixels separately. No forced dirty in P1.

P2 (private C1/C2 only) perform one normal `blur disable` / `blur enable`
cycle, with no parameter or source change, then capture both. Audit/observe
cmd_blur's dirty route. This is a positive reconstruction control; never
substitute this image for P1. C0 keeps visual natural-mutation control only.

P3 submit A once, same geometry, capture both; compare with P0 FX2 and count
any residual B pixels. P4 uses the C2 boundary and tiled clip observations
from all these stages, verifies final draw bounds and whole H2 stability.
The global output cache is not claimed to be a tiled-owned clipped cache.
P5 optional one hide/return camera pair only if earlier gates pass and it
adds a distinct assertion. Omit if main mutation/cache evidence suffices.

Retain scene damage, physical extents, native output commits/presents where
instrumented, output-buffer identities and capture windows. Compare damage
union on the correct output against stabilized RGB changes, with no claim
of minimal damage, every frame or DRM presentation. Exit compositor through
its explicit private socket and retain teardown events before owned-process
fallback cleanup. Destroy/remove only fixture-owned sockets/process groups.

## Budgets, isolation and stop rules

One independent persistent campaign ledger under LAB, exclusive flock,
fsync and reservation BEFORE launch/action. Failed reservations consume;
no refunds, reset or repeat mode. Max 3 total runs, 1 per configuration,
4 background mutations/run (initial A counts), 1 explicit cycle/private run,
1 optional camera pair globally, 20 PNG/run and 60 globally, 150s/run.
Run deadline enforced by parent watchdog; all subprocess operations bounded.
No migration, resize, transform, hotplug, saved episode, popup, close
animation or scheduling test. Offline ledger tests precede any compositor.
Logs/files are bounded and monitored; only a finite client/renderer matrix.
Private 0700 runtime, explicit WAYLAND_DISPLAY, SWAYSOCK and swaymsg -s,
headless backend, no inherited daily sockets/library overrides. Generated
files/builds/captures/logs outside Git; home filesystem LAB avoids the
observed /tmp quota. Cleanup retains evidence, removes private socket tree.

FEASIBLE: all real renderer/source/optimized/filtering gates, natural required
reconstruction, correct stabilized A/B/A pixels, P2 positive reconstruction,
Mosaic boundary exclusion, stable H2 and supportive damage in measured matrix.
PARTIALLY_FEASIBLE: working subset with unqualified mutation/rebuild/damage.
INCONCLUSIVE: optimized source/use or filtering is not exercised/distinguishable.
BLOCKED: a measured stale image violates the identified source correction
intent, forbidden pixels, lifetime defect/crash or blocking standard regression.
Absent dirty alone cannot classify BLOCKED. Preserve failed fixture facts;
never spend an extra run to repair a calibration. No algorithmic correction.
Broader sources, partial damage, failure paths, GPU references, every frame,
other outputs/renderers and ABI/package remain NOT TESTED unless measured.

## C0 fixture failure and pre-run amendment

The sole C0 reservation stopped before captures (0.97s): two same-size
layer configures caused the original client to submit A twice. Actual
mutations are 2, with the second charged after observation, not reserved
before submission. This protocol deviation is retained; no budget is
refunded and C0 is never relaunched. Pristine graphical cache/filtering
control is NOT EXERCISED. The exact C0 runner/client and binary hash are
retained in its run directory. The remaining C1/C2 clients ACK configures
without drawing and submit every image only on an explicitly reserved
runner command. This is fixture correction, not a renderer/SceneFX change.
The standard library/renderer identity from C0 remains usable; its missing
visual comparison cannot be replaced by private source claims.

## Retained campaign and actual observations

LAB: `/home/fy59/swayfx-mosaic-optimized-blur-_ppdud_y/`. No prior `/tmp`
laboratory is a reconstruction dependency. `prepare.py` archives the pinned
project commits, clones SceneFX at its pin, applies unchanged historical
patches, adds separate passive traces and builds privately. New XML inputs,
protocol hashes, current and failed-C0 client/runner sources are preserved
in the [source fixture](../../tooling/probes/step20c-optimized-blur-cache/README.md).
Generated protocols, binaries, logs, PNGs and builds remain outside Git.

| Configuration | Duration | Actual background images | PNGs | Explicit cycles | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| C0 pristine splith, pristine SceneFX | 0.972 s | 2 × A | 0 | 0 | Fixture failure before graphical gates; no repeat |
| C1 private splith | 4.075 s | A/B/A (3) | 11 | 1 | Real cache update, central pixel equality; boundary equivalence unresolved |
| C2 private Mosaic | 4.434 s | A/B/A (3) | 11 | 1 | Same update; measured final clip excludes H2; boundary equivalence unresolved |

All three run reservations are consumed. Actual totals: 8 background images,
22 PNGs of 60, one cycle per private mode, zero camera pairs, one computed
C2 calibration, no migration/resize/transform. C0's second image was charged
only after observation; this is a retained reservation-protocol deviation,
although no numerical limit was exceeded. Every C1/C2 image was explicitly
reserved before its draw command. The shared ticket ledger refuses another
LAB, another run per mode, refunds and corrupt/empty state. No extra
untraced graphical run was possible after C0 failed. Instrumentation
neutrality is **NOT TESTED**, not inferred from similar private outcomes.

### Renderer, layer source and actual use

All three compositors report SceneFX FX, OpenGL ES **3.2**, Mesa
**26.2.4-arch1.1**, AMD Radeon **780M**. `/proc/PID/maps` records the correct
private SceneFX library and installed wlroots 0.20 library. C0 uses a fresh
pristine SceneFX build; C1/C2 use the same private clip/timing/cache-trace
library. Environment `WLR_RENDERER=gles2` is not the renderer evidence.
The FX pass is additionally proven in C1/C2 by successful offscreen setup,
GPU blur/copy and regular optimized-use traces. C0 has renderer identity
but no qualifying graphical/native-cache control.

C1/C2 background server commits show surface resource 3, layer 0
BACKGROUND, mapped=true, global `(-800,0)`, full buffer damage 800×600,
and the namespace `mosaic-dynamic-background`. Their actual scene parent
is the output shell-background tree, whose parent is the global
shell-background tree. The optimized node's actual parent is blur_tree.
The pinned root's applied layer order draws background/bottom before blur
and tiling afterwards. `OPT_BUFFER_DRAW` correlates the surface and its
buffer to a full-output draw before `OPT_GPU_REBUILD`. Client logs record
A/B/A, normal SHM buffers, attach/damage/commit and release. Server sequences
2/3/4 correlate to those three content commits; resource/buffer pointers can
be reused after release and are never treated as permanent image IDs.
The exposed source ROI contains the exact A or B stripe colors. Thus the
mutated surface is a real lower cache source, not a tiled proxy above it.

The glass buffer is fixed premultiplied ARGB `0x88442010`. Its compositor
opacity/blur strength stays 1; alpha blending and blur strength are distinct.
Only the glass receives scoped blur enable/disable. Shadow and corners are
zero; radius 5, passes 3, noise 0, brightness/contrast/saturation 1 and xray
false remain fixed. Both private runs record `optimized=1`, strength 1,
non-null selected cached framebuffer FBO 11 in `OPT_BLUR_USE`. This proves
actual optimized selection independently of xray and node presence.

### Natural invalidation, explicit control and cache ownership

For each private mode, P1 B and P3 A each show one real source commit,
one dirty set for H1, one H1 regeneration attempt/result=1, GPU source blur,
two cache copy draw completions, dirty clear to false and regular optimized
use. H2 has **zero regeneration** in these natural-mutation windows.
The source-only Sway layer-shell hook provides the natural dirty; no blur
command, camera, focus, geometry or parameter mutation is inserted in P1.
P2's one normal disable/enable cycle records six dirty-set observations,
two successful H1 and two successful H2 regenerations, then optimized glass
use on H1. A global dirty consequence of scoped cmd_blur is source-defined;
H2 rebuilds in P2 do not demonstrate contamination. H2 pixels remain stable.

Successful regeneration, completed GPU texture-draw calls and final pixels
remain separate evidence. `fx_render_pass_read_to_buffer` has no success
return or driver fence proof. No GPU readback was added. Initial optimized
nodes start dirty=false, are invalidated by normal setup and source changes,
and clear to false on observed successful regenerations. P3's last stable
H1 render observes dirty=true before regeneration and dirty=false after it;
teardown invalidation is a separate lifetime phase.

| Mode | Output | Offscreen set | Optimized framebuffer | Size | Reuses |
| --- | --- | --- | --- | --- | ---: |
| C1 | H1 | `0x563e16fee600` | `0x563e16fe4750`, FBO 11 | 800×600 | 18 |
| C1 | H2 | `0x563e16f3d430` | `0x563e16f43950`, FBO 5 | 800×600 | 10 |
| C2 | H1 | `0x55e94e85cee0` | `0x55e94e852310`, FBO 11 | 800×600 | 19 |
| C2 | H2 | `0x55e94e6a8f00` | `0x55e94e7b13e0`, FBO 5 | 800×600 | 10 |

Each set retains one blur object and one distinct unblurred object during
its observed lifetime. Normal explicit private compositor exit logs cache
set destruction and exactly one destructor event for each optimized blur
and unblurred FBO object. No resize/allocation-failure path is exercised.
This demonstrates sampled object cleanup, not every GPU/driver reference.
Clients exit with Wayland EPIPE (32) after controlled compositor shutdown;
the compositor exit code is 0 in every run, with no observed compositor
crash. Every private runtime directory/socket is removed and owned child
processes are reaped. There is no daily-session IPC or global kill command.

### Pixels, filtering and the retained boundary anomaly

| Measurement, identical in C1/C2 central ROI | Value |
| --- | ---: |
| FX0 luminance standard deviation | 51.165618 |
| FX2 luminance standard deviation | 0.132211 |
| FX0 horizontal adjacent luminance contrast | 12.351341 |
| FX2 horizontal adjacent luminance contrast | 0.015453 |
| B natural versus B explicit, central changed pixels | 0 |
| A initial versus A returned, central changed pixels | 0 |
| H2 whole RGB differences, every comparison | 0 |

FX0/FX2 changes 240,000 H1 pixels in C1 and 192,000 in C2. These contrast
measurements establish actual filtering beyond fixed alpha compositing.
A→B changes all 480,000 H1 pixels, including the exposed source and glass.
The 80,000-pixel central glass ROI changes with B, equals the independent
explicit reconstruction result exactly and returns exactly to measured A.
This establishes freshness in that central ROI; it is not a whole-cache PASS.
All six H2 PNGs per private run are whole-RGB identical, without masks.

| Whole H1 comparison | C1 changed pixels | C2 changed pixels | Maximum RGB channel delta |
| --- | ---: | ---: | ---: |
| B natural → B explicit | 36,776 | 33,915 | 6 |
| A initial → A returned | 38,308 | 35,340 | 6 |

The B comparison bboxes are `[400,800)×[0,600)` in C1 and
`[480,800)×[0,600)` in C2; A return has the same respective bboxes.
Differences concentrate near output/filter boundaries; central/source ROIs
are exactly unchanged in these equivalence comparisons. The predefined
right boundary ROI changes **19,007** pixels for B natural/explicit and
**20,486** for A return in BOTH private modes, with maximum differences
4 and 5 respectively. These nonzero differences are preserved, never
masked, and cannot be promoted to exact full-image restoration.
This is a shared private standard/Mosaic anomaly, not a demonstrated
Mosaic-only defect. Pristine comparison is missing, so an unmodified
SceneFX runtime attribution remains unproven.

A bounded offline audit of `render_blur_segments`, `get_main_buffer_blur`,
`blur1.frag`, `blur2.frag` and FX texture creation found a plausible history
mechanism: downsample writes only a reduced top-left domain in full-size
ping-pong FBOs, while upsample taps can reach beyond that freshly written
domain; GL_CLAMP_TO_EDGE bounds the whole texture rather than the reduced
valid domain. `edge-model.py` applies the pinned kernels with ideal bilinear
sampling and 8-bit rounding to the retained regeneration/source sequence.
It exhibits history dependence without any renderer edit. In the predefined
boundary ROI, absolute model/native mean channel error is 0.199–0.518,
with 96.67–97.91% of channels within one level; maximum residual is 4.
This supports the hypothesis but does not establish native intermediate
FBO tail contents, GLES precision or causality. No model threshold turns
the anomaly into a PASS, and no shader/algorithm correction is authorized.
A proven stale-image invariant violation is not claimed on that model alone.

### Mosaic clipping and damage

C2 calibration derives delta **-320** from its current camera **480** and
actual glass geometry; applied camera becomes **160**. These coincident
values are measured here, not historical IDs/constants in the fixture.
The regular glass blur is actually at global `(-320,0)`, size 640×600,
so its geometric right edge is +320 on H2. Its final H1 draw is
`[480,800)×[0,600)` output-local, equivalent to global `[-320,0)`.
`PI_SCENE` records applied tiling scene `(-160,0)`, local clip
`(160,0,800,600)` under the H1 output parent. The global tiled viewport is
`[-800,0)×[0,600)`. No target regular-blur draw on H2 is observed; complete
H2 RGB stays unchanged throughout. The cache still covers its full 800×600
output, with a different owner than the tiled final clip. No input event or
universal shader-sampling confinement is asserted.

`OPT_OUTPUT_BUFFER` identifies successful rendered output-state buffers and
physical output damage extents. Native commit/present traces retain their
own identities; no PNG is assigned to a particular native presented buffer.
For all four stabilized H1 transitions in each private mode, the union of
available output-damage extents leaves **zero changed pixels uncovered**.
Client damage, scene TEMPORAL_DAMAGE, cache full-output GPU copies and
output-state damage are recorded separately. Extent coverage proves neither
minimum damage nor every intervening frame. P5 hide/return is NOT EXERCISED:
P1/P3 already address the distinct source mutation, and a camera pair would
not resolve missing pristine control or the boundary source/sampling issue.

## Decision and next gate

`SWAYFX_MOSAIC_OPTIMIZED_BLUR_CACHE_PROBE=PARTIALLY_FEASIBLE`.
Architectural conclusion: **UNDECIDED**. Actual output-scoped cache source,
optimized selection, natural dirty/reconstruction, visible filtering,
central A/B/A freshness, sampled final Mosaic clipping, stable H2 and
sampled teardown are established in C1/C2. Whole-cache correctness is not
established: boundary differences remain, C0 graphical control failed, and
instrumentation neutrality is NOT TESTED. There is no basis here to merge a
private patch or to require a Mosaic-specific redesign.

The next separate rendering gate should complete pristine and untraced
controls and discriminate reduced-domain edge sampling/history at fixed
geometry before the ABI/package gate. Retain this campaign's exact pixels,
source traces and offline model; do not repeat V1 runs or silently strengthen
its result. A later targeted native observation may be justified only by a
predefined bounded hypothesis. Other source layers, partial damage, hidden
owner/camera transitions, output resize/migration, scaling/rotation, failure
paths, driver references and intermediate frames remain NOT TESTED.
STEP20C stays NEXT, production multi-output NOT YET SUPPORTED.

## Offline validation and preservation

Python AST (all current and original fixtures, no bytecode), XML parsing,
controlled protocol regeneration byte equivalence, both C clients compiled
separately as C17 with `-Wall -Wextra -Werror -Wno-unused-parameter`, locked
ledger exhaustion/concurrency/cross-LAB/corruption tests, pinned private
patch applicability and full reconstructed source equivalence passed.
Pristine SwayFX source was independently compared with its pinned archive.
Final private SceneFX/Mosaic and pristine builds pass; Meson `mosaic-model`
passes 1/1. Existing pinned SwayFX libinput switch warnings are retained;
the new trace's pre-run radius-format warning was corrected before graphics.
The two passive instrumentation insertion failures and C0 fixture failure
remain in raw preparation/run evidence. No failure was hidden by retrying
an already-consumed graphical configuration.

Local Markdown targets, complete tracked/new-file diff, whitespace and
bytecode/generated-artifact protection were checked. Production `sway/`,
`include/`, Meson files, cumulative patch, PKGBUILD, UX and AGENTS match the
pre-ticket baseline. Installed compositor/libraries, daily IPC/session,
QuickShell and dotfiles were not modified or targeted by any command.
Cache/source/state/output JSON categories, all run logs, client sources,
configs, captures, native events and exit statuses remain in LAB/results
and LAB/runs. The failed C0 has zero images; no visual result is invented.
All owned processes are reaped and private runtime/socket trees removed.
That validation preceded publication of this historical probe. The new
evidence freeze does not upgrade STEP20C.

Final source manifest: **1006 entries**, SHA-256
`0067ad29b7363d2850f8a7418b271c4e5e7044f6a08fd8e85f39b63413a2d152`.
Final evidence manifest: **106 entries**, SHA-256
`3a83bbf303217d020b5dadb29e357836975a08055540bae006b5c770feb1d34c`.
Every entry was available and matched its recorded digest. The earlier A
913/46-entry historical manifests were reverified after B and remain
unchanged. The B H2 PNG digest in both private modes is
`4471e93ccb6cf3ff4970f61fce405431a228af598d2f1f030a3b7586962ecd7a`;
all six images per mode share it and match complete RGB without a mask.

## Independent evidence freeze (2026-10-13)

The new freeze audited the initial main at `6fd8945d10d1072871bf66f639153a717d7ca758`
and directly queried both remotes at that same commit. All **1006 source**
and **106 evidence** manifest entries were available and matched, before
publication-only documentation edits. The two original manifests and the
historical laboratory remain byte-identical; neither analyzer nor runner was
executed there. A copy of every pre-freeze fixture file is retained in
`/home/fy59/swayfx-mosaic-cache-freeze-audit-m7o528qk/fixture-before-freeze/`.
The historical source manifest names the old README at its repository path;
after this freeze its matching original bytes are in that snapshot. This
provenance distinction is explicit, not a regenerated historical manifest.

An independent reconstruction in the same audit directory applied the full
private patch chain to the pinned archives, then compared all relevant source
bytes to the historical compiled trees. All patches apply without forced
hunks. Both new trace patch hashes match the recorded values:
`a0fd5a64156a79b1605ff3b52bd9accb20390199b2b36e1970389f5086b68f39`
and `b83ff12bf24ee879cc713a134b0c312e9b8bd1b4034ecc2aea124d55a743ebb7`.
C17 builds of the corrected and failed-C0 clients with fatal warnings, both
SceneFX builds, pristine SwayFX, private Mosaic and Meson mosaic-model passed.
The actual corrected callback, extracted verbatim for a bounded offline
harness, ACKed duplicate 800×600 configures without incrementing image
submissions. Locked ledger tests passed; no historical reservation changed.

Independent whole-RGB recalculation reproduces 36,776/33,915 changed B pixels,
38,308/35,340 changed A-return pixels, maximum channel delta 6, zero central
differences and stable H2. The offline model was rerun into a separate output
directory and reproduces its historical JSON exactly. These checks establish
evidence integrity, not native FBO causality or instrumentation neutrality.

The narrow `.gitattributes` patch rule preserves original unified-diff bytes:
blank context lines carry a required leading space and context source tabs
follow a diff marker. C, Python and Markdown retain ordinary whitespace
checks. Source-context applicability and reconstructed source equivalence
were checked independently of the patch-file whitespace exclusion.
