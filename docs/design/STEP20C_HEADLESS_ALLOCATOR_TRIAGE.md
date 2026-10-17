# STEP20C — headless allocator triage

Status: **EXPERIMENTAL / PRISTINE_ALLOCATOR_BLOCKED / CORE_NOT_RUN**.
This is a source-based triage of the [V5 native failure](STEP20C_HEADLESS_BOOT_GATE2.md),
not a renderer repair or a new native authorization. STEP20C remains NEXT;
production multi-output NOT_YET_SUPPORTED. No compositor, build, IPC, device,
scope or production change is authorized by this note.

## Observed result and source boundary

The single approved V5 pristine run failed after 0.361879 seconds, before
private IPC, with oracle null. Its first allocator error was ENOENT opening
`/dev/udmabuf` in the private `/dev`; allocator creation then failed.
CORE has no ATTEMPT and is CORE_NOT_RUN. The preceding Mesa software-rendering
warning is not established as fatal. No effective renderer/backend capability
masks, EGL provider or selected native device identity were recorded.

Static inspection used pristine source archives without `.git`, at these
retained pins. Twelve inspected SceneFX/wlroots files match the corresponding
Git commit objects; this proves neither binary reproducibility nor live capabilities:

- [SwayFX fd71a6bdc061bd633b488ae7b83e8a6981d22f86](https://github.com/wlrfx/swayfx/blob/fd71a6bdc061bd633b488ae7b83e8a6981d22f86/sway/server.c#L283):
  `server.c:283` directly calls `fx_renderer_create`; `:305` calls the allocator.
- [SceneFX 37ccd723bef49e6891156ffafce8f549f01446cc](https://github.com/wlrfx/scenefx/tree/37ccd723bef49e6891156ffafce8f549f01446cc):
  `render/fx_renderer/{util.c,fx_renderer.c,fx_framebuffer.c,fx_offscreen_buffers.c}`
  and `render/egl.c` govern the FX path described below.
- [wlroots d783533489e1f75d6886c2ab5c5960090ef268f8](https://gitlab.freedesktop.org/wlroots/wlroots/-/tree/d783533489e1f75d6886c2ab5c5960090ef268f8):
  `render/allocator/{allocator.c,shm.c,udmabuf.c}`, `render/pixman/renderer.c`,
  `util/shm.c` and `backend/{headless,multi}/backend.c` govern selection.

## Allocation contract inferred from those sources

`open_preferred_drm_fd` honors `WLR_RENDERER_FORCE_SOFTWARE=1` before render-node
selection, preserving FD -1 on this creation path. SceneFX then calls
`wlr_egl_create_with_drm_fd`; its negative-FD path selects an EGL device with
`EGL_MESA_device_software` and allows software. GBM fallback requires FD >= 0.
This explains the intended software route, not the effective V5 EGL identity.

`fx_renderer_create_egl` initializes `render_buffer_caps` to DMABUF only.
SHM/DATA_PTR texture import is a separate capability, not SHM render-target
support. `fx_framebuffer.c:138` rejects targets without `wlr_buffer_get_dmabuf`.
Headless advertises DMABUF, SHM and DATA_PTR; the multi backend intersects
capabilities of presenting backends. Actual V5 masks remain unmeasured.

Allocator predicates test **nonempty bit intersections**, not containment of
all bits in a combined mask. In source order, with B = backend caps,
R = renderer render-buffer caps, D = selected allocator DRM FD:

| Candidate | Eligibility predicate, before compiled-feature/create failures |
| --- | --- |
| GBM | `(B & DMABUF) && (R & DMABUF) && D >= 0` |
| SHM | `(B & (SHM \| DATA_PTR)) && (R & (SHM \| DATA_PTR))` |
| DRM dumb | `(B & (DMABUF \| DATA_PTR)) && (R & (DMABUF \| DATA_PTR)) && D >= 0 && drmIsMaster(D)` |
| UDMABUF | `(B & (DMABUF \| SHM)) && (R & (DMABUF \| SHM)) && D < 0` |

Thus headless + FX DMABUF-only + negative FD skips SHM and reaches UDMABUF
when compiled in. `udmabuf.c:146` opens `/dev/udmabuf` with `O_RDWR | O_CLOEXEC`.
That source path is consistent with the observed failure; it is not a runtime
capture of every predicate. Host metadata reports root:kvm mode0660 and the
user outside kvm. Metadata grants no authority to open or expose the device,
change permissions/group membership, or broaden the sandbox.

## Decision matrix

| Route | Evidence | Hypothesis / future test | Risk / disposition |
| --- | --- | --- | --- |
| Existing software FX | Negative-FD EGL route; DMABUF render targets; UDMABUF ENOENT observed | Measure provider, FD and format/capability sets in a separately approved FX-only helper | Software EGL alone does not supply a compatible allocator; BLOCKED |
| Pixman + SHM | Pixman advertises DATA_PTR; SHM allocator uses `shm_open`, unlink, `ftruncate`, `mmap` | A writable private `/dev/shm` could serve this distinct allocator route without a physical device | No FX compatibility proof; not a substitute pristine control |
| `WLR_RENDERER=pixman` alone | SwayFX directly creates SceneFX; `fx_get_renderer` asserts FX, including offscreen buffers | Any private renderer/compositor change needs a separate design and approval | Environment override cannot replace this FX contract |
| Host UDMABUF / DRM | Device-opening source requirement; no approved exposure | No device experiment proposed here | Sandbox expansion excluded; no workaround promised |

## Smallest next experiment to authorize

Offline validation passes eight cases executing the verbatim allocator-selection
function compiled as C17 with inert callees, plus six static FX/Pixman/call-site/
framebuffer assertions. No device was opened and no EGL was initialized. These
checks validate source selection, not effective EGL identity or target allocation.

The next runtime decision would require a **new explicit approval** for one
small EGL/FX-only helper, without compositor, IPC, systemd scope or host-device
exposure. Before execution, review exact pinned sources/library identities,
helper code, fixed deadline, output/resource bounds and cleanup. Use fresh
private temporary/runtime storage and private `/dev/shm`; never reuse a V5 LAB
or reservation. Record EGL provider/software-device identity, FD < 0,
backend/render/texture caps and render-target formats; refuse device fallback,
missing identity or incompatible allocation. No retries or automatic escalation.

This helper is a proposal, NOT_RUN: measuring EGL identity/caps/formats cannot
resolve an absent allocator and would not qualify boot, rendering or CORE. If it finds no compatible allocation under the existing containment,
retain PRISTINE_ALLOCATOR_BLOCKED / CORE_NOT_RUN and report the limitation;
any renderer or sandbox design change needs its own scoped decision.


## EGL/FX follow-up — 2026-10-17

The [single EGL/FX attempt](STEP20C_HEADLESS_EGL_FX_PROBE.md#observed-single-attempt--2026-10-17)
consumed its reservation but failed at Bubblewrap namespace creation before the
helper. EGL_NOT_RUN / ALLOCATOR_NOT_ATTEMPTED: it supplies no new allocator or
renderer evidence and leaves V5 PRISTINE_ALLOCATOR_BLOCKED / CORE_NOT_RUN intact.
The [task-limit design](STEP20C_EGL_FX_TASK_LIMIT_PROTOCOL.md) is offline only;
its proposed cgroup/scope is a new protocol, not authorized by the older
scope-free proposal above. New qualification and EGL execution need separate
approvals. Historical LABs and raw verdicts remain immutable.
