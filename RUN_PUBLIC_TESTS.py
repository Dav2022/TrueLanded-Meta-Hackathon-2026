"""Offline synthetic competition-only Python acceptance suite."""
from pathlib import Path
import os, subprocess, sys
root=Path(__file__).resolve().parent
env={k:v for k,v in os.environ.items()
     if not (("KEY" in k.upper() or "TOKEN" in k.upper()) and
             any(s in k.upper() for s in ("META","MODEL_API","OPENAI","GITHUB")))}
env["PYTHONDONTWRITEBYTECODE"]="1"
test=subprocess.run([sys.executable,"-B","-m","unittest","discover",
                     "-s",str(root/"tests"),"-p","test_*.py","-q"],
                    cwd=root/"integration",env=env,check=False)
raise SystemExit(test.returncode)
