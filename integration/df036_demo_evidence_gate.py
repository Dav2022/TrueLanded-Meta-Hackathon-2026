"""DF036 fail-closed distinction of an owner's Meta attempt vs mock/replay.

Never claims provider authentication from a local receipt; no I/O beyond private
files; no network, keys, raw body or source lines in output.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json
import df023j_plus_novel_muse as novel
import df023l_offline_diagnostics as diag
import df023l_capture_protocol as capture
import muse_cli

class EvidenceRefusal(ValueError):pass

def _json(path):
 try:
  if path.is_symlink() or path.stat().st_size>170000:raise EvidenceRefusal('PRIVATE_FILE_UNSAFE')
  obj=json.loads(path.read_text('utf8'))
 except (OSError,UnicodeError,ValueError):raise EvidenceRefusal('PRIVATE_EVIDENCE_MISSING_OR_INVALID') from None
 if not isinstance(obj,dict):raise EvidenceRefusal('PRIVATE_OBJECT_EXPECTED')
 return obj

def inspect_attempt(private):
 """Independently verify *local* one-shot process artifacts; never infer origin."""
 root=Path(private)
 if not root.is_dir() or root.is_symlink():raise EvidenceRefusal('PRIVATE_FOLDER_REQUIRED')
 lock=_json(root/muse_cli.LOCK)
 pack=_json(root/muse_cli.PACK)
 novel.validate_pack(pack)
 req=diag.proposed_request(pack)
 if (lock.get('gate')!='ONE_LIVE_ATTEMPT_COMMITTED_BEFORE_NETWORK'
     or lock.get('model')!='muse-spark-1.3'
     or lock.get('request_sha256')!=novel.digest(req)
     or lock.get('pack_sha256')!=novel.digest(pack)
     or lock.get('max_attempts')!=1 or lock.get('retry') is not False
     or lock.get('public_release_approved') is not False):
  raise EvidenceRefusal('ONE_SHOT_LOCK_OR_SOURCE_MISMATCH')
 if not (root/capture.CAPTURE_FILE).is_file():
  return {'gate':'DF036_LOCK_EXISTS_WITHOUT_CAPTURE','model':'muse-spark-1.3',
          'attempt_logged_locally':True,'provider_response_observed':False,
          'inference_proven':False,'human_review_required':True}
 record=capture.audit(root,pack)
 meta=_json(root/capture.METADATA_FILE)
 body=(root/capture.CAPTURE_FILE).read_bytes()
 if sha256(body).hexdigest()!=record['body_sha256']:
  raise EvidenceRefusal('CAPTURE_HASH_DRIFT')
 # Model name inside a response is only a self-reported value, not a signature.
 try: obj=json.loads(body)
 except (UnicodeError,ValueError):obj=None
 claimed_model=obj.get('model') if isinstance(obj,dict) else None
 reported_model_matches=claimed_model=='muse-spark-1.3'
 usage=obj.get('usage') if isinstance(obj,dict) else None
 totals={}
 if isinstance(usage,dict):
  for k in ('prompt_tokens','completion_tokens','total_tokens'):
   v=usage.get(k)
   if type(v) is int and 0<=v<=10000000:totals[k]=v
 return {'gate':'DF036_CAPTURE_LOCAL_CHAIN_VALID_NOT_PROVIDER_ATTESTED',
   'model_requested':'muse-spark-1.3',
   'model_self_report_matches':reported_model_matches,
   'attempt_logged_locally':True,'http_status':record['http_status'],
   'capture_sha256':record['body_sha256'],
   'source_literals_verified':record['literal_fields_verified'],
   'local_source_gate_passed':record['literal_fields_verified']==18 and record['http_status']==200,
   'usage_reported_unattested':totals,
   'meta_inference_proven_independently':False,
   'provider_signed':False,'safe_for_publication':False,
   'human_review_required':True}

def classify_demo(mode,private=None):
 if mode=='mock':return {'mode':'SIMULATED_OFFLINE_NOT_META_INFERENCE','meta_inference_proven':False}
 if mode=='replay':return {'mode':'OWNER_DERIVED_HISTORICAL_REPLAY_NOT_NEW_INFERENCE','meta_inference_proven':False}
 if mode!='private-capture' or not private:raise EvidenceRefusal('EXPLICIT_MODE_AND_PRIVATE_FOLDER_REQUIRED')
 out=inspect_attempt(private)
 return {'mode':'PRIVATE_LOCAL_CAPTURE_UNATTESTED','meta_inference_proven':False,'local_evidence':out}