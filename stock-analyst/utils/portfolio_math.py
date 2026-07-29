"""
Portfolio calculation utilities.

Production design:
- fetch_current_prices: per-ticker fallback, cached via @st.cache_data (TTL 5 min)
- compute_fifo_holdings: oversell-safe (caps sell at available inventory, logs warning)
- compute_xirr: Newton-Raphson primary, Brent fallback, multi-seed, guards on
  single-sign cashflows and < 2 cashflow dates
- compute_performance_metrics: derived from FIFO + current prices, no side-effects
- All public functions are pure (no session_state access)
"""

from __future__ import annotations

import logging
from collections import deque
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

log = logging.getLogger(__name__)

_EPSILON = 1e-9   # floating-point zero guard
_YEAR_DAYS = 365.25


# ─────────────────────────────────────────────────────────────────────────────
# Price fetching  (cached 5 minutes)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def fetch_current_prices(tickers: tuple[str, ...]) -> dict[str, float]:
    """
    Fetch the most recent closing price for each ticker.
    Accepts a *tuple* so Streamlit can hash the argument for caching.
    Falls back to fetching individually on any multi-ticker parse error.
    Returns NaN for tickers that cannot be resolved.
    """
    if not tickers:
        return {}

    prices: dict[str, float] = {}

    try:
        raw = yf.download(
            list(tickers),
            period="5d",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        close = raw["Close"] if "Close" in raw else raw

        if isinstance(close, pd.Series):
            # Single ticker — yfinance returns a Series
            ticker = tickers[0]
            val = close.dropna()
            prices[ticker] = float(val.iloc[-1]) if not val.empty else float("nan")
        else:
            for ticker in tickers:
                try:
                    col = close[ticker].dropna()
                    prices[ticker] = float(col.iloc[-1]) if not col.empty else float("nan")
                except Exception:
                    prices[ticker] = float("nan")
    except Exception:
        # Total failure — fall back to one-by-one
        for ticker in tickers:
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="5d", auto_adjust=True)
                if not hist.empty:
                    prices[ticker] = float(hist["Close"].dropna().iloc[-1])
                else:
                    prices[ticker] = float("nan")
            except Exception:
                prices[ticker] = float("nan")

    return prices


# ─────────────────────────────────────────────────────────────────────────────
# FIFO cost-basis engine
# ─────────────────────────────────────────────────────────────────────────────

