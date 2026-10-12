# Dynamic output ownership source fixture

**EXPERIMENTAL / preserved source-only fixture.** Read the
[protocol and source audit](../../../docs/design/STEP20C_DYNAMIC_OUTPUT_OWNERSHIP_PROBE.md).
No production support or UX contract follows. Reconstruct in a full clone
containing `8345aff0f97d381b768233021fc5c881ec794094` and copy this local fixture.
Old temporary laboratories are not dependencies. No install or live IPC.

The preparer reuses pinned source-only fractional dependencies, builds private
SceneFX/Mosaic and pristine SwayFX 0.6, then compiles the per-event logical-extent
pointer and opaque SHM client with C17. Passive output traces preserve callback
order and clip/render decisions. All artifacts stay in its printed LAB.

Run each mode once in the same campaign. Never delete/reset the ledger or
create another lab to evade failed-action consumption. The runner reserves
D1/D2/D3/D5 before IPC; camera pairs are zero. Each run owns private runtime,
Wayland/IPC sockets and children, which its finally block removes.

```sh
sh tooling/probes/step20c-dynamic-output/prepare.sh
python tooling/probes/step20c-dynamic-output/test-budget.py
python tooling/probes/step20c-dynamic-output/run.py "$LAB" control
python tooling/probes/step20c-dynamic-output/run.py "$LAB" private_standard
python tooling/probes/step20c-dynamic-output/run.py "$LAB" private_mosaic
python tooling/probes/step20c-dynamic-output/analyze.py "$LAB"
```

Every IPC uses the private socket. Pointer coordinates derive from current
get_outputs logical bounds per event. No physical scaling in injection.
Failures remain scientific exclusions, not automatic clipping defects.

## Observed campaign

The one measured campaign at `/tmp/swayfx-mosaic-nested-grab-0zJrQnLj` applied
D1/D2/D3/D5 in all three modes: logical H1 width 800→960→800, workspace 6 and
tiled 8 preserved, H1→H2→H1 ownership and applied clips reassociated. It retained
230 PNGs. Mosaic completed; both controls completed transitions but failed
final calibration through temporary reference occlusion. Their generated
sources remain in their run directories; the final fixture relocates both
references before testing either. No failed dynamic action was replayed.

Result PARTIALLY_FEASIBLE. Stable vacated outputs are exact background;
Mosaic owner hits and both-output calibration pass at all scored stages.
Observed camera 640 remains within recalculated bounds; max-clamp is NOT TESTED.
Mapped popup boxes fit inside the Mosaic viewport at that camera: exterior
points are not proof of a clipped portion after migration. Opaque tiled spill
without a negative clip control, effects (disabled), newly included point hits,
intermediate frames, saved buffers and ABI/package remain unqualified.

Consumed budgets: six reconfigurations, six migrations, zero camera pairs.
The ledger is exhausted for dynamic operations: do not run any mode again in
this campaign. Only offline analysis/validation can be repeated. New campaign
measurements require a separately authorized scope and budget.

`scenario.py` stores source text as a Python constant; `run.py` inserts it into
the inherited bounded runner. Python AST checks cover the modules and all
retained generated runners. Clients compile under C17 -Werror. New patch hashes:

- pointer-dynamic-extents.patch: `b07b1549f541cc55e1170737ea7aa4b869cd97f3411c1b103be1b96b21971eef`
- ownership-trace.patch: `4a4a48566bd5d5fe8edf6146548cbcf4f93500cc62421780b75cd1dcb82abcb6`

The report distinguishes passive callback observation, settled capture and
client delivery. Raw runs, source/evidence manifests and structured analyses
remain outside Git. The original 529-entry evidence manifest and its expected
SHA-256 were verified before an offline analyzer rerun replaced that temporary
manifest with a 528-entry replay inventory. See the report's provenance note;
the original manifest bytes are no longer present in the lab.

For an independent wlroots source audit, fetch the authoritative wlroots Git
repository and inspect commit `d783533489e1f75d6886c2ab5c5960090ef268f8`
(tag 0.20.2). The campaign retains its complete source archive outside Git as
`wlroots-audited-source.tar`; replay binaries link installed wlroots 0.20.2,
without rebuilding or modifying that system library. pkg-config names are
`wlroots-0.20`, `scenefx-0.5` and `wayland-client`.
