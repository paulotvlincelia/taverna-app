"""Original technical host resources; no upstream artwork permission is assumed."""
import copy
import hashlib
import json
from pathlib import Path
import plistlib
import re
import struct
import zlib

import device_identity as identity

PROJECT = identity.PROJECT
INHERITED = ('apps/ios/Shared/Assets.xcassets', 'apps/ios/Shared/SimpleXAssets.xcassets', 'apps/ios/sounds')
SOURCE_DIR = 'tools/taverna/device_test'
LIMITS = dict(signing='NOT RUN', installation='NOT RUN', execution='NOT RUN',
              lan='NOT RUN', delivery='NOT RUN', runtime_storage='NOT RUN',
              transport='PREPARED_NOT_QUALIFIED_ON_DEVICE', readiness='BLOCKED')
PROJECTION = {PROJECT, identity.INFO, 'apps/ios/DeviceTestApp.swift', 'apps/ios/DeviceTestPolicy.swift',
              'apps/ios/DeviceAssets.xcassets/Contents.json',
              'apps/ios/DeviceAssets.xcassets/DeviceIcon.appiconset/Contents.json',
              'apps/ios/DeviceAssets.xcassets/DeviceIcon.appiconset/icon.png',
              'apps/ios/DeviceNotices/LICENSE.txt', 'apps/ios/DeviceNotices/NOTICE.txt'}


def validate_result(result):
    if result.get('status') != 'UNSIGNED_TECHNICAL_PACKAGE_PASS' or result.get('limits') != LIMITS:
        raise ValueError('technical proof promoted to runtime')
    projection = result.get('projection_sha256', {})
    package = result.get('package_sha256', {})
    if set(projection) != PROJECTION or not {'SimpleX', 'Info.plist', 'Assets.car'} <= set(package):
        raise ValueError('incomplete technical projection or package binding')
    if not all(isinstance(v, str) and re.fullmatch('[a-f0-9]{64}', v)
               for v in [result.get('inventory_sha256')] + list(projection.values()) + list(package.values())):
        raise ValueError('invalid technical artifact digest')
    return result



def icon_png():
    # Original geometric test marker: three offset light bars on a navy field.
    # RGB, opaque, no font, image, symbol or vector copied from another source.
    def chunk(kind, body):
        return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body))
    pixels=bytearray()
    for y in range(1024):
        pixels.append(0)
        for x in range(1024):
            bar=any(a<=x<a+110 and b<=y<b+400 for a,b in ((250,350),(457,250),(664,150)))
            pixels.extend((213,235,230) if bar else (23,44,58))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1024,1024,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(pixels,9))+chunk(b'IEND',b'')


def notices(root):
    gif=root/SOURCE_DIR/'SwiftyGif.LICENSE.txt'
    return (b'InnerMesh technical device test. Independent SimpleX Chat fork.\n'
            b'Original technical UI and generated geometric icon: project contributions under AGPLv3.\n'
            b'SimpleX source and source-built core retain AGPLv3 and their original notices.\n'
            b'No upstream proprietary graphic resources are included in this variant.\n'
            b'SwiftyGif is the retained shared-framework dependency, under the following MIT notice:\n\n'+gif.read_bytes())


