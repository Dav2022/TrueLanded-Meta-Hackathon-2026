"""Transport wiring contract tests. All HTTPS fully mocked; zero network."""
from __future__ import annotations
from unittest import TestCase
from unittest.mock import patch
from urllib.error import HTTPError
from io import BytesIO
import df023l_meta_transport as meta
import df023l_offline_diagnostics as offline
import df023j_plus_novel_muse as source

class FakeHttp:
 def __init__(self,code,raw):self.status=code;self.raw=raw;self.max_read=0
 def __enter__(self):return self
 def __exit__(self,*args):return False
 def read(self,n):
  self.max_read=n
  return self.raw[:n]

class OfflineHttpTests(TestCase):
 def setUp(self):
  self.pack=source.make_pack("1234567890abcdef1234567890abcdef")
  self.request=offline.proposed_request(self.pack)
  self.key="LLM_UNIT_TEST_NOT_REAL_123456789012345678"
 def test_one_http_exchange_no_implicit_retries(self):
  hit=FakeHttp(200,b'{"a":"b"}')
  class Opener:
   calls=0
   def open(self,request,timeout):
    self.calls+=1
    self.assert_eq=timeout
    return hit
  opener=Opener()
  with patch("df023l_meta_transport.build_opener",return_value=opener):
   code,body=meta.exchange(self.request,self.key)
  self.assertEqual(opener.calls,1)
  self.assertEqual(opener.assert_eq,75)
  self.assertEqual((code,body),(200,b'{"a":"b"}'))
  self.assertEqual(hit.max_read,meta.MAX_BODY+1)
 def test_http_non200_body_preserved_for_diagnosis(self):
  status=400;raw=b'{"error":{"type":"invalid_request_error"}}'
  ex=HTTPError(meta.ENDPOINT,status,"rejected",{},BytesIO(raw))
  class Opener:
   calls=0
   def open(self,*args,**kwargs):
    self.calls+=1
    raise ex
  op=Opener()
  with patch("df023l_meta_transport.build_opener",return_value=op):
   code,body=meta.exchange(self.request,self.key)
  self.assertEqual(op.calls,1)
  self.assertEqual(code,status)
  self.assertEqual(body,raw)
 def test_no_redirects(self):
  with self.assertRaisesRegex(meta.TransportRefusal,"REDIRECT"):
   meta.NoRedirect().redirect_request(None,None,None,None,None,None)
 def test_token_and_model_refused_before_network(self):
  with patch("df023l_meta_transport.build_opener",
             side_effect=AssertionError("MUST_NEVER_NETWORK")):
   with self.assertRaises(meta.TransportRefusal):
    meta.exchange(self.request,"invalid")
   wrong={**self.request,"model":"other-model"}
   with self.assertRaises(meta.TransportRefusal):
    meta.exchange(wrong,self.key)
 def test_request_never_sends_tools_or_stored_history(self):
  self.assertNotIn("tools",self.request)
  self.assertFalse(self.request["store"])
  self.assertFalse(self.request["stream"])
  self.assertEqual(meta.ENDPOINT,"https://api.meta.ai/v1/chat/completions")

if __name__=="__main__":
 import unittest
 unittest.main()
