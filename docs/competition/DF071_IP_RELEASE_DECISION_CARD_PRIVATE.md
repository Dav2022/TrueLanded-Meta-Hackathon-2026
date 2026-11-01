# DF-071 — IP protection and release decision card (PRIVATE)

**Status: PREPARED / NOT AUTHORIZED / NOT PUBLISHED.**  
**Project:** TrueLanded competition-only Evidence-to-Decision Engine.  
**Nonnegotiable:** no code, raw response, customer record or confidential algorithm from the commercial TrueLanded foundation is implicitly granted to Meta or to the general public.

## 1. Material rights boundary

The Participant Guide §4 requires a **public repository**, new hackathon work explicitly identified, and rights to all assets. The Event Waiver states the participant retains ownership of the Submission but grants organizers an **irrevocable, perpetual, royalty-free, worldwide, non-exclusive license** for broad use; the Materials clause also disclaims organizer confidentiality obligations. Therefore publishing and submission are legally consequential even if a GitHub repository's code license is restrictive.

**Eligible for tentative review:** independent hackathon-only Python/JavaScript source, tests, fictional documents, source integrity cases, provenance, independently generated demo and documentation.

**Prohibited from submission:** proprietary TrueLanded commercial source, private owner-derived viewer/replay, raw DF-039/DF-009 provider responses, API keys, customer records, real shipment documents, third-party copyrighted assets without rights, licensing commitments for any asset not owned.

## 2. Critical flaw in simply exposing the selected GitHub repository

The chosen original remote repository currently includes tracked `viewer/` files and a historic chain of old Git objects. **Merely deleting those files from the last commit or pointing an orphan branch at them does not make all prior objects inaccessible.** The open PR #1 also creates a GitHub pull-request ref referencing earlier history. GitHub's own guidance warns that caches, pull-request references and SHA-addressed commits can remain accessible after a force-push or history rewrite.

Therefore **NO-GO to simply changing `Dav2022/TrueLanded-Meta-Hackathon-2026` to public**. Even replacing `main` would need a full audit of all branches, PR refs, forks, caches and server-side retained objects, an owner-approved destructive migration, backup, and potentially GitHub Support. This is not yet a validated safe path.

## 3. Two release routes

### Route A — preferred for confidential-IP protection and on-time submission

Keep `Dav2022/TrueLanded-Meta-Hackathon-2026` **private as the canonical engineering repository**. Create a *separate*, freshly initialized, public **jury-distribution repository** containing only independently approved, SHA-manifested files, a clean root commit and an owner-selected open-source license. The submission can name **TrueLanded** and link only to this public judging snapshot, while the private engineering repository remains the source of truth.

**Trade-off:** the URL provided to the jurors would differ from the originally selected private engineering repo URL. This is materially safer than trying to purge an existing repository's caches/historical PRs under deadline pressure.

### Route B — retain exact chosen GitHub URL

Back up all refs, close/assess PR #1, perform a legally and technically audited history-filter/cleanup, confirm no sensitive/unlicensed reachable objects, coordinate with GitHub Support as warranted, audit access through the public site and only then make this original repository public. **No guarantee of immediate full purge of GitHub-side object caches.** Not recommended when protecting commercial IP is paramount.

## 4. Licensing decision (owner only)

No code license is selected or granted by this card.

- **Apache-2.0**: permissive redistribution, explicit patent terms/notice requirements. Suitable only if participant owns the exact code and accepts downstream rights.
- **MIT**: short, permissive redistribution; no explicit Apache-style patent grant, also authorizes broad reuse.
- **No open-source license**: preserves default copyright, but may not satisfy the guide's stated open-source expectation. Visibility alone is not a license.

The license would apply **only to the separate hackathon snapshot** explicitly approved by the owner. It cannot undo organizer rights already granted by the waiver for any submitted Materials.

## 5. Required owner decision

- [ ] Authorize Route A (new clean public judging snapshot with separate URL) **or** Route B (high-risk exact URL after complete Git history audit).
- [ ] Select a license for **only** the competition snapshot.
- [ ] Approve publication of the final verified allowlist and exact commit; no commercial source.
- [ ] Confirm contributor list and that third-party assets and accepted terms are cleared.
- [ ] Confirm the video and official submission once final links are reviewed.

**Do not interpret instructions to improve or finish the application as permission to grant a code license or expose unpublished source.**

## References
- Meta Global AI Developer Hackathon Participant Guide, §§4,7.
- Event Waiver, Materials and Hackathon Submission clauses.
- GitHub: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
- GitHub draft PR #1: https://github.com/Dav2022/TrueLanded-Meta-Hackathon-2026/pull/1
