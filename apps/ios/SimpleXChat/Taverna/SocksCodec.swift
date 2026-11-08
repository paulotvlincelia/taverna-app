import Foundation

// Local bridge protocol only. This does not parse or alter SimpleX traffic.
struct SocksDestination: Hashable {
    let host: String
    let port: UInt16
}

enum SocksAction: Equatable {
    case reply(Data)
    case connect(SocksDestination)
    case payload(Data)
    case close
}

struct SocksCodec {
    private enum Stage { case greeting, authentication, request, stream, failed }
    private var stage = Stage.greeting
    private var pending = Data()
    private let username: Data
    private let password: Data
    private let allowed: Set<SocksDestination>

    init(username: Data, password: Data, allowed: Set<SocksDestination>) {
        precondition((1...255).contains(username.count) && (1...255).contains(password.count))
        self.username = username
        self.password = password
        self.allowed = allowed
    }

    static func response(_ status: UInt8) -> Data { Data([5, status, 0, 1, 0, 0, 0, 0, 0, 0]) }

    private func matches(_ a: Data, _ b: Data) -> Bool {
        guard a.count == b.count else { return false }
        return zip(a, b).reduce(UInt8(0)) { $0 | ($1.0 ^ $1.1) } == 0
    }

    mutating func feed(_ data: Data) -> [SocksAction] {
        guard stage != .failed else { return [] }
        guard data.count <= 65536 else { stage = .failed; pending.removeAll(); return [.close] }
        pending.append(data)
        var result: [SocksAction] = []
        func byte(_ index: Int) -> UInt8 { pending[pending.startIndex + index] }
        func bytes(_ range: Range<Int>) -> Data { Data(pending.dropFirst(range.lowerBound).prefix(range.count)) }
        func fail(_ reply: Data) -> [SocksAction] { result + [.reply(reply), .close] }
        while true {
            switch stage {
            case .greeting:
                guard pending.count >= 2 else { return result }
                let count = Int(byte(1))
                guard byte(0) == 5, count > 0 else {
                    stage = .failed; pending.removeAll(); return fail(Data([5,255]))
                }
                guard pending.count >= count + 2 else { return result }
                guard bytes(2..<(count + 2)).contains(2) else {
                    stage = .failed; pending.removeAll(); return fail(Data([5,255]))
                }
                pending.removeFirst(count + 2)
                result.append(.reply(Data([5,2])))
                stage = .authentication
            case .authentication:
                guard pending.count >= 2 else { return result }
                let nameCount = Int(byte(1))
                guard byte(0) == 1, nameCount > 0 else {
                    stage = .failed; pending.removeAll(); return fail(Data([1,1]))
                }
                guard pending.count >= nameCount + 3 else { return result }
                let passwordCount = Int(byte(nameCount + 2))
                guard pending.count >= nameCount + passwordCount + 3 else { return result }
                guard passwordCount > 0,
                      matches(bytes(2..<(nameCount + 2)), username),
                      matches(bytes((nameCount + 3)..<(nameCount + passwordCount + 3)), password) else {
                    stage = .failed; pending.removeAll(); return fail(Data([1,1]))
                }
                pending.removeFirst(nameCount + passwordCount + 3)
                result.append(.reply(Data([1,0])))
                stage = .request
            case .request:
                guard pending.count >= 4 else { return result }
                guard byte(0) == 5, byte(1) == 1, byte(2) == 0 else {
                    stage = .failed; pending.removeAll(); return fail(Self.response(7))
                }
                // Only configured DNS-name routes exist in this qualification.
                guard byte(3) == 3 else {
                    stage = .failed; pending.removeAll(); return fail(Self.response(8))
                }
                guard pending.count >= 5 else { return result }
                let count = Int(byte(4))
                guard count > 0, count <= 253 else {
                    stage = .failed; pending.removeAll(); return fail(Self.response(2))
                }
                guard pending.count >= count + 7 else { return result }
                let hostBytes = bytes(5..<(count + 5))
                let host = String(data: hostBytes, encoding: .ascii)?.lowercased() ?? ""
                let labels = host.split(separator: ".", omittingEmptySubsequences: false)
                let valid = labels.allSatisfy { label in
                    !label.isEmpty && label.count <= 63 && label.first != "-" && label.last != "-"
                    && label.utf8.allSatisfy { (97...122).contains($0) || (48...57).contains($0) || $0 == 45 }
                }
                let port = UInt16(byte(count + 5)) << 8 | UInt16(byte(count + 6))
                let destination = SocksDestination(host: host, port: port)
                guard valid, port != 0, allowed.contains(destination) else {
                    stage = .failed; pending.removeAll(); return fail(Self.response(2))
                }
                pending.removeFirst(count + 7)
                result.append(.connect(destination))
                stage = .stream
            case .stream:
                if !pending.isEmpty { result.append(.payload(pending)); pending = Data() }
                return result
            case .failed:
                return result
            }
        }
    }
}
