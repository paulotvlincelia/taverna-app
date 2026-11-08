"""Private physical-device fixture. Default operations prepare cards, never services."""
import argparse
import hashlib
import importlib.util
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

ROOT=Path(__file__).resolve().parents[2]
DOCKER='/Applications/Docker.app/Contents/Resources/bin/docker'
SOURCE=('tools/taverna/device_fixture.py','tools/taverna/access_proof/fixture.py',
        'tools/taverna/access_proof/gateway.py','tools/taverna/access_proof/client.py',
        'tools/taverna/access_proof/inputs.json','tools/taverna/device_test/DeviceTestPolicy.swift')


def digests():
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCE}


def make_plan(host,ports,run,image,now=None):
    return validate_plan(dict(schema=1,host=host,ports=ports,run=run,image=image,
        lifetime=1200,expiresAt=int(time.time() if now is None else now)+3600,
        live='NOT RUN',source_sha256=digests()),now=now)


def validate_plan(plan,now=None,fresh=True):
    fields={'schema','host','ports','run','image','lifetime','expiresAt','live','source_sha256'}
    if set(plan)!=fields or type(plan['schema']) is not int or plan['schema']!=1 or plan['lifetime']!=1200 or plan['live']!='NOT RUN':raise ValueError('invalid fixture plan scope')
    host=ipaddress.IPv4Address(plan['host'])
    if not any(host in ipaddress.IPv4Network(net) for net in ('10.0.0.0/8','172.16.0.0/12','192.168.0.0/16')) or int(host)%256 in (0,255):raise ValueError('explicit private IPv4 required')
    if (not isinstance(plan['ports'],list) or len(plan['ports'])!=2 or len(set(plan['ports']))!=2
            or any(type(p) is not int or not 1024<=p<=65535 for p in plan['ports'])):raise ValueError('two distinct unprivileged ports required')
    if not re.fullmatch(r'phone-[a-f0-9]{8}',plan['run']) or not re.fullmatch(r'sha256:[a-f0-9]{64}',plan['image']):raise ValueError('invalid isolated run or image digest')
    current=time.time() if now is None else now
    if type(plan['expiresAt']) is not int or fresh and not current<plan['expiresAt']<=current+3600:raise ValueError('fixture plan expired or beyond one hour')
    if plan['source_sha256']!=digests():raise ValueError('fixture source changed; replan required')
    return plan


def dispatch(action,plan,execute,operation):
    if not execute:return dict(action=action,executed=False)
    operation();return dict(action=action,executed=True)


def device_command(arguments,plan):
    args=list(arguments)
    if not args or args[0]!='run':return args
    if '-p' in args:
        expected={f'127.0.0.1::{inner}':f'{plan["host"]}:{outer}:{inner}' for outer,inner in zip(plan['ports'],(15223,15443))}
        for i,value in enumerate(args[:-1]):
            if value=='-p':
                if args[i+1] not in expected:raise ValueError('unexpected gateway binding')
                args[i+1]=expected[args[i+1]]
    if '--name' in args:
        name=args[args.index('--name')+1]
        prefix='taverna-access-proof-'+plan['run']+'-'
        if not name.startswith(prefix):raise ValueError('foreign fixture container')
        role=name[len(prefix):]
        index=args.index(plan['image'])+1
        if role in ('relay','gateway'):args[index:index]=['timeout',str(plan['lifetime'])]
        elif role in ('alice','bob','unknown'):
            if args[index:]!=['sleep','3600']:raise ValueError('unexpected client placeholder')
            args[index:]=['sleep',str(plan['lifetime'])]
        else:raise ValueError('unknown fixture role')
    return args


def enrollment_config(plan,fingerprint,identity,anchor):
    if not re.fullmatch(r'[A-Za-z0-9_-]{43}=?',fingerprint):raise ValueError('invalid fixture relay fingerprint')
    return dict(schema=1,gatewayHost=plan['host'],smpPort=plan['ports'][0],serverName='gateway.test',
                smpServer='smp://'+fingerprint+'@relay.test:5223',expiresAt=plan['expiresAt'],
                identitySHA256=hashlib.sha256(identity).hexdigest(),anchorSHA256=hashlib.sha256(anchor).hexdigest())


def load_fixture(plan):
    previous=os.environ.get('TAVERNA_PROOF_RUN');os.environ['TAVERNA_PROOF_RUN']=plan['run']
    try:
        spec=importlib.util.spec_from_file_location('physical_fixture_'+plan['run'],ROOT/'tools/taverna/access_proof/fixture.py')
        value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    finally:
        if previous is None:os.environ.pop('TAVERNA_PROOF_RUN',None)
        else:os.environ['TAVERNA_PROOF_RUN']=previous
    value.IMAGE=plan['image']
    return value


def private_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with path.open('x') as output:json.dump(value,output,indent=2,sort_keys=True);output.write('\n')
    path.chmod(0o600)


def image_id(reference='taverna-access-proof:20261016'):
    return subprocess.check_output([DOCKER,'image','inspect',reference,'--format','{{.Id}}'],text=True,timeout=20).strip()


