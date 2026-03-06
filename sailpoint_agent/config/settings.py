"""Configuration loader — merges config.yaml + .env + CLI overrides."""

import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

from sailpoint_agent.models.config import AppConfig, LLMConfig, AgentConfig, SearchConfig


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """Load application configuration from YAML file and environment variables.

    Priority (highest to lowest):
    1. Environment variables
    2. config.yaml values
    3. Dataclass defaults
    """
    load_dotenv()

    yaml_config: dict = {}
    if config_path:
        path = Path(config_path)
        if path.exists():
            with open(path) as f:
                yaml_config = yaml.safe_load(f) or {}

    # Build LLM config
    llm_yaml = yaml_config.get("llm", {})
    llm = LLMConfig(
        provider=os.getenv("LLM_PROVIDER", llm_yaml.get("provider", "claude")),
        model=os.getenv("LLM_MODEL", llm_yaml.get("model", "claude-sonnet-4-20250514")),
        api_key=_resolve_api_key(llm_yaml.get("provider", "claude")),
        api_base_url=os.getenv("LLM_API_BASE", llm_yaml.get("api_base_url")),
        temperature=float(llm_yaml.get("temperature", 0.1)),
        max_tokens=int(llm_yaml.get("max_tokens", 4096)),
        timeout=int(llm_yaml.get("timeout", 60)),
    )

    # Build fallback LLM config
    fallback_llm = None
    fallback_yaml = yaml_config.get("fallback_llm")
    if fallback_yaml:
        fallback_llm = LLMConfig(
            provider=fallback_yaml.get("provider", "openai"),
            model=fallback_yaml.get("model", "gpt-4"),
            api_key=_resolve_api_key(fallback_yaml.get("provider", "openai")),
            temperature=float(fallback_yaml.get("temperature", 0.1)),
            max_tokens=int(fallback_yaml.get("max_tokens", 4096)),
        )

    # Build agent config
    agent_yaml = yaml_config.get("agent", {})
    agent = AgentConfig(
        max_iterations=int(agent_yaml.get("max_iterations", 5)),
        confidence_threshold=float(agent_yaml.get("confidence_threshold", 0.85)),
        enable_traces=bool(agent_yaml.get("enable_traces", False)),
        search_depth=int(agent_yaml.get("search_depth", 3)),
    )

    # Build search config
    search_yaml = yaml_config.get("search", {})
    search = SearchConfig(
        sailpoint_domains=search_yaml.get("sailpoint_domains", SearchConfig().sailpoint_domains),
        max_results_per_search=int(search_yaml.get("max_results_per_search", 5)),
        fetch_page_content=bool(search_yaml.get("fetch_page_content", True)),
        fallback_to_general_web=bool(search_yaml.get("fallback_to_general_web", True)),
    )

    return AppConfig(
        llm=llm,
        fallback_llm=fallback_llm,
        agent=agent,
        search=search,
        log_level=os.getenv("LOG_LEVEL", yaml_config.get("log_level", "INFO")),
        log_format=yaml_config.get("log_format", "json"),
    )


def _resolve_api_key(provider: str) -> str:
    """Resolve API key from environment variables based on provider name."""
    key_map = {
        "claude": "ANTHROPIC_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "gpt": "OPENAI_API_KEY",
        "glm": "GLM_API_KEY",
    }
    env_var = key_map.get(provider.lower(), "LITELLM_API_KEY")
    return os.getenv(env_var, "")
