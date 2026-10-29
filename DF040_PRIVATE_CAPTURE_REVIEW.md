# DF-040: Private owner-executed Muse capture review (no new API calls)

**Strictly private; no provider-signed attestation.** DF039 used one owner-authorized actual Muse Spark 1.3 HTTP request. This viewer performs *zero* Meta requests and projects only locally revalidated excerpts from that prior capture. The original response, one-shot lock, tokens, raw body and private receipts stay **OUTSIDE** this repository. No files from DF039 are committed.

## Offline acceptance
Run `python -B RUN_OFFLINE_TESTS.py` (102 tests). Tests exclusively fabricate mock fixtures, and they do **not** access the owner's DF039 archive. The previous `demo/` remains explicitly simulated and is not silently relabeled.

## Review an actual private receipt (owner only)
Run:

```powershell
py -3.11 -B review/server.py --private-evidence-dir "<EXISTING_PRIVATE_CAPTURE_DIR_OUTSIDE_REPOSITORY>" --port 18972
```

Open `http://127.0.0.1:18972/` on the same PC. The server fails closed unless every GET passes the one-shot lock, request SHA, capture SHA, exact-source claims and deterministic cascade. It binds only to localhost, rejects cross-origin, cookies, credentials and state-changing requests, and never returns the original Meta response body. The viewer labels the experience **owner-executed Meta response / local replay**, not fresh model inference. Its source documents are synthetic plaintext; it does not authenticate suppliers, validate operational trade decisions or demonstrate PDF OCR. Human verification is mandatory.

## Technical trust boundary
- A local HTTPS client invocation and its captured response were observed by the owner for DF039. The response self-reported `muse-spark-1.3` and passed local source checking; Meta did **not** issue an independently verified cryptographic signature in the receipt.
- Local SHA-256 checks detect tampering only against the locally established baseline. These do not prove provider issuance or identity.
- `integration/df040_capture_projection.py` rechecks the private evidence; the `review/` server returns only a bounded derived synthetic scene. No request or capture is included in the distributable Git repository.
- The reviewer needs access to a properly authorized private receipt to reproduce this actual-capture replay. Without it, the viewer fails closed. The standalone `demo/` remains reproducible without private secrets but is clearly simulated.

**PUBLIC RELEASE HOLD:** Contest rules, output redistribution and ownership permission remain open. Repository must stay private. No video work authorized until overall Technical Complete.