"""DF023 PRIVATE: bounded, synthetic proof-impact re-evaluation on NEW evidence.

Not a general document parser, legal advice, source authentication, or Muse inference.
All scenarios are explicitly simulated; originals and DF021 are immutable.
"""
from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
import json
import indie_core
import df021_planner
import evidence_graph

VERSION = "df023-proof-impact/0.1-private"
REF = "TL-INDIE-ALPHA"
SYNTHETIC_DOCUMENTS = {
    "CONFIRM_PACKING_28": (
        "REFERENCE: TL-INDIE-ALPHA\n"
        "DOCUMENT: PACKING CONFIRMATION\n"
        "TOTAL UNITS: 28 PCS\n"
        "ISSUER AUTHENTICATION: NOT VERIFIED\n"
    ),
    "REVISED_INVOICE_28_13950": (
        "REFERENCE: TL-INDIE-ALPHA\n"
        "DOCUMENT: PROPOSED REVISED INVOICE\n"
        "SUPERSEDES: invoice.txt\n"
        "QUANTITY: 28 PCS\n"
        "UNIT PRICE: USD 4.50\n"
        "LINE TOTAL: USD 139.50\n"
        "ISSUER AUTHENTICATION: NOT VERIFIED\n"
    ),
    "REVISED_INVOICE_28_12600": (
        "REFERENCE: TL-INDIE-ALPHA\n"
        "DOCUMENT: PROPOSED REVISED INVOICE\n"
        "SUPERSEDES: invoice.txt\n"
        "QUANTITY: 28 PCS\n"
        "UNIT PRICE: USD 4.50\n"
        "LINE TOTAL: USD 126.00\n"
        "ISSUER AUTHENTICATION: NOT VERIFIED\n"
    ),
}
EXPECTED_ACTIONS = {
    "CONFIRM_PACKING_28": "CORROBORATION_ONLY_NO_SUPERSESSION",
    "REVISED_INVOICE_28_13950": "HYPOTHETICAL_REPLACE_INVOICE",
    "REVISED_INVOICE_28_12600": "HYPOTHETICAL_REPLACE_INVOICE",
}

class ProofImpactRefusal(ValueError):
    pass

def fingerprint(data):
    return sha256(json.dumps(data, sort_keys=True, ensure_ascii=True,
                             separators=(",", ":")).encode("utf-8")).hexdigest()

def catalog():
    return {key: {"sha256": sha256(text.encode("utf-8")).hexdigest(),
                  "bytes": len(text.encode("utf-8")),
                  "kind": EXPECTED_ACTIONS[key],
                  "fictional_only": True}
            for key, text in sorted(SYNTHETIC_DOCUMENTS.items())}

def _parse(pinned_text):
    fields = {}
    for line in pinned_text.splitlines():
        if ": " not in line:
            raise ProofImpactRefusal("INVALID_SYNTHETIC_LINE")
        k, v = line.split(": ", 1)
        if k in fields or not v:
            raise ProofImpactRefusal("DUPLICATE_OR_EMPTY_FIELD")
        fields[k] = v
    if fields.get("REFERENCE") != REF or fields.get("ISSUER AUTHENTICATION") != "NOT VERIFIED":
        raise ProofImpactRefusal("REFERENCE_OR_ISSUER_STATUS_REFUSED")
    allowed = ({"REFERENCE", "DOCUMENT", "TOTAL UNITS", "ISSUER AUTHENTICATION"}
               if fields.get("DOCUMENT") == "PACKING CONFIRMATION"
               else {"REFERENCE", "DOCUMENT", "SUPERSEDES", "QUANTITY",
                     "UNIT PRICE", "LINE TOTAL", "ISSUER AUTHENTICATION"})
    if set(fields) != allowed:
        raise ProofImpactRefusal("FIELDS_NOT_ALLOWED")
    if fields["DOCUMENT"] == "PACKING CONFIRMATION":
        if fields["TOTAL UNITS"] != "28 PCS":
            raise ProofImpactRefusal("UNEXPECTED_PACKING_QUANTITY")
        return None, None
    if fields["DOCUMENT"] != "PROPOSED REVISED INVOICE" or fields.get("SUPERSEDES") != "invoice.txt":
        raise ProofImpactRefusal("INVALID_PROPOSED_REVISION")
    if fields["QUANTITY"] != "28 PCS" or fields["UNIT PRICE"] != "USD 4.50":
        raise ProofImpactRefusal("UNEXPECTED_REVISION_VALUES")
    if fields["LINE TOTAL"] not in ("USD 139.50", "USD 126.00"):
        raise ProofImpactRefusal("UNEXPECTED_REVISION_TOTAL")
    return 28, Decimal(fields["LINE TOTAL"].split()[1])

