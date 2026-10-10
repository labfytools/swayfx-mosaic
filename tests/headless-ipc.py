#!/usr/bin/env python3
"""Test d'intégration isolé : aucun socket ou processus de la session active."""

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time


def wait_for(predicate, seconds=8):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(0.05)
    raise RuntimeError("Délai dépassé pendant le test headless")


def stop_group(process):
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
    process.wait(timeout=5)


def main():
    if not all(shutil.which(name) for name in ("kitty", "swaymsg", "grim")):
        raise RuntimeError("kitty, swaymsg et grim sont requis pour ce test")
    binary = Path(os.environ.get("MOSAIC_BINARY", str(
        Path(__file__).resolve().parents[1] / "build-mosaic/sway/swayfx-mosaic")))
    if not binary.is_file():
        raise RuntimeError(f"Binaire absent : {binary}")

    with tempfile.TemporaryDirectory(prefix="mosaic-headless-") as root:
        runtime = Path(root)
        config = runtime / "config"
        config.write_text("workspace 1\n", encoding="utf-8")
        env = os.environ.copy()
        env.update(XDG_RUNTIME_DIR=root, WLR_BACKENDS="headless",
                   WLR_HEADLESS_OUTPUTS="1", WLR_RENDERER="pixman")
        env.pop("WAYLAND_DISPLAY", None)
        env.pop("SWAYSOCK", None)
        children = []
        with (runtime / "compositor.log").open("w") as log:
            compositor = subprocess.Popen([str(binary), "-c", str(config)],
                                          env=env, stdout=log,
                                          stderr=subprocess.STDOUT,
                                          start_new_session=True)
            try:
                def sockets():
                    ipc = list(runtime.glob("sway-ipc.*.sock"))
                    wayland = [entry for entry in runtime.glob("wayland-*")
                               if not entry.name.endswith(".lock")]
                    return (ipc[0], wayland[0]) if ipc and wayland else None

                socket, wayland = wait_for(sockets)
                env["WAYLAND_DISPLAY"] = wayland.name
                env["SWAYSOCK"] = str(socket)

                def ipc(*args):
                    result = subprocess.run(["swaymsg", "-s", str(socket), *args],
                                            env=env, text=True, capture_output=True,
                                            timeout=5, check=True)
                    return json.loads(result.stdout)

                def workspace():
                    tree = ipc("-t", "get_tree")
                    return next(node for output in tree["nodes"]
                                for node in output["nodes"]
                                if node["type"] == "workspace" and node["name"] == "1")

                assert workspace()["layout"] == "splith"
                assert ipc("layout mosaic")[0]["success"]
                assert workspace()["layout"] == "mosaic"
                assert ipc("-t", "get_workspaces")[0]["name"] == "1"

                def launch(index, expected):
                    child = subprocess.Popen(
                        ["kitty", "--class", f"mosaic-step20a-{index}",
                         "/usr/bin/sleep", "30"], env=env,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        start_new_session=True)
                    children.append(child)
                    return wait_for(lambda: workspace()["nodes"]
                                    if len(workspace()["nodes"]) == expected else None)

                a = launch(0, 1)[0]["id"]
                b = launch(1, 2)[1]["id"]
                c = launch(2, 3)[2]["id"]
                assert ipc(f"[con_id={a}] focus")[0]["success"]
                nodes = launch(3, 4)
                ids = [node["id"] for node in nodes]
                assert ids[0] == a and ids[2:] == [b, c], ids
                assert all(node["type"] == "con" for node in nodes)
                assert workspace()["floating_nodes"] == []
                # Les rectangles tiled ne se chevauchent pas ; les gaps Sway
                # configurés restent autorisés.
                assert all(left["rect"]["x"] + left["rect"]["width"] <=
                           right["rect"]["x"]
                           for left, right in zip(nodes, nodes[1:]))
                print("Insertion native :", ids, "(A, X, B, C)")

                assert ipc("focus right")[0]["success"]
                assert workspace()["focus"][0] == b
                assert ipc("focus left")[0]["success"]
                assert workspace()["focus"][0] == ids[1]
                assert [node["id"] for node in workspace()["nodes"]] == ids

                stop_group(children[2])
                nodes = wait_for(lambda: workspace()["nodes"]
                                 if len(workspace()["nodes"]) == 3 else None)
                assert [node["id"] for node in nodes] == ids[:3]
                print("Suppression native :", [node["id"] for node in nodes])
                assert ipc("move right")[0]["success"]
                assert workspace()["layout"] == "mosaic"
                moved = [node["id"] for node in workspace()["nodes"]]
                assert len(moved) == 3 and set(moved) == set(ids[:3]), moved
                print("Déplacement native :", moved)
                assert ipc("move left")[0]["success"]
                assert [node["id"] for node in workspace()["nodes"]] == ids[:3]
                after_move = [node["id"] for node in launch(4, 4)]
                assert after_move[:2] == ids[:2] and after_move[3] == b
                print("Insertion après déplacement :", after_move)
                assert ipc("layout splith")[0]["success"]
                assert workspace()["layout"] == "splith"
                assert [node["id"] for node in workspace()["nodes"]] == after_move
                assert ipc(f"[con_id={a}] focus")[0]["success"]
                assert ipc("layout mosaic")[0]["success"]
                assert workspace()["layout"] == "mosaic"
                reenabled = [node["id"] for node in launch(5, 5)]
                assert reenabled[0] == a and reenabled[2:] == after_move[1:]
                assert workspace()["floating_nodes"] == []
                print("Réactivation sur workspace occupé :", reenabled)

                ws = workspace()
                assert ws["nodes"][-1]["rect"]["x"] + ws["nodes"][-1]["rect"]["width"] > ws["rect"]["x"] + ws["rect"]["width"]
                assert ws["mosaic"]["rows"][0]["children"] == reenabled
                assert ipc(f"[con_id={a}] focus")[0]["success"]
                assert workspace()["mosaic"]["rows"][0]["scroll_x"] == 0
                time.sleep(0.2)  # Laisse finir la transaction Wayland précédente.
                def frame():
                    screenshot = subprocess.run(["grim", "-t", "ppm", "-"], env=env,
                                                capture_output=True, timeout=5,
                                                check=True)
                    return screenshot.stdout

                before_scroll = frame()
                logical_rects = [node["rect"] for node in workspace()["nodes"]]
                assert ipc("layout mosaic scroll 400")[0]["success"]
                assert workspace()["mosaic"]["rows"][0]["scroll_x"] == 400
                time.sleep(0.2)
                after_scroll = frame()
                assert len(after_scroll) == len(before_scroll)
                # A translated tiled scene changes a substantial number of
                # pixels; a blinking cursor alone cannot satisfy this bound.
                changed = sum(left != right for left, right in
                              zip(before_scroll, after_scroll))
                print("Composantes de couleur modifiées par scroll :", changed)
                assert changed > 1000
                assert [node["rect"] for node in workspace()["nodes"]] == logical_rects
                assert ipc("layout mosaic scroll -200")[0]["success"]
                assert workspace()["mosaic"]["rows"][0]["scroll_x"] == 200
                assert ipc(f"[con_id={reenabled[-1]}] focus")[0]["success"]
                assert workspace()["mosaic"]["rows"][0]["scroll_x"] > 200
                assert workspace()["mosaic"]["rows"][0]["focused"] == reenabled[-1]
                assert ipc(f"[con_id={a}] focus")[0]["success"]
                assert workspace()["mosaic"]["rows"][0]["scroll_x"] == 0
                print("Canvas tiled débordant et caméra logique : PASS")

                assert ipc("layout toggle mosaic")[0]["success"]
                assert workspace()["layout"] == "splith"
                assert ipc("layout tabbed")[0]["success"]
                assert ipc("layout toggle mosaic")[0]["success"]
                assert workspace()["layout"] == "mosaic"
                assert len(workspace()["nodes"]) == 5
                assert ipc("layout toggle mosaic")[0]["success"]
                assert workspace()["layout"] == "tabbed"
                print("Retour au layout tabbed choisi sur workspace occupé : PASS")
                assert ipc("workspace 2")[0]["success"]
                assert ipc("layout tabbed")[0]["success"]
                tree = ipc("-t", "get_tree")
                ws2 = next(node for output in tree["nodes"]
                           for node in output["nodes"]
                           if node["type"] == "workspace" and node["name"] == "2")
                assert ws2["layout"] == "tabbed"
                assert ipc("layout toggle mosaic")[0]["success"]
                assert ipc("layout toggle mosaic")[0]["success"]
                tree = ipc("-t", "get_tree")
                ws2 = next(node for output in tree["nodes"]
                           for node in output["nodes"]
                           if node["type"] == "workspace" and node["name"] == "2")
                assert ws2["layout"] == "tabbed"
                assert ipc("workspace 1")[0]["success"]
                assert ipc("layout toggle mosaic")[0]["success"]
                assert workspace()["layout"] == "mosaic"
                assert ipc("layout toggle mosaic")[0]["success"]
                assert workspace()["layout"] == "tabbed"
                helper = os.environ.get("MOSAIC_HELPER")
                if helper:
                    subprocess.run([helper], env=env, check=True, timeout=5)
                    assert workspace()["layout"] == "mosaic"
                    subprocess.run([helper], env=env, check=True, timeout=5)
                    assert workspace()["layout"] == "tabbed"
                print("Toggle Standard↔Mosaic par workspace : PASS")
                assert ipc("layout toggle mosaic")[0]["success"]
                assert ipc(f"[con_id={a}] focus")[0]["success"]
                assert ipc("floating enable")[0]["success"]
                wait_for(lambda: workspace()["floating_nodes"]
                         if len(workspace()["floating_nodes"]) == 1 else None)
                assert workspace()["layout"] == "mosaic"
                assert ipc("floating disable")[0]["success"]
                wait_for(lambda: workspace()["nodes"]
                         if len(workspace()["nodes"]) == 5 else None)
                assert ipc("fullscreen enable")[0]["success"]
                assert workspace()["layout"] == "mosaic"
                assert ipc("fullscreen disable")[0]["success"]
                assert ipc("move scratchpad")[0]["success"]
                wait_for(lambda: workspace()["nodes"]
                         if len(workspace()["nodes"]) == 4 else None)
                assert ipc("scratchpad show")[0]["success"]
                wait_for(lambda: workspace()["floating_nodes"]
                         if len(workspace()["floating_nodes"]) == 1 else None)
                print("Floating, fullscreen et scratchpad : PASS")
                print("IPC et bascules de layout : PASS")
            finally:
                for child in children:
                    stop_group(child)
                stop_group(compositor)


if __name__ == "__main__":
    main()
