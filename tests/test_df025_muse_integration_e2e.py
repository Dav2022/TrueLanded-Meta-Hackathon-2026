"""Offline end-to-end Muse transport path tests. ALL RESPONSES ARE LOCAL MOCKS."""
import json
import unittest
from unittest.mock import patch
import df023l_meta_transport as transport
import df023l_offline_diagnostics as diagnostic
import df023j_plus_novel_muse as synthetic

class _FakeHTTP:
 def __init__(self,code,body):self.status=code;self.body=body
 def __enter__(self):return self
 def __exit__(self,*args):return False
 def read(self,max_bytes):return self.body[:max_bytes]

class _Opener:
 def __init__(self,code,body):self.code=code;self.body=body;self.count=0
 def open(self,req,timeout):
  self.count+=1
  assert timeout==75
  assert req.get_method()=='POST'
  assert req.full_url=='https://api.meta.ai/v1/chat/completions'
  assert b'muse-spark-1.3' in req.data
  return _FakeHTTP(self.code,self.body)

class MockedEndToEnd(unittest.TestCase):
 def setUp(self):
  self.pack=synthetic.make_pack('0123456789abcdef0123456789abcdef')
  self.req=diagnostic.proposed_request(self.pack)
  self.key='LLM_FAKE_TEST_TOKEN_ONLY_NEVER_REAL_123456789'
 def _run(self,code,body):
  opener=_Opener(code,body)
  with patch('df023l_meta_transport.build_opener',return_value=opener):
   status,raw=transport.exchange(self.req,self.key)
  self.assertEqual(opener.count,1)
  return diagnostic.diagnose(self.pack,status,raw)
 def test_full_mock_transport_literal_evidence_to_ranked_next_proof(self):
  fake=synthetic.fake_response_for_tests(self.pack)
  result=self._run(200,synthetic.encoded(fake))
  self.assertEqual(result['category'],'SOURCE_LITERAL_GATE_PASSED')
  self.assertEqual(result['literal_fields_verified'],18)
  self.assertEqual(result['final_next_proof'],'REQ_TECH_SHEET')
  self.assertFalse(result['provider_signed'])
  self.assertTrue(result['human_review_required'])
  self.assertFalse(result['model_called_by_this_module'])
  self.assertEqual(fake['id'],'LOCAL_TEST_DOUBLE_NOT_MUSE')
 def test_http_503_fails_closed(self):
  result=self._run(503,b'{"error":{"type":"service_unavailable"}}')
  self.assertEqual(result['category'],'HTTP_ERROR')
  self.assertEqual(result['literal_fields_verified'],0)
  self.assertNotIn('final_next_proof',result)
 def test_successful_http_but_wrong_literal_fails_closed(self):
  fake=synthetic.fake_response_for_tests(self.pack)
  content=json.loads(fake['choices'][0]['message']['content'])
  content['candidates'][0]['literal_claims'][0]['value']='FORGED_VALUE'
  fake['choices'][0]['message']['content']=json.dumps(content)
  result=self._run(200,synthetic.encoded(fake))
  self.assertEqual(result['category'],'MODEL_RESPONSE_REJECTED_BY_SOURCE_GATE')
  self.assertEqual(result['literal_fields_verified'],0)
  self.assertNotIn('final_next_proof',result)
 def test_unauthorized_model_refused_before_opener(self):
  with patch('df023l_meta_transport.build_opener',side_effect=AssertionError('NETWORK_FORBIDDEN')):
   with self.assertRaises(transport.TransportRefusal):
    transport.exchange({**self.req,'model':'other-model'},self.key)
 def test_invalid_token_refused_before_opener(self):
  with patch('df023l_meta_transport.build_opener',side_effect=AssertionError('NETWORK_FORBIDDEN')):
   with self.assertRaises(transport.TransportRefusal):
    transport.exchange(self.req,'')

if __name__=='__main__':unittest.main()