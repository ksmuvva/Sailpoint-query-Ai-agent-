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
│                     ORCHESTRATOR AGENT                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Meta-ReAct Loop                                             │   │
│  │  1. THINK: Analyze query complexity & parallelism needs      │   │
│  │  2. ACT:   Delegate to multi-specialized agent(s)            │   │
│  │  3. OBSERVE: Collect agent responses                         │   │
│  │  4. SYNTHESIZE: Aggregate into final response                │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │          MULTI-SPECIALIZED AGENT POOL                      │     │
│  │   Each agent is a full SailPoint + IAM domain expert       │     │
│  │                                                            │     │
│  │   Capabilities per agent:                                  │     │
│  │   • Problem Solving & Troubleshooting                      │     │
│  │   • Explaining & Teaching                                  │     │
│  │   • Code Generation (BeanShell, Java, XML, REST, etc.)     │     │
│  │   • Test Case Creation (Unit, Integration, UAT, E2E)       │     │
│  │   • High-Level Design (HLD)                                │     │
│  │   • Low-Level Design (LLD)                                 │     │
│  │   • Technical Design Documents                             │     │
│  │   • IAM Domain Advisory                                    │     │
│  │                                                            │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │     │
│  │  │ Agent A  │ │ Agent B  │ │ Agent C  │ │ Agent D  │     │     │
│  │  │ (full    │ │ (full    │ │ (full    │ │ (full    │     │     │
│  │  │ stack)   │ │ stack)   │ │ stack)   │ │ stack)   │     │     │
│  │  └─────┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘     │     │
│  └────────┼────────────┼────────────┼────────────┼───────────┘     │
│           │            │            │            │                  │
└───────────┼────────────┼────────────┼────────────┼─────────────────┘
            │            │            │            │
            ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       SHARED TOOLS LAYER                            │
│  (All agents have equal access to all tools)                        │
│                                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │
│  │ SailPoint    │ │ API          │ │ Doc          │               │
│  │ Web Search   │ │ Lookup       │ │ Retriever    │               │
│  └──────────────┘ └──────────────┘ └──────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
            │              │                │
            ▼              ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LLM PROVIDER LAYER                            │
│                                                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │
│  │  Claude     │  │  OpenAI    │  │  GLM       │  │  LiteLLM   │  │
│  │  Provider   │  │  Provider  │  │  Provider  │  │  (any LLM) │  │
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
│
├── sailpoint_agent/
│   ├── __init__.py                  # Package version, exports
│   ├── main.py                      # Entry point: parse args, bootstrap, run
│   │
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── app.py                   # Click CLI group & commands
│   │   ├── repl.py                  # Interactive REPL session manager
│   │   └── renderer.py             # Rich console markdown renderer
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── streamlit_app.py         # Streamlit main app
│   │   └── components.py           # Reusable UI components
│   │
│   ├── agents/
│   │   ├── __init__.py              # Agent registry & exports
│   │   ├── base.py                  # BaseAgent ABC with ReAct loop (multi-specialized)
│   │   ├── orchestrator.py          # OrchestratorAgent (routes & coordinates)
│   │   └── sailpoint_agent.py       # SailPointExpertAgent (multi-specialized: problem solving, explaining, coding, design, testing, HLD, LLD, IAM advisory)
│   │
│   ├── tools/
│   │   ├── __init__.py              # Tool registry
│   │   ├── base.py                  # BaseTool ABC
│   │   ├── web_search.py            # SailPointWebSearch tool
│   │   ├── api_lookup.py            # SailPointAPILookup tool
│   │   └── doc_retriever.py         # DocumentationRetriever tool
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py                  # LLMProvider ABC
│   │   ├── factory.py               # LLMProviderFactory
│   │   ├── claude_provider.py       # ClaudeProvider
│   │   ├── openai_provider.py       # OpenAIProvider
│   │   └── litellm_provider.py      # LiteLLMProvider (catch-all)
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── system.py                # System prompts per agent type
│   │   ├── react.py                 # ReAct format instructions
│   │   └── sailpoint.py             # SailPoint domain knowledge prompt fragments
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── query.py                 # UserQuery, QueryType, QueryContext
│   │   ├── response.py              # AgentResponse, Citation, CodeBlock, ReasoningStep
│   │   └── config.py                # AppConfig, LLMConfig, AgentConfig dataclasses
│   │
│   ├── formatters/
│   │   ├── __init__.py
│   │   ├── response.py              # ResponseFormatter
│   │   └── code.py                  # CodeFormatter
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
    ├── test_orchestrator.py
    ├── test_sailpoint_expert_agent.py  # Tests for the multi-specialized SailPointExpertAgent
    ├── test_tools.py
    ├── test_llm_providers.py
    └── test_formatters.py
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

