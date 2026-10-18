"""Actual app process startup gate; exclusively owned simulator and fresh fixture."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools/taverna'))
import ios_session as session
import ios_proof as proof

os.environ.setdefault('TAVERNA_PROOF_RUN', 'startup-'+uuid.uuid4().hex[:8])
spec = importlib.util.spec_from_file_location('startup_fixture', ROOT/'tools/taverna/access_proof/fixture.py')
f = importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
CHECKS = ['missing_start_denied', 'missing_resume_denied', 'core_still_stopped',
          'listener_ready', 'forced_network_config', 'mandatory_socks_mode', 'capability_not_persisted', 'core_started', 'core_running',
          'core_smp_protocol', 'core_xftp_protocol', 'resume_configured', 'core_stopped', 'stopped_start_denied', 'stopped_resume_denied']


class AppStartup(unittest.TestCase):
    def test_actual_core_startup(self):
        build_path = session.inside(ROOT, Path(os.environ['TAVERNA_NATIVE_BUILD']))
        build = json.loads(build_path.read_text())
        proof.validate_stage('native startup build', build)
        self.assertEqual(build['commit'], subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
        clean = subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
        if os.environ.get('TAVERNA_NATIVE_ALLOW_DIRTY') != '1':
            self.assertEqual(build['source_state'], '', 'final gate requires a clean build')
            self.assertEqual(clean, '', 'final gate requires clean source')
        self.assertEqual(len(build['products']), 4)
        for product in build['products']: proof.artifact(ROOT, product)
        owned = json.loads((ROOT/'.build/ios-session.json').read_text())
        session.validate_sdk_indexes(owned)
        session.validate_session(ROOT, owned, owned['udid'])
        guards = json.loads((session.inside(ROOT, Path(os.environ.get('TAVERNA_NATIVE_GUARD', '.build/attempts/guard/guard-manifest.json')))).read_text())
        session.validate_guard(ROOT, guards)
        components = {Path(p).name:p for p in guards}
        app = ROOT/'.build/DerivedData/Build/Products/Debug-iphonesimulator/SimpleX.app'
        info = plistlib.loads((app/'Info.plist').read_bytes())
        bundle = info['CFBundleIdentifier']
        f.initialize()
        try:
            f.start(native=True)
            gateway = json.loads(f.docker('inspect',f.PREFIX+'-gateway').stdout)[0]
            ports = {p:int(gateway['NetworkSettings']['Ports'][str(p)+'/tcp'][0]['HostPort']) for p in (15223,15443)}
            attempt = f.RUN/'ios'; attempt.mkdir()
            cfg = dict(identity=str(f.RUN/'alice/device.p12'), anchor=str(f.RUN/'gateway/ca.der'),
                       smpPort=ports[15223], xftpPort=ports[15443],
                       smpServer='smp://'+(f.RUN/'smp-config/fingerprint').read_text().strip()+'@relay.test:5223',
                       xftpServer='xftp://'+(f.RUN/'xftp-config/fingerprint').read_text().strip()+'@relay.test:8443')
            path=attempt/'config.json'; path.write_text(json.dumps(cfg))
            def sim(*args, check=True, env=None):
                args=list(map(str,args))
                result=subprocess.run(['xcrun','simctl',*map(str,args)],env=env or session.environment(ROOT),capture_output=True,text=True,timeout=120)
                if check and result.returncode: self.fail('simctl failed; inspect local command log')
                with (attempt/'commands.jsonl').open('a') as output: output.write(json.dumps(dict(args=args,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr))+'\n')
                return result
            sim('boot',owned['udid'],check=False)
            sim('bootstatus',owned['udid'],'-b')
            sim('install',owned['udid'],app)
            env=session.environment(ROOT)
            values=dict(DYLD_INSERT_LIBRARIES=components['process-guard.dylib'],
                        TAVERNA_HOST_GUARD=components['host-sandbox'],
                        TAVERNA_GUARD_LOG=str(attempt/'before-main.jsonl'),TAVERNA_NATIVE_PROBE=str(path))
            env.update({'SIMCTL_CHILD_'+key:value for key,value in values.items()})
            sim('launch','--terminate-running-process','--stdout='+str(attempt/'app.stdout.log'),
                '--stderr='+str(attempt/'app.stderr.log'),owned['udid'],bundle,env=env)
            receipt=attempt/'startup-result.json'
            deadline=time.monotonic()+90
            while not receipt.exists() and time.monotonic()<deadline: time.sleep(.2)
            self.assertTrue(receipt.is_file(),'app startup gate timed out; no receipt')
            value=json.loads(receipt.read_text())
            self.assertEqual(value.get('status'),'PASS','native startup assertion failed; inspect local receipt')
            self.assertEqual(value.get('checks'),CHECKS)
            self.assertEqual(value.get('process'),'SimpleX')
            self.assertGreater(value.get('pid',0),0)
            events=[json.loads(line) for line in (attempt/'before-main.jsonl').read_text().splitlines()]
            self.assertTrue(any(e['pid']==value['pid'] and e['phase']=='before_main' and e['loopback'] is True
                                and e['ipv4_errno'] in (1,13) and e['ipv6_errno'] in (1,13) for e in events))
            # Ephemeral SOCKS capability must never appear in application output or defaults.
            for log in (attempt/'app.stdout.log',attempt/'app.stderr.log',receipt):
                self.assertNotRegex(log.read_text(errors='replace'),r'[0-9a-f]{64}:[0-9a-f]{64}@127\.0\.0\.1:')
            value.update(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                         source_state=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),
                         app_sha256=hashlib.sha256((app/'SimpleX').read_bytes()).hexdigest(),udid=owned['udid'],
                         qualification_mode='development' if os.environ.get('TAVERNA_NATIVE_ALLOW_DIRTY')=='1' else 'clean',
                         build_receipt_sha256=hashlib.sha256(build_path.read_bytes()).hexdigest(),
                         source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [ROOT/'apps/ios/Shared/TavernaNativeProbe.swift',ROOT/'apps/ios/Shared/Model/SimpleXAPI.swift',
                                       ROOT/'apps/ios/SimpleXChat/Taverna/CoreTransport.swift',Path(__file__).resolve()]})
            (attempt/'driver-receipt.json').write_text(json.dumps(value,indent=2))
        finally:
            if 'attempt' in locals():
                sim('terminate',owned['udid'],bundle,check=False)
                logs=f.docker('logs',f.PREFIX+'-gateway',check=False)
                (attempt/'gateway.log').write_text(logs.stdout+logs.stderr)
            f.stop()


if __name__=='__main__': unittest.main(verbosity=2)
