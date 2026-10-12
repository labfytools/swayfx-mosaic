#!/bin/sh
# EXPERIMENTAL: reconstruct only private sources in a new temporary lab.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-commit-present-input"
log=$(mktemp /tmp/cpi-prepare-XXXXXXXX)
if ! sh "$repo/tooling/probes/step20c-mutation-coverage/prepare.sh" > "$log" 2>&1; then
    printf 'PRIVATE_BUILD_FAILED log=%s\n' "$log" >&2
    tail -40 "$log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$log")
test -n "$lab" && test -d "$lab"
trap 'rm -rf -- "$lab"' 0
# CONTRACT: the additional listener only reads already-applied top-level
# surface state. No installed wlroots, compositor or backend is changed.
(cd "$lab/mosaic" && git apply --check "$fixture/surface-ordering.patch" &&
    git apply "$fixture/surface-ordering.patch")
meson compile -C "$lab/mosaic-build" -j 8 >> "$log" 2>&1
trap - 0
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$log"
