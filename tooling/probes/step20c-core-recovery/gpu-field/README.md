# STEP20C GPU DCC recovery — EXPERIMENTAL, offline only

This versioned validator copies the executed historical `validate.py`,
`analysis.py` and `test_fixture.py`; exact parent paths/hashes are recorded in
`provenance.json`, and `parent-delta.patch` records their complete source delta.
The historical runner remains byte-identical and is deliberately not copied:
this scope has no admissible runtime acquisition gate or launcher. The two
runner-dependent controller tests are omitted from the copied test module;
31 inherited validator/model tests and five actual-G1 test methods run offline.
Generated reports, logs and payload remain in the new private LAB.

## Exact bounded contract

The local authority is `/usr/include/libdrm/drm_fourcc.h`, SHA256
`992f33804acda60b0b46f1a272942c3592484ea3217d469239f1cb12249de2eb`.
Its AMD section assigns the main image to plane 0 and DCC to plane 1 when
DCC is enabled without RETILE. The same meaning was independently checked
against the [primary Linux UAPI header](https://linux.googlesource.com/linux/kernel/git/torvalds/linux/+/refs/heads/master/include/uapi/drm/drm_fourcc.h).
That moving upstream reference corroborates the semantics; the local SHA pins
this fixture's actual source authority. The exact allowlisted modifier
`020000001046bb04` has vendor AMD=2, tile-version GFX11=4, tile=27,
DCC=1, RETILE=0 and PIPE_ALIGN=1. Other nonzero modifiers are rejected.

For the four known packed 32-bit RGB formats, the image plane must have a
stride of at least `width*4`, divisible by four. The auxiliary DCC pitch is
nonzero uint32; it is not an image stride. Offsets and arithmetic are bounded
and the fixture restricts the metadata to image-before-auxiliary offsets.
This latter restriction is a bounded sanity filter, **not a universal modifier
layout rule**. Exported FD identities and allocation lengths are not observed.
No DCC alignment, tiled physical size, auxiliary extent or allocation bounds
are proved. An accepted plane record returns those explicit limitations.
The linear one-plane case is a synthetic regression control only; no new
non-DCC GPU run or qualification is claimed.

## Actual G1 replay and second blocker

The replay reads only immutable epoch1 metadata/arm/payload and verifies their
fixed hashes. Nine native reads, offsets/ROIs, hashes, attachment channels,
context and all nine saved/restored GL/PACK state fields validate. The added
G1 envelope checks all 11 native writes and two copies, source/destination,
texture unit, sampler/matrix types, composition domains and native order.
A successful envelope is only structural evidence: it never replaces the
strict `validate_epoch()` result.

After the plane repair, **the real epoch still rejects `effective halfpixel`**.
For stages 0–2, `glGetUniformfv` published bits `[983818240,987398144]`, while
float32 source expressions predict `[983815946,987395086]`. For stages 3–5,
observed bits are `[967041024,970620928]` versus `[967038730,970617870]`.
Both shaders declare `precision mediump float`; the private hook queries
active uniforms with `glGetUniformfv` then preserves their bits. Quantization
is a possible explanation, not a proven diagnosis of these readings. No
post-observation tolerance or shader change is introduced, and the float64
ideal model is not upgraded into a GPU arithmetic model.

The hook itself explicitly says its alpha sentinel is not proof of GL read
success or restoration of the GL error queue. `GL_ERROR_QUEUE=UNOBSERVED` and
`read_success=NOT_PROVEN` remain immutable. Fixing those acquisition limits
would require a separately authorized diagnostic contract/build; this ticket
allows zero new compositor/GPU builds. Hence `GPU_DCC_RUNTIME=NOT_RUN`, no
runtime reservation and no new GPU runner. `GPU_MODIFIER_AWARE_OFFLINE` is
`INCONCLUSIVE` for the complete gate even though the isolated plane correction
and adversarial tests pass. Independent review remains pending.

Only A exists: no B or A-return is acquired. The sampled 16×16 U0/cache RGBA
bytes are exact; cache/presubmit differ. Neither observation establishes the
cause of a whole-output inequality, physical DCC correctness, precision loss,
or an A/B/A difference. `GPU_WHOLE_FIELD_CAUSALITY=INCONCLUSIVE`.
The original G1 outcome, exit1, cleanup limits and INCONCLUSIVE remain unchanged.

## Reproduce without starting anything

From repository root (historical private evidence must still exist):

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover \
  -s tooling/probes/step20c-core-recovery/gpu-field -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-core-recovery/gpu-field/replay.py
```

Mutation tests cover unknown formats/modifiers, wrong plane count, image/aux
pitches, duplicated/overflowing offsets, missing fields, truncated/corrupt
samples, read validity/sentinel, GL restoration/context/attachments, ROI/hash,
missing copies/writes, source aliases, samplers and duplicate uniforms. The
unchanged inherited suite additionally covers all nine restoration fields,
clear/external write/lifetime events, blur order, region holes, ping-pong
continuity, reconstruction and ideal-model negative predictions.
