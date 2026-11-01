# DF-073 — Juror video review cut and local screenshot QA (private)

**Status:** PRIVATE VIDEO REVIEW CUT BUILT; not recorded final, uploaded or submitted.  
**Date:** 2026-10-31 America/Costa_Rica.  
**Production source:** `df072-clean-jury-private`, root commit `83b78000b3db382243f446bd7e76f0a0e2d43339`.

## What exists
- Locally rendered video: `DF073_TrueLanded_Jury_Demo_REVIEW_CUT.mp4`.
- Exact measured duration: **175.000 seconds** (<180 seconds).
- Technical format: **1920×1080 / 24 fps / H.264 video + AAC audio**.
- Video SHA-256: `a928a4ed79227f779f99e7e5d5a2f9c347e2fa7490a25a9bd62ce61875be6ce4`.
- A separate `English_Narration_Script.txt` and `English_Captions_Reference.srt` accompany the *private* media bundle.
- Machine voice is a guide for pacing and must be replaced by a quality English narration and checked subtitles before official delivery.
- **No paid Meta API call, live inference, publication, organizer submission or third-party stock media** occurred.

## Representative visual QA
The installed Chrome in the container blocked both `http://127.0.0.1` and `file://`. To inspect the actual page structure, the existing HTML/CSS/JS was rendered into a blank document; the JSON scene was supplied by a local fetch adapter, and the digest operation was bridged to Python hashlib. The application ran its original stage-selection and interactive what-if code, returning:
- `18/18 SYNTHETIC SOURCE LITERALS VERIFIED`
- All three source revisions selected and displayed.
- Fictional invoice change `28 × USD 7.92 = USD 221.76`, with value contradiction conditionally reconciled.
- Hypothetical `31 × USD 7.92 = USD 245.52`, with packing quantity mismatch exposed.
- No application JavaScript errors observed; mobile viewport 390px measured no horizontal overflow.

**CAVEAT:** This adapted visual QA is **not** actual public-network end-to-end acceptance. GitHub Actions independently passed Node tests against real WebCrypto and the Python tests. The final video must be captured from the actual HTTPS-deployed UI.

## Video scenes (175 s)
| Chapter | Duration | Demonstration |
|---|---:|---|
| The problem | 13 s | Trade-document uncertainty |
| Evidence-first | 14 s | Synthetic source literals and boundaries |
| Packing mismatch | 14 s | 28 PCS vs missing proof |
| Invoice A | 16 s | Incorrect USD 235.06 line total |
| Invoice B | 16 s | Corrected USD 221.76 total |
| Next Best Proof | 13 s | Reconciled invoice → specification sheet |
| What-if introduction | 16 s | Browser calculation, not a recorded switch |
| Corrected invoice calculation | 15 s | Updated obligations |
| Alternate quantity | 14 s | New 31-piece hypothesis |
| Muse Spark 1.3 provenance | 15 s | Historical authorized API result, separate offline browser |
| Independent verification | 16 s | Synthetic CI tests and refusal semantics |
| Conclusion | 13 s | Human review, evidence-to-decision |

## Important remaining gates
1. Validate frozen owner DF-069/DF-070 local evidence and reconcile its strongest approved PDF demonstration.
2. Produce the **actual final narrated capture** and verify live playback anonymously.
3. Obtain explicit rights/license approval. A clean branch's lack of parents does **not** sanitize other refs in the same GitHub repository.
4. Follow the owner-approved safe history/cache purge path before setting this existing repo public.
5. Verify accepted Official Rules and submission form fields; submit and save receipt by Nov 4, 20:00 Costa Rica.

**This record is a private asset register, not a release approval.**
