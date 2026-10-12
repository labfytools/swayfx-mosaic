#!/bin/sh
# EXPERIMENTAL: reconstruct buffer readback in a disposable private lab.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-buffer-identity"
prep_log=$(mktemp /tmp/mbi-prepare-XXXXXXXX)
if ! sh "$repo/tooling/probes/step20c-presentation-identity/prepare.sh" > "$prep_log" 2>&1; then
    printf 'PRIVATE_BUILD_FAILED log=%s\n' "$prep_log" >&2
    tail -40 "$prep_log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$prep_log")
test -n "$lab" && test -d "$lab"
trap 'rm -rf -- "$lab"' 0
# CONTRACT: only the source in the just-created private lab is patched.
(cd "$lab/mosaic" && git apply --check "$fixture/buffer-identity.patch" &&
    git apply "$fixture/buffer-identity.patch")
meson compile -C "$lab/mosaic-build" -j 8 >> "$prep_log" 2>&1
sha256sum "$fixture/buffer-identity.patch" "$fixture/prepare.sh" \
    "$fixture/run.py" "$fixture/analyze.py" "$fixture/README.md" \
    > "$lab/buffer-source-sha256.txt"
trap - 0
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$prep_log"
