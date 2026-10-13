# STEP20C SceneFX static distribution and upstream contract

**EXPERIMENTAL / PRESERVED HISTORICAL EVIDENCE / no production integration.**
Protocol recorded before new tests. Phase A frozen and published at
`bb3a112550f45667e501d05d5a08aa8f7d0c02c6`; both remotes equal, clean worktree.
STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT; STEP20D–G PLANNED.
Production multi-output NOT YET SUPPORTED.

## Authority, protocol and decision boundary

[Packaging](../PACKAGING.md), [Architecture](../ARCHITECTURE.md),
[Upstream](../UPSTREAM.md), [Development](../DEVELOPMENT.md),
[Known limitations](../KNOWN_LIMITATIONS.md) and [Roadmap](../ROADMAP.md)
remain authoritative. No UX, production source, recipe, pin, cumulative patch
or system dependency change is authorized. Production strategy:
**NONE — USER DECISION REQUIRED**.

Reuse [historical ABI evidence](STEP20C_SCENEFX_ABI_PACKAGE_FEASIBILITY.md):
current stock package CURRENT_PACKAGE_STAGE_PASS; private shared with stock
SceneFX INCOMPATIBLE_WITH_STOCK_SCENEFX; static ELF resolves without SceneFX
DT_NEEDED, with shared wlroots. Historical verdict PARTIALLY_FEASIBLE.
85 common symbols are not 85 defects; 34 actual wlroots scene bindings have
31 external providers and three wlroots providers. No visibility policy is
authorized. Sizes/offsets and loader success do not establish full semantic ABI.

