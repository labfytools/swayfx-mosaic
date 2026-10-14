# STEP20C targeted fixtures

EXPERIMENTAL / PLANNED. These source fixtures repair bounded measurement
procedures identified in the overnight evidence. STEP20C remains NEXT;
production multi-output remains NOT YET SUPPORTED. No production integration,
UX policy, package dependency, compositor build, installation or live socket
operation is part of this fixture.

The new private laboratory is
`/home/fy59/swayfx-mosaic-targeted-7gge6h8b` (owned mode 0700). The historical
`/home/fy59/swayfx-mosaic-overnight-mcolx0gq` is read only: its 18 runs are
exhausted. Historical verdicts remain unchanged. Public Python tests accept
`--historical` so paths can be supplied explicitly.

`plans.py` declares 13 accessible attempts: scale A/G, held saved A/G, effects
pristine/A/G, refreshed input pristine/A/G and G dynamic/hidden/R90. The
independent ledger permits at most 14 attempts, at most 16 compositor PNGs
per attempt, campaign PNG caps scale24/saved30/FX48/input36/G36, and total174.
Current planned allocation is164. The unused saved diagnostic is disabled;
it requires a separate parent decision, exact diagnostic identity and distinct
review/freeze. No diagnostic attempt is consumed by preparation.

Every launch/action reserves first in the same locked persistent ledger.
It uses `flock`, atomic replacement, file and directory `fsync`; a consumed
run token persists on failure. There is no reset, refund or retry operation.
Local click/motion/grab/chain/camera/mutation/configuration/spawn/capture limits
are reconciled from every reservation. The watchdog stops active measurement
at143 seconds and limits the total run logs to32MiB. Cleanup retains terminal
IPC response, normal process codes, rescue status and150-second bound.

`engine.Session(spec, auth, lab)` exposes `owner`, `find`, `cmd`, `client_cmd`,
`capture`, `pair_capture`, `click`, `close_client`, `debit`, `spawn`, `log`,
`launch_client`, `wait`, `save`, `calibrate` and `inject`. Clients are under
`LAB/clients`; raw run evidence is `LAB/runs/<id>/run`. All compositor/control
IPC explicitly names its private socket; inherited display/library selections
are removed.

Scale/R90 uses five marker pixels and the reviewed pre-owner layer-host
baseline before identifying one new XDG root. The same shared root validator
replays actual D2 and rejects host substitution, multiple candidates, missing
host, incorrect ancestry and incoherent callback order. Replay qualifies
association only; it does not invent missing historical input/final evidence.

Held saved uses source-audited `gaps inner current set 30` and startup
`-Dtxn-timeout=2500`. It requires mapped real SHM, a previous actual ACK,
a new received configure held without ACK, and a natural waiting transaction
timeout with the client alive. Actual argv plus source and elapsed timeout
corroborate2500ms; no native configured-value log exists. A/G expose no saved
node/render identity. SHM and pixels cannot fill that gap, so saved clipping
remains INCONCLUSIVE / SOURCE ONLY.

Input recomputes painted global coordinates after region restore, focus,
camera and layout mutations. It requires fresh local pointer coordinates,
actual client wire/button serial and target. The empty region intentionally
uses the previous global point to compare no owner delivery. Historical F
analysis processes ALL exact output/commit_seq pairs and reports missing
presents. No atomic generation, presented buffer identity or GPU lifetime is
inferred. Dynamic G samples fresh popup input after each resize/migration;
legitimate popup_done is retained and fresh toplevel input is sampled without
recreating a popup chain. Hidden G retains the same chain on return.

Preparation and validation are offline:

```sh
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-targeted/prepare.py --lab LAB
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-targeted/test_targeted.py --historical HIST --output LAB/offline.json
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-targeted/replay.py --historical HIST --output LAB/replay.json
```

Preparation verifies retained binary/client/protocol hashes and privately
compiles only the new FX client. Generated protocol headers/C, binaries, SHM,
logs, captures and runtime directories remain outside Git. `identity.json`
records copied client source SHA and provenance closure. `gate.seal(LAB)`
requires14 passing core tests and5 passing FX tests, executed commands, raw output and exact source bindings, plus typed actual D2/F/E2 replay receipts and binds all fixture/import/client/tool/
binary/library/source evidence. A separate independent reviewer must write
`LAB/review.json` with scope `STEP20C_TARGETED_FINAL_BYTES_V1`, exact freeze SHA
and file bindings, accepted read-only independent review, empty blockers and
bound report bytes. The author does not create that acceptance.

Only after independent acceptance and explicit runtime authorization:

```sh
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-targeted/run.py --lab LAB scale-A
```

Each invocation is one unique attempt. A missing or changed acceptance fails
before a run token, process or runtime exists. This fixture does not launch an
entire campaign automatically. Unexercised matrix cells remain NOT TESTED.
