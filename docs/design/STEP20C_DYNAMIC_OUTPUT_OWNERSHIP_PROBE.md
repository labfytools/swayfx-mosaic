# STEP20C dynamic output geometry and workspace ownership probe

**EXPERIMENTAL / PARTIALLY_FEASIBLE measured subset.** The protocol below
was recorded before dynamic runs; the measured campaign follows it.
STEP20A DONE, STEP20B EXPERIMENTAL, STEP20C NEXT, STEP20D–G PLANNED.
Production multi-output remains NOT YET SUPPORTED. No UX change, production
repair or package/dependency change follows from this probe. The later
dynamic-evidence freeze ticket authorizes publication of this report and its
source-only fixture, without publishing raw laboratory captures.
The fractional evidence freeze passed at `8345aff0f97d381b768233021fc5c881ec794094`
on local main, Forgejo and GitHub, with a clean worktree at the gate.

## Scope and historical evidence

The [fractional probe](STEP20C_FRACTIONAL_SCALING_PROBE.md) qualified sampled
static 800×600 logical boxes with scales 1/1.25/1.5, real nested grabs,
negative origins, boundary hovers, visible blur and excluded shadow spill.
Its result remains PARTIALLY_FEASIBLE. Independent opaque tiled spill,
interior shadow, restored camera hit, optimized caches, source sampling,
saved buffers and intermediate frames remain unqualified. This campaign
asks whether applied viewports and popup clips follow real output resize
and workspace migration. It does not infer atomicity from IPC success.

## Pinned source audit before measurements

SwayFX control: `fd71a6bdc061bd633b488ae7b83e8a6981d22f86` (0.6).
Private Mosaic base: `cd550382b311efdbfe3ed892f4e1d281d852e754` plus the
preserved popup/hidden-owner, temporal damage and presentation patches.
SceneFX: `37ccd723bef49e6891156ffafce8f549f01446cc` (0.5) plus its preserved
private inherited clip and damage trace. wlroots source:
`d783533489e1f75d6886c2ab5c5960090ef268f8` (0.20.2), matching linked version.
The private reconstruction uses the fractional preparer; no old /tmp lab is
a dependency. New instrumentation only reads state in existing callbacks.

| Path | Ownership and ordering established by source |
| --- | --- |
| sway/config/output.c, apply_output_configs | Pending mode/scale is built (scale rounded to 1/120), output states built then backend committed. finalize_output_config places each output in wlr_output_layout; a second pass output_update_position copies the actual logical layout box, then arrange_layers, arrange_root and transaction_commit_dirty run. Optimized blur layer is marked dirty. Input mappings/cursor images are reconfigured, pointer focus cleared and cursor_rebase called. Backend commit precedes final layout/scene arrangement: no atomic applied-scene claim. |
| wlroots types/output/output.c | effective_resolution divides transformed physical dimensions by scale into integer logical dimensions; normal 1200×750 at 1.25 yields 960×600. |
| sway/commands/output.c and output/mode.c | Normal output command parser supports mode/resolution, scale and position subcommands; the command and resulting IPC geometry must both be checked. |
| sway/commands/move.c | move workspace to output uses handler_context.workspace, detaches/reattaches it, arranges old/new outputs, focuses an inactive node within that workspace and considers pointer warp. The usual command/transaction path applies dirty state. |
| sway/tree/workspace.c, workspace_move_to_output | workspace_detach removes old list membership, clears pending owner and dirties workspace/output. output_add_workspace preserves the object ID and attaches the new pending owner. Moving the last old workspace creates a replacement workspace with a different ID. Destination's old empty workspace can be destroyed by workspace_consider_destroy. |
| sway/tree/arrange.c | arrange_workspace takes new owner usable_area and global origin; floating coordinates adjust separately. apply_mosaic_layout computes cells/gaps and clamps logical scroll to real row overflow. Four 640-wide cells without gaps occupy 2560; viewport 800/960 gives maximum 1760/1600. Initial camera 400 remains within both bounds; the clamp branch is not promised exercised. |
| sway/desktop/transaction.c private candidate | Current output/workspace lists reparent tiling layers; tiling node local x=usable x+gap-scroll. Its clip local x=scroll, width/height=usable area minus gaps. Thus scene global position plus clip origin gives viewport. arrange_root subsequently calls arrange_popups. |
| private root popup clip | Actual view container current workspace/output and current top tiled ancestor identify owner. Applied tiling clip/global scene coordinates are intersected with output box. Hidden-owner guard tests applied owner rectangle. Root popup clip becomes global viewport minus root-popup scene origin. No owner pointer is retained in clip state. |
| sway/desktop/xdg_shell.c | Nested popup_create inherits view; parent scene tree preserves hierarchy. Root descriptor uses view content_tree as relative node; configure/unconstrain uses pending owner on initial commit or explicit reposition. Destroy listeners free popup tree. Migration alone must not be assumed to reconfigure XDG geometry. |
| SceneFX types/scene/wlr_scene.c | set_position and reparent trigger scene_node_update. Cached visibility and new bounds determine affected output damage. set_clip updates inherited clip and scene visibility. node_coords sums ancestors; node_at checks inherited logical clip before surface input. Damage subtracts output origin then scales/expands/transforms into physical buffer-local bounds. Output commits/resizes can invalidate whole damage. |
| wlroots types/wlr_cursor.c | Unmapped virtual pointer normalizes into actual combined logical output-layout box. No physical scale in pointer coordinates. Focus/grab dismissal and scene hit remain separate observations. |

