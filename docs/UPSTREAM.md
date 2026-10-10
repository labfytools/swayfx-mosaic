# Upstream relationship

SwayFX Mosaic is intentionally maintained as a small feature delta above SwayFX.

## Initial base

- Project: SwayFX
- Upstream: https://github.com/WillPower3309/swayfx
- Tag: `0.6`
- Commit: `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`
- Sway base reported by SwayFX: 1.12.0
- wlroots ABI used by this base: 0.20
- SceneFX ABI used by this base: 0.5

The original local Arch package was `swayfx 0.6-1`. Its exact build-source commit could not be reconstructed, so the signed/verifiable project base is the public upstream 0.6 tag commit rather than a claim of byte-for-byte equivalence with that package.

## Remote policy

Local development uses:

```text
upstream → SwayFX upstream
origin   → Forgejo canonical repository
github   → GitHub mirror
```

Only the project remotes receive Mosaic commits.

Do not push Mosaic branches to `upstream`.

## Version policy

Mosaic versions follow the SwayFX base explicitly.

Example:

```text
swayfx 0.6
swayfx-mosaic 0.6+mosaic.1
```

A future SwayFX 0.7 does not automatically imply a working Mosaic 0.7 package. The patch must be rebased and validated first.

## Why a separate binary?

SwayFX does not expose a stable runtime plugin ABI for injecting a new layout. Mosaic therefore cannot be shipped as a small external `.so` while leaving the running `/usr/bin/sway` binary unchanged.

The package instead builds the compositor with the Mosaic delta but installs it under a different executable name.

This preserves the operational requirement that ordinary SwayFX can continue to update and remain a safe fallback.
