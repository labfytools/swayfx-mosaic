# Prospective private revision: P1/C8/O1/O2 and G2 wiring

EXPERIMENTAL SOURCE ONLY. No new reservation, IPC, native injection, capture,
compositor launch or GPU execution has been performed by this revision. The
accepted graphics-kit and runtime-git-kit remain immutable. The real budget
retains P0/C1..C7; C7 remains INCONCLUSIVE. G2 and R1 remain NOT_ADMITTED unless
the exact prospective gate below is satisfied (R1 has no override).

The old published commit had a C7 fixture oracle bug: resize uses
max(0,min(previous,max_scroll)), but migration invokes move.c661
workspace_move_to_output, then move.c668 seat_set_focus, then seat.c1204-1212
focused-cell reveal. The observed old800 ->1120 for focused logical1280..1920
and viewport800 was legal. This revision fixes only future/offline predicates;
it never reruns or relabels the consumed C7. C2 future geometry now records
crossing_axis/crossing_boundary; old raw crossingX0 receipts stay immutable.

P1/C8 select an explicit two-equal-child nonleaf splith group by con_id, then
fullscreen that group. The separate fullscreen-client requests legal anchors
350/80 and100/60, widths900, and draws after each configure. Actual configure,
ACK, native buffer, paint and pointer-local input qualify measured crossing.
Noncrossing is NOT_EXERCISED. No Mosaic camera scroll is used in that branch.
P1 captures10; C8 captures12 including a fresh post-fullscreen/splith pair.
C8 compares its actual role/configure/geometry record against P1. This does not
prove an atomic current fullscreen generation; that property is NOT_PROVEN.
Both fullscreen samples compare the complete H2 RGB field against the stable
reference with measured configured popup rectangles clipped to H2 and composed
in A-then-B order. This P1/C8 source correction remains pending independent
delta review; it does not admit either run.

O1/O2 use a distinct oom ELF, captures8, hook1. SMX_OOM_* belongs solely to the
compositor process environment after the clean allowlist. The exclusive nonce
and role token is debited before writing, only after stable reference/owner;
O2 additionally requires real rootA native success and configure/ACK/buffer/map.
The failed popup validates its real button serial/grab wire without awaiting
MAP. Native role, nonce, PID, counters, unpublished pointers and NULL result are
required. Raw client no_memory/errno/exit remain separate from ordinary close.
Only a demonstrated no_memory disconnect has its own scientific cleanup path;
arbitrary errors and compositor death stay INCONCLUSIVE. Any unresolved O1
outcome blocks O2 admission. Missing observations are retained as NOT_PROVEN.

G2 uses the unchanged gpu-kit/scenario.py via GPUSceneSession/AdapterSession.
The actual Session identity is gpu/static SceneFX. The frozen adapter's legacy
'core' name is translated only by that narrow view. MOSAIC_G2_* and WLR_RENDERER
are compositor-only. Every epoch debits mutation+hook before native arm; three
hooks maximum, eight actual captures within the unchanged cap16. Layer-client
closure validates its actual layer role independently of XDG ownership. The
source freeze is supplied by the independent final review and reconciled against
the current immutable GPU manifest and every source SHA/size. No superseded
prospective freeze is hardcoded.
Source-only tests never establish actual GL observability. Capability preflight
acceptance is distinct from native observation; native_gl_status stays NOT_RUN. Rejected A stops B
and A-return; native error queue/readback remains intrusive. Present buffer,
GPU completion, whole-field causality and atomic generations remain NOT_PROVEN.

