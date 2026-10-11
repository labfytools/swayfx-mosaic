#!/bin/sh
# EXPERIMENTAL: reuse the pinned private build, then adapt only lab clients.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-vertical-grab"
prior="$repo/tooling/probes/step20c-nested-grab"
build_log=$(mktemp /tmp/mvg-prepare-XXXXXXXX)
if ! sh "$prior/prepare.sh" > "$build_log" 2>&1; then
    printf 'PRIVATE_BUILD_FAILED log=%s\n' "$build_log" >&2
    tail -40 "$build_log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$build_log")
test -n "$lab" && test -d "$lab"
trap 'rm -rf -- "$lab"' 0
# CONTRACT: the original sources and private compositor patches stay intact;
# these deltas apply only to copies in the disposable laboratory.
cp "$prior/nested-client.c" "$lab/nested-client.c"
cp "$repo/tooling/probes/step20c-valid-grab/pointer-daemon.c" "$lab/pointer-daemon.c"
(cd "$lab" && git apply --check "$fixture/client-vertical.patch" &&
    git apply "$fixture/client-vertical.patch" &&
    git apply --check "$fixture/pointer-extents.patch" &&
    git apply "$fixture/pointer-extents.patch")
cc -std=c17 -Wall -Wextra -Wno-unused-parameter -I"$lab" \
  "$lab/nested-client.c" "$lab/xdg-shell-protocol.c" -o "$lab/nested-client" \
  $(pkg-config --cflags --libs wayland-client)
cc -std=c17 -Wall -Wextra -Wno-unused-parameter -I"$lab" \
  "$lab/pointer-daemon.c" "$lab/virtual-pointer-protocol.c" -o "$lab/pointer-daemon" \
  $(pkg-config --cflags --libs wayland-client)
sha256sum "$fixture"/*.patch "$fixture"/prepare.sh "$fixture"/run.py \
    "$lab/nested-client.c" "$lab/pointer-daemon.c" > "$lab/vertical-source-sha256.txt"
trap - 0
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$build_log"
