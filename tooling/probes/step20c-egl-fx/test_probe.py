"""Tests offline uniquement ; aucun bwrap, aucun helper EGL/FX exécuté."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import run


class SystemctlDurationTests(unittest.TestCase):
    """Passer la sortie CLI réelle au parseur puis à l'admission de production."""

    def admission(self, runtime="12s", stop="2s"):
        import test_cgroup_admission as fixtures
        gate = run.gate.module
        fixture = fixtures.AdmissionTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        evidence = fixture.preflight()
        fixture.cgroups.present = True
        properties = {
            "Id": fixtures.SPEC["unit"], "Description": fixtures.SPEC["description"],
            "InvocationID": "c" * 32, "ControlGroup": fixtures.GROUP,
            "Delegate": "yes", "TasksMax": "256", "KillMode": "control-group",
            "RuntimeMaxUSec": runtime, "TimeoutStopUSec": stop,
        }
        # Literal CLI text, independently of POLICY. No systemctl is spawned.
        text = "\n".join(f"{key}={value}" for key, value in properties.items()
                         if value is not None)
        manager = gate.SystemManager(fixtures.UID, popen=fixtures.native_spawn_forbidden)

        def captured(argv, deadline):
            if "--user" in argv:
                return text
            return "\n".join(f"{key}={value}" for key, value in fixture.manager.owner.items())

        with patch.object(manager, "call", side_effect=captured) as capture:
            receipt = gate.admit(fixtures.SPEC, evidence, 43, fixture.proc,
                                 fixture.cgroups, manager, 1)
        self.addCleanup(os.close, receipt["pidfd"])
        self.assertIn("show", capture.call_args_list[0].args[0])
        return receipt

    def test_rendered_durations_pass_actual_show_parser_and_admission(self):
        receipt = self.admission()
        self.assertEqual(receipt["properties"]["RuntimeMaxUSec"], "12s")
        self.assertEqual(receipt["properties"]["TimeoutStopUSec"], "2s")

    def test_infinite_absent_and_different_durations_are_refused(self):
        for runtime, stop in (("infinity", "2s"), (None, "2s"), ("10s", "2s"),
                              ("12s", "infinity"), ("12s", None), ("12s", "3s"),
                              ("12000000", "2000000")):
            with self.subTest(runtime=runtime, stop=stop):
                with self.assertRaisesRegex(run.gate.module.Refusal, "propriétés/budget"):
                    self.admission(runtime, stop)


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.lab = Path(self.temporary.name)
        self.lab.chmod(0o700)
        (self.lab / "bin").mkdir()
        (self.lab / "fixture").mkdir()
        (self.lab / "bin/probe").write_bytes(b"INERT-NOT-ELF")
        (self.lab / "fixture/run.py").write_text("# inert\n")
        (self.lab / "fixture/cgroup_gate.py").write_text("# inert gate\n")
        self.files = [self.lab / "bin/probe", self.lab / "fixture/run.py",
                      self.lab / "fixture/cgroup_gate.py", Path("/usr/bin/python3"),
                      Path("/usr/bin/systemd-run"), Path("/usr/bin/systemctl"),
                      Path("/usr/bin/env"), Path("/usr/bin/readelf"),
                      Path("/usr/bin/bwrap"), Path("/usr/bin/prlimit")]
        self.manifest = {
            "schema": 2, "kind": "egl", "qualification_mode": "nominal",
            "scope": run.gate.policy("a" * 32), "lab": str(self.lab), "argv": run.command(self.lab),
            "environment": run.ENV, "supervisor_environment": run.HOST_ENV,
            "files": {str(path): {"sha256": run.digest(path), "resolved": str(path.resolve())}
                      for path in self.files},
        }

        self.manifest["scope_argv"] = run.gate.sealed_scope_argv(self.lab, self.manifest)

    def seal(self):
        (self.lab / "manifest.json").write_text(json.dumps(self.manifest))
        return run.digest(self.lab / "manifest.json")

    def verify(self, seal=None):
        if seal is None:
            seal = self.seal()
        with patch.object(run, "__file__", str(self.lab / "fixture/run.py")), \
                patch.dict(os.environ, run.HOST_ENV, clear=True):
            return run.verify(self.lab, seal)

    def test_valid_identity(self):
        self.assertEqual(self.verify()["schema"], 2)

    def test_manifest_drift(self):
        seal = self.seal()
        (self.lab / "manifest.json").write_text("{}")
        with self.assertRaises(run.Refusal):
            self.verify(seal)

    def test_binary_drift(self):
        seal = self.seal()
        (self.lab / "bin/probe").write_bytes(b"CHANGED")
        with self.assertRaises(run.Refusal):
            self.verify(seal)

    def test_script_identity_drift(self):
        seal = self.seal()
        (self.lab / "fixture/run.py").write_text("# changed\n")
        with self.assertRaises(run.Refusal):
            self.verify(seal)

    def test_scope_argv_and_policy_drift(self):
        self.manifest["scope_argv"].append("--property=TasksMax=infinity")
        with self.assertRaises(run.Refusal):
            self.verify()
        self.manifest["scope_argv"] = run.gate.sealed_scope_argv(self.lab, self.manifest)
        self.manifest["scope"]["properties"] = {"TasksMax": "infinity"}
        with self.assertRaises(run.Refusal):
            self.verify()

    def test_helper_drift_refuses_before_import(self):
        seal = self.seal()
        (self.lab / "fixture/cgroup_gate.py").write_text("raise AssertionError('import')")
        with patch.object(run._SealedHelper, "__getattr__", side_effect=AssertionError("import")):
            with self.assertRaisesRegex(run.Refusal, "helper"):
                self.verify(seal)

    def test_forbidden_mount_and_devices(self):
        for device in ("/dev/dri", "/dev/input", "/dev/udmabuf", "/etc", "/sys", "/run/user"):
            with self.subTest(device=device):
                self.manifest["argv"] = run.command(self.lab) + ["--ro-bind", device, device]
                with self.assertRaises(run.Refusal):
                    self.verify()

    def test_environment_pwd_and_extra(self):
        for altered in ({**run.ENV, "PWD": "/"}, {**run.ENV, "HOME": "/home/host"}):
            self.manifest["environment"] = altered
            with self.assertRaises(run.Refusal):
                self.verify()

    def test_supervisor_inherited_environment(self):
        seal = self.seal()
        with patch.dict(os.environ, {**run.HOST_ENV, "LD_PRELOAD": "bad"}, clear=True):
            with self.assertRaises(run.Refusal):
                run.verify(self.lab, seal)

    def test_wrong_launcher_identity(self):
        seal = self.seal()
        with patch.dict(os.environ, run.HOST_ENV, clear=True):
            with self.assertRaises(run.Refusal):
                run.verify(self.lab, seal)

    def test_private_mode(self):
        self.lab.chmod(0o755)
        with self.assertRaises(run.Refusal):
            self.verify()

    def test_budget_exclusive_no_retry(self):
        run.durable(self.lab / "ATTEMPT", b"one", exclusive=True)
        with self.assertRaises(FileExistsError):
            run.durable(self.lab / "ATTEMPT", b"two", exclusive=True)
        self.assertEqual((self.lab / "ATTEMPT").read_bytes(), b"one")

    def test_default_plan_has_no_write_or_spawn(self):
        before = sorted(self.lab.rglob("*"))
        with patch.object(sys, "argv", ["run.py", "--lab", str(self.lab), "--manifest-sha256", "x"]), \
                patch.object(run, "verify", return_value=self.manifest), \
                patch.object(run, "durable", side_effect=AssertionError("write")), \
                patch.object(subprocess, "Popen", side_effect=AssertionError("native boundary")), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run.main(), 0)
        self.assertEqual(sorted(self.lab.rglob("*")), before)

    def test_invalid_identity_stops_before_native_boundary(self):
        with patch.object(sys, "argv", ["run.py", "--lab", str(self.lab), "--manifest-sha256", "bad",
                                       "--approve-native-probe"]), \
                patch.object(run.gate, "run_scope", side_effect=AssertionError("native boundary")), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(run.main(), 20)
        self.assertFalse((self.lab / "ATTEMPT").exists())

    def test_consumed_budget_refuses_passive_plan(self):
        run.durable(self.lab / "ATTEMPT", b"one", exclusive=True)
        with patch.object(sys, "argv", ["run.py", "--lab", str(self.lab), "--manifest-sha256", "x"]), \
                patch.object(run, "verify", return_value=self.manifest), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(run.main(), 20)

    def test_spawn_failure_consumes_budget(self):
        arguments = ["run.py", "--lab", str(self.lab), "--manifest-sha256", "test", "--approve-native-probe"]
        def spawn_failure(lab, manifest, reserve, journal):
            reserve({"mock": True})
            return {"cause": "spawn_failure", "error": "mock spawn failure", "collected": True}, [b"", b""]
        with patch.object(sys, "argv", arguments), \
                patch.object(run, "verify", return_value=self.manifest), \
                patch.object(run.gate, "run_scope", side_effect=spawn_failure) as native, \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(run.main(), 20)
            self.assertEqual(run.main(), 20)
            self.assertEqual(native.call_count, 1)
        self.assertEqual(json.loads((self.lab / "result.json").read_text())["cause"], "spawn_failure")


