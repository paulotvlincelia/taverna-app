# Primeiro build iOS da Taverna — Validation

**Date**: 2026-10-16  
**Spec**: `.specs/features/ios-first-build/spec.md`  
**Implementation SHA**: `6ea482bd4a1912d8eef52904d930c7f6c57bf746`  
**Diff range**: `8b2ffa71dc414615236f3fd41cb3a11876be740c..6ea482bd4a1912d8eef52904d930c7f6c57bf746`  
**Verifier**: independent Codex verifier; author and verifier used distinct worktrees, caches and simulators  
**Verdict**: **PASS**

---

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | ✅ Done | Pinned Nix derivation realized; five libraries and 4,187 objects reproduced from the immutable store output. |
| T2 | ✅ Done | Owned standard-index UDID, physical worktree storage and before-main process containment passed in both sessions. |
| T7 | ✅ Done | Effective Xcode cache paths were inside each worktree; external and symlink escapes are rejected. |
| T3 | ✅ Done | Four real UI methods passed in the approved first-build profile with zero failures/skips. |
| T8 | ✅ Done | Versioned native preparer reproduced all five qualified hashes independently. |
| T4 | ✅ Done | Strict proof validator accepted real products/results and rejected all injected fault classes. |
| T5 | ✅ Done | The versioned guide reproduced the procedure in a new worktree without private context. |
| T6 | ✅ Done | Two clean proofs, independent comparison, exact-SHA CI and this independent report passed. |

## Spec-Anchored Acceptance Criteria

The expected outcomes below were re-derived from `spec.md`; implementation summaries were not treated as evidence. Local receipts remain ignored under each proof worktree's `.build/attempts`; only sanitized results are recorded here.

