#!/bin/sh
# EXPERIMENTAL: rebuild pinned inputs in one private lab; no installation.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
log=$(mktemp /tmp/fractional-prepare-XXXXXXXX)
sh "$repo/tooling/probes/step20c-effects-damage/prepare.sh" > "$log" 2>&1
lab=$(sed -n 's/^LAB=//p' "$log")
test -n "$lab" && test -d "$lab"
# CONTRACT: the baseline is pristine upstream, never a Mosaic-modified tree.
mkdir "$lab/standard"
git -C "$repo" archive fd71a6bdc061bd633b488ae7b83e8a6981d22f86 | tar -xf - -C "$lab/standard"
meson setup "$lab/standard-build" "$lab/standard" -Dwerror=false \
    -Dsd-bus-provider=libsystemd -Dswaybar=false -Dswaynag=false \
    -Dman-pages=disabled -Ddefault-wallpaper=false >> "$log" 2>&1
meson compile -C "$lab/standard-build" -j 8 >> "$log" 2>&1
cp "$log" "$lab/fractional-build-log.txt"
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$log"
