# DF-071 — 180-second jury video: private script and verification sheet
**Status:** production draft; NOT a recorded, approved, uploaded or submitted video.  
**Track:** Indie Developer — Build for Your World.  
**Screen:** primary `docs/` UI on verified local server; no customer files, credentials or real private provider receipts.  
**Narration:** English, neutral professional; illustrative synthetic content clearly labeled.

## Timed storyboard and narration (TARGET 180 s)

### 0:00–0:18 — Problem / juror hook (18 s)
**Screen:** TrueLanded hero; quantity mismatch text.
**Voice:** "An invoice says one quantity. A packing record says another. For an importer, one unsupported assumption can stall the entire customs preparation process. Most AI demos answer questions. TrueLanded asks a different one: which evidence must we obtain before anyone decides?"
**Overlay:** `FICTIONAL DEMO — NOT A CUSTOMS DETERMINATION`.

### 0:18–0:43 — Evidence Spotlight (25 s)
**Screen:** Open the source panel; emphasize quantity and invoice lines, source hash and verification status.
**Voice:** "First, Evidence Spotlight. Meta Muse Spark 1.3 can propose text fields from documents, but its candidates are not trusted automatically. Our code checks each literal against the original synthetic source. If the source does not match, the result is rejected. These hashes are local integrity checks, not supplier signatures."
**Overlay:** `MODEL PROPOSES → SOURCE VERIFIES`.

### 0:43–1:08 — Next Best Proof (25 s)
**Screen:** Next Best Proof and open obligations.
**Voice:** "The system identifies the open documentary contradictions and ranks what proof to request next. Here, the initial fictional evidence points to a reconciled invoice. This is a recommendation only. TrueLanded sends no request, does not classify the product, and does not authorize a customs filing."
**Overlay:** `HUMAN REVIEW REQUIRED`.

### 1:08–1:37 — Counterfactual Cascade (29 s)
**Screen:** Click Invoice revision A, show line total USD 235.06; click revision B, show USD 221.76 and updated proof.
**Voice:** "Watch the cascade. A revised invoice removes the quantity conflict, but introduces an arithmetic inconsistency. Twenty-eight units at seven dollars and ninety-two cents should total two hundred twenty-one dollars and seventy-six cents, not two hundred thirty-five dollars and six cents. A second revision fixes the math. The next missing item is now the technical specification. One correction changed the next decision."
**Overlay:** `28 × $7.92 = $221.76`.

### 1:37–2:04 — Recalculation is authentic, not a visual trick (27 s)
**Screen:** What-if box; change the fictional line total from `235.06` to `221.76`, press Recalculate; optionally change quantity to `31` and value to `245.52`. Restore.
**Voice:** "This is not a prerecorded switch between screens. I can change a fictional invoice amount and the browser recalculates its arithmetic, open obligations, and next proof using deterministic rules. The displayed original source remains unchanged. This bounded, local scenario uses no model calls. A reviewer can inspect both the source and the rule that produced the recommendation."
**Overlay:** `BOUNDED FICTIONAL HYPOTHESIS · ZERO META CALLS`.

### 2:04–2:27 — Show authentic Meta integration, truthfully (23 s)
**Screen:** sanitized local evidence summary: model `muse-spark-1.3`; historical owner-authorized API result: `HTTP 200`, `18/18 source literal matches`; optional code contract view. Never show private receipts/token/paths.
**Voice:** "Where does Meta AI actually contribute? Muse Spark performs candidate extraction. In a separate authorized Model API experiment, the request succeeded, and TrueLanded independently matched eighteen source literals. The browser demo you just saw is intentionally offline. We do not call a replay a fresh Meta inference or treat model output as evidence of legal authority."
**Overlay:** `REAL HISTORICAL META RUN — SEPARATE FROM OFFLINE BROWSER`.

### 2:27–2:49 — Reproducibility / fail closed (22 s)
**Screen:** fresh clean-clone terminal commands, verified green results (only after an actually green CI run and local acceptance), then an intentionally invalid source shown as rejected.
**Voice:** "Every technical claim can be challenged. Independent tests exercise synthetic document changes, invalid amounts and tampered source content. When source evidence fails verification, the interface refuses to recommend. Evaluators can reproduce the offline checks with Python and Node, without our credentials or billable API usage."
**Overlay:** `FAIL CLOSED · AUDITABLE · HUMAN-GATED`.

### 2:49–3:00 — Close / memorable line (11 s)
**Screen:** clean TrueLanded wordmark and evidence-to-decision narrative.
**Voice:** "TrueLanded does not replace customs judgment. It makes the next question defensible. From trade evidence to better decisions. Evidence first; action when justified."
**Overlay:** `TRUELANDED | EVIDENCE → DECISION`.

## Verification / publication gates
- Video duration is **180 seconds or less**; measure the exported media, not the storyboard estimate.
- Record the **actual candidate submitted** and capture only interactions that work.
- 1080p minimum, source literals legible, no fake API call, original copyrighted music or no soundtrack.
- All needed subtitles accurately match narration, human-readable, 16:9.
- If the "authentic Meta run" slide lacks owner-cleared evidence, speak of the verified historical result but **do not show fabricated certification**.
- Do not display raw DF-039 receipt, bearer key, response IDs, local username, filesystem locations or client records.
- Verify the final video from an **unauthenticated viewer**, with playback/audio.
- No video file or hosted URL is currently provided by this document.

**Deadline:** Wednesday, 4 November 2026 21:00 ET = 20:00 Costa Rica.
