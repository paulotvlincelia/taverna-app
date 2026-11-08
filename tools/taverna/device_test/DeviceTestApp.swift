// Original plain foreground test interface, AGPLv3. No inherited graphic design.
import SwiftUI
import UIKit
import Foundation
import Security
import CryptoKit
import SimpleXChat

@main
struct DeviceTestApp: App {
    @StateObject private var test = DeviceTestSession()
    @Environment(\.scenePhase) private var scenePhase
    init() {
        DispatchQueue.global(qos: .background).sync { haskell_init() }
        registerGroupDefaults()
    }
    var body: some Scene {
        WindowGroup {
            NavigationView {
                Form {
                    Section("InnerMesh Test") {
                        Text("Perfil fictício: Device-D1")
                        Text(test.status)
                        if let diagnostic = test.preparationDiagnostic { Text(diagnostic) }
                        Button("Preparar perfil local") { test.prepare() }.disabled(test.busy || test.prepared)
                        Button("Conectar ao teste privado") { test.connect() }.disabled(test.busy || !test.prepared || test.connected)
                    }
                    Section("Conversa de teste") {
                        Button("Criar convite para o segundo cliente") { test.invite() }.disabled(!test.connected || test.busy)
                        if !test.invitation.isEmpty { Text(test.invitation).textSelection(.enabled) }
                        Text(test.contact)
                        Button("Enviar 10 textos fictícios") { test.sendBatch() }.disabled(!test.connected || test.busy || test.batchAttempted || test.contact.isEmpty)
                        Button("Atualizar histórico") { test.refresh() }.disabled(!test.connected || test.busy)
                        Text("Mensagens no histórico: \(test.history.count)")
                        ForEach(test.history) { item in
                            Text("\(item.sent ? "→" : "←") \(item.text)")
                        }
                    }
                    Section("Teste técnico") {
                        Text("Use apenas o perfil e os textos fictícios deste ensaio. Mantenha o app aberto durante a troca.")
                        Text("Código baseado no SimpleX Chat sob AGPLv3; variante independente. Ícone e tela de teste próprios.")
                    }
                }.navigationTitle("InnerMesh Test")
            }.onChange(of: scenePhase) { phase in
                if phase != .active { test.pause() }
            }
        }
    }
}

final class DeviceTestSession: ObservableObject {
    @Published private(set) var status = "Pronto para preparar o perfil local."
    @Published private(set) var preparationDiagnostic: String?
    @Published private(set) var prepared = false
    @Published private(set) var connected = false
    @Published private(set) var busy = false
    @Published private(set) var invitation = ""
    @Published private(set) var contact = ""
    @Published private(set) var history: [DeviceTestHistoryItem] = []
    @Published private(set) var batchAttempted = false
    private let queue = DispatchQueue(label: "innermesh.device-test")
    private let gate = DeviceTestGate()
    private let messages = DeviceTestMessages()
    private var userID: Int64?
    private var contactID: Int64?
    private var controller: chat_ctrl?
    private var initialized: Bool { controller != nil }
    private var historyContainsBatch = false

