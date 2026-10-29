"""DF-023M independent offline validator, run from extracted review bundle.

NOTE: Local author-issued manifest hashes are NOT provider signatures or an
independent attestation that Muse generated specific fields.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json
import re
import sys
ROOT=Path(__file__).resolve().parent
MANIFEST="DF023M_PREPUBLICATION_MANIFEST.json"
EXPECTED=(
 "df023m_server.py","df023m_verify.py","df023m_index.html",
 "df023m_style.css","df023m_ui.js","DF023M_JURY_EVIDENCE.json",
)
class ReplayRefusal(ValueError):pass
def sha(raw):return sha256(raw).hexdigest()
def canonical(info):return json.dumps(info,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode("utf8")
def source_valid(evidence):
 if (not isinstance(evidence,dict) or
     evidence.get("schema")!="DF023M_JURY_DERIVED_REPLAY_V1" or
     evidence.get("gate")!="OWNER_LOCAL_DERIVED_META_RESULT_SOURCE_VERIFIED" or
     evidence.get("model_reported")!="muse-spark-1.3" or
     evidence.get("meta_api_calls_from_this_package")!=0 or
     evidence.get("provider_signed") is not False or
     evidence.get("issuer_authenticated") is not False or
     evidence.get("human_review_required") is not True or
     evidence.get("actual_provider_response_body_embedded") is not False or
     evidence.get("ip_owner_approved_publication") is not False or
     evidence.get("public_release_approved") is not False or
     evidence.get("literal_candidates_verified_against_fictional_source")!=18 or
     evidence.get("final_next_proof")!="REQ_TECH_SHEET" or
     evidence.get("calculation_owner")!="TRUELANDED_DETERMINISTIC_CODE_NOT_MUSE"):
  raise ReplayRefusal("REPLAY_AUTHORITY_OR_MODEL_BOUNDARY")
 check=dict(evidence)
 stored=check.pop("replay_sha256",None)
 if stored!=sha(canonical(check)):
  raise ReplayRefusal("REPLAY_INTERNAL_HASH_CHANGED")
 records=evidence.get("source_documents")
 if not isinstance(records,list) or len(records)!=3:
  raise ReplayRefusal("NOT_THREE_DOCUMENTS")
 expected=("PACKING_NEW","INVOICE_REVISED_INCONSISTENT","INVOICE_REVISED_CORRECTED")
 counts=(4,7,7)
 obs=({"QTY_MISMATCH","TECHNICAL_GAP"},
      {"VALUE_MISMATCH","TECHNICAL_GAP"},
      {"TECHNICAL_GAP"})
 nexts=("REQ_RECONCILED_INVOICE","REQ_RECONCILED_INVOICE","REQ_TECH_SHEET")
 total=0
 for n,entry in enumerate(records):
  if (not isinstance(entry,dict) or entry.get("event_id")!=expected[n] or
      entry.get("source_document_authenticated") is not False or
      entry.get("human_review_required") is not True or
      entry.get("ranked_proof_request_is_executed") is not False or
      set(entry.get("open_obligations",[]))!=obs[n] or
      entry.get("top_next_proof_request")!=nexts[n]):
   raise ReplayRefusal("EXPECTED_SYNTHETIC_OBLIGATIONS_CHANGED")
  lines=entry.get("fictional_source_lines")
  if (not isinstance(lines,list) or len(lines)!=counts[n] or
      entry.get("verified_literal_line_count")!=counts[n] or
      any(not isinstance(x,str) or len(x)>190 or
      re.fullmatch(r"[A-Z ]+: [ -~]+",x) is None for x in lines)):
   raise ReplayRefusal("SOURCE_LINES_OR_CLAIMS_MISSING")
  if sha(("\n".join(lines)+"\n").encode("utf8"))!=entry.get("source_sha256"):
   raise ReplayRefusal("SOURCE_EXACT_SHA256_MISMATCH")
  if "ISSUER AUTHENTICATION: NOT VERIFIED" not in lines:
   raise ReplayRefusal("ISSUER_BASIS_CHANGED")
  total+=counts[n]
 if total!=18:raise ReplayRefusal("NOT_EIGHTEEN_LITERALS")
 if (records[1].get("newly_exposed")!=["VALUE_MISMATCH"] or
     records[2].get("conditionally_reconciled")!=["VALUE_MISMATCH"]):
  raise ReplayRefusal("PROOF_IMPACT_DELTA_CHANGED")
 return True

def verify(root=ROOT):
 root=Path(root)
 file=root/MANIFEST
 if not file.is_file() or file.is_symlink() or file.stat().st_size>20000:
  raise ReplayRefusal("MANIFEST_MISSING")
 try:manifest=json.loads(file.read_text("utf8"))
 except (OSError,UnicodeError,ValueError):raise ReplayRefusal("INVALID_MANIFEST") from None
 if (manifest.get("schema")!="DF023M_PREPUBLICATION_SNAPSHOT_V1" or
     manifest.get("public_release_approved") is not False or
     manifest.get("redistribution_license_granted") is not False or
     manifest.get("provider_signed") is not False or
     manifest.get("model_calls_during_replay")!=0 or
     manifest.get("actual_provider_response_body_embedded") is not False or
     manifest.get("private_api_credentials_embedded") is not False or
     tuple(manifest.get("exact_allowlist",()))!=EXPECTED):
  raise ReplayRefusal("MANIFEST_AUTHORITY_CONTRACT")
 if set(manifest.get("files",{}))!=set(EXPECTED) or {p.name for p in root.iterdir()}!=set(EXPECTED)|{MANIFEST}:
  raise ReplayRefusal("UNKNOWN_OR_MISSING_BUNDLE_FILE")
 for name in EXPECTED:
  file=root/name
  if not file.is_file() or file.is_symlink():
   raise ReplayRefusal("SYMLINK_OR_MISSING_SOURCE")
  raw=file.read_bytes();entry=manifest["files"][name]
  if len(raw)!=entry.get("bytes") or sha(raw)!=entry.get("sha256"):
   raise ReplayRefusal("EXPORTED_SHA256_MISMATCH")
 data=json.loads((root/"DF023M_JURY_EVIDENCE.json").read_text("utf8"))
 source_valid(data)
 if manifest["replay_sha256"]!=data["replay_sha256"]:
  raise ReplayRefusal("MANIFEST_TO_REPLAY_MISMATCH")
 return {"gate":"DF023M_LOCAL_INTEGRITY_REPLAY_PASS",
         "bundle_files":len(EXPECTED)+1,
         "real_model_call_in_this_bundle":False,
         "owner_derived_real_model_summary":True,
         "exact_fictional_source_lines":18,
         "provider_signature_verified":False,
         "human_review_required":True,
         "public_release_approved":False}
if __name__=="__main__":
 try:print(json.dumps(verify(),indent=2))
 except ReplayRefusal as e:
  print("DF023M_BUNDLE_REFUSED="+str(e),file=sys.stderr)
  raise SystemExit(2) from None
