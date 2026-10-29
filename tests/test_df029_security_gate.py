"""Private release security regression: localhost-only, tamper denial, no live network."""
from __future__ import annotations
import copy,json,shutil,socket,sys,threading,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import build_opener,ProxyHandler,Request
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'viewer'))
import df023m_server as viewer
import df023m_verify as verifier
from http.server import ThreadingHTTPServer

class SecurityGate(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.http=ThreadingHTTPServer(('127.0.0.1',0),viewer.Viewer)
  cls.port=cls.http.server_port
  cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True)
  cls.thread.start()
  cls.opener=build_opener(ProxyHandler({}))
 @classmethod
 def tearDownClass(cls):
  cls.http.shutdown();cls.http.server_close();cls.thread.join(timeout=3)
 def request(self,method='GET',path='/api/scene',headers=None):
  req=Request('http://127.0.0.1:'+str(self.port)+path,method=method,headers=headers or {})
  try:
   with self.opener.open(req,timeout=3) as out:return out.status,out.read()
  except HTTPError as exc:return exc.code,exc.read()
 def test_real_replay_requires_verified_manifest(self):
  status,raw=self.request()
  self.assertEqual(status,200)
  payload=json.loads(raw)
  self.assertFalse(payload['evidence']['provider_signed'])
  self.assertFalse(payload['evidence']['issuer_authenticated'])
  self.assertTrue(payload['evidence']['human_review_required'])
  self.assertEqual(payload['evidence']['literal_candidates_verified_against_fictional_source'],18)
 def test_api_no_action_methods(self):
  for method in ('POST','PUT','PATCH','DELETE','OPTIONS'):
   with self.subTest(method=method):
    self.assertEqual(self.request(method=method)[0],405)
 def test_cross_site_origin_refused(self):
  self.assertEqual(self.request(headers={'Origin':'https://attacker.invalid'})[0],403)
 def test_host_header_refused(self):
  self.assertEqual(self.request(headers={'Host':'attacker.invalid'})[0],403)
 def test_cookies_or_credentials_refused(self):
  self.assertEqual(self.request(headers={'Cookie':'sid=1'})[0],403)
  self.assertEqual(self.request(headers={'Authorization':'Bearer fake'})[0],403)
 def test_unknown_path_and_query_refused(self):
  self.assertEqual(self.request(path='/private-key.txt')[0],404)
  self.assertEqual(self.request(path='/api/scene?debug=1')[0],422)
 def test_manifest_rejects_modified_evidence(self):
  with TemporaryDirectory() as tmp:
   folder=Path(tmp)
   for p in (ROOT/'viewer').iterdir():
    if p.is_file():shutil.copy2(p,folder/p.name)
   e=folder/'DF023M_JURY_EVIDENCE.json'
   e.write_bytes(e.read_bytes()+b' ')
   with self.assertRaises(verifier.ReplayRefusal):verifier.verify(folder)
 def test_manifest_rejects_extra_file(self):
  with TemporaryDirectory() as tmp:
   folder=Path(tmp)
   for p in (ROOT/'viewer').iterdir():
    if p.is_file():shutil.copy2(p,folder/p.name)
   (folder/'surprise.txt').write_text('unexpected')
   with self.assertRaises(verifier.ReplayRefusal):verifier.verify(folder)
 def test_loopback_and_security_response_headers(self):
  req=Request('http://127.0.0.1:'+str(self.port)+'/')
  with self.opener.open(req,timeout=3) as resp:
   self.assertEqual(resp.status,200)
   self.assertEqual(resp.headers.get('X-Content-Type-Options'),'nosniff')
   self.assertEqual(resp.headers.get('X-Frame-Options'),'DENY')
   self.assertIn("default-src 'none'",resp.headers.get('Content-Security-Policy'))
  self.assertEqual(self.http.server_address[0],'127.0.0.1')

if __name__=='__main__':unittest.main()