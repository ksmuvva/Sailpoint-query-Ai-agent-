"""SailPoint custom tools registered as an in-process MCP server.

Uses Claude Agent SDK's @tool decorator and create_sdk_mcp_server() to
create tools that agents can invoke during their ReAct loop.
"""

from claude_agent_sdk import tool, create_sdk_mcp_server

from sailpoint_agent.tools.sailpoint_search import sailpoint_web_search
from sailpoint_agent.tools.api_lookup import api_lookup
from sailpoint_agent.tools.doc_retriever import doc_retriever
from sailpoint_agent.models.config import SearchConfig


def create_sailpoint_mcp_server(search_config: SearchConfig = SearchConfig()):
    """Create the in-process MCP server with all SailPoint custom tools.

    This server is passed to ClaudeAgentOptions.mcp_servers and makes
    tools available as mcp__sailpoint-tools__<tool_name>.
    """
    return create_sdk_mcp_server(
        name="sailpoint-tools",
        version="1.0.0",
        tools=[sailpoint_web_search, api_lookup, doc_retriever],
    )


__all__ = ["create_sailpoint_mcp_server", "sailpoint_web_search", "api_lookup", "doc_retriever"]