def render(project, info, root):
    data=copy.deepcopy(project);info=copy.deepcopy(info);o=data['objects']
    targets={o[t]['name']:o[t] for t in o[data['rootObject']]['targets']}
    if set(targets)!={'SimpleX (iOS)','SimpleXChat'}:raise ValueError('unexpected technical target graph')
    host=targets['SimpleX (iOS)']
    def add(path,kind,index):
        ref=f'DE71CE00000000000000{index:04X}'; build=f'DE71CE00000000000001{index:04X}'
        if ref in o or build in o:raise ValueError('technical object collision')
        o[ref]=dict(isa='PBXFileReference',path=path,sourceTree='SOURCE_ROOT',lastKnownFileType=kind)
        o[build]=dict(isa='PBXBuildFile',fileRef=ref)
        o[data['rootObject']]['mainGroup'] # Fail on malformed projects.
        o[o[data['rootObject']]['mainGroup']]['children'].append(ref)
        return build
    sources=[add('DeviceTestApp.swift','sourcecode.swift',1),add('DeviceTestPolicy.swift','sourcecode.swift',2)]
    resources=[add('DeviceAssets.xcassets','folder.assetcatalog',3),add('DeviceNotices','folder',4)]
    phases=[o[p] for p in host['buildPhases']]
    for kind,files in (('PBXSourcesBuildPhase',sources),('PBXResourcesBuildPhase',resources)):
        found=[p for p in phases if p['isa']==kind]
        if len(found)!=1:raise ValueError('unexpected technical source/resource phase')
        found[0]['files']=files
    host['buildPhases']=[p for p in host['buildPhases'] if o[p]['isa']!='PBXShellScriptBuildPhase']
    host['packageProductDependencies']=[p for p in host['packageProductDependencies'] if o[p]['productName']=='SwiftyGif']
    if len(host['packageProductDependencies'])!=1:raise ValueError('missing shared image dependency')
    for phase in phases:
        if phase['isa']=='PBXFrameworksBuildPhase':
            phase['files']=[f for f in phase['files'] if o[f].get('productRef') in host['packageProductDependencies'] or o.get(o[f].get('fileRef'),{}).get('path')=='SimpleXChat.framework']
            if len(phase['files'])!=2:raise ValueError('unexpected host linkage')
        if phase['isa']=='PBXCopyFilesBuildPhase':
            phase['files']=[f for f in phase['files'] if o.get(o[f].get('fileRef'),{}).get('path')=='SimpleXChat.framework']
    for c in o[host['buildConfigurationList']]['buildConfigurations']:
        s=o[c]['buildSettings']
        s['ASSETCATALOG_COMPILER_APPICON_NAME']='DeviceIcon'
        s['ASSETCATALOG_COMPILER_INCLUDE_ALL_APPICON_ASSETS']='NO'
        s.pop('ASSETCATALOG_COMPILER_ALTERNATE_APPICON_NAMES',None)
        for k in list(s):
            if k.startswith('INFOPLIST_KEY_NS') or k.startswith('INFOPLIST_KEY_CFBundleDisplayName'):
                s.pop(k)
        s['SWIFT_OBJC_BRIDGING_HEADER']=''
    shared = targets['SimpleXChat']
    shared_sources = [o[p] for p in shared['buildPhases'] if o[p]['isa'] == 'PBXSourcesBuildPhase']
    if len(shared_sources) != 1:
        raise ValueError('unexpected technical framework source phase')
    for index, name in enumerate(('SocksCodec', 'RelayTransport', 'CoreTransport'), start=5):
        shared_sources[0]['files'].append(add(f'SimpleXChat/Taverna/{name}.swift', 'sourcecode.swift', index))
    for c in o[shared['buildConfigurationList']]['buildConfigurations']:
        settings = o[c]['buildSettings']
        conditions = settings.get('SWIFT_ACTIVE_COMPILATION_CONDITIONS', '$(inherited)')
        settings['SWIFT_ACTIVE_COMPILATION_CONDITIONS'] = conditions + ' TAVERNA_DEVICE_TEST'
    info.pop('CFBundleIcons',None);info.pop('CFBundleIcons~ipad',None)
    info['NSLocalNetworkUsageDescription']='Connect to the private Mac fixture for this technical test.'
    info['UIFileSharingEnabled']=False
    def js(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
    meta={'info':{'author':'innermesh','version':1}}
    catalog='apps/ios/DeviceAssets.xcassets/'
    return {PROJECT:plistlib.dumps(data),identity.INFO:plistlib.dumps(info),
            catalog+'Contents.json':js(meta),
            catalog+'DeviceIcon.appiconset/Contents.json':js(dict(meta,images=[dict(filename='icon.png',idiom='universal',platform='ios',size='1024x1024')])),
            catalog+'DeviceIcon.appiconset/icon.png':icon_png(),
            'apps/ios/DeviceNotices/LICENSE.txt':(root/'LICENSE').read_bytes(),
            'apps/ios/DeviceNotices/NOTICE.txt':notices(root)}


def inventory(root,output):
    rows=[]
    for directory in INHERITED:
        for p in sorted((root/directory).rglob('*')):
            if p.is_symlink():raise ValueError('symlink in source resources')
            if p.is_file():rows.append(dict(path=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),origin='upstream resource',license='assets/ASSETS_LICENSE.md; permission not assumed',disposition='excluded',replacement='DeviceAssets and original technical host'))
    for p,b in sorted(output.items()):
        if p not in (PROJECT,identity.INFO):rows.append(dict(path=p,sha256=hashlib.sha256(b).hexdigest(),origin='original generated test resource or preserved license notice',license='AGPLv3; embedded third-party notices retained',disposition='generated',replacement='self'))
    return rows


def inspect_resources(app,root):
    required={'SimpleX','Info.plist','PkgInfo','Assets.car','DeviceNotices/LICENSE.txt','DeviceNotices/NOTICE.txt','Frameworks/SimpleXChat.framework/SimpleXChat','Frameworks/SimpleXChat.framework/Info.plist'}
    files={str(p.relative_to(app)):p for p in app.rglob('*') if p.is_file()}
    if any(p.is_symlink() for p in app.rglob('*')):raise ValueError('symlink in technical package')
    if not required<=set(files):raise ValueError('missing technical package resources')
    gif_names=set()
    for n in files:
        if n in required:continue
        if re.fullmatch(r'DeviceIcon(?:60x60|76x76)@(?:2|3)x(?:~ipad)?\.png',n):continue
        # Xcode may retain AppIcon-prefixed output filenames, independently of catalog name.
        if re.fullmatch(r'AppIcon(?:60x60|76x76)@(?:2|3)x(?:~ipad)?\.png',n):continue
        match=re.fullmatch(r'Frameworks/(SwiftyGif_[A-Za-z0-9_-]+_PackageProduct)\.framework/(Info\.plist|\1)',n)
        if match:gif_names.add(match[1]);continue
        raise ValueError('unexpected technical package resource: '+n)
    if len(gif_names)!=1:raise ValueError('missing or ambiguous required SwiftyGif framework')
    if files['DeviceNotices/LICENSE.txt'].read_bytes()!=(root/'LICENSE').read_bytes() or files['DeviceNotices/NOTICE.txt'].read_bytes()!=notices(root):raise ValueError('technical license notice differs')
    return {n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in sorted(files.items())}
