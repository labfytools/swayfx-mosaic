# Saved target crossing source fixture

**EXPERIMENTAL / PARTIALLY_FEASIBLE.** See the [report](../../../docs/design/STEP20C_SAVED_BUFFER_TARGET_CROSSING_PROBE.md).
This new campaign has its own locked budget and one disposable `/tmp` LAB.
The prior saved-buffer ledger and captures are read-only historical evidence.
Production source, cumulative patch, package and installed libraries are not
changed. No commit or push is authorized for this fixture.

`prepare.sh` reconstructs the pinned private builds using the preserved
upstream clipping and trace patches, then applies any separately hashed
passive target-geometry instrumentation. It never starts a compositor.
`run.py LAB MODE` uses only private sockets and must pass the source-buffer
geometry preflight before reserving a transaction episode. A failed preflight
ends the run without an exploratory camera retry. The exact runner used is
copied into each run directory. All generated data remain under LAB, outside
Git. Run the offline ledger test before a graphical run.

Completed LAB: `/tmp/swayfx-mosaic-nested-grab-eVtLtpYd`. It used one
calculated Mosaic camera delta, three runs, six episode reservations and 26
captures. The exact executed `fixture-source.py` in each run preserves the
runner before the post-run E2 pointer-correlation fix. Do not replay this
exhausted campaign. The geometry trace patch has SHA-256
`7bbb27bc8617645e1acfd0589a410d470426363bd8a108bd43fc1006747f012e`;
the prior trace patches are referenced by the source manifest. `analyze.py`
regenerates the offline JSON summaries and both manifests without launching
another compositor. Target E1 crossing/render and H1 pixels are measured;
Mosaic E2 timeout cleanup and input remain untested.
