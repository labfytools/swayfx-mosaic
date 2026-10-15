# CORE-C V2 native closure follow-up — experimental source-only kit

This is the new, separately budgeted
`SWAYFX_MOSAIC_STEP20C_COREC_V2_FULLSCREEN_OOM_GLES_NATIVE_CLOSURE_BATCH_V1`
ticket. Its parent is project commit
`d46f854b3026e911659528fe94792aa13837a1d6`. The
[parent kit](../step20c-corec-v2/README.md) and its closed runtime receipts
remain unchanged. This directory does not add a production dependency.

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
