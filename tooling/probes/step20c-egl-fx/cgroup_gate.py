#!/usr/bin/env python3
"""Admission expérimentale cgroup v2 ; aucun effet à l'importation.

Le seul bootstrap natif est fixe et bloqué sur un socket privé. systemd-run
n'a pas besoin de transmettre un descripteur : le bootstrap se connecte par
nom, puis les deux extrémités vérifient SO_PEERCRED et la durée de vie PID.
"""
import argparse
import json
import os
from pathlib import Path
import re
import resource
import select
import selectors
import socket
import stat
import struct
import subprocess
import sys
import threading
import time

CLEAN_ENV = {"PATH": "/usr/bin", "LC_ALL": "C"}
TASKS = 256
# systemctl show renders these D-Bus microsecond properties as durations.
# Compare its exact CLI representation, matching the fixed Sec= launch options.
POLICY = {"Delegate": "yes", "TasksMax": "256", "RuntimeMaxUSec": "12s",
          "TimeoutStopUSec": "2s", "KillMode": "control-group"}
LIMIT = 1048576


class Refusal(RuntimeError):
    """Une preuve absente ou contradictoire interdit la libération."""


def require(condition, message):
    if not condition:
        raise Refusal(message)


def policy(nonce):
    """Identité fraîche, scellée dans le manifeste ; jamais un nom réutilisable."""
    require(re.fullmatch(r"[0-9a-f]{32}", nonce) is not None, "nonce invalide")
    return {"nonce": nonce, "unit": "mosaic-egl-" + nonce + ".scope",
            "description": "Mosaic experimental admission " + nonce,
            "properties": dict(POLICY), "pids_max": TASKS}


def scope_command(spec, bootstrap_argv):
    """Construction fermée du mécanisme manager ; aucune option libre."""
    argv = ["/usr/bin/systemd-run", "--user", "--scope", "--slice=app.slice",
            "--collect", "--no-ask-password", "--expand-environment=no",
            "--unit=" + spec["unit"], "--description=" + spec["description"]]
    properties = ["Delegate=yes", "TasksMax=256", "RuntimeMaxSec=12s",
                  "TimeoutStopSec=2s", "KillMode=control-group"]
    return argv + ["--property=" + value for value in properties] + bootstrap_argv


def bootstrap_command(lab, spec, identity, argv):
    return ["/usr/bin/python3", "-I", str(lab / "fixture/cgroup_gate.py"),
            "--bootstrap", str(lab / "gate.sock"), spec["nonce"],
            str(identity["pid"]), str(identity["startticks"]), *argv]


def sealed_scope_argv(lab, manifest):
    """Seuls PID/startticks seront remplis par le préflight de cette invocation."""
    identity = {"pid": "<SUPERVISOR_PID>", "startticks": "<SUPERVISOR_STARTTICKS>"}
    return scope_command(manifest["scope"], bootstrap_command(
        lab, manifest["scope"], identity, manifest["argv"]))


class ProcFS:
    """Observations procfs strictes, sans migration ni changement de rlimit."""

    def __init__(self, root=Path("/proc")):
        self.root = root

    def identity(self, pid):
        directory = self.root / str(pid)
        before = directory.stat()
        fields = (directory / "stat").read_text().rsplit(")", 1)[1].split()
        lines = (directory / "cgroup").read_text().splitlines()
        require(len(lines) == 1 and lines[0].startswith("0::/"), "cgroup v1/hybride")
        status = dict(line.split(":", 1) for line in
                      (directory / "status").read_text().splitlines() if ":" in line)
        require(set(map(int, status["Uid"].split())) == {before.st_uid},
                "UID process divergent")
        require(directory.stat().st_ino == before.st_ino, "proc identity drift")
        return {"pid": pid, "uid": before.st_uid, "startticks": int(fields[19]),
                "cgroup": lines[0][3:]}

    def uid_threads(self, uid):
        total = 0
        # Every disappearing/unreadable process refuses; a snapshot never reserves.
        for directory in self.root.iterdir():
            if not directory.name.isdecimal():
                continue
            status = dict(line.split(":", 1) for line in
                          (directory / "status").read_text().splitlines()
                          if ":" in line)
            observed_uid = int(status["Uid"].split()[0])
            if observed_uid == uid:
                before = self.identity(int(directory.name))
                require(before["uid"] == uid, "UID drift pendant diagnostic")
                threads = int(status["Threads"])
                tasks = list((directory / "task").iterdir())
                require(threads > 0 and threads == len(tasks),
                        "compte threads incohérent")
                after_status = dict(line.split(":", 1) for line in
                                    (directory / "status").read_text().splitlines()
                                    if ":" in line)
                require(status["Uid"] == after_status["Uid"]
                        and status["Threads"] == after_status["Threads"]
                        and self.identity(int(directory.name)) == before,
                        "UID/count/startticks drift pendant diagnostic")
                total += threads
        require(total > 0, "charge UID inconnue")
        return total

    def nproc(self):
        return resource.getrlimit(resource.RLIMIT_NPROC)

    def pidfd(self, pid):
        return os.pidfd_open(pid)


