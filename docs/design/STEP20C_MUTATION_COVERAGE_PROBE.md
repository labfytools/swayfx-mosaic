# STEP20C mutation coverage and lifetime probe

**Status: EXPERIMENTAL / PARTIALLY_FEASIBLE.** The protocol preceded the
private tests and the findings follow below. STEP20C remains **NEXT** and production
multi-output Mosaic remains **NOT YET SUPPORTED**. This probe uses disposable
private sources and headless sockets; it changes no production compositor,
SceneFX ABI, package, user interaction or installed dependency.

## Question and observation boundary

Determine which applied mutations can change pixels, scene hit geometry,
pointer delivery or only metadata between output-state construction and an
executed input test. The existing `asi_applied_epoch` increments at selected
transaction and popup arrangements only. Equality of this partial counter
cannot establish a complete scene generation. Native output `commit_seq`
and headless `present` identify an output submission, not the scene used by
a later pointer event or a physically displayed frame.

The candidate minimal boundary is workspace/owner identity, applied scene
position, Mosaic tiled and owner-derived popup clips, surface hierarchy,
visibility, order, hit geometry and spatial transform. Client buffer content
is tracked separately from geometry. Output presentation identity is tracked
per output. XDG grab state controls delivery after a scene hit and must be
reported separately. These are hypotheses for comparison, not a new
production generation contract.

## Source and owner audit plan

Inspect pinned Mosaic/SwayFX `transaction.c`, `output.c`, `xdg_shell.c`,
`cursor.c`, `seat.c`, `arrange.c` and `mosaic.c`; private SceneFX clipping;
and the wlroots 0.20.2 scene/output/surface paths. Trace callers and
callbacks for node position, enabled state, reparent/order, creation and
destruction, clips, surface map/unmap, subsurfaces, input region, buffer
commits, scale/transform, damage, effects, animations, workspace/output
changes, focus and XDG grabs. Record the owner of each mutation and whether
it is immediate or transaction applied. A text search alone is insufficient.

The structured inventory in the private laboratory records source function,
object, pixel/hit/damage effect, transaction timing, current epoch coverage,
trigger and verdict. Every untriggered path stays **NOT TESTED**. Distinguish
pixel only, hit only, both, grab delivery only and metadata only. Preserve
monotonic timestamps, applied snapshots, native commits/presents, executed
hits and client events without assigning a fictional frame ID to input.

## Bounded experiments and stop rules

Use HEADLESS-1 `(-800,0)` and HEADLESS-2 `(0,0)`, both 800×600 at scale 1
and normal transform. Run an unmodified SwayFX `splith` control, private
`splith`, and private `mosaic` with trace-only instrumentation first.

* T1: camera 400 → 1280 → 400; correlate actual scene/clip mutation sites,
  partial epoch, output state, commit and present.
* T2: create grabbed A then B; close B while A remains, then close A;
  correlate hierarchy and hit changes, including uncovered sites.
* T3: commit changed client pixels at fixed intended size/position; establish
  a visible new buffer and corresponding native commit/present, then compare
  geometry and partial epoch.
* T4: choose one reproducible input-region, subsurface, order or geometry
  mutation from the source audit; compare scene hit and client delivery.
* T5: compare ordinary `splith` behavior in unmodified and private builds.

Use targeted captures only. Read a true output buffer only if a specific
remaining question requires it; time and bound any such copy per output.
`grim` is an independent capture, not a commit-buffer identity proof.

Audit rejected-commit and output-destroy lock cleanup first in source. A
safe private headless trigger may be used only if the backend and callback
lifetime permit it. Otherwise preserve a clearly synthetic branch test or
mark it **NOT TESTED**; no invalid state or unsafe output destruction is
allowed. Count each extra lock/unlock and retain exit status and logs.

Separate verdicts for mapping, runtime mutation scenarios and cleanup.
**FEASIBLE** covers only triggered bounded paths with matching geometry and
input and no blocking regression. **PARTIALLY_FEASIBLE** retains useful
evidence with important unqualified paths. **INCONCLUSIVE** means reliable
observation was unavailable. **BLOCKED** requires a reproduced mismatch,
unsafe lifetime, crash or blocking regression. The final architecture
answer is **UNDECIDED** unless the tested and source-audited boundary can
actually discriminate native SwayFX consistency from a required additional
transaction/generation contract.

## Source inventory and ownership findings

The audit used private Mosaic derived from published `1f59cb433bcdad006c23df10496cb4709551c624`
and the frozen patch chain, SceneFX 0.5 from
`37ccd723bef49e6891156ffafce8f549f01446cc`, and wlroots 0.20.2
source tag `0.20.2` (`d783533489e1f75d6886c2ab5c5960090ef268f8`).
The [structured inventory](../../tooling/probes/step20c-mutation-coverage/inventory.json)
is copied into the private lab with the scenario matrix. It distinguishes
observed paths from untriggered callers; it is not a claim that all scene
mutations have been exercised.

