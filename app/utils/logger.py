from __future__ import annotations

"""
JSON audit log writer.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR: Final[Path] = PROJECT_ROOT / "logs"
AUDIT_LOG_PATH: Final[Path] = LOGS_DIR / "audit.jsonl"


@dataclass
class AuditLogEntry:
    """
    Schema for audit log records.
    """

    audit_id: str
    user_id: str
    task_type: str
    policy_decision: str
    timestamp: str
    input: str
    output_summary: str


def write_audit_log_entry(entry: AuditLogEntry) -> None:
    """
    Append a JSON audit log entry to the audit.jsonl file.

    The logs directory is created if it does not already exist.

    Args:
        entry: Populated AuditLogEntry instance.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        json_record = json.dumps(asdict(entry), ensure_ascii=False)
        f.write(json_record + "\n")


