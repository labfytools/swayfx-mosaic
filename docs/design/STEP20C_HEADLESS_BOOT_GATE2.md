# STEP20C — Gate 2 headless boot preparation

Status: **EXPERIMENTAL**. V4 pristine: **FAIL before compositor**;
V4 CORE: **NOT_RUN**. V5 native: **PRISTINE_ALLOCATOR_BLOCKED / CORE_NOT_RUN**.
The separately approved single V5 sequence consumed its pristine reservation;
CORE was never attempted. No sequence PASS, private IPC or rendering proof was
obtained. Historical preparation verdicts below are pre-attempt evidence.
Any future native attempt requires a new LAB, budget and explicit approval.

## V5 first native outcome — 2026-10-17

The reviewed V5 fixture ran once from the approved app.slice launcher after
preflight of 12 fixture hashes, 92 manifested files and 98 ELF identities.
The supervisor returned `REFUSED: pristine failed: CORE NOT_RUN`.
The retained pristine receipt records verdict FAIL, elapsed 0.361879 seconds
and oracle null. The scope executed the Python child and native pristine
SwayFX binary: unlike V4, the failure occurred after compositor execution.
The mandatory `PWD=/tmp` correction passed that earlier environment guard.

The relevant diagnostic messages, in order, are:

```text
MESA-EGL: warning: Not allowed to force software rendering when API explicitly selects a hardware device.
[wlr] [render/allocator/udmabuf.c:148] Failed to open /dev/udmabuf: No such file or directory
[wlr] [render/allocator/allocator.c:168] Failed to create allocator
[sway/server.c:308] Failed to create allocator
CHILD REFUSED: compositor exited before private IPC
```

The immediate failure is allocator creation with the host device absent from
the private /dev. The Mesa warning is not established as fatal. Source analysis
must distinguish software EGL rendering from allocation of render targets;
no effective capability masks were logged. See the
[offline allocator triage](STEP20C_HEADLESS_ALLOCATOR_TRIAGE.md).
There is no private IPC, output oracle or rendering evidence. CORE is NOT_RUN,
with no ATTEMPT receipt; no result transfers to that binary.

Post-attempt independent observations found both V5 scopes not-found/inactive,
their cgroups absent and the pristine runtime empty. Stable SwayFX, QuickShell
and greetd remained active with their original process identities. These are
historical post-run observations, not authority to manipulate those services.
The V5 LAB, raw stdout/stderr, result, units and reservation ledger are sealed
historical evidence: never edit or reuse them and never retry pristine there.
Only this sanitized documentary summary is published; raw receipts stay private.

## V4 native failure and prospective V5 repair — 2026-10-17

The approved V4 pristine attempt at 06:09 CEST failed with
`REFUSED: pristine failed: CORE NOT_RUN`. Its raw
`logs/pristine.stderr.raw` contains
`CHILD REFUSED: unexpected sandbox environment`. The strict comparison
`dict(os.environ) == CHILD_ENV` rejected the Python child before its first
compositor Popen. No pristine or CORE compositor, native IPC/socket or rendering
was executed. The pristine reservation is consumed and must never be retried
in `/var/tmp/swayfx-mosaic-step20c-gate2-prep-qglkg45r`; CORE was not reserved.
The retained result records unit LoadState=not-found / ActiveState=inactive
and the cgroup was absent. Historical preparation verdicts below describe
pre-attempt evidence only; they do not requalify this failure.

The harmless post-failure Bubblewrap diagnostic at
`/var/tmp/swayfx-mosaic-step20c-gate2-env-diagnostic-uh25ciwe/RESULT.json`
returned 0 and measured only `extra_keys=["PWD"]`, `PWD="/tmp"`, no missing
keys or changed shared values, and strict_equal=false. The local bwrap(1)
contract preserves PWD through --clearenv. This is a reproduced environment
cause, not a second native attempt.

