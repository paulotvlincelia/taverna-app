# Foundation device tests verification

**Verdict**: PASS
**Profile**: standard
**Diff range**: `7989aedf76bb7ea4206e472d4dd732f81118480e..ded288ea3ba5f971045a9d293e2cdbfa0f5a7a82`
**Round**: 1 - full
**Verifier**: independent sub-agent (author != verifier)
**Verified at**: `ded288ea3ba5f971045a9d293e2cdbfa0f5a7a82`

The feature has only the bounded `checks.md` artifact (no `plan.md` or binding source was
declared). The implementation diff contains the checks artifact and the two test files only;
`DeviceTestPolicy.swift`, the iOS application, workflows, and CI configuration are unchanged.

## Checks

| Check | Claim | Proof run | Evidence | Result |
| --- | --- | --- | --- | --- |
| C1 | A checkout without `.build` prepares its work directory and the Swift probe returns the exact class, fictitious account, and access group. | Clean Git export: `python3.12 -m unittest discover -s tools/taverna/tests -p test_device_identity.py -k test_literal_query_builder_executes_with_explicit_access_group -v` — exit 0, 1 test | `tools/taverna/tests/test_device_identity.py:139` — `(ROOT / '.build').mkdir(exist_ok=True)`; `:19` — `ACCESS = PREFIX + '.' + device.BUNDLE`; `:149` — `self.assertEqual(json.loads(out), {'class': 'genp', 'acct': 'fictitious-item', 'agrp': ACCESS})` | PASS |
| C2 | Portable storage checks exclusion before key access/open and an exclusion error blocks with zero opens. | Clean Git export: `python3.12 -m unittest discover -s tools/taverna/tests -p test_device_storage.py -k test_fresh_key_precedes_native_open -k test_existing_pair_reuses_key -k test_interrupted_creation_reuses_key -k test_backup_exclusion_precedes_open -v` — exit 0, 4 tests | `tools/taverna/tests/test_device_storage.py:132` — `self.assertEqual(row['events'], ['exclude', 'read', 'insert', 'open'])`; `:185` — `self.assertEqual(self.rows['backupError']['events'], ['exclude', 'blocked'])`; `:186` — `self.assertEqual(self.rows['backupError']['opens'], 0)`; production order is `tools/taverna/device_test/DeviceTestPolicy.swift:26` — `try excludeFromBackup(directory)` before key/bank work | PASS |
| C3 | Native storage checks the persisted `isExcludedFromBackup` property for each successful scenario and preserves the zero-open exclusion-failure proof. | Clean Git export: `python3.12 tools/taverna/tests/test_device_storage.py -k test_backup_exclusion_precedes_open -v` — exit 0, 1 test; direct native suite — exit 0, 7 tests | `tools/taverna/tests/test_device_storage.py:81` — `folder.resourceValues(forKeys: [.isExcludedFromBackupKey]).isExcludedFromBackup == true`; `:82` — `excluded = excluded && persisted`; `:184` — `self.assertTrue(self.rows[name]['excluded'])`; `:185-186` — exact blocked event and zero opens | PASS |

Each named proof was located with `rg`/numbered source inspection and appeared individually in
the run output. The additional clean-export suite ran 136/136 tests successfully; the direct
native storage invocation ran 7/7 successfully.

## Coverage

Coverage was recomputed from the scenario construction in `test_device_storage.py`, the native
mode switch, and the assertion bodies—not copied from the checks table.

| Set (size) | Recomputed from | Member -> proof | Unproven |
| --- | --- | --- | --- |
| Preparação de armazenamento portátil (4) | `tools/taverna/tests/test_device_storage.py:96-107`, with `backup_mode = "portable"` at `:19` and the C2 proof assertions | `fresh` -> C2 `:132-136`; `existing` -> C2 `:140-142`; `interrupted` -> C2 `:159-161`; `backupError` -> C2 `:185-186` | - |
| Preparação de armazenamento nativa (4) | Same four rows, with direct execution selecting `backup_mode = "native"` at `tools/taverna/tests/test_device_storage.py:189-192`; the native filesystem read is at `:80-82` | `fresh` -> C3 `:182-184`; `existing` -> C3 `:182-184`; `interrupted` -> C3 `:182-184`; `backupError` -> C3 `:185-186` | - |

The probe also retains seven ambiguous-state members (`onlyChat`, `onlyAgent`, `symlink`,
`sidecarSymlink`, `missingKey`, `invalidKey`, `readError`) and `insertError`; their existing
fail-closed assertions are at `tools/taverna/tests/test_device_storage.py:144-155` and were
green in both the 136-test portable export and the 7-test native direct suite. The retained
`restoredUnchanged` lifecycle assertion is at `:164`. They are existing coverage, not omitted
members of the four-member preparation set introduced by this diff.

## Test policy

