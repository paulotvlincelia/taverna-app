"""Exercise real SMP and persisted chat history with the isolated Simulator core."""
from pathlib import Path
import json
import sys
import time

from device_test_core import Core, ROOT, fixture_and_listener, profile, response, set_network

DEVICE = tuple(f'Device-D1-{index:02}' for index in range(1, 11))
PEER = tuple(f'Peer-{index:02}' for index in range(1, 11))


def peer_api(fixture, cmd, tag):
    result = json.loads(fixture.execute('bob', 'python3', '/source/client.py', 'api', '5225', cmd).stdout)
    assert result.get('type') == tag, (tag, result.get('type'))
    return result


def wait_for(probe, accept, label):
    expires = time.monotonic() + 25
    while True:
        result = probe()
        if accept(result):
            return result
        assert time.monotonic() < expires, label
        time.sleep(.2)


def ready_id(contacts):
    assert len(contacts) <= 1
    for contact in contacts:
        status = contact['activeConn']['connStatus']
        if status == {'type': 'ready'} or status == {'_owsf': True, 'ready': {}}:
            return contact['contactId']
    return None


def connect(core, proxy, route):
    uid = profile(core)
    cmd = f'/_device_test_smp {uid}'
    set_network(core, proxy)
    assert response(core.command(cmd + ' ' + route), 'deviceTestSMP')['smpServers'] == [route]
    assert response(core.command(cmd), 'deviceTestSMP')['smpServers'] == [route]
    response(core.command('/_start main=on snd_files=off'), 'chatStarted')
    return uid


def history(packet, swift):
    rows = []
    for item in packet['chat']['chatItems']:
        item = item.get('chatItem', item)
        content = item['content']
        if swift:
            for direction in ('sndMsgContent', 'rcvMsgContent'):
                if direction in content:
                    message = content[direction]['msgContent']
                    break
            else:
                continue
        else:
            direction = content['type']
            if direction not in ('sndMsgContent', 'rcvMsgContent'):
                continue
            message = content['msgContent']
        if message['type'] == 'text':
            rows.append((item['meta']['itemId'], direction == 'sndMsgContent', message['text']))
    return sorted(rows)


def require_texts(rows, sent, received):
    assert len(rows) == len({row[0] for row in rows}) == 20
    assert tuple(text for _, outgoing, text in rows if outgoing) == sent
    assert tuple(text for _, outgoing, text in rows if not outgoing) == received


def measure(exe, attempt):
    with fixture_and_listener(attempt) as (fixture, proxy, route):
        fixture.clients(native=True, people=('bob',))
        db = attempt / 'device-db'
        with Core(exe, attempt / 'first-process', db) as core:
            user_id = connect(core, proxy, route)
            invite = response(core.command(f'/_connect {user_id}'), 'invitation')
            peer_api(fixture, '/connect ' + invite['connLinkInvitation']['connFullLink'], 'sentConfirmation')
            contact = wait_for(lambda: ready_id(response(core.command('/contacts'), 'contactsList')['contacts']),
                               lambda value: value is not None, 'Device-D1 contact never became ready')
            peer_contact = wait_for(lambda: ready_id(peer_api(fixture, '/contacts', 'contactsList')['contacts']),
                                    lambda value: value is not None, 'peer contact never became ready')
            for text in DEVICE:
                msg = [{'msgContent': {'type': 'text', 'text': text}, 'mentions': {}}]
                command = f'/_send @{contact} live=off ttl=default sign=off json ' + json.dumps(msg)
                response(core.command(command), 'newChatItems')
            for text in PEER:
                peer_api(fixture, '@Device-D1 ' + text, 'newChatItems')

            def device_rows(current):
                return history(response(current.command(f'/_get chat @{contact} count=100'), 'apiChat'), swift=True)

            def peer_rows():
                return history(peer_api(fixture, f'/_get chat @{peer_contact} count=100', 'apiChat'), swift=False)

            before = wait_for(lambda: device_rows(core), lambda rows: len(rows) >= 20, 'Device-D1 delivery incomplete')
            peer_before = wait_for(peer_rows, lambda rows: len(rows) >= 20, 'peer delivery incomplete')
            require_texts(before, DEVICE, PEER)
            require_texts(peer_before, PEER, DEVICE)
            response(core.command('/_stop'), 'chatStopped')
        assert all(Path(str(db) + suffix).is_file() for suffix in ('_chat.db', '_agent.db'))
        fixture.docker('restart', '--time', '3', fixture.PREFIX + '-bob')
        fixture.execute('bob', 'sh', '-c', 'python3 /source/client.py bridge --native > /client/bridge.log 2>&1 &')
        fixture.clients(native=True, people=('bob',))
        with Core(exe, attempt / 'second-process', db) as reopened:
            assert connect(reopened, proxy, route) == user_id
            after = device_rows(reopened)
            peer_after = peer_rows()
            assert after == before and peer_after == peer_before
            require_texts(after, DEVICE, PEER)
            require_texts(peer_after, PEER, DEVICE)
            response(reopened.command('/_stop'), 'chatStopped')

        guards = [json.loads((attempt / name / 'guard.jsonl').read_text())
                  for name in ('first-process', 'second-process')]
        assert guards[0]['pid'] != guards[1]['pid']
        gateway_log = fixture.docker('logs', fixture.PREFIX + '-gateway').stdout
        audits = [json.loads(line) for line in gateway_log.splitlines() if line.startswith('{')]
        assert audits and {row['protocol'] for row in audits} == {'smp'}
        assert any(row['event'] == 'authorized_after_backend' for row in audits)

    print(json.dumps(dict(status='SIMULATOR_DELIVERY_PASS', sent_each_way=10, history_each=20,
                          duplicates=0, device_reopened=True, peer_reopened=True, gateway_protocols=['smp'])))


if __name__ == '__main__':
    path = Path(sys.argv[1]).resolve()
    attempt = Path(sys.argv[2]).resolve()
    assert attempt.is_relative_to(ROOT / '.build')
    attempt.mkdir()
    measure(path, attempt)
