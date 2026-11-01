"""Fresh Oct-27 Indie Evidence Frontier graph and priority sensitivity.

Builds a typed graph from independently computed synthetic source facts,
deterministic checks, open obligations and possible next-document requests.
An OPTIONAL anchored Muse candidate can add advisory *observation* edges;
the model must never add/resolve obligations, alter checks or authorize work.

No remote SDK, OCR pipeline, external document parser or network transport.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
import indie_core
import muse_contract


class EvidenceGraphRefusal(ValueError):
    pass


# FICTITIOUS points; explicit opposite assumptions expose non-robust choices.
PROFILES={
 "direct_source_is_faster":{
  "REQ_RECONCILED_INVOICE":(1,1,1),
  "REQ_PACKING_CONFIRMATION":(3,4,2),
  "REQ_PRICE_BREAKDOWN":(2,2,2),
  "REQ_CARTON_COUNT":(2,2,2),
  "REQ_TECH_SHEET":(1,2,1),
  "REQ_FACTORY_CONFIRMATION":(4,5,3),
 },
 "supplier_and_factory_are_faster":{
  "REQ_RECONCILED_INVOICE":(4,5,2),
  "REQ_PACKING_CONFIRMATION":(1,1,1),
  "REQ_PRICE_BREAKDOWN":(1,1,2),
  "REQ_CARTON_COUNT":(1,2,1),
  "REQ_TECH_SHEET":(4,5,3),
  "REQ_FACTORY_CONFIRMATION":(1,1,1),
 },
}


def fingerprint(obj)->str:
    return sha256(json.dumps(obj,sort_keys=True,
                              separators=(",",":"),ensure_ascii=True).encode()).hexdigest()


def priority_sensitivity(minimal_sets:list[list[str]], profiles=None)->dict:
    profiles=PROFILES if profiles is None else profiles
    if type(minimal_sets) is not list or len(minimal_sets)>4096:
        raise EvidenceGraphRefusal("PRIORITY_SETS_INVALID")
    if type(profiles) is not dict or len(profiles)<2 or len(profiles)>6:
        raise EvidenceGraphRefusal("PRIORITY_PROFILES_INVALID")
    evaluations=[]
    winners=[]
    for profile_name,scores in profiles.items():
        if type(scores) is not dict:
            raise EvidenceGraphRefusal("PRIORITY_PROFILE_MISSING")
        priced=[]
        for i,actions in enumerate(minimal_sets):
            if type(actions) is not list or not all(a in scores for a in actions):
                raise EvidenceGraphRefusal("PRIORITY_UNKNOWN_ACTION")
            numbers=[scores[a] for a in actions]
            if any(type(v) is not tuple or len(v)!=3 or any(
                   type(n) is not int or n<1 or n>9 for n in v)
                   for v in numbers):
                raise EvidenceGraphRefusal("PRIORITY_FAKE_SCORE_INVALID")
            effort=sum(x[0] for x in numbers)
            delay=max((x[1] for x in numbers),default=0)
            burden=sum(x[2] for x in numbers)
            priced.append({"set_index":i,"request_ids":deepcopy(actions),
                           "fictional_score":effort+delay+burden,
                           "fictional_effort":effort,"fictional_delay":delay,
                           "fictional_burden":burden})
        best=min((x["fictional_score"] for x in priced),default=None)
        winning=[x["set_index"] for x in priced if x["fictional_score"]==best]
        winners.append(winning)
        evaluations.append({
            "fictional_profile":profile_name,
            "comparisons":sorted(priced,key=lambda x:(x["fictional_score"],x["request_ids"])),
            "winning_candidate_indices":winning,
        })
    if not minimal_sets:
        status="NO_SYNTHETIC_COVER_AVAILABLE"
        stable_set=None
    elif minimal_sets==[[]]:
        status="NO_ADDITIONAL_REQUEST_MODELLED"
        stable_set=[]
    elif all(len(w)==1 and w==winners[0] for w in winners):
        status="STABLE_WITHIN_FICTIONAL_PROFILES_ONLY"
        stable_set=deepcopy(minimal_sets[winners[0][0]])
    else:
        status="UNSTABLE_WITHOUT_REAL_WORLD_COST_DATA"
        stable_set=None
    return {"status":status,"profiles":evaluations,
            "stable_set_only_if_fictitious_assumptions_hold":stable_set,
            "operational_priority":None,
            "inputs_are_real_costs":False,
            "human_review_required":True}


def build(*,invoice_quantity:int|None=None,
          units_per_carton:int|None=None,
          reviewed_model:dict|None=None)->dict:
    case=indie_core.evaluate(invoice_quantity=invoice_quantity,
                             units_per_carton=units_per_carton)
    claims=case["claims"]
    if reviewed_model is not None:
        if (type(reviewed_model) is not dict or
            reviewed_model.get("kind")!="NEW_INDIE_PDF_MUSE_CANDIDATE_EVIDENCE_GRAPH"
            or reviewed_model.get("source_text_anchor_sha256")!=case["source_anchor_sha256"]
            or reviewed_model.get("authority")!="INSUFFICIENT_AUTHORITY"
            or reviewed_model.get("operational_plan") is not None
            or reviewed_model.get("model")!="muse-spark-1.3"):
            raise EvidenceGraphRefusal("MODEL_REVIEW_AUTHORITY_OR_SOURCE_NOT_TRUSTED")
        # Revalidate each source link against known immutable literal and
        # independently generated PDF hash, not model-supplied metadata.
        pdfs=muse_contract.verified_pdf_bytes()
        if reviewed_model.get("pdf_sha256")!={k:sha256(v).hexdigest()
                                              for k,v in pdfs.items()}:
            raise EvidenceGraphRefusal("MODEL_PDF_PIN_DRIFT")
    nodes=[]
    edges=[]
    for name,source in case["source_docs"].items():
        nodes.append({"id":"doc:"+name,"kind":"DOCUMENT",
                      "sha256":source["sha256"],"status":"FICTIONAL_SOURCE"})
    for field,c in sorted(claims.items()):
        nodes.append({"id":"claim:"+field,"kind":"SOURCE_CLAIM",
                      "field":field,"document":c["document"],"quote":c["quote"],
                      "line":c["line"],"status":"UNVERIFIED"})
        edges.append({"from":"doc:"+c["document"],"to":"claim:"+field,
                      "kind":"CONTAINS_LITERAL"})
    for check_id,result in sorted(case["checks"].items()):
        nodes.append({"id":"check:"+check_id,"kind":"DETERMINISTIC_CHECK",
                      "status":result["status"],"calculation":result["calculation"]})
        for source_claim_id in result["depends_on"]:
            edges.append({"from":"claim:"+source_claim_id,
                          "to":"check:"+check_id,"kind":"CHECK_DEPENDS_ON"})
    for obligation in case["obligations"]:
        key=obligation["id"]
        nodes.append({"id":"proof:"+key,"kind":"OPEN_OBLIGATION",
                      "status":"OPEN_UNVERIFIED",
                      "label":obligation["description"]})
        check_for={
         "QTY_MISMATCH":"invoice_vs_packing",
         "VALUE_MISMATCH":"invoice_value_arithmetic",
         "PACKING_MISMATCH":"packing_carton_arithmetic",
        }
        if key=="TECHNICAL_GAP":
            for field in ("technical.grade","technical.function"):
                edges.append({"from":"claim:"+field,"to":"proof:"+key,
                              "kind":"MISSING_ATTRIBUTE_REQUIRES_PROOF"})
        else:
            edges.append({"from":"check:"+check_for[key],"to":"proof:"+key,
                          "kind":"CONFLICT_OPENS_OBLIGATION"})
    for action in case["candidate_requests"]:
        nodes.append({"id":"request:"+action["id"],"kind":"PROPOSED_ACTION",
                      "status":"NOT_EXECUTED","may_execute":False})
        for proof in action["potential_coverage"]:
            edges.append({"from":"request:"+action["id"],"to":"proof:"+proof,
                          "kind":"POTENTIAL_COVERAGE_NOT_EVIDENCE"})
    candidate_count=0
    if reviewed_model is not None:
        observations=reviewed_model.get("observations")
        if type(observations) is not list or len(observations)>20:
            raise EvidenceGraphRefusal("MODEL_OBSERVATIONS_UNTRUSTED")
        for idx,obs in enumerate(observations):
            if type(obs) is not dict or obs.get("legally_verified") is not False:
                raise EvidenceGraphRefusal("MODEL_TRIES_TO_PROMOTE_SOURCE")
            ref=obs.get("source_field")
            matched=obs.get("model_candidate_status")=="MATCHED_SOURCE_LITERAL_UNVERIFIED"
            if matched:
                expected=claims.get(ref)
                if (expected is None
                    or obs.get("quote")!=expected["quote"]
                    or obs.get("pdf")!=muse_contract.synthetic_pdf.PDF_NAMES[expected["document"]]
                    or obs.get("pdf_sha256")!=reviewed_model["pdf_sha256"].get(obs["pdf"])):
                    raise EvidenceGraphRefusal("FORGED_MODEL_CLAIM_EDGE")
            elif ref is not None or obs.get("model_candidate_status")!="REJECTED_INCORRECT_LITERAL_OR_SEMANTICS":
                raise EvidenceGraphRefusal("INVALID_MODEL_REJECTION_EDGE")
            node_id=f"muse_candidate:{idx:03d}"
            nodes.append({"id":node_id,"kind":"MODEL_CANDIDATE",
                          "status":"MATCHED_UNVERIFIED" if matched else "REJECTED",
                          "field":obs.get("field"),"model":"muse-spark-1.3",
                          "cannot_open_obligations":True})
            if matched:
                edges.append({"from":node_id,"to":"claim:"+ref,
                              "kind":"SOURCE_LITERAL_MATCH_NOT_AUTHENTICITY"})
                candidate_count+=1
    ids=[x["id"] for x in nodes]
    if len(ids)!=len(set(ids)):
        raise EvidenceGraphRefusal("DUPLICATED_GRAPH_NODE")
    priority=priority_sensitivity(case["minimal_sets"])
    result={
      "version":"indie-new-evidence-graph/0.1",
      "case_id":case["case_id"],
      "synthetic_only":True,
      "source_text_anchor_sha256":case["source_anchor_sha256"],
      "branch_hypothetical":case["hypothesis"]["hypothetical_only"],
      "nodes":nodes,"edges":edges,
      "node_count":len(nodes),"edge_count":len(edges),
      "open_proof_obligation_ids":[x["id"] for x in case["obligations"]],
      "minimal_hypothetical_request_sets":deepcopy(case["minimal_sets"]),
      "priority":priority,
      "model_candidates_attached":candidate_count,
      "model_source":"REAL_RECORDED_INFERENCE_REQUIRED" if reviewed_model else "NO_MODEL_DATA",
      "no_model_created_proof":True,
      "human_review_required":True,
      "operational_plan":None,
      "operational_status":"INSUFFICIENT_AUTHORITY",
    }
    result["graph_sha256"]=fingerprint(result)
    return result


def diff(original:dict,scenario:dict)->dict:
    if (original.get("source_text_anchor_sha256")!=
        scenario.get("source_text_anchor_sha256") or
        original.get("branch_hypothetical") is not False or
        scenario.get("branch_hypothetical") is not True):
        raise EvidenceGraphRefusal("GRAPH_BRANCH_SOURCE_CHANGED")
    old=set(original["open_proof_obligation_ids"])
    new=set(scenario["open_proof_obligation_ids"])
    return {
      "resolved_proof_obligations":sorted(old-new),
      "new_proof_obligations":sorted(new-old),
      "unchanged_source_sha256":original["source_text_anchor_sha256"],
      "no_source_mutation":True,
      "no_legal_clearance":True,
    }
