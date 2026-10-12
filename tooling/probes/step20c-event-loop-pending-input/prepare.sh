#!/bin/sh
# EXPERIMENTAL: rebuild private sources only; no installed component is touched.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-event-loop-pending-input"
log=$(mktemp /tmp/epi-prepare-XXXXXXXX)
if ! sh "$repo/tooling/probes/step20c-commit-present-input/prepare.sh" > "$log" 2>&1; then
    printf 'PRIVATE_BUILD_FAILED log=%s\n' "$log" >&2
    tail -40 "$log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$log")
test -n "$lab" && test -d "$lab"
trap 'rm -rf -- "$lab"' 0
# CONTRACT: only the disposable client reports its own flush result/time.
(cd "$lab" && git apply --check "$fixture/client-flush.patch" &&
    git apply "$fixture/client-flush.patch")
cc -std=c17 -Wall -Wextra -Werror -Wno-unused-parameter -I"$lab" \
    "$lab/nested-client.c" "$lab/xdg-shell-protocol.c" \
    -o "$lab/nested-client" $(pkg-config --cflags --libs wayland-client)
trap - 0
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$log"
