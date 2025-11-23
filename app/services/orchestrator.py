from __future__ import annotations

"""
Main workflow orchestration: intake → policy → task + audit logging.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from app.agents.intake_agent import IntakeAgent, TaskType
from app.agents.task_agent import TaskAgent
from app.core.policy import evaluate
from app.models.response_models import OrchestrateResponse
from app.utils.logger import AuditLogEntry, write_audit_log_entry


intake_agent = IntakeAgent()
task_agent = TaskAgent()


def _summarize_agent_output(agent_output: Dict[str, Any] | None) -> str:
    """
    Create a short, log-safe summary of the agent output.

    The goal is to avoid storing the full Claude response in the audit log.
    """
    if not agent_output:
        return ""

    # Prefer well-known keys, otherwise fall back to a truncated JSON string.
    for key in ("summary", "answer", "notes"):
        value = agent_output.get(key)
        if isinstance(value, str):
            return value[:500]

    serialized = json.dumps(agent_output, ensure_ascii=False)
    return serialized[:500]


def orchestrate(user_id: str, text: str) -> Dict[str, Any]:
    """
    Orchestrate the full workflow for a single user request.

    Steps:
        1. Classify request into task type via intake agent.
        2. Evaluate policy for the task and text.
        3. If blocked, skip task execution.
        4. If modified, run task on modified text.
        5. Otherwise, run task on original text.
        6. Write an audit log entry.

    Args:
        user_id: Identifier of the end user.
        text: Raw request text.

    Returns:
        dict: Serialized OrchestrateResponse-compatible dictionary.
    """
    task_type: TaskType = intake_agent.classify(text)
    policy = evaluate(task_type=task_type, text=text)
    decision: str = policy["decision"]
    modified_text: str | None = policy.get("modified_text") or None

    effective_text = modified_text if decision == "modify" and modified_text else text

    agent_output: Dict[str, Any] | None = None
    if decision != "block":
        agent_output = task_agent.run_task(task_type=task_type, text=effective_text)

    audit_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = AuditLogEntry(
        audit_id=audit_id,
        user_id=user_id,
        task_type=task_type,
        policy_decision=decision,
        timestamp=timestamp,
        input=effective_text if decision != "block" else text,
        output_summary=_summarize_agent_output(agent_output),
    )
    write_audit_log_entry(audit_entry)

    response_model = OrchestrateResponse(
        task_type=task_type,
        policy_decision=decision,  # type: ignore[arg-type]
        agent_output=agent_output,
        audit_id=audit_id,
        timestamp=timestamp,
    )

    # Pydantic v1/v2 compatibility for serialization
    try:
        return response_model.model_dump()
    except AttributeError:
        return response_model.dict()