V5 will use a new exclusive mode0700 LAB, fresh scope identities and empty
reservation ledger. Its sole functional correction makes `PWD=/tmp` mandatory
in CHILD_ENV and explicitly emits `--setenv PWD /tmp` after --clearenv, keeping
--chdir /tmp and the complete dictionary equality guard. V4 and older LABs,
including raw failures, remain byte-for-byte unchanged. Offline tests and a
harmless Bubblewrap child must pass, as must the read-only plan from Desktop
Commander under app.slice and independent review. No compositor may run in
this correction mission; a new conversational approval is required for V5.
STEP20C remains NEXT; production multi-output NOT_YET_SUPPORTED.

## Scope and authority

Prepare a symmetric comparison of the retained pristine SwayFX 0.6 and private
Mosaic CORE-C V2. The supervisor stays outside the sandbox; its child enters an
ephemeral delegated systemd user scope under app.slice, then Bubblewrap, then
the fixed binary and private IPC checks. Reuse the combined benign proof at
`/var/tmp/swayfx-mosaic-step20c-combined-benign-z4wk7gog`: its 22/22 checks
qualify that benign child only. Do not reopen historical scientific ledgers.

The original preparation scope excluded changes to production source, C API/ABI,
SceneFX patches, packages, UX, Stable compositor, QuickShell, greetd and UWSM.
It prohibited installation, session switching, compositor execution (including
--version) and live Sway IPC.
The later single V5 native sequence had separate approval, now consumed.
The current documentation-only mission authorizes a reviewed commit and pushes
to origin then github; it authorizes no new compositor or sandbox expansion.
Architecture and UX contracts remain unchanged. STEP20A DONE; STEP20B
EXPERIMENTAL; STEP20C NEXT; STEP20D–G PLANNED; production multi-output
NOT_YET_SUPPORTED. Headless software evidence cannot qualify DRM/GPU, G4,
fullscreen, buffer lifetime, complete effects/damage or daily use.

## Exact identities and passive preflight

| Profile | Retained ELF under /var/tmp/swayfx-mosaic-corec-v2-i516p6po | SHA256 | Build ID |
| --- | --- | --- | --- |
| pristine | controls/pristine/sway | b7fa32116e3c42706b9b02da7df12f27e76d82dd253deb8bdec81519eed145f6 | ba9751c82e73d4043b7651354f20936d070c2227 |
| core | builds/core-mosaic/sway/swayfx-mosaic | 91f48aae2675331e0a2c60ec2fedf983745c521c75232c704a6516a4140801fb | d5d304533f2c8db9d738365e9bd7f2c96779ef8d |

Pristine dynamically needs libscenefx-0.5.so. CORE embeds private SceneFX and
must have no SceneFX DT_NEEDED. Both use system libwlroots-0.20.so with SHA256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
The main build and diagnostic OOM/GPU variants are not substitutes.

Inspect UID, mode, link count, size, SHA, Build ID, ELF class/machine, interpreter,
DT_NEEDED, RPATH/RUNPATH and symbols with readelf, never ldd or the target loader.
Resolve the transitive library closure passively under /usr/lib, recording real
paths and hashes. Inspect EGL vendor JSON, swrast DRI module, XKB and font data
separately: DT_NEEDED is not the dlopen/data closure. Missing or drifted inputs
are refusals, not permission to rebuild, install or change the binary.
Local ABI evidence is exact-pair only; passive resolution does not prove live
relocation, renderer initialization or future update compatibility.

## Environment and containment contract

The manager control plane alone uses an explicitly reconstructed user bus
address. Desktop Commander must be measured under user@1000.service/app.slice;
a launcher under session-6.scope is rejected. No PID from a historical report
is an authority for the new run. Verify manager Delegate=yes, active app.slice,
writable common-ancestor cgroup.procs and memory/pids controllers before spawn.

