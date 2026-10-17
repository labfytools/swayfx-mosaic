# STEP20C — isolated EGL/FX probe preparation

Status: **EXPERIMENTAL / EGL_FX_PROBE_BLOCKED_BEFORE_HELPER / EGL_NOT_RUN / ALLOCATOR_NOT_ATTEMPTED**.
The single historical launch budget is consumed; no retry is authorized.
New admission implementation: **EXPERIMENTAL / IMPLEMENTED_OFFLINE / OFFLINE_REVIEW_ACCEPTED**;
real cgroup qualification and new EGL runtime **NOT_RUN**.
See the [task-limit protocol](STEP20C_EGL_FX_TASK_LIMIT_PROTOCOL.md).
The source-only fixture prepares one future measurement, without authorizing execution.
STEP20C remains NEXT; production multi-output NOT_YET_SUPPORTED.
The [Gate 2 V5 failure](STEP20C_HEADLESS_BOOT_GATE2.md) remains
PRISTINE_ALLOCATOR_BLOCKED / CORE_NOT_RUN; V4 failed before compositor execution.
Historical V4/V5 LABs and verdicts are immutable.

## Measurement contract

Use real pinned SceneFX/wlroots objects without sway_server, compositor,
Wayland display/socket, client, IPC or output capture. A headless backend needs
only its own event loop; it need not be started or create outputs. Inspect
software EGL separately from compatibility of FX render targets. No physical
host device, seat, desktop socket, bus or host network may be exposed.

| Quantity | Prepared observation / explicit limit |
| --- | --- |
| EGL vendor, version, display extensions | Query the actual display owned by the FX path; do not infer from installed metadata |
| Selected software EGL device | Query the device associated with that display and require EGL_MESA_device_software; missing identity is refusal |
| DRM FD | Both backend and renderer getters must return exactly -1; otherwise refusal, no hardware fallback |
| Backend and renderer target caps | Read real headless buffer_caps and renderer render_buffer_caps |
| Texture support | Query format sets separately for DMABUF, DATA_PTR and SHM; no invented texture_caps field |
| Target formats | Query the real FX render format set, distinct from texture formats |
| Target allocation | Always NOT_ATTEMPTED; report pinned-source eligibility separately from allocation or rendering |

Only source-backed, existing interfaces may be used. Internal interfaces must
be identified as such and bound to the exact pinned pair; no public ABI change
or invented getter is permitted. The reviewed choice is explicit
`wlr_egl_create_with_drm_fd(-1)` followed by `fx_renderer_create_egl(egl)`.
These are the real operations of SceneFX's software creation path, accessed
through the exact internal headers, without reading either private struct.
This measures those constructors; it does not exercise the public
fx_renderer_create(backend) entrypoint or its backend-selection policy.

