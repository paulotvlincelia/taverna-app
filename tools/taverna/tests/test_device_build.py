import copy
import json
from pathlib import Path
import plistlib
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import device_build as device

ROOT = Path(__file__).resolve().parents[3]


class ProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = json.loads(subprocess.check_output([
            'plutil', '-convert', 'json', '-o', '-', str(ROOT / device.PROJECT)]))

    def test_only_host_and_framework_without_extensions(self):
        before = copy.deepcopy(self.project)
        result = device.render(self.project)
        objects = result['objects']
        targets = [objects[t] for t in objects[result['rootObject']]['targets']]
        self.assertEqual({t['name'] for t in targets}, {device.HOST, device.SHARED})
        host = next(t for t in targets if t['name'] == device.HOST)
        self.assertEqual([objects[objects[d]['target']]['name']
                          for d in host['dependencies']], [device.SHARED])
        phases = [objects[p] for p in host['buildPhases']
                  if objects[p]['isa'] == 'PBXCopyFilesBuildPhase'
                  and str(objects[p].get('dstSubfolderSpec')) == '13']
        self.assertEqual([p['files'] for p in phases], [[]])
        self.assertEqual(self.project, before)

    def test_device_configuration_disables_all_signing(self):
        result = device.render(self.project)
        configs = [v['buildSettings'] for v in result['objects'].values()
                   if v['isa'] == 'XCBuildConfiguration']
        self.assertTrue(configs)
        for settings in configs:
            self.assertEqual(settings['SDKROOT'], 'iphoneos')
            self.assertEqual(settings['SUPPORTED_PLATFORMS'], 'iphoneos')
            self.assertEqual(settings['CODE_SIGNING_ALLOWED'], 'NO')
            self.assertEqual(settings['CODE_SIGNING_REQUIRED'], 'NO')
            self.assertEqual(settings['CODE_SIGN_IDENTITY'], '')
            self.assertEqual(settings['DEVELOPMENT_TEAM'], '')
            self.assertEqual(settings['PROVISIONING_PROFILE_SPECIFIER'], '')

    def test_unexpected_dependency_is_rejected(self):
        project = copy.deepcopy(self.project)
        host = next(v for v in project['objects'].values()
                    if v.get('isa') == 'PBXNativeTarget' and v['name'] == device.HOST)
        host['dependencies'].pop()
        with self.assertRaisesRegex(ValueError, 'dependency graph'):
            device.render(project)

    def test_unexpected_embedding_is_rejected(self):
        project = copy.deepcopy(self.project)
        phase = next(v for v in project['objects'].values()
                     if v.get('isa') == 'PBXCopyFilesBuildPhase'
                     and str(v.get('dstSubfolderSpec')) == '13' and len(v['files']) == 2)
        phase['files'].pop()
        with self.assertRaisesRegex(ValueError, 'embedded extensions'):
            device.render(project)


def macho(platform=2, command=0x32, cpu=16777228, filetype=1):
    load = (struct.pack('<6I', command, 24, platform, 0x0f0000, 0x1b0100, 0)
            if command == 0x32 else struct.pack('<4I', command, 16, 0x0f0000, 0x1b0100))
    return struct.pack('<8I', 0xfeedfacf, cpu, 0, filetype, 1, len(load), 0, 0) + load


def archive(body):
    header = f'{"part.o/":<16}{0:<12}{0:<6}{0:<6}{100644:<8}{len(body):<10}`\n'.encode()
    return b'!<arch>\n' + header + body + (b'\n' if len(body) % 2 else b'')


