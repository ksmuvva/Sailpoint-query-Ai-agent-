"""Token usage accounting for LLM API calls."""

from dataclasses import dataclass, field
from sailpoint_agent.utils.logger import get_logger

log = get_logger("token_tracker")


@dataclass
class TokenUsage:
    """Token usage for a single request."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model: str = ""

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class TokenTracker:
    """Tracks cumulative token usage across multiple requests."""
    history: list[TokenUsage] = field(default_factory=list)

    def record(self, prompt_tokens: int, completion_tokens: int, model: str = "") -> None:
        """Record token usage for a single request."""
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model=model,
        )
        self.history.append(usage)
        log.info(
            "token_usage",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=usage.total_tokens,
            model=model,
        )

    @property
    def total_prompt_tokens(self) -> int:
        return sum(u.prompt_tokens for u in self.history)

    @property
    def total_completion_tokens(self) -> int:
        return sum(u.completion_tokens for u in self.history)

    @property
    def total_tokens(self) -> int:
        return self.total_prompt_tokens + self.total_completion_tokens

    @property
    def request_count(self) -> int:
        return len(self.history)

    def summary(self) -> dict:
        """Return a summary of token usage."""
        return {
            "requests": self.request_count,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
        }
