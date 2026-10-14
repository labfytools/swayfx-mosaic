# STEP20C — minimal private core graphics qualification

> EXPERIMENTAL — 2026-10-14. Ticket `SWAYFX_MOSAIC_STEP20C_MINIMAL_CORE_BUILD_RUNTIME_AND_GPU_FIELD_GATE_V1`. Eleven E runs executed once; measurement, raw runner exit, terminal IPC and client closure remain separate. Evidence delta review ACCEPTED for experimental fidelity; final dossier review pending at this edition. Documentary publication PREPARED. STEP20C NEXT; production multi-output NOT YET SUPPORTED.

LAB is `/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_/`, outside Git. Paths
below identify private local evidence, not a self-contained public distribution.
The [build/C report](STEP20C_MINIMAL_CORE_BUILD_AND_C_FAILURE_PATHS.md) records
the exact parents, private repair, unit tests and build. The
[integration decision](STEP20C_MINIMAL_CORE_ABI_PACKAGE_AND_INTEGRATION_DECISION.md)
records aggregate limits and remaining gates. Historical reports remain immutable.

## Exact identities and preflight

The core is `LAB/mosaic-build/sway/swayfx-mosaic`, SHA 256
`29baf31aa3eeed259825c87d0799fa5d3dc83710afb967154604eb1c6657f965`, Build ID
`1b42e557e38db3440ae8dcf7ac967e4132223365`. The observed wlroots library is
`/usr/lib/libwlroots-0.20.so`, SHA 256
`7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837`.
Core observations do not qualify A/G, historical diagnostics or the distinct
new GPU diagnostic. E0-pristine uses the pristine control, not the core.

Initial preflight accepted 1,095 files, manifest
`9c75d2249a45d2a9cbdbdb3e0cbff91db82bb89b14d6f580ca12a9ed1ed0b705`.
All three initial attempts failed before captures on
`AttributeError: 'NoneType' object has no attribute 'endswith'` while inspecting
an ancestor's `floating` field. They spent their reservations and were not
retried. Offline fixture repairs and reviews before the remaining cases produced
the R2 manifest `5e49909975ea6776a677280a4e444d5014699bf36b68c68fba3345626b196fd3`
with 1,097 files and review
`0e7525b69fdd3e3f75b5c62fb0c3c833557024c6153c3ee033c2d9eebe9d66d0`
ACCEPTED. This is fixture repair before new reservations, not a core algorithm
change or a rerun of E0/vertical.

Private headless runtime directories, Wayland displays and explicit IPC sockets
were used. Actual logs identify the EGL/Mesa/radeonsi renderer; a requested
renderer environment variable alone is not treated as proof. Each scenario has
its own config, startup/maps/output observations, event log, receipt and raw
stdout/stderr/exit under `LAB/graphics/runs/<case>/run/` and the execution folders.

## Executed matrix

Capture counts are output-capture debits. The fractional and R90 cases each
also retain one marker-source PNG, excluded from capture counts.

| Case | Raw runner exit | Measurement outcome | Output captures | Retained boundary |
| --- | ---: | --- | ---: | --- |
| E0-pristine | 1 | INCONCLUSIVE | 0 | Ancestor fixture failure before comparable standard control |
| E0-core | 1 | INCONCLUSIVE | 0 | Same failure before standard-layout measurement |
| E2-vertical | 1 | INCONCLUSIVE | 0 | Same failure before vertical pixels/input |
| E1 | 1 | INCONCLUSIVE | 6 | First chain sampled; second ancestry fails before standard return |
| E2-fractional | 0 | PASS, sampled | 9 | Scale1.25 grabs/pixels/input/dismissal; marker teardown timeout retained |
| E2-r90 | 0 | PASS, sampled | 9 | Scale1.25/R90 grabs/pixels/input/dismissal; same teardown limit |
| E3 | 0 | PASS, sampled | 17 | Resize/clamp and same-owner workspace migration/input |
| E4 | 1 | INCONCLUSIVE | 12 | Actual current fullscreen ancestor; comparable standard control absent |
| E5 | 1 | NOT_EXERCISED for full scenario | 10 | Hidden-owner pixels/input partial; same-chain return absent after dismissal |
| E6 | 1 | INCONCLUSIVE | 8 | Natural timeout observed; frozen held-serial validator rejects receipt |
| E7 | 0 | PARTIALLY_FEASIBLE | 14 | Classic blur exercised; whole-H1 return FAIL; shadow unexercised |

