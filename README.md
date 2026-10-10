# SwayFX Mosaic

**SwayFX Mosaic** is an experimental SwayFX variant that adds a native **Mosaic / Spatial Canvas** tiling layout.

The goal is not to replace SwayFX, reimplement tiling in userspace, or turn the desktop into a floating-window canvas. Mosaic stays inside the compositor and keeps real Sway containers, workspaces, IPC, fullscreen, floating windows and scratchpad semantics.

> Status: active development. The compositor is not installed as the daily SwayFX session yet.

## Why Mosaic?

Classic tiling is constrained by the physical viewport. Mosaic introduces a logical canvas made of horizontal rows that may extend beyond the visible output.

```text
Workspace
└── Mosaic Canvas
    ├── Row 0: [A][B][C][D]...
    ├── Row 1: [E][F][G]...
    └── ...
```

Each row owns its viewport position and last focused container. The compositor remains the source of truth for order, geometry, focus and scrolling.

## Core rules

- real tiled Sway containers; no floating-window simulation;
- Mosaic is opt-in per workspace;
- standard Sway/SwayFX layouts remain available;
- workspaces continue to exist normally;
- Mosaic state lives in the compositor, not in QuickShell;
- the standard `swayfx` package must remain untouched and independently updatable;
- the Mosaic package installs a separate `/usr/bin/swayfx-mosaic` binary;
- our production artifact is a minimal, reviewable patch on a pinned SwayFX upstream revision.

## Package model

```text
swayfx
└── /usr/bin/sway

swayfx-mosaic
└── /usr/bin/swayfx-mosaic
```

`swayfx-mosaic` must not declare `provides`, `conflicts` or `replaces` against SwayFX. An upstream SwayFX update must never be blocked by this project.

The Arch packaging path is intentionally patch-based:

```text
pinned SwayFX upstream
        +
Mosaic patch set
        ↓
/usr/bin/swayfx-mosaic
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/UPSTREAM.md](docs/UPSTREAM.md).

## Layout switching

The target desktop contract is:

```text
Super + Alt + M  → Applications
Super + Alt + L  → Standard layout ↔ Mosaic
```

The compositor command is:

```text
layout toggle mosaic
```

Each workspace remembers its previous standard layout, so a toggle behaves conceptually like:

```text
tabbed → mosaic → tabbed
splith → mosaic → splith
```

The key binding itself belongs to the user's dotfiles, not to this package.

## Current implementation

The current development tree contains the native Mosaic foundation and the first single-row viewport work:

- native `L_MOSAIC` layout;
- workspace-local Mosaic state;
- ordered Row 0 backed by real `workspace->tiling` containers;
- insertion after the active container;
- workspace-local previous-layout memory;
- `layout toggle mosaic`;
- logical `scroll_x`;
- first scene translation / single-row viewport implementation;
- IPC exposure through `get_tree`;
- model and headless compositor tests;
- Arch package staging limited to `swayfx-mosaic`.

Multi-row behavior, robust multi-output clipping, final sizing policy, camera animation and session restore integration are still development work.

Technical reports:
- [STEP20A — native foundation](docs/STEP20A.md)
- [STEP20B — first scrollable row](docs/STEP20B.md)

## Development

Baseline:

```sh
meson setup build-baseline -Dwerror=false -Dsd-bus-provider=libsystemd
meson compile -C build-baseline
```

Mosaic build:

```sh
meson setup build-mosaic \
  -Dwerror=false \
  -Dsd-bus-provider=libsystemd \
  -Dmosaic-package=true \
  -Dprefix=/usr -Dbindir=bin \
  -Dswaybar=false -Dswaynag=false \
  -Dman-pages=disabled -Ddefault-wallpaper=false

meson compile -C build-mosaic
meson test -C build-mosaic --print-errorlogs
python tests/headless-ipc.py
```

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for the full workflow.

## Repository layout

```text
docs/       design, roadmap and validation reports
patches/    production delta against pinned SwayFX
tests/      Mosaic model and headless compositor tests
tooling/    patch/export maintenance helpers
PKGBUILD    coexistence-oriented Arch package
```

The full SwayFX source remains in the development tree for compositor work. The patch set is the reviewable production delta.

## Upstream and license

SwayFX Mosaic is derived from [SwayFX](https://github.com/WillPower3309/swayfx), itself based on [Sway](https://github.com/swaywm/sway).

Current base:
- SwayFX tag `0.6`;
- commit `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`;
- Sway 1.12.0 base;
- wlroots 0.20 series;
- SceneFX 0.5 series.

The project keeps the upstream MIT license. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).

## Mirrors

Canonical development repository:
- Forgejo: `https://git.labfytools.com/fy59/swayfx-mosaic`

Public mirror:
- GitHub: `https://github.com/labfytools/swayfx-mosaic`
