"""Disposable local fixture; only explicitly named containers/networks are touched."""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
import ssl
import subprocess
import sys
import time

DOCKER = '/Applications/Docker.app/Contents/Resources/bin/docker'
ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / '.build/access-qualification'
SLUG = os.environ.get('TAVERNA_PROOF_RUN','a')
if not re.fullmatch(r'[a-z0-9-]{1,20}',SLUG):raise ValueError('invalid fixture run name')
RUN = WORK / ('run-'+SLUG)
SOURCE = Path(__file__).resolve().parent
IMAGE = 'taverna-access-proof:20261016'
PREFIX = 'taverna-access-proof-'+SLUG
NAMES = [PREFIX + '-' + x for x in ('relay','gateway','alice','bob','unknown')]


def docker(*args, check=True):
    return subprocess.run([DOCKER,*map(str,args)],text=True,capture_output=True,check=check)


def execute(who,*args,check=True):
    return docker('exec',PREFIX+'-'+who,*args,check=check)


def atomic_policy(active):
    path = RUN / 'gateway/policy.json'
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps({'schema':1,'active':active}))
    temporary.replace(path)


def fingerprint(who):
    cert = (RUN / who / 'device.crt').read_text()
    return hashlib.sha256(ssl.PEM_cert_to_DER_cert(cert)).hexdigest()


def make_credentials(native=False):
    directory = RUN / 'gateway'
    directory.mkdir(exist_ok=True)
    for who in ('alice','bob','unknown'):
        (RUN / who).mkdir(exist_ok=True)
    commands = ['set -e','umask 077',
        'openssl req -x509 -newkey ed25519 -nodes -keyout /work/run-a/gateway/ca.key -out /work/run-a/gateway/ca.crt -days 2 -subj /CN=Taverna-Fixture-CA']
    for who in ('gateway','alice','bob','unknown'):
        base='/work/run-a/'+who
        name='server' if who=='gateway' else 'device'
        cn='gateway.test' if who=='gateway' else 'Fixture-'+who
        ext='subjectAltName=DNS:gateway.test\nextendedKeyUsage=serverAuth' if who=='gateway' else 'extendedKeyUsage=clientAuth'
        (RUN/who/(name+'.ext')).write_text(ext+'\n')
        commands += [f'openssl req -newkey ed25519 -nodes -keyout {base}/{name}.key -out {base}/{name}.csr -subj /CN={cn}',
                     f'openssl x509 -req -in {base}/{name}.csr -CA /work/run-a/gateway/ca.crt -CAkey /work/run-a/gateway/ca.key -CAcreateserial -out {base}/{name}.crt -days 2 -extfile {base}/{name}.ext']
    if native:
        commands = [command.replace('-newkey ed25519', '-newkey ec -pkeyopt ec_paramgen_curve:P-256') for command in commands]
        commands += ['openssl x509 -in /work/run-a/gateway/ca.crt -outform DER -out /work/run-a/gateway/ca.der']
        for who in ('alice','bob','unknown'):
            commands += [f'openssl pkcs12 -export -in /work/run-a/{who}/device.crt -inkey /work/run-a/{who}/device.key -certfile /work/run-a/gateway/ca.crt -out /work/run-a/{who}/device.p12 -passout pass:fixture-only']
    result=docker('run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',f'{os.getuid()}:{os.getgid()}',
                  '--mount',f'type=bind,src={WORK},dst=/work',IMAGE,'sh','-c','; '.join(c.replace('/work/run-a/','/work/'+RUN.name+'/') for c in commands))
    (RUN/'cert-generation.log').write_text(result.stdout+result.stderr)
    for who in ('alice','bob','unknown'):
        (RUN/who/'ca.crt').write_bytes((directory/'ca.crt').read_bytes())
        for subdir in ('files','tmp'):(RUN/who/subdir).mkdir(exist_ok=True)
    atomic_policy([fingerprint('alice'),fingerprint('bob')])


def base_run(name,network,mounts):
    args=['run','-d','--name',PREFIX+'-'+name,'--network',PREFIX+'-'+network,'--network-alias',name,
          '--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',f'{os.getuid()}:{os.getgid()}',
          '--memory','384m','--cpus','1']
    for src,dst,ro in mounts:
        args+=['--mount',f'type=bind,src={src},dst={dst}'+(',readonly' if ro else '')]
    return args


def initialize():
    if RUN.exists():raise RuntimeError('Run already exists; preserve it and choose another TAVERNA_PROOF_RUN')
    expected=json.loads((SOURCE/'inputs.json').read_text())
    for record in expected['assets']:
        path=WORK/'bin'/record['name']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:raise ValueError('unqualified binary '+record['name'])
    RUN.mkdir(parents=True)
    result=docker('run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user',f'{os.getuid()}:{os.getgid()}',
        '--mount',f'type=bind,src={WORK},dst=/work',
        '-e','SMP_SERVER_CFG_PATH=/work/'+RUN.name+'/smp-config','-e','SMP_SERVER_LOG_PATH=/work/'+RUN.name+'/smp-log',
        '-e','XFTP_SERVER_CFG_PATH=/work/'+RUN.name+'/xftp-config','-e','XFTP_SERVER_LOG_PATH=/work/'+RUN.name+'/xftp-log',
        IMAGE,'sh','-c','set -e; umask 077; mkdir -p /work/'+RUN.name+'/files; /work/bin/smp-server-ubuntu-24_04-aarch64 init -y --fqdn relay.test --no-password --disable-web; /work/bin/xftp-server-ubuntu-24_04-aarch64 init --fqdn relay.test --path /work/'+RUN.name+'/files --quota 100mb')
    (RUN/'init.log').write_text(result.stdout+result.stderr)
    print('Qualified binaries initialized in a new exclusive run.')


