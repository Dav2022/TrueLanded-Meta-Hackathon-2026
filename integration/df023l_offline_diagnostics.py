"""DF-023L: pure offline response diagnostics; no network, no credentials.
The earlier failed one-shot lock is never read or modified by this module.
Use response snapshots supplied by explicit test fixtures only.
"""
from __future__ import annotations
import hashlib
import json
import re
import df023j_plus_novel_muse as source

MAX_BYTES=160000
class DiagnosticRefusal(ValueError):pass

def proposed_request(fictional_pack):
    request=source.build_request(fictional_pack)
    request["reasoning_effort"]="low"
    request["max_completion_tokens"]=3200
    if request.get("store") is not False or request.get("stream") is not False:
        raise DiagnosticRefusal("REQUEST_CONTRACT_REFUSED")
    return request

def safe_error(raw,http_status):
    if not isinstance(raw,bytes) or len(raw)>MAX_BYTES:
        raise DiagnosticRefusal("BODY_UNAVAILABLE_OR_OVERSIZED")
    result={"status":http_status,"category":"HTTP_ERROR",
            "error_type":"UNKNOWN","error_code":"UNKNOWN","error_param":"NONE"}
    try:
        body=json.loads(raw)
        err=body.get("error",{}) if isinstance(body,dict) else {}
        for field,key in (("error_type","type"),("error_code","code"),
                          ("error_param","param")):
            value=err.get(key) if isinstance(err,dict) else None
            if isinstance(value,str) and re.fullmatch(r"[A-Za-z0-9_./-]{1,64}",value):
                result[field]=value
    except (ValueError,UnicodeError):
        pass
    return result

def diagnose(pack,http_status,raw):
    """Classify strictly. Never print model text, prompts, user fields or headers."""
    source.validate_pack(pack)
    if type(http_status) is not int or not 100<=http_status<=599:
        raise DiagnosticRefusal("BAD_STATUS")
    if not isinstance(raw,bytes) or len(raw)>MAX_BYTES:
        raise DiagnosticRefusal("BODY_UNAVAILABLE_OR_OVERSIZED")
    result={"gate":"DF023L_OFFLINE_DIAGNOSTIC_ONLY",
            "status":http_status,
            "body_sha256":hashlib.sha256(raw).hexdigest(),
            "body_bytes":len(raw),
            "source_pack_sha256":source.digest(pack),
            "provider_signed":False,
            "source_document_authenticated":False,
            "model_called_by_this_module":False,
            "literal_fields_verified":0,
            "human_review_required":True}
    if http_status!=200:
        result.update(safe_error(raw,http_status))
        return result
    try:
        obj=json.loads(raw)
    except (UnicodeError,ValueError):
        result["category"]="HTTP_200_NON_JSON"
        return result
    if not isinstance(obj,dict):
        result["category"]="HTTP_200_NOT_OBJECT"
        return result
    choices=obj.get("choices")
    if isinstance(choices,list) and choices and isinstance(choices[0],dict):
        finish=choices[0].get("finish_reason")
        if isinstance(finish,str) and re.fullmatch(r"[a-z_]{1,32}",finish):
            result["finish_reason"]=finish
    try:
        verdict=source.review(pack,obj)
    except source.NovelRefusal as exc:
        # Own explicit finite error tokens; no provider message content.
        result["category"]="MODEL_RESPONSE_REJECTED_BY_SOURCE_GATE"
        result["local_gate_code"]=str(exc)[:80]
        return result
    result["category"]="SOURCE_LITERAL_GATE_PASSED"
    result["literal_fields_verified"]=verdict["literal_fields_matched"]
    result["final_next_proof"]=verdict["final_next_proof"]
    result["not_issuer_authentication"]=True
    return result
