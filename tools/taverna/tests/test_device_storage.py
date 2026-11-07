"""Exercise the device-test storage policy with disposable files.

Discovery checks the storage flow. Direct execution also checks native backup metadata.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'tools/taverna/device_test'
sys.path.insert(0, str(ROOT / 'tools/taverna'))
import ios_session as session


class DeviceStorage(unittest.TestCase):
    backup_mode = "portable"

    @classmethod
    def setUpClass(cls):
        program = r'''
import Foundation

enum Failure: Error { case read, insert, exclude }
let manager = FileManager.default
let base = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true).resolvingSymlinksInPath()
let nativeBackupExclusion = CommandLine.arguments[2] == "native"
let key = Data(repeating: 42, count: 32).base64EncodedString()
let chat = "_chat.db", agent = "_agent.db"
let legacy = base.appendingPathComponent("restored")
try manager.createDirectory(at: legacy, withIntermediateDirectories: false)
let sentinel = Data("fixture-restored-data".utf8)
for suffix in [chat, agent] {
    try sentinel.write(to: legacy.appendingPathComponent("simplex_v1" + suffix))
}

func run(_ name: String, _ files: [String] = [], _ initialKey: String? = nil,
         _ failure: Failure? = nil, invalidPath: String? = nil) throws -> [String: Any] {
    let support = base.appendingPathComponent(name, isDirectory: true)
    let folder = support.appendingPathComponent("InnerMeshDeviceTest/v1", isDirectory: true)
    try manager.createDirectory(at: folder, withIntermediateDirectories: true)
    for suffix in files {
        try Data("fictitious fixture db".utf8).write(to: folder.appendingPathComponent("profile" + suffix))
    }
    if let invalidPath {
        try manager.createSymbolicLink(at: folder.appendingPathComponent("profile" + invalidPath),
                                       withDestinationURL: legacy.appendingPathComponent("simplex_v1" + chat))
    }
    var events: [String] = []
    var opens = 0, sameKey = false, excluded = false, expectedPrefix = false
    var keyStore = initialKey
    do {
        let (prefix, actualKey) = try DeviceTestStorage.location(
            in: support,
            readKey: {
                events.append("read")
                if failure == .read { throw Failure.read }
                return keyStore
            },
            createKey: {
                events.append("insert")
                if failure == .insert { throw Failure.insert }
                keyStore = key
                return key
            },
            excludeFromBackup: { url in
                events.append("exclude")
                if failure == .exclude { throw Failure.exclude }
                if nativeBackupExclusion {
                    try DeviceTestStorage.excludeFromBackup(url)
                }
                excluded = url.path == folder.path
            })
        events.append("open")
        opens += 1
        sameKey = actualKey == key
        expectedPrefix = prefix.path == folder.appendingPathComponent("profile").path
        if nativeBackupExclusion {
            let persisted = try folder.resourceValues(forKeys: [.isExcludedFromBackupKey]).isExcludedFromBackup == true
            excluded = excluded && persisted
        }
        for suffix in [chat, agent] where !manager.fileExists(atPath: prefix.path + suffix) {
            try Data("fictitious new fixture db".utf8).write(to: URL(fileURLWithPath: prefix.path + suffix))
        }
    } catch {
        events.append("blocked")
    }
    return ["events": events, "opens": opens, "sameKey": sameKey, "expectedPrefix": expectedPrefix,
            "excluded": excluded, "dbs": [chat, agent].map {
                manager.fileExists(atPath: folder.appendingPathComponent("profile" + $0).path)
            }]
}
var output: [String: Any] = [:]
output["fresh"] = try run("fresh")
output["existing"] = try run("existing", [chat, agent], key)
output["interrupted"] = try run("interrupted", [], key)
output["onlyChat"] = try run("onlyChat", [chat], key)
output["onlyAgent"] = try run("onlyAgent", [agent], key)
output["symlink"] = try run("symlink", [], key, invalidPath: chat)
output["sidecarSymlink"] = try run("sidecarSymlink", [chat, agent], key, invalidPath: chat + "-wal")
output["missingKey"] = try run("missingKey", [chat, agent])
output["invalidKey"] = try run("invalidKey", [chat, agent], "invalid fixture key")
output["readError"] = try run("readError", [], nil, .read)
output["insertError"] = try run("insertError", [], nil, .insert)
output["backupError"] = try run("backupError", [], nil, .exclude)
output["restoredUnchanged"] = try [chat, agent].allSatisfy {
    try Data(contentsOf: legacy.appendingPathComponent("simplex_v1" + $0)) == sentinel
}
print(String(decoding: try JSONSerialization.data(withJSONObject: output), as: UTF8.self))
'''
        (ROOT / '.build').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='device-storage-', dir=ROOT / '.build') as tmp:
            base = Path(tmp)
            (base / 'main.swift').write_text(program)
            env = session.environment(ROOT)
            build = subprocess.run(
                ['xcrun', 'swiftc', str(SOURCE / 'DeviceTestPolicy.swift'), str(base / 'main.swift'), '-o', str(base / 'probe')],
                env=env, capture_output=True, text=True, timeout=90)
            if build.returncode:
                raise AssertionError(build.stderr)
            run = subprocess.run(
                ['/usr/bin/sandbox-exec', '-p', '(version 1)(allow default)(deny network*)', str(base / 'probe'), tmp, cls.backup_mode],
                env=env, capture_output=True, text=True, timeout=30)
            if run.returncode:
                raise AssertionError(run.stderr)
            cls.rows = json.loads(run.stdout)

    def test_fresh_key_precedes_native_open(self):
        row = self.rows['fresh']
        self.assertEqual(row['events'], ['exclude', 'read', 'insert', 'open'])
        self.assertEqual(row['dbs'], [True, True])
        self.assertEqual(row['opens'], 1)
        self.assertTrue(row['expectedPrefix'])
        self.assertTrue(row['sameKey'])

    def test_existing_pair_reuses_key(self):
        row = self.rows['existing']
        self.assertEqual(row['events'], ['exclude', 'read', 'open'])
        self.assertTrue(row['sameKey'])
        self.assertTrue(row['expectedPrefix'])

    def test_ambiguous_states_block_open(self):
        for name in ('onlyChat', 'onlyAgent', 'symlink', 'sidecarSymlink', 'missingKey', 'invalidKey', 'readError'):
            with self.subTest(name=name):
                row = self.rows[name]
                self.assertEqual(row['opens'], 0)
                self.assertEqual(row['events'][-1], 'blocked')
                self.assertNotIn('insert', row['events'])

    def test_key_insert_failure_prevents_creation(self):
        row = self.rows['insertError']
        self.assertEqual(row['events'], ['exclude', 'read', 'insert', 'blocked'])
        self.assertEqual((row['opens'], row['dbs']), (0, [False, False]))

    def test_interrupted_creation_reuses_key(self):
        row = self.rows['interrupted']
        self.assertEqual(row['events'], ['exclude', 'read', 'open'])
        self.assertEqual(row['dbs'], [True, True])
        self.assertTrue(row['sameKey'])

    def test_restored_files_and_key_are_outside_fixture_operations(self):
        self.assertTrue(self.rows['restoredUnchanged'])
        host = (SOURCE / 'DeviceTestApp.swift').read_text()
        self.assertNotIn('chatMigrateInit(', host)
        self.assertNotIn('dbContainerGroupDefault.set(', host)
        self.assertIn('readKey: DeviceTestDatabaseKey.read', host)
        self.assertIn('createKey: DeviceTestDatabaseKey.create', host)
        keychain = (ROOT / 'apps/ios/SimpleXChat/KeyChain.swift').read_text()
        dedicated = keychain.split('public enum DeviceTestDatabaseKey', 1)[1].split('\n}', 1)[0]
        self.assertIn('"innermesh.deviceTest.v1.databasePassword"', dedicated)
        self.assertEqual(dedicated.count('baseItemQuery(forKey: account)'), 2)
        self.assertIn('status == errSecItemNotFound', dedicated)
        self.assertIn('SecItemCopyMatching(', dedicated)
        self.assertIn('SecItemAdd(', dedicated)
        self.assertIn('kSecAttrAccessible] = ACCESS_POLICY', dedicated)
        self.assertNotIn('SecItemUpdate(', dedicated)
        self.assertNotIn('SecItemDelete(', dedicated)

    def test_backup_exclusion_precedes_open(self):
        for name in ('fresh', 'existing', 'interrupted'):
            with self.subTest(name=name):
                self.assertTrue(self.rows[name]['excluded'])
        self.assertEqual(self.rows['backupError']['events'], ['exclude', 'blocked'])
        self.assertEqual(self.rows['backupError']['opens'], 0)


if __name__ == '__main__':
    # Direct execution exercises the real Foundation backup metadata adapter.
    DeviceStorage.backup_mode = "native"
    unittest.main()
