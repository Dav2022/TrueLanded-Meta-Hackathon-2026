# DF-036 | Meta Muse participation and evidence readiness

**Status: PRIVATE REVIEW.** Running offline mock tests does NOT demonstrate live inference. No live API call has been authorized in this phase.

## Meta API verified against official documentation (2026-10-29)
- Base `https://api.meta.ai/v1` and Chat Completions `POST /v1/chat/completions`.
- Model `muse-spark-1.3` (Standard) and Bearer environment `MODEL_API_KEY`.
- Model listing `GET /v1/models`; unauthenticated service status `GET /v1/status`.
- Reference: https://dev.meta.ai/docs/api-reference and https://dev.meta.ai/docs/authentication.
- These are endpoint specifications, NOT proof that THIS account's API works at a given location.

## Reproducible offline acceptance
`python -B RUN_OFFLINE_TESTS.py` — 88 tests after DF036. Includes 8 independent anti-spoofing tests.

## Three distinct evidence modes
1. **Mock** — deterministic offline fixture, `meta_inference_proven=false`; useful ONLY for testing UI and verifier.
2. **Historical replay** — owner-derived secondary account of prior Muse use, `meta_inference_proven=false` for THIS execution; no provider-signed receipt.
3. **Private capture** — requires one-shot lock + source pack + response body + metadata/review. `df036_demo_evidence_gate.inspect_attempt` checks local chain. **Never claims authenticated provider origin** from a self-reported model field or local file hash. An independent trusted transport observation/credential-valid invocation still must be established.

## Human-authorized live procedure — NOT executed
- Owner verifies current Meta terms, personal regional authorization and enough account credits.
- Verify API account `/v1/models`, network reliability, timeout and availability on EXACT judge-demo host, without logging secrets.
- Create a NEW private directory outside Git, ensure a valid `MODEL_API_KEY` environment variable without printing it.
- Owner explicitly authorizes a SINGLE potentially billable request, then invokes:

`python -B integration/muse_cli.py --mode execute-live --private-dir <PRIVATE_PATH_OUTSIDE_REPO> --i-authorize-one-billable-call --acknowledge-model-output-untrusted`

No retry in same directory, even for 401/404/429/timeout. Review private hashes, status and self-reported usage without leaking raw outputs or credentials. Do not claim signed Meta attestation unless separately available. Do NOT run this command as CI or a jury-facing default.

## Exact demo differentiation
- **Muse only**: proposed source literal candidates. A provider output is untrusted; wrong/missing source lines are rejected.
- **Evidence Spotlight**: deterministic, source-bound quotations and hashes; does not authenticate document issuer.
- **Next Best Proof**: TrueLanded deterministic proof-request ranking; NOT model-generated legal advice.
- **Counterfactual Cascade**: source revisions change quantity/value/technical obligations, computed deterministically; all hypothetical and subject to human verification.

## Stop conditions (release gate)
- Current user session lacked `MODEL_API_KEY` on 2026-10-29; no live request/metadata or `/v1/models` credential test done.
- The viewer still uses an older historical owner-derived replay; it does NOT dynamically display a fresh result of `muse_cli` and must not be described as if it does.
- Live account verification, actual approved one-shot request, end-to-end *viewer* consumption of that response, licensing/IP and official organizer permissions all remain OPEN.
- No public repository release or video production before Technical Complete.