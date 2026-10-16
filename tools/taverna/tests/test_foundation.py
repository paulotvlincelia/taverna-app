import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('foundation', ROOT / 'tools/taverna/check_foundation.py')
foundation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foundation)


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ['README.md', 'README.upstream.md', 'AGENTS.md', 'CLAUDE.md', 'CONTRIBUTING.md', 'LICENSE']:
            shutil.copy(ROOT / name, self.root / name)
        for name in ['docs/taverna', '.agents/skills', '.specs/features/foundation', '.specs/features/ios-first-build', '.specs/features/invitation-only', '.github/workflows']:
            shutil.copytree(ROOT / name, self.root / name)
        (self.root / 'assets').mkdir()
        shutil.copy(ROOT / 'assets/ASSETS_LICENSE.md', self.root / 'assets/ASSETS_LICENSE.md')
        # Root prose links to original directories; include only targets required by prose.
        for name in ['docs/TRADEMARK.md', 'apps/ios/README.md']:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('Upstream reference\n')
        # Upstream README links are not scanned; Taverna prose is.

    def test_valid_foundation(self):
        self.assertEqual(foundation.check(self.root), [])

    def test_release_stays_blocked(self):
        self.assertTrue(any('BLOCKED' in x for x in foundation.check(self.root, True)))

    def test_license_mutation(self):
        (self.root / 'LICENSE').write_text('wrong')
        self.assertIn('preserved license changed: LICENSE', foundation.check(self.root))

    def test_asset_permission_not_inferred(self):
        p = self.root / 'docs/taverna/asset-policy.json'
        obj = json.loads(p.read_text()); obj['release_status'] = 'PASS'; p.write_text(json.dumps(obj))
        self.assertTrue(any('must remain BLOCKED' in x for x in foundation.check(self.root)))

    def test_missing_metadata(self):
        (self.root / 'docs/taverna/upstream.json').unlink()
        self.assertTrue(any('metadata invalid' in x for x in foundation.check(self.root)))

    def test_invalid_origin(self):
        p = self.root / 'docs/taverna/upstream.json'
        obj = json.loads(p.read_text()); obj['repository'] = 'example/other'; p.write_text(json.dumps(obj))
        self.assertIn('upstream: repository/SHA mismatch', foundation.check(self.root))

    def test_both_licenses_required(self):
        p = self.root / 'docs/taverna/upstream.json'
        obj = json.loads(p.read_text()); del obj['preserved']['assets/ASSETS_LICENSE.md']; p.write_text(json.dumps(obj))
        self.assertIn('upstream: both licenses must be preserved', foundation.check(self.root))

    def test_claude_redirect(self):
        (self.root / 'CLAUDE.md').write_text('Separate rules')
        self.assertIn('CLAUDE.md must redirect to AGENTS.md', foundation.check(self.root))

    def test_broken_link(self):
        with (self.root / 'README.md').open('a') as f: f.write('\n[broken](missing.md)\n')
        self.assertIn('README.md: broken link missing.md', foundation.check(self.root))

    def test_local_path_blocked(self):
        with (self.root / 'README.md').open('a') as f: f.write('\n/Users/example/private\n')
        self.assertIn('README.md: private access material', foundation.check(self.root))

    def test_privileged_workflow(self):
        p = self.root / '.github/workflows/foundation.yml'
        p.write_text(p.read_text() + '\n# secrets.EXAMPLE\n')
        self.assertIn('workflow must be unprivileged and secret-free', foundation.check(self.root))

    def test_extra_workflow(self):
        (self.root / '.github/workflows/release.yml').write_text('name: release')
        self.assertIn('only Foundation workflow may be active', foundation.check(self.root))

    def test_attribution_required(self):
        (self.root / '.agents/skills/tlc-spec-lean/NOTICE.md').unlink()
        self.assertIn('skill attribution missing: tlc-spec-lean/NOTICE.md', foundation.check(self.root))

    def test_cli_failure_nonzero(self):
        p = subprocess.run([sys.executable, str(ROOT / 'tools/taverna/check_foundation.py'), '--root', str(self.root), '--release-assets'], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn('BLOCKED', p.stdout)


if __name__ == '__main__':
    unittest.main()
