"""DF-023 PRIVATE — append-only *synthetic* evidence sequence, never a real intake.

Cumulative simulated arrival sequence; each proposed invoice is considered only
as the current scenario's candidate (not a legally superseding document).
Originals, authority flags, model receipts remain untouched.
"""
from __future__ import annotations
from hashlib import sha256
from decimal import Decimal
import json
import df023_proof_impact as impact
import indie_core
import df021_planner

VERSION = "df023-proof-impact-timeline/0.2-private"
EVENT_ORDER = ("CONFIRM_PACKING_28", "REVISED_INVOICE_28_13950",
               "REVISED_INVOICE_28_12600")
SCENES = (
    ("ORIGINAL DOCUMENTS", "Invoice 31 PCS vs packing list 28 PCS",
     "Quantity discrepancy open; original fictional records are unchanged."),
    ("PACKING CONFIRMATION", "Additional fictional confirmation: 28 PCS",
     "Corroborates the packing list, but does not rewrite the conflicting invoice."),
    ("REVISED INVOICE — VALUE CONFLICT", "Proposed invoice: 28 x $4.50, total $139.50",
     "Quantity aligns conditionally. Stated total exceeds the calculated amount by USD 13.50."),
    ("SECOND REVISION — ARITHMETIC ALIGNS", "Proposed invoice: 28 x $4.50 = $126.00",
     "Arithmetic aligns conditionally; technical proof and issuer authority stay open."),
)

class TimelineRefusal(ValueError):
    pass

def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True).encode("utf8")).hexdigest()

def _state(stage, profile):
    baseline = indie_core.evaluate()
    before = sorted({x["id"] for x in baseline["obligations"]})
    original_hash = baseline["source_anchor_sha256"]
    if stage == 0:
        state = dict(
            open_obligations=before,
            ranking=impact._rank(before, profile),
            value_delta="0.00",
            branch_document=None,
            scenario_source_hash=None,
            parsed_invoice_quantity=31,
            parsed_invoice_total="139.50",
        )
    else:
        event_id = EVENT_ORDER[stage-1]
        model = impact.reassess(event_id, profile=profile)
        if model["original_source_anchor_sha256"] != original_hash:
            raise TimelineRefusal("ORIGINAL_ANCHOR_CHANGED")
        expected = impact.catalog()[event_id]["sha256"]
        if model["new_document_sha256"] != expected:
            raise TimelineRefusal("SCENARIO_DOCUMENT_CHANGED")
        state = dict(
            open_obligations=model["scenario_open_obligations"],
            ranking=model["scenario_next_requests"],
            value_delta=model["illustrative_amount_delta_usd"],
            branch_document=event_id,
            scenario_source_hash=model["new_document_sha256"],
            parsed_invoice_quantity=31 if stage == 1 else 28,
            parsed_invoice_total="139.50" if stage <= 2 else "126.00",
        )
    return state, original_hash

def journey(stage=0, *, profile="direct_source_is_faster"):
    if type(stage) is not int or not 0 <= stage <= 3:
        raise TimelineRefusal("INVALID_STAGE")
    if type(profile) is not str or profile not in df021_planner.ALLOWED_PROFILES:
        raise TimelineRefusal("INVALID_PROFILE")
    timeline=[]
    previous=None
    base_hash=None
    prev_chain_hash=None
    for i in range(stage+1):
        state, original_hash = _state(i, profile)
        if base_hash is None:
            base_hash=original_hash
        elif original_hash != base_hash:
            raise TimelineRefusal("BASELINE_HASH_DRIFT")
        current=set(state["open_obligations"])
        if previous is None:
            became_open=sorted(current)
            resolved=[]
            unchanged=[]
        else:
            became_open=sorted(current-previous)
            resolved=sorted(previous-current)
            unchanged=sorted(current&previous)
        added=list(EVENT_ORDER[:i])
        evidence=[{"event_id":e, "sha256":impact.catalog()[e]["sha256"],
                   "issuer_authenticated":False, "simulation_only":True}
                  for e in added]
        lead=state["ranking"][0]["request_id"] if state["ranking"] else None
        phase={
            "stage":i,"stage_label":SCENES[i][0],
            "headline":SCENES[i][1],"explanation":SCENES[i][2],
            "arrived_synthetic_documents":evidence,
            "latest_event":state["branch_document"],
            "current_candidate_invoice":None if i<=1 else EVENT_ORDER[i-1],
            "branch_source_hash":state["scenario_source_hash"],
            "open_obligations":state["open_obligations"],
            "newly_exposed_since_previous":became_open if i else [],
            "conditionally_reconciled_since_previous":resolved,
            "still_open_since_previous":unchanged,
            "source_invoice_quantity":31,"scenario_invoice_quantity":state["parsed_invoice_quantity"],
            "scenario_invoice_total_usd":state["parsed_invoice_total"],
            "quantity_times_unit_price_usd":str(
                (Decimal(state["parsed_invoice_quantity"]) *
                 Decimal("4.50")).quantize(Decimal(".01"))),
            "arithmetic_delta_usd":state["value_delta"],
            "next_proof_ranked":state["ranking"],
            "top_proof_request":lead,
            "proof_request_issued":False,
            "source_invoice_modified":False,
            "issuer_authenticated":False,"claim_verified":False,
            "human_review_required":True,
            "proof_closure_status":"NOT_AUTHENTICATED_NOT_APPROVED",
            "fictional_costs_only":True,
            "precedence":"SIMULATED_LATEST_PROPOSAL_ONLY_NOT_LEGAL_SUPERSESSION",
            "inference_performed":False,
            "human_override_or_clearance":False,
        }
        phase["previous_chain_hash"]=prev_chain_hash
        phase["chain_hash"]= _digest(phase)
        prev_chain_hash=phase["chain_hash"]
        timeline.append(phase)
        previous=current
    result={
        "version":VERSION,"case_id":impact.REF,"selected_stage":stage,
        "history":timeline, "current":timeline[-1],
        "original_source_anchor_sha256":base_hash,
        "synthetic_sequence_only":True,
        "no_new_model_calls":True, "all_sources_unauthenticated":True,
        "all_evidence_additions_simulated":True,"no_real_world_workflow_execution":True,
        "model_inference_performed":False,
        "immutable_originals":True,
        "human_review_required":True,
        "hash_chain_is_author_derived_not_signature":True,
        "revision_status":"PROPOSED_CANDIDATES_NOT_APPROVED",
        "profiles":[{"id":key,"label":("Direct source faster (fictional)" if key=="direct_source_is_faster"
                         else "Supplier/factory faster (fictional)")}
                     for key in sorted(df021_planner.ALLOWED_PROFILES)],
        "event_catalog":impact.catalog(),
    }
    result["result_sha256"]=_digest(result)
    return result
