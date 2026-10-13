# STEP20C static nested runtime handoff and valid-grab gate

EXPERIMENTAL / INCONCLUSIVE; sole runtime stopped on a fixture observation-window
predicate during standard return. Architecture UNDECIDED. The pre-execution
contract below is preserved; observed results and remaining untested gates follow.
Ticket: `SWAYFX_MOSAIC_STEP20C_RECEIPT_FREEZE_AND_STATIC_NESTED_RUNTIME_V1`.
Phase A is published at `54392cc0de7c8391c4f216cb83eee64be322ec72`, verified
on Forgejo and GitHub with a clean worktree. The historical phase B is preserved for publication by
`SWAYFX_MOSAIC_STEP20C_E2_COMPLETION_AND_PRIVATE_INTEGRATION_BATCH_V1`.
Pre-execution publication restrictions below describe the consumed historical
ticket; they do not authorize a replay. STEP20A DONE, STEP20B EXPERIMENTAL, STEP20C NEXT, STEP20D–G
PLANNED; production multi-output NOT YET SUPPORTED.

## Contract recorded before preparation or execution

Canonical [architecture](../ARCHITECTURE.md), [UX](../UX.md),
[limitations](../KNOWN_LIMITATIONS.md) and [roadmap](../ROADMAP.md) govern.
The [accepted receipt-integrity gate](STEP20C_STATIC_NESTED_RECEIPT_INTEGRITY_GATE.md)
qualifies offline receipts, not runtime. Its LAB
`/home/fy59/swayfx-mosaic-receipt-integrity-cof0umuk/` is read-only.
Verify all 76 source and 199 evidence entries, their fixed manifest hashes,
the accepted report/receipt hashes, 18 source bindings, 15 mandatory receipts,
the actual aggregate's five PASS markers and empty blocker list. Preserve B-01,
the initial CORRECTION_REQUIRED and final independent ACCEPTED separately.

The historical offline-gate lacks `fixture_sha256`; no historical runtime
fixture manifest exists. Its receipts must not be edited. A new transfer
receipt records exact source/destination copies and hashes, historical
acceptance scope, destination LAB and current ticket. Copy accepted receipts
under `accepted-offline/` without rewriting their embedded historical paths.
Retain their raw-byte and parsed-content bindings. The runtime offline-gate is
an explicitly derived transfer receipt, not a newly signed historical review.
Its fixture hash is computed from a real manifest after client preparation.

The [runtime fixture](../../tooling/probes/step20c-static-nested-runtime/README.md)
adds preparation, read-only preflight and single-use dispatch around the
unchanged reviewed runner and modules. Preserve exact copies in LAB/fixture;
historical acceptance covers their bytes, and an independent handoff reviewer
must separately accept the new transfer/authorization/dispatch code and final
manifest. Changes to reviewed runner/modules would expire continuity and
require independent delta acceptance before launch. No Mosaic/SceneFX algorithm
or production source modification is authorized.

## Immutable inventory and ownership

Create one fresh mode-0700 LAB outside Git, one exclusive durable owner registry
for this ticket, one fresh campaign-owner and a registration identifying ticket,
LAB, local UID, binary, binary/wlroots hashes and fixture manifest hash. Do not
reuse old owners or ledgers. Registry creation and launch consumption use
exclusive creation and file/directory fsync; a consumed launch is never refunded.
The existing ledger remains the action authority: run1, chain2, grab4, click9,
capture16, camera2, transition1, move24; maximum runtime150 seconds.

The fixture manifest contains exact runner/modules/scripts/patch/client sources,
protocols, prepared executables, immutable configuration template, accepted
receipt copies and referenced source/evidence manifest bytes. It excludes all
mutable budgets, logs, future PNGs/results, temporary files, authorization and
derived receipts containing the manifest hash, avoiding circular hashes.
Preflight checks excluded identity/authorization/transfer/review records through
explicit bindings. No manifest merely asserts a chosen hash.

Reuse static binary SHA256
`f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b`,
build ID `942db64269640778ee433e5970ba1100bc60f94c`, from the retained stage;
wlroots `/usr/lib/libwlroots-0.20.so` SHA256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
Verify ELF64/x86-64, mode0755, clipping symbols, no SceneFX DT_NEEDED, no
RPATH/RUNPATH and resolved relocations. Build only three historical C17 clients
using the byte-identical static_cross patch and protocol hashes. Copy their
client-build executables exclusively to the runner's LAB root paths; compare
hashes/modes and reject symlinks. No compositor/library rebuild or installation.

