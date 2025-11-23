from __future__ import annotations

"""
FastAPI route definitions.
"""

from fastapi import APIRouter

from app.models.request_models import OrchestrateRequest
from app.models.response_models import OrchestrateResponse
from app.services.orchestrator import orchestrate


router = APIRouter()


@router.post(
    "/orchestrate",
    response_model=OrchestrateResponse,
    summary="Run the policy-aware LLM workflow orchestrator.",
)
async def orchestrate_endpoint(payload: OrchestrateRequest) -> OrchestrateResponse:
    """
    Orchestrate a single LLM workflow request.

    This endpoint:
      * Classifies the request into a task type.
      * Applies policy evaluation (allow, block, modify).
      * Delegates to the task agent (Claude) when allowed.
      * Writes an audit log entry.
    """
    result_dict = orchestrate(user_id=payload.user_id, text=payload.request_text)
    return OrchestrateResponse(**result_dict)


