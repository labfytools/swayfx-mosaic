"""Apply and verify G2 against an explicitly supplied reconstructed CORE tree.

Source-only operation: no build, compositor, Wayland or GPU work is performed.
"""
import argparse
import ctypes
import hashlib
import json
import resource
import shutil
import subprocess
from pathlib import Path

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
assert ctypes.CDLL(None).prctl(4, 0, 0, 0, 0) == 0

KIT = Path(__file__).resolve().parent
EXPECTED = {
    "render/fx_renderer/fx_pass.c": "c2886ef259fc91431dfe97841387082420ab80a0fe2f07e7dcdb71fc95731181",
    "render/fx_renderer/g2_gl.h": "cd175030be6a2e5d0af036c714c03455ef417f78f20360e00f7e6d1d7be7ab13",
    "render/fx_renderer/g2_native.h": "0dfa9e089853a078094736da7f4e133d7fd648500d380dd7f536a7a6f80fdd8e",
}
PATCH_SHA256 = "77d7445ceaf643fd5cc708d31c3f2c77feaeb80f8130c419c55e5514ecc8a75d"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(path):
    return {
        str(file.relative_to(path)): sha(file)
        for file in sorted(path.rglob("*"))
        if file.is_file() and ".git" not in file.relative_to(path).parts
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", required=True, type=Path, help="reconstructed CORE SceneFX source tree")
    parser.add_argument("--destination", required=True, type=Path, help="new, absent output directory")
    parser.add_argument("--work", required=True, type=Path, help="existing disposable directory for receipts/logs")
    args = parser.parse_args()
    core = args.core.resolve(strict=True)
    destination = args.destination.resolve()
    work = args.work.resolve(strict=True)
    if not core.is_dir() or not work.is_dir():
        parser.error("--core and --work must be existing directories")
    if destination.exists():
        parser.error("--destination must not already exist")
    if destination == core or destination in core.parents or core in destination.parents:
        parser.error("--destination must be separate from --core")
    patch_file = KIT / "g2-native.patch"
    if sha(patch_file) != PATCH_SHA256:
        parser.error("kit patch does not match its embedded publication hash")

    before = tree(core)
    shutil.copytree(core, destination, ignore=shutil.ignore_patterns(".git"))
    command = ["patch", "--batch", "--forward", "-p1", "-i", str(patch_file)]
    result = subprocess.run(command, cwd=destination, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    actual = tree(destination)
    changed = {name for name in before.keys() | actual.keys() if before.get(name) != actual.get(name)}
    expected_changed = set(EXPECTED)
    native_hashes = {name: actual.get(name) for name in sorted(expected_changed)}
    receipt = {
        "schema": "G2-portable-source-reproduction-v1",
        "status": "PASS" if result.returncode == 0 and changed == expected_changed and native_hashes == EXPECTED else "FAIL",
        "core": str(core),
        "destination": str(destination),
        "work": str(work),
        "patch_sha256": sha(patch_file),
        "command": command,
        "exit": result.returncode,
        "stdout": result.stdout,
        "changed_files": sorted(changed),
        "expected_native_sha256": EXPECTED,
        "actual_native_sha256": native_hashes,
        "all_changed_files_match_embedded_manifest": changed == expected_changed and native_hashes == EXPECTED,
        "core_unchanged": tree(core) == before,
        "runtime_or_build_started": False,
    }
    receipt_path = work / "gpu-patch-reproduction.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if receipt["status"] == "PASS" and receipt["core_unchanged"] else 1)


if __name__ == "__main__":
    main()
