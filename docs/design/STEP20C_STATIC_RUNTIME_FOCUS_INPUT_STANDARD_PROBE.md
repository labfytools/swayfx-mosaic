# STEP20C static runtime focus, input and standard-return probe

**EXPERIMENTAL / INCONCLUSIVE. Historical campaign frozen as evidence.**
Phase A published `5e2961d05b7b33252718aabc4dbf787724f79ef0` to both remotes,
with a clean worktree. The original phase B was local and unpublished; the later evidence freeze publishes its sources and findings without replay.
[Architecture](../ARCHITECTURE.md), [UX](../UX.md), [Packaging](../PACKAGING.md)
and [Roadmap](../ROADMAP.md) remain authoritative. STEP20A DONE, STEP20B
EXPERIMENTAL, STEP20C NEXT, STEP20D–G PLANNED; production multi-output
NOT YET SUPPORTED. No production, algorithm, shader, package or UX change.

## Historical evidence and exact candidate

The [previous runtime](STEP20C_STATIC_RUNTIME_AND_PACKAGE_CONTRACT.md) remains
PARTIALLY_FEASIBLE / UNDECIDED. It captured h2-reference.png while workspace 2
was focused, then h2-mosaic.png after workspace 1/client setup and Mosaic.
The full RGB comparison failed by 23,807 pixels, bounding box (0,0,800,600).
Changes outside the unchanged reference interior support focus/title/border
variation. No target colors appeared on H2; 182,214 survived on H1. Neither
cropping borders nor a new successful run can retroactively pass that comparison.

