# STEP20C private static runtime and package contract

**EXPERIMENTAL / PRESERVED HISTORICAL EVIDENCE.** No production integration or install.
Protocol established before builds and runtime. Historical verdicts remain
unchanged; [static distribution evidence](STEP20C_SCENEFX_STATIC_DISTRIBUTION_CONTRACT.md)
was published separately. [Packaging](../PACKAGING.md) governs file ownership;
[Architecture](../ARCHITECTURE.md) preserves compositor authority.

## Decision register — 2026-10-13

| Decision | Motivation and authorized scope | Prohibited / residual risks / revision gates |
| --- | --- | --- |
| D1 private static SceneFX | Historical ELF resolves both private clips without system SceneFX replacement; build/run private candidate | No production integration, algorithm change or installed library replacement; semantic interposition and full graphical matrix remain open |
| D2 separate notices | Preserve full incorporated-code attributions and permissions without artificial one-file constraint; private future stage only | Current recipe unchanged; exact notice inventory must follow link inputs and generated protocols; legal clearance not asserted |
| D3 project maintenance | Embedded code does not inherit system SceneFX fixes; project monitors/reviews/rebuilds/requalifies | No named owner/SLA; release maintainer/security reviewer required before distribution; no automatic updater |
| D4 strict pair qualification | Unstable shared scene/renderer types and 85 overlaps require exact build evidence | No inference to later versions, no blocking stock upgrades; inspect headers/symbols/layouts, rebuild, relocations/model/stage/headless/graphics, separate release decision |

Current package: unchanged PKGBUILD, system SceneFX, only `/usr/bin/swayfx-mosaic`,
no STEP20C implementation. Future experimental candidate: static SceneFX, shared
wlroots, system libraries intact, binary plus inventoried notices only.
Long-term direction remains SCENEFX_UPSTREAM_MAINTAINED_CLIP_API; reuse the
historical unsubmitted dossier. Ownership/errors/bounds/lifetime/hit/damage/
versioning need a maintained API; popup ownership remains Mosaic-specific.
No contact or upstream adoption is presumed.

## Bounded protocol

One external LAB, one SceneFX static build, one Mosaic static build with
`--prefix=/usr --bindir=bin -Dmosaic-package=true`, one Meson DESTDIR stage,
one notice addition and one ELF/dependency audit. Reconstruct pinned Mosaic
`cd550382b311efdbfe3ed892f4e1d281d852e754`, SceneFX
`37ccd723bef49e6891156ffafce8f549f01446cc`, SwayFX
`fd71a6bdc061bd633b488ae7b83e8a6981d22f86` and wlroots
`d783533489e1f75d6886c2ab5c5960090ef268f8`; reuse the historical ordered
eight private patches unchanged, verify source equivalence. wlroots stays shared.

A persistent exclusively locked ledger reserves every operation before execution;
failures consume reservations. Test the ledger offline first. One principal run,
optional one indispensable pristine control, at most eight PNGs, one calculated
camera correction, no hide/return pair, 150 seconds per run. Explicit private
mode-0700 runtime/Wayland/IPC sockets; staged executable only. Verify process
mappings before clients or clipping: no SceneFX .so, exact system wlroots and
no historical LAB. Wrong identity stops the run.

HEADLESS-1=(-800,0), HEADLESS-2=(0,0), each 800×600, scale 1, normal.
Use verified historical ordinary SHM client/reference and virtual pointer; verify
actual target crossing x=0, retained H1 pixels, excluded H2 pixels and measured
hits. Return to splith and inspect clip removal. Root valid-grab popup may be
reused only without widening protocol; otherwise NOT TESTED. No nested campaign.
Damage extents are sampled and never establish every-frame coverage. Stop
concerned scenario on crash/ABI/clip/hit leak; no algorithm repairs. Historical
pristine evidence can provide reference semantics, without fresh campaign.

License inventory follows actual linker/compile/generated inputs, preserved
full notices and attribution/provenance/hash/destination. Dynamic system-library
licenses are not indiscriminately copied. Unclosed inventory prevents a ready
distribution verdict. Reproducible procedure is distinct from bit reproducibility.

Results and raw commands/exit codes live outside Git. All untested matrix cells
are NOT TESTED. FEASIBLE is limited to the tested matrix; PARTIALLY_FEASIBLE
retains qualification limits; INCONCLUSIVE reflects unreliable/missing runtime
evidence; BLOCKED requires a demonstrated incompatibility/crash/forbidden leak.
STEP20C remains NEXT; production multi-output NOT YET SUPPORTED.

