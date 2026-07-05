from __future__ import annotations

import hashlib
import json
from pathlib import Path

class ReceiptValidationError(ValueError):
    pass

def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_review_receipt(receipt: dict, *, target: str, hashes: dict[str, str]) -> None:
    required = {"ok", "sent", "kind", "pack_version", "target", "files", "hashes", "message_ids"}
    missing = required - receipt.keys()
    if missing:
        raise ReceiptValidationError(f"missing receipt fields: {', '.join(sorted(missing))}")
    if receipt.get("ok") is not True or receipt.get("sent") is not True:
        raise ReceiptValidationError("receipt not ok/sent")
    if receipt.get("kind") != "review-md-files" or receipt.get("pack_version") != "review_pack_v2":
        raise ReceiptValidationError("receipt kind/version mismatch")
    if receipt.get("target") != target or receipt.get("hashes") != hashes:
        raise ReceiptValidationError("receipt target/hash mismatch")
    files = receipt.get("files")
    if sorted(files) != sorted(hashes):
        raise ReceiptValidationError("receipt file set mismatch")
    message_ids = receipt.get("message_ids")
    if not isinstance(message_ids, list) or len(message_ids) != len(files) or not all(str(x).strip() for x in message_ids):
        raise ReceiptValidationError("receipt message_ids invalid")

def validate_final_receipt(receipt: dict, *, target: str, archive: str, hash_: str) -> None:
    required = {"ok", "sent", "kind", "target", "archive", "hash", "message_id"}
    missing = required - receipt.keys()
    if missing:
        raise ReceiptValidationError(f"missing receipt fields: {', '.join(sorted(missing))}")
    if receipt.get("ok") is not True or receipt.get("sent") is not True:
        raise ReceiptValidationError("receipt not ok/sent")
    if receipt.get("kind") != "final-artifacts":
        raise ReceiptValidationError("receipt kind mismatch")
    if receipt.get("target") != target or receipt.get("archive") != archive or receipt.get("hash") != hash_:
        raise ReceiptValidationError("receipt target/archive/hash mismatch")
    if not str(receipt.get("message_id", "")).strip():
        raise ReceiptValidationError("receipt message_id invalid")