Reuse only the historical staged binary from
`/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt/stage-static/usr/bin/swayfx-mosaic`:
SHA-256 `f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b`,
ELF build ID `942db64269640778ee433e5970ba1100bc60f94c`.
Verify original/copy hash, executable regular-file mode, ELF dependencies and
system wlroots SHA-256 `7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
No SceneFX DT_NEEDED or loaded SceneFX shared mapping is allowed. Stop before
launch if identity is unavailable. No SceneFX/Mosaic build or binary alteration.

Historical C17 saved-client and static-reference plus the extent-adapted virtual
pointer are reused from manifest-verified source. Their historical executable
files are not entries of those manifests: rebuild only these clients from the
verified C/generated-protocol sources, record commands and resulting hashes.
No client algorithm changes. Target alternates two opaque colors on configure;
reference remains RGB (48,48,56) across focus/configure changes. Pointer uses
1600×600 logical extent and global-x + 800 normalization.

## Single-run protocol and stop gates

One new private LAB, mode-0700 runtime, explicit private Wayland display and IPC
socket, WLR_BACKENDS=headless. Every swaymsg uses -s. Only owned process groups
are stopped; preserve exit codes and verify no residual process/socket.
A 150-second deadline and bounded logs apply. No pristine run, no popup.
HEADLESS-1=(-800,0,800,600), HEADLESS-2=(0,0,800,600), scale 1, normal.

Create reference on workspace 2, then filler and target on workspace 1. Both
reference and filler have org.mosaic.StaticReference App ID. Therefore do not
use the broad for_window App ID rule: obtain reference con_id while it is the
only reference and apply `[con_id=ID] border none` in private IPC. Check reference
PID, workspace/output, border none and zero border width; filler keeps its normal
border. Keep focus_follows_mouse no. No daily configuration changes.

Activate Mosaic, read real applied owner/tiling traces and IPC scroll. Compute
one signed camera delta from horizontal content offset and configured width,
then reread scene/scroll. The historical +160 is not a constant. No further
camera command or hide/return. Focus must initially remain target/workspace 1.
If later normal focus changes move the camera, retain that observation and stop
any assertion needing unchanged Mosaic geometry; do not correct it.

PI_OWNER gives an applied scene owner, not a buffer. IPC rect/window_rect/deco_rect
and the client's last real COMMIT size are separate evidence. Use the actual H1
painted color rectangle to identify vertical content and pick an interior point.
Correlate measured paint with horizontal scene offset and client width; never
label the old source_box y estimate a native buffer coordinate. PI_SCENE local
clip plus output-parent origin and tiled translation gives global viewport.

After complete Mosaic setup and sole calibration, park pointer at (-790,590),
wait for stabilization, capture H2 twice at least 500 ms apart. Check 800×600,
full-frame reference color, border, focus/workspace and exact whole RGB equality.
Store PNG hashes and snapshots. No ROI, no tolerance. Failure stops before input.

V1: capture H1/H2, retain positive target-color count on H1, zero on H2, and
whole-H2 equality to preflight. Require content crossing x=0 and clip ending
there. Save every differing pixel coordinate/color on failure; stop dependent tests.

V2: choose a point at least 20 pixels inside the actually painted H1 rectangle,
outside decorations and borders. One right press/release; require actual target
BUTTON 273 states 1 then 0 with recorded serials, no reference delivery. A move
alone is never input proof. Preserve available passive scene hit and Wayland logs.

V3: choose an H2 point within the geometrical continuation of the target content
and the full-frame reference interior. One right press/release; require zero
new target BUTTON events and two real reference events. Record focus after click,
park pointer, stabilize and recapture whole H2 with exact equality. Do not infer
PASS from neither client receiving input.

V4: address the target con_id with layout splith (after V3 global focus is H2;
a bare layout command could affect the wrong workspace). Verify workspace identity,
applied splith, target still mapped, applied owner and PI_SCENE clip_valid=0 on
H1 and ordinary H2. Capture H1/H2. Choose a fresh interior target-colored point
from the standard image, inject one click and require actual target press/release.
Park pointer and recapture H2 after focus transition. Require stable H2 and no
residual clip. Do not reuse the Mosaic click point blindly.

## Budget, analysis and classification

Persistent ledger, exclusive flock, atomic durable reservation before run,
each PNG, each click, camera and bounded pointer movement. Failed reservations
remain consumed; no reset/refund or alternate LAB. Offline tests must precede run.
Limits: run 1, pristine 0, SceneFX/Mosaic builds 0, camera adjustment 1, each of
three named clicks 1, PNG 12, pointer moves 8, duration 150 seconds. Expected
PNG count 8. All generated artifacts stay outside Git. Seal source and evidence
manifests once after collecting results, then verify every entry without rewriting.

Keep client damage requests, scene/output damage extents and stabilized PNGs
separate. No claim of complete intermediate frames or native output-buffer/PNG
identity. Root/nested grabs, other geometry, migration, saved buffers/effects,
full semantic ABI, other wlroots pairs, legal notice closure and named release/
security owners are NOT TESTED or remain open. D1–D4 stay approved privately.

FEASIBLE requires every V1–V4 assertion and conformant binary/dependencies,
no crash or blocking defect in this matrix. PARTIALLY_FEASIBLE retains demonstrated
principal properties with unqualified input/return/pixels. INCONCLUSIVE means an
unreliable fixture. BLOCKED requires demonstrated pixel/input leakage, runtime
ABI defect or standard regression. Focus/calibration error alone is not a clipping
failure. Architecture: STATIC_MOSAIC_FOCUS_INPUT_STANDARD_FEASIBLE_FOR_TESTED_MATRIX,
STATIC_MOSAIC_FOCUS_INPUT_STANDARD_REQUIRES_REDESIGN, or UNDECIDED respectively.

## Independent future reconstruction (not authorized in this campaign)

A later campaign can archive pinned Mosaic cd550382b311efdbfe3ed892f4e1d281d852e754,
SceneFX 37ccd723bef49e6891156ffafce8f549f01446cc and wlroots
d783533489e1f75d6886c2ab5c5960090ef268f8, without the old LAB. Apply the ordered
three SceneFX and five Mosaic patches listed in the
[static distribution report](STEP20C_SCENEFX_STATIC_DISTRIBUTION_CONTRACT.md).
Use SceneFX default_library=static/examples=false, its uninstalled pkg-config
provider and Mosaic --prefix=/usr --bindir=bin with mosaic-package=true,
swaybar/swaynag=false, man-pages=disabled, default-wallpaper=false,
sd-bus-provider=libsystemd, werror=false. Build in independent directories,
qualify exact shared wlroots, model, ELF, notices/stage and new authorized
runtime budgets. Preserve toolchain/generated protocols/patch hashes. This is
source reconstruction, not a promise of byte-reproducibility or permission to
substitute another binary in this ticket.

The [fixture](../../tooling/probes/step20c-static-runtime-followup/README.md)
provides the bounded runner, offline tests and evidence collector.

## Completed campaign — retained fixture failure

`SWAYFX_MOSAIC_STATIC_FOCUS_INPUT_STANDARD_PROBE=INCONCLUSIVE`

Architecture: **UNDECIDED**. LAB:
`/home/fy59/swayfx-mosaic-static-followup-nhwejz6u`. One run, 2.661722 seconds.
The unique runtime stopped before the first screenshot, movement or button.
No restart, second LAB, binary/algorithm repair or budget refund occurred.

### Identity, setup and measured state

The copied executable retains SHA-256
`f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b`,
ELF build ID `942db64269640778ee433e5970ba1100bc60f94c`, mode 0755.
Readelf and ldd -r pass; process maps resolve the qualified system wlroots
0.20.2 binary with SHA-256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
No shared SceneFX or historical LAB dependency appears in the runtime mappings.
Meson/model evidence is reused from A; no new compositor/library build.

Three C17 client-only builds from manifest-verified sources passed syntax and
compilation and produced the same bytes as the historical executables:

| Client | SHA-256 |
| --- | --- |
| saved-client | `3d5d0c5e446b995c210006a5bafe0d86dd5f32a228e1b7137d12af6ec9e217da` |
| static-reference | `11166ea1bb7cb3bb08f10ab93e091c5c5ea8687649b5fb0705288c7ca91680e8` |
| pointer-daemon | `76ad0f093f2b7a97359920b7bd456cfa93a1581c73875547a86eb911f2ed2d7a` |

These hashes are newly recorded; the historical executable files themselves
were not sealed. Historical C/generated protocol inputs were sealed and verified.
The new retained source/command/binary chain supplies explicit provenance.

Both outputs matched the requested negative-origin 800×600/scale-1/normal
matrix. Private configuration retained focus_follows_mouse no. The command
`[con_id=7] border none` succeeded for reference PID 1674352 on workspace 2
(ID 5), H2. Filler ID 8, with the same App ID, kept normal border and width 2.
Target ID 9/PID 1674361 on workspace 1 (ID 6), H1 remained focused; reference
was unfocused. No broad App ID rule affected the filler.

Applied camera read 0 before calibration. The target's horizontal content offset
was -158 with configured width 636; desired left -318 gave signed delta +160.
IPC and scene both read 160 afterward. Applied owner scene became (-320,0),
size 640×600. IPC window offset x=2 and actual client COMMIT size 636×573
support horizontal content continuation [-318,318), crossing x=0. They do not
prove native buffer y or actually visible pixels without a capture.
PI_SCENE records tile-local (-160,0), clip (160,0,800,600), translated through
H1 origin (-800,0) to global clip (-800,0,800,600). H2 records clip_valid=0.
This proves the observed applied clip state, not the unperformed pixel/input gates.

### Exact stopping assertion and source diagnosis

The executed runner required both border none and current_border_width==0.
Reference IPC instead reports:

```json
{"border":"none","current_border_width":2,
 "rect":{"x":0,"y":0,"width":800,"height":600},
 "deco_rect":{"x":0,"y":0,"width":0,"height":0},
 "window_rect":{"x":0,"y":0,"width":800,"height":600}}
