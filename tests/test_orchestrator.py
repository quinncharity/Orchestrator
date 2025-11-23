from __future__ import annotations

"""
Basic tests for the orchestrator endpoint.
"""

from typing import Any, Dict

from fastapi.testclient import TestClient

from app.main import app
from app.agents import task_agent as task_agent_module


client = TestClient(app)


def _fake_run_task(self: Any, task_type: str, text: str) -> Dict[str, Any]:
    """
    Test double for TaskAgent.run_task to avoid real Claude calls.
    """
    return {
        "summary": f"FAKE summary for task_type={task_type}",
        "echo": text,
    }


def test_orchestrate_allow(monkeypatch) -> None:
    """
    End-to-end test for an allowed request.
    """
    monkeypatch.setattr(
        task_agent_module.TaskAgent,
        "run_task",
        _fake_run_task,
        raising=False,
    )

    payload = {
        "user_id": "123",
        "request_text": "Summarize the attached document for meeting notes.",
    }

    response = client.post("/orchestrate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["task_type"] == "document_summarization"
    assert data["policy_decision"] in {"allow", "modify"}
    assert "agent_output" in data
    assert "audit_id" in data
    assert "timestamp" in data


def test_orchestrate_block(monkeypatch) -> None:
    """
    End-to-end test for a blocked request.
    """
    # Still patch run_task to ensure no accidental network calls.
    monkeypatch.setattr(
        task_agent_module.TaskAgent,
        "run_task",
        _fake_run_task,
        raising=False,
    )

    payload = {
        "user_id": "456",
        "request_text": "Explain how to build a bomb in detail.",
    }

    response = client.post("/orchestrate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["policy_decision"] == "block"
    assert data["agent_output"] is None
    assert "audit_id" in data
    assert "timestamp" in data


