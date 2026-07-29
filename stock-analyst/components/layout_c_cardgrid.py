"""
Layout C — Card-Grid Feed
Matches CardGrid.tsx: #F9F8F6 warm background, white cards with shadows,
slate-900 header bar, 4 KPI cards, SVG donut, CSS bar chart, orange AI card.
"""
from __future__ import annotations
import math
import streamlit as st
import pandas as pd

from utils.data_processing import load_and_validate_csv, get_display_df
from utils.portfolio_math import build_holdings_table, compute_performance_metrics, compute_fifo_holdings
from utils.llm_agent import get_portfolio_summary, stream_chat_response

_COLORS = ["#10b981","#0ea5e9","#3b82f6","#8b5cf6","#d946ef","#f43f5e","#f97316","#eab308"]

_BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
#MainMenu, footer, header { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.main .block-container { padding: 1.5rem 2rem !important; max-width: 1400px !important; }
body, .stApp { background: #F9F8F6 !important; font-family: 'Inter', sans-serif !important; }
.modebar { display: none !important; }
/* Card style for st.container */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
    background: white;
}
</style>
"""

SUGGESTED_QUESTIONS = [
    "Summarise my overall trading performance",
    "Which stock has the best unrealised return?",
    "What is my biggest concentration risk?",
    "How does my XIRR compare to S&P 500?",
    "Which trades have been most profitable?",
    "Am I over-exposed to any single sector?",
]


def _card(content_html: str, extra_style: str = "") -> str:
    return f"""
<div style="background:white;border-radius:12px;border:1px solid rgba(226,232,240,0.6);
     box-shadow:0 1px 3px rgba(0,0,0,0.04),0 1px 2px rgba(0,0,0,0.02);
     padding:20px;{extra_style}">{content_html}</div>"""


def _kpi_card(icon: str, label: str, value: str, sub: str = "", color: str = "#0f172a") -> str:
    return f"""
<div style="background:white;border-radius:12px;border:1px solid rgba(226,232,240,0.6);
     box-shadow:0 1px 3px rgba(0,0,0,0.04);padding:20px;display:flex;flex-direction:column;justify-content:space-between;min-height:120px">
  <div style="display:flex;align-items:center;gap:6px;color:#64748b;margin-bottom:8px">
    <span style="font-size:0.9rem">{icon}</span>
    <span style="font-size:0.82rem;font-weight:500">{label}</span>
  </div>
  <div>
    <div style="font-size:1.75rem;font-weight:700;color:{color};letter-spacing:-0.02em;line-height:1">{value}</div>
    {f'<div style="font-size:0.82rem;color:{color};font-weight:600;margin-top:4px">{sub}</div>' if sub else ''}
  </div>
</div>"""


def _svg_donut(slices: list) -> str:
    r, cx, cy = 40, 50, 50
    circ = 2 * math.pi * r
    parts, offset = [], 0.0
    for i, s in enumerate(slices):
        pct = s["pct"]
        color = _COLORS[i % len(_COLORS)]
        dash = pct / 100 * circ
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="transparent" '
            f'stroke="{color}" stroke-width="20" '
            f'stroke-dasharray="{dash:.2f} {circ:.2f}" '
            f'stroke-dashoffset="{-offset:.2f}" />'
        )
        offset += dash
    circles = "".join(parts)
    return f"""
<div style="position:relative;width:180px;height:180px;margin:0 auto">
  <svg viewBox="0 0 100 100" style="transform:rotate(-90deg);width:100%;height:100%">
    {circles}
  </svg>
  <div style="position:absolute;inset:0;display:flex;flex-direction:column;
       align-items:center;justify-content:center">
    <span style="font-size:1.4rem;font-weight:700;color:#1e293b">{len(slices)}</span>
    <span style="font-size:0.65rem;font-weight:600;color:#94a3b8;text-transform:uppercase;
          letter-spacing:0.08em">Tickers</span>
  </div>
</div>"""


def _bar_chart_html(items: list) -> str:
    """CSS horizontal bar chart for P&L by ticker."""
    if not items:
        return '<div style="color:#94a3b8;font-size:0.85rem;padding:12px 0">No realised P&L data yet.</div>'
    max_abs = max(abs(x["value"]) for x in items) or 1
    rows = ""
    for item in items:
        v = item["value"]
        pct = abs(v) / max_abs * 100
        color = "#10b981" if v >= 0 else "#f43f5e"
        label_color = "#059669" if v >= 0 else "#dc2626"
        val_str = f"${v:+,.0f}"
        rows += f"""
<div style="margin-bottom:12px">
  <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:5px">
    <span style="font-weight:600;color:#334155">{item['ticker']}</span>
    <span style="font-weight:600;color:{label_color}">{val_str}</span>
  </div>
  <div style="width:100%;background:#f1f5f9;height:10px;border-radius:999px;overflow:hidden">
    <div style="height:100%;width:{pct:.1f}%;background:{color};border-radius:999px"></div>
  </div>
</div>"""
    return rows


