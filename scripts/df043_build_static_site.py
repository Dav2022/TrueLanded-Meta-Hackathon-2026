"""DF-043: generate and verify a zero-network, synthetic-only static judge demo.

This is intentionally NOT a replay of the owner's real Meta result.
Source extraction is mocked; all calculations are real deterministic engine code.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integration"))
from df037_mock_pipeline import execute, SEED


class StaticDemoRefusal(ValueError):
    pass


def make_scene() -> dict:
    original = execute(SEED)
    if (original.get("gate") != "DF037_FULL_PIPELINE_MOCK_SOURCE_CHECKED"
        or original.get("api_calls") != 0
        or original.get("literal_matches") != 18
        or original.get("final_next_best_proof") != "REQ_TECH_SHEET"
        or len(original.get("stages", [])) != 3):
        raise StaticDemoRefusal("MOCK_SOURCE_GATE_FAILED")
    stages = []
    for item in original["stages"]:
        lines = item["source_lines"]
        if (item["literal_matches"] != len(lines)
            or hashlib.sha256(("\n".join(lines) + "\n").encode("utf8")).hexdigest()
                != item["source_sha256"]):
            raise StaticDemoRefusal("SOURCE_BYTES_FAILED")
        stages.append({
            "event_id": item["stage"],
            "source_lines": lines,
            "source_sha256": item["source_sha256"],
            "literal_matches": item["literal_matches"],
            "open_obligations": item["open_obligations"],
            "newly_exposed": item["newly_exposed"],
            "conditionally_reconciled": item["conditionally_reconciled"],
            "next_best_proof": item["next_best_proof"],
            "issuer_authenticated": False,
            "human_review_required": True,
        })
    return {
        "schema": "TRUELANDED_DF043_SYNTHETIC_STATIC_V1",
        "mode": "SIMULATED_OFFLINE_NOT_META_INFERENCE",
        "model_candidate_source": "LOCAL_TEST_DOUBLE_NOT_META",
        "model_name_requested": "muse-spark-1.3",
        "meta_api_calls_during_site": 0,
        "provider_signature_verified": False,
        "private_receipt_included": False,
        "source_document_issuers_authenticated": False,
        "human_review_required": True,
        "source_pack_sha256": original["source_pack_sha256"],
        "total_literal_matches": 18,
        "final_next_best_proof": "REQ_TECH_SHEET",
        "stages": stages,
    }


def content() -> bytes:
    return (json.dumps(make_scene(), sort_keys=True, ensure_ascii=True,
                       separators=(",", ":")) + "\n").encode("utf8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="Verify static data against the deterministic generator")
    args = parser.parse_args()
    target = ROOT / "docs" / "data.json"
    payload = content()
    if args.check:
        if not target.is_file() or target.read_bytes() != payload:
            print("DF043_STATIC_DATA_DRIFT_REFUSED", file=sys.stderr)
            return 2
        print("DF043_STATIC_DATA_MATCHES_DETERMINISTIC_MOCK_SOURCE")
    else:
        target.write_bytes(payload)
        print("DF043_SYNTHETIC_SITE_DATA_WRITTEN_NO_META_CALLS")
    print("FILE_SHA256=" + hashlib.sha256(payload).hexdigest())
    print("BYTES=" + str(len(payload)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
