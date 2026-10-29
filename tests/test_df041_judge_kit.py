"""DF041 packaging guardrails, no network or private receipts."""
from __future__ import annotations
from pathlib import Path
import importlib.util
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "judge_kit"))
import BUILD_JUDGE_KIT as builder
import VERIFY_JUDGE_KIT as verifier


class DF041SourceBundleTests(unittest.TestCase):
    def test_explicit_allowlist_excludes_old_replay(self):
        self.assertGreaterEqual(len(builder.FILES), 35)
        self.assertFalse(any(name.startswith("viewer/") for name in builder.FILES))
        self.assertFalse(any("df039" in name.lower() for name in builder.FILES))
        self.assertNotIn("RUN_OFFLINE_TESTS.py", builder.FILES)
        self.assertIn("review/server.py", builder.FILES)
        self.assertIn("demo/server.py", builder.FILES)

    def test_zip_paths_reject_bypass(self):
        for name in ("../../secret.key", "/etc/passwd", "test\\.env",
                     "viewer/DF023M_JURY_EVIDENCE.json",
                     "private/df039_live_private/response.json", ".env"):
            with self.subTest(name=name):
                self.assertFalse(builder.normalized_path(name))
        self.assertTrue(builder.normalized_path("integration/df021_planner.py"))

    def test_zip_metadata_is_deterministic_and_not_symlink(self):
        x = builder.zipinfo("integration/df021_planner.py")
        y = builder.zipinfo("integration/df021_planner.py")
        self.assertEqual(x.date_time, y.date_time)
        self.assertEqual(x.date_time, (2026, 10, 29, 0, 0, 0))
        self.assertEqual((x.external_attr >> 16) & 0o170000, 0o100000)

    def test_missing_manifest_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(verifier.BundleRefusal):
                verifier.verify(Path(tmp))

    def test_forged_authority_manifest_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "MANIFEST.json"
            f.write_text(json.dumps({"schema": "DF041_JUDGE_KIT_ALLOWLIST_SHA256_V1",
                                     "mode": "PUBLIC_RELEASE_APPROVED",
                                     "private_model_receipts_included": False}), encoding="utf8")
            with self.assertRaisesRegex(verifier.BundleRefusal, "MANIFEST_AUTHORITY_REFUSED"):
                verifier.verify(Path(tmp))

    def test_non_git_repo_inside_kit_not_required(self):
        self.assertNotIn(".git", builder.FILES)
        self.assertFalse(any(name.startswith(".local-runs") for name in builder.FILES))


if __name__ == "__main__":
    unittest.main()
