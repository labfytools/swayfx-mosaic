# Focused native closure graphics fixture

EXPERIMENTAL SOURCE ONLY. This is a new derivation of the source-only graphics
fixture at Git `d46f854b3026e911659528fe94792aa13837a1d6`, not a modification or
re-admission of P1/C7/C8/O1/G2. No production code, package or UX contract changes.
The closed historical LAB is read-only. All native results remain NOT_RUN until
independent final-byte review, source publication and individual admission.

The eight nonfungible IDs are FS-P(12 captures), FS-C(16), DY-C(16), OM-ROOT(10),
OM-NESTED(10), GPU-G3(12), OM-EXTRA(12), GPU-CTRL(12): sum100, global110, at most
8 runs /150s. No reset/refund/retry API. Graphics source leaves GPU-CTRL and OM-EXTRA NOT_ADMITTED. GPU-G3 is
NOT_ADMITTED by default and has a distinct executable branch requiring B4 and
independent exact-byte/source/build receipts; no gate is inferred from a plan.

WHY: the former fullscreen insertion placed peer outside owner group; migration
ignored focus reveal; root OOM closure required nonexistent B. CONTRACT: exact
owner+peer direct children and measured400/400, current-data clamp then focus
reveal, scenario-created child-first closure. INVARIANT: whole-field expectations
are calculated before acquisition, every action is debited first, raw failure
and mechanical rescue remain visible and cannot establish scientific cleanup.

`fullscreen.prepare_group` uses an existing filler (container_split does not wrap
a singleton H/V child), wraps owner, marks the real group, creates peer on ws3,
then explicitly moves it to that mark. The source route is pinned
`commands/split.c:do_split`, `tree/container.c:container_split`,
`commands/move.c:container_move_to_container` (nonleaf destination adds child).
No empirical runtime adjustment or retry exists. A failed topology/crossing is
NOT_EXERCISED. Both binaries use the same fullscreen-client/protocol XML, explicit
positioner adjustment0 and actual configured rectangles. A/B input, explicit
close B with A surviving, fullscreen exit/splith return and final H2 are sampled.
The complete H2 field composes A then B before each capture; A-only is predicted
after B closes. FS-P uses12 captures; FS-C uses the same12 within16.

IPC `fullscreen_mode` is explicitly **pending** (`ipc-json.c` serializes
`c->pending.fullscreen_mode`); workspace marker1 is not fullscreen proof. A
post-command toplevel configure/ACK/MAP plus measured group geometry, paints and
fresh input corroborates sampled applied fullscreen. Direct observation of the
ancestor's `current.fullscreen_mode` is NOT_OBSERVABLE with these unchanged ELFs;
atomic current-state generation is NOT_PROVEN. The validator rejects a
pending-only or mismatched-owner/workspace certificate. Do not report a native
current-bit measurement that these binaries do not expose.

`cases.dynamic_geometry` derives row extent and uniform gap from current actual
child rectangles and pinned default640 sizing, validates row identity/order and
focused owner, then clamps old scroll to current bounds and performs native
left/right reveal for migration. The audited route is
`commands/move.c:cmd_move_workspace` → arrange old/new output → seat_set_focus →
`input/seat.c` row focus/reveal → `tree/arrange.c:apply_mosaic_layout` and
`tree/mosaic.c:mosaic_row_clamp_scroll`. Neither800 nor1120 is a universal expected
camera. Every resize/migration invalidates previous input/camera/origin; new
painted interior and pointer-local delivery are required, or actual dismissal
records input NOT_EXERCISED. Opening6 + four mutation pairs8 + final pair2=16.