Bubblewrap uses --unshare-user --unshare-all --disable-userns, --new-session,
--die-with-parent, --clearenv; /usr read-only, /bin /lib /lib64 links into /usr,
private /proc and /dev, private tmpfs /tmp and /run. Bind only the sealed LAB
input read-only and run-specific LAB output/runtime writable. No host HOME,
/run/user, /sys, display, seat, bus, configuration, network namespace,
/dev/dri or /dev/input is exposed. Close all inherited FDs other than explicit
stdio; stdio uses /dev/null and bounded pipes, never desktop sockets or a TTY.
The private runtime directory is UID1000 mode0700; all IPC paths belong there.

Do not bind host /etc wholesale. Candidate minimal data are exact EGL vendor
JSON (normally under /usr/share/glvnd/egl_vendor.d), /usr/share/X11/xkb and
/usr/share/fonts. Fontconfig may require a private minimal fonts.conf referring
only to /usr/share/fonts and LAB cache, supplied through FONTCONFIG_FILE.
No host NSS/password, machine-id, seat or ld.so cache is needed by assumption:
any missing requirement must be observed and reviewed, never silently exposed.
/proc/sys and same-UID hostile peers remain security limitations, not a claim
of a hardened general execution service.

SceneFX directly calls fx_renderer_create, not wlr_renderer_autocreate.
WLR_RENDERER=pixman is therefore not evidence of effective Pixman. The source
supports WLR_RENDERER_FORCE_SOFTWARE=1, passing DRM FD -1 into EGL software
device selection. Candidate environment: WLR_BACKENDS=headless,
WLR_HEADLESS_OUTPUTS=2, WLR_RENDERER_FORCE_SOFTWARE=1,
WLR_RENDERER_ALLOW_SOFTWARE=1, LIBGL_ALWAYS_SOFTWARE=1, XWAYLAND disabled by
configuration. Effective EGL/renderer/allocator success remains NOT TESTED.
No automatic GPU fallback or host device exposure is allowed.

## Proposed budget, supervisor and oracle

These are bounds to approve later, not consumed reservations: exactly one
pristine attempt, then exactly one core attempt only if pristine passes all
checks; no retry. At most two 800x600 headless outputs; 30 seconds per run,
TasksMax=64, MemoryMax=1GiB, MemorySwapMax=0, TimeoutStopSec=2s,
KillMode=control-group. Both stdout and stderr are drained concurrently with
16MiB maximum per channel; limit overflow or partial output fails the run.
Capture budget zero for the minimal IPC boot. Missing proof never means PASS.

Before spawn, journal exact argv, hashes, unit name, unique description, fresh
attempt identity and expected cgroup. Reject existing unit, directory, socket
or attempt receipt. Persist atomically with fsync before execution. Record
Popen-owned PID, startticks and pidfd; match manager InvocationID, description
and ControlGroup before any stop. Never kill by guessed/recycled PID, never
stop a foreign unit, and never adopt a pre-existing unit. Unknown ownership
fails cleanup rather than widening authority. All pidfds/pipes must close.
On timeout/cancellation stop only the proven invocation; verify collection,
empty cgroup, exited owned processes and absent LAB sockets. Do not rerun.

Inside the sandbox the minimal client is /usr/bin/swaymsg with an explicit
-s /runtime/sway-ipc.sock; get_version, get_outputs and get_tree are read-only.
The bootstrap must verify socket UID/type/path and the private Wayland socket;
no discovery via inherited SWAYSOCK is allowed. Require exactly two active
800x600 outputs and a valid tree/version for each binary; compare symmetric
fields without requiring equal Mosaic-specific metadata. Request exit only
on the proven private socket, distinguish an exit-IPC disconnect from the
compositor exit status, and independently verify cleanup. No popup, fullscreen,
G4 or graphics capture is required. An empty workspace does not qualify Mosaic
layout behavior, only the minimal native boot/IPC path.

## Refusals, tests and decision