    private func update(_ action: @escaping () -> Void) { DispatchQueue.main.async(execute: action) }
    private func work(
        failureStatus: String = "Teste bloqueado. Confira a configuração, autorização e rede da fixture.",
        _ action: @escaping () throws -> Void
    ) {
        busy = true
        queue.async {
            do { try action() }
            catch {
                self.gate.pause(); TavernaCoreTransport.stop()
                if self.initialized { _ = try? self.command("/_stop") }
                self.update { self.connected = false; self.status = failureStatus }
            }
            self.update { self.busy = false }
        }
    }
    private func command(_ text: String) throws -> DeviceTestResponse {
        guard let controller, let data = sendSimpleXCmdStr(text, controller, retryNum: 0) else {
            throw DeviceTestFailure.response
        }
        return try DeviceTestResponse(data)
    }
    private func json(_ value: Any) throws -> String {
        String(decoding: try JSONSerialization.data(withJSONObject: value, options: [.sortedKeys]), as: UTF8.self)
    }
    private func openFixtureDatabase() throws -> (DBMigrationResult, chat_ctrl?) {
        let support = try FileManager.default.url(for: .applicationSupportDirectory, in: .userDomainMask,
                                                  appropriateFor: nil, create: true)
        let (prefix, key) = try DeviceTestStorage.location(
            in: support, readKey: DeviceTestDatabaseKey.read, createKey: DeviceTestDatabaseKey.create)
        return chatInitDeviceTestDatabase(url: prefix, key: key)
    }
    func prepare() {
        work(failureStatus: "Preparação local bloqueada.") {
            if !self.initialized {
                let (result, controller): (DBMigrationResult, chat_ctrl?)
                do {
                    (result, controller) = try self.openFixtureDatabase()
                } catch DeviceTestStorage.Failure.keychain {
                    self.update { self.preparationDiagnostic = "Inicialização do banco. Falha no Keychain." }
                    throw DeviceTestFailure.configuration
                } catch {
                    self.update { self.preparationDiagnostic = "Inicialização do banco. Armazenamento do teste indisponível." }
                    throw DeviceTestFailure.configuration
                }
                if let failure = self.databaseFailure(result) {
                    self.update { self.preparationDiagnostic = "Inicialização do banco. " + failure }
                    throw DeviceTestFailure.configuration
                }
                guard let controller else {
                    self.update { self.preparationDiagnostic = "Inicialização do banco. Controlador indisponível." }
                    throw DeviceTestFailure.configuration
                }
                self.controller = controller
            }
            var stage = "Consulta do perfil"
            do {
                let active: [String: Any]
                do {
                    active = try self.command("/u").require("activeUser")
                } catch DeviceTestFailure.noActiveUser {
                    stage = "Criação do perfil"
                    active = try self.command("/_create user " + self.json(["profile": ["displayName": "Device-D1", "fullName": ""], "pastTimestamp": false, "userChatRelay": false, "clientService": false])).require("activeUser")
                }
                stage = "Validação do perfil"
                guard let user = active["user"] as? [String: Any],
                      let id = user["userId"] as? Int64,
                      let profile = user["profile"] as? [String: Any], profile["displayName"] as? String == "Device-D1" else { throw DeviceTestFailure.configuration }
                self.userID = id
                self.update {
                    self.preparationDiagnostic = nil
                    self.prepared = true
                    self.status = "Perfil local preparado. Transporte desconectado."
                }
            } catch {
                let diagnostic = stage + ". Falha na preparação local."
                self.update { self.preparationDiagnostic = diagnostic }
                throw error
            }
        }
    }

    private func databaseFailure(_ result: DBMigrationResult) -> String? {
        switch result {
        case .ok: return nil
        case .invalidConfirmation: return "Confirmação de migração inválida."
        case .errorNotADatabase: return "Arquivo incompatível com o banco."
        case .errorMigration: return "Falha de migração."
        case .errorKeychain: return "Falha no Keychain."
        case .unknown: return "Retorno do banco não reconhecido."
        case let .errorSQL(_, detail):
            let codes = [
                "ErrorCan'tOpen": "SQLITE_CANTOPEN", "ErrorPermission": "SQLITE_PERM",
                "ErrorReadOnly": "SQLITE_READONLY", "ErrorIO": "SQLITE_IOERR",
                "ErrorNotADatabase": "SQLITE_NOTADB", "ErrorCorrupt": "SQLITE_CORRUPT",
                "ErrorFull": "SQLITE_FULL", "ErrorBusy": "SQLITE_BUSY",
                "ErrorLocked": "SQLITE_LOCKED", "ErrorAuthorization": "SQLITE_AUTH",
            ]
            // direct-sqlcipher prints the error code before the operation and details.
            let prefix = "SQLite3 returned "
            let tag = detail.hasPrefix(prefix) ? detail.dropFirst(prefix.count).prefix { $0 != " " } : Substring(detail)
            if let code = codes[String(tag)] ?? codes.values.first(where: { $0 == tag }) {
                return "Falha SQLite (" + code + ")."
            }
            return "Falha SQLite."
        }
    }

