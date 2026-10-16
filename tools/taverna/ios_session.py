#!/usr/bin/env python3
"""Local first-build session tools. No accounts, profiles or remote mutations."""
import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import time


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inside(root, path):
    result = Path(path).resolve(strict=True)
    if not result.is_relative_to(root.resolve()):
        raise ValueError(f'path outside worktree: {path}')
    return result


def validate_session(root, record, selected_udid):
    if not record.get('owner') or Path(record['worktree']).resolve() != root.resolve():
        raise ValueError('session worktree/owner mismatch')
    if selected_udid != record['udid']:
        raise ValueError('Xcode destination does not match owned session')
    for storage_key, index_key in [('storage', 'index'), ('logs', 'log_index')]:
        storage = inside(root, record[storage_key])
        index = Path(record[index_key])
        if not index.is_symlink() or index.resolve(strict=True) != storage:
            raise ValueError(f'{index_key}: index does not point to owned storage')
        if index.name != record['udid'] or storage.name != record['udid']:
            raise ValueError('device identity mismatch in paths')
        # Carry canonical physical paths into subsequent commands and receipts.
        record[storage_key] = str(storage)
    device = plistlib.loads((Path(record['storage']) / 'device.plist').read_bytes())
    if device.get('UDID') != record['udid']:
        raise ValueError('device identity does not match session')
    inside(root, Path(record['storage']) / 'data')


def validate_sdk_indexes(record, home=None):
    home = home or Path(os.environ['HOME'])
    expected = dict(index=home / 'Library/Developer/CoreSimulator/Devices' / record['udid'],
                    log_index=home / 'Library/Logs/CoreSimulator' / record['udid'])
    for key, path in expected.items():
        # Compare entries themselves, not their symlink targets.
        if Path(record[key]).absolute() != path.absolute():
            raise ValueError(f'{key}: standard SDK index required')


def validate_guard(root, manifest):
    if not manifest:
        raise ValueError('missing guard manifest')
    for name, expected in manifest.items():
        path = Path(name)
        if not path.is_file():
            raise ValueError(f'missing guard: {path}')
        inside(root, path)
        if sha256(path) != expected:
            raise ValueError(f'guard hash mismatch: {path}')


def guard_proof(path, pid):
    for line in Path(path).read_text().splitlines():
        record = json.loads(line)
        if (record.get('pid') == pid and record.get('executable') == 'SimpleX'
                and record.get('phase') == 'before_main'
                and record.get('ipv4_errno') in (errno.EPERM, errno.EACCES)
                and record.get('ipv6_errno') in (errno.EPERM, errno.EACCES)
                and record.get('loopback') is True):
            return record
    raise ValueError('no valid before-main containment proof for app pid')


def new_attempt(root, name):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', name):
        raise ValueError('invalid attempt name')
    parent = root / '.build/attempts'
    parent.mkdir(parents=True, exist_ok=True)
    inside(root, parent)
    path = parent / name
    path.mkdir()  # Never reuse or remove a previous attempt.
    return path


