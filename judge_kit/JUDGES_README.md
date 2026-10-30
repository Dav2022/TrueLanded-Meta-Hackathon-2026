# TrueLanded | Evidence-to-Decision Engine

> **The document changed. The decision should too.**

**Meta Global AI Developer Hackathon 2026 · Indie Developer · Build for Your World**

TrueLanded helps international-trade professionals answer a practical question: **when commercial documents disagree, which evidence should they request next—and what will change when it arrives?**

Rather than presenting an LLM's output as a customs verdict, TrueLanded separates **candidate extraction with Meta Muse Spark 1.3** from **deterministic verification, evidence planning and human review**.

**Release status:** private technical evaluation candidate. Publication rights and a compatible code license remain subject to the owner's explicit approval.

## The three differentiators

| Capability | What you can observe | What it does **not** claim |
| --- | --- | --- |
| **Evidence Spotlight** | Exact fictional invoice/packing lines, source SHA-256 anchors and fail-closed literal verification | Authentication of a document issuer |
| **Next Best Proof** | The highest-ranked request for missing or contradictory documentary evidence | A binding customs or tariff determination |
| **Counterfactual Cascade** | How a revised document resolves one discrepancy while exposing another | That a real supplier accepted a correction |

The demo shows three hypothetical source updates: a packing reconciliation, an invoice that introduces a value discrepancy, and a corrected invoice that leaves the technical specification outstanding.

## See the interactive experience

The **static browser demo** lives in `docs/`. It runs entirely on the viewer's machine with **no Meta key, server application, Python package installation or billed model call**. From an extracted folder:

```powershell
# Windows
cd docs
py -3.11 -B -m http.server 18973 --bind 127.0.0.1
```

Or on Linux/macOS: `cd docs && python3 -m http.server 18973 --bind 127.0.0.1`.

Open **http://127.0.0.1:18973/**. Select each of the three stages to inspect the source, next documentary proof and newly opened/resolved obligations. The browser hashes every fictional source before displaying its results. It refuses display when the checks fail.

If a public GitHub Pages site is activated later from the `/docs` directory, the same static experience can run over HTTPS without server-side secrets. **No deployment or publication has been authorized in the current private release.**

## Reproduce the engineering independently

Requirements: **Python 3.11+ standard library**; no external Python dependencies and no credentials.

```bash
python3 -B RUN_JUDGE_CHECKS.py
```

On Windows: `py -3.11 -B RUN_JUDGE_CHECKS.py`.

The runner first verifies **every included file against a self-issued SHA-256 manifest**, then runs source-matching, independent-oracle, deterministic decision, local HTTP and security tests, including the static-site fixture generator. It makes **zero provider calls**. The manifest is not a signature by Meta.

To verify that the static data was generated from TrueLanded's actual deterministic code:

```bash
python3 -B scripts/df043_build_static_site.py --check
```

A second local server-style simulated demo is also available: `python3 -B demo/server.py --port 18971`.

## Where Meta AI actually participates

- **Live authenticated experiment (DF-039):** the owner executed a single authenticated Muse Spark 1.3 Chat Completions call using three newly generated fictional plaintext documents. The response was HTTP **200**; TrueLanded checked **18/18 exact source literals**. It reported 684 prompt, 1,290 completion and 1,974 total tokens. The raw provider response and API credentials are **not included** in this evaluation package.
- **Independent offline version (this repository):** uses a **clearly marked local test double** with the Muse Spark 1.3 response shape, then routes the candidates through the same exact-line checks and deterministic planning code. The static page and offline tests **do not make a Meta inference**.
- **Optional independent live test:** `integration/muse_cli.py` implements an explicit **one potentially billable call** with a private one-shot lock, strict model allowlist and no retries. It requires the evaluator's own authorized `MODEL_API_KEY`, deliberate flags and a private folder **outside this repository**. It must never run as the default judge command.

## Source code and provenance

`integration/` contains candidate extraction and deterministic evidence planning; `tests/` contains adversarial and independent-oracle checks; `docs/` contains the client-side demonstration; `demo/` and `review/` contain distinct localhost servers for a mock scene and authorized private-capture replay, respectively. `NEW_WORK.md` identifies contest-only work and provenance. The prior commercial TrueLanded product is not distributed.

This is a **fictional proof-of-concept**: no customer files, customs clearance, document issuer authentication, real PDF OCR validation or automated regulator communication. Humans remain responsible for every operational decision.

**Independent technical checks ≠ official eligibility or license sign-off.** The participant guide and accepted Official Rules determine submission requirements; the owner must approve rights and publication separately.
