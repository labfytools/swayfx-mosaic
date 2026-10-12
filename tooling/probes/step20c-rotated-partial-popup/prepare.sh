#!/bin/sh
# EXPERIMENTAL source-only preparation; never launches a compositor.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-rotated-partial-popup"
base="$repo/tooling/probes/step20c-nested-grab/nested-client.c"
test "$(sha256sum "$base" | cut -d ' ' -f 1)" = 2e40c98af72a0df8b316810589a0be8f4425a763db1de448b49a7813956b6f7d
log=$(mktemp /tmp/rot-partial-prepare-XXXXXXXX)
if ! sh "$repo/tooling/probes/step20c-dynamic-output/prepare.sh" > "$log" 2>&1; then
    printf 'BUILD_FAILED log=%s\n' "$log" >&2
    tail -40 "$log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$log")
test -n "$lab" && test -d "$lab"
cp "$base" "$lab/nested-client.c"
patch -d "$lab" -p1 --dry-run < "$fixture/rot-cross-client.patch" >> "$log" 2>&1
patch -d "$lab" -p1 < "$fixture/rot-cross-client.patch" >> "$log" 2>&1
cc -std=c17 -Wall -Wextra -Werror -Wno-unused-parameter -I"$lab" \
    "$lab/nested-client.c" "$lab/xdg-shell-protocol.c" -o "$lab/nested-client" \
    $(pkg-config --cflags --libs wayland-client) >> "$log" 2>&1
cp "$log" "$lab/partial-build-log.txt"
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$log"
