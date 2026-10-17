# Codex instructions — SwayFX Mosaic

These instructions apply to the entire repository. They define the agent's
working discipline, not the product specification. If this file conflicts with
canonical project documentation, stop and report the conflict; do not silently
choose a convenient interpretation.

## Mission and communication

- Develop **only** the optional native Mosaic / Spatial Canvas layout for SwayFX.
  Do not turn the project into a general-purpose SwayFX fork.
- Explain plans, findings, test evidence and blockers to the user **in French**.
  Follow the existing language/style of each source file and document.
- Be evidence-first. Distinguish **CURRENT**, **EXPERIMENTAL**, **PLANNED**,
  **NOT TESTED**, **BLOCKED**, and **NOT YET SUPPORTED**. Never upgrade a status
  based on a proposed design, a private spike or a successful compile alone.
- Work within the requested scope. Investigations and design proposals do not
  authorize production implementation, packaging changes or live deployment.

## Read before changing anything

1. `git status --short --branch`, current branch, recent commits and diff.
   Preserve pre-existing user changes; do not reset, stash or overwrite them.
2. `docs/README.md` (documentation authority and index).
3. `docs/ARCHITECTURE.md`, `docs/UX.md`,
   `docs/KNOWN_LIMITATIONS.md`, and `docs/ROADMAP.md`.
4. For build/source work: `docs/DEVELOPMENT.md` and `docs/UPSTREAM.md`.
   For packaging: `docs/PACKAGING.md`.
5. For STEP20C: all reports under `docs/design/STEP20C_*.md`,
   especially `STEP20C_POPUP_OWNERSHIP_PROBE.md` and
   `STEP20C_VALID_GRAB_HIDDEN_OWNER_PROBE.md`.

Canonical architecture/UX/packaging/upstream/development documents govern their
own topics. Design documents are proposals or isolated evidence; historical
`docs/STEP20A.md` and `docs/STEP20B.md` are not current specifications.
Resolve contradictory canonical documents **before** implementing behavior.

## Architecture and user-experience invariants

- SwayFX's real compositor and tiling tree own runtime order, focus, geometry,
  camera, transactions, scene, hit testing and IPC. Do not emulate tiling with
  floating windows or give QuickShell, Session V2 or a daemon parallel authority.
- Mosaic is opt-in **inside an ordinary Sway workspace**. Preserve standard
  layouts and the workspace-local `layout toggle mosaic` restoration path.
- Runtime Row 0 **borrows** `workspace->tiling`; Mosaic state does not own Sway
  containers. Additional rows currently exist only in the model, not runtime.
- Keep logical row order, geometry, viewport/camera and focus distinct.
  Keep applied rendering and input consistent with the same transaction state.
- Super alone must never move windows. Intended external bindings are
  Super+Alt+L (standard/Mosaic) and Super+Alt+M (Applications); this repository
  must not install personal bindings, dotfiles or QuickShell configuration.
- Preserve ordinary SwayFX floating, fullscreen, scratchpad, popup and IPC
  behavior unless an explicitly documented, tested Mosaic-specific contract
  requires a change. Do not invent final cell sizes or animation policy.

## Current boundary — STEP20C is a feasibility gate

- **STEP20A: DONE. STEP20B: EXPERIMENTAL. STEP20C: NEXT, not implemented in
  production. STEP20D–G: PLANNED.** Recheck the roadmap on every new task.
- Cross-output viewport clipping is **NOT YET SUPPORTED**; Mosaic is **not**
  validated as a daily-driver compositor. Do not claim otherwise.
- The isolated SceneFX subtree clip covered sampled tiled visual/input cases.
  A later isolated owner-derived root-popup clip covered sampled GTK root and
  nested popup cases on two horizontal headless outputs. A further private
  probe measured a valid-serial XDG grab, found a fully hidden owner leak in
  that initial clip, and closed the sampled leak with a disposable owner
  visibility guard. All remain **PARTIALLY_FEASIBLE**, not a production
  dependency or UX decision.
- Next evidence required: valid-grab nested popup behavior, vertical/negative-
  origin/scaled/rotated outputs, output migration/resize, transaction-generation
  consistency, complete damage/stale-pixel coverage, decorations/shadows/blur/
  saved buffers, and SceneFX/wlroots ABI/package maintenance. Mark any untested
  matrix cell **NOT TESTED**.
- For popup semantics, compare the modified private compositor against an
  unmodified headless SwayFX control. Do not promise universal click-through.
  Offscreen-popup hide/dismiss/reposition UX remains undecided.
- Do not merge private SceneFX experiments into the project, create a permanent
  library fork, alter public ABI, add package dependencies, or claim STEP20C
  production readiness without an explicit decision and closed feasibility
  gates. Use disposable private checkouts, libraries, sockets and logs for
  bounded probes.
