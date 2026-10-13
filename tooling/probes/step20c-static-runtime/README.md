# Private static Mosaic runtime fixture

**EXPERIMENTAL / LOCAL / UNCOMMITTED; no production integration.**
Read the [protocol and decisions](../../../docs/design/STEP20C_STATIC_RUNTIME_AND_PACKAGE_CONTRACT.md).
Current package, production patch and installed desktop remain unchanged.

## Reproduction and one-laboratory ownership

The completed laboratory is `/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt`.
Its run reservation is consumed. **Never rerun prepare/audit/run in that LAB,
reset its budget, create a replacement LAB or execute the old campaigns.**
Future independent reproduction requires a new scoped authorization/budget.
Generated sources, build trees, binaries, PNGs, sockets and logs stay outside Git.

Dependencies: Git, Meson/Ninja, cc C17, pkg-config, readelf/nm/objdump/ldd,
wayland-scanner, swaymsg, grim, Python/Pillow, installed pinned build libraries.
No installation or downloads are performed by these scripts. Local SceneFX
object store must contain the pinned commit. Historical wlroots archive and
private source/patch hashes are verified through the preserved manifests
before prepare; archive provenance remains the sealed ABI campaign.

For a separately authorized fresh LAB, the ordered commands are:

```sh
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-runtime/test-budget.py
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-runtime/prepare.py "$TASKLAB" \
  --scenefx-git "$SCENE_STORE" --historical "$VERIFIED_ABI_LAB"
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-runtime/audit.py "$TASKLAB"
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-runtime/stage.py "$TASKLAB"
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-runtime/clients.py "$TASKLAB"
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-runtime/run.py "$TASKLAB"
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-runtime/collect.py "$TASKLAB"
```

Prepare reconstructs only the static chain, applies eight unchanged private
patches and checks source equivalence. Mosaic is genuinely compiled with
`--prefix=/usr --bindir=bin -Dmosaic-package=true`; only SceneFX is archived.
Meson installation is DESTDIR only. Audit inventories exact root license texts
and compiled/generated notice comments; exact unused archive-member extraction
and legal clearance remain separate distribution gates. Stage refuses links,
foreign files and modes; exactly one binary and four inventoried notice files
were retained. `collect.py` recalculates structured observations offline.
`seal.py` creates exclusive manifests once or verifies them read-only.

The budget uses a stable exclusive flock, atomic ledger replacement and fsync.
Build/stage/notice/audit/run/capture/camera failures retain their reservations.
No refund/reset exists. Offline tests exercise concurrent/exhausted reservations.
Each runtime is mode 0700, with explicit private Wayland and swaymsg sockets,
owned process groups, a 150-second watchdog and 64 MiB per-log stop bound.
The compositor executes only the staged binary. /proc executable/maps identity
is checked before any clients. No live desktop socket is used.

## Completed evidence and limitations

Build, model, real `/usr` prefix, stage, ELF, library identity, headless outputs,
IPC and ordinary client mapping passed. Runtime measured the same 31 wlroots
scene bindings into the executable and three retained wlroots helpers. The
actual renderer was SceneFX FX / OpenGL ES 3.2, AMD Radeon 780M / Mesa 26.2.4;
`WLR_RENDERER=pixman` did not select pixman in this FX path.

One correction of +160 produced an applied target scene x=-320, width=640;
its measured H1 colored region retained 182,214 pixels, and H2 contained zero
target-color pixels. The full H2 comparison failed: 23,807 decoration pixels
changed after the reference lost focus. The IPC-derived content crop remained
exact. This supports a fixture focus-state mismatch, without replacing the
failed whole-output gate with a PASS. The run stopped before scored input and
splith return; both and root/nested popups are NOT TESTED. No algorithm changed,
no second run, no pristine run, three PNGs, one camera correction, ~4 seconds.
All owned processes were reaped and the private runtime was removed.

Overall PARTIALLY_FEASIBLE; runtime comparison scenario INCONCLUSIVE;
architectural conclusion UNDECIDED. The run itself does not demonstrate an
ABI crash or forbidden target hit. Complete license closure, named release/
security owners, broader graphical/ABI qualification and bit reproducibility
remain open. Current package unchanged, STEP20C NEXT, production multi-output
NOT YET SUPPORTED. See the retained fixture-corrections record for failed
offline checks and corrected, unexecuted diagnostic behavior. A future ticket
should first fix reference focus preflight, then explicitly authorize the
minimal input and standard-return qualification.