def prepare(plan):
    validate_plan(plan)
    if image_id(plan['image'])!=plan['image']:raise ValueError('qualified fixture image changed')
    f=load_fixture(plan)
    f.WORK.mkdir(parents=True,exist_ok=True,mode=0o700);f.WORK.chmod(0o700)
    f.initialize() # Docker --network none; no listener or service is started.
    f.make_credentials(native=True) # Offline fictitious P256 credentials only.
    directory=f.RUN/'device-enrollment/DeviceTest';directory.mkdir(parents=True,mode=0o700)
    identity=(f.RUN/'alice/device.p12').read_bytes();anchor=(f.RUN/'gateway/ca.der').read_bytes()
    (directory/'device.p12').write_bytes(identity);(directory/'ca.der').write_bytes(anchor)
    cfg=enrollment_config(plan,(f.RUN/'smp-config/fingerprint').read_text().strip(),identity,anchor)
    private_json(directory/'config.json',cfg)
    evidence=dict(plan_sha256=hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest(),
                  enrollment_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir()},
                  limits=dict(services='NOT RUN',lan='NOT RUN',phone='NOT RUN'))
    private_json(f.RUN/'device-preparation.json',evidence)
    for path in f.RUN.rglob('*'):
        if path.is_symlink():raise ValueError('symlink in fixture output')
        path.chmod(0o700 if path.is_dir() else 0o600)
    f.RUN.chmod(0o700)


def verify_prepared(plan,f):
    evidence=json.loads((f.RUN/'device-preparation.json').read_text())
    expected=hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest()
    directory=f.RUN/'device-enrollment/DeviceTest'
    if evidence.get('plan_sha256')!=expected or evidence.get('enrollment_sha256')!={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir()}:raise ValueError('prepared fixture changed')


def resource_ids(f):
    result={}
    for kind,names in (('container',f.NAMES),('network',[f.PREFIX+'-'+n for n in ('inner','outer','native-host')])):
        for name in names:
            value=f.docker(kind,'inspect',name,check=False)
            if value.returncode==0:result[kind+':'+name]=json.loads(value.stdout)[0]['Id']
    return result


def verify_resource_ids(expected,observed):
    if expected!=observed:raise ValueError('fixture resource ownership conflict; preserve all resources')


def start(plan):
    validate_plan(plan)
    if image_id(plan['image'])!=plan['image']:raise ValueError('fixture image changed')
    f=load_fixture(plan);verify_prepared(plan,f)
    if resource_ids(f):raise ValueError('fixture resource name conflict; no services started')
    original=f.docker;created={}
    ownership=f.RUN/'device-live-resources.json'
    if ownership.exists():raise ValueError('preserve prior live run; choose a fresh plan')
    def docker(*args,**kw):
        value=original(*device_command(args,plan),**kw)
        if value.returncode==0:
            key=None
            if args[:2]==('network','create'):key='network:'+args[-1]
            elif args[0]=='run' and '--name' in args:key='container:'+args[args.index('--name')+1]
            if key:
                created[key]=value.stdout.strip()
                # Record IDs immediately, including partial starts; never cleanup foreign names.
                if ownership.exists():ownership.write_text(json.dumps(created,indent=2)+'\n')
                else:private_json(ownership,created)
        return value
    f.docker=docker
    f.make_credentials=lambda **kwargs:verify_prepared(plan,f)
    f.start(native=True)
    f.clients(native=True,people=('bob',))
    verify_resource_ids(created,resource_ids(f))
    private_json(f.RUN/'device-live-started.json',dict(status='STARTED',run=plan['run'],expiresAt=time.time()+plan['lifetime']))


def cleanup_commands(owned):
    commands=[]
    for key,value in reversed(sorted(owned.items())):
        if key.startswith('container:'):commands.extend([('stop','--time','3',value),('rm',value)])
    for key,value in reversed(sorted(owned.items())):
        if key.startswith('network:'):commands.append(('network','rm',value))
    return commands


def stop(plan):
    validate_plan(plan,fresh=False)
    f=load_fixture(plan)
    expected=json.loads((f.RUN/'device-live-resources.json').read_text())
    verify_resource_ids(expected,resource_ids(f)) # Check every identity before any mutation.
    for command in cleanup_commands(expected):f.docker(*command)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('plan');p.add_argument('--address',required=True);p.add_argument('--ports',nargs=2,type=int,default=[15223,15443]);p.add_argument('--output',type=Path,required=True)
    for name in ('prepare','start','stop'):
        p=sub.add_parser(name);p.add_argument('--plan',type=Path,required=True);p.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    if args.action=='plan':
        path=args.output.resolve()
        if not path.is_relative_to(ROOT/'.state'):raise ValueError('private plan must stay in owned .state')
        plan=make_plan(args.address,args.ports,'phone-'+uuid.uuid4().hex[:8],image_id())
        private_json(path,plan);print(json.dumps(dict(status='PLAN_ONLY',run=plan['run'],live='NOT RUN')))
    else:
        if not args.plan.resolve().is_relative_to(ROOT/'.state'):raise ValueError('private plan must stay in owned .state')
        plan=json.loads(args.plan.read_text())
        validate_plan(plan,fresh=args.action!='stop')
        print(json.dumps(dispatch(args.action,plan,args.execute,lambda:globals()[args.action](plan))))


if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.SubprocessError) as error:
        raise SystemExit('BLOCKED: '+str(error))
