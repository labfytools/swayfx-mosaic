# STEP20C static nested receipt semantic integrity gate

EXPERIMENTAL, offline only; semantic integrity gate READY_FOR_NEW_RUNTIME,
with independent acceptance of the final bound fixture and receipts.
Historical geometry gate remains INCONCLUSIVE. Architecture UNDECIDED;
STEP20C NEXT, production multi-output NOT YET SUPPORTED. No graphical run,
Mosaic/SceneFX build, client execution, capture, input, grab, camera or runtime reservation.

## Pre-implementation contract

The published `write_results.py` SHA-256 is
`94ddab595dd9765d3edaa7158a6a98319f3be6b15a62842e4b10eeacfb530cfa`.
Its `REQUIRED` names fifteen receipts; independent-review is the sixteenth
dependency. `write()` loads the receipts, computes bindings, and calls
`aggregate(evidence, hash_file, bindings)`. The pre-correction function checks status,
field presence, nine-case cardinality and some file hashes. It does not verify
the effective nested content. Three actual in-memory calls accept a bare PASS
input correlation, null rendered content/bbox/count/intersection, or nine
empty root objects. These are R02-A/B/C, not compositor observations.

The correction must use this entrypoint for all decisions. Downstream gates not checked after a failed prerequisite are also INCONCLUSIVE. Invalid evidence
returns INCONCLUSIVE with a named blocker and degrades its dependent marker;
invalid evidence is neither a compositor crash nor an architectural rejection.
Unexpected implementation failures cannot become PASS. Missing files and
malformed JSON must also produce blockers. No old receipts are overwritten.

## Required receipt schema and relationships

| Receipt | Required real content and types | Provenance and semantic relationship |
| --- | --- | --- |
| native-shm | positive integer buffer, rectangle size, positive stride, format, source, identity qualification | Replay actual SHM create/attach/ACK; 420×320, stride 1680, format 1; frame identity remains NOT PROVEN |
| xdg-configure | toplevel rectangle, positive initial/assigned ACK, initial configure, new-buffer boolean, popup qualification | Replay initial 0×0/ACK20 versus assigned 636×573/ACK21; no replacement buffer |
| applied | positive owner/PID/workspace, scene/window rectangles, titlebar, finite scroll, globalclip, generation qualification | Replay IPC/source/applied trace; scene (-320,0,640,600), titlebar25, scroll160, viewport(-800,0,800,600) |
| rendered | content rectangle, bbox, nonnegative integer count, visible intersection, native/destination distinction | Replay native geometry and retained image through existing typed model: (-318,25,636,573), bbox[482,25,800,598), 182214 pixels; output origin, clipping and area agree |
| positioner | integer flags, A/B local rectangles, content origin, predicted A/B, runtime qualification | Source-backed flags0; translate A then B from painted origin; prediction never runtime |
| historical-evidence | complete mandatory input path/hash mapping, diagnostic path, runtime qualification | Actual immutable files must exist; replay source/IPC/calibration/reference inputs are all verified |
| historical-replay | exactly nine unique campaign identities; owner/PID/workspace, origin, A/B/configured, protocol, clip, colors, callbacks, injections, buttons, lifecycle, file inventory, input correlation | Re-execute unchanged replay and R01 correlation on retained logs/IPC/images in a disposable directory, then compare every field, type and value |
| popup-root | nine case/origin/A/clip projections | Exact identity join and projection from independently replayed original data; owner is supplied by that joined replay, not fabricated in the historical root schema |
| popup-nested | nine case/B/protocol/standard/dismissal projections | B→A parent, distinct actual serials, configure/ACK/map and lifecycle replay; same identities/geometries/protocol as historical-replay |
| source-audit | pins, 17 unique source contracts, functions, claims, excerpts, source-version receipt/hash | Mandatory historical contract set; actual source/excerpt/version bytes verified |
| client-provenance | mandatory inputs, patch, adapted source, four protocols, comparison, three builds, C17 command receipts | Retained compilation receipts only; source/output/protocol hashes and flags verified, no new build or execution |
| assertion-register | full source/artifact inventories, AST records, counts, 145 historical assertions | Enumerate current AST and use the existing assertion checker for identities, classification and actual test correlations |
| assertion-coverage | entries, 145 assertions, coverage counts, unresolved list, runtime scope | Recompute from register; partial executed coverage remains explicit |
| offline-core-coverage | status, unproved list | Recompute necessary existing pure model guards from register; no invented runtime coverage |
| test-receipts | complete source inventory, unique actual tests, mode/line/contract observations, statuses | Fresh current code; genuine non-aggregator then negative-suite preflights bootstrap aggregation tests without forcing PASS; the complete mandatory negative test set and final full suite must pass before review |
| independent-review | ACCEPTED, independent=true, exact final source and evidence bindings | Genuine report file/hash, reviewer provenance, executed commands, mandatory independent attack results, findings and limitations; positive unit control has memory-only synthetic acceptance, rejected by the real file-backed writer |

