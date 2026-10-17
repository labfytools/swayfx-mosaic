"""Independent offline tests of the actual installed guard, never its launcher."""

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import prepare


class GuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.environ.get('MOSAIC_INSTALLED_GUARD')
        if not path:
            raise RuntimeError('Set MOSAIC_INSTALLED_GUARD to the audited session.py')
        cls.guard = prepare.load_guard(Path(path))

    def setUp(self):
        self.guard = type(self).guard
        self.env = {'XDG_SEAT': 'seat0', 'XDG_VTNR': '2',
                    'INVOCATION_ID': 'offline', 'NOTIFY_SOCKET': '/offline'}
        self.login = {'User': str(os.getuid()), 'Class': 'user', 'Seat': 'seat0',
                      'VTNr': '2', 'Active': 'yes', 'Remote': 'no', 'Type': 'tty'}
        self.group = '0::/user.slice/session.slice/' + self.guard.WM_UNIT
        self.units = [(self.guard.WM_UNIT, 'activating')]

    def validate(self):
        self.guard.validate_context(self.env, self.group, self.login,
                                    'tty2', self.units)

    def test_valid_simulated_context(self):
        self.validate()

    def test_fake_seat_rejected(self):
        self.login['Seat'] = 'seat1'
        with self.assertRaises(RuntimeError):
            self.validate()

    def test_wrong_service_cgroup_rejected(self):
        self.group = '0::/session.scope'
        with self.assertRaises(RuntimeError):
            self.validate()

    def test_concurrent_stable_including_shutdown_rejected(self):
        for state in ('active', 'activating', 'deactivating'):
            with self.subTest(state=state):
                self.units = [('wayland-wm@sway.desktop.service', state)]
                with self.assertRaises(RuntimeError):
                    self.validate()

    def test_inherited_ipc_and_display_rejected(self):
        for name in ('SWAYSOCK', 'I3SOCK', 'WAYLAND_DISPLAY', 'WAYLAND_SOCKET',
                     'DISPLAY', 'WLR_BACKENDS'):
            with self.subTest(name=name):
                self.env[name] = '/unrelated'
                with self.assertRaises(RuntimeError):
                    self.validate()
                del self.env[name]

    def test_missing_uwsm_rejected(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as directory:
            with self.assertRaises(FileNotFoundError):
                prepare.require_uwsm(self.guard, Path(directory) / 'missing')

    def test_altered_binary_rejected_by_actual_guard(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as directory:
            binary = Path(directory) / 'altered'
            binary.write_bytes(b'not the audited binary')
            binary.chmod(0o500)
            with patch.object(self.guard, 'BINARY', binary):
                with self.assertRaisesRegex(RuntimeError, 'CORE-C V2'):
                    self.guard.verify_files()

    def test_symlink_and_writable_file_refused(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as directory:
            target = Path(directory) / 'target'
            target.write_bytes(b'unchanged')
            link = Path(directory) / 'link'
            link.symlink_to(target)
            with self.assertRaises(OSError):
                self.guard.read_regular(link)
            target.chmod(0o666)
            with self.assertRaises(RuntimeError):
                self.guard.read_regular(target)
            self.assertEqual(target.read_bytes(), b'unchanged')

    def test_import_does_not_dispatch(self):
        with patch('os.execve', side_effect=AssertionError('exec forbidden')), \
                patch('subprocess.run', side_effect=AssertionError('run forbidden')):
            prepare.load_guard(Path(os.environ['MOSAIC_INSTALLED_GUARD']))

    def test_receipt_is_exclusive_and_readonly(self):
        with tempfile.TemporaryDirectory(dir='/var/tmp') as directory:
            path = Path(directory) / 'receipt'
            prepare.write_private(path, b'first')
            self.assertEqual(path.stat().st_mode & 0o777, 0o400)
            with self.assertRaises(FileExistsError):
                prepare.write_private(path, b'replacement')
            self.assertEqual(path.read_bytes(), b'first')


class RepairedLaunchTests(GuardTests):
    """Exercise actual launch with every external effect intercepted."""

    @classmethod
    def setUpClass(cls):
        import repair
        path = Path(os.environ['MOSAIC_INSTALLED_GUARD'])
        source = repair.corrected(path.read_bytes())
        import types
        cls.guard = types.ModuleType('offline_repaired_guard')
        exec(compile(source, '<audited-repair>', 'exec'), cls.guard.__dict__)

    def launch_mocked(self, conflicts, accepted):
        from types import SimpleNamespace
        from contextlib import ExitStack
        env = dict(self.env, XDG_RUNTIME_DIR=f'/run/user/{os.getuid()}',
                   XDG_SESSION_ID='offline')

        def run(argv):
            if 'list-units' in argv:
                return f'{self.guard.WM_UNIT} loaded activating start'
            self.assertIn('Conflicts', argv)
            return conflicts

        def read_text(path, *args, **kwargs):
            if str(path) == '/proc/self/cgroup':
                return self.group
            self.assertEqual(str(path), '/sys/class/tty/tty0/active')
            return 'tty2\n'

        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, env, clear=True))
            for name, value in (
                    ('verify_files', lambda: None),
                    ('secure_directory', lambda path: 123),
                    ('properties', lambda argv: self.login), ('run', run)):
                stack.enter_context(patch.object(self.guard, name, value))
            stack.enter_context(patch('os.fstat', return_value=SimpleNamespace(
                st_uid=os.getuid(), st_mode=0o40700)))
            stack.enter_context(patch('os.close'))
            stack.enter_context(patch.object(Path, 'read_text', read_text))
            chdir = stack.enter_context(patch('os.chdir'))
            execute = stack.enter_context(patch('os.execve'))
            if accepted:
                self.guard.launch()
                execute.assert_called_once()
                self.assertEqual(execute.call_args.args[0], str(self.guard.BINARY))
            else:
                with self.assertRaisesRegex(RuntimeError, 'Isolation'):
                    self.guard.launch()
                execute.assert_not_called()
                chdir.assert_not_called()

    def quoted_conflicts(self):
        units = list(self.guard.EXCLUDED)
        return ' '.join(units[:-1]) + ' "' + units[-1].replace('\\', '\\\\') + '"\n'

    def test_actual_launch_accepts_systemd_quoted_conflicts(self):
        self.launch_mocked(self.quoted_conflicts(), True)

    def test_actual_launch_refuses_each_missing_exclusion(self):
        import shlex
        for missing in self.guard.EXCLUDED:
            with self.subTest(missing=missing):
                units = shlex.split(self.quoted_conflicts())
                units.remove(missing)
                self.launch_mocked(shlex.join(units), False)

    def test_actual_launch_refuses_malformed_quotes(self):
        with self.assertRaises(ValueError):
            self.launch_mocked('"unfinished', True)

    def test_changed_preimage_refused(self):
        import repair
        with self.assertRaises(RuntimeError):
            repair.corrected(b'changed guard')


if __name__ == '__main__':
    unittest.main(verbosity=2)
