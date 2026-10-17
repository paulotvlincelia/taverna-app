"""Fixture-only adapter and control probes for the isolated protocol clients."""
import asyncio
import contextlib
import json
import os
from pathlib import Path
import socket
import ssl
import sys
import time

from gateway import pump


def context(directory):
    ctx = ssl.create_default_context(cafile=str(directory / 'ca.crt'))
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.load_cert_chain(directory / 'device.crt', directory / 'device.key')
    return ctx


async def bridge(directory, native=False):
    ctx = context(directory)
    servers = []
    for local, target in (((5223, 15223), (8443, 15443)) if native else ((15223, 15223), (18443, 15443))):
        async def accept(reader, writer, target=target):
            remote = None
            tasks = []
            try:
                upstream, remote = await asyncio.wait_for(asyncio.open_connection('gateway', target, ssl=ctx, server_hostname='gateway.test'), 3)
                tasks = [asyncio.create_task(pump(reader, remote)), asyncio.create_task(pump(upstream, writer))]
                await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            except (OSError, asyncio.TimeoutError, ssl.SSLError):
                pass
            finally:
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                for stream in (writer, remote):
                    if stream is not None:
                        stream.close()
                        with contextlib.suppress(OSError, ssl.SSLError):
                            await stream.wait_closed()
        servers.append(await asyncio.start_server(accept, '127.0.0.1', local))
    print('READY: fixture client adapter', flush=True)
    await asyncio.gather(*(server.serve_forever() for server in servers))


def client_hello():
    inner = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    inner.check_hostname = False
    inner.verify_mode = ssl.CERT_NONE  # Reachability probe only; native clients still validate relay fingerprints.
    incoming, outgoing = ssl.MemoryBIO(), ssl.MemoryBIO()
    handshake = inner.wrap_bio(incoming, outgoing, server_side=False, server_hostname='relay.test')
    try:
        handshake.do_handshake()
    except ssl.SSLWantReadError:
        pass
    return outgoing.read()


def probe(directory, port, no_certificate=False):
    ctx = ssl.create_default_context(cafile=str(directory / 'ca.crt')) if no_certificate else context(directory)
    try:
        with socket.create_connection(('gateway', port), timeout=3) as tcp:
            with ctx.wrap_socket(tcp, server_hostname='gateway.test') as stream:
                stream.sendall(client_hello())
                return {'allowed_bytes': bool(stream.recv(4096))}
    except (OSError, ssl.SSLError):
        return {'allowed_bytes': False}


def hold(directory, port):
    with socket.create_connection(('gateway', port), timeout=3) as tcp:
        with context(directory).wrap_socket(tcp, server_hostname='gateway.test') as stream:
            stream.sendall(client_hello())
            if not stream.recv(4096):
                raise RuntimeError('backend not reached before the control change')
            print('OPEN', flush=True)
            started = time.monotonic()
            stream.settimeout(65)
            while stream.recv(4096):
                pass
            print(json.dumps({'closed': True, 'seconds': time.monotonic() - started}), flush=True)


def sentinel(directory):
    (directory/'sentinel-count').write_text('0')
    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server.bind(('0.0.0.0',19000))
        server.listen()
        (directory/'sentinel-pid').write_text(str(os.getpid()))
        count=0
        while True:
            conn,_=server.accept()
            with conn:
                count+=1
                (directory/'sentinel-count').write_text(str(count))
                conn.sendall(b'SENTINEL')


def redirect(directory):
    with socket.create_connection(('gateway',15223),timeout=2) as tcp:
        with context(directory).wrap_socket(tcp,server_hostname='gateway.test') as stream:
            stream.settimeout(1)
            stream.sendall(b'CONNECT unknown:19000 HTTP/1.1\r\nHost: unknown:19000\r\n\r\n')
            try:
                stream.recv(64)
            except (OSError,ssl.SSLError):
                pass


async def api(port, command):
    import websockets
    async with websockets.connect('ws://127.0.0.1:' + str(port)) as ws:
        await ws.send(json.dumps({'corrId':'proof','cmd':command}))
        while True:
            value = json.loads(await asyncio.wait_for(ws.recv(), 15))
            if value.get('corrId') == 'proof':
                print(json.dumps(value['resp']))
                return



async def session():
    """One fixture peer socket; preserve asynchronous transfer events."""
    import websockets
    async with websockets.connect('ws://127.0.0.1:5225') as ws:
        async def commands():
            while line := await asyncio.to_thread(sys.stdin.readline):
                await ws.send(line.strip())
        async def responses():
            async for value in ws:
                print(value, flush=True)
        tasks = [asyncio.create_task(commands()), asyncio.create_task(responses())]
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in tasks: task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'bridge': asyncio.run(bridge(Path('/client'), '--native' in sys.argv))
    elif mode == 'probe': print(json.dumps(probe(Path('/client'), int(sys.argv[2]), '--no-cert' in sys.argv)))
    elif mode == 'hold': hold(Path('/client'), int(sys.argv[2]))
    elif mode == 'sentinel': sentinel(Path('/client'))
    elif mode == 'redirect': redirect(Path('/client'))
    elif mode == 'session': asyncio.run(session())
    elif mode == 'api': asyncio.run(api(int(sys.argv[2]),sys.argv[3]))
