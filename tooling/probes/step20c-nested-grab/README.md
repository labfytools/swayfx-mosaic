# STEP20C nested valid-grab fixture (EXPERIMENTAL)

This source-only fixture reproduces the [nested popup probe](../../../docs/design/STEP20C_NESTED_VALID_GRAB_PROBE.md).
It does not enter the Mosaic build, production patch or package. It reuses
the unchanged `pointer-daemon.c`, virtual-pointer XML and three private
patches from [`../step20c-valid-grab/`](../step20c-valid-grab/README.md).

## Bases and dependencies

| Input | Pinned base / version | SHA-256 |
| --- | --- | --- |
| Mosaic private patch | Mosaic `cd550382b311efdbfe3ed892f4e1d281d852e754` | `d416f6413ea097a48a44d231e50ffba363914f46c8687f0ea2e4dcacd5f31fe9` |
| SceneFX private patch | SceneFX `37ccd723bef49e6891156ffafce8f549f01446cc` (0.5) | `c74c515b98da8f5f637e260e6a3755c7a75bd78d1c39e54a67850f1c383e30e7` |
| Hidden-owner guard | After Mosaic private patch | `35785a8f3e863b3c1fd87932d8ff0c2949b03cb04382cc34e1126170968f802b` |
| Persistent virtual pointer | Previous fixture | `a00fcedc38ccb7ca4c25c982d9f38e8bde3168a3833f0c9cf2056e841d720938` |
| Virtual-pointer XML | wlr-protocols `b010a03648b88d143236de193bddbfea0c08bc84` | `3ff6d540be0bc5228195bf072bde42117ea17945a5c2061add5d3cf97d6bb524` |
| `nested-client.c` | This fixture | `2e40c98af72a0df8b316810589a0be8f4425a763db1de448b49a7813956b6f7d` |
| `prepare.sh` | This fixture, post-audit failed-build cleanup | `55fe81b7f17fb1cf8af7089a0034864910c49feccbe4cfe22e857c98b9db0dde` |
| `run.py` | This fixture, post-audit socket isolation and cleanup | `72ff17d8042edf3265b3a0ff91f0bc4805001b1438c4ecadfe29ead76278c9be` |

The measured machine had SwayFX 0.6, wlroots 0.20.2, SceneFX 0.5.0,
Wayland client 1.26.0 and wayland-protocols 1.49. The installed XDG Shell
XML declares version 7; the fixture binds `xdg_wm_base` version 3, like
the previous client. Required local tools include Git, Meson, Ninja, C17
compiler, `pkg-config`, `wayland-scanner`, `kitty`, `swaymsg`, `grim`, `wev`
and Python. `prepare.sh` downloads the pinned SceneFX source into a disposable
directory; it does not install anything.

## Differences from the earlier fixture

`nested-client.c` creates three distinct surfaces and XDG roles. Popup A's
parent is the toplevel `xdg_surface`; popup B's parent is A's `xdg_surface`.
Each popup uses a separate, logged, real pointer-button serial and maps only
after its own configure/ack. The client logs all surface object IDs, events,
local pointer coordinates, `popup_done` and child-first destruction. It accepts
`close_b` and `close_owner` on stdin. The runner exercises three placements:
`visible`, `b_cross` and `both_cross`. No prior source file is modified.

## Fresh replay

Run from a fresh repository checkout at or after the preserved fixture commit.
No old `/tmp` laboratory is needed. The script prints `LAB=/tmp/...` after
building a private SceneFX library, private guarded compositor, new client and
unchanged virtual-pointer daemon. Save that path for subsequent commands.

```sh
prepare_log=$(mktemp /tmp/mng-prepare-XXXXXXXX)
sh tooling/probes/step20c-nested-grab/prepare.sh | tee "$prepare_log"
LAB=$(sed -n 's/^LAB=//p' "$prepare_log")
test -d "$LAB"
python tooling/probes/step20c-nested-grab/run.py "$LAB" control visible_click visible
python tooling/probes/step20c-nested-grab/run.py "$LAB" private_standard visible_click visible
python tooling/probes/step20c-nested-grab/run.py "$LAB" private_mosaic visible_click visible
python tooling/probes/step20c-nested-grab/run.py "$LAB" private_mosaic crossing b_cross
python tooling/probes/step20c-nested-grab/run.py "$LAB" private_mosaic crossing both_cross
python tooling/probes/step20c-nested-grab/run.py "$LAB" private_mosaic close_b visible
python tooling/probes/step20c-nested-grab/run.py "$LAB" private_mosaic outside visible
python tooling/probes/step20c-nested-grab/run.py "$LAB" private_mosaic hidden b_cross
python tooling/probes/step20c-nested-grab/run.py "$LAB" private_mosaic hidden_click b_cross
python tooling/probes/step20c-nested-grab/run.py "$LAB" private_mosaic owner visible
python tooling/probes/step20c-nested-grab/run.py "$LAB" private_mosaic toggle b_cross
```

For a full comparison, repeat `crossing`, `close_b`, `outside` and `owner`
with `control` and `private_standard` as in the report. Each case name is
single-use in a lab; use a new lab or rename an earlier case directory to
retain both iterations. `run.py` uses a short, new `/tmp/mng-*` runtime path
because Unix socket paths have a strict length limit; each case's
`runtime-path` records the path for audit. The script removes inherited desktop
Wayland/IPC variables, uses explicit `swaymsg -s`, terminates and reaps only
its own process groups, then removes its runtime directory. It never reloads
or replaces the daily compositor.

The retained historical runs used the earlier runner and preparation hashes;
the current `prepare.sh` removes an incomplete laboratory on failure, while
`run.py` adds an IPC path-length bound, clears inherited
`I3SOCK`, reaps child processes and removes its runtime directory. It changes
no popup protocol action, capture point or experimental compositor patch.

Each case contains `client.log` with `WAYLAND_DEBUG=1`, `pointer.log`,
`compositor.log`, `wev.log`, `tree-*.json`, `outputs-*.json` and both output
PNGs. Read `POPUP_A/B CREATE`, `GRAB_REQUEST`, `ROLE_CONFIGURE`,
`XDG_CONFIGURE`, `MAP`, `POINTER_*`, `POPUP_DONE` and `DESTROY` in order.
Compare screenshots and traces: a right-output pixel alone does not prove
which surface received a button, and `popup_done` under a legitimate grab
does not prove an invisible surface hit. The `open` scenario intentionally
only captures mapping; `visible_click` also presses B. A case returning zero
is not automatically a scientific PASS.

## Cleanup

After all per-case processes have exited, check `runtime-path` files for any
directory left by an interrupted run and remove only those recorded `/tmp/mng-*`
directories, then remove the named `LAB` directory and `prepare_log`. Preserve
the laboratory while reviewing evidence. Generated
protocol files, binaries, private libraries, sockets, logs and images remain
outside Git. The source fixture and original patches stay in Git.
