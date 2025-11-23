from __future__ import annotations

"""
Intake agent responsible for classifying user requests into task types.
"""

from typing import Literal


TaskType = Literal[
    "document_summarization",
    "data_extraction",
    "general_query",
    "unknown",
]


class IntakeAgent:
    """
    Simple heuristic-based intake agent for classifying requests.
    """

    def classify(self, request_text: str) -> TaskType:
        """
        Classify the incoming request text into a task type.

        Args:
            request_text: Raw user request text.

        Returns:
            TaskType: Classified task type.
        """
        text = request_text.lower()

        # Document summarization heuristics
        summarization_keywords = [
            "summarize",
            "summary",
            "tl;dr",
            "briefly describe",
            "condense",
        ]
        if any(keyword in text for keyword in summarization_keywords):
            return "document_summarization"

        # Data extraction heuristics
        extraction_keywords = [
            "extract",
            "pull out",
            "structured",
            "fields",
            "key information",
            "parse",
        ]
        if any(keyword in text for keyword in extraction_keywords):
            return "data_extraction"

        # General query heuristics
        question_starters = [
            "how ",
            "what ",
            "why ",
            "where ",
            "who ",
            "when ",
        ]
        if text.strip().endswith("?") or any(
            text.strip().startswith(q) for q in question_starters
        ):
            return "general_query"

        return "unknown"


