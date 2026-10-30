"""Adversarial DF042 release-gate tests; no public operations."""
from __future__ import annotations
from pathlib import Path
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "df042_release_preflight", ROOT/"scripts"/"df042_release_preflight.py"
)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def facts():
    return dict(
        new_work_present=True,
        judge_kit_present=True,
        git_clean=True,
        raw_private_receipt_in_git=False,
        high_confidence_secret_blob=False,
        license_owner_approved=False,
        code_rights_owner_approved=False,
        official_rules_reviewed=False,
        public_repo_checked=False,
        video_checked=False,
        history_rights_cleared=False,
        submission_metadata_reviewed=False,
    )


class TestDF042NoGo(unittest.TestCase):
    def test_clean_reproducible_private_repo_is_still_no_go(self):
        out = gate.evaluate_facts(facts())
        self.assertEqual(out["status"], "NO_GO")
        self.assertFalse(out["release_authorized"])
        self.assertIn("LICENSE_EXPLICITLY_OWNER_APPROVED", out["blocking_gates"])
        self.assertIn("THREE_MINUTE_DEMO_VIDEO_ACCESSIBLE", out["blocking_gates"])

    def test_owner_never_auto_authorizes_release_even_when_all_checks_true(self):
        f = facts()
        f.update({name: True for name in (
            "license_owner_approved", "code_rights_owner_approved",
            "official_rules_reviewed", "public_repo_checked",
            "video_checked", "history_rights_cleared",
            "submission_metadata_reviewed"
        )})
        out = gate.evaluate_facts(f)
        self.assertEqual(out["status"], "REVIEW_COMPLETE_NEEDS_EXPLICIT_OWNER_GO")
        self.assertFalse(out["release_authorized"])

    def test_publicity_alone_does_not_clear_license(self):
        f = facts()
        f["public_repo_checked"] = True
        self.assertIn("LICENSE_EXPLICITLY_OWNER_APPROVED",
                      gate.evaluate_facts(f)["blocking_gates"])

    def test_secrets_always_block(self):
        f = facts()
        f["high_confidence_secret_blob"] = True
        self.assertIn("SECRET_SIGNATURE_SCAN_CLEAR",
                      gate.evaluate_facts(f)["blocking_gates"])

    def test_raw_receipts_always_block(self):
        f = facts()
        f["raw_private_receipt_in_git"] = True
        self.assertIn("NO_PRIVATE_RAW_RECEIPT_TRACKED",
                      gate.evaluate_facts(f)["blocking_gates"])

    def test_dirty_tree_blocks(self):
        f = facts()
        f["git_clean"] = False
        self.assertIn("SOURCE_GIT_WORKTREE_CLEAN",
                      gate.evaluate_facts(f)["blocking_gates"])

    def test_historical_rights_separate_from_head(self):
        f = facts()
        f["history_rights_cleared"] = False
        self.assertIn("ALL_GIT_HISTORY_RIGHTS_CLEARED",
                      gate.evaluate_facts(f)["blocking_gates"])

    def test_missing_official_rules_always_block(self):
        f = facts()
        f["official_rules_reviewed"] = False
        self.assertIn("ORIGINAL_OFFICIAL_RULES_ACCEPTED_AND_REVIEWED",
                      gate.evaluate_facts(f)["blocking_gates"])

    def test_missing_provenance_blocks(self):
        f = facts()
        f["new_work_present"] = False
        self.assertIn("NEW_WORK_TRACEABLE",
                      gate.evaluate_facts(f)["blocking_gates"])


if __name__ == "__main__":
    unittest.main()
