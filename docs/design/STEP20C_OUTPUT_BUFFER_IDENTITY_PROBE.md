# STEP20C output buffer identity probe

**Status: EXPERIMENTAL / PARTIALLY_FEASIBLE.** STEP20C
remains **NEXT** and production multi-output Mosaic is **NOT YET SUPPORTED**.
This probe changes no production source, public ABI, package, clipping rule,
transaction rule or UX policy.

## Question and prior evidence

The [presentation probe](STEP20C_PRESENTATION_IDENTITY_PROBE.md) paired 470
headless `present` events with 482 accepted native output commits by
`(output, commit_seq)`. Twelve initial commits had no observed present. It
did not identify the committed buffer or its pixels. Five initial Mosaic
commits had logical camera 1760 with applied scene -1120 and clip x=1120;
this was a transient logical/applied distinction, not a proven pixel or hit
defect. A `grim` image and an IPC reply cannot establish buffer identity.

The fixed experiment uses HEADLESS-1 `(-800,0)` and HEADLESS-2 `(0,0)`, each
800×600, scale 1, normal transform, with the genuine grabbed XDG chain
TOPLEVEL → POPUP_A → POPUP_B. No output reconfiguration is part of this probe.

## Audited API and lifetime model

The installed wlroots is 0.20.2; the source audit uses upstream tag commit
`d783533489e1f75d6886c2ab5c5960090ef268f8`, especially
`types/output/{state,output,render}.c`, `types/buffer/buffer.c`,
`render/{swapchain,allocator/gbm,wlr_texture}.c`, and
`backend/headless/output.c`. Private SceneFX base is
`37ccd723bef49e6891156ffafce8f549f01446cc`; its modified scene build
and FX texture implementation were inspected. The existing private runner
requests `WLR_RENDERER=pixman`, but the actual log shows SceneFX FX renderer,
OpenGL ES 3.2 on AMD Radeon 780M, with 800×600 GBM buffers and AB24/XB24
DRM formats. The requested environment setting is not evidence of the
renderer actually used.

`wlr_scene_output_build_state()` may return without a new buffer when no
render is needed. On the render path it acquires a swapchain buffer, submits
the render pass, calls `wlr_output_state_set_buffer()`, then unlocks its
temporary acquisition. `set_buffer()` locks the buffer for the output state.
`wlr_output_state_finish()` unlocks that state reference and nulls its field.
The compositor must never keep the state pointer after this call.

`wlr_output_commit_state()` shallow-copies and may filter unchanged fields,
test, fail or succeed. The headless backend accepts the state and defers a
`presented=true` event for an enabled output; it does not supply buffer
bytes in that event. On success wlroots increments the output's native
`uint32_t commit_seq` and synchronously emits `events.commit`, whose `state`
pointer is borrowed for the callback. On failure the sequence is not
advanced. A no-buffer configuration commit must not be assigned old pixels.
The headless deferred event can be absent, for example after output
destruction or allocation failure. Its `(output, commit_seq)` is the only
native link to the accepted commit; the counter can wrap, so the probe must
bound its run and preserve output lifetime/epoch in the key.

`wlr_buffer_lock()` increments a consumer lock. Its matching unlock emits
`release` when the last consumer leaves. The swapchain's release listener
marks its slot reusable only then. A probe-owned lock taken while the
output state is live therefore preserves the buffer object and prevents
swapchain reuse until release. It must be unlocked on rejection, present,
timeout and output destruction. Addresses alone are not durable identities:
assign a probe-local monotonically increasing ID while the owned lock is
held. Bound retained buffers to two per output, each to 800×600 and at most
8 MiB of copied bytes; release by 2 seconds even without `present`. Never
retain `event->state` or a data pointer beyond its callback/access scope.

The direct `wlr_buffer_begin_data_ptr_access(READ)` method may return false.
The GBM allocator in this renderer exposes DMA-BUF, not a data-pointer
implementation; no CPU mapping is assumed. On success only the returned
pointer, format and stride are valid until `end_data_ptr_access`, which is
mandatory. The fallback `wlr_texture_from_buffer()` and
`wlr_texture_read_pixels()` must be called only with a valid FX renderer and
texture on the compositor thread. SceneFX FX implements texture readback
using an EGL context, an internal `glFinish()` and `glReadPixels`; this is a
real synchronization and timing perturbation, not a free observation. The
probe must measure it against the same private compositor without readback.
No direct framebuffer read or extra `glFinish()` is permitted. If the
texture cannot be constructed or read safely, content remains UNOBSERVED.

