#!/usr/bin/env python3
"""Sonde spécifique STEP20C : plan passif, puis au plus une tentative approuvée."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import stat
import subprocess
import sys
import time
import types

class _SealedHelper:
    """Chargement différé : le digest du helper précède son import dans main."""

    module = None

    def __getattr__(self, name):
        if self.module is None:
            path = Path(__file__).resolve().with_name("cgroup_gate.py")
            # SourceFileLoader can write __pycache__ even for a passive plan.
            # Compile the sealed sibling bytes directly, without a loader cache.
            module = types.ModuleType("mosaic_cgroup_gate")
            module.__file__ = str(path)
            exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
            self.module = module
        return getattr(self.module, name)


gate = _SealedHelper()

LIMIT = 1024 * 1024
ENV = {
    "PATH": "/usr/bin", "PWD": "/tmp", "LC_ALL": "C",
    "WLR_RENDERER_FORCE_SOFTWARE": "1", "WLR_RENDERER_ALLOW_SOFTWARE": "1",
    "LIBGL_ALWAYS_SOFTWARE": "1", "LP_NUM_THREADS": "2",
    "__EGL_VENDOR_LIBRARY_FILENAMES": "/usr/share/glvnd/egl_vendor.d/50_mesa.json",
}
HOST_ENV = {"PATH": "/usr/bin", "LC_ALL": "C"}


class Refusal(Exception):
    """Le contrat scellé n'est pas satisfait ; ne pas franchir la frontière native."""