Independent review/publication and a new complete manifest are mandatory before
any run. All plans stay NOT_ADMITTED by default. The existing independent review
must additionally bind prospective[run] with decision=ACCEPTED,
source_manifest_sha256 equal to that manifest and client_build_review=ACCEPTED.
P1/C8 also bind client_binary/client_binary_sha256 (the dedicated fullscreen-client)
and client_build_receipt/client_build_receipt_sha256; the gate reconciles the
receipt's source SHA and generated ELF SHA before every action.
O1/O2 additionally bind variant_identity=COREC_V2_NATIVE_OOM_DIAGNOSTIC and
accepted oom_source_review_sha256=a953a38b49bea11e9c19e84ed2d8218a16b2e5d980e0ba57677eeee0ddf62c6c.
G2 additionally binds gpu_source_review=ACCEPTED,
gl_observability_preflight=ACCEPTED, native_gl_status=NOT_RUN,
build_review=ACCEPTED, pair=3, gpu_source_manifest as the canonical final freeze path below LAB and
gpu_source_manifest_sha256 equal to its independently accepted SHA; each of those
three acceptance statuses requires its *_receipt path and *_receipt_sha256. It also binds
gate_file/gate_file_sha256 and binding={binary, client, client_sha256,
source_manifest_sha256, gate_file}. The run nonce is derived from the fresh
ledger reservation token, never prefilled in a source review. The frozen native G2
gate independently requires source_review ACCEPTED, legacy gl_observability PASS,
runtime_authorized true, pair3 and the exact binary SHA. Its legacy PASS is
accepted only with gl_observability_scope=PREFLIGHT_CAPABILITY_ONLY and
native_gl_status=NOT_RUN; real ES3/RBO acceptance comes from epoch metadata. No test invents those
acceptances. The full kit publication must include new graphics and diagnostic
source bytes; source review does not authorize binary build or native execution.

Portable preparation from any working directory (LAB must already be canonical
and owned, all outputs remain under it):

```sh
LAB=/var/tmp/swayfx-mosaic-corec-v2-i516p6po
"$LAB/run-env" python "$LAB/graphics-next-kit/prepare_fullscreen.py" --lab "$LAB"
"$LAB/run-env" python "$LAB/graphics-next-kit/validate_offline.py" --lab "$LAB" --gpu-source-manifest "$LAB/results/gpu-source-freeze-corrected.json"
"$LAB/run-env" python "$LAB/graphics-next-kit/freeze.py" --lab "$LAB"
```

Preparation refuses an existing new client-build directory and never replaces
any of the five accepted clients. No client is executed. Freeze and validation
write graphics-next-work only; no old results or budget files are overwritten.

---

The following historical base README describes the original engine; its old
freeze/preparation destinations are not this revision's commands.

# STEP20C CORE-C V2 graphics source fixture

EXPERIMENTAL. Source implementation and offline controls; graphics preflight is
PENDING_INDEPENDENT_REVIEW. No compositor, Wayland client, IPC, screenshot or real
ledger reservation has been executed while preparing this subtree. STEP20C NEXT;
production multi-output NOT_YET_SUPPORTED; PRODUCTION_AUTHORIZED FALSE.

This is a new derivation, not recovery of old lab evidence. Surviving versioned
core-recovery geometry, wire parser, input, lifecycle, saved validators, C clients
and scenario code are reused with declared V2 changes. Original paths and hashes
are in parent-provenance.json. Synthetic wire-fixture is solely a protocol parser
control; it never qualifies a new binary. No historical replay or binary hash is
an input. Protocol XML is source; generated protocol C/headers and binaries remain
outside the kit. XML copyright/license headers are retained.

## Offline reproduction

Use a canonical, UID-owned direct `/var/tmp/<new-lab>` directory, its owned scratch,
cache, data, pycache, results, logs, graphics-tests folders, and a wrapper redirecting
TMPDIR/TMP/TEMP/XDG_CACHE_HOME/XDG_DATA_HOME/PYTHONPYCACHEPREFIX/CCACHE_DIR into LAB.
Place this subtree as LAB/graphics-kit. Python3, Pillow, C17 compiler, pkg-config,
wayland-client development files and wayland-scanner are prerequisites.

```sh
LAB/run-env python LAB/graphics-kit/prepare.py --lab LAB
LAB/run-env python LAB/graphics-kit/offline/test_graphics_v2.py
LAB/run-env python LAB/graphics-kit/freeze.py --lab LAB
```

Replace LAB with its absolute path. prepare.py creates graphics-tests/client-build
exclusively, generates protocol bindings using system scanner and records versions,
commands, raw statuses and source/output hashes in results/graphics-client-compile.json.
It never executes a client. Tests create only graphics-tests/OFFLINE_TEST_ONLY
ledger fixtures and mock transports for actual Session/run paths. SMX_TEST_LAB
selects the lab when source is placed elsewhere inside a full kit. freeze.py writes
results/graphics-source-freeze.json, never into source inputs. No old absolute lab
or historical raw PNG is needed.

