#!/bin/sh
# Rebuild the distributable delta with a private Git index; the real index and
# upstream commit stay untouched. Run only after validating this source tree.
set -eu
cd "$(dirname "$0")/.."
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT HUP INT TERM
export GIT_INDEX_FILE="$temporary/index"
git read-tree HEAD
git add -A -- include meson.build meson_options.txt sway tests/mosaic-model.c
git diff --cached --binary --full-index -- include meson.build meson_options.txt sway tests/mosaic-model.c \
    > patches/0001-mosaic-layout-viewport.patch
git apply --check --reverse patches/0001-mosaic-layout-viewport.patch
