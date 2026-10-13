# Static SceneFX distribution contract fixture

**EXPERIMENTAL / PRESERVED HISTORICAL EVIDENCE / not production or a package recipe.**
Read the [contract dossier](../../../docs/design/STEP20C_SCENEFX_STATIC_DISTRIBUTION_CONTRACT.md).
All builds, binaries, notices, logs and JSON inventories stay in an external LAB.
No compositor entry point, desktop IPC, installation, package publication,
system library modification or symbol visibility experiment is allowed.

## Protocol before execution

Verify immutable historical manifests, using the exact historical README
snapshot identified by the ABI freeze report. Reuse trusted qualified static
binary after SHA-256 and Meson-option checks. The old build prefix is
`/usr/local`: never change its sealed sources or build metadata. Prepare a
new private Meson installation plan from byte-verified copies of the same
source tree with `--prefix=/usr --bindir=bin` and identical package options.
Reuse the original qualified executable at its expected build-relative path
with identical hash. Run exactly one `meson install --no-rebuild --destdir
LAB/stage-static`. No compilation, linking, stripping or retesting of old
compositor builds is needed. Record the metadata adaptation separately.

If metadata setup fails, retain its failure; do not improvise manual staging
or rerun the historical chain. A future independent reproduction may build
only the static chain from pinned sources and private patches listed in the
[ABI fixture](../step20c-scenefx-abi-package/README.md), with `/usr` prefix
from the beginning. The historical laboratory is not a required future input.

Audit readelf/nm outputs, retained actual loader bindings and source call
sites; never infer provider selection from a matching symbol name.
Notice embedding, if exercised, uses a disposable copy and objcopy only;
byte-for-byte extraction establishes technical feasibility, not legal approval.
Do not stage that altered copy or add a notice policy to production.
Budget: one static DESTDIR stage, zero graphical runs, zero shared builds,
at most one necessary static reconstruction (not required if reuse succeeds).

## Completed local campaign

LAB: `/home/fy59/swayfx-mosaic-static-contract-7_vlvpjw`.
Historical README mapping:
`/home/fy59/swayfx-mosaic-abi-freeze-i6x1osil/historical-fixture-README.md`.
PARTIALLY_FEASIBLE; STATIC_DISTRIBUTION_REQUIRES_CONTRACT_DECISION;
production strategy NONE — USER DECISION REQUIRED. Phase B stays local.

One stage passed with exactly one regular `/usr/bin/swayfx-mosaic`, no symlink,
library or notice. SHA-256
`ccd47ce5b74c132e19bcd46d022a80e90e8a944acc3db521a89427ee7913c614`.
The normal Meson plan uses `/usr`; the reused executable retains its historical
build strings/options. Runtime path/graphics qualification is not claimed.
Initial Python preparation failed on an absent optional `subprojects` directory
before setup/staging. The source-copy assumption was corrected and preparation
resumed; one setup and one install were executed, with zero compositor rebuilds.

```sh
python tooling/probes/step20c-scenefx-static-contract/audit.py LAB \
  --historical HISTORICAL_LAB --historical-readme HISTORICAL_README --stage
```

This historical-reuse mode verifies exact sealed manifest identities and trusted
binaries, records commands/return codes, inventories symbols/provider consumers,
dependencies/source notice candidates, and stages once. `--stage` must never
be run again after `stage-install-started.json` exists. Omitting `--stage`
allows repeated static analysis before sealing only. The sole notice probe
modifies a disposable copy with objcopy, not production or the staged executable.
After sealing, only `--verify` is permitted; it rechecks every new inventory
entry without writing. Historical manifests use their README snapshot mapping.

## Independent reproduction without the old laboratory

Use local Git object stores with the four exact pins in the report. Materialize
new SceneFX and Mosaic sources with `git archive` at their respective commits;
archive pinned wlroots for comparison. Apply the eight private patches in the
report's ordered list with `git apply --check` before each application. Use the
same installed wlroots/header/build identities, compiler/scanner/protocol and
renderer features; otherwise mark the new matrix unqualified, not equivalent.
The report is reproducible from these source inputs, not dependent on retaining
the old executable or `/home/fy59` paths. Future execution needs its own budget
and authorization; these commands were **not run in this ticket**:

```sh
meson setup "$TASKLAB/scene-build" "$TASKLAB/scene-source" \
  -Ddefault_library=static -Dexamples=false -Dwerror=false
meson compile -C "$TASKLAB/scene-build" -j 8
PKG_CONFIG_PATH="$TASKLAB/scene-build/meson-uninstalled" \
  meson setup "$TASKLAB/mosaic-build" "$TASKLAB/mosaic-source" \
  --prefix=/usr --bindir=bin -Dwerror=false -Dsd-bus-provider=libsystemd \
  -Dmosaic-package=true -Dswaybar=false -Dswaynag=false \
  -Dman-pages=disabled -Ddefault-wallpaper=false
PKG_CONFIG_PATH="$TASKLAB/scene-build/meson-uninstalled" \
  meson compile -C "$TASKLAB/mosaic-build" -j 8
meson test -C "$TASKLAB/mosaic-build" mosaic-model --print-errorlogs
meson install -C "$TASKLAB/mosaic-build" --no-rebuild \
  --destdir "$TASKLAB/stage-static"
readelf -hW -dW -Ws -rW -VW "$TASKLAB/mosaic-build/sway/swayfx-mosaic"
nm --format=posix "$TASKLAB/mosaic-build/sway/swayfx-mosaic"
```

On trusted binaries only, retain loader `--list` and relocation/binding
inspection in diagnostic mode (no compositor entry point), as in the preserved
ABI fixture. Inspect complete stage entries with lstat, not just regular-file
counts. Capture actual consumer/provider pairs; preserve package owners and
complete root/generated-protocol notices. The existing historical-reuse audit
intentionally refuses a different sealed identity; a new reproduction needs
its own validated manifests and may use these standard diagnostics directly.
Never execute the historical prepare.py full stock/shared chain just to obtain
static symbol evidence. No bit reproducibility or legal clearance is implied.

## Publication freeze

The historical verdict is unchanged. Subsequent decisions on private static
linking, separate notices, project maintenance and exact-pair qualification
authorize a distinct private runtime gate, not production integration.
Verify the sealed manifests with `verify-freeze.py LAB --snapshot-map MAP`
after publication wording changes. MAP is the external pre-freeze snapshot
mapping recorded in the dossier; it must contain only entries whose exact
original bytes still match the sealed manifest. No manifests are rewritten.
