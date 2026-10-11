# STEP20C valid grab and hidden popup owner probe

**Status: EXPERIMENTAL / PARTIALLY_FEASIBLE — valid-grab fixture demonstrated; hidden-owner leak found in the retained private candidate and closed at sampled points by a further private guard.** This is an isolated feasibility probe, not a production STEP20C implementation or a multi-output support claim. The canonical [architecture](../ARCHITECTURE.md), [UX](../UX.md), [limitations](../KNOWN_LIMITATIONS.md), and [roadmap](../ROADMAP.md) retain authority.

## Problem and existing evidence

SwayFX attaches a root XDG popup scene below `root->layers.popup`, outside its owner's tiled scene tree. The earlier private SceneFX inherited clip, applied to the tiled tree alone, therefore allowed the popup to render and receive pointer events on HEADLESS-2. The later [popup ownership probe](STEP20C_POPUP_OWNERSHIP_PROBE.md) applied a clip to the root popup scene derived from its Mosaic owner's applied tiled viewport. Sampled visible and clipped-away root and nested popup points behaved as intended on two horizontal headless outputs; a standard `splith` return restored sampled ordinary behavior. That probe's GTK request used `xdg_popup.grab(wl_seat, 0)`, so valid-grab behavior remains **NOT TESTED**. Its attempt to hide the owner changed focus and dismissed the popup before measurement; a fully hidden owner remains **NOT TESTED**.

The relevant paths are `sway/desktop/xdg_shell.c` (owner, popup scene creation and unconstrain), `sway/desktop/transaction.c` (applied tiled and popup scene positions), `sway/input/cursor.c` (scene hit traversal), wlroots 0.20 XDG shell grab and pointer handling, and private SceneFX 0.5 inherited render/hit/damage clipping. XDG unconstrain currently reads pending content geometry, while the private clip reads applied scene/current state. Their agreement across transaction generations has not been proved.

## Hypotheses and expected boundary

1. A popup created after a real `wl_pointer.button` serial and `xdg_popup.grab(seat, serial)` remains interactive where visible. At a clipped-away scene position, its surface receives no pointer enter or button. A valid grab may still dismiss the popup or consume an outside click; compare this with unmodified SwayFX instead of assuming click-through.
2. A root popup can remain mapped after its tiled Mosaic owner is translated entirely outside the applied viewport. The owner retains the same Sway container identity and workspace. The private clip should then prevent popup pixels and scene hits outside the owner's viewport. If `popup_done`, unmap, focus change or client teardown occurs first, the test is inconclusive for clipping.
3. Returning the owner to view or leaving Mosaic restores the appropriate sampled popup rendering/input without stale pixels. Comprehensive transaction, damage, effects and output-geometry coverage remains a later gate.

## Experimental protocol and acceptance

Use a small Wayland client with a real XDG toplevel and popup. The client must log pointer enter/leave, both button codes, the exact serial received in a `wl_pointer.button`, the same serial passed to `xdg_popup.grab`, XDG configure acknowledgements, popup mapping, popup pointer events and `popup_done`. Request the grab after the input event and before the first popup buffer commit, in protocol order. Preserve `WAYLAND_DEBUG=1` traces. An arbitrary nonzero serial or a grab request without an interactive configured popup is **FAIL** as a fixture. A popup that closed before the hidden-owner measurement is **INCONCLUSIVE**, not a clip PASS.

Run three private headless cases with two horizontal 800×600 outputs: **A** unmodified SwayFX with a standard layout; **B** private SceneFX/Mosaic binary with a standard layout; **C** that private binary with Mosaic on HEADLESS-1 and an ordinary client on HEADLESS-2. Place the owner and popup so the popup is fully visible, partly visible and physically extends beyond the Mosaic viewport. Inject left and right clicks at visible, clipped-away and ordinary outside positions. Record both output screenshots, global/output/client-local coordinates, client and compositor logs, protocol trace, IPC tree/outputs, applied clip logs, hit and button events, dismissal and `popup_done`. Compare outside-click consumption and dismissal in A/B/C; an invisible popup scene hit is a failure even if a legitimate grab consumes an outside click.