class CgroupFS:
    """Accès exclusivement en lecture au montage unifié et à ses compteurs."""

    def __init__(self, root=Path("/sys/fs/cgroup")):
        self.root = root

    def mount(self):
        matches = []
        for line in Path("/proc/self/mountinfo").read_text().splitlines():
            left, right = line.split(" - ", 1)
            fields = left.split()
            if fields[4] == str(self.root):
                require(right.split()[0] == "cgroup2" and fields[3] == "/",
                        "montage cgroup2 unifié racine requis")
                matches.append((int(fields[0]), fields[2]))
        require(len(matches) == 1, "identité montage ambiguë")
        return matches[0]

    def path(self, group):
        require(group.startswith("/") and ".." not in group.split("/"),
                "chemin cgroup invalide")
        path = self.root / group.lstrip("/")
        require(path.resolve(strict=True) == path, "symlink cgroup refusé")
        require(path.stat().st_dev == self.root.stat().st_dev,
                "montage cgroup divergent")
        return path

    def snapshot(self, group):
        path = self.path(group)
        for name in ("cgroup.type", "pids.max", "pids.current", "cgroup.procs"):
            require(not (path / name).is_symlink(), "symlink fichier cgroup refusé")
        require((path / "cgroup.type").read_text().strip() == "domain",
                "cgroup non domain/threaded")
        info = path.stat()
        return {"inode": info.st_ino, "device": info.st_dev, "uid": info.st_uid,
                "pids_max": (path / "pids.max").read_text().strip(),
                "pids_current": int((path / "pids.current").read_text()),
                "procs": [int(pid) for pid in
                          (path / "cgroup.procs").read_text().split()],
                "children": [entry.name for entry in path.iterdir() if entry.is_dir()]}

    def available(self, group):
        path = self.path(group)
        return ((path / "cgroup.controllers").read_text().split(),
                (path / "cgroup.subtree_control").read_text().split(),
                os.access(path / "cgroup.procs", os.W_OK, effective_ids=True))

    def exists(self, group):
        path = self.root / group.lstrip("/")
        return path.exists() or path.is_symlink()

    def empty(self, group):
        path = self.path(group)
        def fail_walk(error):
            raise error

        walk = os.walk(path, followlinks=False, onerror=fail_walk)
        for directory, names, files in walk:
            current = Path(directory)
            require(not any((current / name).is_symlink() for name in names + files),
                    "symlink dans sous-arbre")
            events = dict(line.split() for line in
                          (current / "cgroup.events").read_text().splitlines())
            if events.get("populated") != "0":
                return False
            if (current / "cgroup.procs").read_text().strip():
                return False
            if (current / "cgroup.threads").read_text().strip():
                return False
            if int((current / "pids.current").read_text()) != 0:
                return False
        return True


class DrainFailure(Refusal):
    """Une collecte échouée conserve les préfixes bruts déjà observés."""

    def __init__(self, message, channels):
        super().__init__(message)
        self.channels = [bytes(channel) for channel in channels]


