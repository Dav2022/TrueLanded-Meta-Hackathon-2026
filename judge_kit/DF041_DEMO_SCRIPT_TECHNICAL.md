# DF-041 — Technical narration outline for a potential 3-minute jury review

This is a **technical outline, not an authorized final competition video**.
Use only after Technical Complete and an explicit video GO.

**0:00–0:25 — Why it matters**: a fictional shipment contains an unreconciled
quantity. A defensible trade decision requires evidence, not a fluent guess.

**0:25–1:00 — Evidence Spotlight**: click stage 1, show the exact source line and
source SHA-256. Explain that LLM extraction is *candidate text*, while the source
gate is deterministic and rejects mismatches. No issuer-authentication claim.

**1:00–1:40 — Next Best Proof**: show that the top request is a reconciled invoice.
The app has not sent the request automatically; human approval is mandatory.

**1:40–2:20 — Counterfactual Cascade**: stage 2 resolves quantity but exposes
value inconsistency; stage 3 resolves value conditionally, leaving a technical
specification gap. Recommendation becomes REQ_TECH_SHEET.

**2:20–2:45 — Meta's actual role**: describe the separately captured DF039
one-shot Muse Spark 1.3 text extraction, HTTP 200 and 18 source matches, but do
not show confidential receipt, do not claim a signature and do not imply the
offline mock currently running calls Meta. A genuine run requires authorized API.

**2:45–3:00 — Verify it**: highlight that a reviewer can run the independent
stdlib test command with no private dependencies. End on the human-review
safeguard and provenance / future production limitations.

**Success criteria:** honest distinction between simulated evaluation, recorded
owner-authorized Meta inference, and deterministic legal/compliance heuristics.