These paths identify pending owner mutation, output logical geometry update,
scroll clamp, transaction application, tiled reparent/position, global popup
rearrangement, clip calculation, pointer rebase and old/new damage. They do
not establish a universal generation ID or a distinct frame for every IPC.

## Geometry, scenarios and hypotheses

D0: H1 1000×750 scale 1.25 at (-800,0), logical 800×600; H2 800×600 scale 1
at (0,0), logical 800×600. Both normal. Workspace 1 starts on H1; workspace 2
contains an ordinary reference on H2. Retain workspace IDs, tiled IDs/order,
XDG map/grab serials, focus and output ownership throughout.

D1 requests `output HEADLESS-1 mode 1200x750 scale 1.25 position -960 0`.
Require physical 1200×750 and logical (-960,0,960,600), H2 unchanged.
D2 restores mode 1000×750 and position -800,0 at the same scale.
D3 moves the verified workspace 1 to H2; D4 observes its pre-opened A/B
hierarchy and any legitimate popup_done. If destroyed, distinct newly grabbed
objects may be created after migration, without asserting persistence.
D5 returns the same workspace to H1. Do not compare the replacement old
workspace with the moved workspace. No additional output/workspace transitions
are allowed for fixture repair after budget consumption.

Hypotheses: viewport follows applied usable area; scroll remains logical and
within recalculated extent; root clip follows current owner, nested clip is
inherited; old output redraws its new active workspace without Mosaic residue;
logical pointer calibration survives changed negative origin. A normal XDG
close or focus warp is not itself a clipping defect.

## References, input, stabilization and damage

Use stable dark background, deterministic red ordinary tiled client, distinct
SHM toplevel, yellow A and green B, plus ordinary wev references. Identify
opaque toplevel geometry/pixels explicitly; translucency from the historical
fractional client is not an opaque-overflow control. A new opaque client build
may replace only SHM alpha, without changing the compositor. Standard tiling
is not a negative opaque-spill control. Independent tiled overflow without
clip ablation remains PARTIAL if not exercised.

Before each capture retain get_outputs/get_workspaces/get_tree and current
private scene/clip trace. Require stable repeated output/workspace geometry,
then retain native accepted commit/present where available and capture twice
for settled equality; timestamps do not imply atomic input/frame identity.
Unestablished stability is INCONCLUSIVE. Compare the vacated old output to its
new active workspace/reference, not the pre-migration image.

Pointer normalization is recomputed from active output rectangles on every
injection: min_x/min_y, max right/bottom, extent and global-minus-min. The
injector accepts that logical extent per event; it never applies scale. After
resize/restoration/migration/return, empirically calibrate ordinary references
on both outputs using enter OR motion and independent (+40,+20) local delta;
retain button delivery and boundary crossing. Calibration failure invalidates
dependent input assertions. Visible owner, popup interior, clipped portion,
new/vacated viewport points and old/new output points use applied coordinates.
Scene hit and client delivery under grabs are distinct. Exterior click tests
are done after persistence observations so normal dismissal cannot obscure D4.

Damage traces are already physical buffer-local extents. Compare changes only
between matching physical-size settled images; for a changed-size buffer,
report new-area coverage separately. No second scale conversion. Optimized
blur, every intermediate frame, minimal damage, all effects and saved buffers
remain NOT TESTED unless directly exercised.

