from pathlib import Path
import os,subprocess,sys,json
root=Path(__file__).resolve().parent
env=dict(os.environ)
for k in list(env):
 if any(w in k.upper() for w in ('KEY','TOKEN')) and any(w in k.upper() for w in ('META','OPENAI','MODEL_API')):env.pop(k)
env['PYTHONDONTWRITEBYTECODE']='1'
tests=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(root/'tests'),'-p','test_*.py','-q'],cwd=root/'integration',env=env)
if tests.returncode:raise SystemExit(tests.returncode)
check=subprocess.run([sys.executable,'-B','df023m_verify.py'],cwd=root/'viewer',env=env)
if check.returncode:raise SystemExit(check.returncode)
print('DF025_MUSE_PRIVATE_DISTRIBUTION_OFFLINE_TESTS_PASS')
