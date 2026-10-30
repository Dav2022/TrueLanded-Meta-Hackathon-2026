"""Verify exactly the bytes listed by the owner-issued manifest. Offline only.

Integrity is local/self-issued, not authentication of Meta or the document issuer.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath


class BundleRefusal(ValueError):
    pass


def verify(root: Path) -> dict:
    root = Path(root)
    manifest_path = root / "MANIFEST.json"
    if not root.is_dir() or root.is_symlink() or not manifest_path.is_file():
        raise BundleRefusal("JUDGE_BUNDLE_ROOT_OR_MANIFEST_MISSING")
    if manifest_path.is_symlink() or manifest_path.stat().st_size > 30_000:
        raise BundleRefusal("MANIFEST_UNSAFE")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf8"))
    except (OSError, UnicodeError, ValueError):
        raise BundleRefusal("MANIFEST_INVALID") from None
    if (not isinstance(manifest, dict) or
        manifest.get("schema") != "DF041_JUDGE_KIT_ALLOWLIST_SHA256_V1" or
        manifest.get("mode") != "PRIVATE_REPRODUCIBILITY_REVIEW_NOT_PUBLIC_RELEASE" or
        manifest.get("evidence") != "SYNTHETIC_OFFLINE_NO_MODEL_CALL" or
        manifest.get("private_model_receipts_included") is not False or
        manifest.get("provider_signed") is not False or
        manifest.get("redistribution_authorized") is not False or
        manifest.get("manifest_issued_by") != "TRUELANDED_OWNER_LOCAL_BUILD_NOT_META"):
        raise BundleRefusal("MANIFEST_AUTHORITY_REFUSED")
    files = manifest.get("files")
    if not isinstance(files, dict) or not 20 <= len(files) <= 60:
        raise BundleRefusal("MANIFEST_FILE_COUNT_REFUSED")
    expected = set(files) | {"MANIFEST.json"}
    actual = set()
    for item in root.rglob("*"):
        relative = item.relative_to(root)
        if relative.parts[0] == ".git":
            if relative.parts == (".git",) and item.is_symlink():
                raise BundleRefusal("SYMLINK_GIT_METADATA_REFUSED")
            continue  # Git metadata exists in a clone, unlike an extracted ZIP.
        if item.is_symlink():
            raise BundleRefusal("SYMLINK_REFUSED")
        if item.is_file():
            name = item.relative_to(root).as_posix()
            actual.add(name)
    if expected != actual:
        raise BundleRefusal("EXTRA_OR_MISSING_FILE")
    for name, entry in files.items():
        p = PurePosixPath(name)
        if (p.is_absolute() or "\\" in name or ".." in p.parts or
            str(p) != name or not isinstance(entry, dict) or
            name.startswith(".") or not isinstance(entry.get("sha256"), str)):
            raise BundleRefusal("UNSAFE_FILE_ENTRY")
        file = root.joinpath(*p.parts)
        if not file.is_file() or file.stat().st_size > 160_000:
            raise BundleRefusal("SOURCE_FILE_MISSING_OR_OVERSIZED")
        raw = file.read_bytes()
        if len(raw) != entry.get("bytes") or sha256(raw).hexdigest() != entry["sha256"]:
            raise BundleRefusal("SOURCE_HASH_MISMATCH")
    return {"gate": "DF041_SELF_ISSUED_BUNDLE_BYTES_MATCH",
            "files_verified": len(files), "source_commit": manifest.get("source_commit"),
            "private_receipts_included": False, "provider_attestation": False,
            "public_release_approved": False}


if __name__ == "__main__":
    print(json.dumps(verify(Path(__file__).resolve().parent), indent=2))