Pins: SwayFX 0.6 `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`;
experimental Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754`;
SceneFX 0.5 `37ccd723bef49e6891156ffafce8f549f01446cc`;
wlroots 0.20.2 `d783533489e1f75d6886c2ab5c5960090ef268f8`.
No newer source is substituted.

Read-only historical laboratory:
`/home/fy59/swayfx-mosaic-abi-package-tp22xfwm`.
New laboratory: `/home/fy59/swayfx-mosaic-static-contract-7_vlvpjw`. Commands, return codes and all generated results
remain there. Historical manifests are verified, never regenerated.

### Planned non-graphical checks

Map source references and ELF definitions into A public used SceneFX, B private
clip, C overlap with wlroots, D remaining dynamic and E executable-local
symbols. Record visibility, version, actual retained binding, owner and risk.
Inspect exported/dynamic tables, relocations and transitive package owners.
Read pinned headers, implementations, renderer/build/protocol contracts.

One static staging uses the qualified binary, not a newly built compositor.
Historical static prefix `/usr/local` requires a fresh private Meson install
plan on identical source bytes with `/usr` prefix; reuse the verified binary
without rebuild/strip, normal DESTDIR installation only. Inspect every entry
including directories, regular files, links, mode, uid/gid and hashes.
One-file shape says nothing about graphics, legal compliance or release readiness.

Audit exact source license texts and source-level notices for incorporated
components. Compare N1 embedded/extractable notice, N2 package metadata and
N3 separate installed notice. An optional disposable ELF-section roundtrip
tests N1 mechanics only. Never evade a license condition to retain one file.

Propose explicit dependency/version gates, manual security ownership and
reproducible source/patch/build provenance plus qualified rollback. Prepare
an upstream API dossier without contact, submission or public-field changes.
Compare maintained upstream API, private static, distinct private shared and
no new SceneFX primitive. Recommendations are not authorizations.

### Classification

FEASIBLE requires staging and relevant binding characterization plus explicit
dependency/maintenance contracts. PARTIALLY_FEASIBLE retains unresolved notice,
maintenance, version or ownership questions. INCONCLUSIVE means missing
essential staging/binding evidence. BLOCKED means a reproducible invariant
failure without validated candidate in scope. Unchosen license or packaging
policy is not automatically a code defect. No graphical campaign is allowed.

## Completed campaign and staging

`SWAYFX_MOSAIC_STATIC_DISTRIBUTION_CONTRACT_PROBE=PARTIALLY_FEASIBLE`

Architecture: **STATIC_DISTRIBUTION_REQUIRES_CONTRACT_DECISION**.
Immediate experimental candidate: private static SceneFX. Conditional long-term
maintenance direction: an upstream-maintained clipping API. Production strategy:
**NONE — USER DECISION REQUIRED**. No option is integrated.

`STATIC_STAGE_FILE_SHAPE_PASS` is measured, not inferred. One normal Meson
DESTDIR install returned 0. Complete non-directory manifest:

| Path | Kind | Mode | Actual uid:gid | Bytes | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `/usr/bin/swayfx-mosaic` | regular ELF | 0755 | 1000:1000 | 6,760,600 | `ccd47ce5b74c132e19bcd46d022a80e90e8a944acc3db521a89427ee7913c614` |

Directories `/usr` and `/usr/bin` are recorded in the complete JSON manifest.
No symlink, library, header, config, service, notice or second regular file.
The future package would own this path as root:root; no ownership change was
attempted. This is not an Arch package or legal distribution qualification.

The historical build has prefix `/usr/local`, bindir `bin`, debug build,
strip=false, mosaic-package=true, swaybar/swaynag=false, man-pages=disabled,
default-wallpaper=false. SceneFX alone has default_library=static; the
compositor's default_library=shared does not make its explicit archive dynamic.
The private new plan used the same package flags and static uninstalled
pkg-config provider, changing only prefix to `/usr` for staging. Sources were
copied and byte-verified against the sealed historical tree. The exact
qualified binary was copied into that plan's build-relative target location.
Meson setup performs its normal dependency/compiler configuration probes;
**no SceneFX or compositor source was compiled or linked again**. Install used
`--no-rebuild`, without tags or manual placement into DESTDIR. The staged hash
still matches the historical binary. Its embedded `/usr/local` configuration
strings were not rebuilt into `/usr`: runtime path suitability is NOT TESTED.
This intentional limitation is why this result qualifies file shape only.

Preparation initially failed because the fixture assumed a `subprojects`
directory absent from the historical archive. That Python failure preceded
Meson setup/install. The fixture was corrected to copy only existing inputs;
the retained preparation was resumed. Exactly one install attempt occurred.
The persistent `stage-install-started.json` prohibits a second attempt; the
historical laboratory and manifests were not changed.

## ELF loading and the five symbol groups

The private binary is ELF64, little-endian x86-64. No RPATH or RUNPATH.
Both clipping functions are FUNC/GLOBAL/DEFAULT, unversioned, in `.symtab`;
`nm` reports ordinary `T` definitions. They are absent from `.dynsym` and
have no unresolved dynamic relocation. They are executable definitions,
**not ELF LOCAL symbols**. Their call sites include private transaction tiled
and popup clipping, with get calls also in private output instrumentation.
No public structure field was introduced by the preserved sidecar patch.

SceneFX is absent from DT_NEEDED and the retained recursive loader graph;
`libwlroots-0.20.so` remains shared. Retained `ldd -r` returned 0 with no
undefined-symbol diagnostics. Strong undefined imports in the ELF are normal
shared-library references, not 891 loader failures. Weak optional imports are
reported separately. New readelf header/dynamic/full-symbol/relocation/version
and nm outputs are preserved; actual provider records are reused from the
sealed trusted loader diagnostics. No compositor entry point was run.

The standalone historical graph contains no SceneFX shared library alongside
the embedded archive. A future plugin, preload or additional dependency could
introduce one; that graph is NOT TESTED. Static embedding does not isolate the
process namespace. No export, rename, hidden-visibility or linker-policy
change was made or recommended without a separate experiment/authorization.

| Group | Definition and evidence | Current owner/provider | Convention and upgrade risk |
| --- | --- | --- | --- |
| A | 73 public SceneFX symbols required as strong imports by shared experimental compositor; static definitions and source references recorded individually | SceneFX implementation embedded in static executable; this set covers compiled SwayFX/Mosaic, not only newly added layout code | Unversioned C scene/effects/renderer functions, unstable public types; new header/body semantics need audit |
| B | `wlr_scene_tree_set_clip`, `wlr_scene_tree_get_clip`; strong private shared imports, executable ordinary definitions | Private SceneFX sidecar; direct static call resolution | No official upstream API/version/error guarantee; private prototype only |
| C | 85 names defined by pristine SceneFX and wlroots and exported by the static executable | Scene, EGL, color and matrix functions; actual providers separately recorded | Matching names alone establish overlap; only observed bindings prove selection; unobserved routes remain uncertain |
| D | 891 distinct strong undefined dynamic symbol base names in static executable, with versions/visibility preserved | Shared wlroots, Wayland, rendering and other system providers selected by retained loader records | ELF version requirements and SONAME do not prove semantic compatibility; all recursive versions matter |
| E | 1,275 ELF LOCAL definitions, including clip sidecar helpers and compositor internals; full table retained | Executable internal implementations | Local helpers have no dynamic ABI; they do not isolate the 85 shared scene/renderer exports |

`scene-symbol-ownership.json` includes groups, source locations, definitions/
reference candidates, full ELF records, consumer/provider pairs and risk per
symbol. A source occurrence is explicitly evidence of a reference candidate;
ELF tables determine definition/import status. Missing runtime records mean
NOT OBSERVED, not an invented provider. `exported-symbols.json` retains the
complete table, including actual symbol versions. Public WLR/SceneFX scene
functions have no ELF symbol-version compatibility namespace in this pair.
Versioned libc/etc imports are retained rather than relabeled unversioned.
Some helpers such as `wlr_scene_subsurface_tree_set_clip` remain dynamic
wlroots imports; that existing surface/subsurface primitive is distinct from
the two private inherited generic tree functions.

### Interposition: intentional integration versus unresolved semantics

The preserved stock/private/static diagnostics each observe **34 wlroots scene
bindings**. The exact same three remain in wlroots:

- `wlr_scene_subsurface_tree_create`
- `wlr_scene_surface_try_from_buffer`
- `wlr_scene_surface_create`

The other 31 bind to system/private SceneFX in shared controls and to the
static executable in the candidate. Their exact names follow below. This
pattern is coherent with ordinary SceneFX integration, already present in
stock; it is not a newly demonstrated clipping failure.

Pinned `wlroots-source/types/scene/xdg_shell.c:66`,
`layer_shell_v1.c:128`, `drag_icon.c:49`, `subsurface_tree.c:246` and
`surface.c:432` show why mixed ownership matters: wlroots helpers construct
SceneFX tree/buffer objects through interposed constructors, then manage
surface listeners and protocol lifecycle. Renderer/color/EGL structs and
callbacks similarly cross library boundaries. Preserving compatible object
and function semantics is necessary for these routes. This necessity follows
from source paths; **no hide/rename counterfactual was tested**. The minimum
safe export set is therefore NOT ESTABLISHED.

The 31 measured bindings are intentional/coherent for the tested pair at the
loader level, and helper construction routes substantiate their integration
role. Complete semantic necessity of every binding and all remaining overlap
paths is uncertain. Unobserved EGL/color/matrix routes must not be called
qualified merely because the names match. Any other wlroots version or distro
build is NOT QUALIFIED. A hypothetical distinct SONAME also does not fix this
process-wide behavior by itself.

```text
wlr_scene_buffer_create
wlr_scene_buffer_from_node
wlr_scene_buffer_send_frame_done
wlr_scene_buffer_set_buffer
wlr_scene_buffer_set_buffer_with_options
wlr_scene_buffer_set_color_encoding
wlr_scene_buffer_set_color_range
wlr_scene_buffer_set_dest_size
wlr_scene_buffer_set_opacity
wlr_scene_buffer_set_opaque_region
wlr_scene_buffer_set_primaries
wlr_scene_buffer_set_source_box
wlr_scene_buffer_set_transfer_function
wlr_scene_buffer_set_transform
wlr_scene_get_scene_output
wlr_scene_node_coords
wlr_scene_node_destroy
wlr_scene_node_place_above
wlr_scene_node_place_below
wlr_scene_node_set_enabled
wlr_scene_node_set_position
wlr_scene_output_build_state
wlr_scene_output_create
wlr_scene_output_destroy
wlr_scene_output_needs_frame
wlr_scene_output_send_frame_done
wlr_scene_output_set_position
wlr_scene_rect_from_node
wlr_scene_timer_finish
wlr_scene_tree_create
wlr_scene_tree_from_node
```

## Dependency contract and conditional future recipe

The static executable's complete direct DT_NEEDED list is:

```text
libcairo.so.2 libdrm.so.2 libjson-c.so.5 libevdev.so.2 libinput.so.10
libudev.so.1 libm.so.6 libpango-1.0.so.0 libgobject-2.0.so.0 libglib-2.0.so.0
libpcre2-8.so.0 libpixman-1.so.0 libwlroots-0.20.so libwayland-server.so.0
libxkbcommon.so.0 libEGL.so.1 libgbm.so.1 libGLESv2.so.2 liblcms2.so.2
libxcb.so.1 libxcb-icccm.so.4 libpangocairo-1.0.so.0 libc.so.6
```

Only SceneFX is statically embedded. EGL/GBM/GLESv2/lcms2 become direct
DT_NEEDED instead of arriving through SceneFX. libdrm and pixman were already
direct ELF needs, but are only makedepends in the current recipe. Static
embedding must not rely on removing SceneFX while accidentally losing runtime
providers previously brought in by it. The retained recursive graph also has
Wayland client, Vulkan, seatd/libseat, display-info, liftoff, libudev, XCB
extensions and renderer/allocator libraries. Their ownership remains with
shared providers; GPU driver modules loaded later are outside loader-only proof.

| Provider in observed system | Candidate future runtime declaration | Reason |
| --- | --- | --- |
| wlroots0.20 | retain, qualify exact build/version matrix | still shared; cannot freeze ordinary SwayFX upgrades |
| wayland | retain | server direct, client/transitive and protocol generation |
| libglvnd | add explicit runtime/build availability | direct EGL and GLESv2 |
| mesa | add explicit runtime/build availability | observed libgbm provider; actual renderer/driver gates remain |
| lcms2 | add explicit runtime/build availability when enabled | direct color-management provider in this build |
| libdrm, pixman | promote to runtime depends | direct DT_NEEDED, currently only makedepends |
| glib2, glibc, xcb-util-wm | make direct ownership explicit in proposed recipe review | GObject/GLib, libc/libm, libxcb-icccm; presently supplied transitively/base system |
| cairo, json-c, libevdev, libinput, systemd-libs, libxcb, libxkbcommon, pango, pcre2 | retain | direct providers and current enabled features |
| gdk-pixbuf2, ttf-font | retain pending runtime feature audit | absence in DT_NEEDED alone does not authorize removal of feature/data requirements |
| scenefx | conditionally remove runtime dependency only after static architecture approval | no SceneFX DT_NEEDED; replace with verified embedded-source build provenance |
| git, meson, ninja, pkgconf, python, wayland-protocols | retain build tools/inputs | source/patch/build/protocol generation |
| kitty, grim | retain future check requirements | not executed in this non-graphical ticket |

This is a proposal, not an applied recipe. Package names describe observed
Arch owners, not universal providers. Requalify clean dependency closure,
feature toggles, strip/notice retention, reproducibility, staging and separate
graphics checks before changing the recipe. No PKGBUILD byte changed.

## Version and shared-structure contract

Only pinned SceneFX 0.5 source plus **observed wlroots 0.20.2-1 binary** is
qualified for these non-graphical checks. Installed headers match the pinned
wlroots source for 121 non-generated files; runtime/version metadata agree.
That does not reconstruct the entire distro build patch set and toolchain.
The Meson range `>=0.20.0,<0.21.0` is a dependency acceptance expression,
not a demonstrated compatibility range. 0.20.0, 0.20.1, another 0.20.2 build,
later 0.20 releases and 0.21 are **NOT TESTED**.

WLR_USE_UNSTABLE exposes public scene nodes, tree, buffers, output, output_state,
surfaces, renderer/buffer implementations, listeners, signals, color transform,
EGL and render-pass conventions. The historical observer measures identical
size/alignment for 17 selected structs and six offsets across installed,
pristine and private headers. Examples: scene_node 112/8, tree 128/8,
scene_buffer 472/8, output 624/8, surface 968/8; tree.children offset 112,
node.parent 8, buffer.buffer 112. It does **not** show equality between native
wlroots scene layouts and extended SceneFX structures, nor exhaustive layouts,
callbacks, enum tags, ownership or semantics.

SceneFX requires Wayland server >=1.24, protocols >=1.41, libdrm >=2.4.129,
xkbcommon >=1.8 and pixman >=0.43; compositor requirements differ in places.
Generated XDG and other Wayland protocol code and scanner inputs are part of
reproduction. The observed wlroots enables DRM, X11, libinput, Xwayland,
GLES2, Vulkan, GBM, udmabuf, session and color management. SceneFX selects its
FX/GLES renderer and observed lcms2 path. Build flags, generated config headers,
protocol versions and actual compiler dependencies must accompany source pins.
No additional renderer or protocol combination was tested here.

Candidate qualification matrix for **each** new shared wlroots build:

| Gate | Required evidence | This ticket |
| --- | --- | --- |
| 1 header/source | API, callbacks, enum and lifecycle diffs; exact distro patches | pinned pair only, subset retained |
| 2 symbols | definitions/imports, versions, all consumer/provider bindings | pinned pair only; visibility isolation untested |
| 3 struct layouts | sizes/alignments/offsets for every crossing type and callback ABI | historical 17 structs/six offsets only |
| 4 clean build | fixed SceneFX/Mosaic sources and patch order, toolchain/features | historical build PASS; no new compositor build |
| 5 loader | complete recursive graph, strong/weak relocations, no duplicate SceneFX | historical trusted graph PASS |
| 6 unit/model | actual production model and library contracts | historical mosaic-model 1/1 in three builds; new version NOT TESTED |
| 7 private stage | complete manifest, notices/strip and provenance | current candidate file shape PASS only |
| 8 separately authorized graphics | standard/Mosaic/control, popups, effects, saved buffers, damage, input, scale/rotation/migration/generation | NOT TESTED for static candidate in this ticket |

Do not pin global wlroots to prevent normal SwayFX upgrades. If Mosaic's pair
becomes unqualified, withhold its candidate release, rebuild/requalify or use
standard SwayFX. File independence is established; update independence is not.

## Candidate security ownership and reproducibility

Bundled SceneFX no longer receives fixes when the system scenefx package is
updated. The **Mosaic distributor/maintainer must explicitly accept ownership**
for monitoring and rebuilding embedded code, with a named reviewer and release
owner. Nobody is assigned by this ticket; an unowned policy is an open gate.
Upstream remains a source of fixes, not the security updater of this executable.

Proposed manual workflow, requiring adoption before distribution:

1. Record SceneFX commit/tag provenance, Git object identity and SHA-256 source
   inventory; list exact private patches in order and their digests. Preserve
   SwayFX/Mosaic/wlroots pins, actual system package/build identities, scanner,
   protocols, toolchain, flags, generated config and link commands.
2. An assigned maintainer reviews upstream releases/commits and security
   advisories affecting SceneFX and copied wlroots scene/renderer code; assess
   relevance and exposure. A second reviewer checks the fix and private clip
   interaction. Set a reporting channel and triage/release response expectations.
3. Review a candidate source revision and rebase private patches explicitly;
   no silent cherry-pick, ABI substitution or automatic update. A fix may alter
   renderer paths, layouts or interposition and require redesign.
4. Rebuild only in a controlled private environment with fixed dependency
   sources/build metadata and no fallback downloads. Recheck symbol/layout/
   loader/dependency gates, model tests, staging/notices and separately authorized
   graphics. Two clean builds with path/timestamp controls are needed before
   claiming bit reproducibility; not performed here.
5. Record artifact/source/notices hashes, review approvals and matrix results.
   Publish only under a separate release authorization. Retain the previous
   qualified artifact and full build manifest for rollback, including compatible
   dependency identities. No updater or release package is created here.

The cost is recurring SceneFX plus copied-wlroots security triage, patch rebases,
shared-wlroots qualification, legal-notice inventory and graphics/release testing.
It is more than rebuilding one compositor after a source change. A reproducible
procedure is proposed; bit-identical artifacts and security response are NOT
ESTABLISHED. Source provenance is necessary but does not itself certify security.

Rollback must never restore system SceneFX/wlroots or overwrite `/usr/bin/sway`.
Replacing/removing only Mosaic preserves ordinary package ownership. An older
Mosaic artifact may fail with newer shared wlroots/renderer providers; it is
not automatically a working rollback. Retain/requalify compatible manifests,
or fall back to the separately maintained standard SwayFX session. Actual
install/update/uninstall/rollback remain NOT TESTED.

## Licenses, incorporated components and notice options

Pinned SwayFX, SceneFX and wlroots root licenses contain MIT copyright,
permission and warranty notices. SceneFX's root notice names Drew DeVault and
Jari Vetoniemi; wlroots additionally names its contributors. Preserve complete
texts, not merely `license=('MIT')`. The licenses and source notice candidates
are retained verbatim in private `license-notices.json`; no notice dump enters Git.
Compiled-source provenance, generated protocol comments, archive symbol input,
compile commands and linker plan are retained separately. The proof does not
claim every archive member is extracted into the final executable.

Important additional condition: generated protocol code carries its own
copyright/permission text. XDG includes Kristian Høgsberg, Rafael Antognolli,
Jasper St. Pierre, Intel, Samsung and Red Hat notices. Generated wlr-layer-shell
and output-power code use permission/warranty language that includes supporting
documentation and restrictions on advertising with copyright-holder names.
An umbrella MIT label alone does not cover this inventory. The existing asset
license and tinywl example notices appear in the broad source inventory but
are not thereby proven incorporated: wallpaper/examples are disabled. Shared
EGL, GBM, GLESv2, lcms2, Wayland, pixman/libdrm and wlroots are not newly copied
as static libraries; their package license metadata is contextual evidence,
not a declaration that all their source is embedded.

The disposable `.mosaic_notices` objcopy probe includes exact root license and
generated protocol texts. A byte-for-byte section extraction passed. This is
an oversized candidate inventory, not a completed incorporated-code notice
closure, public notice interface or approved compliance solution. The copied
binary was never executed or staged. Original and staged qualified binaries
are unchanged. Strip/signing/package transformations and accessible notice
delivery still need tests. No public/source API or visibility policy changes.

| Option | Feasibility/accessibility | One-file contract | Risk and required decision |
| --- | --- | --- | --- |
| N1 embedded section/metadata | add/extract byte identity PASS on disposable ELF; document extraction with binutils without compositor execution | structurally compatible | complete notice closure, end-user discoverability, strip/retention and legal sufficiency not established; user adoption/review required |
| N2 package metadata/source archive | normal `license` metadata identifies a license; it does not automatically deliver its full notices | structurally compatible installed manifest | raw binary transfer and package/source separation can lose notices; actual complete notice-delivery design and legal review required; metadata label alone insufficient |
| N3 separate installed license/notice | conventional readable file, no specialized ELF extraction | incompatible with current exact-one-file rule | requires explicit user packaging-contract decision plus complete notices/review; preferred practical distribution direction if rule can be changed |

Do not drop notice obligations to preserve one installed file. A credible N1
candidate exists technically; a sufficiently solid one-file compliance solution
is **NOT YET QUALIFIED**. Conditional recommendation: allow a distinct installed
notice file (N3) for clarity and discoverability if the user authorizes that
contract change. This ticket neither changes the contract nor asserts final
legal compliance. The protocol-specific supporting-documentation condition
needs assessment for any N1/N2 route.

Primary references inspected: [pinned SceneFX license](https://github.com/wlrfx/scenefx/blob/37ccd723bef49e6891156ffafce8f549f01446cc/LICENSE),
[Meson DESTDIR/no-rebuild](https://mesonbuild.com/Installing.html),
[GNU objcopy sections](https://sourceware.org/binutils/docs/binutils/objcopy.html)
and [Arch PKGBUILD license metadata](https://man.archlinux.org/man/PKGBUILD.5.en).
Local pinned source texts and retained generated comments govern the inventory.
This is a technical/legal-obligation dossier, not legal clearance.

## Separate upstream API dossier — not submitted

An API could express a **generic inherited scene-tree clip**, not Mosaic popup
ownership or UX. Known experimental signatures, retained only as candidates:

```c
void wlr_scene_tree_set_clip(struct wlr_scene_tree *tree,
    const struct wlr_box *clip);
