# STEP20C pending-input event-loop fixture — EXPERIMENTAL

See the [protocol](../../../docs/design/STEP20C_EVENT_LOOP_PENDING_INPUT_PROBE.md).
This fixture rebuilds the pinned private compositor and the same T4 client
in a disposable laboratory. `client-flush.patch` adds a client-side
`wl_display_flush` result and monotonic timestamp after each normal
input-region commit. It changes no server handler or scheduler. The existing
private commit, present, surface, hit and delivery traces remain in use.

```sh
prep=$(sh tooling/probes/step20c-event-loop-pending-input/prepare.sh)
LAB=$(printf '%s\n' "$prep" | sed -n 's/^LAB=//p')
for mode in control private_standard private_mosaic; do
  PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-event-loop-pending-input/run.py \
    "$LAB" "$mode" --cycles 5
done
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-event-loop-pending-input/analyze.py "$LAB"
```

The default runner submits an ordinary IPC rendering/camera request and a
normal client region request before waiting for both results. `--sequential`
keeps the earlier wait-after-each-operation control. `--surface-trace 0`
disables only the additional private surface log site for a limited timing
comparison. The control SwayFX is not instrumented. Up to five cycles per
mode are allowed. The runner logs submission and completion separately;
the client logs its flush result, and server traces determine application.

The lab contains runtime-private sockets, process-owned logs, captures,
generated runner, builds and binaries; none belongs in Git. A manifest
should hash all regular files under the run and structured result directories,
excluding the manifest itself. Never target the daily Sway IPC socket. Stop
after five unsuccessful interleaving attempts; report
`INCONCLUSIVE / NOT EXERCISED` and leave the popup variant untested.

The frozen five-cycle campaign is described in the protocol. A later
independent clone replay used one sequential and one asynchronous private
Mosaic cycle only. It confirmed two applied mutations per run, native
commit/present traces and restored client delivery without reopening the
timing search; its 56-file raw manifest hash is
`f8b54f2ef7f9caca3837e956341ddb5a62f261d0115840d6fd8b0b3540c1e8b9`.
