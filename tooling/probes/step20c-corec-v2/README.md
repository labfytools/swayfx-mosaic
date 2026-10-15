# COREC_V2_REDERIVED — private source-only reconstruction kit

EXPERIMENTAL. This is a **new derivation**, never a recovery of the deleted
historical CORE, CORE-C or G1 bytes. STEP20A DONE; STEP20B EXPERIMENTAL;
STEP20C NEXT; STEP20D–G PLANNED; production multi-output NOT YET SUPPORTED.
No production source, package, installed library, session or ABI is changed by
this kit. Independent source/C review remains required before a private build.

The kit contains two complete cumulative deltas, source assembly/verification,
exact-body C extraction/tests, executable wrong variants and compact evidence.
It contains no upstream fork, archive, generated C slice, library or binary.
An optional `graphics/` directory can coexist without affecting the native
source manifests; its gates and native runtime evidence remain separate.

## Source authority and reproduction

Parents:

| Component | Exact commit | Parent tree |
| --- | --- | --- |
| Mosaic | `cd550382b311efdbfe3ed892f4e1d281d852e754` | `6be2d6cada19bd84673c30dfc4fb900a48b87e86` |
| SceneFX | `37ccd723bef49e6891156ffafce8f549f01446cc` | `685a78b94f9e44ee683e5fea93874557a9fed457` |
| SwayFX pristine audit | `fd71a6bdc061bd633b488ae7b83e8a6981d22f86` | Not an assembly parent |
| wlroots source audit | `d783533489e1f75d6886c2ab5c5960090ef268f8` | Not copied or patched by this kit |

The Mosaic pin is in the project Git history; use a normal project clone that
contains it. SceneFX is fetched from `https://github.com/wlrfx/scenefx.git` at
its exact commit. An optional `--scene-git /path/to/scenefx.git` uses an existing
read-only bare cache **after** verifying commit and parent-tree identity.
No missing historical LAB is referenced by executable code.

Requirements: Git, Python 3.12+ (safe tar extraction filter), POSIX shell;
for C tests, a C17 compiler with GCC-compatible sanitizer flags, pkg-config,
Wayland server, Pixman and wlroots 0.20 development headers/library. No install
or system package changes are performed. The compiler/library pair itself is
not installed or upgraded by the scripts.

Example, from a trusted checkout containing this kit (adjust only project/kit
paths; use a NEW absent destination under `/var/tmp`):

```sh
umask 077
KIT="$PWD/tooling/probes/step20c-corec-v2"
LAB=$(mktemp -d /var/tmp/swayfx-mosaic-corec-v2-reproduce-XXXXXXXX)
mkdir -m700 "$LAB/scratch" "$LAB/cache" "$LAB/pycache" "$LAB/data"
export TMPDIR="$LAB/scratch" TMP="$LAB/scratch" TEMP="$LAB/scratch"
export XDG_CACHE_HOME="$LAB/cache" PYTHONPYCACHEPREFIX="$LAB/pycache"
export CCACHE_DIR="$LAB/cache/ccache" XDG_DATA_HOME="$LAB/data"
python3 -B "$KIT/assemble.py" --project-git "$PWD" --destination "$LAB/source"
python3 -B "$KIT/verify.py" "$LAB/source"
python3 -B "$KIT/tests/run.py" --sources "$LAB/source" --output "$LAB/c-tests"
python3 -B "$KIT/tests/mutations.py" --sources "$LAB/source" --output "$LAB/mutations"
```

The assembler requires an absent explicit destination strictly below
`/var/tmp`, rejects symlink ancestors and creates it with current UID/mode0700.
All temp/cache/data directories are explicitly scoped below that destination.
It removes inherited desktop socket/display variables, reads Git objects,
checks exact commit/tree/patch SHA, extracts the pinned trees, checks/applies
patches without fuzz, and verifies the complete resulting file list, bytes
and modes against `provenance.json` (85 SceneFX + 417 Mosaic regular files).
Git apply replaces changed files using umask; their declared pinned file modes
are restored explicitly. No Git index/ref/config/history is modified.
Failed partial destinations remain for diagnosis; use another absent path.
The test runners likewise redirect temp/cache/data under their private output,
verify all source hashes before extraction, set RLIMIT_CORE=0, and require
Linux PR_SET_DUMPABLE=0 at each C child entry before expected aborts.

