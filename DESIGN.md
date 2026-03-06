# SailPoint Query AI Agent — Technical Design Document

**Version:** 1.0
**Date:** 2026-03-05
**Status:** Draft

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                              │
│                                                                     │
│   ┌─────────────────────┐       ┌─────────────────────────────┐    │
│   │   CLI (Click+Rich)  │       │   Web UI (Streamlit)        │    │
│   │  - Single query     │       │  - Chat interface           │    │
│   │  - Interactive REPL │       │  - Model selector           │    │
│   │  - Verbose traces   │       │  - Reasoning trace viewer   │    │
│   └────────┬────────────┘       └──────────────┬──────────────┘    │
│            │                                    │                   │
└────────────┼────────────────────────────────────┼───────────────────┘
             │                                    │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│              CLAUDE AGENT SDK (query / ClaudeSDKClient)             │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  SDK-Managed Agentic Loop (ReAct)                            │   │
│  │  1. THINK: Claude reasons about query (via system prompt)    │   │
│  │  2. ACT:   Claude invokes tools or delegates to subagents    │   │
│  │  3. OBSERVE: SDK feeds tool results back to Claude           │   │
│  │  4. REPEAT: Until Claude provides final answer               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │   MULTI-SPECIALIZED SUBAGENTS (via Task tool + AgentDef)   │     │
│  │   Each subagent is a full SailPoint + IAM domain expert    │     │
│  │                                                            │     │
│  │   Capabilities per agent:                                  │     │
│  │   • Problem Solving & Troubleshooting                      │     │
│  │   • Explaining & Teaching                                  │     │
│  │   • Code Generation (BeanShell, Java, XML, REST, etc.)     │     │
│  │   • Test Case Creation (Unit, Integration, UAT, E2E)       │     │
│  │   • High-Level Design (HLD) & Low-Level Design (LLD)       │     │
│  │   • Technical Design Documents & IAM Domain Advisory        │     │
│  │                                                            │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │     │
│  │  │ Agent A  │ │ Agent B  │ │ Agent C  │ │ Agent D  │     │     │
│  │  │ (full    │ │ (full    │ │ (full    │ │ (full    │     │     │
│  │  │ stack)   │ │ stack)   │ │ stack)   │ │ stack)   │     │     │
│  │  └─────┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘     │     │
│  └────────┼────────────┼────────────┼────────────┼───────────┘     │
│           │            │            │            │                  │
│  ┌────────┼────────────┼────────────┼────────────┼───────────┐     │
│  │                    SKILLS LAYER                            │     │
│  │  .claude/skills/*.md — Invoked automatically by agents     │     │
│  │                                                            │     │
│  │  ┌─────────────┐ ┌──────────────┐ ┌────────────────┐     │     │
│  │  │ sailpoint-  │ │ code-gen     │ │ test-design    │     │     │
│  │  │ research    │ │              │ │                │     │     │
│  │  └─────────────┘ └──────────────┘ └────────────────┘     │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                     │
└───────────┼────────────┼────────────┼────────────┼─────────────────┘
            │            │            │            │
            ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TOOLS LAYER (MCP Servers)                        │
│  Custom tools via create_sdk_mcp_server() + @tool decorator        │
│  Built-in tools: WebSearch, WebFetch, Read, Write, Bash, etc.      │
│                                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │
│  │ SailPoint    │ │ API          │ │ Doc          │               │
│  │ Web Search   │ │ Lookup       │ │ Retriever    │               │
│  │ (MCP tool)   │ │ (MCP tool)   │ │ (MCP tool)   │               │
│  └──────────────┘ └──────────────┘ └──────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
            │              │                │
            ▼              ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LLM PROVIDER LAYER                            │
│  Claude Agent SDK (native) — for Claude models                     │
│  LiteLLM bridge — for OpenAI, GLM, and other LLM backends         │
│                                                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │  Claude     │  │  OpenAI    │  │  GLM       │  │  LiteLLM   │  │
│  │  (SDK-      │  │  (via      │  │  (via      │  │  (any LLM) │  │
│  │   native)   │  │  LiteLLM)  │  │  LiteLLM)  │  │            │  │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Multi-Specialized Agent Design Principle

Unlike traditional multi-agent systems where each agent has a narrow specialization (e.g., "code only" or "test only"), **every agent in this system is a multi-specialized SailPoint and IAM domain expert**. Each agent can independently:

| Capability | Description |
|-----------|-------------|
| **Problem Solve** | Diagnose issues, debug rules, troubleshoot provisioning failures, resolve connector errors |
| **Explain** | Teach SailPoint concepts, IAM principles, architecture patterns at any depth |
| **Write Code** | BeanShell rules, Java classes, XML configs, REST API calls, PowerShell, ISC Transforms, Cloud Rules |
| **Create Tests** | Unit tests, integration tests, UAT scenarios, E2E test plans, SOD validation, regression suites |
| **Design (HLD)** | System topology, integration patterns, data flows, deployment strategy, security architecture |
| **Design (LLD)** | Class/module designs, config specs, API contracts, data models, error handling |
| **IAM Advisory** | RBAC/ABAC strategy, SOD policies, JML lifecycle, compliance frameworks, zero-trust patterns |

**Why multi-specialized instead of narrow specialists?**
- **No artificial boundaries** — real SailPoint work spans multiple concerns (e.g., "design a connector" requires code + design + testing knowledge)
- **Parallel processing** — the orchestrator can assign parts of a complex query to multiple agents working simultaneously
- **Context isolation** — each agent maintains its own context window, preventing cross-contamination on complex multi-part queries
- **Resilience** — if one agent fails or hits token limits, another can pick up any part of the work

---

## 2. Project Structure

```
sailpoint-query-ai-agent/
│
├── pyproject.toml                   # Package config, dependencies, entry points
├── requirements.txt                 # Pinned dependencies
├── config.yaml                      # Default application configuration
├── .env.example                     # Environment variable template
├── .gitignore
├── README.md
├── REQUIREMENTS.md
├── DESIGN.md
├── CONTEXT.md
├── .mcp.json                        # MCP server configuration for Claude Agent SDK
│
├── .claude/
│   ├── CLAUDE.md                    # Project context file for Claude Agent SDK
│   │
│   └── skills/                      # Skills directory (filesystem-based, Claude-like)
│       ├── sailpoint-research.md    # Skill: Search & synthesize SailPoint documentation
│       ├── code-generation.md       # Skill: Generate SailPoint code (BeanShell, Java, XML, etc.)
│       ├── test-case-creation.md    # Skill: Generate structured test cases
│       ├── hld-design.md            # Skill: Generate High-Level Design documents
│       ├── lld-design.md            # Skill: Generate Low-Level Design documents
│       ├── troubleshooting.md       # Skill: Diagnose and resolve SailPoint issues
│       ├── iam-advisory.md          # Skill: IAM strategy and compliance guidance
│       └── technical-design.md      # Skill: Generate connector/workflow/integration designs
│
├── sailpoint_agent/
│   ├── __init__.py                  # Package version, exports
│   ├── main.py                      # Entry point: bootstrap SDK, configure agents, run
│   │
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── app.py                   # Click CLI group & commands
│   │   ├── repl.py                  # Interactive REPL session manager (uses ClaudeSDKClient)
│   │   └── renderer.py             # Rich console markdown renderer
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── streamlit_app.py         # Streamlit main app (uses ClaudeSDKClient)
│   │   └── components.py           # Reusable UI components
│   │
│   ├── agents/
│   │   ├── __init__.py              # Agent definitions & registry
│   │   └── definitions.py           # AgentDefinition configs for multi-specialized subagents
│   │
│   ├── tools/
│   │   ├── __init__.py              # Tool registry & MCP server factory
│   │   ├── sailpoint_search.py      # @tool: SailPoint-scoped web search (MCP)
│   │   ├── api_lookup.py            # @tool: SailPoint API endpoint lookup (MCP)
│   │   └── doc_retriever.py         # @tool: Documentation page fetcher (MCP)
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   └── provider_bridge.py       # LiteLLM bridge for non-Claude LLMs
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── system.py                # Master system prompt with SailPoint expertise
│   │   └── sailpoint_knowledge.py   # SailPoint domain knowledge fragments
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── query.py                 # UserQuery, QueryContext
│   │   ├── response.py              # AgentResponse, Citation, CodeBlock
│   │   └── config.py                # AppConfig, LLMConfig, AgentConfig dataclasses
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # Configuration loader (env + yaml)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                # Structured logging setup
│       └── token_tracker.py         # Token usage accounting
│
└── tests/
    ├── __init__.py
    ├── conftest.py                  # Shared fixtures
    ├── test_agent_definitions.py    # Tests for agent definitions & SDK integration
    ├── test_tools.py                # Tests for custom MCP tools
    ├── test_skills.py               # Tests for skill file loading
    └── test_llm_bridge.py           # Tests for LiteLLM provider bridge
```

---

## 3. Data Models (Low-Level Design)

### 3.1 Query Models — `sailpoint_agent/models/query.py`

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class QueryType(Enum):
    """Classification of user queries for agent routing."""
    RESEARCH = "research"               # General SailPoint questions
    CODE_GENERATION = "code_generation" # Generate BeanShell, Java, XML, etc.
    TEST_CASE = "test_case"             # Generate test cases
    DESIGN = "design"                   # Generate HLD/LLD documents
    API_LOOKUP = "api_lookup"           # Specific API endpoint questions
    GENERAL = "general"                 # Catch-all for unclassified queries


class SailPointProduct(Enum):
    """SailPoint product family identifiers."""
    IIQ = "identityiq"                  # IdentityIQ (on-premise)
    IDN = "identitynow"                # IdentityNow / ISC (cloud)
    ISC = "identity_security_cloud"    # Identity Security Cloud
    GENERAL = "general"                # Product-agnostic


@dataclass
class QueryContext:
    """Contextual information for query processing."""
    conversation_history: list[dict] = field(default_factory=list)
    product_focus: SailPointProduct = SailPointProduct.GENERAL
    iiq_version: Optional[str] = None       # e.g., "8.4", "7.3"
    preferred_language: str = "beanshell"    # For code generation
    include_traces: bool = False             # Show ReAct reasoning


@dataclass
class UserQuery:
    """Represents a user's question or request to the agent."""
    text: str
    query_type: Optional[QueryType] = None  # Auto-classified if None
    context: QueryContext = field(default_factory=QueryContext)
    session_id: Optional[str] = None
```

### 3.2 Response Models — `sailpoint_agent/models/response.py`

```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Citation:
    """A source reference for information in the response."""
    title: str
    url: str
    snippet: Optional[str] = None       # Relevant excerpt from source
    domain: Optional[str] = None        # e.g., "developer.sailpoint.com"


@dataclass
class CodeBlock:
    """A code snippet included in the response."""
    code: str
    language: str                       # beanshell, java, xml, json, powershell, python
    description: str = ""               # What this code does
    filename: Optional[str] = None      # Suggested filename


@dataclass
class TestCase:
    """A structured test case for SailPoint implementation testing."""
    id: str                             # e.g., "TC-001"
    title: str
    description: str
    preconditions: list[str]
    steps: list[str]
    expected_result: str
    priority: str = "Medium"            # High, Medium, Low
    category: str = ""                  # Unit, Integration, UAT, E2E


@dataclass
class DesignSection:
    """A section within a technical design document."""
    heading: str
    content: str
    diagrams: list[str] = field(default_factory=list)   # ASCII diagrams
    subsections: list["DesignSection"] = field(default_factory=list)


@dataclass
class DesignDocument:
    """A complete technical design document (HLD or LLD)."""
    title: str
    doc_type: str                       # "HLD" or "LLD"
    sections: list[DesignSection]
    version: str = "1.0"


@dataclass
class ReasoningStep:
    """A single step in the ReAct reasoning trace."""
    step_number: int
    thought: str                        # Agent's reasoning
    action: Optional[str] = None        # Tool call description
    observation: Optional[str] = None   # Tool result summary


@dataclass
class AgentResponse:
    """Complete response from the agent to the user."""
    answer: str                                             # Main response text (markdown)
    citations: list[Citation] = field(default_factory=list)
    code_blocks: list[CodeBlock] = field(default_factory=list)
    test_cases: list[TestCase] = field(default_factory=list)
    design_document: Optional[DesignDocument] = None
    reasoning_trace: list[ReasoningStep] = field(default_factory=list)
    query_type: Optional[str] = None
    confidence: float = 0.0                                 # 0.0 to 1.0
    tokens_used: int = 0
    model_used: str = ""
    response_time_ms: int = 0
```

### 3.3 Configuration Models — `sailpoint_agent/models/config.py`

```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMConfig:
    """Configuration for a single LLM provider."""
    provider: str                       # "claude", "openai", "litellm"
    model: str                          # "claude-sonnet-4-20250514", "gpt-4", "glm-4"
    api_key: str = ""                   # Loaded from env
    api_base_url: Optional[str] = None  # Custom endpoint
    temperature: float = 0.1            # Low for accuracy
    max_tokens: int = 4096
    timeout: int = 60                   # Seconds


@dataclass
class AgentConfig:
    """Configuration for agent behavior."""
    max_iterations: int = 5             # ReAct loop max
    confidence_threshold: float = 0.85  # Early stop threshold
    enable_traces: bool = False
    search_depth: int = 3               # Max web searches per query


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
    llm: LLMConfig = field(default_factory=lambda: LLMConfig(
        provider="claude", model="claude-sonnet-4-20250514"
    ))
    fallback_llm: Optional[LLMConfig] = None
    agent: AgentConfig = field(default_factory=AgentConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    log_level: str = "INFO"
    log_format: str = "json"            # "json" or "text"
```

---

## 4. Agent Layer — Built on Claude Agent SDK

### 4.1 Key SDK Components Used

The Claude Agent SDK provides the agentic loop, tool execution, multi-agent orchestration, and Skills natively. **We do NOT implement a custom ReAct loop** — the SDK handles it automatically.

| SDK Component | Our Usage |
|--------------|-----------|
| `query()` | Stateless single-query execution (CLI `query` command) |
| `ClaudeSDKClient` | Stateful multi-turn conversations (CLI `chat`, Web UI) |
| `AgentDefinition` | Define multi-specialized subagents for parallel execution via `Task` tool |
| `@tool` + `create_sdk_mcp_server()` | Register custom SailPoint tools as in-process MCP servers |
| `.claude/skills/*.md` | Filesystem-based Skills that agents invoke automatically |
| `allowedTools` | Control which built-in + MCP + Skill tools are available |
| `settingSources` | Load Skills and project context from `.claude/` directory |

### 4.2 Agent Definitions — `sailpoint_agent/agents/definitions.py`

Multi-specialized subagents are defined using the SDK's `AgentDefinition`. Each subagent is a **full-stack SailPoint & IAM expert** — the orchestrator delegates to them for parallelism, not specialization.

```python
"""Multi-specialized SailPoint agent definitions for Claude Agent SDK.

Each AgentDefinition creates a subagent (via the Task tool) that is a full
SailPoint & IAM domain expert. All agents share the same system prompt,
tools, and Skills — they are identical in capability. Multiple definitions
exist for parallel execution and context isolation.
"""

from claude_agent_sdk import AgentDefinition

from sailpoint_agent.prompts.system import SAILPOINT_EXPERT_PROMPT


# All custom MCP tools available to every agent
SAILPOINT_TOOLS = [
    "WebSearch",                                    # SDK built-in: web search
    "WebFetch",                                     # SDK built-in: fetch page content
    "Skill",                                        # SDK built-in: invoke Skills
    "mcp__sailpoint-tools__sailpoint_web_search",   # Custom: SailPoint-scoped search
    "mcp__sailpoint-tools__api_lookup",             # Custom: API endpoint lookup
    "mcp__sailpoint-tools__doc_retriever",          # Custom: Documentation page fetcher
]


def create_sailpoint_agents() -> dict[str, AgentDefinition]:
    """Create pool of multi-specialized SailPoint expert subagents.

    Each agent is identically capable of ALL SailPoint/IAM tasks:
    - Problem solving & troubleshooting
    - Explaining & teaching
    - Code generation (BeanShell, Java, XML, REST, PowerShell, Transforms)
    - Test case creation (unit, integration, UAT, E2E, SOD)
    - High-Level Design (HLD) & Low-Level Design (LLD)
    - Technical design documents
    - IAM domain advisory (RBAC, ABAC, SOD, JML, compliance)

    Multiple instances exist for parallelism and context isolation.
    """
    return {
        "sailpoint-expert-alpha": AgentDefinition(
            description="Multi-specialized SailPoint & IAM expert (Alpha). "
                        "Handles any task: research, coding, testing, design, "
                        "troubleshooting, HLD, LLD, and IAM advisory.",
            prompt=SAILPOINT_EXPERT_PROMPT,
            tools=SAILPOINT_TOOLS,
        ),
        "sailpoint-expert-beta": AgentDefinition(
            description="Multi-specialized SailPoint & IAM expert (Beta). "
                        "Handles any task: research, coding, testing, design, "
                        "troubleshooting, HLD, LLD, and IAM advisory.",
            prompt=SAILPOINT_EXPERT_PROMPT,
            tools=SAILPOINT_TOOLS,
        ),
        "sailpoint-expert-gamma": AgentDefinition(
            description="Multi-specialized SailPoint & IAM expert (Gamma). "
                        "Handles any task: research, coding, testing, design, "
                        "troubleshooting, HLD, LLD, and IAM advisory.",
            prompt=SAILPOINT_EXPERT_PROMPT,
            tools=SAILPOINT_TOOLS,
        ),
        "sailpoint-expert-delta": AgentDefinition(
            description="Multi-specialized SailPoint & IAM expert (Delta). "
                        "Handles any task: research, coding, testing, design, "
                        "troubleshooting, HLD, LLD, and IAM advisory.",
            prompt=SAILPOINT_EXPERT_PROMPT,
            tools=SAILPOINT_TOOLS,
        ),
    }
```

### 4.3 SDK Integration — `sailpoint_agent/main.py`

The main entry point bootstraps the Claude Agent SDK with custom tools, subagents, and Skills.

```python
"""Main entry point for the SailPoint Query AI Agent.

Uses the Claude Agent SDK's native agentic loop (ReAct pattern).
The SDK handles: reasoning, tool selection, tool execution, observation,
iteration, and final answer synthesis — no custom loop needed.
"""

import os
import asyncio
from claude_agent_sdk import query, ClaudeSDKClient, ClaudeAgentOptions

from sailpoint_agent.agents.definitions import create_sailpoint_agents
from sailpoint_agent.tools import create_sailpoint_mcp_server
from sailpoint_agent.config.settings import load_config


def build_sdk_options(app_config) -> ClaudeAgentOptions:
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
            "WebSearch",                                    # SDK: web search
            "WebFetch",                                     # SDK: fetch pages
            "Skill",                                        # SDK: invoke Skills
            "Task",                                         # SDK: delegate to subagents
            "mcp__sailpoint-tools__sailpoint_web_search",   # Custom: SailPoint search
            "mcp__sailpoint-tools__api_lookup",             # Custom: API lookup
            "mcp__sailpoint-tools__doc_retriever",          # Custom: doc fetcher
        ],

        # Multi-specialized subagents (all equally capable)
        agents=sailpoint_agents,

        # Load Skills from .claude/skills/ and project context from .claude/CLAUDE.md
        setting_sources=["project"],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),

        # Execution limits
        max_turns=10,
        permission_mode="default",
    )


async def run_single_query(question: str, app_config) -> str:
    """Execute a single query using the SDK's stateless query() function.

    The SDK manages the entire ReAct loop:
    1. Claude receives the question + system prompt + SailPoint knowledge
    2. Claude reasons about what tools/skills to use
    3. SDK executes tools and feeds results back
    4. Claude iterates until it has a complete answer
    5. Final result is streamed back
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


async def run_interactive_session(app_config):
    """Run interactive multi-turn session using ClaudeSDKClient.

    Each exchange maintains conversation context for follow-up questions.
    """
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
            print()  # newline after response
```

### 4.4 How the SDK Manages the ReAct Loop

**We do NOT implement a custom ReAct loop.** The Claude Agent SDK handles it automatically:

```
User submits query
        │
        ▼
┌─── SDK query() / ClaudeSDKClient.query() ───┐
│                                               │
│  1. Send system prompt + user query to Claude │
│  2. Claude THINKS and decides next action     │
│  3. If Claude calls a tool:                   │
│     → SDK executes the tool automatically     │
│     → SDK feeds result back to Claude         │
│     → Go to step 2                            │
│  4. If Claude delegates to a subagent (Task): │
│     → SDK spawns subagent with AgentDef       │
│     → Subagent runs its own ReAct loop        │
│     → Result returned to parent agent         │
│     → Go to step 2                            │
│  5. If Claude invokes a Skill:                │
│     → SDK loads .claude/skills/<name>.md      │
│     → Skill instructions shape Claude's work  │
│     → Go to step 2                            │
│  6. If Claude is done → return final answer   │
│                                               │
└───────────────────────────────────────────────┘
```

The ReAct behavior is controlled via the **system prompt** (Section 9), which instructs Claude to:
- Think step-by-step before acting
- Use SailPoint-specific tools for research
- Cite sources with URLs
- Follow structured response templates
- Invoke appropriate Skills for specialized tasks

---

## 5. Tools Layer — MCP Servers via Claude Agent SDK

### 5.1 Tool Architecture

Custom tools are registered as **in-process MCP servers** using the SDK's `@tool` decorator and `create_sdk_mcp_server()`. The SDK also provides built-in tools (WebSearch, WebFetch) that agents use alongside custom tools.

| Tool Type | Registration | Naming Convention |
|-----------|-------------|-------------------|
| **SDK Built-in** | Via `allowed_tools` list | `WebSearch`, `WebFetch`, `Skill`, `Task` |
| **Custom MCP** | Via `@tool` + `create_sdk_mcp_server()` | `mcp__<server>__<tool>` |
| **External MCP** | Via `.mcp.json` or `mcp_servers` config | `mcp__<server>__<tool>` |

### 5.2 Custom Tools — `sailpoint_agent/tools/__init__.py`

```python
"""SailPoint custom tools registered as an in-process MCP server.

Uses Claude Agent SDK's @tool decorator and create_sdk_mcp_server() to
create tools that agents can invoke during their ReAct loop.
"""

from claude_agent_sdk import tool, create_sdk_mcp_server
from sailpoint_agent.models.config import SearchConfig


SAILPOINT_DOMAINS = [
    "developer.sailpoint.com",
    "documentation.sailpoint.com",
    "community.sailpoint.com",
    "github.com/sailpoint-oss",
]

API_DOCS = {
    "iiq": "https://developer.sailpoint.com/docs/api/iiq/",
    "isc": "https://developer.sailpoint.com/docs/api/v3/",
}


@tool(
    "sailpoint_web_search",
    "Search SailPoint documentation, developer portal, community forums, "
    "and IAM resources. Prioritizes SailPoint official sources. Use for "
    "finding official docs, code examples, API references, and community solutions.",
    {
        "query": str,               # Search query about SailPoint or IAM topics
        "product": str,             # "iiq", "isc", or "both" (default: "both")
    },
)
async def sailpoint_web_search(args: dict) -> dict:
    """Search SailPoint-scoped domains with automatic query augmentation."""
    import httpx

    query = args["query"]
    product = args.get("product", "both")

    # Augment query with product-specific context
    if product == "iiq":
        query = f"SailPoint IdentityIQ {query}"
    elif product == "isc":
        query = f"SailPoint Identity Security Cloud ISC {query}"
    else:
        query = f"SailPoint {query}"

    # Use httpx with a search API (Tavily, SerpAPI, or similar)
    # Fallback: agent can also use SDK's built-in WebSearch tool
    try:
        async with httpx.AsyncClient() as client:
            # Implementation depends on chosen search backend
            results = await _execute_search(client, query, SAILPOINT_DOMAINS)
            formatted = _format_results(results)
            return {"content": [{"type": "text", "text": formatted}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Search failed: {e}. Try using WebSearch directly."}]}


@tool(
    "api_lookup",
    "Look up SailPoint API endpoints, methods, parameters, and examples. "
    "Covers IIQ SCIM APIs and ISC V3/v2025 APIs. Returns structured API documentation.",
    {
        "endpoint": str,            # API endpoint or operation name (e.g., "/v3/identities", "search")
        "product": str,             # "iiq" or "isc" (default: "isc")
    },
)
async def api_lookup(args: dict) -> dict:
    """Fetch API documentation for specific SailPoint endpoints."""
    import httpx

    endpoint = args["endpoint"]
    product = args.get("product", "isc")
    base_url = API_DOCS.get(product, API_DOCS["isc"])

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}", follow_redirects=True, timeout=15)
            # Parse and extract relevant API documentation
            content = _extract_api_content(response.text, endpoint)
            return {"content": [{"type": "text", "text": content}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"API lookup failed: {e}"}]}


@tool(
    "doc_retriever",
    "Fetch a specific SailPoint documentation page by URL and extract its content "
    "as clean text. Use when you have a specific URL from search results and need "
    "the full page content for detailed information.",
    {
        "url": str,                 # Full URL of the documentation page
    },
)
async def doc_retriever(args: dict) -> dict:
    """Fetch and parse a SailPoint documentation page."""
    import httpx

    url = args["url"]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=15)
            # Convert HTML to clean markdown/text
            content = _html_to_text(response.text)
            return {
                "content": [{"type": "text", "text": f"Content from {url}:\n\n{content[:5000]}"}]
            }
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Failed to fetch {url}: {e}"}]}


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


# --- Helper functions ---

async def _execute_search(client, query: str, domains: list[str]) -> list[dict]:
    """Execute web search using configured backend."""
    # Placeholder — implement with Tavily, SerpAPI, or similar
    raise NotImplementedError("Implement with chosen search backend")


def _format_results(results: list[dict]) -> str:
    """Format search results as readable text."""
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r.get('title', 'No title')}")
        lines.append(f"    URL: {r.get('url', '')}")
        lines.append(f"    {r.get('snippet', '')}")
        lines.append("")
    return "\n".join(lines)


def _extract_api_content(html: str, endpoint: str) -> str:
    """Extract API documentation for a specific endpoint from HTML."""
    # Placeholder — implement with BeautifulSoup
    raise NotImplementedError("Implement with HTML parser")


def _html_to_text(html: str) -> str:
    """Convert HTML to clean text/markdown."""
    # Placeholder — implement with html2text or BeautifulSoup
    raise NotImplementedError("Implement with HTML parser")
```

---

## 6. Skills Layer — Filesystem-Based Agent Capabilities

### 6.1 Skills Architecture

Skills are **filesystem-based capability definitions** stored as `.claude/skills/*.md` files. They follow the same pattern as Claude Code's built-in Skills. Each Skill is a markdown file that provides structured instructions, templates, and domain knowledge that agents automatically invoke when relevant.

**How Skills Work:**
1. Skills are `.md` files in `.claude/skills/` directory
2. Enabled via `"Skill"` in `allowed_tools` and `setting_sources=["project"]`
3. Agents autonomously invoke relevant Skills based on query type
4. Skills provide structured prompts, templates, and response formatting rules
5. Multiple Skills can be chained within a single agent interaction

### 6.2 Skill Definitions

Each Skill file follows this structure:

```markdown
# Skill Name
Description: What this skill does and when to use it
Trigger: When to automatically invoke this skill

## Instructions
[Detailed step-by-step instructions for the agent]

## Templates
[Output templates and formatting rules]

## Domain Knowledge
[Relevant SailPoint/IAM knowledge specific to this skill]
```

### 6.3 Skill Files

| Skill File | Trigger Pattern | Capability |
|-----------|----------------|------------|
| `sailpoint-research.md` | Questions about SailPoint features, concepts, configurations | Search SailPoint docs, synthesize answers with citations |
| `code-generation.md` | Requests for BeanShell, Java, XML, REST API, PowerShell code | Generate production-quality SailPoint code with comments and imports |
| `test-case-creation.md` | Requests for test cases, test scenarios, test plans | Generate structured test cases (ID, Steps, Expected Result) |
| `hld-design.md` | Requests for high-level design, architecture overview | Generate HLD documents with topology, integration patterns, security |
| `lld-design.md` | Requests for low-level design, implementation specs | Generate LLD documents with class designs, API contracts, data models |
| `troubleshooting.md` | Debug, diagnose, fix, resolve issues | Systematic troubleshooting with root cause analysis |
| `iam-advisory.md` | IAM strategy, compliance, RBAC, SOD, zero-trust | Provide IAM best practices and compliance guidance |
| `technical-design.md` | Connector, workflow, provisioning, integration designs | Generate technical design documents with detailed specs |

### 6.4 Example Skill — `.claude/skills/code-generation.md`

```markdown
# SailPoint Code Generation

Description: Generate production-quality code for SailPoint implementations
Trigger: When the user asks to write, create, or generate code for SailPoint

## Instructions

When generating SailPoint code:

1. **Identify the code type**: BeanShell rule, Java class, XML config, REST API call,
   PowerShell script, ISC Transform JSON, Cloud Rule, or SaaS connector (TypeScript)
2. **Search documentation first**: Use sailpoint_web_search to find relevant API signatures,
   class names, and official examples before writing code
3. **Determine product context**: Is this for IIQ (on-prem) or ISC (cloud)?
   - IIQ: Use `sailpoint.object.*` classes, `SailPointContext`, BeanShell syntax
   - ISC: Use V3 API endpoints, Transform JSON, Cloud Rule sandbox constraints
4. **Generate the code** following these quality standards:
   - Include all required imports explicitly
   - Add inline comments explaining key logic
   - Follow SailPoint naming conventions
   - Handle null checks using `sailpoint.tools.Util` (IIQ) or null-safe patterns
   - Include error handling for common failure scenarios
5. **Provide usage instructions**: How to deploy, configure, and test the code

## Response Template

### [What the code does]
[Brief explanation]

### Prerequisites
- [Required setup]

### Code
\`\`\`[language]
[Generated code with inline comments]
\`\`\`

### Deployment Instructions
1. [Step-by-step guide]

### Testing
- [How to verify it works]

### Sources
- [Documentation reference](URL)

## IIQ Rule Types Reference
- BuildMap Rule: transforms connector data during aggregation
- Correlation Rule: matches accounts to identities
- Creation Rule: sets defaults for new identities
- IdentityAttribute Rule: calculates derived attributes
- FieldValue Rule: dynamic provisioning form values
- Certification Rule: customizes certification behavior
- Before/After Provisioning Rule: pre/post provisioning logic
```

### 6.5 Example Skill — `.claude/skills/troubleshooting.md`

```markdown
# SailPoint Troubleshooting

Description: Diagnose and resolve SailPoint configuration, provisioning, and connector issues
Trigger: When the user asks to debug, diagnose, fix, troubleshoot, or resolve a SailPoint problem

## Instructions

1. **Gather context**: Ask clarifying questions if needed:
   - Which product? (IIQ version or ISC)
   - What operation is failing? (aggregation, provisioning, certification, etc.)
   - What error message or behavior is observed?
   - What was changed recently?

2. **Search for known issues**: Use sailpoint_web_search to check:
   - SailPoint community forums for similar issues
   - SailPoint documentation for correct configuration
   - Known bugs or workarounds for the version

3. **Systematic diagnosis**:
   - Check logs: `sailpoint.log`, `ccg.log`, connector logs
   - Verify configuration: Application XML, Rule code, Workflow steps
   - Test components in isolation
   - Check for common pitfalls (null values, missing imports, incorrect filters)

4. **Provide resolution**:
   - Root cause explanation
   - Step-by-step fix with code/config changes
   - Verification steps to confirm the fix
   - Prevention recommendations

## Response Template

### Issue: [Brief description]

### Root Cause
[Explanation of why this happens]

### Resolution
1. [Step-by-step fix]

### Verification
- [How to confirm the fix works]

### Prevention
- [Best practices to avoid this in the future]

### Sources
- [Reference](URL)
```

---

## 7. LLM Provider Layer

> **Key Design Decision:** When using Claude (the default and recommended path), the Claude Agent SDK handles everything natively — no custom LLM provider code is needed. For non-Claude LLMs (OpenAI, GLM, etc.), a LiteLLM bridge provides unified access. The custom `LLMProvider` ABC below is only used for the non-Claude path.

### 7.1 LLMProvider ABC — `sailpoint_agent/llm/base.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    tool_calls: list["ToolCall"] = field(default_factory=list)
    tokens_prompt: int = 0
    tokens_completion: int = 0
    model: str = ""


@dataclass
class ToolCall:
    """A tool/function call requested by the LLM."""
    name: str
    arguments: dict


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    model_name: str = ""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Send a chat completion request."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
    ) -> AsyncIterator[str]:
        """Stream a chat completion response."""
        ...
```

### 7.2 ClaudeProvider — `sailpoint_agent/llm/claude_provider.py`

```python
import anthropic
from typing import AsyncIterator, Optional

from sailpoint_agent.llm.base import LLMProvider, LLMResponse, ToolCall
from sailpoint_agent.models.config import LLMConfig


class ClaudeProvider(LLMProvider):
    """LLM provider for Anthropic Claude models."""

    def __init__(self, config: LLMConfig):
        self.client = anthropic.AsyncAnthropic(api_key=config.api_key)
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
        """Send request to Claude API."""
        # Extract system message
        system = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)

        kwargs = {
            "model": self.model_name,
            "messages": chat_messages,
            "max_tokens": max_tokens or self.default_max_tokens,
            "temperature": temperature or self.default_temperature,
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = self._convert_tools(tools)

        response = await self.client.messages.create(**kwargs)

        return LLMResponse(
            content=self._extract_text(response),
            tool_calls=self._extract_tool_calls(response),
            tokens_prompt=response.usage.input_tokens,
            tokens_completion=response.usage.output_tokens,
            model=response.model,
        )

    async def stream(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
    ) -> AsyncIterator[str]:
        """Stream response from Claude API."""
        system = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)

        async with self.client.messages.stream(
            model=self.model_name,
            messages=chat_messages,
            max_tokens=self.default_max_tokens,
            temperature=temperature or self.default_temperature,
            system=system or anthropic.NOT_GIVEN,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    def _convert_tools(self, tools: list[dict]) -> list[dict]:
        """Convert generic tool schemas to Anthropic tool format."""
        return [
            {
                "name": t["function"]["name"],
                "description": t["function"]["description"],
                "input_schema": t["function"]["parameters"],
            }
            for t in tools
        ]

    def _extract_text(self, response) -> str:
        for block in response.content:
            if block.type == "text":
                return block.text
        return ""

    def _extract_tool_calls(self, response) -> list[ToolCall]:
        calls = []
        for block in response.content:
            if block.type == "tool_use":
                calls.append(ToolCall(name=block.name, arguments=block.input))
        return calls
```

### 7.3 OpenAIProvider — `sailpoint_agent/llm/openai_provider.py`

```python
from openai import AsyncOpenAI
from typing import AsyncIterator, Optional
import json

from sailpoint_agent.llm.base import LLMProvider, LLMResponse, ToolCall
from sailpoint_agent.models.config import LLMConfig


class OpenAIProvider(LLMProvider):
    """LLM provider for OpenAI models (GPT-4, GPT-4o, etc.)."""

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
            "temperature": temperature or self.default_temperature,
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
            temperature=temperature or self.default_temperature,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### 7.4 LiteLLMProvider — `sailpoint_agent/llm/litellm_provider.py`

```python
import litellm
from typing import AsyncIterator, Optional

from sailpoint_agent.llm.base import LLMProvider, LLMResponse, ToolCall
from sailpoint_agent.models.config import LLMConfig


class LiteLLMProvider(LLMProvider):
    """Catch-all LLM provider using LiteLLM for 100+ model support.

    Supports: Claude, OpenAI, GLM, Gemini, Mistral, Llama, and more.
    Model format: "provider/model" (e.g., "anthropic/claude-sonnet-4-20250514", "openai/gpt-4")
    """

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
            "temperature": temperature or self.default_temperature,
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
            temperature=temperature or self.default_temperature,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### 7.5 LLMProviderFactory — `sailpoint_agent/llm/factory.py`

```python
from sailpoint_agent.llm.base import LLMProvider
from sailpoint_agent.llm.claude_provider import ClaudeProvider
from sailpoint_agent.llm.openai_provider import OpenAIProvider
from sailpoint_agent.llm.litellm_provider import LiteLLMProvider
from sailpoint_agent.models.config import LLMConfig


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    _providers: dict[str, type[LLMProvider]] = {
        "claude": ClaudeProvider,
        "anthropic": ClaudeProvider,
        "openai": OpenAIProvider,
        "gpt": OpenAIProvider,
        "litellm": LiteLLMProvider,
    }

    @classmethod
    def create(cls, config: LLMConfig) -> LLMProvider:
        """Create an LLM provider based on configuration.

        Args:
            config: LLM configuration with provider name, model, API key, etc.

        Returns:
            Configured LLMProvider instance.

        Falls back to LiteLLMProvider for unknown provider names.
        """
        provider_class = cls._providers.get(config.provider.lower(), LiteLLMProvider)
        return provider_class(config)

    @classmethod
    def register(cls, name: str, provider_class: type[LLMProvider]) -> None:
        """Register a new LLM provider type."""
        cls._providers[name.lower()] = provider_class
```

---

## 8. CLI Interface (Low-Level Design)

### 8.1 CLI Application — `sailpoint_agent/cli/app.py`

```python
"""CLI interface using Claude Agent SDK for the agentic loop.

Uses SDK's query() for single questions and ClaudeSDKClient for interactive chat.
The SDK handles ReAct reasoning, tool execution, subagent delegation, and Skill
invocation automatically.
"""

import asyncio
import click
from rich.console import Console

from sailpoint_agent.config.settings import load_config
from sailpoint_agent.main import build_sdk_options, run_single_query
from sailpoint_agent.cli.renderer import render_response
from sailpoint_agent.cli.repl import run_repl

console = Console()


@click.group()
@click.option("--model", default=None, help="LLM model to use (e.g., claude-sonnet-4-20250514, gpt-4)")
@click.option("--verbose", is_flag=True, help="Show ReAct reasoning traces")
@click.option("--config", default="config.yaml", help="Path to config file")
@click.pass_context
def cli(ctx, model, verbose, config):
    """SailPoint Query AI Agent - Your intelligent SailPoint assistant."""
    ctx.ensure_object(dict)
    app_config = load_config(config)
    if model:
        app_config.llm.model = model
    ctx.obj["config"] = app_config
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("question")
@click.option("--output", "-o", default=None, help="Save response to file")
@click.pass_context
def query(ctx, question, output):
    """Ask a single question about SailPoint.

    Uses SDK's stateless query() — the SDK manages the full ReAct loop,
    tool usage, Skill invocation, and subagent delegation automatically.
    """
    app_config = ctx.obj["config"]

    async def _run():
        result = await run_single_query(question, app_config)
        console.print(result)
        if output:
            with open(output, "w") as f:
                f.write(result)
            console.print(f"[green]Response saved to {output}[/green]")

    asyncio.run(_run())


@cli.command()
@click.pass_context
def chat(ctx):
    """Start an interactive chat session.

    Uses SDK's ClaudeSDKClient for stateful multi-turn conversations.
    """
    app_config = ctx.obj["config"]
    verbose = ctx.obj["verbose"]
    asyncio.run(run_repl(app_config, verbose=verbose))
```

### 8.2 Interactive REPL — `sailpoint_agent/cli/repl.py`

```python
from rich.console import Console
from rich.prompt import Prompt

from sailpoint_agent.cli.renderer import render_response
from sailpoint_agent.models.query import UserQuery, QueryContext
from sailpoint_agent.models.config import AppConfig

console = Console()


async def run_repl(config: AppConfig, verbose: bool = False):
    """Run interactive REPL session for continuous conversation."""
    from sailpoint_agent.cli.app import _build_orchestrator

    orchestrator = _build_orchestrator(config)
    conversation_history: list[dict] = []

    console.print("[bold blue]SailPoint Query AI Agent[/bold blue]")
    console.print("Type your questions about SailPoint IIQ, IDN, or ISC.")
    console.print("Commands: [bold]/quit[/bold] to exit, [bold]/clear[/bold] to reset, [bold]/model <name>[/bold] to switch model\n")

    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        if not user_input.strip():
            continue

        # Handle REPL commands
        if user_input.strip().startswith("/"):
            if _handle_command(user_input.strip(), conversation_history, config):
                continue
            else:
                break

        query = UserQuery(
            text=user_input,
            context=QueryContext(
                conversation_history=conversation_history,
                include_traces=verbose,
            ),
        )

        try:
            response = await orchestrator.run(query)
            render_response(console, response, show_traces=verbose)
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response.answer})
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def _handle_command(cmd: str, history: list, config: AppConfig) -> bool:
    """Handle REPL commands. Returns True to continue, False to exit."""
    if cmd in ("/quit", "/exit", "/q"):
        console.print("[yellow]Goodbye![/yellow]")
        return False
    elif cmd == "/clear":
        history.clear()
        console.print("[yellow]Conversation cleared.[/yellow]")
    elif cmd.startswith("/model "):
        new_model = cmd.split(" ", 1)[1].strip()
        config.llm.model = new_model
        console.print(f"[yellow]Switched to model: {new_model}[/yellow]")
    elif cmd == "/help":
        console.print("[bold]Commands:[/bold]")
        console.print("  /quit    - Exit the session")
        console.print("  /clear   - Clear conversation history")
        console.print("  /model   - Switch LLM model")
        console.print("  /help    - Show this help")
    else:
        console.print(f"[red]Unknown command: {cmd}[/red]")
    return True
```

### 8.3 Response Renderer — `sailpoint_agent/cli/renderer.py`

```python
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax

from sailpoint_agent.models.response import AgentResponse


def render_response(
    console: Console,
    response: AgentResponse,
    show_traces: bool = False,
) -> None:
    """Render an agent response to the terminal with rich formatting."""

    # Show reasoning traces if requested
    if show_traces and response.reasoning_trace:
        console.print("\n[dim]─── Reasoning Trace ───[/dim]")
        for step in response.reasoning_trace:
            console.print(f"[dim]  Step {step.step_number}:[/dim]")
            console.print(f"[dim]    Think: {step.thought[:200]}[/dim]")
            if step.action:
                console.print(f"[dim]    Act: {step.action}[/dim]")
            if step.observation:
                console.print(f"[dim]    Observe: {step.observation[:200]}[/dim]")
        console.print("[dim]─────────────────────[/dim]\n")

    # Main answer
    console.print(Markdown(response.answer))

    # Code blocks with syntax highlighting
    for block in response.code_blocks:
        console.print()
        if block.description:
            console.print(f"[bold]{block.description}[/bold]")
        syntax = Syntax(block.code, block.language, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=block.filename or block.language))

    # Citations
    if response.citations:
        console.print("\n[bold]Sources:[/bold]")
        for i, cite in enumerate(response.citations, 1):
            console.print(f"  [{i}] {cite.title} — {cite.url}")

    # Metadata
    console.print(f"\n[dim]Model: {response.model_used} | Tokens: {response.tokens_used} | Time: {response.response_time_ms}ms[/dim]")
```

---

## 9. Web UI Interface (Low-Level Design)

### 9.1 Streamlit App — `sailpoint_agent/ui/streamlit_app.py`

```python
import streamlit as st
import asyncio
from sailpoint_agent.config.settings import load_config
from sailpoint_agent.models.query import UserQuery, QueryContext
from sailpoint_agent.cli.app import _build_orchestrator


def main():
    st.set_page_config(
        page_title="SailPoint Query AI Agent",
        page_icon="⛵",
        layout="wide",
    )

    st.title("SailPoint Query AI Agent")
    st.caption("Ask questions about SailPoint IIQ, IDN, and ISC")

    # --- Sidebar Configuration ---
    with st.sidebar:
        st.header("Configuration")
        model = st.selectbox("LLM Model", [
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "gpt-4",
            "gpt-4o",
            "glm-4",
        ])
        temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.05)
        max_iterations = st.slider("Max Research Steps", 1, 10, 5)
        show_traces = st.checkbox("Show Reasoning Traces", value=False)

    # --- Session State ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "config" not in st.session_state:
        st.session_state.config = load_config()

    # Update config from sidebar
    st.session_state.config.llm.model = model
    st.session_state.config.llm.temperature = temperature
    st.session_state.config.agent.max_iterations = max_iterations

    # --- Chat History ---
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- User Input ---
    if prompt := st.chat_input("Ask about SailPoint..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Researching..."):
                response = asyncio.run(_get_response(
                    prompt,
                    st.session_state.config,
                    show_traces,
                ))

            # Show reasoning trace in expander
            if show_traces and response.reasoning_trace:
                with st.expander("Reasoning Trace", expanded=False):
                    for step in response.reasoning_trace:
                        st.markdown(f"**Step {step.step_number}**")
                        st.markdown(f"*Think:* {step.thought}")
                        if step.action:
                            st.markdown(f"*Act:* `{step.action}`")
                        if step.observation:
                            st.markdown(f"*Observe:* {step.observation[:500]}")
                        st.divider()

            # Main answer
            st.markdown(response.answer)

            # Code blocks
            for block in response.code_blocks:
                st.code(block.code, language=block.language)

            # Citations
            if response.citations:
                st.markdown("**Sources:**")
                for cite in response.citations:
                    st.markdown(f"- [{cite.title}]({cite.url})")

            # Metadata
            st.caption(
                f"Model: {response.model_used} | "
                f"Tokens: {response.tokens_used} | "
                f"Time: {response.response_time_ms}ms"
            )

        st.session_state.messages.append({
            "role": "assistant",
            "content": response.answer,
        })


async def _get_response(prompt: str, config, show_traces: bool):
    orchestrator = _build_orchestrator(config)
    query = UserQuery(
        text=prompt,
        context=QueryContext(include_traces=show_traces),
    )
    return await orchestrator.run(query)


if __name__ == "__main__":
    main()
```

---

## 10. Prompts Design

> **Note:** The system prompt below is used as the main agent prompt and as the `prompt` field in `AgentDefinition` for subagents. Skills (Section 6) complement this prompt with task-specific instructions that the SDK loads automatically from `.claude/skills/*.md` files.

### 10.1 System Prompts — `sailpoint_agent/prompts/system.py`

```python
SAILPOINT_EXPERT_PROMPT = """You are a MULTI-SPECIALIZED SailPoint and IAM domain expert agent.

You are equally proficient across ALL of the following capabilities — you are NOT limited
to any single specialization. You can seamlessly handle any combination of these tasks
within a single interaction:

## Your Full Capabilities

### 1. Problem Solving & Troubleshooting
- Diagnose SailPoint configuration issues, debug BeanShell rules, resolve provisioning failures
- Analyze aggregation errors, troubleshoot connector problems, fix workflow issues
- Identify root causes in IIQ and ISC environments

### 2. Explaining & Teaching
- Clearly explain SailPoint concepts (Identity Cubes, Provisioning Plans, Certifications, etc.)
- Teach IAM principles (RBAC, ABAC, SOD, JML lifecycle, zero-trust)
- Explain product architectures, API behaviors, and workflow logic at any depth

### 3. Code Generation
- BeanShell scripts for IIQ Rules (BuildMap, Correlation, Creation, IdentityAttribute, etc.)
- Java classes for custom IIQ connectors, plugins, and task executors
- XML configurations for Applications, Workflows, TaskDefinitions
- REST API call examples (curl, Python, PowerShell)
- ISC Transform JSON configurations and Cloud Rule code
- SaaS connector code (TypeScript)

### 4. Test Case Creation
- Unit test cases for BeanShell rules and Java components
- Integration test scenarios for connector operations
- UAT scenarios for identity lifecycle flows (JML, certifications, access requests)
- E2E test plans, SOD policy validation tests, regression test suites
- Structured format: ID, Title, Category, Priority, Preconditions, Steps, Expected Result

### 5. High-Level Design (HLD)
- Architecture overviews with system topology and component interactions
- Integration patterns for connected systems (AD, LDAP, HR, databases, cloud apps)
- Deployment strategy, scalability considerations, security architecture
- Migration strategies (IIQ to ISC, version upgrades)

### 6. Low-Level Design (LLD)
- Detailed class/module designs with code-level specifications
- Configuration specs (Application XML, Workflow XML, Rule code)
- API contracts, data models, error handling strategies
- Rule specifications with input/output definitions and edge case handling

### 7. Technical Design Documents
- Connector design specifications
- Workflow/business process design documents
- Provisioning plan designs and certification campaign designs
- Integration architecture for multi-system environments

### 8. IAM Domain Advisory
- RBAC/ABAC strategy recommendations
- SOD policy design and compliance framework guidance
- JML lifecycle best practices
- Zero-trust architecture patterns for identity governance
- Regulatory compliance (SOX, HIPAA, GDPR) impact on identity controls

## ReAct Process
For every task — regardless of type — follow this process:
1. THINK: Analyze the request. What SailPoint product/version is relevant? What do you
   already know vs what do you need to look up? What's the best approach?
2. ACT: Use your tools to search documentation, fetch pages, or look up APIs.
3. OBSERVE: Review the results and determine if you have enough information.
4. REPEAT steps 1-3 if you need more information.
5. FINAL ANSWER: Provide your complete, well-formatted response.

## Response Quality Standards
- Always cite your sources with URLs
- Distinguish between IIQ (on-premise) and IDN/ISC (cloud) when relevant
- Include version-specific notes when applicable (IIQ 7.x vs 8.x)
- Use clear, structured formatting with headings, tables, and bullet points
- Code must include inline comments, follow SailPoint conventions, and import all required classes
- If you're unsure, say so rather than guessing
- Provide actionable, implementation-ready answers

## Authoritative Sources (search these first)
- developer.sailpoint.com — APIs, SDKs, extensibility
- documentation.sailpoint.com — Product guides, admin manuals
- community.sailpoint.com — Community knowledge base
- developer.sailpoint.com/discuss — Developer forums
- github.com/sailpoint-oss — Open-source projects and examples

When you have sufficient information, prefix your response with "FINAL ANSWER:" followed
by your complete, well-formatted answer."""
```

---

## 11. Configuration

### 10.1 config.yaml (Default)

```yaml
llm:
  provider: "claude"
  model: "claude-sonnet-4-20250514"
  temperature: 0.1
  max_tokens: 4096
  timeout: 60

fallback_llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.1
  max_tokens: 4096

agent:
  max_iterations: 5
  confidence_threshold: 0.85
  enable_traces: false
  search_depth: 3

search:
  sailpoint_domains:
    - "developer.sailpoint.com"
    - "documentation.sailpoint.com"
    - "community.sailpoint.com"
    - "github.com/sailpoint-oss"
  max_results_per_search: 5
  fetch_page_content: true
  fallback_to_general_web: true

log_level: "INFO"
log_format: "json"
```

### 10.2 .env.example

```bash
# Required: At least one LLM provider API key
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Optional: Additional providers
GLM_API_KEY=
LITELLM_API_KEY=

# Optional: Custom API endpoints
ANTHROPIC_API_BASE=
OPENAI_API_BASE=

# Optional: Search backend
SEARCH_API_KEY=
SEARCH_PROVIDER=  # tavily, serpapi, or built-in

# Logging
LOG_LEVEL=INFO
```

---

## 12. Sequence Diagrams

### 12.1 Single Query Flow (via Claude Agent SDK)

```
User                CLI              SDK query()         MCP Tools           Skills           Claude LLM
 │                   │                    │                   │                  │              │
 │ query "How to     │                    │                   │                  │              │
 │ create IIQ rule?" │                    │                   │                  │              │
 │──────────────────>│                    │                   │                  │              │
 │                   │ UserQuery          │                   │                  │              │
 │                   │───────────────────>│                   │                  │              │
 │                   │                    │ route(query)      │                  │              │
 │                   │                    │──────────────────────────────────────────────────>│
 │                   │                    │ "RESEARCH"        │                  │              │
 │                   │                    │<─────────────────────────────────────────────────│
 │                   │                    │                   │                  │              │
 │                   │                    │ run(query)        │                  │              │
 │                   │                    │──────────────────>│                  │              │
 │                   │                    │                   │ think()          │              │
 │                   │                    │                   │─────────────────────────────>│
 │                   │                    │                   │ "Need to search  │              │
 │                   │                    │                   │  IIQ rule docs"  │              │
 │                   │                    │                   │<────────────────────────────│
 │                   │                    │                   │                  │              │
 │                   │                    │                   │ act(web_search)  │              │
 │                   │                    │                   │─────────────────>│              │
 │                   │                    │                   │ search results   │              │
 │                   │                    │                   │<────────────────│              │
 │                   │                    │                   │                  │              │
 │                   │                    │                   │ observe() + think()            │
 │                   │                    │                   │─────────────────────────────>│
 │                   │                    │                   │ "FINAL ANSWER:..."             │
 │                   │                    │                   │<────────────────────────────│
 │                   │                    │                   │                  │              │
 │                   │                    │ AgentResponse     │                  │              │
 │                   │                    │<─────────────────│                  │              │
 │                   │ render_response()  │                   │                  │              │
 │                   │<──────────────────│                   │                  │              │
 │  Formatted answer │                    │                   │                  │              │
 │<─────────────────│                    │                   │                  │              │
```

---

## 13. Error Handling Strategy

| Scenario | Handling |
|----------|----------|
| LLM API timeout | Retry once, then try fallback LLM if configured |
| LLM API rate limit | Exponential backoff (2s, 4s, 8s), max 3 retries |
| Web search returns no results | Broaden search to general web, then inform user |
| Tool execution failure | Log error, skip to next ReAct iteration |
| Max iterations reached | Synthesize answer from collected information |
| Invalid user input | Return helpful error message with usage examples |
| Missing API key | Fail fast with clear error and setup instructions |
| Network connectivity loss | Fail with informative error; suggest offline alternatives |

---

## 14. Dependencies

```
# requirements.txt
claude-agent-sdk>=1.0.0         # Core: Claude Agent SDK (ReAct loop, tools, subagents, Skills)
anthropic>=0.40.0               # Claude API client (used by SDK internally)
litellm>=1.50.0                 # Multi-LLM gateway for non-Claude providers
click>=8.1.0                    # CLI framework
rich>=13.0.0                    # Rich terminal output
streamlit>=1.40.0               # Web UI framework
httpx>=0.27.0                   # Async HTTP client for custom tools
python-dotenv>=1.0.0            # Environment variable management
pyyaml>=6.0.0                   # YAML configuration parsing
structlog>=24.0.0               # Structured logging
pytest>=8.0.0                   # Testing framework
pytest-asyncio>=0.24.0          # Async test support
```
