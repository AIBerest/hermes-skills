from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

EVIDENCE_TYPES = {"command_result", "file_hash", "git_diff", "api_response", "log_excerpt", "screenshot", "manual_observation", "external_source_snapshot", "delivery_ack", "approval_manifest"}
RESULTS = {"pass", "fail", "stale", "unverified"}

@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    goal_id: str
    contract_revision: int
    phase_id: str
    criterion_id: str
    type: str
    producer: str
    captured_at: str
    fresh_until: str
    replayable: bool
    result: str
    command: str | None = None
    exit_code: int | None = None
    stdout_path: str | None = None
    stderr_path: str | None = None
    artifact_sha256: str | None = None
    redaction: str = "passed"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.type not in EVIDENCE_TYPES:
            raise ValueError(f"unsupported evidence type: {self.type}")
        if self.result not in RESULTS:
            raise ValueError(f"unsupported evidence result: {self.result}")
        for name in ("evidence_id", "goal_id", "phase_id", "criterion_id", "producer", "captured_at", "fresh_until"):
            if not getattr(self, name):
                raise ValueError(f"{name} is required")

    @classmethod
    def pass_record(cls, *, evidence_id: str, goal_id: str, contract_revision: int, phase_id: str, criterion_id: str, type: str = "command_result", producer: str = "goal_executor", command: str | None = None, exit_code: int | None = 0) -> "EvidenceRecord":
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        return cls(evidence_id=evidence_id, goal_id=goal_id, contract_revision=contract_revision, phase_id=phase_id, criterion_id=criterion_id, type=type, producer=producer, captured_at=now, fresh_until="audit_end", replayable=True, result="pass", command=command, exit_code=exit_code)

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None and (k != "metadata" or v)}


def write_evidence(path: str | Path, records: list[EvidenceRecord]) -> None:
    Path(path).write_text(json.dumps([r.to_dict() for r in records], ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_evidence(path: str | Path) -> list[EvidenceRecord]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [EvidenceRecord(**item) for item in data]
