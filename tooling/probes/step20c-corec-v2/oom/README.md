# CORE-C V2 private native OOM diagnostic source variant

EXPERIMENTAL SOURCE ONLY. Production availability policy UNDECIDED. Distinct from
accepted CORE candidate; no production source or dependency change. R-OOM review,
pair-2 build, ELF/staging review and separate graphics admission remain REQUIRED.
O1/O2 runtime NOT_RUN. No global allocator hook, memory pressure or native run.

Parent is exact independently reviewed CORE trees reconstructed with sibling
`kit/assemble.py`. Parent source/C review SHA256:
`26aa862c741196fdbb8d7cdf5509301e49f763cdd22ffa7bcb1a4bbf09c66f90`.
`provenance.json` binds complete parent and variant files/modes and both deltas.
These are parent-relative patches, not cumulative upstream patches: first assemble
the accepted sibling core kit against its public pins, then apply this variant.
The core provenance SHA is bound, every actual source file is verified before
copying and after forward application. No current-source trust by folder name.

Use private LAB/run-env for EVERY command; TMPDIR/TMP/TEMP and all caches/data
must remain under owned LAB /var/tmp, no session env/loader routing inherited.

```sh
LAB/run-env python LAB/oom-kit/assemble-variant.py --core LAB/review-source-c/fresh --destination LAB/oom-work/fresh-variant
LAB/run-env python LAB/oom-kit/tests/run.py --sources LAB/oom-work/fresh-variant --output LAB/oom-work/new-h1-extension
```

Destination/output must be absent canonical paths under /var/tmp. No Meson,
compositor, Wayland client, IPC or GPU is launched. This extends existing H1 C
corpus; no new native/sanitizer campaign reservation is implicitly authorized.

Only primary popup_create scene allocation uses private wrapper; parent XDG role
is obtained via native wlr_xdg_surface_try_from_wlr_surface. Scope resets on return.
Only sidecar reservation at native factory before scene_tree_init can fail.
Unscoped tree creation and tree calloc stay native. Existing caller NULL paths
remain unchanged; native owner ENOMEM/disconnect must be measured, not simulated.
New private SceneFX symbol is not declared/installed in any public API/header.

Native process-only env: SMX_OOM_TOKEN_PATH absolute private LAB canonical path,
SMX_OOM_NONCE 32 lowercase hex, SMX_OOM_ROLE root_popup|nested_popup, snapshotted at
startup. Runner creates token AFTER startup/owner stability and, for O2, successful
stable rootA. Exact bytes `SMXOOM1 <nonce> <role>\n`, O_EXCL, mode0600, owned regular
single-link file. O_NOFOLLOW/O_NONBLOCK/O_CLOEXEC + UID/type/mode/length/content
checks; invalid input disables injection. Private canonical parent directory is
runner-owned; final component symlink refused. No token deletion/rearming/retry.
Once a valid matching scope consumes it, all subsequent calls succeed normally.
Logging includes identities, counters and pre-init native parent list length;
initialized/listeners/published zero is asserted by position/source and tested
factory adapters, not a complete native damage/lifetime measurement.

Nine cases in normal/UBSan/ASan+UBSan: root one-shot, rootA then nested one-shot,
unarmed, wrong role, malformed length/content, wrong nonce, unsafe mode, symlink,
invalid process config. All verify ordinary allocation and final sidecar cleanup.
Six independently compiled direct mutants target global scope, prepublication,
role, token reuse, malformed acceptance and nonce comparison. Each executable
sets PR_SET_DUMPABLE0/GET_DUMPABLE0 before assertions; parent sets RLIMIT_CORE0.
Exact bodies/slices/fullfile hashes are in evidence/bindings.json. Callsite slice
compiles against native wlroots headers, with reduced popup holder only.
Rendering/damage/IME/transaction adapters are inherited source but these OOM tests
only execute factory/lifecycle paths. No complete compositor build or survival.
Initial extension-1 failed compilation due shell quoting of character literals;
fixed before extension-2 PASS; extension-3 includes corrected native parent typed
callsite and PASS; final extension adds a private forward declaration for native
-Wmissing-prototypes compatibility and again PASS. Failed compile did not count as a killed mutant. The final oracle refinement moves init once in its negative mutant and asserts
parent publication before free; all six kills are direct SIGABRT assertions.
Raw earlier attempts remain private. evidence/result.json is the final bounded evidence, not runtime.

Separate graphics-adapter.py and GRAPHICS_HANDLER_CONTRACT.md supply interfaces
and complete scenario contract using existing reviewed graphics engine. They do
not implement the final settled handler/ledger admission. O1/O2 NOT_ADMITTED;
parent must implement/test/review the integration and publish all sources before
O1. Maximum eight captures, one role-matched failure each. No result transfers.
