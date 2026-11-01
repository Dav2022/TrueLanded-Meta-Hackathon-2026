"""TrueLanded DF-068 — deterministic cross-document evidence adjudication.

Source-typed, shipment-bound evidence, explicit uncertainty, immutable
content-addressed justification DAG, and non-authoritative document delta.

This engine NEVER reads raw user documents or calls models/network. The
caller must supply prior source-bound observations. Real-case conclusions
remain provisional and the manual-source-reading flag is NOT final approval.
"""
from __future__ import annotations

import copy
import dataclasses
import hashlib
import json
import re
from collections import defaultdict
from typing import Any

SCHEMA = "df068/input-source-bound-v1"
RESULT_SCHEMA = "df068/adjudication-v1"
ROLES = {"bill_of_lading", "physical_inspection", "commercial_invoice"}
FIELDS = {"declared_packages", "inspected_packages", "commercial_units", "gross_weight"}
UNITS = {"packages", "pieces", "kg"}
EXPECTED = {
    "bill_of_lading": {("declared_packages", "packages")},
    "physical_inspection": {("inspected_packages", "packages")},
    "commercial_invoice": {("commercial_units", "pieces"), ("gross_weight", "kg")},
}
VISUAL = {"prior_visual_correlated", "ocr_unconfirmed"}  # final approval requires separate trusted reviewer service
OCR_GATES = {
    "HOLD_INCOMPLETE_READ_STABILITY",
    "BLOCK_CONTRADICTORY_OCR_NUMERALS",
    "STABLE_OCR_PROPOSAL_PENDING_HUMAN",
    "ABSTAIN_NO_READ",
    "NOT_APPLICABLE",
}
SHA = re.compile(r"^[0-9a-f]{64}$")
ID = re.compile(r"^[A-Z0-9_]{2,55}$")
ALLOWED_INPUT = {"schema", "case_alias", "documents", "observations", "privacy_gate"}
DOC_FIELDS = {"id", "role", "source_sha256", "case_alias", "page_count"}
OB_FIELDS = {"id", "document_id", "source_sha256", "page", "field", "unit",
             "value", "visual_status", "ocr_gate", "support_label"}
PRIV_FIELDS = {"outbound_approved", "human_privacy_review_complete", "real_sources_local_only"}

class EvidenceRejected(ValueError):
    pass

