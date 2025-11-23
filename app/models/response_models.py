from __future__ import annotations

"""
Pydantic response models for API endpoints.
"""

from typing import Any, Dict, Literal

from pydantic import BaseModel, Field


PolicyDecisionLiteral = Literal["allow", "block", "modify"]


class PolicyResultModel(BaseModel):
    """
    Structured representation of a policy evaluation result.
    """

    decision: PolicyDecisionLiteral = Field(
        ...,
        description="Final policy decision for this request.",
    )
    reason: str = Field(..., description="Human-readable explanation of the decision.")
    modified_text: str | None = Field(
        None,
        description="Policy-modified text, if any.",
    )


class OrchestrateResponse(BaseModel):
    """
    Response schema for the /orchestrate endpoint.
    """

    task_type: str = Field(..., description="Classified task type.")
    policy_decision: PolicyDecisionLiteral = Field(
        ...,
        description="Final policy decision ('allow', 'block', or 'modify').",
    )
    agent_output: Dict[str, Any] | None = Field(
        None,
        description="Full JSON output from the task agent, or null if blocked.",
    )
    audit_id: str = Field(..., description="Unique audit identifier for this request.")
    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp indicating when the orchestration completed.",
    )


