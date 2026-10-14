# STEP20C — minimal core ABI, package and integration decision

> EXPERIMENTAL / PARTIALLY_ADVANCED — 2026-10-14. Ticket `SWAYFX_MOSAIC_STEP20C_MINIMAL_CORE_BUILD_RUNTIME_AND_GPU_FIELD_GATE_V1`. Recommendation: **PRIVATE_CORE_NEEDS_TARGETED_EVIDENCE**. Evidence delta review ACCEPTED for experimental fidelity; final independent dossier review pending at this edition. Documentary publication PREPARED, not an executed publication receipt. STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT; STEP20D–G PLANNED; production multi-output NOT YET SUPPORTED.

LAB is `/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_/`, private and outside Git.
The report combines the [build/C evidence](STEP20C_MINIMAL_CORE_BUILD_AND_C_FAILURE_PATHS.md),
[graphics matrix](STEP20C_MINIMAL_CORE_GRAPHICS_QUALIFICATION.md),
[lifetime/damage/transaction limits](STEP20C_MINIMAL_CORE_LIFETIME_DAMAGE_AND_TXN.md)
and [GPU follow-up](STEP20C_GPU_FULL_FIELD_FRESHNESS_FOLLOWUP.md). It supplements
the [historical source-only report](STEP20C_MINIMAL_PRIVATE_INTEGRATION_CORE.md);
historical FROZEN evidence and consumed budgets remain unchanged.

## Identity, budget and lifecycle state

