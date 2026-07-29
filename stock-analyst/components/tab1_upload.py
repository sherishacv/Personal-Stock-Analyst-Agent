"""
Tab 1 — Data Upload

- CSV upload with full validation (errors shown as st.error, warnings as st.warning)
- Displays formatted transaction table with summary stats
- Exposes a download button for the cleaned/normalised CSV
- Clears downstream cached state on new upload
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from utils.data_processing import load_and_validate_csv, get_display_df


def render_tab1() -> None:
    st.header("📂 Upload Transaction History")
    st.markdown(
        "Upload a CSV with your US stock transaction history. "
        "Required columns: **ticker · date · transaction_type · quantity · price**"
    )

    with st.expander("📋 Expected CSV format & rules", expanded=False):
        st.markdown("""
| ticker | date       | transaction_type | quantity | price   |
|--------|------------|-----------------|----------|---------|
| AAPL   | 2023-01-15 | Buy             | 10       | 135.00  |
| MSFT   | 2023-02-20 | Buy             | 5        | 255.00  |
| AAPL   | 2023-06-10 | Sell            | 3        | 185.00  |

**Rules**
- `transaction_type` must be **Buy** or **Sell** (case-insensitive)
- `quantity` and `price` must be positive numbers
- `date` must be a valid date (YYYY-MM-DD recommended)
- Duplicate rows (identical on all 5 columns) are automatically removed
- On the same date, Buy transactions are processed before Sells
        """)

    uploaded_file = st.file_uploader(
        "Choose your CSV file",
        type=["csv"],
        key="csv_uploader",
        help="Max 200 MB. Only CSV files are accepted.",
    )

    if uploaded_file is None:
        if "transactions_df" not in st.session_state:
            st.info("👆 Upload a CSV file to get started. A sample file is available in the sidebar.")
        return

    # ── Validate ──────────────────────────────────────────────────────────────
    result = load_and_validate_csv(uploaded_file)

    for err in result.errors:
        st.error(f"❌ {err}")

    if not result.ok:
        # Clear stale data so downstream tabs don't use old state
        for key in ("transactions_df", "holdings_df", "performance_metrics"):
            st.session_state.pop(key, None)
        return

    for warn in result.warnings:
        st.warning(f"⚠️ {warn}")

    df = result.df

    # ── Store in session state (invalidate downstream caches) ─────────────────
    prev = st.session_state.get("transactions_df")
    if prev is None or not prev.equals(df):
        st.session_state["transactions_df"] = df
        # Drop stale downstream results so Tab 2/3/4 recompute
        for key in ("holdings_df", "performance_metrics"):
            st.session_state.pop(key, None)

    st.success(
        f"✅ Loaded **{len(df):,}** transactions · "
        f"**{df['ticker'].nunique()}** tickers · "
        f"**{(df['transaction_type'].str.lower() == 'buy').sum()}** buys / "
        f"**{(df['transaction_type'].str.lower() == 'sell').sum()}** sells"
    )

    # ── Summary metrics ───────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Transactions", f"{len(df):,}")
    c2.metric("Unique Tickers", df["ticker"].nunique())
    c3.metric("First Trade", df["date"].min().strftime("%b %d, %Y"))
    c4.metric("Latest Trade", df["date"].max().strftime("%b %d, %Y"))

    st.divider()

    # ── Transaction table ─────────────────────────────────────────────────────
    st.subheader("Transaction History")

    # Filter controls
    col_search, col_type, col_sort = st.columns([2, 1, 1])
    with col_search:
        search_ticker = st.text_input(
            "Filter by ticker", placeholder="e.g. AAPL", label_visibility="collapsed",
            key="tab1_ticker_filter"
        ).strip().upper()
    with col_type:
        tx_filter = st.selectbox("Type", ["All", "Buy", "Sell"], key="tab1_tx_filter")
    with col_sort:
        sort_order = st.selectbox("Sort date", ["Newest first", "Oldest first"], key="tab1_sort")

    filtered = df.copy()
    if search_ticker:
        filtered = filtered[filtered["ticker"].str.contains(search_ticker, na=False)]
    if tx_filter != "All":
        filtered = filtered[filtered["transaction_type"].str.lower() == tx_filter.lower()]
    if sort_order == "Newest first":
        filtered = filtered.sort_values("date", ascending=False)

    st.caption(f"Showing {len(filtered):,} of {len(df):,} transactions")
    st.dataframe(get_display_df(filtered), use_container_width=True, hide_index=True)

    # ── Download cleaned CSV ──────────────────────────────────────────────────
    st.download_button(
        label="⬇️ Download cleaned CSV",
        data=df.assign(date=df["date"].dt.strftime("%Y-%m-%d")).to_csv(index=False),
        file_name="portfolio_cleaned.csv",
        mime="text/csv",
    )
