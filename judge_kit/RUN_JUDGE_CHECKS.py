"""Run independently verifiable synthetic tests from a fresh extracted Judge Kit."""
from __future__ import annotations
from pathlib import Path
import json
import os
import subprocess
import sys
import VERIFY_JUDGE_KIT


def main() -> int:
    root = Path(__file__).resolve().parent
    result = VERIFY_JUDGE_KIT.verify(root)
    print(json.dumps(result, sort_keys=True), flush=True)
    environment = dict(os.environ)
    for name in list(environment):
        upper = name.upper()
        if ("KEY" in upper or "TOKEN" in upper) and any(
            marker in upper for marker in ("META", "MODEL_API", "OPENAI", "GH_", "GITHUB")
        ):
            environment.pop(name, None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        (sys.executable, "-B", "-m", "unittest", "discover",
         "-s", str(root / "tests"), "-p", "test_*.py", "-q"),
        cwd=root / "integration", env=environment, check=False,
    )
    if proc.returncode:
        print("DF041_INDEPENDENT_OFFLINE_ACCEPTANCE_FAIL", file=sys.stderr)
        return proc.returncode
    print("DF041_INDEPENDENT_OFFLINE_ACCEPTANCE_PASS_MODEL_CALLS_0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
