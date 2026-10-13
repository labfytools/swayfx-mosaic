# STEP20C SceneFX / wlroots ABI and package feasibility

**EXPERIMENTAL — PRESERVED HISTORICAL EVIDENCE.**
Protocol recorded before builds. A freeze gate passed at
`7c22b4020edc2d9ab6779d789159937523aae75a` on local, Forgejo and GitHub,
with a clean worktree. STEP20A DONE, STEP20B EXPERIMENTAL, STEP20C NEXT,
STEP20D–G PLANNED; production multi-output NOT YET SUPPORTED.

## Authority and problem

[Packaging](../PACKAGING.md) remains authoritative: exactly one installed
file `/usr/bin/swayfx-mosaic`, no Sway replacement, library overwrite,
conflicts/provides/replaces, personal configuration or service.
The current production patch has no STEP20C clip dependency. The private
SceneFX adds `wlr_scene_tree_set_clip` and `wlr_scene_tree_get_clip` while
retaining the stock SONAME. A shared SONAME does not supply missing symbols.
No strategy is preapproved; conclusions are evidence, not integration authority.

## Pinned sources and comparison

SwayFX 0.6 `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`; private Mosaic
`cd550382b311efdbfe3ed892f4e1d281d852e754`; SceneFX 0.5
`37ccd723bef49e6891156ffafce8f549f01446cc`; wlroots 0.20.2
`d783533489e1f75d6886c2ab5c5960090ef268f8`.
Compare installed SceneFX, rebuilt pristine/private SceneFX, retained pristine
SwayFX, freshly reconstructed production Mosaic and rebuilt private Mosaic.
Preserve ELF headers/dynamic tags, defined/undefined/versioned symbols,
pkg-config flags/features, actual compiler headers and loader resolution.
Compare all public SceneFX headers and public struct size/alignment/offsets
where relevant. Audit the sidecar lifetime and wlroots shared structures.
Installed package versions alone never prove exact source provenance or ABI.

## Budget and isolation

One stock production reconstruction, one DESTDIR staging, one private
SceneFX/Mosaic shared build chain. One optional static SceneFX/Mosaic build
only after source audit establishes a bounded Meson method. No compositor
launch, graphics, system install, package creation, algorithm or UX change.
All source/build/stage/raw evidence stays in a home-directory LAB outside Git.
No inherited session sockets, global library path or loader configuration.
Loader diagnostics use `ld-linux --list` or `ldd -r` on trusted private
artifacts only; these are not compositor execution or graphics tests.
Stop implementing any option needing a public ABI, package-contract change,
new package or architecture migration; record the required future decision.

## Scenarios and decision criteria

S0: apply the unchanged cumulative patch on pinned pristine, prove source
equivalence and PKGBUILD checksums, compile with stock dependencies, run only
Meson model tests, stage once and inspect the complete manifest.
S1: private binary with private versus stock SceneFX; inspect required clip
symbols, same SONAME, RUNPATH/RPATH, transitive needs and missing relocations.
S2: compare upstream API, private static embedding, isolated distinct-SONAME
shared library, and an architecture without a new SceneFX API. Prioritize
standard SwayFX coexistence, independent updates, explicit ownership, security
maintenance, symbol interposition, licenses and versioned wlroots constraints.

FEASIBLE requires S0 staging plus characterized incompatibilities and a
sufficiently demonstrated candidate without identified ABI risk in the matrix.
PARTIALLY_FEASIBLE retains technical/contract/decision gates. INCONCLUSIVE
means insufficient reliable comparison. BLOCKED requires an established
coexistence violation, not the expected missing private functions in stock.
Architecture conclusion remains UNDECIDED until evidence is assessed.

## Limits

No graphical, GPU lifetime/cache, all-frame, rotated/scaled/migrated output,
installation, update or rollback test. Those are NOT TESTED. The optimized
edge property remains a separate shared rendering limitation; native FBO
causality remains unproved. No stock-package provenance assertion beyond
available metadata/source comparison. All optional strategies require a new
explicit integration decision before production work.

