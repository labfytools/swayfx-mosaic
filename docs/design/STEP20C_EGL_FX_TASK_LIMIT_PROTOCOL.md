# STEP20C — EGL/FX task-limit protocol design — 2026-10-17

Status: **EXPERIMENTAL / DESIGN_ONLY / EGL_FX_RETRY_PREP_BLOCKED**.
New runtime: **NOT_RUN**. No scope, Bubblewrap, EGL/FX helper or compositor is
launched by this mission. This documentary batch deliberately leaves the
historical fixture source unchanged. It does not implement cgroup admission.
The [observed failure](STEP20C_HEADLESS_EGL_FX_PROBE.md#observed-single-attempt--2026-10-17)
precedes this design; its consumed reservation remains immutable.

## Evidence, guarantees and admission

| Route / evidence | Risk | Bound actually supplied | Admission condition / disposition |
| --- | --- | --- | --- |
| Historical RLIMIT_NPROC=256 before bwrap; incident reports 1126 UID threads | Immediate task creation failure, also other possible EAGAIN causes | Real-UID thread accounting, not a probe-local quota | REJECT for retry; no syscall-level causal proof |
| Raise NPROC from a procfs count | Count is racy; unrelated UID load changes; no descendant aggregate | Still only real-UID accounting | REJECT as replacement for task containment; no arbitrary count-plus-margin |
| Omit explicit NPROC override, retain inherited soft/hard limits | Removes the intended extra UID restriction; inherited limit can still cause refusal | No new local task bound by itself | Only with independently verified cgroup admission; never silently raise inherited limits |
| Fresh delegated cgroup v2 with pids.max, possibly manager-owned transient user scope | Wrong subtree, post-spawn migration race, insufficient ancestor budget, unauthorized cleanup | Hierarchical task creation limit for admitted descendants, counting threads | SELECTED design direction, NOT IMPLEMENTED or locally qualified; all gates below required |
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

## Minimal selected protocol, pending implementation and review

Use one fresh, exclusively owned **domain** cgroup for the probe descendants;
keep the collecting supervisor outside the kill target. Prefer the existing
user-manager/delegation approach over a new resource framework. Follow
[systemd's delegation ownership rules](https://systemd.io/CGROUP_DELEGATION/):
do not mkdir or write arbitrary manager-owned subtrees. A transient scope is
only a candidate integration mechanism, not proof that its tasks were admitted
before execution. No systemd-run or control-plane mutation is allowed now.

A future source-only patch is conditional on independent design acceptance.
It must implement the following invariants together, not merely delete NPROC:

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

These are **PLANNED / NOT IMPLEMENTED / NOT TESTED for the new protocol**.
The existing fixture's tests cover only its historical protocol. New tests
must call the actual new admission/refusal paths using fake procfs, cgroupfs,
manager and process adapters; no native scope, bwrap, helper or device call.
An execution sentinel must fail the test on any unintended native boundary.

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

First complete the conditional source-only implementation and offline review.
Then request a separate, bounded **benign-child cgroup qualification** approval:
new private 0700 LAB, exact sealed argv/environment, finite task-limit test,
admission-before-exec and timeout/parent-death cleanup evidence. Historical
scope experiments do not waive this gate. No EGL or Bubblewrap in that phase.

Only after that qualification passes, prepare a distinct fresh 0700 EGL/FX LAB
and revised manifest with the new launcher, effective resource policy,
identities, exact command, ownership and cleanup protocol. Preserve pinned
sources/library ABI and the existing closed device/mount/FD policy. Obtain
independent review on that exact manifest and request **new conversational
approval** for one EGL/FX attempt with its own budget. Do not spend it during
preparation, inherit the old approval, or silently retry any failure.

There is deliberately **no exact future native command** in this edition:
no implemented/qualified cgroup launcher or new reviewed manifest exists.
**EGL_FX_RETRY_PREP_BLOCKED** identifies those preparation gates, not a new EGL
failure. It does not require a human decision to weaken containment. The next
smallest technical step is reviewed source-only admission implementation;
any later native qualification still needs explicit user authorization.

## Validation of this documentary batch — 2026-10-17

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
