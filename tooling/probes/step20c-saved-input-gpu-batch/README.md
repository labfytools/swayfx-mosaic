# STEP20C saved/input/GPU batch fixture

EXPERIMENTAL — source-only derived Python fixture for
`SWAYFX_MOSAIC_STEP20C_SAVED_LIFETIME_INPUT_EPOCH_AND_GPU_CAUSALITY_BATCH_V1`.
The historical imported fixtures are immutable. Source status/comments describe
the pre-run sealed snapshot; actual results belong to [results.json](results.json)
and the [gate dossier V2](../../../docs/design/STEP20C_GATE_CLOSURE_DECISION_V2.md).
No fixture wording grants another graphics run or production integration.

LAB is `/home/fy59/swayfx-mosaic-saved-input-gpu-pz4z428f`;
OLD_LAB is `/home/fy59/swayfx-mosaic-targeted-7gge6h8b` and HIST is
`/home/fy59/swayfx-mosaic-overnight-mcolx0gq`. Hardcoded private paths and imported
historical engine/client inputs are deliberate provenance constraints, not a
portable self-contained build kit. Paths must exist and retain exact recorded
bytes. Missing inputs are a setup limit, never grounds to fabricate evidence.

Six one-shot run tokens were consumed (saved C3/A/G, input A/G, diagnostic GPU),
59 output captures and240 actions. Optional native/pristine runs were unused;
no additional run/retry/build is authorized by this README. Never reset/refund
ledger or reuse the historical14-run budget. Python uses durable locked atomic
ledger reservations before actions. The GPU C patch/client/core remain private;
only common Python source/validators/tests and small provenance/results/scientific
JSON receipts are preserved here. No binary, PNG, raw readback, logs, caches,
source archive or production dependency is included.

Offline replay only, from repository root with Python/Pillow and exact retained
private inputs:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tooling/probes/step20c-saved-input-gpu-batch -p 'test_*.py' -v
```

Recorded result42 tests PASS. The separate private GPU suite is six tests PASS;
its imports/data are not distributed here. These tests replay actual wire/log/
PNG inputs and reject hostile evidence mutations; they launch no compositor.
Runtime invocations of saved.py/input.py or ledger initialization are not an
offline reproduction procedure and require separate authorization.

[provenance.json](provenance.json) binds source hashes, binary identities and
private evidence paths. [gpu-native-summary.json](gpu-native-summary.json) is
an exact copy of the scientific XHIGH summary, local FBO history supported,
whole-field causal verdict INCONCLUSIVE. Saved measurements_pass=PASS; input/GPU measurements_pass=PARTIALLY_FEASIBLE,
all raw global runtimes retain terminal IPC1/INCONCLUSIVE. Saved/input scientific
cleanup remains INCONCLUSIVE on helper error32; GPU scientific cleanup PASS.
No atomic generation, exact presented-output identity or GPU completion is
proven. Final independent dossier review ACCEPTED / audit PASS; publication PREPARED at
this edition, with actual refs in the private post-push receipt. STEP20C NEXT; production multi-output NOT YET SUPPORTED.
