"""Configuration models for the SailPoint Query AI Agent."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMConfig:
    """Configuration for a single LLM provider."""
    provider: str = "claude"
    model: str = "claude-sonnet-4-20250514"
    api_key: str = ""
    api_base_url: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 4096
    timeout: int = 60


@dataclass
class AgentConfig:
    """Configuration for agent behavior."""
    max_iterations: int = 5
    confidence_threshold: float = 0.85
    enable_traces: bool = False
    search_depth: int = 3


@dataclass
class SearchConfig:
    """Configuration for web search behavior."""
    sailpoint_domains: list[str] = field(default_factory=lambda: [
        "developer.sailpoint.com",
        "documentation.sailpoint.com",
        "community.sailpoint.com",
        "github.com/sailpoint-oss",
    ])
    max_results_per_search: int = 5
    fetch_page_content: bool = True
    fallback_to_general_web: bool = True


@dataclass
class AppConfig:
    """Root application configuration."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    fallback_llm: Optional[LLMConfig] = None
    agent: AgentConfig = field(default_factory=AgentConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    log_level: str = "INFO"
    log_format: str = "json"