| Class | Actual owner and path | Effect and current coverage |
| --- | --- | --- |
| Camera, tiled clip, owner popup clip | `sway/desktop/transaction.c:arrange_output`, `arrange_popups`, `probe_clip_popup`; `sway/tree/mosaic.c` supplies logical camera | Pixels and hit. Transaction arrangement is marked; direct popup creation can call arrangement independently. T1 sampled. |
| XDG hierarchy and map lifecycle | `sway/desktop/xdg_shell.c:popup_create`, `handle_new_popup`, popup destroy; wlroots `types/scene/subsurface_tree.c` map/unmap/new-subsurface listeners | Pixels and hit. Creation/destruction themselves have no `asi_mark`; incidental arrangements may mark later. T2 A/B lifecycle sampled; subsurface mutation open. |
| Generic scene node and clip | SceneFX `types/scene/wlr_scene.c:wlr_scene_node_set_position`, `set_enabled`, `reparent`, `place_above/below`, `wlr_scene_tree_set_clip`, `scene_node_update` | Pixels, hit and conditional damage. The current counter covers only selected callers. Uninstrumented effects and SceneFX callbacks remain. |
| Client content | wlroots `types/scene/surface.c:handle_scene_surface_surface_commit`, `surface_reconfigure`; SceneFX `wlr_scene_buffer_set_buffer_with_options` | Pixels/damage; hit geometry only if dimensions, crop, transform or related state change. T3 fixed-size recolor sampled with no geometry change. |
| Client input region | wlroots `types/scene/surface.c:scene_buffer_point_accepts_input` → `wlr_surface_point_accepts_input`; SceneFX `scene_node_at_iterator` | Hit only for fixed pixels. T4 changed hit with the same partial epoch and unchanged sampled pixel. |
| Effects and decorations | `sway/desktop/output.c` render update; SceneFX rect/shadow/blur/buffer setters | Mostly pixels/damage, sometimes interactive rect geometry. Broad effect paths **NOT TESTED**. |
| Output and presentation | `sway/desktop/output.c:output_repaint_timer_handler`, commit/present listeners, destroy; wlroots output commit/state/headless deferred present | Per-output submission identity. Neither `commit_seq` nor `present` is an input generation. Fixed geometry only. |
| Grab, focus and IPC | `sway/input/cursor.c:node_at_coords`, `sway/input/seat.c:seat_pointer_notify_button`, wlroots XDG grab handlers | Grab changes delivery after scene hit; focus/IPC can change metadata or decorations without moving hit geometry. Client receipt is separate evidence. |

SceneFX's private tree clip intersects both visible render/damage bounds and
`wlr_scene_node_at()` traversal. Its setter calls `scene_node_update` when
the clip changes. wlroots' subsurface tree reconfigures position and order
on a surface commit and handles map/unmap/new-subsurface callbacks. A simple
search of Mosaic `asi_mark` sites would miss these transitive changes.
`transaction_progress()` applies queued state, arranges root, then marks the
partial epoch; it is not a commit/present barrier. The compositor event loop
orders individual callbacks, but an input callback need not observe the
same scene that a previously built buffer used.

## Runtime matrix and correlations

Lab: `/tmp/swayfx-mosaic-nested-grab-OWIvboDB/`. All nine T1–T5 runs
reported `failure=null`, used private headless sockets and exited through
runner cleanup. The unmodified SwayFX control lacks private native
commit/present logging, so its zero trace count is **no observation**, not
zero actual commits. For each private run, the only unmatched accepted
native commits were initial sequence 2 on each output; no headless present
was observed for those two. No B case used an output-buffer readback.

| Scenario | Private Mosaic | Private `splith` | Unmodified `splith` |
| --- | --- | --- | --- |
| T1/T2 one camera and popup lifecycle cycle | 70 accepted commits / 68 presents; two real A/B grabs; A/B created and destroyed | 57/55; two grabs; A/B created and destroyed | Native counts uninstrumented; two grabs; A/B created and destroyed |
| T3 same-size recolor | 34/32; pixel `(35,68,204)` → `(208,32,192)` | 36/34; same pixel change | Same pixel change; native counts uninstrumented |
| T4 empty/full input region | 42/40; sampled pixel stays `(35,68,204)` | 43/41; same sampled pixel | Same sampled pixel; native counts uninstrumented |

**T1.** The private Mosaic output-state stages show 400/1280/400 with
applied tiling positions `-400/-1280/-400` and tree clips
`(400,0,800,600)/(1280,0,800,600)/(400,0,800,600)`.
SceneFX logged the corresponding actual clip mutations, including a
hidden-owner empty popup clip at 1280. The sampled output stages reached
accepted native commits and headless presents. The epoch advanced at the
transaction and popup arrangements, but it can also advance when sampled
state is unchanged. The controls remained `splith` without a Mosaic camera.