def digest(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def command(lab):
    """Liste fermée : aucun mount, argument ou environnement fourni par l'appelant."""
    argv = [
        "/usr/bin/prlimit", "--as=1073741824", "--cpu=5", "--nofile=64",
        "--fsize=1048576", "--core=0", "--",
        "/usr/bin/bwrap", "--unshare-user", "--unshare-all", "--disable-userns",
        "--new-session", "--die-with-parent", "--clearenv", "--ro-bind", "/usr", "/usr",
        "--symlink", "usr/bin", "/bin", "--symlink", "usr/lib", "/lib",
        "--symlink", "usr/lib", "/lib64", "--proc", "/proc", "--dev", "/dev",
        "--tmpfs", "/dev/shm", "--tmpfs", "/tmp", "--tmpfs", "/run",
        "--ro-bind", str(lab / "bin/probe"), "/probe", "--chdir", "/tmp",
    ]
    for key, value in ENV.items():
        argv.extend(["--setenv", key, value])
    return argv + ["--", "/probe"]


def benign_command(mode):
    """Deux charges fixes, inoffensives, sans Bubblewrap ni bibliothèque EGL."""
    if mode not in ("nominal", "parent-death"):
        raise Refusal("qualification mode invalide")
    delay = "0.2" if mode == "nominal" else "30"
    if mode == "parent-death":
        # Le superviseur peut fermer le pipe avant l'écriture ; le délai doit
        # quand même laisser managerRuntime12 observer la mort du parent.
        script = ("import os,time\n"
                  "try:\n os.write(1,b'BENIGN_PAYLOAD_STARTED\\n')\n"
                  "finally:\n time.sleep(30)")
    else:
        script = ("import os,time; os.write(1,b'BENIGN_PAYLOAD_STARTED\\n'); "
                  "time.sleep(" + delay + ")")
    return ["/usr/bin/python3", "-I", "-S", "-B", "-c", script]


def verify(lab, expected):
    """Lecture seule, y compris pour le plan ; le digest doit venir de la revue."""
    if dict(os.environ) != HOST_ENV:
        raise Refusal("environnement superviseur non conforme ; utiliser env -i")
    if not lab.is_absolute() or lab.resolve() != lab:
        raise Refusal("LAB absolu sans symlink requis")
    info = lab.stat()
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise Refusal("LAB privé mode0700 requis")
    manifest_path = lab / "manifest.json"
    if digest(manifest_path) != expected:
        raise Refusal("digest du manifeste différent de l'approbation")
    manifest = json.loads(manifest_path.read_text())
    if manifest["schema"] != 2 or manifest["lab"] != str(lab):
        raise Refusal("identité du manifeste")
    kind = manifest["kind"]
    if kind not in ("benign", "egl"):
        raise Refusal("type de charge invalide")
    expected_argv = (benign_command(manifest["qualification_mode"])
                     if kind == "benign" else command(lab))
    expected_env = HOST_ENV if kind == "benign" else ENV
    helper = lab / "fixture/cgroup_gate.py"
    helper_identity = manifest["files"].get(str(helper))
    if (not helper_identity or digest(helper) != helper_identity["sha256"]
            or str(helper.resolve()) != helper_identity["resolved"]):
        raise Refusal("identité helper altérée avant import")
    if manifest["scope_argv"] != gate.sealed_scope_argv(lab, manifest):
        raise Refusal("argv du scope altéré")
    if manifest["scope"] != gate.policy(manifest["scope"]["nonce"]):
        raise Refusal("politique scope altérée")
    if manifest["argv"] != expected_argv or manifest["environment"] != expected_env:
        raise Refusal("montages, devices ou environnement altérés")
    if manifest["supervisor_environment"] != HOST_ENV:
        raise Refusal("environnement du superviseur altéré")
    required = {str(lab / "fixture/run.py"),
                str(lab / "fixture/cgroup_gate.py"), "/usr/bin/python3",
                "/usr/bin/systemd-run", "/usr/bin/systemctl", "/usr/bin/env",
                "/usr/bin/readelf"}
    if kind == "egl":
        required.update({str(lab / "bin/probe"), "/usr/bin/bwrap", "/usr/bin/prlimit"})
    if not required.issubset(manifest["files"]):
        raise Refusal("identités requises absentes")
    if Path(__file__).resolve() != lab / "fixture/run.py":
        raise Refusal("utiliser le lanceur scellé du LAB")
    for name, identity in manifest["files"].items():
        path = Path(name)
        if not (path.is_relative_to(lab) or path.is_relative_to("/usr")):
            raise Refusal("dépendance hors LAB neuf ou /usr")
        if digest(path) != identity["sha256"]:
            raise Refusal(f"dérive identité : {path}")
        if not (path.resolve().is_relative_to(lab) or path.resolve().is_relative_to("/usr")):
            raise Refusal(f"dépendance résolue hors LAB ou /usr : {path}")
        if str(path.resolve()) != identity["resolved"]:
            raise Refusal(f"dérive symlink : {path}")
    return manifest


def durable(path, data, exclusive=False):
    """Reçu borné et durable ; O_EXCL rend le budget irréversible avant spawn."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    destination = path if exclusive else path.with_suffix(path.suffix + ".tmp")
    fd = os.open(destination, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if not exclusive:
            os.replace(destination, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except BaseException:
        # A partial ATTEMPT still consumes the budget; do not remove it.
        raise


def supervise(argv, payload_seconds=8.0, total_seconds=10.0):
    """Deux pipes bornés, collecte du seul groupe possédé, aucun retry.

    bwrap conserve le PID namespace jusqu'à la fin du payload ; sa disparition
    termine les descendants de ce namespace. Pas de kill d'un PID déjà récolté.
    Les limites AS/CPU sont par processus ; NPROC hérité porte sur l'UID, pas un cgroup.
    Ce collecteur historique est testé séparément ; main utilise gate.run_scope.
    """
    started = time.monotonic()
    channels = [bytearray(), bytearray()]
    cause = "exit"
    diagnostic = None
    process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=HOST_ENV, close_fds=True,
                               start_new_session=True)
    pidfd = None
    try:
        if hasattr(os, "pidfd_open"):
            try:
                pidfd = os.pidfd_open(process.pid)
            except OSError:
                # Popen remains unreaped and owns this PID during cleanup.
                pidfd = None
        with selectors.DefaultSelector() as selector:
            for index, stream in enumerate((process.stdout, process.stderr)):
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, selectors.EVENT_READ, index)
            killed = False
            while selector.get_map():
                elapsed = time.monotonic() - started
                if not killed and elapsed >= payload_seconds:
                    cause = "timeout"
                if not killed and cause != "exit":
                    # Do not poll/reap before killpg: an unreaped child prevents
                    # PID reuse, even if the child exited between these steps.
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass  # Already exited, still explicitly collected below.
                    killed = True
                if elapsed >= total_seconds:
                    cause = "cleanup_unproven"
                    break
                for key, _ in selector.select(min(0.05, total_seconds - elapsed)):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    target = channels[key.data]
                    room = LIMIT - len(target)
                    target.extend(chunk[:room])
                    if len(chunk) > room and cause == "exit":
                        cause = "output_overflow"
            elapsed = time.monotonic() - started
            wait_budget = total_seconds if killed else payload_seconds
            try:
                code = process.wait(timeout=max(0.001, wait_budget - elapsed))
            except subprocess.TimeoutExpired:
                # Pipes can close while the leader still runs. Preserve the
                # cleanup reserve instead of spending it waiting for payload.
                if cause == "exit":
                    cause = "timeout"
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                try:
                    code = process.wait(timeout=max(0.001, total_seconds -
                                                    (time.monotonic() - started)))
                except subprocess.TimeoutExpired:
                    code = None
                    cause = "cleanup_unproven"
    except BaseException as error:
        # Popen has not been reaped on exceptional drain paths. Never abandon
        # a child because selector/read/collection itself failed.
        cause = "supervisor_failure"
        diagnostic = f"{type(error).__name__}: {error}"[:512]
        code = process.returncode
        if code is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                code = process.wait(timeout=max(0.001, total_seconds -
                                                (time.monotonic() - started)))
            except subprocess.TimeoutExpired:
                code = None
                cause = "cleanup_unproven"
        if not isinstance(error, Exception):
            # Interruption is recorded after cleanup, not allowed to lose the
            # irreversible attempt or raw evidence.
            cause = "interrupted" if code is not None else "cleanup_unproven"
    finally:
        process.stdout.close()
        process.stderr.close()
        if pidfd is not None:
            os.close(pidfd)
    return {"cause": cause, "returncode": code, "error": diagnostic,
            "collected": code is not None, "elapsed": time.monotonic() - started}, channels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab", required=True, type=Path)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--approve-native-probe", action="store_true")
    parser.add_argument("--approve-benign-gate", action="store_true")
    args = parser.parse_args()
    try:
        manifest = verify(args.lab, args.manifest_sha256)
        if (args.lab / "ATTEMPT").exists():
            raise Refusal("budget déjà consommé ; aucun retry")
        approved = args.approve_native_probe or args.approve_benign_gate
        if not approved:
            print(json.dumps({"runtime": "NOT_RUN", "budget": 1,
                              "argv": manifest["argv"], "scope": manifest["scope"],
                              "environment": manifest["environment"]}, indent=2))
            return 0
        if (args.approve_native_probe == args.approve_benign_gate or
                args.approve_benign_gate != (manifest["kind"] == "benign")):
            raise Refusal("drapeau approbation incompatible avec le manifeste")

        def reserve(evidence):
            durable(args.lab / "ATTEMPT", json.dumps({
                "manifest_sha256": args.manifest_sha256, "budget_consumed": 1,
                "scope": manifest["scope"], "preflight": evidence,
            }).encode() + b"\n", exclusive=True)

        def journal(result):
            durable(args.lab / "result.json", json.dumps(result, sort_keys=True).encode() + b"\n")

        result, channels = gate.run_scope(args.lab, manifest, reserve, journal)
        if not (args.lab / "ATTEMPT").exists():
            # Failed read-only preflight does not consume or mutate the LAB.
            print(json.dumps(result))
            return 20
        for name, data in zip(("stdout.raw", "stderr.raw"), channels):
            durable(args.lab / name, data)
        durable(args.lab / "result.json", json.dumps(result, sort_keys=True).encode() + b"\n")
        print(json.dumps(result))
        return 0 if result.get("cause") == "exit" and result.get("returncode") == 0 else 20
    except (RuntimeError, Refusal, OSError, ValueError, KeyError, TypeError) as error:
        print(f"Refus : {error}", file=sys.stderr)
        return 20


if __name__ == "__main__":
    sys.exit(main())
