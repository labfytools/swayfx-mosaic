#!/usr/bin/env python3
"""Préparation passive STEP20C. Compile/inspecte, n'exécute jamais le helper."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tarfile

from run import ENV, HOST_ENV, command, digest, durable

PINS = {
    "scenefx": "37ccd723bef49e6891156ffafce8f549f01446cc",
    "wlroots": "d783533489e1f75d6886c2ab5c5960090ef268f8",
}
FIXTURE = Path(__file__).resolve().parent


def capture(argv):
    return subprocess.check_output(argv, env=HOST_ENV, stderr=subprocess.STDOUT)


def archive_sources(bare, pin, destination):
    """git archive lit seulement le dépôt historique ; vérifier chaque blob extrait."""
    actual = capture(["/usr/bin/git", "--git-dir", str(bare), "rev-parse", pin + "^{commit}"]).decode().strip()
    if actual != pin:
        raise ValueError("commit différent du pin")
    archive = capture(["/usr/bin/git", "--git-dir", str(bare), "archive", pin])
    destination.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        stream.extractall(destination, filter="data")
    tree = capture(["/usr/bin/git", "--git-dir", str(bare), "ls-tree", "-rz", pin])
    count = 0
    for record in tree.split(b"\0"):
        if not record:
            continue
        metadata, raw_name = record.split(b"\t", 1)
        mode, kind, oid = metadata.split()
        if kind != b"blob":
            raise ValueError("type git inattendu")
        path = destination / os.fsdecode(raw_name)
        content = os.readlink(path).encode() if mode == b"120000" else path.read_bytes()
        identity = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        if identity != oid.decode():
            raise ValueError(f"blob différent : {path}")
        count += 1
    return {"commit": pin, "archive_sha256": hashlib.sha256(archive).hexdigest(),
            "verified_blobs": count}


def resolve_library(name):
    if "/" in name:
        path = Path(name)
        if path.is_absolute() and path.is_relative_to("/usr") and path.exists():
            return path
        raise ValueError(f"bibliothèque hors /usr : {name}")
    path = Path("/usr/lib") / name
    if not path.is_file():
        raise ValueError(f"dépendance ELF introuvable : {name}")
    return path


def elf_closure(seeds):
    """Fermeture DT_NEEDED passive ; aucune utilisation de ldd/loader."""
    result = {}
    pending = list(seeds)
    seen = set()
    while pending:
        path = pending.pop()
        if str(path) in result:
            continue
        data = capture(["/usr/bin/readelf", "-dW", str(path)]).decode()
        notes = capture(["/usr/bin/readelf", "-nW", str(path)]).decode()
        needed = re.findall(r"\(NEEDED\).*\[([^]]+)\]", data)
        build_id = re.search(r"Build ID: ([0-9a-f]+)", notes)
        result[str(path)] = {"needed": needed,
                             "build_id": build_id.group(1) if build_id else None}
        canonical = path.resolve()
        if canonical not in seen:
            seen.add(canonical)
            pending.extend(resolve_library(name) for name in needed)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab", type=Path, required=True)
    parser.add_argument("--source-store", type=Path, required=True)
    args = parser.parse_args()
    lab = args.lab
    if not lab.is_absolute() or lab.resolve() != lab:
        raise ValueError("LAB absolu sans symlink requis")
    if lab.exists():
        if lab.stat().st_uid != os.getuid() or lab.stat().st_mode & 0o777 != 0o700:
            raise ValueError("LAB privé mode0700 requis")
        if any(path.name != "evidence" for path in lab.iterdir()):
            raise ValueError("LAB déjà préparé ; aucune réutilisation")
    else:
        lab.mkdir(mode=0o700)
    for name in ("fixture", "sources", "generated", "bin", "evidence"):
        (lab / name).mkdir(exist_ok=True)
    for name in ("probe.c", "run.py", "prepare.py", "test_probe.py", "test_probe_mocks.c", "README.md"):
        shutil.copyfile(FIXTURE / name, lab / "fixture" / name)
    provenance = {}
    for name, pin in PINS.items():
        provenance[name] = archive_sources(args.source_store / (name + ".git"), pin,
                                            lab / "sources" / name)
    # Only generated config/version headers come from the installed build.
    generated = lab / "generated/wlr"
    generated.mkdir()
    for name in ("config.h", "version.h"):
        shutil.copyfile(Path("/usr/include/wlroots-0.20/wlr") / name, generated / name)
    packages = ["scenefx-0.5", "wlroots-0.20", "wayland-server", "egl", "glesv2", "pixman-1", "libdrm"]
    flags = shlex.split(capture(["/usr/bin/pkg-config", "--cflags", *packages]).decode())
    libs = shlex.split(capture(["/usr/bin/pkg-config", "--libs", *packages]).decode())
    if libs.index("-lscenefx-0.5") >= libs.index("-lwlroots-0.20"):
        raise ValueError("ordre de liaison SceneFX puis wlroots requis")
    base = ["/usr/bin/cc", "-std=c17", "-Wall", "-Wextra", "-Werror",
            "-DWLR_USE_UNSTABLE", "-I" + str(lab / "generated"),
            "-I" + str(lab / "sources/scenefx/include"),
            "-I" + str(lab / "sources/wlroots/include"), *flags]
    source = str(lab / "fixture/probe.c")
    commands = [base + ["-fsyntax-only", source],
                base + ["-M", "-MF", str(lab / "evidence/compiled.d"), source],
                base + [source, "-Wl,-z,now", "-Wl,-z,relro", "-o", str(lab / "bin/probe"), *libs]]
    for index, argv in enumerate(commands):
        output = capture(argv)
        durable(lab / "evidence" / f"compile-{index}.log", output)
    deptext = (lab / "evidence/compiled.d").read_text().replace("\\\n", " ")
    dependencies = [Path(name) for name in shlex.split(deptext.split(":", 1)[1])]
    compared = []
    for dependency in dependencies:
        for project, installed in (("scenefx", "/usr/include/scenefx-0.5"),
                                   ("wlroots", "/usr/include/wlroots-0.20")):
            root = lab / "sources" / project / "include"
            if dependency.is_relative_to(root):
                counterpart = Path(installed) / dependency.relative_to(root)
                if counterpart.is_file():
                    if dependency.read_bytes() != counterpart.read_bytes():
                        raise ValueError(f"header installé différent du pin : {counterpart}")
                    compared.append(str(counterpart))
    vendor_json = Path(ENV["__EGL_VENDOR_LIBRARY_FILENAMES"])
    vendor_library = resolve_library(json.loads(vendor_json.read_text())["ICD"]["library_path"])
    # Mesa uses dlopen as well as DT_NEEDED. Seal explicit software DRI,
    # GBM plugin and gallium provider, then their entire DT_NEEDED closure.
    seeds = [lab / "bin/probe", Path("/usr/bin/bwrap"), Path("/usr/bin/prlimit"),
             Path("/usr/bin/python3"), Path("/usr/bin/env"), Path("/usr/lib/ld-linux-x86-64.so.2"),
             vendor_library, Path("/usr/lib/dri/swrast_dri.so")]
    seeds.extend(Path("/usr/lib").glob("libgallium-*.so"))
    seeds.append(Path("/usr/lib/gbm/dri_gbm.so"))
    closure = elf_closure(seeds)
    # Symbols must be definitions in the expected ELF, not merely declarations.
    symbols = {}
    expected = {
        "/usr/lib/libscenefx-0.5.so": ["wlr_egl_create_with_drm_fd", "wlr_egl_destroy",
                                     "wlr_egl_get_display", "fx_renderer_create_egl"],
        "/usr/lib/libwlroots-0.20.so": ["wlr_renderer_get_render_formats"],
    }
    for filename, names in expected.items():
        table = capture(["/usr/bin/readelf", "--dyn-syms", "-W", filename]).decode()
        for name in names:
            if not any(line.split()[-1:] == [name] and " UND " not in line for line in table.splitlines()):
                raise ValueError(f"symbole défini absent : {name}")
        symbols[filename] = names
    files = set(dependencies + [Path(name) for name in closure] + [vendor_json])
    files.update(Path(name) for name in compared)
    files.update(path for root in ("fixture", "sources", "generated")
                 for path in (lab / root).rglob("*") if path.is_file())
    files.update(Path("/usr/bin") / name for name in ("cc", "pkg-config", "readelf", "git"))
    files.update(Path("/usr/lib/pkgconfig") / (name + ".pc") for name in packages)
    identities = {str(path): {"sha256": digest(path), "resolved": str(path.resolve())}
                  for path in sorted(files)}
    manifest = {
        "schema": 1, "lab": str(lab), "runtime": "NOT_RUN", "budget": 1,
        "argv": command(lab), "environment": ENV, "supervisor_environment": HOST_ENV,
        "pins": provenance, "files": identities, "elf_closure": closure,
        "symbols": symbols, "compile_commands": commands,
        "compared_installed_headers": compared,
        "provenance_limit": "Installed ELF bytes are pinned, not reproduced from source. "
                            "Header equality and exported symbols do not prove binary source identity.",
        "dlopen_limit": "Explicit Mesa EGL, swrast, GBM and gallium providers plus DT_NEEDED "
                        "are sealed; conditional runtime dlopen discovery remains NOT_RUN.",
    }
    durable(lab / "manifest.json", json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n")
    seal = digest(lab / "manifest.json")
    print(json.dumps({"runtime": "NOT_RUN", "manifest_sha256": seal, "plan_command":
                     ["/usr/bin/env", "-i", "PATH=/usr/bin", "LC_ALL=C",
                      "/usr/bin/python3", "-I", str(lab / "fixture/run.py"), "--lab", str(lab),
                      "--manifest-sha256", seal]}, indent=2))


if __name__ == "__main__":
    main()
