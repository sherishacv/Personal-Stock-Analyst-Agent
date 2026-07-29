"""
Tab 2 — Consolidated Portfolio View

- Pie chart (allocation by current market value)
- Total portfolio value metric
- Holdings table: FIFO avg cost, current price, unrealized P&L ($  and %)
- AI portfolio health summary (Groq, 2-3 sentences)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.portfolio_math import build_holdings_table
from utils.llm_agent import get_portfolio_summary


# ── Consistent palette & chart base ──────────────────────────────────────────
_PALETTE = [
    "#4F46E5", "#7C3AED", "#0EA5E9", "#10B981",
    "#F59E0B", "#EF4444", "#EC4899", "#14B8A6",
    "#F97316", "#6366F1",
]
_CHART_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=12, color="#374151"),
)
_AXIS = dict(gridcolor="#F1F5F9", linecolor="#E2E8F0", zerolinecolor="#E2E8F0")


def render_tab2() -> None:
    st.header("📊 Consolidated Portfolio View")

    if "transactions_df" not in st.session_state:
        st.warning("⚠️ Upload your transaction history in the **Data Upload** tab first.")
        return

    df: pd.DataFrame = st.session_state["transactions_df"]

    # ── Fetch / cache holdings ────────────────────────────────────────────────
    with st.spinner("Fetching current market prices…"):
        holdings_df = build_holdings_table(df)

    st.session_state["holdings_df"] = holdings_df  # share with Tab 3 / 4

    if holdings_df.empty:
        st.info(
            "No open positions found. All shares appear to have been sold. "
            "Check the Historical Performance tab for lifetime metrics."
        )
        return

    # ── Total value headline ──────────────────────────────────────────────────
    valid_values = holdings_df["Current Value"].dropna()
    total_value = float(valid_values.sum())
    total_cost   = float(holdings_df["Cost Basis"].sum())
    total_unreal = total_value - total_cost
    total_unreal_pct = total_unreal / total_cost * 100 if total_cost > 0 else 0.0

    m1, m2, m3 = st.columns(3)
    m1.metric(
        "💰 Current Portfolio Value",
        f"${total_value:,.2f}",
        delta=f"{'+' if total_unreal >= 0 else ''}${total_unreal:,.2f} unrealised",
    )
    m2.metric(
        "📦 Total Cost Basis",
        f"${total_cost:,.2f}",
    )
    m3.metric(
        "📈 Unrealised Return",
        f"{total_unreal_pct:+.2f}%",
        delta=f"${total_unreal:+,.2f}",
    )

    st.divider()

    # ── Pie chart + AI summary ────────────────────────────────────────────────
    col_chart, col_ai = st.columns([3, 2], gap="large")

    with col_chart:
        st.subheader("Portfolio Allocation")
        pie_df = (
            holdings_df[["Ticker", "Current Value"]]
            .dropna()
            .sort_values("Current Value", ascending=False)
        )
        if not pie_df.empty:
            fig = px.pie(
                pie_df,
                names="Ticker",
                values="Current Value",
                hole=0.42,
                color_discrete_sequence=_PALETTE,
            )
            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>Value: $%{value:,.2f}<br>Share: %{percent}<extra></extra>",
                marker=dict(line=dict(color="#ffffff", width=2)),
            )
            fig.update_layout(
                **_CHART_BASE,
                showlegend=True,
                legend=dict(orientation="v", x=1.02, y=0.5, font=dict(size=12)),
                margin=dict(t=10, b=10, l=10, r=120),
                height=380,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_ai:
        st.subheader("🤖 AI Portfolio Health")

        # Build a metrics dict for the AI (we don't have full metrics yet — compute partial)
        partial_metrics = {
            "total_investment": total_cost,
            "current_portfolio_value": total_value,
            "total_return_dollars": total_unreal,
            "total_return_pct": total_unreal_pct,
            "realized_pnl": 0,        # not available without full df
            "total_sell_proceeds": 0,
            "xirr": None,
        }

        # Use cached summary if holdings haven't changed
        cache_key = f"ai_summary_{hash(holdings_df.to_json())}"
        if cache_key not in st.session_state:
            with st.spinner("Analysing with Groq…"):
                summary = get_portfolio_summary(holdings_df, partial_metrics)
            st.session_state[cache_key] = summary
        else:
            summary = st.session_state[cache_key]

        st.info(summary)
        if st.button("🔄 Refresh AI summary", key="refresh_summary"):
            st.session_state.pop(cache_key, None)
            st.rerun()

    st.divider()

    # ── Holdings breakdown table ──────────────────────────────────────────────
    st.subheader("Holdings Breakdown")
    st.caption("Cost basis calculated using FIFO (First In, First Out) accounting.")

    # Colour-code P&L
    def _fmt_currency(v):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return "N/A"
        return f"${v:,.2f}"

    def _fmt_pct(v):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return "N/A"
        arrow = "▲" if v >= 0 else "▼"
        color = "green" if v >= 0 else "red"
        return f":{color}[{arrow} {abs(v):.2f}%]"

    display = holdings_df.copy()
    display["Avg Cost (FIFO)"] = display["Avg Cost (FIFO)"].apply(_fmt_currency)
    display["Current Price"]   = display["Current Price"].apply(_fmt_currency)
    display["Cost Basis"]      = display["Cost Basis"].apply(_fmt_currency)
    display["Current Value"]   = display["Current Value"].apply(_fmt_currency)
    display["Unrealized Gain ($)"] = display["Unrealized Gain ($)"].apply(_fmt_currency)

    # Render as plain table (markdown colouring not supported in st.dataframe natively)
    # Use st.dataframe with column config for cleaner output
    raw = holdings_df.copy()

    st.dataframe(
        raw,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Quantity": st.column_config.NumberColumn("Quantity", format="%.4f"),
            "Avg Cost (FIFO)": st.column_config.NumberColumn("Avg Cost", format="$%.4f"),
            "Current Price": st.column_config.NumberColumn("Price", format="$%.2f"),
            "Cost Basis": st.column_config.NumberColumn("Cost Basis", format="$%.2f"),
            "Current Value": st.column_config.NumberColumn("Mkt Value", format="$%.2f"),
            "Unrealized Gain ($)": st.column_config.NumberColumn("Unreal. P&L ($)", format="$%.2f"),
            "Unrealized Gain (%)": st.column_config.NumberColumn("Unreal. P&L (%)", format="%.2f%%"),
        },
    )

    # ── Download ──────────────────────────────────────────────────────────────
    st.download_button(
        "⬇️ Download holdings CSV",
        data=holdings_df.to_csv(index=False),
        file_name="current_holdings.csv",
        mime="text/csv",
    )
