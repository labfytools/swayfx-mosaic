#!/bin/sh
# EXPERIMENTAL source-only reconstruction. Never launches a compositor.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-saved-transaction-buffer"
log=$(mktemp /tmp/saved-buffer-prepare-XXXXXXXX)
if ! sh "$repo/tooling/probes/step20c-rotated-partial-popup/prepare.sh" > "$log" 2>&1; then
    printf 'BUILD_FAILED log=%s\n' "$log" >&2
    tail -40 "$log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$log" | head -1)
test -n "$lab" && test -d "$lab"
for source in standard mosaic; do
    git -C "$lab/$source" apply --check "$fixture/sway-saved-trace.patch"
    git -C "$lab/$source" apply "$fixture/sway-saved-trace.patch"
done
git -C "$lab/scenefx" apply --check "$fixture/scenefx-saved-trace.patch"
git -C "$lab/scenefx" apply "$fixture/scenefx-saved-trace.patch"
meson compile -C "$lab/scenefx-build" -j 8 >> "$log" 2>&1
meson compile -C "$lab/standard-build" -j 8 >> "$log" 2>&1
meson compile -C "$lab/mosaic-build" -j 8 >> "$log" 2>&1
cc -std=c17 -Wall -Wextra -Werror -Wno-unused-parameter -I"$lab" \
    "$fixture/saved-client.c" "$lab/xdg-shell-protocol.c" -o "$lab/saved-client" \
    $(pkg-config --cflags --libs wayland-client) >> "$log" 2>&1
cp "$log" "$lab/saved-build-log.txt"
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$log"
