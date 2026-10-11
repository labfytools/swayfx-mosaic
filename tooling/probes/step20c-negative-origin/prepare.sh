#!/bin/sh
# EXPERIMENTAL: rebuild the historical private compositor in a fresh lab.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-negative-origin"
prior="$repo/tooling/probes/step20c-nested-grab"
pointer_patch="$repo/tooling/probes/step20c-vertical-grab/pointer-extents.patch"
build_log=$(mktemp /tmp/mno-prepare-XXXXXXXX)
if ! sh "$prior/prepare.sh" > "$build_log" 2>&1; then
    printf 'PRIVATE_BUILD_FAILED log=%s\n' "$build_log" >&2
    tail -40 "$build_log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$build_log")
test -n "$lab" && test -d "$lab"
trap 'rm -rf -- "$lab"' 0
# CONTRACT: adapt only the copied client; original fixtures and private
# compositor patches retain their historical hashes.
cp "$repo/tooling/probes/step20c-valid-grab/pointer-daemon.c" "$lab/pointer-daemon.c"
(cd "$lab" && git apply --check "$pointer_patch" && git apply "$pointer_patch")
cc -std=c17 -Wall -Wextra -Wno-unused-parameter -I"$lab" \
  "$lab/pointer-daemon.c" "$lab/virtual-pointer-protocol.c" -o "$lab/pointer-daemon" \
  $(pkg-config --cflags --libs wayland-client)
sha256sum "$prior/nested-client.c" "$pointer_patch" "$fixture/prepare.sh" \
  "$fixture/run.py" "$fixture/analyze.py" "$lab/pointer-daemon.c" \
  > "$lab/negative-origin-source-sha256.txt"
trap - 0
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$build_log"
