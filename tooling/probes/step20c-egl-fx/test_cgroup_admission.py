"""Tests des fonctions de production ; aucune création native n'est permise."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import resource
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import run

INERT_POPEN = subprocess.Popen
gate = run.gate
UID = os.getuid()
PID = os.getpid()
BASE = f"/user.slice/user-{UID}.slice/user@{UID}.service"
APP = BASE + "/app.slice"
SPEC = gate.policy("a" * 32)
gate = run.gate.module  # Patch the production module globals, not the lazy proxy.
GROUP = APP + "/" + SPEC["unit"]


def native_spawn_forbidden(*args, **kwargs):
    raise AssertionError("native_spawn_forbidden")


_native_sentinel = None


def setUpModule():
    global _native_sentinel
    _native_sentinel = patch.object(
        subprocess, "Popen", side_effect=native_spawn_forbidden)
    _native_sentinel.start()


def tearDownModule():
    _native_sentinel.stop()


class FakeProc:
    def __init__(self):
        self.identities = {
            PID: {"pid": PID, "uid": UID, "startticks": 111,
                  "cgroup": APP + "/launcher.scope"},
            42: {"pid": 42, "uid": UID, "startticks": 222,
                 "cgroup": BASE + "/init.scope"},
            43: {"pid": 43, "uid": UID, "startticks": 333, "cgroup": GROUP},
        }
        self.limits = (4096, 4096)
        self.load = 1126
        self.writers = []

    def identity(self, pid):
        return dict(self.identities[pid])

    def uid_threads(self, uid):
        return self.load

    def nproc(self):
        return self.limits

    def pidfd(self, pid):
        reader, writer = os.pipe()
        self.writers.append(writer)
        return reader

    def close(self):
        for writer in self.writers:
            os.close(writer)


class FakeCgroups:
    def __init__(self):
        self.mount_id = (1, "0:30")
        self.controllers = (["pids"], ["pids"], True)
        self.present = False
        self.is_empty = True
        self.record = {"inode": 5, "device": 30, "uid": UID,
                       "pids_max": "256", "pids_current": 1, "procs": [43],
                       "children": []}
        self.ancestor = {**self.record, "pids_max": "4096", "pids_current": 3}

    def mount(self):
        return self.mount_id

    def snapshot(self, group):
        return dict(self.record if group == GROUP else self.ancestor)

    def available(self, group):
        return self.controllers

    def exists(self, group):
        return self.present

    def empty(self, group):
        return self.is_empty


class FakeProcess:
    def __init__(self):
        self.returncode = None
        self.stdout = io.BytesIO()
        self.stderr = io.BytesIO()
        self.killed = False
        self.wait_error = None

    def poll(self):
        return self.returncode

    def kill(self):
        self.killed = True
        self.returncode = -9

    def wait(self, timeout):
        if self.wait_error:
            raise self.wait_error
        self.returncode = 0 if self.returncode is None else self.returncode
        return self.returncode


class FakeManager:
    def __init__(self, cgroups):
        self.cgroups = cgroups
        self.created = 0
        self.stopped = []
        self.owner = {"Id": f"user@{UID}.service", "Delegate": "yes",
                      "ActiveState": "active",
                      "ControlGroup": BASE, "InvocationID": "b" * 32, "MainPID": "42"}
        self.app = {"Id": "app.slice", "ActiveState": "active", "ControlGroup": APP}
        self.scope = {"Id": SPEC["unit"], "Description": SPEC["description"],
                      "InvocationID": "c" * 32, "ControlGroup": GROUP, **gate.POLICY}
        self.process = FakeProcess()
        self.create_error = None
        self.stop_error = None

    def show(self, unit, deadline, system=False):
        if unit == f"user@{UID}.service":
            return dict(self.owner)
        if unit == "app.slice":
            return dict(self.app)
        return dict(self.scope) if self.cgroups.present else {"LoadState": "not-found"}

    def create(self, spec, argv):
        self.created += 1
        if self.create_error:
            raise self.create_error
        self.cgroups.present = True
        return self.process

    def stop(self, unit, deadline):
        if self.stop_error:
            raise self.stop_error
        self.stopped.append(unit)
        self.cgroups.present = False


class FakeBarrier:
    def __init__(self, *args):
        self.released = 0
        self.closed = False
        self.error = None

    def accept(self):
        if self.error:
            raise self.error
        return 43

    def release(self):
        self.released += 1

    def close(self):
        self.closed = True


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.sentinel = patch.object(
            subprocess, "Popen", side_effect=native_spawn_forbidden)
        self.sentinel.start()
        self.addCleanup(self.sentinel.stop)
        self.proc = FakeProc()
        self.addCleanup(self.proc.close)
        self.cgroups = FakeCgroups()
        self.manager = FakeManager(self.cgroups)
        self.barrier = FakeBarrier()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.lab = Path(self.temporary.name)
        self.manifest = {"scope": SPEC, "kind": "benign",
                         "qualification_mode": "nominal",
                         "argv": run.benign_command("nominal")}
        self.reservations = []
        self.journal = []

    def preflight(self):
        return gate.preflight(self.proc, self.cgroups, self.manager,
                              UID, PID, time.monotonic() + 1)

    def admitted(self):
        evidence = self.preflight()
        self.cgroups.present = True
        return gate.admit(SPEC, evidence, 43, self.proc, self.cgroups, self.manager,
                          time.monotonic() + 1)

    def execute(self, collector=None, reserve=None, journal=None):
        def collect(process, deadline):
            process.returncode = 0
            return [b"BENIGN_PAYLOAD_STARTED\n", b""]
        return gate.run_scope(
            self.lab, self.manifest, reserve or self.reservations.append,
            journal or (lambda result: self.journal.append(copy.deepcopy(result))),
            self.proc, self.cgroups, self.manager,
            barrier_factory=lambda *args: self.barrier, collector=collector or collect)

    def test_success_uses_production_orchestrator_and_single_release(self):
        result, output = self.execute()
        self.assertEqual(result["cause"], "exit")
        self.assertEqual(self.barrier.released, 1)
        self.assertEqual(len(self.reservations), 1)
        self.assertTrue(self.barrier.closed)
        self.assertEqual(self.manager.stopped, [SPEC["unit"]])
        self.assertEqual([event["phase"] for event in result["phases"]],
                         ["PRECHECK", "SCOPE_CREATED", "ADMITTED", "RELEASED",
                          "COLLECTED",
                          "PAYLOAD_STARTED", "CLEANED"])
        self.assertEqual(self.proc.limits, (4096, 4096))

    def test_session_scope_refused_before_reservation(self):
        self.proc.identities[PID]["cgroup"] = (
            f"/user.slice/user-{UID}.slice/session-6.scope")
        result, _ = self.execute()
        self.assertIn("session scope", result["error"])
        self.assertEqual(self.reservations, [])
        self.assertEqual(self.manager.created, 0)

    def test_nproc_256_under_uid1126_refused_and_never_raised(self):
        self.proc.limits = (256, 256)
        result, _ = self.execute()
        self.assertIn("RLIMIT_NPROC", result["error"])
        self.assertEqual(self.proc.limits, (256, 256))
        self.assertEqual(self.manager.created, 0)

    def test_infinite_inherited_nproc_is_preserved(self):
        self.proc.limits = (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
        self.assertEqual(self.preflight()["nproc"], self.proc.limits)
        self.assertFalse(any(arg.startswith("--nproc")
                             for arg in run.command(self.lab)))

    def test_manager_delegation_identity_and_app_refusals(self):
        cases = (("owner", "Delegate", "no"), ("owner", "Id", "foreign"),
                 ("owner", "InvocationID", ""), ("owner", "ControlGroup", "/"),
                 ("app", "ActiveState", "inactive"), ("app", "ControlGroup", "/"))
        for target, key, bad in cases:
            with self.subTest(key=key, bad=bad):
                original = getattr(self.manager, target)[key]
                getattr(self.manager, target)[key] = bad
                with self.assertRaises(gate.Refusal):
                    self.preflight()
                getattr(self.manager, target)[key] = original

    def test_controllers_and_writable_ancestor(self):
        for controllers in (([], ["pids"], True), (["pids"], [], True),
                            (["pids"], ["pids"], False)):
            self.cgroups.controllers = controllers
            with self.assertRaises(gate.Refusal):
                self.preflight()

    def test_ancestor_headroom_and_inconsistent_current(self):
        for maximum, current in (("1200", 1126), ("4096", -1), ("broken", 0)):
            self.cgroups.ancestor.update(pids_max=maximum, pids_current=current)
            with self.assertRaises(gate.Refusal):
                self.preflight()

    def test_scope_collision_no_spawn(self):
        self.cgroups.present = True
        result, _ = self.execute()
        self.assertIn("occupé", result["error"])
        self.assertEqual(self.manager.created, 0)
        self.assertEqual(self.reservations, [])

    def test_uid_divergence_before_release(self):
        self.proc.identities[43]["uid"] = UID + 1
        result, _ = self.execute()
        self.assertEqual(self.barrier.released, 0)
        self.assertEqual(result["cause"], "CLEANUP_UNPROVEN")
        self.assertEqual(self.manager.stopped, [])

    def test_kernel_budget_membership_and_shape_refusals(self):
        for key, bad in (("pids_max", "max"), ("pids_max", "257"), ("pids_current", 0),
                         ("pids_current", 2), ("procs", [43, 44]),
                         ("children", ["foreign"]),
                         ("uid", UID + 1)):
            with self.subTest(key=key, bad=bad):
                original = self.cgroups.record[key]
                self.cgroups.record[key] = bad
                with self.assertRaises(gate.Refusal):
                    self.admitted()
                self.cgroups.record[key] = original

    def test_scope_manager_properties_are_exact(self):
        for key, bad in (("Id", "foreign.scope"), ("Description", "other"),
                         ("InvocationID", ""), ("ControlGroup", "/wrong"),
                         ("TasksMax", "infinity"), ("Delegate", "no"),
                         ("RuntimeMaxUSec", "infinity"), ("KillMode", "process")):
            with self.subTest(key=key):
                original = self.manager.scope[key]
                self.manager.scope[key] = bad
                with self.assertRaises(gate.Refusal):
                    self.admitted()
                self.manager.scope[key] = original

    def test_startticks_change_during_admission(self):
        original = self.proc.identity
        calls = 0
        def changing(pid):
            nonlocal calls
            value = original(pid)
            if pid == 43:
                calls += 1
                if calls > 1:
                    value["startticks"] += 1
            return value
        self.proc.identity = changing
        with self.assertRaisesRegex(gate.Refusal, "startticks"):
            self.admitted()

    def test_dead_pidfd_refused(self):
        def dead(pid):
            reader, writer = os.pipe()
            os.close(writer)
            return reader
        self.proc.pidfd = dead
        with self.assertRaisesRegex(gate.Refusal, "mort"):
            self.admitted()

    def test_identity_drift_never_stops_foreign_scope(self):
        for key, bad in (("Id", "foreign.scope"), ("Description", "other"),
                         ("InvocationID", "d" * 32), ("ControlGroup", "/foreign")):
            with self.subTest(key=key):
                self.manager.scope = {"Id": SPEC["unit"],
                                      "Description": SPEC["description"],
                                      "InvocationID": "c" * 32, "ControlGroup": GROUP,
                                      **gate.POLICY}
                receipt = self.admitted()
                self.manager.scope[key] = bad
                cleaned = gate.cleanup(SPEC, receipt, None, self.proc, self.cgroups,
                                       self.manager, time.monotonic() + .2)
                self.assertFalse(cleaned["proved"])
                self.assertEqual(self.manager.stopped, [])

    def test_inode_drift_and_recycled_pid_never_stop(self):
        receipt = self.admitted()
        self.cgroups.record["inode"] += 1
        self.assertFalse(gate.cleanup(SPEC, receipt, None, self.proc, self.cgroups,
                                     self.manager, time.monotonic() + .2)["proved"])
        self.assertEqual(self.manager.stopped, [])
        self.cgroups.record["inode"] -= 1
        receipt = self.admitted()
        self.proc.identities[43]["startticks"] += 1
        self.assertFalse(gate.cleanup(SPEC, receipt, None, self.proc, self.cgroups,
                                     self.manager, time.monotonic() + .2)["proved"])
        self.assertEqual(self.manager.stopped, [])

    def test_eof_and_timeout_before_release_never_exec(self):
        for error in (EOFError("child EOF"), TimeoutError("barrier timeout")):
            self.barrier.error = error
            result, _ = self.execute()
            self.assertNotEqual(result["cause"], "exit")
            self.assertEqual(self.barrier.released, 0)

    def test_failures_in_preflight_reservation_admission_and_drain(self):
        for error in (OSError("read failure"), KeyboardInterrupt()):
            with patch.object(self.proc, "uid_threads", side_effect=error):
                result, _ = self.execute()
            self.assertNotEqual(result["cause"], "exit")
            self.assertEqual(self.manager.created, 0)
        def fail(*args):
            raise OSError("mock failure")
        result, _ = self.execute(reserve=fail)
        self.assertEqual(self.manager.created, 0)
        self.assertNotEqual(result["cause"], "exit")
        result, _ = self.execute(collector=fail)
        self.assertNotEqual(result["cause"], "exit")
        self.assertTrue(self.manager.process.stdout.closed)
        self.assertTrue(self.manager.process.stderr.closed)

    def test_spawn_failure_consumes_once_no_cleanup_exception(self):
        self.manager.create_error = OSError("Popen failure")
        result, _ = self.execute()
        self.assertEqual(len(self.reservations), 1)
        self.assertIn("Popen failure", result["error"])
        self.assertEqual(self.manager.stopped, [])

    def test_cleanup_stop_collection_and_events_failures_never_pass(self):
        for mode in ("stop", "collection", "populated"):
            with self.subTest(mode=mode):
                self.manager = FakeManager(self.cgroups)
                self.cgroups.present = False
                self.cgroups.is_empty = mode != "populated"
                if mode == "stop":
                    self.manager.stop_error = OSError("stop failed")
                if mode == "collection":
                    self.manager.process.wait_error = subprocess.TimeoutExpired(
                        "mock", .1)
                result, _ = self.execute()
                self.assertEqual(result["cause"], "CLEANUP_UNPROVEN")

    def test_journal_failure_does_not_abandon_child(self):
        calls = 0
        def journal(result):
            nonlocal calls
            calls += 1
            if calls >= 4:
                raise OSError("journal full")
        result, _ = self.execute(journal=journal)
        self.assertNotEqual(result["cause"], "exit")
        self.assertTrue(self.manager.process.stdout.closed)
        self.assertTrue(self.barrier.closed)

    def test_no_egl_measurement_when_only_exec_requested(self):
        self.manifest["kind"] = "egl"
        result, _ = self.execute()
        self.assertEqual(result["runtime"], "EGL_RESULT_UNINTERPRETED")
        self.assertNotIn("PAYLOAD_STARTED",
                         [event["phase"] for event in result["phases"]])

    def test_parent_death_is_separate_sealed_case(self):
        self.manifest["qualification_mode"] = "parent-death"
        with patch.object(gate.os, "_exit", side_effect=SystemExit(71)) as exit_process:
            result, _ = self.execute()
        exit_process.assert_called_once_with(71)
        self.assertNotEqual(result["cause"], "exit")
        self.assertIn("PARENT_DEATH_TEST",
                      [event["phase"] for event in result["phases"]])

    def test_empty_observed_before_unit_disappears_allows_collection(self):
        def collect(process, deadline):
            self.cgroups.is_empty = True
            self.cgroups.record.update(pids_current=0, procs=[])
            time.sleep(.01)  # Give the production watcher a real observation.
            self.cgroups.present = False
            process.returncode = 0
            return [b"BENIGN_PAYLOAD_STARTED\n", b""]
        self.cgroups.is_empty = False
        result, _ = self.execute(collector=collect)
        self.assertEqual(result["cause"], "exit")
        self.assertTrue(result["cleanup"]["empty_observed"])
        self.assertEqual(self.manager.stopped, [])

    def test_disappeared_without_empty_proof_never_passes(self):
        def collect(process, deadline):
            self.cgroups.present = False
            process.returncode = 0
            return [b"BENIGN_PAYLOAD_STARTED\n", b""]
        self.cgroups.is_empty = False
        result, _ = self.execute(collector=collect)
        self.assertEqual(result["cause"], "CLEANUP_UNPROVEN")
        self.assertEqual(self.manager.stopped, [])

    def test_drain_failure_keeps_captured_prefix_in_orchestrator(self):
        def collect(process, deadline):
            raise gate.DrainFailure("overflow", [b"prefix", b"diagnostic"])
        result, channels = self.execute(collector=collect)
        self.assertNotEqual(result["cause"], "exit")
        self.assertEqual(channels, [b"prefix", b"diagnostic"])


    def test_approved_main_uses_production_gate_and_durable_single_budget(self):
        def execute(lab, manifest, reserve, journal):
            def collect(process, deadline):
                process.returncode = 0
                return [b"BENIGN_PAYLOAD_STARTED\n", b""]
            return gate.run_scope(
                lab, manifest, reserve, journal, self.proc, self.cgroups, self.manager,
                barrier_factory=lambda *args: self.barrier, collector=collect)

        argv = ["run.py", "--lab", str(self.lab), "--manifest-sha256", "reviewed",
                "--approve-benign-gate"]
        with (
            patch.object(sys, "argv", argv),
            patch.object(run, "verify", return_value=self.manifest),
            patch.object(run.gate, "run_scope", side_effect=execute),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(run.main(), 0)
            self.assertEqual(run.main(), 20)
        self.assertEqual(self.manager.created, 1)
        receipt = json.loads((self.lab / "result.json").read_text())
        self.assertEqual(receipt["returncode"], 0)
        self.assertTrue(receipt["cleanup"]["proved"])
        self.assertTrue((self.lab / "ATTEMPT").exists())

    def test_missing_benign_payload_marker_cannot_pass(self):
        def collect(process, deadline):
            process.returncode = 0
            return [b"", b""]
        result, _ = self.execute(collector=collect)
        self.assertNotEqual(result["cause"], "exit")
        self.assertIn("marqueur", result["error"])



class FilesystemTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fs = gate.CgroupFS(self.root)
        self.group = self.root / "scope"
        self.group.mkdir()
        contents = {"cgroup.type": "domain", "pids.max": "256", "pids.current": "1",
                    "cgroup.procs": "43", "cgroup.events": "populated 0\n",
                    "cgroup.threads": ""}
        for name, value in contents.items():
            (self.group / name).write_text(value)

    def test_threaded_and_symlink_rejected_by_production_fs(self):
        (self.group / "cgroup.type").write_text("threaded")
        with self.assertRaisesRegex(gate.Refusal, "domain"):
            self.fs.snapshot("/scope")


        (self.root / "link").symlink_to(self.group)
        with self.assertRaisesRegex(gate.Refusal, "symlink"):
            self.fs.snapshot("/link")

    def test_cgroup_v1_mount_and_nonroot_mount_rejected(self):
        for text in (f"1 0 0:30 / {self.root} rw - cgroup cgroup rw\n",
                     f"1 0 0:30 /subtree {self.root} rw - cgroup2 cgroup rw\n"):
            with patch.object(Path, "read_text", return_value=text):
                with self.assertRaises(gate.Refusal):
                    self.fs.mount()

    def test_recursive_populated_threads_and_symlink(self):
        (self.group / "cgroup.procs").write_text("")
        (self.group / "pids.current").write_text("0")
        self.assertTrue(self.fs.empty("/scope"))
        (self.group / "cgroup.threads").write_text("44")
        self.assertFalse(self.fs.empty("/scope"))
        (self.group / "cgroup.threads").write_text("")
        (self.group / "foreign").symlink_to(self.root)
        with self.assertRaises(gate.Refusal):
            self.fs.empty("/scope")

    def test_proc_v1_and_uid_drift_refused(self):
        directory = self.root / "43"
        directory.mkdir()
        (directory / "stat").write_text("43 (name) " + " ".join(["1"] * 20))
        (directory / "status").write_text(
            f"Uid:\t{UID} {UID} {UID} {UID}\nThreads:\t1\n")
        (directory / "cgroup").write_text("1:name:/legacy\n")
        proc = gate.ProcFS(self.root)
        with self.assertRaisesRegex(gate.Refusal, "v1"):
            proc.identity(43)
        (directory / "cgroup").write_text("0::/scope\n")
        (directory / "status").write_text(
            f"Uid:\t{UID} {UID + 1} {UID} {UID}\nThreads:\t1\n")
        with self.assertRaisesRegex(gate.Refusal, "UID"):
            proc.identity(43)

    def test_proc_uid_thread_diagnostic_rejects_drift_and_disappearance(self):
        directory = self.root / "43"
        directory.mkdir()
        (directory / "stat").write_text("43 (name) " + " ".join(["1"] * 20))
        status = f"Uid:\t{UID} {UID} {UID} {UID}\nThreads:\t1\n"
        (directory / "status").write_text(status)
        (directory / "cgroup").write_text("0::/scope\n")
        (directory / "task/43").mkdir(parents=True)
        proc = gate.ProcFS(self.root)
        self.assertEqual(proc.uid_threads(UID), 1)
        (directory / "task/44").mkdir()
        with self.assertRaisesRegex(gate.Refusal, "threads incohérent"):
            proc.uid_threads(UID)
        (directory / "task/44").rmdir()
        original = Path.read_text
        reads = 0

        def changed(path, *args, **kwargs):
            nonlocal reads
            if path == directory / "status":
                reads += 1
                if reads > 2:
                    return status.replace("Threads:\t1", "Threads:\t2")
            return original(path, *args, **kwargs)

        with patch.object(Path, "read_text", changed):
            with self.assertRaisesRegex(gate.Refusal, "drift"):
                proc.uid_threads(UID)
        (directory / "status").unlink()
        with self.assertRaises(FileNotFoundError):
            proc.uid_threads(UID)



class BenignCommandTests(unittest.TestCase):
    def test_parent_death_payload_sleeps_after_broken_pipe(self):
        sleeps = []

        def broken_write(_fd, _data):
            raise BrokenPipeError("supervisor closed stdout")

        fake_os = type("FakeOS", (), {"write": staticmethod(broken_write)})
        fake_time = type("FakeTime", (), {
            "sleep": staticmethod(sleeps.append),
        })
        script = run.benign_command("parent-death")[-1]

        with patch.dict(sys.modules, {"os": fake_os, "time": fake_time}):
            with self.assertRaises(BrokenPipeError):
                exec(compile(script, "<benign-parent-death>", "exec"), {})

        self.assertEqual(sleeps, [30])
        self.assertIn("time.sleep(0.2)", run.benign_command("nominal")[-1])


class BarrierTests(unittest.TestCase):
    """Sockets locaux et threads inertes ; aucun fork/exec/systemd."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "gate.sock"


    def peer(self, message, reply=None):
        errors = []
        def client():
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as channel:
                    channel.settimeout(1)
                    channel.connect(str(self.path))
                    channel.sendall(message)
                    if reply is not None:
                        received = channel.recv(4096)
                        if received != b"RELEASE " + SPEC["nonce"].encode():
                            errors.append("wrong release")
                        channel.sendall(reply)
            except BaseException as error:
                errors.append(error)
        thread = threading.Thread(target=client)
        thread.start()
        self.addCleanup(lambda: thread.join(timeout=2))
        return thread, errors

    def barrier(self, seconds=1):
        barrier = gate.Barrier(self.path, SPEC["nonce"], UID, PID,
                               time.monotonic() + seconds)
        self.addCleanup(barrier.close)
        return barrier

    def test_real_channel_peer_credentials_and_single_release(self):
        barrier = self.barrier()
        message = json.dumps({"nonce": SPEC["nonce"], "pid": PID}).encode()
        thread, errors = self.peer(message, b"EXEC_REQUESTED " + SPEC["nonce"].encode())
        self.assertEqual(barrier.accept(), PID)
        barrier.release()
        with self.assertRaisesRegex(gate.Refusal, "replay"):
            barrier.accept()
        with self.assertRaisesRegex(gate.Refusal, "seconde"):
            barrier.release()
        thread.join(timeout=2)
        self.assertEqual(errors, [])

    def test_wrong_nonce_and_pid_refuse(self):
        messages = ({"nonce": "bad", "pid": PID},
                    {"nonce": SPEC["nonce"], "pid": PID + 1})
        for data in messages:
            barrier = self.barrier()
            thread, _ = self.peer(json.dumps(data).encode())
            with self.assertRaisesRegex(gate.Refusal, "nonce/PID"):
                barrier.accept()
            thread.join(timeout=2)
            barrier.close()
            # Remove registered cleanup because close is intentionally idempotent.

    def test_eof_and_accept_timeout(self):
        barrier = self.barrier(.05)
        with self.assertRaises(TimeoutError):
            barrier.accept()
        barrier.close()
        barrier = self.barrier()
        thread, _ = self.peer(b"")
        with self.assertRaises((ValueError, gate.Refusal)):
            barrier.accept()
        thread.join(timeout=2)

    def test_bootstrap_no_exec_on_eof_wrong_nonce_parentdeath_timeout(self):
        for action in ("eof", "wrong", "death", "timeout"):
            with self.subTest(action=action):
                listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
                listener.bind(str(self.path))
                listener.listen(1)
                reader, writer = os.pipe()
                class Proc:
                    def identity(self, pid):
                        return {"pid": PID, "uid": UID, "startticks": 123}
                    def pidfd(self, pid):
                        return reader
                def server():
                    with listener.accept()[0] as channel:
                        channel.recv(4096)
                        if action == "wrong":
                            channel.sendall(b"RELEASE wrong")
                        elif action == "death":
                            os.close(writer)
                            # The pidfd EOF itself proves parent death to bootstrap.
                        elif action == "timeout":
                            time.sleep(.05)
                thread = threading.Thread(target=server)
                thread.start()
                with patch.object(gate, "select", wraps=gate.select) as select_module:
                    if action == "timeout":
                        select_module.select.return_value = ([], [], [])
                    with self.assertRaises((gate.Refusal, OSError)):
                        gate.bootstrap(self.path, SPEC["nonce"], PID, 123,
                                       ["forbidden"], Proc(),
                                       execute=native_spawn_forbidden)
                thread.join(timeout=2)
                listener.close()
                self.path.unlink()
                if action != "death":
                    os.close(writer)

    def test_bootstrap_exec_boundary_is_clean_and_closes_control_fds(self):
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.addCleanup(listener.close)
        listener.bind(str(self.path))
        listener.listen(1)
        reader, writer = os.pipe()
        self.addCleanup(lambda: os.close(writer))
        observations = []
        errors = []

        class Proc:
            def identity(self, pid):
                return {"pid": PID, "uid": UID, "startticks": 123}
            def pidfd(self, pid):
                return reader

        def server():
            try:
                with listener.accept()[0] as channel:
                    channel.recv(4096)
                    channel.sendall(b"RELEASE " + SPEC["nonce"].encode())
                    observations.append(channel.recv(4096))
            except BaseException as error:
                errors.append(error)

        thread = threading.Thread(target=server)
        thread.start()
        self.addCleanup(lambda: thread.join(timeout=2))
        executed = []
        with patch.object(gate.os, "closerange") as closed, \
                patch.object(gate.os, "chdir") as chdir:
            with self.assertRaisesRegex(gate.Refusal, "exec retourné"):
                gate.bootstrap(self.path, SPEC["nonce"], PID, 123, ["fixed", "payload"],
                               Proc(), execute=lambda *args: executed.append(args))
        thread.join(timeout=2)
        self.assertEqual(errors, [])
        self.assertEqual(executed, [("fixed", ["fixed", "payload"], gate.CLEAN_ENV)])
        self.assertEqual(observations, [b"EXEC_REQUESTED " + SPEC["nonce"].encode()])
        self.assertEqual(closed.call_args.args[0], 3)
        chdir.assert_called_once_with("/tmp")
        with self.assertRaises(OSError):
            os.fstat(reader)