The private core SHA 256 is
`29baf31aa3eeed259825c87d0799fa5d3dc83710afb967154604eb1c6657f965`, Build ID
`1b42e557e38db3440ae8dcf7ac967e4132223365`. The distinct GPU diagnostic is
`1905a20fa72ebcc7ec47d1584a4653654280288096a20005199eb75673ac0383`, Build ID
`1505e31c3dc08d2a7799c2ee9e1b2705eb61f5fe`. Both are tied to the observed
wlroots SHA 256 `7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
No cross-binary qualification transfer is accepted.

| Resource | Actual consumption | Boundary |
| --- | --- | --- |
| Headless runs | 12/14:11 E and1 G1 | No retries; two conditional slots NOT EXERCISED |
| Output captures | 88:85 E and3 G1 | 180 maximum; failures remain consumed |
| Retained PNG files | 90 | 88 output captures plus two source markers |
| Core builds | One initial SceneFX and one initial Mosaic | Two per-component maximum; no correction core build |
| GPU builds | One distinct diagnostic SceneFX/Mosaic pair | Separate identity and evidence |
| Compositor sanitizer | Zero builds/runs | NOT RUN; C unit sanitizer results remain separate |
| Private stages | Stage1 only | No public package/install/rollback test |

The read-only final protection/budget/process audit records 12 unique run tokens,
166 reserved capture limits and 88 actual debits. Configuration/chain/camera/
move/click/grab/mutation action counts are 137/9/13/34/25/12/28. Its 316 protected
file bindings and 307 historical-reference bindings remain unchanged. All 12
outcomes report runtime removal; the audit finds zero private process candidates
and zero LAB sockets. These are the audit's recorded observations, not a new
execution performed for documentation.

The three initial E failures occur before PNG; they are spent attempts, not
controls. R2 has four runner exits 1/four 0; all E terminal IPC exits 1 with
compositor0 are preserved. Mechanical cleanup passes; process recovery is not
universal scientific client closure. G1 scientific cleanup is INCONCLUSIVE.
No unconsumed slot authorizes another run after documentary closure by itself.

| Lifecycle distinction | Actual state |
| --- | --- |
| PRIVATE_CORE_BUILDABLE | PASS for the exact reviewed private sources/build |
| PRIVATE_CORE_TESTED_MATRIX | PARTIAL, as the per-cell ledger below specifies |
| READY_FOR_INTEGRATION_REVIEW | NOT READY; targeted evidence and contract decisions remain |
| PRODUCTION_AUTHORIZED | FALSE |
| Documentary preparation | PREPARED at this edition |
| Final independent dossier review | PENDING at this edition |

Source and prebuild/delta reviewers accepted their scoped inputs. The evidence
delta reviewer checks 319 recorded hashes with 319 matches and no divergence,
accepting fidelity with E/F qualification PARTIAL. These scoped reviews do not
substitute for final independent review of the final dossier bytes. Actual
publication commits, remote refs and closeout status belong to the private
post-push receipt and final handoff, not a prospective assertion in this edition.

## Exact-pair ABI and private stage

The core is ELF64,6,744,472 bytes,0755, statically incorporates the private
SceneFX archive and has no SceneFX DT_NEEDED or RPATH/RUNPATH. `ldd -r` exits 0
without unresolved symbols observed. Private clip exports are present. Existing
non-graphical `LD_BIND_NOW --version` evidence has 43 bindings for40 unique scene
symbols. Layout measurements are node 112/tree 128 bytes, offsets parent 8,
enabled 32, visible 88, children 112. These checks qualify local observations for
the exact pair; they do not establish universal runtime ABI compatibility,
future update safety or absence of interposition hazards. The historical85
overlaps are not silently reclassified as defects or a new core inventory.

The actual archive SHA 256 is
`191ec14fc08c4aeb83e6b313c0f23cda67e10bebe15e29d47bfd192256286f3a`.
Compile-command/Ninja dependency inventory records 885 unique hashed files,
277 translation units and32 generated protocols/shaders. The build report
preserves the failed provenance helper and initially unrecorded Ninja exit,
with a separate later read-only exit0 record; no original receipt is rewritten.

Stage1 verifies exactly the following regular files, without symlinks:

| DESTDIR path | Mode |
| --- | --- |
| `/usr/bin/swayfx-mosaic` | 0755 |
| `/usr/share/licenses/swayfx-mosaic/SceneFX-LICENSE` | 0644 |
| `/usr/share/licenses/swayfx-mosaic/SwayFX-LICENSE` | 0644 |
| `/usr/share/licenses/swayfx-mosaic/wlroots-LICENSE` | 0644 |
| `/usr/share/licenses/swayfx-mosaic/INCORPORATED-NOTICES` | 0644 |

This passes file-shape validation under the
[approved private static contract](STEP20C_STATIC_RUNTIME_AND_PACKAGE_CONTRACT.md).
Notices remain PARTIAL / LEGAL_NOT_APPROVED; exact incorporation coverage,
full future package reproduction and named release/security ownership are
not closed. No full makepkg/package build or real install/rollback test is
claimed. The current [package contract](../PACKAGING.md), PKGBUILD/system
SceneFX dependency and one-binary production package remain unchanged.
Ordinary SwayFX and `/usr/bin/sway` remain independent fallback requirements.

## Evidence marker ledger

| Marker | Recorded result |
| --- | --- |
| MINIMAL_CORE_SOURCE_REPLAY | PASS |
| CORE_C_GEOMETRY_TESTS | PASS, extracted-body unit scope |
| CORE_OOM_POLICY | OOM_ABORT_EXPERIMENTAL; production availability open |
| CORE_SANITIZER_TESTS | PASS unit normal/UBSan/ASan; compositor NOT RUN |
| CORE_PRIVATE_BUILD | PASS |
| CORE_PRIVATE_ELF_ABI | PASS local ELF/relocation/layout checks only |
| CORE_PRIVATE_STAGE | PASS five-file shape; notices PARTIAL / LEGAL_NOT_APPROVED |
| CORE_GRAPHICS_PREFLIGHT | PASS for the frozen inputs actually executed |
| CORE_PRISTINE_STANDARD | INCONCLUSIVE, initial pre-capture fixture failure |
| CORE_HORIZONTAL | INCONCLUSIVE overall; first-chain PARTIALLY_FEASIBLE, standard return NOT EXERCISED |
| CORE_VERTICAL | INCONCLUSIVE, pre-capture fixture failure |
| CORE_FRACTIONAL | PARTIALLY_FEASIBLE for sampled scale 1.25 matrix, closure limits retained |
| CORE_R90 | PARTIALLY_FEASIBLE for sampled scale 1.25/R90 matrix, closure limits retained |
| CORE_DYNAMIC | PARTIALLY_FEASIBLE for sampled resize/clamp/migration/input |
| CORE_FULLSCREEN | INCONCLUSIVE, actual non-leaf ancestor but no comparable standard control |
| CORE_HIDDEN_OWNER | PARTIALLY_FEASIBLE hidden samples; full same-chain return NOT EXERCISED |
| CORE_SAVED_TIMEOUT | INCONCLUSIVE full scenario; native five-second timeout observed before ACK/teardown |
| CORE_FX | PARTIALLY_FEASIBLE; classic exercised, whole-H1 FAIL, shadow NOT EXERCISED |
| CORE_SAMPLED_APPLIED_INPUT | PARTIALLY_FEASIBLE |
| CORE_SAMPLED_DAMAGE | PARTIALLY_FEASIBLE |
| CORE_NATIVE_BUFFER_IDENTITY | NOT_PROVEN |
| CORE_GPU_LIFETIME | NOT_PROVEN |
| CORE_ATOMIC_GENERATION | NOT_PROVEN |
| CORE_COMPLETE_DAMAGE | NOT_PROVEN |
| GPU_FULL_FIELD_DESIGN_REVIEW | PASS for accepted scoped source/preflight review |
| GPU_FULL_FIELD_DIAGNOSTIC | INCONCLUSIVE, sole raw epoch rejected |
| GPU_WHOLE_FIELD_CAUSALITY | INCONCLUSIVE |
| CORE_PRIVATE_PACKAGE_ABI | PARTIALLY_FEASIBLE; exact-pair components pass, maintenance/package/legal gates open |
| CORE_FINAL_INDEPENDENT_REVIEW | NOT_PROVEN at this edition; final review pending |
| CORE_DOCUMENTARY_PUBLICATION | PARTIAL at this edition; PREPARED lifecycle state, no publication PASS asserted here |

`SWAYFX_MOSAIC_STEP20C_MINIMAL_CORE_BUILD_RUNTIME_AND_GPU_FIELD_GATE_V1=PARTIALLY_ADVANCED`
records the scientific advancement of this campaign. It does not mean
PRODUCTION_READY or supersede raw failures.

## Risks, reproduction scope and closing criteria

P0–P3 below prioritize remaining evidence/decisions; an unclosed gate is not
automatically a demonstrated product defect. The scoped reviewers report no
blocking product finding in the accepted evidence delta.

| Priority / fact | Identity, source and reproducer | Scope and closing criterion | Dependencies / human decision |
| --- | --- | --- | --- |
| P0 integration exclusion: production is not authorized | Exact core 29baf31, ticket and canonical architecture/package contracts | Preserve production boundaries until relevant gates and contracts are explicitly accepted | Separate production/merge/distribution decision; no automatic consequence of private success |
| P1 OOM availability: sidecar allocation failure aborts | Exact extracted SceneFX bodies, `c-tests-lifecycle` targeted second-allocation failure; three raw SIGABRT -6 | Unit path proven, compositor survival not proven; close with an accepted availability response and exact C/runtime evidence | OptionA remains experimental; alternativesB/C not demonstrated, no new public ABI/policy invented |
| P1 native lifetime and coherent applied state remain unproved | Core29baf31 E6 wire/native timeout; native scene transaction/source callbacks; no C3/PI identity transfer | Close native buffer identity, reference/retirement/release/GPU completion, coherent scene/input/present and complete damage independently | Required rendering/input coherence contract; choose mechanism only after documented decision |
| P1 whole-field effects uncertainty | Core29baf31 E7 whole-H1 FAIL 33,789/max RGB 6/5/1; G1 distinct1905a20 rejected first epoch | Preserve raw differences; acquire accepted discriminating full-field evidence with valid modifier-aware metadata and GL success/restoration observability | New scoped/reviewed experiment; no shader/clear/clamp change from an unaccepted hypothesis |
| P1 maintenance and distribution | Core exact-pair symbols/layout/providers, Stage1 and incorporation inventory | Complete notices/legal review, reproducible future package, dependency/security rebuild and exact-pair requalification plan | Name release/security owners; separate public distribution decision; all other pairs NOT QUALIFIED |
| P2 missing controls and transitions | Initial E0/vertical fixture failures, E1 second owner wrong ancestry, E4 no standard fullscreen control, E5 dismissed chain | New accepted fixture/scope for comparable standard/vertical, full standard return, actual fullscreen policy and viable hidden-owner return evidence | Offscreen-popup hide/dismiss/reposition/click-through UX remains UNDECIDED; no universal promise |
| P2 limited client closure and sanitizer scope | E1/E6 normal close unacquired, E2 helpers error 32/marker timeout, G1 clients1; unit sanitizers only | Attest normal client closure independently from terminal/process cleanup; native compositor sanitizer if justified by a new gate | Separate bounded scope and binary identity; no consumed retry |
| P3 evidence/publication completion | Final source/report/fixture bytes, exact manifests and scoped delta review | Final independent dossier review, compact public provenance and actual publication/closeout receipts | Publication lifecycle recorded truthfully; do not upgrade gates merely to finish documentation |

## Recommendation and next decisions

**PRIVATE_CORE_NEEDS_TARGETED_EVIDENCE** is the single recommendation.
The new core is actually buildable and passes its real extracted C tests and
sampled scale/R90/dynamic matrix. It still lacks a comparable new standard
control, full horizontal return, qualified fullscreen/hidden transition,
native saved/GPU lifetime and atomic-generation/complete-damage evidence.
G1's rejected first epoch cannot settle whole-field GPU attribution. These
facts justify targeted evidence, not a redesign conclusion or integration readiness.

The next human decisions are the production OOM availability response;
offscreen popup/fullscreen expectations where controls are incomplete;
release/security maintenance owners and legal distribution closure; and the
scope of any further targeted native/graphics/GPU gates. This report adopts
none of those decisions. Native compositor authority and Row0 borrowing remain
required, and [UX](../UX.md), AGENTS, production sources/tests, PKGBUILD and
the cumulative production patch are unchanged. No STEP20D or daily-driver
qualification follows. Private raw logs/readbacks/builds/core patches stay
outside Git; compact public evidence can record their hashes and limitations.

The [public source/provenance fixture](../../tooling/probes/step20c-minimal-core-gate/README.md)
preserves compact exact inputs and metadata. Its C extraction runners require
the external private source bodies; archived graphics runners cannot relaunch
consumed reservations. It contains no functional core patch, extracted core
body, GPU hook, binary or raw readback. It does not constitute an independently
redistributable source package or an authorization for a new experiment.
