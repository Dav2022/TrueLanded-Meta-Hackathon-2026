# DF-043 — Owner release-decision card (not a license or permission)

The competition deadline is **2026-11-04 21:00 ET / 20:00 Costa Rica**. The Participant Guide requires a **public repository** and an **accessible three-minute video**.

## Proposed release strategy: isolated, minimal and verifiable

- Keep the existing private GitHub repository and its audit history untouched.
- Construct a new **local one-commit sanitized snapshot** from the deterministic Judge Kit, including `docs/` for GitHub Pages. The snapshot does **not** contain the seven historical viewer files, old Git blobs, private Meta captures or commercial TrueLanded files.
- **Do not create a public remote or change visibility until owner expressly approves** the release route, copyright rights, and a concrete license.
- On approval, create a fresh GitHub repository within the hackathon period, push only the sanitized snapshot, and enable GitHub Pages from `main`/`docs`. Recheck that the organizer permits this repository-creation and submission route.
- Verify both repository and demo URL anonymously; the sample documents remain explicitly fictional. The judges can reproduce a separately authorized live Muse request using their own Meta credentials, but not the owner’s private DF-039 receipt.

## Owner decisions required before a public push

1. **Rights:** affirm that the selected competition-only files and all contributions may be redistributed and no employer/client/coauthor rights prevent it. Similarity scans are not legal proof.
2. **License:** choose an explicit permissible license for **only this released subset**. MIT is short/permissive; Apache-2.0 includes an express patent grant. Neither license should be silently applied to commercial TrueLanded.
3. **Rules:** review the authentic accepted Official Rules/waiver and original organizer messages, especially requirements for a new repo and what counts as new work. The supplied Guide is an authoritative supporting source but not a complete copy of the accepted waiver.
4. **Identity:** confirm the sole participant/team and whether legal names must appear.
5. **Publication:** separately authorize any public GitHub repo creation, push or visiblity change.
6. **Video:** confirm video content and rights, render final 3-minute artifact, verify accessible link.
7. **Form:** review and submit before Nov 4 at 20:00 Costa Rica, then capture acknowledgement.

**No-go until:** rights + license + authentic accepted rules + repo visibility + accessible video + contribution metadata. A green test suite cannot substitute for those decisions.
