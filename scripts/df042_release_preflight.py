"""DF042 offline release gate: fail closed without rights, video or full rules.

Read-only. Does not change GitHub visibility, grant licenses or access credentials.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPOSITORY = "Dav2022/TrueLanded-Meta-Hackathon-2026"
HISTORY_MARKERS = (
    "viewer/DF023M_JURY_EVIDENCE.json",
    "viewer/DF023M_PREPUBLICATION_MANIFEST.json",
    "viewer/df023m_index.html",
)


def git(*args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True,
        check=True, timeout=20,
    ).stdout


def evaluate_facts(facts: dict) -> dict:
    """Pure, explicitly conservative policy mapping; no implicit approvals."""
    checks = {
        "NEW_WORK_TRACEABLE": bool(facts.get("new_work_present")),
        "STANDALONE_OFFLINE_KIT": bool(facts.get("judge_kit_present")),
        "SOURCE_GIT_WORKTREE_CLEAN": bool(facts.get("git_clean")),
        "NO_PRIVATE_RAW_RECEIPT_TRACKED": not bool(facts.get("raw_private_receipt_in_git")),
        "SECRET_SIGNATURE_SCAN_CLEAR": not bool(facts.get("high_confidence_secret_blob")),
        "LICENSE_EXPLICITLY_OWNER_APPROVED": bool(facts.get("license_owner_approved")),
        "COMPETITION_CODE_RIGHTS_OWNER_SIGNOFF": bool(facts.get("code_rights_owner_approved")),
        "ORIGINAL_OFFICIAL_RULES_ACCEPTED_AND_REVIEWED": bool(facts.get("official_rules_reviewed")),
        "GITHUB_REPOSITORY_PUBLIC_ANONYMOUSLY_ACCESSIBLE": bool(facts.get("public_repo_checked")),
        "THREE_MINUTE_DEMO_VIDEO_ACCESSIBLE": bool(facts.get("video_checked")),
        "ALL_GIT_HISTORY_RIGHTS_CLEARED": bool(facts.get("history_rights_cleared")),
        "PRESENTATION_LISTS_NEW_WORK_AND_CONTRIBUTORS": bool(facts.get("submission_metadata_reviewed")),
    }
    must = tuple(name for name, ok in checks.items() if not ok)
    return {
        "gate": "DF042_PRIVATE_PREPARATION_PASS_PUBLIC_RELEASE_NO_GO" if must
                else "DF042_RELEASE_CHECKS_RECORDED_HUMAN_APPROVAL_STILL_REQUIRED",
        "release_authorized": False,  # Always human decision outside software.
        "status": "NO_GO" if must else "REVIEW_COMPLETE_NEEDS_EXPLICIT_OWNER_GO",
        "checks": checks,
        "blocking_gates": must,
    }


def inspect() -> dict:
    tracked = git("ls-files", "-z").decode("utf8").split("\0")
    tracked = {name for name in tracked if name}
    clean = not git("status", "--porcelain")
    source_commit = git("rev-parse", "HEAD").decode("ascii").strip()
    # The repo exists as a separate competition repo but we do NOT infer from
    # Git author dates that GitHub created it during the permitted window.
    raw_names = {"UNTRUSTED_HTTP_BODY_PRIVATE.bin",
                 "HTTP_CAPTURE_METADATA_PRIVATE.json",
                 "ONE_BILLABLE_ATTEMPT_LOCK_PRIVATE.json",
                 "LITERAL_GATE_REVIEW_PRIVATE.json"}
    raw_tracked = [s for s in tracked if Path(s).name in raw_names]
    history = git("rev-list", "--objects", "--all").decode("utf8", errors="replace")
    history_has_viewer = any(marker in history for marker in HISTORY_MARKERS)
    secret_matches = []
    for record in history.splitlines():
        if not record:continue
        object_id = record.split(" ", 1)[0]
        if git("cat-file", "-t", object_id).strip() != b"blob":
            continue
        if int(git("cat-file", "-s", object_id)) > 500_000:
            continue
        raw = git("cat-file", "blob", object_id)
        if any(re.search(pattern, raw) for pattern in (
            rb"ghp_[A-Za-z0-9]{30,}",
            rb"github_pat_[A-Za-z0-9_]{25,}",
            rb"sk-proj-[A-Za-z0-9_-]{20,}",
            rb"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        )):
            secret_matches.append(object_id)
    facts = {
        "new_work_present": "NEW_WORK.md" in tracked,
        "judge_kit_present": "judge_kit/BUILD_JUDGE_KIT.py" in tracked,
        "git_clean": clean,
        "raw_private_receipt_in_git": bool(raw_tracked),
        "high_confidence_secret_blob": bool(secret_matches),
        "license_owner_approved": False,  # This task does not grant rights.
        "code_rights_owner_approved": False,
        "official_rules_reviewed": False,  # Full authenticated waiver unavailable.
        "public_repo_checked": False,  # Repo has remained private; online verify separately.
        "video_checked": False,
        "history_rights_cleared": not history_has_viewer and False,
        "submission_metadata_reviewed": False,
    }
    result = evaluate_facts(facts)
    return {
        "schema": "DF042_RELEASE_PREFLIGHT_V1",
        "source_commit": source_commit,
        "source_repository": SOURCE_REPOSITORY,
        "tracked_files": len(tracked),
        "commits": len(git("rev-list", "HEAD").splitlines()),
        "existing_history_contains_derived_viewer": history_has_viewer,
        "raw_private_receipts_tracked": len(raw_tracked),
        "secret_signatures_in_historical_git_blobs": len(secret_matches),
        **result,
        "notes": [
            "A private repository cannot meet the guide's public-repository submission requirement.",
            "No LICENSE: public visibility alone is not a free/open source license.",
            "Deleting the historical viewer from HEAD does not erase Git object history.",
            "Exact hash comparison with commercial source does not prove independent origin.",
            "Model API output ownership does not grant third-party intellectual property.",
            "No publication, license assignment, video or irreversible Git rewrite is performed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-release-ready", action="store_true")
    args = parser.parse_args()
    try:
        result = inspect()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError):
        print("DF042_RELEASE_PREFLIGHT_ERROR_FAIL_CLOSED", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.require_release_ready and result["status"] != "REVIEW_COMPLETE_NEEDS_EXPLICIT_OWNER_GO":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
