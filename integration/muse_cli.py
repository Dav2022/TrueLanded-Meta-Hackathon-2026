"""Opt-in Meta Muse CLI. Offline by default. Live calls require two explicit flags.

This code is a technical candidate, not a claim of provider authorization or
hackathon release rights. Model results remain untrusted and locally stored.
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import df023j_plus_novel_muse as synthetic
import df023l_offline_diagnostics as diag
import df023l_meta_transport as transport
import df023l_capture_protocol as capture

LOCK='ONE_BILLABLE_ATTEMPT_LOCK_PRIVATE.json'
PACK='SYNTHETIC_SOURCE_PACK_PRIVATE.json'

class Refusal(ValueError):pass

def write_once(path, data):
    with path.open('xb') as stream:stream.write(data)

def safe_folder(raw):
    if raw is None:raise Refusal('PRIVATE_DIRECTORY_REQUIRED')
    p=Path(raw).expanduser().absolute()
    if not p.is_dir() or p.is_symlink():raise Refusal('EXISTING_PRIVATE_DIRECTORY_REQUIRED')
    bundle=Path(__file__).resolve().parents[1]
    if p==bundle or bundle in p.parents:raise Refusal('PRIVATE_DIRECTORY_MUST_BE_OUTSIDE_DISTRIBUTION')
    if any((p/x).exists() for x in (LOCK,capture.CAPTURE_FILE,capture.METADATA_FILE,capture.REVIEW_FILE)):
        raise Refusal('PRIVATE_ATTEMPT_ALREADY_EXISTS')
    return p

def prepare(folder,seed=None):
    if (folder/PACK).exists():raise Refusal('PACK_ALREADY_EXISTS')
    pack=synthetic.make_pack(seed)
    write_once(folder/PACK,synthetic.encoded(pack)+b'\n')
    return pack

def load(folder):
    try:pack=json.loads((folder/PACK).read_text(encoding='utf8'))
    except (OSError,ValueError,UnicodeError):raise Refusal('PREPARED_PACK_REQUIRED') from None
    return synthetic.validate_pack(pack)

def summary(pack):
    req=diag.proposed_request(pack)
    return {'gate':'DF025_CLI_PREFLIGHT_OFFLINE','model':req['model'],
       'synthetic_only':True,'document_count':len(pack['documents']),
       'request_sha256':synthetic.digest(req),'pack_sha256':synthetic.digest(pack),
       'store':req['store'],'stream':req['stream'],
       'new_meta_requests':0,'provider_receipt_claimed':False,
       'human_review_required':True}

def main(argv=None):
    p=argparse.ArgumentParser(description='TrueLanded Muse integration technical candidate; offline by default')
    p.add_argument('--mode',choices=('preflight','mock','execute-live'),default='preflight')
    p.add_argument('--private-dir',help='Existing private directory; outside distributed bundle')
    p.add_argument('--seed',help='32 lowercase hex digits, for reproducible synthetic preflight only')
    p.add_argument('--i-authorize-one-billable-call',action='store_true')
    p.add_argument('--acknowledge-model-output-untrusted',action='store_true')
    args=p.parse_args(argv)
    if args.mode!='execute-live':
        pack=synthetic.make_pack(args.seed)
        out=summary(pack)
        if args.mode=='mock':
            raw=synthetic.encoded(synthetic.fake_response_for_tests(pack))
            check=diag.diagnose(pack,200,raw)
            out.update({'gate':'OFFLINE_MOCK_ONLY_NOT_PROVIDER_EVIDENCE',
              'mock_source_literals':check['literal_fields_verified'],
              'mock_next_proof':check['final_next_proof'],
              'actual_provider_call':False})
        print(json.dumps(out,indent=2))
        return 0
    if not args.i_authorize_one_billable_call or not args.acknowledge_model_output_untrusted:
        raise Refusal('EXPLICIT_LIVE_AUTHORIZATION_FLAGS_REQUIRED')
    folder=safe_folder(args.private_dir)
    token=os.environ.pop('MODEL_API_KEY','')
    if not token.startswith('LLM') or len(token)<24:
        raise Refusal('VALID_MODEL_API_KEY_REQUIRED')
    if args.seed is not None:raise Refusal('LIVE_MODE_SEED_OVERRIDE_DENIED')
    if (folder/PACK).is_file():
        pack=load(folder)
    else:pack=prepare(folder)
    request=diag.proposed_request(pack)
    lock={'gate':'ONE_LIVE_ATTEMPT_COMMITTED_BEFORE_NETWORK',
          'utc':datetime.now(timezone.utc).isoformat(),
          'model':request['model'],'request_sha256':synthetic.digest(request),
          'pack_sha256':synthetic.digest(pack),'max_attempts':1,
          'retry':False,'public_release_approved':False}
    write_once(folder/LOCK,synthetic.encoded(lock)+b'\n')
    try:status,body=transport.exchange(request,token)
    except Exception:
        print(json.dumps({'gate':'ONE_LIVE_ATTEMPT_NETWORK_ERROR_LOCK_RETAINED',
              'status':'REFUSED','token_logged':False,'retry':False}))
        return 3
    result=capture.save(folder,pack,status,body)
    # This only verifies locally supplied bytes, NOT an issuer/provider signature.
    print(json.dumps({'gate':'ONE_LIVE_ATTEMPT_CAPTURED_FOR_PRIVATE_REVIEW',
          'http_status':status,'local_category':result.get('category'),
          'literal_fields_verified':result.get('literal_fields_verified',0),
          'provider_signature_verified':False,'human_review_required':True,
          'no_retry':True,'public_release_approved':False}))
    return 0 if status==200 and result.get('category')=='SOURCE_LITERAL_GATE_PASSED' else 4

if __name__=='__main__':
    try:sys.exit(main())
    except (Refusal,synthetic.NovelRefusal,transport.TransportRefusal,capture.CaptureRefusal) as ex:
        print(json.dumps({'gate':'CLI_FAIL_CLOSED','reason':str(ex),'meta_calls_made_by_refusal':0}),file=sys.stderr)
        sys.exit(2)