For the hidden-owner case, open and verify the popup first. Move only the Mosaic camera so the owner's *applied* tiled rectangle is entirely outside the viewport, without opening new windows or transferring focus as part of the maneuver. Record its container ID, logical rectangle, `scroll_x`, output viewport, popup configure/map state, scene clip, two-output pixels and pointer events. Move the camera back, then separately test workspace switch and owner destruction. Distinguish clip removal from XDG dismissal and unmap. Check appearance, movement and disappearance for sampled stale pixels and SceneFX damage records, without claiming exhaustive damage correctness.

| Scenario | Control A | Private standard B | Private Mosaic C | Acceptance state |
| --- | --- | --- | --- | --- |
| Valid-serial XDG grab | PASS: button/grab serial 61 | PASS: serial 61 | PASS: serial 55 | PASS: configured, interactive popup and outside-click dismissal without protocol error |
| Entire popup inside HEADLESS-1 | PASS: 250×190, both buttons | PASS: same | PASS: same | PASS at `(350,150)`; no `popup_done` |
| Visible region of crossing popup | PASS at `(700,150)` | PASS at `(700,150)` | PASS at `(700,150)` | PASS for sampled left/right popup events |
| Partly clipped popup | Ordinary cross-output popup visible | Same as control | Visible HEADLESS-1, clipped HEADLESS-2 | PASS at sampled pixels and pointer positions |
| Input outside viewport `(900,150)` | Popup receives left/right | Popup receives left/right | No popup enter/button; `wev` receives left/right | PASS for sampled clipped region; valid grab also sends `popup_done` |
| True exterior `(900,400)` under grab | `wev` gets left/right; `popup_done` | Same as control | Same as control | PASS for sampled dismissal and delivery |
| Nested popup | NOT TESTED in this probe | NOT TESTED | NOT TESTED | Previous non-valid-grab nested case does not qualify this row |
| Fully hidden owner with popup still mapped | No camera analogue | No camera analogue | Baseline FAIL; private guard PASS at sampled point | Owner stayed ID 8; no `popup_done` before hidden measurement |
| Return of hidden owner | — | — | PASS at sampled point with same popup | Camera 1280→400 restored yellow popup without configure/recreation |
| Return to standard layout | Ordinary reference | Ordinary reference | PASS at `(900,150)` | Clip cleared; popup pixel and right-button delivery returned |
| Workspace switch / owner destruction | NOT TESTED | NOT TESTED | Measured separately | Switch sent `popup_done`; destroy ended client without `popup_done` |
| Damage and stale pixels | Sampled screenshots | Sampled screenshots | PARTIAL | No yellow residue at tested points; logs show damage, no complete effect/transaction proof |

Any persistent visible/hittable leak or unavoidable ordinary-layout regression is **BLOCKED** for this approach. Positive sampled cases with open gates are **PARTIALLY_FEASIBLE**. If a reliable fixture cannot be obtained, the affected cases are **INCONCLUSIVE** or **NOT TESTED**. This matrix does not qualify STEP20C as complete.

## Isolation and starting provenance

No production source, package, dotfile, installed library, session or live IPC socket may change. Use a dedicated `/tmp` laboratory with private source/build directories, `XDG_RUNTIME_DIR`, `WAYLAND_DISPLAY`, explicit `SWAYSOCK`, headless outputs and process-local `LD_LIBRARY_PATH` only for the private compositor. Do not alter the public `struct wlr_scene_tree` layout. Transient logs, screenshots, generated protocol code and builds stay outside the repository. The later evidence-freeze task retained only reviewed source fixtures under [`tooling/probes/step20c-valid-grab/`](../../tooling/probes/step20c-valid-grab/README.md); they are not production dependencies.

At probe start, local `main`, `origin/main` and `github/main` were `76a765a9965815a52586cc10e56e9d99f2720bcb`; the worktree was clean. Installed `wayland-client`, SceneFX and wlroots pkg-config versions were 1.26.0, 0.5.0 and 0.20.2. `/usr/bin/sway` reported SwayFX 0.6. The retained `/tmp/swayfx-mosaic-popup-yEamPX/` laboratory exists: private Mosaic source HEAD `cd550382b311efdbfe3ed892f4e1d281d852e754`, SceneFX source HEAD `37ccd723bef49e6891156ffafce8f549f01446cc`; complete private patch SHA-256 values match the prior report (`d416f6413ea097a48a44d231e50ffba363914f46c8687f0ea2e4dcacd5f31fe9` and `c74c515b98da8f5f637e260e6a3755c7a75bd78d1c39e54a67850f1c383e30e7`). Private binaries exist but will be copied or rebuilt in a new disposable laboratory before use. Their presence alone is not a new result.

