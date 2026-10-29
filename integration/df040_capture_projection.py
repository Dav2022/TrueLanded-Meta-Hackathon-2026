"""DF040: private, replay-only projection of one locally captured response.

Never contacts Meta or changes the archived receipt. Validate lock/capture/source
again on every request. Any publicly redistributed output needs separate review.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json
import df036_demo_evidence_gate as gate
import df023j_plus_novel_muse as novel
import muse_cli
import df023l_capture_protocol as capture

class ReplayRefusal(ValueError):pass

def project(private):
    root=Path(private)
    if not root.is_dir() or root.is_symlink():raise ReplayRefusal('PRIVATE_FOLDER_REQUIRED')
    try:
        check=gate.inspect_attempt(root)
        if (check.get('gate')!='DF036_CAPTURE_LOCAL_CHAIN_VALID_NOT_PROVIDER_ATTESTED'
            or check.get('http_status')!=200
            or check.get('source_literals_verified')!=18
            or check.get('model_self_report_matches') is not True):
            raise ReplayRefusal('LOCAL_EVIDENCE_NOT_ACCEPTED')
        pack=novel.validate_pack(json.loads((root/muse_cli.PACK).read_text('utf8')))
        raw=(root/capture.CAPTURE_FILE).read_bytes()
        verdict=novel.review(pack,json.loads(raw))
        if verdict['literal_fields_matched']!=18 or len(verdict['phases'])!=3:
            raise ReplayRefusal('SOURCE_GATE_FAILED')
        docs={x['event_id']:x for x in pack['documents']}
        phases=[]
        for item in verdict['phases']:
            d=docs[item['event_id']]
            lines=d['untrusted_text'].splitlines()
            if len(lines)!=item['model_literal_fields_exactly_matched']:
                raise ReplayRefusal('LITERAL_COVERAGE_INCOMPLETE')
            phases.append({'event_id':item['event_id'],
              'fictional_source_lines':lines,'source_sha256':d['source_sha256'],
              'verified_literals':item['model_literal_fields_exactly_matched'],
              'open_obligations':item['open_obligations'],
              'newly_exposed':item['newly_exposed'],
              'conditionally_reconciled':item['conditionally_reconciled'],
              'next_best_proof':item['top_next_proof_request'],
              'source_document_authenticated':False,'human_review_required':True})
        return {'gate':'DF040_PRIVATE_OWNER_CAPTURE_DERIVED_REPLAY_PASS',
           'mode':'OWNER_EXECUTED_META_CAPTURE_REPLAY_NOT_NEW_INFERENCE',
           'model_requested':'muse-spark-1.3',
           'model_self_reported':'muse-spark-1.3',
           'local_capture_http_status':200,
           'capture_sha256':sha256(raw).hexdigest(),
           'request_sha256':verdict['request_sha256'],
           'source_pack_sha256':verdict['source_pack_sha256'],
           'verified_literal_count':18,
           'model_role':'UNTRUSTED_SOURCE_LITERAL_EXTRACTION',
           'calculation_owner':'TRUELANDED_DETERMINISTIC_CODE_NOT_META',
           'phases':phases,'final_next_proof':verdict['final_next_proof'],
           'model_calls_during_this_replay':0,'provider_signed':False,
           'provider_origin_independently_attested':False,
           'document_issuers_authenticated':False,
           'human_review_required':True,'public_release_approved':False}
    except ReplayRefusal:raise
    except Exception:raise ReplayRefusal('PRIVATE_LOCAL_EVIDENCE_REFUSED') from None