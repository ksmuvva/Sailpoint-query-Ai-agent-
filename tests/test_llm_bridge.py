"""Tests for LLM provider bridge and factory."""

import pytest
from unittest.mock import patch, MagicMock

from sailpoint_agent.models.config import LLMConfig
from sailpoint_agent.llm.factory import LLMProviderFactory


def test_factory_creates_claude_provider():
    """Verify factory creates ClaudeProvider for 'claude' config."""
    config = LLMConfig(provider="claude", model="claude-sonnet-4-20250514", api_key="test")

    with patch("sailpoint_agent.llm.claude_provider.anthropic"):
        provider = LLMProviderFactory.create(config)

    from sailpoint_agent.llm.claude_provider import ClaudeProvider
    assert isinstance(provider, ClaudeProvider)


def test_factory_creates_claude_for_anthropic():
    """Verify factory creates ClaudeProvider for 'anthropic' alias."""
    config = LLMConfig(provider="anthropic", model="claude-sonnet-4-20250514", api_key="test")

    with patch("sailpoint_agent.llm.claude_provider.anthropic"):
        provider = LLMProviderFactory.create(config)

    from sailpoint_agent.llm.claude_provider import ClaudeProvider
    assert isinstance(provider, ClaudeProvider)


def test_factory_creates_openai_provider():
    """Verify factory creates OpenAIProvider for 'openai' config."""
    config = LLMConfig(provider="openai", model="gpt-4", api_key="test")

    with patch("sailpoint_agent.llm.openai_provider.AsyncOpenAI"):
        provider = LLMProviderFactory.create(config)

    from sailpoint_agent.llm.openai_provider import OpenAIProvider
    assert isinstance(provider, OpenAIProvider)


def test_factory_creates_litellm_for_unknown():
    """Verify factory falls back to LiteLLMProvider for unknown providers."""
    config = LLMConfig(provider="unknown-provider", model="some-model")

    with patch("sailpoint_agent.llm.litellm_provider.litellm"):
        provider = LLMProviderFactory.create(config)

    from sailpoint_agent.llm.litellm_provider import LiteLLMProvider
    assert isinstance(provider, LiteLLMProvider)


def test_factory_register_custom_provider():
    """Verify custom providers can be registered."""
    from sailpoint_agent.llm.base import LLMProvider

    class CustomProvider(LLMProvider):
        def __init__(self, config):
            self.model_name = config.model

        async def chat(self, messages, tools=None, temperature=None, max_tokens=None):
            pass

        async def stream(self, messages, temperature=None):
            yield ""

    LLMProviderFactory.register("custom", CustomProvider)
    config = LLMConfig(provider="custom", model="custom-model")
    provider = LLMProviderFactory.create(config)

    assert isinstance(provider, CustomProvider)
    assert provider.model_name == "custom-model"

    # Cleanup
    del LLMProviderFactory._providers["custom"]


def test_config_defaults():
    """Verify LLMConfig has sensible defaults."""
    config = LLMConfig()

    assert config.provider == "claude"
    assert config.model == "claude-sonnet-4-20250514"
    assert config.temperature == 0.1
    assert config.max_tokens == 4096
    assert config.timeout == 60
