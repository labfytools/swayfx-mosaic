# Development workflow

Use separate build directories and headless compositor tests. Ordinary development does not install into `/usr`, reload Sway, or change the active desktop session. The current package is experimental; see [Packaging](PACKAGING.md) for the file-ownership contract.

## Repository and remotes

| Remote | Role | Push policy |
| --- | --- | --- |
| `origin` | Canonical Forgejo project | Project changes |
| `github` | Public GitHub mirror | Same reviewed project commits |
| `upstream` | SwayFX source | Fetch only; never push Mosaic changes |

`main` contains the project's public history: imported SwayFX 0.6 base plus Mosaic commits. The external `upstream` remote retains SwayFX history. Public instructions must not depend on a private local branch. Make focused development branches from `main`; merge or publish only after the source delta, tests, docs, and patch agree.

## Base and prerequisites

The pinned base is SwayFX tag `0.6`, commit `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`, using wlroots 0.20 and SceneFX 0.5. Meson, Ninja, the base build dependencies, Python, and the headless test dependencies (`kitty`, `grim`) are needed for the respective checks. Review [Upstream](UPSTREAM.md) before changing the pin. The exact older local Arch package build source is not reconstructible; do not claim byte-identical provenance.

## Pristine baseline build

Use a pristine checkout of the pinned upstream commit for baseline validation, or an already-retained baseline build known to come from that commit. Do not treat a Mosaic-modified tree as an upstream baseline.

```sh
meson setup build-baseline -Dwerror=false -Dsd-bus-provider=libsystemd
meson compile -C build-baseline -j 8
meson test -C build-baseline --print-errorlogs
```

The historical upstream baseline had no Meson tests. A fresh baseline build is especially important for an upstream update. The command above assumes the current working tree is the pristine baseline; use a separate checkout so the Mosaic tree is not altered.

## Mosaic build and headless tests

From the project development tree:

```sh
meson setup build-mosaic \
  -Dwerror=false -Dsd-bus-provider=libsystemd \
  -Dmosaic-package=true -Dprefix=/usr -Dbindir=bin \
  -Dswaybar=false -Dswaynag=false \
  -Dman-pages=disabled -Ddefault-wallpaper=false
meson compile -C build-mosaic -j 8
meson test -C build-mosaic --print-errorlogs
python tests/headless-ipc.py
git diff --check
```

The headless script starts its own compositor socket; use its documented `MOSAIC_BINARY` environment variable for a nondefault build path. Do not send test commands to the running desktop's IPC socket. Record compiler/test failures, not only passes.

## Staging and package checks

```sh
meson install -C build-mosaic --destdir /tmp/swayfx-mosaic-stage
find /tmp/swayfx-mosaic-stage -type f -print
makepkg --printsrcinfo
makepkg --verifysource
```

Inspect the staging manifest. With `mosaic-package=true`, the expected installed file is `/usr/bin/swayfx-mosaic` under the staging root. This is staging, not live installation. A full `makepkg` build is required before a release, with its own build/test output and manifest review.

## Patch export

The development tree contains full SwayFX source for editing. `patches/0001-mosaic-layout-viewport.patch` is the complete production delta against the imported pristine SwayFX 0.6 commit `a57e3f2c4d88f258c2f038343a398c6d5be1fb59` (whose relevant source matches pinned upstream `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`). Run the regression test before export:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v tests/test_export_patch.py
sh -n tooling/export-patch.sh
tooling/export-patch.sh
sha256sum patches/0001-mosaic-layout-viewport.patch
git diff --check
```

The exporter uses a separate temporary Git index and object directory and includes staged, unstaged, added and deleted package source under `include/`, `sway/`, `meson.build`, `meson_options.txt` and `tests/mosaic-model.c`. It refuses unresolved conflicts in those paths and does not change the real index or object database. Before atomic replacement, it requires a nonempty patch, reverse applicability to the current tree, forward applicability to a pristine archive of the imported base, and equivalence of source contents, file modes and links. Failure leaves the prior patch intact. Review the resulting patch and update the checksum in `PKGBUILD` whenever its bytes change.

For an independent release check when the pinned upstream commit is available locally, use a disposable archive of that exact commit:

```sh
(
  set -eu
  upstream=fd71a6bdc061bd633b488ae7b83e8a6981d22f86
  imported=a57e3f2c4d88f258c2f038343a398c6d5be1fb59
  patch_file="$PWD/patches/0001-mosaic-layout-viewport.patch"
  git diff --exit-code "$upstream" "$imported" -- \
    include meson.build meson_options.txt sway tests/mosaic-model.c
  pristine=$(mktemp -d)
  trap 'rm -rf "$pristine"' 0
  git archive "$upstream" > "$pristine/base.tar"
  mkdir "$pristine/source"
  tar -xf "$pristine/base.tar" -C "$pristine/source"
  (cd "$pristine/source" && git apply --check "$patch_file" && git apply "$patch_file")
  for source in include sway meson.build meson_options.txt tests/mosaic-model.c; do
    git diff --no-index --exit-code -- "$pristine/source/$source" "$source"
  done
)
```

Then review the patch and run the package checks in [Packaging](PACKAGING.md). `git apply --check` in an already-patched development tree is not a valid forward-application check. These exporter checks do not qualify the package without a full `makepkg` build and staged manifest inspection.

## Upstream update branch

1. Fetch `upstream` and identify the exact new release commit.
2. Create a dedicated branch/checkout for the new base; inspect SwayFX changes in affected files.
3. Update Architecture, UX, Packaging, Upstream, and limitations for any changed contract before implementing the forward port.
4. Adapt the Mosaic delta manually if the patch conflicts. Never force or silently skip hunks.
5. Build and test the pristine new base, then Mosaic and standard layouts on that base.
6. Run model/headless IPC/rendering tests, stage the package, inspect file ownership, and update the pin, version, patch, and checksums together.
7. Publish only after the new base is validated. The normal SwayFX package continues updating independently.

See [Packaging](PACKAGING.md) and [Upstream](UPSTREAM.md) for release invariants. Desktop key bindings belong to user dotfiles and are not installed here.
