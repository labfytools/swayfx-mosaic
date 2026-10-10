# Contributing

SwayFX Mosaic is an experimental native layout. Keep contributions within Mosaic behavior, its validation, documentation, patch maintenance, and isolated packaging. Unrelated SwayFX customization, personal dotfiles, QuickShell UI, and desktop themes are outside this repository's current scope.

## Contribution flow

1. Read the [documentation index](docs/README.md), [architecture](docs/ARCHITECTURE.md), and [known limitations](docs/KNOWN_LIMITATIONS.md).
2. Document a user-visible change in [UX](docs/UX.md) and an architecture change in [Architecture](docs/ARCHITECTURE.md) **before** implementation. Packaging changes update [Packaging](docs/PACKAGING.md); upstream changes update [Upstream](docs/UPSTREAM.md).
3. Keep the source delta focused on Mosaic and preserve real Sway containers, standard layouts, and package coexistence.
4. Add tests that exercise changed production behavior. Run the relevant build, Meson tests, headless compositor tests, and `git diff --check` as described in [Development](docs/DEVELOPMENT.md).
5. Report failed tests and unresolved limitations plainly. Never hide a failure or force-apply a patch to a new upstream revision.
6. Submit a reviewable change with its contract, validation evidence, and scope. The [Forgejo repository](https://git.labfytools.com/fy59/swayfx-mosaic) is canonical; GitHub is a public mirror.

Do not install over `/usr/bin/sway` or make `swayfx-mosaic` conflict with ordinary SwayFX.
