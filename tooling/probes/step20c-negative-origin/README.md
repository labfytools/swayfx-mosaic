# STEP20C negative-origin nested-grab fixture (EXPERIMENTAL)

This source-only fixture rebuilds the pinned private compositor and SceneFX
through the historical [nested-grab fixture](../step20c-nested-grab/README.md),
then applies only the historical parameterized
[pointer patch](../step20c-vertical-grab/pointer-extents.patch) to a disposable
client copy. The original nested client supplies two real XDG grabs and
horizontal placements. No production source, installed library or historical
fixture is modified. The [probe report](../../../docs/design/STEP20C_NEGATIVE_ORIGIN_NESTED_GRAB_PROBE.md)
contains the coordinate contract and evidence.

## Pinned inputs

| Input | Base | SHA-256 |
| --- | --- | --- |
| SceneFX private patch | SceneFX `37ccd723bef49e6891156ffafce8f549f01446cc` | `c74c515b98da8f5f637e260e6a3755c7a75bd78d1c39e54a67850f1c383e30e7` |
| Mosaic private patch | Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754` | `d416f6413ea097a48a44d231e50ffba363914f46c8687f0ea2e4dcacd5f31fe9` |
| Hidden-owner guard | After Mosaic private patch | `35785a8f3e863b3c1fd87932d8ff0c2949b03cb04382cc34e1126170968f802b` |
| `nested-client.c` | Original nested fixture | `2e40c98af72a0df8b316810589a0be8f4425a763db1de448b49a7813956b6f7d` |
| `pointer-daemon.c` | Original valid-grab fixture, then patch below | `a00fcedc38ccb7ca4c25c982d9f38e8bde3168a3833f0c9cf2056e841d720938` |
| `pointer-extents.patch` | Original vertical fixture | `4eeb9f808d0941edca82dc3c5d24a9c936cc3d9d8bb80af3db6aed6af0d47c50` |

The new `prepare.sh` (`ed9d0e8bf50338d39519e003463e637cdba3ecfb147e05a097e88ac6c8def694`),
`run.py` (`7b9e2d311dcf942e4dc625b8fcc25c650b7c3ec1f604828397cf1de120b43541`),
`analyze.py` (`2d33f4876ea1e982b32f9e73145db86836ba2fa7f5382f9433b4b9f076098a49`)
and patched pointer source (`ede9a39adbe1744c771a784f6ad0c296259e36b942c78d75be620b86b9f2a66d`)
can be rechecked against the source manifest in each laboratory. The
three private patches, nested client and pointer patch remain byte-identical
to their historical versions. No new SceneFX, Mosaic or client patch is
needed for this geometry; all changes are in the new runner and wrapper.

## Fresh preparation and replay

Run from a full Git checkout containing the pinned commits. Dependencies are
those listed in the linked historical fixture: Git, Meson, Ninja, C17
compiler, `pkg-config`, `wayland-scanner`, `kitty`, `grim`, `wev`, `swaymsg`,
Python and the documented development libraries. `prepare.sh` creates a new
temporary laboratory, checks and applies private patches there, builds
SceneFX/Mosaic privately, generates protocol bindings and compiles the two
clients. It prints `LAB` and `BUILD_LOG`; retain both paths.
`analyze.py` additionally needs Pillow to decode the retained PNG captures.

```sh
prep=$(sh tooling/probes/step20c-negative-origin/prepare.sh)
printf '%s\n' "$prep"
LAB=$(printf '%s\n' "$prep" | sed -n 's/^LAB=//p')
test -d "$LAB"
for mode in control private_standard private_mosaic; do
  python tooling/probes/step20c-negative-origin/run.py "$LAB" "$mode" pointer negative
  python tooling/probes/step20c-negative-origin/run.py "$LAB" "$mode" visible negative
  python tooling/probes/step20c-negative-origin/run.py "$LAB" "$mode" b_cross negative
  python tooling/probes/step20c-negative-origin/run.py "$LAB" "$mode" both_cross negative
  python tooling/probes/step20c-negative-origin/run.py "$LAB" "$mode" a_cross negative
  python tooling/probes/step20c-negative-origin/run.py "$LAB" "$mode" outside negative
done
for scenario in hidden hidden_click toggle; do
  python tooling/probes/step20c-negative-origin/run.py "$LAB" private_mosaic "$scenario" negative
done
for mode in control private_standard private_mosaic; do
  python tooling/probes/step20c-negative-origin/run.py "$LAB" "$mode" b_cross positive
done
PYTHONDONTWRITEBYTECODE=1 python tooling/probes/step20c-negative-origin/analyze.py "$LAB"
```

Each invocation creates a single-use `run-GEOMETRY-CASE-SCENARIO` directory
under `LAB`. Retain a failed case by renaming its directory before retrying.
The runner writes `outputs-verified.json`, `injections.json`,
`pointer-validation.json`, `measurements.json` for popup scenarios, IPC tree
and output snapshots, `WAYLAND_DEBUG=1` client trace, `wev`, pointer and
compositor logs, captures of both outputs, and `exit-status.json`. The
coordinate conversion is `sent_x=global_x-min_x` after IPC confirms the
negative layout bounds; the absolute extent is `1600×600`. Inspect client
events as well as pointer acknowledgements. A control popup crossing is
conclusive only if actual pixels and buttons cross the border.

Each case uses a short, private mode-0700 `/tmp/mno-*` runtime and an explicit
discovered `SWAYSOCK` for every `swaymsg -s` call. `WAYLAND_DISPLAY` is private.
The runner removes its own runtime only after reaping its process groups and
writing exit codes. Private SceneFX is loaded only for the private compositor.
The current desktop and ordinary Sway IPC socket are never addressed.

## Checks and cleanup

```sh
sh -n tooling/probes/step20c-negative-origin/prepare.sh
PYTHONDONTWRITEBYTECODE=1 python -c 'import ast; ast.parse(open("tooling/probes/step20c-negative-origin/run.py").read())'
(cd "$LAB" && sha256sum -c negative-origin-source-sha256.txt)
git diff --check
```

Review measurements and hash evidence before removing the named `LAB` and
`BUILD_LOG`. Generated protocol sources, binaries, captures, logs and sockets
remain outside Git. Cleanup must target only paths printed by this probe;
historical laboratories and the active session are outside its ownership.
