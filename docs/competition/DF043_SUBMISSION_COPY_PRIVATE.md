# DF-043 — Submission copy candidate (private; not filed)

**Date:** 2026-10-29, Costa Rica. **Source:** Meta Participant Guide + DF-035–DF-043 verified engineering records. This text is a draft for the portal, not an assertion of formal eligibility.

## Track / Theme
- **Track:** Indie Developer.
- **Theme:** Build for Your World.
- **Title:** TrueLanded — Evidence-to-Decision Engine.
- **Tagline:** The document changed. The decision should too.

## One-sentence description
TrueLanded turns conflicting international-trade documents into verifiable evidence matches, prioritized proof requests and traceable what-if decisions using Meta Muse Spark 1.3 candidate extraction.

## Problem
Importers and trade-compliance operators face conflicting invoice, packing and product-technical evidence. Resolving the uncertainty requires knowing **which missing document to obtain next**, not another unconstrained chatbot answer. A quantity conflict can disappear after a corrected record, only to expose a value discrepancy or a technical-specification gap.

## What we built during this hackathon
Three integrated capabilities created for the competition: **Evidence Spotlight** (exact source literals checked against original text and hashes), **Next Best Proof** (deterministic ranking of missing evidence), and **Counterfactual Cascade** (how new fictional documents change unresolved obligations). A static browser walkthrough, a localhost application, a private-capture reviewer and a standard-library test harness make the results auditable.

## Where Meta's model matters
Muse Spark 1.3 proposes literal fields from a newly generated, fictional three-document packet through Meta Model API. In the owner-authorized test **DF-039**, the authenticated request returned **HTTP 200** and the source-matching engine verified **18/18 literal fields**. The model is an untrusted extractor; TrueLanded independently validates and computes all proof requests and counterfactual deltas. No model output grants customs clearance.

## What judges can reproduce
- Browser walkthrough with three document revisions, offline, without secrets.
- Python stdlib verification of all allowlisted package files, deterministic source logic and adversarial failure cases.
- Optional one-shot Muse execution with **the evaluator's own authorized Meta key**, clearly separated from default offline verification.
- Code and provenance inventory in `NEW_WORK.md`.

**Do not claim** that the static site or test suite makes a live Meta call. The original DF-039 capture remains private, without a provider-signed attestation.

## Why it matters
Trade operators can see **what changed, why it changed, what evidence to request and what remains unresolved**. Source-bound claims help reduce unreviewable model assertions. The example is synthetic and preliminary; no performance, time-saving or regulatory impact claim has been measured on real shipments.

## Suggested submission components (not yet sent)
- **Repository URL:** pending owner release approval and anonymous-access verification.
- **Browser demo URL:** pending GitHub Pages/public hosting from `/docs` on released repository.
- **Three-minute video URL:** pending production and public/unlisted accessibility verification.
- **Team contributor names:** pending owner confirmation.
- **License and rights:** pending owner sign-off.
- **Original accepted Official Rules:** pending document examination.
- **Meta-use notes:** `integration/muse_cli.py`, DF-039 summarized result, source gate, fail-closed behavior.

## Source-limited note
The Participant Guide §4 explicitly requires identifying new work; §7 requires a public repository, accessible video and contributor list. The official event page confirms the submission cutoff on Nov 4 at 21:00 Eastern (Nov 4 20:00 Costa Rica). Other fields must be checked in the live portal instead of invented.
