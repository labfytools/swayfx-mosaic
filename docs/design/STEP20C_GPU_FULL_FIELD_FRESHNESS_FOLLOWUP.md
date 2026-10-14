# STEP20C — GPU full-field freshness follow-up

> EXPERIMENTAL / INCONCLUSIVE — 2026-10-14. One distinct G1 diagnostic run, no retry. The source design/preflight was accepted; its only raw epoch was rejected before any accepted GPU receipt or analysis. Final dossier review pending; documentary publication PREPARED. STEP20C NEXT; production multi-output NOT YET SUPPORTED.

Ticket: `SWAYFX_MOSAIC_STEP20C_MINIMAL_CORE_BUILD_RUNTIME_AND_GPU_FIELD_GATE_V1`.
LAB: `/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_/`, private and outside Git.
The [historical ROI report](STEP20C_GPU_FBO_CACHE_CAUSALITY.md) remains immutable:
its108 native ROI reads support local outside-fresh-domain history, first
sampled fresh divergence down-2, with whole-field causality INCONCLUSIVE.
Those observations do not qualify the new core or G1.

## Source question and distinct identity

`LAB/gpu-design/HANDOFF.md` records a source-only prospective design. Full
physical 800×600 ping/pong textures remain allocated across down/up passes;
fresh rasterized regions change by pass, rather than resizing those textures.
The audit distinguishes geometry regions, viewport/scissor state, shader
qualifiers, actual buffer formats, copy/cache and arithmetic precision. It does
not treat a `mediump` source declaration or a precision query as a measurement
of effective GPU rounding. The intended experiment extends local support
observations to A/B/A fields with prospective readback/data bounds and explicit
GL/FBO/pack/restoration checks. It does not modify functional shaders, clears,
clamps or samplers.

The separately built/executed diagnostic has SHA 256
`1905a20fa72ebcc7ec47d1584a4653654280288096a20005199eb75673ac0383`, Build ID
`1505e31c3dc08d2a7799c2ee9e1b2705eb61f5fe`. It is not core SHA 29baf31.
Source gate SHA 256
`58535958c0c55b3bee758bfda413df594302122f9a9da2e1a4aedde3889b9f5f`
and independent source/runtime preflights are ACCEPTED for their scoped inputs.
Actual maps/logs identify the diagnostic and wlroots SHA 256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`,
without a dynamic SceneFX mapping. Logs identify EGL Mesa/radeonsi, OpenGL ES3.2
and AMD Radeon780M, with renderD128 descriptors observed. Two EGL_BAD_ALLOC
messages occur during eglQueryDevicesEXT before successful renderer startup;
no causal connection to the later metadata rejection is demonstrated.

## Sole run and immediate rejection

The recorded command `python -B gpu-field/runner.py` returns1 after 4.743s,
`Rejected: dmabuf fields`. It spends one run and three output captures: two H2
references and one H1 witness. Only epoch 1/A is armed. The native log emits
`GPU_FIELD end epoch=1 points=9 complete=1`; these are publication markers for
raw data, not an accepted readback result. No B/epoch 2 or A-return/epoch 3,
accepted epoch receipt or full-field analysis is produced.

| Raw file | Size | SHA 256 |
| --- | ---: | --- |
| `LAB/gpu-field/runtime/epoch-1.meta` | 19,686 bytes | `c8ca51bca694db9e21471356a4260064ed81ab7013a88d4edb4b8572044a825c` |
| `LAB/gpu-field/runtime/epoch-1.rgba` | 8,312,048 bytes | `a6dc7fd873e1ab7e52e04625bacb3251ba8e1aad2e766811efebde7ae7932a99` |

The metadata has 24 records:1 begin,9 samples,11 writes,2 copies,1 end.
`read_success=NOT_PROVEN`, `GL_ERROR_QUEUE=UNOBSERVED`, effective precision
UNCERTAIN. File sizes/hashes establish retained integrity, not glReadPixels
success, synchronization neutrality or independently complete GL restoration.

The read-only diagnosis in `LAB/audit/gpu-rejection/G1-rejection.md` compares
the writer and frozen validator. The validator requires **every** DMA-BUF plane
stride to be at least800×4=3200. All nine samples report DMA-BUF available,
size 800×600 and planes `[[3584,0],[1024,2293760]]`. The first stride passes;
the second1024 fails that first demonstrated rejecting predicate. Role formats
match the validator: main XR24/875713112, effects AB24/875708993, cache
XB24/875709016. Neither absent DMA-BUF nor a wrong role format explains this
immediate rejection. This initial rejection-only audit establishes no GPU
failure, driver defect or specific DCC explanation; raw pixels remain rejected.

A subsequent read-only modifier audit, separately recorded in
`LAB/audit/gpu-rejection/modifier-layout-audit.json`, observes the same modifier
`020000001046bb04` in all nine objects: AMD vendor 2, GFX11 tile version 4,
DCC 1, RETILE 0, PIPE_ALIGN 1. The local libdrm header and the
[Linux DRM format modifier header](https://raw.githubusercontent.com/torvalds/linux/master/include/uapi/drm/drm_fourcc.h)
describe main image surface in plane0 and DCC surface in plane1 for this
non-retiled layout. Requiring the image stride `width*4` on every plane is
therefore not justified for this modifier: a fixture predicate defect is
established. This interpretation neither proves global DMA-BUF validity nor
GL read success and changes no raw gate. No validator repair or replay occurs.

## Cleanup, status and next evidence

Compositor exits 0; background, filler0 and glass exit1 while the other tracked
processes exit0. Scientific cleanup remains INCONCLUSIVE; mechanical cleanup
passes with the private runtime removed and identified processes reaped.
`LAB/gpu-execution/G1-summary.json` indexes49 artefacts with tree manifest SHA 256
`ccd45c0a56c1ee72ff7bcd84711090745012911a7ecc3e0d890aa52ccb715329`.
The scout's read-only audit verifies these49 hashes; it does not rerun the
validator or reconstruct unavailable data. No diagnostic or core retry,
functional shader correction, system-library change or historical replay follows.

`GPU_FULL_FIELD_DESIGN_REVIEW=PASS` denotes the accepted design review receipt.
`GPU_FULL_FIELD_DIAGNOSTIC=INCONCLUSIVE` and
`GPU_WHOLE_FIELD_CAUSALITY=INCONCLUSIVE` denote actual evidence. A new proposed
gate must first specify and review valid per-plane metadata semantics and
read-success/error/restoration observability, using primary format evidence;
only a separately accepted scope/budget may acquire another diagnostic matrix.
No remaining slot is consumed by this documentary suggestion. The
[integration dossier](STEP20C_MINIMAL_CORE_ABI_PACKAGE_AND_INTEGRATION_DECISION.md)
retains PRIVATE_CORE_NEEDS_TARGETED_EVIDENCE; this rejected first epoch closes
neither core graphics nor whole-field causality.
