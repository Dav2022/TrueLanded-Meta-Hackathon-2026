"""CLI safety: no real HTTPS; tests simulate transport with unittest patch."""
import io,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import muse_cli
import df023j_plus_novel_muse as novel

class TestCli(unittest.TestCase):
 def test_default_no_external_calls(self):
  with patch('df023l_meta_transport.exchange',side_effect=AssertionError('NETWORK_FORBIDDEN')):
   with patch('sys.stdout',new_callable=io.StringIO) as output:
    self.assertEqual(muse_cli.main([]),0)
   self.assertIn('DF025_CLI_PREFLIGHT_OFFLINE',output.getvalue())
 def test_mock_no_external_calls(self):
  with patch('df023l_meta_transport.exchange',side_effect=AssertionError('NETWORK_FORBIDDEN')):
   with patch('sys.stdout',new_callable=io.StringIO) as output:
    self.assertEqual(muse_cli.main(['--mode','mock']),0)
   self.assertIn('OFFLINE_MOCK_ONLY_NOT_PROVIDER_EVIDENCE',output.getvalue())
 def test_live_requires_both_flags(self):
  with patch('df023l_meta_transport.exchange',side_effect=AssertionError('NETWORK_FORBIDDEN')):
   with self.assertRaisesRegex(muse_cli.Refusal,'EXPLICIT_LIVE_AUTHORIZATION'):
    muse_cli.main(['--mode','execute-live'])
   with self.assertRaisesRegex(muse_cli.Refusal,'EXPLICIT_LIVE_AUTHORIZATION'):
    muse_cli.main(['--mode','execute-live','--i-authorize-one-billable-call'])
 def test_missing_key_refused_no_attempt_lock(self):
  with tempfile.TemporaryDirectory() as d:
   with patch.dict(os.environ,{'MODEL_API_KEY':''}):
    with patch('df023l_meta_transport.exchange',side_effect=AssertionError('NETWORK_FORBIDDEN')):
     with self.assertRaisesRegex(muse_cli.Refusal,'VALID_MODEL_API_KEY_REQUIRED'):
      muse_cli.main(['--mode','execute-live','--private-dir',d,'--i-authorize-one-billable-call','--acknowledge-model-output-untrusted'])
   self.assertFalse((Path(d)/muse_cli.LOCK).exists())
 def test_preexisting_lock_always_refused(self):
  with tempfile.TemporaryDirectory() as d:
   (Path(d)/muse_cli.LOCK).write_text('{}',encoding='utf8')
   with patch('df023l_meta_transport.exchange',side_effect=AssertionError('NETWORK_FORBIDDEN')):
    with self.assertRaisesRegex(muse_cli.Refusal,'PRIVATE_ATTEMPT_ALREADY_EXISTS'):
     muse_cli.main(['--mode','execute-live','--private-dir',d,'--i-authorize-one-billable-call','--acknowledge-model-output-untrusted'])
 def test_live_mocked_exchange_writes_lock_before_attempt(self):
  with tempfile.TemporaryDirectory() as d:
   with patch.dict(os.environ,{'MODEL_API_KEY':'LLM_TEST_NOT_REAL_123456789123456789'}):
    with patch('df023l_meta_transport.exchange',side_effect=RuntimeError('SIMULATED_IO_FAILURE')) as exch:
     with patch('sys.stdout',new_callable=io.StringIO):
      code=muse_cli.main(['--mode','execute-live','--private-dir',d,'--i-authorize-one-billable-call','--acknowledge-model-output-untrusted'])
   self.assertEqual(code,3);exch.assert_called_once()
   self.assertTrue((Path(d)/muse_cli.LOCK).exists())
   self.assertTrue((Path(d)/muse_cli.PACK).exists())
   self.assertFalse((Path(d)/'UNTRUSTED_HTTP_BODY_PRIVATE.bin').exists())
 def test_failed_live_attempt_cannot_retry_same_folder(self):
  with tempfile.TemporaryDirectory() as d:
   (Path(d)/muse_cli.LOCK).write_text('{}')
   with self.assertRaises(muse_cli.Refusal):
    muse_cli.safe_folder(d)

if __name__=='__main__':unittest.main()