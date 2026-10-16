"""IOS-04/05/10/15: session ownership and fail-closed preparation."""
import importlib.util
import errno
import json
from pathlib import Path
import plistlib
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('ios_session', ROOT / 'tools/taverna/ios_session.py')
session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session)


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'worktree'
        self.root.mkdir()
        self.udid = '00000000-0000-0000-0000-000000000001'
        storage = self.root / '.build/SimulatorDevices' / self.udid
        (storage / 'data').mkdir(parents=True)
        (storage / 'device.plist').write_bytes(plistlib.dumps({'UDID': self.udid}))
        logs = self.root / '.build/SimulatorLogs' / self.udid
        logs.mkdir(parents=True)
        index = self.base / 'device-index' / self.udid
        index.parent.mkdir()
        index.symlink_to(storage)
        log_index = self.base / 'log-index' / self.udid
        log_index.parent.mkdir()
        log_index.symlink_to(logs)
        self.record = dict(owner='test', worktree=str(self.root), udid=self.udid,
                           storage=str(storage), logs=str(logs), index=str(index),
                           log_index=str(log_index))

    def test_owned_device_and_local_physical_storage_accepted(self):
        session.validate_session(self.root, self.record, self.udid)
        self.assertEqual(Path(self.record['index']).resolve(), Path(self.record['storage']))

    def test_foreign_xcode_destination_rejected(self):
        with self.assertRaisesRegex(ValueError, 'destination'):
            session.validate_session(self.root, self.record, 'foreign')

    def test_storage_outside_worktree_rejected(self):
        outside = self.base / 'other-device'
        outside.mkdir()
        self.record['storage'] = str(outside)
        with self.assertRaisesRegex(ValueError, 'worktree'):
            session.validate_session(self.root, self.record, self.udid)

    def test_redirected_index_rejected(self):
        index = Path(self.record['index'])
        index.unlink()
        other = self.root / '.build/other'
        other.mkdir()
        index.symlink_to(other)
        with self.assertRaisesRegex(ValueError, 'index'):
            session.validate_session(self.root, self.record, self.udid)

    def test_sdk_standard_indexes_required(self):
        record = dict(self.record,
            index=str(self.base / 'Library/Developer/CoreSimulator/Devices' / self.udid),
            log_index=str(self.base / 'Library/Logs/CoreSimulator' / self.udid))
        session.validate_sdk_indexes(record, self.base)
        record['index'] = str(self.base / 'private-set' / self.udid)
        with self.assertRaisesRegex(ValueError, 'standard SDK index'):
            session.validate_sdk_indexes(record, self.base)

    def test_logs_outside_worktree_rejected(self):
        self.record['logs'] = str(self.base)
        with self.assertRaisesRegex(ValueError, 'worktree'):
            session.validate_session(self.root, self.record, self.udid)

    def test_device_identity_mismatch_rejected(self):
        (Path(self.record['storage']) / 'device.plist').write_bytes(plistlib.dumps({'UDID': 'other'}))
        with self.assertRaisesRegex(ValueError, 'identity'):
            session.validate_session(self.root, self.record, self.udid)

    def test_missing_or_changed_guard_rejected(self):
        binary = self.root / '.build/helper'
        binary.write_bytes(b'qualified helper')
        manifest = {str(binary): session.sha256(binary)}
        session.validate_guard(self.root, manifest)
        binary.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'hash'):
            session.validate_guard(self.root, manifest)
        binary.unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            session.validate_guard(self.root, manifest)

    def test_attempts_preserved_and_cannot_overwrite(self):
        attempt = session.new_attempt(self.root, 'first')
        (attempt / 'evidence').write_text('keep')
        with self.assertRaises(FileExistsError):
            session.new_attempt(self.root, 'first')
        second = session.new_attempt(self.root, 'second')
        self.assertNotEqual(attempt, second)
        self.assertEqual((attempt / 'evidence').read_text(), 'keep')

    def test_attempt_path_escape_rejected(self):
        with self.assertRaisesRegex(ValueError, 'attempt'):
            session.new_attempt(self.root, '../other')

    def test_guard_proof_requires_both_denials_and_local_connection(self):
        path = self.root / 'guard.jsonl'
        valid = dict(pid=42, executable='SimpleX', phase='before_main',
                     ipv4_errno=1, ipv6_errno=13, loopback=True)
        path.write_text(json.dumps(valid) + '\n')
        proof = session.guard_proof(path, 42)
        self.assertEqual(proof['pid'], 42)
        self.assertEqual(proof['executable'], 'SimpleX')
        self.assertEqual(proof['phase'], 'before_main')
        self.assertEqual(proof['ipv4_errno'], errno.EPERM)
        self.assertEqual(proof['ipv6_errno'], errno.EACCES)
        self.assertIs(proof['loopback'], True)
        for field, value in [('ipv4_errno', 36), ('ipv6_errno', 0), ('loopback', False), ('pid', 99)]:
            bad = dict(valid, **{field: value})
            path.write_text(json.dumps(bad) + '\n')
            with self.assertRaisesRegex(ValueError, 'containment'):
                session.guard_proof(path, 42)