## Protocol and safety gate

Before readback, verify the exact source/ABI and active renderer, then log
PRE_BUILD, POST_BUILD, COMMIT_ACCEPTED and PRESENT_CALLBACK separately.
POST_BUILD may expose `pending.buffer` when `WLR_OUTPUT_STATE_BUFFER` is set.
Take one additional lock only for such a live buffer, copy dimensions,
format, crop/destination box and state flags, and release on every path.
Do not predict success from `commit_seq+1`; record the native value only
after accepted commit. A commit callback may be used to check the actual
state's buffer identity while its borrowed pointer is valid. Distinguish
rejected commits, observed but uncommitted buffers, configuration commits,
accepted commits without present and `presented=false`.

Try CPU data-pointer access first. If unavailable, audit and try the FX
texture API. Read at most 8 MiB into a private copy, SHA-256 the raw bytes,
record format/stride/width/height and padding separately, and decode only
known DRM formats. Transform, source crop and destination box govern ROI
mapping. A second read at present is allowed only while the owned lock is
still valid; otherwise byte stability until present is UNPROVEN. Never infer
that `present` cryptographically attests to pixels. Compare applied scene
and clip at build with buffer pixels, while preserving any PRE_BUILD to
COMMIT_ACCEPTED differences. Pointer deliveries are a separate event stream.

Run one stable 400 case first. If ownership or synchronization fails, stop
readback and conclude INCONCLUSIVE. Otherwise run 400 → 1280 → 400, at most
three pairs, separate pointer targeting runs and unmodified/private `splith`
controls. Keep source fixtures under `tooling/probes/step20c-buffer-identity/`
and generated builds, logs, sockets and snapshots in one private `/tmp` lab.
Bound trace size, process duration and locks; reap only owned processes.
Preserve negative results and label fixture failures separately.

## Verdict criteria

- **FEASIBLE:** safe true-buffer readback, format-aware pixels matching the
  sampled applied scene/clip, native commit/present pairing, bounded cleanup
  and no blocking regression in this fixed matrix.
- **PARTIALLY_FEASIBLE:** true buffer access exists, but content decoding,
  retention through present or some correlation remains unproven.
- **INCONCLUSIVE:** no safe supported readback or insufficient identity data;
  a clean access failure is a capability result, not a compositor bug.
- **BLOCKED:** reproducible memory violation, crash, confirmed scene/buffer
  inconsistency or blocking renderer regression.

An accepted headless commit is not a physical presentation. Any scaling,
rotation, migration, complete effects/damage or SceneFX ABI qualification is
**NOT TESTED** here. No verdict authorizes STEP20C production work.

## Measured private laboratory

The disposable laboratory is `/tmp/swayfx-mosaic-nested-grab-QwCf4FLm/`.
The private patch is preserved at
[`tooling/probes/step20c-buffer-identity/buffer-identity.patch`](../../tooling/probes/step20c-buffer-identity/buffer-identity.patch),
SHA-256 `d62e8c3a166e60a6eb394de58f51da1e37c3e7ac49671a361bd106ac64e2b427`.
It was applied after the published presentation fixture in a fresh private
checkout, compiled, and compared byte-for-byte with the separately edited
laboratory source. The final fixture uses a stricter cap than the protocol:
one extra buffer lock on HEADLESS-1, 80 snapshots maximum of 1,920,000 bytes
each, and a two-second timer. Each snapshot is written to a private file
after an FX texture read. The source comment, release log and native event
trace document every lock/unlock path. The patch changes no clip/hit rule.