def _rank(obligations, profile):
    if profile not in df021_planner.ALLOWED_PROFILES or type(profile) is not str:
        raise ProofImpactRefusal("UNKNOWN_FICTIONAL_PROFILE")
    rows = []
    for rid, target in sorted(indie_core.PROPOSALS.items()):
        covered = sorted(set(target) & set(obligations))
        if not covered:
            continue
        effort, delay, burden = evidence_graph.PROFILES[profile][rid]
        weighted = sum(df021_planner.WEIGHTS[x] for x in covered)
        rows.append({"request_id": rid, "may_address": covered,
                     "fictional_efficiency": round(weighted / (effort + delay + burden), 4),
                     "not_acquired": True})
    return sorted(rows, key=lambda r: (-r["fictional_efficiency"], r["request_id"]))

def reassess(event_id, *, supplied_bytes=None, profile="direct_source_is_faster"):
    """Evaluate allowlisted fictional NEW document as a hypothetical branch only.

    The bytes parameter is an exact-match integrity check, NOT an upload facility.
    Evidence from an unauthenticated issuer cannot close a real proof obligation.
    """
    if type(event_id) is not str or event_id not in SYNTHETIC_DOCUMENTS:
        raise ProofImpactRefusal("EVENT_NOT_WHITELISTED")
    if type(profile) is not str or profile not in df021_planner.ALLOWED_PROFILES:
        raise ProofImpactRefusal("PROFILE_NOT_WHITELISTED")
    text = SYNTHETIC_DOCUMENTS[event_id]
    expected = text.encode("utf-8")
    if supplied_bytes is not None and (type(supplied_bytes) is not bytes or
                                       len(supplied_bytes) > 4096 or supplied_bytes != expected):
        raise ProofImpactRefusal("DOCUMENT_BYTES_OR_HASH_MISMATCH")
    quantity, stated_total = _parse(text)
    baseline = indie_core.evaluate()
    before = {x["id"] for x in baseline["obligations"]}
    invoice_qty = 31 if quantity is None else quantity
    invoice_total = Decimal("139.50") if stated_total is None else stated_total
    packing_qty = 28
    per_unit = Decimal("4.50")
    after = set()
    if invoice_qty != packing_qty:
        after.add("QTY_MISMATCH")
    if per_unit * invoice_qty != invoice_total:
        after.add("VALUE_MISMATCH")
    if 4 * 7 != packing_qty:
        after.add("PACKING_MISMATCH")
    if "TECHNICAL_GAP" in before:
        after.add("TECHNICAL_GAP")
    potential = {k: v for k, v in indie_core.PROPOSALS.items() if set(v) & after}
    sets = indie_core.minimal_cover(sorted(after), potential)
    ranked = _rank(after, profile)
    original = df021_planner.plan(profile=profile)
    result = {
        "version": VERSION, "case_id": REF, "event_id": event_id,
        "event_is_simulated": True, "new_document_sha256": sha256(expected).hexdigest(),
        "original_source_anchor_sha256": baseline["source_anchor_sha256"],
        "original_document_bytes_modified": False,
        "evidence_intake": "FICTIONAL_DOCUMENT_EXACT_BYTES_MATCH_ONLY",
        "issuer_authenticated": False, "claim_verified": False,
        "revision_applied_to_real_document": False, "human_review_required": True,
        "authorizes_declaration_or_payment": False, "model_inference_performed": False,
        "before_open_obligations": sorted(before), "scenario_open_obligations": sorted(after),
        "conditionally_resolved": sorted(before - after),
        "newly_exposed": sorted(after - before),
        "original_top_request": original["requests"][0]["request_id"],
        "scenario_next_requests": ranked,
        "scenario_top_request": ranked[0]["request_id"] if ranked else None,
        "scenario_minimal_cover_sets": sets,
        "proof_closure_status": "NOT_AUTHENTICATED_NOT_APPROVED",
        "originals_superseded": False,
        "pending_reviews": ["VALIDATE_DOCUMENT_ISSUER", "REVIEW_CONTRADICTORY_RECORDS",
                            "HUMAN_DECISION_REQUIRED"],
        "impact_semantics": "CONDITIONAL_INTERNAL_CONSISTENCY_NOT_VERIFIED_LEGAL_PROOF",
        "illustrative_amount_delta_usd": str(
            (Decimal(invoice_qty) * per_unit - invoice_total).quantize(Decimal("0.01"))),
        "fictional_assumption_profile": profile,
        "no_real_world_probability_or_cost_claim": True,
    }
    result["result_sha256"] = fingerprint(result)
    return result
