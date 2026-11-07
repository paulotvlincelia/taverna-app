from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'tools/taverna/device_test'
sys.path.insert(0,str(ROOT/'tools/taverna'))
import ios_session as session


class PhysicalPolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT/'.build').mkdir(exist_ok=True)

    def run_host_harness(self, script, expected):
        with tempfile.TemporaryDirectory(dir=ROOT/'.build') as t:
            base=Path(t);(base/'main.swift').write_text(script)
            env=session.environment(ROOT)
            compiled=subprocess.run(['xcrun','swiftc',str(SOURCE/'DeviceTestPolicy.swift'),str(base/'main.swift'),'-o',str(base/'checks')],capture_output=True,text=True,env=env,timeout=120)
            self.assertEqual(compiled.returncode,0,compiled.stderr)
            result=subprocess.run([str(base/'checks')],capture_output=True,text=True,env=env,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout.strip(),expected)

    def test_native_literal_host_scene_callback_invalidates_transport_and_core(self):
        source=(SOURCE/'DeviceTestApp.swift').read_text()
        anchor='}.onChange(of: scenePhase) { phase in\n'
        self.assertEqual(source.count(anchor),1)
        callback=source.split(anchor,1)[1].split('\n            }',1)[0]
        pause=source[source.index('    func pause()'):source.rindex('\n}')]
        # Run the literal callback and pause method; scheduling is synchronous only in this harness.
        script='''import Foundation
import SwiftUI
struct ImmediateQueue { func async(execute body: () -> Void) { body() } }
enum TavernaCoreTransport { static var stops=0; static func stop() { stops += 1 } }
final class Host {
    let gate=DeviceTestGate(), queue=ImmediateQueue()
    var connected=true, initialized=true, status="", commands:[String]=[]
    func command(_ value:String) throws { commands.append(value) }
    func update(_ body:() -> Void) { body() }
'''+pause+'''
}
var test=Host()
func sceneChanged(_ phase:ScenePhase) {
'''+callback+r'''
}
func denied(_ action:() throws -> Void) { do { try action(); preconditionFailure("accepted paused action") } catch {} }
for initialized in [true,false] {
    for phase in [ScenePhase.active,.inactive,.background] {
        test=Host(); test.initialized=initialized
        try test.gate.connect(configure:{},apply:{},verify:{},start:{})
        let before=TavernaCoreTransport.stops
        sceneChanged(phase)
        if phase == .active {
            precondition(test.connected && test.gate.ready)
            precondition(TavernaCoreTransport.stops==before && test.commands.isEmpty)
            var allowed=false;try test.gate.perform { allowed=true };precondition(allowed)
        } else {
            precondition(!test.connected && !test.gate.ready)
            precondition(TavernaCoreTransport.stops==before+1)
            precondition(test.commands == (initialized ? ["/_stop"] : []))
            var allowed=false;denied { try test.gate.perform { allowed=true } };precondition(!allowed)
        }
    }
}
print("device-host lifecycle checks PASS")
'''
        self.run_host_harness(script,'device-host lifecycle checks PASS')

    def test_native_literal_host_history_requests_exact_bound_and_renders_rows(self):
        source=(SOURCE/'DeviceTestApp.swift').read_text()
        history=source[source.index('    private func readHistory()'):source.index('    func refresh()')]
        script='''import Foundation
final class Host {
    var contactID:Int64?, contact="", history:[DeviceTestHistoryItem]=[]
    var historyContainsBatch=false, batchAttempted=false, commands:[String]=[]
    var contacts:[[String:Any]]=[]
    func update(_ body:() -> Void) { body() }
    func command(_ value:String) throws -> DeviceTestResponse {
        commands.append(value)
        if value == "/contacts" {
            return try DeviceTestResponse(JSONSerialization.data(withJSONObject:["result":["contactsList":["contacts":contacts]]]))
        }
        return try DeviceTestResponse(Data(#"{"result":{"apiChat":{"chat":{"chatItems":[{"meta":{"itemId":2},"content":{"sndMsgContent":{"msgContent":{"type":"text","text":"Device-D1-02"}}}},{"meta":{"itemId":1},"content":{"rcvMsgContent":{"msgContent":{"type":"text","text":"Peer-01"}}}}]}}}}"#.utf8))
    }
    func refreshHistory() throws { try readHistory() }
'''+history+r'''
}
func denied(_ action:() throws -> Void) { do { try action(); preconditionFailure("accepted invalid contacts") } catch {} }
let test=Host()
test.contacts=[["contactId":Int64(42),"localDisplayName":"Fixture-Peer"]]
try test.refreshHistory()
precondition(test.commands == ["/contacts","/_get chat @42 count=100"])
precondition(test.contactID==42 && test.contact=="Fixture-Peer")
precondition(test.history == [DeviceTestHistoryItem(id:1,text:"Peer-01",sent:false),DeviceTestHistoryItem(id:2,text:"Device-D1-02",sent:true)])
precondition(test.historyContainsBatch && test.batchAttempted)
let empty=Host();empty.contactID=42;try empty.refreshHistory()
precondition(empty.contactID==nil && empty.commands==["/contacts"])
let multiple=Host();multiple.contacts=test.contacts+test.contacts
denied { try multiple.refreshHistory() }
precondition(multiple.commands==["/contacts"] && multiple.contactID==nil)
let malformed=Host();malformed.contacts=[["contactId":Int64(42)]]
denied { try malformed.refreshHistory() }
precondition(malformed.commands==["/contacts"] && malformed.contactID==nil)
print("device-host history checks PASS")
'''
        self.run_host_harness(script,'device-host history checks PASS')

    def test_native_configuration_boundary_history_and_lifecycle(self):
        harness=r'''
import Foundation
func check(_ value: @autoclosure () -> Bool) { precondition(value()) }
func denied(_ body: () throws -> Void) { do { try body(); preconditionFailure("accepted invalid state") } catch {} }
let now=Date(timeIntervalSince1970:2_000_000_000)
let valid:[String:Any]=["schema":1,"gatewayHost":"192.168.40.2","smpPort":15223,"serverName":"gateway.test","smpServer":"smp://"+String(repeating:"A",count:43)+"=@relay.test:5223","expiresAt":2_000_000_600,"identitySHA256":String(repeating:"a",count:64),"anchorSHA256":String(repeating:"b",count:64)]
func data(_ value:[String:Any]) throws -> Data { try JSONSerialization.data(withJSONObject:value) }
let cfg=try DeviceTestConfiguration.decode(data(valid),now:now)
check(cfg.gatewayHost=="192.168.40.2" && cfg.smpPort==15223 && cfg.serverName=="gateway.test")
var unpadded=valid;unpadded["smpServer"]=cfg.smpServer.replacingOccurrences(of:"=@",with:"@")
let normalized=try DeviceTestConfiguration.decode(data(unpadded),now:now)
check(normalized.canonicalSMPServer==cfg.smpServer && cfg.canonicalSMPServer==cfg.smpServer)
for (key,value) in [("gatewayHost","127.0.0.1" as Any),("gatewayHost","8.8.8.8"),("gatewayHost","0.0.0.0"),("gatewayHost","192.168.01.2"),("gatewayHost","172.32.0.2"),("gatewayHost","10.0.0.255"),("smpPort",0),("smpPort",443),("smpPort",65536),("smpPort",true),("serverName","evil.test"),("smpServer","smp://public.test"),("expiresAt",1_999_999_999),("expiresAt",2_000_086_401),("identitySHA256","wrong"),("anchorSHA256","wrong"),("schema",2)] {
 var bad=valid;bad[key]=value;denied { _=try DeviceTestConfiguration.decode(data(bad),now:now) }
}
var bad=valid;bad["extra"]=1;denied { _=try DeviceTestConfiguration.decode(data(bad),now:now) }
bad=valid;bad.removeValue(forKey:"anchorSHA256");denied { _=try DeviceTestConfiguration.decode(data(bad),now:now) }
let original=String(data:try data(valid),encoding:.utf8)!
let duplicate=Data(("{\"schema\":1,"+original.dropFirst()).utf8)
denied { _=try DeviceTestConfiguration.decode(duplicate,now:now) }
for host in ["10.1.2.3","172.16.0.1","172.31.255.254","192.168.0.1"] { check(DeviceTestConfiguration.privateIPv4(host)) }
let gate=DeviceTestGate();var trace:[String]=[]
denied { try gate.perform { trace.append("send") } };check(trace.isEmpty)
try gate.connect(configure:{trace.append("configure")},apply:{trace.append("apply")},verify:{trace.append("verify")},start:{trace.append("start")})
check(gate.ready && trace==["configure","apply","verify","start"])
try gate.perform { trace.append("send") };check(trace.last=="send")
gate.pause();check(!gate.ready);denied { try gate.perform { trace.append("wrong") } }
for failure in 0..<4 {
 let g=DeviceTestGate();var sequence:[Int]=[]
 func step(_ n:Int) throws { sequence.append(n);if n==failure { throw DeviceTestFailure.denied } }
 denied { try g.connect(configure:{try step(0)},apply:{try step(1)},verify:{try step(2)},start:{try step(3)}) }
 check(!g.ready && sequence==Array(0...failure))
}
let interrupted=DeviceTestGate()
denied { try interrupted.connect(configure:{interrupted.pause()},apply:{preconditionFailure()},verify:{preconditionFailure()},start:{preconditionFailure()}) }
let packet=Data(#"{"result":{"_owsf":true,"chat":{"chatItems":[{"chatItem":{"meta":{"itemId":2},"content":{"sndMsgContent":{"msgContent":{"type":"text","text":"Device-D1-02"}}}}},{"chatItem":{"meta":{"itemId":1},"content":{"rcvMsgContent":{"msgContent":{"type":"text","text":"Peer-01"}}}}}]}}}"#.utf8)
let result=try DeviceTestResponse(packet)
let rows=try result.history()
check(rows.map(\.id)==[1,2] && rows.map(\.text)==["Peer-01","Device-D1-02"] && rows.map(\.sent)==[false,true])
denied { _=try DeviceTestResponse(Data(#"{"error":{"chatError":{}}}"#.utf8)) }
let duplicateItems=Data(#"{"result":{"chat":{"chatItems":[{"chatItem":{"meta":{"itemId":1},"content":{"sndMsgContent":{"msgContent":{"type":"text","text":"a"}}}}},{"chatItem":{"meta":{"itemId":1},"content":{"sndMsgContent":{"msgContent":{"type":"text","text":"b"}}}}}]}}}"#.utf8)
denied { _=try DeviceTestResponse(duplicateItems).history() }
check(DeviceTestMessages.texts==Array(1...10).map{String(format:"Device-D1-%02d",$0)})
let batch=DeviceTestMessages();var sent:[String]=[]
try batch.send { sent.append($0) };check(sent==DeviceTestMessages.texts)
denied { try batch.send { sent.append($0) } };check(sent.count==10)

try DeviceTestServers.verify(["smpServers": [cfg.smpServer]], server: cfg.smpServer)
for incorrect: [String: Any] in [[:], ["smpServers": cfg.smpServer], ["smpServers": []],
        ["smpServers": [cfg.smpServer, cfg.smpServer]], ["smpServers": [cfg.smpServer.replacingOccurrences(of: "relay.test", with: "other.test")]],
        ["smpServers": ["smp://BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB@relay.test:5223"]]] {
    denied { try DeviceTestServers.verify(incorrect, server: cfg.smpServer) }
}
let network:[String:Any]=["socksProxy":"fixture-capability","socksMode":"always","smpProxyMode":"never","smpProxyFallback":"prohibit","smpWebPortServers":"off"]
var legacyFallback=network;legacyFallback["smpProxyFallback"]="no"
denied { try DeviceTestServers.verifyNetwork(legacyFallback,proxy:"fixture-capability") }
try DeviceTestServers.verifyNetwork(network,proxy:"fixture-capability")
for key in network.keys {
 var incorrect=network;incorrect[key]="wrong"
 denied { try DeviceTestServers.verifyNetwork(incorrect,proxy:"fixture-capability") }
 incorrect.removeValue(forKey:key);denied { try DeviceTestServers.verifyNetwork(incorrect,proxy:"fixture-capability") }
}
denied { try DeviceTestServers.verifyNetwork(network,proxy:nil) }
gate.pause();denied { try gate.connect(configure:{preconditionFailure()},apply:{},verify:{},start:{}) }
gate.resume();try gate.connect(configure:{},apply:{},verify:{},start:{})
check(gate.ready)

// Actual APIGetChat response: CRApiChat wraps an AChat whose chatItems are plain CChatItem objects.
let apiPacket=Data(#"{"result":{"apiChat":{"user":{},"chat":{"chatItems":[{"meta":{"itemId":3},"content":{"rcvMsgContent":{"msgContent":{"type":"text","text":"Peer-03"}}}}]}}}}"#.utf8)
let apiRows=try DeviceTestResponse(apiPacket).history()
check(apiRows==[DeviceTestHistoryItem(id:3,text:"Peer-03",sent:false)])
print("physical-policy checks PASS")
'''
        with tempfile.TemporaryDirectory(dir=ROOT/'.build') as t:
            base=Path(t);(base/'main.swift').write_text(harness)
            env=session.environment(ROOT)
            compiled=subprocess.run(['xcrun','swiftc',str(SOURCE/'DeviceTestPolicy.swift'),str(base/'main.swift'),'-o',str(base/'checks')],capture_output=True,text=True,env=env,timeout=120)
            self.assertEqual(compiled.returncode,0,compiled.stderr)
            result=subprocess.run([str(base/'checks')],capture_output=True,text=True,env=env,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout.strip(),'physical-policy checks PASS')

    def test_device_host_binds_policy_without_simulator_or_product_ui(self):
        app=(SOURCE/'DeviceTestApp.swift').read_text()
        for required in ('gate.connect(', 'TavernaCoreTransport.configure(', 'TavernaCoreTransport.withNetworkConfig(', 'readback', 'verifyServers(', 'gate.perform', 'gate.pause()', 'TavernaCoreTransport.stop()', 'scenePhase', 'SecPKCS12Import', 'DeviceTestConfiguration.decode', 'chatInitDeviceTestDatabase(', 'DeviceTestMessages'):
            self.assertIn(required,app)
        for forbidden in ('TavernaNativeProbe','targetEnvironment(simulator)','ProcessInfo.processInfo.environment','registerForRemoteNotifications','BGTaskScheduler','URLSession','print(','logger.','UserDefaults.standard.set','ContentView('):
            self.assertNotIn(forbidden,app)
        self.assertIn('guard values.isRegularFile == true, values.isSymbolicLink != true',app)
        self.assertIn('body.count <= limit',app)
        self.assertIn('SHA256.hash(data: body)',app)
        self.assertIn('guard contacts.count <= 1',app)

    def test_device_host_selects_smp_and_verifies_before_start(self):
        app=(SOURCE/'DeviceTestApp.swift').read_text()
        connect=app[app.index('    func connect()'):app.index('    private func verifyServers(')]
        configured,apply=connect.split('}, apply: {',1)
        apply,verify=apply.split('}, verify: {',1)
        verify,start=verify.split('}, start: {',1)
        self.assertIn('try self.gate.connect(configure:',configured)
        self.assertEqual(configured.count('.init(host:'),1)
        self.assertIn('.init(host: "relay.test", port: 5223',configured)
        self.assertIn('singleSMP: true',configured)
        self.assertIn('let server = cfg.canonicalSMPServer',configured)
        self.assertIn('self.command("/_network ',apply)
        self.assertIn(r'self.command("/_device_test_smp \(id) \(server)")',apply)
        self.assertIn('.require("deviceTestSMP")',apply)
        self.assertNotIn('/_servers ',connect)
        readback = app[app.index('    private func verifyServers('):app.index('    func invite()')]
        self.assertIn(r'command("/_device_test_smp \(id)").require("deviceTestSMP")',readback)
        self.assertIn('DeviceTestServers.verify(body, server: server)',readback)
        self.assertIn('self.command("/network")',verify)
        self.assertIn('DeviceTestServers.verifyNetwork(',verify)
        self.assertIn('self.verifyServers(',verify)
        self.assertIn('self.command("/_start main=on snd_files=off")',start)
        self.assertNotIn('/_start ',configured+apply+verify)

    def test_native_exact_device_file_loader_rejects_escape_size_and_digest(self):
        source=(SOURCE/'DeviceTestApp.swift').read_text()
        loader=source[source.index('    private func file('):source.index('    func connect()')]
        anchor='FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]'
        self.assertEqual(loader.count(anchor),1)
        loader=loader.replace(anchor,'documents').replace('private func file','func file')
        with tempfile.TemporaryDirectory(dir=ROOT/'.build') as t:
            base=Path(t);docs=base/'Documents';docs.mkdir();(docs/'DeviceTest').mkdir()
            root_literal=__import__('json').dumps(str(docs))
            script='import Foundation\nimport CryptoKit\nlet documents=URL(fileURLWithPath:'+root_literal+')\n'+loader+r'''
func denied(_ action: () throws -> Void) { do { try action(); preconditionFailure("accepted invalid file") } catch {} }
let dir=documents.appendingPathComponent("DeviceTest")
let target=dir.appendingPathComponent("device.p12")
let bytes=Data("fictitious-data".utf8)
try bytes.write(to:target)
let digest=SHA256.hash(data:bytes).map{String(format:"%02x",$0)}.joined()
let read=try file("device.p12",limit:1024,digest:digest);precondition(read==bytes)
denied { _=try file("device.p12",limit:1) }
denied { _=try file("device.p12",limit:1024,digest:String(repeating:"0",count:64)) }
denied { _=try file("missing",limit:1024) }
try Data().write(to:target);denied { _=try file("device.p12",limit:1024) }
try FileManager.default.removeItem(at:target)
try FileManager.default.createSymbolicLink(at:target,withDestinationURL:documents)
denied { _=try file("device.p12",limit:1024) }
try FileManager.default.removeItem(at:target)
try FileManager.default.removeItem(at:dir)
try FileManager.default.createSymbolicLink(at:dir,withDestinationURL:documents)
denied { _=try file("device.p12",limit:1024) }
print("device-file checks PASS")
'''
            (base/'main.swift').write_text(script)
            env=session.environment(ROOT)
            compiled=subprocess.run(['xcrun','swiftc',str(SOURCE/'DeviceTestPolicy.swift'),str(base/'main.swift'),'-o',str(base/'checks')],capture_output=True,text=True,env=env,timeout=120)
            self.assertEqual(compiled.returncode,0,compiled.stderr)
            result=subprocess.run([str(base/'checks')],capture_output=True,text=True,env=env,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout.strip(),'device-file checks PASS')


if __name__=='__main__':unittest.main()
