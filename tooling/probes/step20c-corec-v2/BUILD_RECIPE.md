# Private CORE C V2 build recipe — EXPERIMENTAL

Run only after exact source/C independent review of the assembled source. This recipe creates no production install. Source reconstruction is exact; binary bit-for-bit reproducibility across compilers/timestamps is NOT PROVEN. Require >=20GiB filesystem free, new LAB solely below /var/tmp, redirected TMP/cache/data, no inherited display/session/loader routing, RLIMIT_CORE0, parallel jobs<=8. Use the assembled `scene` and `mosaic` directories, not a Mosaic checkout as pristine.

From an already owned LAB with sources assembled using the kit:

```sh
meson setup "$LAB/build-scene" "$ASSEMBLED/scene" --prefix=/usr --wrap-mode=nodownload -Ddefault_library=static -Dexamples=false
meson compile -C "$LAB/build-scene" -j8
```

Supply PKG_CONFIG_PATH="$LAB/build-scene/meson-uninstalled" for Mosaic setup only. Its pkg-config executable wrapper must invoke the real pkg-config using argv and add --static to --libs requests so the static archive dependency closure is linked; do not modify system pkg-config or install SceneFX. Retain wrapper bytes/argv/raw statuses and resolved dependency paths. Use default compiler for both libraries; record version and headers. A shell wrapper equivalent for these controlled invocations is `exec /usr/bin/pkg-config --static "$@"`; the executed campaign used a Python execv wrapper which appended --static only for --libs. Check the actual Ninja link command for the private archive and native symbols; a successful setup alone is insufficient.

```sh
PKG_CONFIG="$PRIVATE_PKG_CONFIG_WRAPPER" PKG_CONFIG_PATH="$LAB/build-scene/meson-uninstalled" meson setup "$LAB/build-mosaic" "$ASSEMBLED/mosaic" --prefix=/usr --bindir=bin --wrap-mode=nodownload -Dmosaic-package=true -Dsd-bus-provider=libsystemd -Dswaybar=false -Dswaynag=false -Dman-pages=disabled -Ddefault-wallpaper=false -Dc_args=-Wno-error=switch
meson compile -C "$LAB/build-mosaic" -j8
meson test -C "$LAB/build-mosaic" mosaic-model --print-errorlogs
```

The private c_args compatibility exception keeps -Wswitch warnings visible. GCC16.2.1 plus the installed newer libinput enum SCROLL_CIRCULAR caused the original -Werror build failure at upstream ipc-json.c1175. scroll_method is initialized to unknown before that switch, so no source change was made. Original failure and final warning remain evidence. It is not a general permission to suppress compiler failures.

Verify readelf/nm/ldd-r, no SceneFX DT_NEEDED/RPATH/RUNPATH, exact wlroots SHA7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837 and actual factory binding from wlroots to the executable before runtime. Stage only Mosaic with `DESTDIR="$LAB/stage" meson install -C "$LAB/build-mosaic" --no-rebuild`; add the three exact pinned LICENSE texts and conservative INCORPORATED-NOTICES. Exactly binary0755 plus four notices0644 are allowed under the ticket paths. No symlinks, library or system package. LEGAL_NOT_APPROVED.

This recipe does not reserve a build/run or authorize bypassing budgets/publication/review. Every new build identity requires its own measured SHA/BuildID and reviewer receipt. Retained pristine is independently qualified, never built from these Mosaic sources. No compositor --version or live IPC is part of build validation.

## Separate diagnostic variants

OOM uses `python3 oom/assemble-variant.py --core "$ASSEMBLED" --destination "$OOM_SOURCES"` with an absent destination below /var/tmp. Its complete parent and result manifests are embedded in oom/provenance.json. Build the resulting scene/mosaic using the same private recipe, distinct directories and identity.

GPU uses `python3 gpu/reproduce.py --core "$ASSEMBLED/scene" --destination "$GPU_SCENE" --work "$GPU_WORK"`. Mosaic sources remain the exact CORE sources. For the private GPU SceneFX setup additionally use `-Dc_args=-D_XOPEN_SOURCE=700`; the initial build failure for an undeclared realpath prototype is preserved. This feature macro exposes the XSI declaration without suppressing type diagnostics or changing source. Every binary is separately qualified. The native acquisition root intentionally binds this diagnostic identity to /var/tmp/swayfx-mosaic-corec-v2-i516p6po/gpu-work/acquisition. Rebinding it creates a new source and binary identity requiring new review, not a reuse of this candidate's native evidence.

The G2 client can be compiled without running it: generate client-header and private-code for gpu/protocols/xdg-shell.xml and wlr-layer-shell-unstable-v1.xml into an explicit private build directory. Name the headers xdg-shell-client.h and layer-shell-client.h. Compile gpu/clients-g2.c plus both generated protocol C files with `cc -std=c17 -O2 -Wall -Wextra -Werror -Wno-unused-parameter -I "$CLIENT_BUILD" ... -o "$CLIENT_BUILD/g2-client" $(pkg-config --cflags --libs wayland-client)`. Capture exact argv and SHA of inputs/outputs. Compilation alone grants no run admission.
