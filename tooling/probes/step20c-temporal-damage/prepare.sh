#!/bin/sh
# EXPERIMENTAL: private rebuild, with a separate lifecycle-only client patch.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-temporal-damage"
prep_log=$(mktemp /tmp/mtd-prepare-XXXXXXXX)
if ! sh "$repo/tooling/probes/step20c-negative-origin/prepare.sh" > "$prep_log" 2>&1; then
    printf 'PRIVATE_BUILD_FAILED log=%s\n' "$prep_log" >&2
    tail -40 "$prep_log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$prep_log")
test -n "$lab" && test -d "$lab"
trap 'rm -rf -- "$lab"' 0
# CONTRACT: the timing trace is applied only after the preserved private clip
# patch, in this disposable SceneFX checkout; it changes no public header.
(cd "$lab/scenefx" && git apply --check "$fixture/scenefx-timing.patch" &&
    git apply "$fixture/scenefx-timing.patch")
meson compile -C "$lab/scenefx-build" -j 8 >> "$prep_log" 2>&1
(cd "$lab/mosaic" && git apply --check "$fixture/mosaic-output-timing.patch" &&
    git apply "$fixture/mosaic-output-timing.patch")
meson compile -C "$lab/mosaic-build" -j 8 >> "$prep_log" 2>&1
cp "$repo/tooling/probes/step20c-nested-grab/nested-client.c" "$lab/nested-client.c"
(cd "$lab" && git apply --check "$fixture/client-cycle.patch" && git apply "$fixture/client-cycle.patch")
cc -std=c17 -Wall -Wextra -Wno-unused-parameter -I"$lab" \
    "$lab/nested-client.c" "$lab/xdg-shell-protocol.c" -o "$lab/nested-client" \
    $(pkg-config --cflags --libs wayland-client)
sha256sum "$repo/tooling/probes/step20c-nested-grab/nested-client.c" \
    "$repo/tooling/probes/step20c-vertical-grab/pointer-extents.patch" \
    "$repo/tooling/probes/step20c-valid-grab/scenefx-popup-plus-base.patch" \
    "$repo/tooling/probes/step20c-valid-grab/mosaic-popup-plus-base.patch" \
    "$repo/tooling/probes/step20c-valid-grab/hidden-guard.patch" \
    "$fixture/scenefx-timing.patch" \
    "$fixture/mosaic-output-timing.patch" \
    "$fixture/client-cycle.patch" "$lab/nested-client.c" \
    "$fixture/prepare.sh" "$fixture/run.py" "$fixture/analyze.py" \
    > "$lab/temporal-source-sha256.txt"
trap - 0
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$prep_log"
