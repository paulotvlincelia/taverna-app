// Original technical test policy, AGPLv3. No product artwork or UI code.
import Foundation

enum DeviceTestFailure: Error { case configuration, denied, response, history, noActiveUser }

enum DeviceTestStorage {
    enum Failure: Error { case storage, keychain }

    static func location(
        in applicationSupport: URL,
        readKey: () throws -> String?,
        createKey: () throws -> String,
        excludeFromBackup: (URL) throws -> Void = excludeFromBackup
    ) throws -> (URL, String) {
        let manager = FileManager.default
        let root = applicationSupport.resolvingSymlinksInPath()
        let parent = root.appendingPathComponent("InnerMeshDeviceTest", isDirectory: true)
        let directory = parent.appendingPathComponent("v1", isDirectory: true)
        for url in [parent, directory] {
            if let attributes = try attributes(at: url) {
                guard attributes[.type] as? FileAttributeType == .typeDirectory else { throw Failure.storage }
            } else {
                try manager.createDirectory(at: url, withIntermediateDirectories: false)
            }
        }
        try excludeFromBackup(directory)

        let prefix = directory.appendingPathComponent("profile")
        let banks = [prefix.path + "_chat.db", prefix.path + "_agent.db"]
        let present = try banks.map { try regularFile(at: $0) }
        guard present[0] == present[1] else { throw Failure.storage }
        for bank in banks {
            for suffix in ["-wal", "-shm", "-journal", ".bak"] {
                if try regularFile(at: bank + suffix), !present[0] { throw Failure.storage }
            }
        }
        do {
            let key: String
            if let saved = try readKey() {
                key = saved
            } else {
                guard !present[0] else { throw Failure.keychain }
                key = try createKey()
            }
            guard Data(base64Encoded: key)?.count == 32 else { throw Failure.keychain }
            return (prefix, key)
        } catch {
            throw Failure.keychain
        }
    }

    static func excludeFromBackup(_ directory: URL) throws {
        var url = directory
        var values = URLResourceValues()
        values.isExcludedFromBackup = true
        try url.setResourceValues(values)
        url.removeAllCachedResourceValues()
        guard try url.resourceValues(forKeys: [.isExcludedFromBackupKey]).isExcludedFromBackup == true else {
            throw Failure.storage
        }
    }

    private static func attributes(at url: URL) throws -> [FileAttributeKey: Any]? {
        do {
            return try FileManager.default.attributesOfItem(atPath: url.path)
        } catch let error as CocoaError where error.code == .fileNoSuchFile || error.code == .fileReadNoSuchFile {
            return nil
        }
    }

    private static func regularFile(at path: String) throws -> Bool {
        guard let attributes = try attributes(at: URL(fileURLWithPath: path)) else { return false }
        guard attributes[.type] as? FileAttributeType == .typeRegular,
              attributes[.referenceCount] as? Int == 1 else { throw Failure.storage }
        return true
    }
}

struct DeviceTestConfiguration: Decodable {
    let schema: Int
    let gatewayHost: String
    let smpPort: UInt16
    let serverName: String
    let smpServer: String
    let expiresAt: Int
    let identitySHA256: String
    let anchorSHA256: String

    var canonicalSMPServer: String {
        if smpServer.contains("=@") { return smpServer }
        return smpServer.replacingOccurrences(of: "@", with: "=@")
    }

    static func privateIPv4(_ host: String) -> Bool {
        let parts = host.split(separator: ".", omittingEmptySubsequences: false)
        guard parts.count == 4 else { return false }
        let numbers = parts.compactMap { UInt8($0) }
        guard numbers.count == 4, zip(parts, numbers).allSatisfy({ String($0.1) == $0.0 }),
              numbers[3] > 0, numbers[3] < 255 else { return false }
        return numbers[0] == 10 || (numbers[0] == 172 && (16...31).contains(numbers[1])) ||
            (numbers[0] == 192 && numbers[1] == 168)
    }