| Code | Files / proofs | Required expectation | Expectation met | Evidence |
| --- | --- | --- | --- | --- |
| Preparação do probe de identidade | `test_device_identity.py` / C1 | Swift query returns exact class, account, and group in a clean checkout | yes | `tools/taverna/tests/test_device_identity.py:139`, `:149`; C1 clean-export proof passed |
| Probe de armazenamento | `test_device_storage.py` / C2 portable and C3 native | Three successful paths preserve order and the exclusion failure blocks before open | yes | C2 `:132`, `:140`, `:159`, `:185-186`; C3 `:81-82`, `:184-186`; both proof modes passed |

## Faults injected

Each mutation was made in its own `git worktree add --detach ... HEAD` scratch copy, the narrowest
covering proof was run, and the scratch worktree was removed. The real worktree was clean before
and after the fault runs, prior to writing this report (`git status --porcelain=v1` produced no
rows).

| Mutation | Scratch proof and observed failure | Killed |
| --- | --- | --- |
| Omit `tools/taverna/tests/test_device_identity.py:139` (`.build` preparation) | C1 exact proof exited 1 with `FileNotFoundError` creating the temporary directory | yes |
| Replace `tools/taverna/device_test/DeviceTestPolicy.swift:26` with a branch that skips `excludeFromBackup` | C2 exact proof exited 1; all four tests exposed missing `exclude` ordering, and `backupError` opened instead of blocking | yes |
| Replace `DeviceTestPolicy.swift:26` with `try? excludeFromBackup(directory)` | C2 exact proof exited 1; `backupError` produced `['exclude', 'read', 'insert', 'open']` instead of `['exclude', 'blocked']` and zero opens | yes |
| Replace the native adapter call at `tools/taverna/tests/test_device_storage.py:72` with a no-op | C3 exact proof exited 1; all three successful subtests failed `:184` because persisted `isExcludedFromBackup` was false | yes |

The fourth mutation demonstrates that C3 tests the actual Foundation resource value rather than a
path-only callback flag. The third mutation demonstrates that portable exclusion errors still
fail closed. No mutation was applied to the production worktree.

## Swept existing

| Dimension | Re-read constraint | Evidence | Result |
| --- | --- | --- | --- |
| validation | C1, C2, and C3 are individually green at the exact implementation head | Checks table and proof output above | PASS |
| failure modes | Exclusion failure records `blocked` and opens zero databases in both modes | `tools/taverna/tests/test_device_storage.py:185-186` | PASS |
| idempotency | Existing pair reuses the saved key; interrupted creation reuses it after exclusion/read | `:140-142`, `:159-161` | PASS |
| authorization | Storage probe runs under the network-denying sandbox policy | `tools/taverna/tests/test_device_storage.py:123-125` — `sandbox-exec` profile contains `(deny network*)` | PASS |
| concurrency | Identity probe uses a unique `TemporaryDirectory` under the checkout-local `.build` | `tools/taverna/tests/test_device_identity.py:140` | PASS |
| data lifecycle | Dedicated `InnerMeshDeviceTest/v1` path and restored fixture isolation remain asserted | `tools/taverna/device_test/DeviceTestPolicy.swift:17-18`; `tools/taverna/tests/test_device_storage.py:164-179` | PASS |
| dependency failure | Exclusion callback errors are covered before any open | `tools/taverna/tests/test_device_storage.py:68-70`, `:185-186` | PASS |
| state transitions | Exclusion event precedes read/insert/open on fresh, existing, and interrupted paths | `:132`, `:140`, `:159` | PASS |
| observability | n/a — the approved scope is local execution of existing tests | `checks.md` policy | accepted |

## Gate

| Command | Result |
| --- | --- |
| `python3.12 -m unittest discover -s tools/taverna/tests -v` in a clean export of `ded288ea3ba5f971045a9d293e2cdbfa0f5a7a82` | 136 passed, 0 failed (`OK`) |
| `python3.12 tools/taverna/tests/test_device_storage.py -v` in the clean export | 7 passed, 0 failed (`OK`) |
| `python3.12 tools/taverna/check_foundation.py` | exit 0 — `PASS: foundation only; no iOS build or release proof` |
| `python3.12 -m compileall -q tools/taverna` | exit 0 |
| `git diff --check 7989aedf76bb7ea4206e472d4dd732f81118480e..ded288ea3ba5f971045a9d293e2cdbfa0f5a7a82` | exit 0 |
| `python3 .agents/skills/tlc-spec-lean/scripts/validate_checks.py foundation-device-tests --root .` | 0 errors, 0 warnings |

`python3 .agents/skills/tlc-spec-lean/scripts/validate_verification.py foundation-device-tests
--root .` is the final completion gate for this report.

## Scope limits

Evidence is local macOS only. The GitHub `macos-15` rerun is outside this verification scope,
and no GitHub/API, push, merge, or publication action was performed.