## Running observations

The new laboratory is `/tmp/swayfx-mosaic-valid-grab-7SA2yO/`. It holds copies of the verified private sources, fresh `scenefx-build/` and `mosaic-build/`, `grab-client.c`, generated XDG protocol files, `pointer-daemon.c`, `run.py`, and per-case logs/screenshots. The client initially observed `wl_seat.capabilities(0)` before a virtual pointer existed; a first attempt without a persistent pointer produced no usable input and is not counted. The corrected fixture starts a virtual-pointer process before the client, retains it for the full scenario and logs injected events. A second initial Mosaic attempt used logical IPC `rect.x` as if it were rendered x; correcting by the measured `scroll_x` gave the real input point. These failed fixture attempts do not count as scientific observations.

In `run-control`, `run-private_standard` and `run-private_mosaic`, the client received a real left `wl_pointer.button` press serial (61, 61 and 55 respectively) on its toplevel and passed the identical serial in `xdg_popup.grab(wl_seat, serial)` before the popup's first commit. Each run received `xdg_popup.configure` followed by `xdg_surface.configure` (62 in control and private standard, 56 in private Mosaic), acknowledged it and mapped a 500×190 yellow SHM popup. The client stayed alive and received no protocol error. At global `(900,150)`, the standard control and private standard screenshots show yellow popup pixels on HEADLESS-2; the private Mosaic screenshot shows the ordinary output client. This is initial valid-serial and visual evidence, pending more pointer comparisons.

The retained private candidate **fails the fully hidden owner case**. The owner remained container ID 8 with logical rectangle `(640,25,640,575)` and the same focused Mosaic row. The applied camera changed from `scroll_x=400` to `1280`, putting the owner horizontally at `[-640,0)` against viewport `[0,800)`. No `popup_done` occurred before or during the measurement; the client remained alive. The popup remained yellow at HEADLESS-1 `(100,150)` while the normal background at `(300,150)` was dark. A virtual-pointer move entered the popup (`POINTER_ENTER target=popup`), and a right click at `(100,150)` generated popup button 273 press/release. The private log changed the root clip from `local=-242,-25 800x600` to `local=638,-25 800x600`, a viewport-only clip that still intersects the popup despite its owner being completely outside. Returning to `scroll_x=400` preserved the mapped popup and generated no `popup_done`; the later ordinary outside right click delivered to `wev` and then `popup_done`. Screenshots and logs are in `run-private_mosaic_hit/`. This is a real scene pixel/hit leak, not a grab-only outside-click effect. It blocks accepting the current owner-derived viewport clip *as implemented* for fully hidden owners.

To discriminate whether the failure was inherent to the architecture, a second private variant checked the owner's applied scene rectangle before setting the popup clip. That change is a feasibility discriminant, not a production patch or a settled UX policy.

That discriminant was implemented only in the copied private `mosaic/sway/desktop/transaction.c`, with the previous file retained as `transaction-before-hidden.c`. After rebuilding the private compositor, `run-private_mosaic/` and `run-private_mosaic_hit/` repeated the same 400→1280→400 camera sequence. The guard checks whether the owner's applied scene rectangle intersects the applied viewport and sets an empty root-popup clip when it does not. At hidden `(100,150)`, the yellow baseline pixel `(224,192,32)` became ordinary dark background `(30,30,46)`; the hover produced no popup enter and the hidden right click produced no popup button. The compositor logged `PROBE_POPUP_HIDDEN_OWNER` once for the hide transition. The popup remained mapped and no `popup_done` occurred during hide or hover; with no hidden click, returning the camera restored its visible yellow region without a new popup configure or recreation. In the separate hidden-click run, the valid grab generated `popup_done` on the outside click, as expected from grab dismissal, while the popup surface received no button. These are sampled visual/input results for the private guard; they do not settle whether offscreen popups should be hidden, dismissed or repositioned in production.

