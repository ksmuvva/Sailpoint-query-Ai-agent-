"""Catch-all LLM provider using LiteLLM for 100+ model support.

Supports: Claude, OpenAI, GLM, Gemini, Mistral, Llama, and more.
Model format: "provider/model" (e.g., "anthropic/claude-sonnet-4-20250514", "openai/gpt-4")
"""

from typing import AsyncIterator, Optional

import litellm

from sailpoint_agent.llm.base import LLMProvider, LLMResponse, ToolCall
from sailpoint_agent.models.config import LLMConfig


class LiteLLMProvider(LLMProvider):
    """LLM provider using LiteLLM for unified multi-model access."""

    def __init__(self, config: LLMConfig):
        self.model_name = config.model
        self.default_temperature = config.temperature
        self.default_max_tokens = config.max_tokens
        if config.api_key:
            litellm.api_key = config.api_key
        if config.api_base_url:
            litellm.api_base = config.api_base_url

    async def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens or self.default_max_tokens,
            "temperature": temperature if temperature is not None else self.default_temperature,
        }
        if tools:
            kwargs["tools"] = tools

        response = await litellm.acompletion(**kwargs)
        choice = response.choices[0]

        tool_calls = []
        if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(ToolCall(
                    name=tc.function.name,
                    arguments=tc.function.arguments
                    if isinstance(tc.function.arguments, dict)
                    else {},
                ))

        return LLMResponse(
            content=choice.message.content or "",
            tool_calls=tool_calls,
            tokens_prompt=response.usage.prompt_tokens,
            tokens_completion=response.usage.completion_tokens,
            model=self.model_name,
        )

    async def stream(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
    ) -> AsyncIterator[str]:
        response = await litellm.acompletion(
            model=self.model_name,
            messages=messages,
            max_tokens=self.default_max_tokens,
            temperature=temperature if temperature is not None else self.default_temperature,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
