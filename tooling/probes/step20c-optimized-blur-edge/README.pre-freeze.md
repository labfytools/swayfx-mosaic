# Optimized blur edge causality fixture

**EXPERIMENTAL / LOCAL / UNCOMMITTED.** Read the
[pre-registered protocol](../../../docs/design/STEP20C_OPTIMIZED_BLUR_EDGE_CAUSALITY_PROBE.md).
The historical V1 cache campaign is closed; never launch or analyze into it.
This fixture is a new four-slot comparative campaign, not a renderer fix.

From a full project clone containing the pinned project commits, with Meson,
Ninja, C17, Wayland scanner, compatible wlroots 0.20 build dependencies,
Python numpy/Pillow, grim and swaymsg, use:

```sh
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-optimized-blur-edge/test-budget.py
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-optimized-blur-edge/prepare.py
```

Preparation builds only, creates a new LAB outside Git and retrieves pinned
SceneFX. It reads the published V1 XML/patches and older preserved patch chain
without modifying them. Compiler logs and all generated files stay in LAB.
Offline callback, source, AST, ledger, patch, build and linker preflight must
pass before any run. The client ACKs background configures without drawing;
only explicit A/B/A commands can submit its three 800×600 images.

Execute `run.py LAB R0`, then R1, R2 and R3 exactly once each, with
PYTHONDONTWRITEBYTECODE=1. The persistent locked
`~/swayfx-mosaic-optimized-edge-v1-budget.json` binds all four slots to one LAB.
Failed launch/action reservations count; no refund, reset or alternate LAB.
Each run has 3 images, 1 scoped blur cycle, 12 PNG maximum and a 150 s watchdog.
All sockets/IPC are explicitly private; cleanup targets recorded children only.
R2/R3 share binary/client/library/config; OPT_TRACE absent versus 1 toggles new
cache traces. Old private traces remain enabled in both. No GPU readback,
forced clearing, shader, algorithm, production, package or desktop changes.

Keep exact executed sources, configurations, binary/library identities,
client events, logs, PNGs, exit codes and manifests outside Git. Analyze all
RGB pixels without excluding edge bands. Model/source sampling possibilities
are not native causality. Results and final offline validation are recorded
in the protocol after the four attempts. No commit or push for this fixture.

## Closed V1 campaign

LAB `/home/fy59/swayfx-mosaic-optimized-edge-a55yjb8n` consumed all four runs,
12 images,48 captures,4 cycles and two initial Mosaic corrections; no rerun
is allowed. All controls completed. R0/R1 full RGB and R2/R3 full RGB match
in six states, while the edge anomaly persists in pristine and without OPT.
Result PARTIALLY_FEASIBLE, architecture UNDECIDED; native FBO cause unresolved.
The next justified distinct gate is ABI/package audit with this limitation.
A proposed selective GPU observation is documented but not executed.

Offline analysis in this new LAB is `analyze.py LAB` then `model.py LAB`.
`model.py` reuses exact V1 functions through AST selection without running the
historical writer. Native rebuild schedule exists only for R3. `preflight.py`
affects offline files only and must precede all graphical runs; no re-execution
of the exhausted run slots is authorized. Source/evidence manifest creation
is separate from analysis to preserve final inventories. Generated outputs
remain outside Git. All runtime/socket directories were removed and owned
children reaped; compositor exit=0, clients retain controlled-shutdown EPIPE.

`seal.py LAB` creates each final manifest once and refuses replacement; verify
its entries rather than regenerating after sealing. Optional `plot.py LAB`
requires matplotlib and produces a standalone SVG from complete column/row
arrays; it is an offline figure, not another captured PNG. Its cache stays
in LAB. Run all derived analysis before sealing.