## Budgets and stopping rules

One persistent campaign ledger and exclusive flock spans all three modes.
Reserve each dynamic action before IPC launch; failed launched actions consume
the reservation, interrupted reservations remain consumed. Each mode gets at
most one D1, D2, D3 and D5: six resize/restoration actions and six migrations
globally. Camera maximum one pair globally; planned consumption zero pairs.
Initial camera setup 400 is not an extra hide/return pair. Never reset ledger
or use another lab to bypass counts. Failed modes remain in matrix. Static
analysis and offline budget tests need no dynamic reservation.

All private sources/builds/runs/PNGs/logs/manifests stay in one disposable LAB;
only source fixtures and passive patches live under tooling/probes.
No algorithm, shader, damage policy, callback order, hit testing, headless
backend or public ABI change. No commit/push in B.

FEASIBLE requires applied requested transitions, identity/owner/clip correctness,
settled pixel/hit agreement and compatible measured damage, with standard
controls passing. PARTIALLY_FEASIBLE leaves qualified transitions but open XDG,
effects/input/damage cells. INCONCLUSIVE means refused geometry or inadequate
fixture/state evidence. BLOCKED requires reproduced forbidden pixels/hits,
wrong-owner clip, corruption/crash or blocking ordinary-layout regression.
Preserve minimal reproducer and stop affected assertions; do not repair
production. A refused command, lawful popup_done, absent redundant enter,
normal focus change or correct camera clamp alone is not BLOCKED.

## Retained fixture incident before the Mosaic run

The ordinary control completed all four dynamic actions and retained D5 popup
captures, then timed out during D5 left-reference calibration. Both references
had migrated with workspace 1. The sequential adapter moved the left reference
to its target before moving the right reference away; the latter occluded the
former. The right log recorded the requested (20,30) enter while the left log
did not. This is reference-placement ambiguity, not evidence of a Mosaic input
failure. The private-standard run already launched with the same source is
retained. No dynamic action is replayed. The final fixture moves both references
before scoring either, and uniquely retained per-run sources distinguish the
versions. Earlier D5 input-dependent assertions remain NOT TESTED if unscored.

## Measured campaign — 2026-10-12

**CURRENT evidence: EXPERIMENTAL / PARTIALLY_FEASIBLE.** The protocol above
was written before measurement. Laboratory:
`/tmp/swayfx-mosaic-nested-grab-0zJrQnLj`. All sources were reconstructed from
pinned Git inputs, not copied from the historical fractional lab. Private
SceneFX/Mosaic and pristine SwayFX built; patched clients passed C17 -Werror.
Model Meson test passed 1/1. Runtime uses actual FX GLES 3.2 Mesa
26.2.4-arch1.1 / Radeon 780M; the inherited pixman environment request does not
identify the renderer actually selected by SwayFX.

Three attempted runs retained 230 PNGs: ordinary control 72, private splith 72,
private Mosaic 86. Both controls ended with the documented reference-occlusion
calibration failure after all four transitions and D5 captures. Their compositor
exit status was zero; they are **not** whole-run PASS. Mosaic completed with
failure=null. No failed action/run was replayed or removed. Per-run generated
source SHA-256: both controls
`795dd53d7bcc2ea40f35cba7d88c97af316a6057d7631f214fdbd1a38dc0da4c`;
Mosaic corrected-reference fixture
`63cff2a4521e06f1d7f9ba04f4a7049956134fcfe589e89e1352ee03d31e5096`.

### Actual geometry, identity and camera

| Stage | H1 actual physical / scale / logical global rect | Workspace 1 owner | Workspace ID / tiled ID |
| --- | --- | --- | --- |
| D0 | 1000×750 / 1.25 / (-800,0,800,600) | H1 | 6 / 8 |
| D1 | 1200×750 / 1.25 / (-960,0,960,600) | H1 | 6 / 8 |
| D2 | 1000×750 / 1.25 / (-800,0,800,600) | H1 | 6 / 8 |
| D3 | restored D0 geometry | H2 | 6 / 8 |
| D5 | restored D0 geometry | H1 | 6 / 8 |