class ManagerTests(unittest.TestCase):
    def test_actual_argv_and_environment_with_injected_popen(self):
        seen = []
        manager = gate.SystemManager(
            UID, popen=lambda argv, **kwargs: seen.append((argv, kwargs)))
        manager.create(SPEC, ["fixed-bootstrap"])
        argv, kwargs = seen[0]
        self.assertIn("--scope", argv)
        self.assertIn("--property=TasksMax=256", argv)
        self.assertIn("--property=RuntimeMaxSec=12s", argv)
        self.assertIn("--property=TimeoutStopSec=2s", argv)
        self.assertIn("--property=KillMode=control-group", argv)
        self.assertEqual(argv[-1], "fixed-bootstrap")
        self.assertTrue(kwargs["close_fds"])
        self.assertEqual(kwargs["env"]["XDG_RUNTIME_DIR"], f"/run/user/{UID}")
        self.assertNotIn("pass_fds", kwargs)
        self.assertNotIn("DBUS_SESSION_BUS_ADDRESS", gate.CLEAN_ENV)


class ProductionDrainTests(unittest.TestCase):
    """Pipes réels à taille minuscule, sans enfant ni exécutable."""

    def pipes(self, stdout=b"", stderr=b""):
        process = FakeProcess()
        for name, data in (("stdout", stdout), ("stderr", stderr)):
            reader, writer = os.pipe()
            os.write(writer, data)
            os.close(writer)
            stream = os.fdopen(reader, "rb")
            setattr(process, name, stream)
            self.addCleanup(stream.close)
        return process

    def test_exact_bound_and_both_channels(self):
        process = self.pipes(b"x" * 16, b"y" * 16)
        channels = gate.drain(process, time.monotonic() + .1, limit=16)
        self.assertEqual(channels, [b"x" * 16, b"y" * 16])
        self.assertEqual(process.returncode, 0)

    def test_overflow_preserves_bounded_prefix(self):
        process = self.pipes(b"x" * 17)
        with self.assertRaises(gate.DrainFailure) as context:
            gate.drain(process, time.monotonic() + .1, limit=16)
        self.assertIn("overflow", str(context.exception))
        self.assertEqual(context.exception.channels[0], b"x" * 16)

    def test_timeout_and_read_failure_are_bounded(self):
        process = self.pipes(b"x")
        with self.assertRaises(gate.DrainFailure):
            gate.drain(process, time.monotonic() - .1)
        with patch.object(gate.os, "read", side_effect=OSError("mock read error")):
            with self.assertRaisesRegex(gate.DrainFailure, "mock read"):
                gate.drain(process, time.monotonic() + .1)

    def test_manager_call_failure_collects_only_its_child(self):
        process = self.pipes(b"x" * 17)
        manager = gate.SystemManager(UID, popen=lambda *args, **kwargs: process)
        with patch.object(gate, "drain", side_effect=OSError("manager drain crash")):
            with self.assertRaisesRegex(OSError, "manager drain"):
                manager.call(["injected"], time.monotonic() + .2)
        self.assertTrue(process.killed)
        self.assertTrue(process.stdout.closed)
        self.assertTrue(process.stderr.closed)