OOM root closes A→TOP, nested failure closes B→A→TOP after mapped rootA; no_memory
requires actual wl_display.error code1 and client ENOMEM/EPROTO, separately from
requested error0 close. Every created object gets one wire destroy in reverse
hierarchy; release accounting and requested close are required. Failed popup
must never MAP. Native role/PID/nonce/counters and the same-XDG NULL return bind
the failure. The diagnostic's `children` is **existing parent children**, not
children owned by the failed tree (`wl_list_length(&parent->children)`); retain
its raw value. Initialized/listeners/published0 plus the audited prepublication
NULL path establish the scoped failed node, without inventing a new child-count
counter or demanding nested parent_children0. RootA native success, real wire
grab/configure/ACK/SHM/map and clipped pre-injection paint qualify nested start.

Availability identity (actual /proc exe hash, BuildID, mappings, exact wlroots,
static SceneFX), tree/outputs and fresh exclusive neighbor press/release are
saved **before cleanup**. A surviving painted rootA receives fresh right-button
input before any neighbor click, checked against its actual configure, updated
owner origin, exclusive wire pair and pointer-local coordinates. Actual root
dismissal and ENOMEM disconnect remain distinct NOT_EXERCISED input outcomes.
H2 pre/post/final must equal the whole reference. Failed-popup color is absent
on both outputs before/post injection; final owner close rejects both A and B
on both outputs. Surviving A is allowed after nested B failure.
Fail-closed and availability are separate observations; full damage, GPU
retirement, presented-buffer identity and atomic generation remain NOT_PROVEN.
OM-NESTED needs qualified root outcome and scientific cleanup, or a new explicit
independent dependency review with rationale and no common native fault.

Preparation never executes clients or compositors. All generated protocols,
ELFs, pycache, caches, tests and receipts belong to a fresh canonical owned0700
LAB directly below /var/tmp. Run every command using an allowlist environment
with TMPDIR/TMP/TEMP=LAB/scratch, XDG_CACHE_HOME=LAB/cache, XDG_DATA_HOME=LAB/data,
PYTHONPYCACHEPREFIX=LAB/pycache, CCACHE_DIR=LAB/cache/ccache, SMX_LAB=LAB. Source
may reside in a fresh Git extraction; no historical absolute path is required.

```sh
python graphics/prepare.py --lab "$LAB"
python graphics/validate_offline.py --lab "$LAB"
python graphics/freeze.py --lab "$LAB" --author author-identity
```

The optional `validate_offline.py --historical-c7 <read-only-run-directory>`
replays preserved resized-back and migrated-H2 snapshots through the same live
validator and rejects a stale-camera mutation. It does not upgrade old C7.
The manifest goes to LAB/followup-work/source-manifest.json and contains only
relative hashes and modes for the **whole followup source kit**. Review/test/publication
and runtime identities stay outside source. Review is never generated by these
commands. `freeze` refuses replacement; changed source requires a new explicitly
reviewed freeze path/version using `--output "$LAB/followup-work/source-v2.json"`,
not an automatic rewrite at launch.

Independent review JSON binds ticket, manifest_sha256, independent:true,
reviewer different from manifest.author, decision:ACCEPTED, runs[ID] with
ACCEPTED/client_build_review and client_build_receipt path/SHA. `gates[NAME]`
binds decision:ACCEPTED, manifest_sha256 and receipt path/SHA: the receipt requires
status PASS, tests_run>0, failures0 and source_digest of the manifest files.
Required names: FULLSCREEN_COMPARABILITY_OFFLINE, MIGRATION_REFOCUS_OFFLINE,
OOM_ROOT_NESTED_ORACLE_OFFLINE, separately by scenario. Runtime identity file
is external via review.runtime_manifest / runtime_manifest_sha256, with ticket
and identities[pristine/core/oom]: binary path/SHA/BuildID, wlroots path/SHA,
build_review and source_qualification ACCEPTED; pristine also binds its shared
SceneFX path/SHA. OOM runs additionally require oom_source_review ACCEPTED,
variant_identity COREC_V2_NATIVE_OOM_DIAGNOSTIC and source_manifest_sha256 in
runs[ID]. Clients are newly built in LAB/followup-work/client-build. Source,
protocol and ELF hashes are reconciled before admission and actions.

