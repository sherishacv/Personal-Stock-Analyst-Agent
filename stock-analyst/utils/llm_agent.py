"""
Groq LLM utilities — production design:

- No module-level singleton (Streamlit workers can share state unpredictably).
  A fresh Groq client is created per call; the SDK is lightweight.
- Retry with exponential back-off (up to 3 attempts) on transient 503 / 429 errors.
- Token-budget guard: system context is truncated to ~6 000 chars so we never
  blow the llama-3.3-70b-versatile 8 192-token context limit even with a long
  transaction history.
- Chat streaming: stream=True gives word-by-word output via st.write_stream.
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Generator, Iterator

import pandas as pd
from groq import Groq, APIStatusError, APITimeoutError, RateLimitError

log = logging.getLogger(__name__)

MODEL = "llama-3.3-70b-versatile"
MAX_RETRIES = 3
BASE_BACKOFF = 1.0          # seconds; doubles each retry
CONTEXT_CHAR_BUDGET = 6_000 # approximate char budget for portfolio context block


# ─────────────────────────────────────────────────────────────────────────────
# Client factory
# ─────────────────────────────────────────────────────────────────────────────

def _get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Add it as a Replit Secret named GROQ_API_KEY."
        )
    return Groq(api_key=api_key)


def _call_with_retry(client: Groq, **kwargs) -> str:
    """Call chat.completions.create with retries on transient errors."""
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content.strip()
        except (APITimeoutError, APIStatusError, RateLimitError) as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                sleep_time = BASE_BACKOFF * (2 ** (attempt - 1))
                log.warning("Groq API error (attempt %d/%d): %s — retrying in %.1fs",
                            attempt, MAX_RETRIES, exc, sleep_time)
                time.sleep(sleep_time)
            else:
                raise
        except Exception:
            raise
    raise RuntimeError(f"All {MAX_RETRIES} Groq attempts failed") from last_exc


# ─────────────────────────────────────────────────────────────────────────────
# Context builder (shared by summary + chat)
# ─────────────────────────────────────────────────────────────────────────────

def _build_portfolio_context(
    holdings_df: pd.DataFrame,
    metrics: dict,
    df: pd.DataFrame | None = None,
    char_budget: int = CONTEXT_CHAR_BUDGET,
) -> str:
    """
    Build a structured portfolio context string, truncated to char_budget.
    Keeps metrics and holdings (most important); truncates transaction history
    from the tail if budget is tight.
    """
    xirr = metrics.get("xirr")
    xirr_str = f"{xirr:.2f}%" if xirr is not None else "N/A"
    ret_d = metrics.get("total_return_dollars", 0)
    ret_p = metrics.get("total_return_pct", 0)

    # ── Metrics block ─────────────────────────────────────────────────────────
    metrics_block = (
        f"=== PORTFOLIO METRICS ===\n"
        f"Total Invested:          ${metrics.get('total_investment', 0):>12,.2f}\n"
        f"Total Sell Proceeds:     ${metrics.get('total_sell_proceeds', 0):>12,.2f}\n"
        f"Realised P&L:            ${metrics.get('realized_pnl', 0):>12,.2f}\n"
        f"Current Portfolio Value: ${metrics.get('current_portfolio_value', 0):>12,.2f}\n"
        f"Total Return:            ${ret_d:>+12,.2f}  ({ret_p:+.2f}%)\n"
        f"XIRR (annualised):       {xirr_str}\n"
    )

    # ── Holdings block ────────────────────────────────────────────────────────
    if not holdings_df.empty:
        # Compute allocation % for the AI
        total_val = holdings_df["Current Value"].dropna().sum()
        hdf = holdings_df.copy()
        hdf["Allocation %"] = (hdf["Current Value"] / total_val * 100).round(1)
        holdings_block = "\n=== CURRENT HOLDINGS ===\n" + hdf.to_string(index=False)
    else:
        holdings_block = "\n=== CURRENT HOLDINGS ===\nNo open positions."

    combined = metrics_block + holdings_block
    remaining_budget = char_budget - len(combined)

    # ── Transaction history (fill remaining budget, most-recent first) ────────
    if df is not None and not df.empty and remaining_budget > 200:
        tx_str = df.sort_values("date", ascending=False).to_string(index=False)
        if len(tx_str) > remaining_budget - 50:
            tx_str = tx_str[: remaining_budget - 80] + "\n... (truncated)"
        combined += "\n\n=== TRANSACTION HISTORY ===\n" + tx_str

    return combined


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2 — Portfolio health summary (single-shot)
# ─────────────────────────────────────────────────────────────────────────────

def get_portfolio_summary(
    holdings_df: pd.DataFrame,
    metrics: dict,
) -> str:
    """
    Return a 2-3 sentence portfolio health + concentration-risk summary.
    """
    if holdings_df.empty:
        return "No current holdings to analyse."

    try:
        client = _get_client()
        context = _build_portfolio_context(holdings_df, metrics, char_budget=3_000)

        prompt = (
            "You are a concise, data-driven financial analyst.\n\n"
            f"{context}\n\n"
            "In exactly 2-3 sentences, summarise:\n"
            "1. Overall portfolio health and sector/ticker diversification.\n"
            "2. The single greatest concentration risk and whether the portfolio is "
            "net-positive or net-negative in total return terms.\n"
            "Use specific ticker names and percentages. No bullet points. No markdown headers."
        )

        return _call_with_retry(
            client,
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=220,
            temperature=0.35,
        )

    except Exception as exc:
        return f"⚠️ AI summary unavailable: {exc}"


# ─────────────────────────────────────────────────────────────────────────────
# Tab 4 — Chat agent (streaming)
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM_PREAMBLE = (
    "You are an expert personal US stock portfolio analyst with deep knowledge of "
    "equity markets, technical analysis, and portfolio theory. "
    "You have been given the user's complete portfolio data below. "
    "Answer questions accurately, cite specific numbers from the data, and be concise. "
    "If asked about real-time news or intraday price movements, clarify that your price "
    "data has a ~5-minute cache delay and you have no access to live news feeds. "
    "Do not invent data that is not present. Use Markdown for formatting when helpful."
)


def build_system_prompt(
    holdings_df: pd.DataFrame,
    metrics: dict,
    df: pd.DataFrame | None = None,
) -> str:
    context = _build_portfolio_context(holdings_df, metrics, df=df)
    return f"{_SYSTEM_PREAMBLE}\n\n{context}"


def stream_chat_response(
    messages: list[dict],
    holdings_df: pd.DataFrame,
    metrics: dict,
    df: pd.DataFrame | None = None,
) -> Iterator[str]:
    """
    Yield response tokens one by one (for use with st.write_stream).
    Falls back to a single-string yield on streaming error.
    """
    client = _get_client()
    system_prompt = build_system_prompt(holdings_df, metrics, df=df)
    groq_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=groq_messages,
            max_tokens=1_024,
            temperature=0.45,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as exc:
        # Fallback: non-streaming
        log.warning("Streaming failed, falling back to non-streaming: %s", exc)
        try:
            text = _call_with_retry(
                client,
                model=MODEL,
                messages=groq_messages,
                max_tokens=1_024,
                temperature=0.45,
            )
            yield text
        except Exception as exc2:
            yield f"⚠️ Error communicating with AI: {exc2}"
