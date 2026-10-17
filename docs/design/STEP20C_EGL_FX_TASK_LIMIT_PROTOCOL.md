# STEP20C — EGL/FX task-limit protocol design — 2026-10-17

Status: **EXPERIMENTAL / IMPLEMENTED_OFFLINE / OFFLINE_REVIEW_ACCEPTED**.
New runtime: **NOT_RUN**. No scope, Bubblewrap, EGL/FX helper or compositor is
launched by this mission. The source-only runner now implements the gate;
qualification against the real manager remains separately approval-gated.
The [observed failure](STEP20C_HEADLESS_EGL_FX_PROBE.md#observed-single-attempt--2026-10-17)
precedes this design; its consumed reservation remains immutable.

## Adopted implementation slice — 2026-10-17

The implementation ticket authorizes source-only Python and inert tests now.
Use an explicitly owned transient user scope under app.slice, Delegate=yes,
TasksMax=256, with supervisor outside the scope and bounded manager runtime
and stop deadlines. A fixed bootstrap must wait before any payload exec;
validate the manager/kernel/process identities and release once only.
Channel EOF, invalid nonce, missing proof or timeout must fail closed. Keep
NPROC inherited, removing only the explicit 256 override after cgroup admission.
No real scope or payload may run in this implementation mission. Code and inert
behavioral validation establish IMPLEMENTED_OFFLINE; scoped code review is
accepted; final audit and its one bounded repair are complete. The
private observer repair has independent targeted acceptance.
Fresh private qualification LABs/manifests and exact benign commands are required;
benign qualification and EGL execution each need separate conversational approval.
The historical validation section below retains its original provenance and
does not describe current implementation coverage.

## Evidence, guarantees and admission

| Route / evidence | Risk | Bound actually supplied | Admission condition / disposition |
| --- | --- | --- | --- |
| Historical RLIMIT_NPROC=256 before bwrap; incident reports 1126 UID threads | Immediate task creation failure, also other possible EAGAIN causes | Real-UID thread accounting, not a probe-local quota | REJECT for retry; no syscall-level causal proof |
| Raise NPROC from a procfs count | Count is racy; unrelated UID load changes; no descendant aggregate | Still only real-UID accounting | REJECT as replacement for task containment; no arbitrary count-plus-margin |
| Omit explicit NPROC override, retain inherited soft/hard limits | Removes the intended extra UID restriction; inherited limit can still cause refusal | No new local task bound by itself | Only with independently verified cgroup admission; never silently raise inherited limits |
| Fresh delegated cgroup v2 with pids.max, possibly manager-owned transient user scope | Wrong subtree, post-spawn migration race, insufficient ancestor budget, unauthorized cleanup | Hierarchical task creation limit for admitted descendants, counting threads | IMPLEMENTED_OFFLINE; real qualification NOT_RUN; all gates below required |
| Prior benign-child scope experiments in Gate 2 | Different launcher context, identity and lifecycle | Evidence for that earlier scope only | Do not inherit PASS; repeat only under new explicit approval |
| AS 1 GiB / CPU 5 s / NOFILE 64 / FSIZE 1 MiB / CORE 0 | Multiple processes multiply several limits; tmpfs and total storage remain separate | Per-process address space/CPU/FD limits, per-file size, disabled core dumps | Preserve exact settings; no claim of aggregate memory/CPU/storage quota |
| 8 s payload + 2 s cleanup; 1 MiB per raw pipe | Stuck cleanup, leaked descendants, parent death | Supervised deadline and captured-output bounds on observed paths | Preserve; failure to prove cleanup is BLOCKED, never a retry |
| Closed mount/environment/device/FD policy | Dlopen drift, inherited socket or control-plane leak | Fixed exposure and sealed inputs, not total resource containment | Preserve pins, ABI, manifest closure and exact allowlists; no new host device/mount |

Linux [RLIMIT_NPROC documentation](https://man7.org/linux/man-pages/man2/getrlimit.2.html)
explains the real-UID thread limit and EAGAIN at creation. A procfs scan is a
refusal diagnostic, not an atomic reservation: disappearing entries, unreadable
status, UID changes or inconsistent thread counts must be reported explicitly.
The [kernel cgroup v2 contract](https://docs.kernel.org/admin-guide/cgroup-v2.html#pid)
counts TIDs hierarchically and rejects task creation over the limit. Migration
can exceed pids.max, so a verified empty private group and controlled admission
are essential. A namespace alone supplies no task quota.

## Implemented protocol — real qualification pending

Use one fresh, exclusively owned **domain** cgroup for the probe descendants;
keep the collecting supervisor outside the kill target. Prefer the existing
user-manager/delegation approach over a new resource framework. Follow
[systemd's delegation ownership rules](https://systemd.io/CGROUP_DELEGATION/):
do not mkdir or write arbitrary manager-owned subtrees. A transient scope is
only a candidate integration mechanism, not proof that its tasks were admitted
before execution. No systemd-run or control-plane mutation is allowed now.

The source-only runner implements the following invariants together.
Independent code review and native qualification are separate gates:

1. Validate cgroup2 mount identity from mountinfo, domain type, delegation,
   pids controller availability/enabling, exact owned path, directory identity,
   permissions, ancestor constraints and current launcher membership. Reject
   session-scope placement where the selected delegation requires app.slice.
   Read-only observations in this mission show this agent in a session scope;
   root controller availability does not prove delegation. No permission or
   membership repair is automatic. Historical scope names/PIDs grant no authority.
2. Seal a finite task budget in the new manifest. Candidate **pids.max=256**
   preserves the old intended local ceiling, now counting bwrap, wrappers and
   all helper threads together. It is not an assertion of sufficient capacity:
   LP_NUM_THREADS=2 does not bound every Mesa thread. Review the task inventory
   and ancestor headroom; insufficient capacity refuses without raising limits.
3. Establish ownership and a blocked-child admission handshake before any
   prlimit/bwrap/helper exec or descendant creation. Verify the child's PID
   lifetime, actual membership and effective pids.max before release. Moving
   an already running payload afterwards is forbidden. Parent failure/EOF must
   leave the child unable to execute the payload. Never migrate the desktop or
   collecting agent. No cgroup mount, directory FD or user bus reaches payload.
4. After cgroup admission, omit only the explicit NPROC=256 override, retain
   the inherited UID soft/hard limits and all other prlimit settings. Record
   inherited NPROC, real UID, diagnostic thread-count provenance and effective
   cgroup properties; any known lower-than-UID-load NPROC refuses explicitly.
   Count uncertainty/drift cannot be accepted as a proof of headroom. No fallback
   to a larger NPROC, unlimited task count, unconfined launch or new device.
5. Reserve the new single attempt durably with O_EXCL before creating its
   scope/child or otherwise mutating native execution state. A collision,
   partial reservation, admission failure or spawn failure consumes that attempt;
   do not remove ATTEMPT. Passive inspection writes nothing. Journal bounded
   admission, release, result and cleanup phases, including interrupted paths.
6. Prove cleanup of only the owned scope/subtree, collect the owned child and
   observe subtree empty before removal. Require a tested external cleanup
   authority on supervisor death; die-with-parent alone is not that proof.
   Any use of cgroup.kill requires verified exclusive ownership and supervisor
   exclusion. PID lists alone cannot prove subtree emptiness; use recursive
   cgroup.events populated=0 and task counters as well as child collection.
   Namespace teardown remains an additional mechanism. Cleanup exceeding the
   fixed reserve is failure, never permission for broad kills or retry.

pids.max supplies no aggregate memory, CPU-time or disk ceiling. Preserve the
existing limited claims; do not present AS times task count as a usable memory
reservation. Ancestor pressure and same-UID hostile interference remain risks.
Adding memory/CPU controllers would require a separately reviewed protocol,
not an implicit expansion here. No global UID or manager configuration changes.

## Offline acceptance matrix — required before new preparation

These paths are exercised **OFFLINE** through the actual admission,
bootstrap, collection and cleanup functions, using fake procfs, cgroupfs,
manager/process adapters and local inert channels. The new test module installs
a native-spawn sentinel. Existing historical tests are adapted to schema2.
No real scope, bwrap, helper or device is involved; runtime remains NOT_RUN.

| Offline case | Required observation |
| --- | --- |
| NPROC below UID threads; 256 vs 1126 fixture | Explicit refusal before native state or reservation |
| UID/count drift, disappearing/unreadable proc entries | Diagnostic uncertainty/refusal, no invented capacity |
| Missing controller, cgroup v1, threaded/foreign/replaced group, symlink | Refusal, no writes to foreign subtree |
| Wrong mount identity, unexpected mount/device or environment injection | Refusal before release; inherited bus/FD absent from payload |
| Missing delegation/ownership, wrong launcher scope, exhausted ancestor | Refusal; no fallback and no desktop migration |
| Wrong child lifetime/membership, wrong or unlimited pids.max | Blocked child never released |
| Reservation collision, hash mismatch or altered manifest | No launch; prior reservation/bytes preserved |
| Timeout, closed/full pipes, admission failure, parent death | Bounded receipts; only owned cleanup; unproven collection fails |
| Cleanup target replaced or supervisor inside target | Refuse kill; preserve failure evidence |
| Happy passive path | No mutation, no reservation, no native spawn |

Review exact source hashes and revised manifest semantics on the same bytes;
AST/format checks and targeted tests precede a second review of implementation.
Do not inherit any runtime PASS from mocked tests, linked ELF or the earlier
755 dependency identities. No C, SceneFX, wlroots, engine, package, production
patch or public ABI change is needed or authorized by this documentary design.

## Future authorization sequence — not executable instructions

The runner now has separate schema2 benign/EGL kinds and approval flags.
`prepare.py --benign --qualification-mode nominal|parent-death` creates fresh
0700 qualification LABs and exact sealed passive commands. Independent review
must accept the final scripts and manifests before qualification approval.
The nominal payload is fixed Python; the distinct parent-death LAB deliberately
exits its supervisor after release, with manager runtime/stop limits as the
independent cleanup authority. Its result requires external observation;
a supervisor that has exited cannot certify its own cleanup or write CLEANED.
Its private gate.sock may remain as an artifact. External observation must be
read-only and bind the same invocation, cgroup identity and task lifetimes;
absence of that evidence is not successful cleanup.

After benign qualification passes, prepare **another** fresh 0700 EGL LAB and
manifest. Preserve exact source/library ABI and the closed mount/device/FD policy;
obtain review and a separate new conversational EGL approval. No historical
reservation or approval is reusable. The old NPROC256 fixture remains preserved
in its immutable historical LAB; repository schema2 accepts only the new policy.
No EGL retry is authorized by source-only readiness or by benign qualification.

## Implementation evidence — 2026-10-17

`cgroup_gate.py` implements read-only preflight, explicit manager-owned scope
creation, AF_UNIX SOCK_SEQPACKET admission with SO_PEERCRED on both ends,
PID/startticks/pidfd and invocation/inode checks, single release, bounded drain
and owned cleanup. A bounded observer reads recursive emptiness concurrently;
ENOENT/ENODEV is never a substitute for populated=0. Missing evidence produces
CLEANUP_UNPROVEN. The bootstrap closes descriptors above stderr before exec.

The helper is loaded only after its digest check and without bytecode writes;
real isolated passive-CLI tests exercise the no-write boundary. Scope properties
are TasksMax=256, RuntimeMaxSec=12s, TimeoutStopSec=2s, KillMode=control-group:
the manager deadline bounds orphaned execution independently of the supervisor;
normal supervision uses a 10-second deadline including cleanup. These limits
remain local experimental values to qualify, not measured Mesa requirements.
New manifests seal the scope command/properties, scripts, tool ELF identities
and dependency closure. No C, compositor, ABI or packaging change is made.

The inert suite passes; exact final counts and source bindings belong to the
final review and private handoff after the bounded repairs. A real
passive preparation exposed a systemctl RUNPATH resolution defect; the failed
fresh LAB and traceback are retained privately and the defect is repaired with
explicit ELF resolution tests before final preparation. No native attempt was
consumed by that preparation failure.

Pre-admission manager diagnostics are not retained as raw stdout/stderr; the
supervisor error is retained. This is a bounded diagnostic limitation, not
proof of manager behavior. Neither offline tests nor the manager deadline
establish actual cleanup after supervisor death: nominal and parent-death
qualification remain NOT_RUN. Final review may establish readiness to request
benign approval; this edition does not predeclare that readiness or authorize
any scope, benign payload, Bubblewrap or EGL execution.

## Historical validation of the preceding documentary batch — 2026-10-17

The existing `test_probe.py` suite passes **23/23** with
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tooling/probes/step20c-egl-fx -p test_probe.py -v`.
It uses inert Python children for supervisor paths and mocks the native launch
boundary; no Bubblewrap or real helper is run. AST parsing of the three existing
Python scripts and file-target checks for local links in the seven changed
Markdown files pass. `git diff --check` passes. These checks do not test the
proposed cgroup protocol or certify Python style changes (there are none).

Read-only before/after SHA256 inventories agree for all 593 regular non-symlink
files under the historical LAB; its manifest still lists 755 dependency
identities, including external files. This inventory checks retained file bytes,
not an atomic filesystem snapshot or metadata preservation guarantee. No raw
inventory, log, private manifest, binary or personal scope identifier is published.
Native build, C harness, cgroup qualification, Bubblewrap and EGL/FX: **NOT RUN**
in this mission. Independent review and actual publication outcome are reported
in the task handoff; this document does not predeclare their PASS.

## Source-only closeout — 2026-10-17

**CGROUP_PROBE_IMPLEMENTED_OFFLINE_READY_FOR_BENIGN_APPROVAL**.
Repository behavior tests: **75 PASS**; Python AST5, local link targets and
diff whitespace checks pass. Two fresh benign LABs contain matching source
fixtures,47 sealed file identities and39 ELF records each; their exact isolated
passive commands pass without writes or ATTEMPT. The actual native runner and
external observer remain **NOT_RUN**.

The single final audit found one BLOCKING in the private parent-death observer:
it could accept cleanup without observing an executed benign payload surviving
its supervisor. The bounded repair requires exact cmdline/PID/startticks/cgroup,
same scope invocation/inode/policy, at least1s observed survival after the
supervisor lifetime disappears, then observed recursive emptiness and unit/cgroup
absence within14s (global30s). Fourteen deterministic tests pass; independent
targeted review accepts this repair. No second general final audit was run.
The configuration alone is not claimed to prove RuntimeMax caused termination.

Private LABs retain REPORT_IMPLEMENTATION.md, BENIGN_GATE_APPROVAL.md and
EGL_GATE_NEXT.md, reviewed source/diff hashes and test evidence. Nominal and
parent-death cases have distinct budgets; the latter needs its concurrent
read-only observer. Exact private paths/digests belong to the approval dossier
and task handoff, not public unit identifiers. Historical evidence and consumed
reservations are unchanged. Real manager admission, parent-death cleanup and
Mesa task sufficiency remain unqualified. Separate conversational approval is
required before benign acquisition, then another fresh LAB/review/approval
before any EGL attempt. STEP20C remains NEXT, multi-output NOT_YET_SUPPORTED.
