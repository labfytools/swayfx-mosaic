# Development workflow

## Safety rule

Development must not replace the daily SwayFX installation or reload the active desktop session.

Use separate build directories and headless compositor tests.

## Upstream

The initial supported base is SwayFX 0.6 at:

```text
fd71a6bdc061bd633b488ae7b83e8a6981d22f86
```

The `upstream` remote must point to the SwayFX repository.

## Baseline build

```sh
meson setup build-baseline \
  -Dwerror=false \
  -Dsd-bus-provider=libsystemd

meson compile -C build-baseline -j 8
meson test -C build-baseline --print-errorlogs
```

The upstream base currently defines no Meson tests.

## Mosaic build

```sh
meson setup build-mosaic \
  -Dwerror=false \
  -Dsd-bus-provider=libsystemd \
  -Dmosaic-package=true \
  -Dprefix=/usr \
  -Dbindir=bin \
  -Dswaybar=false \
  -Dswaynag=false \
  -Dman-pages=disabled \
  -Ddefault-wallpaper=false

meson compile -C build-mosaic -j 8
meson test -C build-mosaic --print-errorlogs
python tests/headless-ipc.py
git diff --check
```

## Package staging

Never install to the live system as part of routine validation.

```sh
rm -rf /tmp/swayfx-mosaic-stage
meson install -C build-mosaic --destdir /tmp/swayfx-mosaic-stage
find /tmp/swayfx-mosaic-stage -type f -print
```

The staging manifest must remain limited to the Mosaic-owned artifact(s), currently `/usr/bin/swayfx-mosaic`.

## Patch export

The development tree contains the full source because compositor work is easier there. The distributable delta lives under `patches/`.

Use the project tooling to regenerate the patch after source changes, then verify:

```sh
git apply --check patches/0001-mosaic-layout-viewport.patch
```

The patch must correspond to the pinned upstream commit used by `PKGBUILD`.

## Arch package

```sh
makepkg --printsrcinfo
makepkg --verifysource
```

A full package build is expected before a release, not necessarily after every edit.

The package must not:
- replace `swayfx`;
- conflict with `swayfx`;
- provide `sway`;
- install `/usr/bin/sway`;
- install the user's QuickShell configuration or personal dotfiles.

## Updating upstream

When SwayFX publishes a new version:

1. fetch `upstream`;
2. inspect relevant compositor changes;
3. create a dedicated rebase/update branch;
4. update the pinned source revision;
5. reapply or rewrite the Mosaic patch;
6. build the new upstream baseline;
7. build Mosaic;
8. run model/headless tests;
9. test standard Sway layouts;
10. only then bump the Mosaic package version.

If the patch does not apply cleanly, stop and adapt it manually.

## Daily-session integration

The final package is intentionally independent from the user's desktop configuration.

The user's dotfiles may launch `swayfx-mosaic` in a dedicated session and bind:

```text
Super+Alt+M → Applications
Super+Alt+L → layout toggle mosaic
```

Those bindings are not packaged here.
