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
    "WebSearch",
    "WebFetch",
    "Skill",
    "mcp__sailpoint-tools__sailpoint_web_search",
    "mcp__sailpoint-tools__api_lookup",
    "mcp__sailpoint-tools__doc_retriever",
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