def environment(root):
    env = {key: value for key, value in os.environ.items()
           if key in ('PATH', 'HOME', 'USER', 'LOGNAME', 'SHELL', 'LANG') or key.startswith('LC_')}
    for key, name in {'CFFIXED_USER_HOME': 'xcode-user', 'TMPDIR': 'xcode-tmp',
                      'CLANG_MODULE_CACHE_PATH': 'clang-module-cache',
                      'SWIFT_MODULE_CACHE_PATH': 'swift-module-cache',
                      'XDG_CONFIG_HOME': 'xcode-config', 'XDG_CACHE_HOME': 'xcode-cache'}.items():
        path = root / '.build' / name
        path.mkdir(parents=True, exist_ok=True)
        inside(root, path)
        env[key] = str(path) + ('/' if key == 'TMPDIR' else '')
    env.update(DEVELOPER_DIR='/Applications/Xcode.app/Contents/Developer',
               GIT_TERMINAL_PROMPT='0', GIT_ASKPASS='/usr/bin/false',
               GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')
    return env


def build_cache_args(root):
    return [f'CACHE_ROOT={root}/.build/xcode-build-cache',
            f'SHARED_PRECOMPS_DIR={root}/.build/PrecompiledHeaders',
            f'SDK_STAT_CACHE_DIR={root}/.build/SDKStatCaches',
            f'COMPILATION_CACHE_CAS_PATH={root}/.build/xcode-build-cache/CompilationCache.noindex']


def validate_build_paths(root, settings):
    required = ('CACHE_ROOT', 'SHARED_PRECOMPS_DIR', 'SDK_STAT_CACHE_DIR', 'COMPILATION_CACHE_CAS_PATH')
    optional = ('PROJECT_TEMP_ROOT', 'CONFIGURATION_BUILD_DIR',
                'CONFIGURATION_TEMP_DIR', 'DERIVED_FILE_DIR', 'OBJECT_FILE_DIR', 'SYMROOT')
    for key in required + optional:
        if key in optional and key not in settings:
            continue
        value = settings.get(key)
        if not value or not Path(value).resolve().is_relative_to(root.resolve()):
            raise ValueError(f'{key}: build state outside worktree or missing')


def run(command, root, env, timeout=120):
    return subprocess.run(command, cwd=root, env=env, text=True, capture_output=True,
                          timeout=timeout, check=True)


def create(root, owner, runtime, device_type):
    record_path = root / '.build/ios-session.json'
    if record_path.exists():
        raise ValueError('session exists; inspect and reconcile before creating another')
    env = environment(root)
    # The standard index must see the native registration before relocating storage.
    udid = run(['xcrun', 'simctl', 'create', f'Taverna-{root.name}', device_type, runtime],
               root, env).stdout.strip()
    if not re.fullmatch(r'[A-Fa-f0-9-]{36}', udid):
        raise ValueError('simctl did not return a UDID; inspect registration manually')
    home = Path(os.environ['HOME'])
    index = home / 'Library/Developer/CoreSimulator/Devices' / udid
    storage = root / '.build/SimulatorDevices' / udid
    logs = root / '.build/SimulatorLogs' / udid
    log_index = home / 'Library/Logs/CoreSimulator' / udid
    record = dict(owner=owner, worktree=str(root), udid=udid, storage=str(storage),
                  logs=str(logs), index=str(index), log_index=str(log_index),
                  runtime=runtime, device_type=device_type, state='registration-created')
    # Save ownership before any move; a partial failure requires reconciliation.
    record_path.write_text(json.dumps(record, indent=2) + '\n')
    storage.parent.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True)
    if storage.exists() or index.is_symlink() or not index.is_dir() or log_index.exists():
        raise ValueError('registration paths conflict; preserve and reconcile')
    index.rename(storage)
    index.symlink_to(storage, target_is_directory=True)
    log_index.parent.mkdir(parents=True, exist_ok=True)
    log_index.symlink_to(logs, target_is_directory=True)
    validate_session(root, record, udid)
    validate_sdk_indexes(record)
    record['state'] = 'Shutdown'
    record_path.write_text(json.dumps(record, indent=2) + '\n')
    return record


def build_guard(root, attempt):
    env = environment(root)
    source = root / 'tools/taverna/ios'
    host = attempt / 'host-sandbox'
    library = attempt / 'process-guard.dylib'
    sdk = run(['xcrun', '--sdk', 'iphonesimulator', '--show-sdk-path'], root, env).stdout.strip()
    commands = [
        ['xcrun', '--sdk', 'macosx', 'clang', '-Wall', '-Wextra', str(source / 'host-sandbox.c'), '-o', str(host)],
        ['xcrun', '--sdk', 'iphonesimulator', 'clang', '-Wall', '-Wextra', '-target',
         'arm64-apple-ios15.0-simulator', '-isysroot', sdk, '-dynamiclib',
         str(source / 'process-guard.c'), '-o', str(library)],
        ['codesign', '--force', '--sign', '-', str(library)],
    ]
    for i, command in enumerate(commands):
        result = run(command, root, env)
        (attempt / f'compile-{i}.json').write_text(json.dumps(dict(command=command,
            exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr), indent=2) + '\n')
    files = [source / 'host-sandbox.c', source / 'process-guard.c', host, library]
    manifest = {str(path): sha256(path) for path in files}
    validate_guard(root, manifest)
    (attempt / 'guard-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return dict(DYLD_INSERT_LIBRARIES=str(library), TAVERNA_HOST_GUARD=str(host),
                TAVERNA_GUARD_LOG=str(attempt / 'guard.jsonl'))


