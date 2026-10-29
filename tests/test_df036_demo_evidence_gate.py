import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import df036_demo_evidence_gate as gate
import df023j_plus_novel_muse as novel
import df023l_offline_diagnostics as diag
import df023l_capture_protocol as capture
import muse_cli

class Df036EvidenceTests(unittest.TestCase):
 def setup_private(self,root):
  pack=novel.make_pack('0123456789abcdef0123456789abcdef')
  (root/muse_cli.PACK).write_bytes(novel.encoded(pack)+b'\n')
  req=diag.proposed_request(pack)
  lock={'gate':'ONE_LIVE_ATTEMPT_COMMITTED_BEFORE_NETWORK','model':'muse-spark-1.3',
        'request_sha256':novel.digest(req),'pack_sha256':novel.digest(pack),
        'max_attempts':1,'retry':False,'public_release_approved':False}
  (root/muse_cli.LOCK).write_bytes(novel.encoded(lock)+b'\n')
  return pack
 def test_mock_and_replay_never_count_as_live(self):
  for name in ('mock','replay'):
   with self.subTest(name=name):
    self.assertFalse(gate.classify_demo(name)['meta_inference_proven'])
 def test_private_mode_requires_evidence(self):
  with self.assertRaises(gate.EvidenceRefusal):gate.classify_demo('private-capture')
 def test_no_attempt_refused(self):
  with tempfile.TemporaryDirectory() as f:
   with self.assertRaises(gate.EvidenceRefusal):gate.inspect_attempt(f)
 def test_locked_without_capture_is_not_live(self):
  with tempfile.TemporaryDirectory() as f:
   self.setup_private(Path(f))
   out=gate.inspect_attempt(f)
   self.assertFalse(out['provider_response_observed'])
 def test_fake_capture_never_becomes_provider_proof(self):
  with tempfile.TemporaryDirectory() as f:
   path=Path(f);pack=self.setup_private(path)
   fake=novel.fake_response_for_tests(pack)
   fake['usage']={'prompt_tokens':101,'completion_tokens':20,'total_tokens':121}
   capture.save(path,pack,200,novel.encoded(fake))
   out=gate.inspect_attempt(path)
   self.assertTrue(out['local_source_gate_passed'])
   self.assertEqual(out['source_literals_verified'],18)
   self.assertFalse(out['meta_inference_proven_independently'])
   self.assertFalse(out['safe_for_publication'])
   self.assertEqual(out['usage_reported_unattested']['total_tokens'],121)
 def test_mutated_lock_rejected(self):
  with tempfile.TemporaryDirectory() as f:
   path=Path(f);self.setup_private(path)
   lockpath=path/muse_cli.LOCK
   record=json.loads(lockpath.read_text())
   record['model']='foreign-model'
   lockpath.write_text(json.dumps(record))
   with self.assertRaisesRegex(gate.EvidenceRefusal,'ONE_SHOT_LOCK_OR_SOURCE_MISMATCH'):
    gate.inspect_attempt(path)
 def test_tampered_capture_refused(self):
  with tempfile.TemporaryDirectory() as f:
   path=Path(f);pack=self.setup_private(path)
   capture.save(path,pack,200,novel.encoded(novel.fake_response_for_tests(pack)))
   with (path/capture.CAPTURE_FILE).open('ab') as stream:stream.write(b' ')
   with self.assertRaises(capture.CaptureRefusal):gate.inspect_attempt(path)
 def test_no_public_content_in_report(self):
  with tempfile.TemporaryDirectory() as f:
   path=Path(f);pack=self.setup_private(path)
   capture.save(path,pack,200,novel.encoded(novel.fake_response_for_tests(pack)))
   out=gate.classify_demo('private-capture',path)
   raw=json.dumps(out)
   self.assertNotIn('untrusted_text',raw)
   self.assertNotIn('Authorization',raw)
   self.assertNotIn('TL-DEMO-',raw)

if __name__=='__main__':unittest.main()