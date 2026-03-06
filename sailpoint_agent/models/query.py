"""Query models for the SailPoint Query AI Agent."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class QueryType(Enum):
    """Classification of user queries for agent routing."""
    RESEARCH = "research"
    CODE_GENERATION = "code_generation"
    TEST_CASE = "test_case"
    DESIGN = "design"
    API_LOOKUP = "api_lookup"
    GENERAL = "general"


class SailPointProduct(Enum):
    """SailPoint product family identifiers."""
    IIQ = "identityiq"
    IDN = "identitynow"
    ISC = "identity_security_cloud"
    GENERAL = "general"


@dataclass
class QueryContext:
    """Contextual information for query processing."""
    conversation_history: list[dict] = field(default_factory=list)
    product_focus: SailPointProduct = SailPointProduct.GENERAL
    iiq_version: Optional[str] = None
    preferred_language: str = "beanshell"
    include_traces: bool = False


@dataclass
class UserQuery:
    """Represents a user's question or request to the agent."""
    text: str
    query_type: Optional[QueryType] = None
    context: QueryContext = field(default_factory=QueryContext)
    session_id: Optional[str] = None
