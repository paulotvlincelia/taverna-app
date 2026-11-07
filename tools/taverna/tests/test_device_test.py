import copy
import hashlib
import json
from pathlib import Path
import plistlib
import struct
import sys
import tempfile
import zlib
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import device_build as device
import device_identity as identity
import device_test as technical
from test_device_identity import profile

ROOT = Path(__file__).resolve().parents[3]


class TechnicalResources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT/'.build').mkdir(exist_ok=True)

    def render(self):
        p = device.render(device.read_project(ROOT/device.PROJECT))
        overlay = identity.render(p, {n:(ROOT/n).read_bytes() for n in identity.INPUTS}, profile())
        return technical.render(plistlib.loads(overlay[device.PROJECT]), plistlib.loads(overlay[identity.INFO]), ROOT)

    def test_exact_host_graph_and_framework_dependency(self):
        output = self.render()
        p = plistlib.loads(output[device.PROJECT]); o = p['objects']
        targets = {o[t]['name']:o[t] for t in o[p['rootObject']]['targets']}
        host = targets[device.HOST]
        self.assertEqual(len(targets), 2)
        phases = [o[n] for n in host['buildPhases']]
        self.assertNotIn('PBXShellScriptBuildPhase', [p['isa'] for p in phases])
        def refs(phase):
            return [o[o[f]['fileRef']]['path'] for p in phases if p['isa']==phase for f in p['files']]
        self.assertEqual(refs('PBXSourcesBuildPhase'), ['DeviceTestApp.swift','DeviceTestPolicy.swift'])
        self.assertEqual(refs('PBXResourcesBuildPhase'), ['DeviceAssets.xcassets','DeviceNotices'])
        self.assertEqual([o[d]['productName'] for d in host['packageProductDependencies']], ['SwiftyGif'])
        linked = [o[f] for p in phases if p['isa']=='PBXFrameworksBuildPhase' for f in p['files']]
        self.assertEqual(len(linked), 2)
        self.assertEqual(sorted(o[o[f]['fileRef']]['path'] for p in phases if p['isa']=='PBXCopyFilesBuildPhase' for f in p['files']), ['SimpleXChat.framework'])
        configs=[o[c]['buildSettings'] for c in o[host['buildConfigurationList']]['buildConfigurations']]
        for c in configs:
            self.assertEqual(c['ASSETCATALOG_COMPILER_APPICON_NAME'], 'DeviceIcon')
            self.assertNotIn('ASSETCATALOG_COMPILER_ALTERNATE_APPICON_NAMES',c)
            self.assertEqual(c['ASSETCATALOG_COMPILER_INCLUDE_ALL_APPICON_ASSETS'],'NO')
        shared = targets[device.SHARED]
        swift_paths = [o[o[f]['fileRef']]['path'] for phase in shared['buildPhases']
                       if o[phase]['isa'] == 'PBXSourcesBuildPhase'
                       for f in o[phase]['files']]
        adapters = [path for path in swift_paths if path.startswith('SimpleXChat/Taverna/')]
        self.assertCountEqual(adapters, [
            'SimpleXChat/Taverna/SocksCodec.swift',
            'SimpleXChat/Taverna/RelayTransport.swift',
            'SimpleXChat/Taverna/CoreTransport.swift',
        ])
        for config in o[shared['buildConfigurationList']]['buildConfigurations']:
            self.assertIn('TAVERNA_DEVICE_TEST', o[config]['buildSettings']['SWIFT_ACTIVE_COMPILATION_CONDITIONS'].split())
        info=plistlib.loads(output[identity.INFO])
        self.assertNotIn('CFBundleIcons',info)
        self.assertEqual(info['NSLocalNetworkUsageDescription'], 'Connect to the private Mac fixture for this technical test.')

    def test_graph_drift_rejected_without_mutation(self):
        p = device.render(device.read_project(ROOT/device.PROJECT))
        p['objects'][p['rootObject']]['targets']=[]
        before=copy.deepcopy(p)
        with self.assertRaises(ValueError): technical.render(p,{},ROOT)
        self.assertEqual(p,before)

    def test_graphics_are_generated_rgb_and_inventory_is_complete(self):
        output=self.render()
        icon=output['apps/ios/DeviceAssets.xcassets/DeviceIcon.appiconset/icon.png']
        self.assertEqual(icon[:8],b'\x89PNG\r\n\x1a\n')
        self.assertEqual(struct.unpack('>IIBBBBB',icon[16:29]),(1024,1024,8,2,0,0,0))
        self.assertEqual(icon,technical.icon_png())
        offset=8;compressed=b''
        while offset<len(icon):
            size=struct.unpack('>I',icon[offset:offset+4])[0]
            if icon[offset+4:offset+8]==b'IDAT':compressed+=icon[offset+8:offset+8+size]
            offset+=12+size
        raw=zlib.decompress(compressed)
        def pixel(x,y):return tuple(raw[y*(1024*3+1)+1+x*3:y*(1024*3+1)+1+x*3+3])
        self.assertEqual(pixel(0,0),(23,44,58))
        for point in ((250,350),(359,749),(457,250),(566,649),(664,150),(773,549)):
            self.assertEqual(pixel(*point),(213,235,230))
        for point in ((249,350),(360,350),(457,249),(567,649),(664,149),(774,549)):
            self.assertEqual(pixel(*point),(23,44,58))
        colors={tuple(raw[y*(3073)+1+x*3:y*(3073)+1+x*3+3]) for y in range(1024) for x in range(1024)}
        self.assertEqual(colors,{(23,44,58),(213,235,230)})

        inv=technical.inventory(ROOT,output)
        excluded=[r for r in inv if r['disposition']=='excluded']
        expected={str(p.relative_to(ROOT)) for d in technical.INHERITED for p in (ROOT/d).rglob('*') if p.is_file()}
        self.assertEqual({r['path'] for r in excluded},expected)
        for r in excluded:
            self.assertEqual(r['sha256'],hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest())
            self.assertEqual(r['license'],'assets/ASSETS_LICENSE.md; permission not assumed')
            self.assertEqual(r['replacement'],'DeviceAssets and original technical host')
        for row in inv:
            self.assertTrue(all(row.get(k) for k in ('path','sha256','origin','license','disposition','replacement')))
        own=[r for r in inv if r['disposition']=='generated']
        self.assertEqual({r['path'] for r in own},set(output)-{device.PROJECT,identity.INFO})
        for row in own:
            self.assertEqual(row['sha256'],hashlib.sha256(output[row['path']]).hexdigest())

    def test_package_is_closed_and_every_byte_bound(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.build') as t:
            app=Path(t)/'SimpleX.app';app.mkdir()
            files={'SimpleX':b'host','Info.plist':b'info','PkgInfo':b'pkg','Assets.car':b'catalog',
                   'AppIcon60x60@2x.png':b'icon','Frameworks/SimpleXChat.framework/SimpleXChat':b'core',
                   'Frameworks/SimpleXChat.framework/Info.plist':b'core-info',
                   'Frameworks/SwiftyGif_TEST_PackageProduct.framework/SwiftyGif_TEST_PackageProduct':b'gif',
                   'Frameworks/SwiftyGif_TEST_PackageProduct.framework/Info.plist':b'gif-info',
                   'DeviceNotices/LICENSE.txt':(ROOT/'LICENSE').read_bytes(),
                   'DeviceNotices/NOTICE.txt':technical.notices(ROOT)}
            for n,b in files.items():
                p=app/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            result=technical.inspect_resources(app,ROOT)
            self.assertEqual(result,{n:hashlib.sha256(b).hexdigest() for n,b in sorted(files.items())})
            for name in ('sounds/in_call.mp3','CodeScanner.bundle/Assets.car','other.png','embedded.mobileprovision','_CodeSignature/CodeResources','PlugIns/a.appex/a','Frameworks/WebRTC.framework/WebRTC'):
                p=app/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'blocked')
                with self.assertRaises(ValueError,msg=name):technical.inspect_resources(app,ROOT)
                p.unlink()
            (app/'DeviceNotices/NOTICE.txt').write_bytes(b'altered')
            with self.assertRaises(ValueError):technical.inspect_resources(app,ROOT)

    def test_technical_receipt_cannot_promote_limits_or_omit_source_binding(self):
        result=dict(status='UNSIGNED_TECHNICAL_PACKAGE_PASS', limits=dict(technical.LIMITS),
                    projection_sha256={p:'a'*64 for p in technical.PROJECTION},
                    package_sha256={p:'b'*64 for p in ('SimpleX','Info.plist','Assets.car')},
                    inventory_sha256='c'*64)
        self.assertEqual(technical.validate_result(result),result)
        for key in technical.LIMITS:
            bad=copy.deepcopy(result);bad['limits'][key]='PASS'
            with self.subTest(key=key),self.assertRaises(ValueError):technical.validate_result(bad)
        for field in ('projection_sha256','package_sha256'):
            bad=copy.deepcopy(result);bad[field]={}
            with self.assertRaises(ValueError):technical.validate_result(bad)
        bad=copy.deepcopy(result);bad['inventory_sha256']='wrong'
        with self.assertRaises(ValueError):technical.validate_result(bad)
        command=device.build_command(ROOT,ROOT/'.build/source/apps/ios/SimpleX.xcodeproj',identity=True,technical_mode=True)
        self.assertEqual(command[command.index('-derivedDataPath')+1],str(ROOT/'.build/TechnicalDerivedData'))
        self.assertIn('CODE_SIGNING_ALLOWED=NO',command)
        device.validate_command(ROOT,command)


if __name__=='__main__':unittest.main()