The final three-pair run `private_mosaic-buffer_cycles-1791774958990683685`
kept owner IPC ID 8 and exactly one A/B map through all three 400 → 1280 →
400 pairs. It observed 80 accepted native output commits and 78 headless
present events. Both unmatched commits were initial sequence 2, one per
output, before workspace assignment: **UNEXPLAINED / NO PRESENT OBSERVED**.
The logged `BI_RELEASE age_ns` starts when the post-commit hold record is
installed; it excludes the earlier probe-owned lock time spent in readback
and commit. The two-second timeout likewise starts after that work. It
bounds waiting for an absent `present`, not a stalled GPU readback call.
Thirty-two selected HEADLESS-1 output-state buffers were GBM DMA-BUFs at
800×600, source format XB24 (`0x34325258`), with default full-buffer source
crop and destination. Direct CPU data-pointer access failed cleanly for all
32. SceneFX FX's `wlr_texture_from_buffer()` and
`wlr_texture_read_pixels()` read all 32 into XRGB8888, stride 3200,
1,920,000 bytes, with no row padding. Raw and top-down normalized RGB
SHA-256 are recorded for every selected buffer in `results/`.

For all 32, the native synchronous commit callback contained that same
live buffer, the commit was accepted with its actual `commit_seq`, a matching
headless `presented=true` event arrived, and 28 extra locks were released on
that event. Four other selected locks, IDs 3, 15, 21 and 27, were released
early by a **private instrumentation scope defect**: after their HEADLESS-1
commits, a HEADLESS-2 repaint reached the unconditional global
`bi_release_hold("superseded")` immediately after `POST_BUILD`. The
HEADLESS-2 build had a buffer but the probe did not select it, and no new
HEADLESS-1 submission caused those four releases. Their native presents
arrived later, after the probe had relinquished its references; this does
not prove byte stability through presentation. The old `superseded` log
reason is the instrumentation's label, not a demonstrated same-output
buffer replacement. No sample needed timeout or
output-destroy release. Only three buffers were read a second time while
still locked at `present`; all three raw SHA-256 values matched their
precommit values. Byte stability through `present` for the other 29 is
**NOT TESTED**; four of those were not retained until presentation. The headless event does not itself attest to bytes.

Three representative identified buffers are:

| Probe ID / native commit | Applied scene and clip | Exact A/B pixels | Raw SHA-256 | Present reread |
| --- | --- | --- | --- | --- |
| 8 / HEADLESS-1:23 | `-400,0` / `400,0,800,600` | 42,200 / 17,940 | `9e6d2f7b094fd5124c0207a30cb294acec3a01da15b90008d7f7449d27e1ee7c` | equal |
| 12 / HEADLESS-1:27 | `-1280,0` / `1280,0,800,600` | 0 / 0 | `03e815da50d0f04b16660340db19c1a03225f31bac0824d490c2ffbab0ee165c` | equal |
| 16 / HEADLESS-1:31 | `-400,0` / `400,0,800,600` | 42,200 / 17,940 | `9e6d2f7b094fd5124c0207a30cb294acec3a01da15b90008d7f7449d27e1ee7c` | equal |

All nine selected 1280 snapshots across the three pairs had zero exact A/B
pixels. All 32 sampled commit scenes agreed with their applied clip at 400
or 1280. The 400 snapshots before A/B mapped or after their explicit closure
are not classified as missing popups; the runner event stream preserves
those lifecycle states. PNG captures remain supplementary and are never
assigned a buffer sequence solely by timestamp.

The separate transient run
`private_mosaic-buffer_cycles-1791775118486687664` observed PRE_BUILD,
POST_BUILD and COMMIT_ACCEPTED at logical `scroll_x=1760`, applied tiled
scene `-1120,0` and applied clip `1120,0,800,600`. Its actual HEADLESS-1
buffer at native sequence 10 was read (raw SHA-256
`9a8c1cc62f439f812ce501fe49b99c883c9839f377bdd7f1caaecc05ca5a4c86`),
presented in headless, and released. A/B were not yet in the settled
state; the read does not show an incorrect pixel or invisible hit. The
applied scene/clip, rather than the newer logical camera, are the valid
state to compare with this buffer.

