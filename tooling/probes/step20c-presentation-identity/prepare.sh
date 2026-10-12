#!/bin/sh
# EXPERIMENTAL: build a private compositor with native commit/present tracing.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-presentation-identity"
prep_log=$(mktemp /tmp/mpi-prepare-XXXXXXXX)
if ! sh "$repo/tooling/probes/step20c-temporal-damage/prepare.sh" > "$prep_log" 2>&1; then
    printf 'PRIVATE_BUILD_FAILED log=%s\n' "$prep_log" >&2
    tail -40 "$prep_log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$prep_log")
test -n "$lab" && test -d "$lab"
trap 'rm -rf -- "$lab"' 0
# CONTRACT: apply only to the already-patched private Mosaic source;
# never to this repository's production compositor or installed libraries.
(cd "$lab/mosaic" && git apply --check "$fixture/presentation-events.patch" &&
    git apply "$fixture/presentation-events.patch")
meson compile -C "$lab/mosaic-build" -j 8 >> "$prep_log" 2>&1
sha256sum "$fixture/presentation-events.patch" "$fixture/prepare.sh" \
    "$fixture/run.py" "$fixture/analyze.py" "$fixture/README.md" \
    > "$lab/presentation-source-sha256.txt"
trap - 0
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$prep_log"
