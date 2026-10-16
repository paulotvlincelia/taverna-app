#!/usr/bin/env python3
"""Record and validate local iOS proof. Simulator success never proves device push."""
import argparse
import datetime
import hashlib
import json
import plistlib
from pathlib import Path
import re
import subprocess
import sys
import time

import ios_native as native
import ios_session as session

sha256 = native.sha256
require = native.require
REQUIRED_TESTS = {'Tests_iOS/testExample()', 'Tests_iOS/testLaunchPerformance()',
                  'Tests_iOS/testFirstBuildOnboarding()', 'Tests_iOSLaunchTests/testLaunch()'}
PRODUCTS = {'SimpleX.app': 'SimpleX', 'SimpleXChat.framework': 'SimpleXChat',
            'SimpleX NSE.appex': 'SimpleX NSE', 'SimpleX SE.appex': 'SimpleX SE'}
NATIVE_SYMBOLS = {'_chat_migrate_init_key', '_chat_send_cmd', '_chat_recv_msg_wait', '_hs_init'}


def validate_stage(name, record):
    require(record and type(record.get('exit_code')) is int and record['exit_code'] == 0,
            name + ': missing or failed required stage')
    require(record.get('command') and isinstance(record['command'], list), name + ': missing command')
    require(not record.get('timed_out') and not record.get('test_timed_out'), name + ': timeout')
    require(record.get('test_exit_code', 0) == 0, name + ': test failure hidden by aggregate exit code')


def validate_profile(record, plan):
    profile = record.get('ui_profile')
    require(profile in ('first-build', 'full-matrix'), 'missing or unknown UI profile')
    require(plan.get('EnvironmentVariables', {}).get('TAVERNA_UI_PROFILE') == profile,
            'runner UI profile mismatch')
    require(not plan.get('OnlyTestIdentifiers') and not plan.get('SkipTestIdentifiers'), 'filtered UI profile')
    if profile == 'first-build':
        require(all(record.get(key) == value for key, value in
                    [('ui_language', 'en'), ('ui_region', 'US'), ('ui_orientation', 'portrait'),
                     ('ui_appearance', 'light')]), 'first-build UI profile configuration mismatch')
    return profile


def validate_clean_source(record, strict):
    require(not strict or record.get('source_state') == '', 'clean source required for final reproduction')


def artifact(root, record):
    path = session.inside(root, record['path'])
    require(path.is_file(), 'missing artifact: ' + str(path))
    require(sha256(path) == record['sha256'], 'artifact hash mismatch: ' + str(path))
    return path


def product_platform(path):
    value = native.macho(path.read_bytes())
    require(value['header'][1] == 16777228 and value['header'][3] in (2, 6)
            and value['platforms'] == [7], 'product must be arm64 iOS Simulator')
    return dict(architecture='arm64', platform=7)


def validate_results(summary, tree, udid):
    total = summary.get('totalTestCount', 0)
    require(type(total) is int and total > 0, 'empty test execution')
    require(summary.get('result') == 'Passed' and summary.get('passedTests') == total,
            'test summary not fully passed')
    require(all(summary.get(key) == 0 for key in ('failedTests', 'skippedTests', 'expectedFailures'))
            and summary.get('testFailures') == [], 'test failure/skip present')
    devices = tree.get('devices', [])
    require(devices and all(d.get('deviceId') == udid and d.get('architecture') == 'arm64'
            and d.get('platform') == 'iOS Simulator' for d in devices), 'test destination mismatch')
    configs = summary.get('devicesAndConfigurations', [])
    require(configs and all(c.get('device') in devices for c in configs), 'summary destination mismatch')
    seen = set()
    def visit(node):
        if node.get('nodeType') == 'Test Case':
            require(node.get('result') == 'Passed', 'test case is ' + str(node.get('result')))
            require(node.get('nodeIdentifier'), 'test case identifier missing')
            seen.add(node['nodeIdentifier'])
        elif node.get('nodeType') == 'Test Case Run':
            require(node.get('result') == 'Passed', 'test case run did not pass')
        for child in node.get('children', []):
            visit(child)
    for node in tree.get('testNodes', []):
        visit(node)
    require(REQUIRED_TESTS <= seen, 'required tests not executed: ' + ', '.join(sorted(REQUIRED_TESTS - seen)))
    require(total >= len(REQUIRED_TESTS), 'required test count mismatch')
    return dict(executed=total, failed=summary['failedTests'], skipped=summary['skippedTests'],
                required_cases=sorted(REQUIRED_TESTS), discovered_cases=sorted(seen))


