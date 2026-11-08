"""Exercise the compiled iOS core under the owned Simulator network guard."""
import argparse
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/taverna'))
import ios_session

ROUTE = 'smp://1GV7X3rvpMH7P_KYzs70GNR1XSO0eWbzQi3sIUQ3R5A=@relay.test:5223'
FIXTURE_SOCKS = 'fixture:fixture@127.0.0.1:38071'


def response(packet, tag):
    result = packet.get('result', {})
    assert set(result) - {'_owsf'} == {tag}, (tag, packet.keys(), result.keys())
    return result[tag]


def profile(core, name='Device-D1'):
    data = core.command('/u')
    if 'error' in data:
        assert 'noActiveUser' in json.dumps(data)
        body = dict(profile=dict(displayName=name, fullName=''), pastTimestamp=False,
                    userChatRelay=False, clientService=False)
        data = core.command('/_create user ' + json.dumps(body))
    user = response(data, 'activeUser')['user']
    assert user['profile']['displayName'] == name
    return user['userId']


def set_network(core, proxy):
    network = response(core.command('/network'), 'networkConfig')['networkConfig']
    expected = dict(socksProxy=proxy, socksMode='always', smpProxyMode='never',
                    smpProxyFallback='prohibit', smpWebPortServers='off')
    network.update(expected)
    network['tcpConnectTimeout'] = dict(backgroundTimeout=4000000, interactiveTimeout=4000000)
    response(core.command('/_network ' + json.dumps(network)), 'cmdOk')
    readback = response(core.command('/network'), 'networkConfig')['networkConfig']
    assert {key: readback[key] for key in expected} == expected


def build(directory, archives):
    ios = ROOT / 'apps/ios/SimpleXChat'
    test = ROOT / 'tools/taverna/native_access_tests'
    sdk = subprocess.check_output(['xcrun', '--sdk', 'iphonesimulator', '--show-sdk-path'], text=True).strip()
    exe = directory / 'device-test-core'
    command = ['xcrun', '--sdk', 'iphonesimulator', 'clang', '-target', 'arm64-apple-ios15.0-simulator',
               '-isysroot', sdk, '-Wall', '-Wextra', '-DTAVERNA_GUARD_EXECUTABLE="device-test-core"',
               str(test / 'DeviceTestCore.c'), str(ios / 'hs_init.c'),
               str(ROOT / 'tools/taverna/ios/process-guard.c')]
    command += [str(path) for path in sorted(archives.glob('*.a'))]
    command += ['-framework', 'Security', '-framework', 'CoreFoundation',
                '-liconv', '-lcharset', '-lc++', '-lz', '-o', str(exe)]
    subprocess.run(command, check=True, timeout=180)
    return exe


class Core:
    def __init__(self, exe, run, database, mode='technical'):
        self.exe, self.run, self.database, self.mode = exe, run, database, mode
        self.process = None
        self.buffer = bytearray()
        self.fds = []

    def __enter__(self):
        self.run.mkdir()
        config = json.loads((ROOT / '.build/ios-session.json').read_text())
        ios_session.validate_session(ROOT, config, config['udid'])
        ios_session.validate_sdk_indexes(config)
        incoming, outgoing = self.run / 'commands', self.run / 'responses'
        self.guard_log = self.run / 'guard.jsonl'
        helper = self.exe.parent / 'host-sandbox'
        env = dict(os.environ, SIMCTL_CHILD_TAVERNA_HOST_GUARD=str(helper),
                   SIMCTL_CHILD_TAVERNA_GUARD_LOG=str(self.guard_log))
        try:
            for path in (incoming, outgoing):
                os.mkfifo(path, 0o600)
                self.fds.append(os.open(path, os.O_RDWR | os.O_NONBLOCK))
            with (self.run / 'process.log').open('wb') as log:
                self.process = subprocess.Popen(
                    ['xcrun', 'simctl', 'spawn', config['udid'], str(self.exe),
                     str(self.database), self.mode, str(incoming), str(outgoing)],
                    env=env, stdout=log, stderr=log)
            assert 'ok' in self.read()
            [guard] = [json.loads(line) for line in self.guard_log.read_text().splitlines()]
            assert guard['ipv4_errno'] in (1, 13) and guard['ipv6_errno'] in (1, 13)
            assert guard['loopback'] is True and guard['mechanism'] == 'kernel_sandbox'
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    def read(self):
        deadline = time.monotonic() + 25
        while b'\n' not in self.buffer:
            assert self.process.poll() is None, 'simulator core exited before returning a response'
            timeout = deadline - time.monotonic()
            assert timeout > 0, 'simulator core response timed out'
            if select.select([self.fds[1]], [], [], min(timeout, .25))[0]:
                self.buffer.extend(os.read(self.fds[1], 65536))
        line, _, rest = self.buffer.partition(b'\n')
        self.buffer = bytearray(rest)
        return json.loads(line)

    def command(self, text):
        data = text.encode() + b'\n'
        assert b'\n' not in data[:-1] and len(data) < 4096
        assert os.write(self.fds[0], data) == len(data)
        return self.read()

    def __exit__(self, error_type, error, traceback):
        try:
            if self.process and self.process.poll() is None:
                os.write(self.fds[0], b'\n')
                try:
                    self.process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        self.process.wait()
                    if error_type is None:
                        raise
            if self.process is not None and error_type is None:
                assert self.process.returncode == 0, 'simulator core failed to close'
        finally:
            for fd in self.fds:
                os.close(fd)


