# LESSONS - auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Specify/Design)

Corroborated across multiple features. Safe to apply as guidance.

_none_

## Candidates (under observation - do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-001 - Derive every fixture output path from the selected run identifier and prove it in a fresh worktree
- signal: `gate_fail` · recurrence: 1 feature(s) · scope: `tools/taverna/access_proof` · harmful: 0
- features: invitation-only
- evidence: .specs/features/invitation-only/access-proof-validation.md#ciclo-1 (tools/taverna/access_proof)
- last seen: 2026-10-16T23:24:16Z

### L-002 - Record sanitized authorization decisions and backend-open failures before treating a TLS EOF as causal evidence
- signal: `gate_fail` · recurrence: 1 feature(s) · scope: `tools/taverna/native_access_tests` · harmful: 0
- features: invitation-only
- evidence: .specs/features/invitation-only/native-review.md#t2-fail-no-gate-causa-inconclusive (tools/taverna/native_access_tests)
- last seen: 2026-10-17T00:00:37Z

### L-003 - Assert every fail-closed configuration field against an independent literal or contract, never against a second call to its producer
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `apps/ios/SimpleXChat/Taverna` · harmful: 0
- features: invitation-only
- evidence: .specs/features/invitation-only/native-startup-review.md:M6 (apps/ios/SimpleXChat/Taverna)
- last seen: 2026-10-17T00:26:03Z

### L-004 - Resolve system share-sheet actions from observed descendant accessibility elements, then prove repeated invocation before using them as a transport gate
- signal: `gate_fail` · recurrence: 1 feature(s) · scope: `apps/ios/Tests iOS` · harmful: 0
- features: invitation-only
- evidence: .specs/features/invitation-only/share-resume-review.md#instabilidade-observada (apps/ios/Tests iOS)
- last seen: 2026-10-18T23:35:28Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