def console_counts(text):
    from collections import Counter
    records = re.findall(r"^Test Case '-\[(\S+) (\S+)\]' (started|passed|failed)", text, flags=re.M)
    counters = {state: Counter() for state in ('started', 'passed', 'failed')}
    for cls, name, state in records:
        counters[state][cls.split('.')[-1] + '/' + name + '()'] += 1
    require(not counters['failed'] and counters['started'] == counters['passed']
            and REQUIRED_TESTS <= set(counters['started']), 'incomplete or failed console test executions')
    return dict(expanded_executions=sum(counters['started'].values()), expanded_passed=sum(counters['passed'].values()),
                expanded_failed=sum(counters['failed'].values()), per_method=dict(counters['passed']))


def validate_containment(events, minimum):
    require(len(events) >= minimum, 'missing before-main launch evidence')
    for event in events:
        require(type(event.get('pid')) is int and event['pid'] > 0
                and event.get('executable') == 'SimpleX' and event.get('phase') == 'before_main'
                and event.get('ipv4_errno') in (1, 13) and event.get('ipv6_errno') in (1, 13)
                and event.get('loopback') is True, 'invalid before-main containment event')


def read_json(root, path):
    return json.loads(session.inside(root, path).read_text())


def output_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def command(root, args, timeout=120):
    result = subprocess.run(args, cwd=root, env=session.environment(root), capture_output=True,
                            text=True, timeout=timeout)
    require(result.returncode == 0, f'command failed ({result.returncode}): {args[0]}: {result.stderr}')
    return result


def inspect_products(root, directory, evidence):
    products = []
    for name, executable in PRODUCTS.items():
        bundle = session.inside(root, directory / name)
        info = plistlib.loads((bundle / 'Info.plist').read_bytes())
        require(info.get('CFBundleExecutable') == executable, 'unexpected product executable: ' + name)
        binary = session.inside(root, bundle / executable)
        platform = product_platform(binary)
        display = command(root, ['codesign', '-dvv', str(bundle)])
        require('Signature=adhoc' in display.stderr and 'TeamIdentifier=not set' in display.stderr,
                'ad hoc signature without account required: ' + name)
        verified = command(root, ['codesign', '--verify', '--strict', str(bundle)])
        output_json(evidence / (name + '.signature.json'), dict(display=display.stderr,
                    verify_exit=verified.returncode, verify_stderr=verified.stderr))
        products.append(dict(name=name, path=str(binary), sha256=sha256(binary),
                             bundle_identifier=info['CFBundleIdentifier'], **platform, signing='adhoc'))
    framework = directory / 'SimpleXChat.framework/SimpleXChat'
    result = command(root, ['xcrun', 'nm', '-gU', str(framework)])
    symbols = {line.split()[-1] for line in result.stdout.splitlines() if line.split()}
    require(NATIVE_SYMBOLS <= symbols, 'real native framework symbols missing')
    (evidence / 'native-symbols.txt').write_text(result.stdout)
    return products


def code_diff(root, commit):
    return command(root, ['git', 'diff', commit, '--binary', '--', 'apps/ios']).stdout.encode()


