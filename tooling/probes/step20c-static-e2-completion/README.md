# Static E2 completion fixture

**EXPERIMENTAL / PREPARATION; runtime NOT RUN, review PENDING.**
Ticket `SWAYFX_MOSAIC_STEP20C_E2_COMPLETION_AND_PRIVATE_INTEGRATION_BATCH_V1`.
No production source, UX, packaging or cumulative patch change. STEP20C stays
NEXT; production multi-output is NOT YET SUPPORTED.

`derivation.json` identifies initial exact copies from the frozen
`step20c-static-nested-geometry-replay` fixture at
`c5f96a34e3924275179365938d02f3a318c0c4bf`. Model, IPC adapters, observations,
pixels, predicates and core geometry/protocol/terminal tests are retained.
`reusable_tests.py` preserves the identified AST method bodies. The historical
readiness aggregate and its ACCEPTED review grant no acceptance here.

`transition.py` is shared by raw historical replay and the new E2-only runner.
It examines the entire selected H1 callback window: old applied Mosaic,
targeted accepted splith, first coherent applied standard, then at least two
coherent standard observations. It verifies source-backed `current` layout,
actual owner scene, exact workspace/output/XDG identities, unique enabled root,
clip removal, capture intervals, and no reactivation through standard B input.
PI_POPUP lacks owner IDs and reports the global popup root on both outputs.
Unique live XDG hierarchy plus exact IPC ancestry supplies bounded correlation;
independent observations do **not** establish an atomic transaction generation.

Historical request-start time was not recorded. `replay.py` uses the previous
actual capture event and first monotonic trace after actual command handling as
an explicit request interval. It preserves the old applied root after handling
and before reply, followed by two cleared roots; no row is discarded. The
historical cleanup was compositor shutdown, corroborated by seat capabilities0,
then destruction. It does not qualify normal owner close. Replay cuts only at
that explicit shutdown boundary, retaining any earlier dismissal/destruction.

The new runner records exact IPC request start and actual reply separately.
Its transition window starts at a complete source-backed Mosaic commit after
A/B are fully mapped and before the request; earlier pre-root callbacks stay
in separate opening evidence. Absence of an eligible callback is INCONCLUSIVE.
Only E2 runs: real left TOPLEVEL opens A, real left A opens B, right B in standard,
explicit client close B, then a fresh measured A right click. Each point comes
from a measured solid interior with an8px margin. Every click records fresh
client protocol deltas, full button pairs and wire/callback coordinates.
Configured/applied destinations remain distinct from native420x320 SHM; an old
Mosaic observation is not reparsed with a later standard configure. Client
close requests are recorded before flushing stdin. B destruction and COMMAND
close_b DONE must match exact objects, without popup_done. A preserves map/IDs,
exact pixels on both outputs, zero B colors and input. Normal owner close must
be corroborated by command, child-first destruction and wire destroy requests.
Final whole H2 RGB equals the initial #303038 reference without mask/tolerance;
final H1 has no popup colors. Raw terminal IPC/compositor/client codes and rescue
are retained separately. Terminal IPC1 alone does not undo completed science.

Budget: run1, chain1, grabs2, complete clicks4, camera1, transition1, PNG12,
positions16. Maximum150s; active work watchdog cuts at143s to leave cleanup
margin. Two full H2 references are identical. Runtime is0700, private two-output
headless H1(-800,0)/H2(0,0), 800x600 scale1 normal, with explicit private swaymsg
socket. No pristine control, compositor/SceneFX build or desktop operation.

## Offline preparation

All outputs below are in a **new** directory outside Git. Commands never reserve
a real runtime budget, launch a client/compositor or change historical LAB bytes.

```sh
F=tooling/probes/step20c-static-e2-completion
O=/home/fy59/swayfx-mosaic-e2-batch-hyrd8qm1/implementation-final-offline
mkdir "$O"
PYTHONDONTWRITEBYTECODE=1 python "$F/tests_offline.py" --output "$O/test-receipts.json" > "$O/tests.log" 2>&1
PYTHONDONTWRITEBYTECODE=1 python "$F/replay.py" --output "$O/replay.json"
PYTHONDONTWRITEBYTECODE=1 python "$F/audit.py" "$O/source-audit.json"
PYTHONDONTWRITEBYTECODE=1 python "$F/gate.py" "$O"
```

The gate requires nonempty exact test inventory, actual executed PASS receipts,
every temporal negative rejection, final source hashes, raw replay equality and
an exhaustive current static assertion inventory. Audit PASS means classified
source inventory; graphical execution coverage remains NOT TESTED.
Negative handoff tests simulate records only in temporary isolated directories;
these are explicitly synthetic and never mint a real independent review.

`handoff.py prepare "$O"` creates the sole fresh registered LAB, exact source
manifest and prospective handoff. It reuses the historical exact C17 clients
and their actual adapted static_cross/protocol sources byte-for-byte; no build
or client execution is required. Static binary identity remains
f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b,
build ID942db64269640778ee433e5970ba1100bc60f94c, mapped wlroots identity
7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837.
The original source directory is part of the frozen runtime manifest, alongside
installed fixture, binaries/clients, actual private trace source and receipts.

## Independent review before dispatch

The implementation author does not generate acceptance. A genuine independent
read-only reviewer must produce a report and `results/handoff-review.json` with:
status ACCEPTED, independent=true, read_only=true,
scope STATIC_E2_COMPLETION_FINAL_BYTES, blockers=[], fixture_sha256,
source_sha256 (all final source files), runtime_handoff_sha256,
authorization_sha256, registration_sha256, gate_sha256, report_file and its
report_sha256. These bind the actual final files, not a historical gate.

After parent approval, `handoff.py preflight LAB` publishes an exact preflight.
Only then may the parent run `launch.py LAB` once. Exclusive O_EXCL consumed token
precedes dispatch. Runner repeats reviewed source preflight and checks the exact
consumed token before its lock or run debit. Wrong/old LAB, token, binary,
wlroots, stale review, changed manifest/runner, existing run/socket and prior
consumption fail closed. Failure never refunds the ticket; no automatic retry.
No runtime dispatch has been performed during implementation.