The E matrix spends 11 runs and 85 output captures, retains 87 PNG files,
and does not contain a successful new pristine standard control. All E terminal
IPC commands return 1 while the compositor exits 0. Raw R2 runner exits are
**four 1 / four 0**, in addition to the three initial exits 1. The separate
`LAB/gpu-execution/r2-count-discrepancy.json` corrects an earlier aggregate
progress statement of three/five; per-run raw files and historical summaries
remain unchanged. A runner exit 0 is not a universal terminal-IPC PASS.

## Popup geometry, input and remaining transitions

E1 uses two horizontal headless outputs with the Mosaic owner on H1 and a
whole-H2 stable reference. Its first TOPLEVEL→A→B chain has real
`wl_pointer.button` grab serials 31 and 40, native A350×170 and B300×130.
A is at `(-218,105,350,170)`, B at `(-118,165,300,130)`, both actually cross
x=0. Sampled H1/H2 color counts are owner 142,794/0, A24,080/0, B15,340/0.
Outside input yields `popup_done` and destruction B then A, with no invisible
popup button delivered. The second owner opens on workspace 2/H2/splith rather
than the intended Mosaic ancestry; validation stops before the standard-return
path. That transition, B-close/A-survival and final standard input are
NOT EXERCISED in this core campaign. First-chain evidence is PARTIALLY_FEASIBLE;
the global E1 result remains INCONCLUSIVE.

E2-fractional has H1 physical 1000×750, scale 1.25, logical 800×600 at x=-800;
H2 is800×600 scale1. E2-r90 has H1 physical 750×1000, scale 1.25, transform90,
the same logical output and negative origin, with asymmetric marker evidence.
Each has real grab serials 33/42 and the same logical A/B crossing geometry.
H1/H2 color counts are owner 223,038/0, A37,650/0, B23,961/0. Visible input,
forbidden popup input and sampled outside dismissal pass; reference button
pairs are retained. These samples do not promise universal click-through.

E3 resizes H1 logically800→960→800 and moves the same workspace 6 and owner 10
H1→H2→H1. The clamp is960 after relative request1920 with three children and
gaps0; the existing 640 minimum is an experimental source fact, not final UX
sizing. Four input checks pass at recorded global points `(-273,168)`,
`(-275,168)`, `(366,168)` and `(-434,168)`. Native grab serials 40/49 persist
in the sampled chain. No universal transaction atomicity follows.

E4 observes owner 9 with fullscreen0 beneath non-leaf container 10 with current
fullscreen1; workspace 6 also reports a fullscreen marker. The non-leaf actual
ancestor, rather than that workspace marker alone, establishes the exercised
ascendance. Real grab serials 49/58 and nested captures/input are retained.
Without a comparable standard fullscreen control, exemption/cross-output
policy remains INCONCLUSIVE; an absent clip is not classified as a leak by fiat.

E5 samples hidden-owner masking and input, then the outside click legitimately
causes popup_done and destroys A/B before camera restoration. The same-chain
return is NOT EXERCISED. This does not settle hide/dismiss/reposition UX.
E6's timeout and E7's rendering limits are detailed in the
[lifetime/damage report](STEP20C_MINIMAL_CORE_LIFETIME_DAMAGE_AND_TXN.md).

## Closure, review and reproduction boundary

Every E runner receipt labels `scientific_cleanup=PASS` and records private
runtime removal. That label is the runner's process-recovery gate, not proof
that every client closed normally with Wayland error 0. E1/E6 normal client
closure is not acquired. E2 owners report error 0, but reference/filler helpers
report error 32 after compositor stop; each marker swaybg reaches a three-second
cleanup timeout. E3/E4/E5/E7 normal closure is attested for the relevant clients;
E7's three FX clients terminate error 0 normally before compositor shutdown.
Mechanical cleanup and protocol/normal closure therefore remain separate.

`LAB/graphics-execution/summary.json`, `LAB/graphics-execution-R2/summary.json`
and their per-run manifests preserve hashes and raw observations. Existing
commands are recorded as `python -B graphics/run.py <case>`; they are provenance,
not instructions to rerun a consumed reservation. Any future experiment needs
its own accepted scope, fixture gate and budget. The evidence delta review
checks 319 hashes without divergences and accepts fidelity with E/F qualification
PARTIAL. Final independent dossier review is pending; publication is PREPARED
at this edition, with actual publication identities reserved for the private
post-push receipt and final handoff. No production source, UX or package change.