| Criterion | Spec-defined outcome | `file:line` + assertion and observed outcome | Result |
| --- | --- | --- | --- |
| IOS-01 | The native manifest fixes immutable source/recipe URLs, source commit and evidence, licenses, received hash, and hashes of the five used libraries. | `.specs/features/ios-first-build/native-inputs.json:1` records the bundle hash/size; `:18` records five per-library original/final hashes and licenses; `:125`–`:142` records immutable source/recipe/WebRTC provenance. `tools/taverna/ios_native.py:169` asserts the exact ZIP member set and `:182` asserts each original hash. Both independent native preparations returned exit 0 with manifest SHA-256 `ae89d70e…`. | ✅ PASS |
| IOS-02 | Unknown origin, changed locks/hash, incompatible platform or otherwise unqualified input blocks with non-zero status. | `tools/taverna/tests/test_ios_native.py:133` mutates source/lock identities and asserts `ValueError`; `:145` mutates library hash/count/platform and asserts rejection. `tools/taverna/ios_native.py:244` converts validation failures to exit 2. The sensor's platform, payload and bundle-hash mutants were all killed. | ✅ PASS |
| IOS-03 | SwiftPM resolution preserves exactly the seven pinned revisions unless explicitly reviewed. | `docs/taverna/ios-build.md:81` asserts the lock hash before resolution and `:84` asserts the same hash afterward plus `len(...['pins']) == 7`. Both sessions resolved seven pins with unchanged `Package.resolved`; the manifest retained `swiftpm_lock_sha256` at `.specs/features/ios-first-build/native-inputs.json:129`. | ✅ PASS |
| IOS-04 | Products, downloads, writable caches, databases, simulator data and logs stay in the owning worktree; only standard SDK aliases and immutable Nix store reuse are allowed. | `tools/taverna/tests/test_ios_session.py:47` and `:72` assert rejection of external data/logs; `:125`–`:143` assert every effective Xcode cache path and symlink target stays inside the worktree. `tools/taverna/tests/test_ios_proof.py:213` asserts SourcePackages/package-cache/DerivedData cannot alias another worktree. Both clean receipts recorded distinct local roots/caches. | ✅ PASS |
| IOS-05 | Xcode selects the session-exclusive UDID from the standard SDK index while physical data/logs belong to the worktree. | `tools/taverna/tests/test_ios_session.py:39` asserts the index resolves to owned physical storage; `:43` rejects a foreign destination; `:63` rejects a non-standard index. Runtime preflight/control and both strict proofs selected their own distinct UDIDs and recorded no new device IDs. | ✅ PASS |
| IOS-06 | Effective signing is recorded for every target without Apple-account authentication or automatic provisioning. | `tools/taverna/ios_proof.py:205` requires all five targets; `:210`–`:212` asserts `CODE_SIGNING_ALLOWED=YES`, identity `-`, empty development team and empty provisioning profile. `:139`–`:146` verifies each bundle's ad hoc signature. Both builds returned `account_provisioning: NOT USED`. | ✅ PASS |
| IOS-07 | Over-limit downloads/expansion and unsafe extraction paths fail non-zero. | `tools/taverna/tests/test_ios_native.py:118` injects traversal, duplicate and symlink entries and asserts rejection; `:130` asserts expansion-limit rejection. `docs/taverna/ios-build.md:66` fixes 5 GiB/30 minutes for WebRTC, while `:73` and `:78` assert path/link confinement. Both real downloads/preparations passed their limits and hashes. | ✅ PASS |
| IOS-08 | A successful Debug scheme build identifies app, SimpleXChat framework, Notification Service Extension and Share Extension products. | `tools/taverna/ios_proof.py:21` defines the required four products; `:131`–`:152` asserts their executable identities, signatures and framework symbols. Each build receipt recorded exactly `SimpleX.app`, `SimpleXChat.framework`, `SimpleX NSE.appex` and `SimpleX SE.appex`. | ✅ PASS |
| IOS-09 | Executables and linked native code are arm64 and iOS Simulator platform, not merely arm64. | `tools/taverna/tests/test_ios_native.py:62` rejects macOS/iPhone/legacy or non-arm64 objects; `:73` asserts converted platform 7. `tools/taverna/tests/test_ios_proof.py:125` asserts real product Mach-O bytes yield `{architecture: arm64, platform: 7}` and rejects other combinations. Both strict proofs validated all four products and all 4,187 native objects. | ✅ PASS |
| IOS-10 | Before app main, remote IPv4/IPv6 are denied and loopback works in the app process; global VPN/firewall and iOS services remain outside the claim. | `tools/taverna/tests/test_ios_session.py:107` asserts PID/executable/`before_main`, both denial errnos and loopback; `tools/taverna/tests/test_ios_proof.py:136` rejects any invalid launch event. `apps/ios/Tests iOS/Tests_iOS.swift:190` repeats the same assertion in every launch. Both strict proofs recorded nine valid events; the control's unguarded negative case was rejected. | ✅ PASS |
| IOS-11 | With fresh app data, Get started is visible/hittable and enabled within 30 seconds. | `apps/ios/Tests iOS/Tests_iOS.swift:56` selects `Get started`; `:57`–`:60` assert existence, hittability, enabled state and elapsed time ≤30 seconds. Both real onboarding methods passed on fresh app data. | ✅ PASS |
| IOS-12 | After tapping Get started, Your profile is visible within 30 seconds and the test stops without submitting. | `apps/ios/Tests iOS/Tests_iOS.swift:67` taps Get started; `:68`–`:75` assert `Your profile` exists/is hittable within 30 seconds; the method ends after the evidence attachment at `:79`, with no form submission. Both real onboarding methods passed. | ✅ PASS |
| IOS-13 | The approved first-build profile runs all four required methods/assertions in English/portrait/light with zero failures/skips; the full matrix remains available and pending. | `tools/taverna/tests/test_ios_proof.py:37` asserts the exact profile dimensions and rejects filters; `:58`–`:64` asserts four required cases and zero failures/skips. `apps/ios/Tests iOS/Tests_iOSLaunchTests.swift:12` preserves matrix expansion outside first-build. Both proofs recorded 4/4 passed, 0 failed, 0 skipped, `first-build`, and `full_matrix: PENDING`. | ✅ PASS |
| IOS-14 | A failed/timed-out/missing mandatory stage, product or test cannot produce PASS and returns non-zero with the stage identified. | `tools/taverna/tests/test_ios_proof.py:98` asserts failures/timeouts for native/build/test are rejected; `:107` rejects missing stages/commands; `:112` rejects missing/wrong/external products; `:168` asserts a failed build starts no simulator steps. All six sensor mutants caused non-zero targeted tests. | ✅ PASS |
| IOS-15 | Retrying preserves prior evidence in a new attempt and never erases another session. | `tools/taverna/tests/test_ios_session.py:94` asserts an existing attempt cannot be overwritten, a second attempt differs and the first evidence remains; `:103` rejects attempt-path escape. A and B used separate attempt trees/UDIDs, and both ended by shutting down only their owned destination. | ✅ PASS |
| IOS-16 | Each attempt records source state/commit, input manifest, toolchain/runtime/destination, sanitized commands/exits, product hashes and test results. | `tools/taverna/ios_proof.py:290`–`:344` records build identity, clean state, manifest, settings, commands, products/hashes, Xcode/SDK and exit; `:347`–`:429` records the test destination/profile/commands/exits/device delta/shutdown. Both strict receipts contained the required fields and were accepted by `verify(..., strict=True)`. | ✅ PASS |
| IOS-17 | Two successful clean executions use the same commit/manifest/profile but distinct worktrees, caches and simulators. | `tools/taverna/tests/test_ios_proof.py:177` asserts matching commit/manifest and two runs while rejecting dirty, failed, mismatched or shared state; `:191` rejects symlink aliases to the same physical worktree. The real comparison returned exit 0 for author/verifier on the same SHA and manifest with distinct worktrees/UDIDs. | ✅ PASS |
| IOS-18 | An independent Verifier approves every AC on the final implementation SHA, including injected faults and successful CI on that SHA. | This report provides 20/20 evidence-or-zero rows; the discrimination sensor below killed 6/6 faults. GitHub Foundation runs `38968716168` and `38968724419` both concluded `success` with head SHA `6ea482bd4a1912d8eef52904d930c7f6c57bf746`. | ✅ PASS |
| IOS-19 | The consolidated report separates simulator app/UI, locally realized core and device signing/push; PASS is limited to proved scopes. | `tools/taverna/tests/test_ios_proof.py:147` asserts failure-state separation (`NOT PROVEN`, `NOT CHECKED`, `NOT RUN`, `BLOCKED`). Both strict receipts report `local_build_ui: PASS`, `native_core: LOCAL_SOURCE_REALIZED`, `device_signing_push: NOT RUN`, and distribution blocked by separate identity/assets/license gates. | ✅ PASS |
| IOS-20 | While asset/distribution permissions remain pending, binaries, screenshots and result bundles stay outside published repository files. | `.gitignore:91` ignores the entire per-worktree `.build/` evidence tree. `tools/taverna/tests/test_foundation.py:37` asserts release remains blocked and `:44` rejects inferring asset permission. Diff inspection found no PNG/JPEG/GIF/xcresult/archive/dylib/binary additions in the implementation range; raw evidence stayed local. | ✅ PASS |