Authorization is explicit for this ticket and exact LAB, scope
`one-new-static-nested-headless-run`, with explicit_user_authorization=true,
owner_registry, binary, binary_sha256 and wlroots_sha256. The original
authorization.py is always called. Additional read-only preflight verifies
exact ticket, owner/UID, registration, immutable manifest and accepted review,
actual binary/wlroots/client identity and a completely unused ledger.
Offline negative tests must refuse every specified invalid authorization,
old/exhausted LAB, changed/missing manifest, unaccepted review and consumed run.
No socket, subprocess compositor or debit is allowed during those tests.

Only after independent handoff acceptance and all controls PASS may preflight
publish `STATIC_NESTED_RUNTIME_PREFLIGHT=PASS`. Dispatch then exclusively consumes
the ticket launch token and executes the frozen runner, which atomically debits
run before runtime creation. A failed launch consumes authorization permanently.
No second run, even after a fixture failure.

## Scientific run and stop rules

HEADLESS-1(-800,0), HEADLESS-2(0,0), each800×600, scale1, normal. Runtime0700,
private Wayland and explicit private swaymsg -s only; inherited desktop/loader
settings are removed. Record observed renderer/log/mappings; WLR_RENDERER=pixman
alone does not identify the actual SceneFX renderer. Historical controls are
read-only; no new pristine run. Reference H2 is a unique PID/AppID/con_id on
workspace2, targeted border none, full800×600 #303038; stored border width need
not be zero. Two full RGB captures after calibration, at least500ms apart,
must be identical. Stop dependent measurements on instability.

Each new E1/E2 owner has separately observed container/PID/workspace, applied
scene/content/titlebar, native420×320 SHM versus tiled destination, camera and
global clip[-800,0)×[0,600). At most one calculated camera correction per chain.
Never hardcode historical identities or adjust popup positions empirically.
Actual configure/ACK/map determines A and B geometry and both must cross x=0.
Open A with a real toplevel left-button serial and B with a fresh A serial;
require pre-map grabs and correct toplevel→A→B hierarchy and distinct serials.

E1 measures H1 popup retention, whole-H2 equality, owner-derived root/inherited
clip, visible B right press/release and forbidden H2 continuation right click.
Distinguish actual invisible delivery from legitimate topmost-first popup_done
and child-first destruction; record H2 reference callbacks and residual pixels.
Close E1 normally and never reuse destroyed objects.

E2 uses a fresh process/objects/serials in the same compositor. Open both grabs
under Mosaic, then targeted owner layout splith without outside click. Require
same workspace, mapped owner/A/B, no premature dismissal, tiled/root/inherited
clip removal. Remeasure standard origin, A/B H2 pixels and full masks; H2 may
normally differ from the empty reference while popups overflow. Click B on H2,
close B explicitly, verify A survives, click A, close owner and require whole-H2
reference restoration. Preserve raw IPC/compositor/client exit codes and streams.
IPC exit1 is separable only after completed science, handled exit/compositor0,
clean client exits, no protocol/crash and no rescue masking earlier failure.

Stop on identity/isolation/protocol/serial/parent failure, absent/non-comparable
popup, unstable reference, demonstrated leak, standard regression/residual clip,
crash or budget limit. Fixture failures are INCONCLUSIVE; demonstrated product
defects BLOCKED. No retry or algorithm repair is authorized. Available damage
extents qualify only measured intervals: no all-frame/minimal-damage/native-PNG
buffer/atomic-generation claim. Hidden owner, scale/rotation/migration/effects/
saved buffers remain separate gates.

## Closeout requirements

Retain exact runner/clients/config, provenance/authorization/handoff/review,
preflight/budget, all measured geometry/protocol/serial/clip/pixel/input/lifecycle,
damage/terminal/cleanup/matrix/summary receipts, raw logs/IPC/PNGs and final
source/evidence manifests in LAB. Generated/binary/large files stay outside Git.
Document actual PASS/FAIL/NOT TESTED, raw codes and budget. A handoff failure
means runtime NOT_RUN and global INCONCLUSIVE. Otherwise apply the ticket's
FEASIBLE/PARTIALLY_FEASIBLE/INCONCLUSIVE/BLOCKED criteria. Architectural choice is
tested-matrix feasibility, requires-redesign, or UNDECIDED; no production gate
is closed by this isolated campaign. Phase B must remain uncommitted/unpublished.

## Preparation candidate correction, before independent acceptance

The first 19-test preflight suite had five harness errors: unchanged
model.require correctly raised Invalid(ValueError), but tests expected
AssertionError. Its FAIL receipt, logs, source candidate, manifest and original
registration are preserved separately. Only new test exception expectations
are corrected; no historical reviewed module changes. The same LAB and zero
ledger remain in place. The original exclusive registration is immutable.
A single exclusive/fsynced registration-amendment explicitly binds its hash,
superseded fixture hash, final fixture hash and unchanged ticket/LAB/UID/owner/
binary identities. Handoff, authorization and new independent acceptance bind
both registration hashes separately. No budget/owner/token reset occurs.
The first candidate has no independent acceptance; its invalidated manifest
cannot authorize runtime. Only the reviewed final candidate can pass preflight.

