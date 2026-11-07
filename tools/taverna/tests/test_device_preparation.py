"""Literal technical-host preparation with fictitious persistent core state."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'tools/taverna/device_test'
sys.path.insert(0, str(ROOT / 'tools/taverna'))
import ios_session as session


class LocalProfilePreparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (SOURCE / 'DeviceTestApp.swift').read_text()
        s = cls.source
        work = s[s.index('    private func work('):s.index('    private func command(')]
        command = s[s.index('    private func command('):s.index('    private func json(')]
        prepare = s[s.index('    func prepare()'):s.index('    private func file(')]
        history = s[s.index('    private func readHistory()'):s.index('    func pause()')]
        pause = s[s.index('    func pause()'):s.rindex('\n}')]
        api = (ROOT / 'apps/ios/SimpleXChat/API.swift').read_text()
        migration_types = '\n'.join(re.search(r'public (?:enum|struct) ' + name + r':.*?\n}', api, re.S).group()
                                    for name in ('DBMigrationResult', 'MigrationError', 'UpMigration', 'MTRError'))
        json_method = s[s.index('    private func json('):s.index('    private func openFixtureDatabase(')]
        button = re.search(r'Button\("Atualizar histórico"\).*\.disabled\(([^\n]+)\)', s)
        if not button:
            raise AssertionError('literal refresh button condition not found')
        fixture = (ROOT / 'tests/JSONFixtures.hs').read_text()
        missing = re.search(r'^noActiveUserSwift = (".*")$', fixture, re.MULTILINE)
        if not missing:
            raise AssertionError('upstream missing-user wire fixture not found')
        absent = json.loads(missing.group(1))
        script = 'import Foundation\n' + migration_types + '''\nstruct ImmediateQueue { func async(execute action: () -> Void) { action() } }
enum TavernaCoreTransport { static func stop() {} }
final class FixtureStore {
    var profile: [String: Any]?
    var readMode = "normal", loseCreateReply = false
    var migrationResult: DBMigrationResult = .ok
    var migrations = 0, creations = 0, commands: [String] = []
    var rejected: [String] = [], started = false
    var contacts: [[String: Any]] = []
    init(_ name: String? = nil) {
        if let name { profile = ["userId": Int64(41), "profile": ["displayName": name]] }
    }
}
typealias chat_ctrl = FixtureStore
func sendSimpleXCmdStr(_ text: String, _ controller: chat_ctrl?, retryNum: Int32) -> Data? {
    guard let controller, retryNum == 0 else { return nil }
    return try? controller.reply(text)
}
extension FixtureStore {
    func reply(_ text: String) throws -> Data {
        let store = self
        store.commands.append(text)
        func result(_ tag: String, _ body: [String: Any]) throws -> Data {
            try JSONSerialization.data(withJSONObject: ["result": [tag: body]])
        }
        if text == "/u" {
            if store.readMode == "malformed" { return Data("invalid".utf8) }
            if store.readMode == "unexpected" { return try result("cmdOk", [:]) }
            if store.readMode == "error" {
                return Data(#"{"error":{"errorStore":{"storeError":{"databaseError":{}}}}}"#.utf8)
            }
            if let profile = store.profile { return try result("activeUser", ["user": profile]) }
            return Data(''' + json.dumps(absent) + '''.utf8)
        }
        if text.hasPrefix("/_create user ") {
            let body = try JSONSerialization.jsonObject(with: Data(text.dropFirst("/_create user ".count).utf8)) as! [String: Any]
            store.creations += 1
            store.profile = ["userId": Int64(41), "profile": body["profile"]!]
            if store.loseCreateReply {
                store.loseCreateReply = false
                return Data("invalid".utf8)
            }
            return try result("activeUser", ["user": store.profile!])
        }
        if text == "/contacts" {
            // Same precondition as ListContacts -> withUser in the real core.
            guard store.started else {
                store.rejected.append("chatNotStarted")
                return Data(#"{"error":{"error":{"errorType":{"chatNotStarted":{}}}}}"#.utf8)
            }
            return try result("contactsList", ["contacts": store.contacts])
        }
        if text.hasPrefix("/_get chat ") {
            return try result("apiChat", ["chat": ["chatItems": [
                ["meta": ["itemId": Int64(3)], "content": ["rcvMsgContent": ["msgContent": ["type": "text", "text": "Fixture-03"]]]]
            ]]])
        }
        if text == "/_stop" { store.started = false; return try result("cmdOk", [:]) }
        throw DeviceTestFailure.denied
    }
}
final class Host {
    let store: FixtureStore
    let queue = ImmediateQueue(), gate = DeviceTestGate()
    var controller: chat_ctrl?
    var initialized: Bool { controller != nil }
    var busy = false, prepared = false, connected = false
    var status = "Pronto para preparar o perfil local."
    var preparationDiagnostic: String?
    var storageFailure: DeviceTestStorage.Failure?
    var userID: Int64?, contactID: Int64?, contact = ""
    var history: [DeviceTestHistoryItem] = []
    var historyContainsBatch = false, batchAttempted = false
    init(_ store: FixtureStore) { self.store = store }
    func update(_ action: () -> Void) { action() }
    private func openFixtureDatabase() throws -> (DBMigrationResult, chat_ctrl?) {
        if let storageFailure { throw storageFailure }
        store.migrations += 1
        return (store.migrationResult, store.migrationResult == .ok ? store : nil)
    }
    func attemptCommand() -> Bool { (try? command("/u")) != nil }
''' + work + command + json_method + prepare + history + pause + '''
    func fixtureConnect() throws {
        gate.resume()
        try gate.connect(configure: {}, apply: {}, verify: {}, start: { store.started = true })
        connected = true
    }
}
func refreshDisabled(_ test: Host) -> Bool { ''' + button.group(1) + ''' }
func snapshot(_ test: Host) -> [String: Any] {
    ["prepared": test.prepared, "connected": test.connected, "status": test.status,
     "diagnostic": test.preparationDiagnostic as Any? ?? NSNull(),
     "initialized": test.initialized, "profilePresent": test.store.profile != nil,
     "profileName": (test.store.profile?["profile"] as? [String: Any])?["displayName"] ?? NSNull(),
     "userID": test.userID as Any? ?? NSNull(), "creations": test.store.creations,
     "migrations": test.store.migrations, "commands": test.store.commands,
     "rejected": test.store.rejected, "started": test.store.started,
     "refreshDisabled": refreshDisabled(test), "contactID": test.contactID as Any? ?? NSNull(),
     "history": test.history.map { ["id": $0.id, "text": $0.text, "sent": $0.sent] as [String: Any] }]
}
var output: [String: Any] = [:]
let fresh = Host(FixtureStore()); fresh.prepare(); output["fresh"] = snapshot(fresh)
fresh.prepare(); output["repeat"] = snapshot(fresh)
let reopened = Host(fresh.store); reopened.prepare(); output["reopen"] = snapshot(reopened)
for mode in ["error", "malformed", "unexpected"] {
    let store = FixtureStore("Device-D1"); store.readMode = mode
    let host = Host(store); host.prepare(); output[mode] = snapshot(host)
}
let other = Host(FixtureStore("Fixture-Other")); other.prepare(); output["other"] = snapshot(other)
let failedMigration = FixtureStore(); failedMigration.migrationResult = .errorKeychain
let migration = Host(failedMigration); migration.prepare(); output["migration"] = snapshot(migration)
let secret = "/private/FIXTURE-PATH FIXTURE-KEY FIXTURE-PROFILE"
let failures: [(String, DBMigrationResult)] = [
    ("invalidConfirmation", .invalidConfirmation),
    ("errorNotADatabase", .errorNotADatabase(dbFile: secret)),
    ("errorMigration", .errorMigration(dbFile: secret, migrationError: .upgrade(upMigrations: []))),
    ("errorKeychain", .errorKeychain),
    ("unknown", .unknown(json: secret)),
    ("errorSQL", .errorSQL(dbFile: secret, migrationSQLError: "unstructured error " + secret + " SQLITE_CANTOPEN")),
]
for (key, result) in failures {
    let store = FixtureStore(); store.migrationResult = result
    let host = Host(store); host.prepare(); output[key] = snapshot(host)
}
for (native, code) in [
    ("ErrorCan'tOpen", "CANTOPEN"), ("ErrorPermission", "PERM"), ("ErrorReadOnly", "READONLY"), ("ErrorIO", "IOERR"),
    ("ErrorNotADatabase", "NOTADB"), ("ErrorCorrupt", "CORRUPT"), ("ErrorFull", "FULL"), ("ErrorBusy", "BUSY"),
    ("ErrorLocked", "LOCKED"), ("ErrorAuthorization", "AUTH"),
] {
    let store = FixtureStore()
    store.migrationResult = .errorSQL(dbFile: secret, migrationSQLError: "SQLite3 returned " + native + " while attempting to perform open: " + secret)
    let host = Host(store); host.prepare(); output[code] = snapshot(host)
}
let rawCode = FixtureStore()
rawCode.migrationResult = .errorSQL(dbFile: secret, migrationSQLError: "SQLITE_CANTOPEN")
let rawHost = Host(rawCode); rawHost.prepare(); output["rawCode"] = snapshot(rawHost)
migration.pause(); output["afterPause"] = snapshot(migration)
failedMigration.migrationResult = .ok
migration.prepare(); output["recoveredMigration"] = snapshot(migration)
let unavailable = Host(FixtureStore()); output["uninitializedCommand"] = unavailable.attemptCommand()
let competing = Host(FixtureStore("Other")); let routed = Host(FixtureStore("Device-D1"))
routed.prepare(); _ = competing
output["routedCommand"] = routed.attemptCommand()
output["routed"] = snapshot(routed); output["competing"] = snapshot(competing)
for (name, failure) in [("storage", DeviceTestStorage.Failure.storage), ("dedicatedKey", .keychain)] {
    let blocked = Host(FixtureStore()); blocked.storageFailure = failure; blocked.prepare()
    output[name] = snapshot(blocked)
}
let lostStore = FixtureStore(); lostStore.loseCreateReply = true
let lost = Host(lostStore); lost.prepare(); output["lostReply"] = snapshot(lost)
lost.prepare(); output["retryLostReply"] = snapshot(lost)
let offline = Host(FixtureStore("Device-D1")); offline.prepare()
let before = offline.store.commands.count; offline.refresh()
var offlineState = snapshot(offline)
offlineState["commandsAfterRefresh"] = Array(offline.store.commands.dropFirst(before))
output["offlineRefresh"] = offlineState
let online = Host(FixtureStore("Device-D1")); online.prepare(); try online.fixtureConnect()
online.store.contacts = [["contactId": Int64(77), "localDisplayName": "Fixture-Peer"]]
let connectedButton = refreshDisabled(online)
let start = online.store.commands.count; online.refresh()
var onlineState = snapshot(online)
onlineState["buttonDisabledBeforeRefresh"] = connectedButton
onlineState["commandsAfterRefresh"] = Array(online.store.commands.dropFirst(start))
output["connectedRefresh"] = onlineState
print(String(decoding: try JSONSerialization.data(withJSONObject: output, options: [.sortedKeys]), as: UTF8.self))
'''
        (ROOT / '.build').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='profile-host-', dir=ROOT / '.build') as tmp:
            base = Path(tmp)
            (base / 'main.swift').write_text(script)
            env = session.environment(ROOT)
            compiled = subprocess.run(['xcrun', 'swiftc', str(SOURCE / 'DeviceTestPolicy.swift'), str(base / 'main.swift'), '-o', str(base / 'probe')], capture_output=True, text=True, env=env, timeout=120)
            if compiled.returncode:
                raise AssertionError(compiled.stderr)
            ran = subprocess.run(['/usr/bin/sandbox-exec', '-p', '(version 1)(allow default)(deny network*)', str(base / 'probe')], capture_output=True, text=True, env=env, timeout=30)
            if ran.returncode:
                raise AssertionError(ran.stderr)
            cls.rows = json.loads(ran.stdout)
            evidence = ROOT / '.build/profile-preparation-observations.json'
            evidence.write_text(json.dumps(cls.rows, indent=2) + '\n')

    def test_local_creation_completes_without_history_or_start(self):
        r = self.rows['fresh']
        self.assertEqual((r['prepared'], r['connected'], r['started']), (True, False, False))
        self.assertEqual(r['status'], 'Perfil local preparado. Transporte desconectado.')
        self.assertEqual((r['userID'], r['creations'], r['migrations']), (41, 1, 1))
        self.assertEqual(r['rejected'], [])
        self.assertEqual(r['commands'][0], '/u')
        self.assertEqual(len(r['commands']), 2)
        created = json.loads(r['commands'][1].removeprefix('/_create user '))
        self.assertEqual(created, {'profile': {'displayName': 'Device-D1', 'fullName': ''}, 'pastTimestamp': False, 'userChatRelay': False, 'clientService': False})

    def test_repeated_and_reopened_preparation_reuses_saved_profile(self):
        for name in ('repeat', 'reopen'):
            with self.subTest(name=name):
                r = self.rows[name]
                self.assertEqual((r['prepared'], r['connected'], r['userID']), (True, False, 41))
                self.assertEqual((r['profileName'], r['creations']), ('Device-D1', 1))
                self.assertEqual(r['commands'].count('/u'), 2 if name == 'repeat' else 3)
                self.assertFalse(any(c == '/contacts' or c.startswith('/_start') or c.startswith('/_get chat') for c in r['commands']))

    def test_commands_require_and_use_fixture_controller(self):
        self.assertFalse(self.rows['uninitializedCommand'])
        self.assertTrue(self.rows['routedCommand'])
        self.assertEqual(self.rows['routed']['commands'], ['/u', '/u'])
        self.assertEqual(self.rows['competing']['commands'], [])

    def test_storage_and_key_errors_block_profile_commands(self):
        for name, detail in (('storage', 'Armazenamento do teste indisponível.'),
                             ('dedicatedKey', 'Falha no Keychain.')):
            with self.subTest(name=name):
                row = self.rows[name]
                self.assertEqual(row['diagnostic'], 'Inicialização do banco. ' + detail)
                self.assertEqual((row['initialized'], row['prepared'], row['commands']), (False, False, []))

    def test_unknown_user_queries_never_authorize_creation(self):
        for name in ('error', 'malformed', 'unexpected'):
            with self.subTest(name=name):
                r = self.rows[name]
                self.assertEqual((r['prepared'], r['connected'], r['creations']), (False, False, 0))
                self.assertEqual(r['profileName'], 'Device-D1')
                self.assertEqual(r['commands'], ['/u', '/_stop'])

    def test_migration_and_different_profile_fail_without_overwriting(self):
        m = self.rows['migration']
        self.assertEqual((m['prepared'], m['connected'], m['initialized'], m['profilePresent']), (False, False, False, False))
        self.assertEqual((m['commands'], m['creations']), ([], 0))
        r = self.rows['other']
        self.assertEqual((r['prepared'], r['connected'], r['profileName'], r['creations']), (False, False, 'Fixture-Other', 0))
        self.assertEqual(r['commands'], ['/u', '/_stop'])

    def test_lost_creation_reply_recovery_preserves_the_saved_profile(self):
        first, retried = self.rows['lostReply'], self.rows['retryLostReply']
        self.assertEqual((first['prepared'], first['profilePresent'], first['creations']), (False, True, 1))
        self.assertEqual((retried['prepared'], retried['connected'], retried['userID']), (True, False, 41))
        self.assertEqual((retried['profileName'], retried['creations'], retried['migrations']), ('Device-D1', 1, 1))
        self.assertEqual(retried['commands'][-1], '/u')

    def test_database_failure_reports_category_and_only_supported_sqlite_code(self):
        cases = {
            'invalidConfirmation': 'Confirmação de migração inválida.',
            'errorNotADatabase': 'Arquivo incompatível com o banco.',
            'errorMigration': 'Falha de migração.',
            'errorSQL': 'Falha SQLite.',
            'errorKeychain': 'Falha no Keychain.',
            'unknown': 'Retorno do banco não reconhecido.',
        }
        codes = ('CANTOPEN', 'PERM', 'READONLY', 'IOERR', 'NOTADB', 'CORRUPT', 'FULL', 'BUSY', 'LOCKED', 'AUTH')
        cases.update({code: f'Falha SQLite (SQLITE_{code}).' for code in codes})
        cases['rawCode'] = 'Falha SQLite (SQLITE_CANTOPEN).'
        for case, detail in cases.items():
            with self.subTest(case=case):
                row = self.rows[case]
                self.assertEqual(row['diagnostic'], f'Inicialização do banco. {detail}')
                self.assertEqual((row['initialized'], row['prepared'], row['commands']), (False, False, []))

    def test_post_initialization_failure_reports_actual_stage(self):
        self.assertEqual(self.rows['error']['diagnostic'], 'Consulta do perfil. Falha na preparação local.')
        self.assertEqual(self.rows['lostReply']['diagnostic'], 'Criação do perfil. Falha na preparação local.')
        self.assertEqual(self.rows['other']['diagnostic'], 'Validação do perfil. Falha na preparação local.')
        self.assertEqual(self.rows['error']['commands'], ['/u', '/_stop'])
        self.assertEqual(self.rows['lostReply']['creations'], 1)
        self.assertEqual(self.rows['other']['creations'], 0)

    def test_screen_exposes_only_sanitized_diagnostic(self):
        self.assertRegex(self.source, r'if let diagnostic = test.preparationDiagnostic \{ Text\(diagnostic\) \}\s+Button\("Preparar perfil local"')
        for case in ('errorNotADatabase', 'errorMigration', 'unknown', 'errorSQL', 'CANTOPEN'):
            text = self.rows[case]['diagnostic']
            for token in ('FIXTURE-PATH', 'FIXTURE-KEY', 'FIXTURE-PROFILE', 'sqlErrorDetails'):
                self.assertNotIn(token, text)
        self.assertEqual(self.rows['CANTOPEN']['diagnostic'], 'Inicialização do banco. Falha SQLite (SQLITE_CANTOPEN).')

    def test_pause_retains_last_preparation_diagnostic(self):
        row = self.rows['afterPause']
        self.assertEqual(row['status'], 'Teste pausado. Reconecte para continuar.')
        self.assertEqual(row['diagnostic'], 'Inicialização do banco. Falha no Keychain.')

    def test_success_preserves_copy_and_clears_diagnostic(self):
        row = self.rows['recoveredMigration']
        self.assertEqual(row['status'], 'Perfil local preparado. Transporte desconectado.')
        self.assertEqual((row['diagnostic'], row['prepared'], row['connected']), (None, True, False))

    def test_history_requires_connection_and_preserves_exact_bound(self):
        offline = self.rows['offlineRefresh']
        self.assertTrue(offline['refreshDisabled'])
        self.assertEqual(offline['commandsAfterRefresh'], ['/_stop'])
        self.assertEqual(offline['rejected'], [])
        connected = self.rows['connectedRefresh']
        self.assertFalse(connected['buttonDisabledBeforeRefresh'])
        self.assertEqual(connected['commandsAfterRefresh'], ['/contacts', '/_get chat @77 count=100'])
        self.assertEqual(connected['contactID'], 77)
        self.assertEqual(connected['history'], [{'id': 3, 'text': 'Fixture-03', 'sent': False}])


if __name__ == '__main__':
    unittest.main()