**Status**: ✅ 20/20 criteria match precise spec outcomes; 0 uncovered criteria and 0 spec-precision gaps.

## Discrimination Sensor

Baseline and final `git status --porcelain --untracked-files=all` in the verifier worktree were both empty. Mutations were made only in file copies under the verifier's ignored `.build/sensor`, then discarded. No simulator was created for the sensor.

| Mutation | Target assertion | Outcome |
| --- | --- | --- |
| M1: accept iPhone platform 2 as simulator platform 7 | `tools/taverna/tests/test_ios_native.py:64` — incompatible platform must raise `ValueError` | ✅ Killed; expected exception was not raised, targeted test failed. |
| M2: disable payload/header/version preservation | `tools/taverna/tests/test_ios_native.py:77` — changed payload must raise `ValueError` | ✅ Killed; expected exception was not raised, targeted test failed. |
| M3: disable native bundle SHA-256 check | `tools/taverna/tests/test_ios_native.py:115` — wrong bundle hash must raise `ValueError` | ✅ Killed; expected exception was not raised, targeted test failed. |
| M4: allow an Xcode destination different from the owned UDID | `tools/taverna/tests/test_ios_session.py:44` — foreign destination must raise `ValueError` | ✅ Killed; expected exception was not raised, targeted test failed. |
| M5: stop enforcing light appearance in first-build | `tools/taverna/tests/test_ios_proof.py:46` — dark appearance must raise profile error | ✅ Killed; expected exception was not raised, targeted test failed. |
| M6: stop rejecting skipped tests in the result summary | `tools/taverna/tests/test_ios_proof.py:88` — `skippedTests=1` must raise `ValueError` | ✅ Killed; expected exception was not raised, targeted test failed. |

**Sensor depth**: critical-path expanded manual sensor  
**Result**: **6/6 killed, 0 survived — PASS**

## Independent Reproduction

| Proof | Source / manifest / profile | UI result | Isolation |
| --- | --- | --- | --- |
| Author (`ios-proof-author`) | SHA `6ea482bd4…`; manifest `ae89d70e…`; first-build | 4 passed, 0 failed, 0 skipped; 9 containment events | UDID `1ADD50F8-A951-49AB-A542-4A07093C5A48`; clean source; own worktree/cache |
| Verifier (`ios-proof-verifier`) | SHA `6ea482bd4…`; manifest `ae89d70e…`; first-build | 4 passed, 0 failed, 0 skipped; 9 containment events | UDID `F4069260-2B4C-4A61-B026-0357BA03D63E`; clean source; own worktree/cache |

`ios_proof.py compare` returned exit 0 and asserted equal SHA/manifest/profile plus distinct physical worktrees, DerivedData and UDIDs. Product equality was not required; each proof independently validated its own real products.