## Executed handoff and authorization

New LAB: `/home/fy59/swayfx-mosaic-static-nested-runtime-pvn0osxm/`.
The initial preparation FAIL (19 tests, five harness errors) remains in
`candidate-v1/` and raw logs. The corrected suite passed 19 tests in8.008s;
the independent reviewer separately ran all19 PASS. Original registration
SHA256 `4a60089a548df2f9f2210e58e8fe23459104ff0002a01f6735a98d6f26faf0bf`
remains intact. The exclusive amendment SHA256 is
`362ab64728ca359c700bf1755d91788be9508ba776f03c711eda5f7d03df4d84`.
No ledger, owner or consumed token was reset. Final runtime inventory has92
immutable entries, SHA256
`1982bcc27dcc1d567997554c77791f42e5edaf447ccc12c21aea7f25659bf566`.
The historical runner SHA256 remains
`4382f2c0ffc8a41a6a65aecfca72dff762ded528f667288d179acbb354a9fcc9`.

Independent handoff review `/root/handoff_review` (Sol/medium, isolated,
read-only) accepts final sources, transfers and bindings. Its exact report was
materialized by the parent without textual alteration, SHA256
`af04fa9979ee24b5f87cff70807d7d853d316dbafb8660d7e779c0798088684c`.
This review is separate from the historical offline ACCEPTED; neither signs
new graphical results. Original historical report/review/76-source/199-proof
manifest bytes were checked again after runtime and remain unchanged.

`STATIC_NESTED_RUNTIME_HANDOFF=PASS`

`STATIC_NESTED_RUNTIME_PREFLIGHT=PASS`

The complete reviewed preflight passed before any reservation, with all
counters zero and no run/socket. Dispatch consumed its exclusive ticket token,
then the unchanged runner reserved exactly one run. Post-run pure checks of
both original authorize() and strict preflight refuse `fresh-run-required`.
No second runner/compositor launch was attempted. The unused action allowance
does not permit another run or budget reimbursement.

## Observed binary, outputs and reference

The original and private copy remain SHA256 f82557c1…21f7603b, full hash above,
ELF64 x86-64, mode0755, expected build ID, both clipping definitions, no
SceneFX dynamic dependency or RPATH/RUNPATH and resolved relocations. Actual
process maps identify system `/usr/lib/libwlroots-0.20.so` with the expected
SHA256; pkg-config reports0.20.2. No dynamic SceneFX was loaded. The rendering
log observes Mesa EGL, AMD GL vendor, AMD Radeon780M radeonsi and successful
FX renderer shader initialization. The actual path is FX/GLES, not Pixman;
the requested environment variable alone was not treated as renderer evidence.

Outputs have the exact requested signed geometry, scale1/normal. H2 reference
is PID2051837, con_id7, workspace2 (workspace ID5), AppID
org.mosaic.StaticReference, border none, empty decoration and full800×600
window. Stored border width2 is legitimate. The targeted con_id command leaves
the H1 filler unaffected. Both full RGB references are uniform#303038 and
identical, zero changed pixels, capture starts834.619ms apart.

E1 owner con_id9/PID2051849 and E2 con_id10/PID2052030 occupy workspace1
(ID6) on H1. Each uses one computed correction -320, scroll480→160, scene
(-320,0,640,600), painted content origin(-318,25). Native SHM420×320 remains
distinct from configured tiled content636×573, border/titlebar translation and
paint. The global tiled and owner-derived root viewport is[-800,0)×[0,600).

## E1 and E2 Mosaic observations

| Measurement | E1 | E2 |
| --- | --- | --- |
| Root real left-button grab serial |33|91|
| Nested real left-button grab serial |42|100|
| Root configured local rectangle |100,80,350,170|100,80,350,170|
| Nested configured local rectangle |100,60,300,130|100,60,300,130|
| Root global rectangle |[-218,105,350,170]|[-218,105,350,170]|
| Nested global rectangle |[-118,165,300,130]|[-118,165,300,130]|
| H1 A/B exact color pixels |24080 /15340|24080 /15340|
| H2 A/B color pixels |0 /0|0 /0|
| Whole-H2 comparison |exact reference|exact reference|

Both levels actually cross x=0 in both chains. Client and WAYLAND_DEBUG records
confirm real serial provenance, pre-map grab, bufferless initial commit,
configure/ACK/attach/map and TOPLEVEL→A→B parent IDs. Four serials are distinct.
E2 is a fresh process/Wayland connection; repeated numeric protocol IDs belong
to separate connection namespaces and denote fresh objects, not reused E1
objects. Root trace is correlated with each actual owner and one live root;
B inherits through the preserved exact source hierarchy. No direct independent
child-clip instrumentation is invented.