def drain(process, deadline, limit=LIMIT):
    """Collecte bornée ; le propriétaire effectue le stop et le wait final."""
    channels = [bytearray(), bytearray()]
    try:
        with selectors.DefaultSelector() as selector:
            for index, stream in enumerate((process.stdout, process.stderr)):
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, selectors.EVENT_READ, index)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                require(remaining > 0, "drain timeout")
                for key, _ in selector.select(min(.05, remaining)):
                    chunk = os.read(key.fd, 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    target = channels[key.data]
                    room = limit - len(target)
                    target.extend(chunk[:room])
                    require(len(chunk) <= room, "stdout/stderr overflow")
        process.wait(timeout=max(.001, deadline - time.monotonic()))
        return channels
    except BaseException as error:
        raise DrainFailure(f"{type(error).__name__}: {error}", channels) from error


class SystemManager:
    """Les seules mutations sont la création scellée et le stop possédé."""

    def __init__(self, uid, popen=None):
        self.popen = popen or subprocess.Popen
        self.environment = {
            **CLEAN_ENV, "XDG_RUNTIME_DIR": f"/run/user/{uid}",
            "DBUS_SESSION_BUS_ADDRESS": f"unix:path=/run/user/{uid}/bus",
            "SYSTEMD_PAGER": "cat", "SYSTEMD_COLORS": "0",
        }

    def spawn(self, argv):
        return self.popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, close_fds=True,
                          env=self.environment, start_new_session=True)

    def call(self, argv, deadline):
        """Auxiliaire borné, récolté même si la lecture échoue."""
        require(deadline - time.monotonic() > .1, "budget manager épuisé")
        process = self.spawn(argv)
        try:
            channels = drain(process, deadline - .05, limit=65536)
            require(process.returncode == 0, "manager commande refusée")
            return bytes(channels[0]).decode("utf-8", errors="strict")
        finally:
            try:
                if process.poll() is None:
                    process.kill()  # Our unreaped Popen only; never a discovered PID.
                process.wait(timeout=max(.001, deadline - time.monotonic()))
            finally:
                process.stdout.close()
                process.stderr.close()

    def show(self, unit, deadline, system=False):
        argv = ["/usr/bin/systemctl"] + ([] if system else ["--user"])
        text = self.call(argv + ["show", unit, "--no-pager"], deadline)
        return dict(line.split("=", 1) for line in text.splitlines() if "=" in line)

    def stop(self, unit, deadline):
        argv = ["/usr/bin/systemctl", "--user", "--no-ask-password", "stop", unit]
        self.call(argv, deadline)

    def create(self, spec, bootstrap):
        return self.spawn(scope_command(spec, bootstrap))


def ancestors(group):
    current = Path(group)
    while str(current) != "/":
        yield str(current)
        current = current.parent


def capacity(cgroups, app):
    """Le headroom observé est un critère de refus, pas une réservation."""
    records = {}
    for group in ancestors(app):
        record = cgroups.snapshot(group)
        count = record["pids_current"]
        require(count >= 0, "pids.current négatif")
        maximum = record["pids_max"]
        if maximum != "max":
            require(maximum.isdecimal(), "pids.max ancêtre invalide")
            require(int(maximum) - count >= TASKS, "capacité ancêtre insuffisante")
        records[group] = record
    return records


def preflight(proc, cgroups, manager, uid, pid, deadline):
    """Toutes les observations précèdent ATTEMPT et la première mutation."""
    require(uid != 0 and uid == os.geteuid(), "UID réel/effectif invalide")
    mount = cgroups.mount()
    base = f"/user.slice/user-{uid}.slice/user@{uid}.service"
    app = base + "/app.slice"
    launcher = proc.identity(pid)
    require(launcher["uid"] == uid and launcher["cgroup"].startswith(app + "/"),
            "launcher hors app.slice ; session scope refusé")
    owner = manager.show(f"user@{uid}.service", deadline, system=True)
    require(owner.get("Id") == f"user@{uid}.service"
            and owner.get("Delegate") == "yes" and owner.get("ActiveState") == "active"
            and owner.get("ControlGroup") == base, "manager non délégué/invalide")
    require(re.fullmatch(r"[0-9a-f]{32}", owner.get("InvocationID", "")),
            "identité invocation manager absente")
    manager_process = proc.identity(int(owner["MainPID"]))
    require(manager_process["uid"] == uid
            and manager_process["cgroup"].startswith(base + "/"),
            "identité process manager divergente")
    application = manager.show("app.slice", deadline)
    require(application.get("Id") == "app.slice"
            and application.get("ActiveState") == "active"
            and application.get("ControlGroup") == app, "app.slice inactif/invalide")
    controllers, enabled, writable = cgroups.available(app)
    require("pids" in controllers and "pids" in enabled, "contrôleur pids absent")
    require(writable, "ancêtre commun non writable")
    limits = proc.nproc()
    load = proc.uid_threads(uid)
    require(all(value == resource.RLIM_INFINITY or value >= load for value in limits),
            f"inherited RLIMIT_NPROC insuffisant : {limits}, charge UID={load}")
    return {"launcher": launcher, "manager": owner, "manager_process": manager_process,
            "mount": mount, "app": app, "uid": uid, "nproc": limits,
            "uid_threads_diagnostic": load, "ancestors": capacity(cgroups, app)}


