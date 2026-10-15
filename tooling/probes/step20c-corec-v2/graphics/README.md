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
| P1 | 10 | NOT_ADMITTED: no comparable fullscreen offline certificate |
| C1 | 18 | horizontal B/forbidden dismissal, new second chain, splith return |
| C2 | 12 | vertical y600 actual root/nested configure geometry |
| C3 | 12 | H1 physical1000x750 scale1.25 logical800x600 negative origin; marker |
| C4 | 12 | H1 physical750x1000 scale1.25 transform90, IPC/PNG marker |
| C5 | 12 | hidden motion only until return, same objects/grabs, fresh B input |
| C6 | 12 | real SHM held configure, txn-timeout5000 argv, natural timeout/ACK |
| C7 | 14 | 800→960→800, H1→H2→H1 stable IDs, input after each mutation |
| C8 | 12 | NOT_ADMITTED: same fullscreen certificate missing as P1 |
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