    static func decode(_ data: Data, now: Date = Date()) throws -> Self {
        let keys: Set<String> = ["schema", "gatewayHost", "smpPort", "serverName", "smpServer", "expiresAt", "identitySHA256", "anchorSHA256"]
        guard data.count <= 4096,
              let object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              Set(object.keys) == keys,
              let text = String(data: data, encoding: .utf8) else { throw DeviceTestFailure.configuration }
        // Configuration is a flat, bounded object with literal ASCII keys and values.
        // Reject duplicate/escaped keys instead of accepting JSONDecoder's last value.
        let fields = try NSRegularExpression(pattern: #"(?<!\\)"([A-Za-z0-9]+)"\s*:"#)
        let matches = fields.matches(in: text, range: NSRange(text.startIndex..., in: text))
        guard matches.count == keys.count else { throw DeviceTestFailure.configuration }
        let cfg = try JSONDecoder().decode(Self.self, from: data)
        let digest = #"^[a-f0-9]{64}$"#
        guard cfg.schema == 1, privateIPv4(cfg.gatewayHost), cfg.smpPort >= 1024,
              cfg.serverName == "gateway.test",
              cfg.smpServer.range(of: #"^smp://[A-Za-z0-9_-]{43}=?@relay\.test:5223$"#, options: .regularExpression) != nil,
              Double(cfg.expiresAt) > now.timeIntervalSince1970,
              Double(cfg.expiresAt) <= now.timeIntervalSince1970 + 86400,
              cfg.identitySHA256.range(of: digest, options: .regularExpression) != nil,
              cfg.anchorSHA256.range(of: digest, options: .regularExpression) != nil else { throw DeviceTestFailure.configuration }
        return cfg
    }
}

final class DeviceTestGate {
    private let lock = NSLock()
    private var generation = 0
    private var connected = false
    private var foreground = true
    var ready: Bool { lock.lock(); defer { lock.unlock() }; return connected }
    func pause() { lock.lock(); generation += 1; connected = false; foreground = false; lock.unlock() }
    func resume() { lock.lock(); generation += 1; foreground = true; connected = false; lock.unlock() }
    func connect(configure: () throws -> Void, apply: () throws -> Void,
                 verify: () throws -> Void, start: () throws -> Void) throws {
        lock.lock()
        guard foreground else { lock.unlock(); throw DeviceTestFailure.denied }
        generation += 1; connected = false
        let token = generation; lock.unlock()
        func valid() throws {
            lock.lock(); defer { lock.unlock() }
            guard generation == token else { throw DeviceTestFailure.denied }
        }
        do {
            try valid(); try configure()
            try valid(); try apply()
            try valid(); try verify()
            try valid(); try start()
            lock.lock(); defer { lock.unlock() }
            guard generation == token else { throw DeviceTestFailure.denied }
            connected = true
        } catch { pause(); throw error }
    }
    func perform<T>(_ action: () throws -> T) throws -> T {
        guard ready else { throw DeviceTestFailure.denied }
        return try action()
    }
}

struct DeviceTestHistoryItem: Identifiable, Equatable {
    let id: Int64
    let text: String
    let sent: Bool
}

struct DeviceTestResponse {
    let tag: String
    let body: [String: Any]
    init(_ data: Data) throws {
        guard let root = try JSONSerialization.jsonObject(with: data) as? [String: Any] else { throw DeviceTestFailure.response }
        if Set(root.keys).subtracting(["_owsf"]) == ["error"],
           let error = root["error"] as? [String: Any], Set(error.keys).subtracting(["_owsf"]) == ["error"],
           let chat = error["error"] as? [String: Any], Set(chat.keys).subtracting(["_owsf"]) == ["errorType"],
           let reason = chat["errorType"] as? [String: Any], Set(reason.keys).subtracting(["_owsf"]) == ["noActiveUser"],
           let empty = reason["noActiveUser"] as? [String: Any], empty.isEmpty {
            throw DeviceTestFailure.noActiveUser
        }
        guard root["error"] == nil, var result = root["result"] as? [String: Any] else { throw DeviceTestFailure.response }
        result.removeValue(forKey: "_owsf")
        guard result.count == 1, let tag = result.keys.first,
              let body = result[tag] as? [String: Any] else { throw DeviceTestFailure.response }
        self.tag = tag; self.body = body
    }
    func require(_ expected: String) throws -> [String: Any] {
        guard tag == expected else { throw DeviceTestFailure.response }; return body
    }
    func history() throws -> [DeviceTestHistoryItem] {
        let body: [String: Any]
        if tag == "apiChat", let chat = self.body["chat"] as? [String: Any] { body = chat }
        else if tag == "chatItems" || tag == "chat" { body = self.body }
        else { throw DeviceTestFailure.history }
        guard let items = body["chatItems"] as? [[String: Any]], items.count <= 100 else { throw DeviceTestFailure.history }
        var rows: [DeviceTestHistoryItem] = []
        for entry in items {
            let item = (entry["chatItem"] as? [String: Any]) ?? entry
            guard let meta = item["meta"] as? [String: Any], let id = meta["itemId"] as? Int64,
                  let content = item["content"] as? [String: Any] else { throw DeviceTestFailure.history }
            let sent = content["sndMsgContent"] != nil
            guard let wrapped = content[sent ? "sndMsgContent" : "rcvMsgContent"] as? [String: Any],
                  let message = wrapped["msgContent"] as? [String: Any], message["type"] as? String == "text",
                  let text = message["text"] as? String else { continue }
            guard !rows.contains(where: { $0.id == id }) else { throw DeviceTestFailure.history }
            rows.append(.init(id: id, text: text, sent: sent))
        }
        return rows.sorted { $0.id < $1.id }
    }
}

final class DeviceTestMessages {
    static let texts = (1...10).map { String(format: "Device-D1-%02d", $0) }
    private var attempted = false
    func send(_ action: (String) throws -> Void) throws {
        guard !attempted else { throw DeviceTestFailure.denied }
        // Consume before send: an ambiguous failure cannot cause an automatic duplicate batch.
        attempted = true
        for text in Self.texts { try action(text) }
    }
}

enum DeviceTestServers {
    static func verify(_ effective: [String: Any], server: String) throws {
        guard effective["smpServers"] as? [String] == [server] else { throw DeviceTestFailure.denied }
    }
    static func verifyNetwork(_ network: [String: Any], proxy: String?) throws {
        guard let proxy, network["socksProxy"] as? String == proxy,
              network["socksMode"] as? String == "always",
              network["smpProxyMode"] as? String == "never",
              network["smpProxyFallback"] as? String == "prohibit",
              network["smpWebPortServers"] as? String == "off" else { throw DeviceTestFailure.denied }
    }
}
