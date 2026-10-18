import Foundation
import Network
import Security

// Lifecycle is confined to queue. The caller supplies authenticated configuration
// and its own identity; enrollment and persistent credential storage are separate.
final class RelayTransport {
    struct Endpoint {
        let host: String
        let port: UInt16
        let serverName: String
    }
    enum Failure: Error { case configuration, random, stopped }
    private let queue = DispatchQueue(label: "taverna.relay-transport")
    private let routes: [SocksDestination: Endpoint]
    private let anchor: SecCertificate
    private let identity: SecIdentity
    private let deadline: TimeInterval
    private let limit: Int
    private let username: Data
    private let password: Data
    private var listener: NWListener?
    private var sessions: [UUID: Session] = [:]

    init(routes: [SocksDestination: Endpoint], anchor: SecCertificate, identity: SecIdentity,
         handshakeTimeout: TimeInterval = 5, connectionLimit: Int = 32) throws {
        guard routes.count == 2, routes.values.allSatisfy({ !$0.host.isEmpty && !$0.serverName.isEmpty && $0.port != 0 }),
              (0.1...30).contains(handshakeTimeout), (1...128).contains(connectionLimit) else { throw Failure.configuration }
        self.routes = routes; self.anchor = anchor; self.identity = identity
        deadline = handshakeTimeout; limit = connectionLimit
        func random() throws -> Data {
            var bytes = [UInt8](repeating: 0, count: 32)
            guard SecRandomCopyBytes(kSecRandomDefault, bytes.count, &bytes) == errSecSuccess else { throw Failure.random }
            return Data(bytes.map { String(format: "%02x", $0) }.joined().utf8)
        }
        username = try random(); password = try random()
    }

    // This string is a secret local capability. Never log or persist it.
    func start(_ completion: @escaping (Result<String, Error>) -> Void) {
        queue.async { [self] in
            guard listener == nil else { completion(.failure(Failure.configuration)); return }
            do {
                let params = NWParameters.tcp
                params.requiredLocalEndpoint = .hostPort(host: .ipv4(.loopback), port: .any)
                let value = try NWListener(using: params, on: .any)
                listener = value
                var delivered = false
                value.stateUpdateHandler = { [weak self] state in
                    guard let self else { return }
                    if case .ready = state, let port = value.port, !delivered {
                        delivered = true
                        completion(.success(String(decoding: self.username, as: UTF8.self) + ":" + String(decoding: self.password, as: UTF8.self) + "@127.0.0.1:" + String(port.rawValue)))
                    } else if case let .failed(error) = state {
                        if !delivered { delivered = true; completion(.failure(error)) }
                        self.stopOnQueue()
                    }
                }
                value.newConnectionHandler = { [weak self] connection in
                    guard let self, self.sessions.count < self.limit else { connection.cancel(); return }
                    let id = UUID()
                    let session = Session(client: connection, codec: SocksCodec(username: self.username, password: self.password, allowed: Set(self.routes.keys)), queue: self.queue,
                        timeout: self.deadline, connect: { [weak self] in self?.connection($0) }, ended: { [weak self] in self?.sessions.removeValue(forKey: id) })
                    self.sessions[id] = session
                    session.start()
                }
                value.start(queue: queue)
            } catch { completion(.failure(error)) }
        }
    }

    func stop() { queue.async { [self] in stopOnQueue() } }
    private func stopOnQueue() {
        listener?.newConnectionHandler = nil
        listener?.stateUpdateHandler = nil
        listener?.cancel(); listener = nil
        for session in Array(sessions.values) { session.close() }
        sessions.removeAll()
    }

    private func connection(_ destination: SocksDestination) -> NWConnection? {
        guard let endpoint = routes[destination], let port = NWEndpoint.Port(rawValue: endpoint.port),
              let localIdentity = sec_identity_create(identity) else { return nil }
        let tls = NWProtocolTLS.Options()
        sec_protocol_options_set_min_tls_protocol_version(tls.securityProtocolOptions, .TLSv13)
        sec_protocol_options_set_local_identity(tls.securityProtocolOptions, localIdentity)
        sec_protocol_options_set_tls_server_name(tls.securityProtocolOptions, endpoint.serverName)
        let anchor = self.anchor
        sec_protocol_options_set_verify_block(tls.securityProtocolOptions, { _, trust, complete in
            let evaluated = sec_trust_copy_ref(trust).takeRetainedValue()
            guard SecTrustSetAnchorCertificates(evaluated, [anchor] as CFArray) == errSecSuccess,
                  SecTrustSetAnchorCertificatesOnly(evaluated, true) == errSecSuccess,
                  SecTrustSetPolicies(evaluated, SecPolicyCreateSSL(true, endpoint.serverName as CFString)) == errSecSuccess else { complete(false); return }
            complete(SecTrustEvaluateWithError(evaluated, nil))
        }, queue)
        return NWConnection(host: NWEndpoint.Host(endpoint.host), port: port, using: NWParameters(tls: tls, tcp: NWProtocolTCP.Options()))
    }

