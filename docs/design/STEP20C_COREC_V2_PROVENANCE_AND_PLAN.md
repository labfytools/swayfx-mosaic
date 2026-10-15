# STEP20C CORE-C V2 — provenance and pre-implementation plan

EXPERIMENTAL / PLANNED. Ticket SWAYFX_MOSAIC_STEP20C_REBUILD_FROM_GIT_COREC_OOM_GPU_NIGHT_SHIFT_V1.
Baseline main/origin/github 339dda45bc81b953e2f0afadf28765149e3a1ba1, clean at start.
This is a new derivation COREC_V2_REDERIVED, never recovery of lost CORE/G1 bytes.

## Authority and forbidden scope

The compositor owns tree, pending/current transactions, scene, camera, focus, hit testing and IPC. Row0 borrows workspace->tiling. STEP20C remains NEXT; production multi-output NOT_YET_SUPPORTED; PRODUCTION_AUTHORIZED FALSE. No changes to production source on main, UX/Packaging contracts, PKGBUILD, cumulative production patch, pins, installed libraries, personal config or daily session. Existing BLOCKED ticket and all its budgets remain closed.

Only newly reviewed experimental sources/patches/scripts/reports under tooling/probes/step20c-corec-v2 and docs may be committed. Sources and all generated files are private under /var/tmp/swayfx-mosaic-corec-v2-i516p6po. Only per-run sockets may occupy mode0700 /tmp/smx-* directories. No heavy /tmp or new home labs. TMPDIR/TMP/TEMP/cache/pycache/ccache/data redirected by LAB/run-env, inspected per child.

## Source authority and identity

SwayFX pristine pin fd71a6bdc061bd633b488ae7b83e8a6981d22f86 and Mosaic parent cd550382b311efdbfe3ed892f4e1d281d852e754 exist in project Git. Archive each independently; the modified main source is never a pristine control. SceneFX pin 37ccd723bef49e6891156ffafce8f549f01446cc was fetched from https://github.com/wlrfx/scenefx.git, object/tree verified; tree685a78b94f9e44ee683e5fea93874557a9fed457. Installed wlroots-0.20.so SHA must equal 7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837; actual runtime mapping checked separately. Source wlroots pin d783533489e1f75d6886c2ab5c5960090ef268f8 retrieved only if the callsite/ABI audit requires it.

Inputs are classified REUSED_VERSIONED_SOURCE, PINNED_UPSTREAM_FETCH, RECONSTRUCTED_NEW_DERIVATION, HISTORICAL_REPORTED_ONLY, MISSING_NOT_RECOVERABLE. Old manifests, raw PNG, CORE29baf31/G1 binaries and hook are not required inputs and are never claimed restored. Every new source and binary obtains its own hashes, new binding offsets and Build ID. No historic successful rendering, C test or runtime observation transfers by label.

## Functional reconstruction

Use versioned functional subtree/root-popup clip and hidden-owner patches only after exact forward apply on pinned parents, zero rejected/fuzz hunks. Identify/remove optional timing/PI/OPT instrumentation from the new functional derivative; declare any remaining trace. Preserve root popup in native global stacking layer with nested descendants inheriting the root clip. Clip uses the actual current tiled owner/workspace and applied scene/viewport; fullscreen exemption walks current non-leaf ancestors. Fully hidden owner gives empty clip; standard/floating/fullscreen bypass clears the extra clip without deciding offscreen-popup UX. No click-through promise.

Port option C from its surviving reference hunks to full native types/scene/wlr_scene.c. Factory allocates tree then inactive sidecar before scene_tree_init/publication. Reservation failure frees unpublished allocations and returns NULL. Setter allocates nothing for eligible trees; NULL deactivates while retaining reservation, zero remains active and blocks hits/render. Inactive reservations ignored by get/visibility/render/hit. Destroy detaches/frees once. Root/embedded/nonfactory trees are enumerated and never silently admitted as reserved. Preserve installed struct layout and private setter signature.

Audit all direct/indirect create/init/set/get/enabled/destroy/reparent callers in full SceneFX and Mosaic, including constructor rollback, outputs/workspaces, popup roots/nested, fullscreen/fading and saved_surface_tree. For each record source/function, parent ownership, first use, NULL handling, publication/listeners, reactivation and damage limits. Ordinary allocation abort wrappers are documented as actual availability behavior, never silently treated as survival. A concrete unsafe NULL use must be repaired narrowly within this experimental derivation and reviewed once; unresolved safety blocks dependent builds/runs.

Arithmetic uses wide validated bounds before narrowing, finite/range checks before double-to-int, safe intersections for extreme disjoint boxes, aliases and zero area. Required WHY/CONTRACT/INVARIANT comments ship with their new behavior.

## Spaces and evidence

SHM buffer native dimensions, XDG configure/ACK, assigned tiled destination, actual applied scene origin, global/local clip, output logical/physical geometry and PNG dimensions are distinct. Client callbacks/serials, current IPC metadata, native output commit/present and CPU/GPU buffer lifetime are separate observations. No common atomic generation is assumed or created. Invalidation of geometry after mutations is mandatory. Damage stubs are declared unit support, never native engine proof; stabilized PNG coverage is not frame-by-frame completeness.

