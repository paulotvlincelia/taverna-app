"""Owned simulator + fixture controls for native payload qualification only."""
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import socket
import subprocess
import sys
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools/taverna'))
import ios_proof as proof
import ios_session as session


def normalize(value):
    # Only the C API's top-level tagged union differs from the CLI encoding.
    if 'result' in value:
        result = {key:body for key,body in value['result'].items() if key != '_owsf'}
        if not isinstance(result, dict) or len(result) != 1:
            raise ValueError('invalid core result')
        tag, body = next(iter(result.items()))
        return dict(body, type=tag)
    if 'error' in value:
        raise ValueError('core error; inspect ignored fixture response')
    return value


class PayloadSession:
    def __init__(self, case):
        self.case = case
        self.sequence = 0
        self.peer_sequence = 0
        self.frames = []
        self.lock = threading.Lock()
        self.evidence = []
        self.process = None
        self.bundle = None
        self.peer_log = None
        slug = 'payload-'+uuid.uuid4().hex[:8]
        os.environ['TAVERNA_PROOF_RUN'] = slug
        spec = importlib.util.spec_from_file_location('payload_fixture_'+slug, ROOT/'tools/taverna/access_proof/fixture.py')
        self.f = importlib.util.module_from_spec(spec); spec.loader.exec_module(self.f)
        self.directory = self.f.RUN/'ios'

    def wait(self, predicate, seconds, label):
        deadline = time.monotonic()+seconds
        while time.monotonic() < deadline:
            result = predicate()
            if result: return result
            time.sleep(.1)
        self.case.fail(label+' timed out; inspect ignored fixture')

    def sim(self, *args, check=True, env=None):
        result = subprocess.run(['xcrun','simctl',*map(str,args)], cwd=ROOT,
                                env=env or session.environment(ROOT), capture_output=True, text=True, timeout=120)
        with (self.directory/'commands.jsonl').open('a') as output:
            output.write(json.dumps(dict(args=list(map(str,args)), exit_code=result.returncode,
                                         stdout=result.stdout, stderr=result.stderr))+'\n')
        if check: self.case.assertEqual(result.returncode, 0, 'simctl failed; inspect ignored command log')
        return result

    def start(self):
        c = self.case
        self.build_path = session.inside(ROOT, Path(os.environ['TAVERNA_NATIVE_BUILD']))
        self.build = json.loads(self.build_path.read_text())
        proof.validate_stage('native payload build', self.build)
        self.commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
        self.state = subprocess.check_output(['git','status','--porcelain'], cwd=ROOT, text=True)
        c.assertEqual(self.build['commit'], self.commit)
        if os.environ.get('TAVERNA_NATIVE_ALLOW_DIRTY') != '1':
            c.assertEqual(self.build['source_state'], '')
            c.assertEqual(self.state, '')
        c.assertEqual(len(self.build['products']), 4)
        for product in self.build['products']: proof.artifact(ROOT, product)
        self.source_paths = [Path(__file__), Path(__file__).with_name('test_payload.py'),
                             ROOT/'apps/ios/Shared/TavernaNativeProbe.swift', ROOT/'apps/ios/Shared/Model/SimpleXAPI.swift',
                             *sorted((ROOT/'apps/ios/SimpleXChat/Taverna').glob('*.swift')),
                             *[ROOT/'tools/taverna/access_proof'/name for name in ('client.py','fixture.py','gateway.py')]]
        self.source_hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source_paths}
        self.owned = json.loads((ROOT/'.build/ios-session.json').read_text())
        session.validate_sdk_indexes(self.owned)
        session.validate_session(ROOT, self.owned, self.owned['udid'])
        guards = json.loads((session.inside(ROOT, Path(os.environ.get('TAVERNA_NATIVE_GUARD', '.build/attempts/guard/guard-manifest.json')))).read_text())
        session.validate_guard(ROOT, guards)
        components = {Path(p).name:p for p in guards}
        self.app_path = ROOT/'.build/DerivedData/Build/Products/Debug-iphonesimulator/SimpleX.app'
        self.bundle = plistlib.loads((self.app_path/'Info.plist').read_bytes())['CFBundleIdentifier']
        self.f.initialize()
        self.f.start(native=True, transfer_delay=.015)
        self.f.clients(native=True, people=('bob',))
        self.directory.mkdir()
        gateway = json.loads(self.f.docker('inspect',self.f.PREFIX+'-gateway').stdout)[0]
        ports = {p:int(gateway['NetworkSettings']['Ports'][str(p)+'/tcp'][0]['HostPort']) for p in (15223,15443)}
        self.cfg = dict(identity=str(self.f.RUN/'alice/device.p12'), anchor=str(self.f.RUN/'gateway/ca.der'),
                        smpPort=ports[15223], xftpPort=ports[15443], mode='payload',
                        smpServer='smp://'+(self.f.RUN/'smp-config/fingerprint').read_text().strip()+'@relay.test:5223',
                        xftpServer='xftp://'+(self.f.RUN/'xftp-config/fingerprint').read_text().strip()+'@relay.test:8443')
        config = self.directory/'config.json'; config.write_text(json.dumps(self.cfg))
        self.peer_log = (self.f.RUN/'bob/session.stderr.log').open('w')
        self.process = subprocess.Popen([self.f.DOCKER,'exec','-i',self.f.PREFIX+'-bob','python3','/source/client.py','session'],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.peer_log, text=True, bufsize=1)
        def read_peer():
            for line in self.process.stdout:
                value = json.loads(line)
                with self.lock: self.frames.append(value)
                with (self.f.RUN/'bob/events.jsonl').open('a') as log: log.write(json.dumps(value)+'\n')
        self.reader = threading.Thread(target=read_peer, daemon=True); self.reader.start()
        self.sim('boot',self.owned['udid'], check=False)
        self.sim('bootstatus',self.owned['udid'],'-b')
        self.sim('install',self.owned['udid'],self.app_path)
        env = session.environment(ROOT)
        values = dict(DYLD_INSERT_LIBRARIES=components['process-guard.dylib'], TAVERNA_HOST_GUARD=components['host-sandbox'],
                      TAVERNA_GUARD_LOG=str(self.directory/'before-main.jsonl'), TAVERNA_NATIVE_PROBE=str(config))
        env.update({'SIMCTL_CHILD_'+k:v for k,v in values.items()})
        self.sim('launch','--terminate-running-process','--stdout='+str(self.directory/'app.stdout.log'),
                 '--stderr='+str(self.directory/'app.stderr.log'),self.owned['udid'],self.bundle,env=env)
        self.wait(lambda: (self.directory/'payload-ready.json').exists() or (self.directory/'startup-result.json').exists(), 90, 'payload startup')
        c.assertTrue((self.directory/'payload-ready.json').exists(), 'payload bootstrap failed; inspect startup result')
        ready = json.loads((self.directory/'payload-ready.json').read_text())
        c.assertEqual(ready['process'], 'SimpleX')
        c.assertIs(ready['exclusive_servers'], True)
        guards = [json.loads(line) for line in (self.directory/'before-main.jsonl').read_text().splitlines()]
        c.assertTrue(any(e['pid'] == ready['pid'] and e['phase'] == 'before_main' and e['loopback'] is True and
                         e['ipv4_errno'] in (1,13) and e['ipv6_errno'] in (1,13) for e in guards))
        self.ready = ready
        self.wait(lambda: self.peer('/u').get('type') == 'activeUser', 15, 'peer WebSocket')

    def app(self, command):
        self.sequence += 1
        request = self.directory/f'request-{self.sequence}.json'
        temporary = request.with_suffix('.tmp'); temporary.write_text(json.dumps({'command':command})); temporary.replace(request)
        response = self.directory/f'response-{self.sequence}.json'
        self.wait(response.exists, 75, 'app command')
        return normalize(json.loads(response.read_text()))

    def peer(self, command):
        self.peer_sequence += 1
        correlation = str(self.peer_sequence)
        self.process.stdin.write(json.dumps({'corrId':correlation,'cmd':command})+'\n'); self.process.stdin.flush()
        def find():
            with self.lock:
                return next((f['resp'] for f in self.frames if f.get('corrId') == correlation), None)
        return self.wait(find, 30, 'peer command')

    @staticmethod
    def contents(response):
        values = []
        for item in response.get('chatItems', []):
            content = item['chatItem']['content']
            if 'rcvMsgContent' in content: content = dict(content['rcvMsgContent'], type='rcvMsgContent')
            values.append(content)
        return values

    def files(self, who):
        return (self.directory if who == 'ios' else self.f.RUN/'bob')/'files'

    def client_path(self, who, name):
        return str(self.files('ios')/name) if who == 'ios' else '/client/files/'+name

    def events(self, who):
        if who == 'ios':
            path = self.directory/'events.jsonl'
            lines = path.read_text().splitlines() if path.exists() else []
            # FileHandle appends each event in one write; incomplete last lines wait for next poll.
            return [json.loads(line) for line in lines if line.endswith('}')]
        with self.lock: frames = list(self.frames)
        result = []
        for frame in frames:
            if frame.get('corrId') is not None: continue
            event = frame.get('resp', {})
            meta = event.get('fileTransferMeta', event.get('rcvFileTransfer', {}))
            result.append(dict(event, fileId=meta.get('fileId')))
        return result

    def event(self, who, kind, file_id, seconds, predicate=lambda x: True):
        return self.wait(lambda: next((e for e in self.events(who) if e.get('type') == kind and
                                     e.get('fileId') == file_id and predicate(e)), None), seconds, kind)

    def audit(self):
        logs = self.f.docker('logs',self.f.PREFIX+'-gateway').stdout
        (self.directory/'gateway.log').write_text(logs)
        return [json.loads(line) for line in logs.splitlines() if line.startswith('{')]

    def active_connections(self):
        audit = self.audit()
        ended = {e['connection'] for e in audit if e['event'] in
                 ('client_stream_ended','backend_stream_ended','authorization_ended','transport_error')}
        return [e for e in audit if e['event'] == 'authorized_after_backend' and e['connection'] not in ended]

    def deny(self, mode):
        if mode == 'revoke': self.f.atomic_policy([self.f.fingerprint('bob')])
        elif mode == 'missing': (self.f.RUN/'gateway/policy.json').unlink()
        else: raise ValueError('unknown denial')

    def closed_by_authorization(self, active):
        audit = self.audit()
        ended = {e['connection'] for e in audit if e['event'] == 'authorization_ended'}
        closed = {e['connection'] for e in audit if e['event'] == 'streams_closed'}
        return all(e['connection'] in ended and e['connection'] in closed for e in active)

    @contextmanager
    def sentinel(self):
        class Sentinel:
            count = 0
            def positive_control(self):
                with socket.create_connection(('127.0.0.1',self.port), timeout=2) as sock:
                    self_control = sock.recv(1)
                    if self_control != b'!': raise AssertionError('sentinel positive control failed')
        probe = Sentinel()
        with socket.socket() as listener:
            listener.bind(('127.0.0.1',0)); listener.listen(); listener.settimeout(.1)
            probe.port = listener.getsockname()[1]
            stopped = threading.Event()
            def serve():
                while not stopped.is_set():
                    try: connection,_ = listener.accept()
                    except socket.timeout: continue
                    with connection:
                        probe.count += 1
                        connection.sendall(b'!')
            thread = threading.Thread(target=serve, daemon=True); thread.start()
            try: yield probe
            finally: stopped.set(); thread.join(timeout=2)

    def record(self, check):
        for product in self.build['products']: proof.artifact(ROOT, product)
        current = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source_paths}
        self.case.assertEqual(current, self.source_hashes, 'source changed during qualification')
        self.case.assertEqual(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), self.commit)
        self.case.assertEqual(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True), self.state)
        for name in ('app.stdout.log','app.stderr.log','events.jsonl'):
            self.case.assertNotRegex((self.directory/name).read_text(errors='replace'), r'[0-9a-f]{64}:[0-9a-f]{64}@127\.0\.0\.1:')
        receipt = dict(status='CHECK_PASS', check=check, commit=self.commit, source_state=self.state,
                       qualification_mode='development' if os.environ.get('TAVERNA_NATIVE_ALLOW_DIRTY') == '1' else 'clean',
                       build_receipt_sha256=hashlib.sha256(self.build_path.read_bytes()).hexdigest(),
                       app_sha256=hashlib.sha256((self.app_path/'SimpleX').read_bytes()).hexdigest(),
                       source_sha256=self.source_hashes,
                       udid=self.owned['udid'], process=self.ready, evidence=self.evidence)
        (self.directory/'payload-receipt.json').write_text(json.dumps(receipt, indent=2))

    def close(self):
        try:
            if self.bundle and self.directory.exists():
                self.sim('terminate',self.owned['udid'],self.bundle,check=False)
                self.audit()
        finally:
            try:
                if self.process:
                    if self.process.poll() is None: self.process.terminate()
                    self.process.wait(timeout=5)
                    self.reader.join(timeout=5)
                    self.process.stdin.close()
                    self.process.stdout.close()
                if self.peer_log: self.peer_log.close()
            finally:
                self.f.stop()
