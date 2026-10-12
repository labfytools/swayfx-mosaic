# STEP20C presentation identity fixture — EXPERIMENTAL

The [protocol](../../../docs/design/STEP20C_PRESENTATION_IDENTITY_PROBE.md)
precedes the private instrumentation. Only fixed two-output headless geometry
`HEADLESS-1 (-800,0)` and `HEADLESS-2 (0,0)`, both 800×600 at scale 1 and
normal transform, is in scope. STEP20C remains NEXT and production
multi-output Mosaic is NOT YET SUPPORTED.

The base is the published temporal fixture at Mosaic commit
`d19b15bfdeaa49ce81317c88a1baa250220a9998`: pinned SwayFX
`fd71a6bdc061bd633b488ae7b83e8a6981d22f86`, private Mosaic
`cd550382b311efdbfe3ed892f4e1d281d852e754`, and private SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc`, plus the historical
clip, popup guard and timing patches named in the
[temporal README](../step20c-temporal-damage/README.md). Installed wlroots
0.20.2 is audited against upstream tag commit
`d783533489e1f75d6886c2ab5c5960090ef268f8`.

The new [`presentation-events.patch`](presentation-events.patch), SHA-256
`dbf1f1d11c9c741b641916d25ac22bcb13c3455ee3002e1f534aa6794cd8a538`,
is applied only after the temporal private Mosaic patch in a disposable lab.
It adds a listener to the private compositor's internal output object,
logs native `commit_seq` and headless present event fields, and reads scene
position and clip in the accepted commit callback. The listener is removed
before output destruction. No public SceneFX ABI, headless backend,
production build, cumulative patch or package is changed. Neither a commit
callback nor a `grim` screenshot proves the pixels in a specific commit
buffer. Logging may perturb timing.

## Rebuild and replay

Requires the temporal fixture's Git/Meson/Ninja/C17, Wayland, Kitty, `grim`,
`wev`, `swaymsg` and Pillow dependencies. Run from a full clone containing
the pinned commits and this uncommitted phase-B fixture directory; when
starting from published `main`, copy this directory into that clone first.
The source manifest verifies the copied inputs. Preparation checks patch applicability with
`git apply --check`, builds private SceneFX and Mosaic, compiles private C17
clients and prints the laboratory and build log. All runtime sockets are
private; only the private compositor loads the private SceneFX library.

```sh
prep=$(sh tooling/probes/step20c-presentation-identity/prepare.sh)
printf '%s\n' "$prep"
LAB=$(printf '%s\n' "$prep" | sed -n 's/^LAB=//p')
(cd "$LAB" && sha256sum -c temporal-source-sha256.txt && \
    sha256sum -c presentation-source-sha256.txt)
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-presentation-identity/run.py \
  "$LAB" private_mosaic identity
for mode in control private_standard private_mosaic; do
  PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-presentation-identity/run.py \
    "$LAB" "$mode" cycles --cycles 1
done
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-presentation-identity/run.py \
  "$LAB" private_mosaic hidden_click
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-presentation-identity/run.py \
  "$LAB" private_mosaic outside
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-presentation-identity/analyze.py "$LAB"
```

The `identity` run creates A/B once with genuine button serials, executes
five settled hide/return pairs and then twelve faster alternating requests.
After the last return, it sends a fresh B button without closing or
recreating either popup. `cycles` exercises explicit B then A closure;
`hidden_click` and `outside` are separate grab-dismissal runs. The runner
limits duration, captures and bytes, records exit codes, reaps only its own
process groups, and removes only its private runtime. Do not use the daily
Wayland or Sway IPC socket.

The [negative-origin input fixture](../step20c-negative-origin/README.md)
can also run `b_cross` for all three configurations and `visible` for private
Mosaic in the prepared lab. These runs show pointer delivery at the clipped
boundary, with their own `analysis.json`; they are not silently merged into
the seven-run presentation summary.

```sh
for mode in control private_standard private_mosaic; do
  PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-negative-origin/run.py \
    "$LAB" "$mode" b_cross negative
done
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-negative-origin/run.py \
  "$LAB" private_mosaic visible negative
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-negative-origin/analyze.py "$LAB"
```

## Correlation and retained evidence

`LAB/presentation-results/` contains `events.jsonl`, `commits.json`,
`presentations.json`, `camera-states.json`, `damage-analysis.json`,
`input-analysis.json`, `pixel-analysis.json`, `transitions.json`,
`matrix.json` and `summary.json`. The analyzer pairs only an actual native
`(output, commit_seq)`. The scene, owner and root-popup clip lines logged
inside that synchronous commit callback are associated with that callback.
It never assigns a `grim` PNG, pointer event or preceding damage extent to
a commit without proof. PNG records contain monotonic capture bounds,
output, SHA-256, fixed ROI and exact A/B color counts. Client event lines
lack a common monotonic timestamp; this is an explicit input limitation.

The measured laboratory is `/tmp/swayfx-mosaic-nested-grab-FQLULvot/`.
It retains a pilot identity run, the final identity run, five further
presentation runs, four separate crossing/visible input controls, private
builds and raw logs. The [report](../../../docs/design/STEP20C_PRESENTATION_IDENTITY_PROBE.md)
records the limited PARTIALLY_FEASIBLE verdict. The source manifest is
`presentation-source-sha256.txt`; the retained artifact manifest is
`presentation-artifacts-sha256.txt` under `presentation-results/`.

## Validation and cleanup

```sh
sh -n tooling/probes/step20c-presentation-identity/prepare.sh
PYTHONDONTWRITEBYTECODE=1 python -c 'import ast,pathlib; [ast.parse(p.read_text()) for p in pathlib.Path("tooling/probes/step20c-presentation-identity").glob("*.py")]'
meson test -C "$LAB/mosaic-build" --print-errorlogs
(cd "$LAB" && sha256sum -c presentation-source-sha256.txt)
git diff --check
```

Inspect `exit-status.json`, native event logs, XDG client traces, IPC trees,
PNG hashes and matrix assertions before a verdict. Keep failed runs. If
cleaning later, remove only the printed `LAB` and `BUILD_LOG` paths after
preserving their evidence; never clean all `/tmp` or alter the daily session.