def same_lifetime(first, second):
    return all(first[key] == second[key] for key in ("pid", "uid", "startticks"))


def scope_identity(spec, observed, group):
    """Nonce Description + invocation + chemin ; aucun stop sur nom seul."""
    for key, expected in (("Id", spec["unit"]), ("Description", spec["description"]),
                          ("ControlGroup", group)):
        require(observed.get(key) == expected, "scope identité divergente : " + key)
    require(re.fullmatch(r"[0-9a-f]{32}", observed.get("InvocationID", "")),
            "scope InvocationID absent")


class Barrier:
    """Socket privé, authentifié et à libération unique, sans FD relayé."""

    def __init__(self, path, nonce, uid, pid, deadline):
        self.path = path
        self.nonce = nonce
        self.uid = uid
        self.pid = pid
        self.deadline = deadline
        self.connection = None
        self.released = False
        require(len(os.fsencode(path)) < 104, "nom socket trop long")
        self.listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        try:
            self.listener.bind(str(path))
            os.chmod(path, 0o600)
            self.listener.listen(1)
        except BaseException:
            self.listener.close()
            raise

    def accept(self):
        require(self.connection is None and not self.released,
                "bootstrap replay refusé")
        self.listener.settimeout(max(.001, self.deadline - time.monotonic()))
        self.connection, _ = self.listener.accept()
        self.connection.settimeout(max(.001, self.deadline - time.monotonic()))
        pid, uid, _ = struct.unpack("3i", self.connection.getsockopt(
            socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))
        require(uid == self.uid, "bootstrap UID divergent")
        message = json.loads(self.connection.recv(4096))
        require(message == {"nonce": self.nonce, "pid": pid},
                "bootstrap nonce/PID invalide")
        return pid

    def release(self):
        require(not self.released, "seconde release refusée")
        require(time.monotonic() < self.deadline, "release timeout")
        self.released = True
        self.connection.sendall(("RELEASE " + self.nonce).encode())
        message = self.connection.recv(4096)
        require(message == ("EXEC_REQUESTED " + self.nonce).encode(),
                "bootstrap EOF/exec intent absent")

    def close(self):
        if self.connection is not None:
            self.connection.close()
        self.listener.close()
        self.path.unlink(missing_ok=True)


def bootstrap(path, nonce, supervisor_pid, startticks, argv, proc=None,
              execute=os.execve):
    """Attendre avant prlimit/bwrap ; EOF, parent mort et nonce faux refusent."""
    proc = proc or ProcFS()
    identity = proc.identity(supervisor_pid)
    require(identity["uid"] == os.getuid() and identity["startticks"] == startticks,
            "superviseur identité divergente")
    descriptor = proc.pidfd(supervisor_pid)
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as channel:
            channel.settimeout(4)
            channel.connect(str(path))
            peer_pid, peer_uid, _ = struct.unpack("3i", channel.getsockopt(
                socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))
            require(peer_pid == supervisor_pid and peer_uid == os.getuid(),
                    "serveur étranger")
            require(same_lifetime(identity, proc.identity(supervisor_pid)),
                    "PID superviseur recyclé")
            channel.sendall(json.dumps({"nonce": nonce, "pid": os.getpid()}).encode())
            ready, _, _ = select.select([descriptor, channel], [], [], 4)
            require(descriptor not in ready and channel in ready, "parent mort/timeout")
            require(channel.recv(4096) == ("RELEASE " + nonce).encode(),
                    "EOF/nonce release invalide")
            require(not select.select([descriptor], [], [], 0)[0],
                    "parent mort avant exec")
            channel.sendall(("EXEC_REQUESTED " + nonce).encode())
        os.close(descriptor)
        descriptor = None
        # Do not rely on systemd-run's internal bus descriptor inheritance.
        # close_fds at Popen protects the initial launch; close again at payload.
        ceiling = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        require(ceiling != resource.RLIM_INFINITY, "NOFILE hérité non fini")
        os.closerange(3, ceiling)
        os.chdir("/tmp")
        execute(argv[0], argv, CLEAN_ENV)
        raise Refusal("exec retourné sans remplacement")
    finally:
        if descriptor is not None:
            os.close(descriptor)