E1 visible B right click at(-108,175), local(10,10), delivers serial51 press
and52 release, button273, only to B. Forbidden point(91,195) lies within B's
geometric continuation on H2. Neither popup receives a button; reference H2
receives the actual press/release serial62/63. popup_done and destruction occur
B then A. This is a legitimate outside dismissal, not an invisible popup hit.
E1's post-dismissal H2 is exactly restored; E1 toplevel closes normally with
child-first destruction. These are measured sampled outcomes, not universal
click-through semantics.

## Standard return, actual failure and offline analysis

E2 opens A/B under Mosaic and reaches targeted `[con_id=10] layout splith`,
IPC0/success true, without an outside click. The retained standard snapshot
has the same workspaceID6, layout splith, mapped/visible owner. A/B both remain
present in standard PNGs; no popup_done is recorded. Destruction occurs only
during terminal shutdown after the fixture stops.

The runner fails `root-window-state-consistent` in `root_clip()`. Its window
begins before the layout command is applied and contains both states of the
same root tree0x56292fbcc170:

| Trace ns | Applied observation |
| --- | --- |
|181923034904618|enabled1, clip_valid1, local clip(-482,-25,800,600), prior Mosaic state|
|181923236944243|enabled1, clip_valid0, clip(0,0,0,0), applied standard state|

The layout IPC response is ns181923035203192. Requiring an unchanged root
through this transition is an invalid fixture precondition. The raw failure,
runner exit1 and incomplete-measurements flag remain unchanged. This evidence
does not establish an atomic transaction-generation contract or demonstrate a
product clipping defect. No runner/binary/algorithm was repaired or rerun.

Separate offline reanalysis of the existing standard snapshot/logs/PNGs finds
content origin(-398,25), A[-298,105,350,170], B[-198,165,300,130], settled tiled
clip_valid0/layout1 and root clip_valid0. Exact A/B masks have3120/13260 pixels
on H2. These observations corroborate removal of the inherited boundary and
ordinary overflow; H2 reference equality is intentionally not required during
that overflow. They are labelled OFFLINE_REDERIVED, not a completed runner
standard gate. The parent collector initially used an incorrect PI_MOSAIC
trace name; its failed attempt is retained. Correct PI_SCENE parsing then
completed offline checks without modifying runtime evidence.

Standard B right click, explicit B close with A survival, standard A right
click, normal E2 close and final whole-H2 restoration are **NOT TESTED**.
Missing measurements cannot be filled by source inspection or clean shutdown.
Verdict remains **INCONCLUSIVE**, architecture **UNDECIDED**; static nested
continuity is demonstrated for the sampled Mosaic portion, not the complete
requested standard-input/close matrix. No algorithmic change is justified by
this fixture-window failure.

## Terminal codes, cleanup, budget and remaining limits

Actual runner/dispatch exit1; terminal swaymsg exit1, stdout empty, stderr
`Unable to receive IPC response`. The compositor log shows handled exit and
shutdown; compositor exit0. E1/E2/reference/filler/pointer exits are all0.
No protocol error, crash, watchdog or rescue was recorded. All six PIDs are
reaped, runtime `/tmp/msng-hnvg_4l5` removed, no private socket remains.
Scientific measurements were incomplete: terminal transport is **not** granted
the completed-science exception; `scientific_cleanup_pass=false` and
`transport_incident=false` stay intact despite successful process cleanup.

| Budget | Used | Limit |
| --- | ---: | ---: |
|compositor|1|1|
|XDG chains|2|2|
|grabs|4|4|
|complete clicks|6|9|
|PNG captures|13|16|
|camera corrections|2|2|
|splith transitions|1|1|
|positions|8|24|
|seconds|16.486893|150|

370 damage extents are retained with capture windows. They describe sampled
mapping/dismissal/return intervals only, not every frame, minimal damage,
native PNG buffer identity or atomic generation. Direct child clip trace,
hidden owner, scale/rotation, migration/resize, effects, saved buffers,
exhaustive ABI/graphics maintenance and distribution gates remain open.
No new pristine run was performed; retained controls keep their original scope.
All310 protected source/system/package/patch paths remain unchanged.

`SWAYFX_MOSAIC_STATIC_NESTED_RUNTIME_PROBE=INCONCLUSIVE`

`SWAYFX_MOSAIC_STEP20C_RECEIPT_FREEZE_AND_STATIC_NESTED_RUNTIME_V1=INCONCLUSIVE`

Smallest justified next gate: correct and independently validate the standard
transition observation-window predicate offline against these immutable traces,
then request a separate bounded authorization for still-unmeasured standard
A/B input, child close/survival and final H2 restoration. No current-ticket
rerun, production integration or UX decision follows.
