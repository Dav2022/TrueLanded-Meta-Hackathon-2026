# DF-041 — Evaluation, traceability and restricted release matrix

**Source:** 2026-10-29 internal review, organizer Discord report supplied by owner,
and the official public event page (which confirms Indie track and Nov 4 deadline).
Discord claims about public repo creation and dependencies still require
authentication against original organizer posts / Official Rules.

| Judge claim / risk | Testable evidence in independent kit | Boundary | Gate |
|---|---|---|---|
| Repository started during contest | GitHub repository created 2026-10-29; source_commit in MANIFEST; NEW_WORK records original competitive commits | File dates/commits are not copyright clearance | CONDITIONAL |
| No commercial code dependency | Standalone archive includes its own integration modules; offline tests run without other source trees | IP licensing and author declarations need legal sign-off | TECH PASS; RIGHTS OPEN |
| Evidence Spotlight | Source lines + SHA-256 + 18 exact source literals | Issuer identity unauthenticated | TECH PASS (synthetic) |
| Next Best Proof | Deterministic REQ_RECONCILED_INVOICE to REQ_TECH_SHEET with tests | Not legal advice or automated communication | TECH PASS (synthetic) |
| Counterfactual Cascade | Quantity mismatch to value mismatch to technical gap across fictitious sources | Conditional simulation only, not trade ruling | TECH PASS |
| Meta participation | Meta transport and strict muse-spark-1.3 contract + opt-in CLI | Offline evaluation uses mock. DF039 real receipt stays private | PARTIAL |
| Independent execution | RUN_JUDGE_CHECKS.py; source-only bundle, Python stdlib; both OS targets | Third-party genuine inference needs their own authorized token | PASS (offline) |
| No commercial/IP/private leakage | Git-object allowlist; no viewer historical summary, secrets or DF039 receipts; ZIP file audit | Need human rights review before publication | TECH PASS; RIGHTS OPEN |
| Security | Fail-closed quote checking, hardcoded localhost viewer, no write endpoint, no replay credentials | Self-issued hashes are not external attestation | TECH PASS |
| Submit repository/video/track | Repo remains private; video frozen; event form not submitted here | Rights and Official Rules approval required | BLOCKED |

**Public competition deadline:** Nov 4, 2026 9:00 p.m. Eastern = Nov 4 8:00 p.m. Costa Rica.
**Sources:** https://cerebralvalley.ai/e/meta-ai-developer-hackathon ;
https://dev.meta.ai/events/global-hackathon .

## Decision

**GO:** independent private evaluation package, security tests, offline clone,
provenance matrix, organizer rule reconciliation.
**NO-GO:** public release, selecting an unsupported license, publishing original
model receipts, providing client records, claiming a signed provider attestation,
or claiming an offline mock is fresh Meta inference.

The kit can be shared only after an explicit separate determination of
licensing, legal rights, event rules and user authorization.

## DF-043 independent visual walkthrough
The allowlisted evaluation ZIP now includes `docs/` for a responsive static experience that can be deployed later via GitHub Pages. This is an offline **synthetic** example with browser SHA checks and clearly marked zero Meta calls. Publishing it requires the same owner approval/licensing gates as the repository.
