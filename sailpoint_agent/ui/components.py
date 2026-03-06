"""Reusable Streamlit UI components for the SailPoint Query AI Agent."""

import streamlit as st
from sailpoint_agent.models.response import AgentResponse


def render_citations(response: AgentResponse) -> None:
    """Render source citations below the response."""
    if not response.citations:
        return

    st.markdown("**Sources:**")
    for cite in response.citations:
        st.markdown(f"- [{cite.title}]({cite.url})")


def render_code_blocks(response: AgentResponse) -> None:
    """Render code blocks with syntax highlighting."""
    for block in response.code_blocks:
        if block.description:
            st.markdown(f"**{block.description}**")
        st.code(block.code, language=block.language)


def render_reasoning_trace(response: AgentResponse) -> None:
    """Render reasoning trace in an expandable section."""
    if not response.reasoning_trace:
        return

    with st.expander("Reasoning Trace", expanded=False):
        for step in response.reasoning_trace:
            st.markdown(f"**Step {step.step_number}**")
            st.markdown(f"*Think:* {step.thought}")
            if step.action:
                st.markdown(f"*Act:* `{step.action}`")
            if step.observation:
                st.markdown(f"*Observe:* {step.observation[:500]}")
            st.divider()


def render_metadata(response: AgentResponse) -> None:
    """Render response metadata (model, tokens, time)."""
    if response.model_used or response.tokens_used:
        st.caption(
            f"Model: {response.model_used} | "
            f"Tokens: {response.tokens_used} | "
            f"Time: {response.response_time_ms}ms"
        )
