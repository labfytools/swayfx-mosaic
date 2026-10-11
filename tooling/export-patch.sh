#!/bin/sh
# CONTRACT: export the complete Mosaic source delta from the verified SwayFX 0.6
# import. The private index includes staged, unstaged and untracked source,
# while the caller's real index and unrelated project files remain untouched.
set -eu
cd "$(dirname "$0")/.."
repository=$(pwd -P)
base=a57e3f2c4d88f258c2f038343a398c6d5be1fb59
patch=patches/0001-mosaic-layout-viewport.patch

# INVARIANT: a different history must not replace the production artifact
# with a partial delta.
test "$(git rev-parse --show-toplevel)" = "$repository"
test "$(git rev-parse --verify "${base}^{commit}")" = "$base"
git merge-base --is-ancestor "$base" HEAD
# CONTRACT: an unresolved merge has no unambiguous source state to publish.
# Check the caller's index before switching Git to the private one.
if test -n "$(git ls-files -u -- include meson.build meson_options.txt sway tests/mosaic-model.c)"; then
    echo 'Cannot export with unresolved source conflicts' >&2
    exit 1
fi

temporary=$(mktemp -d)
candidate=
cleanup() {
    rm -rf "$temporary"
    if test -n "$candidate"; then
        rm -f "$candidate"
    fi
}
trap cleanup 0
trap 'exit 1' 1 2 3 15
candidate=$(mktemp "$repository/patches/.mosaic-patch.XXXXXX")

# Git add may need to create blobs for working-tree edits. Keep those objects
# private too; the repository object database is only an alternate read source.
original_objects=$(git rev-parse --path-format=absolute --git-path objects)
mkdir "$temporary/objects"
export GIT_OBJECT_DIRECTORY="$temporary/objects"
export GIT_ALTERNATE_OBJECT_DIRECTORIES="$original_objects"
export GIT_INDEX_FILE="$temporary/index"
git read-tree "$base"
# Only package source belongs in the patch. -A includes additions, removals,
# staged changes and working-tree edits without changing the caller's index.
git add -A -- include meson.build meson_options.txt sway tests/mosaic-model.c
git diff --cached --binary --full-index "$base" -- \
    include meson.build meson_options.txt sway tests/mosaic-model.c > "$candidate"
test -s "$candidate"

# Reverse applicability checks the current tree. Forward application and a
# source content and mode comparison catch incomplete exports before publication.
git apply --check --reverse "$candidate"
mkdir "$temporary/pristine"
git archive "$base" > "$temporary/base.tar"
tar -xf "$temporary/base.tar" -C "$temporary/pristine"
(
    cd "$temporary/pristine"
    git apply --check "$candidate"
    git apply "$candidate"
)
for source in include sway meson.build meson_options.txt tests/mosaic-model.c; do
    git diff --no-index --exit-code -- "$temporary/pristine/$source" "$source"
done

# candidate lives beside patch, so rename is atomic on the same filesystem.
chmod 644 "$candidate"
mv -f "$candidate" "$patch"
candidate=