def admit(spec, evidence, pid, proc, cgroups, manager, deadline):
    """Figer l'identité complète avant RELEASE, puis revalider immédiatement."""
    group = evidence["app"] + "/" + spec["unit"]
    observed = manager.show(spec["unit"], deadline)
    scope_identity(spec, observed, group)
    require(all(observed.get(key) == value for key, value in POLICY.items()),
            "scope propriétés/budget divergents")
    identity = proc.identity(pid)
    require(identity["uid"] == evidence["uid"] and identity["cgroup"] == group,
            "bootstrap PID/UID/membership divergent")
    pidfd = proc.pidfd(pid)
    try:
        record = cgroups.snapshot(group)
        require(record["uid"] == evidence["uid"] and record["pids_max"] == "256",
                "pids.max non fini/incorrect ou propriétaire divergent")
        require(record["procs"] == [pid] and record["pids_current"] == 1
                and not record["children"],
                "scope occupé/pids.current incohérent")
        require(same_lifetime(identity, proc.identity(pid)), "PID/startticks divergent")
        require(proc.identity(evidence["launcher"]["pid"]) == evidence["launcher"],
                "superviseur déplacé/identité divergente")
        require(cgroups.mount() == evidence["mount"], "montage remplacé")
        capacity(cgroups, evidence["app"])
        require(not select.select([pidfd], [], [], 0)[0],
                "bootstrap mort avant admission")
        current_manager = manager.show(
            f"user@{evidence['uid']}.service", deadline, system=True)
        require(all(current_manager.get(key) == evidence["manager"].get(key)
                    for key in ("MainPID", "InvocationID", "ControlGroup", "Delegate")),
                "manager identité remplacée")
        observed_manager = proc.identity(evidence["manager_process"]["pid"])
        require(observed_manager == evidence["manager_process"],
                "manager PID/startticks divergent")
        load = proc.uid_threads(evidence["uid"])
        require(proc.nproc() == evidence["nproc"] and all(
            value == resource.RLIM_INFINITY or value >= load for value in proc.nproc()),
            "NPROC/charge UID divergent avant release")
        return {"properties": observed, "process": identity, "cgroup": group,
                "kernel": record, "pidfd": pidfd}
    except BaseException:
        os.close(pidfd)
        raise


def validate_owned(spec, receipt, cgroups, manager, deadline):
    """Même invocation et inode ; un PID mort n'autorise jamais un nouveau PID."""
    observed = manager.show(spec["unit"], deadline)
    scope_identity(spec, observed, receipt["cgroup"])
    require(observed["InvocationID"] == receipt["properties"]["InvocationID"],
            "scope invocation remplacée")
    kernel = cgroups.snapshot(receipt["cgroup"])
    require(all(kernel[key] == receipt["kernel"][key]
                for key in ("inode", "device", "uid")),
            "scope inode/propriétaire remplacé")


