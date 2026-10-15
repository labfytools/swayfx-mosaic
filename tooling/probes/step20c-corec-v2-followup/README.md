# CORE-C V2 native closure follow-up — experimental source-only kit

This is the new, separately budgeted
`SWAYFX_MOSAIC_STEP20C_COREC_V2_FULLSCREEN_OOM_GLES_NATIVE_CLOSURE_BATCH_V1`
ticket. Its parent is project commit
`d46f854b3026e911659528fe94792aa13837a1d6`. The
[parent kit](../step20c-corec-v2/README.md) and its closed runtime receipts
remain unchanged. This directory does not add a production dependency.

## Post-campaign portability repair — OFFLINE_ONLY

The closed campaign executed commit
`c55373eab3c53132bf1157acc9cfc9edd451156e`, source manifest v2 SHA256
`2e9fe75a48466fa1a9e3081137146d5cfffb35145c1749160e2c4f350bc6e5b7`.
Its historical GPU client SHA256 is
`4e791780ac62152245891459864283750681b136a246c3c39ccf36b4f33972b4`;
its G3 compositor SHA256 is
`9da90b178f20ea79bc9fb2a105c227f9d5d66a9de7eac77ff4ec3ea102908658`.
These identities and their original receipts remain authoritative for that
campaign. FS-P was NOT_EXERCISED at the client identity guard. A separate
post-campaign probe reproduced EACCES for a nondumpable child, while the
original FS-P errno remains NOT_OBSERVABLE. GPU-G3 was INCONCLUSIVE with zero
captures, epochs and arms: reference exited2 after configure/ACK and before SHM.
The old client required the retired LAB's absolute TMPDIR. DY-C, OM-ROOT and
OM-NESTED were PARTIALLY_FEASIBLE in the sampled scope (32 captures total).

The following source changes are **OFFLINE_ONLY**, made after that campaign,
and have never run in a compositor. The GPU SHM path helper requires SMX_LAB
to be a canonical owned0700 direct child of `/var/tmp` whose name begins
`swayfx-mosaic-step20c-native-closure-`, and TMPDIR to be its exact canonical
owned0700 `scratch` directory. It rejects missing values, old-ticket/outside
paths, symlinks, foreign ownership, wrong modes and truncation, with explicit
stderr diagnostics. mkstemp stays in that scratch directory. Existing core and
dumpability guards remain mandatory.

Fullscreen client identity still requires an observed matching PID/proc/exe
path and SHA. Inaccessible proc identity now saves NOT_OBSERVABLE plus the
operation and original OS error/errno before the same mandatory gate refuses.
This improves diagnostics and does not fix or exercise the native fullscreen
gate; a future observable identity proof remains to be designed. No self-report
substitute or weakened dumpability is admitted.

The new helper tests execute only extracted production C path-validation code,
and Python identity predicates. A corrected client may be compiled offline;
that is not a native qualification. The campaign budget is closed: these bytes
authorize no retry, new reservation, GPU-CTRL or other headless run. They require
a new parent-owned source freeze and independent review, without rewriting any
historical manifest, review, admission, ledger or runtime receipt.

The follow-up derives prospective fullscreen, migration/refocus and root/nested
OOM fixtures in `graphics/`, and a distinct intrusive GLES diagnostic in `gpu/`.
Each implementation has its own offline tests. Independent acceptance of the
final source bytes and verified publication to both project remotes are
required before a runtime reservation. A source test or a successful build is
not native runtime evidence. No campaign is admitted by this README.

The G2 Wayland client sets `RLIMIT_CORE` to zero, sets
`PR_SET_DUMPABLE=0`, and verifies `PR_GET_DUMPABLE=0` before any Wayland
operation. This protects the client itself; the compositor's `exec` does not
preserve a parent's `prctl` dumpable setting. The parent also applies
`RLIMIT_CORE=0` to owned children, while compositor dumpability after `exec`
remains an explicit limitation.

Generated sources, clients, binaries, builds, receipts, logs, raw readbacks and
captures belong in a new mode-0700 LAB below `/var/tmp`. Redirect `TMPDIR`,
`TMP`, `TEMP`, `XDG_CACHE_HOME`, `XDG_DATA_HOME`, `PYTHONPYCACHEPREFIX` and
`CCACHE_DIR` there for every build/test. Runtime sockets must be private,
short, checked for quota, and explicitly selected. Never use an inherited
desktop socket or display. Keep heavy artifacts outside HOME and Git.

The eight named reservations have fixed, nonfungible ceilings:

| Run | Output captures maximum | Dependency |
| --- | ---: | --- |
| FS-P | 12 | Reviewed comparable pristine fullscreen fixture |
| FS-C | 16 | Same reviewed client and actual FS-P comparison |
| DY-C | 16 | Reviewed native-source refocus oracle |
| OM-ROOT | 10 | Reviewed root-only closure and availability oracle |
| OM-NESTED | 10 | Safe root result, or explicit independent dependency review |
| GPU-G3 | 12 | Reviewed capability/readback source and distinct built ELF |
| OM-EXTRA | 12 | New distinct discriminant and additional review |
| GPU-CTRL | 12 | New attribution question and additional review |

Maximum eight runs, 150 seconds each, 18 captures per run, and 110 output
captures globally; the named ceilings sum to 100. A reservation is consumed
even on failure. No retry, reset, refund, historical token or scenario renaming
is permitted. Optional entries are not admitted by default. The previous
ticket's unused reservations are closed and cannot be transferred.

CORE and OOM production mechanisms remain unchanged. Runtime Row 0 borrows
Sway's real tiling list. Pending IPC geometry, applied scene/input evidence,
native commits, presentation and buffer lifetime remain distinct. Stable
screenshots cannot establish atomic generation, complete damage or GPU
completion. OOM production policy and offscreen-popup UX remain undecided.

STEP20A DONE; STEP20B EXPERIMENTAL; STEP20C NEXT; STEP20D–G PLANNED.
PRODUCTION_MULTI_OUTPUT=NOT_YET_SUPPORTED; PRODUCTION_AUTHORIZED=FALSE.
No installation, live session operation, production source/patch, public ABI,
package recipe or UX change is authorized by this kit.
