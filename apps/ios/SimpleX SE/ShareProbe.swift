import Foundation
import SimpleXChat
import Security

#if DEBUG && targetEnvironment(simulator)
// Selected only by the before-main guard for a worktree-owned simulator fixture.
enum ShareProbe {
    private enum Failure: Error { case assertion(String), configuration }
    private struct Configuration: Decodable {
        let identity: String, anchor: String, smpServer: String, xftpServer: String
        let smpPort: UInt16, xftpPort: UInt16, sentinelPort: UInt16
    }
    static func startIfRequested(completion: @escaping () -> Void) -> Bool {
        guard let path = ProcessInfo.processInfo.environment["TAVERNA_SHARE_PROBE"] else { return false }
        DispatchQueue.global().async {
            run(path)
            DispatchQueue.main.async(execute: completion)
        }
        return true
    }
    private static func run(_ path: String) {
        var checks: [String] = []
        let directory = URL(fileURLWithPath: path).deletingLastPathComponent()
        let output = directory.appendingPathComponent("share-result.json")
        guard !FileManager.default.fileExists(atPath: output.path) else { return }
        func require(_ value: Bool, _ label: String) throws {
            guard value else { throw Failure.assertion(label) }; checks.append(label)
        }
        func raw(_ command: String) throws -> [String: Any] {
            guard let data = sendSimpleXCmdStr(command, retryNum: 0),
                  let value = try JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let result = value["result"] as? [String: Any] else { throw Failure.assertion("core_response") }
            return result
        }
        func networkBody() throws -> [String: Any] {
            guard let body = try raw("/network")["networkConfig"] as? [String: Any],
                  let network = body["networkConfig"] as? [String: Any] else { throw Failure.assertion("network_readback") }
            return network
        }
        func actual() throws -> NetCfg {
            try JSONDecoder().decode(NetCfg.self, from: JSONSerialization.data(withJSONObject: networkBody()))
        }
        func stopped() throws -> Bool { try raw("/_check running")["chatStopped"] != nil }
        func record(_ status: String, _ failure: String? = nil) {
            var value: [String: Any] = ["status": status, "checks": checks,
                "process": ProcessInfo.processInfo.processName, "pid": ProcessInfo.processInfo.processIdentifier]
            value["failure"] = failure
            if let data = try? JSONSerialization.data(withJSONObject: value, options: [.sortedKeys]) {
                try? data.write(to: output, options: .atomic)
            }
        }
        if ProcessInfo.processInfo.environment["TAVERNA_SHARE_DISCOVERY"] == "1" {
            checks.append("view_did_load_without_core")
            record("UI_CONTROL_ONLY")
            return
        }
        do {
            let cfg = try JSONDecoder().decode(Configuration.self, from: Data(contentsOf: URL(fileURLWithPath: path)))
            let fixture = directory.deletingLastPathComponent().path + "/"
            guard [cfg.identity, cfg.anchor].allSatisfy({ URL(fileURLWithPath: $0).resolvingSymlinksInPath().path.hasPrefix(fixture) }) else { throw Failure.configuration }
            registerGroupDefaults()
            // Only the fresh worktree-owned fixture database is used.
            dbContainerGroupDefault.set(.documents)
            storeDBPassphraseGroupDefault.set(false)
            let model = ShareModel()
            try require(model.initChat(with: "fixture-only-passphrase") != nil && !hasChatCtrl(), "no_controller_without_transport")
            haskell_init_se()
            let db = getAppDatabasePath()
            guard !hasDatabase() else { throw Failure.assertion("database_must_be_new") }
            let (_, seeded) = chatInitTemporaryDatabase(url: db, key: "fixture-only-passphrase")
            guard let seeded else { throw Failure.assertion("seed_database") }
            guard sendSimpleXCmdStr("/_create user {\"profile\":{\"displayName\":\"Share-proof\",\"fullName\":\"\"},\"pastTimestamp\":false}", seeded, retryNum: 0) != nil else { throw Failure.assertion("seed_user") }
            _ = chat_close_store(seeded)
            let (_, migration) = chatMigrateInit("fixture-only-passphrase")
            guard migration == .ok else { throw Failure.assertion("database") }
            do { _ = try apiStartChat(); throw Failure.assertion("missing_start") }
            catch TavernaCoreTransport.Failure.notReady { checks.append("missing_start_denied") }
            do { try apiActivateChat(); throw Failure.assertion("missing_resume") }
            catch TavernaCoreTransport.Failure.notReady { checks.append("missing_resume_denied") }
            try require(try stopped(), "core_still_stopped")
            chatCloseStore(); resetChatCtrl()
            var items: CFArray?
            guard SecPKCS12Import(try Data(contentsOf: URL(fileURLWithPath: cfg.identity)) as CFData,
                [kSecImportExportPassphrase as String: "fixture-only"] as CFDictionary, &items) == errSecSuccess,
                let first = (items as? [[String: Any]])?.first, let value = first[kSecImportItemIdentity as String],
                let anchor = SecCertificateCreateWithData(nil, try Data(contentsOf: URL(fileURLWithPath: cfg.anchor)) as CFData) else { throw Failure.configuration }
            let ready = DispatchSemaphore(value: 0)
            var configured: Result<Void, Error>?
            TavernaCoreTransport.configure(routes: [
                .init(host: "relay.test", port: 5223, gatewayHost: "127.0.0.1", gatewayPort: cfg.smpPort, gatewayName: "gateway.test"),
                .init(host: "relay.test", port: 8443, gatewayHost: "127.0.0.1", gatewayPort: cfg.xftpPort, gatewayName: "gateway.test")],
                anchor: anchor, identity: value as! SecIdentity) { configured = $0; ready.signal() }
            guard ready.wait(timeout: .now()+10) == .success, let configured else { throw Failure.assertion("listener") }
            try configured.get(); checks.append("listener_ready")
            let expected = try TavernaCoreTransport.networkConfig(getNetCfg())
            var boundaries: [String: Bool] = [:]
            TavernaShareCommandProbe.beforeSend = { command in
                let boundary: String
                switch command {
                case .startChat: boundary = "cold"
                case .apiActivateChat: boundary = "resume"
                default: return
                }
                // Read /network synchronously as the dispatcher serializes the actual
                // start/activate command. The observer never returns a mocked response.
                guard let body = try? networkBody(),
                      let observed = try? JSONDecoder().decode(NetCfg.self, from: JSONSerialization.data(withJSONObject: body))
                else { boundaries[boundary] = false; return }
                boundaries[boundary] = observed == expected && body["socksMode"] as? String == "always"
            }
            defer { TavernaShareCommandProbe.beforeSend = nil }
            try require(model.initChat(with: "fixture-only-passphrase") == nil, "cold_model_started")
            try require(boundaries["cold"] == true, "cold_network_before_start")
            let initial = try actual()
            try require(initial == expected && initial.socksProxy != nil && initial.smpProxyMode == .never &&
                        initial.smpProxyFallback == .prohibit && initial.smpWebPortServers == .off, "managed_network")
            let json = try JSONSerialization.jsonObject(with: JSONEncoder().encode(initial)) as? [String: Any]
            try require(json?["socksMode"] as? String == "always", "mandatory_socks_mode")
            let defaults = [UserDefaults.standard.dictionaryRepresentation(), groupDefaults.dictionaryRepresentation()]
            try require(try defaults.allSatisfy { !String(decoding: try PropertyListSerialization.data(fromPropertyList: $0, format: .xml, options: 0), as: UTF8.self).contains(expected.socksProxy!) }, "capability_not_persisted")
            for (server, label) in [(cfg.smpServer, "smp_protocol"), (cfg.xftpServer, "xftp_protocol")] {
                let result = try raw("/_server test 1 \(server)")
                guard let body = result["serverTestResult"] as? [String: Any] else { throw Failure.assertion(label) }
                try require(body["testServer"] as? String == server && (body["testFailure"] == nil || body["testFailure"] is NSNull), label)
            }
            // This loopback endpoint is reachable and outside the two allowed routes.
            // A direct fallback would reach the Python sentinel despite socket instrumentation.
            for (server, label) in [(cfg.smpServer.replacingOccurrences(of: "relay.test:5223", with: "127.0.0.1:\(cfg.sentinelPort)"), "smp_no_direct_fallback"),
                                    (cfg.xftpServer.replacingOccurrences(of: "relay.test:8443", with: "127.0.0.1:\(cfg.sentinelPort)"), "xftp_no_direct_fallback")] {
                let result = try raw("/_server test 1 \(server)")
                guard let body = result["serverTestResult"] as? [String: Any] else { throw Failure.assertion(label) }
                try require(body["testServer"] as? String == server && body["testFailure"] != nil && !(body["testFailure"] is NSNull), label)
            }
            // Force an unsafe prior setting while suspended. The real resume path must replace it.
            let suspended = try raw(SEChatCommand.apiSuspendChat(timeoutMicroseconds: 0).cmdString)
            try require(suspended["cmdOk"] != nil, "suspended")
            _ = try raw("/_network \(encodeJSON(NetCfg.defaults))")
            try require(model.initChat() == nil, "model_resumed")
            try require(boundaries["resume"] == true, "resume_network_before_activate")
            try require(try actual() == expected, "resumed_managed_network")
            _ = try raw("/_stop")
            try require(try stopped(), "core_stopped")
            TavernaCoreTransport.stop()
            do { _ = try apiStartChat(); throw Failure.assertion("stopped_start") }
            catch TavernaCoreTransport.Failure.notReady { checks.append("stopped_start_denied") }
            do { try apiActivateChat(); throw Failure.assertion("stopped_resume") }
            catch TavernaCoreTransport.Failure.notReady { checks.append("stopped_resume_denied") }
            try require(try stopped(), "core_remains_stopped")
            record("PASS")
        } catch {
            TavernaCoreTransport.stop()
            if case let Failure.assertion(label) = error { record("FAIL", label) }
            else { record("FAIL", "configuration_or_core_error") }
        }
    }
}
#endif
