# Private CORE recovery graphics fixtures

EXPERIMENTAL, source-only. No production implementation, dependency, compositor
build or live-desktop operation. Historical E runs and laboratory are immutable.
The new laboratory is `/home/fy59/swayfx-mosaic-core-recovery-qmhckba5`.

`parent-provenance.json` records every parent source byte at commit 70954e26.
Changed Python modules are fresh fixture sources; changed C clients retain SHM
protocol buffers until observable release, emit explicit close receipts and
separate those releases from native GPU retirement. Generated protocol C/headers
remain in the historical source directory and are copied only to the private
LAB by `prepare.py`. No generated binaries, protocol files, PNG or logs belong
in this source directory. The private LAB `source-delta.patch` is a textual parent/new comparison.

From the repository root:

```sh
python -B -m unittest discover -s tooling/probes/step20c-core-recovery/graphics -p test_recovery.py
python -B tooling/probes/step20c-core-recovery/graphics/replay.py
python -B tooling/probes/step20c-core-recovery/graphics/prepare.py
```

Preparation compiles only five private C17 clients and does not connect to
Wayland. Copy the reviewed fixture Python/config/source tree into LAB/graphics,
then seal exact identities and the resulting client binaries using `seal.py`.
An independent ACCEPTED review must bind the manifest's exact SHA before
`run.py <S-id>` is allowed to debit the separate durable ticket budget.
`begin()` verifies manifest bytes, binary/wlroots identity, authorized family,
pre-existing run absence and limits before the durable reservation. The parent
owns budget initialization and runtime serialization. Never rerun a consumed ID.

Prospective capture ceilings are 12/12/18/12/12/14/14/14/12 (120 total).
S0/S1 standard compare actual H2 A/B paint and input, explicit B close, surviving
A input and final whole-H2 RGB. S2 first exercises Mosaic dismissal, then selects
and verifies workspace1/H1/Mosaic before its second owner's spawn; a wrong map
is rejected before any click. Its live second chain then performs the same
standard return. No mapped chain is silently moved. S3/S4 use actual H2 y=600,
configured popup Y crossings, output-local captures and measured global input.
Missing crossing is NOT EXERCISED, never clipping PASS.

S5/S6 apply fullscreen to a genuine nonleaf con ancestor, not the workspace IPC
fullscreen marker. Each retains equivalent raw paint/input/return observations;
a separate paired analysis must compare their results without defining new UX.
S7 hides and returns the first chain without any intervening click, verifies its
live IDs/grabs and visible B input, then closes explicitly. Optional destructive
hidden dismissal is omitted to preserve the bounded prospective sequence; E5
already observes that separate lifecycle, without proving universal click-through.
S8 has a preserved PRE-RELEASE HOLD proof and a separate POST-RELEASE ACK/commit
validator. E6 replay already acquires all eight images and the timeout/release
ordering; S8 is justified only for missing normal-close, SHM release and final
restoration observations. Saved native identity/GPU completion remain NOT PROVEN.

Clients close before private compositor exit. Explicit receipt, child-first
protocol destruction, SHM release, client error/code, terminal IPC, mechanical
cleanup, measurements and architectural verdict remain distinct observations.
IPC exit1 is retained verbatim; allowed transport handling never changes it to 0.
No native clip/tree/buffer generation hooks exist on the CORE SHA, so effective
clip removal is sampled through A/B spill plus paint/pointer corroboration.
No full damage coverage or transaction atomicity is inferred from screenshots.

Offline negatives call the same predicates imported by Session/run/cases:
null/real/branch floating, wrong owner/PID/path/workspace/output/layout, fake
fullscreen ancestry, unmapped B/fake grabs/parent/native buffer size, absent Y
crossing/wrong output/frame, destructive hidden click, effective standard
continuation absent, one-pixel RGB corruption/mask, pending IPC, wrong SHA and
superficial PASS, HOLD ACK contamination, inverted release phases/dead client,
and incomplete scientific closure. Unobserved native tree state stays explicit.
