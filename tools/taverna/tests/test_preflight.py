import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('preflight', ROOT / 'tools/taverna/preflight.py')
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)

VERSIONS = {'git': 'git version 2.50.1', 'gh': 'gh version 2.70.0', 'python3.12': 'Python 3.12.12', 'xcodebuild': 'Xcode 26.0', 'ghc': '9.6.3', 'cabal': '3.10.3.0'}


def ready_tools(argv):
    if 'rev-parse' in argv:
        return 0, 'a' * 40
    if 'simctl' in argv:
        return 0, json.dumps({'devices': {'runtime': [{'isAvailable': True}]}})
    if argv[0] == 'xcrun':
        return 0, '26.0'
    return 0, VERSIONS[argv[0]]


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '.build/SimulatorDevices').mkdir(parents=True)

    def test_tool_presence_does_not_prove_ios_build(self):
        result = preflight.inspect(self.root, ready_tools)
        self.assertEqual(result['gates']['foundation_tools']['status'], 'PASS')
        self.assertEqual(result['gates']['ios_simulator']['status'], 'BLOCKED')
        self.assertEqual(result['gates']['core_from_source']['status'], 'BLOCKED')
        self.assertEqual(result['gates']['signed_device']['status'], 'BLOCKED')
        self.assertEqual(result['checks']['ghc']['version'], '9.6.3')
        self.assertEqual(result['source_commit'], 'a' * 40)
        self.assertFalse(result['build_proven'])
        self.assertFalse(result['push_proven'])

    def test_each_missing_dependency_blocks_its_gate(self):
        for name in VERSIONS:
            with self.subTest(tool=name):
                runner = lambda argv: (127, '') if argv[0] == name else ready_tools(argv)
                result = preflight.inspect(self.root, runner)
                key = 'python' if name == 'python3.12' else 'xcode' if name == 'xcodebuild' else name
                self.assertEqual(result['checks'][key]['status'], 'BLOCKED')
                self.assertEqual(result['checks'][key]['reason'], 'missing')
                self.assertTrue(any(key in gate['blocked_by'] for gate in result['gates'].values()))

    def test_wrong_ghc_rejected(self):
        runner = lambda argv: (0, '9.12.2') if argv[0] == 'ghc' else ready_tools(argv)
        result = preflight.inspect(self.root, runner)
        self.assertEqual(result['checks']['ghc']['status'], 'BLOCKED')
        self.assertEqual(result['checks']['ghc']['required'], '9.6.3')

    def test_wrong_python_rejected(self):
        runner = lambda argv: (0, 'Python 3.13.1') if argv[0] == 'python3.12' else ready_tools(argv)
        self.assertEqual(preflight.inspect(self.root, runner)['checks']['python']['status'], 'BLOCKED')

    def test_failed_sdk_blocks(self):
        runner = lambda argv: (1, '') if 'iphoneos' in argv else ready_tools(argv)
        result = preflight.inspect(self.root, runner)
        self.assertIn('ios_sdk', result['gates']['ios_simulator']['blocked_by'])

    def test_empty_or_malformed_simulator_list(self):
        for data in ('{}', '{bad', 'null', '{"devices":{}}', '{"devices":{"runtime":[{"isAvailable":false}]}}'):
            runner = lambda argv: (0, data) if 'simctl' in argv else ready_tools(argv)
            self.assertEqual(preflight.inspect(self.root, runner)['checks']['simulators']['status'], 'BLOCKED')

    def test_timeout_is_explicit(self):
        runner = lambda argv: (124, '') if argv[0] == 'xcodebuild' else ready_tools(argv)
        self.assertEqual(preflight.inspect(self.root, runner)['checks']['xcode']['reason'], 'timeout')

    def test_state_paths_are_distinct_and_readonly(self):
        first = self.root / 'one'; first.mkdir()
        second = self.root / 'two'; second.mkdir()
        a, b = preflight.state_layout(first), preflight.state_layout(second)
        self.assertTrue(set(a.values()).isdisjoint(b.values()))
        self.assertTrue(all(Path(path).is_relative_to(first.resolve()) for path in a.values()))
        self.assertFalse((first / '.build').exists())

    def test_state_symlink_escape_blocked(self):
        work = self.root / 'work'; work.mkdir()
        (work / '.build').symlink_to(self.root)
        with self.assertRaisesRegex(ValueError, 'escapes'):
            preflight.state_layout(work)
        self.assertEqual(preflight.inspect(work, ready_tools)['checks']['state_isolation']['status'], 'BLOCKED')

    def test_no_account_or_secret_commands(self):
        seen = []
        def runner(argv):
            seen.append(argv)
            return ready_tools(argv)
        preflight.inspect(self.root, runner)
        self.assertEqual(len(seen), 10)
        self.assertTrue(all(argv[0] in {'git', 'gh', 'python3.12', 'xcodebuild', 'xcrun', 'ghc', 'cabal'} for argv in seen))
        self.assertFalse(any('security' in word or 'op' == word or 'auth' == word for argv in seen for word in argv))

    def test_run_command_errors_do_not_leak_stderr(self):
        with patch.object(preflight.subprocess, 'run', side_effect=FileNotFoundError):
            self.assertEqual(preflight.run_command(['missing']), (127, ''))
        with patch.object(preflight.subprocess, 'run', side_effect=subprocess.TimeoutExpired('x', 15)):
            self.assertEqual(preflight.run_command(['slow']), (124, ''))
        with patch.object(preflight.subprocess, 'run', side_effect=PermissionError):
            self.assertEqual(preflight.run_command(['denied']), (126, ''))
        with patch.object(preflight.subprocess, 'run', return_value=subprocess.CompletedProcess('x', 1, '', 'secret')):
            self.assertEqual(preflight.run_command(['x']), (1, ''))

    def test_missing_session_simulator_set_never_queries_global_devices(self):
        (self.root / '.build/SimulatorDevices').rmdir()
        seen = []
        def runner(argv):
            seen.append(argv)
            return ready_tools(argv)
        result = preflight.inspect(self.root, runner)
        self.assertEqual(result['checks']['simulators']['status'], 'BLOCKED')
        self.assertFalse(any('simctl' in argv for argv in seen))
        self.assertFalse((self.root / '.build/SimulatorDevices').exists())

    def test_only_worktree_simulator_set_is_queried(self):
        seen = []
        def runner(argv):
            seen.append(argv)
            return ready_tools(argv)
        preflight.inspect(self.root, runner)
        command = next(argv for argv in seen if 'simctl' in argv)
        self.assertEqual(command[2:4], ['--set', str(self.root / '.build/SimulatorDevices')])

    def test_cli_empty_path_exit_two_and_json(self):
        result = subprocess.run([sys.executable, str(ROOT / 'tools/taverna/preflight.py'), '--root', str(self.root)], env={**os.environ, 'PATH': self.temp.name}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        data = json.loads(result.stdout)
        self.assertEqual(data['overall'], 'BLOCKED')
        self.assertEqual(data['checks']['git']['reason'], 'missing')
        self.assertIsNone(data['source_commit'])


if __name__ == '__main__':
    unittest.main()
