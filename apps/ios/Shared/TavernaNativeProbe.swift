import Foundation
import SimpleXChat
import Security
import SwiftUI

// Simulator-only qualification. No enrollment, production credential loading or
// product UI. Release/device builds cannot select this path using environment variables.
enum TavernaNativeProbe {
    static var active: Bool {
        #if DEBUG && targetEnvironment(simulator)
        return ProcessInfo.processInfo.environment["TAVERNA_NATIVE_PROBE"] != nil || TavernaShareHost.active
        #else
        return false
        #endif
    }

    static func startIfRequested() {
        #if DEBUG && targetEnvironment(simulator)
        guard ProcessInfo.processInfo.environment["TAVERNA_NATIVE_PROBE"] != nil else { return }
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
        let mode: String?
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
            if cfg.mode == "payload" {
                for name in ["files", "tmp", "assets"] {
                    try FileManager.default.createDirectory(at: directory.appendingPathComponent(name), withIntermediateDirectories: false)
                }
                try apiSetAppFilePaths(filesFolder: directory.appendingPathComponent("files").path,
                                       tempFolder: directory.appendingPathComponent("tmp").path,
                                       assetsFolder: directory.appendingPathComponent("assets").path, ctrl: ctrl)
            }
            try require(try apiStartChat(ctrl: ctrl), "core_started")
            let running: ChatResponse0 = try chatSendCmdSync(.checkChatRunning, bgTask: false, ctrl: ctrl, log: false)
            if case .chatRunning = running { checks.append("core_running") } else { throw Failure.assertion("core_running") }
            if cfg.mode == "payload" {
                try configureServers(cfg, userId: user.userId, ctrl: ctrl, directory: directory)
            }
            for (server, name) in [(cfg.smpServer, "core_smp_protocol"), (cfg.xftpServer, "core_xftp_protocol")] {
                let tested: ChatResponse0 = try chatSendCmdSync(.apiTestProtoServer(userId: user.userId, server: server), bgTask: false, ctrl: ctrl, log: false)
                guard case let .serverTestResult(_, address, nil) = tested, address == server else { throw Failure.assertion(name) }
                checks.append(name)
            }
            try apiActivateChatChecked(ctrl: ctrl); checks.append("resume_configured")
            if cfg.mode == "payload" {
                try payloadLoop(cfg, ctrl: ctrl, directory: directory)
            }
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

    private static func configureServers(_ cfg: Configuration, userId: Int64, ctrl: chat_ctrl, directory: URL) throws {
        func command<R: ChatAPIResult>(_ cmd: ChatCommand, _ label: String) throws -> R {
            guard let data = sendSimpleXCmdStr(cmd.cmdString, ctrl, retryNum: 0) else { throw Failure.assertion(label) }
            // Fixture-only server configuration responses do not contain NetCfg.
            try data.write(to: directory.appendingPathComponent(label + ".json"), options: .atomic)
            let result: APIResult<R> = decodeAPIResult(data)
            do { return try apiResult(result) } catch { throw Failure.assertion(label) }
        }
        let existing: ChatResponse0 = try command(.apiGetUserServers(userId: userId), "server_read")
        guard case let .userServers(_, groups) = existing else { throw Failure.assertion("server_read") }
        var disabled = groups.map { group in
            var g = group
            g.smpServers = g.smpServers.map { var s = $0; s.enabled = false; return s }
            g.xftpServers = g.xftpServers.map { var s = $0; s.enabled = false; return s }
            return g
        }
        disabled.append(UserOperatorServers(operator: nil,
            smpServers: [UserServer(server: cfg.smpServer, preset: false, enabled: true, deleted: false)],
            xftpServers: [UserServer(server: cfg.xftpServer, preset: false, enabled: true, deleted: false)], chatRelays: []))
        let set: ChatResponse2 = try command(.apiSetUserServers(userId: userId, userServers: disabled), "server_set")
        guard case .cmdOk = set else { throw Failure.assertion("server_set") }
        let read: ChatResponse0 = try command(.apiGetUserServers(userId: userId), "server_readback")
        guard case let .userServers(_, actual) = read,
              actual.flatMap({ $0.smpServers }).filter({ $0.enabled }).map({ $0.server }) == [cfg.smpServer],
              actual.flatMap({ $0.xftpServers }).filter({ $0.enabled }).map({ $0.server }) == [cfg.xftpServer]
        else { throw Failure.assertion("exclusive_servers") }
    }

    // A bounded local fixture mailbox, compiled only for DEBUG Simulator. It
    // cannot configure transport, issue arbitrary core commands or select UI.
    private static func payloadLoop(_ cfg: Configuration, ctrl: chat_ctrl, directory: URL) throws {
        func write(_ value: [String: Any], _ name: String) throws {
            try JSONSerialization.data(withJSONObject: value, options: [.sortedKeys]).write(to: directory.appendingPathComponent(name), options: .atomic)
        }
        try write(["ready": true, "pid": ProcessInfo.processInfo.processIdentifier,
                   "process": ProcessInfo.processInfo.processName, "exclusive_servers": true], "payload-ready.json")
        let events = directory.appendingPathComponent("events.jsonl")
        FileManager.default.createFile(atPath: events.path, contents: nil)
        let stream = try FileHandle(forWritingTo: events)
        defer { try? stream.close() }
        let deadline = Date().addingTimeInterval(600)
        var sequence = 1
        while Date() < deadline {
            let request = directory.appendingPathComponent("request-\(sequence).json")
            if FileManager.default.fileExists(atPath: request.path) {
                let value = try JSONSerialization.jsonObject(with: Data(contentsOf: request)) as? [String: String]
                guard let command = value?["command"] else { throw Failure.configuration }
                if command == "stop" { return }
                var result: [String: Any]
                if command.hasPrefix("test:") || command.hasPrefix("sentinel:") {
                    let server: String
                    if command == "test:smp" { server = cfg.smpServer }
                    else if command == "test:xftp" { server = cfg.xftpServer }
                    else if command.hasPrefix("sentinel:"), let port = UInt16(command.dropFirst(9)), port > 0 {
                        server = cfg.smpServer.replacingOccurrences(of: "relay.test:5223", with: "127.0.0.1:\(port)")
                    } else { throw Failure.configuration }
                    let tested: ChatResponse0 = try chatSendCmdSync(.apiTestProtoServer(userId: 1, server: server), bgTask: false, ctrl: ctrl, log: false)
                    guard case let .serverTestResult(_, address, failure) = tested, address == server else { throw Failure.assertion("protocol_result") }
                    result = ["type": "protocolTest", "failed": failure != nil]
                } else {
                    let files = directory.appendingPathComponent("files").path + "/"
                    let parts = command.split(separator: " ", omittingEmptySubsequences: true)
                    let fileCommand = (parts.count == 3 && parts[0] == "/_upload" && parts[1] == "1") ||
                                      (parts.count == 4 && parts[0] == "/_download" && parts[1] == "1" && parts[2].hasPrefix("simplex:/file#"))
                    let fileAllowed = fileCommand && parts.last.map { path in
                        let resolved = URL(fileURLWithPath: String(path)).resolvingSymlinksInPath().path
                        return resolved.hasPrefix(files) && !String(path).contains("..")
                    } == true
                    guard command == "/_connect 1" || command == "/contacts" || command == "/tail @Proof-bob 20" ||
                          (command.hasPrefix("@Proof-bob ") && command.count < 512 && !command.contains("\n")) || fileAllowed
                    else { throw Failure.configuration }
                    guard let data = sendSimpleXCmdStr(command, ctrl, retryNum: 0),
                          let decoded = try JSONSerialization.jsonObject(with: data) as? [String: Any]
                    else { throw Failure.assertion("command_result") }
                    result = decoded
                }
                try write(result, "response-\(sequence).json")
                sequence += 1
            }
            let event: APIResult<ChatEvent>? = recvSimpleXMsg(ctrl, messageTimeout: 50_000)
            var projected: [String: Any]?
            if case let .result(value) = event {
                switch value {
                case let .sndStandaloneFileComplete(_, meta, uris):
                    projected = ["type": "sndStandaloneFileComplete", "fileId": meta.fileId, "rcvURIs": uris]
                case let .rcvStandaloneFileComplete(_, path, transfer):
                    projected = ["type": "rcvStandaloneFileComplete", "fileId": transfer.fileId, "targetPath": path]
                case let .sndFileProgressXFTP(_, _, meta, sent, total):
                    projected = ["type": "sndFileProgressXFTP", "fileId": meta.fileId, "sentSize": sent, "totalSize": total]
                case let .sndFileError(_, _, meta, _):
                    projected = ["type": "sndFileError", "fileId": meta.fileId]
                case let .rcvFileError(_, _, _, transfer):
                    projected = ["type": "rcvFileError", "fileId": transfer.fileId]
                default: break
                }
            }
            if let projected {
                var data = try JSONSerialization.data(withJSONObject: projected, options: [.sortedKeys]); data.append(10)
                try stream.write(contentsOf: data)
            }
        }
        throw Failure.assertion("payload_deadline")
    }
    #endif
}

// UIKit is the actual extension host; this surface only exists in DEBUG Simulator.
enum TavernaShareHost {
    static var active: Bool {
        #if DEBUG && targetEnvironment(simulator)
        ProcessInfo.processInfo.environment["TAVERNA_SHARE_HOST"] == "1"
        #else
        false
        #endif
    }
}
#if DEBUG && targetEnvironment(simulator)
struct TavernaShareHostView: View {
    @State private var showing = false
    var body: some View {
        Button("Share qualification") { showing = true }
            .sheet(isPresented: $showing) { TavernaShareSheet() }
    }
}
private struct TavernaShareSheet: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: ["Taverna fictitious sharing qualification"], applicationActivities: nil)
    }
    func updateUIViewController(_ controller: UIActivityViewController, context: Context) {}
}
#endif
