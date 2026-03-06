"""Shared test fixtures for SailPoint Query AI Agent tests."""

import pytest

from sailpoint_agent.models.config import AppConfig, LLMConfig, AgentConfig, SearchConfig
from sailpoint_agent.models.query import UserQuery, QueryContext, SailPointProduct
from sailpoint_agent.models.response import AgentResponse, Citation, CodeBlock, ReasoningStep


@pytest.fixture
def app_config() -> AppConfig:
    """Create a test application configuration."""
    return AppConfig(
        llm=LLMConfig(
            provider="claude",
            model="claude-sonnet-4-20250514",
            api_key="test-key",
            temperature=0.1,
            max_tokens=4096,
        ),
        agent=AgentConfig(
            max_iterations=3,
            confidence_threshold=0.85,
            enable_traces=False,
            search_depth=2,
        ),
        search=SearchConfig(
            max_results_per_search=3,
            fetch_page_content=True,
            fallback_to_general_web=False,
        ),
    )


@pytest.fixture
def sample_query() -> UserQuery:
    """Create a sample user query for testing."""
    return UserQuery(
        text="How do I create a BuildMap rule in IdentityIQ?",
        context=QueryContext(
            product_focus=SailPointProduct.IIQ,
            iiq_version="8.4",
        ),
    )


@pytest.fixture
def sample_response() -> AgentResponse:
    """Create a sample agent response for testing."""
    return AgentResponse(
        answer="# BuildMap Rule\n\nA BuildMap rule transforms data during aggregation...",
        citations=[
            Citation(
                title="IIQ Rule Guide",
                url="https://developer.sailpoint.com/docs/rules",
                domain="developer.sailpoint.com",
            ),
        ],
        code_blocks=[
            CodeBlock(
                code='import sailpoint.object.ResourceObject;\n\n// Transform the map\nMap map = new HashMap();',
                language="beanshell",
                description="BuildMap Rule Example",
            ),
        ],
        reasoning_trace=[
            ReasoningStep(
                step_number=1,
                thought="Need to search for BuildMap rule documentation",
                action="sailpoint_web_search",
                observation="Found relevant docs on developer.sailpoint.com",
            ),
        ],
        model_used="claude-sonnet-4-20250514",
        tokens_used=1500,
        response_time_ms=3200,
    )
