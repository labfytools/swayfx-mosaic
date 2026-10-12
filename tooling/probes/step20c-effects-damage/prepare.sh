#!/bin/sh
# EXPERIMENTAL: only private copied sources and a bounded SHM client.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-effects-damage"
log=$(mktemp /tmp/fxd-prepare-XXXXXXXX)
if ! sh "$repo/tooling/probes/step20c-temporal-damage/prepare.sh" > "$log" 2>&1; then
    printf 'PRIVATE_BUILD_FAILED log=%s\n' "$log" >&2
    tail -40 "$log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$log")
test -n "$lab" && test -d "$lab"
trap 'rm -rf -- "$lab"' 0
# CONTRACT: native identities come from existing output callbacks; the
# preserved listener changes no commit/present or scene decision.
presentation="$repo/tooling/probes/step20c-presentation-identity/presentation-events.patch"
git -C "$lab/mosaic" apply --check "$presentation"
git -C "$lab/mosaic" apply "$presentation"
meson compile -C "$lab/mosaic-build" -j 8 >> "$log" 2>&1
# CONTRACT: optional trace is passive and exists only in this private copy.
if [ "${STEP20C_EFFECT_TRACE:-0}" = 1 ]; then
    git -C "$lab/scenefx" apply --check "$fixture/effect-trace.patch"
    git -C "$lab/scenefx" apply "$fixture/effect-trace.patch"
    meson compile -C "$lab/scenefx-build" -j 8 >> "$log" 2>&1
fi
# CONTRACT: only the disposable top-level SHM client becomes translucent.
(cd "$lab" && git apply --check "$fixture/effect-glass.patch" &&
    git apply "$fixture/effect-glass.patch")
cc -std=c17 -Wall -Wextra -Werror -Wno-unused-parameter -I"$lab" \
    "$lab/nested-client.c" "$lab/xdg-shell-protocol.c" \
    -o "$lab/nested-client" $(pkg-config --cflags --libs wayland-client) >> "$log" 2>&1
sha256sum "$fixture"/*.patch "$fixture"/*.py "$fixture/prepare.sh" \
    "$fixture/README.md" "$presentation" \
    "$repo/tooling/probes/step20c-applied-state-input/run.py" \
    "$repo/tooling/probes/step20c-nested-grab/prepare.sh" \
    "$repo/tooling/probes/step20c-nested-grab/nested-client.c" \
    "$repo/tooling/probes/step20c-negative-origin/prepare.sh" \
    "$repo/tooling/probes/step20c-vertical-grab/pointer-extents.patch" \
    "$repo/tooling/probes/step20c-valid-grab/scenefx-popup-plus-base.patch" \
    "$repo/tooling/probes/step20c-valid-grab/mosaic-popup-plus-base.patch" \
    "$repo/tooling/probes/step20c-valid-grab/hidden-guard.patch" \
    "$repo/tooling/probes/step20c-valid-grab/pointer-daemon.c" \
    "$repo/tooling/probes/step20c-valid-grab/wlr-virtual-pointer-unstable-v1.xml" \
    "$repo/tooling/probes/step20c-temporal-damage/prepare.sh" \
    "$repo/tooling/probes/step20c-temporal-damage/scenefx-timing.patch" \
    "$repo/tooling/probes/step20c-temporal-damage/mosaic-output-timing.patch" \
    "$repo/tooling/probes/step20c-temporal-damage/client-cycle.patch" \
    "$lab/nested-client.c" "$lab/pointer-daemon.c" \
    "$lab/xdg-shell-protocol.c" "$lab/xdg-shell-client.h" \
    "$lab/virtual-pointer-protocol.c" "$lab/virtual-pointer-client.h" \
    "$lab/scenefx/types/scene/wlr_scene.c" "$lab/mosaic/sway/desktop/output.c" \
    > "$lab/effects-source-sha256.txt"
cp "$log" "$lab/effects-build-log.txt"
trap - 0
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$log"
