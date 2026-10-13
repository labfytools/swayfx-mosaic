# Static nested geometry replay — EXPERIMENTAL offline fixture

This fixture corrects the frozen `../step20c-static-nested-grab/` experiment.
It does not implement production STEP20C and does not qualify the new static
popup scenario. Architecture remains UNDECIDED; new runtime is NOT TESTED.
The protocol was written before implementation in
[`STEP20C_STATIC_NESTED_GEOMETRY_REPLAY_GATE.md`](../../../docs/design/STEP20C_STATIC_NESTED_GEOMETRY_REPLAY_GATE.md).

The current ticket authorizes **offline reads, Python tests, protocol generation
and client-only C17 compilation**. It authorizes no compositor/client execution,
new capture, pointer, grab, camera, runtime/socket creation or execution ledger.
No runtime command is permitted by this README. Historical LABs, fixtures,
manifests and ledgers are read-only. Generated output belongs outside Git.

## Model and corrected paths

`model.py` uses immutable, half-open, tagged rectangles and owner/workspace/
observation-window provenance. NativeSHM, XDGConfigure, AppliedContent,
SceneGlobal, PopupLocal, GlobalViewport and OutputPNG are distinct. `content`
accounts explicitly for borders, titlebar and view offsets; `to_png` applies the
measured output origin after visible intersection. Scaling/transform without
measurement, pending state and mismatched provenance fail closed.

`observations.py` keeps native buffer create/attach/initial ACK/map separate
from subsequent configured destination/ACK. The historical client maps its
420×320 native SHM after configure0×0/ACK20, then receives636×573/ACK21 without
a replacement buffer. Applied content(-318,25,636,573), captured bbox
(482,25,800,598) and182214 blue pixels are separately corroborated. PNG does not
prove the identity of the native committed buffer/frame or atomic transaction.

`pixels.py` validates exact RGB masks using the same conversions for replay and
future runner. It accounts for output origin, inherited clip and B occluding A.
The opening point must also fit actual native input bounds: SceneFX destination
size alone does not enlarge the wlroots surface input region.

`run.py` is prepared for a separately authorized future ticket. E1 and E2 have
separate processes/owner identities and real left-button serials. Actual
configure/ACK/map, not the positioner request, drives A/B and pointer geometry;
missing crossing reports NOT EXERCISED. A bounded root/owner window must identify
one consistent root tree. Standard return remeasures owner/content origin and
root/tiled clip state with A/B still mapped, then measures B, explicitly closes
B, measures surviving A and finally compares the exact H2 reference. Dismissal
is separate from an invisible popup receiving a button. Cleanup records actual
IPC stdout/stderr/exit, handled compositor exit, process codes, reaping and
rescue. Missing scientific measurements cannot become success after clean exit.

`authorization.py` refuses before locks/debits/processes/runtime creation unless
a distinct explicit future authorization, completed accepted independent review,
ready marker and fresh registered LAB are present. The current offline LAB and
historical failed LAB are forbidden. This ticket does not initialize a runtime
budget. `ledger.py` creates ledgers only in test-owned temporary directories;
future registration is outside this ticket. Debits lock, validate and fsync
before returning; exhaustion, concurrency, corruption and failed compound
reservations are exercised, without refunds or resets. Future maxima remain
1 run,2 chains,4 grabs,2 camera operations (one per chain),1 transition,9 clicks,
16 PNG,24 positions,150 seconds.

## Exact offline commands

From the repository root, using the newly registered offline LAB (which must
already have `raw/` and `results/`):

```sh
LAB=/home/fy59/swayfx-mosaic-static-nested-geometry-replay-a56csvoo
FIXTURE=tooling/probes/step20c-static-nested-geometry-replay
PYTHONDONTWRITEBYTECODE=1 python "$FIXTURE/prepare_clients.py" "$LAB"
PYTHONDONTWRITEBYTECODE=1 python "$FIXTURE/replay.py" "$LAB"
PYTHONDONTWRITEBYTECODE=1 python "$FIXTURE/tests_offline.py" "$LAB"
PYTHONDONTWRITEBYTECODE=1 python "$FIXTURE/assertions.py" "$LAB"
PYTHONDONTWRITEBYTECODE=1 python "$FIXTURE/assertions.py" "$LAB" --check
PYTHONDONTWRITEBYTECODE=1 python "$FIXTURE/write_results.py" "$LAB"
git diff --check
```

