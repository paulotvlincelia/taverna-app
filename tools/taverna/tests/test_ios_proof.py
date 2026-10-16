"""IOS-08/09/13/14/16/19: actual artifacts and no empty success."""
import copy
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/taverna'))
spec = importlib.util.spec_from_file_location('ios_proof', ROOT / 'tools/taverna/ios_proof.py')
proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proof)


def result_fixture():
    # Fictional values, shaped by xcresulttool 0.4.0's observed JSON.
    device = dict(deviceId='owned-simulator', architecture='arm64', platform='iOS Simulator',
                  modelName='iPhone 17', osVersion='27.0', osBuildNumber='24A434')
    cases = [dict(nodeIdentifier=name, nodeType='Test Case', name=name.split('/')[-1], result='Passed')
             for name in sorted(proof.REQUIRED_TESTS)]
    tree = dict(devices=[device], testPlanConfigurations=[], testNodes=[
        dict(name='Fictional plan', nodeType='Test Plan', result='Passed', children=cases)])
    summary = dict(result='Passed', totalTestCount=4, passedTests=4, failedTests=0,
                   skippedTests=0, expectedFailures=0, testFailures=[], devicesAndConfigurations=[dict(device=device)])
    return summary, tree


class ProofTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / '.build/test-temp'; parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_first_build_profile_is_explicit_and_bound_to_runner(self):
        record = dict(ui_profile='first-build', ui_language='en', ui_region='US',
                      ui_orientation='portrait', ui_appearance='light')
        plan = dict(EnvironmentVariables=dict(TAVERNA_UI_PROFILE='first-build'),
                    OnlyTestIdentifiers=[], SkipTestIdentifiers=[])
        self.assertEqual(proof.validate_profile(record, plan), 'first-build')
        for field, value in [('ui_profile', 'unknown'), ('ui_language', 'pt'),
                             ('ui_region', 'BR'), ('ui_orientation', 'landscape'),
                             ('ui_appearance', 'dark')]:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'profile'):
                proof.validate_profile(dict(record, **{field: value}), plan)
        for env in [{}, dict(TAVERNA_UI_PROFILE='full-matrix')]:
            with self.subTest(env=env), self.assertRaisesRegex(ValueError, 'profile'):
                proof.validate_profile(record, dict(plan, EnvironmentVariables=env))
        for key in ('OnlyTestIdentifiers', 'SkipTestIdentifiers'):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'filtered'):
                proof.validate_profile(record, dict(plan, **{key: ['testLaunch']}))
        full = dict(ui_profile='full-matrix')
        self.assertEqual(proof.validate_profile(full,
                         dict(EnvironmentVariables=dict(TAVERNA_UI_PROFILE='full-matrix'))), 'full-matrix')

    def test_all_required_cases_with_zero_failure_and_skip(self):
        summary, tree = result_fixture()
        result = proof.validate_results(summary, tree, 'owned-simulator')
        self.assertEqual(result['executed'], 4)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(result['skipped'], 0)
        self.assertEqual(set(result['required_cases']), proof.REQUIRED_TESTS)

    def test_empty_or_partial_success_is_rejected(self):
        summary, tree = result_fixture()
        for count in (0, 1):
            bad = copy.deepcopy(tree); bad['testNodes'][0]['children'] = bad['testNodes'][0]['children'][:count]
            values = dict(summary, totalTestCount=count, passedTests=count)
            with self.subTest(count=count), self.assertRaisesRegex(ValueError, 'required|empty'):
                proof.validate_results(values, bad, 'owned-simulator')

    def test_each_required_case_must_have_passed(self):
        summary, tree = result_fixture()
        for name in proof.REQUIRED_TESTS:
            bad = copy.deepcopy(tree)
            for case in bad['testNodes'][0]['children']:
                if case['nodeIdentifier'] == name:
                    case['result'] = 'Skipped'
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'case|Skipped'):
                proof.validate_results(summary, bad, 'owned-simulator')

    def test_summary_failures_skips_expected_failures_and_wrong_count_rejected(self):
        summary, tree = result_fixture()
        for field, value in [('result', 'Failed'), ('failedTests', 1), ('skippedTests', 1),
                             ('expectedFailures', 1), ('passedTests', 0), ('testFailures', [{'message': 'failure'}])]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                proof.validate_results(dict(summary, **{field: value}), tree, 'owned-simulator')

    def test_results_bound_to_owned_simulator_and_runtime_platform(self):
        summary, tree = result_fixture()
        for field, value in [('deviceId', 'other'), ('architecture', 'x86_64'), ('platform', 'iOS')]:
            bad = copy.deepcopy(tree); bad['devices'][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'destination'):
                proof.validate_results(summary, bad, 'owned-simulator')

    def test_required_stage_failure_or_timeout_cannot_be_hidden_by_cleanup(self):
        good = dict(exit_code=0, command=['fictional-tool'])
        for stage in ('native', 'build', 'test'):
            for bad in [dict(good, exit_code=65), dict(good, timed_out=True),
                        dict(good, test_exit_code=124, test_timed_out=True)]:
                with self.subTest(stage=stage, bad=bad), self.assertRaisesRegex(ValueError, stage):
                    proof.validate_stage(stage, bad)
        proof.validate_stage('test', dict(good, test_exit_code=0, test_timed_out=False))

    def test_missing_stage_or_command_is_not_success(self):
        for bad in [{}, dict(exit_code=0), dict(exit_code=0, command=[])]:
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'build'):
                proof.validate_stage('build', bad)

    def test_product_must_exist_match_hash_and_be_inside_worktree(self):
        path = self.root / 'product'; path.write_bytes(b'fictional product')
        record = dict(path=str(path), sha256=proof.sha256(path))
        self.assertEqual(proof.artifact(self.root, record), path)
        with self.assertRaisesRegex(ValueError, 'hash'):
            proof.artifact(self.root, dict(record, sha256='0' * 64))
        path.unlink()
        with self.assertRaises(OSError):
            proof.artifact(self.root, record)
        outside = self.root.parent / 'not-owned'
        with self.assertRaises((OSError, ValueError)):
            proof.artifact(self.root, dict(record, path=str(outside)))

    def test_product_platform_read_from_actual_macho_bytes(self):
        for platform, cpu in ((7, 16777228), (2, 16777228), (1, 16777228), (7, 16777223)):
            command = struct.pack('<6I', 0x32, 24, platform, 15 << 16, 27 << 16, 0)
            data = struct.pack('<8I', 0xfeedfacf, cpu, 0, 2, 1, len(command), 0, 0) + command
            path = self.root / 'binary'; path.write_bytes(data)
            if platform == 7 and cpu == 16777228:
                self.assertEqual(proof.product_platform(path), dict(architecture='arm64', platform=7))
            else:
                with self.assertRaisesRegex(ValueError, 'Simulator'):
                    proof.product_platform(path)

    def test_every_launch_event_must_prove_both_denials_before_main(self):
        event = dict(pid=42, executable='SimpleX', phase='before_main', ipv4_errno=1,
                     ipv6_errno=13, loopback=True)
        proof.validate_containment([event], 1)
        for field, value in [('pid', 0), ('executable', 'Other'), ('phase', 'after_main'),
                             ('ipv4_errno', 0), ('ipv6_errno', 36), ('loopback', False)]:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'containment'):
                proof.validate_containment([event, dict(event, **{field: value})], 1)
        with self.assertRaisesRegex(ValueError, 'missing'):
            proof.validate_containment([], 1)

    def test_failed_report_keeps_local_core_and_device_states_separate(self):
        result = proof.verify(self.root, self.root / 'missing-build', self.root / 'missing-test',
                              self.root / 'missing-native', self.root / 'missing-bindings', 'failure')
        self.assertEqual(result['exit_code'], 2)
        self.assertEqual(result['local_build_ui'], 'NOT PROVEN')
        self.assertEqual(result['native_core'], 'NOT CHECKED')
        self.assertEqual(result['device_signing_push'], 'NOT RUN')
        self.assertTrue(result['distribution'].startswith('BLOCKED'))

    def test_recorded_process_retains_failure_code_and_timeout(self):
        failed = proof.record_stage(self.root, self.root, 'failure',
                                    [sys.executable, '-c', 'raise SystemExit(65)'], 10)
        self.assertEqual(failed['exit_code'], 65)
        self.assertFalse(failed['timed_out'])
        timed = proof.record_stage(self.root, self.root, 'timeout',
                                   [sys.executable, '-c', 'import time; time.sleep(2)'], .02)
        self.assertEqual(timed['exit_code'], 124)
        self.assertTrue(timed['timed_out'])
        with self.assertRaisesRegex(ValueError, 'timeout'):
            proof.validate_stage('timeout', timed)

    def test_test_recorder_stops_at_failed_build_without_starting_simulator(self):
        build = self.root / 'build'; build.mkdir()
        (build / 'receipt.json').write_text(json.dumps(dict(exit_code=65, command=['fictional-build'])))
        result = proof.record_tests(self.root, build, 'refused-test', self.root / 'missing-guard')
        self.assertEqual(result['exit_code'], 2)
        self.assertIn('build: missing or failed required stage', result['error'])
        self.assertEqual(result['steps'], [])
        self.assertNotIn('test_exit_code', result)

    def test_two_clean_runs_require_same_commit_inputs_and_distinct_state(self):
        a = self.root / 'a'; b = self.root / 'b'; a.mkdir(); b.mkdir()
        first = dict(exit_code=0, local_build_ui='PASS', clean_source=True, source_commit='a' * 40,
                     native_manifest_sha256='b' * 64, ui_profile='first-build', worktree=str(a), udid='first')
        second = dict(first, worktree=str(b), udid='second')
        result = proof.compare_runs(first, second)
        self.assertEqual(result['source_commit'], 'a' * 40)
        self.assertEqual(result['native_manifest_sha256'], 'b' * 64)
        self.assertEqual(len(result['runs']), 2)
        for field, value in [('source_commit', 'c' * 40), ('native_manifest_sha256', 'c' * 64), ('source_commit', ''), ('native_manifest_sha256', ''),
                             ('worktree', str(a)), ('udid', 'first'), ('clean_source', False), ('exit_code', 124), ('ui_profile', 'full-matrix'), ('ui_profile', '')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                proof.compare_runs(first, dict(second, **{field: value}))

    def test_two_paths_to_same_physical_worktree_are_not_independent(self):
        a = self.root / 'original'; a.mkdir(); alias = self.root / 'alias'; alias.symlink_to(a, target_is_directory=True)
        first = dict(exit_code=0, local_build_ui='PASS', clean_source=True, source_commit='a' * 40,
                     native_manifest_sha256='b' * 64, ui_profile='first-build', worktree=str(a), udid='first')
        with self.assertRaisesRegex(ValueError, 'distinct'):
            proof.compare_runs(first, dict(first, worktree=str(alias), udid='second'))

    def test_console_counts_all_ui_configurations_without_hiding_missing_cases(self):
        lines = []
        for identifier in sorted(proof.REQUIRED_TESTS) + ['Tests_iOSLaunchTests/testLaunch()']:
            cls, name = identifier.split('/')
            stem = f"Test Case '-[Tests_iOS.{cls} {name[:-2]}]' "
            lines += [stem + 'started.', stem + 'passed (1.0 seconds).']
        text = '\n'.join(lines)
        result = proof.console_counts(text)
        self.assertEqual(result['expanded_executions'], 5)
        self.assertEqual(result['expanded_passed'], 5)
        self.assertEqual(result['per_method']['Tests_iOSLaunchTests/testLaunch()'], 2)
        for bad in ['', '\n'.join(lines[:-1]), text.replace('passed (1.0 seconds).', 'failed (1.0 seconds).', 1)]:
            with self.subTest(text=bad[:25]), self.assertRaises(ValueError):
                proof.console_counts(bad)

    def test_package_and_product_caches_cannot_alias_another_worktree(self):
        state = self.root / '.build'; state.mkdir()
        self.assertIn(str(state / 'SourcePackages'), proof.package_args(self.root))
        for name in ('SourcePackages', 'package-cache', 'DerivedData'):
            alias = state / name; alias.symlink_to(self.root.parent, target_is_directory=True)
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, name):
                proof.package_args(self.root)
            alias.unlink()

    def test_final_clean_gate_refuses_dirty_source(self):
        with self.assertRaisesRegex(ValueError, 'clean'):
            proof.validate_clean_source(dict(source_state=' M app.swift'), True)
        proof.validate_clean_source(dict(source_state=''), True)
        proof.validate_clean_source(dict(source_state=' M app.swift'), False)


if __name__ == '__main__':
    unittest.main()
