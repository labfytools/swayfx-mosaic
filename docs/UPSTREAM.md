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

## Approved private STEP20C static candidate — 2026-10-13

The user approved four decisions for documentation and private prototypes only:
private static SceneFX; separate complete notices under
`/usr/share/licenses/swayfx-mosaic/`; project responsibility for embedded
SceneFX maintenance; and qualification of each exact SceneFX/wlroots pair.
See the [decision register and bounded runtime gate](design/STEP20C_STATIC_RUNTIME_AND_PACKAGE_CONTRACT.md).
The current PKGBUILD, system SceneFX dependency, one-binary package, production
sources and cumulative patch remain unchanged. The future private stage may
contain only `/usr/bin/swayfx-mosaic` and justified regular notice files below
the license directory. No private shared library, session, service, config or
Sway symlink is allowed. No real installation is authorized.

Mosaic owns monitoring, impact review, rebuild and requalification of embedded
SceneFX fixes, including renderer/shaders/dependencies/ABI/buffer lifetime/clip/
damage changes. Before public distribution, a release maintainer and security
reviewer must be designated; no names or SLA are assigned. Preserve exact source,
patch, compiler/options/dependency, notice, test and artifact manifests.
A new relevant dependency build requires header/symbol/shared-layout inspection,
rebuild, relocation/model/staging/headless checks and graphical requalification
of relevant paths, then a separate publication decision. No automatic update
subsystem is added. Ordinary SwayFX upgrades remain independent and standard
SwayFX remains the fallback. All other pairs are NOT QUALIFIED.

These decisions do not settle popup UX or close STEP20C production gates.
STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT; STEP20D–G PLANNED.
Production multi-output remains NOT YET SUPPORTED.

## Overnight private maintenance evidence

The [annotated reconstruction report](design/STEP20C_ANNOTATED_REBUILD_AND_PRIVATE_STAGE.md)
qualifies only the exact private SceneFX 0.5 source and shared wlroots 0.20.2
build recorded there. Local header/layout/symbol/relocation checks establish no
future semantic ABI guarantee. Any relevant source or dependency build change
requires impact review, rebuild and fresh qualification of the new binary;
no previous SHA's graphics results are inherited. Release and security roles
remain unnamed, and no SLA is established. Future recipe and notices remain
PARTIALLY_FEASIBLE: syntax/input correspondence passed, complete makepkg and
human legal/distribution review remain open. The [decision draft](design/STEP20C_PRODUCTION_INTEGRATION_DECISION_DRAFT.md)
records proposed monitoring, requalification and rollback without adopting a
production integration or changing normal SwayFX upgrade independence.
