#!/bin/sh
# EXPERIMENTAL: disposable sources only; caller owns successful LAB.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-dynamic-output"
log=$(mktemp /tmp/dynamic-output-prepare-XXXXXXXX)
if ! sh "$repo/tooling/probes/step20c-fractional-scale/prepare.sh" > "$log" 2>&1; then
    printf 'BUILD_FAILED log=%s\n' "$log" >&2
    tail -40 "$log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$log")
test -n "$lab" && test -d "$lab"
# CONTRACT: reversing the glass fixture yields an opaque XRGB owner;
# no compositor algorithm or historical patch is changed.
(cd "$lab" && git apply --check -R "$repo/tooling/probes/step20c-effects-damage/effect-glass.patch" &&
 git apply -R "$repo/tooling/probes/step20c-effects-damage/effect-glass.patch" &&
 git apply --check "$fixture/pointer-dynamic-extents.patch" &&
 git apply "$fixture/pointer-dynamic-extents.patch")
(cd "$lab/mosaic" && git apply --check "$fixture/ownership-trace.patch" && git apply "$fixture/ownership-trace.patch")
meson compile -C "$lab/mosaic-build" -j 8 >> "$log" 2>&1
for client in nested-client pointer-daemon; do
    protocol=xdg-shell
    test "$client" != pointer-daemon || protocol=virtual-pointer
    cc -std=c17 -Wall -Wextra -Werror -Wno-unused-parameter -I"$lab" \
       "$lab/$client.c" "$lab/$protocol-protocol.c" -o "$lab/$client" \
       $(pkg-config --cflags --libs wayland-client) >> "$log" 2>&1
done
cp "$log" "$lab/dynamic-build-log.txt"
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$log"
