from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/taverna'))
import device_fixture as fixture


class DeviceFixture(unittest.TestCase):
    def plan(self):
        return fixture.make_plan('192.168.40.2',[15223,15443],'phone-a1b2c3d4','sha256:'+'a'*64,now=2_000_000_000)

    def test_plan_is_explicit_bounded_and_has_no_live_default(self):
        p=self.plan()
        self.assertEqual(p['host'],'192.168.40.2')
        self.assertEqual(p['ports'],[15223,15443])
        self.assertEqual((p['lifetime'],p['expiresAt']),(1200,2_000_003_600))
        self.assertEqual(p['live'],'NOT RUN')
        self.assertEqual(fixture.validate_plan(p,now=2_000_000_001),p)
        self.assertIn('tools/taverna/access_proof/gateway.py',p['source_sha256'])
        for action in ('prepare','start','stop'):
            calls=[]
            result=fixture.dispatch(action,p,False,lambda: calls.append('ran'))
            self.assertEqual(result,{'action':action,'executed':False})
            self.assertEqual(calls,[])

    def test_invalid_or_drifted_plan_is_rejected(self):
        for host in ('127.0.0.1','0.0.0.0','::1','8.8.8.8','172.32.0.2','192.168.01.2','10.0.0.0','10.0.0.255'):
            with self.subTest(host=host),self.assertRaises(ValueError):fixture.make_plan(host,[15223,15443],'phone-a1b2c3d4','sha256:'+'a'*64)
        for ports in ([15223,15223],[443,15443],[True,15443],[15223,65536],[15223]):
            with self.subTest(ports=ports),self.assertRaises(ValueError):fixture.make_plan('192.168.1.2',ports,'phone-a1b2c3d4','sha256:'+'a'*64)
        for key,value in [('run','other-session'),('image','latest'),('lifetime',3600),('live','PASS'),('extra',1)]:
            p=self.plan();p[key]=value
            with self.assertRaises(ValueError):fixture.validate_plan(p,now=2_000_000_001)
        p=self.plan();p['source_sha256']['tools/taverna/access_proof/gateway.py']='0'*64
        with self.assertRaises(ValueError):fixture.validate_plan(p,now=2_000_000_001)
        with self.assertRaises(ValueError):fixture.validate_plan(self.plan(),now=2_000_003_601)
        self.assertEqual(fixture.validate_plan(self.plan(),now=2_000_003_601,fresh=False),self.plan())

    def test_binding_adapter_retains_original_loopback_input_and_bounds_services(self):
        p=self.plan();prefix='taverna-access-proof-'+p['run']
        args=['run','-d','--name',prefix+'-gateway','-p','127.0.0.1::15223','-p','127.0.0.1::15443',p['image'],'python3','/source/gateway.py','/gateway','--audit']
        before=list(args);actual=fixture.device_command(args,p)
        self.assertEqual(args,before)
        self.assertEqual([actual[i+1] for i,v in enumerate(actual) if v=='-p'],['192.168.40.2:15223:15223','192.168.40.2:15443:15443'])
        self.assertEqual(actual[actual.index(p['image'])+1:],['timeout','1200','python3','/source/gateway.py','/gateway','--audit'])
        for binding in ('0.0.0.0:15223:15223','127.0.0.1::443'):
            changed=list(args);changed[changed.index('-p')+1]=binding
            with self.assertRaises(ValueError):fixture.device_command(changed,p)
        relay=['run','--name',prefix+'-relay',p['image'],'sh','-c','fixed relay command']
        self.assertEqual(fixture.device_command(relay,p)[-5:],['timeout','1200','sh','-c','fixed relay command'])
        read=['container','inspect',prefix+'-relay']
        self.assertEqual(fixture.device_command(read,p),read)
        base=(ROOT/'tools/taverna/access_proof/fixture.py').read_text()
        self.assertIn("['-p','127.0.0.1::15223','-p','127.0.0.1::15443']",base)

    def test_enrollment_config_contains_only_fictitious_pins_and_matches_policy(self):
        p=self.plan()
        value=fixture.enrollment_config(p,'A'*43+'=',b'fixture identity',b'fixture anchor')
        self.assertEqual(set(value),{'schema','gatewayHost','smpPort','serverName','smpServer','expiresAt','identitySHA256','anchorSHA256'})
        self.assertEqual(value['smpServer'],'smp://'+'A'*43+'=@relay.test:5223')
        self.assertEqual(value['serverName'],'gateway.test')
        self.assertEqual(value['gatewayHost'],p['host'])
        self.assertEqual(value['smpPort'],15223)
        import hashlib
        self.assertEqual(value['identitySHA256'],hashlib.sha256(b'fixture identity').hexdigest())
        self.assertEqual(value['anchorSHA256'],hashlib.sha256(b'fixture anchor').hexdigest())
        with self.assertRaises(ValueError):fixture.enrollment_config(p,'public.test',b'a',b'b')

    def test_resource_ownership_refuses_foreign_or_replaced_ids_before_cleanup(self):
        expected={'container:a':'own-a','network:b':'own-b'}
        self.assertEqual(fixture.verify_resource_ids(expected,dict(expected)),None)
        self.assertEqual(fixture.cleanup_commands(expected),[('stop','--time','3','own-a'),('rm','own-a'),('network','rm','own-b')])
        for observed in ({'container:a':'foreign','network:b':'own-b'},{'container:a':'own-a','network:b':'foreign'},{'container:a':'own-a','network:b':'own-b','network:extra':'x'}):
            with self.assertRaises(ValueError):fixture.verify_resource_ids(expected,observed)


if __name__=='__main__':unittest.main()