Preparation copies versioned nested/pointer/reference plus its included saved
client source, applies the byte-identical placement patch in private storage,
regenerates protocols and compares exact retained files. It compiles three
utilities with `-std=c17 -Wall -Wextra -Werror -Wno-unused-parameter`, without
executing them. No Mosaic/SceneFX build, package staging or installation occurs.
Future runtime requires only versioned sources and freshly discovered identities;
it does not read the old temporary historical LABs. Offline replay currently
reads the frozen failed LAB and old nested LAB explicitly; absent artifacts are
NOT AVAILABLE / NOT REPLAYED, never manufactured.

## Coverage and review

`assertions.py` enumerates every historical assertion (145), Defect/exit raises,
condition, resource/validation call, coordinate operation and latest/index
selection, plus the proposed runner/model. Source hashes and AST keys make
missing, duplicate, unclassified, stale and fabricated test receipts fail closed.
Per-entry positive/negative IDs refer to executed line or exact failed named
contract receipts. A reached line does not prove every conjunct. Retired history
has an explicit rationale; runtime-only observations remain NOT TESTED. The
register-format tests qualify only the checker itself, never scientific facts.
Core pure model/conversion/provenance/ledger/authorization/mask guards need real
positive and negative receipts. All remaining necessary unproved guards prevent
readiness. Inventory/classification completion is distinct from branch coverage.

`write_results.py` emits explicit readiness and requested JSON aliases. It never
signs the independent review marker. The independent configured reviewer must
review the final source delta, E1/E2/standard/cleanup, register and evidence and
write `independent-review.md/json` in the LAB. Before that review, the fixture is
**INCONCLUSIVE / prepared for independent review**, never READY. Manifests are
sealed only after parent review and final correction, outside this fixture.


## Bounded independent-review repairs R01–R03

The initial independent report remains immutable and CORRECTION_REQUIRED.
These repairs belong only to this new offline fixture and its external LAB.
They provide no new runtime result and no architectural decision.

R01: `correlate_historical` validates every identifiable local callback against
actual configured A/B and fresh standard origins through the shared
`pointer_local` predicate. The versioned injector starts at1000; motion and
button wire times bind each click to its global action. Wire callback numeric
values and surface identities must agree with client callbacks. Automatic
map retargets use the previous global point when the next motion precedes the
next button; surviving A after B close retains its observed local point.
Early seat callbacks before the first identifiable injected enter are retained
as NOT AVAILABLE / NOT REPLAYED with their scope. Software layout motion keeps
its actual wire time and last injected point; it acquires no fabricated
injection timestamp. All buttons are retained, paired and checked; the final
forbidden action is separated from earlier legitimate visible buttons and its
actual observed events feed dismissal. Corrupted coordinates, recipients,
extra invisible buttons and button order fail closed.

Historical R02 disposition (published freeze): `aggregate` was the single gate implementation used by writer and tests.
SHM, XDG/configured geometry, source contracts/pins, client provenance/C17,
all nine historical cases, register/coverage/core and test receipts are
mandatory and checked for freshness and structural presence. The bounded
review demonstrates that effective semantic completeness is still insufficient;
null geometry and bare PASS/empty popup records can evade these checks. An independent ACCEPTED review must bind the exact
`source_delta` and `evidence_sha256` published in runner-readiness; stale
acceptance blocks readiness. Marker values are exact PASS or INCONCLUSIVE;
`marker_scope` describes their limited offline meaning separately. Synthetic
acceptance used in tests exists in memory only. No author signs a review.