## 4. Agent Layer (Low-Level Design)

### 4.1 BaseAgent — `sailpoint_agent/agents/base.py`

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
import time

from sailpoint_agent.llm.base import LLMProvider
from sailpoint_agent.tools.base import BaseTool, ToolResult
from sailpoint_agent.models.query import UserQuery
from sailpoint_agent.models.response import AgentResponse, ReasoningStep
from sailpoint_agent.models.config import AgentConfig
from sailpoint_agent.utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents. Implements the ReAct loop.

    Each agent built from this base is a MULTI-SPECIALIZED SailPoint & IAM expert
    capable of: problem solving, explaining, coding, test creation, HLD, LLD,
    technical design, and IAM domain advisory. The orchestrator distributes work
    across agents for parallelism and context isolation, not for specialization.
    """

    def __init__(
        self,
        name: str,
        llm: LLMProvider,
        tools: list[BaseTool],
        system_prompt: str,
        config: AgentConfig = AgentConfig(),
    ):
        self.name = name
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.system_prompt = system_prompt
        self.config = config
        self.reasoning_trace: list[ReasoningStep] = []

    async def run(self, query: UserQuery) -> AgentResponse:
        """Execute the ReAct loop: Think → Act → Observe → Repeat/Answer."""
        messages = self._build_initial_messages(query)
        start_time = time.monotonic()
        total_tokens = 0

        for iteration in range(1, self.config.max_iterations + 1):
            # THINK: Generate reasoning about current state
            thought = await self.think(messages)
            logger.info(f"[{self.name}] Step {iteration} - Think: {thought[:100]}...")

            # Check if agent wants to give final answer
            if self._is_final_answer(thought):
                return self._build_response(
                    answer=self._extract_answer(thought),
                    start_time=start_time,
                    total_tokens=total_tokens,
                )

            # ACT: Select and execute a tool
            tool_name, tool_args = await self.select_tool(thought)
            action_desc = f"{tool_name}({tool_args})"
            logger.info(f"[{self.name}] Step {iteration} - Act: {action_desc}")

            result = await self.act(tool_name, tool_args)
            total_tokens += result.tokens_used

            # OBSERVE: Process tool output
            observation = await self.observe(result)
            logger.info(f"[{self.name}] Step {iteration} - Observe: {observation[:100]}...")

            # Record reasoning trace
            self.reasoning_trace.append(ReasoningStep(
                step_number=iteration,
                thought=thought,
                action=action_desc,
                observation=observation,
            ))

            # Update message history for next iteration
            messages.extend([
                {"role": "assistant", "content": f"Thought: {thought}\nAction: {action_desc}"},
                {"role": "user", "content": f"Observation: {observation}"},
            ])

        # Max iterations reached — synthesize best answer from collected info
        return await self._synthesize_final(messages, start_time, total_tokens)

    async def think(self, messages: list[dict]) -> str:
        """Generate a reasoning step given current context."""
        think_messages = messages + [
            {"role": "user", "content": "Think step-by-step about what you know and what you still need to find out. If you have enough information, provide your FINAL ANSWER."}
        ]
        response = await self.llm.chat(think_messages)
        return response.content

    @abstractmethod
    async def select_tool(self, thought: str) -> tuple[str, dict]:
        """Given a thought, select the appropriate tool and arguments.
        Returns (tool_name, tool_arguments_dict)."""
        ...

    async def act(self, tool_name: str, tool_args: dict) -> ToolResult:
        """Execute the selected tool."""
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                output=f"Tool '{tool_name}' not found. Available: {list(self.tools.keys())}",
            )
        tool = self.tools[tool_name]
        return await tool.execute(**tool_args)

    async def observe(self, result: ToolResult) -> str:
        """Process tool output into a text observation."""
        if result.success:
            return result.output[:2000]  # Truncate long outputs
        return f"Tool execution failed: {result.error}"

    def _build_initial_messages(self, query: UserQuery) -> list[dict]:
        """Build the initial message list with system prompt and user query."""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query.text},
        ]

    def _is_final_answer(self, thought: str) -> bool:
        """Check if the thought contains a final answer marker."""
        return "FINAL ANSWER:" in thought.upper()

    def _extract_answer(self, thought: str) -> str:
        """Extract the final answer from a thought string."""
        marker = "FINAL ANSWER:"
        idx = thought.upper().find(marker)
        if idx >= 0:
            return thought[idx + len(marker):].strip()
        return thought

    def _build_response(
        self, answer: str, start_time: float, total_tokens: int
    ) -> AgentResponse:
        """Construct an AgentResponse from the final answer."""
        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        return AgentResponse(
            answer=answer,
            reasoning_trace=self.reasoning_trace,
            tokens_used=total_tokens,
            model_used=self.llm.model_name,
            response_time_ms=elapsed_ms,
        )

    async def _synthesize_final(
        self, messages: list[dict], start_time: float, total_tokens: int
    ) -> AgentResponse:
        """Synthesize a final answer when max iterations are reached."""
        messages.append({
            "role": "user",
            "content": "You have reached the maximum number of research steps. Based on everything you have gathered so far, provide your FINAL ANSWER now.",
        })
        response = await self.llm.chat(messages)
        return self._build_response(response.content, start_time, total_tokens)
```

### 4.2 OrchestratorAgent — `sailpoint_agent/agents/orchestrator.py`

```python
from typing import Optional

from sailpoint_agent.agents.base import BaseAgent
from sailpoint_agent.llm.base import LLMProvider
from sailpoint_agent.models.query import UserQuery, QueryType
from sailpoint_agent.models.response import AgentResponse
from sailpoint_agent.models.config import AgentConfig
from sailpoint_agent.utils.logger import get_logger

logger = get_logger(__name__)

COMPLEXITY_ANALYSIS_PROMPT = """You are a query analyzer for a SailPoint AI agent.
Analyze the user's query and determine:
1. COMPLEXITY: SIMPLE (single concern) or COMPOUND (multiple concerns needing parallel work)
2. TASK_TYPES: List all task types present (comma-separated):
   - RESEARCH: Questions about SailPoint IIQ, IDN, ISC, or IAM concepts
   - CODE_GENERATION: Write BeanShell, Java, XML, JSON, PowerShell, or API code
   - TEST_CASE: Create test cases or test scenarios
   - DESIGN_HLD: High-level architecture design
   - DESIGN_LLD: Low-level implementation design
   - TROUBLESHOOTING: Debug or diagnose SailPoint issues
   - EXPLANATION: Explain concepts, processes, or behaviors
   - IAM_ADVISORY: IAM strategy, compliance, best practices advice
   - GENERAL: Greetings, meta-questions, or unclear queries

