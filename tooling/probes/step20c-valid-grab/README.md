# STEP20C valid-grab / hidden-owner fixture (EXPERIMENTAL)

This fixture preserves the bounded headless comparison reported in
[the STEP20C probe](../../../docs/design/STEP20C_VALID_GRAB_HIDDEN_OWNER_PROBE.md).
It is not part of the Mosaic build or package. Its private SceneFX symbols and
Mosaic edits are feasibility evidence, not production interfaces. The result is
**PARTIALLY_FEASIBLE** at the measured pixels and pointer locations only.

## Provenance and exact inputs

| Input | Base / origin | SHA-256 |
| --- | --- | --- |
| `mosaic-popup-plus-base.patch` | Complete private delta against Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754` | `d416f6413ea097a48a44d231e50ffba363914f46c8687f0ea2e4dcacd5f31fe9` |
| `scenefx-popup-plus-base.patch` | Complete private delta against [SceneFX](https://github.com/wlrfx/scenefx) tag 0.5, `37ccd723bef49e6891156ffafce8f549f01446cc` | `c74c515b98da8f5f637e260e6a3755c7a75bd78d1c39e54a67850f1c383e30e7` |
| `hidden-guard.patch` | Incremental private delta after the Mosaic patch | `35785a8f3e863b3c1fd87932d8ff0c2949b03cb04382cc34e1126170968f802b` |
| `grab-client.c` | Original valid-serial XDG client from the probe lab | `202afdc5dae0ee4aba570eef4a563f8b298474eb84e33af9510c4c81c05d16e4` |
| `pointer-daemon.c` | Original persistent virtual pointer from the probe lab | `a00fcedc38ccb7ca4c25c982d9f38e8bde3168a3833f0c9cf2056e841d720938` |
| `run.py` | Original headless runner from the probe lab | `b2aaa90188ea387cb8a69aa69935b56e63f5ce70eb98e74783b0fb3c9236a41f` |
| `wlr-virtual-pointer-unstable-v1.xml` | [wlr-protocols](https://github.com/swaywm/wlr-protocols), `b010a03648b88d143236de193bddbfea0c08bc84`, `unstable/` | `3ff6d540be0bc5228195bf072bde42117ea17945a5c2061add5d3cf97d6bb524` |

The six lab files above are byte-identical to the originals in
`/tmp/swayfx-mosaic-valid-grab-7SA2yO/`; none was adapted. The protocol XML
regenerates that lab's `virtual-pointer-client.h` and
`virtual-pointer-protocol.c` byte-for-byte. `xdg-shell.xml` comes from the
installed `wayland-protocols` package. The pinned pristine SwayFX base is
`fd71a6bdc061bd633b488ae7b83e8a6981d22f86`; **do not apply the Mosaic
private patch to that base**. The Mosaic commit above already includes the
project's prior Mosaic changes.

The original environment used SwayFX 0.6 (`swayfx` 0.6-1), SceneFX 0.5
(`scenefx` 0.5-1), wlroots 0.20.2 (`wlroots0.20` 0.20.2-1),
`wayland-client` 1.26.0, and the installed `wayland-protocols` XML. Meson,
Ninja, `wayland-scanner`, a C17 compiler, `pkg-config`, Python, `kitty`,
`swaymsg`, `grim`, `wev`, and `/usr/bin/sway` are required. Package releases
and scanner versions may change; record them when reproducing.

## Rebuild in a new temporary laboratory

Run from this repository root. The commands copy only source fixtures into a
new `mktemp` directory; all compiled files, sockets, logs and captures stay
there. Keep `R` for the commands below, then remove it during cleanup.

```sh
set -eu
R=$(mktemp -d /tmp/swayfx-mosaic-valid-grab-replay-XXXXXXXX)
F="$PWD/tooling/probes/step20c-valid-grab"
cp "$F/grab-client.c" "$F/pointer-daemon.c" "$F/run.py" "$F"/*.patch \
  "$F/wlr-virtual-pointer-unstable-v1.xml" "$R/"
mkdir "$R/mosaic" "$R/scenefx"
git archive cd550382b311efdbfe3ed892f4e1d281d852e754 | tar -xf - -C "$R/mosaic"
git clone --quiet https://github.com/wlrfx/scenefx.git "$R/scenefx-git"
git -C "$R/scenefx-git" checkout --quiet --detach 37ccd723bef49e6891156ffafce8f549f01446cc
git -C "$R/scenefx-git" archive HEAD | tar -xf - -C "$R/scenefx"
(cd "$R/scenefx" && git apply --check "$R/scenefx-popup-plus-base.patch" && git apply "$R/scenefx-popup-plus-base.patch")
(cd "$R/mosaic" && git apply --check "$R/mosaic-popup-plus-base.patch" && git apply "$R/mosaic-popup-plus-base.patch")
# This is the unguarded baseline. Save it only in the temporary lab.
cp "$R/mosaic/sway/desktop/transaction.c" "$R/transaction-before-hidden.c"
(cd "$R/mosaic" && git apply --check "$R/hidden-guard.patch" && git apply "$R/hidden-guard.patch")

meson setup "$R/scenefx-build" "$R/scenefx" -Dexamples=false -Dwerror=false
meson compile -C "$R/scenefx-build" -j 8
PKG_CONFIG_PATH="$R/scenefx-build/meson-uninstalled" meson setup "$R/mosaic-build" "$R/mosaic" \
  -Dmosaic-package=true -Ddefault-wallpaper=false -Dswaybar=false -Dswaynag=false \
  -Dman-pages=disabled -Dsd-bus-provider=libsystemd -Dwerror=false
PKG_CONFIG_PATH="$R/scenefx-build/meson-uninstalled" meson compile -C "$R/mosaic-build" -j 8

wayland-scanner client-header /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml "$R/xdg-shell-client.h"
wayland-scanner private-code /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml "$R/xdg-shell-protocol.c"
wayland-scanner client-header "$R/wlr-virtual-pointer-unstable-v1.xml" "$R/virtual-pointer-client.h"
wayland-scanner private-code "$R/wlr-virtual-pointer-unstable-v1.xml" "$R/virtual-pointer-protocol.c"
cc -std=c17 -Wall -Wextra -Wno-unused-parameter -I"$R" "$R/grab-client.c" "$R/xdg-shell-protocol.c" -o "$R/grab-client" $(pkg-config --cflags --libs wayland-client)
cc -std=c17 -Wall -Wextra -Wno-unused-parameter -I"$R" "$R/pointer-daemon.c" "$R/virtual-pointer-protocol.c" -o "$R/pointer-daemon" $(pkg-config --cflags --libs wayland-client)
```

For the **unguarded** comparison, reconstruct a second disposable Mosaic
source/build directory from the same Mosaic commit and apply only the first
Mosaic patch. Keep the guarded binary intact for restoration:

```sh
mkdir "$R/mosaic-unguarded"
git archive cd550382b311efdbfe3ed892f4e1d281d852e754 | tar -xf - -C "$R/mosaic-unguarded"
(cd "$R/mosaic-unguarded" && git apply --check "$R/mosaic-popup-plus-base.patch" && git apply "$R/mosaic-popup-plus-base.patch")
cmp "$R/mosaic-unguarded/sway/desktop/transaction.c" "$R/transaction-before-hidden.c"
PKG_CONFIG_PATH="$R/scenefx-build/meson-uninstalled" meson setup "$R/mosaic-unguarded-build" "$R/mosaic-unguarded" \
  -Dmosaic-package=true -Ddefault-wallpaper=false -Dswaybar=false -Dswaynag=false \
  -Dman-pages=disabled -Dsd-bus-provider=libsystemd -Dwerror=false
PKG_CONFIG_PATH="$R/scenefx-build/meson-uninstalled" meson compile -C "$R/mosaic-unguarded-build" -j 8
```

The original runner always selects `R/mosaic-build/sway/swayfx-mosaic`. To run
the unguarded case, first save that *temporary* guarded binary and replace it
with the unguarded build; restore it afterward. Never modify a system binary
or library.

## Run the original reference cases

`run.py` resolves its laboratory from its own copied path. It removes inherited
`WAYLAND_DISPLAY` and `SWAYSOCK`, creates a mode-0700 run directory for each
case, starts a two-output headless compositor, discovers its new sockets, and
passes that socket explicitly to every `swaymsg -s` call. The private SceneFX
library path is process-local to the private compositor. It never targets the
active desktop socket. Run only these previously reported cases:

```sh
python "$R/run.py" control boundary_left
python "$R/run.py" private_standard boundary_right
python "$R/run.py" private_mosaic boundary_left
python "$R/run.py" private_mosaic      # guarded, no hidden click; tests mapped return
python "$R/run.py" private_mosaic_hit  # guarded hidden-click case
cp "$R/mosaic-build/sway/swayfx-mosaic" "$R/guarded-swayfx-mosaic"
cp "$R/mosaic-unguarded-build/sway/swayfx-mosaic" "$R/mosaic-build/sway/swayfx-mosaic"
mv "$R/run-private_mosaic_hit" "$R/run-private_mosaic_hit-guarded"
python "$R/run.py" private_mosaic_hit  # unguarded baseline
cp "$R/guarded-swayfx-mosaic" "$R/mosaic-build/sway/swayfx-mosaic"
```

The runner reuses `run-private_mosaic_hit/` for both variants; rename that
directory within `R` after the unguarded run to retain both result sets.
Check `client.log` for the same received/used nonzero serial and XDG configure;
inspect `pointer.log`, `wev.log`, IPC JSON and the left/right PNGs. Expected
sampled observations: standard control and private standard deliver popup
input at `(900,150)`; Mosaic clips that point; unguarded hidden owner leaks a
yellow pixel and popup enter/button at `(100,150)`; guarded hidden owner shows
ordinary background and no popup enter/button there; the no-click guarded
case shows the same mapped popup after camera return. A hidden outside click
may trigger `popup_done` under the valid grab without delivering a popup
button, as it did in the original report. Treat any disagreement as a new
observation, not as a reason to rewrite the recorded result.

The probe does not establish universal leak freedom, full transaction/damage
correctness, effects/saved-buffer behavior, ABI durability, general
multi-output safety, or an offscreen-popup UX policy. Valid-grab nested
popups and other output geometries remain **NOT TESTED**.

## Cleanup

After all processes started by `run.py` have exited, remove only the new lab:

```sh
rm -rf -- "$R"
```

Do not clean the original probe laboratory as part of this procedure.
