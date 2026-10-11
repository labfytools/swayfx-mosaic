"""Offline regression checks for the cumulative package patch exporter."""

import hashlib
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PATCH = Path("patches/0001-mosaic-layout-viewport.patch")
BASE = "a57e3f2c4d88f258c2f038343a398c6d5be1fb59"


def run(*args, cwd, env=None, check=True):
    return subprocess.run(
        args, cwd=cwd, env=env, check=check, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def digest(data):
    return hashlib.sha256(data).hexdigest()


class ExportPatchTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mosaic-export-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.clone = self.root / "clone"
        # The clone retains the imported base but never changes the real repo.
        run("git", "clone", "-q", "--no-hardlinks", str(ROOT), str(self.clone), cwd=self.root)
        shutil.copy2(ROOT / "tooling/export-patch.sh", self.clone / "tooling/export-patch.sh")
        shutil.copy2(ROOT / PATCH, self.clone / PATCH)

    def export(self, *, env=None, check=True):
        return run("sh", "tooling/export-patch.sh", cwd=self.clone, env=env, check=check)

    def test_complete_idempotent_and_index_untouched(self):
        original = (self.clone / PATCH).read_bytes()
        self.export()
        first = (self.clone / PATCH).read_bytes()
        self.assertTrue(first)
        self.assertEqual(first, original)
        self.export()
        self.assertEqual((self.clone / PATCH).read_bytes(), first)

        # One staged source edit plus one later working-tree edit must both
        # appear, while the real staged index remains byte-identical.
        source = self.clone / "sway/tree/mosaic.c"
        with source.open("a") as file:
            file.write("\n/* export staged marker */\n")
        run("git", "add", "sway/tree/mosaic.c", cwd=self.clone)
        with source.open("a") as file:
            file.write("/* export working marker */\n")
        index = self.clone / ".git/index"
        index_before = index.read_bytes()
        objects_before = sorted(str(path.relative_to(self.clone / ".git/objects"))
                                for path in (self.clone / ".git/objects").rglob("*")
                                if path.is_file())
        staged_before = run("git", "diff", "--cached", "--binary", cwd=self.clone).stdout
        self.export()
        changed = (self.clone / PATCH).read_bytes()
        self.assertIn(b"export staged marker", changed)
        self.assertIn(b"export working marker", changed)
        self.assertEqual(index.read_bytes(), index_before)
        self.assertEqual(sorted(str(path.relative_to(self.clone / ".git/objects"))
                                for path in (self.clone / ".git/objects").rglob("*")
                                if path.is_file()), objects_before)
        self.assertEqual(run("git", "diff", "--cached", "--binary", cwd=self.clone).stdout,
                         staged_before)
        self.export()
        self.assertEqual((self.clone / PATCH).read_bytes(), changed)

    def test_untracked_source_and_failure_preserve_patch(self):
        source = self.clone / "include/sway/tree/export-probe.h"
        source.write_text("/* untracked source marker */\n")
        self.export()
        exported = (self.clone / PATCH).read_bytes()
        self.assertIn(b"untracked source marker", exported)

        # Ignored files cannot be exported by Git. Source equivalence must
        # reject this late validation failure before replacing the artifact.
        ignored = self.clone / "include/sway/tree/export-probe.o"
        ignored.write_text("ignored source marker\n")
        failed = self.export(check=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(digest((self.clone / PATCH).read_bytes()), digest(exported))

        # Also cover an early temporary-allocation failure.
        env = os.environ.copy()
        env["TMPDIR"] = str(self.root / "missing")
        failed = self.export(env=env, check=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(digest((self.clone / PATCH).read_bytes()), digest(exported))

    def test_source_deletion_is_exported(self):
        source = self.clone / "include/sway/tree/node.h"
        source.unlink()
        self.export()
        patch = (self.clone / PATCH).read_bytes()
        self.assertIn(b"deleted file mode", patch)
        self.assertIn(b"include/sway/tree/node.h", patch)

    def test_unmerged_source_index_preserves_patch(self):
        original = (self.clone / PATCH).read_bytes()
        path = "include/sway/tree/container.h"
        blob = run("git", "rev-parse", f"HEAD:{path}", cwd=self.clone).stdout.strip()
        run("git", "update-index", "--force-remove", path, cwd=self.clone)
        subprocess.run(
            ["git", "update-index", "--index-info"], cwd=self.clone,
            input=f"100644 {blob} 1\t{path}\n100644 {blob} 2\t{path}\n",
            text=True, check=True, capture_output=True,
        )
        index = self.clone / ".git/index"
        index_before = index.read_bytes()
        failed = self.export(check=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("unresolved source conflicts", failed.stderr)
        self.assertEqual(index.read_bytes(), index_before)
        self.assertEqual((self.clone / PATCH).read_bytes(), original)

    def test_source_mode_change_is_exported(self):
        source = self.clone / "sway/tree/mosaic.c"
        source.chmod(0o755)
        self.export()
        patch = (self.clone / PATCH).read_bytes()
        self.assertIn(b"new file mode 100755", patch)
        self.assertEqual(source.stat().st_mode & 0o777, 0o755)

    def test_interruption_preserves_patch_and_cleans_temporary_files(self):
        original = (self.clone / PATCH).read_bytes()
        tool_dir = self.root / "tools"
        tool_dir.mkdir()
        wrapper = tool_dir / "git"
        wrapper.write_text(
            "#!/bin/sh\n"
            "if test \"$1\" = archive; then kill -TERM \"$PPID\"; exit 1; fi\n"
            f"exec {shlex.quote(shutil.which('git'))} \"$@\"\n"
        )
        wrapper.chmod(0o755)
        scratch = self.root / "scratch"
        scratch.mkdir()
        env = os.environ.copy()
        env["PATH"] = f"{tool_dir}:{env['PATH']}"
        env["TMPDIR"] = str(scratch)
        failed = self.export(env=env, check=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual((self.clone / PATCH).read_bytes(), original)
        self.assertEqual(list((self.clone / "patches").glob(".mosaic-patch.*")), [])
        self.assertEqual(list(scratch.iterdir()), [])

    def test_forward_apply_and_source_equivalence(self):
        self.export()
        pristine = self.root / "pristine"
        pristine.mkdir()
        archive = self.root / "base.tar"
        with archive.open("wb") as file:
            subprocess.run(["git", "archive", BASE], cwd=self.clone,
                           check=True, stdout=file)
        run("tar", "-xf", str(archive), "-C", str(pristine), cwd=self.root)
        run("git", "apply", "--check", str(self.clone / PATCH), cwd=pristine)
        run("git", "apply", str(self.clone / PATCH), cwd=pristine)
        for name in ("include", "sway", "meson.build", "meson_options.txt",
                     "tests/mosaic-model.c"):
            run("git", "diff", "--no-index", "--exit-code", "--",
                str(pristine / name), str(self.clone / name), cwd=self.root)


if __name__ == "__main__":
    unittest.main()
