"""LLM provider for OpenAI models (GPT-4, GPT-4o, etc.)."""

import json
from typing import AsyncIterator, Optional

from openai import AsyncOpenAI

from sailpoint_agent.llm.base import LLMProvider, LLMResponse, ToolCall
from sailpoint_agent.models.config import LLMConfig


class OpenAIProvider(LLMProvider):
    """LLM provider for OpenAI models."""

    def __init__(self, config: LLMConfig):
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.api_base_url,
        )
        self.model_name = config.model
        self.default_temperature = config.temperature
        self.default_max_tokens = config.max_tokens

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

        response = await self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(ToolCall(
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                ))

        return LLMResponse(
            content=choice.message.content or "",
            tool_calls=tool_calls,
            tokens_prompt=response.usage.prompt_tokens,
            tokens_completion=response.usage.completion_tokens,
            model=response.model,
        )

    async def stream(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
    ) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.default_max_tokens,
            temperature=temperature if temperature is not None else self.default_temperature,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
