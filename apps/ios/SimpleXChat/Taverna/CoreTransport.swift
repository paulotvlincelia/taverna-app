import Foundation
import Security

// Each process owns its listener and capability. Enrollment supplies the identity;
// there is deliberately no persisted SOCKS secret or implicit direct mode.
public enum TavernaCoreTransport {
    public struct Route {
        let host: String
        let port: UInt16
        let gatewayHost: String
        let gatewayPort: UInt16
        let gatewayName: String
        public init(host: String, port: UInt16, gatewayHost: String, gatewayPort: UInt16, gatewayName: String) {
            self.host = host; self.port = port; self.gatewayHost = gatewayHost
            self.gatewayPort = gatewayPort; self.gatewayName = gatewayName
        }
    }
    public enum Failure: Error { case notReady, alreadyConfigured, stopped }
    private static let lock = NSLock()
    private static var transport: RelayTransport?
    private static var capability: String?
    private static var generation = UUID()

    public static func configure(routes: [Route], anchor: SecCertificate, identity: SecIdentity,
                                 completion: @escaping (Result<Void, Error>) -> Void) {
        lock.lock()
        guard transport == nil else { lock.unlock(); completion(.failure(Failure.alreadyConfigured)); return }
        do {
            var endpoints: [SocksDestination: RelayTransport.Endpoint] = [:]
            for route in routes {
                let destination = SocksDestination(host: route.host, port: route.port)
                guard endpoints[destination] == nil else { throw RelayTransport.Failure.configuration }
                endpoints[destination] = .init(host: route.gatewayHost, port: route.gatewayPort, serverName: route.gatewayName)
            }
            let value = try RelayTransport(routes: endpoints, anchor: anchor, identity: identity)
            let token = UUID(); generation = token; transport = value
            lock.unlock()
            value.start { result in
                lock.lock()
                guard generation == token else {
                    lock.unlock(); value.stop(); completion(.failure(Failure.stopped)); return
                }
                switch result {
                case let .success(proxy):
                    capability = proxy; lock.unlock(); completion(.success(()))
                case let .failure(error):
                    transport = nil; capability = nil; lock.unlock(); completion(.failure(error))
                }
            }
        } catch { lock.unlock(); completion(.failure(error)) }
    }

    public static func networkConfig(_ base: NetCfg) throws -> NetCfg {
        lock.lock(); defer { lock.unlock() }
        guard let capability else { throw Failure.notReady }
        var cfg = base
        cfg.socksProxy = capability
        cfg.socksMode = .always
        cfg.smpProxyMode = .never
        cfg.smpProxyFallback = .prohibit
        cfg.smpWebPortServers = .off
        return cfg
    }

    public static func stop() {
        lock.lock()
        let value = transport
        capability = nil; transport = nil; generation = UUID()
        lock.unlock()
        value?.stop()
    }
}