The final hidden-owner log recorded the applied owner scene rectangle `(-640,0,640,600)` and applied viewport `(0,0,800,600)`, directly confirming their empty horizontal intersection. IPC retained the owner's logical rectangle `(640,25,640,575)` and container identity; the scene coordinates differ because camera translation and decorations are applied by the compositor. This is why the guard uses scene position rather than treating IPC `rect.x` as physical x.

## Comparative pointer and lifecycle results

The XDG positioner reported popup geometry `(350,80,500,190)` relative to the owner in all three compositor configurations. The private Mosaic owner was logical `(640,25,640,575)` with camera 400 at popup creation. The control and private standard layout rendered the popup at global `(900,150)` (HEADLESS-2 local `(100,150)`), where screenshots read `(224,192,32)`. They delivered both left button 272 and right button 273 to the popup at that point; `wev` received neither, and the popup was not dismissed. In Mosaic, HEADLESS-2 local `(100,150)` read ordinary client `(238,238,238)` with no popup enter/button at global `(900,150)`. `wev` received both left and right buttons in separate runs; each exterior click also caused `popup_done`. At visible Mosaic popup `(700,150)`, left and right clicks reached the popup in separate runs without `popup_done`. Thus the clipped-away surface was not receiving events, while the valid grab still handled dismissal. The pointer entered and left the popup on camera changes; the client-local coordinates remained reported by Wayland, but exhaustive coordinate transformations were not tested.

A second XDG positioner variant `(50,80,250,190)` kept the entire popup within HEADLESS-1. In control, private standard and private Mosaic runs, global `(350,150)` was yellow `(224,192,32)` and the popup received both left and right buttons without `popup_done`; HEADLESS-2 local `(100,150)` remained ordinary `(238,238,238)`. These separate `fully_visible` runs establish the whole-popup case instead of inferring it from the visible portion of a crossing popup.

At the true exterior `(900,400)`, both button codes reached `wev` and caused `popup_done` in **all** three configurations. The direct control comparison is important: a `popup_done` alone does not mean that a hidden scene surface received the click. Returning from Mosaic to `splith` while the popup remained open made HEADLESS-2 local `(100,150)` yellow again and delivered right button 273 to the popup, with no `popup_done` before that click. Switching workspaces while the owner was hidden sent `popup_done` and left the client alive. Destroying the hidden owner instead terminated the client; no `popup_done` was observed in that path. Neither mechanism is counted as a clip proof.

Sampled damage observations are limited. On HEADLESS-1, exact yellow popup-color pixels counted 39,520 while open, 0 with the private guard and owner hidden, and 39,520 after camera return. The unguarded baseline had 40,280 yellow pixels while the owner was hidden. The private SceneFX log contains `SPIKE_DAMAGE` entries on both outputs during the transitions, including large regions; these logs do not isolate popup-only invalidation. The captured frames show no yellow residue at the sampled point after hiding or after `popup_done`, but do not prove all vacated pixels, frames, effects or saved transaction buffers are correct. The client remained mapped during the no-click hide/return run; no new XDG configure was required for its return.

## Reproduction and retained artifacts

The original laboratory root is `/tmp/swayfx-mosaic-valid-grab-7SA2yO/`; this path is historical and **not required** for the preserved [replay fixture](../../tooling/probes/step20c-valid-grab/README.md). Its three private source patches are `mosaic-popup-plus-base.patch` (SHA-256 `d416f6413ea097a48a44d231e50ffba363914f46c8687f0ea2e4dcacd5f31fe9`), `scenefx-popup-plus-base.patch` (`c74c515b98da8f5f637e260e6a3755c7a75bd78d1c39e54a67850f1c383e30e7`) and `hidden-guard.patch` (`35785a8f3e863b3c1fd87932d8ff0c2949b03cb04382cc34e1126170968f802b`). The first Mosaic patch applies to the already-Mosaic project commit `cd550382b311efdbfe3ed892f4e1d281d852e754`, **not** directly to pristine upstream SwayFX `fd71a6bd...`; an initial attempted `git apply --check` on the upstream commit failed at `transaction.c:974`. The SceneFX patch applies to `37ccd723bef49e6891156ffafce8f549f01446cc`. Applying the patches in that order on clean archives, then comparing `include/`, `sway/`, Meson files, the Mosaic model test, and SceneFX `include/` and `types/` against the laboratory sources passed. The archive check is a source reproducibility check, not a package/ABI qualification.

