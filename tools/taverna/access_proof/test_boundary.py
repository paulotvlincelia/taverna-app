"""Live integration checks for the explicit disposable fixture, never production."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest
import uuid

import fixture as f


class BoundaryProof(unittest.TestCase):
    def setUp(self):
        f.atomic_policy([f.fingerprint('alice'),f.fingerprint('bob')])
        self.addCleanup(f.atomic_policy,[f.fingerprint('alice'),f.fingerprint('bob')])
        time.sleep(.3)

    def assert_denied(self,who,port,no_cert=False):
        args=['python3','/source/client.py','probe',str(port)]
        if no_cert:args+=['--no-cert']
        result=json.loads(f.execute(who,*args).stdout)
        self.assertEqual(result,{'allowed_bytes':False})

    def open_stream(self,port):
        process=subprocess.Popen([f.DOCKER,'exec',f.PREFIX+'-alice','python3','/source/client.py','hold',str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.addCleanup(lambda: process.poll() is None and process.terminate())
        self.assertEqual(process.stdout.readline().strip(),'OPEN')
        return process

    def assert_closed(self,process):
        try:
            stdout,stderr=process.communicate(timeout=4)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.communicate(timeout=3)
            self.fail('existing stream not closed within the observed 4-second bound')
        self.assertEqual(process.returncode,0,stderr)
        value=json.loads(stdout)
        self.assertIs(value['closed'],True)
        self.assertLess(value['seconds'],60)

    def test_00_active_device_reaches_both_real_backends(self):
        for port in (15223,15443):
            result=json.loads(f.execute('alice','python3','/source/client.py','probe',str(port)).stdout)
            self.assertEqual(result,{'allowed_bytes':True})

    def test_01_real_smp_two_way(self):
        contacts=f.api('alice','/contacts')['contacts']
        if not contacts:
            invite=f.api('alice','/_connect 1')
            self.assertEqual(invite['type'],'invitation')
            connect=f.api('bob','/connect '+invite['connLinkInvitation']['connFullLink'])
            self.assertEqual(connect['type'],'sentConfirmation')
        for sender,recipient in [('alice','bob'),('bob','alice')]:
            message='Taverna synthetic proof '+uuid.uuid4().hex
            response=f.api(sender,'@Proof-'+recipient+' '+message)
            self.assertEqual(response['type'],'newChatItems')
            deadline=time.monotonic()+10
            while True:
                response=f.api(recipient,'/tail @Proof-'+sender+' 20')
                values=[x['chatItem']['content'] for x in response.get('chatItems',[])]
                if {'type':'rcvMsgContent','msgContent':{'type':'text','text':message}} in values:break
                if time.monotonic()>deadline:self.fail('exact SMP message was not received')
                time.sleep(.2)
            self.assertIn({'type':'rcvMsgContent','msgContent':{'type':'text','text':message}},values)

    def upload(self):
        name='payload-'+uuid.uuid4().hex+'.bin'
        payload=(b'Taverna synthetic bytes, no private data.\n'*2048)
        (f.RUN/'alice/files'/name).write_bytes(payload)
        fp=(f.RUN/'xftp-config/fingerprint').read_text().strip()
        result=f.execute('alice','/bin-proof/xftp-ubuntu-24_04-aarch64','send','/client/files/'+name,'/client/files','-s',f'xftp://{fp}@localhost:18443','-r','1','--tmp','/client/tmp')
        self.assertIn('File uploaded!',result.stdout)
        description=f.RUN/'alice/files'/(name+'.xftp')/'rcv1.xftp'
        self.assertTrue(description.is_file())
        return name,payload,description

    def test_02_real_xftp_exact_bytes(self):
        name,payload,description=self.upload()
        (f.RUN/'bob/files'/'rcv.xftp').write_bytes(description.read_bytes())
        f.execute('bob','/bin-proof/xftp-ubuntu-24_04-aarch64','recv','/client/files/rcv.xftp','/client/files','-r','1','--tmp','/client/tmp','-y')
        received=f.RUN/'bob/files'/name
        self.assertTrue(received.is_file())
        self.assertEqual(received.read_bytes(),payload)

    def test_03_missing_certificate(self):
        for port in (15223,15443):
            with self.subTest(port=port):self.assert_denied('alice',port,no_cert=True)

    def test_04_unknown_device_same_ca(self):
        for port in (15223,15443):
            with self.subTest(port=port):self.assert_denied('unknown',port)

    def test_05_revocation_cuts_open_sessions_and_new_access(self):
        streams=[self.open_stream(port) for port in (15223,15443)]
        f.atomic_policy([f.fingerprint('bob')])
        for process in streams:self.assert_closed(process)
        for port in (15223,15443):self.assert_denied('alice',port)

    def test_06_missing_policy_fails_closed(self):
        streams=[self.open_stream(port) for port in (15223,15443)]
        (f.RUN/'gateway/policy.json').unlink()
        for process in streams:self.assert_closed(process)
        for port in (15223,15443):self.assert_denied('alice',port)

    def test_07_invalid_policy_fails_closed(self):
        for bad in ('{','null','{"schema":1,"active":"all"}','{"schema":true,"active":[]}', '{"schema":2,"active":[]}', '{"schema":1,"active":[123]}', '{"schema":1,"active":["bad"]}', '{}'):
            with self.subTest(policy=bad):
                f.atomic_policy([f.fingerprint('alice'),f.fingerprint('bob')])
                streams=[self.open_stream(port) for port in (15223,15443)]
                (f.RUN/'gateway/policy.json').write_text(bad)
                for process in streams:self.assert_closed(process)
                for port in (15223,15443):self.assert_denied('alice',port)

    def test_08_revoked_device_cannot_fetch_existing_file(self):
        name,payload,description=self.upload()
        (f.RUN/'alice/files'/'rcv-revoked.xftp').write_bytes(description.read_bytes())
        f.atomic_policy([f.fingerprint('bob')])
        time.sleep(.3)
        denied_name='denied-'+uuid.uuid4().hex
        denied=f.RUN/'alice/files'/denied_name
        denied.mkdir()
        result=f.execute('alice','/bin-proof/xftp-ubuntu-24_04-aarch64','recv','/client/files/rcv-revoked.xftp','/client/files/'+denied_name,'-r','0','--tmp','/client/tmp','-y',check=False)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(list(denied.iterdir()),[])
        (f.RUN/'bob/files'/'rcv-active.xftp').write_bytes(description.read_bytes())
        f.execute('bob','/bin-proof/xftp-ubuntu-24_04-aarch64','recv','/client/files/rcv-active.xftp','/client/files','-r','1','--tmp','/client/tmp','-y')
        self.assertEqual((f.RUN/'bob/files'/name).read_bytes(),payload)

    def test_09_only_internal_networks_no_public_ports(self):
        for network in ('inner','outer'):
            info=json.loads(f.docker('network','inspect',f.PREFIX+'-'+network).stdout)[0]
            self.assertIs(info['Internal'],True)
        for name in f.NAMES:
            info=json.loads(f.docker('inspect',name).stdout)[0]
            self.assertFalse(info['HostConfig']['PortBindings'])
            self.assertFalse(info['HostConfig']['Privileged'])
            self.assertIs(info['HostConfig']['ReadonlyRootfs'],True)
        relay=json.loads(f.docker('inspect',f.PREFIX+'-relay').stdout)[0]
        address=relay['NetworkSettings']['Networks'][f.PREFIX+'-inner']['IPAddress']
        for port in (5223,8443):
            code='import socket; s=socket.create_connection(('+repr(address)+','+str(port)+'),timeout=1)'
            result=f.execute('alice','python3','-c',code,check=False)
            self.assertNotEqual(result.returncode,0,'direct backend bypass')


    def test_10_fixed_backends_do_not_follow_client_destination(self):
        pid_file=f.RUN/'unknown/sentinel-pid'
        pid_file.unlink(missing_ok=True)
        f.docker('exec','-d',f.PREFIX+'-unknown','python3','/source/client.py','sentinel')
        deadline=time.monotonic()+3
        while not pid_file.exists():
            if time.monotonic()>deadline:self.fail('sentinel not ready')
            time.sleep(.05)
        pid=int(pid_file.read_text())
        self.addCleanup(f.execute,'unknown','kill',str(pid))
        direct=f.execute('alice','python3','-c',"import socket; s=socket.create_connection(('unknown',19000),timeout=2); print(s.recv(8).decode()); s.close()")
        self.assertEqual(direct.stdout.strip(),'SENTINEL')
        counter=f.RUN/'unknown/sentinel-count'
        self.assertEqual(counter.read_text(),'1')
        f.execute('alice','python3','/source/client.py','redirect')
        time.sleep(.1)
        self.assertEqual(counter.read_text(),'1','client-supplied destination reached sentinel')


if __name__=='__main__':unittest.main(verbosity=2)
