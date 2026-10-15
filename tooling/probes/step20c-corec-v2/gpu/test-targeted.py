"""Offline source-only checks using explicit reconstructed CORE prerequisites."""
import argparse
import ctypes
import json
import resource
import shlex
import subprocess
import sys
from pathlib import Path

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
assert ctypes.CDLL(None).prctl(4, 0, 0, 0, 0) == 0
KIT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", required=True, type=Path, help="reconstructed CORE SceneFX source tree")
    parser.add_argument("--compile-commands", required=True, type=Path, help="CORE compile_commands.json")
    parser.add_argument("--work", required=True, type=Path, help="existing disposable directory for outputs/logs")
    args = parser.parse_args()
    core = args.core.resolve(strict=True)
    compile_commands = args.compile_commands.resolve(strict=True)
    work = args.work.resolve(strict=True)
    if not core.is_dir() or not work.is_dir():
        parser.error("--core and --work must be existing directories")
    if not compile_commands.is_file():
        parser.error("--compile-commands must name a regular file")
    entries = json.loads(compile_commands.read_text())
    source = core / "render/fx_renderer/fx_pass.c"
    entry = next((item for item in entries
                  if Path(item["file"]).as_posix().endswith("/render/fx_renderer/fx_pass.c")), None)
    if entry is None:
        parser.error("compile_commands.json has no entry for --core/render/fx_renderer/fx_pass.c")
    args_cc = shlex.split(entry["command"])
    args_cc = args_cc[args_cc.index("cc"):]
    base = []
    skip = False
    for token in args_cc:
        if skip:
            skip = False
            continue
        if token in ("-o", "-MF", "-MQ"):
            skip = True
            continue
        if token in ("-MD", "-c") or token.startswith("-std="):
            continue
        if token.endswith("/fx_pass.c"):
            continue
        base.append(token)
    base += ["-std=c17", "-D_GNU_SOURCE"]
    protocol_runner = """import sys,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
import test_protocol as t
t.BASE=Path(sys.argv[2])
with tempfile.TemporaryDirectory(prefix='protocol-controlled-', dir=t.BASE) as temp:
 p=Path(temp); p.chmod(0o700)
 for name in ('framing','accepted','rejected','token'): (p/name).mkdir(mode=0o700)
 with patch.object(t.protocol, 'FRAME', (2,3)):
  t.framing(p/'framing'); t.token_test(p/'token')
  t.scenario_test(p/'accepted',False); t.scenario_test(p/'rejected',True)
"""
    commands = [
        (["cc", "-std=c17", "-Wall", "-Wextra", "-Werror", "-I" + str(KIT), str(KIT / "test_gl.c"), "-o", str(work / "test_gl")], work),
        ([str(work / "test_gl")], work),
        (["python", str(KIT / "validate_source.py")], work),
        (base + [str(source), "-fsyntax-only"], Path(entry["directory"])),
        ([sys.executable, "-c", protocol_runner, str(KIT), str(work)], work),
        (base + ["-I" + str(core / "render/fx_renderer"), "-Wno-unused-function", "-ffunction-sections", "-fdata-sections", str(KIT / "test_native.c"), "-Wl,--gc-sections", "-o", str(work / "test_native")], Path(entry["directory"])),
        ([str(work / "test_native")], work),
    ]
    commands += [(["wayland-scanner", "client-header", str(KIT / "protocols" / xml), str(work / header)], work)
                 for xml, header in [("wlr-layer-shell-unstable-v1.xml", "layer-shell-client.h"), ("xdg-shell.xml", "xdg-shell-client.h")]]
    commands += [(["cc", "-std=c17", "-Wall", "-Wextra", "-Werror", "-Wno-unused-parameter", "-I" + str(work), "-fsyntax-only", str(KIT / "clients-g2.c")], work)]
    rows = []
    for index, (command, cwd) in enumerate(commands):
        result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        log = work / f"final-g2-test-{index}.log"
        log.write_text(result.stdout)
        rows.append({"command": command, "cwd": str(cwd), "returncode": result.returncode, "log": str(log)})
        print(f"{index}: exit={result.returncode}\n{result.stdout}")
        if result.returncode:
            break
    passed = len(rows) == len(commands) and all(row["returncode"] == 0 for row in rows)
    (work / "gpu-targeted-tests.json").write_text(json.dumps({
        "schema": "G2-targeted-source-only-portable-v1", "core": str(core),
        "compile_commands": str(compile_commands), "work": str(work),
        "core_limit": [0, 0], "test_process_dumpable": 0,
        "campaigns_started": 0, "commands": rows, "pass": passed,
        "native_build_or_runtime_started": False,
    }, indent=2) + "\n")
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