bool wlr_scene_tree_get_clip(struct wlr_scene_tree *tree,
    struct wlr_box *clip);
```

No signature is frozen. In particular a void setter cannot report the private
sidecar's allocation failure. A maintained API may need a result/error enum or
another upstream-owned storage/lifecycle design. No such code, fields or ABI
change is implemented here. Public structures must not grow without maintainer
agreement on ABI/version policy and all cross-library consumers.

| Topic | Demonstrated private/source behavior | Proposed maintained contract / required tests |
| --- | --- | --- |
| coordinates | copied tree-local integer wlr_box; descendant traversal intersects ancestor clips | logical tree-local half-open rectangle, explicit conversion to output/buffer; checked addition/narrowing/overflow |
| ownership | sidecar owns copied box; tree pointer borrowed; destroy listener frees sidecar | caller may discard box after successful set; tree owns clip lifetime; main scene-thread use only, no independent worker authority |
| NULL | setter clears, absent clear is no-op; getter asserts non-NULL output | NULL rectangle removes own clip; invalid tree/out pointer must have documented error/assertion policy; get absent returns false and define untouched out value |
| empty/negative | zero dimensions accepted; negative dimensions asserted | zero area excludes descendant pixels/hits; negative sizes rejected explicitly; no silent signed overflow or allocation failure |
| update/idempotence | same box memcmp returns early; clear/update invokes scene_node_update | compare semantic coordinates rather than struct padding; same effective clip idempotent; allocation error preserves old state and reported status |
| moving/reparenting | traversal follows parent chain and local→global coordinates | own clip moves with tree; inherited effective clip recomputed on reparent; old/new output damage invalidated; cyclic/invalid reparent rejected by existing ownership rules |
| destruction | listener removes and frees sidecar | no references/listeners after tree destruction; recursive destruction, clear-before-destroy, failed allocation and destruction during callbacks tested |
| inheritance | intersections in private descendant render/hit traversal | getter distinguishes own clip from effective inherited clip; empty ancestor dominates; nested trees and negative origins tested |
| rendering/hit | sampled historical tiled/popup render/hit behavior only | same applied effective bounds for render and hit; other node types, occlusion and buffer-local coordinates must agree |
| damage | private node update and sampled damage; complete proof absent | invalidate exposed/vacated regions on set/clear/move/reparent/output changes; all-frame stale-pixel coverage and cache invalidation |
| effects | sampled shadows/blur; shared edge limitation unresolved | define whether clip limits final coverage versus blur source sampling, shadows/rounded corners/optimized cache; preserve ordinary effects semantics |
| saved buffers | sampled historical held/timeout paths, no complete GPU lifetime proof | consistent applied geometry for saved nodes; destroy/release/ACK/timeout and cross-output lifetime tests |
| rotation/scaling | separate sampled historical probes, not static-candidate graphics | output-transform and fractional rounding policy, damage expansion, conservative raster bounds with exact logical hit contract |
| performance | private linear global sidecar lookup | scalable lookup/storage, bounded per-frame work, no unbounded allocator churn; benchmark deep trees/many clips, cache mutation coherency |
| ABI/version | two private functions, unchanged measured public header layouts | maintained feature/version exposure, compile/link guards, cross-wlroots compatibility policy; exact paired-version qualification |

Mosaic must separately retain tiled-owner identity, root/nested popup hierarchy,
applied workspace/output viewport and owner visibility. The private empty clip
for a fully hidden owner is **Mosaic-owned policy evidence**, not a generic
SceneFX requirement to know workspaces or XDG grab semantics. Offscreen hide,
dismiss or reposition remains undecided UX. No universal click-through promise:
valid grabs still have their ordinary dismissal behavior, compared with stock.
SceneFX cannot alone assign a Sway transaction generation or popup owner.

Questions for a future authorized maintainer discussion: is inherited tree clip
an acceptable primitive? Which coordinate and empty/error policy? Can own/effective
queries remain separate? Where may storage live without incompatible public
layouts? Which consumers must retain interposed providers? What damage/effects/
saved-buffer semantics can be guaranteed? How should capabilities, ABI and
wlroots pairs be versioned? What tests/benchmarks belong upstream? Would an
error-reporting setter be preferable? No contact, issue, PR or submission occurs.

Required future tests include C API syntax/invalid arguments, box overflow and
allocation failures, idempotence, nested clips, reparent and destruction,
render/hit agreement, complete damage and effects/cache/saved-buffer coverage,
scaling/rotation/migration, shared-object crossings and performance. A successful
compile or signature proposal does not close those tests.

## Architectural decision matrix

| Dimension | A maintained upstream API | B private static SceneFX | C distinct private dynamic identity | D no SceneFX extension |
| --- | --- | --- | --- | --- |
| evidence | private primitive only; upstream acceptance unknown | pinned build/ELF/bindings and one stage PASS | private same-SONAME selection observed; distinct identity NOT TESTED | alternative clipping mechanism not demonstrated |
| maintenance | upstream primitive if accepted; Mosaic owner/viewport still ours | embedded source/security/rebase/version owner required | private library/security/rebase/version owner required | broader Mosaic rendering/input maintenance possible |
| system dependencies | supported maintained SceneFX/wlroots pair | shared wlroots/graphics, no shared SceneFX need | shared wlroots plus private SceneFX file | existing SceneFX/wlroots, unknown new needs |
| SwayFX coexistence | standard packages intact, normal upstream transition | standard binary/libraries intact; file shape PASS | extra private path must be approved | possible filesystem independence, architecture unproved |
| ABI/interposition | official contract still to negotiate; existing integration persists | 85 overlaps; 31 measured wlroots routes into executable | distinct SONAME separates lookup, not namespace/struct semantics | no new clip exports, existing unstable APIs still matter |
| upgrades | paired versions and release qualification | no automatic SceneFX fixes, wlroots upgrades unqualified | private fixes plus shared wlroots qualification | unknown forward-port cost |
| packaging | possible one binary, notices remain | one binary staged; notice/security contracts open | extra library and notices require contract change | unknown final shape |
| licenses/security | preserve notices; upstream plus Mosaic release owners | complete embedded notices and project security owner | notices plus private-library security owner | inventory remains; project owns alternate mechanism |
| rollback | old release only with compatible dependencies; stock fallback | old embedded code may be vulnerable/incompatible; stock fallback | must roll binary/private library together, shared graph still matters | unqualified alternate rollback |
| delivery complexity | external agreement, maintained release and integration | controlled source/archive/patch/provenance/notices builds | private identity/path/RUNPATH/transitive binding contract | largest unexplored implementation risk |
| residual risks | API acceptance and graphical gates | semantics, versions, notices, ownership and graphics | same plus double library/lookup risk | popup stacking/hits/effects/damage/saved buffers/generation |
| minimum next step | authorize discussion after local API/notice review | user contract decisions, then separately scoped version/notice tests | user new-file contract then bounded identity/binding prototype | architecture study; no renderer implementation authorized |

B is the **best demonstrated immediate experimental candidate**: no new owned
SceneFX library file, no absent system clip symbol dependency, explicit ELF
and staging evidence. A is the **conditional best long-term maintenance
orientation**, because a maintained generic primitive could avoid perpetual
private patches. This is an engineering recommendation, not evidence of
upstream commitment. C is not qualified by the existing same-SONAME build;
D is not established by output scissor or surface cropping alone.

Required user decisions: candidate architecture or continued investigation;
N1/N2/N3 notice route and any packaging-contract change; named security/release
owner and response policy; supported exact wlroots build qualification policy
without blocking standard upgrades; acceptable rollback/support boundary;
permission for any upstream contact; scope of separately authorized graphics,
version, reproducibility and delivery tests. No production choice is applied.

## Reproduction, validation and unclosed gates

Historical source/evidence manifests remain unchanged and fully verified with
the explicit README snapshot mapping from phase A. This campaign reuses ELF
and actual bindings, without rerunning historical builds or loader tracing.
The new audit fixture preserves its own command/return-code/raw records. It
allows repeat static analyses before sealing, but has an exclusive staging
attempt marker and refuses sealed results.

For an independent future reconstruction, archive exact pinned Mosaic and
SceneFX objects; apply preserved patches in order:

```text
SceneFX: step20c-valid-grab/scenefx-popup-plus-base.patch
         step20c-temporal-damage/scenefx-timing.patch
         step20c-optimized-blur-cache/scenefx-cache-trace.patch