@contextmanager
def fixture_and_listener(directory):
    assert 'TAVERNA_PROOF_RUN' not in os.environ
    os.environ['TAVERNA_PROOF_RUN'] = 'smp-sim-' + uuid.uuid4().hex[:8]
    try:
        spec = importlib.util.spec_from_file_location(
            'device_test_smp_fixture', ROOT / 'tools/taverna/access_proof/fixture.py')
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
    finally:
        del os.environ['TAVERNA_PROOF_RUN']
    fixture.IMAGE = fixture.docker('image', 'inspect', '--format', '{{.Id}}', fixture.IMAGE).stdout.strip()
    assert fixture.IMAGE.startswith('sha256:')
    fixture.initialize()
    try:
        fixture.start(native=True)
        port = fixture.docker('port', fixture.PREFIX + '-gateway', '15223/tcp').stdout.strip()
        host, port = port.rsplit(':', 1)
        assert host == '127.0.0.1'
        source = ROOT / 'apps/ios/SimpleXChat/Taverna'
        driver = directory / 'relay-driver'
        subprocess.run(['xcrun', 'swiftc', '-swift-version', '5', '-warnings-as-errors',
                        str(source / 'SocksCodec.swift'), str(source / 'RelayTransport.swift'),
                        str(ROOT / 'tools/taverna/native_access_tests/RelayDriver.swift'),
                        '-o', str(driver)], check=True, timeout=120)
        driver_config = directory / 'listener.json'
        driver_config.write_text(json.dumps(dict(identity=str(fixture.RUN / 'alice/device.p12'),
                                                anchor=str(fixture.RUN / 'gateway/ca.der'),
                                                host=host, serverName='gateway.test', smpPort=int(port),
                                                xftpPort=0, destinations=[5223], singleSMP=True)))
        relay_hash = (fixture.RUN / 'smp-config/fingerprint').read_text().strip()
        route = f'smp://{relay_hash}@relay.test:5223'
        with subprocess.Popen([str(driver), str(driver_config)], text=True, stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as relay:
            try:
                assert select.select([relay.stdout], [], [], 10)[0], 'listener did not bind'
                proxy = json.loads(relay.stdout.readline())['proxy']
                yield fixture, proxy, route
            finally:
                if relay.poll() is None:
                    try:
                        relay.communicate('quit\n', timeout=8)
                    except subprocess.TimeoutExpired:
                        relay.kill()
                        relay.communicate()
    finally:
        fixture.stop()
        for name in fixture.NAMES:
            assert fixture.docker('container', 'inspect', name, check=False).returncode != 0
        for kind in ('inner', 'outer', 'native-host'):
            name = fixture.PREFIX + '-' + kind
            assert fixture.docker('network', 'inspect', name, check=False).returncode != 0


def check_authorization(exe, directory, fixture, proxy, route):
    with Core(exe, directory / 'authorized', directory / 'authorized-db') as core:
        uid = profile(core)
        read = f'/_device_test_smp {uid}'
        start = '/_start main=on snd_files=off'
        set_network(core, proxy)
        assert response(core.command(read + ' ' + route), 'deviceTestSMP')['smpServers'] == [route]
        assert response(core.command(read), 'deviceTestSMP')['smpServers'] == [route]
        def authorize(*roles):
            fingerprints = [fixture.fingerprint(role) for role in roles]
            fixture.atomic_policy(fingerprints)
            data = fixture.execute('gateway', 'cat', '/gateway/policy.json').stdout
            assert json.loads(data) == dict(schema=1, active=fingerprints)
        authorize('bob')
        denied = core.command(read)
        assert denied['error']['error']['errorType']['commandError']['message'] == 'device test SMP authorization failed'
        response(core.command('/_check running'), 'chatStopped')
        authorize('alice', 'bob')
        assert response(core.command(read), 'deviceTestSMP')['smpServers'] == [route]
        response(core.command(start), 'chatStarted')
        assert 'error' in core.command(read)
        workers = response(core.command('/get workers details'), 'agentWorkersDetails')['agentWorkersDetails']
        assert all(workers[key] == {} for key in ('xftpRcvWorkers', 'xftpSndWorkers', 'xftpDelWorkers'))
        response(core.command('/_stop'), 'chatStopped')


def check_core(exe, directory):
    with Core(exe, directory / 'ordinary', directory / 'ordinary-db', 'ordinary') as core:
        uid = profile(core)
        assert 'chatNotStarted' in json.dumps(core.command(f'/_servers {uid}'))
        assert 'error' in core.command(f'/_device_test_smp {uid} {ROUTE}')
        response(core.command('/_start main=off snd_files=off'), 'chatStarted')
        response(core.command(f'/_servers {uid}'), 'userServers')
        response(core.command('/_stop'), 'chatStopped')

    with Core(exe, directory / 'technical', directory / 'technical-db') as core:
        assert 'error' in core.command(f'/_device_test_smp 1 {ROUTE}')
        uid = profile(core)
        read = f'/_device_test_smp {uid}'
        start = '/_start main=on snd_files=off'
        assert response(core.command(read), 'deviceTestSMP')['smpServers'] == []
        assert 'error' in core.command(start)
        assert 'error' in core.command(f'/_device_test_smp {uid + 1} {ROUTE}')
        assert 'error' in core.command(f"{read} {ROUTE.replace('relay.test', 'public.test')}")
        assert 'error' in core.command(f"{read} {ROUTE.replace('smp://', 'xftp://')}")
        assert response(core.command(read + ' ' + ROUTE), 'deviceTestSMP')['smpServers'] == [ROUTE]
        assert 'error' in core.command(read)
        response(core.command('/_check running'), 'chatStopped')
        assert 'error' in core.command(start)
        set_network(core, FIXTURE_SOCKS)
        assert 'error' in core.command('/_start main=off snd_files=off')
        assert 'error' in core.command('/_start')

    with Core(exe, directory / 'wrong-profile', directory / 'wrong-db') as core:
        uid = profile(core, 'Other')
        assert 'error' in core.command(f'/_device_test_smp {uid} {ROUTE}')

    with fixture_and_listener(directory) as (fixture, proxy, route):
        check_authorization(exe, directory, fixture, proxy, route)

    print('Simulator SMP core startup checks PASS')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('attempt', type=Path)
    parser.add_argument('archives', type=Path)
    args = parser.parse_args()
    attempt = args.attempt.resolve()
    assert attempt.is_relative_to(ROOT / '.build')
    attempt.mkdir()
    helper = attempt / 'host-sandbox'
    subprocess.run(['xcrun', '--sdk', 'macosx', 'clang',
                    str(ROOT / 'tools/taverna/ios/host-sandbox.c'), '-o', str(helper)], check=True)
    check_core(build(attempt, args.archives.resolve()), attempt)


if __name__ == '__main__':
    main()
