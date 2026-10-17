"""Real native Network.framework + TLS fixture; no app/iOS completion claim."""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import select
import socket
import ssl
import subprocess
import sys
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[3]
if 'TAVERNA_PROOF_RUN' not in os.environ:
    os.environ['TAVERNA_PROOF_RUN'] = 'native-' + uuid.uuid4().hex[:8]
module = importlib.util.spec_from_file_location('native_fixture', ROOT/'tools/taverna/access_proof/fixture.py')
f = importlib.util.module_from_spec(module); module.loader.exec_module(f)


def receive(sock, count):
    output = b''
    while len(output) < count:
        block = sock.recv(count-len(output))
        if not block: raise EOFError('native connection closed')
        output += block
    return output


class NativeTransport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.drivers = []
        f.initialize()
        try:
            f.start(native=True)
            value = json.loads(f.docker('inspect',f.PREFIX+'-gateway').stdout)[0]
            cls.ports = {port:int(value['NetworkSettings']['Ports'][str(port)+'/tcp'][0]['HostPort']) for port in (15223,15443)}
            cls.bindings = value['HostConfig']['PortBindings']
        except BaseException:
            f.stop(); raise

    @classmethod
    def tearDownClass(cls):
        logs=f.docker('logs',f.PREFIX+'-gateway',check=False)
        (f.RUN/'gateway.log').write_text(logs.stdout+logs.stderr)
        for process in cls.drivers:
            if process.poll() is None:
                process.stdin.write('quit\n'); process.stdin.flush()
                process.wait(timeout=10)
            process.stdin.close(); process.stdout.close(); process._native_stderr.close()
        f.stop()

    def setUp(self):
        self.restore_policy()

    def tearDown(self):
        self.restore_policy()

    def restore_policy(self):
        f.atomic_policy([f.fingerprint('alice'),f.fingerprint('bob')])
        expected=hashlib.sha256((f.RUN/'gateway/policy.json').read_bytes()).hexdigest()
        started=time.monotonic()
        # Read the consumer's mounted view, not just the host's successful rename.
        # This bounds fixture preparation; it does not delay revocation assertions.
        while True:
            result=f.execute('gateway','python3','-c',"import hashlib; print(hashlib.sha256(open('/gateway/policy.json','rb').read()).hexdigest())",check=False)
            observed=result.returncode==0 and result.stdout.strip()==expected
            with (f.RUN/'policy-readbacks.jsonl').open('a') as output:
                output.write(json.dumps(dict(observed=observed,seconds=time.monotonic()-started,exit_code=result.returncode,stderr=result.stderr))+'\n')
            if observed:return
            if time.monotonic()-started>=5:
                self.fail('gateway did not observe prepared policy within 5 seconds; inspect policy-readbacks.jsonl')
            time.sleep(.05)

    def driver(self, who='alice', anchor=None, name='gateway.test', limit=32, timeout=3):
        attempt=f.RUN/('driver-'+uuid.uuid4().hex)
        attempt.mkdir()
        cfg=dict(identity=str(f.RUN/who/'device.p12'),anchor=str(anchor or f.RUN/'gateway/ca.der'),
                 host='127.0.0.1',serverName=name,smpPort=self.ports[15223],xftpPort=self.ports[15443],limit=limit,timeout=timeout)
        path=attempt/'config.json'; path.write_text(json.dumps(cfg))
        errors=(attempt/'stderr.log').open('w')
        process=subprocess.Popen([str(ROOT/'.build/native-access/relay-driver'),str(path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=errors,text=True)
        process._native_stderr=errors; self.drivers.append(process)
        self.assertTrue(bool(select.select([process.stdout],[],[],10)[0]),'native listener startup timed out')
        line=process.stdout.readline()
        self.assertTrue(bool(line),'native listener exited before startup')
        value=json.loads(line)
        self.assertTrue(set(value)=={'proxy'},'native listener failed')
        auth,address=value['proxy'].split('@'); username,password=auth.split(':'); host,port=address.split(':')
        return process,username.encode(),password.encode(),(host,int(port))

    def local(self, driver, wrong=False):
        _,username,password,address=driver
        sock=socket.create_connection(address,timeout=5)
        self.addCleanup(sock.close)
        sock.sendall(b'\x05\x01\x02')
        self.assertEqual(receive(sock,2),b'\x05\x02')
        password=b'not-this-process' if wrong else password
        sock.sendall(bytes([1,len(username)])+username+bytes([len(password)])+password)
        result=receive(sock,2)
        if wrong:
            self.assertEqual(result,b'\x01\x01'); return sock
        self.assertEqual(result,b'\x01\x00')
        return sock

    def connect(self, driver, port=5223, host='relay.test'):
        sock=self.local(driver)
        name=host.encode('ascii')
        sock.sendall(bytes([5,1,0,3,len(name)])+name+port.to_bytes(2,'big'))
        self.assertEqual(receive(sock,10),bytes([5,0,0,1,0,0,0,0,0,0]))
        return sock

    def inner_tls(self, driver, port=5223):
        sock=self.connect(driver,port)
        directory='smp-config' if port==5223 else 'xftp-config'
        context=ssl.create_default_context(cafile=str(f.RUN/directory/'ca.crt'))
        context.set_alpn_protocols(['h2'] if port==8443 else [])
        secured=context.wrap_socket(sock,server_hostname='relay.test')
        self.addCleanup(secured.close)
        expected=ssl.PEM_cert_to_DER_cert((f.RUN/directory/'server.crt').read_text())
        self.assertEqual(secured.getpeercert(binary_form=True),expected)
        return secured

    def test_00_active_preserves_real_inner_tls(self):
        driver=self.driver()
        for port in (5223,8443):
            with self.subTest(protocol=port):
                secured=self.inner_tls(driver,port)
                self.assertIn(secured.version(),('TLSv1.2','TLSv1.3'))

    def test_01_local_authentication_and_process_separation(self):
        first=self.driver(); second=self.driver()
        self.assertTrue(first[1:3]!=second[1:3],'process credentials must differ')
        sock=self.local(first,wrong=True)
        self.assertEqual(sock.recv(1),b'')
        sock=socket.create_connection(first[3],timeout=5); self.addCleanup(sock.close)
        sock.sendall(b'\x05\x01\x00')
        self.assertEqual(receive(sock,2),b'\x05\xff')
        # Use the other process credential at the first listener.
        mixed=(first[0],second[1],second[2],first[3])
        sock=socket.create_connection(mixed[3],timeout=5); self.addCleanup(sock.close)
        sock.sendall(b'\x05\x01\x02'); self.assertEqual(receive(sock,2),b'\x05\x02')
        sock.sendall(bytes([1,len(mixed[1])])+mixed[1]+bytes([len(mixed[2])])+mixed[2])
        self.assertEqual(receive(sock,2),b'\x01\x01')

    def test_02_destination_sentinel_and_port_are_denied(self):
        driver=self.driver()
        sentinel=socket.socket(); sentinel.bind(('127.0.0.1',0)); sentinel.listen(); sentinel.settimeout(.3)
        self.addCleanup(sentinel.close)
        control=socket.create_connection(sentinel.getsockname(),timeout=5); control.close()
        accepted,_=sentinel.accept(); accepted.close()
        for host,port in [('127.0.0.1',sentinel.getsockname()[1]),('sentinel.test',5223),('relay.test',443)]:
            sock=self.local(driver); value=host.encode()
            sock.sendall(bytes([5,1,0,3,len(value)])+value+port.to_bytes(2,'big'))
            self.assertEqual(receive(sock,10),bytes([5,2,0,1,0,0,0,0,0,0]))
        with self.assertRaises(socket.timeout):sentinel.accept()

    def test_03_unknown_device_cannot_handshake_inner(self):
        driver=self.driver('unknown')
        for port in (5223,8443):
            with self.subTest(protocol=port):
                with self.assertRaises((EOFError,ssl.SSLError,OSError)):self.inner_tls(driver,port)

    def test_04_wrong_gateway_hostname_and_ca_are_denied(self):
        for cfg in [dict(name='not-the-gateway.test'),dict(anchor=f.RUN/'smp-config/server.crt')]:
            # PEM is not DER; convert an unrelated valid certificate to isolate trust failure.
            if 'anchor' in cfg:
                anchor=f.RUN/'unrelated.der'
                anchor.write_bytes(ssl.PEM_cert_to_DER_cert(cfg['anchor'].read_text()))
                cfg['anchor']=anchor
            driver=self.driver(**cfg)
            with self.assertRaises((EOFError,ssl.SSLError,OSError)):self.inner_tls(driver)

    def test_05_revocation_and_policy_failure_cut_streams(self):
        driver=self.driver()
        for unavailable in (False,True):
            with self.subTest(unavailable=unavailable):
                streams=[self.inner_tls(driver,p) for p in (5223,8443)]
                started=time.monotonic()
                if unavailable:(f.RUN/'gateway/policy.json').unlink()
                else:f.atomic_policy([f.fingerprint('bob')])
                for stream in streams:
                    stream.settimeout(5)
                    while stream.recv(65536):pass
                self.assertLess(time.monotonic()-started,60)
                with self.assertRaises((EOFError,ssl.SSLError,OSError)):self.inner_tls(driver)
                self.restore_policy()

    def test_06_timeout_and_connection_limit(self):
        driver=self.driver(limit=2,timeout=1)
        one=socket.create_connection(driver[3],timeout=5); self.addCleanup(one.close)
        two=socket.create_connection(driver[3],timeout=5); self.addCleanup(two.close)
        time.sleep(.05)
        three=socket.create_connection(driver[3],timeout=5); self.addCleanup(three.close)
        self.assertEqual(three.recv(1),b'')
        self.assertEqual(one.recv(1),b''); self.assertEqual(two.recv(1),b'')
        # Closing timed-out sessions must release capacity.
        self.inner_tls(driver)

    def test_07_stop_closes_listener_and_streams(self):
        driver=self.driver(); stream=self.inner_tls(driver)
        driver[0].stdin.write('stop\n'); driver[0].stdin.flush()
        self.assertTrue(bool(select.select([driver[0].stdout],[],[],5)[0]))
        self.assertEqual(json.loads(driver[0].stdout.readline()),{'stopping':True})
        stream.settimeout(5)
        while stream.recv(65536):pass
        with self.assertRaises(OSError):socket.create_connection(driver[3],timeout=1)

    def test_08_bindings_are_loopback_only(self):
        self.assertEqual(set(self.bindings),{'15223/tcp','15443/tcp'})
        for bindings in self.bindings.values():
            self.assertTrue(all(value['HostIp']=='127.0.0.1' for value in bindings))
        driver=self.driver()
        with self.assertRaises(OSError):socket.create_connection(('::1',driver[3][1]),timeout=.3)

    def test_09_outer_tunnel_does_not_replace_inner_trust(self):
        driver=self.driver()
        for port in (5223,8443):
            with self.subTest(protocol=port):
                sock=self.connect(driver,port)
                wrong=ssl.create_default_context(cafile=str(f.RUN/'gateway/ca.crt'))
                with self.assertRaises(ssl.SSLCertVerificationError):
                    wrong.wrap_socket(sock,server_hostname='relay.test')


if __name__=='__main__':
    print('Native transport fixture:',f.SLUG,flush=True)
    program=unittest.main(verbosity=2,exit=False)
    result=program.result
    hashes={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [
        Path(__file__),ROOT/'tools/taverna/access_proof/fixture.py',ROOT/'tools/taverna/access_proof/gateway.py',
        ROOT/'apps/ios/SimpleXChat/Taverna/SocksCodec.swift',ROOT/'apps/ios/SimpleXChat/Taverna/RelayTransport.swift',
        ROOT/'tools/taverna/native_access_tests/RelayDriver.swift',ROOT/'.build/native-access/relay-driver']}
    receipt=dict(command=sys.argv,run=f.SLUG,tests=result.testsRun,failures=result.failures,errors=result.errors,
                 skipped=len(result.skipped),successful=result.wasSuccessful(),source_sha256=hashes)
    # Tracebacks are local evidence. Do not serialize test objects or capabilities.
    receipt['failures']=[text for _,text in result.failures]
    receipt['errors']=[text for _,text in result.errors]
    if f.RUN.exists():
        with (f.RUN/'native-test-receipt.json').open('x') as output:json.dump(receipt,output,indent=2)
    sys.exit(0 if result.wasSuccessful() else 1)