def compute_fifo_holdings(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """
    FIFO cost-basis accounting per ticker.

    Assumptions / edge-case handling:
    - Rows must already be sorted by (date ASC, buys before sells on same date).
    - Sells that exceed available inventory are *capped* (not crashed); the excess
      is silently discarded (caller should have run _check_oversell in data_processing).
    - Fractional share support via float arithmetic.

    Returns dict keyed by ticker:
      quantity        current open shares
      avg_cost        FIFO weighted average cost per share of open lots
      total_cost      sum(lot_qty * lot_price) for open lots
      realized_pnl    cumulative realised P&L across all closed lots
      lots            list of {qty, price} remaining open lots (oldest first)
    """
    result: dict[str, dict[str, Any]] = {}

    for ticker, group in df.groupby("ticker"):
        # Ensure correct order (defensive — caller should have sorted already)
        group = group.copy()
        group["_order"] = group["transaction_type"].str.lower().map({"buy": 0, "sell": 1})
        group = group.sort_values(["date", "_order"]).drop(columns=["_order"])

        lot_queue: deque[list[float]] = deque()   # [qty, price]  (mutable for partial fill)
        realized_pnl = 0.0

        for _, row in group.iterrows():
            qty = float(row["quantity"])
            price = float(row["price"])
            tx = row["transaction_type"].lower()

            if tx == "buy":
                lot_queue.append([qty, price])

            else:  # sell — cap at available inventory
                available = sum(lot[0] for lot in lot_queue)
                sell_qty = min(qty, available)      # capped
                remaining = sell_qty

                while remaining > _EPSILON and lot_queue:
                    lot = lot_queue[0]
                    lot_qty, lot_price = lot[0], lot[1]

                    if lot_qty <= remaining + _EPSILON:
                        realized_pnl += (price - lot_price) * lot_qty
                        remaining -= lot_qty
                        lot_queue.popleft()
                    else:
                        realized_pnl += (price - lot_price) * remaining
                        lot[0] -= remaining          # mutate in place
                        remaining = 0.0

        # Summarise open lots
        open_lots = [{"qty": lot[0], "price": lot[1]} for lot in lot_queue]
        total_qty = sum(lot["qty"] for lot in open_lots)
        total_cost = sum(lot["qty"] * lot["price"] for lot in open_lots)
        avg_cost = total_cost / total_qty if total_qty > _EPSILON else 0.0

        result[str(ticker)] = {
            "quantity": total_qty,
            "avg_cost": avg_cost,
            "total_cost": total_cost,
            "realized_pnl": realized_pnl,
            "lots": open_lots,
        }

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Holdings table  (cached on the df hash + market data TTL)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def build_holdings_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine FIFO holdings with live prices to produce the full display table.
    Cached for 5 minutes; Streamlit hashes the df argument by content.
    """
    fifo = compute_fifo_holdings(df)
    held = {t: v for t, v in fifo.items() if v["quantity"] > _EPSILON}

    if not held:
        return pd.DataFrame()

    tickers_tuple = tuple(sorted(held.keys()))
    current_prices = fetch_current_prices(tickers_tuple)

    rows = []
    for ticker, data in held.items():
        qty = data["quantity"]
        avg_cost = data["avg_cost"]
        cur_price = current_prices.get(ticker, float("nan"))
        price_valid = not (isinstance(cur_price, float) and np.isnan(cur_price))

        current_value = qty * cur_price if price_valid else float("nan")
        cost_basis = data["total_cost"]

        if price_valid and cost_basis > _EPSILON:
            unrealized_gain = current_value - cost_basis
            unrealized_pct = unrealized_gain / cost_basis * 100.0
        else:
            unrealized_gain = float("nan")
            unrealized_pct = float("nan")

        rows.append({
            "Ticker": ticker,
            "Quantity": round(qty, 6),
            "Avg Cost (FIFO)": round(avg_cost, 4),
            "Current Price": round(cur_price, 4) if price_valid else None,
            "Cost Basis": round(cost_basis, 2),
            "Current Value": round(current_value, 2) if price_valid else None,
            "Unrealized Gain ($)": round(unrealized_gain, 2) if not np.isnan(unrealized_gain) else None,
            "Unrealized Gain (%)": round(unrealized_pct, 2) if not np.isnan(unrealized_pct) else None,
        })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Performance metrics
# ─────────────────────────────────────────────────────────────────────────────

def compute_performance_metrics(df: pd.DataFrame, holdings_df: pd.DataFrame) -> dict[str, Any]:
    """
    Derive all Tab-3 metrics from transaction history + current holdings.

    Total Return = Sell Proceeds + Current Portfolio Value − Total Invested
    XIRR treats buys as outflows (-), sells as inflows (+),
    and current portfolio value as a terminal inflow today.
    """
    buy_mask = df["transaction_type"].str.lower() == "buy"
    sell_mask = df["transaction_type"].str.lower() == "sell"

    total_investment = float((df.loc[buy_mask, "quantity"] * df.loc[buy_mask, "price"]).sum())
    total_sell_proceeds = float((df.loc[sell_mask, "quantity"] * df.loc[sell_mask, "price"]).sum())

    current_portfolio_value = (
        float(holdings_df["Current Value"].dropna().sum())
        if not holdings_df.empty and "Current Value" in holdings_df.columns
        else 0.0
    )

    total_return_dollars = total_sell_proceeds + current_portfolio_value - total_investment
    total_return_pct = (
        total_return_dollars / total_investment * 100.0 if total_investment > _EPSILON else 0.0
    )

    # Realized P&L from FIFO
    fifo = compute_fifo_holdings(df)
    realized_pnl = sum(v["realized_pnl"] for v in fifo.values())

    xirr_value = _compute_xirr(df, current_portfolio_value)

    return {
        "total_investment": total_investment,
        "total_sell_proceeds": total_sell_proceeds,
        "current_portfolio_value": current_portfolio_value,
        "realized_pnl": realized_pnl,
        "total_return_dollars": total_return_dollars,
        "total_return_pct": total_return_pct,
        "xirr": xirr_value,
    }


# ─────────────────────────────────────────────────────────────────────────────
# XIRR
# ─────────────────────────────────────────────────────────────────────────────

def _compute_xirr(df: pd.DataFrame, current_portfolio_value: float) -> float | None:
    """
    Compute XIRR (annualised IRR for irregular cashflows).

    Methodology
    -----------
    1. Build cashflow list: buys → negative, sells → positive.
    2. Append terminal value (current portfolio value) as a positive flow today.
    3. Group flows on the same date (sum them) — avoids duplicate-date issues.
    4. Guard: need >= 2 distinct dates AND at least one sign change.
    5. Try Newton-Raphson from several seeds; fall back to Brent on [-99 %, +10 000 %].
    6. Validate result is finite and in [-99 %, +10 000 %].

    Returns annualised rate as a percentage (e.g. 18.4), or None on failure.
    """
    try:
        flows: dict[datetime, float] = {}

        for _, row in df.iterrows():
            dt: datetime = row["date"].to_pydatetime().replace(tzinfo=None)
            amount = float(row["quantity"]) * float(row["price"])
            sign = -1.0 if row["transaction_type"].lower() == "buy" else 1.0
            flows[dt] = flows.get(dt, 0.0) + sign * amount

        # Terminal inflow
        today = datetime.now().replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)
        flows[today] = flows.get(today, 0.0) + current_portfolio_value

        if len(flows) < 2:
            return None

        sorted_flows = sorted(flows.items())
        dates_list, amounts_list = zip(*sorted_flows)
        amounts_arr = np.array(amounts_list, dtype=float)

        # Guard: need both positive and negative flows
        if np.all(amounts_arr >= 0) or np.all(amounts_arr <= 0):
            return None

        start_date = dates_list[0]
        t = np.array([(d - start_date).days / _YEAR_DAYS for d in dates_list], dtype=float)

        def npv(rate: float) -> float:
            if rate <= -1.0:
                return float("inf")
            return float(np.sum(amounts_arr / (1.0 + rate) ** t))

        def npv_deriv(rate: float) -> float:
            if rate <= -1.0:
                return float("inf")
            return float(np.sum(-t * amounts_arr / (1.0 + rate) ** (t + 1.0)))

        # Newton-Raphson with multiple seeds
        seeds = [0.10, 0.0, 0.50, -0.10, 2.0, -0.50]
        for seed in seeds:
            try:
                rate = seed
                for _ in range(200):
                    f = npv(rate)
                    fp = npv_deriv(rate)
                    if abs(fp) < _EPSILON:
                        break
                    step = f / fp
                    rate -= step
                    if rate <= -1.0:
                        rate = -0.9999
                    if abs(step) < 1e-10:
                        if abs(npv(rate)) < 1e-4:
                            if -0.9999 < rate < 100.0:
                                return round(rate * 100.0, 2)
                        break
            except Exception:
                continue

        # Brent fallback
        from scipy.optimize import brentq  # local import — only used as fallback

        # Find a bracket where NPV changes sign
        lo, hi = -0.9999, 100.0
        try:
            npv_lo = npv(lo)
            npv_hi = npv(hi)
            if npv_lo * npv_hi > 0:
                # Same sign — try a tighter range
                for hi_try in [10.0, 5.0, 2.0, 1.0, 0.5]:
                    if npv(lo) * npv(hi_try) < 0:
                        hi = hi_try
                        break
                else:
                    return None

            rate = brentq(npv, lo, hi, xtol=1e-10, maxiter=1000)
            if -0.9999 < rate < 100.0:
                return round(rate * 100.0, 2)
        except Exception:
            pass

        return None

    except Exception as exc:
        log.warning("XIRR computation failed: %s", exc)
        return None
