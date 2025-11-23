from __future__ import annotations

"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI

from app.api.routes import router as orchestrator_router


app = FastAPI(
    title="Policy-Aware LLM Workflow Orchestrator",
    version="0.1.0",
    description=(
        "A policy-aware orchestrator that routes user requests through "
        "intake, policy evaluation, and LLM task execution with JSON auditing."
    ),
)


app.include_router(orchestrator_router)


