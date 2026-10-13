# Optimized blur cache fixture

**EXPERIMENTAL / PARTIALLY_FEASIBLE; preserved evidence, campaign closed.** Read the
[protocol](../../../docs/design/STEP20C_OPTIMIZED_BLUR_CACHE_PROBE.md) before
running. Reconstruct pinned sources in one new LAB outside Git. Do not use
or reset a historical saved-buffer/effects ledger. No production source,
package, installed library, shader or clipping algorithm changes.

The preparation builds only; the locked ledger's offline tests must pass
before the three single-mode runs. All generated protocols, binaries,
private libraries, PNGs and raw logs remain in LAB. Record every failed
reserved launch/action; no retry for a consumed mode. Analyze offline after
owned-process/socket cleanup. The separate freeze ticket publishes this source-only historical evidence.

## Execution and reconstruction

The V1 campaign is closed in
`/home/fy59/swayfx-mosaic-optimized-blur-_ppdud_y`. C0 failed before captures
through duplicate same-size background configures, without a retry. Its
original `clients-c0-original.c` and `run-c0-original.py` are preserved as
failed fixture evidence. The current client ACKs background configures
without submitting pixels; all A/B images are runner-commanded after a
persistent reservation. C1/C2 completed central cache mutation, filtered
pixels, H2 stability and sampled cleanup; boundary differences remain.
The verdict is **PARTIALLY_FEASIBLE**, architecture **UNDECIDED**. The
freeze publishes this fixture/report without new graphical execution.

Build-only reconstruction in a fresh LAB requires the pinned project
commits in a full clone, Meson/Ninja/C17, installed compatible wlroots
0.20.2/SceneFX build dependencies, Wayland scanner, and network access to
the pinned SceneFX and protocol sources. No system install is used.

```sh
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-optimized-blur-cache/prepare.py
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-optimized-blur-cache/test-budget.py
```

The preparer prints LAB and builds only. It retains failed preflight source
copies/logs and supports a pre-graphics preparation continuation in that LAB;
Meson build continuation should use the existing build directories. The
new `scenefx-cache-trace.patch` and `sway-source-trace.patch` are passive
standalone deltas after the historical clip/timing/guard/presentation chain.
`instrument.py` deterministically generates them from those sources;
no preserved historical patch is rewritten. XML provenance is in
`protocol-provenance.json`: layer-shell is pinned to wlr-protocols
`b010a03648b88d143236de193bddbfea0c08bc84`; the retained XDG XML came from
wayland-protocols 1.49 and has a fixed checked digest. Generated files remain
in LAB. The current and original C clients compile separately with C17 and
fatal warnings.

The already-consumed graphic invocations were `run.py LAB C0`, `C1`, `C2`.
**Do not execute them again for this ticket.** The ledger at
`~/swayfx-mosaic-optimized-blur-v1-budget.json` is shared across clones and
LABs, locks atomically and refuses a second mode run or another LAB.
It has no reset/refund operation. C0's second unreserved initial image is
charged and documented as a reservation-protocol deviation; numerical
limits were not exceeded. A new authorized ticket must define its own
protocol/budget before new graphics, rather than reset this one.

Offline analysis remains repeatable:

```sh
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-optimized-blur-cache/edge-model.py "$LAB"
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-optimized-blur-cache/analyze.py "$LAB"
```

These analyzers write derived results and manifests. Never target the closed
historical LAB: use a separate offline copy/output tree. The freeze audit
preserved the exact pre-freeze fixture in the external snapshot named in the
report; its README is the byte-identical source-manifest input. Raw logs/PNGs and per-run executed sources stay
immutable. The offline model is a hypothesis about reduced-domain sampling,
not native GPU readback or a shader fix. The complete source/evidence
manifest digests and validation are recorded in the report after the final
analysis. Full H1 differences are retained alongside the predefined ROIs;
no boundary anomaly is excluded to obtain a PASS. No PNG/native-buffer
identity, all-frame damage, GPU reference release or instrumentation
neutrality is claimed. Runtime directories are removed and all owned
processes reaped. No production patch, package or desktop change follows.
