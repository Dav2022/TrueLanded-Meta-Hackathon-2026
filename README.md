# TrueLanded | Meta Global AI Developer Hackathon 2026

**PRIVATE competition implementation review — not approved for public release.**

This repository contains an independent, runnable **fictional** evidence-planning demonstration:
Evidence Spotlight (source-bound literals), Next Best Proof (deterministic request prioritization), Counterfactual Cascade (three hypothetical document states), and optional Muse Spark 1.3 integration.

## Verify offline
Python 3.11+ required, no additional Python dependencies. Run:

```bash
python -B RUN_OFFLINE_TESTS.py
```

The offline test uses synthetic cases, mock model responses, and source-bound historical owner-derived replay. **It does not make a real Muse call.** An optional live mode is explicitly opt-in and is **not authorized for use** until owner approves an individual API request and latest terms and endpoint are verified. Never put tokens or provider receipts in Git.

The evidence hashes are author-computed integrity checks, **not Meta signatures** or issuer authentication. All supplier and customs decisions remain subject to human review. No actual customs-clearance claim is made.

## Scope and terms
See `NEW_WORK.md` for per-file provenance and `RELEASE_HOLD.md` for outstanding rights and contest gates. This repository is not licensed or authorized for redistribution. The pre-event commercial TrueLanded source and customer documents are **excluded**.

## Local UI
`cd viewer && python -B df023m_server.py --port 18970`; open `http://127.0.0.1:18970/`. Local-only review surface, not an internet deployment.

## DF-041 independent evaluator (PRIVATE)
The audited kit generator is `judge_kit/BUILD_JUDGE_KIT.py`. It builds a commit-pinned, allowlisted ZIP outside this repository, with SHA-256 manifest and its own `RUN_JUDGE_CHECKS.py`. The kit deliberately excludes original DF039 receipts and the historical viewer. It does not authorize publication. See `judge_kit/JUDGES_README.md` and `judge_kit/DF041_RELEASE_MATRIX.md`.

## DF-042 publication and eligibility (private review)
Read `docs/competition/DF042_RULES_EVIDENCE_MATRIX.md`, `DF042_IP_RIGHTS_AND_HISTORY_REVIEW.md` and `DF042_SUBMISSION_READINESS.md`. Offline gate: `python -B scripts/df042_release_preflight.py`. This checks selected release blockers but never grants publication rights. The Guide requires a public repo and an accessible three-minute video; both remain **NO-GO**. A clean Judge Kit ZIP does not erase old Git history.
