# STEP20C vertical-output nested grab fixture (EXPERIMENTAL)

This source-only fixture reuses the pinned private
[nested-grab build](../step20c-nested-grab/README.md) and the unchanged
[valid-grab patches](../step20c-valid-grab/README.md). It does not enter the
ordinary Mosaic build, production patch or package. The comparative protocol,
observations and limits are in the
[vertical probe report](../../../docs/design/STEP20C_VERTICAL_OUTPUT_NESTED_GRAB_PROBE.md).

## Provenance and SHA-256

| Input | Role / origin | SHA-256 |
| --- | --- | --- |
| SceneFX private patch | Unchanged, SceneFX `37ccd723bef49e6891156ffafce8f549f01446cc` | `c74c515b98da8f5f637e260e6a3755c7a75bd78d1c39e54a67850f1c383e30e7` |
| Mosaic private patch | Unchanged, Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754` | `d416f6413ea097a48a44d231e50ffba363914f46c8687f0ea2e4dcacd5f31fe9` |
| Hidden-owner guard | Unchanged, after Mosaic private patch | `35785a8f3e863b3c1fd87932d8ff0c2949b03cb04382cc34e1126170968f802b` |
| `client-vertical.patch` | Adds three vertical placements and a 575 px toplevel buffer to a temporary copy of the preserved `nested-client.c` | `58e1c41cde875ebf2edf25adb0ae98c03cb33aaf26ab4088a8782880a366e837` |
| `pointer-extents.patch` | Adds validated WIDTH/HEIGHT arguments to a temporary copy of the preserved `pointer-daemon.c` | `4eeb9f808d0941edca82dc3c5d24a9c936cc3d9d8bb80af3db6aed6af0d47c50` |
| `prepare.sh` | Reuses the earlier pinned private build, applies the two fixture patches and recompiles only the clients | `6003004eaa3cbd005ca29d3e2319e1e8fe15377d4a883d352b27e289d70fbb52` |
| `run.py` | Isolated comparative runner, derived from preserved nested-grab runner | `b7dc778c01d9e8e1f058c1aa2bb0e3e0e8dfa6ad1ba8e5af122a0503cd7eef96` |

The patched laboratory clients have SHA-256
`b2381f088994202a0577318b2da3bcf799362c6d5308be1e66a6bdd55a1fc76b`
(`nested-client.c`) and
`ede9a39adbe1744c771a784f6ad0c296259e36b942c78d75be620b86b9f2a66d`
(`pointer-daemon.c`). The originals and all three compositor/library patches
remain byte-identical. `client-vertical.patch` adds `v_visible`,
`v_b_cross` and `v_both_cross` and sets the vertical toplevel buffer height
to 575 px. A's `y=350/480` anchors then remain inside its effective window
geometry; horizontal client behavior is unchanged. `pointer-extents.patch` keeps left/right
button behavior and rejects invalid coordinates; the runner passes
`800 1200` vertically or `1600 600` horizontally. The virtual pointer stays
alive for the case. The copied runner changes output geometry, verifies IPC
output rectangles/scale/transform, derives sample points from configured
popup geometry and the actual `wev` rectangle, saves `measurements.json`,
and records process exit statuses. It does not change production C.

The measured environment used SwayFX 0.6 (`/usr/bin/sway`), SceneFX 0.5,
wlroots 0.20.2, Wayland client 1.26.0 and wayland-protocols 1.49. Required
tools: Git, Meson, Ninja, a C17 compiler, `pkg-config`, `wayland-scanner`,
Python, `kitty`, `swaymsg`, `grim` and `wev`. The prior `prepare.sh` fetches
the pinned SceneFX commit into a disposable directory, applies its private
patch first, then the Mosaic patch and hidden-owner guard, builds private
SceneFX and Mosaic, generates the XDG and virtual-pointer protocols and
compiles both clients. This wrapper applies the two new patches only to
temporary client copies and recompiles them. No system installation occurs.

## Fresh replay

Run from the root of a full Git checkout with the pinned Mosaic commit in its
object database. A source-only `git archive` is insufficient because the
reused nested-grab preparation runs `git archive` on that pinned commit.
The build prints a real `LAB=` path and the
private build log path. Capture that output rather than substituting a
fictitious temporary directory. An unsuccessful preparation prints its log
path and cleans its incomplete laboratory.

```sh
prep=$(sh tooling/probes/step20c-vertical-grab/prepare.sh)
printf '%s\n' "$prep"
LAB=$(printf '%s\n' "$prep" | sed -n 's/^LAB=//p')
test -d "$LAB"
python tooling/probes/step20c-vertical-grab/run.py "$LAB" control visible vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_standard visible vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_mosaic visible vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" control b_cross vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_standard b_cross vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_mosaic b_cross vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" control both_cross vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_standard both_cross vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_mosaic both_cross vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" control below_left vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_standard below_left vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_mosaic below_left vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" control below_a vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_standard below_a vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_mosaic below_a vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_mosaic hidden vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_mosaic hidden_click vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_mosaic toggle vertical
python tooling/probes/step20c-vertical-grab/run.py "$LAB" control b_cross horizontal
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_standard b_cross horizontal
python tooling/probes/step20c-vertical-grab/run.py "$LAB" private_mosaic b_cross horizontal
```

Each run creates a single-use `run-GEOMETRY-CASE-SCENARIO` directory in `LAB`.
Its `outputs-verified.json`, IPC tree/output snapshots, `measurements.json`,
`client.log` (`WAYLAND_DEBUG=1`), `pointer.log`, `wev.log`, `compositor.log`,
two-output PNGs and `exit-status.json` are the evidence. `runtime-path`
records a new short mode-0700 `/tmp/mvg-*` directory; the runner removes it
after reaping only processes it started. It clears inherited
`WAYLAND_DISPLAY`, `SWAYSOCK`, `I3SOCK` and client `LD_LIBRARY_PATH`;
private SceneFX is loaded only by the private compositor. Every `swaymsg`
uses the discovered socket with `-s`. The daily desktop is never addressed.

Verify the configured A/B XDG rectangles and matching real button serials
before using any pixel comparison. A crossing estimate is insufficient:
standard controls must show popup pixels on HEADLESS-2 and receive the
sampled lower button. Compare Mosaic upper popup buttons, lower `wev`
buttons, `popup_done` order and both PNGs. The runner can finish normally
even when scientific evidence is **INCONCLUSIVE**; use the report criteria.
One outside click may dismiss the grabbed hierarchy, so left, right and A
lower tests are separate runs. The `toggle` case changes layout with both
popups still open. Horizontal regression uses the same adapted pointer with
its historical `(1600,600)` extents.

## Cleanup

Preserve the lab until measurements and hashes have been reviewed. A normal
run removes its own runtime directory. For an interrupted run, inspect its
`runtime-path` and remove only that recorded `/tmp/mvg-*` directory after
confirming its private processes have stopped. Then remove only the named
`LAB` and the printed `BUILD_LOG`. Never remove the old historical labs or
any system library. Generated sources, binaries, sockets, logs and captures
stay outside Git.