class EmptyWitness:
    """Observer avant release et pendant stop, sans autorité de mutation.

    Un ENOENT/ENODEV n'est jamais converti en populated=0. Les lectures du
    même inode doivent réellement constater events=0 et l'absence de tâches.
    """

    def __init__(self, cgroups, receipt):
        self.cgroups = cgroups
        self.receipt = receipt
        self.empty_seen = False
        self.errors = []
        self.finished = threading.Event()
        self.thread = threading.Thread(target=self._observe, daemon=True)
        self.thread.start()

    def sample(self):
        try:
            record = self.cgroups.snapshot(self.receipt["cgroup"])
            require(all(record[key] == self.receipt["kernel"][key]
                        for key in ("inode", "device", "uid")),
                    "witness inode divergent")
            if self.cgroups.empty(self.receipt["cgroup"]):
                # Recheck inode after recursive observation, before accepting proof.
                after = self.cgroups.snapshot(self.receipt["cgroup"])
                require(all(after[key] == record[key]
                            for key in ("inode", "device", "uid")),
                        "witness inode remplacé pendant lecture")
                self.empty_seen = True
        except (FileNotFoundError, ProcessLookupError):
            # Disappearance alone never establishes emptiness.
            return
        except BaseException as error:
            self.errors.append(f"{type(error).__name__}: {error}"[:512])
            self.finished.set()

    def _observe(self):
        while not self.finished.is_set():
            self.sample()
            self.finished.wait(.002)

    def close(self):
        self.finished.set()
        self.thread.join(timeout=.1)
        require(not self.thread.is_alive(), "witness arrêt non prouvé")


def cleanup(spec, receipt, process, proc, cgroups, manager, deadline, witness=None):
    """Ne jamais laisser une exception de cleanup masquer son verdict fermé."""
    errors = []
    empty_seen = False
    try:
        if receipt is not None:
            if witness is not None:
                witness.sample()
                empty_seen = witness.empty_seen
                require(not witness.errors, "witness observation échouée")
            observed = manager.show(spec["unit"], deadline)
            exists = cgroups.exists(receipt["cgroup"])
            if observed.get("LoadState") == "not-found" and not exists:
                require(empty_seen, "vide récursif non observé avant disparition")
            else:
                validate_owned(spec, receipt, cgroups, manager, deadline)
                try:
                    current = proc.identity(receipt["process"]["pid"])
                except FileNotFoundError:
                    current = None
                require(current is None or current == receipt["process"],
                        "PID/membership divergent avant stop")
                empty_seen = empty_seen or cgroups.empty(receipt["cgroup"])
                manager.stop(spec["unit"], deadline)
                while time.monotonic() < deadline:
                    if witness is not None:
                        witness.sample()
                        require(not witness.errors, "witness observation échouée")
                        empty_seen = empty_seen or witness.empty_seen
                    observed = manager.show(spec["unit"], deadline)
                    exists = cgroups.exists(receipt["cgroup"])
                    if exists:
                        validate_owned(spec, receipt, cgroups, manager, deadline)
                        empty_seen = empty_seen or cgroups.empty(receipt["cgroup"])
                    if observed.get("LoadState") == "not-found" and not exists:
                        require(empty_seen,
                                "vide récursif non observé avant disparition")
                        break
                    time.sleep(.02)
                else:
                    raise Refusal("unit/cgroup disparition non prouvée")
        else:
            require(not cgroups.exists(evidence_group(spec)),
                    "scope créé sans ownership établi")
    except BaseException as error:
        errors.append(f"{type(error).__name__}: {error}"[:512])
    if witness is not None:
        try:
            witness.close()
        except BaseException as error:
            errors.append("witness close: " + str(error)[:128])
    if process is not None:
        try:
            if process.poll() is None:
                process.kill()  # Exact unreaped launcher child only.
            process.wait(timeout=max(.001, deadline - time.monotonic()))
        except BaseException as error:
            errors.append(f"collection: {type(error).__name__}: {error}"[:512])
        for stream in (process.stdout, process.stderr):
            try:
                stream.close()
            except BaseException as error:
                errors.append("pipe close: " + str(error)[:128])
    if receipt is not None:
        try:
            os.close(receipt["pidfd"])
        except OSError as error:
            errors.append("pidfd close: " + str(error))
    return {"proved": not errors, "empty_observed": empty_seen, "errors": errors}


def evidence_group(spec):
    uid = os.getuid()
    return f"/user.slice/user-{uid}.slice/user@{uid}.service/app.slice/" + spec["unit"]


