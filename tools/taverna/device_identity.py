"""Project dedicated storage into a disposable, unsigned iOS device source copy."""
import copy
from datetime import datetime, timezone
import hashlib
import plistlib
import re

BUNDLE = 'cc.quietmesh.innermesh.devicebuild'
GROUP_ID = 'group.' + BUNDLE
GROUP = 'apps/ios/SimpleXChat/AppGroup.swift'
KEYCHAIN = 'apps/ios/SimpleXChat/KeyChain.swift'
INFO = 'apps/ios/SimpleX--iOS--Info.plist'
DELEGATE = 'apps/ios/Shared/AppDelegate.swift'
APP = 'apps/ios/Shared/SimpleXApp.swift'
PROJECT = 'apps/ios/SimpleX.xcodeproj/project.pbxproj'
ENTITLEMENTS = 'apps/ios/DeviceTest.entitlements'
INPUTS = (GROUP, KEYCHAIN, INFO, DELEGATE, APP)
FOREGROUND_REMOVALS = ('UIBackgroundModes', 'BGTaskSchedulerPermittedIdentifiers',
                      'NSUserActivityTypes', 'CFBundleURLTypes')
LIMITS = dict(signing='NOT RUN', installation='NOT RUN', execution='NOT RUN',
              runtime_storage='NOT RUN', assets='BLOCKED', transport='BLOCKED',
              installation_readiness='BLOCKED')


def configuration(profile):
    prefixes = profile.get('ApplicationIdentifierPrefix')
    if (not isinstance(prefixes, list) or len(prefixes) != 1
            or not isinstance(prefixes[0], str) or not re.fullmatch('[A-Z0-9]{10}', prefixes[0])):
        raise ValueError('invalid profile prefix')
    prefix = prefixes[0]
    access = prefix + '.' + BUNDLE
    entitlements = {'application-identifier': access,
                    'com.apple.developer.team-identifier': prefix,
                    'com.apple.security.application-groups': [GROUP_ID],
                    'keychain-access-groups': [access], 'get-task-allow': True}
    allowed = dict(entitlements, **{'keychain-access-groups': [prefix + '.*', 'com.apple.token']})
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if (profile.get('TeamIdentifier') != [prefix] or profile.get('Entitlements') != allowed
            or profile.get('ProvisionsAllDevices', False)
            or 'iOS' not in profile.get('Platform', [])
            or not isinstance(profile.get('CreationDate'), datetime)
            or not isinstance(profile.get('ExpirationDate'), datetime)
            or not profile['CreationDate'] <= now < profile['ExpirationDate']):
        raise ValueError('profile scope or lifetime differs')
    for field, kind in (('ProvisionedDevices', str), ('DeveloperCertificates', bytes)):
        values = profile.get(field)
        if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], kind) or not values[0]:
            raise ValueError('profile must contain one device and one certificate')
    return dict(bundle=BUNDLE, group=GROUP_ID, prefix=prefix, keychain_group=access,
                entitlements=entitlements, display_name='InnerMesh Test')


def once(source, old, new):
    if source.count(old) != 1:
        raise ValueError('consumer anchor missing or ambiguous')
    return source.replace(old, new)


def render(project, sources, profile):
    cfg = configuration(profile)
    data = copy.deepcopy(project)
    objects = data['objects']
    targets = [objects[t] for t in objects[data['rootObject']]['targets']]
    if len(targets) != 2 or {t['name'] for t in targets} != {'SimpleX (iOS)', 'SimpleXChat'}:
        raise ValueError('unexpected device targets')
    for target in targets:
        host = target['name'] == 'SimpleX (iOS)'
        configs = objects[target['buildConfigurationList']]['buildConfigurations']
        for c in configs:
            settings = objects[c]['buildSettings']
            if settings.get('PRODUCT_BUNDLE_IDENTIFIER') != BUNDLE + ('' if host else '.shared'):
                raise ValueError('device target identity differs')
            if settings.get('CODE_SIGNING_ALLOWED') != 'NO':
                raise ValueError('device projection must remain unsigned')
            if host:
                settings['CODE_SIGN_ENTITLEMENTS'] = 'DeviceTest.entitlements'
            else:
                settings.pop('CODE_SIGN_ENTITLEMENTS', None)
    group = sources[GROUP].decode()
    keychain = sources[KEYCHAIN].decode()
    if group.count('public let APP_GROUP_NAME =') != 1 or keychain.count('private let ACCESS_GROUP:') != 1:
        raise ValueError('consumer anchor missing or ambiguous')
    for path, anchor in ((DELEGATE, 'application.registerForRemoteNotifications()'),
                         (APP, 'BGManager.shared.register()')):
        if sources[path].decode().count(anchor) != 1:
            raise ValueError('consumer anchor missing or ambiguous')
    group = once(group, 'public let APP_GROUP_NAME = "group.chat.simplex.app"',
                 'public let APP_GROUP_NAME = "' + cfg['group'] + '"')
    keychain = once(keychain, 'private let ACCESS_GROUP: String = "5NN7GUYB6T.chat.simplex.app"',
                    'private let ACCESS_GROUP: String = "' + cfg['keychain_group'] + '"')
    # This projection has only iphoneos targets. Every query must carry its group;
    # inherited C preprocessor symbols are not Swift platform conditions.
    keychain = once(keychain, '    #if TARGET_OS_IOS && !TARGET_OS_SIMULATOR\n'
                    '        query[kSecAttrAccessGroup] = ACCESS_GROUP\n    #endif',
                    '    query[kSecAttrAccessGroup] = ACCESS_GROUP as AnyObject')
    info = plistlib.loads(sources[INFO])
    for key in FOREGROUND_REMOVALS:
        info.pop(key, None)
    info['CFBundleDisplayName'] = cfg['display_name']
    delegate = once(sources[DELEGATE].decode(), '        application.registerForRemoteNotifications()',
                    '        // Foreground device test: no APNs registration.')
    app = once(sources[APP].decode(), '        BGManager.shared.register()',
               '        // Foreground device test: no background task registration.')
    return {PROJECT: plistlib.dumps(data), GROUP: group.encode(), KEYCHAIN: keychain.encode(),
            INFO: plistlib.dumps(info), DELEGATE: delegate.encode(), APP: app.encode(),
            ENTITLEMENTS: plistlib.dumps(cfg['entitlements'])}


