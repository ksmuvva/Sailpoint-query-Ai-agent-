"""Factory for creating LLM provider instances."""

from sailpoint_agent.llm.base import LLMProvider
from sailpoint_agent.llm.claude_provider import ClaudeProvider
from sailpoint_agent.llm.openai_provider import OpenAIProvider
from sailpoint_agent.llm.litellm_provider import LiteLLMProvider
from sailpoint_agent.models.config import LLMConfig


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    _providers: dict[str, type[LLMProvider]] = {
        "claude": ClaudeProvider,
        "anthropic": ClaudeProvider,
        "openai": OpenAIProvider,
        "gpt": OpenAIProvider,
        "litellm": LiteLLMProvider,
    }

    @classmethod
    def create(cls, config: LLMConfig) -> LLMProvider:
        """Create an LLM provider based on configuration.

        Falls back to LiteLLMProvider for unknown provider names.
        """
        provider_class = cls._providers.get(config.provider.lower(), LiteLLMProvider)
        return provider_class(config)

    @classmethod
    def register(cls, name: str, provider_class: type[LLMProvider]) -> None:
        """Register a new LLM provider type."""
        cls._providers[name.lower()] = provider_class
