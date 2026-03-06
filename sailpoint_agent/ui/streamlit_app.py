"""Streamlit-based web UI for SailPoint Query AI Agent."""

import asyncio

import streamlit as st

from sailpoint_agent.config.settings import load_config
from sailpoint_agent.main import run_single_query


def main():
    st.set_page_config(
        page_title="SailPoint Query AI Agent",
        page_icon="sailboat",
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
        st.session_state.config = load_config("config.yaml")

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
                result = asyncio.run(
                    run_single_query(prompt, st.session_state.config)
                )

            st.markdown(result)

        st.session_state.messages.append({
            "role": "assistant",
            "content": result,
        })


if __name__ == "__main__":
    main()
