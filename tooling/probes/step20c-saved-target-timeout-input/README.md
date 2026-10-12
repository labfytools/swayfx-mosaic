# Saved target natural timeout and input fixture

**EXPERIMENTAL / PARTIALLY_FEASIBLE.** The [protocol and result](../../../docs/design/STEP20C_SAVED_TARGET_TIMEOUT_INPUT_PROBE.md)
defines a single new Mosaic run with one natural timeout episode. The
previous crossing campaign and its exhausted ledger are immutable historical
evidence. This fixture reconstructs the pinned compositor privately, uses a
fixed opaque XDG SHM H2 reference, and stores all generated data under one
new `/tmp` LAB. No production source, package or installed library is changed.

Run `prepare.sh` to reconstruct the private binaries without launching a
compositor. Run the offline `test-budget.py` before the sole `run.py LAB`
invocation. The runner requires two identical H2 captures before any
transaction reservation, calculates no more than one relative camera delta,
and copies its exact source into the run directory. `analyze.py LAB` derives
structured results and SHA-256 manifests from retained raw files. Never
reuse an old LAB or reset a consumed ledger.

The sole run used `/tmp/swayfx-mosaic-nested-grab-iKwhINe5`. Its ledger
records one run, one episode, one camera adjustment and eight captures.
The exact executed Python source is saved as `runs/*/fixture-source.py`.
The static reference and the target retained their real configure/ACK
processing; the target held serial 50 until natural SwayFX timeout. Its
crossing saved node rendered on H1, the whole H2 RGB image remained
identical before/during/after, and the target tree was destroyed. One H2
pointer sample reached the static reference; the visible H1 sample hit the
saved scene buffer without a Wayland surface. Full damage and native GPU
lifetime remain unqualified. `analyze.py` is offline only and may be rerun
without spending a graphics budget; run it with `PYTHONDONTWRITEBYTECODE=1`.