    private func file(_ name: String, limit: Int, digest: String? = nil) throws -> Data {
        guard ["config.json", "device.p12", "ca.der"].contains(name) else { throw DeviceTestFailure.configuration }
        let documents = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].resolvingSymlinksInPath()
        let directory = documents.appendingPathComponent("DeviceTest", isDirectory: true)
        let url = directory.appendingPathComponent(name)
        guard directory.resolvingSymlinksInPath() == directory,
              url.resolvingSymlinksInPath() == url else { throw DeviceTestFailure.configuration }
        let values = try url.resourceValues(forKeys: [.isRegularFileKey, .isSymbolicLinkKey, .fileSizeKey])
        guard values.isRegularFile == true, values.isSymbolicLink != true,
              let size = values.fileSize, size > 0, size <= limit else { throw DeviceTestFailure.configuration }
        let body = try Data(contentsOf: url)
        guard body.count <= limit else { throw DeviceTestFailure.configuration }
        if let digest {
            let actual = SHA256.hash(data: body).map { String(format: "%02x", $0) }.joined()
            guard actual == digest else { throw DeviceTestFailure.configuration }
        }
        return body
    }
    func connect() {
        guard UIApplication.shared.applicationState == .active else { return }
        gate.resume()
        work {
            guard let id = self.userID else { throw DeviceTestFailure.denied }
            let cfg = try DeviceTestConfiguration.decode(self.file("config.json", limit: 4096))
            let server = cfg.canonicalSMPServer
            let p12 = try self.file("device.p12", limit: 65536, digest: cfg.identitySHA256)
            let der = try self.file("ca.der", limit: 16384, digest: cfg.anchorSHA256)
            var items: CFArray?
            guard SecPKCS12Import(p12 as CFData, [kSecImportExportPassphrase as String: "fixture-only"] as CFDictionary, &items) == errSecSuccess,
                  let first = (items as? [[String: Any]])?.first,
                  let object = first[kSecImportItemIdentity as String],
                  let anchor = SecCertificateCreateWithData(nil, der as CFData) else { throw DeviceTestFailure.configuration }
            let identity = object as! SecIdentity
            try self.gate.connect(configure: {
                let ready = DispatchSemaphore(value: 0)
                var result: Result<Void, Error>?
                TavernaCoreTransport.configure(routes: [
                    .init(host: "relay.test", port: 5223, gatewayHost: cfg.gatewayHost, gatewayPort: cfg.smpPort, gatewayName: cfg.serverName)
                ], anchor: anchor, identity: identity, singleSMP: true) { result = $0; ready.signal() }
                guard ready.wait(timeout: .now() + 10) == .success, let result else { throw DeviceTestFailure.denied }
                try result.get()
            }, apply: {
                try TavernaCoreTransport.withNetworkConfig(NetCfg.defaults) { network in
                    _ = try self.command("/_network " + self.json(try JSONSerialization.jsonObject(with: JSONEncoder().encode(network)))).require("cmdOk")
                }
                _ = try self.command("/_device_test_smp \(id) \(server)").require("deviceTestSMP")
            }, verify: {
                let readback = try self.command("/network").require("networkConfig")
                guard let network = readback["networkConfig"] as? [String: Any] else { throw DeviceTestFailure.response }
                let expected = try TavernaCoreTransport.networkConfig(NetCfg.defaults)
                try DeviceTestServers.verifyNetwork(network, proxy: expected.socksProxy)
                try self.verifyServers(id: id, server: server)
            }, start: {
                try TavernaCoreTransport.withNetworkConfig(NetCfg.defaults) { _ in
                    let response = try self.command("/_start main=on snd_files=off")
                    guard response.tag == "chatStarted" || response.tag == "chatRunning" else { throw DeviceTestFailure.response }
                }
            })
            self.update {
                self.connected = self.gate.ready
                if self.connected { self.status = "Transporte configurado. Conecte o segundo cliente para testar a entrega." }
            }
            try self.readHistory()
        }
    }
    private func verifyServers(id: Int64, server: String) throws {
        let body = try command("/_device_test_smp \(id)").require("deviceTestSMP")
        try DeviceTestServers.verify(body, server: server)
    }
    func invite() {
        work {
            try self.gate.perform {
                guard let id = self.userID else { throw DeviceTestFailure.denied }
                let body = try self.command("/_connect \(id)").require("invitation")
                guard let link = body["connLinkInvitation"] as? [String: Any], let text = link["connFullLink"] as? String else { throw DeviceTestFailure.response }
                self.update { self.invitation = text }
            }
        }
    }
    func sendBatch() {
        batchAttempted = true
        work {
            try self.gate.perform {
                try self.readHistory()
                guard let id = self.contactID, !self.historyContainsBatch else { throw DeviceTestFailure.denied }
                try self.messages.send { text in
                    try self.gate.perform {
                        let body = [["msgContent": ["type": "text", "text": text], "mentions": [:]]]
                        _ = try self.command("/_send @\(id) live=off ttl=default sign=off json " + self.json(body)).require("newChatItems")
                    }
                }
                try self.readHistory()
            }
        }
    }
    private func readHistory() throws {
        let body = try command("/contacts").require("contactsList")
        guard let contacts = body["contacts"] as? [[String: Any]] else { throw DeviceTestFailure.response }
        guard contacts.count <= 1 else { throw DeviceTestFailure.denied }
        guard let peer = contacts.first else { contactID = nil; return }
        guard let id = peer["contactId"] as? Int64, let name = peer["localDisplayName"] as? String else { throw DeviceTestFailure.response }
        contactID = id
        let rows = try command("/_get chat @\(id) count=100").history()
        historyContainsBatch = rows.contains { $0.sent && DeviceTestMessages.texts.contains($0.text) }
        self.update { self.contact = name; self.history = rows; self.batchAttempted = self.batchAttempted || self.historyContainsBatch }
    }
    func refresh() { work { guard self.initialized else { throw DeviceTestFailure.denied }; try self.gate.perform { try self.readHistory() } } }
    func pause() {
        gate.pause()
        connected = false
        TavernaCoreTransport.stop()
        queue.async {
            if self.initialized { _ = try? self.command("/_stop") }
            self.update { self.status = "Teste pausado. Reconecte para continuar." }
        }
    }
}
