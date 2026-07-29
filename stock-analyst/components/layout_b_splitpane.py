"""
Layout B — Command Center (Split Pane)
Matches SplitPane.tsx: dark slate-950 top bar, dark slate-900 sidebar,
white detail panel, metrics row, sparkline, amber AI insight strip.
"""
from __future__ import annotations
import math
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.data_processing import load_and_validate_csv
from utils.portfolio_math import build_holdings_table, compute_fifo_holdings
from utils.llm_agent import stream_chat_response

_COLORS = ["#6366f1","#3b82f6","#0ea5e9","#06b6d4","#14b8a6","#10b981","#f59e0b","#ef4444"]

_BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
#MainMenu, footer, header { display: none !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }
body, .stApp { background: #f1f5f9 !important; font-family: 'Inter', sans-serif !important; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stMetric"] {
    background: transparent !important;
    border: none !important;
    border-right: 1px solid #e2e8f0 !important;
    border-radius: 0 !important;
    padding: 20px 24px !important;
    box-shadow: none !important;
}
[data-testid="stMetricLabel"] { font-size: 0.68rem !important; font-weight: 700 !important; color: #64748b !important;
    text-transform: uppercase !important; letter-spacing: 0.06em !important; }
[data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 800 !important; color: #0f172a !important; }
.modebar { display: none !important; }
</style>
"""

SUGGESTED_QUESTIONS = [
    "Summarise my overall trading performance",
    "Which stock has the best unrealised return?",
    "What is my biggest concentration risk?",
    "How does my XIRR compare to S&P 500?",
]


def _sidebar_item_html(ticker: str, value: float, alloc_pct: float, pl_pct: float, selected: bool) -> str:
    bg = "background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.3);box-shadow:inset 2px 0 0 #6366f1;" if selected else "border:1px solid transparent;"
    name_color = "#a5b4fc" if selected else "#cbd5e1"
    val_color = "white" if selected else "#94a3b8"
    pl_bg = "rgba(52,211,153,0.2)" if pl_pct >= 0 else "rgba(248,113,113,0.2)"
    pl_color = "#34d399" if pl_pct >= 0 else "#f87171"
    pl_str = f"{'+' if pl_pct >= 0 else ''}{pl_pct:.1f}%"
    bar_w = min(100, abs(alloc_pct))
    bar_color = "#6366f1" if selected else "#475569"
    return f"""
<div style="padding:10px 12px;border-radius:8px;margin-bottom:4px;cursor:pointer;{bg}">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px">
    <span style="font-weight:700;font-size:0.88rem;color:{name_color}">{ticker}</span>
    <span style="font-size:0.85rem;font-weight:600;color:{val_color}">${value:,.0f}</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px">
    <div style="flex:1;height:4px;background:#1e293b;border-radius:2px;overflow:hidden">
      <div style="height:100%;width:{bar_w:.0f}%;background:{bar_color};border-radius:2px"></div>
    </div>
    <span style="font-size:9px;color:#64748b;min-width:28px">{alloc_pct:.0f}%</span>
    <span style="font-size:0.72rem;font-weight:600;background:{pl_bg};color:{pl_color};
          padding:2px 6px;border-radius:4px">{pl_str}</span>
  </div>
</div>"""


def _metric_box(label: str, value: str, color: str = "#0f172a") -> str:
    return f"""
<div style="padding:20px 24px;border-right:1px solid #e2e8f0;flex:1">
  <div style="font-size:0.68rem;font-weight:700;color:#64748b;text-transform:uppercase;
       letter-spacing:0.06em;margin-bottom:8px">{label}</div>
  <div style="font-size:1.6rem;font-weight:800;color:{color};letter-spacing:-0.02em">{value}</div>
</div>"""


def _sparkline_svg() -> str:
    """Decorative sparkline SVG."""
    return """
<svg width="100%" height="120" viewBox="0 0 600 120" preserveAspectRatio="none"
     style="display:block">
  <defs>
    <linearGradient id="sg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#6366f1" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#6366f1" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <path d="M0,100 C40,85 80,110 120,105 C160,100 200,65 240,70 C280,75 320,30 360,38
           C400,46 440,14 480,20 C520,26 560,8 600,0 L600,120 L0,120 Z"
        fill="url(#sg)"/>
  <path d="M0,100 C40,85 80,110 120,105 C160,100 200,65 240,70 C280,75 320,30 360,38
           C400,46 440,14 480,20 C520,26 560,8 600,0"
        fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="600" cy="0" r="4" fill="white" stroke="#6366f1" stroke-width="2.5"/>
</svg>"""


def render_layout_b() -> None:
    st.markdown(_BASE_CSS, unsafe_allow_html=True)

    if "transactions_df" not in st.session_state:
        _no_data_screen()
        return

    df = st.session_state["transactions_df"]
    with st.spinner(""):
        holdings_df = build_holdings_table(df)
    st.session_state["holdings_df"] = holdings_df

    total_val = float(holdings_df["Current Value"].dropna().sum())
    cost_b = float(holdings_df["Cost Basis"].sum())
    unreal = total_val - cost_b
    unreal_pct = unreal / cost_b * 100 if cost_b > 0 else 0.0
    delta_str = f"{'+' if unreal_pct >= 0 else ''}{unreal_pct:.1f}%"

    # ── Top bar ───────────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="height:40px;background:#020617;border-bottom:1px solid #1e293b;display:flex;
     align-items:center;justify-content:space-between;padding:0 16px;font-family:'Inter',sans-serif">
  <div style="display:flex;align-items:center;gap:8px">
    <span style="color:#818cf8;font-size:0.9rem">📈</span>
    <span style="font-size:0.85rem;font-weight:600;color:white">Portfolio Analyst</span>
  </div>
  <div style="display:flex;align-items:center;gap:6px;font-size:0.82rem;color:#94a3b8">
    <span>{df['ticker'].nunique()} holdings</span>
    <span>·</span>
    <span style="color:white;font-weight:600">${total_val:,.2f}</span>
    <span style="color:#34d399;font-size:0.72rem;display:flex;align-items:center;gap:2px">↑ {delta_str}</span>
  </div>
  <div style="display:flex;align-items:center;gap:16px;font-size:0.78rem;color:#64748b">
    <span>💬 AI Chat</span>
    <span>📈 Performance</span>
    <span>⚙️</span>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Body: sidebar + detail ─────────────────────────────────────────────────
    left, right = st.columns([1, 3], gap="small")

    # Get selected ticker from state
    tickers_list = sorted(holdings_df["Ticker"].tolist())
    sel = st.session_state.get("b_selected", tickers_list[0] if tickers_list else None)

    with left:
        # Dark sidebar
        sidebar_items = ""
        for _, r in holdings_df.iterrows():
            t = r["Ticker"]
            val = r.get("Current Value", 0) or 0
            pct = val / total_val * 100 if total_val > 0 else 0
            pl = r.get("Unrealized Gain (%)", 0) or 0
            sidebar_items += _sidebar_item_html(t, val, pct, pl, t == sel)

        st.markdown(f"""
<div style="background:#0f172a;border-radius:8px;height:calc(100vh - 80px);
     display:flex;flex-direction:column;overflow:hidden">
  <div style="padding:12px 16px;font-size:0.7rem;font-weight:700;color:#64748b;
       text-transform:uppercase;letter-spacing:0.08em;border-bottom:1px solid #1e293b;
       display:flex;justify-content:space-between;align-items:center">
    <span>Holdings</span><span>📂</span>
  </div>
  <div style="flex:1;overflow-y:auto;padding:8px">
    {sidebar_items}
  </div>
  <div style="padding:16px;background:#020617;border-top:1px solid #1e293b;margin-top:auto">
    <div style="font-size:0.72rem;font-weight:600;color:#64748b;margin-bottom:4px">Portfolio Value</div>
    <div style="font-size:1.4rem;font-weight:900;color:white;letter-spacing:-0.02em">${total_val:,.2f}</div>
    <div style="font-size:0.82rem;font-weight:600;color:#34d399;display:flex;align-items:center;gap:4px;margin-top:2px">
      ↑ ${unreal:+,.0f} ({unreal_pct:+.1f}%) All Time
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        # Ticker radio (invisible — just for state)
        new_sel = st.radio("Select ticker", tickers_list,
                           label_visibility="collapsed", key="b_selected",
                           index=tickers_list.index(sel) if sel in tickers_list else 0)

    with right:
        _render_detail(new_sel, df, holdings_df, total_val)


def _render_detail(ticker: str, df: pd.DataFrame, holdings_df: pd.DataFrame, total_val: float) -> None:
    row = holdings_df[holdings_df["Ticker"] == ticker]
    if row.empty:
        st.warning(f"No data for {ticker}")
        return
    r = row.iloc[0]
    val = r.get("Current Value", 0) or 0
    cost_b = r.get("Cost Basis", 0) or 0
    price = r.get("Current Price", 0) or 0
    avg = r.get("Avg Cost (FIFO)", 0) or 0
    qty = r.get("Quantity", 0) or 0
    unreal_d = r.get("Unrealized Gain ($)", 0) or 0
    unreal_p = r.get("Unrealized Gain (%)", 0) or 0
    pct_of_port = val / total_val * 100 if total_val > 0 else 0
    pnl_color = "#059669" if unreal_d >= 0 else "#dc2626"

    # Detail header
    st.markdown(f"""
<div style="background:white;border-bottom:1px solid #e2e8f0;padding:20px 24px;
     display:flex;justify-content:space-between;align-items:flex-end">
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px">
      <h1 style="font-size:1.8rem;font-weight:900;color:#0f172a;margin:0;letter-spacing:-0.03em">{ticker}</h1>
    </div>
    <div style="display:flex;align-items:baseline;gap:10px">
      <span style="font-size:1.6rem;font-weight:800;color:#1e293b;letter-spacing:-0.02em">${price:,.2f}</span>
      <span style="background:#f0fdf4;border:1px solid #bbf7d0;color:#15803d;font-size:0.82rem;
            font-weight:700;padding:4px 10px;border-radius:6px">↑ current price</span>
    </div>
  </div>
  <div style="display:flex;gap:8px">
    <button style="padding:7px 14px;font-size:0.82rem;font-weight:700;border:1px solid #e2e8f0;
            border-radius:8px;background:white;color:#334155;cursor:pointer">Trade</button>
    <button style="padding:7px 14px;font-size:0.82rem;font-weight:700;border:none;
            border-radius:8px;background:#4338ca;color:white;cursor:pointer">Analyze</button>
  </div>
</div>""", unsafe_allow_html=True)

    # 4-metric row
    pnl_val_color = "#059669" if unreal_d >= 0 else "#dc2626"
    st.markdown(f"""
<div style="background:white;border-bottom:1px solid #e2e8f0;display:flex">
  {_metric_box("Shares Held", f"{qty:,.4f}")}
  {_metric_box("Avg Cost (FIFO)", f"${avg:,.2f}")}
  {_metric_box("Unrealized P&L", f"${unreal_d:+,.2f}", pnl_val_color)}
  {_metric_box("Portfolio Weight", f"{pct_of_port:.1f}%")}
</div>""", unsafe_allow_html=True)

    # Main detail area
    col_chart, col_sidebar = st.columns([3, 2], gap="medium")

    with col_chart:
        # Ticker transaction bar chart
        ticker_df = df[df["ticker"] == ticker].copy()
        buys = ticker_df[ticker_df["transaction_type"].str.lower() == "buy"]
        sells = ticker_df[ticker_df["transaction_type"].str.lower() == "sell"]

        st.markdown("""
<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:16px;
     box-shadow:0 1px 3px rgba(0,0,0,0.04);margin-top:12px">
  <div style="font-size:0.85rem;font-weight:700;color:#0f172a;margin-bottom:4px">Transaction History</div>
""", unsafe_allow_html=True)

        fig = go.Figure()
        if not buys.empty:
            fig.add_trace(go.Bar(x=buys["date"], y=buys["quantity"] * buys["price"],
                                 name="Buy", marker_color="#6366f1",
                                 hovertemplate="%{x|%b %d}<br>$%{y:,.0f}<extra>Buy</extra>"))
        if not sells.empty:
            fig.add_trace(go.Bar(x=sells["date"], y=sells["quantity"] * sells["price"],
                                 name="Sell", marker_color="#f97316",
                                 hovertemplate="%{x|%b %d}<br>$%{y:,.0f}<extra>Sell</extra>"))
        fig.update_layout(barmode="group", height=200,
                          plot_bgcolor="white", paper_bgcolor="white",
                          margin=dict(t=10, b=30, l=50, r=10),
                          yaxis=dict(tickformat="$,.0f", gridcolor="#f1f5f9"),
                          xaxis=dict(gridcolor="transparent"),
                          legend=dict(orientation="h", y=1.1, font_size=11))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # AI insight strip (amber)
        metrics = st.session_state.get("performance_metrics", {})
        cache_key = f"b_ai_{ticker}_{hash(str(val))}"
        if cache_key not in st.session_state:
            ai_text = f"**{ticker}** represents **{pct_of_port:.1f}%** of your portfolio with an unrealized P&L of **${unreal_d:+,.0f}** ({unreal_p:+.1f}%). Your FIFO avg cost of **${avg:,.2f}** vs current **${price:,.2f}** shows {'a favorable' if unreal_d >= 0 else 'an unfavorable'} position."
            st.session_state[cache_key] = ai_text
        ai_text = st.session_state[cache_key]

        st.markdown(f"""
<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px 16px;
     display:flex;align-items:flex-start;gap:12px;margin-top:12px">
  <div style="background:#fef3c7;border:1px solid #fcd34d;border-radius:8px;padding:6px;
       color:#d97706;flex-shrink:0">✨</div>
  <div>
    <div style="font-size:0.82rem;font-weight:800;color:#92400e;margin-bottom:4px">AI Insight — {ticker}</div>
    <div style="font-size:0.83rem;color:#78350f;line-height:1.55">{ai_text}</div>
  </div>
</div>""", unsafe_allow_html=True)

    with col_sidebar:
        fifo = compute_fifo_holdings(df)
        real_pnl = fifo.get(ticker, {}).get("realized_pnl", 0)

        st.markdown(f"""
<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:16px;
     box-shadow:0 1px 3px rgba(0,0,0,0.04);margin-top:12px">
  <div style="font-size:0.82rem;font-weight:700;color:#0f172a;margin-bottom:12px">Position Summary</div>
  <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f1f5f9">
    <span style="font-size:0.82rem;color:#64748b">Market Value</span>
    <span style="font-size:0.82rem;font-weight:700;color:#0f172a">${val:,.2f}</span>
  </div>
  <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f1f5f9">
    <span style="font-size:0.82rem;color:#64748b">Cost Basis</span>
    <span style="font-size:0.82rem;font-weight:700;color:#0f172a">${cost_b:,.2f}</span>
  </div>
  <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f1f5f9">
    <span style="font-size:0.82rem;color:#64748b">Unrealized P&L</span>
    <span style="font-size:0.82rem;font-weight:700;color:{pnl_color}">${unreal_d:+,.2f}</span>
  </div>
  <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f1f5f9">
    <span style="font-size:0.82rem;color:#64748b">Realized P&L</span>
    <span style="font-size:0.82rem;font-weight:700;color:{'#059669' if real_pnl >= 0 else '#dc2626'}">${real_pnl:+,.2f}</span>
  </div>
  <div style="display:flex;justify-content:space-between;padding:8px 0">
    <span style="font-size:0.82rem;color:#64748b">Portfolio Weight</span>
    <span style="font-size:0.82rem;font-weight:700;color:#0f172a">{pct_of_port:.1f}%</span>
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # Mini chat
        st.markdown("""
<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:16px;
     box-shadow:0 1px 3px rgba(0,0,0,0.04)">
  <div style="font-size:0.82rem;font-weight:700;color:#0f172a;margin-bottom:10px">🤖 Ask AI</div>
""", unsafe_allow_html=True)
        _mini_chat(df, holdings_df)
        st.markdown("</div>", unsafe_allow_html=True)


def _mini_chat(df, holdings_df):
    metrics = st.session_state.get("performance_metrics", {})
    key = "chat_b"
    if key not in st.session_state:
        st.session_state[key] = []

    for msg in st.session_state[key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    for q in SUGGESTED_QUESTIONS[:2]:
        if st.button(q, key=f"bq_{q[:15]}", use_container_width=True):
            st.session_state[key].append({"role": "user", "content": q})
            st.session_state["_b_pending"] = q
            st.rerun()

    if "_b_pending" in st.session_state:
        p = st.session_state.pop("_b_pending")
        history = list(st.session_state[key])
        with st.chat_message("assistant"):
            try:
                r = st.write_stream(stream_chat_response(history, holdings_df, metrics, df=df))
            except Exception as e:
                r = f"⚠️ {e}"; st.markdown(r)
        st.session_state[key].append({"role": "assistant", "content": r or ""})

    prompt = st.chat_input("Ask about this position…", key="b_chat")
    if prompt:
        st.session_state[key].append({"role": "user", "content": prompt})
        history = list(st.session_state[key])
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                r = st.write_stream(stream_chat_response(history, holdings_df, metrics, df=df))
            except Exception as e:
                r = f"⚠️ {e}"; st.markdown(r)
        st.session_state[key].append({"role": "assistant", "content": r or ""})


def _no_data_screen():
    st.markdown(_BASE_CSS, unsafe_allow_html=True)
    st.markdown("""
<div style="background:#020617;height:40px;display:flex;align-items:center;padding:0 16px">
  <span style="color:white;font-weight:600;font-size:0.85rem">📈 Portfolio Analyst</span>
</div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("""
<div style="background:#0f172a;border-radius:8px;padding:20px;color:#94a3b8;margin-top:8px">
  <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;
       margin-bottom:12px">Holdings</div>
  <div style="font-size:0.85rem;color:#475569;text-align:center;padding:20px 0">
    No data loaded
  </div>
</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='margin-top:8px'>", unsafe_allow_html=True)
        st.info("📂 Upload your portfolio CSV to get started.")
        uploaded = st.file_uploader("CSV", type=["csv"], key="b_init_upload", label_visibility="collapsed")
        if uploaded:
            from utils.data_processing import load_and_validate_csv
            result = load_and_validate_csv(uploaded)
            if result.ok:
                st.session_state["transactions_df"] = result.df
                st.rerun()
            for e in result.errors:
                st.error(e)
        try:
            with open("sample_portfolio.csv", "rb") as f:
                st.download_button("⬇️ Download sample CSV", f.read(), "sample_portfolio.csv", "text/csv")
        except FileNotFoundError:
            pass
        st.markdown("</div>", unsafe_allow_html=True)
