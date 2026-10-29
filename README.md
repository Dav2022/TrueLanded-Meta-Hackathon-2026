# TrueLanded | Meta Global AI Developer Hackathon 2026

**PRIVATE competition implementation review — not approved for public release.**

This repository contains an independent, runnable **fictional** evidence-planning demonstration:
Evidence Spotlight (source-bound literals), Next Best Proof (deterministic request prioritization), Counterfactual Cascade (four hypothetical states), and optional Muse Spark 1.3 integration.

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