def verify(root, build_path, test_path, native_path, bindings_path, attempt_name, strict=False):
    evidence = session.new_attempt(root, attempt_name)
    result = dict(stage='proof-validation', started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  command=sys.argv, scope='local app build and complete UI only', local_build_ui='NOT PROVEN',
                  native_core='NOT CHECKED', device_signing_push='NOT RUN',
                  distribution='BLOCKED: identity/assets/license release gates', exit_code=2)
    try:
        build_path = session.inside(root, build_path); test_path = session.inside(root, test_path)
        native_path = session.inside(root, native_path)
        build = read_json(root, build_path / 'receipt.json'); test = read_json(root, test_path / 'receipt.json')
        prepared = read_json(root, native_path / 'receipt.json')
        for name, record in [('native', prepared), ('build', build), ('test', test)]:
            validate_stage(name, record)
        validate_clean_source(build, strict)
        if strict:
            require(build.get('recording_tool_sha256') == sha256(Path(__file__))
                    and test.get('recording_tool_sha256') == sha256(Path(__file__)), 'proof recorder changed')
            require(len(build.get('products', [])) == 4, 'missing recorded build products')
        for product in build.get('products', []):
            artifact(root, product)
        require(build['commit'] == test['commit'], 'source commits differ between build and tests')
        require(test['build_receipt_sha256'] == sha256(build_path / 'receipt.json'), 'test/build receipt binding mismatch')
        manifest_path = root / '.specs/features/ios-first-build/native-inputs.json'
        manifest = read_json(root, manifest_path); native.validate_manifest(root, manifest)
        manifest_hash = sha256(manifest_path)
        require(all(r['native_manifest_sha256'] == manifest_hash for r in (build, test, prepared)), 'native manifest mismatch')
        bindings = read_json(root, bindings_path)
        require(bindings['native_manifest_sha256'] == manifest_hash, 'native binding mismatch')
        require(set(bindings['libraries']) == {r['name'] for r in manifest['libraries']}, 'native library set mismatch')
        for library in manifest['libraries']:
            path = session.inside(root, bindings['libraries'][library['name']]); native.validate_library(path, library)
            generated = session.inside(root, native_path / 'sim' / library['name']); native.validate_library(generated, library)
        artifact(root, dict(path=bindings['webrtc_binary'], sha256=manifest['webrtc']['used_binary_sha256']))
        require(prepared['tool_source_sha256'] == sha256(root / 'tools/taverna/ios_native.py'), 'native preparer changed')
        patch = (build_path / 'source-diff.patch').read_bytes()
        require(hashlib.sha256(patch).hexdigest() == build['source_diff_sha256'], 'build source patch changed')
        parts = re.split(b'(?=^diff --git )', patch, flags=re.M)
        ios_patch = b''.join(p for p in parts if p.startswith(b'diff --git ') and b'apps/ios/' in p.splitlines()[0])
        require(ios_patch == code_diff(root, build['commit']), 'iOS source changed after build')
        require(test['source_code_diff_sha256'] == hashlib.sha256(ios_patch).hexdigest(), 'test source binding mismatch')
        for name, expected in build['test_source_sha256'].items():
            artifact(root, dict(path=str(root / name), sha256=expected))
        owned = test['session']; session.validate_sdk_indexes(owned)
        session.validate_session(root, owned, owned['udid'])
        require(not test.get('new_device_ids'), 'test created an unqualified simulator')
        require(any(s['name'] == 'shutdown' and s['exit_code'] == 0 for s in test['steps']), 'owned simulator shutdown failed')
        settings = read_json(root, build_path / 'settings.stdout.json')
        required_targets = {'SimpleX (iOS)', 'SimpleXChat', 'SimpleX NSE', 'SimpleX SE', 'Tests iOS'}
        require(required_targets <= {r['target'] for r in settings}, 'missing target signing settings')
        for target in settings:
            bs = target['buildSettings']; session.validate_build_paths(root, bs)
            require(bs.get('CODE_SIGNING_ALLOWED') == 'YES' and bs.get('CODE_SIGN_IDENTITY') == '-'
                    and not bs.get('DEVELOPMENT_TEAM') and not bs.get('PROVISIONING_PROFILE_SPECIFIER'),
                    'target account/provisioning mismatch: ' + target['target'])
        xctest = session.inside(root, test_path / 'tests.xcresult')
        summary = json.loads(command(root, ['xcrun', 'xcresulttool', 'get', 'test-results', 'summary', '--path', str(xctest), '--compact']).stdout)
        tree = json.loads(command(root, ['xcrun', 'xcresulttool', 'get', 'test-results', 'tests', '--path', str(xctest), '--compact']).stdout)
        output_json(evidence / 'summary.json', summary); output_json(evidence / 'tests.json', tree)
        tests = validate_results(summary, tree, owned['udid'])
        tests.update(console_counts(session.inside(root, test_path / 'tests.stdout.log').read_text()))
        require(not any(a.startswith(('-only-testing', '-skip-testing')) for a in test['command']), 'filtered suite cannot prove complete execution')
        configured = session.inside(root, test_path / 'configured.xctestrun.plist')
        require(sha256(configured) == test['xctestrun_sha256'], 'test configuration changed')
        plan = plistlib.loads(configured.read_bytes())['Tests iOS']
        require(not plan.get('OnlyTestIdentifiers') and not plan.get('SkipTestIdentifiers'), 'filtered xctestrun')
        profile = validate_profile(test, plan)
        guard_path = Path(plan['EnvironmentVariables']['TAVERNA_GUARD_MANIFEST'])
        artifact(root, dict(path=str(guard_path), sha256=test['guard_manifest_sha256']))
        guards = read_json(root, guard_path); session.validate_guard(root, guards)
        events = []
        for file in session.inside(root, test_path / 'guard-events').glob('*.jsonl'):
            for line in session.inside(root, file).read_text().splitlines():
                events.append(json.loads(line))
        validate_containment(events, tests['expanded_executions'])
        products = inspect_products(root, root / '.build/DerivedData/Build/Products/Debug-iphonesimulator', evidence)
        if build.get('products'):
            require({p['path']: p['sha256'] for p in products} == {p['path']: p['sha256'] for p in build['products']}, 'build products changed after tests')
        result.update(exit_code=0, local_build_ui='PASS', source_commit=build['commit'], clean_source=(build['source_state'] == ''),
                      native_core='LOCAL_SOURCE_REALIZED', native_manifest_sha256=manifest_hash, products=products,
                      tests=tests, containment_events=len(events), worktree=str(root), udid=owned['udid'],
                      ui_profile=profile, full_matrix=('PENDING' if profile == 'first-build' else 'PASS'),
                      xcode=command(root, ['xcodebuild', '-version']).stdout.strip(),
                      sdk=command(root, ['xcrun', '--sdk', 'iphonesimulator', '--show-sdk-version']).stdout.strip())
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        result['error'] = str(error)
    result['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    output_json(evidence / 'receipt.json', result)
    return result


def record_stage(root, attempt, name, args, seconds):
    record = dict(name=name, command=args, started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  timeout_seconds=seconds)
    with (attempt / (name + '.stdout.log')).open('w') as out, (attempt / (name + '.stderr.log')).open('w') as err:
        process = subprocess.Popen(args, cwd=root, env=session.environment(root), stdout=out, stderr=err)
        record['pid'] = process.pid
        output_json(attempt / (name + '.active.json'), record)
        try:
            code = process.wait(timeout=seconds); timed_out = False
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()
            code, timed_out = 124, True
    record.update(exit_code=code, timed_out=timed_out,
                  finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    output_json(attempt / (name + '.receipt.json'), record)
    return record


def package_args(root):
    for name in ('SourcePackages', 'package-cache', 'DerivedData'):
        require((root / '.build' / name).resolve().is_relative_to(root.resolve()),
                name + ': writable build state escapes worktree')
    return ['-clonedSourcePackagesDirPath', str(root / '.build/SourcePackages'), '-packageCachePath',
            str(root / '.build/package-cache'), '-disableAutomaticPackageResolution',
            '-onlyUsePackageVersionsFromResolvedFile', '-skipPackageUpdates', '-scmProvider', 'system']


def guard_components(root, manifest_path):
    guards = read_json(root, manifest_path); session.validate_guard(root, guards)
    names = {Path(p).name: p for p in guards}
    require(len(guards) == 4 and set(names) == {'host-sandbox.c', 'process-guard.c', 'host-sandbox', 'process-guard.dylib'},
            'complete guard manifest required')
    for name in ('host-sandbox.c', 'process-guard.c'):
        require(Path(names[name]).resolve() == root / 'tools/taverna/ios' / name, 'foreign guard source')
    return names


def record_build(root, attempt_name, guard_path, bindings_path, allow_dirty=False):
    attempt = session.new_attempt(root, attempt_name); deadline = time.monotonic() + 5400
    record = dict(stage='build-for-testing', command=sys.argv, timeout_seconds=5400,
                  started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), exit_code=2)
    try:
        owned = read_json(root, root / '.build/ios-session.json'); session.validate_sdk_indexes(owned)
        session.validate_session(root, owned, owned['udid']); guard_components(root, guard_path)
        manifest_path = root / '.specs/features/ios-first-build/native-inputs.json'
        manifest = read_json(root, manifest_path); native.validate_manifest(root, manifest)
        bindings = read_json(root, bindings_path)
        require(bindings['native_manifest_sha256'] == sha256(manifest_path), 'native binding mismatch')
        for library in manifest['libraries']:
            path = session.inside(root, bindings['libraries'][library['name']]); native.validate_library(path, library)
            require(path == root / 'apps/ios/Libraries/sim' / library['name'], 'build library binding path mismatch')
        record.update(commit=command(root, ['git', 'rev-parse', 'HEAD']).stdout.strip(),
                      source_state=command(root, ['git', 'status', '--porcelain']).stdout,
                      native_manifest_sha256=sha256(manifest_path), session=owned,
                      recording_tool_sha256=sha256(Path(__file__)))
        validate_clean_source(record, not allow_dirty)
        patch = command(root, ['git', 'diff', '--binary']).stdout.encode()
        (attempt / 'source-diff.patch').write_bytes(patch); record['source_diff_sha256'] = hashlib.sha256(patch).hexdigest()
        record['test_source_sha256'] = {str(p.relative_to(root)): sha256(p) for p in (root / 'apps/ios/Tests iOS').glob('*.swift')}
        identity = ['CODE_SIGNING_ALLOWED=YES', 'CODE_SIGN_IDENTITY=-', 'CODE_SIGN_STYLE=Manual',
                    'DEVELOPMENT_TEAM=', 'PROVISIONING_PROFILE_SPECIFIER=', 'ARCHS=arm64', 'ONLY_ACTIVE_ARCH=YES']
        paths = [f'SYMROOT={root}/.build/DerivedData/Build/Products',
                 f'OBJROOT={root}/.build/DerivedData/Build/Intermediates.noindex'] + session.build_cache_args(root)
        args = ['xcodebuild', '-showBuildSettings', '-json', '-alltargets', '-project',
                'apps/ios/SimpleX.xcodeproj', '-configuration', 'Debug', '-sdk', 'iphonesimulator']
        settings = record_stage(root, attempt, 'settings', args + package_args(root) + identity + paths, 300)
        validate_stage('settings', settings)
        text = (attempt / 'settings.stdout.log').read_text(); (attempt / 'settings.stdout.json').write_text(text)
        targets = json.loads(text)
        require({'SimpleX (iOS)', 'SimpleXChat', 'SimpleX NSE', 'SimpleX SE', 'Tests iOS'} <= {t['target'] for t in targets}, 'missing target')
        for target in targets:
            bs = target['buildSettings']; session.validate_build_paths(root, bs)
            require(bs.get('PLATFORM_NAME') == 'iphonesimulator' and bs.get('CODE_SIGN_IDENTITY') == '-'
                    and not bs.get('DEVELOPMENT_TEAM') and not bs.get('PROVISIONING_PROFILE_SPECIFIER'), 'target signing mismatch')
            if target['target'] == 'SimpleX (iOS)':
                require(bs.get('EXECUTABLE_NAME') == 'SimpleX', 'guard executable selector mismatch')
        args = ['xcodebuild', 'build-for-testing', '-project', 'apps/ios/SimpleX.xcodeproj', '-scheme', 'SimpleX (iOS)',
                '-configuration', 'Debug', '-sdk', 'iphonesimulator', '-destination', 'platform=iOS Simulator,id=' + owned['udid'],
                '-destination-timeout', '30', '-derivedDataPath', str(root / '.build/DerivedData'), '-jobs', '5']
        args += package_args(root) + ['-resultBundlePath', str(attempt / 'build.xcresult')] + identity + paths
        record['command'] = args; output_json(attempt / 'active.json', record)
        built = record_stage(root, attempt, 'build', args, native.remaining(deadline, 5400)); validate_stage('build', built)
        products = inspect_products(root, root / '.build/DerivedData/Build/Products/Debug-iphonesimulator', attempt)
        require(code_diff(root, record['commit']) == b''.join(p for p in re.split(b'(?=^diff --git )', patch, flags=re.M)
                if p.startswith(b'diff --git ') and b'apps/ios/' in p.splitlines()[0]), 'source changed during build')
        record.update(exit_code=0, products=products, account_provisioning='NOT USED',
                      xcode=command(root, ['xcodebuild', '-version']).stdout.strip(),
                      sdk=command(root, ['xcrun', '--sdk', 'iphonesimulator', '--show-sdk-version']).stdout.strip())
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        record['error'] = str(error)
    record['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    output_json(attempt / 'receipt.json', record); return record


def record_tests(root, build_path, attempt_name, guard_path, profile='first-build'):
    attempt = session.new_attempt(root, attempt_name); deadline = time.monotonic() + 3600
    record = dict(stage='ui-test-session', command=sys.argv, timeout_seconds=3600,
                  started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), exit_code=2, steps=[])
    booted = False
    def step(name, args, seconds=120, required=True, cleanup=False):
        result = record_stage(root, attempt, name, args, seconds if cleanup else native.remaining(deadline, seconds))
        record['steps'].append(dict(name=name, command=args, exit_code=result['exit_code']))
        if required:
            validate_stage(name, result)
        return result, (attempt / (name + '.stdout.log')).read_text()
    try:
        require(profile in ('first-build', 'full-matrix'), 'unknown UI profile')
        record['ui_profile'] = profile
        build_path = session.inside(root, build_path); built = read_json(root, build_path / 'receipt.json'); validate_stage('build', built)
        require(len(built.get('products', [])) == 4, 'missing recorded build products')
        for product in built['products']:
            artifact(root, product)
        owned = read_json(root, root / '.build/ios-session.json'); session.validate_sdk_indexes(owned)
        session.validate_session(root, owned, owned['udid']); names = guard_components(root, guard_path)
        patch = code_diff(root, built['commit'])
        parts = re.split(b'(?=^diff --git )', (build_path / 'source-diff.patch').read_bytes(), flags=re.M)
        require(patch == b''.join(p for p in parts if p.startswith(b'diff --git ') and b'apps/ios/' in p.splitlines()[0]), 'source changed after build')
        for name, expected in built['test_source_sha256'].items():
            artifact(root, dict(path=str(root / name), sha256=expected))
        record.update(session=owned, commit=built['commit'], source_code_diff_sha256=hashlib.sha256(patch).hexdigest(),
                      build_receipt_sha256=sha256(build_path / 'receipt.json'), native_manifest_sha256=built['native_manifest_sha256'],
                      guard_manifest_sha256=sha256(guard_path), recording_tool_sha256=sha256(Path(__file__)))
        products = root / '.build/DerivedData/Build/Products'
        matches = list(products.glob('SimpleX (iOS)_iphonesimulator*-arm64.xctestrun'))
        require(len(matches) == 1, 'missing or ambiguous SDK xctestrun')
        original = matches[0].read_bytes(); plan = plistlib.loads(original)
        require(plan['__xctestrun_metadata__']['FormatVersion'] == 1 and set(plan) == {'Tests iOS', '__xctestrun_metadata__'}, 'unqualified xctestrun format')
        target = plan['Tests iOS']; require(not target.get('OnlyTestIdentifiers') and not target.get('SkipTestIdentifiers'), 'filtered SDK xctestrun')
        target.setdefault('EnvironmentVariables', {}).update(TAVERNA_UI_ROOT=str(root), TAVERNA_UI_ATTEMPT=str(attempt), TAVERNA_GUARD_MANIFEST=str(guard_path.resolve()), TAVERNA_UI_PROFILE=profile)
        app = target.setdefault('UITargetAppEnvironmentVariables', {})
        app['DYLD_INSERT_LIBRARIES'] = ':'.join(p for p in [app.get('DYLD_INSERT_LIBRARIES', ''), names['process-guard.dylib']] if p)
        (attempt / 'guard-events').mkdir()
        app.update(TAVERNA_HOST_GUARD=names['host-sandbox'], TAVERNA_GUARD_LOG=str(attempt / 'guard-events/framework-before-main.jsonl'))
        configured = products / ('Taverna-' + attempt_name + '.xctestrun')
        with configured.open('xb') as output:
            output.write(plistlib.dumps(plan))
        (attempt / 'original.xctestrun.plist').write_bytes(original)
        (attempt / 'configured.xctestrun.plist').write_bytes(configured.read_bytes())
        record['xctestrun_sha256'] = sha256(configured)
        _, text = step('devices-before', ['xcrun', 'simctl', 'list', 'devices', '--json']); before = json.loads(text)
        devices = [d for group in before['devices'].values() for d in group]
        require([d['state'] for d in devices if d['udid'] == owned['udid']] == ['Shutdown'], 'owned destination is busy')
        before_ids = {d['udid'] for d in devices}
        step('boot', ['xcrun', 'simctl', 'boot', owned['udid'], '--arch=arm64']); booted = True
        step('bootstatus', ['xcrun', 'simctl', 'bootstatus', owned['udid'], '-b'], seconds=180)
        if profile == 'first-build':
            step('appearance-set', ['xcrun', 'simctl', 'ui', owned['udid'], 'appearance', 'light'])
            _, appearance = step('appearance-read', ['xcrun', 'simctl', 'ui', owned['udid'], 'appearance'])
            require(appearance.strip() == 'light', 'first-build appearance mismatch')
            record.update(ui_language='en', ui_region='US', ui_orientation='portrait', ui_appearance=appearance.strip())
        absent, _ = step('existing-app-container', ['xcrun', 'simctl', 'get_app_container', owned['udid'], 'chat.simplex.app', 'data'], required=False)
        require(absent['exit_code'] == 2, 'fresh app data required; preserve old data and create another owned destination')
        args = ['xcodebuild', 'test-without-building', '-xctestrun', str(configured), '-destination', 'platform=iOS Simulator,id=' + owned['udid'],
                '-destination-timeout', '30', '-parallel-testing-enabled', 'NO', '-maximum-concurrent-test-simulator-destinations', '1',
                '-resultBundlePath', str(attempt / 'tests.xcresult'), '-testLanguage', 'en', '-testRegion', 'US']
        record['command'] = args; output_json(attempt / 'active.json', record)
        tested = record_stage(root, attempt, 'tests', args, native.remaining(deadline, 3600))
        record.update(test_exit_code=tested['exit_code'], test_timed_out=tested['timed_out'], exit_code=tested['exit_code'])
        _, text = step('devices-after', ['xcrun', 'simctl', 'list', 'devices', '--json'], cleanup=True)
        after_ids = {d['udid'] for group in json.loads(text)['devices'].values() for d in group}
        record['new_device_ids'] = sorted(after_ids - before_ids)
        require(not record['new_device_ids'], 'Xcode created an unqualified destination')
        session.validate_session(root, owned, owned['udid'])
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        record['error'] = str(error)
        if record['exit_code'] == 0 or 'test_exit_code' not in record:
            record['exit_code'] = 2
    finally:
        if booted:
            try:
                step('shutdown', ['xcrun', 'simctl', 'shutdown', owned['udid']], cleanup=True)
            except (ValueError, OSError, subprocess.SubprocessError) as error:
                record['shutdown_error'] = str(error)
                if record['exit_code'] == 0:
                    record['exit_code'] = 2
    record['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    output_json(attempt / 'receipt.json', record); return record


def compare_runs(first, second):
    for record in (first, second):
        require(record.get('exit_code') == 0 and record.get('local_build_ui') == 'PASS'
                and record.get('clean_source') is True, 'two clean successful proofs required')
    require(first.get('ui_profile') in ('first-build', 'full-matrix')
            and first['ui_profile'] == second.get('ui_profile'), 'UI profile mismatch across runs')
    require(re.fullmatch(r'[0-9a-f]{40}', first['source_commit'])
            and re.fullmatch(r'[0-9a-f]{64}', first['native_manifest_sha256']), 'missing source/input identity')
    require(first['source_commit'] == second['source_commit']
            and first['native_manifest_sha256'] == second['native_manifest_sha256'], 'source/input mismatch across runs')
    roots = [Path(r['worktree']).resolve(strict=True) for r in (first, second)]
    require(roots[0] != roots[1] and first.get('udid') and second.get('udid')
            and first['udid'] != second['udid'], 'distinct worktrees and simulators required')
    caches = [root / '.build/DerivedData' for root in roots]
    require(all(cache.resolve().is_relative_to(root) for root, cache in zip(roots, caches))
            and caches[0].resolve() != caches[1].resolve(), 'distinct owned caches required')
    return dict(source_commit=first['source_commit'], native_manifest_sha256=first['native_manifest_sha256'], ui_profile=first['ui_profile'],
                runs=[dict(worktree=str(root), udid=record['udid']) for root, record in zip(roots, (first, second))])


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'compare':
        parser = argparse.ArgumentParser(description='Compare two independently validated clean local proofs')
        parser.add_argument('--first', type=Path, required=True)
        parser.add_argument('--second', type=Path, required=True)
        parser.add_argument('--attempt', required=True)
        args = parser.parse_args(sys.argv[2:]); root = Path(__file__).resolve().parents[2]
        attempt = session.new_attempt(root, args.attempt)
        result = dict(stage='reproduction-comparison', exit_code=2, command=sys.argv)
        try:
            values = [json.loads(p.resolve(strict=True).read_text()) for p in (args.first, args.second)]
            for path, value in zip((args.first, args.second), values):
                require(path.resolve().is_relative_to(Path(value['worktree']).resolve()), 'proof is outside its recorded worktree')
            result.update(compare_runs(*values), exit_code=0)
        except (ValueError, OSError, KeyError, TypeError) as error:
            result['error'] = str(error)
        output_json(attempt / 'receipt.json', result); print(json.dumps(result, indent=2)); return result['exit_code']
    if len(sys.argv) > 1 and sys.argv[1] in ('build', 'test'):
        action = sys.argv[1]
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--attempt', required=True)
        parser.add_argument('--guard-manifest', type=Path, required=True)
        if action == 'build':
            parser.add_argument('--bindings', type=Path, default=Path('.build/native-input-bindings.json'))
            parser.add_argument('--allow-dirty', action='store_true')
        else:
            parser.add_argument('--build-attempt', type=Path, required=True)
            parser.add_argument('--ui-profile', choices=('first-build', 'full-matrix'), default='first-build')
        args = parser.parse_args(sys.argv[2:]); root = Path(__file__).resolve().parents[2]
        result = (record_build(root, args.attempt, args.guard_manifest, args.bindings, args.allow_dirty) if action == 'build' else
                  record_tests(root, args.build_attempt, args.attempt, args.guard_manifest, args.ui_profile))
        print(json.dumps(result, indent=2)); return result['exit_code']
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-attempt', type=Path, required=True)
    parser.add_argument('--test-attempt', type=Path, required=True)
    parser.add_argument('--native-attempt', type=Path, required=True)
    parser.add_argument('--bindings', type=Path, default=Path('.build/native-input-bindings.json'))
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--require-clean', action='store_true')
    args = parser.parse_args(); root = Path(__file__).resolve().parents[2]
    result = verify(root, args.build_attempt, args.test_attempt, args.native_attempt, args.bindings,
                    args.attempt, args.require_clean)
    print(json.dumps(result, indent=2)); return result['exit_code']


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError) as error:
        print(f'FAIL: {error}', file=sys.stderr); sys.exit(2)