`grab-client.c` SHA-256 is `202afdc5dae0ee4aba570eef4a563f8b298474eb84e33af9510c4c81c05d16e4`; `pointer-daemon.c` is `a00fcedc38ccb7ca4c25c982d9f38e8bde3168a3833f0c9cf2056e841d720938`; `run.py` is `b2aaa90188ea387cb8a69aa69935b56e63f5ce70eb98e74783b0fb3c9236a41f`. These six source files are now byte-identically preserved in Git with the three patches. The added upstream `wlr-virtual-pointer-unstable-v1.xml` at `wlr-protocols` commit `b010a03648b88d143236de193bddbfea0c08bc84` has SHA-256 `3ff6d540be0bc5228195bf072bde42117ea17945a5c2061add5d3cf97d6bb524` and regenerates the original virtual-pointer C/header byte-for-byte. Generated XDG and virtual-pointer C/header files, both private builds, the earlier unguarded `transaction-before-hidden.c`, and per-run `client.log` (including `WAYLAND_DEBUG=1`), `pointer.log`, `wev.log`, `compositor.log`, IPC JSON and two-output PNG files remain outside Git in the original laboratory. `run-private_mosaic_hit_baseline/` is the retained unguarded leak; `run-private_mosaic_hit/` is the guarded hidden-click comparison. `run-control/`, `run-private_standard/`, `run-private_mosaic/`, the six `boundary_{left,right}` directories, `outside_left`, `visible_left`, `fully_visible`, `standard_return`, `lifecycle_switch` and `lifecycle_destroy` directories retain the other cases.

The core commands used, after copying or reconstructing the two verified private sources and applying `hidden-guard.patch`, were:

```sh
R=/tmp/swayfx-mosaic-valid-grab-7SA2yO
meson setup "$R/scenefx-build" "$R/scenefx" -Dexamples=false -Dwerror=false
meson compile -C "$R/scenefx-build" -j 8
PKG_CONFIG_PATH="$R/scenefx-build/meson-uninstalled" meson setup "$R/mosaic-build" "$R/mosaic" \
  -Dmosaic-package=true -Ddefault-wallpaper=false -Dswaybar=false -Dswaynag=false \
  -Dman-pages=disabled -Dsd-bus-provider=libsystemd -Dwerror=false
PKG_CONFIG_PATH="$R/scenefx-build/meson-uninstalled" meson compile -C "$R/mosaic-build" -j 8
wayland-scanner client-header /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml "$R/xdg-shell-client.h"
wayland-scanner private-code /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml "$R/xdg-shell-protocol.c"
cc -std=c17 -Wall -Wextra -Wno-unused-parameter -I"$R" "$R/grab-client.c" "$R/xdg-shell-protocol.c" -o "$R/grab-client" $(pkg-config --cflags --libs wayland-client)
cc -std=c17 -Wall -Wextra -Wno-unused-parameter -I"$R" "$R/pointer-daemon.c" "$R/virtual-pointer-protocol.c" -o "$R/pointer-daemon" $(pkg-config --cflags --libs wayland-client)
python "$R/run.py" control boundary_left
python "$R/run.py" private_standard boundary_right
python "$R/run.py" private_mosaic boundary_left
python "$R/run.py" private_mosaic boundary_right
python "$R/run.py" private_mosaic fully_visible
python "$R/run.py" private_mosaic
python "$R/run.py" private_mosaic_hit
```

