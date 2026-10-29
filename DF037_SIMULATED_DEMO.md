# DF-037 — Interactive source-bound simulated demonstration

**Private / mock only. NOT a real Meta inference.** Python 3.11+, stdlib only.

Run `python -B RUN_OFFLINE_TESTS.py` (96 tests). Start the localhost read-only UI: `python -B demo/server.py --port 18971`; open `http://127.0.0.1:18971/`.

API `GET /api/mock-scene` generates a deterministic, seeded, fictitious three-document pack, applies a locally generated test-double reply shaped like Meta's `muse-spark-1.3` Chat Completions response, and verifies all 18 source literals. TrueLanded's deterministic engine produces the proof ranking and the counterfactual transitions (quantity mismatch → value mismatch → technical sheet still needed). The result always includes `SIMULATED_OFFLINE_NOT_META_INFERENCE`, `api_calls=0` and `meta_inference_proven=false`.

The independent viewer displays Evidence Spotlight, Next Best Proof and Counterfactual Cascade using `textContent` only (no dynamic HTML insertion), refuses foreign Origin/Host, query strings and state-mutating methods, and fails closed on malformed source output. This demonstration never authenticates a supplier or issues clearance. No API key is used, and no model provider output is invented as genuine.

**Remaining DF-037 live acceptance:** an owner-approved genuine Muse attempt, model access confirmation and a separate read-only source-verified bridge from that private captured result to an evaluator. The private capture MUST be explicitly marked live only when the request/response route is independently evidenced; current mock cannot satisfy this. Hosting/public video remain withheld until release gates close.