Rectangles use [x,y,width,height]; PNG bbox uses [x1,y1,x2,y2).
IDs/serials/counts are integers (booleans are invalid), coordinates are finite.
Positive visible counts require positive valid bboxes; count cannot exceed area.
No semantic trust is granted merely because a file hashes to its own receipt.
Re-derived source observations must match, including owner, workspace, camera,
output origin, titlebar, source/destination and input local/global translation.

The fixed nine-campaign gate is intentionally scenario-specific. Standard
control `clip=null` is required and legitimate. Color `bbox=null` is legitimate
with zero pixels. Nested `standard=null` and `dismissal=null` are legitimate
only where their original scenario did not exercise that operation. Toggle
requires its real standard receipt; close_b requires explicit B close and A
survival in the original replay (the historical nested projection lacks that
field); outside/dismissal scenarios require real done/destruction and absence
of forbidden popup buttons. Unattributable early seat callbacks keep their
explicit NOT AVAILABLE label. Native-frame and atomic-generation qualifications
remain unproved. Missing scenario-required facts are invalid, never filled in.

## Freshness, mutation tests and independent review

Bind all fixture source files and all fifteen evidence files. The aggregator
checks the current source bytes and actual loaded evidence against these files;
review must contain the identical bindings. A source or receipt change after
review invalidates acceptance, even if a new matching author hash is supplied.
Inventories with defined mandatory sets reject omitted members. The historical
67/88-entry sealed manifests remain read-only and are never regenerated.

Order: reproduce R02; correct real aggregate; positive control; deletion,
null/{}/[]/empty-string mutations; cross-receipt contradictions; stale/missing
source/evidence/patch/review bindings; writer test in a private directory;
nine-case replay; new receipts; AST/Shell/Git/inventory; source freeze;
independent review of final bytes; binding verification; verdict; new manifests.
Each original counterexample has its own test and receipt. Tests use independent
deep copies and call the actual aggregate, with no replacement policy/mock.

One configured Astra/high final-reviewer independently reproduces attacks
without relying on the author's mutation suite. It records files/hashes,
commands/results, limits and ACCEPTED/CORRECTION_REQUIRED/NOT_PROVEN. One
bounded correction and delta review are allowed; unresolved material findings
keep INCONCLUSIVE. An accepted earlier version cannot sign changed bytes.

Marker dependencies retain the existing geometry/XDG/assertion/regression/
review groups; any invalid mandatory dependency prevents READY_FOR_NEW_RUNTIME.
READY means only readiness to request authorization in a separate ticket.
Static popup qualification and architectural conclusions are untouched.

## Results

Phase A was published at `bbd7da24036f741130b2ff542f429b416fb9c7e5` on both
origin/main and github/main, with a clean worktree at its gate. Phase B remains
local, uncommitted and unpublished. The historical verdict is not superseded.

