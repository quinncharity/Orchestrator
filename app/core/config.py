from __future__ import annotations

"""
Application configuration and Anthropic client initialization.
"""

from dataclasses import dataclass
from functools import lru_cache
import os
from typing import Final

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

ANTHROPIC_API_KEY_ENV: Final[str] = "ANTHROPIC_API_KEY"


@dataclass
class Settings:
    """
    Simple settings container for application configuration.
    """

    anthropic_api_key: str


@lru_cache
def get_settings() -> Settings:
    """
    Load settings from environment variables and return a cached Settings instance.

    Raises:
        RuntimeError: If the Anthropic API key is not configured.
    """
    api_key = os.getenv(ANTHROPIC_API_KEY_ENV)
    if not api_key:
        raise RuntimeError(
            f"{ANTHROPIC_API_KEY_ENV} is not set. "
            "Configure it in your environment or .env file."
        )

    return Settings(anthropic_api_key=api_key)


@lru_cache
def get_anthropic_client() -> Anthropic:
    """
    Create and cache a configured Anthropic client.

    Returns:
        Anthropic: Configured Anthropic client instance.
    """
    settings = get_settings()
    return Anthropic(api_key=settings.anthropic_api_key)


