# STEP20C commit/present/input ordering — EXPERIMENTAL

The [protocol](../../../docs/design/STEP20C_COMMIT_PRESENT_INPUT_ORDERING_PROBE.md)
was written before this fixture. Everything here is a source fixture for a
disposable private laboratory; no code enters the production compositor,
SceneFX ABI, package, cumulative Mosaic patch or daily session.

## Replay

```sh
prep=$(sh tooling/probes/step20c-commit-present-input/prepare.sh)
LAB=$(printf '%s\n' "$prep" | sed -n 's/^LAB=//p')
for mode in control private_standard private_mosaic; do
  PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-commit-present-input/run.py \
    "$LAB" "$mode" --cycles 5
done
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-commit-present-input/analyze.py "$LAB"
```

The prepare chain rebuilds the pinned private SceneFX/Mosaic fixtures and
fetches wlroots 0.20.2 at commit
`d783533489e1f75d6886c2ab5c5960090ef268f8` inside the new lab.
Its two audited scene files are hash-checked by the Mutation Coverage
preparator. `surface-ordering.patch` adds a passive top-level surface commit
trace after wlroots applies the client input region. Existing private traces
provide build, commit, present, hit and seat notification. The client uses
ordinary `wl_surface.set_input_region` and `wl_surface.commit` requests.

The runner reuses the frozen headless runtime, explicit IPC socket, process
group cleanup and geometry checks. It defaults to five bounded cycles and
`ASI_MODE=0` (trace-only). Standard controls are unmodified SwayFX `splith`
and private SwayFX `splith`. Native output events are uninstrumented in the
unmodified control. Camera requests in the private Mosaic case supply
ordinary scene damage; no backend scheduling is changed. A missing natural
commit/mutation/present interleaving must be reported **INCONCLUSIVE**.

The runner is sequential: `command()` waits for IPC response,
`client_command()` waits for a client log confirmation, and `inject()` waits
for pointer confirmation. A Mosaic camera reply precedes submission of the
next input-region request. Those process round trips can exceed the native
commit-to-present interval. The executed callbacks and delivery remain valid;
the timing question requires a separately recorded nonblocking experiment.

For a complete evidence manifest outside Git, hash every regular file under
the three `runs/` directories plus the ten structured results, excluding
the two older source/artifact manifests and the new manifest itself. The
historical frozen lab's `raw-evidence-sha256.txt` contains 94 entries and
hashes to `9b74584936d44be5accb1f3882482fbd1eb85bc5c696b4551d45076b76ff4f8d`.
The independent replay manifest has the same scope and hashes to
`7d4e5c3860cc5ea3b63668441efa58bf31ef3197c6d22890cbaccee70543d41a`.

Set `CPI_SURFACE_TRACE=0` before `run.py` for a paired workload with only the
additional `ORDER_SURFACE_COMMIT` log site disabled. Keep these paired runs
in a separate lab from the three analysis runs; `analyze.py` deliberately
rejects ambiguous duplicate mode runs. The old private build, hit and
commit/present traces still execute in this comparison.

Raw logs, screenshots, generated runner, binaries, build trees, sockets and
structured JSON analysis remain in `LAB`, outside Git. Stop or terminate the
runner normally to remove its private runtime. A killed runner may leave its
lab and sockets for manual, targeted cleanup; never touch the live Sway
socket. The real rejected-commit backend path remains **NOT TESTED**.