Respond in format:
COMPLEXITY: <SIMPLE|COMPOUND>
TASK_TYPES: <comma-separated list>"""


class OrchestratorAgent:
    """Coordinates multi-specialized agents for query processing.

    Each agent in the pool is a FULL SailPoint & IAM domain expert capable of
    problem solving, explaining, coding, design, test creation, HLD, LLD, and
    IAM advisory. The orchestrator distributes work for parallelism and context
    isolation, not because agents have narrow specializations.

    Uses a meta-ReAct pattern:
    1. THINK: Analyze query complexity and identify parallelism opportunities
    2. ACT: Assign to one or more multi-specialized agents
    3. OBSERVE: Collect agent responses
    4. SYNTHESIZE: Aggregate into unified final response
    """

    def __init__(
        self,
        llm: LLMProvider,
        agents: dict[str, BaseAgent],
        config: AgentConfig = AgentConfig(),
    ):
        self.llm = llm
        self.agent_pool = agents  # Pool of multi-specialized SailPointExpertAgents
        self.config = config

    async def analyze_query(self, query: UserQuery) -> dict:
        """Analyze query complexity and identify task types.

        Returns dict with 'complexity' (SIMPLE|COMPOUND) and 'task_types' list.
        Any agent can handle any task type — this analysis is used for
        parallelism decisions, not for routing to narrow specialists.
        """
        messages = [
            {"role": "system", "content": COMPLEXITY_ANALYSIS_PROMPT},
            {"role": "user", "content": query.text},
        ]
        response = await self.llm.chat(messages)
        return self._parse_analysis(response.content)

    def _get_available_agent(self) -> BaseAgent:
        """Get the next available agent from the pool.

        All agents are equally capable — selection is based on availability,
        not specialization. Any agent can handle any SailPoint/IAM task.
        """
        # Simple round-robin; in production, check agent busy state
        agents = list(self.agent_pool.values())
        return agents[0]

    async def run(self, query: UserQuery) -> AgentResponse:
        """Execute the orchestration loop with multi-specialized agents."""
        # Step 1: THINK — Analyze query complexity
        analysis = await self.analyze_query(query)
        logger.info(f"[Orchestrator] Analysis: {analysis}")

        if analysis["complexity"] == "COMPOUND" and len(analysis["task_types"]) > 1:
            # Step 2a: ACT — Distribute sub-tasks across multiple agents in parallel
            # Each agent is fully capable of any task type
            return await self._run_parallel(query, analysis["task_types"])
        else:
            # Step 2b: ACT — Assign to a single agent (any agent can handle it)
            agent = self._get_available_agent()
            logger.info(f"[Orchestrator] Assigning to: {agent.name}")

            # Step 3: OBSERVE
            response = await agent.run(query)
            response.query_type = analysis["task_types"][0] if analysis["task_types"] else "general"
            return response

    async def _run_parallel(
        self, query: UserQuery, task_types: list[str]
    ) -> AgentResponse:
        """Distribute compound queries across multiple multi-specialized agents.

        Each agent handles a sub-task independently. All agents have full
        SailPoint/IAM expertise — they are assigned by availability, not specialty.
        """
        import asyncio

        agents = list(self.agent_pool.values())
        tasks = []
        for i, task_type in enumerate(task_types):
            agent = agents[i % len(agents)]
            sub_query = UserQuery(
                text=f"[Focus on {task_type}]: {query.text}",
                context=query.context,
            )
            tasks.append(agent.run(sub_query))
            logger.info(f"[Orchestrator] Assigned {task_type} to {agent.name}")

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self._synthesize_results(results)

    def _synthesize_results(self, results: list) -> AgentResponse:
        """Combine results from multiple multi-specialized agents."""
        combined_answer = []
        all_citations = []
        for result in results:
            if isinstance(result, AgentResponse):
                combined_answer.append(result.answer)
                all_citations.extend(result.citations)
        return AgentResponse(
            answer="\n\n---\n\n".join(combined_answer),
            citations=all_citations,
        )

    def _parse_analysis(self, content: str) -> dict:
        """Parse complexity analysis response."""
        lines = content.strip().split("\n")
        complexity = "SIMPLE"
        task_types = ["RESEARCH"]
        for line in lines:
            if line.startswith("COMPLEXITY:"):
                complexity = line.split(":", 1)[1].strip()
            elif line.startswith("TASK_TYPES:"):
                task_types = [t.strip() for t in line.split(":", 1)[1].split(",")]
        return {"complexity": complexity, "task_types": task_types}
```

### 4.3 SailPointExpertAgent — `sailpoint_agent/agents/sailpoint_agent.py`

This is the **single multi-specialized agent class** used by all agents in the pool. Every instance has the full range of SailPoint and IAM capabilities.

```python
from sailpoint_agent.agents.base import BaseAgent
from sailpoint_agent.llm.base import LLMProvider
from sailpoint_agent.tools.base import BaseTool
from sailpoint_agent.models.config import AgentConfig
from sailpoint_agent.models.response import CodeBlock
from sailpoint_agent.prompts.system import SAILPOINT_EXPERT_PROMPT


class SailPointExpertAgent(BaseAgent):
    """Multi-specialized SailPoint and IAM domain expert agent.

    Unlike narrow specialist agents, this agent is capable of ALL SailPoint tasks:
    - Problem solving & troubleshooting (debug rules, diagnose provisioning, fix connectors)
    - Explaining & teaching (concepts, architectures, APIs, workflows at any depth)
    - Code generation (BeanShell, Java, XML, REST API, PowerShell, ISC Transforms, Cloud Rules)
    - Test case creation (unit, integration, UAT, E2E, SOD validation, regression)
    - High-Level Design (HLD) (system topology, integration patterns, deployment strategy)
    - Low-Level Design (LLD) (class/module design, config specs, API contracts, data models)
    - Technical design documents (connector specs, workflow designs, provisioning plans)
    - IAM domain advisory (RBAC/ABAC strategy, SOD, JML lifecycle, compliance, zero-trust)

    The orchestrator creates multiple instances of this agent for parallelism and
    context isolation, not because they have different capabilities.

    Tools: sailpoint_web_search, doc_retriever, api_lookup (all tools available to all agents)
    """

    def __init__(
        self,
        name: str,
        llm: LLMProvider,
        tools: list[BaseTool],
        config: AgentConfig = AgentConfig(),
    ):
        super().__init__(
            name=name,
            llm=llm,
            tools=tools,
            system_prompt=SAILPOINT_EXPERT_PROMPT,
            config=config,
        )

    async def select_tool(self, thought: str) -> tuple[str, dict]:
        """Intelligently select the best tool based on current reasoning.

        This agent has access to ALL tools and uses LLM-based tool selection
        to pick the optimal tool for any task type.

        Decision logic:
        - If thought mentions needing to search → sailpoint_web_search
        - If thought mentions a specific URL → doc_retriever
        - If thought mentions API endpoint details → api_lookup
        - For any task (code, test, design, troubleshooting) → search first, then synthesize
        """
        messages = [
            {"role": "system", "content": self._tool_selection_prompt()},
            {"role": "user", "content": f"Based on this reasoning, select a tool:\n{thought}"},
        ]
        response = await self.llm.chat(messages, tools=self._tool_schemas())
        return self._parse_tool_call(response)

    def _tool_selection_prompt(self) -> str:
        tool_descriptions = "\n".join(
            f"- {name}: {tool.description}" for name, tool in self.tools.items()
        )
        return f"""You are a multi-specialized SailPoint expert selecting the best tool.
