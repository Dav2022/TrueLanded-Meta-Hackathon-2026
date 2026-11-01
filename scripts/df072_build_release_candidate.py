"""DF-072: build a safe, narrow, private competition-release *candidate*.
This script DOES NOT publish, grant a license, change repository refs or include
private Meta receipts. It exports only explicitly enumerated synthetic source.
It cannot make the original repository's Git history safe to publicize.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path, PurePosixPath
import argparse, json, os, re, subprocess, sys, zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "integration/indie_core.py", "integration/evidence_graph.py",
    "integration/df021_planner.py", "integration/df023_proof_impact.py",
    "integration/df023_timeline.py", "integration/df023j_plus_novel_muse.py",
    "integration/df023l_offline_diagnostics.py", "integration/df037_mock_pipeline.py",
    "integration/muse_contract.py", "integration/synthetic_pdf.py",
    "integration/muse_cli.py", "integration/df023l_meta_transport.py",
    "integration/df023l_capture_protocol.py",
    "scripts/df043_build_static_site.py",
    "docs/index.html", "docs/style.css", "docs/app.js",
    "docs/data.json", "docs/counterfactual.js",
    "demo/index.html", "demo/server.py", "demo/style.css", "demo/ui.js",
    "tests/test_df021_planner.py", "tests/test_df023_proof_impact.py",
    "tests/test_df023_timeline.py", "tests/test_df026_independent_oracle.py",
    "tests/test_df037_mock_e2e.py", "tests/test_df043_static_site.py",
    "tests/test_df071_counterfactual.cjs", "tests/test_df071_browser_contract.cjs",
)
EXCLUDED = ("viewer/", "review/", "private/", ".github/", ".git/",
            "df040", "df039", "receipt", "capture.bin", "user_data",
            "api_key", ".env", "SECRET", "token.txt")
SECRETS = (
    rb"ghp_[A-Za-z0-9]{30,}",
    rb"github_pat_[A-Za-z0-9_]{25,}",
    rb"sk-proj-[A-Za-z0-9_-]{20,}",
    rb"-----BEGIN [A-Z ]*PRIVATE KEY-----",
)
README = """# TrueLanded — Evidence-to-Decision Engine

**Meta Global AI Developer Hackathon 2026 · Indie Developer · Build for Your World**

**The document changed. The decision should too.**

This competition-only synthetic demonstrator is separate from the pre-existing commercial
TrueLanded project. Meta Muse Spark 1.3 participated in separately recorded,
owner-authorized historical candidate text extraction; **the browser demo is an
offline simulation and does not perform a new model call**. The deterministic
engine verifies synthetic literal source data, tracks conflicting obligations,
ranks missing evidence and recalculates bounded hypothetical invoice scenarios.
Neither source hashes nor model candidates authenticate issuers or authorize
customs filing. Human review is required.

Run the site: \`cd docs && python -m http.server 18973 --bind 127.0.0.1\`.
Open \`http://127.0.0.1:18973/\`; WebCrypto requires a secure context.

Run offline tests: \`python -B RUN_PUBLIC_TESTS.py\` (Python 3.11+).
Optional Node 22 adversarial tests:
\`node --test tests/test_df071_counterfactual.cjs tests/test_df071_browser_contract.cjs\`.

Code provenance: isolated competition modules created during the October 2026
hackathon, with technical project records maintained privately by their owner.
No commercial TrueLanded source, confidential customer documents, real Meta
response bodies, provider keys, or copyright-cleared assumptions are included.

**PREPUBLICATION CANDIDATE — NOT YET LICENSED OR APPROVED FOR PUBLIC RELEASE.**
A code license must be explicitly authorized by the owner before publication.
"""
RUNNER = '''"""Offline synthetic competition-only Python acceptance suite."""
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
'''

def git(*args: str) -> bytes:
    return subprocess.run(("git", "-C", str(ROOT), *args), check=True,
                          capture_output=True, timeout=30).stdout

def build(destination: Path) -> dict:
    if not destination.is_absolute():
        raise ValueError("ABSOLUTE_DESTINATION_REQUIRED")
    destination = destination.resolve()
    if destination.exists() or ROOT == destination or ROOT in destination.parents:
        raise ValueError("OUTPUT_EXISTS_OR_INSIDE_GIT")
    if git("status", "--porcelain"):
        raise ValueError("SOURCE_TREE_NOT_COMMITTED")
    commit = git("rev-parse", "HEAD").decode("ascii").strip()
    if len(commit) != 40:
        raise ValueError("SOURCE_COMMIT_INVALID")
    out = {}
    for path in FILES:
        pure = PurePosixPath(path)
        if pure.is_absolute() or ".." in pure.parts or pure.as_posix() != path:
            raise ValueError("UNSAFE_FILE_PATH")
        if any(marker.lower() in path.lower() for marker in EXCLUDED):
            raise ValueError("FORBIDDEN_HISTORY_OR_PRIVATE_PATH:" + path)
        raw = git("show", commit + ":" + path)
        if len(raw) > 160_000:
            raise ValueError("FILE_TOO_LARGE")
        if any(re.search(pat, raw) for pat in SECRETS):
            raise ValueError("SECRET_PATTERN_FOUND")
        out[path] = raw
    out["README.md"] = README.replace("\`", "\`").encode("utf8")
    out["RUN_PUBLIC_TESTS.py"] = RUNNER.encode("utf8")
    manifest = {
        "schema": "DF072_ALLOWLISTED_PREPUBLICATION_V1",
        "source_repository": "Dav2022/TrueLanded-Meta-Hackathon-2026",
        "source_commit": commit,
        "history_included": False,
        "source_document_type": "SYNTHETIC_ONLY",
        "actual_meta_response_embedded": False,
        "licensed_for_publication": False,
        "publication_approved": False,
        "signature_by_meta_or_issuer": False,
        "files": {name: {"sha256": sha256(raw).hexdigest(), "bytes": len(raw)}
                  for name, raw in sorted(out.items())},
    }
    out["PREPUBLICATION_MANIFEST.json"] = (
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode("utf8")
    if len(out) > 45 or sum(map(len, out.values())) > 2_000_000:
        raise ValueError("EXPORT_SIZE_REFUSED")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9, allowZip64=False) as archive:
        for name, raw in sorted(out.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 31, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100644 << 16)
            archive.writestr(info, raw)
    return {"status": "DF072_PRIVATE_ALLOWLIST_EXPORT_PASS",
            "count": len(out), "source_commit": commit,
            "archive_bytes": destination.stat().st_size,
            "archive_sha256": sha256(destination.read_bytes()).hexdigest(),
            "public_release": False}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        print(json.dumps(build(args.output), indent=2, sort_keys=True))
    except (ValueError, OSError, subprocess.CalledProcessError) as e:
        print("DF072_CLEAN_EXPORT_REFUSED:" + type(e).__name__, file=sys.stderr)
        raise SystemExit(2)
