"""Build a deterministic, strictly allowlisted DF041 evaluation ZIP from Git HEAD.

Never exports model captures, commercial code, historical owner-derived replay or
any item not explicitly enumerated. Self-issued hashes are NOT Meta signatures.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = (
    "df021_planner.py", "df023_proof_impact.py", "df023_timeline.py",
    "df023j_plus_novel_muse.py", "df023l_capture_protocol.py",
    "df023l_meta_transport.py", "df023l_offline_diagnostics.py",
    "df036_demo_evidence_gate.py", "df037_mock_pipeline.py",
    "df040_capture_projection.py", "evidence_graph.py", "indie_core.py",
    "muse_cli.py", "muse_contract.py", "synthetic_pdf.py",
)
TESTS = (
    "test_df021_planner.py", "test_df023_proof_impact.py",
    "test_df023_timeline.py", "test_df023l_meta_transport.py",
    "test_df023l_offline_observability.py", "test_df025_muse_cli.py",
    "test_df025_muse_integration_e2e.py", "test_df026_independent_oracle.py",
    "test_df036_demo_evidence_gate.py", "test_df037_mock_e2e.py",
    "test_df040_private_capture_review.py", "test_df043_static_site.py",
)
DEMO = ("index.html", "server.py", "style.css", "ui.js")
REVIEW = ("index.html", "server.py", "style.css", "ui.js")
STATIC_SITE = ("index.html", "style.css", "app.js", "counterfactual.js", "data.json")
DOCUMENTS = ("NEW_WORK.md", "RELEASE_HOLD.md", "DF036_META_DEMO_READINESS.md",
             "DF037_SIMULATED_DEMO.md", "DF040_PRIVATE_CAPTURE_REVIEW.md")
FILES = {
    **{"integration/" + name: "integration/" + name for name in INTEGRATION},
    **{"tests/" + name: "tests/" + name for name in TESTS},
    **{"demo/" + name: "demo/" + name for name in DEMO},
    **{"review/" + name: "review/" + name for name in REVIEW},
    **{"docs/" + name: "docs/" + name for name in STATIC_SITE},
    "scripts/df043_build_static_site.py": "scripts/df043_build_static_site.py",
    **{name: name for name in DOCUMENTS},
    "README.md": "judge_kit/JUDGES_README.md",
    "RUN_JUDGE_CHECKS.py": "judge_kit/RUN_JUDGE_CHECKS.py",
    "VERIFY_JUDGE_KIT.py": "judge_kit/VERIFY_JUDGE_KIT.py",
}
FORBIDDEN = ("private.bin", "api_key", "token.txt", ".env", ".pem", ".key",
             "df039_live_private", "df023m_jury_evidence",
             "http_capture_metadata", "one_billable_attempt_lock")
MAX_FILE = 160_000
MAX_ARCHIVE = 2_000_000


def git(*args: str) -> bytes:
    result = subprocess.run(("git", "-C", str(ROOT), *args),
                            capture_output=True, check=True)
    return result.stdout


def git_revision() -> str:
    revision = git("rev-parse", "HEAD").decode("ascii").strip()
    if len(revision) != 40 or git("status", "--porcelain"):
        raise ValueError("DF041_REQUIRES_CLEAN_COMMITTED_GIT_HEAD")
    return revision


def normalized_path(name: str) -> bool:
    p = PurePosixPath(name)
    return not (p.is_absolute() or "\\" in name or ".." in p.parts or
                name.startswith(".") or str(p) != name or
                any(x.lower() in name.lower() for x in FORBIDDEN))


def zipinfo(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 10, 29, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (0o100644 << 16)
    return info


def build(destination: Path) -> dict:
    revision = git_revision()
    if not destination.is_absolute():
        raise ValueError("ABSOLUTE_DESTINATION_REQUIRED")
    destination = destination.resolve(strict=False)
    if destination.exists() or destination == ROOT or ROOT in destination.parents:
        raise ValueError("OUTPUT_EXISTS_OR_INSIDE_GIT_REPOSITORY")
    destination.parent.mkdir(parents=True, exist_ok=True)
    items: dict[str, bytes] = {}
    for archive_name, git_path in FILES.items():
        if not normalized_path(archive_name):
            raise ValueError("UNSAFE_ARCHIVE_NAME")
        mode = git("ls-tree", revision, "--", git_path).decode("utf8")
        if not mode.startswith("100644 ") and not mode.startswith("100755 "):
            raise ValueError("NON_REGULAR_SOURCE_FILE_" + git_path)
        contents = git("show", revision + ":" + git_path)
        if len(contents) > MAX_FILE:
            raise ValueError("EXCESSIVE_SOURCE_BYTES_" + git_path)
        items[archive_name] = contents
    manifest = {
        "schema": "DF041_JUDGE_KIT_ALLOWLIST_SHA256_V1",
        "source_repository": "Dav2022/TrueLanded-Meta-Hackathon-2026",
        "source_commit": revision,
        "mode": "PRIVATE_REPRODUCIBILITY_REVIEW_NOT_PUBLIC_RELEASE",
        "evidence": "SYNTHETIC_OFFLINE_NO_MODEL_CALL",
        "private_model_receipts_included": False,
        "provider_signed": False,
        "redistribution_authorized": False,
        "manifest_issued_by": "TRUELANDED_OWNER_LOCAL_BUILD_NOT_META",
        "files": {
            key: {"sha256": sha256(value).hexdigest(), "bytes": len(value)}
            for key, value in sorted(items.items())
        },
    }
    raw_manifest = (json.dumps(manifest, ensure_ascii=True, sort_keys=True,
                               separators=(",", ":")) + "\n").encode("utf8")
    items["MANIFEST.json"] = raw_manifest
    total = sum(map(len, items.values()))
    if total > MAX_ARCHIVE:
        raise ValueError("ARCHIVE_TOO_LARGE")
    with destination.open("xb") as target:
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9, allowZip64=False) as archive:
            for name, content in sorted(items.items()):
                archive.writestr(zipinfo(name), content, compress_type=zipfile.ZIP_DEFLATED,
                                 compresslevel=9)
    return {"gate": "DF041_DETERMINISTIC_ALLOWLIST_EXPORT_PASS",
            "source_commit": revision, "files": len(items),
            "zip_sha256": sha256(destination.read_bytes()).hexdigest(),
            "bytes": destination.stat().st_size, "output": str(destination),
            "includes_private_receipts": False, "public_release_approved": False}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    try:
        print(json.dumps(build(args.output), sort_keys=True, indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        print("DF041_EXPORT_REFUSED=" + type(error).__name__, file=sys.stderr)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
