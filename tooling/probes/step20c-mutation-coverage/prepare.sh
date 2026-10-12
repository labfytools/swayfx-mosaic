#!/bin/sh
# EXPERIMENTAL: all modified compositor/client sources stay in /tmp.
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
fixture="$repo/tooling/probes/step20c-mutation-coverage"
prep_log=$(mktemp /tmp/mutation-prepare-XXXXXXXX)
if ! sh "$repo/tooling/probes/step20c-applied-state-input/prepare.sh" > "$prep_log" 2>&1; then
    printf 'PRIVATE_BUILD_FAILED log=%s\n' "$prep_log" >&2
    tail -40 "$prep_log" >&2
    exit 1
fi
lab=$(sed -n 's/^LAB=//p' "$prep_log")
test -n "$lab" && test -d "$lab"
trap 'rm -rf -- "$lab"' 0
# CONTRACT: source-audit inputs belong to this lab and are pinned to the
# audited wlroots release. Never use an older machine-local source tree.
wlroots_commit=d783533489e1f75d6886c2ab5c5960090ef268f8
git clone --quiet https://gitlab.freedesktop.org/wlroots/wlroots.git "$lab/wlroots-git"
git -C "$lab/wlroots-git" checkout --quiet --detach "$wlroots_commit"
test "$(git -C "$lab/wlroots-git" rev-parse HEAD)" = "$wlroots_commit"
mkdir "$lab/wlroots"
git -C "$lab/wlroots-git" archive HEAD | tar -xf - -C "$lab/wlroots"
printf '%s\n' \
    'b8c83f292006bc44d349891b1d460245db9dae891e986e6dc2006572f99a7f97  types/scene/surface.c' \
    'e73655cc589321f18a824ed4b153c9b1973f9c41a0f8d52b1d380e28a42671cc  types/scene/subsurface_tree.c' |
    (cd "$lab/wlroots" && sha256sum --quiet -c -)
(
    cd "$lab"
    git apply --check "$fixture/mutation-client.patch"
    git apply "$fixture/mutation-client.patch"
)
cc -std=c17 -Wall -Wextra -Werror -Wno-unused-parameter -I"$lab" \
    "$lab/nested-client.c" "$lab/xdg-shell-protocol.c" \
    -o "$lab/nested-client" $(pkg-config --cflags --libs wayland-client)
trap - 0
printf 'LAB=%s\nBUILD_LOG=%s\n' "$lab" "$prep_log"
