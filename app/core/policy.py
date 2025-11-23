from __future__ import annotations

"""
Policy evaluation logic for user requests.
"""

import re
from typing import Any, Dict, Literal, TypedDict


PolicyDecision = Literal["allow", "block", "modify"]


class PolicyResult(TypedDict):
    """
    Typed structure for policy evaluation results.
    """

    decision: PolicyDecision
    reason: str
    modified_text: str | None


DISALLOWED_KEYWORDS = [
    "build a bomb",
    "make a bomb",
    "terrorist attack",
    "kill",
    "assassinate",
]


def _contains_disallowed_content(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in DISALLOWED_KEYWORDS)


EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    re.MULTILINE,
)

PHONE_PATTERN = re.compile(
    r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}\b",
    re.MULTILINE,
)


def _redact_pii(text: str) -> str:
    """
    Redact simple forms of PII such as emails and phone numbers.
    """
    redacted = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
    redacted = PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)
    return redacted


def evaluate(task_type: str, text: str) -> Dict[str, Any]:
    """
    Evaluate policy for the given task type and text.

    Args:
        task_type: Classified task type.
        text: Raw input text from user.

    Returns:
        dict: PolicyResult-shaped dictionary containing the decision, reason,
        and optionally modified text.
    """
    if _contains_disallowed_content(text):
        return PolicyResult(
            decision="block",
            reason="Blocked due to disallowed content.",
            modified_text=None,
        )

    redacted_text = _redact_pii(text)
    if redacted_text != text:
        return PolicyResult(
            decision="modify",
            reason="Modified to redact potential PII.",
            modified_text=redacted_text,
        )

    return PolicyResult(
        decision="allow",
        reason="Allowed by default policy. No disallowed content detected.",
        modified_text=None,
    )


