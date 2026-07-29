"""
AI-powered Personal Stock Analyst Agent
========================================
Entry point — Classic Tabs layout.
"""

from __future__ import annotations
import streamlit as st

st.set_page_config(
    page_title="Stock Analyst Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── Fade-in ─────────────────────────────────────────────────────────── */
@keyframes _fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.main .block-container {
    animation: _fadeUp 0.3s ease-out both;
    padding-top: 1.5rem !important;
    max-width: 1200px;
}

/* ── Page background ─────────────────────────────────────────────────── */
.stApp { background: #F8FAFC; }

/* ── Title / header scale ────────────────────────────────────────────── */
h1 { font-size: 1.65rem !important; font-weight: 700 !important; color: #0F172A !important; }
h2 { font-size: 1.15rem !important; font-weight: 600 !important; color: #1E293B !important; margin-top: 0.25rem !important; }
h3 { font-size: 1rem   !important; font-weight: 600 !important; color: #1E293B !important; }
p, li, .stMarkdown { color: #334155; font-size: 0.92rem; }

/* ── Caption ─────────────────────────────────────────────────────────── */
small, .stCaption p, [data-testid="stCaptionContainer"] p {
    color: #94A3B8 !important; font-size: 0.78rem !important;
}

/* ── Metric cards ────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 18px 22px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 6px 18px rgba(79,70,229,0.13);
    transform: translateY(-2px);
}
[data-testid="stMetricLabel"] > div {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: #64748B !important;
}
[data-testid="stMetricValue"] > div {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #0F172A !important;
}
[data-testid="stMetricDelta"] > div { font-size: 0.82rem !important; font-weight: 500 !important; }

/* ── Tab bar ─────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: transparent;
    border-bottom: 2px solid #E2E8F0 !important;
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 22px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #64748B !important;
    background: transparent !important;
    transition: color 0.15s ease, background 0.15s ease;
    margin-bottom: -2px;
}
.stTabs [aria-selected="true"] {
    color: #4F46E5 !important;
    background: #EEF2FF !important;
    border-bottom: 2px solid #4F46E5 !important;
}
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    color: #4F46E5 !important;
    background: #F5F3FF !important;
}

/* ── Buttons ─────────────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    border: 1px solid #E2E8F0 !important;
    background: #ffffff !important;
    color: #374151 !important;
    transition: all 0.15s ease !important;
    padding: 6px 16px !important;
}
.stButton > button:hover {
    border-color: #4F46E5 !important;
    color: #4F46E5 !important;
    background: #EEF2FF !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important;
}
.stDownloadButton > button {
    border-radius: 8px !important;
    border: 1px solid #C7D2FE !important;
    background: #EEF2FF !important;
    color: #4F46E5 !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    transition: all 0.15s ease !important;
}
.stDownloadButton > button:hover {
    background: #E0E7FF !important;
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important;
}

/* ── Dataframe ────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] iframe { border-radius: 10px; }
[data-testid="stDataFrameResizable"] { border: 1px solid #E2E8F0; border-radius: 10px; overflow: hidden; }

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #E2E8F0 !important;
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] small { color: #64748B; }

/* ── Alert boxes ─────────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Divider ─────────────────────────────────────────────────────────── */
hr { border-color: #E2E8F0 !important; margin: 1.25rem 0 !important; }

/* ── Expander ────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    background: #ffffff !important;
}
[data-testid="stExpander"] summary { font-weight: 500 !important; color: #374151 !important; }

/* ── File uploader ────────────────────────────────────────────────────── */
[data-testid="stFileUploadDropzone"] {
    border: 2px dashed #C7D2FE !important;
    border-radius: 12px !important;
    background: #F5F3FF !important;
    transition: all 0.15s ease;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #4F46E5 !important;
    background: #EEF2FF !important;
}

/* ── Chat ────────────────────────────────────────────────────────────── */
[data-testid="stChatInput"] textarea {
    border-radius: 12px !important;
    border-color: #E2E8F0 !important;
}
[data-testid="stChatInput"] textarea:focus { border-color: #4F46E5 !important; box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important; }
[data-testid="stChatMessage"] { border-radius: 12px !important; }

/* ── Info box ────────────────────────────────────────────────────────── */
.stInfo { border-left-color: #4F46E5 !important; }

/* ── Selectbox / text input ──────────────────────────────────────────── */
[data-baseweb="select"] > div, [data-baseweb="input"] > div {
    border-radius: 8px !important;
    border-color: #E2E8F0 !important;
}
[data-baseweb="select"] > div:focus-within, [data-baseweb="input"] > div:focus-within {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important;
}

/* ── Spinner accent ──────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: #4F46E5 !important; }
</style>
""", unsafe_allow_html=True)

from components.tab1_upload import render_tab1
from components.tab2_portfolio import render_tab2
from components.tab3_performance import render_tab3
from components.tab4_chat import render_tab4

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if "transactions_df" in st.session_state:
        df = st.session_state["transactions_df"]
        st.success("**Portfolio loaded**")
        st.markdown(f"""
| | |
|---|---|
| Transactions | **{len(df):,}** |
| Tickers | **{df['ticker'].nunique()}** |
| First trade | **{df['date'].min().strftime('%b %d, %Y')}** |
| Latest trade | **{df['date'].max().strftime('%b %d, %Y')}** |
""")
        tickers = sorted(df["ticker"].unique())
        st.caption("Tickers: " + " · ".join(tickers))
        if st.button("🗑️ Clear portfolio data", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    else:
        st.info("No portfolio loaded.\nGo to **Data Upload** to get started.")
    st.markdown("---")
    st.markdown("**📄 Need a sample file?**")
    try:
        with open("sample_portfolio.csv", "rb") as f:
            st.download_button(
                "⬇️ Download sample_portfolio.csv",
                data=f.read(),
                file_name="sample_portfolio.csv",
                mime="text/csv",
                use_container_width=True,
            )
    except FileNotFoundError:
        pass
    st.markdown("---")
    st.caption(
        "Data: [Yahoo Finance](https://finance.yahoo.com) via yfinance · "
        "AI: [Groq](https://groq.com) llama-3.3-70b-versatile · "
        "Prices cached 5 min"
    )

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("📈 Personal Stock Analyst Agent")
st.markdown(
    "Powered by **yfinance** (live prices) · **Groq LLaMA-3.3-70B** (AI analysis) · "
    "**FIFO** cost-basis accounting · **XIRR** time-weighted returns"
)
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📂  Data Upload",
    "📊  Portfolio View",
    "📈  Historical Performance",
    "🤖  AI Analyst",
])
with tab1:
    render_tab1()
with tab2:
    render_tab2()
with tab3:
    render_tab3()
with tab4:
    render_tab4()
