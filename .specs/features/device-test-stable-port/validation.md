## Validation: porte do ensaio SMP para a base estável - PASS

# Porte do ensaio SMP para a base estável

**Verdict**: PASS

**Date**: 2026-11-07
**Spec**: `.specs/features/device-test-stable-port/spec.md`
**Diff range**: `c25dc4eb0d963afa916ac7605c5f2665e66318ba..94fcf93273cdf316359a361eae757475a2eabafe`
**Verifier**: independent sub-agent, author and verifier are different agents

## Task completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 listener and fixture | PASS | 14 native transport tests passed. |
| T2 dedicated SMP startup | PASS | Compiled Simulator core passed authorization, revocation, route checks, and restart delivery. |
| T3 technical host and package | PASS | 136 portable tests passed. The arm64 unsigned build produced the expected app and framework products. |

## Spec-anchored acceptance criteria

| Criterion | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| PORT-01. Stable ancestry and technical-only scope | The candidate descends from `stable` and projects only the SMP test sources, host, fixture, and tests. | `tools/taverna/tests/test_device_test.py:53-63` asserts the three adapter paths and `tools/taverna/tests/test_device_test.py:68-73` rejects graph drift. Independent Git ancestry and publication-policy inventory covered 3 commits, 40 paths, and 48 inspected object versions with zero policy violations. | PASS |
| PORT-02. Authorized single SMP route before start | An authorized route is accepted and the effective route equals the configured route. | `tools/taverna/native_access_tests/device_test_core.py:201-203` asserts the route after configuration and readback. `tools/taverna/native_access_tests/device_test_core.py:214-215` asserts authorization before start. | PASS |
| PORT-03. Revocation and route mismatch stop the chat | Revoked identity, wrong route, wrong scheme, wrong profile, or wrong SOCKS configuration produce errors and leave the controller stopped. | `tools/taverna/native_access_tests/device_test_core.py:209-218` asserts the revocation error, stopped state, and disabled extra workers. `tools/taverna/native_access_tests/device_test_core.py:236-247` asserts route, profile, and network failures before startup. | PASS |
| PORT-04. Ten texts each way survive restart | Both clients preserve the same 20 unique items, directions, and ordering after reopening. | `tools/taverna/native_access_tests/device_test_delivery.py:70-73` asserts 20 unique items and both directions. `tools/taverna/native_access_tests/device_test_delivery.py:101-116` asserts delivery, database persistence, process restart, and identical reopened histories. | PASS |
| PORT-05. Unsigned arm64 package binds source and core | The technical receipt binds projected sources, compiled core, five native libraries, and unsigned package outputs. | `tools/taverna/tests/test_device_build.py:160-184` asserts iOS device SDK, unsigned settings, fixed package resolution, and owned paths. `tools/taverna/tests/test_device_test.py:132-149` asserts receipt limits and source/package binding. The independent receipt reported `UNSIGNED_DEVICE_BUILD_PASS`, two products, 280 core hashes, five libraries, and `UNSIGNED_TECHNICAL_PACKAGE_PASS`. | PASS |
| PORT-06. Existing portable suite is retained | All 76 base tests remain green, with the ported suite green. | The independent build gate ran 136 tests with 0 failures. The baseline comparison found the original 76 test cases present in the final set. | PASS |

## Edge cases

- PASS. A revoked identity and mismatched route fail before chat start, covered by `tools/taverna/native_access_tests/device_test_core.py:209-247`.
- PASS. Both clients restart with their existing test stores and retain the same 20 items, covered by `tools/taverna/native_access_tests/device_test_delivery.py:106-116`.
- PASS. The ordinary controller remains usable, covered by `tools/taverna/native_access_tests/device_test_core.py:222-229`.

## Gate results

| Gate | Result |
| --- | --- |
| `git diff --check` and Foundation | PASS |
| `python3.12 -m compileall -q tools/taverna` | PASS |
| Portable suite | 136 passed, 0 failed |
| Native transport suite | 14 passed, 0 failed |
| Compiled Simulator startup probe | PASS |
| Compiled Simulator delivery probe | PASS, 10 texts each way, 20 items per history, 0 duplicates, both clients reopened |
| Technical arm64 unsigned build | PASS, 2 products, signing and installation not run |

The Nix component source matched all 280 core source hashes. The five converted Simulator archives preserved their object identities and platform invariants. The build receipt bound its source, compiled core, native libraries, and package outputs.

No physical-device signing, installation, live-network test, push, or pull request was performed. Those actions remain outside this feature specification.

## Discrimination sensor

The sensor ran in five isolated disposable worktrees. The real checkout remained clean before and after each mutation.

| Mutation | Test that detected it | Result |
| --- | --- | --- |
| `apps/ios/SimpleXChat/Taverna/SocksCodec.swift:102`, allow-list check changed to unconditional rejection | `SocksTests` failed the exact SMP route assertion | Killed |
| `tools/taverna/device_build.py:121`, `CODE_SIGNING_ALLOWED=NO` changed to `YES` | `test_device_build.py:166` failed | Killed |
| `tools/taverna/device_identity.py:36`, dedicated keychain wildcard changed | `test_device_identity` rejected the profile scope | Killed |
| `tools/taverna/device_test.py:105`, `CoreTransport.swift` replaced with an unknown adapter | `test_device_test.py:57-61` failed the adapter set assertion | Killed |
| `apps/ios/SimpleXChat/KeyChain.swift`, dedicated account changed | `test_device_storage.py:160` failed the dedicated-account assertion | Killed |

**Sensor result**: 5/5 killed.

## Code quality

| Principle | Status |
| --- | --- |
| Minimum code and requested scope | PASS |
| Surgical changes and existing style | PASS |
| No unrelated Share, NSE, or publication changes | PASS |
| Spec-anchored assertions | PASS |
| Per-layer happy path, edge, and error coverage | PASS |
| Every new test maps to a listed criterion or edge case | PASS |
| Project guidelines followed | PASS, `AGENTS.md`, `CONTRIBUTING.md`, and TLC references |

## Summary

**Overall**: PASS, ready for local review.
**Spec-anchored check**: 6/6 acceptance criteria matched.
**Sensor**: 5/5 mutations killed.
**Gate**: 136 portable, 14 transport, native startup, native delivery, and unsigned package gates passed.

The candidate is ready for the maintainer's local publication-package review. The owned Simulator was shut down after the independent probes completed. No remote write has been performed.