class DeviceValidationTests(unittest.TestCase):
    def products(self, root):
        base = root / '.build/products'
        app = base / 'SimpleX.app'
        shared = app / 'Frameworks/SimpleXChat.framework'
        shared.mkdir(parents=True)
        for bundle, name, kind, identifier in (
                (app, 'SimpleX', 2, device.BUNDLE),
                (shared, 'SimpleXChat', 6, device.BUNDLE + '.shared')):
            (bundle / name).write_bytes(macho(filetype=kind))
            (bundle / 'Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier': identifier}))
        return base, app, shared

    def test_products_require_real_device_platform_and_unsigned_bundles(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            base, app, shared = self.products(root)
            unsigned = subprocess.CompletedProcess([], 1, b'', b'code object is not signed at all')
            with patch('device_build.subprocess.run', return_value=unsigned):
                result = device.inspect_products(root, base)
                self.assertEqual({r['name'] for r in result}, {'SimpleX', 'SimpleXChat'})
                self.assertTrue(all(r['platform'] == 2 and r['has_profile'] is False
                                    and r['has_signature'] is False and r['has_extensions'] is False
                                    for r in result))
                (app / 'SimpleX').write_bytes(macho(platform=7, filetype=2))
                with self.assertRaisesRegex(ValueError, 'device Mach-O'):
                    device.inspect_products(root, base)

    def test_products_reject_extensions_profiles_and_signatures(self):
        unsigned = subprocess.CompletedProcess([], 1, b'', b'code object is not signed at all')
        for forbidden in ('PlugIns/NSE.appex', 'embedded.mobileprovision', '_CodeSignature'):
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp).resolve()
                base, app, _ = self.products(root)
                path = app / forbidden
                if path.suffix == '.mobileprovision':
                    path.write_text('fixture')
                else:
                    path.mkdir(parents=True)
                with patch('device_build.subprocess.run', return_value=unsigned):
                    with self.assertRaises(ValueError):
                        device.inspect_products(root, base)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            base, _, _ = self.products(root)
            signed = subprocess.CompletedProcess([], 0, b'', b'valid signature')
            with patch('device_build.subprocess.run', return_value=signed):
                with self.assertRaisesRegex(ValueError, 'unsigned state'):
                    device.inspect_products(root, base)

    def test_vendor_device_dylib_thin_and_fat(self):
        thin = macho(filetype=6)
        fat = struct.pack('>7I', 0xcafebabe, 1, 16777228, 0, 32, len(thin), 3)
        fat += b'\0' * (32 - len(fat)) + thin
        for body in (thin, fat):
            result = device.inspect_vendor_binary(body)
            self.assertEqual(result['platform'], 2)
            self.assertEqual(result['architecture'], 'arm64')
        for body in (macho(platform=7, filetype=6), fat[:28],
                     struct.pack('>7I', 0xcafebabe, 2, 16777228, 0, 32, len(thin), 3)):
            with self.assertRaises(ValueError):
                device.inspect_vendor_binary(body)

    def test_device_archive_accepts_modern_and_legacy(self):
        for body in (macho(), macho(command=0x25)):
            result = device.inspect_library(archive(body))
            self.assertEqual(result['objects'], 1)
            self.assertEqual(result['platform'], 2)
            self.assertEqual(result['architecture'], 'arm64')

    def test_archive_rejects_simulator_macos_wrong_cpu_and_empty(self):
        for body in (macho(platform=7), macho(platform=1), macho(command=0x24),
                     macho(cpu=0x01000007), macho(filetype=2)):
            with self.assertRaisesRegex(ValueError, 'device Mach-O'):
                device.inspect_library(archive(body))
        with self.assertRaises(ValueError):
            device.inspect_library(b'!<arch>\n')

    def test_device_build_command_uses_owned_paths_without_signing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            cmd = device.build_command(root, root / device.PROJECT)
            self.assertEqual(cmd[cmd.index('-sdk') + 1], 'iphoneos')
            self.assertEqual(cmd[cmd.index('-destination') + 1], 'generic/platform=iOS')
            self.assertIn('CODE_SIGNING_ALLOWED=NO', cmd)
            self.assertIn('CODE_SIGNING_REQUIRED=NO', cmd)
            self.assertIn('CODE_SIGN_IDENTITY=', cmd)
            self.assertIn('-disableAutomaticPackageResolution', cmd)
            self.assertNotIn('-allowProvisioningUpdates', cmd)
            device.validate_command(root, cmd)
            for path in ('-derivedDataPath', '-clonedSourcePackagesDirPath', '-packageCachePath'):
                self.assertTrue(Path(cmd[cmd.index(path) + 1]).is_relative_to(root))
            for key in ('CFFIXED_USER_HOME', 'TMPDIR', 'CLANG_MODULE_CACHE_PATH',
                        'SWIFT_MODULE_CACHE_PATH', 'XDG_CONFIG_HOME', 'XDG_CACHE_HOME'):
                self.assertTrue(Path(device.session.environment(root)[key]).is_relative_to(root))
            for extra in ('-allowProvisioningUpdates', 'CODE_SIGNING_ALLOWED=YES'):
                with self.assertRaises(ValueError):
                    device.validate_command(root, cmd + [extra])
            wrong = list(cmd)
            wrong[wrong.index('-derivedDataPath') + 1] = '/tmp/shared'
            with self.assertRaises(ValueError):
                device.validate_command(root, wrong)

    def receipt(self, root):
        products = [dict(name=n, platform=2, architecture='arm64', sha256='1' * 64,
                         has_extensions=False, has_profile=False, has_signature=False)
                    for n in ('SimpleX', 'SimpleXChat')]
        libraries = [dict(name=n, platform=2, architecture='arm64', sha256='2' * 64, objects=1)
                     for n in device.EXPECTED_LIBS]
        return dict(status='UNSIGNED_DEVICE_BUILD_PASS', build_exit_code=0,
                    limits=dict(device.LIMITS), core_sha256={'src/Chat.hs': '3' * 64},
                    component_sha256={'src/Chat.hs': '3' * 64}, source_sha256={'host': '4' * 64},
                    source_after_sha256={'host': '4' * 64}, recipe_sha256={'flake.lock': '5' * 64},
                    core_derivation='component.drv', products=products, libraries=libraries,
                    command=device.build_command(root, root / device.PROJECT))

    def test_receipt_retains_build_only_limits(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            r = device.validate_receipt(root, self.receipt(root))
            self.assertEqual(r['limits']['product'], 'BLOCKED')
            self.assertEqual(r['limits']['installation'], 'NOT RUN')

    def test_receipt_rejects_promoted_or_incomplete_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            changes = [lambda r: r['products'][0].update(platform=7),
                       lambda r: r['products'][0].update(has_extensions=True),
                       lambda r: r['products'][0].update(has_profile=True),
                       lambda r: r['products'][0].update(has_signature=True),
                       lambda r: r['products'].pop(),
                       lambda r: r['libraries'].pop(),
                       lambda r: r['libraries'][0].update(objects=0),
                       lambda r: r['libraries'][0].update(sha256='invalid'),
                       lambda r: r['limits'].update(product='PASS'),
                       lambda r: r['component_sha256'].update(other='6' * 64),
                       lambda r: r['source_after_sha256'].update(host='7' * 64),
                       lambda r: r.update(build_exit_code=65)]
            for change in changes:
                r = self.receipt(root)
                change(r)
                with self.assertRaises(ValueError):
                    device.validate_receipt(root, r)


if __name__ == '__main__':
    unittest.main()
