"""IOS-01/02/07/09/15: fixed native bytes, confined extraction and payload."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import struct
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/taverna'))
spec = importlib.util.spec_from_file_location('ios_native', ROOT / 'tools/taverna/ios_native.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


def object_bytes(platform=7, cpu=16777228, legacy=False):
    segment = struct.pack('<II16sQQQQIIII', 0x19, 72, b'', 0, 16, 256, 16, 7, 7, 0, 0)
    version = (struct.pack('<4I', 0x25, 16, 11 << 16, 0) if legacy else
               struct.pack('<6I', 0x32, 24, platform, 11 << 16, 0, 0))
    commands = segment + version
    header = struct.pack('<8I', 0xfeedfacf, cpu, 0, 1, 2, len(commands), 0, 0)
    return (header + commands).ljust(256, b'\0') + b'unchanged-code!!'


def archive(entries):
    data = b'!<arch>\n'
    for name, body in entries:
        encoded = name.encode()
        body = encoded + body
        header = f'{"#1/" + str(len(encoded)):<16}{0:<12}{0:<6}{0:<6}{"644":<8}{len(body):<10}`\n'.encode()
        data += header + body + (b'\n' if len(body) % 2 else b'')
    return data


class NativeTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / '.build/test-temp'
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_all_archive_members_including_duplicate_names_preserved(self):
        raw = archive([('duplicate-long-name.o', object_bytes()),
                       ('duplicate-long-name.o', object_bytes())])
        items = native.members(raw)
        self.assertEqual([n for n, _ in items], ['duplicate-long-name.o'] * 2)
        self.assertEqual([b for _, b in items], [object_bytes()] * 2)
        self.assertEqual(native.inspect_archive(raw)['objects'], 2)

    def test_archive_truncation_and_unsafe_member_rejected(self):
        raw = archive([('entry.o', object_bytes())])
        for bad in (raw[:7], raw[:-5], archive([('../entry.o', object_bytes())])):
            with self.subTest(bytes=len(bad)), self.assertRaises(ValueError):
                native.members(bad)

    def test_real_object_platform_required_not_just_arm64(self):
        for platform, cpu in ((2, 16777228), (1, 16777228), (7, 16777223)):
            with self.subTest(platform=platform, cpu=cpu), self.assertRaisesRegex(ValueError, 'arm64.*Simulator'):
                native.inspect_archive(archive([('entry.o', object_bytes(platform, cpu))]))
        with self.assertRaisesRegex(ValueError, 'arm64.*Simulator'):
            native.inspect_archive(archive([('entry.o', object_bytes(legacy=True))]))

    def test_platform_retag_preserves_code_symbols_offsets_and_minimum_sdk(self):
        before = object_bytes(legacy=True)
        after = object_bytes(platform=7)
        native.require_preserved(before, after)
        self.assertEqual(native.macho(after)['platforms'], [7])
        self.assertEqual(native.invariant(before), native.invariant(after))
        changed = bytearray(after)
        changed[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'payload'):
            native.require_preserved(before, changed)
        changed = bytearray(after)
        struct.pack_into('<I', changed, 32 + 72 + 12, 12 << 16)
        with self.assertRaisesRegex(ValueError, 'payload'):
            native.require_preserved(before, changed)

    def test_header_and_non_version_commands_cannot_change(self):
        before = object_bytes(legacy=True)
        for offset in (24, 32 + 56):
            changed = bytearray(object_bytes())
            changed[offset] ^= 1
            with self.subTest(offset=offset), self.assertRaisesRegex(ValueError, 'payload'):
                native.require_preserved(before, changed)

    def test_malformed_or_missing_load_commands_rejected(self):
        for raw in (object_bytes()[:50], b'not macho', struct.pack('<8I', 0xfeedfacf, 16777228, 0, 1, 0, 0, 0, 0)):
            with self.subTest(length=len(raw)), self.assertRaises(ValueError):
                native.macho(raw)

    def make_zip(self, entries):
        path = self.root / 'input.zip'
        with zipfile.ZipFile(path, 'w') as z:
            for name, data in entries:
                z.writestr(name, data)
        return path

    def test_zip_only_extracts_fixed_set_and_checks_hashes(self):
        data = archive([('entry.o', object_bytes())])
        path = self.make_zip([('one.a', data)])
        expected = dict(bundle_sha256=native.sha256(path), bundle_bytes=path.stat().st_size,
                        libraries=[dict(name='one.a', original_sha256=hashlib.sha256(data).hexdigest())])
        destination = self.root / 'original'
        native.extract_bundle(path, destination, expected)
        self.assertEqual((destination / 'one.a').read_bytes(), data)
        with self.assertRaises(FileExistsError):
            native.extract_bundle(path, destination, expected)
        wrong = dict(expected, bundle_sha256='0' * 64)
        with self.assertRaisesRegex(ValueError, 'bundle hash'):
            native.extract_bundle(path, self.root / 'bad', wrong)

    def test_zip_escape_link_duplicates_and_expansion_limit_rejected(self):
        symlink = zipfile.ZipInfo('one.a'); symlink.create_system = 3
        symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
        entries = [[('../one.a', b'bad')], [('one.a', b'a'), ('one.a', b'b')], [(symlink, b'target')]]
        for i, group in enumerate(entries):
            path = self.make_zip(group)
            expected = dict(bundle_sha256=native.sha256(path), bundle_bytes=path.stat().st_size,
                            libraries=[dict(name='one.a', original_sha256='0' * 64)])
            with self.subTest(case=i), self.assertRaises(ValueError):
                native.extract_bundle(path, self.root / f'bad{i}', expected)
        path = self.make_zip([('one.a', b'123456789')])
        expected.update(bundle_sha256=native.sha256(path), bundle_bytes=path.stat().st_size)
        with self.assertRaisesRegex(ValueError, 'limit'):
            native.extract_bundle(path, self.root / 'large', expected, max_bytes=5)

    def test_unknown_source_or_changed_locks_rejected(self):
        manifest = json.loads((ROOT / '.specs/features/ios-first-build/native-inputs.json').read_text())
        native.validate_manifest(ROOT, manifest)
        for field in ('upstream_commit', 'flake_lock_sha256', 'cabal_project_sha256', 'swiftpm_lock_sha256'):
            bad = copy.deepcopy(manifest); bad[field] = '0' * 64
            with self.subTest(field=field), self.assertRaises(ValueError):
                native.validate_manifest(ROOT, bad)

    def test_expired_preparation_budget_rejected_before_tool_call(self):
        with self.assertRaisesRegex(ValueError, 'timeout'):
            native.remaining(0, 30)

    def test_library_actual_hash_count_and_platform_required(self):
        data = archive([('entry.o', object_bytes())]); path = self.root / 'one.a'; path.write_bytes(data)
        record = dict(name='one.a', sha256=native.sha256(path), objects=1)
        native.validate_library(path, record)
        for field, value in [('sha256', '0' * 64), ('objects', 0)]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                native.validate_library(path, dict(record, **{field: value}))
        path.write_bytes(archive([('entry.o', object_bytes(platform=2))]))
        with self.assertRaisesRegex(ValueError, 'Simulator'):
            native.validate_library(path, dict(record, sha256=native.sha256(path)))


if __name__ == '__main__':
    unittest.main()
