"""DF-023L local capture protocol: archive HTTP evidence BEFORE validation.

NO network transport; NO API credentials; no public release; no signed provider
attestation. A future separately authorized adapter may use this interface.
Captures are untrusted until origin provenance is established independently.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json
import df023j_plus_novel_muse as novel
import df023l_offline_diagnostics as diag

CAPTURE_FILE="UNTRUSTED_HTTP_BODY_PRIVATE.bin"
METADATA_FILE="HTTP_CAPTURE_METADATA_PRIVATE.json"
REVIEW_FILE="LITERAL_GATE_REVIEW_PRIVATE.json"
class CaptureRefusal(ValueError):pass

def sha(data):return sha256(data).hexdigest()
def write_new(path,raw):
    with Path(path).open("xb") as f:f.write(raw)
def save(private, pack, status, body):
    """Write untrusted body first, even if not JSON, HTTP error or bad quotes.

    Use only a NEW empty private folder. Never overwrite a previous attempt.
    No origin/authenticity assertions are made from captured response content.
    """
    novel.validate_pack(pack)
    dest=Path(private)
    if not dest.is_dir() or dest.is_symlink():
        raise CaptureRefusal("PRIVATE_DESTINATION_MISSING")
    if any((dest/name).exists() for name in
           (CAPTURE_FILE,METADATA_FILE,REVIEW_FILE)):
        raise CaptureRefusal("EXISTING_CAPTURE_REFUSE_OVERWRITE")
    if not isinstance(body,bytes) or len(body)>diag.MAX_BYTES:
        raise CaptureRefusal("BOUNDED_BODY_REQUIRED")
    if type(status) is not int or not 100<=status<=599:
        raise CaptureRefusal("INVALID_HTTP_STATUS")
    write_new(dest/CAPTURE_FILE,body)
    meta={
       "gate":"UNTRUSTED_HTTP_CAPTURE_WRITTEN_BEFORE_VERIFICATION",
       "http_status":status,"body_sha256":sha(body),"bytes":len(body),
       "pack_sha256":novel.digest(pack),
       "provider_origin_authenticated":False,
       "provider_cryptographically_signed":False,
       "model_inference_verified":False,
       "source_issuer_authenticated":False,
       "new_network_requests":0,
       "public_release_approved":False,
    }
    write_new(dest/METADATA_FILE,novel.encoded(meta)+b"\n")
    result=diag.diagnose(pack,status,body)
    result.update({
       "http_capture_sha256":meta["body_sha256"],
       "origin_of_supplied_bytes":"UNATTESTED_OFFLINE_INPUT",
       "not_a_live_provider_receipt":True,
       "provider_origin_authenticated":False,
    })
    write_new(dest/REVIEW_FILE,novel.encoded(result)+b"\n")
    return {k:result.get(k) for k in (
       "gate","category","status","body_sha256","body_bytes",
       "local_gate_code","literal_fields_verified",
       "not_a_live_provider_receipt","human_review_required")}

def audit(private,pack):
    novel.validate_pack(pack)
    dest=Path(private)
    try:
        meta=json.loads((dest/METADATA_FILE).read_text("utf8"))
        review=json.loads((dest/REVIEW_FILE).read_text("utf8"))
        body=(dest/CAPTURE_FILE).read_bytes()
    except (OSError,UnicodeError,ValueError):
        raise CaptureRefusal("CAPTURE_FILES_UNAVAILABLE") from None
    if (meta.get("body_sha256")!=sha(body)
       or meta.get("bytes")!=len(body)
       or meta.get("pack_sha256")!=novel.digest(pack)
       or meta.get("model_inference_verified") is not False
       or meta.get("provider_origin_authenticated") is not False):
        raise CaptureRefusal("CAPTURE_INTEGRITY_REFUSED")
    rechecked=diag.diagnose(pack,meta["http_status"],body)
    for key in ("gate","category","status","body_sha256",
                "literal_fields_verified","source_pack_sha256"):
        if rechecked.get(key)!=review.get(key):
            raise CaptureRefusal("RECORDED_REVIEW_MISMATCH")
    if review.get("not_a_live_provider_receipt") is not True:
        raise CaptureRefusal("UNTRUSTED_ORIGIN_CLAIM_CHANGED")
    return {"gate":"DF023L_LOCAL_CAPTURE_REPLAY_PASS_UNATTESTED",
            "body_sha256":sha(body),
            "http_status":meta["http_status"],
            "literal_fields_verified":rechecked["literal_fields_verified"],
            "provider_origin_authenticated":False,
            "real_meta_inference_proven":False,
            "no_http_requests_performed":True}
