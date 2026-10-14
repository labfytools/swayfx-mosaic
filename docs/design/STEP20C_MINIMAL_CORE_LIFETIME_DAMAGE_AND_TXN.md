# STEP20C — minimal core lifetime, damage and transaction limits

> EXPERIMENTAL — 2026-10-14. Same new minimal-core ticket and LAB as the [graphics report](STEP20C_MINIMAL_CORE_GRAPHICS_QUALIFICATION.md). Evidence delta review ACCEPTED for experimental fidelity; final independent dossier review pending. Publication PREPARED. STEP20C NEXT; production multi-output NOT YET SUPPORTED.

LAB is `/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_/`, private and outside Git.
The exact core SHA 256 is
`29baf31aa3eeed259825c87d0799fa5d3dc83710afb967154604eb1c6657f965`.
Historical C3 saved instance15 and PI/C3/OPT instrumentation are not transferred
to this core. Missing PI hooks do not demonstrate that an event did not occur.
The [build/C report](STEP20C_MINIMAL_CORE_BUILD_AND_C_FAILURE_PATHS.md) records
real extracted-body unit tests and their reduced support types; these do not
replace compositor lifetime or rendering proof.

## Natural timeout: native observation and rejected global receipt

E6 opens a real XDG client, arms `hold_next_configure`, then changes runtime
gaps with `gaps inner current set 30`. Owner configure 39 has assigned636×513
and is genuinely held at monotonic ns266629075726834. The native compositor
log records `Transaction ... timed out (1 waiting)` at 00:00:07.998, approximately
five seconds after transaction setup. The held captures precede the timeout;
the natural-timeout captures follow it, before release/ACK and teardown.
This is not an ACK-driven completion or a shutdown timeout.

The release command is recorded at ns266634202244001, ACK 39 at
ns266634202350097 and commit 39 at ns266634203165208. The frozen validator later
requires the held serial to remain unACKed across the accumulated log and
rejects it after the legitimate release/ACK. The raw E6 runner exit1 and
`Ambiguous: held serial must remain unACKed` are retained. A real natural timeout
is demonstrated independently, but the complete saved scenario remains
INCONCLUSIVE with its global receipt not accepted.

Evidence is in `LAB/graphics/runs/E6/run/owner.log`, `compositor.log`,
`events.jsonl`, saved captures and outcome, indexed by
`LAB/graphics-execution-R2/summary.json`. No retrospective validator rerun,
corrected receipt or consumed run retry is used. Normal owner closure is not
acquired; owner error 32 at compositor teardown prevents a universal scientific
normal-close claim. There is no native saved-node identity instrumentation in
this SHA, so saved node/buffer identity is NOT OBSERVABLE here and the native
buffer identity gate remains NOT PROVEN. An SHM commit or a screenshot cannot
identify the retained native saved buffer or its GPU release.

## Input and damage: sampled evidence only

E1's first grabbed chain, E2 fractional/R90 and E3 resize/migration establish
sampled applied geometry, clipped pixels and input observations. E5 supplies
partial hidden-owner evidence before outside dismissal ends the same chain.
Current fullscreen ancestor exemption is actually reached in E4, but its
policy lacks a comparable standard control. The matrix does not establish
an atomic snapshot shared by transactions, scene, hit testing and present.

The private SceneFX `scene_output_damage` intersects damage with the physical
output bounds, logs `SPIKE_DAMAGE` extents and adds the region to damage rings.
An extent is a bounding box of a submitted region. It is not the complete
region, a native frame-content identity, a successful output commit, a present
receipt or proof that every changed pixel was presented. No absent present
event is invented from accepted damage or output state. Scale/transform
observations and sampled whole-output PNG comparisons remain separate from
all-frame logical-to-physical damage coverage.

## Effects and residual restoration

E7 actually exercises classic blur at a fixed64×64 ROI:4,096 pixels change at
constant source, with adjacent variation12.783068783068783 off versus
0.09027777777777778 on. The original source and prospective ROI remain fixed.
Native filter extents are not observable because core OPT instrumentation was
removed. Sampled blur evidence is not evidence for every decoration, saved
buffer, shadow or cache path.

The optimized A/B/A source return retains byte-identical source SHM, but whole
H1 A/A-return equality fails at 33,789 pixels, bbox `[480,0,800,600]`, maximum
absolute RGB delta `[6,5,1]`. Whole H2 remains exact in all three sampled states.
These raw full-image differences remain FAIL; no crop, mask or posthoc
tolerance converts them to PASS. Historical pristine/A/G differences remain
historical comparisons, not a new matched control or evidence transferred
to this SHA. Whole-field causal attribution remains INCONCLUSIVE.

Shadows are enabled, but the observed off/on images are identical. Visible
shadow contribution is therefore **SHADOW_NOT_EXERCISED**, not a validated
shadow exclusion result. The three FX clients close normally with error 0 before
the compositor. E7 remains PARTIALLY_FEASIBLE despite its runner exit0.
The [GPU follow-up](STEP20C_GPU_FULL_FIELD_FRESHNESS_FOLLOWUP.md) documents the
separate diagnostic's rejected epoch and does not repair this core result.

## Gate ledger and closure criteria

| Gate | Recorded status | Evidence needed to close the wider gate |
| --- | --- | --- |
| CORE_SAMPLED_APPLIED_INPUT | PARTIALLY_FEASIBLE | Finish comparable standard/fullscreen/hidden return paths with actual identities |
| CORE_SAMPLED_DAMAGE | PARTIALLY_FEASIBLE | Correlate exact regions and homologous sampled changed pixels without implying all-frame coverage |
| CORE_NATIVE_BUFFER_IDENTITY | NOT PROVEN | Actual native source/scene/saved/output buffer identity join on this binary |
| CORE_GPU_LIFETIME | NOT PROVEN | Native references, retirement/release and GPU completion evidence, independent of client release/teardown |
| CORE_ATOMIC_GENERATION | NOT PROVEN | Evidence for one coherent applied render/input/transaction/present state; no counter mechanism selected |
| CORE_COMPLETE_DAMAGE | NOT PROVEN | Full relevant frame coverage including effects, saved buffers and stale pixels |

CPU unit normal/UBSan/ASan results cover the extracted sidecar/listener/popup
paths only. Full compositor sanitizer is NOT RUN. OOM unit abort remains
`OOM_ABORT_EXPERIMENTAL`, P1 availability risk, not production-safe survival.
Node destruction, Wayland client release, mechanical process cleanup and GPU
completion are different observations. The native compositor/tree authority,
Row0 borrowing and required applied rendering/input consistency are unchanged.
No atomic architecture, popup UX, shader fix or production integration follows.
