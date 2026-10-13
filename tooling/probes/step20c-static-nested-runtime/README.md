# Static nested runtime handoff — EXPERIMENTAL

This preserved fixture belongs only to ticket
`SWAYFX_MOSAIC_STEP20C_RECEIPT_FREEZE_AND_STATIC_NESTED_RUNTIME_V1`.
Read the [pre-execution protocol](../../../docs/design/STEP20C_STATIC_NESTED_RUNTIME_HANDOFF_AND_VALID_GRAB.md).
The consumed runtime result is [INCONCLUSIVE](RESULTS.md); handoff and preflight
are PASS. Standard B/A input, explicit B close/A survival and final whole-H2
restoration remain NOT TESTED. The original pre-execution fixture and receipts
remain byte-identical in the LAB; these documentation status updates do not
modify the executed scripts or authorize another launch. STEP20C NEXT, architecture
UNDECIDED, production multi-output NOT YET SUPPORTED.

Preparation validates sealed offline evidence, preserves exact copies, builds
only C17 clients, verifies/copies the existing static binary, and creates one
new exclusive ticket-owned LAB/registry/ledger. The historical runner and its
modules are unchanged. A real immutable inventory protects runtime inputs;
mutable runtime output and circular derived hash records are excluded.

The original authorization gate is called by both the new read-only preflight
and the frozen runner. A separate handoff acceptance binds new dispatch code,
manifest and provenance; historical ACCEPTED is never reused to sign this code.
Preflight requires offline negative tests, binary/client identity, current ticket,
owner/UID, unused persistent budget and no prior runtime. Dispatch consumes a
durable exclusive ticket token before the runner's existing debit. Neither
failed launches nor failed actions are refunded. No second run is authorized.

Do not run any script from an old ticket/LAB. All outputs, clients, binaries,
PNGs, logs and sockets belong outside Git. No Mosaic/SceneFX build, production
change, package operation, daily IPC or desktop configuration is permitted.