class ElfPreparationTests(unittest.TestCase):
    """Analyse ELF de production avec capture passive simulée."""

    HEADER = ("Class: ELF64\nMachine: Advanced Micro Devices X86-64\n"
              "Build ID: abc123\n")

    def test_systemd_direct_runpath_is_recorded_and_not_inherited(self):
        import prepare
        tool = Path("/usr/bin/systemctl")
        library = Path("/usr/lib/systemd/libsystemd-test.so")
        libc = Path("/usr/lib/libc.so.6")
        data = {
            tool: self.HEADER + "(RUNPATH) [/usr/lib/systemd]\n"
                  "(NEEDED) [libsystemd-test.so]\n",
            library: self.HEADER + "(NEEDED) [libc.so.6]\n",
            libc: self.HEADER,
        }
        # A private namesake must not capture a transitive libc edge.
        candidates = {library, libc, Path("/usr/lib/systemd/libc.so.6")}
        with (
            patch.object(prepare, "capture", side_effect=lambda argv: data[Path(argv[-1])].encode()),
            patch.object(Path, "is_file", lambda path: path in candidates),
            patch.object(prepare, "trusted_system_path") as trusted,
        ):
            closure = prepare.elf_closure([tool])
        self.assertEqual(closure[str(tool)]["runpath"], ["/usr/lib/systemd"])
        self.assertEqual(closure[str(library)]["runpath"], [])
        self.assertEqual(set(closure), {str(path) for path in data})
        trusted.assert_any_call(Path("/usr/lib/systemd"))

    def test_unapproved_runpaths_and_rpath_are_refused(self):
        import prepare
        for tag, value in (("RUNPATH", "$ORIGIN"), ("RUNPATH", "relative"),
                           ("RUNPATH", "/tmp"),
                           ("RUNPATH", "/usr/lib/systemd:/usr/lib"),
                           ("RUNPATH", "/usr/lib/systemd:"),
                           ("RPATH", "/usr/lib/systemd")):
            with self.subTest(tag=tag, value=value), patch.object(
                    prepare, "capture", return_value=(
                        self.HEADER + f"({tag}) [{value}]\n").encode()):
                with self.assertRaises(ValueError):
                    prepare.elf_closure([Path("/usr/bin/systemctl")])
        with patch.object(prepare, "capture", return_value=(
                self.HEADER + "(RUNPATH) [/usr/lib/systemd]\n").encode()):
            with self.assertRaises(ValueError):
                prepare.elf_closure([Path("/usr/bin/other")])

    def test_writable_system_component_is_refused(self):
        import prepare
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "modifiable"):
                prepare.trusted_system_path(Path(temporary))