def start(native=False, transfer_delay=0):
    for name in NAMES:
        if docker('container','inspect',name,check=False).returncode==0: raise RuntimeError('Existing fixture: preserve and inspect '+name)
    for net in ('inner','outer'):
        docker('network','create','--internal',PREFIX+'-'+net)
    if native:
        # Docker does not publish ports on an internal-only network. This
        # dedicated host-facing bridge contains only the gateway, never relays.
        docker('network','create',PREFIX+'-native-host')
    make_credentials(native=native)
    smp=RUN/'smp-config/smp-server.ini'
    smp.write_text(smp.read_text().replace('port = 5223,443','port = 5223'))
    xftp=RUN/'xftp-config/file-server.ini'
    xftp.write_text(xftp.read_text().replace('port = 443','port = 8443'))
    args=base_run('relay','inner',[(WORK,'/work',False)])
    for key,value in {'SMP_SERVER_CFG_PATH':'/work/run-a/smp-config','SMP_SERVER_LOG_PATH':'/work/run-a/smp-log','XFTP_SERVER_CFG_PATH':'/work/run-a/xftp-config','XFTP_SERVER_LOG_PATH':'/work/run-a/xftp-log'}.items():args+=['-e',key+'='+value.replace('/work/run-a/','/work/'+RUN.name+'/')]
    docker(*args,IMAGE,'sh','-c',f'/work/bin/smp-server-ubuntu-24_04-aarch64 start > /work/{RUN.name}/smp.log 2>&1 & /work/bin/xftp-server-ubuntu-24_04-aarch64 start > /work/{RUN.name}/xftp.log 2>&1 & wait')
    gateway_args=base_run('gateway','native-host' if native else 'inner',[(RUN/'gateway','/gateway',True),(SOURCE,'/source',True)])
    if native:
        gateway_args += ['-p','127.0.0.1::15223','-p','127.0.0.1::15443']
    docker(*gateway_args,IMAGE,'python3','/source/gateway.py','/gateway',*(['--audit', '--transfer-delay', str(transfer_delay)] if native else []))
    if native:
        docker('network','connect',PREFIX+'-inner',PREFIX+'-gateway')
    docker('network','connect','--alias','gateway',PREFIX+'-outer',PREFIX+'-gateway')
    for who in ('alice','bob','unknown'):
        docker(*base_run(who,'outer',[(RUN/who,'/client',False),(WORK/'bin','/bin-proof',True),(SOURCE,'/source',True)]),*(['--add-host','relay.test:127.0.0.1'] if native else []),IMAGE,'sleep','3600')
    time.sleep(1)
    for who in ('alice','bob'):
        execute(who,'sh','-c','python3 /source/client.py bridge '+('--native ' if native else '')+'> /client/bridge.log 2>&1 &')
    time.sleep(.5)
    print('Fixture started: private inner/outer networks; '+('native gateway on loopback only.' if native else 'zero published ports.'))


def api(who,cmd):
    value=execute(who,'python3','/source/client.py','api','5225',cmd)
    response=json.loads(value.stdout)
    if cmd.startswith('/connect ') and response.get('type') == 'sentConfirmation':
        # sentConfirmation acknowledges an asynchronous command, not an active
        # mutual contact. Fixture callers need the actual peer state before send.
        deadline=time.monotonic()+15
        while True:
            ready=[]
            for peer in ('alice','bob'):
                result=execute(peer,'python3','/source/client.py','api','5225','/contacts')
                contacts=json.loads(result.stdout).get('contacts',[])
                ready.append(any(c.get('activeConn',{}).get('connStatus') == {'type':'ready'} for c in contacts))
            if all(ready): break
            if time.monotonic() >= deadline: raise RuntimeError('fixture mutual contact did not become ready')
            time.sleep(.1)
    return response


def clients(native=False, people=('alice','bob')):
    smp=(RUN/'smp-config/fingerprint').read_text().strip()
    xftp=(RUN/'xftp-config/fingerprint').read_text().strip()
    for who in people:
        args=['/bin-proof/simplex-chat-ubuntu-24_04-aarch64','-d','/client/chat','-k','fixture-only-passphrase','-y','--disable-backup',
              '--user-display-name','Proof-'+who,'-p','5225','-s',f'smp://{smp}@'+('relay.test:5223' if native else 'localhost:15223'),'--xftp-server',f'xftp://{xftp}@'+('relay.test:8443' if native else 'localhost:18443'),
              '--smp-proxy','never','--smp-proxy-fallback','no','--smp-web-port-servers','off','--temp-folder','/client/tmp','--files-folder','/client/files']
        # sh only redirects fixed filenames; native command arguments are constant fixture values.
        import shlex
        execute(who,'sh','-c',shlex.join(args)+' > /client/chat.log 2>&1 &')
    deadline=time.monotonic()+30
    for who in people:
        while True:
            try:
                response=api(who,'/u')
                assert response['type']=='activeUser',response
                break
            except (AssertionError,ValueError,subprocess.CalledProcessError):
                if time.monotonic()>deadline: raise
                time.sleep(.3)
    print('Official CLI fixture clients ready; default public routing disabled.')


def stop():
    for name in reversed(NAMES):
        if docker('container','inspect',name,check=False).returncode==0:
            docker('stop','--time','3',name)
            docker('rm',name)
    for net in ('outer','inner','native-host'):
        if docker('network','inspect',PREFIX+'-'+net,check=False).returncode==0:
            docker('network','rm',PREFIX+'-'+net)
    print('Only named fixture containers/networks removed; files preserved.')


if __name__=='__main__':
    {'init':initialize,'start':start,'clients':clients,'stop':stop}[sys.argv[1]]()
