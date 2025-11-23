from __future__ import annotations

"""
Task agent that delegates execution to Anthropic Claude with structured JSON output.
"""

import json
from typing import Any, Dict

from anthropic import Anthropic

from app.core.config import get_anthropic_client
from app.agents.intake_agent import TaskType


class TaskAgent:
    """
    Executes tasks by calling Anthropic Claude with JSON-structured responses.
    """

    def __init__(self, client: Anthropic | None = None) -> None:
        """
        Initialize the task agent.

        The Anthropic client is resolved lazily to make testing easier.

        Args:
            client: Optional pre-configured Anthropic client.
        """
        self._client: Anthropic | None = client

    @property
    def client(self) -> Anthropic:
        """
        Return a configured Anthropic client, creating it lazily if needed.
        """
        if self._client is None:
            self._client = get_anthropic_client()
        return self._client

    def _build_prompt(self, task_type: TaskType, text: str) -> str:
        """
        Build a thin task-specific instruction that wraps the user text.
        """
        if task_type == "document_summarization":
            instructions = (
                "You are an assistant that summarizes documents. "
                "Return a concise JSON object with the following shape:\n"
                '{\n'
                '  "summary": "short paragraph summary",\n'
                '  "key_points": ["bullet point 1", "bullet point 2"]\n'
                "}\n"
                "Only return valid JSON."
            )
        elif task_type == "data_extraction":
            instructions = (
                "You are an assistant that extracts structured data from text. "
                "Return a JSON object describing the key fields you find, for example:\n"
                '{\n'
                '  "fields": {\n'
                '    "names": ["..."],\n'
                '    "dates": ["..."],\n'
                '    "amounts": ["..."]\n'
                "  }\n"
                "}\n"
                "Only return valid JSON."
            )
        elif task_type == "general_query":
            instructions = (
                "You are a helpful assistant answering a general query. "
                "Return a JSON object with this shape:\n"
                '{\n'
                '  "answer": "direct answer in natural language",\n'
                '  "supporting_facts": ["fact 1", "fact 2"]\n'
                "}\n"
                "Only return valid JSON."
            )
        else:
            instructions = (
                "You are a robust assistant handling an unclassified request. "
                "Return a JSON object that captures your best response, with this shape:\n"
                '{\n'
                '  "answer": "your answer",\n'
                '  "notes": "any caveats or assumptions"\n'
                "}\n"
                "Only return valid JSON."
            )

        return f"{instructions}\n\nUser request:\n{text}"

    def run_task(self, task_type: TaskType, text: str) -> Dict[str, Any]:
        """
        Execute a task of the given type using Claude with JSON output mode.

        Args:
            task_type: Classified task type.
            text: Text to operate on (original or policy-modified).

        Returns:
            dict: Parsed JSON object returned by Claude.

        Raises:
            RuntimeError: If the Claude response cannot be parsed as JSON.
        """
        prompt = self._build_prompt(task_type, text)

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        # Anthropic response contains a list of content blocks.
        if not response.content:
            raise RuntimeError("Claude returned an empty response.")

        first_block = response.content[0]
        raw_text = getattr(first_block, "text", None) or str(first_block)

        try:
            parsed: Dict[str, Any] = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Claude returned invalid JSON content.") from exc

        if not isinstance(parsed, dict):
            raise RuntimeError("Claude JSON response is not a JSON object.")

        return parsed


