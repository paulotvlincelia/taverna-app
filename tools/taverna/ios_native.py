#!/usr/bin/env python3
"""Prepare pinned native libraries in an exclusive local attempt; never download."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import struct
import subprocess
import sys
import time
import zipfile

import ios_session as session

UPSTREAM = '479548ee53ffb73db73841e77acbeee5a78dbbd5'
LOCK = 'apps/ios/SimpleX.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved'
VERSION_COMMANDS = (0x24, 0x25, 0x2f, 0x30, 0x32)
TOOLS = Path('/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin')
MAX_BYTES = 5 * 1024 ** 3


def sha256(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def members(data):
    require(data[:8] == b'!<arch>\n', 'invalid archive signature')
    pos, result = 8, []
    while pos < len(data):
        header = data[pos:pos + 60]
        require(len(header) == 60 and header[58:] == b'`\n', 'truncated archive header')
        size = int(header[48:58])
        require(size >= 0, 'invalid archive length')
        body = data[pos + 60:pos + 60 + size]
        require(len(body) == size, 'truncated archive member')
        name = header[:16].decode().strip().rstrip('/')
        if name.startswith('#1/'):
            length = int(name[3:])
            require(0 < length <= len(body), 'invalid archive member name length')
            name, body = body[:length].decode().rstrip('\0'), body[length:]
        pos += 60 + size + size % 2
        if name in ('__.SYMDEF', '__.SYMDEF SORTED', '__.SYMDEF_64', '__.SYMDEF_64 SORTED'):
            continue
        require(name and Path(name).name == name and name not in ('.', '..')
                and not any(c in name for c in '\n\r\\\0'), 'unsafe archive member name')
        result.append((name, body))
    require(pos == len(data) and result, 'empty or truncated archive')
    return result


def macho(data):
    require(len(data) >= 32, 'truncated Mach-O header')
    header = struct.unpack_from('<8I', data)
    require(header[0] == 0xfeedfacf, 'expected thin little-endian Mach-O 64')
    end, pos, commands, versions, platforms = 32 + header[5], 32, [], [], []
    require(end <= len(data), 'truncated Mach-O load commands')
    for _ in range(header[4]):
        require(pos + 8 <= end, 'missing Mach-O load command')
        command, length = struct.unpack_from('<II', data, pos)
        require(length >= 8 and pos + length <= end, 'invalid Mach-O load command')
        raw = bytes(data[pos:pos + length])
        if command == 0x32:
            require(length >= 24, 'truncated build version')
            platform, minimum, sdk, tools = struct.unpack_from('<4I', raw, 8)
            require(length == 24 + tools * 8, 'invalid build version tools')
            platforms.append(platform); versions.append((minimum, sdk))
        elif command in VERSION_COMMANDS:
            require(length == 16, 'invalid legacy version')
            versions.append(struct.unpack_from('<II', raw, 8))
            platforms.append('legacy')
        commands.append((command, raw))
        pos += length
    require(pos == end and len(versions) == 1, 'missing or ambiguous Mach-O platform')
    return dict(header=header, commands=commands, end=end, versions=versions, platforms=platforms)


def invariant(data):
    parsed = macho(data); header = parsed['header']; end = parsed['end']
    require(header[1] == 16777228 and header[3] == 1, 'expected arm64 object')
    offsets, other = [], []
    for command, raw in parsed['commands']:
        if command not in VERSION_COMMANDS:
            other.append(raw)
        if command == 0x19:
            require(len(raw) >= 72, 'truncated segment')
            fileoff, filesize = struct.unpack_from('<QQ', raw, 40)
            sections = struct.unpack_from('<I', raw, 64)[0]
            require(72 + sections * 80 <= len(raw), 'truncated sections')
            if fileoff and filesize:
                require(fileoff >= end and fileoff + filesize <= len(data), 'invalid segment payload')
                offsets.append(fileoff)
            for i in range(sections):
                section = 72 + i * 80
                size = struct.unpack_from('<Q', raw, section + 40)[0]
                off = struct.unpack_from('<I', raw, section + 48)[0]
                kind = struct.unpack_from('<I', raw, section + 64)[0] & 0xff
                if size and kind not in (1, 12, 18):
                    require(off >= end and off + size <= len(data), 'invalid section payload')
                    offsets.append(off)
        elif command == 2:
            require(len(raw) == 24, 'invalid symbol table command')
            symoff, count, stroff, size = struct.unpack_from('<4I', raw, 8)
            for off, length in ((symoff, count * 16), (stroff, size)):
                if length:
                    require(off >= end and off + length <= len(data), 'invalid symbol payload')
                    offsets.append(off)
    first = min(offsets) if offsets else len(data)
    return dict(header=header[:5] + header[6:],
                non_version_sha256=hashlib.sha256(b''.join(other)).hexdigest(),
                payload_offset=first, payload_sha256=hashlib.sha256(data[first:]).hexdigest(),
                versions=parsed['versions'], bytes=len(data))


def require_preserved(before, after):
    require(invariant(before) == invariant(after), 'native payload/header/versions changed')


def inspect_archive(data):
    entries = members(data)
    for _, body in entries:
        parsed = macho(body)
        require(parsed['header'][1] == 16777228 and parsed['header'][3] == 1
                and parsed['platforms'] == [7], 'native object must be arm64 iOS Simulator')
    return dict(objects=len(entries), architecture='arm64', platform=7)


def validate_library(path, record):
    require(sha256(path) == record['sha256'], 'native library hash mismatch: ' + record['name'])
    actual = inspect_archive(Path(path).read_bytes())
    require(actual['objects'] == record['objects'], 'native object count mismatch: ' + record['name'])
    return actual


def validate_manifest(root, manifest):
    require(manifest['schema'] == 1 and manifest['upstream_commit'] == UPSTREAM, 'unknown native source')
    base = 'https://github.com/simplex-chat/simplex-chat/'
    require(manifest['source_url'] == base + 'tree/' + UPSTREAM
            and manifest['recipe_url'] == base + 'blob/' + UPSTREAM + '/flake.nix', 'native source URL mismatch')
    for key, path in [('flake_lock_sha256', 'flake.lock'), ('cabal_project_sha256', 'cabal.project'),
                      ('swiftpm_lock_sha256', LOCK)]:
        require(manifest[key] == sha256(root / path), 'changed lock/source: ' + key)
    require(manifest['licenses']['simplex']['sha256'] == sha256(root / 'LICENSE'), 'native license mismatch')
    libraries = manifest['libraries']; names = [v['name'] for v in libraries]
    require(len(libraries) == 5 and len(set(names)) == 5 and sum(v['objects'] for v in libraries) == 4187,
            'unexpected fixed native set')
    require(manifest['core_realization'] == 'LOCAL_SOURCE_REALIZED', 'native realization missing')
    for library in libraries:
        require(library['architecture'] == 'arm64' and library['platform'] == 7
                and library['code_data_relocations_preserved'] is True and library['licenses'],
                'unqualified native manifest entry')


def extract_bundle(bundle, destination, manifest, max_bytes=MAX_BYTES):
    require(bundle.stat().st_size <= max_bytes and bundle.stat().st_size == manifest['bundle_bytes'],
            'native bundle size limit/mismatch')
    require(sha256(bundle) == manifest['bundle_sha256'], 'native bundle hash mismatch')
    expected = {v['name']: v['original_sha256'] for v in manifest['libraries']}
    with zipfile.ZipFile(bundle) as source:
        entries = source.infolist(); names = [entry.filename for entry in entries]
        require(len(names) == len(set(names)) and set(names) == set(expected), 'unexpected or duplicate ZIP paths')
        require(sum(entry.file_size for entry in entries) <= max_bytes, 'native ZIP expansion limit')
        for entry in entries:
            path = PurePosixPath(entry.filename)
            require(not path.is_absolute() and len(path.parts) == 1 and path.name not in ('.', '..')
                    and '\\' not in entry.filename and not entry.is_dir()
                    and not stat.S_ISLNK(entry.external_attr >> 16), 'unsafe native ZIP path')
        destination.mkdir()  # Preserve previous output; no overwrite.
        for entry in entries:
            path = destination / entry.filename
            with source.open(entry) as original, path.open('xb') as target:
                shutil.copyfileobj(original, target)
            require(sha256(path) == expected[entry.filename], 'original library hash mismatch')


def remaining(deadline, cap):
    seconds = deadline - time.monotonic()
    require(seconds > 0, 'native preparation timeout')
    return min(seconds, cap)


def convert_archive(source, destination, work, record, deadline):
    work.mkdir(); entries = members(source.read_bytes()); paths, proofs = [], []
    for ordinal, (name, data) in enumerate(entries):
        folder = work / f'{ordinal:05d}'; folder.mkdir()
        original, converted = folder / (name + '.input'), folder / name
        original.write_bytes(data); info = invariant(data)
        def version(number):
            return f'{number >> 16}.{(number >> 8) & 255}.{number & 255}'
        minimum, sdk = info['versions'][0]
        command = [str(TOOLS / 'vtool'), '-set-build-version', 'iossim', version(minimum), version(sdk),
                   '-replace', '-output', str(converted), str(original)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=remaining(deadline, 30))
        require(result.returncode == 0, 'vtool failed: ' + result.stderr)
        changed = converted.read_bytes(); require_preserved(data, changed)
        require(macho(changed)['platforms'] == [7], 'conversion did not produce Simulator object')
        paths.append(converted)
        proofs.append(dict(ordinal=ordinal, name=name, original_sha256=hashlib.sha256(data).hexdigest(),
                           simulator_sha256=sha256(converted), invariant=info))
    filelist = work / 'objects.txt'; filelist.write_text(''.join(str(p) + '\n' for p in paths))
    command = [str(TOOLS / 'libtool'), '-static', '-D', '-o', str(destination), '-filelist', str(filelist)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=remaining(deadline, 120))
    (work / 'libtool.json').write_text(json.dumps(dict(command=command, exit_code=result.returncode,
        stdout=result.stdout, stderr=result.stderr), indent=2))
    require(result.returncode == 0, 'libtool failed: ' + result.stderr)
    rebuilt = members(destination.read_bytes())
    require([n for n, _ in rebuilt] == [n for n, _ in entries], 'archive member order/names changed')
    for ordinal, ((_, original), (_, converted)) in enumerate(zip(entries, rebuilt)):
        require_preserved(original, converted)
        require(hashlib.sha256(converted).hexdigest() == proofs[ordinal]['simulator_sha256'],
                'rebuilt object hash mismatch')
    validate_library(destination, record)
    (work / 'object-proof.json').write_text(json.dumps(proofs, indent=2))


def prepare(root, bundle, attempt_name, manifest_path):
    attempt = session.new_attempt(root, attempt_name)
    deadline = time.monotonic() + 5400
    record = dict(stage='native-preparation', started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  timeout_seconds=5400, monitor_pid=os.getpid(), tool_source_sha256=sha256(Path(__file__)),
                  command=sys.argv, core_origin='local pinned Nix product; see native-inputs.json', app_build='NOT RUN')
    (attempt / 'active.json').write_text(json.dumps(record, indent=2))
    try:
        manifest = json.loads(manifest_path.read_text()); validate_manifest(root, manifest)
        record['native_manifest_sha256'] = sha256(manifest_path)
        record['tools'] = {name: sha256(TOOLS / name) for name in ('vtool', 'libtool')}
        require(record['tools'] == manifest['conversion']['tool_sha256'], 'conversion tool hash mismatch')
        extract_bundle(bundle, attempt / 'original', manifest)
        (attempt / 'sim').mkdir(); records = []
        for library in manifest['libraries']:
            name = library['name']; destination = attempt / 'sim' / name
            convert_archive(attempt / 'original' / name, destination, attempt / (name + '.objects'), library, deadline)
            records.append(dict(name=name, path=str(destination), sha256=sha256(destination), objects=library['objects']))
        record.update(exit_code=0, libraries=records)
    except (ValueError, OSError, KeyError, struct.error, zipfile.BadZipFile, subprocess.SubprocessError) as error:
        record.update(exit_code=2, error=str(error))
    record['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (attempt / 'receipt.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args(); root = Path(__file__).resolve().parents[2]
    result = prepare(root, args.bundle, args.attempt, root / '.specs/features/ios-first-build/native-inputs.json')
    print(json.dumps(result, indent=2)); return result['exit_code']


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError) as error:
        print(f'BLOCKED: {error}', file=sys.stderr); sys.exit(2)
