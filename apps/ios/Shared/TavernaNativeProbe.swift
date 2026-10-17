import Foundation
import SimpleXChat
import Security

// Simulator-only qualification. No enrollment, production credential loading or
// UI. Release/device builds cannot select this path using environment variables.
enum TavernaNativeProbe {
    static var active: Bool {
        #if DEBUG && targetEnvironment(simulator)
        return ProcessInfo.processInfo.environment["TAVERNA_NATIVE_PROBE"] != nil
        #else
        return false
        #endif
    }

    static func startIfRequested() {
        #if DEBUG && targetEnvironment(simulator)
        guard active else { return }
        DispatchQueue.global().async { run() }
        #endif
    }

    #if DEBUG && targetEnvironment(simulator)
    private enum Failure: Error { case assertion(String), configuration }
    private struct Configuration: Decodable {
        let identity: String
        let anchor: String
        let smpPort: UInt16
        let xftpPort: UInt16
        let smpServer: String
        let xftpServer: String
    }
    private static func run() {
        var checks: [String] = []
        var output: URL?
        func require(_ condition: Bool, _ name: String) throws {
            guard condition else { throw Failure.assertion(name) }; checks.append(name)
        }
        func record(_ status: String, _ failure: String? = nil) {
            guard let output else { return }
            var value: [String: Any] = ["status": status, "checks": checks, "process": ProcessInfo.processInfo.processName, "pid": ProcessInfo.processInfo.processIdentifier]
            value["failure"] = failure
            if let data = try? JSONSerialization.data(withJSONObject: value, options: [.sortedKeys]) {
                try? data.write(to: output, options: .atomic)
            }
        }
        do {
            let path = ProcessInfo.processInfo.environment["TAVERNA_NATIVE_PROBE"]!
            let cfgURL = URL(fileURLWithPath: path).resolvingSymlinksInPath()
            let checkout = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
            guard cfgURL.path.hasPrefix(checkout.appendingPathComponent(".build/access-qualification/run-").path),
                  cfgURL.lastPathComponent == "config.json", cfgURL.deletingLastPathComponent().lastPathComponent == "ios" else { throw Failure.configuration }
            let directory = cfgURL.deletingLastPathComponent()
            output = directory.appendingPathComponent("startup-result.json")
            guard !FileManager.default.fileExists(atPath: output!.path) else { return }
            let cfg = try JSONDecoder().decode(Configuration.self, from: Data(contentsOf: cfgURL))
            let fixture = directory.deletingLastPathComponent().path + "/"
            guard [cfg.identity, cfg.anchor].allSatisfy({ URL(fileURLWithPath: $0).resolvingSymlinksInPath().path.hasPrefix(fixture) }) else { throw Failure.configuration }
            let (migration, pointer) = chatInitTemporaryDatabase(url: directory.appendingPathComponent("core"), key: "fixture-only-passphrase")
            guard migration == .ok, let ctrl = pointer else { throw Failure.assertion("database") }
            func stopped() throws -> Bool {
                let response: ChatResponse0 = try chatSendCmdSync(.checkChatRunning, bgTask: false, ctrl: ctrl, log: false)
                if case .chatStopped = response { return true }; return false
            }
            do { _ = try apiStartChat(ctrl: ctrl); throw Failure.assertion("missing_start") }
            catch TavernaCoreTransport.Failure.notReady { checks.append("missing_start_denied") }
            do { try apiActivateChatChecked(ctrl: ctrl); throw Failure.assertion("missing_resume") }
            catch TavernaCoreTransport.Failure.notReady { checks.append("missing_resume_denied") }
            try require(try stopped(), "core_still_stopped")
            var items: CFArray?
            guard SecPKCS12Import(try Data(contentsOf: URL(fileURLWithPath: cfg.identity)) as CFData,
                                 [kSecImportExportPassphrase as String: "fixture-only"] as CFDictionary, &items) == errSecSuccess,
                  let first = (items as? [[String: Any]])?.first,
                  let value = first[kSecImportItemIdentity as String],
                  let anchor = SecCertificateCreateWithData(nil, try Data(contentsOf: URL(fileURLWithPath: cfg.anchor)) as CFData) else { throw Failure.configuration }
            let identity = value as! SecIdentity
            let ready = DispatchSemaphore(value: 0)
            var result: Result<Void, Error>?
            TavernaCoreTransport.configure(routes: [
                .init(host: "relay.test", port: 5223, gatewayHost: "127.0.0.1", gatewayPort: cfg.smpPort, gatewayName: "gateway.test"),
                .init(host: "relay.test", port: 8443, gatewayHost: "127.0.0.1", gatewayPort: cfg.xftpPort, gatewayName: "gateway.test")],
                anchor: anchor, identity: identity) { result = $0; ready.signal() }
            guard ready.wait(timeout: .now() + 10) == .success, let result else { throw Failure.assertion("listener_timeout") }
            try result.get(); checks.append("listener_ready")
            let user = try apiCreateActiveUser(Profile(displayName: "Native-proof", fullName: ""), ctrl: ctrl)
            // No queues exist yet. Network policy must precede the first start.
            try setNetworkConfig(NetCfg.defaults, ctrl: ctrl)
            let response: ChatResponse0 = try chatSendCmdSync(.apiGetNetworkConfig, bgTask: false, ctrl: ctrl, log: false)
            guard case let .networkConfig(actual) = response else { throw Failure.assertion("network_config") }
            let expected = try TavernaCoreTransport.networkConfig(NetCfg.defaults)
            try require(actual == expected && actual.socksProxy != nil && actual.smpProxyMode == .never && actual.smpProxyFallback == .prohibit && actual.smpWebPortServers == .off, "forced_network_config")
            let encoded = try JSONSerialization.jsonObject(with: JSONEncoder().encode(actual)) as? [String: Any]
            try require(encoded?["socksMode"] as? String == "always", "mandatory_socks_mode")
            let proxy = expected.socksProxy!
            let defaults = [UserDefaults.standard.dictionaryRepresentation(), groupDefaults.dictionaryRepresentation()]
            let persisted = try defaults.map { try PropertyListSerialization.data(fromPropertyList: $0, format: .xml, options: 0) }
            try require(persisted.allSatisfy { !String(decoding: $0, as: UTF8.self).contains(proxy) }, "capability_not_persisted")
            try require(try apiStartChat(ctrl: ctrl), "core_started")
            let running: ChatResponse0 = try chatSendCmdSync(.checkChatRunning, bgTask: false, ctrl: ctrl, log: false)
            if case .chatRunning = running { checks.append("core_running") } else { throw Failure.assertion("core_running") }
            for (server, name) in [(cfg.smpServer, "core_smp_protocol"), (cfg.xftpServer, "core_xftp_protocol")] {
                let tested: ChatResponse0 = try chatSendCmdSync(.apiTestProtoServer(userId: user.userId, server: server), bgTask: false, ctrl: ctrl, log: false)
                guard case let .serverTestResult(_, address, nil) = tested, address == server else { throw Failure.assertion(name) }
                checks.append(name)
            }
            try apiActivateChatChecked(ctrl: ctrl); checks.append("resume_configured")
            let stop: ChatResponse0 = try chatSendCmdSync(.apiStopChat, bgTask: false, ctrl: ctrl, log: false)
            guard case .chatStopped = stop else { throw Failure.assertion("stop") }
            try require(try stopped(), "core_stopped")
            TavernaCoreTransport.stop()
            do { _ = try apiStartChat(ctrl: ctrl); throw Failure.assertion("stopped_start") }
            catch TavernaCoreTransport.Failure.notReady { checks.append("stopped_start_denied") }
            do { try apiActivateChatChecked(ctrl: ctrl); throw Failure.assertion("stopped_resume") }
            catch TavernaCoreTransport.Failure.notReady { checks.append("stopped_resume_denied") }
            _ = user // No profile or payload is written to the public receipt.
            record("PASS")
        } catch {
            TavernaCoreTransport.stop()
            // Do not serialize core errors: a network response may contain capability data.
            if case let Failure.assertion(name) = error { record("FAIL", name) }
            else { record("FAIL", "configuration_or_core_error") }
        }
    }
    #endif
}