Publication JSON binds ticket, decision VERIFIED, source_commit, manifest SHA,
source_digest, origin_sha/github_sha equal to that commit, offline_test_only:false
and direct remote_observations origin/github {argv:[git,ls-remote,remote,
refs/heads/main],exit:0,stdout:<commit + ref>}. The real preflight also hashes
`git show <commit>:<source-path>` bytes for every source entry before reservation.
The same gate reads `git ls-tree -rz --full-tree <commit> -- <kit-prefix>`
without a shell, parses NUL-delimited paths and requires the exact inventory,
blob type and matching 100644/100755 modes. Local freeze/refreeze rejects
nonportable modes: source files use 0644 (or explicitly reviewed 0755); receipt
0600 permissions are never represented as portable source permissions.
Matching remote strings alone do not bind a source kit to Git. Ledger init is
an explicit parent operation `Ledger(LAB).initialize()` after provenance gate;
no child/test creates a real ledger. Example single-case CLI after publication:

```sh
python graphics/run.py FS-P --lab "$LAB" \
  --manifest "$LAB/followup-work/source-manifest.json" \
  --review "$LAB/reviews/independent-graphics.json" \
  --publication "$LAB/reviews/pre-run-publication.json"
```

Ledger state/lock enforce nofollow, regular file, owner, mode0600, single link,
stable flock inode and atomic fsync replacement. Offline tests use only
OFFLINE_TEST_ONLY ledgers and can never launch Session. Missing, stale or
superficial input rejects before debit. Logs/actions are bounded; an independent
watchdog TERM143/KILL≤146 seconds owns only registered process groups. Runtime
creation probes quota with a write in a new /tmp/smx-*0700 directory and falls
back on EDQUOT/ENOSPC to /var/tmp/smx-* if UNIX path fits. Runtime is socket-only.
All IPC uses explicit private swaymsg -s. Daily display/socket/loader variables
are excluded by allowlist. Prlimit sets core0 for every owned child; fixture
clients and Python explicitly set PR_SET_DUMPABLE0. Linux may reset dumpable on
exec of the unchanged compositor ELF: this is a stated limitation, never an
asserted native dumpable0 measurement. No system coredump cleanup is attempted.

The GPU-G3 adapter imports only the frozen sibling gpu/ modules and validates
every module origin and the exact acquisition ROOT. Its Session identity stays
GPU-G3/gpu. The adapter redirects MOSAIC_G3_DIR/NONCE and WLR_RENDERER exclusively
to compositor_environment; ordinary helpers and clients receive no hook vars.
Each epoch debits mutation+hook before arm. Rejected/incomplete A stops before
B and A-return. Native protocol validation and GL queries are owned by gpu/,
not reimplemented here. GPU background closure checks its real layer-shell role;
reference/glass check XDG, all with actual error0 exit/SHM release/wire destroys.

Additional GPU review fields: gates.B4 with the ordinary test semantic receipt;
runs.GPU-G3 gpu_source_review/gl_observability_preflight/build_review ACCEPTED,
each with *_receipt and *_receipt_sha256 whose content is independent:true,
decision ACCEPTED and exact manifest_sha256; native_gl_status NOT_RUN;
gpu_source_manifest(+SHA) schema G3-relative-source-freeze-v1; gpu_client_build_receipt
(+SHA) {status:PASS,source_sha256:<gpu/clients-g2.c>,client_sha256:<new ELF>};
gate_file(+SHA); reviewed_scene_sha256; binding {binary,client,client_sha256,
source_manifest_sha256,gate_file,reviewed_scene_sha256}. The native gate separately
binds source_review ACCEPTED, gl_observability PASS, runtime_authorized true,
diagnostic GPU-G3, binary_sha256 and exact acquisition_root. Every receipt must
be canonical owned0600 below the new LAB. Runtime identity gpu binary must differ
from every other identity. These are input contracts, never auto-written accepts.