## Completed private campaign

LAB: `/home/fy59/swayfx-mosaic-static-runtime-hm5kbdkt`.
The preceding static-distribution freeze commit was
`4f4f3fefcdcf979f8be126d6671062ecb1d65b50`, published on both remotes.
The runtime campaign below was phase B of that earlier ticket. Its evidence
is now preserved by the separate static-runtime freeze ticket; it is not the
new focus/input/standard-return campaign.

`SWAYFX_MOSAIC_STATIC_RUNTIME_PACKAGE_GATE=PARTIALLY_FEASIBLE`

Architecture: **UNDECIDED**. The single runtime comparison scenario is
**INCONCLUSIVE**; no reproduced ABI crash or forbidden target hit is established.

| Gate | Observation |
| --- | --- |
| Source/build | Eight unchanged patches applied; full private source equivalence PASS; one static SceneFX and one Mosaic build, model 1/1 PASS |
| Prefix | Real Meson `/usr`, bindir `bin`, compiled sysconfdir `/etc` (compiler spelling `//etc`); no copied `/usr/local` binary |
| Staging | STATIC_STAGE_WITH_LICENSES=PASS; five regular files; user-owned private DESTDIR |
| ELF | ELF64 x86-64, both private clip T definitions and direct calls, no SceneFX DT_NEEDED, no RPATH/RUNPATH, ldd -r without unresolved symbols |
| Runtime | Staged executable actually loaded; exact system wlroots and no shared SceneFX in /proc maps; two prescribed outputs, IPC and ordinary clients mapped |
| Renderer | Actual SceneFX FX / OpenGL ES 3.2 Mesa 26.2.4, AMD Radeon 780M; headless backend, no physical display session |
| Interposition | 34 observed runtime wlroots scene bindings: 31 into executable, three wlroots helper providers unchanged |
| Applied clipping | +160 sole camera correction, owner scene x=-320,width=640; local inherited clip=(160,0,800,600), both set/get paths observed through retained traces |
| Pixels | 182,214 H1 target-color pixels, zero H2 target colors; H2 content crop identical |
| Reference gate | Whole H2 FAIL: 23,807 changed pixels outside IPC content bounds, coherent with focused→unfocused decorations; cannot claim whole-output equality |
| Input/standard return | NOT TESTED: run stopped at reference gate before button scoring and splith |
| Popup | Root/nested grabbed popup NOT TESTED; historical controls retained, no fresh pristine run |
| Damage | Native TEMPORAL_DAMAGE extents retained; complete frame coverage NOT TESTED |
| Budget | scene=1,mosaic=1,stage=1,notices=1,ELF=1,principal run=1,control=0,camera=1,PNG=3; ~3.999 seconds, no retries/refunds |
| Cleanup | Compositor exit 0 on owned SIGTERM cleanup, clients exit 0; pointer terminated -15; all owned groups reaped and private runtime removed |

