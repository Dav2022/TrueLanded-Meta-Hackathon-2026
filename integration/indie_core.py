"""TrueLanded Indie Challenge — newly authored standalone proof-question engine.

Created during the Oct 27-Nov 4, 2026 hackathon build period.
No provider SDK, no external dependencies and no actual customer documents.

This is a synthetic DEMONSTRATION OF ALGORITHM only, not a legal
decision, a tariff classifier, proof acquisition, or verification of issuer.

The source documents are new text-only mock documents, NOT PDF/OCR.
"""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from itertools import combinations
import json

VERSION="indie-standalone-proof-frontier/0.1"
DOCS={
  "invoice.txt": (
    "REFERENCE: TL-INDIE-ALPHA\n"
    "ITEM: SYNTHETIC-PUMP-CASING\n"
    "QUANTITY: 31 PCS\n"
    "UNIT PRICE: USD 4.50\n"
    "LINE TOTAL: USD 139.50\n"
  ),
  "packing.txt": (
    "REFERENCE: TL-INDIE-ALPHA\n"
    "ITEM: SYNTHETIC-PUMP-CASING\n"
    "CARTONS: 4 CTN\n"
    "UNITS PER CARTON: 7 PCS\n"
    "TOTAL UNITS: 28 PCS\n"
  ),
  "product-sheet.txt": (
    "REFERENCE: TL-INDIE-ALPHA\n"
    "ITEM: SYNTHETIC-PUMP-CASING\n"
    "MATERIAL GRADE: NOT PROVIDED\n"
    "INTENDED FUNCTION: NOT PROVIDED\n"
  ),
}
FIELD_LINES={
  "invoice.quantity": ("invoice.txt","QUANTITY"),
  "invoice.unit_price": ("invoice.txt","UNIT PRICE"),
  "invoice.line_total": ("invoice.txt","LINE TOTAL"),
  "packing.cartons": ("packing.txt","CARTONS"),
  "packing.units_each": ("packing.txt","UNITS PER CARTON"),
  "packing.total_units": ("packing.txt","TOTAL UNITS"),
  "technical.grade": ("product-sheet.txt","MATERIAL GRADE"),
  "technical.function": ("product-sheet.txt","INTENDED FUNCTION"),
}
OBLIGATIONS={
 "QTY_MISMATCH":"Clarify quantity between invoice and packing",
 "VALUE_MISMATCH":"Reconcile invoice line arithmetic",
 "PACKING_MISMATCH":"Reconcile carton arithmetic",
 "TECHNICAL_GAP":"Obtain missing material and function facts",
}
# Proposed means unverified, never acquired. Candidate scores are not costs.
PROPOSALS={
 "REQ_RECONCILED_INVOICE":("QTY_MISMATCH","VALUE_MISMATCH"),
 "REQ_PACKING_CONFIRMATION":("QTY_MISMATCH","PACKING_MISMATCH"),
 "REQ_PRICE_BREAKDOWN":("VALUE_MISMATCH",),
 "REQ_CARTON_COUNT":("PACKING_MISMATCH",),
 "REQ_TECH_SHEET":("TECHNICAL_GAP",),
 "REQ_FACTORY_CONFIRMATION":("TECHNICAL_GAP",),
}


class EngineRefusal(ValueError):
    pass


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _parse_literal(document: str, label: str) -> dict:
    matches=[(n+1,line) for n,line in enumerate(DOCS[document].splitlines())
             if line.startswith(label+": ")]
    if len(matches)!=1:
        raise EngineRefusal("AMBIGUOUS_LITERAL")
    number,line=matches[0]
    value=line[len(label)+2:]
    return {"document":document,"label":label,"value":value,
            "quote":line,"line":number,
            "source_sha256":digest(DOCS[document].encode("utf-8")),
            "source_status":"SYNTHETIC_LITERAL_NOT_AUTHENTICATED"}


def source_claims() -> dict:
    return {field:_parse_literal(document,label)
            for field,(document,label) in FIELD_LINES.items()}


def _quantity(value: str) -> int:
    left,right=value.split(" ",1)
    if right not in ("PCS","CTN"):
        raise EngineRefusal("INCOMPARABLE_UNIT")
    parsed=int(left)
    if parsed<0:
        raise EngineRefusal("NEGATIVE_QUANTITY")
    return parsed


def _money(value: str) -> Decimal:
    currency,amount=value.split(" ",1)
    if currency!="USD":
        raise EngineRefusal("INCOMPARABLE_CURRENCY")
    parsed=Decimal(amount)
    if not parsed.is_finite() or parsed<0:
        raise EngineRefusal("INVALID_CURRENCY")
    return parsed


def minimal_cover(obligations: list[str], options: dict[str, tuple[str,...]]) -> list[list[str]]:
    """Fresh straightforward exhaustive exact inclusion-minimal enumeration.

    Never interprets potential coverage as proof acquired.
    Bounded to 12 synthetic candidate requests.
    """
    if len(options)>12 or len(obligations)>8:
        raise EngineRefusal("SEARCH_BOUND_EXCEEDED")
    wanted=set(obligations)
    feasible=[]
    ids=sorted(options)
    for count in range(len(ids)+1):
        for subset in combinations(ids,count):
            reached=set()
            for name in subset:
                reached.update(options[name])
            if reached>=wanted:
                feasible.append(frozenset(subset))
    keep=[one for one in feasible if not any(other<one for other in feasible)]
    return sorted([sorted(x) for x in keep],key=lambda x:(len(x),x))