`SWAYFX_MOSAIC_STATIC_NESTED_RECEIPT_INTEGRITY_GATE=READY_FOR_NEW_RUNTIME`

The final genuine independent review is ACCEPTED. The actual file-backed writer,
using that review rather than a synthetic test receipt, returns READY_FOR_NEW_RUNTIME
with all five markers PASS and no blockers. R02 is RESOLVED for this offline
fixture; R01/R03 retain their historical accepted status. No material finding
remains in the bounded review scope. Architecture remains UNDECIDED.

## Initial independent review and bounded repair

The initial Astra/high read-only audit rejects the version with B-01:
`write()` lets a JSON decoder RecursionError escape, leaving pre-existing
runner-readiness/offline-gate READY files unchanged. The direct reproduction
uses a 200001-byte rendered.json with 100000 nested arrays. The initial
CORRECTION_REQUIRED report and bindings are retained separately; no acceptance
of changed bytes is implied.

The authorized repair is limited to treating decoder/encoder RecursionError
as an invalid required receipt, and a real writer regression proving both
old READY artifacts become INCONCLUSIVE. No parser framework, runtime change
or scientific dataset limit is introduced. The current-code offline
validation was rerun and the repaired delta submitted to an independent reviewer.


## Final executed evidence and limitations

Private laboratory: `/home/fy59/swayfx-mosaic-receipt-integrity-cof0umuk/`.
Historical laboratory: `/home/fy59/swayfx-mosaic-static-nested-geometry-replay-a56csvoo/`.
The original `aggregate()` and fixture are retained in `sources-before/`; the
initial reviewed version is in `reviewed-fixture-v1/`, and final code in
`proposed-fixture/`. `raw/phase-B-complete.diff` records the complete local delta.

| Executed check | Final observed result |
| --- | --- |
| Non-aggregator bootstrap | 145 tests PASS, genuine receipts |
| Mandatory negative bootstrap | 204 tests PASS, genuine receipts |
| Final full offline suite | 206 tests PASS, 474.694 seconds |
| Original R02-A/B/C | 3 separate mutations INCONCLUSIVE with named blockers |
| Field deletion | 2668 mutations INCONCLUSIVE |
| Null / empty object / empty list / empty string | 10604 invalid mutations INCONCLUSIVE; legitimate omissions separately accepted |
| Cross-receipt contradiction | 173 mutations INCONCLUSIVE |
| Stale/missing files, source/patch/review bindings | 30 mutations INCONCLUSIVE |
| Recorded mutation total | 13478 rejected, no recorded invalid mutation READY |
| Positive complete receipt control | READY_FOR_NEW_RUNTIME; SYNTHETIC_IN_MEMORY_ONLY |
| Historical replay | All nine campaigns PASS through unchanged replay/R01 functions |
| AST register | 2371 sites, including 145 frozen historical assertions; 314 positive+negative, 872 positive-only, 1179 unexecuted |
| Pure model coverage | No unresolved pure invariant; partial executed coverage remains explicit |
| Independent final delta | 12 required attacks rejected, one memory positive accepted, three real-writer controls PASS |
| Actual accepted writer | READY_FOR_NEW_RUNTIME, five PASS markers, no blockers; final source/receipt bindings unchanged |

The initial independent Astra/high report is CORRECTION_REQUIRED due to B-01.
One bounded repair was performed, followed by the read-only Sol/medium delta
review ACCEPTED for the new 18-source/15-receipt bindings. These are distinct
reviews; the older review was never reused as acceptance of changed code.
The final report is `independent-review.md` (SHA-256
`311af1fe694d1bde88884afa21ef16a4fe908d6cfa47b6cbed515d1a21fedc9e`),
and its receipt is `results/independent-review.json` (SHA-256
`4d8401978e69a6c54f2f6144ba06deff4952671bc8e1ae3008376ab6ffe01e09`).

Final source SHA-256 values:

- `write_results.py`: `9202522721caa1815d3824a3db315c8cdb27e607ce1678907774faa1c9c14c0c`.
- `receipt_integrity.py`: `3f32003f7de74336f2be17e063295d51f683d40936568fd8aebebeb5d3f9b45f`.
- `tests_offline.py`: `0e188fe64d0c3d8a6fda227bf4ef8b31658b86390b5ed73d97d0e3bf851b67d1`.

Commands and exit codes are retained in `results/commands.json`, reviewer
receipts, final validation receipts and `raw/`. Intermediate author test failures
(including an incomplete assertion inventory and test-bootstrap completeness)
were corrected before freeze and remain preserved. The delta review's first
static-harness attempt exited 1 due to a Path conversion typo; its correction
and successful retry are retained. None is concealed as a successful run.

The existing offline suite prepared three client-only C17 utilities in disposable
test directories; no client was executed, and neither compositor nor SceneFX
was built. No new image, serial, pointer injection, grab, camera operation,
compositor socket, runtime reservation or installation was produced. Retained
image parsing is offline replay, not capture. Protected production files,
package, cumulative patch and historical sealed manifest entries are unchanged.

Freshness binds raw receipt bytes as well as canonical parsed content and source
bytes. A formatting change also expires a reviewed file. New source or receipt
bytes require new independent acceptance; matching freshly calculated author
hashes alone cannot preserve a prior ACCEPTED verdict. Source/evidence manifests
are sealed only for this new laboratory after final checks. Historical manifests
remain exactly the published 67/88-entry originals.

This finite mutation campaign and independent audit support the fixed historical
fixture contract; they do not prove arbitrary future receipt schemas or universal
parser/resource resilience. READY is solely permission-request readiness.
Native-frame identity, atomic transaction generation, GPU-reference lifetime,
new static popup geometry/pixels/input/grabs/dismissal/standard return, and the
remaining output/damage/effects/ABI matrix remain NOT TESTED or NOT PROVEN as
previously documented. No architectural or UX decision follows. STEP20C stays
NEXT and production multi-output stays NOT YET SUPPORTED. The smallest next
step is a separately authorized static-popup runtime ticket; this ticket
performs no such run.

## Historical receipt-integrity evidence freeze — 2026-10-13

Ticket `SWAYFX_MOSAIC_STEP20C_RECEIPT_FREEZE_AND_STATIC_NESTED_RUNTIME_V1`,
phase A, preserves the accepted R02 version for publication. Statements above
about local/unpublished phase B and absent runtime authorization describe the
previous offline ticket. This freeze changes no reviewed fixture byte and no
sealed laboratory file; the separate runtime handoff requires its own evidence,
authorization and independent acceptance.

The 76 source entries and 199 evidence entries in the receipt-integrity LAB
were individually verified. Manifest SHA-256 values are respectively
`dbd96db3f19f6eb60fc8be13c62b1e71944a759b481d008a7825b3720cf525ce` and
`f00ca54e39bff031a5bda585ea52cfebe9239e71b4c7ee7dc5c41a930e1598b3`.
The final report and review receipt hashes remain exactly those recorded above.
All 18 source and 15 mandatory receipt bindings match independent acceptance.
The actual aggregate was freshly called: READY_FOR_NEW_RUNTIME, five PASS
markers, no blocker. The three original R02 counterexamples were freshly
rejected; a disposable real-writer B-01 check replaced both prior READY files
with INCONCLUSIVE. No synthetic independent acceptance was persisted.

The retained 206-test, nine-replay and 13478-rejected-mutation results were
verified from their immutable receipts, not relabelled as a newly executed full
suite. Python AST, Markdown links, complete diff including untracked files,
310 protected paths and `git diff --check` passed. No runtime, build, capture,
client execution, socket or reservation belongs to phase A. Historical initial
CORRECTION_REQUIRED and final ACCEPTED reviews remain separate. Architecture
UNDECIDED; static popup runtime NOT TESTED; STEP20C NEXT, production multi-output
NOT YET SUPPORTED.