class DrainTests(unittest.TestCase):
    def fake_python(self, script, **kwargs):
        return run.supervise([sys.executable, "-I", "-c", script], **kwargs)

    def test_exit_and_channels(self):
        result, channels = self.fake_python("import os; os.write(1,b'out'); os.write(2,b'err')")
        self.assertEqual(result["returncode"], 0)
        self.assertTrue(result["collected"])
        self.assertEqual(channels, [b"out", b"err"])

    def test_nonzero_exit(self):
        result, _ = self.fake_python("raise SystemExit(7)")
        self.assertEqual(result["returncode"], 7)
        self.assertEqual(result["cause"], "exit")

    def test_exact_output_bound(self):
        result, channels = self.fake_python(f"import os; os.write(1,b'x'*{run.LIMIT}); os.write(2,b'y'*{run.LIMIT})")
        self.assertEqual(result["cause"], "exit")
        self.assertEqual(list(map(len, channels)), [run.LIMIT, run.LIMIT])

    def test_output_overflow(self):
        result, channels = self.fake_python(f"import os; os.write(1,b'x'*{run.LIMIT + 1})")
        self.assertEqual(result["cause"], "output_overflow")
        self.assertEqual(len(channels[0]), run.LIMIT)
        self.assertTrue(result["collected"])

    def test_timeout_collection(self):
        result, _ = self.fake_python("import time; time.sleep(30)", payload_seconds=0.1, total_seconds=0.8)
        self.assertEqual(result["cause"], "timeout")
        self.assertTrue(result["collected"])
        self.assertLess(result["elapsed"], 1.0)

    def test_closed_pipes_preserve_cleanup_reserve(self):
        result, _ = self.fake_python("import os,time; os.close(1); os.close(2); time.sleep(30)",
                                     payload_seconds=0.1, total_seconds=0.8)
        self.assertEqual(result["cause"], "timeout")
        self.assertTrue(result["collected"])
        self.assertLess(result["elapsed"], 0.6)

    def test_read_failure_collects_owned_child(self):
        real_popen = subprocess.Popen
        children = []
        def remember(*args, **kwargs):
            child = real_popen(*args, **kwargs)
            children.append(child)
            return child
        real_read = os.read
        def fail_drain(fd, size):
            if size == 65536:
                raise OSError("mock read failure")
            return real_read(fd, size)
        with patch.object(run.subprocess, "Popen", side_effect=remember), \
                patch.object(run.os, "read", side_effect=fail_drain):
            result, _ = self.fake_python("import os,time; os.write(1,b'x'); time.sleep(30)")
            self.assertEqual(result["cause"], "supervisor_failure")
        self.assertIsNotNone(children[0].returncode)

    def test_collection_failure_explicit(self):
        real_wait = subprocess.Popen.wait
        def delayed_wait(child, *args, **kwargs):
            real_wait(child, timeout=1)
            raise subprocess.TimeoutExpired("mock collection", 0)
        with patch.object(subprocess.Popen, "wait", delayed_wait):
            result, _ = self.fake_python("pass", payload_seconds=0.05, total_seconds=0.2)
        self.assertEqual(result["cause"], "cleanup_unproven")
        self.assertFalse(result["collected"])


class SourceTests(unittest.TestCase):
    def test_device_guard_precedes_fx_and_ownership(self):
        source = Path(__file__).with_name("probe.c").read_text()
        self.assertLess(source.index("query_display(display, EGL_DEVICE_EXT"),
                        source.index("renderer = fx_renderer_create_egl(egl)"))
        self.assertLess(source.index("if (!software || drm)"), source.index("renderer = fx_renderer_create_egl(egl)"))
        self.assertIn("} else if (egl != NULL)", source)
        self.assertIn("egl = NULL;", source)
        for forbidden in ("eglQueryDevicesEXT(", "wlr_fx_renderer_get_egl(", "wl_display_create(",
                          "wlr_backend_start(", "wlr_headless_add_output(", "wlr_allocator_autocreate(",
                          "wlr_buffer_create(", "glDraw", "->texture_caps", "->egl", "->display"):
            self.assertNotIn(forbidden, source)
        self.assertIn('"PWD=/tmp"', source)
        self.assertIn("modifiers > 4096", source)


if __name__ == "__main__":
    unittest.main()