## Completed non-graphical audit (2026-10-13)

`SWAYFX_MOSAIC_SCENEFX_ABI_PACKAGE_PROBE=PARTIALLY_FEASIBLE`

Architecture: **SCENEFX_ABI_PACKAGE_REQUIRES_ARCHITECTURAL_DECISION**.
No production strategy is selected. The current package passes its separate
stock build/stage gate. The naive experimental/stock-library combination is
INCOMPATIBLE_WITH_STOCK_SCENEFX. Static embedding is technically demonstrated
but retains interposition, shared-wlroots, security and notice gates.

LAB: `/home/fy59/swayfx-mosaic-abi-package-tp22xfwm/`.
Raw commands/stdout/stderr/return codes are in `raw/`; derived evidence is
in `results/`. All build artifacts remain external to Git. Sources are fresh
archives of verified fixed Git objects, not copies of dirty historical source
trees. SceneFX and wlroots object stores were read-only inputs. The pristine
SwayFX executable is explicitly reused from the sealed A laboratory, with
SHA-256 checked against A's identity; it was not rebuilt or launched.

## Installed dependencies and source identity

Installed package metadata: SceneFX `0.5-1`, wlroots0.20 `0.20.2-1`, SwayFX
`0.6-1`. pkg-config reports SceneFX **0.5.0** as `scenefx-0.5`, wlroots
**0.20.2** as `wlroots-0.20`; generated installed headers and a tiny observer
calling native `wlr_version_get_*` agree on runtime wlroots 0.20.2.
The `.pc` files reside in `/usr/lib/pkgconfig`, with include roots
`/usr/include/scenefx-0.5` and `/usr/include/wlroots-0.20`.
All ten queried wlroots build features are true: DRM, X11, libinput, Xwayland,
GLES2, Vulkan, GBM, udmabuf, session and color management.

The 121 non-generated installed wlroots headers exactly match the pinned
0.20.2 source archive. Installed generated config/version headers are retained
separately. No wlroots source was patched. Header equality and runtime version
do not recover the complete distro binary build provenance, patch set or flags;
that exact provenance remains **NOT ESTABLISHED**. Other 0.20 builds and future
updates are **NOT TESTED**. Compiler dependency output and Meson compile
commands/dependencies record the actual headers and library paths used, rather
than relying only on declared package versions.

## S0: unchanged current production package

`PKGBUILD` remains byte-identical to A. Version `0.6+mosaic.1-1`, x86_64,
MIT, SwayFX fixed Git pin, no conflicts/provides/replaces.
Depends: cairo, gdk-pixbuf2, libevdev, libinput, json-c, systemd-libs, wayland,
libxcb, libxkbcommon, pango, pcre2, scenefx, ttf-font, wlroots0.20.
Makedepends: git, meson, ninja, pkgconf, python, wayland-protocols, libdrm, pixman.
Checkdepends: kitty, grim. The declared graphical check was deliberately not
executed; this ticket forbids compositor launches. `makepkg --printsrcinfo`
passed; no package build/install command or dependency installation was used.

Checksums recomputed without changing the recipe:

| Input | Expected and actual SHA-256 | Result |
| --- | --- | --- |
| cumulative production patch | `a04cd06a6ef4fc58e3b40333a53226849e82d9a4757b9ccee58ad7b59a23ff4b` | PASS |
| headless IPC source | `0a16c887ca6a87f0392c2eef498b4fad78b9f32afaf7d2a6c0e5e0e37c3c1744` | PASS |
| upstream Git source | recipe SKIP plus exact commit check/archive | PASS pinned source; no archive checksum invented |

The cumulative patch passed forward application on a pristine archive of
`fd71a6bdc061bd633b488ae7b83e8a6981d22f86`. Full source equivalence passed
for include/, sway/, meson.build, meson_options.txt and tests/mosaic-model.c.
The build used the recipe's Meson package flags, prefix `/usr`, bindir `bin`,
stock SceneFX and wlroots, `-j 8`. Meson mosaic-model passed 1/1.

