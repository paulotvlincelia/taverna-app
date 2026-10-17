"""NP-04/07/08: system-invoked Share Extension, never an in-process substitute."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import signal
import socket
import threading
import subprocess
import sys
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools/taverna'))
import ios_session as session
import ios_proof as proof

CHECKS = ['no_controller_without_transport', 'missing_start_denied', 'missing_resume_denied',
          'core_still_stopped', 'listener_ready', 'cold_model_started', 'managed_network',
          'mandatory_socks_mode', 'capability_not_persisted', 'smp_protocol', 'xftp_protocol',
          'smp_no_direct_fallback', 'xftp_no_direct_fallback', 'suspended', 'model_resumed', 'resumed_managed_network', 'core_stopped',
          'stopped_start_denied', 'stopped_resume_denied', 'core_remains_stopped']


class LoopbackSentinel:
    """Observable positive control; never uses a production address."""
    def __init__(self):
        self.count = 0
        self.listener = socket.socket()
        self.listener.bind(('127.0.0.1', 0))
        self.listener.listen()
        self.listener.settimeout(.1)
        self.port = self.listener.getsockname()[1]
        self.stopped = threading.Event()
        def serve():
            while not self.stopped.is_set():
                try: connection, _ = self.listener.accept()
                except socket.timeout: continue
                with connection:
                    self.count += 1
                    connection.sendall(b'!')
        self.thread = threading.Thread(target=serve, daemon=True)
        self.thread.start()

    def positive_control(self):
        with socket.create_connection(('127.0.0.1', self.port), timeout=2) as connection:
            if connection.recv(1) != b'!': raise AssertionError('sentinel positive control failed')

    def close(self):
        self.stopped.set()
        self.thread.join(timeout=2)
        self.listener.close()


class ShareStartup(unittest.TestCase):
    def test_system_invoked_share_process(self):
        build_path = session.inside(ROOT, Path(os.environ['TAVERNA_NATIVE_BUILD']))
        build = json.loads(build_path.read_text())
        proof.validate_stage('share build', build)
        commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        state = subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
        self.assertEqual(build['commit'], commit)
        if os.environ.get('TAVERNA_NATIVE_ALLOW_DIRTY') != '1':
            self.assertEqual(build['source_state'], '')
            self.assertEqual(state, '')
        self.assertEqual(len(build['products']), 4)
        for product in build['products']: proof.artifact(ROOT, product)
        owned = json.loads((ROOT/'.build/ios-session.json').read_text())
        session.validate_sdk_indexes(owned)
        session.validate_session(ROOT, owned, owned['udid'])
        manifest_path = session.inside(ROOT, Path(os.environ.get('TAVERNA_NATIVE_GUARD', '.build/attempts/guard/guard-manifest.json')))
        session.validate_guard(ROOT, json.loads(manifest_path.read_text()))
        slug = 'share-'+uuid.uuid4().hex[:8]
        os.environ['TAVERNA_PROOF_RUN'] = slug
        spec = importlib.util.spec_from_file_location('share_fixture_'+slug, ROOT/'tools/taverna/access_proof/fixture.py')
        f = importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
        request = ROOT/'.build/share-probe-request.txt'
        self.assertFalse(request.exists(), 'preserve existing qualification request')
        f.initialize()
        try:
            sentinel = LoopbackSentinel()
            sentinel.positive_control()
            self.assertEqual(sentinel.count, 1)
            f.start(native=True)
            directory = f.RUN/'ios'; directory.mkdir()
            gateway = json.loads(f.docker('inspect',f.PREFIX+'-gateway').stdout)[0]
            ports = {p:int(gateway['NetworkSettings']['Ports'][str(p)+'/tcp'][0]['HostPort']) for p in (15223,15443)}
            cfg = dict(sentinelPort=sentinel.port, identity=str(f.RUN/'alice/device.p12'), anchor=str(f.RUN/'gateway/ca.der'),
                       smpPort=ports[15223], xftpPort=ports[15443],
                       smpServer='smp://'+(f.RUN/'smp-config/fingerprint').read_text().strip()+'@relay.test:5223',
                       xftpServer='xftp://'+(f.RUN/'xftp-config/fingerprint').read_text().strip()+'@relay.test:8443')
            config = directory/'config.json'; config.write_text(json.dumps(cfg))
            request.write_text(str(config)+'\n'+('discovery\n' if os.environ.get('TAVERNA_SHARE_DISCOVERY_ONLY')=='1' else 'socket-test\n' if os.environ.get('TAVERNA_SHARE_SOCKET_TEST')=='1' else ''))
            products = ROOT/'.build/DerivedData/Build/Products'
            plans = list(products.glob('SimpleX (iOS)_iphonesimulator*-arm64.xctestrun'))
            self.assertEqual(len(plans), 1)
            plan = plistlib.loads(plans[0].read_bytes())
            self.assertEqual(plan['__xctestrun_metadata__']['FormatVersion'], 1)
            target = plan['Tests iOS']
            target['OnlyTestIdentifiers'] = ['TavernaShareTests/testSystemShareExtension']
            target.pop('SkipTestIdentifiers', None)
            target.setdefault('EnvironmentVariables', {}).update(TAVERNA_UI_ROOT=str(ROOT),
                TAVERNA_GUARD_MANIFEST=str(manifest_path), TAVERNA_UI_ATTEMPT=str(directory),
                TAVERNA_UI_PROFILE='first-build', TAVERNA_SHARE_CONFIG=str(config))
            # Qualification has its own named test. Existing onboarding methods/assertions remain intact.
            configured = products/('Taverna-'+slug+'.xctestrun'); configured.write_bytes(plistlib.dumps(plan))
            (directory/'share.xctestrun.plist').write_bytes(configured.read_bytes())
            command = ['xcodebuild','test-without-building','-xctestrun',str(configured),
                       '-destination','platform=iOS Simulator,id='+owned['udid'], '-parallel-testing-enabled','NO',
                       '-resultBundlePath',str(directory/'share.xcresult')]
            with (directory/'ui.stdout.log').open('w') as stdout, (directory/'ui.stderr.log').open('w') as stderr:
                result = subprocess.run(command,cwd=ROOT,env=session.environment(ROOT),stdout=stdout,stderr=stderr,timeout=300)
            (directory/'ui-command.json').write_text(json.dumps(dict(command=command,exit_code=result.returncode)))
            self.assertEqual(result.returncode, 0, 'share UI gate failed; inspect ignored logs')
            summary = subprocess.run(['xcrun','xcresulttool','get','test-results','summary','--path',str(directory/'share.xcresult'),
                                      '--format','json'],env=session.environment(ROOT),capture_output=True,text=True,check=True)
            counts = json.loads(summary.stdout)
            self.assertEqual(counts['passedTests'], 1)
            self.assertEqual(counts['failedTests'], 0)
            self.assertEqual(counts['skippedTests'], 0)
            value = json.loads((directory/'share-result.json').read_text())
            self.assertEqual(value['status'], 'PASS')
            self.assertEqual(value['checks'], CHECKS)
            time.sleep(.3)
            self.assertEqual(sentinel.count, 1, 'extension bypass reached unauthorized loopback sentinel')
            value['sentinel'] = dict(positive_control_connections=1, unauthorized_connections=0)
            self.assertEqual(value['process'], 'SimpleX SE')
            self.assertGreater(value['pid'], 0)
            guard = [json.loads(line) for line in (directory/'share-before-main.jsonl').read_text().splitlines()]
            self.assertTrue(any(e['pid']==value['pid'] and e['executable']=='SimpleX SE' and e['phase']=='before_main' and
                                e['loopback'] is True and e['ipv4_errno'] in (1,13) and e['ipv6_errno'] in (1,13) for e in guard))
            mechanism = 'test_socket_interposition' if os.environ.get('TAVERNA_SHARE_SOCKET_TEST')=='1' else 'kernel_sandbox'
            self.assertTrue(any(e.get('mechanism')==mechanism and e['pid']==value['pid'] for e in guard))
            value['test_containment'] = mechanism
            audit = f.docker('logs',f.PREFIX+'-gateway').stdout
            (directory/'gateway.log').write_text(audit)
            events = [json.loads(line) for line in audit.splitlines() if line.startswith('{')]
            self.assertEqual({e['protocol'] for e in events if e['event']=='authorized_after_backend'}, {'smp','xftp'})
            for path in directory.glob('*.json*'):
                if path.name not in ('config.json','share.xctestrun'):
                    self.assertNotRegex(path.read_text(errors='replace'), r'[0-9a-f]{64}:[0-9a-f]{64}@127\.0\.0\.1:')
            self.assertEqual(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),state)
            self.assertEqual(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),commit)
            value.update(commit=commit,source_state=state,qualification_mode='development' if state else 'clean',
                         build_receipt_sha256=hashlib.sha256(build_path.read_bytes()).hexdigest(),
                         products=build['products'],udid=owned['udid'],ui_counts=counts,
                         source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                             [ROOT/'apps/ios/SimpleX SE'/name for name in ('ShareAPI.swift','ShareModel.swift','ShareProbe.swift','ShareProbeGuard.c')]+[Path(__file__)]})
            (directory/'share-driver-receipt.json').write_text(json.dumps(value,indent=2))
        finally:
            if 'sentinel' in locals(): sentinel.close()
            if request.exists() and 'config' in locals() and request.read_text() in (str(config)+'\n', str(config)+'\ndiscovery\n', str(config)+'\nsocket-test\n'): request.unlink()
            if 'directory' in locals():
                guard_file=directory/'share-before-main.jsonl'
                events=list(map(json.loads,guard_file.read_text().splitlines())) if guard_file.exists() else []
                if (directory/'share-result.json').exists(): events.append(json.loads((directory/'share-result.json').read_text()))
                for event in events:
                    pid=event['pid']
                    process=subprocess.run(['ps','-p',str(pid),'-o','comm='],capture_output=True,text=True).stdout.strip()
                    if process.startswith(owned['storage']+'/data/Containers/Bundle/Application/') and process.endswith('/SimpleX SE.appex/SimpleX SE'):
                        try: os.kill(pid,signal.SIGTERM)
                        except ProcessLookupError: pass
            f.stop()


if __name__=='__main__': unittest.main(verbosity=2)
