#!/usr/bin/env python3
"""Assemble NEW private source trees; no build, install, runtime or Git mutation."""
import argparse, hashlib, io, json, os, pathlib, stat, subprocess, tarfile
HERE = pathlib.Path(__file__).resolve().parent

def run(argv, **kw):
    return subprocess.check_output(argv, stderr=subprocess.PIPE, **kw)

def manifest(root):
    result = {}
    for p in sorted(root.rglob("*")):
        if p.is_symlink():
            raise ValueError(f"Unexpected symlink: {p}")
        if p.is_file():
            result[str(p.relative_to(root))] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "mode": oct(p.stat().st_mode & 0o777)}
    return result

def verify(root, provenance):
    results = {}
    for name, entry in provenance["components"].items():
        actual = manifest(root / name)
        if actual != entry["files"]:
            raise ValueError(f"Source bytes/modes/file list mismatch: {name}")
        results[name] = {"files": len(actual), "manifest_sha256": hashlib.sha256(json.dumps(actual, sort_keys=True).encode()).hexdigest()}
    return results

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-git", type=pathlib.Path, required=True)
    ap.add_argument("--scene-git", type=pathlib.Path, help="optional read-only verified bare cache; otherwise fetch exact public pin")
    ap.add_argument("--destination", type=pathlib.Path, required=True)
    args = ap.parse_args()
    dest = args.destination.absolute()
    if not dest.is_relative_to(pathlib.Path("/var/tmp")) or dest == pathlib.Path("/var/tmp"):
        raise ValueError("Explicit destination strictly below /var/tmp required")
    if dest.exists() or dest.is_symlink() or dest.resolve() != dest:
        raise ValueError("Destination must be absent, without symlink ancestors")
    if not dest.parent.is_dir():
        raise ValueError("Existing destination parent required")
    # All generated writes, including Git/cache/Python temp files, remain here.
    os.umask(0o077)
    dest.mkdir(mode=0o700)
    if dest.stat().st_uid != os.getuid() or stat.S_IMODE(dest.stat().st_mode) != 0o700:
        raise ValueError("Destination owner/mode mismatch")
    for key, sub in [("TMPDIR", "scratch"), ("TMP", "scratch"), ("TEMP", "scratch"), ("XDG_CACHE_HOME", "cache"), ("CCACHE_DIR", "cache/ccache"), ("PYTHONPYCACHEPREFIX", "pycache"), ("XDG_DATA_HOME", "data")]:
        path = dest / sub
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.environ[key] = str(path)
    for key in ("SWAYSOCK", "WAYLAND_DISPLAY", "DISPLAY", "XDG_RUNTIME_DIR"):
        os.environ.pop(key, None)
    p = json.loads((HERE / "provenance.json").read_text())
    scene_git = args.scene_git
    if scene_git is None:
        scene_git = dest / "scene.git"
        run(["git", "init", "--bare", str(scene_git)])
        run(["git", "--git-dir=" + str(scene_git), "fetch", "--depth=1", p["scene_remote"], p["components"]["scene"]["pin"]])
    receipts = []
    for name, entry in p["components"].items():
        git = ["git", "--git-dir=" + str(scene_git)] if name == "scene" else ["git", "-C", str(args.project_git)]
        pin = entry["pin"]
        if run(git + ["rev-parse", pin + "^{commit}"]).decode().strip() != pin:
            raise ValueError("Commit mismatch")
        if run(git + ["rev-parse", pin + "^{tree}"]).decode().strip() != entry["parent_tree"]:
            raise ValueError("Parent tree mismatch")
        patch = HERE / entry["patch"]
        if hashlib.sha256(patch.read_bytes()).hexdigest() != entry["patch_sha256"]:
            raise ValueError("Patch checksum mismatch")
        root = dest / name
        root.mkdir(mode=0o700)
        archive = run(git + ["archive", "--format=tar", pin])
        with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
            tf.extractall(root, filter="data")
        # Disable discovery of any enclosing project repository.
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(dest))
        run(["git", "apply", "--check", str(patch)], cwd=root, env=env)
        run(["git", "apply", str(patch)], cwd=root, env=env)
        # git apply replaces changed regular files using process umask. Restore
        # their pinned regular-file mode explicitly inside this private tree.
        for relative in entry["changed_files"]:
            (root / relative).chmod(int(entry["files"][relative]["mode"], 8))
        receipts.append({"component": name, "parent_pin": pin, "parent_tree": entry["parent_tree"], "archive_sha256": hashlib.sha256(archive).hexdigest(), "patch_sha256": entry["patch_sha256"], "forward_apply_rc": 0})
    result = {"identity": p["identity"], "status": "EXACT_FOR_NEW_TREE", "components": verify(dest, p), "receipts": receipts}
    (dest / "assembly-receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
