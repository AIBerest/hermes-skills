from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import zipfile

SECRET_PATTERNS = [
    re.compile(rb"-----BEGIN (?:RSA |OPENSSH |EC |DSA |)?PRIVATE KEY-----"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(rb"(?<![A-Za-z0-9])sk-[A-Za-z0-9]{32,}"),
    re.compile(rb"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
]

class ArchiveSecurityError(ValueError):
    pass

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())

def resolve_allowlist(root: Path, items: list[str] | None = None) -> list[tuple[Path, str]]:
    root = root.resolve()
    if items is None:
        candidates = [p for p in sorted(root.rglob("*")) if "out" not in p.relative_to(root).parts]
    else:
        candidates = [root / item for item in items]
    files = []
    seen_case = set()
    for p in candidates:
        rel_path = p.relative_to(root) if p.is_absolute() and str(p).startswith(str(root)) else p.relative_to(root) if p.exists() and root in p.parents else None
        if rel_path is None:
            rel_path = p.relative_to(root)
        rel = rel_path.as_posix()
        if rel.startswith("../") or rel.startswith("/") or "\x00" in rel:
            raise ArchiveSecurityError(f"path escape: {rel}")
        st = p.lstat()
        if stat.S_ISLNK(st.st_mode):
            raise ArchiveSecurityError(f"SGV-PACKAGE-SYMLINK: {rel}")
        if not stat.S_ISREG(st.st_mode):
            if p.is_dir():
                continue
            raise ArchiveSecurityError(f"SGV-PACKAGE-SPECIAL-FILE: {rel}")
        resolved = p.resolve(strict=True)
        if not resolved.is_relative_to(root):
            raise ArchiveSecurityError(f"SGV-PACKAGE-PATH-ESCAPE: {rel}")
        lowered = rel.lower()
        if lowered in seen_case:
            raise ArchiveSecurityError(f"SGV-PACKAGE-CASE-COLLISION: {rel}")
        seen_case.add(lowered)
        data = p.read_bytes()
        if any(pat.search(data) for pat in SECRET_PATTERNS):
            raise ArchiveSecurityError(f"SGV-PACKAGE-SECRET: {rel}")
        files.append((p, rel))
    return sorted(files, key=lambda item: item[1])

def deterministic_zip(root: str | Path, archive: str | Path, manifest: str | Path, items: list[str] | None = None) -> dict:
    root = Path(root).resolve(); archive = Path(archive); manifest = Path(manifest)
    archive.parent.mkdir(parents=True, exist_ok=True); manifest.parent.mkdir(parents=True, exist_ok=True)
    files = resolve_allowlist(root, items)
    file_records = []
    for p, rel in files:
        file_records.append({"path": rel, "sha256": sha256_file(p), "bytes": p.stat().st_size, "mode": "0644"})
    embedded = {"manifest_version": "1.0", "files": file_records, "secret_scan": "passed"}
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for record, (p, rel) in zip(file_records, files):
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            zf.writestr(info, p.read_bytes())
        info = zipfile.ZipInfo("MANIFEST.json", date_time=(1980, 1, 1, 0, 0, 0))
        info.external_attr = 0o100644 << 16
        zf.writestr(info, json.dumps(embedded, ensure_ascii=False, indent=2, sort_keys=True).encode())
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        if any(name.startswith("../") or name.startswith("/") for name in names):
            raise ArchiveSecurityError("SGV-PACKAGE-ZIP-TRAVERSAL")
        for record in file_records:
            if sha256_bytes(zf.read(record["path"])) != record["sha256"]:
                raise ArchiveSecurityError(f"SGV-PACKAGE-ZIP-HASH-MISMATCH: {record['path']}")
    result = {"ok": True, "archive": str(archive), "hash": sha256_file(archive), "files": file_records, "embedded_manifest": "MANIFEST.json"}
    manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