- A bounded probe may preserve reviewed source fixtures and private patch files
  under `tooling/probes/` with base commits, hashes, reproduction instructions
  and an explicit experimental status. Keep generated files, binaries, build
  trees, sockets, large logs and transient captures outside Git. Fixture
  preservation does not add a production build dependency or authorize merging
  the experimental patch.

## Safe development workflow

1. State the exact scope, accepted contract, expected files and test plan.
   Prefer one small, reviewable change at a time.
2. **Docs first:** change `docs/UX.md` for user-visible behavior and
   `docs/ARCHITECTURE.md` for architecture **before** implementation. Update
   Packaging/Upstream/Development when those contracts change; update Known
   Limitations/Roadmap with actual evidence. Never present a proposal as shipped.
3. Use existing C, Sway/wlroots/SceneFX conventions. Keep ownership/lifetimes,
   container identity, popup hierarchy, pending/current state and output
   coordinates explicit. Add regression tests for changed behavior.
   For Python probe tools, use readable PEP 8 formatting, short functions and
   docstrings explaining effects and refusals. Comment design/ownership
   invariants and explicit error handling; keep offline tests reproducible and
   independently reviewed without starting native workloads.
4. Build and test in isolated build directories; never install, reload,
   restart or replace the **running desktop session**. Never operate on the
   live Sway IPC socket. Headless tests must use their own `XDG_RUNTIME_DIR`,
   `WAYLAND_DISPLAY` and explicit `SWAYSOCK` / `swaymsg -s`.
5. For a normal source change, verify the documented sequence as applicable:

   ```sh
   meson compile -C build-mosaic -j 8
   meson test -C build-mosaic --print-errorlogs
   MOSAIC_BINARY="$PWD/build-mosaic/sway/swayfx-mosaic" python tests/headless-ipc.py
   git diff --check
   ```

   If the build directory does not exist, set it up **as documented** in
   `docs/DEVELOPMENT.md`. Do not rebuild a supposed upstream baseline in a
   Mosaic-modified checkout. For documentation-only changes, validate links,
   consistency, and `git diff --check`; do not claim runtime tests were run.
6. For packaging tasks, use **DESTDIR staging only** and verify the complete
   manifest contains exactly `/usr/bin/swayfx-mosaic` for the current package.
   The approved private future STEP20C candidate may additionally stage only
   justified notices under `/usr/share/licenses/swayfx-mosaic/`. This exception
   does not authorize PKGBUILD changes or real installation; coexistence with
   standard SwayFX is mandatory. No live install, sudo,
   `pacman`, session switch or system library replacement without explicit
   user authorization.

## Package, patch and upstream safety

- Pinned base: SwayFX `0.6` at
  `fd71a6bdc061bd633b488ae7b83e8a6981d22f86`,
  wlroots 0.20 and SceneFX 0.5. Never assume an upstream update is compatible.
- The ordinary SwayFX package owns `/usr/bin/sway`; this project may stage
  only `/usr/bin/swayfx-mosaic` for the current package. The private future
  STEP20C candidate may also stage justified separate license notices as above.
  No `provides`, `conflicts` or `replaces`
  against sway/SwayFX. Do not alter or block normal SwayFX upgrades.
- Remotes: `origin` = canonical Forgejo; `github` = public mirror;
  `upstream` = SwayFX fetch-only. Never push Mosaic to `upstream`.
- Production patch: `patches/0001-mosaic-layout-viewport.patch`, intended as
  the **complete cumulative delta** against the pinned pristine upstream
  commit. Verify forward application on a clean pinned checkout, source
  equivalence, and the `PKGBUILD` checksum before treating it as releasable.
- `tooling/export-patch.sh` builds the cumulative delta from the verified
  pristine SwayFX 0.6 import in a private index. Run its offline regression
  test, export, review the patch, verify forward application and source
  equivalence on a clean pinned checkout, then check/update the `PKGBUILD`
  checksum. The exporter validates before atomic replacement and must leave
  the previous artifact intact on failure. Never force-apply hunks.
- Do not modify git history, branches, remotes or package version/pins without
  an explicit scoped reason. For this repository, Codex must commit each
  coherent batch after documentation, applicable tests and independent review,
  then push origin followed by github and verify that both remote branch SHAs
  match the intended commit. This permanent user instruction excludes force
  pushes, upstream pushes, history rewriting, other repositories, private
  evidence, personal identifiers, secrets/credentials, binaries, raw logs,
  large files and unvalidated PASS claims. It grants no production change,
  native execution or sandbox expansion beyond the current task's scope.

## Required handoff after each task

Report in French: files changed, exact behavior or finding, commands run and
PASS/FAIL/NOT RUN results, limitations/risks, and whether anything was
committed/pushed. Keep the working tree visible and identify the next
**smallest justified step**. Never conceal failed tests or silently broaden
the task into STEP20C production work.