## Runtime admission contract — NOT RUN

Only the parent orchestrator initializes Ledger(lab) and spends real budget after
independent build review, source-kit publication and per-scenario review. The
single-case CLI accepts run ID and --lab/--manifest/--review/--publication. No all
cases or retry mode exists. APIs: initialize/admit/action_debit/complete, no
reset/refund. Reserved failures stay consumed. All action debits precede action.

Immutable manifest schema graphics-v2-frozen-inputs requires ticket, lab, author,
source_root, files (ALL relative source SHA256), plans=plans.RUNS, limits=plans.LIMITS,
identities, kit_manifest, kit_manifest_sha256. Exclude mutable captures, logs,
ledgers, reviews, generated artifacts and self. The separately hashed full-kit
manifest binds core recipes/patches/tests as well: ticket, source_root, files,
source_commit. Addition/removal/modification invalidates admission.

Per-case review: decision ACCEPTED, independent true, reviewer different from
author, manifest_sha256, authorized_runs. Identity: binary, binary_sha256, wlroots,
wlroots_sha256, build_review ACCEPTED, source_qualification ACCEPTED; pristine also
pristine_scene/pristine_scene_sha256. No old binary hash is assumed. Publication:
ticket, decision VERIFIED, source_commit, kit_manifest_sha256, source_digest
(gate.digest of graphics files map), origin_sha/github_sha both equal full-kit
source_commit, offline_test_only false. Parent records direct git ls-remote
observations and associates published commit to kit bytes; runner does no network.
All bytes and input/review/publication hashes are rebound before each action.
OFFLINE_TEST_ONLY cannot authorize a Session. Stable flock inode, no-follow,
UID/link/type checks, atomic fsync replacements, token and monotonic duration
protect against duplicate spend/stale use.

Environment allowlist clears inherited display/runtime/socket/loader/backend and
activation. Only mode0700 /tmp/smx-unique holds sockets. Logs/PNG/source marker
PNG/SHM/cache/temp stay in LAB. C clients check LAB/scratch lengths before mkstemp;
launcher requires canonical owned scratch. Every swaymsg uses private explicit -s.
Owned PID/groups, raw stdout/stderr, /proc/PID/exe SHA/maps, loaded wlroots exact
7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837, SceneFX mapping,
actual renderer and EGL startup log lines are recorded (empty EGL is NOT_OBSERVABLE).
Watchdog kills only owned groups. Normal close/SHM release/Wayland error0 are
scientific closure. Forced mechanical cleanup never qualifies it. Terminal IPC,
client/compositor and outer runner raw exits remain distinct.

## Frozen intent and limits

| ID | Captures | Scenario/admission before independent review |
| --- | ---: | --- |
| P0 | 10 | pristine standard reduced homologous chain, B close/A survives |
| P1 | 10 | NOT_ADMITTED: pending fullscreen whole-H2 source delta review |
| C1 | 18 | horizontal B/forbidden dismissal, new second chain, splith return |
| C2 | 12 | vertical y600 actual root/nested configure geometry |
| C3 | 12 | H1 physical1000x750 scale1.25 logical800x600 negative origin; marker |
| C4 | 12 | H1 physical750x1000 scale1.25 transform90, IPC/PNG marker |
| C5 | 12 | hidden motion only until return, same objects/grabs, fresh B input |
| C6 | 12 | real SHM held configure, txn-timeout5000 argv, natural timeout/ACK |
| C7 | 14 | 800→960→800, H1→H2→H1 stable IDs, input after each mutation |
| C8 | 12 | NOT_ADMITTED: pending fullscreen whole-H2 source delta review |
| O1 | 8 | NOT_ADMITTED: first-allocation diagnostic source/binary unavailable |
| O2 | 8 | NOT_ADMITTED: second-allocation diagnostic source/binary unavailable |
| G2 | 16 | NOT_ADMITTED: new GPU hook/observability unavailable |
| R1 | 14 | NOT_ADMITTED: independent discriminant unspecified; never retry |

