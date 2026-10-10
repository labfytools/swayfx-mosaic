# Upstream maintenance

SwayFX Mosaic is an independent derivative of [SwayFX](https://github.com/WillPower3309/swayfx), which is based on [Sway](https://github.com/swaywm/sway). It is not endorsed by either project's maintainers. Preserve their license and attribution; see [LICENSE](../LICENSE) and [NOTICE](../NOTICE.md).

## Pinned source base

| Item | Current value |
| --- | --- |
| SwayFX tag | `0.6` |
| Upstream commit | `fd71a6bdc061bd633b488ae7b83e8a6981d22f86` |
| Reported Sway base | 1.12.0 |
| wlroots series | 0.20 |
| SceneFX series | 0.5 |

The historical locally installed Arch package was `swayfx 0.6-1`, but its exact source revision could not be reconstructed from available package metadata. The public SwayFX 0.6 tag is the verifiable project base; do not claim byte-for-byte equivalence with that older package.

## Remote policy and history

`origin` is the canonical Forgejo project; `github` is the public mirror; `upstream` is SwayFX and is **fetch only**. No Mosaic branch or commit is pushed to SwayFX upstream. The project's `main` has clean public project history rooted in the imported SwayFX 0.6 base. The upstream remote remains an external source of new releases, not a project publication target.

## Delta and versioning

The maintained production delta is `patches/0001-mosaic-layout-viewport.patch` on the pinned source commit. The package builds the full compositor because SwayFX has no stable external layout plugin ABI, then installs a distinct binary. Example versions are `swayfx 0.6` and `swayfx-mosaic 0.6+mosaic.1`. A SwayFX `0.7` release does not automatically validate a Mosaic `0.7` package.

## Forward-port procedure

1. Fetch upstream; inspect the release tag, commit, relevant source changes, and dependency versions.
2. Open a dedicated update branch and document changed architecture/UX/package assumptions before implementation.
3. Build the pristine upstream baseline at the candidate commit.
4. Rebase or manually forward-port the Mosaic patch. On conflict, inspect both implementations and adapt the delta deliberately; never force automatic patch application or accept rejected hunks.
5. Review exported patch scope; update pinned commit, package version, and checksums together.
6. Build Mosaic, run model and headless compositor tests, verify standard layouts, IPC, rendering, and package staging/file ownership.
7. Update [known limitations](KNOWN_LIMITATIONS.md), [roadmap](ROADMAP.md), and release notes with the observed result.

A failed patch check or changed compositor contract blocks that candidate release until resolved. It does not justify modifying the ordinary SwayFX package or using an ABI-incompatible binary workaround. The normal SwayFX package must remain independently updatable.