```

This failed the stored-width predicate before writing owner-geometry.json or
reference-preflight.json and before any capture reservation. Offline collection
reconstructs the actual owner/reference observations from retained IPC/traces
and explicitly labels all unexecuted results NOT TESTED.

Source diagnosis: `sway/commands/border.c:cmd_border` calls set_border(B_NONE);
it changes border_thickness only with a second argument. `sway/ipc-json.c`
publishes current.border_thickness unconditionally. `sway/desktop/transaction.c`
sets the effective border width/top to zero for B_NONE. Therefore stored width 2
is compatible with no border. The runner confused stored configuration with
effective decoration geometry. No rendered border or Mosaic leak is demonstrated.
The initial protocol's zero-width expectation above is retained as the failed
hypothesis; it is not a new product contract. The exact executed runner remains
unchanged, and no corrected runner is represented as executed.

### Matrix, damage and cleanup

| Gate | Result |
| --- | --- |
| Binary, loader, exact wlroots | PASS |
| Output geometry, client mapping, focus, targeted border mode | PASS IPC/source evidence |
| Calculated camera and applied clip | OBSERVED; no pixel qualification |
| Two H2 reference captures / whole RGB equality | NOT TESTED; zero PNG |
| H1 retained pixels / H2 forbidden colors | NOT TESTED in B |
| Visible Mosaic button | NOT TESTED |
| Invisible Mosaic non-delivery / reference H2 delivery | NOT TESTED |
| H2 focus-transition RGB stability | NOT TESTED |
| splith return / clip removal / standard button | NOT TESTED |
| Root/nested popup or grab | NOT TESTED, deliberately outside scope |
| Damage | Setup/client/scene/output extents retained; no PNG correlation or intermediate-frame coverage |
| Crash/protocol error | No crash; each ordinary client exited 0 with error=0 |
| Cleanup | PASS; compositor exit 0, three clients exit 0, owned pointer terminated -15; PIDs and private runtime absent |

The owned runtime was `/tmp/msr-330t08c8`, removed after all owned process groups
were reaped. No daily IPC, installation, system dependency replacement, package,
production patch/source, UX, dotfile, QuickShell, Codex or STEP20D change occurred.

Budget: SceneFX build 0, Mosaic build 0, binary modification 0, run 1/1, pristine
0, camera 1/1, captures 0/12, each named click 0/1, moves 0/8. The consumed run
prevents further execution despite unused PNG/click capacity. The persistent
owner registration and ledger are retained and never reset.

The future smallest justified gate is a separately authorized single run after
correcting the fixture's border-semantic predicate and testing it offline against
this retained border-none/width-2 snapshot. Keep the same focus/RGB/input/splith
objectives and exact candidate identity if still available. No SceneFX or clip
algorithm modification is justified by this fixture failure. This ticket does
not close the static runtime continuity gate or authorize STEP20C integration.

Q1–Q2 reference stability and full RGB: NOT TESTED. Q3 forbidden pixels: NOT
TESTED in B; A's zero target colors remain historical only. Q4–Q9 button delivery,
invisible input, focus RGB, clip removal and standard input: NOT TESTED. Q10
static/shared behavioral equivalence: not established by this run. Q11 algorithm
change justified: no demonstrated runtime anomaly. Q12 wider geometry, lifecycle,
full damage/effects/saved buffers, applied-generation and exhaustive ABI remain
unqualified, as do this run's intended principal gates. Q13 preparation for
integration: the static build/load candidate is established, but the requested
continuity evidence remains open. Q14 next technical gate: correct the fixture
and obtain a newly authorized bounded RGB/input/standard-return observation.
D1–D4 persist; STEP20C NEXT, production multi-output NOT YET SUPPORTED.

## Validation and integrity receipt

Python AST, shell/recipe syntax, concurrent/exhausted persistent-ledger tests,
exact-RGB and actual-button offline tests, retained border snapshot/source
semantics, local Markdown links, source-only fixture, protected source/system
hashes, unchanged executed runner and owned-process/socket cleanup: PASS.
Runtime scenario: FAIL at fixture assertion, scientific verdict INCONCLUSIVE.
Meson/model: historical qualified results reused, NOT RUN anew. Standard test
suite/headless campaign: NOT RUN, would exceed the authorized runtime scope.
No subagent review was requested; the parent performed the bounded source,
contract, provenance and final evidence audit. No independent review is claimed.

188 TEMPORAL_DAMAGE trace lines are retained from setup. They establish no
post-click, standard-return or every-frame damage result.

B source manifest: 24 entries, SHA-256
`5f9ab2b6d1ca23ef7743623d1e544237c8b70b62fe6de8164a46f1342e5a8ee2`.
B evidence manifest: 46 entries, SHA-256
`41cc5e3d305d89e83314723e67d7116c36d1503dd35647894bc898c49343e1a5`.
Both were created once and every entry verified. Executed fixture and later
collector/final fixture are distinct source directories. The report and final
Git diff are outside these inventories to avoid circular digests. A's original
manifests still verify without rewriting or snapshot remapping.

Final tracked B delta: this report plus Architecture, Known Limitations,
Roadmap, documentation index and Changelog; source-only follow-up fixture added.
No AGENTS, UX, Packaging, PKGBUILD, cumulative patch or production source change
in B. Local main and both remotes remain the A publication commit
`5e2961d05b7b33252718aabc4dbf787724f79ef0`; B remains unstaged and uncommitted.

## Static focus fixture evidence freeze — 2026-10-13

This new freeze task starts at main
`5e2961d05b7b33252718aabc4dbf787724f79ef0`. Direct `git ls-remote`
queries to canonical Forgejo and GitHub both returned that exact commit.
The expected local documentation and source-only fixture were audited in full.
No foreign change was found. This preservation commit does not alter the
historical executed runner, either historical manifest, or any raw observation.
The earlier LOCAL/UNCOMMITTED statements describe the original campaign's state,
not the publication state of this frozen evidence.

All 24 source and 46 evidence entries pass their original SHA-256 inventories;
the manifest digests above are unchanged. The Python files match the sealed
final-fixture byte for byte, and run.py matches the actually executed fixture.
Python AST, offline RGB/button tests, concurrent/exhausted ledger tests,
read-only collector verification, shell recipe syntax, local Markdown links
and git diff --check pass. Production source, package recipe and cumulative
patch are unchanged. No graphical test, compositor/library build or historical
budget reservation is performed by this freeze. Run 1/1 and camera 1/1 remain
consumed; unused captures/clicks/moves cannot authorize another historical run.

The source audit also reads the pristine pinned SwayFX border command:
`fd71a6bdc061bd633b488ae7b83e8a6981d22f86:sway/commands/border.c`.
Its B_NONE handling and optional second-argument thickness assignment match
the retained candidate semantics. IPC thickness is stored metadata; effective
border/decor geometry is separate. The failure remains INCONCLUSIVE / UNDECIDED.
The separately authorized RGB/input/splith ticket must supply a corrected pure
predicate, replay actual IPC and audit the entire preflight before its own run.

`SWAYFX_MOSAIC_STATIC_FOCUS_FIXTURE_FREEZE=PASS`