def render_layout_c() -> None:
    st.markdown(_BASE_CSS, unsafe_allow_html=True)

    # ── Row 1: Top bar ────────────────────────────────────────────────────────
    has_data = "transactions_df" in st.session_state
    df = st.session_state.get("transactions_df", pd.DataFrame())
    status_text = (
        f"Portfolio loaded · {df['ticker'].nunique()} tickers · {len(df):,} transactions"
        if has_data else "No portfolio loaded — upload a CSV to get started"
    )

    hcol1, hcol2 = st.columns([3, 1])
    with hcol1:
        st.markdown(f"""
<div style="background:white;border-radius:12px;border:1px solid rgba(226,232,240,0.6);
     box-shadow:0 1px 3px rgba(0,0,0,0.04);padding:14px 20px;display:flex;align-items:center;gap:12px">
  <div style="background:#0f172a;border-radius:8px;padding:7px;display:flex;align-items:center;
       justify-content:center;font-size:1rem">💼</div>
  <div>
    <div style="font-weight:700;font-size:1rem;color:#0f172a;letter-spacing:-0.01em">Portfolio Analyst</div>
    <div style="font-size:0.8rem;color:#64748b">{status_text}</div>
  </div>
</div>""", unsafe_allow_html=True)
    with hcol2:
        try:
            with open("sample_portfolio.csv", "rb") as f:
                st.download_button("⬇️ Sample CSV", f.read(), "sample_portfolio.csv",
                                   "text/csv", use_container_width=True, key="c_dl")
        except FileNotFoundError:
            pass
        if has_data and st.button("🗑️ Clear", key="c_clear2", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Upload card ───────────────────────────────────────────────────────────
    with st.expander("📂 Upload / Replace Transaction CSV", expanded=not has_data):
        up_col1, up_col2 = st.columns([3, 1])
        with up_col1:
            st.caption("Required columns: **ticker · date · transaction_type · quantity · price**")
            uploaded = st.file_uploader("CSV", type=["csv"], key="c_uploader",
                                        label_visibility="collapsed")
        with up_col2:
            st.markdown(" ")

        if uploaded:
            result = load_and_validate_csv(uploaded)
            for err in result.errors:
                st.error(f"❌ {err}")
            if result.ok:
                for w in result.warnings:
                    st.warning(f"⚠️ {w}")
                df_new = result.df
                prev = st.session_state.get("transactions_df")
                if prev is None or not prev.equals(df_new):
                    st.session_state["transactions_df"] = df_new
                    for k in ("holdings_df", "performance_metrics"):
                        st.session_state.pop(k, None)
                st.success(f"✅ {len(df_new):,} transactions loaded · {df_new['ticker'].nunique()} tickers")
                st.rerun()

    if not has_data:
        return

    df = st.session_state["transactions_df"]

    # Fetch holdings
    with st.spinner("Fetching current prices…"):
        holdings_df = build_holdings_table(df)
    st.session_state["holdings_df"] = holdings_df

    total_val = float(holdings_df["Current Value"].dropna().sum())
    cost = float(holdings_df["Cost Basis"].sum())
    unreal = total_val - cost
    unreal_pct = unreal / cost * 100 if cost > 0 else 0.0

    # Compute full metrics
    metrics_key = f"perf_metrics_{hash(df.to_json())}"
    if metrics_key not in st.session_state and not holdings_df.empty:
        with st.spinner("Computing metrics…"):
            metrics = compute_performance_metrics(df, holdings_df)
        st.session_state[metrics_key] = metrics
        st.session_state["performance_metrics"] = metrics
    metrics = st.session_state.get(metrics_key, {})
    xirr = metrics.get("xirr")
    realized = metrics.get("realized_pnl", 0)

    # ── Row 2: 4 KPI cards ────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(_kpi_card("💰", "Portfolio Value", f"${total_val:,.0f}"), unsafe_allow_html=True)
    k2.markdown(_kpi_card("📦", "Cost Basis", f"${cost:,.0f}"), unsafe_allow_html=True)

    unreal_color = "#059669" if unreal >= 0 else "#dc2626"
    k3.markdown(_kpi_card("📈", "Unrealized P&L",
                          f"${unreal:+,.0f}", f"{unreal_pct:+.1f}%", unreal_color),
                unsafe_allow_html=True)

    xirr_color = "#059669" if (xirr or 0) >= 0 else "#dc2626"
    xirr_str = f"{xirr:+.1f}%" if xirr is not None else "N/A"
    k4.markdown(_kpi_card("📐", "XIRR (Annualized)", xirr_str,
                          "Since first trade", xirr_color if xirr else "#64748b"),
                unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Row 3: Donut (5 cols) + Holdings table (7 cols) ───────────────────────
    if not holdings_df.empty:
        col_donut, col_table = st.columns([5, 7], gap="medium")

        with col_donut:
            pie_df = holdings_df[["Ticker", "Current Value"]].dropna().copy()
            pie_df["pct"] = (pie_df["Current Value"] / pie_df["Current Value"].sum() * 100).round(0).astype(int)
            slices = pie_df.rename(columns={"Ticker": "ticker"}).to_dict("records")

            legend_dots = "".join([
                f'<div style="display:flex;align-items:center;gap:5px;font-size:0.8rem">'
                f'<div style="width:9px;height:9px;border-radius:50%;background:{_COLORS[i % len(_COLORS)]};flex-shrink:0"></div>'
                f'<span style="font-weight:600;color:#334155">{r["ticker"]}</span>'
                f'<span style="color:#94a3b8">{r["pct"]}%</span></div>'
                for i, r in enumerate(slices)
            ])

            st.markdown(_card(f"""
<div style="display:flex;align-items:center;gap:6px;margin-bottom:16px">
  <span style="font-size:1rem">🥧</span>
  <h3 style="font-size:0.9rem;font-weight:700;color:#1e293b;margin:0">Allocation</h3>
</div>
{_svg_donut(slices)}
<div style="display:flex;flex-wrap:wrap;gap:8px 16px;justify-content:center;margin-top:16px">
  {legend_dots}
</div>
"""), unsafe_allow_html=True)

        with col_table:
            # Styled HTML holdings table
            rows_html = ""
            for _, r in holdings_df.iterrows():
                t = r["Ticker"]
                qty = r.get("Quantity", 0) or 0
                avg = r.get("Avg Cost (FIFO)", 0) or 0
                val = r.get("Current Value", 0) or 0
                pl_d = r.get("Unrealized Gain ($)", 0) or 0
                pl_p = r.get("Unrealized Gain (%)", 0) or 0
                pl_color = "#059669" if pl_d >= 0 else "#dc2626"
                pl_str = f"${pl_d:+,.0f} ({pl_p:+.1f}%)"
                rows_html += f"""
<tr style="border-bottom:1px solid #f8fafc">
  <td style="padding:9px 12px;font-weight:700;color:#0f172a;font-size:0.85rem">{t}</td>
  <td style="padding:9px 12px;text-align:right;font-size:0.83rem;color:#475569">{qty:,.2f}</td>
  <td style="padding:9px 12px;text-align:right;font-size:0.83rem;color:#64748b">${avg:,.2f}</td>
  <td style="padding:9px 12px;text-align:right;font-weight:600;font-size:0.83rem;color:#0f172a">${val:,.0f}</td>
  <td style="padding:9px 12px;text-align:right;font-weight:600;font-size:0.83rem;color:{pl_color}">{pl_str}</td>
</tr>"""

            st.markdown(_card(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
  <div style="display:flex;align-items:center;gap:6px">
    <span style="font-size:1rem">💼</span>
    <h3 style="font-size:0.9rem;font-weight:700;color:#1e293b;margin:0">Holdings</h3>
  </div>
</div>
<div style="overflow-x:auto">
<table style="width:100%;border-collapse:collapse">
  <thead>
    <tr style="border-bottom:1px solid #f1f5f9">
      <th style="padding:6px 12px;text-align:left;font-size:0.72rem;font-weight:600;color:#94a3b8">Ticker</th>
      <th style="padding:6px 12px;text-align:right;font-size:0.72rem;font-weight:600;color:#94a3b8">Shares</th>
      <th style="padding:6px 12px;text-align:right;font-size:0.72rem;font-weight:600;color:#94a3b8">Avg Cost</th>
      <th style="padding:6px 12px;text-align:right;font-size:0.72rem;font-weight:600;color:#94a3b8">Market Value</th>
      <th style="padding:6px 12px;text-align:right;font-size:0.72rem;font-weight:600;color:#94a3b8">Unrealized P&amp;L</th>
    </tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
"""), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Row 4: P&L bar chart + AI summary ─────────────────────────────────────
    col_chart, col_ai = st.columns([7, 5], gap="medium")

    with col_chart:
        fifo = compute_fifo_holdings(df)
        pnl_items = sorted(
            [{"ticker": t, "value": v["realized_pnl"]}
             for t, v in fifo.items() if abs(v["realized_pnl"]) > 0.01],
            key=lambda x: x["value"], reverse=True
        )

        # Also add unrealized P&L items if no realized
        if not pnl_items:
            pnl_items = sorted(
                [{"ticker": r["Ticker"], "value": r.get("Unrealized Gain ($)", 0) or 0}
                 for _, r in holdings_df.iterrows()],
                key=lambda x: x["value"], reverse=True
            )
            chart_label = "Unrealized P&L"
        else:
            chart_label = "Realized P&L"

        bar_html = _bar_chart_html(pnl_items)

        st.markdown(_card(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
  <div style="display:flex;align-items:center;gap:6px">
    <span style="font-size:1rem">📊</span>
    <h3 style="font-size:0.9rem;font-weight:700;color:#1e293b;margin:0">P&L by Asset</h3>
  </div>
  <span style="font-size:0.72rem;font-weight:600;color:#64748b;background:#f1f5f9;
       padding:3px 8px;border-radius:6px">{chart_label}</span>
</div>
{bar_html}
"""), unsafe_allow_html=True)

    with col_ai:
        cache_key = f"c_ai_{hash(holdings_df.to_json())}"
        partial = {
            "total_investment": cost, "current_portfolio_value": total_val,
            "total_return_dollars": unreal, "total_return_pct": unreal_pct,
            "realized_pnl": realized, "total_sell_proceeds": metrics.get("total_sell_proceeds", 0),
            "xirr": xirr,
        }
        if cache_key not in st.session_state:
            with st.spinner("Analysing with Groq…"):
                st.session_state[cache_key] = get_portfolio_summary(holdings_df, partial)
        summary = st.session_state[cache_key]

        st.markdown(f"""
<div style="background:linear-gradient(180deg,#fff7ed 0%,white 100%);border-radius:12px;
     border:1px solid #fed7aa;box-shadow:0 1px 3px rgba(0,0,0,0.04);padding:20px;height:100%">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
    <div style="display:flex;align-items:center;gap:8px">
      <div style="background:#f97316;border-radius:6px;padding:5px;font-size:0.8rem">🤖</div>
      <span style="font-size:0.9rem;font-weight:700;color:#7c2d12">AI Analysis</span>
      <span style="font-size:0.65rem;font-weight:800;color:#ea580c;background:#ffedd5;
            padding:2px 5px;border-radius:4px;letter-spacing:0.05em;text-transform:uppercase">Groq</span>
    </div>
  </div>
  <div style="font-size:0.85rem;color:#44403c;line-height:1.65">
    {summary}
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh AI", key="c_refresh_ai2", use_container_width=True):
            st.session_state.pop(cache_key, None)
            st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── AI Chat card ──────────────────────────────────────────────────────────
    st.markdown(_card("""
<div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
  <span style="font-size:1.1rem">🤖</span>
  <h3 style="font-size:0.9rem;font-weight:700;color:#1e293b;margin:0">AI Analyst Chat</h3>
</div>"""), unsafe_allow_html=True)

    st.markdown("**💡 Suggested:**")
    qcols = st.columns(3)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        if qcols[i % 3].button(q, key=f"cq2_{i}", use_container_width=True):
            st.session_state.setdefault("chat_c2", [])
            st.session_state["_c2_pending"] = q

    if "chat_c2" not in st.session_state:
        st.session_state["chat_c2"] = []
    for msg in st.session_state["chat_c2"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if "_c2_pending" in st.session_state:
        p = st.session_state.pop("_c2_pending")
        _do_chat(p, df, holdings_df, metrics, "chat_c2")
        st.rerun()

    user_input = st.chat_input("Ask anything about your portfolio…", key="c2_input")
    if user_input:
        _do_chat(user_input, df, holdings_df, metrics, "chat_c2")

    if st.session_state.get("chat_c2"):
        if st.button("🗑️ Clear chat", key="c2_clear_chat"):
            st.session_state["chat_c2"] = []
            st.rerun()


def _do_chat(text: str, df, holdings_df, metrics, key: str) -> None:
    st.session_state[key].append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.markdown(text)
    history = list(st.session_state[key])
    with st.chat_message("assistant"):
        try:
            r = st.write_stream(stream_chat_response(history, holdings_df, metrics, df=df))
        except Exception as e:
            r = f"⚠️ {e}"
            st.markdown(r)
    st.session_state[key].append({"role": "assistant", "content": r or ""})