def preflight(root, record, attempt, guard_manifest):
    validate_sdk_indexes(record)
    validate_session(root, record, record['udid'])
    validate_guard(root, guard_manifest)
    command = ['xcodebuild', '-showBuildSettings', '-json', '-project',
        'apps/ios/SimpleX.xcodeproj', '-scheme', 'SimpleX (iOS)', '-configuration', 'Debug',
        '-sdk', 'iphonesimulator', '-destination', f"platform=iOS Simulator,id={record['udid']}",
        '-destination-timeout', '10', '-clonedSourcePackagesDirPath', str(root / '.build/SourcePackages'),
        '-packageCachePath', str(root / '.build/package-cache'),
        '-derivedDataPath', str(root / '.build/DerivedData'), '-disableAutomaticPackageResolution',
        '-onlyUsePackageVersionsFromResolvedFile', '-skipPackageUpdates', '-scmProvider', 'system',
        '-resultBundlePath', str(attempt / 'settings.xcresult'), 'CODE_SIGNING_ALLOWED=NO',
        'DEVELOPMENT_TEAM=', 'CODE_SIGN_IDENTITY=', 'ARCHS=arm64', 'ONLY_ACTIVE_ARCH=YES']
    command += build_cache_args(root)
    result = subprocess.run(command, cwd=root, env=environment(root), capture_output=True,
                            text=True, timeout=300)
    (attempt / 'settings.stdout').write_text(result.stdout)
    (attempt / 'settings.stderr').write_text(result.stderr)
    (attempt / 'settings-command.json').write_text(json.dumps(dict(command=command,
        exit_code=result.returncode), indent=2) + '\n')
    if result.returncode:
        raise ValueError(f'Xcode preflight failed: exit {result.returncode}')
    targets = json.loads(result.stdout)
    if not targets:
        raise ValueError('missing Xcode destination settings')
    for target in targets:
        settings = target['buildSettings']
        validate_build_paths(root, settings)
        validate_session(root, record, settings.get('TARGET_DEVICE_IDENTIFIER'))
        if settings.get('PLATFORM_NAME') != 'iphonesimulator':
            raise ValueError('Xcode destination platform mismatch')
    proof = dict(session=record, targets=targets, guard_manifest=guard_manifest,
                 app_build='NOT RUN', app_launch='NOT RUN')
    (attempt / 'preflight.json').write_text(json.dumps(proof, indent=2) + '\n')
    return proof


