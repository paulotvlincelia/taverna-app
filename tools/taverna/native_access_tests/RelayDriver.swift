import Foundation
import Security

// Qualification executable only. Its capability leaves via an anonymous pipe,
// never a file, logger, defaults store or personal Keychain.
@main struct RelayDriver {
    static func output(_ value: [String: Any]) {
        let data = try! JSONSerialization.data(withJSONObject: value, options: [.sortedKeys])
        FileHandle.standardOutput.write(data + Data([10]))
    }
    static func main() throws {
        guard CommandLine.arguments.count == 2 else { throw RelayTransport.Failure.configuration }
        let cfg = try JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1]))) as! [String: Any]
        var items: CFArray?
        var options: [String: Any] = [kSecImportExportPassphrase as String: "fixture-only"]
        #if os(macOS)
        guard #available(macOS 15, *) else { throw RelayTransport.Failure.configuration }
        options[kSecImportToMemoryOnly as String] = true
        #endif
        let p12 = try Data(contentsOf: URL(fileURLWithPath: cfg["identity"] as! String))
        guard SecPKCS12Import(p12 as CFData, options as CFDictionary, &items) == errSecSuccess,
              let first = (items as? [[String: Any]])?.first,
              let value = first[kSecImportItemIdentity as String] else { throw RelayTransport.Failure.configuration }
        let identity = value as! SecIdentity
        let ca = try Data(contentsOf: URL(fileURLWithPath: cfg["anchor"] as! String))
        guard let anchor = SecCertificateCreateWithData(nil, ca as CFData) else { throw RelayTransport.Failure.configuration }
        let host = cfg["host"] as! String
        let name = cfg["serverName"] as! String
        let smp = (cfg["smpPort"] as! NSNumber).uint16Value
        let xftp = (cfg["xftpPort"] as! NSNumber).uint16Value
        let limit = cfg["limit"] as? Int ?? 32
        let timeout = cfg["timeout"] as? Double ?? 3
        let transport = try RelayTransport(routes: [SocksDestination(host: "relay.test", port: 5223): .init(host: host, port: smp, serverName: name),
                SocksDestination(host: "relay.test", port: 8443): .init(host: host, port: xftp, serverName: name)], anchor: anchor, identity: identity,
                handshakeTimeout: timeout, connectionLimit: limit)
        transport.start { result in
                switch result {
                case let .success(proxy): output(["proxy": proxy])
                case .failure: output(["error": "listener_failed"])
                }
        }
        DispatchQueue.global().async {
            while let command = readLine() {
                if command == "stop" { transport.stop(); output(["stopping": true]) }
                else if command == "quit" { transport.stop(); exit(0) }
            }
            transport.stop(); exit(0)
        }
        dispatchMain()
    }
}
