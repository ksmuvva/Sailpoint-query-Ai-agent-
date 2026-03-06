"""Tests for agent definitions and SDK integration."""

import pytest
from unittest.mock import patch, MagicMock


def test_sailpoint_tools_list():
    """Verify SAILPOINT_TOOLS contains expected tool names."""
    from sailpoint_agent.agents.definitions import SAILPOINT_TOOLS

    assert "WebSearch" in SAILPOINT_TOOLS
    assert "WebFetch" in SAILPOINT_TOOLS
    assert "Skill" in SAILPOINT_TOOLS
    assert "mcp__sailpoint-tools__sailpoint_web_search" in SAILPOINT_TOOLS
    assert "mcp__sailpoint-tools__api_lookup" in SAILPOINT_TOOLS
    assert "mcp__sailpoint-tools__doc_retriever" in SAILPOINT_TOOLS


@patch("sailpoint_agent.agents.definitions.AgentDefinition")
def test_create_sailpoint_agents_returns_four_agents(mock_agent_def):
    """Verify four multi-specialized agents are created."""
    mock_agent_def.side_effect = lambda **kwargs: MagicMock(**kwargs)

    from sailpoint_agent.agents.definitions import create_sailpoint_agents

    agents = create_sailpoint_agents()

    assert len(agents) == 4
    assert "sailpoint-expert-alpha" in agents
    assert "sailpoint-expert-beta" in agents
    assert "sailpoint-expert-gamma" in agents
    assert "sailpoint-expert-delta" in agents


@patch("sailpoint_agent.agents.definitions.AgentDefinition")
def test_all_agents_have_same_tools(mock_agent_def):
    """Verify all agents share the same tool set."""
    captured_tools = []
    mock_agent_def.side_effect = lambda **kwargs: (captured_tools.append(kwargs.get("tools")), MagicMock(**kwargs))[1]

    from sailpoint_agent.agents.definitions import create_sailpoint_agents

    create_sailpoint_agents()

    # All agents should have identical tool lists
    for tools in captured_tools:
        assert tools == captured_tools[0]


@patch("sailpoint_agent.agents.definitions.AgentDefinition")
def test_all_agents_have_same_prompt(mock_agent_def):
    """Verify all agents share the same system prompt."""
    captured_prompts = []
    mock_agent_def.side_effect = lambda **kwargs: (captured_prompts.append(kwargs.get("prompt")), MagicMock(**kwargs))[1]

    from sailpoint_agent.agents.definitions import create_sailpoint_agents

    create_sailpoint_agents()

    for prompt in captured_prompts:
        assert prompt == captured_prompts[0]
        assert "MULTI-SPECIALIZED" in prompt
