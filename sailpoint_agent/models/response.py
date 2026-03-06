"""Response models for the SailPoint Query AI Agent."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Citation:
    """A source reference for information in the response."""
    title: str
    url: str
    snippet: Optional[str] = None
    domain: Optional[str] = None


@dataclass
class CodeBlock:
    """A code snippet included in the response."""
    code: str
    language: str
    description: str = ""
    filename: Optional[str] = None


@dataclass
class TestCase:
    """A structured test case for SailPoint implementation testing."""
    id: str
    title: str
    description: str
    preconditions: list[str]
    steps: list[str]
    expected_result: str
    priority: str = "Medium"
    category: str = ""


@dataclass
class DesignSection:
    """A section within a technical design document."""
    heading: str
    content: str
    diagrams: list[str] = field(default_factory=list)
    subsections: list["DesignSection"] = field(default_factory=list)


@dataclass
class DesignDocument:
    """A complete technical design document (HLD or LLD)."""
    title: str
    doc_type: str
    sections: list[DesignSection]
    version: str = "1.0"


@dataclass
class ReasoningStep:
    """A single step in the ReAct reasoning trace."""
    step_number: int
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None


@dataclass
class AgentResponse:
    """Complete response from the agent to the user."""
    answer: str
    citations: list[Citation] = field(default_factory=list)
    code_blocks: list[CodeBlock] = field(default_factory=list)
    test_cases: list[TestCase] = field(default_factory=list)
    design_document: Optional[DesignDocument] = None
    reasoning_trace: list[ReasoningStep] = field(default_factory=list)
    query_type: Optional[str] = None
    confidence: float = 0.0
    tokens_used: int = 0
    model_used: str = ""
    response_time_ms: int = 0
