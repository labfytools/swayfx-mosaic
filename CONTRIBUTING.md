# Contributing

SwayFX Mosaic is experimental compositor work. Changes should stay narrowly focused on the Mosaic / Spatial Canvas layout and its packaging/tests.

## Before changing code

Read:
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/DEVELOPMENT.md`
- `docs/UPSTREAM.md`

## Scope

Appropriate contributions include:
- Mosaic layout model;
- geometry, viewport and scene behavior;
- focus/input behavior required by Mosaic;
- IPC additions required to expose Mosaic state;
- Mosaic tests;
- patch maintenance and packaging.

Desktop shell features, themes, personal key bindings and unrelated SwayFX customizations belong elsewhere.

## Required checks

At minimum:

```sh
meson compile -C build-mosaic -j 8
meson test -C build-mosaic --print-errorlogs
python tests/headless-ipc.py
git diff --check
```

For upstream rebases, also rebuild the pristine baseline and validate the standard Sway layouts.

## Compatibility

Do not introduce a package conflict with ordinary `swayfx`.

Do not install over `/usr/bin/sway`.

Do not treat QuickShell or an external daemon as the authoritative Mosaic state store.

## Commits

Keep commits reviewable and explain:
- the compositor invariant being changed;
- why the change belongs in Mosaic;
- the validation performed;
- any known limitation.

Never hide failed tests or force-apply the Mosaic patch to an unvalidated upstream revision.