def run_scope(lab, manifest, reserve, journal, proc=None, cgroups=None,
              manager=None, barrier_factory=Barrier, collector=drain):
    """Orchestration injectée : préflight, réserve, admission, release et récolte."""
    proc = proc or ProcFS()
    cgroups = cgroups or CgroupFS()
    manager = manager or SystemManager(os.getuid())
    spec = manifest["scope"]
    started = time.monotonic()
    process = barrier = receipt = witness = None
    channels = [b"", b""]
    result = {"cause": "failure", "phases": [], "runtime": "NOT_RUN",
              "returncode": None, "collected": False}

    def phase(name, **detail):
        result["phases"].append({"phase": name, **detail})
        journal(result)

    try:
        evidence = preflight(proc, cgroups, manager, os.getuid(), os.getpid(),
                             started + 3)
        group = evidence["app"] + "/" + spec["unit"]
        require(manager.show(spec["unit"], started + 3).get("LoadState") == "not-found"
                and not cgroups.exists(group), "scope déjà occupé ; aucun spawn")
        # PRECHECK is not journaled until ATTEMPT: failed preflight stays read-only.
        reserve(evidence)
        phase("PRECHECK", nproc=evidence["nproc"],
              uid_threads=evidence["uid_threads_diagnostic"])
        barrier = barrier_factory(lab / "gate.sock", spec["nonce"], os.getuid(),
                                  os.getpid(), started + 5)
        identity = evidence["launcher"]
        bootstrap_argv = bootstrap_command(lab, spec, identity, manifest["argv"])
        process = manager.create(spec, bootstrap_argv)
        phase("SCOPE_CREATED", status="creation_requested")
        pid = barrier.accept()
        receipt = admit(spec, evidence, pid, proc, cgroups, manager, started + 5)
        public_receipt = {key: value for key, value in receipt.items()
                          if key != "pidfd"}
        phase("ADMITTED", ownership=public_receipt)
        witness = EmptyWitness(cgroups, receipt)
        validate_owned(spec, receipt, cgroups, manager, started + 5)
        require(proc.identity(pid) == receipt["process"], "PID drift avant release")
        require(not select.select([receipt["pidfd"]], [], [], 0)[0],
                "bootstrap mort avant release")
        barrier.release()
        phase("RELEASED", exec_intent=True)
        if manifest.get("qualification_mode") == "parent-death":
            # Only a separately sealed, separately approved benign LAB can reach this.
            require(manifest["kind"] == "benign", "parent-death réservé au bénin")
            phase("PARENT_DEATH_TEST", external_cleanup_required=True)
            os._exit(71)
        channels = collector(process, started + 8)
        result["returncode"] = process.returncode
        result["collected"] = process.returncode is not None
        phase("COLLECTED", returncode=process.returncode)
        if manifest["kind"] == "benign":
            require(b"BENIGN_PAYLOAD_STARTED\n" in channels[0],
                    "marqueur payload bénin absent")
            phase("PAYLOAD_STARTED", proof="benign stdout marker")
        result["runtime"] = ("BENIGN" if manifest["kind"] == "benign"
                             else "EGL_RESULT_UNINTERPRETED")
        result["cause"] = "exit" if process.returncode == 0 else "payload_failure"
    except BaseException as error:
        if isinstance(error, DrainFailure):
            channels = error.channels
        result["cause"] = ("interrupted" if isinstance(error, KeyboardInterrupt)
                           else "failure")
        result["error"] = f"{type(error).__name__}: {error}"[:512]
    finally:
        if barrier is not None:
            try:
                barrier.close()
            except BaseException as error:
                result["barrier_cleanup_error"] = str(error)[:512]
        if process is not None:
            cleaned = cleanup(spec, receipt, process, proc, cgroups, manager,
                              started + 10, witness=witness)
            result["cleanup"] = cleaned
            if not cleaned["proved"] or "barrier_cleanup_error" in result:
                result["cause"] = "CLEANUP_UNPROVEN"
            try:
                phase("CLEANED", proved=cleaned["proved"])
            except BaseException as error:
                result["cause"] = "journal_failure"
                result["error"] = str(error)[:512]
    result["elapsed"] = time.monotonic() - started
    return result, channels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap", nargs=argparse.REMAINDER, required=True)
    args = parser.parse_args().bootstrap
    require(len(args) >= 5, "bootstrap argv absent")
    bootstrap(Path(args[0]), args[1], int(args[2]), int(args[3]), args[4:])


if __name__ == "__main__":
    try:
        main()
    except (Refusal, OSError, ValueError) as error:
        print("Bootstrap refusé: " + str(error), file=sys.stderr)
        sys.exit(70)