`verify.py` detects added/deleted/changed source files and mode changes. It does
not certify a compiler, binary, renderer, live session or graphically correct
compositor. `provenance.json` fixes the new patch/tree hashes and distinguishes
REUSED_VERSIONED_SOURCE, PINNED_UPSTREAM_FETCH, RECONSTRUCTED_NEW_DERIVATION,
HISTORICAL_REPORTED_ONLY and MISSING_NOT_RECOVERABLE. The old eight-patch stack,
old private reduced scene.c SHA and missing closeout receipts are not required.

## New private behavior and boundaries

The complete SceneFX `types/scene/wlr_scene.c` now allocates a private 64-byte
sidecar **before** native `scene_tree_init` publishes the new tree. Reservation
failure frees the unpublished tree and returns NULL with no listener or parent
list entry. After native node signal initialization, the successful reservation
attaches a destroy listener. No public tree/node field is added. The private
header API remains `void wlr_scene_tree_set_clip(...)` plus `bool get_clip(...)`.

The setter does not allocate. NULL deactivates but retains a reservation until
destroy; inactive entries are absent to get/render/hit. A zero box is active
and masks pixels/input. Idempotent setters do not run updates. Passing an
unreserved embedded root aborts explicitly even with NDEBUG; production callers
are audited to target factory-created workspace/popup trees. This precondition
check is not the failed-reservation behavior and is not a native OOM policy.
Lookup is linear in the number of reserved factory trees, including inactive
entries. Measured native tree128B and sidecar64B; allocator overhead NOT MEASURED.
Every factory-created tree reserves one sidecar, not just Mosaic-clipped trees.

Functional clips cover tree-local visibility and hit filters, applied-owner
root popup clips and nested inheritance, actual leaf-owner hidden masking,
CURRENT ancestor fullscreen exemption, standard clip retirement and helper
refresh in the fading branch. Integer translation/intersection and ancestor
coordinates are checked before narrowing; invalid camera values never convert
before finite/range checks. Unrepresentable clips fail closed. This does not
qualify unrelated renderer scale/transform arithmetic or complete effects.

Concrete constructor safety repairs are limited to IME refocus and protocol
back-pointer admission, container dim-rect NULL first use, xdg image-capture
rollback, and defined nullable partial-constructor cleanup in output/workspace/
view/seat. See `evidence/callsite-audit.json` and `callsite-locations.json` for
source ownership, rollback, root, reactivation and listener limits. wlroots
helper sources check factory NULL before first use; the actual linked provider
still requires independent ELF qualification. Unchecked tinywl/examples remain
outside the Mosaic compositor build and are not qualified by this kit.

Three passive traces are intentionally retained, not called uninstrumented:

```text
SPIKE_CLIP tree=%p rect=%d,%d %dx%d
PROBE_POPUP_CLIP owner=%p local=%d,%d %dx%d
PROBE_POPUP_HIDDEN_OWNER owner=%p applied=%d,%d %dx%d viewport=%d,%d %dx%d
```

A state-changing NULL setter and active zero both print `rect=0,0 0x0`; idempotent
inactive NULL does not print. The logs alone cannot distinguish those states.
Logging timing/cost neutrality is NOT PROVEN; there is no transaction-generation,
commit/present or GPU identity claim. SPIKE_DAMAGE is removed; PI/OPT diagnostic
hooks are not included. Ordinary renderer and transaction-timeout logs remain.

## Exact-body C evidence

`tests/extract.py` generates slices only into private output, recording each
full source-file SHA, start/end byte offsets, first line and slice SHA. Native
SceneFX struct definitions (with WLR_PRIVATE), real Wayland signals, addon sets
and Pixman regions are used. The actual factory, scene_tree_init/scene_node_init,
full native destroy, set_enabled, reparent, coords, clip setter/getter, numerical
guards, clip intersection/input filter and native hit iterator are compiled.
IME refocus and popup/workspace helpers use exact bodies with explicitly
reduced Sway/protocol structs in handwritten support includes.

Adapters replace scene_node_update/visibility and buffer/effect helpers outside
the exercised tree paths; they count/consume callback inputs and **do not prove
native damage or rendering**. Buffer/effect stubs abort if unexpectedly exercised.
The full private source retains native old/new visibility and damage update;
no stub replaces that path in a compositor source tree.