class PreparationTests(unittest.TestCase):
    def test_benign_preparation_uses_no_compiler_and_seals_actual_scripts(self):
        import prepare
        with tempfile.TemporaryDirectory() as temporary:
            lab = Path(temporary) / "fresh"
            argv = ["prepare.py", "--lab", str(lab), "--benign"]
            with (
                patch.object(sys, "argv", argv),
                patch.object(prepare, "capture", side_effect=native_spawn_forbidden),
                patch.object(prepare, "elf_closure", return_value={}) as closure,
                contextlib.redirect_stdout(io.StringIO()),
            ):
                prepare.main()
            manifest = json.loads((lab / "manifest.json").read_text())
            closure.assert_called_once()
            self.assertEqual(manifest["kind"], "benign")
            self.assertEqual(manifest["argv"], run.benign_command("nominal"))
            self.assertEqual(manifest["scope"], gate.policy(manifest["scope"]["nonce"]))
            self.assertIn(str(lab / "fixture/cgroup_gate.py"), manifest["files"])
            self.assertFalse((lab / "ATTEMPT").exists())
            self.assertFalse((lab / "bin/probe").exists())


    def test_exact_isolated_passive_cli_creates_no_cache_or_process_payload(self):
        import prepare
        with tempfile.TemporaryDirectory() as temporary:
            lab = Path(temporary) / "fresh"
            preparation_argv = ["prepare.py", "--lab", str(lab), "--benign"]
            with (
                patch.object(sys, "argv", preparation_argv),
                patch.object(prepare, "capture", side_effect=native_spawn_forbidden),
                patch.object(prepare, "elf_closure", return_value={}),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                prepare.main()
            manifest_hash = run.digest(lab / "manifest.json")
            argv = ["/usr/bin/python3", "-I", str(lab / "fixture/run.py"),
                    "--lab", str(lab), "--manifest-sha256", manifest_hash]
            before = sorted(str(path.relative_to(lab)) for path in lab.rglob("*"))

            def inert_only(command, *args, **kwargs):
                if command != argv:
                    return native_spawn_forbidden(command, *args, **kwargs)
                return INERT_POPEN(command, *args, **kwargs)

            # This exact source-only Python command is permitted; every other
            # executable/argument boundary remains forbidden by the sentinel.
            with patch.object(subprocess, "Popen", side_effect=inert_only):
                process = subprocess.run(argv, env=run.HOST_ENV, capture_output=True,
                                         timeout=3, check=False)
            self.assertEqual(process.returncode, 0, process.stderr.decode())
            self.assertEqual(json.loads(process.stdout)["runtime"], "NOT_RUN")
            self.assertEqual(before, sorted(str(path.relative_to(lab))
                                           for path in lab.rglob("*")))
            self.assertFalse((lab / "ATTEMPT").exists())



if __name__ == "__main__":
    unittest.main()
