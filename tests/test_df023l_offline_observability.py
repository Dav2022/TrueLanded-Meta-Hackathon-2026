"""DF-023L: adversarial offline tests. NO Meta transport and NO credentials."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
import json
import unittest
import df023j_plus_novel_muse as novel
import df023l_offline_diagnostics as diag
import df023l_capture_protocol as archive

class OfflineObservabilityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pack=novel.make_pack("abcdef0123456789abcdef0123456789")
  cls.model=novel.fake_response_for_tests(cls.pack)
  cls.raw=novel.encoded(cls.model)
 def test_request_uses_official_supported_low_not_none(self):
  req=diag.proposed_request(self.pack)
  self.assertEqual(req["reasoning_effort"],"low")
  self.assertEqual(req["max_completion_tokens"],3200)
  self.assertEqual(req["model"],"muse-spark-1.3")
  self.assertFalse(req["store"])
  self.assertFalse(req["stream"])
  self.assertNotIn("tools",req)
 def test_mock_response_not_claimed_as_meta_even_if_all_literals_match(self):
  d=diag.diagnose(self.pack,200,self.raw)
  self.assertEqual(d["category"],"SOURCE_LITERAL_GATE_PASSED")
  self.assertEqual(d["literal_fields_verified"],18)
  self.assertFalse(d["model_called_by_this_module"])
  self.assertFalse(d["provider_signed"])
  self.assertFalse(d["source_document_authenticated"])
 def test_http_400_classified_without_message_echo(self):
  raw=novel.encoded({"error":{"type":"invalid_request_error",
         "code":None,"param":"reasoning_effort",
         "message":"PRIVATE_SECRET_SHOULD_NOT_BE_ECHOED"}})
  d=diag.diagnose(self.pack,400,raw)
  self.assertEqual(d["error_type"],"invalid_request_error")
  self.assertEqual(d["error_param"],"reasoning_effort")
  self.assertNotIn("PRIVATE_SECRET",str(d))
 def test_http_429_and_503_differentiated(self):
  for status,kind in ((429,"rate_limit_error"),(503,"server_error")):
   with self.subTest(status=status):
    raw=novel.encoded({"error":{"type":kind,
         "code":"service_overloaded","message":"redacted"}})
    d=diag.diagnose(self.pack,status,raw)
    self.assertEqual(d["status"],status)
    self.assertEqual(d["error_type"],kind)
    self.assertEqual(d["literal_fields_verified"],0)
 def test_http_200_non_json_distinct(self):
  d=diag.diagnose(self.pack,200,b"not-json")
  self.assertEqual(d["category"],"HTTP_200_NON_JSON")
 def test_http_200_truncated_reason_identified(self):
  fake=deepcopy(self.model)
  fake["choices"][0]["finish_reason"]="length"
  d=diag.diagnose(self.pack,200,novel.encoded(fake))
  self.assertEqual(d["category"],"MODEL_RESPONSE_REJECTED_BY_SOURCE_GATE")
  self.assertEqual(d["local_gate_code"],"RESPONSE_NOT_STOP")
  self.assertEqual(d["finish_reason"],"length")
 def test_http_200_wrong_quote_classified(self):
  fake=deepcopy(self.model)
  body=json.loads(fake["choices"][0]["message"]["content"])
  body["candidates"][0]["literal_claims"][0]["value"]="FAKE"
  fake["choices"][0]["message"]["content"]=json.dumps(body)
  d=diag.diagnose(self.pack,200,novel.encoded(fake))
  self.assertEqual(d["local_gate_code"],"SOURCE_LITERAL_MISMATCH")
 def test_not_accept_unbounded_or_untyped_input(self):
  for status,raw in ((True,b"ok"),(200,"text"),(200,b"x"*(diag.MAX_BYTES+1))):
   with self.subTest(s=status),self.assertRaises(diag.DiagnosticRefusal):
    diag.diagnose(self.pack,status,raw)
 def test_error_classifier_refuses_provider_freeform_injection(self):
  raw=novel.encoded({"error":{"type":"XX\nLEAK",
           "code":"safe_error","param":"key/../newline\n",
           "message":"secret"}})
  d=diag.safe_error(raw,400)
  self.assertEqual(d["error_type"],"UNKNOWN")
  self.assertEqual(d["error_code"],"safe_error")
  self.assertEqual(d["error_param"],"NONE")
  self.assertNotIn("secret",str(d))
 def test_capture_records_bytes_before_validation_failure(self):
  bad=deepcopy(self.model)
  bad["choices"][0]["finish_reason"]="length"
  raw=novel.encoded(bad)
  with TemporaryDirectory() as dir:
   result=archive.save(dir,self.pack,200,raw)
   self.assertEqual(result["local_gate_code"],"RESPONSE_NOT_STOP")
   self.assertEqual((Path(dir)/archive.CAPTURE_FILE).read_bytes(),raw)
   self.assertEqual(archive.audit(dir,self.pack)["http_status"],200)
 def test_capture_http_error_without_credentials_or_raw_console(self):
  raw=novel.encoded({"error":{"type":"invalid_request_error",
       "message":"UNTRUSTED_FULL_MESSAGE"}})
  with TemporaryDirectory() as dir:
   result=archive.save(dir,self.pack,400,raw)
   self.assertEqual(result["status"],400)
   self.assertNotIn("UNTRUSTED_FULL_MESSAGE",str(result))
   self.assertEqual(archive.audit(dir,self.pack)["real_meta_inference_proven"],False)
 def test_capture_cannot_overwrite_prior_attempt(self):
  with TemporaryDirectory() as dir:
   archive.save(dir,self.pack,200,self.raw)
   with self.assertRaises((archive.CaptureRefusal,FileExistsError)):
    archive.save(dir,self.pack,200,self.raw)
 def test_tampering_original_body_refused(self):
  with TemporaryDirectory() as dir:
   archive.save(dir,self.pack,200,self.raw)
   with (Path(dir)/archive.CAPTURE_FILE).open("ab") as f:f.write(b"tampered")
   with self.assertRaisesRegex(archive.CaptureRefusal,"INTEGRITY"):
    archive.audit(dir,self.pack)
 def test_forged_authoritative_review_refused(self):
  with TemporaryDirectory() as dir:
   archive.save(dir,self.pack,200,self.raw)
   p=Path(dir)/archive.REVIEW_FILE
   d=json.loads(p.read_text("utf8"))
   d["not_a_live_provider_receipt"]=False
   p.write_text(json.dumps(d),encoding="utf8")
   with self.assertRaisesRegex(archive.CaptureRefusal,"ORIGIN"):
    archive.audit(dir,self.pack)
 def test_pack_modification_cannot_replay(self):
  with TemporaryDirectory() as dir:
   archive.save(dir,self.pack,200,self.raw)
   other=novel.make_pack("1234567890abcdef1234567890abcdef")
   with self.assertRaisesRegex(archive.CaptureRefusal,"INTEGRITY"):
    archive.audit(dir,other)

if __name__=="__main__":unittest.main()
