#!/bin/sh
# EXPERIMENTAL: build all private inputs in a fresh temporary laboratory.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-valid-grab"
lab=$(mktemp -d /tmp/swayfx-mosaic-nested-grab-XXXXXXXX)
# CONTRACT: a failed preparation leaves no unreported private build or socket
# tree; a successful one transfers LAB ownership to the caller.
trap 'rm -rf -- "$lab"' 0
mkdir "$lab/mosaic" "$lab/scenefx"
git -C "$repo" archive cd550382b311efdbfe3ed892f4e1d281d852e754 | tar -xf - -C "$lab/mosaic"
git clone --quiet https://github.com/wlrfx/scenefx.git "$lab/scenefx-git"
git -C "$lab/scenefx-git" checkout --quiet --detach 37ccd723bef49e6891156ffafce8f549f01446cc
git -C "$lab/scenefx-git" archive HEAD | tar -xf - -C "$lab/scenefx"
(cd "$lab/scenefx" && git apply --check "$fixture/scenefx-popup-plus-base.patch" && git apply "$fixture/scenefx-popup-plus-base.patch")
(cd "$lab/mosaic" && git apply --check "$fixture/mosaic-popup-plus-base.patch" && git apply "$fixture/mosaic-popup-plus-base.patch" && git apply --check "$fixture/hidden-guard.patch" && git apply "$fixture/hidden-guard.patch")
meson setup "$lab/scenefx-build" "$lab/scenefx" -Dexamples=false -Dwerror=false
meson compile -C "$lab/scenefx-build" -j 8
PKG_CONFIG_PATH="$lab/scenefx-build/meson-uninstalled" meson setup "$lab/mosaic-build" "$lab/mosaic" \
  -Dmosaic-package=true -Ddefault-wallpaper=false -Dswaybar=false -Dswaynag=false \
  -Dman-pages=disabled -Dsd-bus-provider=libsystemd -Dwerror=false
PKG_CONFIG_PATH="$lab/scenefx-build/meson-uninstalled" meson compile -C "$lab/mosaic-build" -j 8
wayland-scanner client-header /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml "$lab/xdg-shell-client.h"
wayland-scanner private-code /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml "$lab/xdg-shell-protocol.c"
wayland-scanner client-header "$fixture/wlr-virtual-pointer-unstable-v1.xml" "$lab/virtual-pointer-client.h"
wayland-scanner private-code "$fixture/wlr-virtual-pointer-unstable-v1.xml" "$lab/virtual-pointer-protocol.c"
cc -std=c17 -Wall -Wextra -Wno-unused-parameter -I"$lab" \
  "$repo/tooling/probes/step20c-nested-grab/nested-client.c" "$lab/xdg-shell-protocol.c" \
  -o "$lab/nested-client" $(pkg-config --cflags --libs wayland-client)
cc -std=c17 -Wall -Wextra -Wno-unused-parameter -I"$lab" \
  "$fixture/pointer-daemon.c" "$lab/virtual-pointer-protocol.c" \
  -o "$lab/pointer-daemon" $(pkg-config --cflags --libs wayland-client)
sha256sum "$fixture"/*.patch "$repo/tooling/probes/step20c-nested-grab/nested-client.c" > "$lab/source-sha256.txt"
trap - 0
printf 'LAB=%s\n' "$lab"
