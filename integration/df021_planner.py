"""DF-021 Next Best Proof: bounded, assumption-explicit synthetic acquisition planner.

The output ranks requests by *potential* obligation coverage / assumed friction.
It never treats coverage as completed, emits real-world probabilities, authenticates
an issuer, mutates source documents, or authorizes an operational action.
"""
from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
import json
import indie_core
import evidence_graph

VERSION="df021-next-best-proof/1.0"
WEIGHTS={"QTY_MISMATCH":3,"VALUE_MISMATCH":4,
         "PACKING_MISMATCH":2,"TECHNICAL_GAP":2}
ALLOWED_PROFILES=tuple(evidence_graph.PROFILES)

class PlannerRefusal(ValueError):
    pass

def _digest(data):
    return sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def plan(*,invoice_quantity=None,profile="direct_source_is_faster"):
    if profile not in ALLOWED_PROFILES or type(profile) is not str:
        raise PlannerRefusal("PROFILE_NOT_ALLOWED")
    if invoice_quantity is not None and (type(invoice_quantity) is not int or
                                          invoice_quantity not in (28,31)):
        raise PlannerRefusal("ONLY_28_OR_31_SYNTHETIC_HYPOTHESES")
    case=indie_core.evaluate(invoice_quantity=invoice_quantity)
    baseline=indie_core.evaluate()
    obligations={item["id"] for item in case["obligations"]}
    anchor=case["source_anchor_sha256"]
    if anchor!=baseline["source_anchor_sha256"]:
        raise PlannerRefusal("SOURCE_HASH_DRIFT")
    graph=evidence_graph.build(invoice_quantity=invoice_quantity)
    if graph["source_text_anchor_sha256"]!=anchor or graph["operational_plan"] is not None:
        raise PlannerRefusal("GRAPH_AUTHORITY_DRIFT")
    rows=[]
    for req in case["candidate_requests"]:
        rid=req["id"]
        covered=sorted(set(req["potential_coverage"]) & obligations)
        if not covered:
            continue
        across={}
        for name,scores in evidence_graph.PROFILES.items():
            effort,delay,burden=scores[rid]
            weighted=sum(WEIGHTS[o] for o in covered)
            friction=effort+delay+burden
            across[name]={"effort":effort,"delay":delay,"burden":burden,
                          "weighted_coverage":weighted,
                          "fictional_efficiency":round(weighted/friction,4)}
        rows.append({"request_id":rid,"may_address":covered,
                     "does_not_resolve":True,
                     "scores_by_profile":across,
                     "source":"FICTIONAL_REQUEST_NOT_ACQUIRED"})
    def ordered(profile_name):
        return sorted(rows,key=lambda r:(-r["scores_by_profile"][profile_name]["fictional_efficiency"],
                                           r["request_id"]))
    selected=ordered(profile)
    leaders={name:(ordered(name)[0]["request_id"] if rows else None)
             for name in ALLOWED_PROFILES}
    stability=("STOP_NO_OPEN_OBLIGATIONS" if not obligations else
               "NO_CANDIDATE" if not rows else
               "STABLE_UNDER_TESTED_PROFILES" if len(set(leaders.values()))==1 else
               "SENSITIVE_TO_ASSUMPTIONS")
    diff=(indie_core.compare(baseline,case)
          if case["hypothesis"]["hypothetical_only"] else
          {"source_unchanged":True,"opened_checks":[],"resolved_checks":[],
           "opened_obligations":[],"operational_plan_authorized":False})
    output={"version":VERSION,"case_id":case["case_id"],
            "selected_profile":profile,"profile_options":list(ALLOWED_PROFILES),
            "synthetic_only":True,"model_inference_performed":False,
            "historical_muse_result_is_not_for_this_scenario":True,
            "source_anchor_sha256":anchor,
            "hypothetical_branch":case["hypothesis"]["hypothetical_only"],
            "hypothetical_invoice_quantity":invoice_quantity,
            "open_obligations":sorted(obligations),
            "requests":selected,"rank_winner_by_profile":leaders,
            "ranking_stability":stability,
            "minimal_coverage_sets":case["minimal_sets"],
            "scenario_assumptions_not_real_world_costs":True,
            "score_semantics":"WEIGHTED_POTENTIAL_COVERAGE_DIVIDED_BY_ASSUMED_EFFORT_DELAY_BURDEN_NOT_PROBABILITY",
            "potential_coverage_not_verified_resolution":True,
            "graph_authority":"INSUFFICIENT_AUTHORITY",
            "human_review_required":True,"operational_plan":None,
            "execute_request_authorized":False,
            "changes":diff,"source_documents_unchanged":True,
            "technical_method":"EXACT_INCLUSION_MINIMAL_SETS_PLUS_DETERMINISTIC_SCENARIO_RANKING"}
    output["result_sha256"]=_digest(output)
    return output

def spotlight():
    claims=indie_core.source_claims()
    candidate=claims["invoice.quantity"]
    key=candidate["document"]
    text=indie_core.DOCS[key]
    lines=text.splitlines()
    matches=[i for i,line in enumerate(lines)
             if line==candidate["quote"]]
    if len(matches)!=1 or matches[0]+1!=candidate["line"]:
        raise PlannerRefusal("SPOTLIGHT_SOURCE_BINDING_REFUSED")
    from synthetic_pdf import PDF_NAMES
    import muse_contract
    pdf=PDF_NAMES.get(key)
    if pdf is None:
        raise PlannerRefusal("NO_WHITELISTED_PDF_FOR_SOURCE")
    # Bind the displayed text to the same independently pinned PDF commitment.
    if pdf not in muse_contract.verified_pdf_bytes():
        raise PlannerRefusal("PDF_PIN_NOT_VERIFIED")
    return {"kind":"DF021_DETERMINISTIC_SOURCE_SPOTLIGHT",
            "field":"invoice.quantity","value":candidate["value"],
            "quote":candidate["quote"],"document":key,"source_line":candidate["line"],
            "text_lines":lines,"source_text_sha256":candidate["source_sha256"],
            "pdf_url":"/api/pdf/invoice.pdf" if key=="invoice.txt" else None,
            "pdf_page":1,"pdf_region_status":"NOT_MODEL_LOCALIZED",
            "binding":"EXACT_SOURCE_TEXT_LINE","issuer_authenticated":False,
            "model_generated_bbox":False,"document_is_synthetic":True}
