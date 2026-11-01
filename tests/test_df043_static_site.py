"""DF043 third-party accessible static simulated judge demo tests. Offline only."""
from __future__ import annotations
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import threading
import unittest
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
SPEC = importlib.util.spec_from_file_location(
    "df043_generator", ROOT / "scripts" / "df043_build_static_site.py")
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


class DF043SiteTests(unittest.TestCase):
    def test_versioned_json_is_reproducible(self):
        self.assertEqual((SITE / "data.json").read_bytes(), build.content())

    def test_all_three_stages_are_exact_source_grounded(self):
        data = json.loads((SITE / "data.json").read_text("utf8"))
        self.assertEqual(data["schema"], "TRUELANDED_DF043_SYNTHETIC_STATIC_V1")
        self.assertEqual([len(s["source_lines"]) for s in data["stages"]], [4, 7, 7])
        self.assertEqual([s["literal_matches"] for s in data["stages"]], [4, 7, 7])
        for stage in data["stages"]:
            raw = ("\n".join(stage["source_lines"]) + "\n").encode("utf8")
            self.assertEqual(sha256(raw).hexdigest(), stage["source_sha256"])
            self.assertFalse(stage["issuer_authenticated"])
            self.assertTrue(stage["human_review_required"])
        self.assertIn("VALUE_MISMATCH", data["stages"][1]["newly_exposed"])
        self.assertIn("VALUE_MISMATCH", data["stages"][2]["conditionally_reconciled"])
        self.assertEqual(data["final_next_best_proof"], "REQ_TECH_SHEET")

    def test_no_false_provider_attestation_or_credential(self):
        data = json.loads((SITE / "data.json").read_text("utf8"))
        self.assertEqual(data["meta_api_calls_during_site"], 0)
        self.assertFalse(data["provider_signature_verified"])
        self.assertFalse(data["private_receipt_included"])
        self.assertEqual(data["model_candidate_source"], "LOCAL_TEST_DOUBLE_NOT_META")
        self.assertEqual(data["mode"], "SIMULATED_OFFLINE_NOT_META_INFERENCE")
        for filename in ("index.html", "app.js", "counterfactual.js", "style.css", "data.json"):
            text = (SITE / filename).read_text("utf8")
            self.assertNotIn("LLM_", text)
            self.assertNotIn("github_pat_", text)
            self.assertNotIn("sk-proj-", text)
            self.assertNotIn("UNTRUSTED_HTTP_BODY_PRIVATE", text)

    def test_site_enforces_text_only_untrusted_data_and_source_hash(self):
        script = (SITE / "app.js").read_text("utf8")
        self.assertIn("crypto.subtle.digest", script)
        self.assertIn("textContent", script)
        self.assertIn("replaceChildren", script)
        self.assertNotIn("innerHTML", script)
        self.assertNotIn("eval(", script)
        self.assertNotIn("meta_api_key", script.lower())
        self.assertNotIn("https://", script)
        self.assertNotIn("fetch('http", script)
        self.assertIn("SOURCE_SHA256_MISMATCH", script)
        self.assertIn("SOURCE_INDEX_SHA256_MISMATCH", script)
        self.assertIn("verified_source_index_sha256", script)
        self.assertIn("renderWhatIf", script)
        from hashlib import sha256 as digest
        scene = json.loads((SITE / "data.json").read_text("utf8"))
        index = "".join(s["event_id"] + "\n" + s["source_sha256"] + "\n"
                        for s in scene["stages"])
        self.assertEqual(digest(index.encode("utf8")).hexdigest(),
                         "a0cc3282929ff0e67958ee27901016c7bcd21fd857d06796e3fa7d220e677ecc")
        self.assertIn("counterfactual.js", (SITE / "index.html").read_text("utf8"))
        html = (SITE / "index.html").read_text("utf8")
        self.assertIn("Content-Security-Policy", html)
        self.assertIn("SIMULATED", html)
        self.assertIn("script-src 'self'", html)

    def test_local_http_static_assets_are_accessible_without_key(self):
        class Quiet(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(SITE), **kwargs)
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Quiet)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for path in ("/", "/index.html", "/style.css", "/app.js", "/counterfactual.js", "/data.json"):
                with self.subTest(path=path):
                    with urlopen(f"http://127.0.0.1:{server.server_port}{path}",
                                 timeout=4) as response:
                        self.assertEqual(response.status, 200)
                        self.assertGreater(len(response.read()), 100)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_static_site_contains_no_private_pdf_or_historical_replay(self):
        names = sorted(x.name for x in SITE.iterdir() if x.is_file())
        self.assertEqual(names, ["adjudication-data.json", "adjudication.html", "adjudication.js",
                                 "app.js", "counterfactual.js", "data.json", "index.html", "style.css"])


if __name__ == "__main__":
    unittest.main()
