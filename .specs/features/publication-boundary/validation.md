# Public publication boundary validation

**Verdict**: PASS
**Profile**: standard
**Diff range**: `da9136c541dd4ca06da0269dfd12355a360e0d3b..84ca975dee8c2a0fb89eec790a42707de38521e4`
**Round**: 1 - staged public component
**Verifier**: independent sub-agent (author != verifier)

This report covers the generic document checker delivered in this public
component. It does not claim application release, infrastructure readiness, or
any metadata publication.

## Checks

| Check | Claim | Proof run | Evidence | Result |
| --- | --- | --- | --- | --- |
| BND-01 | Newly added owned specifications and handoff documents are reached by the checker and a generic prohibited local-access fixture is rejected. | `python3.12 -m unittest tools.taverna.tests.test_foundation.FoundationTests.test_new_feature_private_material_is_checked tools.taverna.tests.test_foundation.FoundationTests.test_root_handoff_is_checked -v` | `tools/taverna/check_foundation.py:45-66`; `tools/taverna/tests/test_foundation.py:104-118` | PASS |
| BND-02 | Relative links that are missing or resolve outside the checkout are rejected. | `python3.12 -m unittest tools.taverna.tests.test_foundation.FoundationTests.test_new_feature_links_are_checked tools.taverna.tests.test_foundation.FoundationTests.test_relative_link_outside_repository_is_rejected -v` | `tools/taverna/check_foundation.py:55-63`; `tools/taverna/tests/test_foundation.py:110-134` | PASS |
| BND-03 | Existing and broken symlinks in owned document paths are rejected without reading external content. | `python3.12 -m unittest tools.taverna.tests.test_foundation.FoundationTests.test_owned_document_symlink_is_rejected tools.taverna.tests.test_foundation.FoundationTests.test_broken_document_symlink_is_rejected -v` | `tools/taverna/check_foundation.py:48-53`; `tools/taverna/tests/test_foundation.py:120-139` | PASS |

## Coverage

| Set (size) | Recomputed from | Member → proof | Unproven |
| --- | --- | --- | --- |
| Owned document roots (3) | `tools/taverna/check_foundation.py:45-47` | root documents, `docs/taverna`, `.specs`, `.agents/skills` → `test_new_feature_private_material_is_checked`, `test_root_handoff_is_checked` | - |
| Relative-link outcomes (2) | `tools/taverna/check_foundation.py:55-63` | missing target, outside target → `test_new_feature_links_are_checked`, `test_relative_link_outside_repository_is_rejected` | - |
| Symlink outcomes (2) | `tools/taverna/check_foundation.py:48-53` | existing target, broken target → `test_owned_document_symlink_is_rejected`, `test_broken_document_symlink_is_rejected` | - |

## Faults injected

Each mutation was applied in a disposable detached worktree and the covering
test failed; the real checkout remained unchanged.

| Mutation | Covering proof | Killed |
| --- | --- | --- |
| Remove recursive `.specs` traversal (`tools/taverna/check_foundation.py:46`) | `test_new_feature_private_material_is_checked` | yes |
| Remove the explicit symlink rejection (`tools/taverna/check_foundation.py:49`) | `test_broken_document_symlink_is_rejected` | yes |

## Gates

- `python3.12 -m unittest discover -s tools/taverna/tests -q`: `76 passed`, zero failures or skips.
- `python3.12 tools/taverna/check_foundation.py --root .`: PASS.
- `python3.12 -m compileall -q tools/taverna`: PASS.
- `git diff --check`: PASS.
