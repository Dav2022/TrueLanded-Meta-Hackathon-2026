"""DF037 E2E mock judge surface: deterministic HTTP and source gate, no Meta calls."""
from __future__ import annotations
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request,build_opener,ProxyHandler
from urllib.error import HTTPError
from unittest.mock import patch
import importlib.util,json,sys,threading,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'demo'))
sys.path.insert(0,str(ROOT/'integration'))
import df037_mock_pipeline as pipe
import server as app
import df023j_plus_novel_muse as novel

class DF037SimulatedE2E(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
  cls.port=cls.server.server_port
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
  cls.thread.start();cls.http=build_opener(ProxyHandler({}))
 @classmethod
 def tearDownClass(cls):
  cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=3)
 def get(self,path='/api/mock-scene',method='GET',headers=None):
  req=Request(f'http://127.0.0.1:{self.port}{path}',method=method,headers=headers or {})
  try:
   with self.http.open(req,timeout=5) as response:return response.status,response.read(),response.headers
  except HTTPError as error:return error.code,error.read(),error.headers
 def test_full_mock_pipeline_computes_real_deterministic_delta(self):
  with patch('df023l_meta_transport.exchange',side_effect=AssertionError('REAL_META_CALL_FORBIDDEN')):
   data=pipe.execute()
  self.assertEqual(data['gate'],'DF037_FULL_PIPELINE_MOCK_SOURCE_CHECKED')
  self.assertFalse(data['meta_inference_proven']);self.assertEqual(data['api_calls'],0)
  self.assertEqual(data['literal_matches'],18)
  self.assertEqual([x['literal_matches'] for x in data['stages']],[4,7,7])
  self.assertIn('QTY_MISMATCH',data['stages'][0]['open_obligations'])
  self.assertIn('VALUE_MISMATCH',data['stages'][1]['newly_exposed'])
  self.assertIn('VALUE_MISMATCH',data['stages'][2]['conditionally_reconciled'])
  self.assertEqual(data['final_next_best_proof'],'REQ_TECH_SHEET')
 def test_new_seed_changes_sources_but_logic_is_same(self):
  a=pipe.execute('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
  b=pipe.execute('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')
  self.assertNotEqual(a['source_pack_sha256'],b['source_pack_sha256'])
  self.assertEqual(a['final_next_best_proof'],b['final_next_best_proof'])
 def test_mutated_fake_model_response_refuses_display(self):
  pack=novel.make_pack(pipe.SEED)
  response=novel.fake_response_for_tests(pack)
  payload=json.loads(response['choices'][0]['message']['content'])
  payload['candidates'][0]['literal_claims'][0]['exact_source_line']='REFERENCE: MALICIOUS'
  response['choices'][0]['message']['content']=json.dumps(payload)
  result=pipe.execute(response_override=novel.encoded(response))
  self.assertTrue(result['no_go']);self.assertEqual(result['api_calls'],0)
 def test_http_api_source_trace_and_no_meta_claim(self):
  status,raw,headers=self.get();data=json.loads(raw)
  self.assertEqual(status,200)
  self.assertEqual(data['mode'],'SIMULATED_OFFLINE_NOT_META_INFERENCE')
  self.assertEqual(data['response_origin'],'LOCAL_TEST_DOUBLE_NOT_META')
  self.assertFalse(data['provider_signed']);self.assertEqual(data['literal_matches'],18)
  self.assertEqual(headers.get('X-Frame-Options'),'DENY')
 def test_cross_origin_and_host_refusal(self):
  self.assertEqual(self.get(headers={'Origin':'https://attacker.invalid'})[0],403)
  self.assertEqual(self.get(headers={'Host':'attacker.invalid'})[0],403)
 def test_non_readonly_and_query_refusal(self):
  self.assertEqual(self.get(method='POST')[0],405)
  self.assertEqual(self.get('/api/mock-scene?live=true')[0],422)
  self.assertEqual(self.get('/.env')[0],404)
 def test_local_ui_assets_return(self):
  for path in ('/','/index.html','/ui.js','/style.css'):
   with self.subTest(path=path):self.assertEqual(self.get(path)[0],200)
 def test_server_blocks_tampered_pipeline(self):
  with patch.object(app.df037_mock_pipeline,'execute',return_value={'gate':'DF037_MOCK_SOURCE_VALIDATION_REFUSED'}):
   self.assertEqual(self.get()[0],503)
if __name__=='__main__':unittest.main()