**T2.** The private client created distinct A and B XDG surfaces with
two pointer-derived grab serials. `close_b` destroyed B; a subsequent right
button reached A, then `close_a` destroyed A. The same A-after-B input
result and lifecycle occurred in both standard controls. Direct creation,
map, and destruction of the scene objects are not individually covered by
`asi_applied_epoch`; later transaction arrangements caused separate marks.
The trace proves the sampled hierarchy/lifecycle and actual A delivery,
not a complete mutation-generation boundary.

**T3.** The private client issued a second `wl_surface.attach` and commit
for the toplevel at the same 420×320 size and unchanged intended position.
The new color was visible in a targeted capture after HEADLESS-1 native
commit/present 20 in the Mosaic run. Its COMMIT_ACCEPTED stage still had
epoch 12, tile `-400,0` and clip `(400,0,800,600)`; the prior relevant
stage had the same values. Thus a real content change was absent from the
partial epoch, as expected for a content-only mutation. The capture is
temporally correlated with the native event, not an exact read of its buffer.

**T4.** No popup or XDG grab was active. At one global point on the
toplevel, the executed `ASI_HIT` changed from its surface to `nil` after
the client committed an empty input region. Both hits recorded epoch 12,
tile `-400,0` and clip `(400,0,800,600)`. The pixel at that point remained
`(35,68,204)` in all three captures. Before and after restoration the
toplevel received a right-button press; while empty it received none.
Unmodified and private standard layouts likewise delivered two toplevel
presses, before and after the empty region, with unchanged sampled pixels.
An incidental later transaction mark does not erase the same-epoch hit
counterexample. This is an actual hit-affecting mutation missed by the
counter, without a demonstrated clipping defect.

**T5.** Standard layouts preserved the popup close order, A delivery after
B closed, toplevel recolor, and input-region behavior. Private trace logging
added native records but no reproduced blocking difference in these cases.
No exhaustive timing or effects comparison was made.

## Output-buffer lifetime audit

`sway/desktop/output.c:output_repaint_timer_handler` takes an extra probe
lock before `wlr_output_commit_state`. On a rejected commit it directly
unlocks that reference, before the state is finished. On an accepted commit,
it installs the lock in the output-scoped slot and starts a timer; a same
output buffer replacement releases the old slot. `begin_destroy` releases
an active slot before the output pointers/listeners are removed. The helper
clears the slot before removing its timer and unlocking. wlroots 0.20.2
`types/output/output.c:wlr_output_commit_state` emits the native commit
event synchronously after acceptance; `types/output/state.c` owns a separate
buffer reference until `wlr_output_state_finish`; headless `present` is
deferred and cancellation on output destroy is handled by wlroots.

One controlled **real private headless** case retained buffer ID 1 after
HEADLESS-1 `present` sequence 30, then stopped the compositor normally.
`begin_destroy` emitted exactly one `ASI_RELEASE id=1
reason=output_destroy`, age 863,608,059 ns; the compositor exited 0 and
the runner removed its private runtime. This qualifies that sampled
output-destroy path only. A C17 synthetic model passed once-only release
for direct rejected commit and repeated destroy release, but **no real
rejected commit was triggered**. Backend rejected-commit cleanup is
**NOT TESTED**. The synthetic result cannot qualify a real backend.

## Verdicts and architectural boundary

* Mapping: **PARTIALLY_FEASIBLE**. Source ownership and major classes are
  identified, but output migration, animations, effects, subsurfaces,
  stacking and other scene callers remain untriggered.
* Mutation scenarios T1–T5: **FEASIBLE for the bounded matrix**. Observed
  geometry, clip, hits and client delivery agree. T4 disproves completeness
  of `asi_applied_epoch`; T3 shows why pixels must not automatically be
  folded into a geometric generation.
* Cleanup: **PARTIALLY_FEASIBLE**. A real held-reference output destruction
  passed; the backend rejected-commit branch remains **NOT TESTED**.
* Overall probe: **PARTIALLY_FEASIBLE**. No sampled crash, invisible hit,
  clip leak or standard-layout regression was reproduced. This does not
  qualify production STEP20C or all SceneFX mutations.

The minimal candidate coherence boundary is an applied **geometry/hit**
identity for workspace and owner, scene position, viewport and tiled/root
popup clip, hierarchy, enabled state, order, surface hit geometry and
spatial transforms. A separate **content** identity may track attached
buffers and effect pixels without pretending they change hit geometry.
Native **presentation identity** remains `(output, commit_seq)` with the
headless present observation. Grab state must be associated with delivery,
not retroactively treated as the scene hit. This separation is a research
hypothesis, not an authorized production API or counter design.