The source-only fixture lives in the new private LAB until independent review
justifies publication. Its default is a read-only plan: no directory creation,
manager mutation, Bubblewrap, socket connection or native target execution.
A future launch requires its dedicated flag after separate conversational
approval; tests cannot grant that approval. Test production predicates with
fake manager/cgroup/procfs and private temporary files, including session scope,
wrong ELF/ABI/Build ID, inherited environment/socket, forbidden mounts, unit
collision, InvocationID mismatch, recycled PID/startticks, timeout and partial
output. No real scope or compositor in offline tests.

| Gate | Required evidence | Preparation status |
| --- | --- | --- |
| Exact binaries and passive closure | ELF_DEPENDENCIES.json and raw inspection | PASS, passive only |
| Combined benign isolation | Prior immutable receipt and 22 checks | PASS, benign only |
| Current launcher and environment | Fresh observations and frozen sandbox spec | PASS for preparation |
| Fixture and refusal tests | Frozen source hashes, raw tests, independent review | PASS, V4 / 27 offline tests |
| V4 pristine native boot/IPC/cleanup | One reservation consumed; refused before compositor | FAIL before compositor |
| V4 CORE native boot/IPC/cleanup | Pristine failed; no reservation | NOT_RUN |
| V5 pristine native boot/IPC | One approved reservation consumed; allocator failure before IPC | PRISTINE_ALLOCATOR_BLOCKED |
| V5 CORE native boot/IPC | Pristine failed; no ATTEMPT | CORE_NOT_RUN |
| V5 post-attempt cleanup | Independent scope/cgroup/runtime observations | Absent / empty, sampled |
| Physical GPU, FS/G4 and full STEP20C | Outside this tranche | NOT TESTED |

The private LAB must contain GATE2_PREP_REPORT.md, ELF_DEPENDENCIES.json,
SANDBOX_SPEC.md, NATIVE_RUN_REVIEW.md, APPROVAL_GATE2.md, validation logs,
SHA manifest and before/after observations. Preserve raw failures. Record the
final offline verdict here after validation. Only all closed preparation gates
permit GATE2_NATIVE_BOOT_READY_FOR_APPROVAL; otherwise use
GATE2_BOOT_PREP_BLOCKED_WITH_EVIDENCE. Those labels describe preparation only; the later V5 native failure above
supersedes NOT_RUN for pristine, without qualifying boot/IPC.

## Historical preparation evidence — before the V4 attempt

The private source-only fixture is retained in
`/var/tmp/swayfx-mosaic-step20c-gate2-prep-qglkg45r/fixture`, not published as a
production tool. FIXTURE_SHA256SUMS_V3 binds eight files. Independent passive
review rechecked 96 main ELF entries, 46 supplemental tool entries (overlapping),
1409 data files and all 14 files bound by the prior combined benign receipt.
The current fixture inspects 98 unique ELF files, including its Python child.
Retained source manifests match 85 SceneFX and 417 Mosaic files. No rebuild
or new binary reproducibility claim follows.

The default V3 plan passes from Desktop Commander under app.slice (exit0,
launcher_error null) and refuses the Codex session-scope launch path. Both
remain PREPARATION_ONLY / native NOT_RUN. The planned native scope uses
RuntimeMax25s within the supervisor's 30s total bound, preserving cleanup time.

V2's independent review found an uncollected systemctl-stop auxiliary on its
timeout path. The bounded V3 repair reserves one second within the existing
deadline and finalizes only the exact owned Popen. Its delta review passes;
five independently executed mocked methods pass, and the separate tester
passes all 23 offline tests plus eight before/after fixture hashes and AST/local
style checks. Raw initial failures and V2 evidence remain retained. Ruff/Black
are unavailable and were not installed. Native boot, new sandbox mounts,
EGL/renderer/allocator and real cleanup remain NOT TESTED.

The LAB contains the sandbox specification, exact future approval commands,
passive inventories, raw logs, review records and final preparation report.
The frozen fixture README records its pre-review state; NATIVE_RUN_REVIEW.md
and GATE2_PREP_REPORT.md carry later review outcomes without rewriting that
sealed source set. The final preparation verdict is recorded below after the
pre-freeze audit. No native approval or reservation has been consumed.

