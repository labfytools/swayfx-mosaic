#!/bin/sh
# EXPERIMENTAL source-only build; never launches a compositor.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-saved-target-timeout-input"
log=$(mktemp /tmp/saved-timeout-prepare-XXXXXXXX)
if ! sh "$repo/tooling/probes/step20c-saved-buffer-target-crossing/prepare.sh" > "$log" 2>&1; then
    printf 'BUILD_FAILED log=%s\n' "$log" >&2
    tail -40 "$log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$log" | head -1)
test -n "$lab" && test -d "$lab"
git -C "$lab/mosaic" apply --check "$fixture/target-hit-trace.patch"
git -C "$lab/mosaic" apply "$fixture/target-hit-trace.patch"
meson compile -C "$lab/mosaic-build" -j 8 >> "$log" 2>&1
for client in saved-client static-reference; do
    cc -std=c17 -Wall -Wextra -Werror -Wno-unused-parameter -I"$lab" \
        "$fixture/$client.c" "$lab/xdg-shell-protocol.c" -o "$lab/$client" \
        $(pkg-config --cflags --libs wayland-client) >> "$log" 2>&1
done
cp "$log" "$lab/saved-timeout-build-log.txt"
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$log"
