import copy
import hashlib
from datetime import datetime, timedelta
import json
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import device_build as device
import device_identity as identity

ROOT = Path(__file__).resolve().parents[3]
PREFIX = 'A1B2C3D4E5'
ACCESS = PREFIX + '.' + device.BUNDLE


def profile():
    now = datetime.now()
    return dict(Name='Fictitious device profile', ApplicationIdentifierPrefix=[PREFIX],
                TeamIdentifier=[PREFIX], ProvisionedDevices=['fictitious-device'],
                DeveloperCertificates=[b'fictitious-public-certificate'], Platform=['iOS'],
                CreationDate=now - timedelta(days=1), ExpirationDate=now + timedelta(days=30),
                Entitlements={'application-identifier': ACCESS,
                              'com.apple.developer.team-identifier': PREFIX,
                              'com.apple.security.application-groups': [identity.GROUP_ID],
                              'keychain-access-groups': [PREFIX + '.*', 'com.apple.token'],
                              'get-task-allow': True})


class IdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = device.render(device.read_project(ROOT / device.PROJECT))
        cls.sources = {p: (ROOT / p).read_bytes() for p in identity.INPUTS}

    def overlay(self, source=None, project=None):
        return identity.render(project or self.project, source or self.sources, profile())

    def test_profile_yields_exact_narrow_host_entitlements(self):
        cfg = identity.configuration(profile())
        self.assertEqual(cfg['entitlements'], {
            'application-identifier': ACCESS,
            'com.apple.developer.team-identifier': PREFIX,
            'com.apple.security.application-groups': ['group.' + device.BUNDLE],
            'keychain-access-groups': [ACCESS], 'get-task-allow': True})
        self.assertEqual(cfg['keychain_group'], ACCESS)

    def test_wrong_or_broader_profile_is_rejected(self):
        changes = [
            lambda p: p.update(ApplicationIdentifierPrefix=['WRONG']),
            lambda p: p.update(TeamIdentifier=['Z9Y8X7W6V5']),
            lambda p: p.update(ProvisionedDevices=[]),
            lambda p: p.update(ProvisionedDevices=['a', 'b']),
            lambda p: p.update(DeveloperCertificates=[]),
            lambda p: p.update(DeveloperCertificates=[b'a', b'b']),
            lambda p: p.update(ProvisionsAllDevices=True),
            lambda p: p.update(Platform=['macOS']),
            lambda p: p.update(ExpirationDate=datetime.now()-timedelta(days=1)),
            lambda p: p.update(CreationDate=datetime.now()+timedelta(days=1)),
            lambda p: p['Entitlements'].update({'application-identifier': PREFIX + '.other'}),
            lambda p: p['Entitlements'].update({'com.apple.security.application-groups': ['group.other']}),
            lambda p: p['Entitlements'].update({'keychain-access-groups': ['OTHER.*']}),
            lambda p: p['Entitlements'].update({'get-task-allow': False}),
            lambda p: p['Entitlements'].update({'aps-environment': 'development'}),
            lambda p: p['Entitlements'].update({'com.apple.developer.usernotifications.filtering': True})]
        for change in changes:
            with self.subTest(change=change):
                p = profile()
                change(p)
                with self.assertRaises(ValueError):
                    identity.configuration(p)

    def test_projection_changes_only_owned_copy_and_requested_fields(self):
        before = copy.deepcopy((self.project, self.sources))
        output = self.overlay()
        self.assertEqual((self.project, self.sources), before)
        self.assertEqual(set(output), set(identity.INPUTS) | {identity.ENTITLEMENTS, device.PROJECT})
        self.assertIn(('public let APP_GROUP_NAME = "' + identity.GROUP_ID + '"').encode(),
                      output[identity.GROUP])
        self.assertNotIn(b'group.chat.simplex.app', output[identity.GROUP])
        self.assertNotIn(b'5NN7GUYB6T', output[identity.KEYCHAIN])
        self.assertNotIn(b'TARGET_OS_', output[identity.KEYCHAIN])
        self.assertEqual(plistlib.loads(output[identity.ENTITLEMENTS]),
                         identity.configuration(profile())['entitlements'])
        data = plistlib.loads(output[device.PROJECT])
        objs = data['objects']
        for t in objs[data['rootObject']]['targets']:
            target = objs[t]
            for c in objs[target['buildConfigurationList']]['buildConfigurations']:
                settings = objs[c]['buildSettings']
                if target['name'] == device.HOST:
                    self.assertEqual(settings['CODE_SIGN_ENTITLEMENTS'], 'DeviceTest.entitlements')
                else:
                    self.assertFalse(settings.get('CODE_SIGN_ENTITLEMENTS'))
                self.assertEqual(settings['CODE_SIGNING_ALLOWED'], 'NO')

    def test_foreground_projection_removes_handlers_and_startup_registration(self):
        output = self.overlay()
        info = plistlib.loads(output[identity.INFO])
        self.assertEqual(info['CFBundleDisplayName'], 'InnerMesh Test')
        for key in identity.FOREGROUND_REMOVALS:
            self.assertNotIn(key, info)
        self.assertNotIn(b'application.registerForRemoteNotifications()', output[identity.DELEGATE])
        self.assertNotIn(b'BGManager.shared.register()', output[identity.APP])

    def test_missing_ambiguous_consumers_and_wrong_target_fail_without_mutation(self):
        for path, anchor in ((identity.GROUP, b'public let APP_GROUP_NAME ='),
                             (identity.KEYCHAIN, b'private let ACCESS_GROUP:'),
                             (identity.DELEGATE, b'application.registerForRemoteNotifications()'),
                             (identity.APP, b'BGManager.shared.register()')):
            for replacement in (b'changed anchor', anchor + b'\n' + anchor):
                sources = dict(self.sources)
                sources[path] = sources[path].replace(anchor, replacement)
                before = copy.deepcopy(sources)
                with self.assertRaises(ValueError):
                    self.overlay(source=sources)
                self.assertEqual(sources, before)
        data = copy.deepcopy(self.project)
        setting = next(v['buildSettings'] for v in data['objects'].values()
                       if v.get('isa') == 'XCBuildConfiguration'
                       and v['buildSettings'].get('PRODUCT_BUNDLE_IDENTIFIER') == device.BUNDLE)
        setting['PRODUCT_BUNDLE_IDENTIFIER'] = 'other.app'
        with self.assertRaises(ValueError):
            self.overlay(project=data)

    def test_literal_query_builder_executes_with_explicit_access_group(self):
        source = self.overlay()[identity.KEYCHAIN].decode()
        constant = re.search(r'^private let ACCESS_GROUP:.*$', source, re.M).group()
        function = source[source.index('private func baseItemQuery('):]
        self.assertNotIn('SecItem', function)
        harness = 'import Foundation\nimport Security\n' + constant + '\n' + function
        harness += '\nlet q = baseItemQuery(forKey: "fictitious-item")\n'
        harness += 'print(String(data: try! JSONSerialization.data(withJSONObject: q), encoding: .utf8)!)\n'
        with tempfile.TemporaryDirectory(dir=ROOT / '.build') as temp:
            folder = Path(temp)
            swift = folder / 'query.swift'
            swift.write_text(harness)
            executable = folder / 'query'
            env = device.session.environment(ROOT)
            subprocess.run(['xcrun', 'swiftc', str(swift), '-o', str(executable)],
                           env=env, check=True, capture_output=True, timeout=60)
            out = subprocess.check_output([str(executable)], env=env, text=True, timeout=10)
        self.assertEqual(json.loads(out), {'class': 'genp', 'acct': 'fictitious-item', 'agrp': ACCESS})


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = device.render(device.read_project(ROOT / device.PROJECT))
        cls.sources = {p: (ROOT / p).read_bytes() for p in identity.INPUTS}

    def package(self, root):
        tree = root / 'source'
        overlay = identity.render(self.project, self.sources, profile())
        for name, body in overlay.items():
            p = tree / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(body)
        app = root / 'SimpleX.app'
        shared = app / 'Frameworks/SimpleXChat.framework'
        shared.mkdir(parents=True)
        info = plistlib.loads(overlay[identity.INFO])
        info['CFBundleIdentifier'] = device.BUNDLE
        (app / 'Info.plist').write_bytes(plistlib.dumps(info))
        (shared / 'Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier': device.BUNDLE + '.shared'}))
        hashes = {p: hashlib.sha256(body).hexdigest() for p, body in overlay.items()}
        return tree, app, hashes

    def test_package_inspector_preserves_exact_configuration_and_limits(self):
        with tempfile.TemporaryDirectory() as temp:
            tree, app, hashes = self.package(Path(temp))
            report = identity.inspect_package(tree, app, profile(), hashes)
            self.assertEqual(report['status'], 'UNSIGNED_DEVICE_IDENTITY_PASS')
            self.assertEqual(report['entitlements']['keychain-access-groups'], [ACCESS])
            self.assertEqual(report['projection_sha256'], hashes)
            self.assertEqual(report['limits'], {
                'signing': 'NOT RUN', 'installation': 'NOT RUN', 'execution': 'NOT RUN',
                'runtime_storage': 'NOT RUN', 'assets': 'BLOCKED', 'transport': 'BLOCKED',
                'installation_readiness': 'BLOCKED'})

    def test_changed_product_metadata_and_embedding_are_rejected(self):
        for field, value in [('CFBundleIdentifier', 'other.app'),
                             ('CFBundleDisplayName', 'Other'),
                             ('UIBackgroundModes', ['remote-notification']),
                             ('CFBundleURLTypes', []), ('NSUserActivityTypes', ['INStartCallIntent'])]:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temp:
                tree, app, hashes = self.package(Path(temp))
                p = app / 'Info.plist'
                info = plistlib.loads(p.read_bytes())
                info[field] = value
                p.write_bytes(plistlib.dumps(info))
                with self.assertRaises(ValueError):
                    identity.inspect_package(tree, app, profile(), hashes)
        for path in ['PlugIns/Other.appex', '_CodeSignature', 'embedded.mobileprovision',
                     'Frameworks/SimpleXChat.framework/_CodeSignature']:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as temp:
                tree, app, hashes = self.package(Path(temp))
                (app / path).mkdir(parents=True)
                with self.assertRaises(ValueError):
                    identity.inspect_package(tree, app, profile(), hashes)

    def test_modified_projection_and_wrong_permissions_are_rejected(self):
        for path in [identity.GROUP, identity.KEYCHAIN, identity.ENTITLEMENTS, device.PROJECT]:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as temp:
                tree, app, hashes = self.package(Path(temp))
                (tree / path).write_bytes(b'changed after build')
                with self.assertRaises(ValueError):
                    identity.inspect_package(tree, app, profile(), hashes)
        with tempfile.TemporaryDirectory() as temp:
            tree, app, hashes = self.package(Path(temp))
            p = tree / identity.ENTITLEMENTS
            ent = plistlib.loads(p.read_bytes())
            ent['keychain-access-groups'] = [PREFIX + '.*']
            p.write_bytes(plistlib.dumps(ent))
            hashes[identity.ENTITLEMENTS] = hashlib.sha256(p.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):
                identity.inspect_package(tree, app, profile(), hashes)
        with tempfile.TemporaryDirectory() as temp:
            tree, app, hashes = self.package(Path(temp))
            p = app / 'Frameworks/SimpleXChat.framework/Info.plist'
            p.write_bytes(plistlib.dumps({'CFBundleIdentifier': 'other.shared'}))
            with self.assertRaises(ValueError):
                identity.inspect_package(tree, app, profile(), hashes)

    def test_receipt_rejects_promotion_and_missing_profile_binding(self):
        with tempfile.TemporaryDirectory() as temp:
            tree, app, hashes = self.package(Path(temp))
            report = identity.inspect_package(tree, app, profile(), hashes)
            report['profile_sha256'] = 'a' * 64
            identity.validate_result(report)
            for field in ['profile_sha256', 'limits', 'projection_sha256']:
                changed = copy.deepcopy(report)
                changed[field] = {} if field != 'profile_sha256' else ''
                with self.assertRaises(ValueError):
                    identity.validate_result(changed)
            promoted = copy.deepcopy(report)
            promoted['limits']['installation_readiness'] = 'PASS'
            with self.assertRaises(ValueError):
                identity.validate_result(promoted)

    def test_identity_build_command_keeps_separate_owned_products_and_disables_signing(self):
        cmd = device.build_command(ROOT, ROOT / device.PROJECT, identity=True)
        self.assertEqual(cmd[cmd.index('-derivedDataPath') + 1], str(ROOT / '.build/IdentityDerivedData'))
        self.assertIn('CODE_SIGNING_ALLOWED=NO', cmd)
        self.assertNotIn('-allowProvisioningUpdates', cmd)
        device.validate_command(ROOT, cmd)

    def test_effective_host_settings_cannot_select_inherited_permissions(self):
        settings = dict(PRODUCT_BUNDLE_IDENTIFIER=device.BUNDLE,
                        CODE_SIGN_ENTITLEMENTS='DeviceTest.entitlements',
                        INFOPLIST_FILE='SimpleX--iOS--Info.plist', CODE_SIGNING_ALLOWED='NO',
                        PLATFORM_NAME='iphoneos')
        identity.validate_host_settings(settings)
        for key, value in [('PRODUCT_BUNDLE_IDENTIFIER', 'other.app'),
                           ('CODE_SIGN_ENTITLEMENTS', 'SimpleX (iOS).entitlements'),
                           ('INFOPLIST_FILE', 'Other.plist'),
                           ('CODE_SIGNING_ALLOWED', 'YES'), ('PLATFORM_NAME', 'iphonesimulator')]:
            changed = dict(settings, **{key: value})
            with self.assertRaises(ValueError):
                identity.validate_host_settings(changed)


if __name__ == '__main__':
    unittest.main()