Mosaic:  step20c-valid-grab/mosaic-popup-plus-base.patch
         step20c-valid-grab/hidden-guard.patch
         step20c-temporal-damage/mosaic-output-timing.patch
         step20c-presentation-identity/presentation-events.patch
         step20c-optimized-blur-cache/sway-source-trace.patch
```

Use the historical fixture's exact Meson static-chain flags, setting Mosaic
prefix `/usr`/bindir `bin` initially, with the static SceneFX uninstalled
pkg-config directory only for that build. Keep wlroots shared and archive its
pinned source for audits. Verify each patch/digest and qualified installed
header/build inputs. No stock/shared chain is needed. A future reproduction
requires its own authorization and provenance rather than expecting the old
laboratory to exist or silently accepting a different library build. Do not
run historical prepare.py just to analyze symbols: it builds unnecessary chains.
The qualified-source regeneration path is independent of historical binaries;
bit identity and reproducibility across machines remain NOT TESTED.

Current result files include complete staging/ELF/export/ownership/interposition,
transitive dependencies, versions, security, licenses/notice options, upstream
API, architectural matrix, unresolved gates and summary. Private source/evidence
manifests seal the final inventories, excluding themselves and this report's
integrity appendix to avoid cyclic digests. No generated file enters Git.

NOT TESTED: static-candidate graphics/GPU/readback, another wlroots version or
build, distinct-SONAME/private-path delivery, all-frame damage/effects/cache/
saved-buffer lifetimes, applied-generation consistency, upgrade/rollback,
strip/sign/package notice retention, complete legal compliance and bit
reproducibility. Historical graphical subset results are not transferred into
a new static distribution qualification. STEP20C remains NEXT.

Final ELF count: 88 dynamic definitions, comprising the 85 common SceneFX/
wlroots exports plus libc-related `optarg`, `optind`, `stderr` data records.
These data records are not additional SceneFX functions. Seven generated
protocol notice records are preserved from compiled inputs.

Final checks PASS: Python AST, existing shell/recipe syntax, local Markdown
links, source-only fixture/whitespace, complete stage/hash, retained ELF/bindings,
structured policy dossiers, protected sources/recipe/patch/UX/AGENTS, unchanged
canonical packaging contract, installed sway/SceneFX/wlroots hashes and no LAB
processes/sockets. Meson model results are historical, not reexecuted.
The parent performed one closeout dossier/fixture review; this is not an
independent subagent review. Failures and corrections are explicitly retained.

## Final inventory integrity and local state

Source manifest: **1892 entries**, SHA-256
`5ad64eaf0aec2290689c46b7754eb4563980396ba2a06e852d1c8e903086f138`.

Evidence manifest: **143 entries**, SHA-256
`85d034f4075436bbdda302afdfa94955365aa51adcfb7e8b04ed6bb28377f649`.

Both new manifests are sealed and reverified; original 1,463/204 historical
manifests remain unchanged. The report itself and complete diff are excluded
from those inventories to avoid cyclic digests. Phase A HEAD remains
`bb3a112550f45667e501d05d5a08aa8f7d0c02c6` on local, origin and github.
Phase B remains unstaged/uncommitted/unpublished: report/fixture plus
Architecture, Known Limitations, Packaging evidence appendix, Roadmap, README
and Changelog only. No protected production/system/session change, installation,
package creation/publication, upstream submission or STEP20D work occurred.

Recommended next smallest step: user review of notice route (N3 recommended
conditionally), security/release ownership and exact wlroots qualification
policy, then a separately scoped test authorization. No production integration
is authorized by this dossier.

`SWAYFX_MOSAIC_STATIC_DISTRIBUTION_CONTRACT_PROBE=PARTIALLY_FEASIBLE`

`STATIC_DISTRIBUTION_REQUIRES_CONTRACT_DECISION`

## Subsequent user decisions — 2026-10-13

After this campaign, the user approved private static SceneFX for the immediate
STEP20C candidate, separate complete license notices for a future candidate,
project responsibility for embedded SceneFX maintenance, and strict qualification
of each SceneFX/wlroots pair. These decisions authorize documentation and private
prototypes only; the current package, production patch and source remain unchanged.
No individual owner or response SLA is assigned. The historical verdict and
architectural conclusion above are unchanged. A separate runtime/package gate
must build a real `/usr` binary and qualify loaded libraries and sampled clipping.

The evidence-freeze audit verified all 1,892 source and 143 evidence entries
before changing publication wording. Original manifests were neither regenerated
nor overwritten. For later verification, map the seven updated documentation
entries through `/home/fy59/swayfx-mosaic-static-contract-freeze-v1/snapshot-map.json`;
all other entries use their original paths. Snapshot bytes are retained outside
Git, with original hashes verified by `verify-freeze.py`.
