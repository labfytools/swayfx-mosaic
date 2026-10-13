# Static nested valid-grab fixture

EXPERIMENTAL / FROZEN FAILURE EVIDENCE. No production integration.
Read the [protocol](../../../docs/design/STEP20C_STATIC_NESTED_VALID_GRAB_PROBE.md).
One exclusive laboratory, one existing immutable static binary, client-only
C17 builds; no SceneFX/Mosaic build or pristine run. Original nested source is
retained separately; `placement.patch` adds only legal static_cross anchors.

`prepare.py` verifies identity/provenance and compiles clients outside Git.
`check.py` exercises actual historical observations and labelled synthetic
negative fixtures, ledger concurrency/exhaustion/corruption, lifecycle and exit
classification before run reservation. `run.py` shares those predicates,
consumes reservations before every action, and preserves real terminal codes.
`collect.py` records only measured states and seals inventories once.

```sh
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-nested-grab/prepare.py
# Use only the LAB printed and registered by prepare; no second LAB or reset.
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-static-nested-grab/check.py "$LAB"
# Only after STATIC_NESTED_GRAB_FIXTURE_PREFLIGHT=PASS:
PYTHONDONTWRITEBYTECODE=1 python "$LAB/fixture/run.py" "$LAB"
PYTHONDONTWRITEBYTECODE=1 python "$LAB/fixture/collect.py" "$LAB"
```

Budgets: 1 run, 2 chains, 4 grabs, 2 calculated camera corrections (one per
chain), 1 splith transition, 9 complete clicks, 16 PNGs, 24 positions, 150 s.
Failed actions consume budget. Private sockets/groups only, no desktop IPC.
Generated protocol/client binaries/logs/JSON/PNG/build files stay outside Git.
Fixture preflight success is not graphical evidence. Results appended after
collection; every unexecuted matrix cell remains NOT TESTED.


## Completed campaign: INCONCLUSIVE, do not rerun

LAB `/home/fy59/swayfx-mosaic-static-nested-grab-m0a5e2qh`; run exhausted1/1.
Only E1 toplevel mapped: two stable full #303038 H2 images, computed camera
480→160 by -320, measured applied tiled clip, H1 blue182214 pixels. No popup,
click or grab occurred. Runner exits1 on its painted-height320 assertion;
actual height573. A further IPC window_rect.y=0/titlebar y25 assertion was
invalid but unreached. The original run.py here and LAB/fixture remain exact
failed evidence, **not a qualified replay runner**. Before any fresh separately
authorized campaign, repair/replay all geometric assertions offline. No runtime
retry is permitted by this ticket; unused chain/click/capture capacity is not
a new run authorization. The recipes above describe the preparation/run that
was attempted, not permission to repeat it.

`check.py` now counts ValueError from a deliberately removed-button negative
as rejection; the initial immutable checker is retained in LAB/fixture and the
corrected preflight checker in LAB/preflight-correction. Recorded preflight PASS
covers its tests, but the full geometric source/assertion audit was insufficient.
No historical gate/runtime status or manifest is rewritten. `geometry_audit.py`
rechecks actual SHM/configure/ACK/map, scene/IPC/paint, reference RGB, zero
popup/button/grab and terminal codes without launching a graphical process.
Post-run collector/diagnostic copies are in LAB/postrun-fixture, separate from
the executed fixture. Source/evidence inventories include these distinctions.

Terminal swaymsg actual1 (response receive failure), compositor0, all four
clients/injector0, no rescue or residual process/socket. Earlier measurement
failure is preserved; shutdown success cannot qualify scientific success.
Budget: run1, chain1, grab0, camera1, transition0, click0, move1, PNG3,
5.485246415 seconds. New Mosaic/SceneFX builds0, pristine runs0.
Source30 entries SHA256
`9b76aae162faa631bf1930677d484359dfc3e29ace237b9aee2daa3d5cd68dc4`;
evidence96 entries SHA256
`5750d1e74636c2d276800f795ed0214c3e12999908149855af0b382a2da9bfb4`.
Both are sealed once and verified. Root/nested input, crossings, dismissal,
standard-return/input/residues and related damage remain NOT TESTED.

Read-only completed-lab checks (never rerun collect or regenerate manifests):

```sh
PYTHONDONTWRITEBYTECODE=1 python "$LAB/postrun-fixture/geometry_audit.py" "$LAB"
PYTHONDONTWRITEBYTECODE=1 python - "$LAB" <<'PYCODE'
import sys
from pathlib import Path
lab = Path(sys.argv[1])
sys.path.insert(0, str(lab / 'postrun-fixture'))
from support import verify
for name in ['fixture-freeze', 'source', 'evidence']:
    print(name, verify(lab / 'results' / (name + '-sha256.txt')))
PYCODE
```

Verdict SWAYFX_MOSAIC_STATIC_NESTED_VALID_GRAB_PROBE=INCONCLUSIVE.
Architecture UNDECIDED. STEP20C NEXT; multi-output NOT YET SUPPORTED.
This historical failure fixture is frozen for publication. The separate new
offline geometry-review fixture remains local, uncommitted and unpublished.