## Gates and sequence

Storage + Git -> this independent plan/provenance review -> reconstruct full sources and callsite audit -> exact-body C normal/ASan/UBSan/float-cast + direct mutants -> independent source/C review -> one private static pair build/ELF/model/stage -> build review. Kit must reassemble byte-equivalently from surviving project Git + pinned public SceneFX in a second empty private directory, with no LAB absolute dependency. Publish the reviewed source-only kit on origin then github before ANY headless reservation.

Graphics implementation and C17 clients then require their own offline positive/negative checks and independent per-scenario review bound to hashes. Runtime gates debit ledger before spawn/capture/button/camera/mutation. Conditional OOM diagnostics are distinct binaries and require exact failpoint safety review. GPU new source-only hook/contract and negative tests are independent; insufficient observability means no GPU build/run. Final analysis/docs -> one final deep audit -> allowed bounded repair -> final validation -> second documentary commit/push -> direct remote equality + seal.

## Tests and adversarial evidence

C: NULL/box/idem/zero/NULL/reuse; targeted first/second reservation failures; no prepublication listeners/node; parent/child destroy order, reparent/back, no ABA false-positive from address reuse; embedded root rejection; inactive and zero inherited hits; safe finite/INT_MIN/MAX geometry; relevant current fullscreen/hidden/standard/fading cases. Compile real bodies bound to full-file/slice hashes in C17 -Wall -Wextra -Werror as compatible, normal, UBSan incl float-cast and ASan+UBSan. Native Wayland signals/Pixman are real, any adapters/stubs labeled. Mutants must actually fail the invariant, including publish-before-reservation, setter allocation, inactive-visible, NULL-free, unreserved-root, ignored-NULL, zero-hit, double-free, unsafe intersection and unchecked conversion.

Runtime: current owner/PID/workspace1/H1/tiling ancestry validated before and after second spawn; real button press/release serial -> popup grab -> configure/ACK/map for root+nested; cross-output geometry measured not assumed; whole-H2 RGB exact where required; standard overflow and B-close/A-survival; no outside click before hidden return; phased saved HOLD/timeout-before-release/ACK/live/normal-close; dynamic input resampled after resize/migration; fullscreen comparable only when non-leaf current ancestor, same children/configure and actual crossing exist. Codes runner/terminal IPC/compositor/clients and scientific/mechanical cleanup remain distinct.

GPU: new diagnostic source from pinned SceneFX, never old G1. Plane roles not generic image stride on DCC auxiliary; no inferred FD/allocation bounds. Query uniform bits/CPU ideals/precision capability separately; no fitted epsilon. Explicit intrusive error attribution if glGetError used (consumes flags, cannot restore queue). Save/restore actual functional GL/EGL state and bounded read framing; no shader/sampler/clear/clamp/cache computation changes. No read_success from sentinel/file/FBO alone. Prospective fixed A/B/A at most256MiB raw; first rejected epoch stops without retry. Whole field causality, exact presented-buffer identity and GPU completion remain independent.

## New budgets and resource bounds

Runs P0=10 P1=10 C1=18 C2=12 C3=12 C4=12 C5=12 C6=12 C7=14 C8=12 O1=8 O2=8 G2=16 R1=14 capture caps sum170, below global180; max14runs,18captures/run,150s/run. R1 is only a reviewed new discriminant, never a consumed-run retry. First failed reservation remains consumed. At most3 private SceneFX+Mosaic pairs (CORE, OOM distinct, GPU distinct),3 DESTDIR,2 sanitizer compilation campaigns, -j8 max. A retained pristine may be used only after source/binary identity qualified; no unauthorized extra pristine build assumed.

Ledger: stable exclusive lock inode, UID/owner/root, immutable run token and binary/source/review bindings, atomic replacement plus fsync; local action quotas frozen before admission. Negative tests: old ticket/LAB/token, changed source/binary/wlroots/reviewer, second reservation, global/local caps and inherited daily socket. No graph run until source kit publication verified directly. Never clone/reset budgets.

Storage cap18GiB generated, alert12GiB; minimum20GiB filesystem free before builds and256MiB /tmp available before runtime. Check footprint at stage boundaries and refuse further allocations at cap. Only owned nonsealed dispensable generated probe files may be removed. Preserve LAB after closeout, no automatic purge. Document future selective purge without executing it. Preserve indispensable new patches and recipes in Git before graphics so LAB deletion cannot erase source reproducibility.

## Open decisions and limits

OOM production availability policy UNDECIDED; alternatives A abort/B bool+mask/C preallocation remain distinct. Popup hide/dismiss/reposition, universal click-through, final animation and sizes, release/security owners, legal notice approval and maintenance/distribution remain human decisions. Technical role transitions inside this scope need no repeated user permission. FROZEN/public API/schema/new subsystem changes outside scope stop rather than silently redefine contracts.
