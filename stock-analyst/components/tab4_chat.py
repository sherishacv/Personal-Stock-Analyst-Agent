"""
Tab 4 — AI Analyst Chat

- Streaming responses via Groq (word-by-word output with st.write_stream)
- Full portfolio context injected into every system prompt
- Suggested question chips
- Persistent chat history in session state
- Clear chat button
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from utils.llm_agent import stream_chat_response


SUGGESTED_QUESTIONS = [
    "Summarise my overall trading performance",
    "Which stock has the best unrealised return?",
    "What is my biggest concentration risk?",
    "How does my XIRR compare to a typical S&P 500 return?",
    "Which trades have been most profitable?",
    "Am I over-exposed to any single sector?",
]


def render_tab4() -> None:
    st.header("🤖 AI Analyst — Chat with Your Portfolio")

    if "transactions_df" not in st.session_state:
        st.warning("⚠️ Upload your transaction history in the **Data Upload** tab first.")
        return

    df: pd.DataFrame = st.session_state["transactions_df"]

    if "holdings_df" not in st.session_state:
        st.info("💡 Visit the **Portfolio View** tab first to load current prices, then return here.")
        return

    holdings_df: pd.DataFrame = st.session_state["holdings_df"]
    metrics: dict = st.session_state.get("performance_metrics", {})

    # ── Suggested question chips ──────────────────────────────────────────────
    st.markdown("**💡 Suggested questions:**")
    cols = st.columns(3)
    for i, question in enumerate(SUGGESTED_QUESTIONS):
        if cols[i % 3].button(question, key=f"q_{i}", use_container_width=True):
            st.session_state.setdefault("chat_messages", [])
            st.session_state["_pending_message"] = question

    st.divider()

    # ── Initialise chat history ───────────────────────────────────────────────
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    # ── Render existing messages ──────────────────────────────────────────────
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Handle pending message from buttons ──────────────────────────────────
    if "_pending_message" in st.session_state:
        pending = st.session_state.pop("_pending_message")
        _handle_user_message(pending, df, holdings_df, metrics)
        st.rerun()

    # ── Chat input ────────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask anything about your portfolio…")
    if user_input and user_input.strip():
        _handle_user_message(user_input.strip(), df, holdings_df, metrics)

    # ── Clear chat ────────────────────────────────────────────────────────────
    if st.session_state.get("chat_messages"):
        st.write("")
        if st.button("🗑️ Clear conversation", key="clear_chat"):
            st.session_state["chat_messages"] = []
            st.rerun()


def _handle_user_message(
    user_input: str,
    df: pd.DataFrame,
    holdings_df: pd.DataFrame,
    metrics: dict,
) -> None:
    """Append user message, stream AI response, update chat history."""
    st.session_state["chat_messages"].append({"role": "user", "content": user_input})

    # Display the user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build message history (exclude system prompt — handled inside stream_chat_response)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state["chat_messages"]
    ]

    # Stream the AI response
    with st.chat_message("assistant"):
        try:
            response_text = st.write_stream(
                stream_chat_response(history, holdings_df, metrics, df=df)
            )
        except Exception as exc:
            response_text = f"⚠️ Error: {exc}"
            st.markdown(response_text)

    st.session_state["chat_messages"].append(
        {"role": "assistant", "content": response_text or ""}
    )