    private final class Session {
        let client: NWConnection
        var codec: SocksCodec
        let queue: DispatchQueue
        let timeout: TimeInterval
        let connect: (SocksDestination) -> NWConnection?
        let ended: () -> Void
        var remote: NWConnection?
        var ready = false
        var closed = false
        var pending = Data()
        var timer: DispatchSourceTimer?

        init(client: NWConnection, codec: SocksCodec, queue: DispatchQueue, timeout: TimeInterval,
             connect: @escaping (SocksDestination) -> NWConnection?, ended: @escaping () -> Void) {
            self.client = client; self.codec = codec; self.queue = queue; self.timeout = timeout; self.connect = connect; self.ended = ended
        }
        func start() {
            let deadline = DispatchSource.makeTimerSource(queue: queue)
            deadline.schedule(deadline: .now() + timeout)
            deadline.setEventHandler { [weak self] in self?.close() }
            timer = deadline; deadline.resume()
            client.stateUpdateHandler = { [weak self] state in
                if case .ready = state { self?.readClient() }
                else if case .failed = state { self?.close() }
            }
            client.start(queue: queue)
        }
        func close() {
            guard !closed else { return }; closed = true
            timer?.cancel(); timer = nil
            client.stateUpdateHandler = nil; remote?.stateUpdateHandler = nil
            client.cancel(); remote?.cancel(); remote = nil; pending.removeAll()
            ended()
        }
        func readClient() {
            guard !closed else { return }
            client.receive(minimumIncompleteLength: 1, maximumLength: 65536) { [weak self] data, _, eof, error in
                guard let self, !self.closed else { return }
                guard error == nil, let data, !data.isEmpty else { self.close(); return }
                let actions = self.codec.feed(data)
                let rejecting = actions.contains(.close)
                for (index, action) in actions.enumerated() {
                    switch action {
                    case let .reply(value):
                        self.client.send(content: value, completion: .contentProcessed { [weak self] error in
                            if error != nil || (rejecting && index == actions.count - 2) { self?.close() }
                        })
                    case let .connect(destination): self.open(destination)
                    case let .payload(value): self.pending.append(value)
                    case .close:
                        if actions.count == 1 { self.close() }
                    }
                }
                guard !rejecting, !self.closed else { return }
                if eof { self.close(); return }
                if self.ready { self.writePending() }
                else if self.remote == nil { self.readClient() }
            }
        }
        func open(_ destination: SocksDestination) {
            guard remote == nil, let value = connect(destination) else { close(); return }
            remote = value
            value.stateUpdateHandler = { [weak self] state in
                guard let self, !self.closed else { return }
                if case .ready = state {
                    self.ready = true; self.timer?.cancel(); self.timer = nil
                    self.client.send(content: SocksCodec.response(0), completion: .contentProcessed { [weak self] error in
                        guard let self else { return }
                        if error != nil { self.close(); return }
                        self.writePending(); self.readRemote()
                    })
                } else if case .failed = state { self.close() }
            }
            value.start(queue: queue)
        }
        func writePending() {
            guard !closed, let remote, ready else { return }
            guard !pending.isEmpty else { readClient(); return }
            let bytes = pending; pending = Data()
            remote.send(content: bytes, completion: .contentProcessed { [weak self] error in
                if error != nil { self?.close() } else { self?.readClient() }
            })
        }
        func readRemote() {
            guard !closed, let remote else { return }
            remote.receive(minimumIncompleteLength: 1, maximumLength: 65536) { [weak self] data, _, eof, error in
                guard let self, !self.closed else { return }
                guard error == nil, let data, !data.isEmpty else { self.close(); return }
                self.client.send(content: data, completion: .contentProcessed { [weak self] error in
                    if error != nil || eof { self?.close() } else { self?.readRemote() }
                })
            }
        }
    }
}