Caps sum170, global180, max14runs,18captures/run,150s/run. C7 spends opening6 plus
four mutation pairs8; final post-close pixel capture explicitly NOT_TESTED.
Legitimate popup_done is recorded; no dead popup gets clicked, its input is
NOT_EXERCISED. All runtime results NOT_RUN; sampled success at most
PARTIALLY_FEASIBLE, never production readiness. No final OOM/popup policy chosen.

C1 uses A350x170/B300x130 configured/native popup sizes and requires real crossing,
not requested placement alone. P0 reuses mapped images to stay within10. Before
and after second spawn, workspace1/H1/Mosaic tiled ancestry/PID are checked;
second ownerID/PID must be fresh. floating=null is handled with actual tiled
branch membership and nested ancestry. SHM dimensions, configure destination,
decoration fields and current origins stay distinct. Fresh pointer-local input
and paint corroborate current IPC candidates. Whole H2 RGB is exact zero tolerance
and no mask, except expected standard overflow. Source marker PNG is separate from
screenshot count; actual marker screenshot is debited. Root/nested configure ACK
map and actual pointer press→grab serial are checked independently. Dismissal is
not invisible delivery or universal click-through.

Core source retains three passive formats SPIKE_CLIP, PROBE_POPUP_CLIP and
PROBE_POPUP_HIDDEN_OWNER; temporal neutrality NOT_PROVEN. NULL/zero both print0x0;
no identity/generation is inferred. SPIKE_DAMAGE/PI/OPT absent. Native commit/present,
complete damage, saved-tree identity, buffer identity, GPU completion and atomic
generation remain NOT_OBSERVABLE/NOT_PROVEN absent distinct native measurement.
evidence.native_present rejects fake/cross-run records; never manufactures one.
evidence.fullscreen_certificate is offline-only and cannot itself enable P1/C8.

Offline handler quota controls exercise the actual sequencing with explicit fake
I/O, not native scientific measurements: P0=10, C1=16, C2=8, C3/C4=8+1 startup
marker screenshot, C5=12, C6=10, C7=14. All fake spawn/configuration/mutation/input/
chain/camera actions are checked against the same local caps. Real protocol,
serial, closure, source/publication and geometry adversarial tests are separate.
Initial vertical quota fixture failure is retained in the lab log; its source
fixture correction is disclosed in results/graphics-offline.json.

The swaybg marker helper is explicitly terminated/reaped immediately after the
calibration capture. Its raw helper-exit status is retained separately; expected
helper SIGTERM is never a scientific XDG close/SHM-release claim. A direct test
exercises this actual helper retirement path without launching swaybg.

## Bounded R-runtime repair — OFFLINE ONLY

The watchdog owns TERM at elapsed143s and autonomous KILL no later than146s
(or after a two-second grace for log-limit expiry). Main cleanup uses the same
absolute146s deadline, with reaping bounded by147s. Process registration and
watchdog expiry share a lock. The offline real Python child ignores TERM in its
own session/group; KILL is observed without invoking main cleanup. This is a
mechanical watchdog test, not native compositor cleanup evidence.

C7 now rejects a wrong reconstructed clamp at every resize/migration. The pinned
mosaic.c row calloc leaves minimum_cell_width zero; no production setter exists;
arrange.c and mosaic.c use640. This is independently corroborated by all three
actual direct-child IPC widths640 and zero-gap x positions, at viewport widths
below1920. The predicate rejects a different shape instead of guessing a policy.
Expected scroll is min(previous scroll,1920-current viewport width). Every sampled
mutation image rejects popup-colored pixels outside the current output viewport;
H2 must additionally equal the whole static reference after both resizes and
return toH1. Each surviving chain requires a newly sampled B interior and fresh
pointer-local delivery; dismissal records NOT_EXERCISED input without clicking a
destroyed popup. Source identity/publication binding and all original caps remain.
These are pending IPC plus sampled paint/input predicates, not native applied
state or generation/damage proof. Runtime remains NOT_RUN pending delta review.
