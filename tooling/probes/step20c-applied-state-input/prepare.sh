#!/bin/sh
# EXPERIMENTAL: rebuild only in a disposable private laboratory.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-applied-state-input"
prep_log=$(mktemp /tmp/asi-prepare-XXXXXXXX)
if ! sh "$repo/tooling/probes/step20c-buffer-identity/prepare.sh" > "$prep_log" 2>&1; then
    printf 'PRIVATE_BUILD_FAILED log=%s\n' "$prep_log" >&2
    tail -40 "$prep_log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$prep_log")
test -n "$lab" && test -d "$lab"
trap 'rm -rf -- "$lab"' 0
(cd "$lab/mosaic" && git apply --check "$fixture/applied-state-input.patch" &&
    git apply "$fixture/applied-state-input.patch")
meson compile -C "$lab/mosaic-build" -j 8 >> "$prep_log" 2>&1
sha256sum "$fixture/applied-state-input.patch" "$fixture/prepare.sh" \
    "$fixture/run.py" "$fixture/analyze.py" "$fixture/README.md" \
    > "$lab/asi-source-sha256.txt"
trap - 0
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$prep_log"
