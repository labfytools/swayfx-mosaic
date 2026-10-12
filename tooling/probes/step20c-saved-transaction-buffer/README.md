# Saved transaction buffer source fixture

**EXPERIMENTAL / INCONCLUSIVE.** The protocol and source audit are in
[the report](../../../docs/design/STEP20C_SAVED_TRANSACTION_BUFFER_PROBE.md).
This directory preserves only reviewed source. It does not add a production
dependency or authorize a SceneFX merge. Generated builds, sockets, captures,
large logs and results belong under a private LAB outside Git.

`prepare.sh` reconstructs pinned disposable sources and compiles the C17
controlled XDG client. `run.py LAB MODE` reserves a locked persistent budget
before a headless run; modes are `control`, `private_standard` and
`private_mosaic`, once each. `analyze.py LAB` derives a bounded matrix from
the raw event/PNG files and writes manifests. `test-budget.py` exercises
the ledger without launching a compositor. No command may use the daily IPC
socket; runner IPC always passes `swaymsg -s` with the private socket.

For the completed campaign, use each run's manifest-covered
`runs/*/fixture-source.py` to reconstruct the exact executed code. The current
`run.py` matches the final private Mosaic copy (SHA-256 `cdece69cf956e550779bd992b0d38234629ca1e611dfb3fb0348c04841c47f59`).
The pristine copy (`bc041eb7be89da9e198bb9ca2e25cfe86467c264e3687e6d9d3f3836e82ce40c`)
had no pointer injector. The private-standard copy
(`67aa3fb94901739bea0b1d0e0cf881081d2388a02256dddc45282d7a4bc86b25`)
added six retained-window pointer actions; they delayed its valid ACK past
timeout. The final copy removed those actions. Do not rerun this exhausted
campaign or treat the current source as identical to all historical runs.

The default transaction timeout is 200 ms; the fixture requests
`-Dtxn-timeout=1200` for each comparable mode. A source trace, configure
hold and a screenshot alone do not establish saved-buffer rendering: the
saved node must be nonempty, enabled, in the render list, and geometrically
cross the tested boundary. Missing observations are NOT EXERCISED or
INCONCLUSIVE. Historical ledgers are separate and never reset. The completed
LAB is `/tmp/swayfx-mosaic-nested-grab-KYJ2pj1o`; its ledger has one run
per mode. **Do not rerun a mode or reset this ledger.** The private-standard
ACK episode timed out during slow fixture input, and the Mosaic target camera
settled at 1760, leaving its snapshot outside H1. The partial-overflow gate
is NOT EXERCISED; see the report for exact limits.
