# Minimal private core gate — preserved experimental fixtures

This is the source archive of the consumed
`SWAYFX_MOSAIC_STEP20C_MINIMAL_CORE_BUILD_RUNTIME_AND_GPU_FIELD_GATE_V1`
campaign, not a production dependency or a new execution authorization.
Scientific result: **PARTIALLY_ADVANCED**. Recommendation:
**PRIVATE_CORE_NEEDS_TARGETED_EVIDENCE**. STEP20C remains NEXT;
production multi-output remains NOT YET SUPPORTED.

The private laboratory is `/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_`.
The ledger has 12 distinct consumed runs out of 14, 88 output-capture debits
out of 180, one initial core build per component, one diagnostic GPU build
pair and one DESTDIR stage. Failed attempts remain consumed. The two optional
slots are not retry slots. No existing run, build, stage or test is to be
repeated under this archive. No production installation was performed.

## Contents and provenance

`provenance.json` binds every copied file byte-for-byte to the private LAB and
references the larger immutable manifests and receipts by SHA-256. Generated
extracted `.inc` bodies, functional private core patches, fork sources, clients'
binaries, build trees, PNG captures, raw GPU readbacks and large logs remain
outside Git. This is deliberately not a self-contained compositor source kit.

- `c-tests-fixed/`: C17 geometry tests and exact-byte extraction/command
  scripts. The private finite-scroll correction passed 184 assertions in
  normal, UBSan and ASan+UBSan variants; the original six UB reproductions
  remain in the LAB. Extraction requires `mosaic-fixed/` and `scene-core/`
  under the private LAB and generates the excluded core bodies. The reduced
  adapters do not reproduce full compositor ownership or ABI.
- `c-tests-lifecycle/`: real core slice extraction and reduced adapters using
  native Wayland listeners and Pixman regions. Ordinary variants passed;
  targeted sidecar allocation failure terminated each variant with raw
  `-6 / SIGABRT`. **OOM_ABORT_EXPERIMENTAL**, availability risk P1, is not an
  accepted production contract. Its README describes the exact coverage and
  the preserved first fixture failure.
- `graphics/`: the final R2 Python fixture sources, sealed configurations,
  C17 client/protocol sources, input trace fixture and bounded repair tests.
  `run.py`, `gate.py`, `prepare.py` and `seal.py` retain historical laboratory
  assumptions; moving them does not establish a valid source freeze, binary
  identity, accepted independent review or durable ticket ledger.
- `gpu-field/`: frozen readback validator, analysis and offline test source.
  `test_native_hash.py` requires the excluded diagnostic header under
  `scene/render/fx_renderer/gpu_field_private.h`; its earlier ten CPU hash
  cases passed, but no new execution is claimed by preservation.
- `evidence/`: final consumed budget, independent E/F review transcription,
  GPU rejection/layout audit, local ABI provider summary and the separate
  correction of an aggregate R2 exit-count error. Transcriptions are labelled
  as such; original runtime receipts are unchanged.

The exact core binary is
`29baf31aa3eeed259825c87d0799fa5d3dc83710afb967154604eb1c6657f965`
(Build ID `1b42e557e38db3440ae8dcf7ac967e4132223365`). The GPU diagnostic is
`1905a20fa72ebcc7ec47d1584a4653654280288096a20005199eb75673ac0383`
(Build ID `1505e31c3dc08d2a7799c2ee9e1b2705eb61f5fe`). Their runtime data
are distinct. Both used the measured wlroots library
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.

## Recorded execution and limits

The historical C commands were `python run.py` from the corresponding private
C test folder; each command, stdout/stderr and raw return code is retained
there. Graphical runs were reserved through `python -B graphics/run.py <ID>`
and the sole G1 through `python -B gpu-field/runner.py`, with private runtime
directories, sockets, reviewed byte freezes and local/global debits. These
commands describe consumed evidence; they are not instructions to launch again.
Any future reproduction requires a separately authorized scope and budget,
exact parent replay, new private source/binary identities and independent gates.
Never point these scripts at a daily desktop socket or reuse a consumed token.

E0 controls and the vertical cell stopped before captures on a fixture error.
E1's first chain, fractional/R90 and resize/migration provide sampled evidence;
standard return and fullscreen policy are not qualified by comparable controls.
E5's chain was dismissed by outside input before camera return. E6 observed a
natural timeout before late ACK, but its frozen validator still failed.
E7 classic blur was exercised; shadows were not. Whole-H1 A/A-return retained
33,789 different pixels without mask or tolerance. Exact sampled H2 does not
prove complete damage, native saved identity, GPU lifetime or atomic generation.

G1 stopped after nine first-A sample records and 8,312,048 raw bytes because
the frozen validator rejected the auxiliary DMA-BUF plane stride. No accepted
epoch receipt, B/A-return epochs or causal analysis exist. Read success remains
NOT PROVEN, the GL error queue UNOBSERVED and whole-field causality INCONCLUSIVE.
The modifier audit explains the invalid per-plane stride assumption without
changing the validator, accepting rejected bytes or refunding the run.

Runner exits, terminal IPC exit 1, compositor/client exits and normal client
closure are separate evidence. A runner's `scientific_cleanup=PASS` here is its
process-recovery gate; E1/E6 normal close was not acquired and E2 helpers show
error 32 despite nested owners closing normally. G1 scientific cleanup remains
INCONCLUSIVE. Mechanical process recovery alone is not a GPU lifetime proof.

Read the [build/C report](../../../docs/design/STEP20C_MINIMAL_CORE_BUILD_AND_C_FAILURE_PATHS.md),
[graphics qualification](../../../docs/design/STEP20C_MINIMAL_CORE_GRAPHICS_QUALIFICATION.md),
[lifetime/damage report](../../../docs/design/STEP20C_MINIMAL_CORE_LIFETIME_DAMAGE_AND_TXN.md),
[GPU follow-up](../../../docs/design/STEP20C_GPU_FULL_FIELD_FRESHNESS_FOLLOWUP.md)
and [ABI/integration decision](../../../docs/design/STEP20C_MINIMAL_CORE_ABI_PACKAGE_AND_INTEGRATION_DECISION.md)
for the actual scientific matrix and remaining gates. Publication of this source
archive does not authorize merging the private core, distribution or daily use.