Require EGL_EXT_device_query or EGL_EXT_device_base and query EGL_DEVICE_EXT from the
created display before FX creation. Require EGL_MESA_device_software and reject
DRM device extensions before FX initialization: its DRM getter can otherwise
attempt to open a render node. The selected device identity is borrowed until
EGL destruction, as specified by
[EGL_EXT_device_query](https://registry.khronos.org/EGL/extensions/EXT/EGL_EXT_device_query.txt). Before FX construction succeeds the helper owns EGL; after
success the renderer owns it. Destroy renderer (or untransferred EGL), then
backend, then event loop. Format sets are borrowed until renderer destruction.
The declared wlr_fx_renderer_get_egl has no export and must not be used.

No allocator is called: eligibility from real caps plus pinned source is
reported separately from target allocation, which is NOT_ATTEMPTED. Without
UDMABUF and with DMABUF-only FX targets/FD -1, no pinned allocator route is
compatible under this confinement. No general impossibility theorem is claimed.
FX construction initializes its own internal resources; the helper calls no
buffer/framebuffer creation or draw command. No invented texture_caps field is
used. JSONL records EGL identity before FX construction, then formats, caps,
FDs and completion. Strings are bounded to 16384 bytes, sets to 256 formats,
each format to 64 modifiers, and the four sets to 4096 modifiers total.
Missing identity or overflow refuses rather than truncates. Exit 0 means only
completed measurement; exit 20 means refused/incomplete. Inaccessible required
ABI or a mandatory host device blocks preparation instead of weakening isolation.

## Source-only preparation and identity boundary

The [eight-file fixture](../../tooling/probes/step20c-egl-fx/README.md) contains
probe.c, prepare.py, run.py, cgroup_gate.py, test_probe.py,
test_cgroup_admission.py, test_probe_mocks.c and README.md.
Its README gives exact preparation and inert-test commands. prepare.py creates
a new private mode0700 LAB, extracts SceneFX and wlroots from pinned Git
objects, checks every extracted blob, compares compiled installed headers and
copies only generated wlroots config/version headers. The pins and public
source URLs are recorded in the [allocator triage](STEP20C_HEADLESS_ALLOCATOR_TRIAGE.md).
Compilation uses C17 syntax checking and linking, SceneFX before wlroots;
neither the target loader, ldd nor the real helper is executed.

The private manifest seals argv, environments, compile commands, cc -M inputs,
source/header/script/tool/helper hashes, ELF identities and DT_NEEDED closure.
The historical prepared manifest covers 755 files, 80 ELF identities,
17 compared installed headers and 557 source blobs. Installed ELF bytes/Build IDs are pinned, not
reproduced from source; header/export agreement proves no binary source identity.
Mesa EGL, swrast, GBM dri and gallium providers are explicit closure seeds;
conditional runtime dlopen remains unobserved. The inspected ELF closure has
no RPATH/RUNPATH; prepare.py does not enforce a general RPATH rejection policy.
Licences remain in private source archives; no binary, raw log or private
manifest belongs in Git.

## Historical pre-attempt confinement and budget

run.command fixes prlimit then Bubblewrap with --unshare-user --unshare-all
--disable-userns --new-session --die-with-parent --clearenv, read-only /usr,
/bin → usr/bin and /lib,/lib64 → usr/lib, private /proc and /dev, tmpfs
/dev/shm, /tmp and /run, and only the new helper bound read-only at /probe.
The working directory is /tmp. No host HOME, /etc, /sys, /run/user, /dev/dri,
/dev/input, /dev/udmabuf, seat, desktop socket, bus or host network is exposed.
The supervisor environment is exactly PATH=/usr/bin and LC_ALL=C; the helper
adds PWD=/tmp, WLR_RENDERER_FORCE_SOFTWARE=1, WLR_RENDERER_ALLOW_SOFTWARE=1,
LIBGL_ALWAYS_SOFTWARE=1, LP_NUM_THREADS=2 and
__EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/50_mesa.json.
This selects the Mesa ICD; software identity still requires the associated-device
query. No caller-supplied mount/environment or automatic alternative ICD is allowed.

Budget: one launch, no retry; 8 s payload plus 2 s cleanup reserve within a
nominal supervised 10 s total; 1 MiB each raw stdout/stderr; AS 1 GiB, CPU 5 s,
NOFILE 64, FSIZE 1 MiB, CORE 0 and NPROC 256. AS/CPU apply per process; NPROC
applies to the global UID, not an aggregate cgroup. The supervisor closes
inherited FDs, drains pipes concurrently, uses pidfd when available and cleans
only its own unreaped leader/process group; bwrap PID namespace exit terminates
its descendants. Unproven collection is failure. This provides no hostile
same-UID-peer guarantee. Receipts/raw channels stay bounded and private, with
atomic writes/fsync. No systemd scope, compositor, client, socket or capture.

## Historical pre-attempt preparation and approval boundary

Offline evidence: 23 Python tests and eight inert C-mock scenarios passed;
the real helper passed C17 syntax checking and linking without execution.
The C harness replaces all EGL/Wayland/wlroots calls and links only libc.
Independent validation confirms the sealed target manifest, all 755 file
identities, fixture/source correspondence, passive plan, C17 syntax and inert
C tests. Python tests were also independently exercised on identical fixtures
in a separate preparation; its different path-dependent manifest is not drift
of the target LAB. Historical V5's 101 checked files are unchanged.
The unique independent code/protocol review is PASS, with no BLOCKING or
NON_BLOCKING defect. Final preparation verdict:
**EGL_FX_PROBE_READY_FOR_APPROVAL / runtime NOT_RUN**.
No ATTEMPT exists and the single-launch budget remains unconsumed. This verdict
qualifies preparation only; software EGL/FX success remains unmeasured.

The default run.py entrypoint only verifies and prints a passive plan: no files
created, Bubblewrap or ELF launched. Copy the manifest digest from the reviewed
preparation; do not recompute it to accept drift. The historical command template below is retained for provenance only; it is
not an admissible retry procedure:

```sh
/usr/bin/env -i PATH=/usr/bin LC_ALL=C /usr/bin/python3 -I \
  /var/tmp/NEW_PRIVATE_LAB/fixture/run.py \
  --lab /var/tmp/NEW_PRIVATE_LAB --manifest-sha256 REVIEWED_DIGEST \
  --approve-native-probe
```

This is **not authorization**: a separate conversational approval is required.
The flag durably consumes ATTEMPT before spawn; any failure, including spawn
failure, forbids retry. Existing ATTEMPT also refuses the passive plan.
Invoking the real helper, even --version, remains forbidden in this preparation.
No device access, compositor, scope, live IPC, installation or production ABI
change is authorized. Runtime remains NOT_RUN.


## Observed single attempt — 2026-10-17

This dated result supersedes the pre-attempt READY_FOR_APPROVAL and unconsumed
budget statements above, which remain historical evidence. The approved launch
was made from published commit `99f1fbeb4010c7f3ff82c97138431a3c0c5c387c`.
The private historical LAB is retained locally, unchanged; neither its private
manifest nor raw logs are published. Its reviewed manifest SHA256 is
`205ca2780bb1ca4d21a71beabd46b9aef27d9b6b64fa6345c749f7f3280e75c8`.

Read-only inspection in this mission confirms ATTEMPT with budget_consumed=1,
stdout length 0, stderr length 71, and result cause=exit, returncode=1,
collected=true, elapsed=0.003128459007712081 seconds, error=null.
The diagnostic is `bwrap: Creating new namespace failed: Resource temporarily unavailable`.
The retained launcher is byte-identical to run.py at baseline `99f1fbeb` and applies
`prlimit --nproc=256` before Bubblewrap creates namespaces.

The namespace creation failed before the C helper, EGL or SceneFX started.
No EGL identity, capability, FD, allocation, texture or target was measured.
The strict verdict is **EGL_FX_PROBE_BLOCKED_BEFORE_HELPER / EGL_NOT_RUN /
ALLOCATOR_NOT_ATTEMPTED**, not an EGL initialization failure. Collection of
the child is recorded; it does not establish renderer success.

The supplied incident diagnosis reports 93 processes / 1126 threads for real
UID 1000, with zero procfs read errors, and the normal process limit 60706.
These are historical measurements supplied with the ticket, not a new atomic
procfs snapshot. Linux RLIMIT_NPROC accounts threads of the real UID. Setting
256 below that reported load is the very probable cause of the immediate
EAGAIN-like namespace failure; no syscall trace proves which kernel counter
failed. Namespace permission metadata alone cannot eliminate every other cause.
See the [Linux manual](https://man7.org/linux/man-pages/man2/getrlimit.2.html).

The previous 755 sealed dependency identities and linked helper remain passive
preparation evidence, with no new runtime success. The reservation is exhausted
even though the helper never started. Never remove ATTEMPT, modify the old LAB,
rerun its launcher, or reuse its digest to admit revised inputs. No new native
process, Bubblewrap, scope, device exposure or compositor was authorized or
executed in this incident follow-up. The subsequent
[task-limit protocol](STEP20C_EGL_FX_TASK_LIMIT_PROTOCOL.md) now records the
source-only implementation separately from this historical result.

## Subsequent cgroup admission implementation — offline only

The schema2 runner implements a manager-owned probe-local scope, a blocked
AF_UNIX peer-credential admission handshake before payload exec, inherited
NPROC without the explicit 256 override, bounded collection and owned cleanup.
The scope budget is TasksMax=256, RuntimeMaxSec=12s and TimeoutStopSec=2s;
normal supervision remains bounded to 10 s including cleanup. Mocked/inert
validation exercises the admission and refusal paths without a real scope,
Bubblewrap or EGL helper. This establishes IMPLEMENTED_OFFLINE, with final
review accepted after a bounded private-observer repair; it does not
qualify real manager behavior or Mesa capacity.

Fresh benign nominal and parent-death LABs require distinct manifests and budgets.
Parent-death qualification requires external read-only observation: a dead
supervisor cannot certify CLEANED, and its private gate.sock can remain as an
artifact. Pre-admission manager diagnostics are not retained as raw output;
the supervisor error remains available. These limits must stay explicit in
the qualification handoff. Real qualification is NOT_RUN and requires new
conversational approval after the accepted offline review. Only after benign qualification
may a separately reviewed fresh EGL LAB be proposed for its own approval.
The historical ATTEMPT, manifest, failure and exhausted one-launch budget
remain unchanged. STEP20C stays NEXT; production multi-output remains
NOT_YET_SUPPORTED.
