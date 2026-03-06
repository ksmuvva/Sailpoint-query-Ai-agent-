"""Main entry point for the SailPoint Query AI Agent.

Uses the Claude Agent SDK's native agentic loop (ReAct pattern).
The SDK handles: reasoning, tool selection, tool execution, observation,
iteration, and final answer synthesis — no custom loop needed.
"""

import os

from claude_agent_sdk import query, ClaudeSDKClient, ClaudeAgentOptions

from sailpoint_agent.agents.definitions import create_sailpoint_agents
from sailpoint_agent.tools import create_sailpoint_mcp_server
from sailpoint_agent.config.settings import load_config
from sailpoint_agent.models.config import AppConfig


def build_sdk_options(app_config: AppConfig) -> ClaudeAgentOptions:
    """Build Claude Agent SDK options with SailPoint tools, agents, and Skills."""

    sailpoint_mcp = create_sailpoint_mcp_server(app_config.search)
    sailpoint_agents = create_sailpoint_agents()

    return ClaudeAgentOptions(
        # Custom SailPoint tools via in-process MCP server
        mcp_servers={
            "sailpoint-tools": sailpoint_mcp,
        },

        # Built-in SDK tools + custom MCP tools + Skills
        allowed_tools=[
            "WebSearch",
            "WebFetch",
            "Skill",
            "Task",
            "mcp__sailpoint-tools__sailpoint_web_search",
            "mcp__sailpoint-tools__api_lookup",
            "mcp__sailpoint-tools__doc_retriever",
        ],

        # Multi-specialized subagents (all equally capable)
        agents=sailpoint_agents,

        # Load Skills from .claude/skills/ and project context from .claude/CLAUDE.md
        setting_sources=["project"],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),

        # Execution limits
        max_turns=app_config.agent.max_iterations * 2,
        permission_mode="default",
    )


async def run_single_query(question: str, app_config: AppConfig) -> str:
    """Execute a single query using the SDK's stateless query() function.

    The SDK manages the entire ReAct loop:
    1. Claude receives the question + system prompt + SailPoint knowledge
    2. Claude reasons about what tools/skills to use
    3. SDK executes tools and feeds results back
    4. Claude iterates until it has a complete answer
    5. Final result is returned
    """
    options = build_sdk_options(app_config)

    result_text = ""
    async for message in query(prompt=question, options=options):
        if message.type == "assistant":
            for block in message.content:
                if hasattr(block, "text"):
                    result_text += block.text
        if message.type == "result" and message.subtype == "success":
            result_text = message.result
    return result_text


async def run_interactive_session(app_config: AppConfig):
    """Run interactive multi-turn session using ClaudeSDKClient."""
    options = build_sdk_options(app_config)

    async with ClaudeSDKClient(options=options) as client:
        while True:
            user_input = input("\nYou: ").strip()
            if user_input in ("/quit", "/exit", "/q"):
                break

            await client.query(user_input)
            async for message in client.receive_response():
                if message.type == "assistant":
                    for block in message.content:
                        if hasattr(block, "text"):
                            print(block.text, end="", flush=True)
            print()
