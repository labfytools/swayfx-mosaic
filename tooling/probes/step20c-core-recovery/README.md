# STEP20C CORE recovery, OOM and DCC qualification

EXPERIMENTAL, source-only evidence for
`SWAYFX_MOSAIC_STEP20C_CORE_RECOVERY_OOM_AND_DCC_QUALIFICATION_BATCH_V1`.
Baseline: `70954e26f62fb3df25995e31b0c615762ff85a60`.
Private LAB: `/home/fy59/swayfx-mosaic-core-recovery-qmhckba5`.

This fixture adds no production dependency or implementation. STEP20A DONE;
STEP20B EXPERIMENTAL; STEP20C NEXT; STEP20D–G PLANNED;
PRODUCTION_MULTI_OUTPUT NOT_YET_SUPPORTED; PRODUCTION_AUTHORIZED FALSE.

## Evidence and scope

- [Graphics sources](graphics/README.md) preserve the new S0–S8 runner and
  shared offline predicates. Nine runs, 102 output PNG, 120 reserved capture
  slots, no retries, no compositor/GPU builds or staging. All runner exits0;
  terminal IPC exits1 remain distinct. Scientific and mechanical cleanup pass.
- [GPU sources](gpu-field/README.md) repair the per-plane metadata predicate
  and replay historical G1 without altering its outcome. Thirty-six tests pass;
  the complete epoch still rejects `effective halfpixel`, read success is
  NOT_PROVEN and the GL error queue is UNOBSERVED. New GPU runtime NOT_RUN.
- [OOM sources](oom/README.md) preserve A/B/C private prototype patches,
  extraction bindings and C17 harnesses. Forty expected command results and
  six rejected mutants are independently reproduced. Session survival and
  native damage remain unproved; production OOM policy is UNDECIDED.
- [Results](evidence/results.json), [provenance](provenance.json), the
  [durable budget snapshot](evidence/budget.json) and scoped review summaries
  bind compact public metadata. Reviewer receipts are faithful structured
  transcriptions materialized by the parent, not reviewer-authored files or
  verbatim transcripts. Final deep review and actual publication identities
  are recorded separately in the private post-publication closeout.

The nested fixture READMEs and source manifests retain their submission
edition, including then-pending reviews. The later scoped review receipts and
this directory's results record completed runtime/review evidence separately;
the frozen pre-run source bytes are not rewritten to update lifecycle labels.

Three published Python copies have one final blank line removed solely for
the new-file whitespace check. The [reversible normalization receipt](evidence/public-source-eof-normalization.json)
records both hashes, the exact suffix and equal AST/compiled bytecode. The
executed LAB copies and their accepted manifest are unchanged; those three
published files are not claimed byte-identical to the executed sources.

The historical LAB and its 4,688 entries remain unchanged. New sources have
their own parent hashes/deltas; historical failures are never reclassified.
The residual two conditional tokens do not authorize a retry or another run.
Every S identifier is consumed. The archived runtime launcher is evidence,
not permission to reuse this closed campaign.

Fullscreen cross-output remains NOT_EXERCISED: S5/S6 popups stayed inside H1,
and their ancestor child counts/owner heights differ. The raw vertical
`geometry.crossing` field retains its generic X/0 result; the executed Y/600
predicate and configured Y bounds establish the separate vertical crossing.
No raw source or receipt is edited to hide that metadata limitation.

## Offline reproduction

The following commands read retained historical/private evidence and launch
no compositor. Use `-B` to avoid changing historical directories with caches.
Choose a new, absent output filename for each audit or collection receipt.

```sh
python -B -m unittest discover -s tooling/probes/step20c-core-recovery/graphics -p 'test_*.py' -v
python -B -m unittest discover -s tooling/probes/step20c-core-recovery/gpu-field -p 'test_*.py' -v
python -B -m unittest discover -s tooling/probes/step20c-saved-input-gpu-batch -p test_native.py -v
python -B tooling/probes/step20c-core-recovery/audit.py --output /tmp/new-core-recovery-audit.json
python -B tooling/probes/step20c-core-recovery/collect.py --lab /home/fy59/swayfx-mosaic-core-recovery-qmhckba5 --output /tmp/new-core-recovery-collection.json
```

See the OOM README for a new private extraction/test directory; never rerun
its generators into the frozen evidence directory. Full source forks,
generated protocol files/slices, compiled clients/harnesses, ELF files, PNG,
DMA-BUF data and large logs remain outside Git. This is not a standalone
redistributable build kit, an OOM policy adoption or a production release.

The [V3 decision](../../../docs/design/STEP20C_CORE_QUALIFICATION_DECISION_V3.md)
provides the scientific interpretation and open integration gates.
