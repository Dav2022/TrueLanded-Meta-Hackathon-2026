# TrueLanded — Submission overview for judges

**Event:** Meta Global AI Developer Hackathon 2026
**Track:** Indie Developer
**Theme:** Build for Your World
**Category:** International trade / documentary evidence verification
**Author:** David Soto Leon

## Executive overview
International-trade documents routinely conflict: an invoice and a packing record can disagree on quantity while other legally material information remains missing. Extracting plausible fields is not enough. A system must connect every factual assertion to a reproducible source, reject unsupported substitutions and expose which additional document would change the decision.

**TrueLanded is a competition-only synthetic, evidence-to-decision demonstrator** that pairs historically recorded Meta Muse Spark candidate extraction with deterministic source verification, missing-proof prioritization and a fail-closed adversarial lab. It makes the limits of the evidence visible to a human reviewer rather than inventing authority to file customs documents.

## Three judging links
1. [Watch 2:47 demo film (1080p)](https://dav2022.github.io/TrueLanded-Meta-Hackathon-2026/watch.html)
2. [Try the interactive synthetic documentary demo](https://dav2022.github.io/TrueLanded-Meta-Hackathon-2026/)
3. [Replay 30 fabricated adversarial cases](https://dav2022.github.io/TrueLanded-Meta-Hackathon-2026/adjudication.html)

**Public contest source:** [TrueLanded repository](https://github.com/Dav2022/TrueLanded-Meta-Hackathon-2026).

## Clear competition work boundary
**Pre-existing:** The separate commercial TrueLanded concept and proprietary project are not submitted.

**Built for the hackathon:** Isolated synthetic evidence workflow, source-bound literal verification, bounded counterfactual calculator, source-integrity gating, missing-proof recommendations, browser demonstration and adversarial lab with precomputed synthetic verdicts. Only the public contest-specific code is released under MIT.

## Use of Meta tools — precise provenance
An authorized, separately recorded historical Meta Muse Spark 1.3 call proposed candidate documentary fields. An independent local verifier evaluated 18 source literals against its corresponding fictional document pack. Ten additional Muse Code High evaluations examined synthetic cases separately. The 18 literal checks are **not** the same population as a distinct earlier six-observation candidate extraction.

The public browser does not call Meta's API live. The public repository does not contain raw model outputs, credentials or real customer records. This separation protects private data and makes deterministic local evidence checks reproducible. The documented Meta usage should be judged as recorded development/evaluation, **not as a live API integration**.

## Decision-oriented product features
- **Evidence Spotlight:** source literal → exact trace → integrity check.
- **Next Best Proof:** recommends a reconciled invoice when primary documents disagree; sends nothing automatically.
- **Counterfactual Cascade:** adjusting quantity from 31 to 28 produces a bounded synthetic hypothetical value of USD 221.76 (28 × 7.92). It does not certify customs valuation; missing technical specifications remain unresolved.
- **Tampering defense:** independently pinned evidence-index integrity blocks altered source substitution even if the source hash is recomputed. Hash matching cannot establish issuer authenticity.
- **Adjudication Lab:** 30 fabricated attack inputs with reproducible **offline precomputed Python outcomes**. Case T04 excludes unsupported invoice quantities from the relevant comparison; case T20 rejects forged approval; case T12 blocks unsupported conclusions from inconsistent primary records. The browser does not run Python inference or claim a universal security benchmark.

## Reproduction (local, Python 3.11+, Node 22+ optional)
```sh
python -B RUN_PUBLIC_TESTS.py
node --test tests/test_df071_counterfactual.cjs tests/test_df071_browser_contract.cjs
python -B scripts/df073_build_adjudication.py --check
cd docs && python -m http.server 18973 --bind 127.0.0.1
```
Visit http://127.0.0.1:18973/ (WebCrypto requires a secure context). The local server hosts a static demonstration and makes no paid API requests.

**Verified on Nov 2, 2026:** 56/56 Python tests PASS, 10/10 Node tests PASS, 30 synthetic attack cases reproduced. Public repository, interactive site and lab returned HTTP 200.

## Limits and human controls
All datasets and documents shown are fictional. A source hash binds bytes, not identity, supplier legitimacy, or regulatory compliance. A bounded arithmetic hypothesis is not an official customs decision. Human reviewers determine legal, evidentiary and trade decisions; the demonstrator makes no transmission or regulatory filing.

**Audiovisual rights:** The film is provided for judging by the owner. It is not MIT-licensed; see [AUDIOVISUAL_RIGHTS.md](AUDIOVISUAL_RIGHTS.md).

## The take-away
TrueLanded changes the question from **“What does AI think this document says?”** to **“What can the evidence actually support — and what must a person verify next?”**
