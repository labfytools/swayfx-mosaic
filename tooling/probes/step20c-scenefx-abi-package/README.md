# SceneFX ABI/package audit fixture

**EXPERIMENTAL / PRESERVED EVIDENCE / no production integration.**
Read the [protocol](../../../docs/design/STEP20C_SCENEFX_ABI_PACKAGE_FEASIBILITY.md).
Private sources/builds/results must stay outside Git. No script may launch a
compositor, use desktop IPC, install system files or change package contracts.
Budgets: one stock reconstruction/stage, one private shared chain, optionally
one static chain after source inspection. ELF checks are diagnostics only.
Generated artifacts and manifests stay in LAB.

## Build-only reproduction

Use a full Mosaic clone containing the fixed commits, installed stock build
prerequisites and local Git object stores containing pinned SceneFX and wlroots.
`prepare.py` does not fetch or install missing dependencies. It archives exact
objects, applies retained private patches in new copies, and logs each bounded
build command. Create a new LAB under your home directory, outside this clone.
A LAB can be prepared only once; a failed preparation consumes that attempt.
Do not bypass the ticket's build budget with another directory.

```sh
python tooling/probes/step20c-scenefx-abi-package/prepare.py LAB \
  --scenefx-git /path/to/scenefx-object-store \
  --wlroots-git /path/to/wlroots-object-store --static
python tooling/probes/step20c-scenefx-abi-package/audit.py LAB
python tooling/probes/step20c-scenefx-abi-package/summarize.py LAB
```

`--static` is optional and requires the source-audit decision documented in
this ticket. `--pristine-binary` optionally accepts only the A campaign's
SHA-256-qualified retained pristine executable; otherwise its ELF comparison
is NOT TESTED. A newly reproduced baseline binary needs its own provenance
qualification, not substitution under that historical identity.
The retained completed LAB is `/home/fy59/swayfx-mosaic-abi-package-tp22xfwm`.
Its optional static trial was exercised once; no new run/build is authorized
by these instructions for this completed ticket.

`audit.py` checks complete stage entries including symlinks, recipe digests,
ELF headers/symbols/version requirements, loader paths and relocations, public
header differences, C17 struct-layout observers and compiler dependencies.
It runs only diagnostic loader modes and small non-graphical layout/version
observers. It never runs a compositor entry point. `ldd -r` diagnostics are
checked even when its status is zero. Its stock-versus-private process library
paths are temporary and recorded. Required tools: cc, Meson/Ninja, pkg-config,
readelf, nm, objdump, the native x86-64 glibc loader, ldd and read-only Arch
package metadata (`pacman -Qi`; no package installation). Other platforms are
NOT TESTED, rather than silently inferred compatible.

`summarize.py` records measured
S0/S1 results separately from inferred architectural options. Static loader
success does not establish graphics, semantic ABI, future updates or licensing
clearance. All generated JSON/logs/source archives/builds remain in LAB.

## Completed result

Current package: **CURRENT_PACKAGE_STAGE_PASS**, exactly one regular ELF
`/usr/bin/swayfx-mosaic`, stock dynamic dependencies, no clip references.
Shared private binary with stock SceneFX: **INCOMPATIBLE_WITH_STOCK_SCENEFX**,
two missing strong clip symbols despite the common SONAME. Shared private
resolution and static embedding pass non-graphical build/model/loader checks.
Seventeen layouts and six selected offsets match; 85 exports overlap wlroots.
Stock/private/static wlroots scene bindings are retained, including the mix
between SceneFX providers and wlroots helpers. Distinct private SONAME,
future-version safety, GPU lifetimes and graphical behavior are NOT TESTED.

Overall **PARTIALLY_FEASIBLE**; architecture
**SCENEFX_ABI_PACKAGE_REQUIRES_ARCHITECTURAL_DECISION**. No packaging option is
adopted. The historical campaign is closed; STEP20C NEXT and production multi-output
NOT YET SUPPORTED. `seal.py LAB` refuses existing manifests; `seal.py LAB
--verify` verifies all entries without regenerating. Derive all evidence and
finalize fixtures before sealing. Report and complete diff are captured outside
the sealed inventory to avoid self-referential digest dependencies.

## ABI evidence freeze

The October 2026 freeze verifies the original 1,463 source entries and 204
evidence entries without rerunning the campaign. Their manifest hashes remain
`a27fa33d57d3423e09f02430f04cfed643762d876099b7f88489229115c4a1e5` and
`86f7654c8ad962053644ce2c4c13eb9f026d6618b171e0cc3a8fc3034eb380d5`.
This README's publication wording changed after verification. To verify the
sealed historical source manifest subsequently, map only its README entry to
the exact pre-freeze snapshot recorded in the report. Do not regenerate the
manifest or substitute other source files. Python fixture bytes are unchanged.
The old report's A/B labels refer to its earlier ticket, not the new static
distribution-contract phase. That later phase must remain local.