def canonical(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")

def fingerprint(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()

def _exact(obj: Any, keys: set[str], label: str) -> None:
    if type(obj) is not dict or set(obj) != keys:
        raise EvidenceRejected(label + "_EXACT_SCHEMA")

def _sha(value: Any) -> None:
    if type(value) is not str or not SHA.fullmatch(value):
        raise EvidenceRejected("SOURCE_HASH_INVALID")

def _id(value: Any) -> None:
    if type(value) is not str or not ID.fullmatch(value):
        raise EvidenceRejected("DOCUMENT_OR_CLAIM_ID_INVALID")

def validate(request: dict) -> dict:
    _exact(request, ALLOWED_INPUT, "INPUT")
    if request["schema"] != SCHEMA:
        raise EvidenceRejected("INPUT_SCHEMA_UNSUPPORTED")
    _id(request["case_alias"])
    _exact(request["privacy_gate"], PRIV_FIELDS, "PRIVACY")
    p = request["privacy_gate"]
    for v in p.values():
        if type(v) is not bool:
            raise EvidenceRejected("PRIVACY_FLAGS_NOT_BOOLEAN")
    if p["outbound_approved"] or p["human_privacy_review_complete"]:
        # This module cannot receive or issue approval to transfer real sources.
        raise EvidenceRejected("OUTBOUND_APPROVAL_CANNOT_BE_SELF_ASSERTED")
    if type(request["documents"]) is not list or not 1 <= len(request["documents"]) <= 12:
        raise EvidenceRejected("DOCUMENT_COUNT_INVALID")
    documents = {}
    for doc in request["documents"]:
        _exact(doc, DOC_FIELDS, "DOCUMENT")
        _id(doc["id"])
        if doc["id"] in documents:
            raise EvidenceRejected("DUPLICATE_DOCUMENT_ID")
        if doc["role"] not in ROLES or doc["case_alias"] != request["case_alias"]:
            raise EvidenceRejected("ROLE_OR_SHIPMENT_MISMATCH")
        _sha(doc["source_sha256"])
        if type(doc["page_count"]) is not int or not 1 <= doc["page_count"] <= 200:
            raise EvidenceRejected("DOCUMENT_PAGE_COUNT_INVALID")
        if any(x["source_sha256"] == doc["source_sha256"] for x in documents.values()):
            raise EvidenceRejected("SAME_SOURCE_CANNOT_IMPERSONATE_DIFFERENT_ROLE")
        documents[doc["id"]] = doc
    if type(request["observations"]) is not list or len(request["observations"]) > 100:
        raise EvidenceRejected("OBSERVATION_LIST_INVALID")
    ids = set()
    for obs in request["observations"]:
        _exact(obs, OB_FIELDS, "OBSERVATION")
        _id(obs["id"])
        if obs["id"] in ids:
            raise EvidenceRejected("DUPLICATE_OBSERVATION_ID")
        ids.add(obs["id"])
        doc = documents.get(obs["document_id"])
        if doc is None:
            raise EvidenceRejected("ORPHAN_OBSERVATION")
        _sha(obs["source_sha256"])
        if obs["source_sha256"] != doc["source_sha256"]:
            raise EvidenceRejected("OBSERVATION_CROSS_SOURCE_HASH")
        if type(obs["page"]) is not int or not 1 <= obs["page"] <= doc["page_count"]:
            raise EvidenceRejected("OBSERVATION_PAGE_OUT_OF_RANGE")
        if obs["field"] not in FIELDS or obs["unit"] not in UNITS:
            raise EvidenceRejected("UNKNOWN_FIELD_OR_UNIT")
        if (obs["field"], obs["unit"]) not in EXPECTED[doc["role"]]:
            raise EvidenceRejected("FIELD_UNIT_SOURCE_ROLE_INCOMPATIBLE")
        if type(obs["value"]) is not int or not 0 <= obs["value"] <= 10000000:
            raise EvidenceRejected("NONINTEGER_OR_IMPOSSIBLE_COUNT")
        if obs["visual_status"] not in VISUAL or obs["ocr_gate"] not in OCR_GATES:
            raise EvidenceRejected("UNSUPPORTED_EVIDENCE_REVIEW_STATE")
        if (type(obs["support_label"]) is not str or
                not 1 <= len(obs["support_label"]) <= 85 or
                any(ch in obs["support_label"] for ch in "<>\\\r\n")):
            raise EvidenceRejected("PUBLIC_SUPPORT_LABEL_INVALID")
        if doc["role"] == "physical_inspection" and obs["field"] == "inspected_packages":
            # Handwritten evidence marked OCR stable is not promoted solely from OCR.
            if obs["visual_status"] == "ocr_unconfirmed" and obs["ocr_gate"] == "NOT_APPLICABLE":
                raise EvidenceRejected("OCR_UNKNOWN_FOR_UNCONFIRMED_INSPECTION")
    return request

@dataclasses.dataclass(frozen=True)
class GraphNode:
    id: str
    type: str
    label: str
    depends_on: tuple[str, ...]
    properties: dict
    evidence_sha256: str

class Graph:
    def __init__(self):
        self.nodes: list[GraphNode] = []
        self.by_id = {}

    def add(self, name: str, kind: str, label: str,
            dependencies: tuple[str, ...] = (), **properties: Any) -> GraphNode:
        _id(name)
        if name in self.by_id:
            raise EvidenceRejected("DUPLICATE_GRAPH_NODE")
        for dep in dependencies:
            if dep not in self.by_id:
                raise EvidenceRejected("DAG_DEPENDENCY_MISSING")
        content = {"id": name, "type": kind, "label": label,
                   "depends_on": list(dependencies), "properties": properties,
                   "parent_hashes": [self.by_id[d].evidence_sha256 for d in dependencies]}
        node = GraphNode(name, kind, label, dependencies, properties,
                         fingerprint(content))
        self.by_id[name] = node
        self.nodes.append(node)
        return node

    def export(self) -> list[dict]:
        return [dataclasses.asdict(node) for node in self.nodes]

def adjudicate(data: dict) -> dict:
    """Never infer legal liability, missing SKU, actual arrival or financial loss."""
    validate(data)
    frozen = copy.deepcopy(data)
    graph = Graph()
    case = frozen["case_alias"]
    graph.add("CASE_CONTEXT", "context", "Expediente de un solo embarque",
              (), case_alias=case, privacy_outbound=False)
    docs = {d["id"]: d for d in frozen["documents"]}
    role_to_doc_ids: dict[str, list[str]] = defaultdict(list)
    for doc in sorted(frozen["documents"], key=lambda x: x["id"]):
        role_to_doc_ids[doc["role"]].append(doc["id"])
        graph.add("DOC_" + doc["id"], "primary_document",
                  {"bill_of_lading": "B/L", "physical_inspection": "Acta de examen",
                   "commercial_invoice": "Factura comercial"}[doc["role"]],
                  ("CASE_CONTEXT",),
                  role=doc["role"], source_sha256=doc["source_sha256"],
                  pages=doc["page_count"], document_id=doc["id"])
    by_field: dict[str, list[dict]] = defaultdict(list)
    excluded = []
    vulnerabilities = []
    human_required = []
    for obs in sorted(frozen["observations"], key=lambda x: x["id"]):
        doc = docs[obs["document_id"]]
        graph.add("OBS_" + obs["id"], "source_observation",
                  obs["support_label"], ("DOC_" + doc["id"],),
                  field=obs["field"], value=obs["value"], unit=obs["unit"],
                  source_sha256=obs["source_sha256"], page=obs["page"],
                  visual_status=obs["visual_status"], ocr_gate=obs["ocr_gate"])
        by_field[obs["field"]].append(obs)
        if obs["field"] in ("commercial_units", "gross_weight"):
            excluded.append({"observation_id": obs["id"],
                "reason": "INCOMPATIBLE_QUANTITY_DIMENSION",
                "unit": obs["unit"], "field": obs["field"]})
            graph.add("EXC_" + obs["id"], "excluded_quantity",
                      "No comparar unidades comerciales o peso con bultos",
                      ("OBS_" + obs["id"],),
                      role=doc["role"], dimension=obs["unit"])
        if obs["ocr_gate"] in ("HOLD_INCOMPLETE_READ_STABILITY",
                               "BLOCK_CONTRADICTORY_OCR_NUMERALS", "ABSTAIN_NO_READ"):
            vulnerabilities.append({"observation_id": obs["id"],
                "gate": obs["ocr_gate"],
                "requires_human": True})
            graph.add("WARN_" + obs["id"], "visual_uncertainty",
                      "La lectura automática no es concluyente",
                      ("OBS_" + obs["id"],), ocr_gate=obs["ocr_gate"])
        if True:  # no final review can be asserted inside this untrusted input
            human_required.append(obs["id"])
    primary = ("declared_packages", "inspected_packages")
    groups: dict[str, dict] = {}
    for field in primary:
        entries = by_field.get(field, [])
        approved = [x for x in entries if x["visual_status"] != "ocr_unconfirmed"]
        values = set(x["value"] for x in approved)
        if len(values) > 1:
            groups[field] = {"status": "CONFLICTING_VISUAL_PRIMARY_VALUES",
                             "value": None, "source_obs": [x["id"] for x in approved]}
        elif len(values) == 1:
            groups[field] = {"status": "PRIMARY_VALUE_FROM_PRIOR_VISUAL",
                             "value": next(iter(values)),
                             "source_obs": [x["id"] for x in approved]}
        else:
            groups[field] = {"status": "NO_VISUALLY_CORRELATED_PRIMARY",
                             "value": None, "source_obs": []}
    cross = {"status": "", "declared": groups["declared_packages"]["value"],
             "inspected": groups["inspected_packages"]["value"],
             "difference": None,
             "source_observations": [],
             "physical_shortage_confirmed": False,
             "review_final_approved": False}
    if any(groups[f]["status"] == "CONFLICTING_VISUAL_PRIMARY_VALUES" for f in primary):
        cross["status"] = "BLOCKED_CONFLICTING_PRIMARY_DOCUMENT_EVIDENCE"
    elif any(groups[f]["value"] is None for f in primary):
        cross["status"] = "BLOCKED_INSUFFICIENT_VISUALLY_CORRELATED_SOURCES"
    else:
        declared, inspected = (groups[f]["value"] for f in primary)
        delta = declared - inspected
        dependencies = tuple("OBS_" + key for f in primary for key in groups[f]["source_obs"])
        source_ids = [key for f in primary for key in groups[f]["source_obs"]]
        cross.update(difference=delta, source_observations=source_ids,
                     status="DOCUMENTARY_QUANTITY_DIFFERENCE_FOR_REVIEW")
        graph.add("ARITHMETIC_DELTA", "derived_documentary_arithmetic",
                  "Diferencia aritmética de bultos entre fuentes", dependencies,
                  declared=declared, inspected=inspected, difference=delta,
                  formula="declared_packages_minus_inspected_packages",
                  assertion_of_physical_shortage=False)
        if delta < 0:
            cross["status"] = "DOCUMENTARY_QUANTITY_SURPLUS_FOR_REVIEW"
        elif delta == 0:
            cross["status"] = "NO_DOCUMENTARY_PACKAGE_DIFFERENCE_FOR_REVIEW"
    warnings = []
    if vulnerabilities:
        warnings.append("OCR_VISUAL_UNSTABLE")
    if human_required:
        warnings.append("FINAL_HUMAN_SOURCE_REVIEW_PENDING")
    if excluded:
        warnings.append("NONCOMPARABLE_UNITS_EXCLUDED")
    if cross["status"].startswith("BLOCKED"):
        warnings.append("PRIMARY_EVIDENCE_BLOCKED")
    for idx, label in enumerate((
        "No se identifica qué bultos o SKU faltan",
        "No se atribuye responsabilidad al transportista u otro tercero",
        "No se demuestra daño patrimonial ni derecho a reintegro",
        "No se infiere un faltante por diferencias de peso o unidades de factura",
        "El hash vincula bytes, no autentica al emisor",
    ), start=1):
        graph.add("LIMIT_" + str(idx), "inference_prohibition", label,
                  ("CASE_CONTEXT",), cannot_prove=True)
    review = {"privacy_outbound_allowed": False,
              "data_export_approved": False,
              "human_source_final_approved": False,
              "automatic_customs_action_authorized": False,
              "source_stability_uncertainties": vulnerabilities,
              "human_confirmation_needed_for": sorted(human_required),
              "independent_ocr_not_legally_conclusive": True}
    if cross["status"] == "DOCUMENTARY_QUANTITY_DIFFERENCE_FOR_REVIEW":
        dependencies = ("ARITHMETIC_DELTA",)
    else:
        dependencies = ("CASE_CONTEXT",)
    graph.add("DECISION_SUMMARY", "decision",
              "Conclusión documental preliminar, no decisión aduanera",
              dependencies, adjudication_status=cross["status"],
              human_approved=review["human_source_final_approved"],
              published=False)
    result = {"schema": RESULT_SCHEMA, "case_alias": case,
              "source_input_sha256": fingerprint(frozen),
              "adjudication": cross, "primary_groups": groups,
              "excluded_noncomparable": excluded, "warnings": sorted(set(warnings)),
              "review": review, "evidence_graph": graph.export(),
              "lineage_root_sha256": graph.by_id["DECISION_SUMMARY"].evidence_sha256,
              "source_identity_authenticated": False,
              "legal_entitlement_determined": False,
              "actual_missing_goods_identified": False,
              "external_calls": 0}
    return result

def public_projection(result: dict) -> dict:
    """Privacy-constrained UI view. Never expose original source SHA/private IDs."""
    if result.get("schema") != RESULT_SCHEMA:
        raise EvidenceRejected("OUTPUT_SCHEMA")
    compact = copy.deepcopy(result)
    compact.pop("source_input_sha256", None)
    compact.pop("lineage_root_sha256", None)
    for node in compact["evidence_graph"]:
        node.pop("evidence_sha256", None)
        node["properties"].pop("source_sha256", None)
        node["properties"].pop("document_id", None)
    return compact
