"""Build narrow precomputed synthetic lab results; never includes model responses."""
from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'integration'))
import df069_adjudication as core
def content():
    raw=(ROOT/'fixtures/df069_synthetic_attacks.json').read_bytes()
    rows=[]
    for case in json.loads(raw)['cases']:
        request=case['request']; docs={d.get('id'):d.get('role') for d in request.get('documents',[])}
        inputs=[{'role':docs.get(o.get('document_id'),'unknown'),'field':o.get('field'),'unit':o.get('unit'),'value':o.get('value')} for o in request.get('observations',[])]
        try:
            r=core.adjudicate(request); a=r['adjudication']
            output={'status':a['status'],'declared':a['declared'],'inspected':a['inspected'],'difference':a['difference'],'excluded':len(r['excluded_noncomparable']),'evidence_nodes':len(r['evidence_graph'])}
        except core.EvidenceRejected:
            output={'status':'REJECTED_INPUT','declared':None,'inspected':None,'difference':None,'excluded':None,'evidence_nodes':0}
        expected=case['expected']
        assert output['status']==expected['gate'] and output['difference']==expected['difference']
        rows.append({'id':case['id'],'inputs':inputs,'output':output,'matches_expected':True})
    data={'schema':'DF073_SYNTHETIC_PRECOMPUTED_ADJUDICATION_V1','mode':'PRECOMPUTED_PYTHON_RESULTS_NOT_LIVE_INFERENCE','engine_sha256':hashlib.sha256((ROOT/'integration/df069_adjudication.py').read_bytes()).hexdigest(),'fixture_sha256':hashlib.sha256(raw).hexdigest(),'human_review_required':True,'issuer_authenticated':False,'legal_action_authorized':False,'meta_calls':0,'cases':rows}
    return (json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')
if __name__=='__main__':
    target=ROOT/'docs/adjudication-data.json'; raw=content()
    if '--check' in sys.argv:
        if target.read_bytes()!=raw: raise SystemExit('DF073_ADJUDICATION_DATA_DRIFT')
    else: target.write_bytes(raw)
    print('DF073_ADJUDICATION_30_SYNTHETIC_VERDICTS_MATCH')
