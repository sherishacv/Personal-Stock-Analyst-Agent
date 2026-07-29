"""
Tab 3 — Historical Performance

Metrics: Total Invested · Total Sell Proceeds · Realised P&L ·
         Current Value · Total Return ($  and %) · XIRR

Charts:
- Cumulative net cash flow over time
- Monthly buy-vs-sell activity bar chart
- Per-ticker realised P&L bar chart
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from utils.portfolio_math import compute_performance_metrics, compute_fifo_holdings


# ── Consistent palette & chart base ──────────────────────────────────────────
_CHART_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=12, color="#374151"),
)
_AXIS = dict(gridcolor="#F1F5F9", linecolor="#E2E8F0", zerolinecolor="#E2E8F0")
# Semantic colours — kept consistent throughout all charts
_BUY_COLOR  = "#4F46E5"   # indigo
_SELL_COLOR = "#F59E0B"   # amber
_POS_COLOR  = "#059669"   # emerald
_NEG_COLOR  = "#DC2626"   # red


def render_tab3() -> None:
    st.header("📈 Historical Performance")

    if "transactions_df" not in st.session_state:
        st.warning(
            "⚠️ Upload your transaction history in the **Data Upload** tab first."
        )
        return

    df: pd.DataFrame = st.session_state["transactions_df"]

    # Reuse holdings_df from Tab 2 if already computed; otherwise trigger it
    if "holdings_df" not in st.session_state:
        st.info(
            "💡 Visit the **Portfolio View** tab first to load current prices, then return here."
        )
        return

    holdings_df: pd.DataFrame = st.session_state["holdings_df"]

    # ── Compute / cache metrics ────────────────────────────────────────────────
    metrics_key = f"perf_metrics_{hash(df.to_json())}"
    if metrics_key not in st.session_state:
        with st.spinner("Computing performance metrics…"):
            metrics = compute_performance_metrics(df, holdings_df)
        st.session_state[metrics_key] = metrics
        st.session_state["performance_metrics"] = metrics  # share with Tab 4
    else:
        metrics = st.session_state[metrics_key]
        st.session_state["performance_metrics"] = metrics

    # ── Key metrics ───────────────────────────────────────────────────────────
    st.subheader("Lifetime Portfolio Metrics")

    r1c1, r1c2, r1c3 = st.columns(3)
    r1c1.metric(
        "💸 Total Invested",
        f"${metrics['total_investment']:,.2f}",
        help="Sum of all Buy transaction values (qty × price)",
    )
    r1c2.metric(
        "💵 Total Sell Proceeds",
        f"${metrics['total_sell_proceeds']:,.2f}",
        help="Sum of all Sell transaction values",
    )
    r1c3.metric(
        "📦 Current Portfolio Value",
        f"${metrics['current_portfolio_value']:,.2f}",
        help="Market value of open positions using latest available prices",
    )

    st.write("")  # spacing

    r2c1, r2c2, r2c3 = st.columns(3)

    ret_d = metrics["total_return_dollars"]
    ret_p = metrics["total_return_pct"]
    r2c1.metric(
        "📊 Total Return",
        f"${ret_d:+,.2f}",
        delta=f"{ret_p:+.2f}%",
        help="Sell Proceeds + Current Value − Total Invested",
    )

    real_pnl = metrics.get("realized_pnl", 0)
    r2c2.metric(
        "✅ Realised P&L",
        f"${real_pnl:+,.2f}",
        help="Profit/loss from fully closed lots (FIFO)",
    )

    xirr = metrics.get("xirr")
    if xirr is not None:
        xirr_label = f"{xirr:+.2f}%"
        xirr_delta = "annualised"
    else:
        xirr_label = "N/A"
        xirr_delta = "Insufficient data"
    r2c3.metric(
        "📐 XIRR",
        xirr_label,
        delta=xirr_delta,
        help=(
            "Extended IRR — time-weighted annualised return accounting for "
            "irregular cashflow dates. Buys = outflows, Sells + Current Value = inflows."
        ),
    )

    st.divider()

    # ── Cumulative net cash flow ───────────────────────────────────────────────
    st.subheader("Cumulative Net Cash Flow")
    st.caption(
        "Negative = net capital deployed; positive = net cash recovered via sells. "
        "Does **not** include current open-position value."
    )

    cf = (
        df.assign(
            cf=df.apply(
                lambda r: -(r["quantity"] * r["price"])
                if r["transaction_type"].lower() == "buy"
                else (r["quantity"] * r["price"]),
                axis=1,
            )
        )
        .groupby("date")["cf"]
        .sum()
        .cumsum()
        .reset_index(name="cumulative_cf")
    )
    cf.columns = ["Date", "Cumulative Net CF ($)"]

    final_val = float(cf["Cumulative Net CF ($)"].iloc[-1])
    line_color = _POS_COLOR if final_val >= 0 else _NEG_COLOR
    fill_color = "rgba(5,150,105,0.10)" if final_val >= 0 else "rgba(220,38,38,0.10)"

    fig_cf = go.Figure()
    fig_cf.add_trace(
        go.Scatter(
            x=cf["Date"],
            y=cf["Cumulative Net CF ($)"],
            mode="lines",
            name="Net Cash Flow",
            line=dict(color=line_color, width=2.5),
            fill="tozeroy",
            fillcolor=fill_color,
            hovertemplate="%{x|%b %d, %Y}<br>$%{y:,.2f}<extra></extra>",
        )
    )
    fig_cf.add_hline(y=0, line_dash="dot", line_color="#94A3B8", opacity=0.6)
    fig_cf.update_layout(
        **_CHART_BASE,
        xaxis=dict(**_AXIS, title="Date"),
        yaxis=dict(**_AXIS, tickformat="$,.0f"),
        hovermode="x unified",
        margin=dict(t=20, b=40, l=70, r=20),
        height=320,
    )
    st.plotly_chart(fig_cf, use_container_width=True)

    st.divider()

    # ── Monthly buy vs sell ────────────────────────────────────────────────────
    col_bar, col_pnl = st.columns(2, gap="large")

    with col_bar:
        st.subheader("Monthly Activity")
        activity = (
            df.assign(
                value=df["quantity"] * df["price"],
                month=df["date"].dt.to_period("M").dt.to_timestamp(),
            )
            .groupby(["month", "transaction_type"])["value"]
            .sum()
            .reset_index()
        )

        fig_bar = go.Figure()
        for tx_type, color in [("Buy", _BUY_COLOR), ("Sell", _SELL_COLOR)]:
            sub = activity[activity["transaction_type"].str.capitalize() == tx_type]
            fig_bar.add_trace(
                go.Bar(
                    x=sub["month"],
                    y=sub["value"],
                    name=tx_type,
                    marker_color=color,
                    marker_line=dict(width=0),
                    hovertemplate=f"{tx_type}<br>%{{x|%b %Y}}<br>$%{{y:,.2f}}<extra></extra>",
                )
            )
        fig_bar.update_layout(
            **_CHART_BASE,
            xaxis=dict(**_AXIS),
            yaxis=dict(**_AXIS, tickformat="$,.0f"),
            barmode="group",
            bargap=0.25,
            hovermode="x unified",
            legend=dict(orientation="h", y=1.08, font=dict(size=12)),
            margin=dict(t=20, b=40, l=70, r=20),
            height=320,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_pnl:
        st.subheader("Realised P&L by Ticker")
        fifo = compute_fifo_holdings(df)
        pnl_rows = [
            {"Ticker": t, "Realised P&L ($)": round(v["realized_pnl"], 2)}
            for t, v in fifo.items()
            if abs(v["realized_pnl"]) > 0.01
        ]
        if pnl_rows:
            pnl_df = pd.DataFrame(pnl_rows).sort_values("Realised P&L ($)")
            colors = [
                _NEG_COLOR if v < 0 else _POS_COLOR for v in pnl_df["Realised P&L ($)"]
            ]
            fig_pnl = go.Figure(
                go.Bar(
                    x=pnl_df["Realised P&L ($)"],
                    y=pnl_df["Ticker"],
                    orientation="h",
                    marker_color=colors,
                    marker_line=dict(width=0),
                    hovertemplate="%{y}<br>$%{x:,.2f}<extra></extra>",
                )
            )
            fig_pnl.add_vline(x=0, line_dash="dot", line_color="#94A3B8", opacity=0.6)
            fig_pnl.update_layout(
                **_CHART_BASE,
                xaxis=dict(**_AXIS, tickformat="$,.0f"),
                yaxis=dict(**_AXIS),
                margin=dict(t=20, b=40, l=60, r=20),
                height=320,
            )
            st.plotly_chart(fig_pnl, use_container_width=True)
        else:
            st.info(
                "No realised P&L yet — no positions have been fully or partially closed."
            )

    # ── Download ──────────────────────────────────────────────────────────────
    summary_rows = [
        {"Metric": k.replace("_", " ").title(), "Value": v} for k, v in metrics.items()
    ]
    st.download_button(
        "⬇️ Download performance summary CSV",
        data=pd.DataFrame(summary_rows).to_csv(index=False),
        file_name="performance_summary.csv",
        mime="text/csv",
    )
