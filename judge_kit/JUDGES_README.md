# TrueLanded DF-041 — Independent Judge Evaluation Kit

**Status: prepared for private technical review, NOT approved for public distribution.**
**Category:** Indie Developer · Meta Global AI Developer Hackathon 2026.
**Runtime:** Python 3.11+ standard library and a modern browser; no packages to install.

## A. Reproduce without credentials, Internet or private materials

Extract this ZIP into an empty folder, open a terminal there, then run:

Windows: 'py -3.11 -B RUN_JUDGE_CHECKS.py'
Linux/macOS: 'python3 -B RUN_JUDGE_CHECKS.py'

The check verifies every allowlisted byte using the **owner-issued** SHA-256 manifest, then
runs the synthetic source, deterministic planner, security, model-response-shape,
and local HTTP tests. **No Meta inference occurs during this test.**
Expected success marker: DF041_INDEPENDENT_OFFLINE_ACCEPTANCE_PASS_MODEL_CALLS_0.

To inspect the three-stage simulated demonstration:

'python3 -B demo/server.py --port 18971'

On Windows, 'py -3.11 -B demo/server.py --port 18971' also works.
Open http://127.0.0.1:18971/ **on that computer**. It is read-only and
local; SIMULATED_OFFLINE_NOT_META_INFERENCE is always displayed.

## B. Evaluate the functionality

1. **Evidence Spotlight** — the fictional source lines and their SHA-256 anchors.
2. **Next Best Proof** — ranks what evidence to request after each source change.
3. **Counterfactual Cascade** — a fictional packing revision, inconsistent invoice
   and corrected invoice progressively change the unresolved obligations.

The local mock is a test double with the expected Muse Spark 1.3 API response
contract. TrueLanded checks exact quoted lines, rejects fabricated quotes and
recomputes the proof selection in independent deterministic code. It **does not
claim** that the mock is a Meta response.

## C. Optional genuine Meta execution (not needed for offline evaluation)

If you have **your own authorized Meta Model API access**, you can inspect
'integration/muse_cli.py' and the private read-only replay
'review/server.py'. That is an explicit, potentially billable, one-attempt
workflow. It requires the operator to provide their own MODEL_API_KEY,
create a private directory **outside this bundle** and authorize each operation.
Never add any credential or captured response to this ZIP or a public repo.
An offline replay cannot establish the provider's origin by itself.

The project owner previously performed one authorized request to
'muse-spark-1.3' yielding HTTP 200 and 18/18 source-literal matches.
The original response body and local receipts are **not included** in this kit.
Without a separate authorized receipt, 'review/server.py' must fail closed.

## D. What this DOES NOT prove

- No actual trade clearance, tax classification, issuer authenticity, customer PDFs
  or regulatory decision is verified in this fictional demonstration.
- Hashes and this manifest are **self-issued**, not signatures by Meta or suppliers.
- The offline mock does not authenticate Muse inference.
- A reviewer without their own Meta credentials cannot reproduce the *live*
  model execution merely from the ZIP.
- Access and redistribution rights, the final public license and official rules
  require separate human review. This private bundle is not a publication license.

See NEW_WORK.md for provenance and RELEASE_HOLD.md for outstanding rights.
MANIFEST.json names the exact source commit and every included byte.
