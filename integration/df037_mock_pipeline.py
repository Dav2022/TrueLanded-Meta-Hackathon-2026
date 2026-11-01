"""DF037 local mock E2E: same source verifier as Muse integration, ZERO API."""
from __future__ import annotations
from hashlib import sha256
import df023j_plus_novel_muse as novel
import df023l_offline_diagnostics as diagnostic

SEED='6e5ca17ef036bee7001029384756abcd'

def execute(seed=SEED,response_override=None):
    pack=novel.make_pack(seed)
    req=diagnostic.proposed_request(pack)
    raw=novel.encoded(novel.fake_response_for_tests(pack)) if response_override is None else response_override
    diagnosis=diagnostic.diagnose(pack,200,raw)
    if diagnosis['category']!='SOURCE_LITERAL_GATE_PASSED' or diagnosis['literal_fields_verified']!=18:
        return {'gate':'DF037_MOCK_SOURCE_VALIDATION_REFUSED',
                'mode':'SIMULATED_OFFLINE_NOT_META_INFERENCE',
                'reason':diagnosis['category'],
                'api_calls':0,'meta_inference_proven':False,
                'no_go':True}
    verdict=novel.review(pack,__import__('json').loads(raw))
    phases=verdict['phases']
    if len(phases)!=3 or phases[-1]['top_next_proof_request']!='REQ_TECH_SHEET':
        raise ValueError('DETERMINISTIC_FRONTIER_REFUSED')
    sources={d['event_id']:d for d in pack['documents']}
    rows=[]
    for phase in phases:
        source=sources[phase['event_id']]
        rows.append({
            'stage':phase['event_id'],
            'source_sha256':source['source_sha256'],
            'source_lines':source['untrusted_text'].splitlines(),
            'literal_matches':phase['model_literal_fields_exactly_matched'],
            'open_obligations':phase['open_obligations'],
            'newly_exposed':phase['newly_exposed'],
            'conditionally_reconciled':phase['conditionally_reconciled'],
            'next_best_proof':phase['top_next_proof_request'],
            'human_review_required':True,
            'source_document_authenticated':False,
        })
    return {
        'gate':'DF037_FULL_PIPELINE_MOCK_SOURCE_CHECKED',
        'mode':'SIMULATED_OFFLINE_NOT_META_INFERENCE',
        'model_contract_requested':'muse-spark-1.3',
        'response_origin':'LOCAL_TEST_DOUBLE_NOT_META',
        'model_reported_not_proven':'muse-spark-1.3',
        'api_calls':0,'meta_inference_proven':False,
        'provider_signed':False,'human_review_required':True,
        'live_execution_approved':False,
        'request_sha256':novel.digest(req),
        'response_sha256':sha256(raw).hexdigest(),
        'source_pack_sha256':novel.digest(pack),
        'literal_matches':verdict['literal_fields_matched'],
        'calculation_owner':'TRUELANDED_DETERMINISTIC_CODE_NOT_META',
        'stages':rows,
        'final_next_best_proof':verdict['final_next_proof'],
    }