### Historical V4 preparation outcome (superseded by native refusal)

**GATE2_NATIVE_BOOT_READY_FOR_APPROVAL**. Native Gate 2 **NOT_RUN**.
The unique deep audit on V3 found an additional passive-child finalization
defect in inspect_command on exceptions/cancellation. The single bounded final
repair V4 reserves 0.25s inside the existing deadline, finalizes only its owned
Popen and reports unproven collection explicitly. Four targeted methods were
independently exercised; bounded delta review passes and the separate tester
passes all 27 tests and eight V4 hashes before/after. The default V4 plan
passes through Desktop Commander with no native execution. Historical V2/V3
failures and the failed V3 audit remain intact; no second deep audit occurred.

Two NON_BLOCKING observations persist: internal IPC/exit auxiliaries rely on
the enclosing scope/PID namespace after exceptional local teardown, and the
full attempt chain is not simulated end-to-end. They are not runtime evidence.
The LAB's APPROVAL_GATE2.md binds the exact V4 fixture, future command and
unchanged two-profile identities. No native authorization follows from this
preparation verdict; the first native attempt still requires separate approval.

## Historical V5 correction evidence — before the native attempt

New exclusive mode0700 LAB:
`/var/tmp/swayfx-mosaic-step20c-gate2-v5-ge8wddpa`.
The imported V4 fixture passes all eight source hashes. The sole functional
change adds mandatory `PWD=/tmp` to CHILD_ENV, automatically emitted as an
explicit --setenv after --clearenv. child.py, its complete environment equality
and --chdir /tmp remain unchanged. The new LAB and scope identities are V5-only;
no historical ledger was imported or reopened.

The targeted suite passes 31 tests (27 inherited, four new). The harmless
Bubblewrap child returns 0, strict_equal=true, PWD=/tmp, cwd=/tmp, no extra or
missing keys and no changed shared values. It exercises child.main's guards
with every Popen replaced by a refusal at the native boundary. The sandbox
argv/environment prefix is exact V5; only the final Python script/profile is
replaced with a harmless -c payload. All seven namespaces differ from host;
mount/device/FD/network checks pass. The owned child is reaped with pidfd
confirmation, transient directories removed and no remaining sockets.
This qualifies the environment correction only, not a native boot.

The read-only plan passes from Desktop Commander under app.slice (rc0,
launcher_error=null; 98 ELF inspected passively). The Codex session-scope
refusal is retained (rc1). No real scope or IPC was created by these checks.
HISTORICAL_COMPARISON.json confirms the five historical LAB trees unchanged.
Before the native attempt, V5 receipts ATTEMPT-pristine.json and
ATTEMPT-core.json were absent. The later pristine reservation is consumed.

REPORT_V5.md, APPROVAL_V5.md, ENV_DIFF_V5.json, BENIGN_ARGV_V5.json,
FIXTURE_SHA256SUMS_V5 and raw logs are retained in that LAB. The independent audit passes with no BLOCKING finding. Its NON_BLOCKING
harmless-helper pidfd acquisition cleanup observation received a bounded
repair and two mocked failure subcases; the targeted final suite now passes
32 test methods. A fresh harmless Bubblewrap run also passes on the repaired
helper. The independent repair-delta review passes (12 source hashes, one mocked
method/two failure subcases). The final source/evidence manifests and
FINAL_VALIDATION_V5.json retain the closed checks.
Verdict: **GATE2_V5_READY_FOR_NEW_NATIVE_APPROVAL**.
The read-only reviewer return is transcribed by the parent in
review/REPAIR_REVIEW_V5.md; the unique audit report remains intact. At that preparation stage no native V5 execution was authorized.
The separately approved V5 attempt is recorded above: pristine allocator FAIL,
CORE NOT_RUN. V4 pristine remains FAIL before compositor; V4 CORE NOT_RUN.
STEP20C remains NEXT; production multi-output NOT_YET_SUPPORTED.