The verifier also inspected the three local B screenshots exported from the ignored xcresult. They show the English `Get started` control visibly enabled, then the light/portrait `Your profile` screen with an empty name field and disabled `Create profile` action. The PNGs and export manifest remain local under `.build` and are not published.

## Gate Check

| Gate | Result |
| --- | --- |
| `python3.12 -m unittest discover -s tools/taverna/tests -v` | ✅ 70 passed, 0 failed, 0 skipped |
| `python3.12 tools/taverna/check_foundation.py` | ✅ exit 0; Foundation scope only |
| `python3.12 -m compileall -q tools/taverna` | ✅ exit 0 |
| `git diff --check 8b2ffa71…6ea482bd4` | ✅ exit 0 |
| `validate_spec.py .specs/features/ios-first-build/spec.md` | ✅ 0 errors, 0 warnings |
| `validate_tasks.py .specs/features/ios-first-build/tasks.md` | ✅ 0 errors; 9 non-blocking granularity/documentation warnings already reconciled by the task plan |
| Full native/session/iOS/proof in author worktree | ✅ exit 0; clean source |
| Full native/session/iOS/proof in verifier worktree | ✅ exit 0; clean source |
| Independent reproduction comparison | ✅ exit 0 |
| GitHub Foundation push run `38968716168` | ✅ success on exact implementation SHA |
| GitHub Foundation PR run `38968724419` | ✅ success on exact implementation SHA |

- **Python test count before feature**: 28 (`git grep` at base SHA)
- **Python test count after feature**: 70
- **Delta**: +42 tests
- **iOS profile**: four logical/expanded executions, all passed, zero failed/skipped
- **Full matrix**: PENDING by explicit owner-approved scope; it is available and is not claimed as passed

## Code Quality and Scope

| Principle | Status |
| --- | --- |
| Minimum/surgical code | ✅ Three iOS source/test files plus local proof tooling; the app compatibility change is limited to the documented SwiftUI type alias. |
| No scope creep | ✅ No branding, protocol, cryptography, server, DNS, VPN, Apple account, APNs, physical-device or production change. |
| Existing patterns/tests preserved | ✅ Four required methods include the three inherited methods; full-matrix behavior remains available. |
| Fail closed | ✅ Missing/failed/timed-out stages, dirty source, foreign state, partial tests and wrong artifacts prevent PASS. |
| Payload/conjunction rule | ✅ Provenance fields, product fields, signing fields, containment fields and UI states are asserted by value, not merely by call occurrence. |
| Documented guidelines | ✅ `AGENTS.md`, `CONTRIBUTING.md`, `docs/taverna/environments.md`, `docs/taverna/ios-build.md`, TLC validate/sub-agent/lessons references. |
| Published evidence sanitized | ✅ No private paths, screenshots, binaries or result bundles are included in this report or implementation diff. |

## Edge Cases

- [x] macOS/iPhone/non-arm64 native inputs rejected despite architecture similarities.
- [x] unknown source, changed lock, wrong hashes and unsafe ZIP entries rejected.
- [x] standard SDK alias pointing outside owned storage, foreign UDID and external caches rejected.
- [x] missing/changed containment helper and invalid before-main events rejected.
- [x] xcodebuild success without required products/tests and partial/filtered/skipped tests rejected.
- [x] retries cannot overwrite an existing attempt or remove another session's evidence.
- [x] report keeps simulator build/UI, local core realization and device signing/push states separate.

## Requirement Traceability Update

| Requirement | Previous status | Verifier status |
| --- | --- | --- |
| IOS-01…IOS-20 | In Progress / In Tasks | ✅ Verified on implementation SHA `6ea482bd4a1912d8eef52904d930c7f6c57bf746` |

## Summary

**Overall**: ✅ Ready for the report-only closing commit and normal integration review.

**Spec-anchored check**: 20/20 ACs matched exact outcomes; no precision gaps.  
**Sensor**: 6/6 mutants killed.  
**Local gates**: 70 Python tests plus both clean full iOS proofs passed.  
**CI**: push and PR Foundation runs passed on the exact implementation SHA.  
**Proved scope**: Debug arm64 iOS Simulator build, locally realized pinned core, before-main app-process containment and first-build onboarding profile.  
**Remaining product gates**: full UI matrix, device signing/push, identity/assets licensing and distribution remain explicitly PENDING/NOT RUN/BLOCKED; they are outside this feature's approved PASS.

No lesson was recorded: validation produced no failed AC, surviving mutant, spec-precision gap, gate failure or `SPEC_DEVIATION` signal.