def control(root, record, attempt, manifest):
    """Integration gate with our own UIKit control, never the messenger."""
    preflight(root, record, attempt, manifest)
    env = environment(root)
    steps = []

    def step(name, command, extra=None, timeout=120):
        try:
            result = subprocess.run(command, cwd=root, env=dict(env, **(extra or {})),
                capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            steps.append(dict(name=name, command=command, exit_code=124, timeout=True))
            (attempt / 'steps.json').write_text(json.dumps(steps, indent=2) + '\n')
            raise
        (attempt / f'{name}.stdout').write_text(result.stdout)
        (attempt / f'{name}.stderr').write_text(result.stderr)
        steps.append(dict(name=name, command=command, exit_code=result.returncode))
        (attempt / 'steps.json').write_text(json.dumps(steps, indent=2) + '\n')
        result.check_returncode()
        return result.stdout

    binaries = {Path(path).name: path for path in manifest}
    source = root / 'tools/taverna/ios'
    for name in ('host-sandbox.c', 'process-guard.c', 'host-sandbox', 'process-guard.dylib'):
        if name not in binaries:
            raise ValueError(f'missing guard component: {name}')
    for name in ('host-sandbox.c', 'process-guard.c'):
        if Path(binaries[name]).resolve() != source / name:
            raise ValueError(f'guard source does not belong to checkout: {name}')
    sdk = step('sdk', ['xcrun', '--sdk', 'iphonesimulator', '--show-sdk-path']).strip()
    app = attempt / 'SessionControl.app'
    app.mkdir()
    bundle = 'cc.quietmesh.taverna.session-control'
    info = dict(CFBundleIdentifier=bundle, CFBundleExecutable='SimpleX',
        CFBundleName='Session control', CFBundlePackageType='APPL', CFBundleVersion='1',
        CFBundleShortVersionString='1.0', LSRequiresIPhoneOS=True, MinimumOSVersion='15.0',
        UIApplicationSceneManifest=dict(UIApplicationSupportsMultipleScenes=False, UISceneConfigurations={}))
    (app / 'Info.plist').write_bytes(plistlib.dumps(info))
    step('compile', ['xcrun', '--sdk', 'iphonesimulator', 'clang', '-target',
        'arm64-apple-ios15.0-simulator', '-isysroot', sdk, '-fobjc-arc', '-framework',
        'UIKit', '-framework', 'Foundation', str(source / 'control.m'), '-o', str(app / 'SimpleX')])
    step('sign', ['codesign', '--force', '--sign', '-', str(app)])
    # Never erase/clone/delete devices. A busy device causes boot to fail.
    step('boot', ['xcrun', 'simctl', 'boot', record['udid'], '--arch=arm64'])
    try:
        step('bootstatus', ['xcrun', 'simctl', 'bootstatus', record['udid'], '-b'])
        step('install', ['xcrun', 'simctl', 'install', record['udid'], str(app)])
        extra = dict(SIMCTL_CHILD_DYLD_INSERT_LIBRARIES=binaries['process-guard.dylib'],
            SIMCTL_CHILD_TAVERNA_HOST_GUARD=binaries['host-sandbox'],
            SIMCTL_CHILD_TAVERNA_GUARD_LOG=str(attempt / 'guard.jsonl'))
        launch = step('launch', ['xcrun', 'simctl', 'launch', '--terminate-running-process',
            '--stdout=' + str(attempt / 'app.stdout'), '--stderr=' + str(attempt / 'app.stderr'),
            record['udid'], bundle], extra)
        pid = int(launch.strip().rsplit(':', 1)[1])
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if (attempt / 'app.stdout').is_file() and 'UIKIT_CONTROL_READY' in (attempt / 'app.stdout').read_text():
                break
            time.sleep(.2)
        proof = guard_proof(attempt / 'guard.jsonl', pid)
        if 'UIKIT_CONTROL_READY' not in (attempt / 'app.stdout').read_text():
            raise ValueError('control never reached UIKit interface')
        step('terminate', ['xcrun', 'simctl', 'terminate', record['udid'], bundle])
        step('uncontained-launch', ['xcrun', 'simctl', 'launch',
            '--stdout=' + str(attempt / 'uncontained.stdout'),
            '--stderr=' + str(attempt / 'uncontained.stderr'), record['udid'], bundle])
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            path = attempt / 'uncontained.stdout'
            if path.is_file() and 'UIKIT_EXTERNAL_CONNECT_ERRNO=' in path.read_text():
                break
            time.sleep(.2)
        output = (attempt / 'uncontained.stdout').read_text()
        if 'UIKIT_CONTROL_READY' in output or f'UIKIT_EXTERNAL_CONNECT_ERRNO={errno.EINPROGRESS}' not in output:
            raise ValueError('uncontained control did not discriminate policy')
        receipt = dict(synthetic_control=True, taverna_build='NOT RUN', pid=pid,
            guard_proof=proof, negative_control_rejected=True, guard_manifest=manifest,
            control_source_hash=sha256(source / 'control.m'), executable_hash=sha256(app / 'SimpleX'))
    finally:
        step('shutdown', ['xcrun', 'simctl', 'shutdown', record['udid']])
    (attempt / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    create_parser = sub.add_parser('create')
    create_parser.add_argument('--owner', required=True)
    create_parser.add_argument('--runtime', required=True)
    create_parser.add_argument('--device-type', required=True)
    check_parser = sub.add_parser('check')
    check_parser.add_argument('--udid', required=True)
    guard_parser = sub.add_parser('guard')
    guard_parser.add_argument('--attempt', required=True)
    preflight_parser = sub.add_parser('preflight')
    preflight_parser.add_argument('--attempt', required=True)
    preflight_parser.add_argument('--guard-manifest', type=Path, required=True)
    control_parser = sub.add_parser('control')
    control_parser.add_argument('--attempt', required=True)
    control_parser.add_argument('--guard-manifest', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    if args.command == 'create':
        result = create(root, args.owner, args.runtime, args.device_type)
    elif args.command == 'check':
        result = json.loads((root / '.build/ios-session.json').read_text())
        validate_sdk_indexes(result)
        validate_session(root, result, args.udid)
    elif args.command == 'guard':
        result = build_guard(root, new_attempt(root, args.attempt))
    else:
        record = json.loads((root / '.build/ios-session.json').read_text())
        manifest = json.loads(args.guard_manifest.read_text())
        operation = control if args.command == 'control' else preflight
        result = operation(root, record, new_attempt(root, args.attempt), manifest)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        sys.exit(2)
