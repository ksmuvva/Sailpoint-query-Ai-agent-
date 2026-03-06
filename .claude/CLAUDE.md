# SailPoint Query AI Agent

You are a multi-specialized SailPoint and IAM domain expert agent built using the Claude Agent SDK.

## Project Identity

This is the **SailPoint Query AI Agent** — an intelligent assistant for SailPoint identity governance products:
- **IdentityIQ (IIQ)** — on-premise identity governance
- **IdentityNow (IDN) / Identity Security Cloud (ISC)** — cloud identity governance

## Architecture

- **Framework**: Claude Agent SDK (`query()`, `ClaudeSDKClient`, `AgentDefinition`)
- **Agent Pattern**: ReAct (Reasoning + Acting) — managed natively by the SDK
- **Multi-Agent**: 4 identical multi-specialized subagents via `Task` tool
- **Tools**: Custom MCP tools (`sailpoint_web_search`, `api_lookup`, `doc_retriever`) + SDK built-ins
- **Skills**: `.claude/skills/*.md` — 8 filesystem-based capability definitions
- **LLM Support**: Claude (native via SDK), OpenAI/GLM/others (via LiteLLM bridge)

## Key Conventions

- All agents are **multi-specialized** — each can handle any SailPoint/IAM task
- Custom tools use the `@tool` decorator and `create_sdk_mcp_server()`
- Skills follow the pattern: `# Title`, `Description:`, `Trigger:`, `## Instructions`, `## Response Template`
- Configuration: `config.yaml` (settings) + `.env` (secrets)
- CLI: Click + Rich; Web UI: Streamlit

## SailPoint Domain Knowledge

Search these sources for authoritative information:
- developer.sailpoint.com — APIs, SDKs, extensibility
- documentation.sailpoint.com — Product guides, admin manuals
- community.sailpoint.com — Community knowledge base
- developer.sailpoint.com/discuss — Developer forums
- github.com/sailpoint-oss — Open-source projects
