"""Build-only iOS device variant. Never provisions, signs, installs or launches."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import struct
import subprocess
import sys
import zipfile

import device_identity as storage
import device_test as technical
import ios_native as native
import ios_proof as proof
import ios_session as session

HOST = 'SimpleX (iOS)'
SHARED = 'SimpleXChat'
EXTENSIONS = {'SimpleX NSE', 'SimpleX SE'}
BUNDLE = 'cc.quietmesh.innermesh.devicebuild'
PROJECT = 'apps/ios/SimpleX.xcodeproj/project.pbxproj'
ROOT = Path(__file__).resolve().parents[2]
ASSET_SCRIPT = 'scripts/ios/copy-assets.sh'
NIX = '/nix/var/nix/profiles/default/bin/nix'
EXPECTED_LIBS = {r['name'] for r in json.loads(
    (ROOT / '.specs/features/ios-first-build/native-inputs.json').read_text())['libraries']}
LIMITS = dict(signing='NOT RUN', profiles='NOT CREATED', installation='NOT RUN',
              execution='NOT RUN', networking='NOT RUN', device_tests='NOT RUN',
              assets='BLOCKED', runtime_identity='BLOCKED', product='BLOCKED')


def read_project(path):
    return json.loads(subprocess.check_output(['plutil', '-convert', 'json', '-o', '-', str(path)]))


def source_files(root):
    files = {path.relative_to(root).as_posix(): native.sha256(path)
             for path in sorted((root / 'apps/ios').rglob('*'))
             if path.is_file() and '/Libraries/' not in path.as_posix() and '/xcuserdata/' not in path.as_posix()}
    files[ASSET_SCRIPT] = native.sha256(root / ASSET_SCRIPT)
    return files


def core_files(root):
    suffixes = {'.hs', '.hsc', '.hsig', '.c', '.h', '.cpp'}
    paths = sorted(path for path in (root / 'src').rglob('*') if path.is_file() and path.suffix in suffixes)
    return {path.relative_to(root).as_posix(): native.sha256(path) for path in paths}


def verify_component_source(path, expected):
    actual = {name: native.sha256(path / name) for name in expected if (path / name).is_file()}
    if not expected or actual != expected:
        raise ValueError('component source differs from current source')
    return actual


def prepare_packages(root, source):
    destination = root / '.build/SourcePackages'
    shutil.copytree(source, destination, symlinks=True)
    for path in destination.rglob('*'):
        if path.is_symlink() and not path.resolve().is_relative_to(destination):
            raise ValueError('package link escapes owned copy')
    pins = json.loads((root / native.LOCK).read_text())['pins']
    for pin in pins:
        checkouts = [p for p in (destination / 'checkouts').iterdir() if p.name.lower() == pin['identity'].lower()]
        if len(checkouts) != 1:
            raise ValueError('package checkout absent')
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=checkouts[0], text=True).strip()
        if revision != pin['state']['revision']:
            raise ValueError('package checkout pin drift')
    manifest = json.loads((root / '.specs/features/ios-first-build/native-inputs.json').read_text())
    binary = destination / 'artifacts/webrtc/WebRTC/WebRTC.xcframework/ios-x86_64_arm64-simulator/WebRTC.framework/WebRTC'
    if native.sha256(binary) != manifest['webrtc']['used_binary_sha256']:
        raise ValueError('WebRTC checksum drift')


def device_macho(body, filetypes):
    parsed = native.macho(body)
    versions = [cmd for cmd, _ in parsed['commands'] if cmd in native.VERSION_COMMANDS]
    correct_platform = (parsed['platforms'] == [2] or
                        (parsed['platforms'] == ['legacy'] and versions == [0x25]))
    if (parsed['header'][1] != 16777228 or parsed['header'][3] not in filetypes
            or not correct_platform):
        raise ValueError('expected arm64 iOS device Mach-O')
    return parsed


def inspect_library(body):
    objects = native.members(body)
    for _, obj in objects:
        device_macho(obj, {1})
    return dict(objects=len(objects), architecture='arm64', platform=2,
                sha256=hashlib.sha256(body).hexdigest())


def inspect_vendor_binary(body):
    thin = body
    if body[:4] == b'\xca\xfe\xba\xbe':
        if len(body) < 28 or struct.unpack_from('>I', body, 4)[0] != 1:
            raise ValueError('expected one arm64 vendor slice')
        cpu, _, offset, size, alignment = struct.unpack_from('>5I', body, 8)
        if (cpu != 16777228 or alignment > 31 or offset < 28 or size < 32
                or offset + size > len(body) or offset % (1 << alignment)):
            raise ValueError('invalid vendor slice bounds or architecture')
        thin = body[offset:offset + size]
    device_macho(thin, {6})
    return dict(architecture='arm64', platform=2,
                sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))


def build_command(root, project, identity=False, technical_mode=False):
    return ['xcodebuild', 'build', '-project', str(project), '-scheme', 'Device Build',
            '-configuration', 'Debug', '-sdk', 'iphoneos',
            '-destination', 'generic/platform=iOS',
            '-derivedDataPath', str(root / ('.build/TechnicalDerivedData' if technical_mode else '.build/IdentityDerivedData' if identity else '.build/DerivedData')),
            '-jobs', '2'] + \
        proof.package_args(root) + session.build_cache_args(root) + [
            'CODE_SIGNING_ALLOWED=NO', 'CODE_SIGNING_REQUIRED=NO',
            'CODE_SIGN_STYLE=Manual', 'CODE_SIGN_IDENTITY=', 'DEVELOPMENT_TEAM=',
            'PROVISIONING_PROFILE=', 'PROVISIONING_PROFILE_SPECIFIER=',
            'ARCHS=arm64', 'ONLY_ACTIVE_ARCH=YES']


def validate_command(root, cmd):
    project = Path(cmd[cmd.index('-project') + 1])
    if not project.resolve().is_relative_to(root.resolve()):
        raise ValueError('build project outside owned worktree')
    identity = cmd[cmd.index('-derivedDataPath') + 1] == str(root / '.build/IdentityDerivedData')
    technical_mode = cmd[cmd.index('-derivedDataPath') + 1] == str(root / '.build/TechnicalDerivedData')
    if cmd != build_command(root, project, identity=identity, technical_mode=technical_mode):
        raise ValueError('unsafe or changed device build command')


def validate_receipt(root, receipt):
    if receipt.get('status') != 'UNSIGNED_DEVICE_BUILD_PASS' or receipt.get('build_exit_code') != 0:
        raise ValueError('device build not successful')
    if receipt.get('limits') != LIMITS:
        raise ValueError('build proof promoted to runtime or installation')
    if 'identity' in receipt:
        storage.validate_result(receipt['identity'])
    mode = str(root / '.build/TechnicalDerivedData') in receipt.get('command', [])
    if mode != ('technical' in receipt) or mode and 'identity' not in receipt:
        raise ValueError('technical build mode or identity binding differs')
    if mode:
        technical.validate_result(receipt['technical'])
    if not receipt.get('core_sha256') or receipt.get('component_sha256') != receipt['core_sha256']:
        raise ValueError('native component source mismatch')
    if not receipt.get('source_sha256') or receipt.get('source_after_sha256') != receipt['source_sha256']:
        raise ValueError('source changed during build')
    if not receipt.get('recipe_sha256') or not receipt.get('core_derivation'):
        raise ValueError('native recipe provenance missing')
    validate_command(root, receipt['command'])
    products = receipt.get('products', [])
    libraries = receipt.get('libraries', [])
    if len(products) != 2 or {p['name'] for p in products} != {'SimpleX', 'SimpleXChat'}:
        raise ValueError('unexpected device product set')
    if len(libraries) != 5 or {p['name'] for p in libraries} != EXPECTED_LIBS:
        raise ValueError('incomplete native library set')
    for row in products + libraries:
        digest = row.get('sha256', '')
        if (row.get('platform') != 2 or row.get('architecture') != 'arm64'
                or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest)):
            raise ValueError('invalid device artifact identity')
    for row in products:
        if any(row.get(k) is not False for k in ('has_extensions', 'has_profile', 'has_signature')):
            raise ValueError('unexpected embedding, profile or signature')
    for row in libraries:
        if type(row.get('objects')) is not int or row['objects'] < 1:
            raise ValueError('empty native library')
    return receipt


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def inspect_products(root, base):
    app = base / 'SimpleX.app'
    bundles = {'SimpleX': app, 'SimpleXChat': app / 'Frameworks/SimpleXChat.framework'}
    products = []
    if list(app.rglob('*.appex')):
        raise ValueError('unexpected embedded extension')
    for name, bundle in bundles.items():
        path = session.inside(root, bundle / name)
        device_macho(path.read_bytes(), {2} if name == 'SimpleX' else {6})
        info = plistlib.loads((bundle / 'Info.plist').read_bytes())
        expected = BUNDLE if name == 'SimpleX' else BUNDLE + '.shared'
        if info.get('CFBundleIdentifier') != expected:
            raise ValueError('device product bundle identifier differs')
        signed = subprocess.run(['codesign', '-dv', str(bundle)], capture_output=True,
                                env=session.environment(root), timeout=30)
        if signed.returncode == 0 or b'not signed at all' not in signed.stderr:
            raise ValueError('unsigned state not confirmed')
        if (bundle / 'embedded.mobileprovision').exists() or (bundle / '_CodeSignature').exists():
            raise ValueError('unexpected profile or signature')
        products.append(dict(name=name, path=str(path.relative_to(root)), sha256=native.sha256(path),
                             bytes=path.stat().st_size, architecture='arm64', platform=2,
                             has_extensions=False, has_profile=False, has_signature=False))
    return products


def run(root, name, bundle, component_source, derivation, prior_receipt, packages, vendor_zip,
        identity_profile=None, technical_mode=False):
    root = root.resolve()
    profile = profile_hash = None
    if identity_profile is not None:
        profile_body = identity_profile.read_bytes()
        profile = plistlib.loads(profile_body)
        storage.configuration(profile)
        profile_hash = hashlib.sha256(profile_body).hexdigest()
    if technical_mode and profile is None:
        raise ValueError('technical mode requires the qualified identity profile')
    attempt = session.new_attempt(root, name)
    source = source_files(root)
    core = core_files(root)
    recipes = {n: native.sha256(root / n) for n in (
        'flake.nix', 'flake.lock', 'cabal.project', 'simplex-chat.cabal', native.LOCK,
        'tools/taverna/device_build.py')}
    if profile is not None:
        recipes['tools/taverna/device_identity.py'] = native.sha256(root / 'tools/taverna/device_identity.py')
    if technical_mode:
        for name in ('tools/taverna/device_test.py', 'tools/taverna/device_test/DeviceTestApp.swift', 'tools/taverna/device_test/DeviceTestPolicy.swift', 'tools/taverna/device_test/SwiftyGif.LICENSE.txt'):
            recipes[name] = native.sha256(root / name)
    prior = json.loads(prior_receipt.read_text())
    if prior.get('core_sha256') != core:
        raise ValueError('qualified core source differs')
    component = verify_component_source(component_source, core)
    if not bundle.resolve().is_relative_to('/nix/store'):
        raise ValueError('native bundle must be immutable store output')
    drv_data = json.loads(subprocess.check_output([
        NIX, '--extra-experimental-features', 'nix-command', 'derivation', 'show', str(derivation)],
        env=session.environment(root), timeout=30))
    entries = drv_data.get('derivations', drv_data)
    entry = entries.get(derivation.name) or entries.get(str(derivation))
    if not entry or Path(entry['env']['src']) != component_source:
        raise ValueError('native derivation source mismatch')
    output = entry['outputs']['out']['path']
    if not output.startswith('/'):
        output = '/nix/store/' + output
    if bundle.resolve().parent != Path(output):
        raise ValueError('native derivation output mismatch')
    tree = attempt / 'source'
    shutil.copytree(root / 'apps/ios', tree / 'apps/ios',
                    ignore=shutil.ignore_patterns('Libraries', 'xcuserdata'))
    for path in (tree / 'apps/ios').rglob('*'):
        if path.is_symlink():
            raise ValueError('symlink in owned source copy')
    project = render(read_project(root / PROJECT))
    projection_hashes = {}
    if profile is not None:
        overlay = storage.render(project, {p: (tree / p).read_bytes() for p in storage.INPUTS}, profile)
        for path, body in overlay.items():
            (tree / path).write_bytes(body)
        projection_hashes = {p: native.sha256(tree / p) for p in overlay}
        project = plistlib.loads(overlay[PROJECT])
    else:
        (tree / PROJECT).write_bytes(plistlib.dumps(project))
    resource_inventory = []
    technical_hashes = {}
    if technical_mode:
        resources = technical.render(project, plistlib.loads((tree / storage.INFO).read_bytes()), root)
        for filename in ('DeviceTestApp.swift', 'DeviceTestPolicy.swift'):
            resources['apps/ios/' + filename] = (root / technical.SOURCE_DIR / filename).read_bytes()
        resource_inventory = technical.inventory(root, resources)
        for path, body in resources.items():
            (tree / path).parent.mkdir(parents=True, exist_ok=True)
            (tree / path).write_bytes(body)
        technical_hashes = {p: native.sha256(tree / p) for p in resources}
        projection_hashes = {p: native.sha256(tree / p) for p in projection_hashes}
        project = plistlib.loads(resources[PROJECT])
        write_json(attempt / 'graphics-inventory.json', resource_inventory)
    asset_script = tree / ASSET_SCRIPT
    asset_script.parent.mkdir(parents=True)
    shutil.copy2(root / ASSET_SCRIPT, asset_script)
    target = next(t for t in project['objects'][project['rootObject']]['targets']
                  if project['objects'][t]['name'] == HOST)
    scheme = tree / 'apps/ios/SimpleX.xcodeproj/xcshareddata/xcschemes/Device Build.xcscheme'
    scheme.write_text('<Scheme version="1.3"><BuildAction parallelizeBuildables="YES" '
                      'buildImplicitDependencies="YES"><BuildActionEntries><BuildActionEntry '
                      'buildForRunning="YES" buildForTesting="NO" buildForProfiling="NO" '
                      'buildForArchiving="NO" buildForAnalyzing="YES"><BuildableReference '
                      'BuildableIdentifier="primary" BlueprintIdentifier="' + target + '" '
                      'BuildableName="SimpleX.app" BlueprintName="SimpleX (iOS)" '
                      'ReferencedContainer="container:SimpleX.xcodeproj"/></BuildActionEntry>'
                      '</BuildActionEntries></BuildAction></Scheme>')
    libs = tree / 'apps/ios/Libraries/ios'
    libs.mkdir(parents=True)
    expected = {r['name']: r['original_sha256'] for r in prior['libraries']}
    if set(expected) != EXPECTED_LIBS:
        raise ValueError('qualified native library set differs')
    libraries = []
    with zipfile.ZipFile(bundle) as archive:
        if len(archive.infolist()) != 5 or set(archive.namelist()) != EXPECTED_LIBS:
            raise ValueError('unexpected native bundle entries')
        if sum(x.file_size for x in archive.infolist()) > native.MAX_BYTES:
            raise ValueError('oversized native bundle')
        for filename in sorted(EXPECTED_LIBS):
            body = archive.read(filename)
            row = inspect_library(body)
            if row['sha256'] != expected[filename]:
                raise ValueError('qualified native archive hash differs')
            path = libs / filename
            path.write_bytes(body)
            libraries.append(dict(name=filename, path=str(path.relative_to(root)), **row))
    owned_packages = root / '.build/SourcePackages'
    if not owned_packages.exists():
        prepare_packages(root, packages)
    for path in owned_packages.rglob('*'):
        if path.is_symlink() and not path.resolve().is_relative_to(owned_packages):
            raise ValueError('package link escapes owned copy')
    pins = json.loads((root / native.LOCK).read_text())['pins']
    for pin in pins:
        candidates = [p for p in (owned_packages / 'checkouts').iterdir()
                      if p.name.lower() == pin['identity'].lower()]
        if len(candidates) != 1:
            raise ValueError('locked package missing')
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=candidates[0],
                                           env=session.environment(root), text=True).strip()
        if revision != pin['state']['revision']:
            raise ValueError('locked package revision differs')
    if technical_mode:
        gif_dirs = [p for p in (owned_packages / 'checkouts').iterdir() if p.name.lower() == 'swiftygif']
        if len(gif_dirs) != 1 or (gif_dirs[0] / 'LICENSE').read_bytes() != (root / technical.SOURCE_DIR / 'SwiftyGif.LICENSE.txt').read_bytes():
            raise ValueError('retained package license differs from locked source')
    manifest = json.loads((root / '.specs/features/ios-first-build/native-inputs.json').read_text())
    if native.sha256(vendor_zip) != manifest['webrtc']['received_sha256']:
        raise ValueError('locked WebRTC archive checksum differs')
    vendor = root / '.build/SourcePackages/artifacts/webrtc/WebRTC/WebRTC.xcframework/ios-arm64/WebRTC.framework/WebRTC'
    with zipfile.ZipFile(vendor_zip) as archive:
        matches = [p for p in archive.namelist()
                   if p.endswith('WebRTC.xcframework/ios-arm64/WebRTC.framework/WebRTC')]
        if len(matches) != 1 or hashlib.sha256(archive.read(matches[0])).hexdigest() != native.sha256(vendor):
            raise ValueError('WebRTC device binary differs from locked archive')
    vendor_record = inspect_vendor_binary(vendor.read_bytes())
    vendor_record.update(path=str(vendor.relative_to(root)), name='WebRTC',
                         archive_sha256=native.sha256(vendor_zip),
                         package_revision=json.loads((root / native.LOCK).read_text())['pins'])
    cmd = build_command(root, tree / 'apps/ios/SimpleX.xcodeproj', identity=profile is not None, technical_mode=technical_mode)
    validate_command(root, cmd)
    compiled = source_files(tree)
    settings_cmd = list(cmd)
    settings_cmd[1:2] = ['-showBuildSettings', '-json']
    with (attempt / 'settings.stderr.log').open('w') as err:
        settings = subprocess.run(settings_cmd, cwd=root, env=session.environment(root),
                                  stdout=subprocess.PIPE, stderr=err, timeout=300, text=True)
    (attempt / 'settings.json').write_text(settings.stdout)
    if settings.returncode:
        raise ValueError('device build settings failed')
    for target_settings in json.loads(settings.stdout):
        values = target_settings['buildSettings']
        session.validate_build_paths(root, values)
        if values.get('PLATFORM_NAME') != 'iphoneos' or values.get('CODE_SIGNING_ALLOWED') != 'NO':
            raise ValueError('unsafe effective device build settings')
    if profile is not None:
        host_settings = [row['buildSettings'] for row in json.loads(settings.stdout) if row.get('target') == HOST]
        if len(host_settings) != 1:
            raise ValueError('missing or ambiguous effective host settings')
        storage.validate_host_settings(host_settings[0])
    write_json(attempt / 'inputs.json', dict(command=cmd, libraries=libraries,
               core_sha256=core, component_sha256=component, recipe_sha256=recipes,
               source_sha256=source, compiled_sha256=compiled, vendor=vendor_record,
               identity_profile_sha256=profile_hash, identity_projection_sha256=projection_hashes))
    with (attempt / 'build.log').open('w') as log:
        result = subprocess.run(cmd, cwd=root, env=session.environment(root),
                                stdout=log, stderr=subprocess.STDOUT, timeout=5400)
    if result.returncode or '** BUILD SUCCEEDED **' not in (attempt / 'build.log').read_text():
        raise ValueError('device build failed; see owned build.log')
    base = Path(cmd[cmd.index('-derivedDataPath') + 1]) / 'Build/Products/Debug-iphoneos'
    products = inspect_products(root, base)
    identity_result = None
    if profile is not None:
        if native.sha256(identity_profile) != profile_hash:
            raise ValueError('private profile input changed during build')
        identity_result = storage.inspect_package(tree, base / 'SimpleX.app', profile, projection_hashes)
        identity_result['profile_sha256'] = profile_hash
        storage.validate_result(identity_result)
    technical_result = None
    if technical_mode:
        if {p: native.sha256(tree / p) for p in technical_hashes} != technical_hashes:
            raise ValueError('technical projection changed during build')
        technical_result = dict(status='UNSIGNED_TECHNICAL_PACKAGE_PASS',
            projection_sha256=technical_hashes,
            inventory_sha256=native.sha256(attempt / 'graphics-inventory.json'),
            package_sha256=technical.inspect_resources(base / 'SimpleX.app', root),
            limits=dict(technical.LIMITS))
    if source_files(tree) != compiled:
        raise ValueError('compiled source copy changed')
    for row in libraries + [vendor_record]:
        if native.sha256(root / row['path']) != row['sha256']:
            raise ValueError('native input changed during build')
    if recipes != {n: native.sha256(root / n) for n in recipes}:
        raise ValueError('build recipe changed')
    receipt = dict(status='UNSIGNED_DEVICE_BUILD_PASS', build_exit_code=result.returncode,
                   source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                   command=cmd, core_sha256=core, component_sha256=component,
                   source_sha256=source, source_after_sha256=source_files(root),
                   compiled_sha256=compiled, recipe_sha256=recipes, libraries=libraries,
                   products=products, vendor=vendor_record, core_derivation=derivation.name,
                   bundle_sha256=native.sha256(bundle), limits=dict(LIMITS))
    if identity_result is not None:
        receipt['identity'] = identity_result
    if technical_result is not None:
        receipt['technical'] = technical_result
    validate_receipt(root, receipt)
    write_json(attempt / 'receipt.json', receipt)
    return receipt


def render(project):
    data = copy.deepcopy(project)
    objects = data['objects']
    root = objects[data['rootObject']]
    targets = {objects[t]['name']: t for t in root['targets']}
    host, shared = targets[HOST], targets[SHARED]
    expected = {HOST: EXTENSIONS | {SHARED}, SHARED: set()}
    for name, wanted in expected.items():
        actual = [objects[objects[d]['target']]['name']
                  for d in objects[targets[name]]['dependencies']]
        if len(actual) != len(wanted) or set(actual) != wanted:
            raise ValueError('unexpected source dependency graph')
    target = objects[host]
    target['dependencies'] = [d for d in target['dependencies']
                              if objects[d]['target'] == shared]
    phases = [objects[p] for p in target['buildPhases']
              if objects[p]['isa'] == 'PBXCopyFilesBuildPhase'
              and str(objects[p].get('dstSubfolderSpec')) == '13']
    if len(phases) != 1:
        raise ValueError('unexpected source extension phase')
    products = [objects[f]['fileRef'] for f in phases[0]['files']]
    if len(products) != 2 or set(products) != {
            objects[targets[n]]['productReference'] for n in EXTENSIONS}:
        raise ValueError('unexpected source embedded extensions')
    phases[0]['files'] = []
    root['targets'] = [host, shared]
    attributes = root.get('attributes', {}).get('TargetAttributes', {})
    root['attributes']['TargetAttributes'] = {
        k: v for k, v in attributes.items() if k in (host, shared)}
    for name, identifier in ((HOST, BUNDLE), (SHARED, BUNDLE + '.shared')):
        configurations = objects[objects[targets[name]]['buildConfigurationList']]
        for config in configurations['buildConfigurations']:
            objects[config]['buildSettings']['PRODUCT_BUNDLE_IDENTIFIER'] = identifier
    for obj in objects.values():
        if obj['isa'] == 'XCBuildConfiguration':
            obj['buildSettings'].update(
                SUPPORTED_PLATFORMS='iphoneos', SDKROOT='iphoneos',
                CODE_SIGNING_ALLOWED='NO', CODE_SIGNING_REQUIRED='NO',
                CODE_SIGN_STYLE='Manual', CODE_SIGN_IDENTITY='',
                DEVELOPMENT_TEAM='', PROVISIONING_PROFILE='',
                PROVISIONING_PROFILE_SPECIFIER='')
    seen = set()

    def visit(value):
        if isinstance(value, str) and value in objects and value not in seen:
            seen.add(value)
            visit(objects[value])
        elif isinstance(value, dict):
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(data['rootObject'])
    data['objects'] = {k: v for k, v in objects.items() if k in seen}
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('bundle', 'component-source', 'derivation', 'prior-receipt', 'packages-source', 'vendor-zip'):
        parser.add_argument('--' + arg, type=Path, required=True)
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--technical', action='store_true', help='original technical host and private foreground bootstrap; unsigned only')
    parser.add_argument('--identity-profile', type=Path,
                        help='private decoded plist of the already CMS/trust-verified development profile')
    args = parser.parse_args()
    try:
        receipt = run(ROOT, args.attempt, args.bundle, args.component_source, args.derivation,
                      args.prior_receipt, args.packages_source, args.vendor_zip, args.identity_profile, args.technical)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('BLOCKED: ' + str(error), file=sys.stderr)
        raise SystemExit(2)
    print(json.dumps(dict(status=receipt['status'], products=len(receipt['products']),
                         installation=receipt['limits']['installation'])))
