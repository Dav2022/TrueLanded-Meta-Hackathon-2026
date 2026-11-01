# DF-071 — Meta Hackathon portal submission copy
**PRIVATE DRAFT · NOT SUBMITTED · NO RIGHTS OR PUBLICATION APPROVAL**

## Fields based on the Participant Guide

**Project title:** TrueLanded — Evidence-to-Decision Engine

**Track:** Indie Developer

**Theme:** Build for Your World

**Tagline:** The document changed. The decision should too.

**One-line description (153 characters):** TrueLanded turns contradictory trade documents into source-checked evidence, prioritized proof requests, and explainable what-if decisions using Meta Muse Spark.

### Project description (for the portal)

An invoice says 31 units while the packing record says 28. The next document arrives, but instead of resolving the case, it exposes a different inconsistency. In real international trade, the problem is not merely extracting text — it is identifying which missing proof will most effectively reduce uncertainty *before a human acts*.

TrueLanded is an evidence-to-decision demonstrator built for the Meta Global AI Developer Hackathon 2026. **Evidence Spotlight** checks candidate fields against exact synthetic source literals. **Next Best Proof** ranks which additional documentary evidence may address the unresolved obligations, while clearly identifying assumptions. **Counterfactual Cascade** demonstrates how a proposed revised document can reconcile one contradiction yet reveal another.

In a separate authorized historical Meta Model API experiment, Muse Spark 1.3 proposed fields from newly generated fictional trade documents. The owner-recorded request completed with HTTP 200; TrueLanded's independent source check matched 18/18 literals. The browser experience is deliberately offline and uses a *clearly identified local test double*, never a fabricated live Muse response. All discrepancy checks, evidence ranking, hypothetical arithmetic and safety gating are our deterministic code.

The interactive judge page does more than replay three predefined revisions: change a fictional invoice quantity or line total and it recalculates open issues, newly exposed or conditionally reconciled discrepancies, and the next proof request. Source-index SHA-256 checks are validated locally; tampered evidence is rejected. An independent ZIP-based Judge Kit reproduces the tests with Python 3.11 and optional Node 22, without customer records, paid inference or API credentials.

**TrueLanded is not a customs ruling.** It does not certify document issuers, independently verify commercial truth, authorize declarations, contact suppliers or replace professional responsibility. It demonstrates a safer way to direct the *next question* and keep every recommendation challengeable.

### What was built during the hackathon (explicit provenance)
- Competition-only source-bound candidate checking and documentary verification.
- Deterministic proof-selection frontier, competing assumptions and hypothetical obligation changes.
- Synthetic evaluation records and adversarial cases; rejection of unsupported source changes.
- Accessible static juror walkthrough and bounded arithmetic what-if, with explicit Meta provenance.
- Clean, independently verifiable Judge Kit and CI tests on Windows and Ubuntu.
- See `NEW_WORK.md` and commit provenance for exact distinctions from pre-existing commercial TrueLanded.

### Meta use (precise statement)
**Model:** `muse-spark-1.3` via Meta Model API.  
**Role:** propose textual candidate fields (untrusted inputs).  
**Owner-recorded source-bound experiment:** HTTP 200, 18/18 exact literal matches on three synthetic source records in DF-039.  
**Browser:** offline synthetic fixture; zero live model requests.  
**Safety boundary:** claims verified by deterministic source checks; no model may create legal clearance or authenticate document issuers.  
**Do not mislabel low reasoning-effort historical receipts as High inference.**

### How to evaluate
1. Open the website and select the packing confirmation, invoice revision A and invoice revision B.
2. Observe how the next requested evidence changes from a reconciled invoice to a technical specification.
3. In the what-if panel, set quantity `28` and line total `221.76`; inspect the recalculation. Then try quantity `31` and `245.52`.
4. Tamper with fictional evidence in a local test copy to see the display refuse source-integrity failures.
5. Clone the source or extract the separately generated Judge Kit. Run Python 3.11 tests; run optional Node 22 browser tests. All default verification is offline.

## Mandatory real submission information — NOT YET POPULATED
- [ ] **Public source repository:** URL; verify anonymous access and cleaned history.
- [ ] **Public HTTPS web demo:** URL; verify mobile/desktop and anonymous access.
- [ ] **Final 3-minute video:** URL; verify playback, exact duration and legibility without login.
- [ ] **Contributor list:** user-confirmed actual eligible participants, no invented teammates.
- [ ] **License & rights:** user-approved license covering only competition module; audit third-party code.
- [ ] **Date/time and portal receipt:** actual confirmation from Cerebral Valley.
- [ ] **Release commit SHA:** hash of cleaned, final publicly accessible commit.

**Hard stop:** do not mark this submitted and do not provide fake placeholder links to the portal. The deadline is Wed Nov 4, 2026, 9 PM Eastern = 8 PM Costa Rica.