H2 stayed physical 800×600 / scale 1 / (0,0,800,600), normal transform.
All three modes applied this matrix, confirmed by outputs/workspaces/tree,
physical PNG dimensions and retained repeated-state observations. Workspace
1's tiled order stayed [7,8,9,10]. In standard layouts its owner width changed
200→240→200; Mosaic remained four 640-wide cells, row extent 2560.

The base fixture initially set camera 400; calibration focus/temporary reference
insertion subsequently produced **observed camera 640** before D0 scoring.
No additional explicit camera scroll or hide/return pair was issued. The
camera stayed 640 in D0/D1/D2/D3/D5 scored snapshots. Actual maximum overflow
was 1760 at width 800 and 1600 at width 960, so conservation is valid and the
maximum-bound clamp branch is **NOT TESTED**. Do not claim scroll 400 persisted
or that a clamp event was experimentally demonstrated.

| Stage | Applied tiling global origin | Local tiled clip | Derived global viewport |
| --- | --- | --- | --- |
| D0 | (-1440,0) | (640,0,800,600) | (-800,0,800,600) |
| D1 | (-1600,0) | (640,0,960,600) | (-960,0,960,600) |
| D2 | (-1440,0) | (640,0,800,600) | (-800,0,800,600) |
| D3 | (-640,0) | (640,0,800,600) | (0,0,800,600) |
| D5 | (-1440,0) | (640,0,800,600) | (-800,0,800,600) |

All 42 pre-capture tiled-clip observations matched their actual output rect.
DO_POPUP records for actual owner 8/workspace 6 derive the same three global
viewport rectangles from root position plus local clip, and change owner_output
H1→H2→H1. Ignore view-less popup-layer descriptors with owner_id=0 as tiled-XDG
ownership evidence. A callback output label is the observer, not necessarily
the popup's owner. No stale old-owner clip is observed in retained stable states.

The last H1 workspace's departure created workspace 3, ID 13, on H1. On return,
H2 acquired a replacement workspace 2 with **new ID 14**; its initial workspace
2 had ID 5. Workspace 1 remained ID 6 throughout. Calibration later moves the
ordinary floating references between these active workspaces; that is not a
workspace migration or a scientific camera action.

### Popups, input and pixels

Every recorded grab used the real unchanged received button serial: 10 grabs
in each control, 12 in Mosaic. A/B were pre-opened for each transition. Both
migrations retained the then-open root/nested hierarchy in sampled captures;
D3 had no popup_done. The D3 exterior right click later produced one A and one
B popup_done in all modes, then a distinct valid hierarchy was recreated before
D5. D5's cumulative done counts remained 1/1: no new migration dismissal was
observed. Wire IDs can be reused after explicit destruction; recreated chains
are distinct objects. Configure/ack/map, client logs and private root-tree
identities are retained; this does not promise universal popup persistence.

Mosaic ordinary-reference calibration passed on both outputs at D0/D1/D2/D3/D5,
with independent logical (+40,+20) local motion and left/right delivery. Pointer
normalization changed 1600×600→1760×600→1600×600 from applied output bounds,
with min_x -800→-960→-800, never physical scaling. Both standard controls passed
D0/D1/D2/D3; their final D5 calibration/hit is NOT TESTED because of the retained
occlusion incident. Mosaic owner right buttons arrived at all five stages,
and visible popup interactions used the new owner's applied coordinates.

Exterior (-20,190) on old H1 after D3 and (20,190) on H2 after D5 delivered no
Mosaic popup button. **These are outside points, not demonstrated clipped
popup portions**: at the measured camera 640 the Mosaic b_cross A/B boxes fit
inside the viewport. No extra camera pair was spent to force spill. Thus
migration clip reassociation is directly traced, but clipped-portion input
and a real Mosaic popup overflow challenge after migration remain NOT EXERCISED.
Controls did show real nested spill on H2 before migration: 15,860 green pixels
in D0/D2/D5 and 260 after D1. Do not substitute those differently arranged
standard boxes for a same-geometry negative Mosaic control.

Mosaic D3's vacated H1 was exactly 750,000 dark background pixels, with zero
owner/A/B colors; D5's vacated H2 was exactly 480,000 background pixels.
These full-image checks support absence of any stale rendered residue in those
settled samples, rather than checking only exact popup colors. The destination
showed owner and permitted yellow/green popup pixels: D3 H2 owner 264,148,
A 42,200, B 39,000; D5 H1 owner 412,930, A 66,075, B 61,125. All 24 Mosaic
capture-pair comparisons were identical. All 72 corresponding standard/private-standard PNGs were pixel-identical,
including their retained final D5 captures.

