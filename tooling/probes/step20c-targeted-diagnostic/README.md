# Optional C3 saved diagnostic — EXPERIMENTAL

This fixture is a separate fixed `saved-diagnostic-A` experiment. Core
`step20c-targeted` final sources, plans, freeze and review are immutable.
A/G saved runs remain INCONCLUSIVE: their actual serial39 636x573→636x513
was held, but the old absent-IPC-`ws.gaps` predicate aborted before target
captures and natural timeout. No qualification transfers to the new binary.
STEP20C remains NEXT; production cross-output support is NOT YET SUPPORTED.

## Contract and source

`saved-passive.patch` applies only to the historical A private
`mosaic-source/sway/tree/view.c`; base/new/patch hashes are recorded under
same LAB `diagnostic/source-provenance.json`. The full source is private.
Sway view saved-copy creation/removal owns all normal references and scene
mutations. The patch observes existing lock counts before/after the existing
set-buffer call; it adds no buffer lock, unlock, copy retention, ACK, timeout,
scheduler, rendering, readback or timeline waiting. No public ABI changes.
One calloc sidecar per actual saved copy observes output_sample, node destroy,
source release and source destroy. It detaches sample on node destruction,
nulls whichever object dies first, and frees exactly after both die. A NULL
source needs only node destruction. Stable scalar addresses remain labels,
never dereferenced after destruction. Source buffer destruction may precede
node destruction because SceneFX retains its texture. Native release/destroy
and a release timeline pointer/point do **not** prove GPU completion.
Logging causes CPU timing overhead; instrumentation neutrality is NOT PROVEN.

Native saved tree logs bind owner/container ID, scene parent and content tree.
Creation logs distinguish saved-node, original scene-node and raw source-buffer
addresses, source crop, destination size and transform. output_sample logs the
actual saved node global geometry, viewport, enable state and each applied
ancestor clip at that sample (`sample_ns`). Existing unmodified SceneFX
OPT_BUFFER_DRAW records bind that same node/output to actual draw extents.
The validator measures the intersection of **that saved node**, its viewport
and observed clips; another node's rectangle cannot substitute for it.

## Gate and global budget extension

`diagnostic.py` adds exactly the fixed fourteenth spec **in memory only** during
this process's original `gate.locked`, `action_debit` and shared `Session` use.
Original `gate.verify` runs before registration and after unregistering.
`diagnostic-registration.json` persists the exact spec; `final_budget(lab)`
requires it for extended reconciliation. It never edits the frozen module,
original review or previous tokens/events. The original review does not accept
this extension. Independent preparation review and a separate runtime review
bind exact original freeze/review, diagnostic source/patch/tests, private source,
clients, wlroots, the original A SceneFX static archive and uninstalled pc.
The runtime freeze additionally binds the staged new binary.

Only the same LAB is accepted. All13 original tokens must precede diagnostic
build/stage/run. One build token and one stage token are O_EXCL/fsynced before
the action under a flock; diagnostic/budget.json is separate from runtime
captures. Failed actions still consume their token. No retries/refunds/reset.
Only one known `saved-diagnostic-A` runtime token is appended under the original
global flock/fsynced reconciliation. Limits remain global14 runs/174 PNG,
saved3 runs/30 PNG, per-run16 maximum; C3 itself uses at most10 PNG,2 clicks,
1 camera,150 seconds. `Session` supplies isolated sockets, maps and cleanup.
A final caller must use this extension's `final_budget`, since the frozen
original validator intentionally knows only its thirteen original specs.

## Review and execution protocol

1. `prepare.py --lab /home/fy59/swayfx-mosaic-targeted-7gge6h8b` runs offline
   tests, persists registration and seals preparation bytes. It requires the
   C17 syntax receipt. It does not accept its own result.
2. Independent review must write preparation-review.json with scope,
   ACCEPTED status, independent=true, blockers=[], exact freeze_sha256/files,
   report_file/report_sha256. No compositor build before that acceptance.
3. Parent reserves `reserve_build_stage(lab,'build')` before the ONE Mosaic
   private build. Reuse **exactly** HIST/scene-build/libscenefx-0.5.a and
   HIST/scene-build/meson-uninstalled/scenefx-0.5-uninstalled.pc. Zero SceneFX
   builds or edits. Parent reserves stage before ONE DESTDIR stage and verifies
   its manifest. No install, live IPC, second lab or system library change.
4. Parent seals runtime-freeze.json (scope/spec/files=bindings(lab,True)), then
   independent runtime-review.json with analogous exact-byte acceptance.
5. Only then `run.py --lab SAME_LAB` may consume the optional token once.
   H1=-800,H2=0, normal scale1; real SHM crossing and at most one camera;
   beforehold applied state; gaps inner current set30; pending workspace
   rectangle/owner identity and actual held wire dimensions; native saved
   create/draw/sample before2500ms; held H1/H2 pair; natural2500ms timeout with
   client alive and unACKed serial; requested live geometry/saved node gone;
   stable H1/H2 pair; normal protocol close; final H1/H2 pair. Ten PNG total
   including two H2 static references. No held-serial ACK during cleanup.
6. Postrun analysis uses the same pending_geometry, held_configure,
   saved_identity, saved_removal and native_pairs predicates as offline/runtime. Final global
   budget must use final_budget. Any missing required native evidence fails
   closed; partial observations cannot become GPU-lifetime qualification.

Offline native trace fixture in test_diagnostic.py is explicitly synthetic;
wire/IPC positive and negative tests use actual saved-A/G consumed logs and
snapshots read-only. No synthetic native test is runtime evidence. Complete
intermediate damage, GPU/CPU completion, atomic generation, other output
geometries, and instrumentation neutrality remain NOT PROVEN/NOT TESTED.

## Refused preparation correction C3

The previous preparation was refused for C3-CREATE-WINDOW and
C3-REMOVE-WINDOW. Its exact source bytes, aliases, receipts and review are
preserved in LAB/diagnostic/superseded-preparation-review-refused-v3.
Creation must follow the requested command, precede unique owner/tree
activation, and identify an unreused actual saved node. Every sample must
follow activation and bind its exact node/source/output.

Natural removal uses the same saved_removal predicate in the wait, before
live captures and in final/postrun validation. It requires the unmodified
positive-waiter transaction timeout RAW line after activation, then the exact
SD_REMOVE owner/tree/content, then each measured saved-node/source destruction.
SD_REMOVE is emitted before synchronous node destruction in the unchanged
passive C patch. Destruction must follow creation and precede the first live
capture boundary and normal explicit-close request. The native timeout line
has no monotonic ns; destruction occurs before the runner observes timeout,
so runner observation is not a lower bound. The audited single queued
transaction gives this fixed experiment its raw-order association; it is not
a general transaction-generation or GPU-completion claim.

prepare.py copies current diagnostic sources into diagnostic/diagnostic-source,
reuses unchanged passive C and its existing C17 receipt, writes source-bound
offline results and creates a new O_EXCL preparation freeze after the refused
receipts have been archived. It never creates an accepted review. The C3 runner
journals named private runtime, run, log and socket paths after Session creation
and startup without changing the frozen core.
