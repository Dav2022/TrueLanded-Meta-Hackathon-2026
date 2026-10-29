"""DF040 read-only real owner capture projection: test with synthetic fixtures only."""
from __future__ import annotations
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.request import Request,build_opener,ProxyHandler
from urllib.error import HTTPError
from unittest.mock import patch
import json,threading,tempfile,unittest,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'integration'));sys.path.insert(0,str(ROOT/'review'))
import df040_capture_projection as projection
import df023l_capture_protocol as capture
import df023j_plus_novel_muse as novel
import df023l_offline_diagnostics as diag
import muse_cli
import importlib.util
_spec=importlib.util.spec_from_file_location("df040_private_review_server",ROOT/"review"/"server.py")
app=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(app)

class TestPrivateCaptureReview(unittest.TestCase):
 def init_files(self,root):
  pack=novel.make_pack('a90123456789abcdef0123456789abcd')
  (root/muse_cli.PACK).write_bytes(novel.encoded(pack)+b'\n')
  req=diag.proposed_request(pack)
  lock={'gate':'ONE_LIVE_ATTEMPT_COMMITTED_BEFORE_NETWORK',
      'model':'muse-spark-1.3','request_sha256':novel.digest(req),
      'pack_sha256':novel.digest(pack),'max_attempts':1,'retry':False,
      'public_release_approved':False}
  (root/muse_cli.LOCK).write_bytes(novel.encoded(lock)+b'\n')
  reply=novel.fake_response_for_tests(pack)
  capture.save(root,pack,200,novel.encoded(reply))
 def test_local_mock_never_claims_live(self):
  with tempfile.TemporaryDirectory() as tmp:
   self.init_files(Path(tmp))
   with patch('df023l_meta_transport.exchange',side_effect=AssertionError('NO_NETWORK')):
    out=projection.project(tmp)
   self.assertEqual(out['verified_literal_count'],18)
   self.assertEqual(out['model_calls_during_this_replay'],0)
   self.assertFalse(out['provider_signed'])
   self.assertFalse(out['provider_origin_independently_attested'])
   self.assertEqual(out['final_next_proof'],'REQ_TECH_SHEET')
   self.assertEqual([r['verified_literals'] for r in out['phases']],[4,7,7])
 def test_missing_receipt_refuses(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(projection.ReplayRefusal):projection.project(tmp)
 def test_body_tamper_refuses(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.init_files(root)
   with (root/capture.CAPTURE_FILE).open('ab') as f:f.write(b'FORGED')
   with self.assertRaises(projection.ReplayRefusal):projection.project(tmp)
 def test_lock_tamper_refuses(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.init_files(root)
   f=root/muse_cli.LOCK;obj=json.loads(f.read_text('utf8'))
   obj['model']='another-model';f.write_text(json.dumps(obj))
   with self.assertRaises(projection.ReplayRefusal):projection.project(tmp)
 def test_http_has_no_raw_provider_body(self):
  with tempfile.TemporaryDirectory() as tmp:
   self.init_files(Path(tmp))
   server=ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
   server.private_evidence_dir=tmp
   thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   opener=build_opener(ProxyHandler({}));base=f'http://127.0.0.1:{server.server_port}'
   def get(path,headers=None,method='GET'):
    req=Request(base+path,headers=headers or {},method=method)
    try:
     with opener.open(req,timeout=5) as r:return r.status,r.read(),r.headers
    except HTTPError as e:return e.code,e.read(),e.headers
   try:
    code,raw,headers=get('/api/private-capture-scene')
    self.assertEqual(code,200);payload=json.loads(raw)
    self.assertEqual(payload['gate'],'DF040_PRIVATE_OWNER_CAPTURE_DERIVED_REPLAY_PASS')
    self.assertNotIn(b'choices',raw);self.assertNotIn(b'authorization',raw.lower())
    self.assertEqual(headers['X-Frame-Options'],'DENY')
    self.assertEqual(get('/',method='POST')[0],405)
    self.assertEqual(get('/api/private-capture-scene?secret=1')[0],422)
    self.assertEqual(get('/api/private-capture-scene',{'Origin':'https://evil.example'})[0],403)
    self.assertEqual(get('/.env')[0],404)
   finally:server.shutdown();server.server_close();thread.join(timeout=3)
 def test_existing_real_df039_capture_is_read_only(self):
  # No reference to actual private receipts in distributable tests.
  self.assertFalse((ROOT/'df039_live_private').exists())
if __name__=='__main__':unittest.main()