Exactly one `meson install --destdir LAB/stage-current --no-rebuild` ran.
Complete non-directory manifest (including symlinks):

```text
/usr/bin/swayfx-mosaic
```

**CURRENT_PACKAGE_STAGE_PASS**. One regular executable ELF64 x86-64, no
symlinks, second binary, library, config, dotfile, service or session file.
The staged binary has no clip references, no RPATH or RUNPATH; its SceneFX
and wlroots references resolve against `/usr/lib`, with no missing relocations.
This qualifies only S0 in the measured build/loader/stage matrix. It is not
a full Arch release package, graphical test, or STEP20C qualification.

## ELF comparison

All compared objects are ELF64 x86-64. Every ELF header, dynamic table, dynamic
symbol table, version table, nm listing and objdump output is retained.

| Object | SONAME or SceneFX dependency | Clip symbols | RPATH / RUNPATH |
| --- | --- | --- | --- |
| installed SceneFX | `libscenefx-0.5.so` | neither defined | absent |
| rebuilt pristine SceneFX | same | neither defined | absent |
| rebuilt private SceneFX | same | both defined | absent |
| retained pristine SwayFX | DT_NEEDED `libscenefx-0.5.so` | neither required | historical pristine build RUNPATH retained |
| staged current Mosaic | DT_NEEDED `libscenefx-0.5.so` | neither required | absent |
| shared experimental Mosaic | DT_NEEDED `libscenefx-0.5.so` | both strong undefined | new private SceneFX build RUNPATH |
| static experimental Mosaic | no SceneFX DT_NEEDED | both present in ordinary symbol table | absent |
| installed wlroots | `libwlroots-0.20.so` | neither defined | absent |

Exact artifact digests and sizes:

| Object | Bytes | SHA-256 |
| --- | ---: | --- |
| stock-binary-elf | 6312256 | `479c55bdbf2cc10e72f4ed8633fc7287d15358ed3f451dd2e6bb350671985af0` |
| experimental-binary-elf | 6324344 | `058e51366a71f54ff7824f9a166e3d5cd6797c14f39968ba03587c30bb07bb05` |
| static-binary-elf | 6760600 | `ccd47ce5b74c132e19bcd46d022a80e90e8a944acc3db521a89427ee7913c614` |
| system-scenefx-symbols | 182216 | `63586ffbe268c6830b5782d5327e8ca3624dbd9b9c9b0e93e591e94ca28a6e62` |
| pristine-scenefx-symbols | 493216 | `4e342bbd832ae6e6cfb62938af5bf1fb6b46d30ec50c8b4eea50b652892af19e` |
| private-scenefx-symbols | 504792 | `b9582b6c7dd2f903f6de740534f71356261f3e0b84143a24f666f64575b1d91c` |
| system-wlroots-elf | 1378496 | `7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837` |
| pristine-sway-elf | 6297064 | `8ac865481bc0487344210cd0e16d8e6c7655b29db887cd58ddc11b0ca22fe494` |

Installed and rebuilt pristine SceneFX have exactly the same exported symbol
set. Private SceneFX adds precisely `wlr_scene_tree_set_clip` and
`wlr_scene_tree_get_clip`; no stock export is removed. The new functions are
unversioned. ELF version requirements for dependency symbols are retained;
there is no versioned clip API contract. A common SONAME selects a library
identity for DT_NEEDED; it is not evidence that this library implements every
undefined function required by the consumer.

## S1: actual runtime search and relocations

`ld-linux-x86-64.so.2 --list` inspected library selection without running
application main. `ldd -r` on these trusted generated executables checked
relocations; return code alone is insufficient because missing-symbol
diagnostics can be emitted with status zero. The audit explicitly checks
stdout for missing symbols. No command launched the compositor.

