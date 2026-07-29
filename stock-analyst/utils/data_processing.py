"""
Data loading and validation utilities for stock transaction CSV files.

Production rules:
- Row-level error reporting (row index + value, not just "column X is bad")
- Future-date detection (warning, not hard reject)
- NaN/null row detection
- Oversell pre-check per ticker (warning)
- Ticker symbol sanity check
- Duplicate row detection
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from io import StringIO
from typing import Optional

import pandas as pd


REQUIRED_COLUMNS = {"ticker", "date", "transaction_type", "quantity", "price"}
VALID_TRANSACTION_TYPES = {"buy", "sell"}

# Reasonable US ticker: 1-5 uppercase letters, optionally suffixed with . + 1-2 letters (e.g. BRK.B)
import re

_TICKER_RE = re.compile(r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$")


@dataclass
class ValidationResult:
    df: Optional[pd.DataFrame] = None
    errors: list[str] = field(default_factory=list)  # hard errors — upload rejected
    warnings: list[str] = field(
        default_factory=list
    )  # soft warnings — accepted but flagged

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def load_and_validate_csv(uploaded_file) -> ValidationResult:
    """
    Load and deeply validate a transaction CSV.
    Returns a ValidationResult; check .ok before using .df.
    """
    result = ValidationResult()

    # ── 1. Parse ─────────────────────────────────────────────────────────────
    try:
        # Re-seek in case Streamlit has already read the buffer
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
        raw = uploaded_file.read()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        df = pd.read_csv(StringIO(raw))
    except Exception as exc:
        result.errors.append(f"Cannot parse file as CSV: {exc}")
        return result

    if df.empty:
        result.errors.append("The uploaded file is empty.")
        return result

    # ── 2. Column names ───────────────────────────────────────────────────────
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        result.errors.append(
            f"Missing required columns: {', '.join(sorted(missing))}. "
            "Required: ticker, date, transaction_type, quantity, price"
        )
        return result

    # ── 3. Drop fully-blank rows ──────────────────────────────────────────────
    blank_mask = df[list(REQUIRED_COLUMNS)].isnull().all(axis=1)
    if blank_mask.any():
        result.warnings.append(f"Dropped {blank_mask.sum()} fully-blank row(s).")
        df = df[~blank_mask].copy()

    # ── 4. NaN checks (required fields) ──────────────────────────────────────
    for col in REQUIRED_COLUMNS:
        null_rows = df.index[df[col].isnull()].tolist()
        if null_rows:
            display_rows = [
                r + 2 for r in null_rows[:5]
            ]  # +2: 1 for header, 1 for 0-index
            result.errors.append(
                f"Column '{col}' has missing values at row(s): {display_rows}"
                + (" …" if len(null_rows) > 5 else "")
            )
    if result.errors:
        return result

    # ── 5. Ticker normalisation & format check ────────────────────────────────
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    bad_tickers = df[~df["ticker"].str.match(r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$")]
    if not bad_tickers.empty:
        bads = bad_tickers["ticker"].unique().tolist()[:10]
        result.warnings.append(
            f"Unusual ticker symbol(s) — verify they are valid US tickers: {bads}"
        )

    # ── 6. transaction_type ───────────────────────────────────────────────────
    df["transaction_type"] = df["transaction_type"].astype(str).str.strip().str.lower()
    invalid_mask = ~df["transaction_type"].isin(VALID_TRANSACTION_TYPES)
    if invalid_mask.any():
        bad_vals = df.loc[invalid_mask, "transaction_type"].unique().tolist()
        bad_rows = [r + 2 for r in df.index[invalid_mask].tolist()[:5]]
        result.errors.append(
            f"Invalid transaction_type value(s) {bad_vals} at row(s) {bad_rows}. "
            "Allowed values: Buy, Sell (case-insensitive)."
        )
        return result

    # ── 7. Date parsing ───────────────────────────────────────────────────────
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        parsed_dates = pd.to_datetime(df["date"], errors="coerce", utc=False)

    bad_date_rows = df.index[parsed_dates.isnull()].tolist()
    if bad_date_rows:
        display_rows = [r + 2 for r in bad_date_rows[:5]]
        result.errors.append(
            f"Cannot parse date at row(s) {display_rows}. Use YYYY-MM-DD or MM/DD/YYYY format."
        )
        return result

    df["date"] = parsed_dates

    future_mask = df["date"] > pd.Timestamp.now(tz=None)
    if future_mask.any():
        future_tickers = df.loc[future_mask, "ticker"].unique().tolist()
        result.warnings.append(
            f"{future_mask.sum()} transaction(s) have future dates (tickers: {future_tickers}). "
            "These are included but may affect XIRR."
        )

    # ── 8. Numeric fields ─────────────────────────────────────────────────────
    for col in ("quantity", "price"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
        bad_rows = df.index[df[col].isnull()].tolist()
        if bad_rows:
            display_rows = [r + 2 for r in bad_rows[:5]]
            result.errors.append(
                f"Non-numeric value in '{col}' at row(s) {display_rows}."
            )

    if result.errors:
        return result

    nonpos_qty = df.index[df["quantity"] <= 0].tolist()
    if nonpos_qty:
        result.errors.append(
            f"'quantity' must be > 0. Offending row(s): {[r + 2 for r in nonpos_qty[:5]]}"
        )

    nonpos_price = df.index[df["price"] <= 0].tolist()
    if nonpos_price:
        result.errors.append(
            f"'price' must be > 0. Offending row(s): {[r + 2 for r in nonpos_price[:5]]}"
        )

    if result.errors:
        return result

    # ── 9. Duplicate detection ────────────────────────────────────────────────
    dup_cols = ["ticker", "date", "transaction_type", "quantity", "price"]
    dup_mask = df.duplicated(subset=dup_cols, keep="first")
    if dup_mask.any():
        result.warnings.append(
            f"{dup_mask.sum()} duplicate row(s) detected and removed (identical ticker/date/"
            "type/quantity/price)."
        )
        df = df[~dup_mask].copy()

    # ── 10. Oversell check ────────────────────────────────────────────────────
    oversell_tickers = _check_oversell(df)
    for ticker, detail in oversell_tickers.items():
        result.warnings.append(
            f"Ticker {ticker}: sell quantity exceeds available lots on {detail['date'].strftime('%Y-%m-%d')} "
            f"(attempted to sell {detail['attempted']:.4f}, available {detail['available']:.4f}). "
            "FIFO will cap the sell at available inventory."
        )

    # ── 11. Final sort & normalise ────────────────────────────────────────────
    # On same date, process buys before sells to maximise inventory availability
    df["_tx_order"] = df["transaction_type"].map({"buy": 0, "sell": 1})
    df = (
        df.sort_values(["date", "_tx_order"])
        .drop(columns=["_tx_order"])
        .reset_index(drop=True)
    )
    df["transaction_type"] = df["transaction_type"].str.capitalize()

    result.df = df
    return result


def _check_oversell(df: pd.DataFrame) -> dict:
    """
    Pre-flight oversell detection. Returns {ticker: {date, attempted, available}}.
    Only reports the first oversell event per ticker.
    """
    oversells = {}
    for ticker, group in df.groupby("ticker"):
        group = group.sort_values(["date", "transaction_type"])
        inventory = 0.0
        for _, row in group.iterrows():
            qty = float(row["quantity"])
            if row["transaction_type"].lower() == "buy":
                inventory += qty
            else:
                if qty > inventory + 1e-9 and ticker not in oversells:
                    oversells[str(ticker)] = {
                        "date": row["date"],
                        "attempted": qty,
                        "available": inventory,
                    }
                inventory = max(0.0, inventory - qty)
    return oversells


def get_display_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return a nicely-formatted copy for Streamlit display."""
    display = df.copy()
    display["date"] = display["date"].dt.strftime("%Y-%m-%d")
    display["price"] = display["price"].map("${:,.2f}".format)
    display["quantity"] = display["quantity"].map("{:,.4f}".format)
    display.columns = [c.replace("_", " ").title() for c in display.columns]
    return display