Executed tests cover NULL/box/idempotent/zero/NULL/reuse without setter allocation,
first and separately second reservation failure before publication/listeners,
parent/child destroy orders, reparent/back, reservation-address reuse without
false stale clips, embedded root rejection, native hit iterator zero masking,
applied leaf owner hidden/return, nested inheritance, current non-leaf fullscreen,
standard clip retirement, IME failure/refocus/descriptor rollback/destroy, aliases,
INT_MIN/MAX, NaN/infinities and large scroll. Full native fading/transaction
execution, native OOM survival, graphics and effects are NOT TESTED here.

Normal C17, UBSan (including float-cast-overflow/signed-integer-overflow/bounds),
and ASan+UBSan passed. Root rejection is an expected SIGABRT (raw rc-6), never an
OOM-survival success. Ten executable wrong variants all compile and are detected:
publish-before-reserve, allocating setter, visible inactive reservation,
NULL-free reservation, silently accepted root, unchecked caller NULL, zero hit,
doublefree/listener, unsafe intersection and unchecked float conversion. The
root-accepted mutant exits0, which is detected because the correct root test
must abort. A compile failure does not count as killing a mutant.

Ten early expected-SIGABRT systemd coredumps were observed before dumpability
was disabled (2,261,704 bytes, outside LAB under system management); eight
additional journal-only events had corefile:none after RLIMIT_CORE=0 and before
prctl. No deletion or sudo was used. RLIMIT_CORE alone is insufficient for a
piped Linux core handler. The final parent audit observed no new coredump entry
for either final corpus after the checked prctl fix.
The final harness requires PR_SET_DUMPABLE=0 before any tested assertion and
checks PR_GET_DUMPABLE. Do not claim zero writes outside LAB for early runs.

Initial extractor/header setup failures and the first mutation campaign failure
are retained in the private command logs and summarized in `evidence/c-tests.json`.
The mutant root-return harness initially leaked its root, causing ASan to mask
that mutant; the corrected return destroys it, and all ten mutants are then
exercised and detected. Evidence is newly generated, not historical inheritance.

## Gates, budgets and persistence

`evidence/reproduction.json`: source reproduction EXACT_FOR_NEW_TREE, including
second independent public-fetch assembly with identical receipt/manifests.
`evidence/c-tests.json`: PASS_BOUNDED_REVIEW_PENDING. Source audit is
SOURCE_AUDITED_REVIEW_PENDING. Independent source/C review must set the final
gates; successful compile/test adapters alone authorize no native runtime.

This kit consumes no functional Meson build, no DESTDIR stage, no compositor,
Wayland client, socket, IPC, graphical/OOM run or capture budget. Its C campaign
is serial, within j<=8, and never exhausts real RAM. `gates.json` gives the small
machine-readable source-only gate contract. Generated output remains private;
retain LAB for audit and do not automatically purge it. Publication and the
outer source-only bundle manifest are owned by the parent workflow after review.

## Reviewed diagnostic and prospective graphics supplements

`oom/` contains complete separately reviewed deltas and parent/result manifests;
`gpu/` contains the new, separately reviewed G2 instrumentation and a portable
source reconstruction helper. These diagnostics are distinct from the CORE
binary. `graphics/` contains the reviewed prospective P1/C8/O1/O2/G2 handlers;
all remain NOT_ADMITTED by default until per-case publication/binary/client and
independent review bindings pass. No source-only receipt grants a native run.

Always run the root `verify.py` on reconstructed CORE before variant helpers.
For G2 compare the complete reproduced tree, including modes, against the parent
manifest plus the three declared exact changed files. Its helper checks those
changed files and does not independently qualify an arbitrary parent. To syntax
check the GPU fx_pass body use test-targeted.py --core with the reconstructed GPU
target (the CORE argument shown in its historical CLI example instead checks the
CORE body). compile_commands supplies declared includes only; generated headers
must be prepared in an explicit private directory. See BUILD_RECIPE.md.

Small historical receipts under reviews/ and evidence/ retain the input paths
and status at their time of review. They are audit evidence, not executable
requirements for a vanished LAB. Source reconstruction requires only this Git
kit, pinned Git objects/public sources and declared tools. G2_ROOT is a declared
candidate-bound constant: changing it requires a new source/binary identity.
The surviving-source derivation never recovers historical lost bytes.
