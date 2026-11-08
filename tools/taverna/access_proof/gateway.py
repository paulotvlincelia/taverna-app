"""Experimental TLS boundary; not a deployed Taverna service or enrollment API."""
from __future__ import annotations

import asyncio
import contextlib
import hashlib
import itertools
import json
from pathlib import Path
import ssl
import sys

# Administrative constants. No client-supplied destination or CONNECT API.
ROUTES = ((15223, 'relay', 5223), (15443, 'relay', 8443))
POLL_SECONDS = 0.2
AUDIT_IDS = itertools.count(1)


def permitted(policy: Path, certificate: bytes) -> bool:
    try:
        value = json.loads(policy.read_text())
        active = value['active']
        if type(value.get('schema')) is not int or value['schema'] != 1 or not isinstance(active, list):
            return False
        if not all(isinstance(x, str) and len(x) == 64 and all(c in '0123456789abcdef' for c in x) for x in active):
            return False
        return hashlib.sha256(certificate).hexdigest() in active
    except (OSError, ValueError, KeyError, TypeError):
        return False


async def pump(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while block := await reader.read(65536):
        writer.write(block)
        await writer.drain()


async def connect(reader, writer, *, policy, backend, audit=False, transfer_delay=0):
    connection_id=next(AUDIT_IDS) if audit else None
    def record(event):
        if audit:
            # Fixture diagnostics: no peer, certificate, key, payload or address.
            print(json.dumps({'event':event,'connection':connection_id,'protocol':'smp' if backend[1]==5223 else 'xftp'}),flush=True)
    certificate = writer.get_extra_info('peercert', default=None)
    tls = writer.get_extra_info('ssl_object')
    der = tls.getpeercert(binary_form=True) if tls and certificate else b''
    remote = None
    tasks = []
    try:
        if not der or not permitted(policy, der):
            record('denied_before_backend')
            return
        record('authorized_before_backend')
        upstream, remote = await asyncio.wait_for(asyncio.open_connection(*backend), 3)
        # Recheck after opening the backend: revocation can race the connect.
        if not permitted(policy, der):
            record('denied_after_backend')
            return
        record('authorized_after_backend')

        async def watch():
            while permitted(policy, der):
                await asyncio.sleep(POLL_SECONDS)
            record('association_no_longer_active')

        async def upload():
            while block := await reader.read(16384 if transfer_delay else 65536):
                if transfer_delay and backend[1] == 8443:
                    await asyncio.sleep(transfer_delay)
                remote.write(block)
                await remote.drain()

        tasks = [asyncio.create_task(upload()), asyncio.create_task(pump(upstream, writer)), asyncio.create_task(watch())]
        done,_ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task,event in zip(tasks,('client_stream_ended','backend_stream_ended','authorization_ended')):
            if task in done:record(event)
    except (OSError, asyncio.TimeoutError, ssl.SSLError):
        record('transport_error')
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        for stream in (writer, remote):
            if stream is not None:
                stream.close()
                with contextlib.suppress(OSError, ssl.SSLError, asyncio.CancelledError):
                    await stream.wait_closed()
        record('streams_closed')


async def main(directory, audit=False, transfer_delay=0):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(directory / 'server.crt', directory / 'server.key')
    context.load_verify_locations(directory / 'ca.crt')
    servers = []
    for port, host, target in ROUTES:
        async def accept(reader, writer, target=target, host=host):
            await connect(reader, writer, policy=directory / 'policy.json', backend=(host, target), audit=audit, transfer_delay=transfer_delay)
        servers.append(await asyncio.start_server(accept, '0.0.0.0', port, ssl=context, ssl_handshake_timeout=3))
    print('READY: experimental boundary; two fixed backends; no enrollment', flush=True)
    await asyncio.gather(*(server.serve_forever() for server in servers))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    parser.add_argument('--audit', action='store_true')
    parser.add_argument('--transfer-delay', type=float, default=0)
    args = parser.parse_args()
    if not 0 <= args.transfer_delay <= .1: parser.error('fixture delay outside bound')
    asyncio.run(main(args.directory, audit=args.audit, transfer_delay=args.transfer_delay))