You can handle ANY task: research, coding, testing, design, troubleshooting, or advisory.
Select the most relevant tool for your current reasoning step.

Available tools:
{tool_descriptions}"""

    def _tool_schemas(self) -> list[dict]:
        """Convert tools to LLM function-calling schema format."""
        return [tool.to_schema() for tool in self.tools.values()]

    def _parse_tool_call(self, response) -> tuple[str, dict]:
        """Extract tool name and arguments from LLM response."""
        if response.tool_calls:
            call = response.tool_calls[0]
            return call.name, call.arguments
        # Fallback: default to web search
        return "sailpoint_web_search", {"query": "SailPoint documentation"}

    def _parse_code_blocks(self, text: str) -> list[CodeBlock]:
        """Extract code blocks from response text (used for any task that includes code)."""
        blocks = []
        parts = text.split("```")
        for i in range(1, len(parts), 2):
            block = parts[i]
            lines = block.split("\n", 1)
            language = lines[0].strip() if lines else "text"
            code = lines[1] if len(lines) > 1 else block
            blocks.append(CodeBlock(
                code=code.strip(),
                language=language or "text",
                description="",
            ))
        return blocks
```

---

## 5. Tools Layer (Low-Level Design)

### 5.1 BaseTool — `sailpoint_agent/tools/base.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    output: str
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    tokens_used: int = 0


class BaseTool(ABC):
    """Abstract base class for all agent tools."""

    name: str = ""
    description: str = ""

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given arguments."""
        ...

    def to_schema(self) -> dict:
        """Convert tool to LLM function-calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self._parameters_schema(),
            },
        }

    @abstractmethod
    def _parameters_schema(self) -> dict:
        """Return JSON Schema for tool parameters."""
        ...
```

### 5.2 SailPointWebSearch — `sailpoint_agent/tools/web_search.py`

```python
from sailpoint_agent.tools.base import BaseTool, ToolResult
from sailpoint_agent.models.config import SearchConfig


class SailPointWebSearch(BaseTool):
    """Web search tool scoped to SailPoint and IAM documentation sources.

    Searches SailPoint domains first, then falls back to general web if configured.
    Uses Claude Agent SDK WebSearch or a configurable search backend.
    """

    name = "sailpoint_web_search"
    description = (
        "Search SailPoint documentation, developer portal, community forums, "
        "and IAM resources. Use for finding official docs, code examples, "
        "API references, and community solutions."
    )

    SAILPOINT_DOMAINS = [
        "developer.sailpoint.com",
        "documentation.sailpoint.com",
        "community.sailpoint.com",
        "github.com/sailpoint-oss",
    ]

    def __init__(self, search_config: SearchConfig = SearchConfig()):
        self.config = search_config

    async def execute(
        self,
        query: str,
        domains: list[str] | None = None,
    ) -> ToolResult:
        """Search for SailPoint-related content.

        Args:
            query: Search query string
            domains: Optional domain filter (defaults to SAILPOINT_DOMAINS)
        """
        target_domains = domains or self.SAILPOINT_DOMAINS

        try:
            # Phase 1: Search SailPoint-scoped domains
            results = await self._search(query, allowed_domains=target_domains)

            # Phase 2: Fallback to general web if no results and configured
            if not results and self.config.fallback_to_general_web:
                results = await self._search(f"SailPoint {query}")

            if not results:
                return ToolResult(
                    success=False,
                    output="No results found.",
                    error="No search results for query.",
                )

            formatted = self._format_results(results)
            return ToolResult(success=True, output=formatted)

        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

    async def _search(
        self, query: str, allowed_domains: list[str] | None = None
    ) -> list[dict]:
        """Execute web search. Implementation delegates to search backend."""
        # This will be implemented using Claude Agent SDK WebSearch tool
        # or a pluggable search backend (SerpAPI, Tavily, etc.)
        raise NotImplementedError("Implement with chosen search backend")

    def _format_results(self, results: list[dict]) -> str:
        """Format search results as readable text for the agent."""
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] {r.get('title', 'No title')}")
            lines.append(f"    URL: {r.get('url', '')}")
            lines.append(f"    {r.get('snippet', '')}")
            lines.append("")
        return "\n".join(lines)

    def _parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query about SailPoint or IAM topics",
                },
                "domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of domains to restrict search to",
                },
            },
            "required": ["query"],
        }
```

### 5.3 SailPointAPILookup — `sailpoint_agent/tools/api_lookup.py`

```python
from sailpoint_agent.tools.base import BaseTool, ToolResult


class SailPointAPILookup(BaseTool):
    """Look up SailPoint API endpoints and specifications.

    Provides structured API information for IIQ SCIM APIs and ISC V3 APIs.
    """

    name = "api_lookup"
    description = (
        "Look up SailPoint API endpoints, methods, parameters, and examples. "
        "Covers IIQ SCIM APIs and ISC V3 APIs."
    )

    API_DOCS = {
        "iiq_scim": "https://developer.sailpoint.com/docs/api/iiq/",
        "isc_v3": "https://developer.sailpoint.com/docs/api/v3/",
    }

    async def execute(self, query: str, product: str = "isc") -> ToolResult:
        """Look up API documentation.

        Args:
            query: API endpoint or operation to look up
            product: "iiq" or "isc" (default: "isc")
        """
        base_url = self.API_DOCS.get(f"{product}_scim" if product == "iiq" else f"{product}_v3")
        if not base_url:
            return ToolResult(success=False, output="", error=f"Unknown product: {product}")

        # Fetch and parse API documentation page
        try:
            content = await self._fetch_api_docs(base_url, query)
            return ToolResult(success=True, output=content)
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

    async def _fetch_api_docs(self, base_url: str, query: str) -> str:
        """Fetch API docs from SailPoint developer portal."""
        raise NotImplementedError("Implement with HTTP client")

    def _parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "API endpoint or operation name to look up",
                },
                "product": {
                    "type": "string",
                    "enum": ["iiq", "isc"],
                    "description": "SailPoint product (iiq or isc)",
                },
            },
            "required": ["query"],
        }
```

### 5.4 DocumentationRetriever — `sailpoint_agent/tools/doc_retriever.py`

```python
from sailpoint_agent.tools.base import BaseTool, ToolResult


class DocumentationRetriever(BaseTool):
    """Fetch and parse a specific documentation page for detailed content."""

    name = "doc_retriever"
    description = (
        "Fetch a specific SailPoint documentation page by URL and extract "
        "its content. Use when you have a specific URL from search results "
        "and need the full page content."
    )

    async def execute(self, url: str) -> ToolResult:
        """Fetch and parse a documentation page.

        Args:
            url: Full URL of the documentation page to fetch
        """
        try:
            content = await self._fetch_and_parse(url)
            return ToolResult(
                success=True,
                output=content,
                metadata={"url": url},
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

    async def _fetch_and_parse(self, url: str) -> str:
        """Fetch URL content and convert to clean text/markdown."""
        # Implementation: use httpx to fetch, then html2text or similar to parse
        raise NotImplementedError("Implement with HTTP client + HTML parser")

    def _parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL of the documentation page to fetch",
                },
            },
            "required": ["url"],
        }
```

---

## 6. LLM Provider Layer (Low-Level Design)

### 6.1 LLMProvider ABC — `sailpoint_agent/llm/base.py`

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

### 6.2 ClaudeProvider — `sailpoint_agent/llm/claude_provider.py`

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

### 6.3 OpenAIProvider — `sailpoint_agent/llm/openai_provider.py`

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

### 6.4 LiteLLMProvider — `sailpoint_agent/llm/litellm_provider.py`

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

### 6.5 LLMProviderFactory — `sailpoint_agent/llm/factory.py`

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

## 7. CLI Interface (Low-Level Design)

### 7.1 CLI Application — `sailpoint_agent/cli/app.py`

```python
import asyncio
import click
from rich.console import Console

from sailpoint_agent.config.settings import load_config
from sailpoint_agent.cli.renderer import render_response
from sailpoint_agent.cli.repl import run_repl
from sailpoint_agent.models.query import UserQuery, QueryContext

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
    """Ask a single question about SailPoint."""
    app_config = ctx.obj["config"]
    verbose = ctx.obj["verbose"]

    user_query = UserQuery(
        text=question,
        context=QueryContext(include_traces=verbose),
    )

    async def _run():
        orchestrator = _build_orchestrator(app_config)
        response = await orchestrator.run(user_query)
        render_response(console, response, show_traces=verbose)
        if output:
            _save_to_file(response, output)

    asyncio.run(_run())


@cli.command()
@click.pass_context
def chat(ctx):
    """Start an interactive chat session."""
    app_config = ctx.obj["config"]
    verbose = ctx.obj["verbose"]
    asyncio.run(run_repl(app_config, verbose=verbose))


def _build_orchestrator(config):
    """Bootstrap the orchestrator with a pool of multi-specialized agents.

    Each agent in the pool is an identical SailPointExpertAgent — a full-stack
    SailPoint & IAM expert capable of problem solving, explaining, coding,
    testing, HLD, LLD, design, and IAM advisory. Multiple instances exist
    for parallelism and context isolation, not for narrow specialization.
    """
    from sailpoint_agent.agents.orchestrator import OrchestratorAgent
    from sailpoint_agent.agents.sailpoint_agent import SailPointExpertAgent
    from sailpoint_agent.llm.factory import LLMProviderFactory
    from sailpoint_agent.tools.web_search import SailPointWebSearch
    from sailpoint_agent.tools.api_lookup import SailPointAPILookup
    from sailpoint_agent.tools.doc_retriever import DocumentationRetriever

    llm = LLMProviderFactory.create(config.llm)
    tools = [SailPointWebSearch(config.search), SailPointAPILookup(), DocumentationRetriever()]

    # Pool of multi-specialized agents (all equally capable of any task)
    agents = {
        "agent_alpha": SailPointExpertAgent(name="Agent-Alpha", llm=llm, tools=tools, config=config.agent),
        "agent_beta": SailPointExpertAgent(name="Agent-Beta", llm=llm, tools=tools, config=config.agent),
        "agent_gamma": SailPointExpertAgent(name="Agent-Gamma", llm=llm, tools=tools, config=config.agent),
        "agent_delta": SailPointExpertAgent(name="Agent-Delta", llm=llm, tools=tools, config=config.agent),
    }

    return OrchestratorAgent(llm=llm, agents=agents, config=config.agent)


def _save_to_file(response, filepath: str):
    with open(filepath, "w") as f:
        f.write(response.answer)
    console.print(f"[green]Response saved to {filepath}[/green]")
```

### 7.2 Interactive REPL — `sailpoint_agent/cli/repl.py`

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

### 7.3 Response Renderer — `sailpoint_agent/cli/renderer.py`

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

## 8. Web UI Interface (Low-Level Design)

### 8.1 Streamlit App — `sailpoint_agent/ui/streamlit_app.py`

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

## 9. Prompts Design

### 9.1 System Prompts — `sailpoint_agent/prompts/system.py`

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

## 10. Configuration

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

## 11. Sequence Diagrams

### 11.1 Single Query Flow

```
User                CLI              Orchestrator        ResearchAgent       WebSearch        LLM
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

## 12. Error Handling Strategy

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

## 13. Dependencies

```
# requirements.txt
anthropic>=0.40.0
openai>=1.50.0
litellm>=1.50.0
click>=8.1.0
rich>=13.0.0
streamlit>=1.40.0
httpx>=0.27.0
python-dotenv>=1.0.0
pyyaml>=6.0.0
structlog>=24.0.0
pytest>=8.0.0
pytest-asyncio>=0.24.0
```
