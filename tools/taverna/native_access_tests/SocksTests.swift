import Foundation

@main struct SocksTests {
    static var assertions = 0
    static func expect(_ value: @autoclosure () -> Bool, _ message: String) {
        assertions += 1
        if !value() { fatalError(message) }
    }
    static let smp = SocksDestination(host: "relay.test", port: 5223)
    static let xftp = SocksDestination(host: "relay.test", port: 8443)
    static func codec() -> SocksCodec { SocksCodec(username: Data("user".utf8), password: Data("secret".utf8), allowed: [smp, xftp]) }
    static let greeting = Data([5, 2, 0, 2])
    static func auth(_ password: String = "secret") -> Data {
        Data([1, 4]) + Data("user".utf8) + Data([UInt8(password.utf8.count)]) + Data(password.utf8)
    }
    static func request(_ host: String = "relay.test", port: UInt16 = 5223, command: UInt8 = 1) -> Data {
        Data([5, command, 0, 3, UInt8(host.utf8.count)]) + Data(host.utf8) + Data([UInt8(port >> 8), UInt8(port & 255)])
    }
    static func main() {
        var c = codec()
        expect(c.feed(greeting) == [.reply(Data([5, 2]))], "NP-01: select username/password, never no-auth")
        expect(c.feed(auth()) == [.reply(Data([1, 0]))], "NP-01: valid process credential")
        expect(c.feed(request()) == [.connect(smp)], "NP-02: exact SMP route")
        expect(c.feed(Data([1,2,3])) == [.payload(Data([1,2,3]))], "NP-03: opaque bytes after authorization")
        c = codec()
        let pipeline = greeting + auth() + request(port: 8443) + Data([22,3,3])
        expect(c.feed(pipeline) == [.reply(Data([5,2])), .reply(Data([1,0])), .connect(xftp), .payload(Data([22,3,3]))], "NP-01/02: pipelined negotiation retains TLS bytes")
        c = codec()
        var events: [SocksAction] = []
        for byte in pipeline { events += c.feed(Data([byte])) }
        expect(events == [.reply(Data([5,2])), .reply(Data([1,0])), .connect(xftp), .payload(Data([22])), .payload(Data([3])), .payload(Data([3]))], "NP-01: fragmented frames do not authorize early or lose bytes")
        for bytes: [UInt8] in [[4,1,2], [5,1,0], [5,0]] {
            c = codec(); expect(c.feed(Data(bytes)) == [.reply(Data([5,255])), .close], "NP-01: unsupported version/method denied")
            expect(c.feed(pipeline).isEmpty, "NP-01: failed handshake cannot recover")
        }
        c = codec(); _ = c.feed(greeting)
        expect(c.feed(auth("wrong")) == [.reply(Data([1,1])), .close], "NP-01: wrong process credential denied")
        c = codec(); _ = c.feed(greeting)
        expect(c.feed(Data([1,0])) == [.reply(Data([1,1])), .close], "NP-01: empty username denied")
        c = codec(); _ = c.feed(greeting)
        expect(c.feed(Data([2,4]) + Data("user".utf8)) == [.reply(Data([1,1])), .close], "NP-01: invalid auth version denied")
        for (host, port) in [("sentinel.test", UInt16(5223)), ("relay.test", UInt16(443)), ("relay.test", UInt16(0)), ("relay.test.", UInt16(5223)), ("-bad.test", UInt16(5223)), ("relay\0.test", UInt16(5223))] {
            c = codec(); _ = c.feed(greeting + auth())
            let result = c.feed(request(host, port: port))
            expect(result == [.reply(SocksCodec.response(2)), .close], "NP-02: unauthorized or malformed destination denied before connect")
        }
        c = codec(); _ = c.feed(greeting + auth())
        expect(c.feed(request(command: 2)) == [.reply(SocksCodec.response(7)), .close], "NP-02: BIND/UDP commands unsupported")
        for addressType: UInt8 in [1,4,255] {
            c = codec(); _ = c.feed(greeting + auth())
            expect(c.feed(Data([5,1,0,addressType])) == [.reply(SocksCodec.response(8)), .close], "NP-02: unconfigured IP forms denied without DNS")
        }
        c = codec(); _ = c.feed(greeting + auth())
        expect(c.feed(Data([5,1,1,3,1,97,0,80])) == [.reply(SocksCodec.response(7)), .close], "NP-02: reserved field rejected")
        c = codec()
        expect(c.feed(Data(repeating: 0, count: 65537)) == [.close], "NP-01: input chunk bound")
        expect(SocksCodec.response(2) == Data([5,2,0,1,0,0,0,0,0,0]), "NP-02: precise ruleset-denied frame")
        c = codec(); _ = c.feed(greeting + auth())
        expect(c.feed(request("RELAY.TEST")) == [.connect(smp)], "NP-02: ASCII domain case normalization")
        print("SocksTests: \(assertions) assertions passed; NP-01/02 codec only")
    }
}
