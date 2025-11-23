from __future__ import annotations

"""
Pydantic request models for API endpoints.
"""

from pydantic import BaseModel, Field


class OrchestrateRequest(BaseModel):
    """
    Request body schema for the /orchestrate endpoint.
    """

    user_id: str = Field(..., description="Unique identifier of the end user.")
    request_text: str = Field(
        ...,
        description="Natural language request text to be processed by the orchestrator.",
    )