The private stage trace records PRE_BUILD, POST_BUILD and COMMIT_ACCEPTED
workspace, logical camera, applied tiled scene and tiled clip. The native
commit callback additionally records current owner geometry and root-popup
clip; the client trace records A/B mapping and real grab serials. The
owner-visibility guard's Boolean decision and nested-popup mapping are not
atomically exported at each stage and remain **UNOBSERVED** there. The
runner's requested camera commands and IPC replies are kept separately.
No stage record is treated as an atomic rendering or input snapshot.

Separate fixed-geometry pointer runs against the instrumented private
binary used two valid XDG button serials. The visible case delivered a B
button. The clipped B-crossing click delivered an ordinary client button
and child-first B/A `popup_done`, with no B button from that clipped point.
The hidden-owner click delivered no popup button and dismissed B then A.
These events have no native frame ID and are not attributed to a buffer.
Both unmodified SwayFX and private `splith` controls completed their
ordinary sampled cycle without runner failure; they have no Mosaic camera.

### Instrumentation impact and limits

Sequential three-pair runs with the same private instrumentation family,
with and without `BI_OUTPUT_DIR`, observed 80/78 native commits/presents
in both. Median build time was 0.089/0.085 ms; median POST_BUILD to
COMMIT_ACCEPTED was 1.542/0.141 ms; median commit callback to present
callback was 0.384/0.317 ms. The no-readback control used the same stage
logging; the final lock-selection correction only executes with readback.
Total run duration was about 5.5/5.35 s. These are
small samples with host scheduling noise, but the readback path clearly
perturbs timing. SceneFX's internal `glFinish()` is a plausible contributor;
the experiment does not isolate its cost from copying, file I/O and logs.
No crash, renderer error, rejected sampled commit, protocol failure or
repeatable pixel/input inconsistency appeared. Headless presentation is not
physical presentation. The current test does not prove input and pixel
coherence for every transaction generation, all effects/saved buffers,
other renderers or all 80 commits.

**Verdict: PARTIALLY_FEASIBLE.** The actual submitted buffer and sampled
pixels can be read safely through the FX texture API, then tied to a native
commit and headless present while an owned lock prevents swapchain reuse.
The readback's timing cost, four cross-output early releases, three-of-32 second-read
coverage and lack of an atomic scene/input generation prevent a general
temporal-coherence claim.
The next smallest experiment is a bounded lower-impact readback method or
explicit render/transaction generation tag, validated against the same
native buffer identity and pointer event stream. Do not integrate this
private patch into production.

The five-file `buffer-source-sha256.txt` in the lab has SHA-256
`0fed9458f3793d05018af6ce9bf4a674208c700829726c1a1b8e0e434088bfef`;
all five entries passed. The main lab's `buffer-artifacts-sha256.txt` has
501 entries and SHA-256
`94a3097686d47dc3cd06b6c0b24f630544bff5e7b798ccc9934461799310339b`;
all 501 passed. It covers selected raw/derived buffers, the main and
transient results, controls, pointer runs and source manifests. The
historical five-source manifest was verified before the scientific wording
in the fixture README was corrected. Its original README had SHA-256
`add56c3de06671fd14bbb504456f1339eaaa7d0209f11444a9cb940f3435aa59`
and is retained as `buffer-fixture-README-before-rectification.md` in the
private lab. The corrected README has a new hash; re-running the old
manifest directly against the current repository README must flag that
intentional documentation change. The experimental patch, runner,
analyzer and preparation script retain their historical hashes.
fixed patch was independently rebuilt in
`/tmp/swayfx-mosaic-nested-grab-I3RluIc1/`; its instrumented compositor
source was byte-identical and a one-pair run read and committed 20 selected
buffers, paired all 20 with headless present, released 18 on present and
two earlier from the same cross-output scope defect, with three equal second reads. Its separate
`buffer-artifacts-sha256.txt` covers the final-patch pointer and `splith`
controls, one-pair replay and raw buffers: 379 entries, SHA-256
`1ae1b391fc4a0664d852830141d8d012e6e55966a7e38ce6362b4337eb51d5af`;
all 379 passed. The main lab's earlier pointer/control runs were made during
patch development; the independent lab repeats them against the final
fixture. Neither set assigns input to a native commit. These are private
experimental artifacts, not a permanent library dependency.
