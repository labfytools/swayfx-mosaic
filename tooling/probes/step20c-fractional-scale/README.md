# Fractional-scale source fixture

**EXPERIMENTAL / preserved source-only evidence, PARTIALLY_FEASIBLE.** Read the
[protocol](../../../docs/design/STEP20C_FRACTIONAL_SCALING_PROBE.md) first.
Reconstruct private pinned sources through the effects preparer in a new full
clone. The scaling runner adapts only fixture Python; no render,
clip, damage, shader, input decision or ABI changes. Artifacts stay in the
single temporary lab. All camera runs reserve from a two-pair global ledger.

## Reproduction from sources

Use a full clone containing base commit
`aefee44c636a1529eca9a082658fd80b4d17cf5f` and the preserved fractional
fixture. No historical lab is required. `prepare.sh` rebuilds pinned
private SceneFX/Mosaic and C17 clients through the preserved preparer chain,
then builds a pristine SwayFX 0.6 standard control. It prints a fresh LAB path.
All generated protocols, libraries and binaries stay there; nothing is installed.

```sh
sh tooling/probes/step20c-fractional-scale/prepare.sh
# Set LAB to the exact printed path; use this same lab for the entire campaign.
python tooling/probes/step20c-fractional-scale/test-budget.py
python tooling/probes/step20c-fractional-scale/run.py "$LAB" control G0 --scenario calibration
python tooling/probes/step20c-fractional-scale/run.py "$LAB" control G1
python tooling/probes/step20c-fractional-scale/run.py "$LAB" private_standard G1
python tooling/probes/step20c-fractional-scale/run.py "$LAB" private_mosaic G1 --camera-pairs 1
python tooling/probes/step20c-fractional-scale/run.py "$LAB" control G2
python tooling/probes/step20c-fractional-scale/run.py "$LAB" private_standard G2
python tooling/probes/step20c-fractional-scale/run.py "$LAB" private_mosaic G2 --camera-pairs 1
python tooling/probes/step20c-fractional-scale/analyze.py "$LAB"
```

Every run first calibrates both ordinary references. Failed runs are retained
and consume any reserved pair. A lab-wide flock serializes runners, persisted
reservations survive launch failure/interruption, and a missing ledger in an
existing campaign is rejected. Camera default is zero; after two reservations,
only zero-pair variants are accepted. `test-budget.py` executes the actual
reservation block with the launch tail replaced; it never launches a compositor.
Do not use another lab or delete the ledger to bypass exhaustion.

For G1/G2 root/nested comparisons, use `--scenario outside --placement
both_cross` in each mode, with zero pairs. The existing b_cross variant is the
default; its separate outside click is at logical (20,190). Root-A forbidden
input uses a separate Mosaic both_cross run with `--outside-y 140`. Optional
G3 main uses zero pairs in each mode after G1/G2 calibration succeeds.
The fully qualified matrix is explicitly listed in the report; absence of a
scenario in this short command example is not a PASS.

## Coordinate and artifact contract

The runner sets requested physical modes and scales in private configs, checks
get_outputs logical 800×600 rectangles and normal transforms, and gives grim
an explicit per-output scale. It checks actual PNG sizes against physical modes.
Global pointer points remain logical: sent_x=global_x+800, extent 1600×600.
Calibration records requested placement, measured surface origin, independent
local-motion delta and left/right delivery. IPC frame coordinates are separate.

The analyzer retains full-image differences, predeclared logical/physical ROIs,
complete edge columns, exact popup colors, configured popup-box edge conversions,
contrast/luminance metrics and settled damage coverage. Damage trace extents are
already physical. Equality of full neighboring PNGs also detects non-exact-color
filtering pixels. Exact-color counts alone are not treated as a leak detector.
Captured images and input logs are related observations, not atomic frame identity.

All attempted runs, including ten failed early calibration fixtures, remain in
`/tmp/swayfx-mosaic-nested-grab-0DfvGCxn` for this execution. The final adapter
saves a uniquely named generated source per attempt and a source copy per run.
Earlier reusable calibration source names were overwritten: exact generated
sources for every early failed attempt are not all retained. Their logs,
configurations, captures and documented fixture defects are retained. This
limits forensic replay of those failures, not the final source-only reproduction.
The final source/evidence manifests live outside Git in fractional-results.

## Observed qualification

G1/G2/G3 requested modes and scales were applied. Both standard controls prove
popup and shadow overflow; private Mosaic's neighboring popup/FX1/FX2 images
remain unchanged, while visible blur and permitted popup pixels persist.
Two G1/G2 camera pairs restore exact popup PNGs. Result is PARTIALLY_FEASIBLE:
opaque tiled overflow controls, interior Mosaic shadow, optimized caches,
restored Mosaic hit before layout return and intermediate frames are unqualified.
No production correction is implemented. STEP20C stays NEXT, multi-output
NOT YET SUPPORTED. The original fractional campaign was local during the effects freeze; its
source-only evidence is now preserved separately.

## Freeze replay: no new camera pair

For the fractional freeze, run G1 calibration and G1/G2 three-mode
`--scenario outside --placement b_cross --camera-pairs 0`. Do not run the
camera commands in the historical campaign example above during this freeze.
The historical two-pair ledger is exhausted and remains authoritative for
its camera evidence; a fresh rebuild supplies no additional camera evidence.
