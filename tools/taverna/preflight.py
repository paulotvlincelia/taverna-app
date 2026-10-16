"""Read-only development preflight. BLOCKED is not a build failure or readiness proof."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Callable

GHC_REQUIRED = '9.6.3'  # upstream flake.nix compiler-nix-name = "ghc963"
LAYOUT = ('DerivedData', 'SourcePackages', 'cabal', 'stack', 'tmp', 'logs')


def state_layout(root: Path) -> dict[str, str]:
    """Resolve per-worktree state and reject symlink escape, without creating it."""
    root = root.resolve()
    paths = {name: (root / '.build' / name).resolve() for name in LAYOUT}
    if any(not path.is_relative_to(root) for path in paths.values()):
        raise ValueError('BLOCKED: writable state escapes the worktree')
    return {name: str(path) for name, path in paths.items()}


def run_command(argv: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=15)
        # stderr may contain local paths or sensitive account diagnostics: never emit it.
        return result.returncode, result.stdout
    except FileNotFoundError:
        return 127, ''
    except subprocess.TimeoutExpired:
        return 124, ''
    except OSError:
        return 126, ''


def inspect(root: Path, run: Callable = run_command) -> dict:
    checks: dict[str, dict] = {}
    definitions = {
        'git': (['git', '--version'], r'git version ([0-9.]+)', None),
        'gh': (['gh', '--version'], r'gh version ([0-9.]+)', None),
        'python': (['python3.12', '--version'], r'Python (3\.12\.\d+)', '3.12'),
        'xcode': (['xcodebuild', '-version'], r'Xcode ([0-9.]+)', None),
        'ios_sdk': (['xcrun', '--sdk', 'iphoneos', '--show-sdk-version'], r'^([0-9.]+)\s*$', None),
        'simulator_sdk': (['xcrun', '--sdk', 'iphonesimulator', '--show-sdk-version'], r'^([0-9.]+)\s*$', None),
        'ghc': (['ghc', '--numeric-version'], r'^([0-9.]+)\s*$', GHC_REQUIRED),
        'cabal': (['cabal', '--numeric-version'], r'^([0-9.]+)\s*$', None),
    }
    for name, (argv, pattern, required) in definitions.items():
        code, output = run(argv)
        match = re.search(pattern, output.strip()) if code == 0 else None
        version = match.group(1) if match else None
        valid = version is not None and (not required or (version.startswith('3.12.') if name == 'python' else version == required))
        checks[name] = {'status': 'PASS' if valid else 'BLOCKED', 'version': version,
                        'required': required or 'available',
                        'reason': None if valid else ('missing' if code == 127 else 'timeout' if code == 124 else 'unavailable or incompatible')}
    code, output = run(['xcrun', 'simctl', 'list', 'devices', 'available', '--json'])
    try:
        devices = json.loads(output)['devices'] if code == 0 else {}
        count = sum(1 for values in devices.values() for device in values
                    if device.get('isAvailable') is True)
        valid = count > 0
    except (ValueError, KeyError, TypeError, AttributeError):
        count, valid = 0, False
    checks['simulators'] = {'status': 'PASS' if valid else 'BLOCKED', 'available_count': count,
                            'reason': None if valid else 'no available simulator proven'}
    try:
        state_layout(root)
        checks['state_isolation'] = {'status': 'PASS', 'reason': 'layout confined to worktree; does not prove session ownership/UDID assignment'}
    except ValueError as exc:
        checks['state_isolation'] = {'status': 'BLOCKED', 'reason': str(exc)}
    # F0 cannot infer library provenance, compile results, signing, or APNs from installed tools.
    checks['core_libraries'] = {'status': 'BLOCKED', 'reason': 'library provenance/compatibility and build proof required in F1'}
    checks['signing'] = {'status': 'BLOCKED', 'reason': 'manual authorized Apple identity/capabilities proof required; no credentials inspected'}
    groups = {
        'foundation_tools': ('git', 'gh', 'python', 'state_isolation'),
        'ios_simulator': ('xcode', 'ios_sdk', 'simulator_sdk', 'simulators', 'state_isolation', 'core_libraries'),
        'core_from_source': ('ghc', 'cabal', 'state_isolation', 'core_libraries'),
        'signed_device': ('xcode', 'ios_sdk', 'core_libraries', 'signing'),
    }
    gates = {name: {'status': 'PASS' if all(checks[key]['status'] == 'PASS' for key in keys) else 'BLOCKED',
                    'blocked_by': [key for key in keys if checks[key]['status'] != 'PASS']}
             for name, keys in groups.items()}
    code, sha = run(['git', '-C', str(root), 'rev-parse', 'HEAD'])
    sha = sha.strip()
    return {'schema': 1, 'scope': 'read-only-tooling-preflight',
            'source_commit': sha if code == 0 and re.fullmatch(r'[0-9a-f]{40}', sha) else None,
            'checks': checks, 'gates': gates,
            'overall': 'BLOCKED' if any(g['status'] != 'PASS' for g in gates.values()) else 'PASS',
            'build_proven': False, 'push_proven': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = inspect(args.root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['overall'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
