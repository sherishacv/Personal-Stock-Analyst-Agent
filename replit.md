# Stock Analyst Agent

An AI-powered personal stock portfolio analyst built with Streamlit. Upload your US stock transaction history (CSV) and get live portfolio analysis, performance metrics, XIRR, and interactive chat with a Groq LLM analyst.

## Run & Operate

- **Workflow:** `Stock Analyst App` — runs `cd stock-analyst && .venv/bin/streamlit run app.py --server.port 5000`
- **Sample data:** `stock-analyst/sample_portfolio.csv` — 30 transactions across AAPL, MSFT, GOOGL, NVDA, TSLA, AMZN, META

## Stack

- **Runtime:** Python 3.12 via Nix + uv virtual environment at `stock-analyst/.venv`
- **Package management:** uv (strictly)
- **UI:** Streamlit 1.59
- **Market data:** yfinance (live prices, 5-day window)
- **LLM:** Groq (`llama-3.3-70b-versatile`)
- **Charts:** Plotly
- **Math:** scipy (XIRR via Brent root-finding), numpy, pandas

## Project Structure

```
stock-analyst/
├── app.py                        # Entry point, tab layout
├── pyproject.toml                # uv project dependencies
├── .venv/                        # uv virtual environment (Python 3.12)
├── .streamlit/config.toml        # Server config (port 5000, headless)
├── sample_portfolio.csv          # Example CSV for testing
├── utils/
│   ├── data_processing.py        # CSV load + validation
│   ├── portfolio_math.py         # FIFO cost basis, XIRR, metrics
│   └── llm_agent.py              # Groq client, portfolio summary, chat
└── components/
    ├── tab1_upload.py             # Data Upload tab
    ├── tab2_portfolio.py          # Portfolio View tab
    ├── tab3_performance.py        # Historical Performance tab
    └── tab4_chat.py               # AI Chat tab
```

## CSV Format

Required columns: `ticker`, `date`, `transaction_type` (Buy/Sell), `quantity`, `price`

## Architecture Decisions

- **FIFO cost basis:** Implemented in `portfolio_math.py` using a deque-based lot queue per ticker. Sells consume the oldest lots first.
- **XIRR:** Implemented with `scipy.optimize.brentq` on NPV function — buys = negative cashflows, sells + current value = positive cashflows.
- **uv venv path:** Created at `stock-analyst/.venv` using Nix Python at `/nix/store/sj74dzrygwdxpb54fv7zc6ry75ay4f3n-python-wrapped-0.1.0/bin/python3`. The system `.pythonlibs` does not contain a Python binary, only uv tooling.
- **State flow:** `transactions_df` → `holdings_df` → `performance_metrics` all stored in `st.session_state`. Tab 3 and 4 require Tab 2 to have been visited first (to populate `holdings_df`).
- **Groq model:** `llama-3.3-70b-versatile` — balances speed and quality for portfolio context windows.

## User Preferences

- Use `uv` strictly for all Python package management
- No manual transaction entry — CSV upload only
- FIFO method for cost basis accounting

## Gotchas

- Run `uv pip install <pkg>` from inside `stock-analyst/` with `.venv` active to add packages
- yfinance uses a 5-day lookback window for current prices; weekend/holiday prices use the last available close
- Tab 3 and Tab 4 require visiting Tab 2 first (fetches current prices and populates session state)
- To reinstall the venv: `cd stock-analyst && uv venv --python <nix-python-path> .venv && uv pip install -r pyproject.toml`

## Pointers

- See the `pnpm-workspace` skill for monorepo workspace structure
- See the `streamlit` skill for Streamlit-specific configuration