The runner gives each case its own mode-0700 headless `XDG_RUNTIME_DIR`, discovers that case's Wayland/IPC sockets, and always passes the private socket with `swaymsg -s`. It sets private `LD_LIBRARY_PATH` only on the private compositor process; clients and injectors do not inherit it. Its virtual pointer remains alive until the case ends. Installed packages were `swayfx 0.6-1`, `scenefx 0.5-1` and `wlroots0.20 0.20.2-1`; `pkg-config` reported Wayland client 1.26.0, SceneFX 0.5.0 and wlroots 0.20.2. `ldd` with process-local `LD_LIBRARY_PATH` resolved the private `libscenefx-0.5.so` and system `libwlroots-0.20.so`. `nm -D` found the private `wlr_scene_tree_set_clip` and `wlr_scene_tree_get_clip` symbols. The copied SceneFX source matched the verified prior private source byte-for-byte in the modified files; no installed SceneFX or wlroots file changed.

### Evidence freeze and independent replay

The later evidence-freeze task preserved the six original source files and one
upstream protocol XML in [the Git fixture](../../tooling/probes/step20c-valid-grab/README.md).
The original six SHA-256 values above matched both the lab and the Git copies.
The XML at a pinned `wlr-protocols` commit regenerated the lab's virtual-pointer
header and C source byte-for-byte. No original fixture was edited, so there is
no adapted-source hash. The XDG protocol code, build directories, binaries,
logs, IPC JSON, screenshots, sockets and `transaction-before-hidden.c` remain
temporary artifacts outside Git; the latter is reconstructible by applying
the first Mosaic patch before the guard. The original `/tmp` lab remains
historical evidence, while the linked README can create a fresh lab at any
temporary path.

A fresh archive of Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754`
and a fresh clone of SceneFX `37ccd723bef49e6891156ffafce8f549f01446cc`
accepted their respective private patches with `git apply --check` and no
rejects. The guard then applied to the patched Mosaic source. The four changed
Mosaic/SceneFX files and the pre-guard transaction file matched the original
lab byte-for-byte. Both guarded and unguarded private compositors, the private
SceneFX library and both C clients compiled in the new lab. The replay runner
set per-case headless sockets and explicit `swaymsg -s`; inspection found no
path to the active Sway IPC socket.

The bounded replay ran `control boundary_left`, `private_standard
boundary_right`, `private_mosaic boundary_left`, guarded `private_mosaic`,
guarded `private_mosaic_hit`, and unguarded `private_mosaic_hit`. The control
and private standard used button serial 61 for both receipt and `xdg_popup.grab`;
private Mosaic used 55 for both. All received popup configure. The right-output
sample `(100,150)` stayed yellow `(224,192,32)` in control/private standard
and ordinary `(238,238,238)` in private Mosaic. With the owner hidden, the
unguarded left-output sample `(100,150)` stayed yellow and the popup received
right button 273; the guarded sample became background `(30,30,46)`, with no
hidden popup enter/button. The guarded no-click hide/return counted 39,520
exact yellow pixels before hiding, 0 while hidden and 39,520 after return,
without `popup_done` before return. The guarded hidden-click run did cause
`popup_done`, as expected for the valid grab's outside dismissal. These are
repeated **sampled** observations, not a wider qualification matrix.

## Decision and remaining gates

**PARTIALLY_FEASIBLE for this bounded probe.** The serial was genuinely received and used, the configured grabbed popup was interactive, and the private owner-visibility guard removed the demonstrated fully hidden owner pixel/hit leak while keeping the popup mapped for camera return. It also preserved sampled standard-layout behavior. The unguarded owner-derived viewport clip alone is **FAIL** for the hidden-owner invariant. A production policy for hiding versus dismissing or repositioning an offscreen popup is still undecided, and the private guard's use of `animation_state.current_width/height` needs a committed-generation/lifetime contract before any implementation. The probe did not exercise a valid-grab nested popup, vertical/negative/scaled/rotated outputs, output migration/resize, complete damage/effect/saved-buffer coverage, exact pending/current generation synchronization, or SceneFX/wlroots ABI/package maintenance. Those cells remain **NOT TESTED** or **PARTIAL**; multi-output Mosaic remains **NOT YET SUPPORTED**.

The smallest next experiment is a controlled valid-grab nested popup plus transaction/output-migration and damage measurements against the same unmodified SwayFX control, followed by a separate scientific/UX decision about offscreen popup lifecycle. Do not import either private patch into production on this evidence.
