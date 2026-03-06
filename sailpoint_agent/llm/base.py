"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional


@dataclass
class ToolCall:
    """A tool/function call requested by the LLM."""
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    tokens_prompt: int = 0
    tokens_completion: int = 0
    model: str = ""


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    When using Claude (the default path), the Claude Agent SDK handles
    everything natively. This ABC is only used for the non-Claude LLM path.
    """

    model_name: str = ""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Send a chat completion request."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
    ) -> AsyncIterator[str]:
        """Stream a chat completion response."""
        ...