The restored opaque XRGB SHM owner is actually visible and interactive, unlike
using the historical translucent S1 name as opaque proof. Its source buffer
stays 420×320 while configure sizes differ; compositor applied container,
surface and rendering sizes must remain distinct. Ordinary wev references also
retain their 640×480 surface despite smaller requested floating frames. No
independent unclipped **tiled opaque spill** control was exercised. That
assertion remains PARTIAL; a private clip ablation was not performed. Newly
included/vacated viewport-specific hit points were not independently scored.
Shadows/blur were disabled here; dynamic effects, optimized cache correctness,
saved buffers and intermediate frames remain NOT TESTED.

### Damage, commit/present and boundedness

Private splith recorded 1,760 damage events; Mosaic recorded 1,585.
Mosaic native traces contained 412 accepted commit identities, 404 present
identities, 404 matching pairs. Private splith recorded 362 / 354 / 354.
The terminal unpresented commits include teardown; counts alone are not a
render defect. Ordinary control has no native damage/commit instrumentation.
No frame identity is inferred for a screenshot or input event.

Physical extents covered every measured equal-size settled pixel difference.
For Mosaic migration D3, H1/H2 changed 625,428 / 370,119 pixels; D5 changed
578,428 / 400,119. Each had zero changed pixels outside available extents.
For resize, compare common buffer-local pixels and all new-buffer area rather
than asserting equal-sized images: D1 adds 150,000 physical pixels and changes
223,000 common pixels; D2 changes 52,974 common pixels. Coverage outside the
available physical extent union was zero. Retired old-only buffer area, minimal
damage and each intermediate frame are not qualified by this calculation.
Broad/full-output invalidation is compatible with these observations.

The persistent locked ledger contains exactly D1/D2/D3/D5 once per mode:
**reconfiguration 6/6, migration 6/6, camera pairs 0/1**. Both failed controls
consume all their launched actions. Offline tests exercised the actual lock,
persistence, duplicate/exhaustion and missing-ledger rejection. The inherited
lock descriptor also stays open in the generated child. No automatic refunds,
reset, additional lab or dynamic replay was used.

All three runtime directories were removed and all owned client/compositor
processes terminated. No production files, historical patches, cumulative
patch, PKGBUILD, UX, AGENTS, system libraries, desktop session or dotfiles
changed. No live IPC, install, STEP20D, commit or push occurred in B.

### Architectural answers and remaining gate

| Question | Evidence-backed answer |
| --- | --- |
| Q1 viewport after logical resize | Yes in measured D1/D2: 800→960→800 logical width with corresponding origins. |
| Q2 camera | Conserved 640 within real maxima 1760/1600; maximum clamp branch NOT TESTED. |
| Q3 tiled clip | Yes, local clip width and global scene translation yield each applied output rectangle. |
| Q4 popup output owner | Yes for mapped owner-8 root/nested hierarchies in the sampled states; current owner follows workspace H1→H2→H1. |
| Q5 stale clip | None in stable retained traces/captures; no every-intermediate-frame proof. |
| Q6 workspace identity | Workspace 6/name 1 and tiled 8 survive both migrations; order/layout retained. |
| Q7 last old workspace | Departure creates workspace 13/name 3 on H1; return creates workspace 14/name 2 on H2. These are not workspace 6. |
| Q8 old pixels | Vacated outputs are exactly their new empty workspace's dark background before reference calibration. |
| Q9 new rendering/effects | Owner and permitted A/B pixels appear at the new scale; effects disabled and NOT TESTED. |
| Q10 hit/viewport | Calibrated visible owner/popups and exterior points agree; newly included points and clipped-popup portions NOT EXERCISED. |
| Q11 negative-origin pointer | Yes, measured logical extent changes to 1760 and both reference deltas/buttons pass in Mosaic. |
| Q12 damage coverage | Available physical extent unions cover settled changes/new area; no minimal, retired-buffer or per-frame guarantee. |
| Q13 ordinary rules | Cursor rebase/focus changes, replacement workspaces, explicit popup destruction/recreation and exterior-click popup_done are ordinary paths, not clip defects. |
| Q14 redesign | No reproduced wrong-owner clip, invisible hit, crash or persistent pixel leak requires redesign here. Incomplete assertions are not a proof of complete correctness. |
| Q15 next gate | Rotation is the next distinct geometric gate: this campaign changes owner and scale/origin/width but uses only normal transforms. Before production, separately close opaque overflow, maximum-clamp, migrated clipped-popup input, remaining effects/saved buffers and SceneFX ABI/package gates. Repair the reference fixture before future comparisons; do not replay this exhausted campaign. |