def evaluate(*, invoice_quantity: int|None=None, units_per_carton: int|None=None,
             model_suggestions: list[dict]|None=None) -> dict:
    # Hypotheses are separate branches; original source literals are immutable.
    for item in (invoice_quantity,units_per_carton):
        if item is not None and (type(item) is not int or not 0<=item<=10000):
            raise EngineRefusal("INVALID_HYPOTHESIS")
    source=source_claims()
    qty=_quantity(source["invoice.quantity"]["value"])
    price=_money(source["invoice.unit_price"]["value"])
    line_total=_money(source["invoice.line_total"]["value"])
    cartons=_quantity(source["packing.cartons"]["value"])
    per_carton=_quantity(source["packing.units_each"]["value"])
    packed=_quantity(source["packing.total_units"]["value"])
    hypothetical=invoice_quantity is not None or units_per_carton is not None
    q=qty if invoice_quantity is None else invoice_quantity
    each=per_carton if units_per_carton is None else units_per_carton
    checks={
       "invoice_vs_packing":{
          "status":"MATCH" if q==packed else "CONFLICT",
          "depends_on":["invoice.quantity","packing.total_units"],
          "calculation":f"{q} PCS vs {packed} PCS"},
       "invoice_value_arithmetic":{
          "status":"MATCH" if Decimal(q)*price==line_total else "CONFLICT",
          "depends_on":["invoice.quantity","invoice.unit_price","invoice.line_total"],
          "calculation":f"{q} × USD {price:.2f} = USD {(Decimal(q)*price):.2f}; stated USD {line_total:.2f}"},
       "packing_carton_arithmetic":{
          "status":"MATCH" if cartons*each==packed else "CONFLICT",
          "depends_on":["packing.cartons","packing.units_each","packing.total_units"],
          "calculation":f"{cartons} cartons × {each} = {cartons*each}; stated {packed}"},
    }
    obligations=[]
    if checks["invoice_vs_packing"]["status"]=="CONFLICT":
        obligations.append("QTY_MISMATCH")
    if checks["invoice_value_arithmetic"]["status"]=="CONFLICT":
        obligations.append("VALUE_MISMATCH")
    if checks["packing_carton_arithmetic"]["status"]=="CONFLICT":
        obligations.append("PACKING_MISMATCH")
    if any(source[x]["value"]=="NOT PROVIDED" for x in
           ("technical.grade","technical.function")):
        obligations.append("TECHNICAL_GAP")
    obligations.sort()
    available={name:targets for name,targets in PROPOSALS.items()
               if set(targets)&set(obligations)}
    option_sets=minimal_cover(obligations,available)
    docs={k:{"sha256":digest(v.encode()),"lines":len(v.splitlines()),
             "text":v,"source_status":"SYNTHETIC_ONLY"} for k,v in DOCS.items()}
    anchor=digest(json.dumps({"files":{k:v["sha256"] for k,v in docs.items()},
                              "claims":source},sort_keys=True).encode())
    suggestions=[]
    if model_suggestions is not None:
        if not isinstance(model_suggestions,list) or len(model_suggestions)>20:
            raise EngineRefusal("MODEL_CANDIDATES_SCHEMA_REFUSED")
        for suggestion in model_suggestions:
            if not isinstance(suggestion,dict) or set(suggestion)!={"field","document","quote","value"}:
                raise EngineRefusal("MODEL_CANDIDATE_SHAPE_REFUSED")
            field=suggestion["field"]
            ref=source.get(field)
            matched=(ref is not None and suggestion["document"]==ref["document"]
                     and suggestion["quote"]==ref["quote"] and suggestion["value"]==ref["value"])
            suggestions.append({
                "field":field if type(field) is str and len(field)<=80 else "REJECTED",
                "status":"SOURCE_LITERAL_MATCHED_NOT_VERIFIED" if matched
                         else "REJECTED_MISSING_OR_INCORRECT_SOURCE",
                "source_ref":field if matched else None,
            })
    return {
      "version":VERSION,
      "case_id":"TL-INDIE-ALPHA",
      "synthetic_only":True,
      "source_docs":docs,
      "claims":source,
      "source_anchor_sha256":anchor,
      "hypothesis":{"invoice_quantity":invoice_quantity,
                    "units_per_carton":units_per_carton,
                    "hypothetical_only":hypothetical},
      "checks":checks,
      "obligations":[{"id":id,"description":OBLIGATIONS[id],
                      "status":"OPEN_UNVERIFIED"} for id in obligations],
      "candidate_requests":[{"id":k,
                              "potential_coverage":sorted(set(v)&set(obligations)),
                              "execution_authorized":False} for k,v in sorted(available.items())],
      "minimal_sets":option_sets,
      "model_candidates":suggestions,
      "claim_review_status":"UNVERIFIED",
      "issuer_authenticity":"UNKNOWN",
      "policy_authority":"PENDING_REVIEW",
      "plan":None,"plan_status":"INSUFFICIENT_AUTHORITY",
      "no_external_model_calls":True,
      "no_source_mutation":True,
      "source_input_kind":"ORIGINAL_SYNTHETIC_TEXT_NOT_PDF",
    }


def compare(base: dict, hypothetical: dict) -> dict:
    if (base["source_anchor_sha256"]!=hypothetical["source_anchor_sha256"]
        or base["hypothesis"]["hypothetical_only"]
        or not hypothetical["hypothesis"]["hypothetical_only"]):
        raise EngineRefusal("INVALID_COMPARISON")
    b=base["checks"]; h=hypothetical["checks"]
    new=[x for x in b if b[x]["status"]=="MATCH" and h[x]["status"]=="CONFLICT"]
    resolved=[x for x in b if b[x]["status"]=="CONFLICT" and h[x]["status"]=="MATCH"]
    return {"source_unchanged":True,"opened_checks":new,"resolved_checks":resolved,
            "opened_obligations":sorted({x["id"] for x in hypothetical["obligations"]}
                                        -{x["id"] for x in base["obligations"]}),
            "operational_plan_authorized":False}