The build/stage/executed binary SHA-256 is
`f82557c1a9978a5e9665b9b4291b74880253725359e3df1c5b8d554921f7603b`,
size 6,760,304 bytes. Different bytes/size from the historical binary are not
a regression claim; prefix/source/build paths differ.
Qualified shared wlroots build: Arch `wlroots0.20 0.20.2-1`, ELF SHA-256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`,
Build ID `2cd3a56136647a9da32b9a682606911aa2498393`. Installed nongenerated
headers match the pinned archive; selected historical layouts are retained,
without rerunning the old ABI campaign. Other pairs NOT QUALIFIED. This pair's
input, standard return and wider graphical behavior remain unqualified.

### Notice manifest and distribution boundary

Meson produced only `/usr/bin/swayfx-mosaic`. The future-package simulation
added four 0644 files under `/usr/share/licenses/swayfx-mosaic/`:
`SwayFX-LICENSE`, `SceneFX-LICENSE`, `wlroots-LICENSE`,
`INCORPORATED-NOTICES`. Root texts are byte-identical to pinned sources;
compiled generated protocol copyright/permission/warranty comments are included
verbatim with their source provenance. wlroots notice covers copied code in
SceneFX, not a dump of every dynamic system dependency. The inventory records
compile commands, source hashes, protocol comments, destinations and root
attribution. Notice hashes and the complete five-file manifest are in results.
The technical stage passes; exact unused archive-member extraction, all copied
header/shader notice closure and final legal review remain distribution gates.
No definitive legal compliance is asserted.

### Failed fixture checks and reproducibility limits

The first offline multiprocessing ledger test failed for missing `__main__`
guard on Python 3.14; corrected and PASS before runtime. The ELF audit completed
its one diagnostic batch and notice addition, then failed an incorrect assertion
looking for `/usr` in config.h. Stage validation instead verifies actual Meson
options and compiler SYSCONFDIR. That erroneous assertion was corrected locally,
without rerunning the audit batch or repeating staging. Initial direct loader
trace yielded no scene bindings; real runtime LD_DEBUG provides the 31/3 result.
The local audit fixture now uses diagnostic ldd -r for future reproduction; this
correction has NOT been executed on a second binary.

The principal run compared H2 while focused at baseline and unfocused in Mosaic.
The whole-output assertion stopped the scenario. Offline IPC/color comparison
localizes all differences outside the unchanged content rectangle; this supports
a reference-fixture mismatch, not a demonstrated forbidden clip leak. No new
run, capture, algorithm fix or budget reset follows. The collector's initial
crop double-counted decoration height; its corrected offline crop follows IPC
rect/window_rect and passes. Failures are retained in the correction record.
The initial audit source reconstruction is documented as reconstructed after
correction, not contemporaneously hashed. Current fixture corrections are not
additional executed evidence. Bit reproducibility needs independent builds and
remains NOT TESTED under this one-build budget.

Next smallest justified ticket: establish a reference focus state before its
baseline capture, then authorize one bounded same-static-binary run for measured
clipped input and splith return. Keep notices/maintainer designation/full ABI and
existing STEP20C graphics/generation/lifetime gates separate before any real
PKGBUILD change. No integration approval follows from this partial result.

The [source-only fixture](../../tooling/probes/step20c-static-runtime/README.md)
records commands, budgets and failed-check limitations. The run's field named
`source_box` used applied owner scene x plus IPC window offsets; its y=0 was an
estimate missing title decoration. Offline color bounds independently locate
visible content at H1 local `(482,25)..(800,598)`, consistent with global
x=-318 crossing. No claim of exact raw buffer y identity is made from that field.
The final parent audit checks contracts, delta, raw provenance and limitations;
no independent subagent review was invoked.

## Sealed integrity receipt

Source manifest: 1,397 entries, SHA-256
`ed55bd418595ca977c022fa98917a899072cf3b6f0fb15457db823081046e797`.
Evidence manifest: 146 entries, SHA-256
`e260ce5793ffc9a29ee4bfa2189663feeb6dc025bd46d3f5ddebccd225f3eef1`.
Both were created once and all entries reverified. This report and full delta
are outside the manifest set to avoid circular digests. Historical 1,892/143
manifests still verify through the pre-freeze snapshot mapping. No manifest
was regenerated or overwritten.

Final AST, shell/recipe syntax, local Markdown links, source-only fixture,
whitespace, stage identity/modes/hash, budget, protected system/source/recipe/
patch checks and owned-process/socket cleanup PASS. Runtime reference gate
FAIL is retained; input/standard return and broader tests NOT RUN / NOT TESTED.
No B commit, push, production edit or installation occurred.

## Static-runtime evidence freeze — 2026-10-13

The new freeze audit starts at main `4f4f3fefcdcf979f8be126d6671062ecb1d65b50`,
with both directly queried remote main references equal. Only the expected
documentation and source-only static-runtime fixture are included. The historical
PARTIALLY_FEASIBLE verdict and UNDECIDED architecture are unchanged.

All 1,397 source and 146 evidence entries verify against the original manifests.
The ten fixture files, including its README, remain byte-identical because their
absolute paths are sealed in the source manifest. Its LOCAL/UNCOMMITTED wording
and this report's earlier A/B labels describe the historical campaign at closure,
not the later publication state. No corrected runner is executed during freeze.

Independent offline RGB recount retains 23,807 changed H2 pixels and the complete
image bounding box; the reference interior is identical, 182,214 target pixels
remain on H1, and no target color appears on H2. These findings support a focus/
decoration fixture explanation without replacing the failed whole-H2 comparison.
The original scene-derived source_box is not an exact native buffer rectangle.
Input, splith return and popups remain NOT TESTED for this historical run.

D1–D4 remain approved only for documentation and private experiments. Static
linkage does not close semantic ABI, legal notice inventory, release/security
ownership or wider graphical gates. The next separately bounded gate reuses
the exact binary, normalizes the H2 reference before comparison, and measures
three button deliveries and standard clip removal. No new build or old-LAB run
is part of this freeze. STEP20C stays NEXT; production multi-output remains
NOT YET SUPPORTED.