**DYNAMIC_OUTPUT_OWNERSHIP_FEASIBLE_FOR_TESTED_MATRIX**, limited to the stable
normal-transform geometry/ownership subset actually measured. Overall probe
**PARTIALLY_FEASIBLE** due to the standard D5 fixture failures, unexercised
maximum clamp/migrated popup spill and effects/input/damage scope limits.
STEP20C remains NEXT; production multi-output NOT YET SUPPORTED.

`SWAYFX_MOSAIC_DYNAMIC_OUTPUT_OWNERSHIP_PROBE=PARTIALLY_FEASIBLE`

### Final provenance and technical validation

The 916-entry source manifest `results/source-sha256.txt` has SHA-256
`a4071f6bf3d9a0825954c1b0c504502a3d4c007d83eab2bae8de51fb58594ee4`.
The 529-entry complete raw-evidence manifest `results/evidence-sha256.txt`
has SHA-256
`48d8126b84a000ca2ac6ca3e7e7d1b465b6e63bda18c168a128fe6fe660c695a`.
Both verified entry by entry. Source inventory includes the complete pinned
wlroots 0.20.2 source archive used for audit; replay depends on pinned sources
and installed matching wlroots, not on an old temporary lab.

The subsequent freeze audit verified all 529 original evidence-manifest entries
and the expected manifest SHA-256 before invoking the offline analyzer. That
analyzer rewrote `results/evidence-sha256.txt` in the temporary lab, replacing
the original 529-entry file with a 528-entry inventory of the files present at
replay time (SHA-256 `3da3a499d5e398fbc85e85c0bd07bf0bf2bc9778e111b4ac7bae2e036e8af6a2`).
The raw runs and their 230 PNGs were not replayed or removed. The original
manifest bytes were not retained separately; its pre-replay verification is
recorded by the audit transcript and the closeout digest above. This is an
audit-tool side effect and a provenance limitation, not a new measurement or
a reason to upgrade the scientific verdict.
The source manifest likewise verified before this documentation freeze. Its
historical fixture-README entry records SHA-256
`0b35a83a1fb92e83be5d27c9acf9a38a4d017dc5a1018bf3a706b76b52f695f4`;
the published README now documents the later freeze and therefore no longer
matches that one historical source entry. The scripts and experimental patches
were not changed.

Final adapter reconstruction reproduced the measured corrected Mosaic generated
runner byte-for-byte offline, without reservation or launch. New private patches
reverse-applied then forward-applied in isolated files and reproduced measured
source bytes. All Python modules and retained generated runners passed AST;
shell syntax, C17 -Werror, private/pristine builds and model 1/1 passed.
Documentation links and ordinary git diff --check passed. Complete source-only
diff evidence is retained outside Git; new unified patch context whitespace
must be distinguished from whitespace in C/Python source additions.

Phase A publication remains `8345aff0f97d381b768233021fc5c881ec794094` on
local main, Forgejo origin/main and GitHub github/main. The gate worktree was
clean. B changes are confined to this report, its source fixture, README index,
Architecture, Known Limitations, Roadmap and Changelog, with an empty Git index.
No B commit or push occurred. All source/patch/package/session invariants above
remain in force.

A post-publication recheck of the historical fractional source manifest still
matches its recorded SHA-256 and verifies 38/39 paths against the current tree.
The sole changed path is the fractional fixture README: its historical bytes
(`6e800abfa2d48c047640fde787747fb9a6e6021152cb3718aafa7abea09f3bf5`)
remain in the independent freeze clone, while the published README includes
later freeze replay instructions. The historical 1,986-entry evidence manifest
and both independent freeze manifests verify completely. No historical
manifest was rewritten and no measurement source was changed by this README
update.

`SWAYFX_MOSAIC_FRACTIONAL_SCALING_FREEZE=PASS`

`SWAYFX_MOSAIC_STEP20C_FRACTIONAL_FREEZE_AND_DYNAMIC_OUTPUT_OWNERSHIP_V1=PARTIALLY_FEASIBLE`
