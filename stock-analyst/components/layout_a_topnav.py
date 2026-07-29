"""
Layout A — Top Nav + Dashboard-First
Matches the TopNav.tsx mockup exactly: white top bar, indigo accents,
KPI cards, SVG donut, glassmorphism AI card, styled holdings table.
"""
from __future__ import annotations
import math
import streamlit as st
import pandas as pd

from utils.data_processing import load_and_validate_csv, get_display_df
from utils.portfolio_math import build_holdings_table
from utils.llm_agent import get_portfolio_summary, stream_chat_response

_COLORS = ["#4f46e5","#3b82f6","#0ea5e9","#06b6d4","#14b8a6","#10b981","#f59e0b","#ef4444"]

_BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
#MainMenu, footer, header { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }
body, .stApp { background: #f8fafc !important; font-family: 'Inter', sans-serif !important; }
/* Nav radio buttons → pill style */
div[data-testid="stHorizontalBlock"] { gap: 0 !important; }
.stRadio > div { flex-direction: row; gap: 4px; }
.stRadio label { font-size: 0.85rem !important; font-weight: 500 !important; }
/* Hide default radio circles */
.stRadio [data-baseweb="radio"] > div:first-child { display: none; }
/* Streamlit metric override */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
[data-testid="stMetricLabel"] { font-size: 0.78rem !important; font-weight: 600 !important; color: #64748b !important; text-transform: uppercase; letter-spacing: 0.04em; }
[data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 800 !important; color: #0f172a !important; }
[data-testid="stMetricDelta"] { font-size: 0.82rem !important; font-weight: 600 !important; }
/* Hide plotly modebar */
.modebar { display: none !important; }
/* Hide the nav radio (state only — visual nav is HTML) */
div[data-testid="stRadio"] { display: none !important; }
</style>
"""

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
    return (
        f'<svg viewBox="0 0 100 100" style="transform:rotate(-90deg);width:100%;height:100%">'
        + "".join(parts) + "</svg>"
    )

def _kpi_html(label: str, value: str, trend: str = "", positive: bool = True, icon: str = "💰") -> str:
    trend_color = "#16a34a" if positive else "#dc2626"
    trend_arrow = "↑" if positive else "↓"
    trend_html = (
        f'<span style="font-size:0.8rem;font-weight:600;color:{trend_color};margin-left:6px">'
        f'{trend_arrow} {trend}</span>'
        if trend else ""
    )
    return f"""
<div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:1rem 1.25rem;
     box-shadow:0 1px 3px rgba(0,0,0,0.05);display:flex;align-items:center;justify-content:space-between">
  <div>
    <div style="font-size:0.72rem;font-weight:600;color:#64748b;text-transform:uppercase;
         letter-spacing:0.05em;margin-bottom:4px">{label}</div>
    <div style="display:flex;align-items:baseline">
      <span style="font-size:1.5rem;font-weight:800;color:#0f172a">{value}</span>
      {trend_html}
    </div>
  </div>
  <div style="width:36px;height:36px;border-radius:50%;background:#f8fafc;border:1px solid #e2e8f0;
       display:flex;align-items:center;justify-content:center;font-size:1rem">{icon}</div>
</div>"""

def _topnav_html(total: float | None, delta_pct: float | None, active: str) -> str:
    if total is not None:
        val_str = f"${total:,.0f}"
        delta_str = f"{'+' if delta_pct >= 0 else ''}{delta_pct:.1f}%"
        delta_color = "#16a34a" if delta_pct >= 0 else "#dc2626"
        badge = (
            f'<div style="display:flex;align-items:center;gap:12px;padding-right:16px;'
            f'border-right:1px solid #e2e8f0;margin-right:8px">'
            f'<div style="text-align:right"><div style="font-size:9px;font-weight:700;color:#94a3b8;'
            f'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:2px">Total Value</div>'
            f'<div style="font-size:0.9rem;font-weight:900;color:#0f172a">{val_str}</div></div>'
            f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;color:{delta_color};'
            f'font-size:0.72rem;font-weight:700;padding:3px 8px;border-radius:6px">'
            f'↑ {delta_str}</div></div>'
        )
    else:
        badge = '<span style="font-size:0.8rem;color:#94a3b8;margin-right:8px">No portfolio loaded</span>'

    nav_items = [("📊", "Overview"), ("📈", "Performance"), ("📂", "Upload"), ("🤖", "AI Chat")]
    nav_html = ""
    for icon, label in nav_items:
        is_active = label == active
        bg = "background:#eff6ff;color:#4338ca;" if is_active else "color:#475569;"
        nav_html += (
            f'<span style="display:inline-flex;align-items:center;gap:5px;padding:5px 10px;'
            f'border-radius:6px;font-size:0.82rem;font-weight:{"600" if is_active else "500"};'
            f'{bg}cursor:pointer">{icon} {label}</span>'
        )
    return f"""
<div style="height:48px;background:white;border-bottom:1px solid #e2e8f0;display:flex;
     align-items:center;justify-content:space-between;padding:0 20px;
     box-shadow:0 1px 3px rgba(0,0,0,0.04);position:sticky;top:0;z-index:100;margin:0 -20px">
  <div style="display:flex;align-items:center;gap:20px">
    <span style="font-size:1.05rem;font-weight:800;color:#4338ca;letter-spacing:-0.3px">
      📈 Portfoli<span style="color:#0f172a">AI</span>
    </span>
    <div style="display:flex;align-items:center;gap:2px">{nav_html}</div>
  </div>
  <div style="display:flex;align-items:center">{badge}
    <div style="width:30px;height:30px;border-radius:50%;background:#eff6ff;border:1px solid #c7d2fe;
         display:flex;align-items:center;justify-content:center;font-size:0.8rem">👤</div>
  </div>
</div>"""

def _holdings_table_html(holdings_df: pd.DataFrame) -> str:
    rows = ""
    for _, r in holdings_df.iterrows():
        t = r["Ticker"]
        qty = r.get("Quantity", 0) or 0
        avg = r.get("Avg Cost (FIFO)", 0) or 0
        price = r.get("Current Price", 0) or 0
        val = r.get("Current Value", 0) or 0
        pl_d = r.get("Unrealized Gain ($)", 0) or 0
        pl_p = r.get("Unrealized Gain (%)", 0) or 0
        pl_pos = pl_d >= 0
        pl_bg = "#f0fdf4" if pl_pos else "#fff1f2"
        pl_color = "#16a34a" if pl_pos else "#dc2626"
        pl_arrow = "↑" if pl_pos else "↓"
        rows += f"""
<tr style="border-bottom:1px solid #f1f5f9">
  <td style="padding:8px 16px">
    <div style="display:flex;align-items:center;gap:10px">
      <div style="width:28px;height:28px;border-radius:6px;background:#f1f5f9;display:flex;
           align-items:center;justify-content:center;font-size:0.72rem;font-weight:700;color:#334155">
        {t[0]}
      </div>
      <div>
        <div style="font-weight:700;font-size:0.88rem;color:#0f172a">{t}</div>
      </div>
    </div>
  </td>
  <td style="padding:8px 16px;text-align:right;font-size:0.85rem;color:#475569">{qty:,.2f}</td>
  <td style="padding:8px 16px;text-align:right;font-size:0.85rem;color:#64748b">${avg:,.2f}</td>
  <td style="padding:8px 16px;text-align:right;font-size:0.85rem;font-weight:600;color:#0f172a">${price:,.2f}</td>
  <td style="padding:8px 16px;text-align:right;font-size:0.85rem;font-weight:700;color:#0f172a">${val:,.0f}</td>
  <td style="padding:8px 16px;text-align:right">
    <span style="display:inline-flex;align-items:center;gap:2px;padding:3px 8px;border-radius:6px;
          background:{pl_bg};color:{pl_color};font-size:0.78rem;font-weight:700">
      {pl_arrow} ${abs(pl_d):,.0f} ({abs(pl_p):.1f}%)
    </span>
  </td>
</tr>"""

    return f"""
<div style="background:white;border:1px solid #e2e8f0;border-radius:12px;
     box-shadow:0 1px 3px rgba(0,0,0,0.05);overflow:hidden">
  <div style="padding:12px 16px;border-bottom:1px solid #e2e8f0;display:flex;
       align-items:center;justify-content:space-between">
    <span style="font-weight:700;color:#0f172a;font-size:0.9rem">Position Details</span>
    <span style="font-size:0.75rem;color:#4338ca;font-weight:600;background:#eff6ff;
          padding:3px 8px;border-radius:6px">FIFO Cost Basis</span>
  </div>
  <div style="overflow-x:auto">
  <table style="width:100%;border-collapse:collapse">
    <thead>
      <tr style="background:#f8fafc">
        <th style="padding:8px 16px;text-align:left;font-size:0.72rem;font-weight:700;
             color:#64748b;text-transform:uppercase;letter-spacing:0.05em">Asset</th>
        <th style="padding:8px 16px;text-align:right;font-size:0.72rem;font-weight:700;
             color:#64748b;text-transform:uppercase;letter-spacing:0.05em">Shares</th>
        <th style="padding:8px 16px;text-align:right;font-size:0.72rem;font-weight:700;
             color:#64748b;text-transform:uppercase;letter-spacing:0.05em">Avg Cost</th>
        <th style="padding:8px 16px;text-align:right;font-size:0.72rem;font-weight:700;
             color:#64748b;text-transform:uppercase;letter-spacing:0.05em">Price</th>
        <th style="padding:8px 16px;text-align:right;font-size:0.72rem;font-weight:700;
             color:#64748b;text-transform:uppercase;letter-spacing:0.05em">Market Value</th>
        <th style="padding:8px 16px;text-align:right;font-size:0.72rem;font-weight:700;
             color:#64748b;text-transform:uppercase;letter-spacing:0.05em">Unrealized P&amp;L</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
  </div>
</div>"""

def _ai_card_shell() -> str:
    return """
<div style="background:linear-gradient(135deg,#f8f9ff 0%,white 50%,#f0f4ff 100%);
     border:1px solid #e0e7ff;border-radius:12px;padding:20px;position:relative;overflow:hidden;height:100%">
  <div style="position:absolute;top:-40px;right:-40px;width:180px;height:180px;
       background:rgba(165,180,252,0.2);border-radius:50%;filter:blur(40px);pointer-events:none"></div>
  <div style="position:absolute;bottom:-40px;left:-40px;width:180px;height:180px;
       background:rgba(196,181,253,0.2);border-radius:50%;filter:blur(40px);pointer-events:none"></div>
  <div style="position:relative;display:flex;align-items:center;gap:10px;margin-bottom:16px">
    <div style="width:34px;height:34px;border-radius:8px;background:#4338ca;display:flex;
         align-items:center;justify-content:center;font-size:0.9rem;box-shadow:0 2px 8px rgba(67,56,202,0.3)">✨</div>
    <div>
      <div style="font-weight:700;color:#0f172a;font-size:0.9rem">AI Portfolio Health</div>
      <div style="font-size:0.68rem;font-weight:600;color:#4338ca;text-transform:uppercase;
           letter-spacing:0.06em">Powered by Groq</div>
    </div>
  </div>
</div>"""


def render_layout_a() -> None:
    st.markdown(_BASE_CSS, unsafe_allow_html=True)

    # Compute headline values
    total_val, delta_pct = None, None
    holdings_df = st.session_state.get("holdings_df", pd.DataFrame())
    if not holdings_df.empty:
        total_val = float(holdings_df["Current Value"].dropna().sum())
        cost = float(holdings_df["Cost Basis"].sum())
        delta_pct = (total_val - cost) / cost * 100 if cost > 0 else 0.0

    # Nav state
    nav = st.session_state.get("a_nav", "Overview")
    st.markdown(_topnav_html(total_val, delta_pct, nav), unsafe_allow_html=True)

    # Nav selector (hidden radio that syncs)
    st.markdown('<div style="padding:12px 20px 0 20px">', unsafe_allow_html=True)
    new_nav = st.radio("nav", ["Overview", "Performance", "Upload", "AI Chat"],
                       horizontal=True, label_visibility="collapsed", key="a_nav")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="padding:0 20px 20px 20px">', unsafe_allow_html=True)

    if new_nav == "Upload":
        _render_upload()
    elif new_nav == "Performance":
        _render_performance()
    elif new_nav == "AI Chat":
        _render_chat()
    else:
        _render_overview()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_overview() -> None:
    if "transactions_df" not in st.session_state:
        st.markdown("""
<div style="margin-top:48px;text-align:center">
  <div style="font-size:3rem;margin-bottom:12px">📊</div>
  <h2 style="color:#0f172a;font-weight:800;font-size:1.4rem">No portfolio loaded</h2>
  <p style="color:#64748b;font-size:0.9rem;margin-bottom:20px">
    Go to <b>Upload</b> to get started, or download the sample file below.
  </p>
</div>""", unsafe_allow_html=True)
        try:
            with open("sample_portfolio.csv", "rb") as f:
                st.download_button("⬇️ Download sample_portfolio.csv", f.read(),
                                   "sample_portfolio.csv", "text/csv")
        except FileNotFoundError:
            pass
        return

    df = st.session_state["transactions_df"]
    with st.spinner("Fetching current prices…"):
        holdings_df = build_holdings_table(df)
    st.session_state["holdings_df"] = holdings_df

    if holdings_df.empty:
        st.info("No open positions found.")
        return

    total_val = float(holdings_df["Current Value"].dropna().sum())
    cost = float(holdings_df["Cost Basis"].sum())
    unreal = total_val - cost
    unreal_pct = unreal / cost * 100 if cost > 0 else 0.0

    # KPI row
    kpi1 = _kpi_html("Portfolio Value", f"${total_val:,.2f}",
                     f"{unreal_pct:+.1f}%", unreal >= 0, "💰")
    kpi2 = _kpi_html("Cost Basis", f"${cost:,.2f}", "", True, "📦")
    kpi3 = _kpi_html("Unrealized P&L", f"${unreal:+,.0f}",
                     f"{unreal_pct:+.1f}%", unreal >= 0, "📈")
    c1, c2, c3 = st.columns(3)
    c1.markdown(kpi1, unsafe_allow_html=True)
    c2.markdown(kpi2, unsafe_allow_html=True)
    c3.markdown(kpi3, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Donut + AI side by side
    col_left, col_right = st.columns([3, 2], gap="medium")

    with col_left:
        # Build donut slices
        pie_df = holdings_df[["Ticker", "Current Value"]].dropna().copy()
        pie_df["pct"] = (pie_df["Current Value"] / pie_df["Current Value"].sum() * 100).round(0).astype(int)
        slices = pie_df.to_dict("records")

        legend_items = "".join([
            f'<div style="display:flex;align-items:center;gap:6px">'
            f'<div style="width:8px;height:8px;border-radius:2px;background:{_COLORS[i % len(_COLORS)]}"></div>'
            f'<span style="font-size:0.82rem;font-weight:600;color:#334155">{r["Ticker"]}</span>'
            f'<span style="font-size:0.82rem;color:#94a3b8">{r["pct"]}%</span></div>'
            for i, r in enumerate(slices)
        ])

        st.markdown(f"""
<div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:20px;
     box-shadow:0 1px 3px rgba(0,0,0,0.05)">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
    <span style="font-weight:700;color:#0f172a">Asset Allocation</span>
    <span style="font-size:0.72rem;color:#64748b;background:#f1f5f9;padding:3px 8px;border-radius:6px;font-weight:600">By Market Value</span>
  </div>
  <div style="display:flex;align-items:center;gap:24px">
    <div style="width:100px;height:100px;flex-shrink:0">
      {_svg_donut(slices)}
    </div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px 20px;flex:1">
      {legend_items}
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown(_holdings_table_html(holdings_df), unsafe_allow_html=True)

    with col_right:
        # AI summary card with glassmorphism shell
        cache_key = f"ai_summary_{hash(holdings_df.to_json())}"
        partial = {"total_investment": cost, "current_portfolio_value": total_val,
                   "total_return_dollars": unreal, "total_return_pct": unreal_pct,
                   "realized_pnl": 0, "total_sell_proceeds": 0, "xirr": None}
        if cache_key not in st.session_state:
            with st.spinner("Analysing with Groq…"):
                st.session_state[cache_key] = get_portfolio_summary(holdings_df, partial)
        summary = st.session_state[cache_key]

        st.markdown(f"""
<div style="background:linear-gradient(135deg,#f8f9ff 0%,white 50%,#f0f4ff 100%);
     border:1px solid #e0e7ff;border-radius:12px;padding:20px;position:relative;overflow:hidden">
  <div style="position:absolute;top:-40px;right:-40px;width:180px;height:180px;
       background:rgba(165,180,252,0.2);border-radius:50%;filter:blur(40px)"></div>
  <div style="position:absolute;bottom:-40px;left:-40px;width:180px;height:180px;
       background:rgba(196,181,253,0.15);border-radius:50%;filter:blur(40px)"></div>
  <div style="position:relative;display:flex;align-items:center;gap:10px;margin-bottom:16px">
    <div style="width:34px;height:34px;border-radius:8px;background:#4338ca;display:flex;
         align-items:center;justify-content:center;font-size:0.9rem;
         box-shadow:0 2px 8px rgba(67,56,202,0.3)">✨</div>
    <div>
      <div style="font-weight:700;color:#0f172a;font-size:0.9rem">AI Portfolio Health</div>
      <div style="font-size:0.68rem;font-weight:600;color:#4338ca;text-transform:uppercase;
           letter-spacing:0.06em">Powered by Groq LLaMA-3.3-70B</div>
    </div>
  </div>
  <div style="position:relative;background:rgba(255,255,255,0.7);backdrop-filter:blur(8px);
       border:1px solid rgba(255,255,255,0.9);border-radius:10px;padding:14px;
       box-shadow:0 4px 20px rgba(79,70,229,0.06);font-size:0.88rem;color:#334155;line-height:1.6">
    {summary}
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh AI analysis", key="a_refresh_ai", use_container_width=True):
            st.session_state.pop(cache_key, None)
            st.rerun()

        # Quick stats card
        st.markdown(f"""
<div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:16px;
     box-shadow:0 1px 3px rgba(0,0,0,0.05);margin-top:4px">
  <div style="font-size:0.72rem;font-weight:700;color:#94a3b8;text-transform:uppercase;
       letter-spacing:0.05em;margin-bottom:12px">Portfolio Summary</div>
  <div style="display:flex;justify-content:space-between;margin-bottom:8px">
    <span style="font-size:0.83rem;color:#64748b">Transactions</span>
    <span style="font-size:0.83rem;font-weight:700;color:#0f172a">{len(df):,}</span>
  </div>
  <div style="display:flex;justify-content:space-between;margin-bottom:8px">
    <span style="font-size:0.83rem;color:#64748b">Tickers</span>
    <span style="font-size:0.83rem;font-weight:700;color:#0f172a">{df['ticker'].nunique()}</span>
  </div>
  <div style="display:flex;justify-content:space-between;margin-bottom:8px">
    <span style="font-size:0.83rem;color:#64748b">First trade</span>
    <span style="font-size:0.83rem;font-weight:700;color:#0f172a">{df['date'].min().strftime('%b %d, %Y')}</span>
  </div>
  <div style="display:flex;justify-content:space-between">
    <span style="font-size:0.83rem;color:#64748b">Latest trade</span>
    <span style="font-size:0.83rem;font-weight:700;color:#0f172a">{df['date'].max().strftime('%b %d, %Y')}</span>
  </div>
</div>""", unsafe_allow_html=True)


def _render_upload() -> None:
    st.markdown("""
<div style="margin:24px 0 20px 0">
  <h2 style="font-size:1.3rem;font-weight:800;color:#0f172a;margin-bottom:4px">📂 Upload Transaction CSV</h2>
  <p style="color:#64748b;font-size:0.88rem">Required columns: <b>ticker · date · transaction_type · quantity · price</b></p>
</div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        try:
            with open("sample_portfolio.csv", "rb") as f:
                st.download_button("⬇️ Sample CSV", f.read(), "sample_portfolio.csv", "text/csv",
                                   use_container_width=True)
        except FileNotFoundError:
            pass

    with col1:
        uploaded = st.file_uploader("CSV file", type=["csv"], key="a_uploader",
                                    label_visibility="collapsed")

    if uploaded is None:
        if "transactions_df" in st.session_state:
            df = st.session_state["transactions_df"]
            st.markdown(f"""
<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px 16px;
     display:flex;align-items:center;gap:10px;margin-top:8px">
  <span style="font-size:1.2rem">✅</span>
  <div>
    <div style="font-weight:700;color:#14532d;font-size:0.9rem">Portfolio loaded</div>
    <div style="color:#166534;font-size:0.82rem">{len(df):,} transactions · {df['ticker'].nunique()} tickers</div>
  </div>
</div>""", unsafe_allow_html=True)
        return

    result = load_and_validate_csv(uploaded)
    for err in result.errors:
        st.error(f"❌ {err}")
    if not result.ok:
        return
    for warn in result.warnings:
        st.warning(f"⚠️ {warn}")
    df = result.df
    prev = st.session_state.get("transactions_df")
    if prev is None or not prev.equals(df):
        st.session_state["transactions_df"] = df
        for k in ("holdings_df", "performance_metrics"):
            st.session_state.pop(k, None)
    st.success(f"✅ Loaded {len(df):,} transactions · {df['ticker'].nunique()} tickers")
    st.dataframe(get_display_df(df), use_container_width=True, hide_index=True)


def _render_performance() -> None:
    from components.tab3_performance import render_tab3
    render_tab3()


def _render_chat() -> None:
    from components.tab4_chat import render_tab4
    render_tab4()