**Architecture answer: UNDECIDED.** The current SwayFX/SceneFX live scene
was consistent with rendering and input in the sampled states, including
the input-region mutation. The partial epoch is demonstrably insufficient
as a generation identity. The evidence does not show whether existing
event-loop ordering alone can enforce the required cross-time relation
between an already built output buffer and a later hit during all relevant
Mosaic mutations. The smallest discriminating next experiment is a
controlled private mutation of hit geometry **between a known output-state
build and its deferred headless present**, with scene state sampled at
build, immediately before and after the mutation, at present, and at an
executed hit. It must retain one output's native `(output, commit_seq)` and
client delivery evidence. It should first use the proven input-region path,
then a Mosaic clip/owner change if the first case cannot distinguish the
contracts. Broader output/effect coverage follows only after this temporal
question is resolved.

## Reproduction, hashes and validation

The [fixture README](../../tooling/probes/step20c-mutation-coverage/README.md)
provides exact rebuild and replay commands. `mutation-results/` contains
the structured scenario matrix, lifetime record, copied inventory, and
source/artifact SHA-256 manifests. All generated builds, buffers, logs,
captures, sockets and manifests stay outside Git. The private client patch
applies on the frozen nested-client source; it does not touch Mosaic or
installed SceneFX/wlroots. The trace-only scenarios use no probe locks.

The private client patch SHA-256 is
`abee78ffa80729c395374c037f71b4a3e1158b81df6079ce6effc36afdf5eef6`.
The 15-source manifest SHA-256 is
`2875c22de8bb3a86d8d2f05296e9e141033980bb765e5e8958d5565ef47530ae`.
The 420-artifact manifest SHA-256 is
`f0761406414f3131017fc135c01caa4c643463117ae3f7a135d2b12ffa6ae2bc`.
The scenario matrix and lifetime record SHA-256 values are
`db2924f300fa139c9d16729ee62a17782698ecb517d42110e9507821c53d5aa1`
and `3a1e4900a83ebdcd9b9725caf18519f05de99aad8ab0b58104bd8c73f9bb1658`.
Both manifests passed `sha256sum --quiet -c` in the retained lab.

The original source manifest records two wlroots paths under the historical
`/tmp/mosaic-wlroots-0202-source/`; it remains unchanged evidence, not a
replay instruction. The corrected preparator fetches the audited wlroots
0.20.2 commit `d783533489e1f75d6886c2ab5c5960090ef268f8` into each new
lab and checks the two source hashes before analysis. The corrected analyzer
reads `LAB/wlroots/types/scene/{surface,subsurface_tree}.c`. New runs generate
new manifests with their own lab paths; the historical manifest hashes above
are preserved. This changes source provenance handling only, not T1–T5
instrumentation or the verdict.

An independent clone of `main` at `1f59cb433bcdad006c23df10496cb4709551c624`
with this source fixture overlaid rebuilt private SceneFX and Mosaic, then
replayed all nine T1–T5 mode/scenario runs and one output-destroy run in
`/tmp/swayfx-mosaic-nested-grab-no8fPnyy/`. All ten runners reported
`failure=null`. The three T1/T2 controls each made two real grabs. T3's
sampled color changed `(35,68,204)` → `(208,32,192)` in all three modes;
T4's sampled color remained `(35,68,204)` and each mode delivered exactly
two toplevel presses around the empty-region interval. Private Mosaic had
76/74 native commits/presents in T1/T2, 40/38 in T3 and 42/40 in T4;
private standard had 56/54, 33/31 and 42/40. Unmodified control native
counts remain uninstrumented. The output-destroy replay retained one lock,
released it once with `reason=output_destroy`, and exited 0; the C17 model
passed separately. The replay does not upgrade rejected-commit status.

The corrected `prepare.sh` SHA-256 is
`eb8482fc4cb6f96636d89a9510cd1e5de9750ebd16d55630e3af6585fe8933e6`;
the corrected `analyze.py` SHA-256 is
`be96ed839d957a51e724be79b78b0124b63a4c67691d5d409f88ab05dd60c4ab`.
The new 15-source and 364-artifact manifests hash to
`61a4e856e0f6cc26bccf661d7ec81f88256a0a3ee34e5bc7cbdf4063faa44f53`
and `11233d9e2f08f9c503d74e43157b787423bda50ef507b16a6670e0d64e235471`;
every entry passed `sha256sum -c`. The new scenario matrix and lifetime
record hash to `001ed3f324156692ae4b1e71298ac4c00f631b5d0a6839db024bc2e6489eed90`
and `8e862792d15b021a61f88b0e926b4d67678ada5a8e2d5ee930dc68511365a0b5`.
Artifact counts differ because the bounded replay produced different native
timings and capture files; the historical 420-file manifest was not rewritten.
The remaining **NOT TESTED** paths are not upgraded by a successful compile
or a synthetic model.