| Consumer / provider | Selected library | Result |
| --- | --- | --- |
| current staged Mosaic / default | `/usr/lib/libscenefx-0.5.so` | PASS selection/relocations |
| experimental / default | LAB/scene-private-build/libscenefx-0.5.so via build RUNPATH | PASS selection/relocations only |
| experimental / private process path | same private library | PASS selection/relocations only |
| same experimental / stock process path | `/usr/lib/libscenefx-0.5.so` | two missing strong symbols |
| static experimental / default | no SceneFX loaded; stock wlroots still loaded | PASS selection/relocations only |

The stock counterfactual uses the loader's process-local `--library-path
/usr/lib` and a separately recorded `LD_LIBRARY_PATH=/usr/lib` only for
`ldd -r`. DT_RUNPATH is overridden in this tested setup. No global environment
was modified. Build RUNPATH is an absolute temporary path and is not a
distribution policy. Moving/removing that private library can expose the
stock fallback and its missing functions. No universal loader claim follows
for preload, secure execution, another RUNPATH or a changed library graph.
The documented search semantics are in [ld.so](https://man7.org/linux/man-pages/man8/ld.so.8.html).

## Public headers, structures and lifetime

All seven installed public SceneFX headers match pristine source bytes. The
private difference is only two declarations in types/wlr_scene.h. All
existing typedefs, enums, callbacks, public struct members and ownership
comments in these headers remain byte-identical. Private instrumentation
headers are internal, not installed public API. No wlroots header is changed.

C17 `-Wall -Wextra -Werror` observers report identical size/alignment for 17
SceneFX/wlroots structs in stock/pristine/private configurations, plus six
selected member offsets. Examples: scene_node 112/8, scene_tree 128/8, scene
304/8, scene_buffer 472/8, scene_output 344/8, wlr_output 624/8, output_state
208/8, surface 968/8. Full results are in struct-abi-audit.json. This is a
measured layout subset; complete semantic ABI compatibility is not proven.

The retained working patch stores clips in a file-local linked sidecar list
in types/scene/wlr_scene.c. Each record holds a tree pointer, copied wlr_box
and destroy listener; clearing or node destruction removes the listener and
frees the record. Set copies a tree-local rectangle, NULL clears, nonnegative
dimensions are asserted; get copies or returns false. No clip field is added
to a public struct. Linear lookup, unchecked coordinate addition and silent
allocation failure remain private-prototype production design gates. This
ticket does not repair them or freeze these API semantics.

The historical first discarded candidate added a public tree field and
crashed; the [spike report](STEP20C_SCENEFX_CLIPPING_SPIKE.md) retains that
separate evidence. It must not be conflated with the preserved sidecar patch.
No additional current ABI failure beyond the two absent stock functions was
demonstrated in this non-graphical matrix. That is not proof of absence of
semantic, allocation, concurrency, GPU or future-version defects.

## Transitive dependencies and symbol ownership

SceneFX stock/pristine/private share the same direct dependency list:
wlroots, wayland-server, libm, libdrm, pixman, EGL, GBM, GLESv2, lcms2 and
libc. wlroots additionally depends on Vulkan, libinput, libseat, libudev,
display-info, liftoff, Wayland client and XCB components, among others.
All DT_NEEDED entries and recursive loader paths are retained; 72 resolved
system-library paths map to 50 installed package metadata/license records.
No library package was installed.

SceneFX and wlroots define **85 common dynamic symbols**, including scene,
EGL, matrix and color functions. This overlap already exists with stock
SceneFX and does not by itself demonstrate a new clipping regression.
Controlled `LD_DEBUG=bindings` with relocation tracing shows 34 wlroots
scene bindings in each stock/private/static case: 31 go to SceneFX (or the
static executable), three remain in wlroots. Thus distinct SONAME or static
embedding alone does not isolate the process-wide symbol namespace.
The complete binding records distinguish actual provider from matching names.
A future design must preserve all shared-struct and function semantics across
this graph; hiding/renaming every symbol blindly could break wlroots's scene
helper integration. No symbol renaming or visibility experiment is authorized
or performed here.

## S2: static feasibility and license constraints

The pinned [SceneFX Meson target](https://github.com/wlrfx/scenefx/blob/37ccd723bef49e6891156ffafce8f549f01446cc/meson.build)
is a native library() honoring `default_library=static`. One private static
SceneFX build and one Mosaic link use its uninstalled pkg-config file; no
production Meson edit is needed for this laboratory demonstration.

The static executable is 6,760,600 bytes versus shared experimental 6,324,344
(+436,256 bytes, about 6.90%, both unstripped local builds). It contains both
clip implementations as ordinary `T` symbols, not new dynamic exports.
DT_NEEDED no longer names SceneFX; EGL/GBM/GLESv2/lcms2 are direct dependencies
instead. wlroots remains dynamic, and 85 common exports remain observable.
Model and loader checks pass. There is no second staging, strip, package build
or graphical run; the one-file ELF shape is demonstrated, a static release
package is **NOT TESTED**.

SwayFX, pinned SceneFX and wlroots use MIT notices. The source license texts
and transitive package license metadata are retained. Static copying requires
preservation of copyright/permission notices, per the
[SceneFX license](https://github.com/wlrfx/scenefx/blob/37ccd723bef49e6891156ffafce8f549f01446cc/LICENSE).
A separately installed notice would expand the current exact-one-file manifest.
An embedded notice strategy is possible in principle but **NOT TESTED** and
requires explicit packaging/legal review; this audit asserts no blanket legal
clearance. Embedded SceneFX security fixes require Mosaic rebuilds and an
identified maintenance owner. Static embedding does not freeze shared wlroots
or make future system updates ABI-safe.

## Comparative architecture matrix

| Criterion | A: upstream clipping API | B: static private SceneFX | C: distinct private shared library | D: no new SceneFX API |
| --- | --- | --- | --- | --- |
| Technical evidence | prototype only; acceptance unknown | build/model/relocations PASS | private lookup PASS; distinct identity NOT TESTED | architecture unknown |
| System libraries intact | normal upstream update only | yes | yes if isolated | yes |
| /usr/bin/sway intact | yes | yes | yes | yes |
| Coexistence | supported upstream version required | file ownership preserved; symbol/version qualification pending | extra file and complete lookup/binding contract required | unproved implementation |
| Stable clip API | absent today | private | private | no new API, mechanism unproved |
| ABI | future release unestablished | measured layouts/relocations pass; semantic/future ABI unestablished | same SONAME naive stock incompatible; isolated design unestablished | unestablished |
| Exactly one package file | possible after adoption | ELF shape demonstrated; notices/stage pending | no | possible, not demonstrated |
| Upgrade risk | medium shared-version transition | high until wlroots/security policy | medium/high; shared wlroots persists | unknown |
| SceneFX maintenance | upstream if accepted | Mosaic embedded-code owner needed | private-library owner needed | stock upstream; alternate mechanism owned by Mosaic |
| wlroots maintenance | qualified version pair | shared 0.20 ABI/interposition | shared 0.20 ABI/interposition | stock APIs plus larger Mosaic implementation |
| Reproducibility | fixed prototype inputs only | commands/sources retained, bit identity untested | laboratory lookup only | not tested |
| Human decision | yes, no submission approved | yes, bundling/security/license contract | yes, new file/SONAME/package ownership | yes, new architecture |

A is the conditional long-term maintenance direction: one maintained generic
primitive rather than perpetual private API patches. It needs maintainer
agreement, an ownership/error/bounds contract, version policy and closure of
remaining graphical gates. No upstream contact/submission occurred and no
acceptance is presumed.
B is the most concretely demonstrated candidate that avoids owning a second
SceneFX file and removes dependency on the system SceneFX's clip symbols. It
does not yet establish safe independent wlroots upgrades or a distributable
one-file notice strategy. C separates filesystem ownership and library identity
but requires a packaging decision and still shares a symbol namespace.
D cannot be called viable: surface crops/output scissor alone do not establish
popup-owner rendering, topmost hit traversal, damage, effects, saved buffers,
scale/rotation/migration or applied transaction consistency. No alternate
clipping engine is developed.

## Upgrade and hypothetical rollback

S0 can coexist by file ownership with standard SwayFX. No recipe conflict or
replacement blocks its updates. That does not guarantee an old Mosaic binary
will load after every shared SceneFX/wlroots upgrade. Requalify and rebuild
Mosaic separately; do not pin or replace system libraries to force it to work.
Static SceneFX makes Mosaic independent of system SceneFX updates, but an
embedded security fix requires its own rebuild and shared wlroots remains a
constraint. A private shared library likewise needs its own security/rebase
policy and explicit transitive compatibility.

Hypothetical removal of S0 deletes only /usr/bin/swayfx-mosaic and leaves
/usr/bin/sway, SceneFX and wlroots untouched. C would additionally remove only
its approved private library path. Real install, upgrade, uninstall and
rollback are NOT TESTED and were not attempted.

## Evidence-backed answers Q1–Q18

| Question | Answer |
| --- | --- |
| Q1 current stock build/stage? | Yes: clean pinned source/patch equivalence, stock Meson build and single DESTDIR stage PASS. |
| Q2 exact manifest? | Yes, exactly one regular ELF /usr/bin/swayfx-mosaic, no symlink. |
| Q3 added symbols? | Exactly wlr_scene_tree_set_clip and wlr_scene_tree_get_clip, no removed export. |
| Q4 required? | Both strong undefined in the shared private Mosaic binary; both ordinary definitions in static. |
| Q5 SONAME? | Names a provider, does not certify its export set; stock selection proves the two functions missing. |
| Q6 public layouts? | No member/type/enum/callback change in retained SceneFX headers, no wlroots source change; 17 sizes/alignments and six offsets identical. |
| Q7 further ABI incompatibility? | None newly demonstrated in current non-graphical matrix; 85 overlaps and mixed scene bindings are observed constraints, not proof of a new crash. Historical discarded struct-field candidate did crash separately. |
| Q8 stock with private binary? | No: missing strong clip relocations; unmodified stock cannot satisfy the tested binary. |
| Q9 static? | Build/model/loader shape passes with no SceneFX DT_NEEDED; one-file distribution still needs notice, security and wlroots decisions. |
| Q10 isolated shared? | Separate file/SONAME/RUNPATH could isolate library selection; process-wide symbol interactions remain. Distinct-SONAME build NOT TESTED. |
| Q11 package changes? | A needs approved supported API/version dependency; B approved embedding and notices/security/build policy; C extra file/identity/lookup contract; D architecture decision without necessarily another file. None applied. |
| Q12 update independence? | B removes shared SceneFX dependency and preserves file independence most concretely here; shared wlroots still prevents unconditional update-safety claims. |
| Q13 long-term maintenance? | A conditionally, if officially accepted/maintained; no acceptance evidence. Otherwise B/C need explicit project owners for security and rebases. |
| Q14 upstream preferable? | Conditional maintenance inference from one shared maintained primitive; error/bounds/ABI policy, ownership and graphical gates still missing. No submission authorized. |
| Q15 GPU/caches/version risks? | Not measured here; all-frame damage, references, effects and cache semantics must be separately qualified across actual version pairs. |
| Q16 shared edge phenomenon? | Separate rendering limitation carried across all options; static linkage does not repair it or prove native causality. |
| Q17 choose now? | Evidence supports candidate comparison only; explicit user architecture/packaging decision required before integration. |
| Q18 smallest next work? | Non-graphical contract dossier for static symbol binding/ownership, version qualification, security owner and one-file notices, plus an upstream API proposal dossier without submission. No new renderer or production patch. |

## Budget, validation and limits

PASS: one stock reconstruction, one stock stage, one private shared chain,
one optional static chain, one rebuilt pristine SceneFX reference. All Meson
setup/compile commands returned zero; mosaic-model 1/1 in stock, private
shared and static builds. C17 layout observers pass. AST, shell syntax, patch
application/equivalence, recipe checksums, export/symbol/header/loader and
license inventories are checked independently of graphical evidence.

Zero compositor launches, graphical runs, installations and packages generated.
NOT RUN: graphical headless IPC suite, GPU readback, physical backend/scanout,
new geometry/caches/lifetimes, actual update/rollback, another wlroots binary
version, bit-reproducible builds, static staging, distinct-SONAME build or
upstream submission. Preparation guards were tightened after the single build
chain; LAB/prepare-executed.py preserves the prior executed version and command
logs. No build was repeated for that non-behavioral fixture hardening.

The report and source fixture remain local and uncommitted. No source Mosaic
production, PKGBUILD, cumulative patch, UX, AGENTS, source pin or installed
compositor/library was changed. Final integrity and manifest details follow.

## Final integrity and local handoff

Source inventory: **1,463 entries**, SHA-256
`a27fa33d57d3423e09f02430f04cfed643762d876099b7f88489229115c4a1e5`.
Evidence inventory: **204 entries**, SHA-256
`86f7654c8ad962053644ce2c4c13eb9f026d6618b171e0cc3a8fc3034eb380d5`.
Both were sealed once and every entry independently checked again.
Original A source/evidence manifests remain byte-identical and pass with the
explicit historical README snapshot mapping.

Final normal checks PASS: AST for all four B Python scripts; shell syntax
for the existing exporter and PKGBUILD; C17 observers; all recorded builds and
three model tests; patch application/source equivalence; recipe digests;
Markdown local links; complete tracked/new-file whitespace/source-only audit;
protected production/UX/AGENTS/package/pin paths; installed sway/SceneFX/wlroots
hash equality; absence of LAB processes and sockets. The deep closeout review
was performed by the parent, not by an independent subagent; its findings and
fixture hardening are recorded in results/closeout-review.json.

Local HEAD and directly queried origin/main and github/main remain
`7c22b4020edc2d9ab6779d789159937523aae75a`. A was published; B has no staged
files, commit or push. The final worktree intentionally contains only the B
report/fixture and synchronized Architecture, Known Limitations, Roadmap,
README, Packaging audit section and Changelog. Packaging authority is unchanged.
Complete B diff, including untracked files, is retained as LAB/complete-phase-b.diff.
This report/diff is outside the sealed scientific inventory to avoid digest cycles.

No system install, package distribution, library replacement, live-session IPC,
QuickShell/dotfile/Codex change or STEP20D work occurred. No experimental process
or private socket remains. STEP20C NEXT; production multi-output NOT YET SUPPORTED.

## ABI/package evidence freeze — new ticket phase A

The preceding local handoff records the historical campaign state and its
A/B labels. This freeze publishes those ABI/package findings, without
reclassification, new builds, staging or compositor execution. The new static
distribution-contract phase B is separate and is not part of this commit.

All 1,463 source and 204 evidence entries were verified before changing the
fixture README's publication wording. Historical manifests are immutable.
For later verification, map only the historical fixture README path to:

`/home/fy59/swayfx-mosaic-abi-freeze-i6x1osil/historical-fixture-README.md`

The snapshot retains the hash in the original manifest; all other paths must
be checked directly. The four Python scripts are unchanged. Freeze audit
commands and historical-result verification are retained in `/home/fy59/swayfx-mosaic-abi-freeze-i6x1osil`.
Current package remains CURRENT_PACKAGE_STAGE_PASS; private shared with stock
SceneFX remains INCOMPATIBLE_WITH_STOCK_SCENEFX; static remains build/loader
evidence with no historical static staging or graphical qualification.

`SWAYFX_MOSAIC_SCENEFX_ABI_PACKAGE_PROBE=PARTIALLY_FEASIBLE`

`SCENEFX_ABI_PACKAGE_REQUIRES_ARCHITECTURAL_DECISION`

No distribution architecture or production integration is authorized.