def inspect_package(tree, app, profile, expected_hashes):
    cfg = configuration(profile)
    paths = set(INPUTS) | {PROJECT, ENTITLEMENTS}
    hashes = {p: hashlib.sha256((tree / p).read_bytes()).hexdigest() for p in paths}
    if hashes != expected_hashes:
        raise ValueError('projected identity source changed')
    entitlements = plistlib.loads((tree / ENTITLEMENTS).read_bytes())
    if entitlements != cfg['entitlements']:
        raise ValueError('requested permissions differ from dedicated profile scope')
    data = plistlib.loads((tree / PROJECT).read_bytes())
    objects = data['objects']
    targets = [objects[t] for t in objects[data['rootObject']]['targets']]
    if len(targets) != 2 or {t['name'] for t in targets} != {'SimpleX (iOS)', 'SimpleXChat'}:
        raise ValueError('unexpected projected target set')
    for target in targets:
        host = target['name'] == 'SimpleX (iOS)'
        for c in objects[target['buildConfigurationList']]['buildConfigurations']:
            settings = objects[c]['buildSettings']
            if (settings.get('PRODUCT_BUNDLE_IDENTIFIER') != BUNDLE + ('' if host else '.shared')
                    or settings.get('CODE_SIGNING_ALLOWED') != 'NO'
                    or settings.get('CODE_SIGN_ENTITLEMENTS', '') != ('DeviceTest.entitlements' if host else '')):
                raise ValueError('projected target permissions differ')
    if (list(app.rglob('*.appex')) or list(app.rglob('embedded.mobileprovision'))
            or any((p / '_CodeSignature').exists() for p in (
                app, app / 'Frameworks/SimpleXChat.framework'))):
        raise ValueError('unexpected extension, signature or profile')
    info = plistlib.loads((app / 'Info.plist').read_bytes())
    shared = plistlib.loads((app / 'Frameworks/SimpleXChat.framework/Info.plist').read_bytes())
    if (info.get('CFBundleIdentifier') != BUNDLE
            or info.get('CFBundleDisplayName') != cfg['display_name']
            or shared.get('CFBundleIdentifier') != BUNDLE + '.shared'
            or any(k in info for k in FOREGROUND_REMOVALS)):
        raise ValueError('device package metadata differs from foreground variant')
    return dict(status='UNSIGNED_DEVICE_IDENTITY_PASS', entitlements=entitlements,
                projection_sha256=hashes, limits=dict(LIMITS))


def validate_result(result):
    if result.get('status') != 'UNSIGNED_DEVICE_IDENTITY_PASS' or result.get('limits') != LIMITS:
        raise ValueError('identity proof promoted to installation or runtime')
    hashes = result.get('projection_sha256', {})
    if set(hashes) != set(INPUTS) | {PROJECT, ENTITLEMENTS}:
        raise ValueError('incomplete identity projection binding')
    if not all(isinstance(v, str) and re.fullmatch('[0-9a-f]{64}', v)
               for v in [result.get('profile_sha256')] + list(hashes.values())):
        raise ValueError('invalid identity or profile digest')
    return result


def validate_host_settings(settings):
    expected = dict(PRODUCT_BUNDLE_IDENTIFIER=BUNDLE, CODE_SIGN_ENTITLEMENTS='DeviceTest.entitlements',
                    INFOPLIST_FILE='SimpleX--iOS--Info.plist', CODE_SIGNING_ALLOWED='NO',
                    PLATFORM_NAME='iphoneos')
    if any(settings.get(k) != v for k, v in expected.items()):
        raise ValueError('effective host identity or permission settings differ')