R03: the runner calls shared `terminal_exchange`, with injected executor/wait
functions in offline mocks. It stores the obtained IPC code and stdout/stderr
before fallible compositor wait, then records compositor exit/error separately.
IPC7 followed by wait timeout preserves7 and both streams, and stays a scientific
failure. Invocation failure keeps an explicit null IPC code. Completed measures
plus a clean handled compositor exit may retain IPC1 as a transport incident;
incomplete measures cannot become scientific success.

New aggregation negative receipts record the specific false gate and caller
line. They qualify offline rejection decisions, not graphical observations or
all conjuncts. The exhaustive current AST and all145 frozen historical asserts
remain inventoried. Re-run the offline sequence after source changes before
handing the final unsealed fixture to the parent for bounded review.


## Historical offline disposition — INCONCLUSIVE / NOT READY

The independent tester ran195 tests with0 failures and all9 historical cases.
The bounded independent reviewer ran65 targeted tests PASS and resolved R01/R03,
but demonstrated R02 remains blocking for readiness: bare PASS input correlation,
null rendered values, or nine empty root records each produce erroneous synthetic
READY with the actual aggregate. The parent independently reproduced all three.
See the linked geometry-gate report for the retained findings, tested scope and
final assessed gate matrix. LAB/bounded-review.md and results/bounded-review.json
record CORRECTION_REQUIRED. Initial Astra report remains unchanged.

No independent acceptance exists. Actual readiness remains INCONCLUSIVE.
The four raw technical PASS labels do not prove effective receipt completeness.
The fixture is prepared but NOT READY; run.py must remain unexecuted. The next
step is a separately scoped offline correction of aggregate's semantic-content
guards and their negative regressions. No new runtime/budget is authorized.

## Local R02 semantic integrity correction

See [the receipt contract](../../../docs/design/STEP20C_STATIC_NESTED_RECEIPT_INTEGRITY_GATE.md).
`aggregate()` remains the single decision function used by `write()` and tests.
`receipt_integrity.py` replays the original data through existing geometry,
protocol and R01 correlation functions in disposable offline directories, and
compares every typed receipt field. It uses the existing AST checker and checks
complete mandatory file inventories. Null clips in standard controls, zero-color
null bboxes and scenario-specific absent standard/dismissal observations remain
legitimate; required toggle/close/dismissal observations cannot be deleted.
No historical receipt, raw log, image or sealed manifest is rewritten.

Bindings cover all fixture sources, all mandatory receipt file bytes and the
canonical parsed content. A changed source/receipt loses prior acceptance.
Unit M0 acceptance is synthetic, explicitly memory-only. The real writer only
reads the external independent review; it never signs acceptance. Final readiness
is determined by that exact bound review and the genuine test receipts.

In a new offline LAB, run the existing replay, run `tests_offline.py LAB --preflight`,
then `assertions.py LAB`. Copy these genuine receipts under `LAB/preflight/results/`
before running `tests_offline.py LAB --negative-preflight`. Regenerate the AST
receipts and replace the new LAB preflight snapshot with these genuinely executed
negative-suite receipts, then run `tests_offline.py LAB` for the final validation.
This prevents circular test bootstrapping
without forcing PASS or substituting old source hashes. Regenerate the final
AST receipts, freeze source/evidence bytes, and request independent review.
Initial preflight covers non-aggregator tests. Negative preflight collects all
required negative test IDs without claiming M0 readiness. Final validation uses
that complete snapshot and must pass its positive controls as well. The suite
executes the R02/mutation/writer tests. No synthetic review file is written.
All generated output belongs outside Git. These are Python/offline operations
only; no runtime command or ledger initialization is authorized.

The historical INCONCLUSIVE verdict above remains frozen. The local semantic
gate can establish only readiness to request a separate future authorization,
never static popup success. R01/R03 and the runner are unchanged. Phase B is
local, uncommitted and unpublished.

The bounded B-01 repair treats JSON decoder/encoder recursion exhaustion as
malformed required evidence. The real writer must replace pre-existing READY
artifacts with INCONCLUSIVE; decoder failure never retains a qualified gate.
This is receipt error handling, not a compositor/SceneFX rejection.
