"""
Gap Mean Reversion Dashboard — Trading Terminal
NSE Gap Mean Reversion Strategy | Unified Single-Page Layout
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
import math
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Gap MR Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# DARK THEME CSS
# ─────────────────────────────────────────────

st.markdown(
    """
    <style>
    .stApp { background-color: #0a0d14; color: #e8eaf6; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0e1117 !important; border-right: 1px solid #1e2130; }
    [data-testid="stSidebar"] * { color: #c5cae9 !important; }

    /* Top metric cards */
    .stat-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 16px 18px;
        text-align: center;
    }
    .stat-label { font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 1.2px; }
    .stat-value { font-size: 26px; font-weight: 700; color: #f9fafb; margin-top: 4px; }
    .stat-sub { font-size: 12px; color: #9ca3af; margin-top: 2px; }

    /* Trade plan cards */
    .trade-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .trade-card-label { font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 1.2px; }
    .trade-card-value { font-size: 32px; font-weight: 800; margin: 6px 0 4px; }
    .trade-card-sub { font-size: 12px; color: #6b7280; }

    /* Signal card */
    .signal-card-long {
        background: linear-gradient(135deg, #052e16 0%, #064e3b 100%);
        border: 1px solid #059669;
        border-radius: 14px;
        padding: 24px 28px;
        text-align: center;
    }
    .signal-card-short {
        background: linear-gradient(135deg, #450a0a 0%, #7f1d1d 100%);
        border: 1px solid #dc2626;
        border-radius: 14px;
        padding: 24px 28px;
        text-align: center;
    }
    .signal-card-none {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 14px;
        padding: 24px 28px;
        text-align: center;
    }
    .signal-text { font-size: 36px; font-weight: 900; letter-spacing: 2px; }
    .signal-long-text { color: #34d399; }
    .signal-short-text { color: #f87171; }
    .signal-none-text { color: #6b7280; }
    .signal-meta { font-size: 14px; color: #9ca3af; margin-top: 8px; }

    /* Section header */
    .section-header {
        font-size: 12px;
        font-weight: 600;
        color: #4b5563;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 20px 0 10px;
        border-bottom: 1px solid #1f2937;
        padding-bottom: 6px;
    }

    /* Market stats bar */
    .stat-bar {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 12px 16px;
        display: flex;
        gap: 32px;
        align-items: center;
        flex-wrap: wrap;
    }
    .stat-bar-item { display: inline-flex; flex-direction: column; }
    .stat-bar-label { font-size: 10px; color: #4b5563; text-transform: uppercase; letter-spacing: 1px; }
    .stat-bar-val { font-size: 15px; font-weight: 600; color: #e5e7eb; }

    /* Position size sidebar */
    .pos-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #1f2937;
        font-size: 13px;
    }
    .pos-label { color: #6b7280; }
    .pos-val { color: #e5e7eb; font-weight: 600; }

    /* Disclaimer */
    .disclaimer {
        background: #0e1117;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 11px;
        color: #4b5563;
        margin-top: 16px;
    }

    /* Streamlit overrides */
    div[data-testid="stMetricValue"] { color: #f9fafb; }
    h1, h2, h3, h4 { color: #e8eaf6 !important; }
    .stDataFrame { border-radius: 8px; }
    .stExpander { background: #111827 !important; border: 1px solid #1f2937 !important; border-radius: 10px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# SECTOR DATABASE
# ─────────────────────────────────────────────

SECTOR_DB: dict[str, list[str]] = {
    "BANKING": [
        "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS",
        "INDUSINDBK.NS", "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "UNIONBANK.NS",
        "FEDERALBNK.NS", "IDFCFIRSTB.NS", "BANDHANBNK.NS", "AUBANK.NS", "RBLBANK.NS",
        "YESBANK.NS",
    ],
    "IT": [
        "TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS",
        "LTIM.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "HEXAWARE.NS",
        "KPITTECH.NS", "TATAELXSI.NS", "OFSS.NS", "NIITTECH.NS", "MASTEK.NS",
        "CYIENT.NS",
    ],
    "PHARMA": [
        "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "BIOCON.NS",
        "APOLLOHOSP.NS", "AUROPHARMA.NS", "TORNTPHARM.NS", "LUPIN.NS", "ALKEM.NS",
        "GLENMARK.NS", "IPCA.NS", "NATCO.NS", "GRANULES.NS", "LAURUSLABS.NS",
        "ABBOTINDIA.NS",
    ],
    "AUTO": [
        "MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS",
        "EICHERMOT.NS", "ASHOKLEY.NS", "TVSMOTOR.NS", "MOTHERSON.NS", "BOSCHLTD.NS",
        "EXIDEIND.NS", "AMARAJABAT.NS", "BALKRISIND.NS", "CEAT.NS", "MRF.NS",
        "SONACOMS.NS",
    ],
    "ENERGY": [
        "RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS", "HINDPETRO.NS",
        "GAIL.NS", "PETRONET.NS", "COALINDIA.NS", "NTPC.NS", "POWERGRID.NS",
        "ADANIGREEN.NS", "TATAPOWER.NS", "TORNTPOWER.NS", "CESC.NS", "NHPC.NS",
        "ADANIPORTS.NS",
    ],
    "FMCG": [
        "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS",
        "MARICO.NS", "GODREJCP.NS", "COLPAL.NS", "EMAMILTD.NS", "TATACONSUM.NS",
        "JUBLFOOD.NS", "MCDOWELL-N.NS", "RADICO.NS", "VARUNBEV.NS", "PGHH.NS",
        "VENKEYS.NS",
    ],
}

ALL_TICKERS: list[str] = [t for tickers in SECTOR_DB.values() for t in tickers]
TICKER_TO_SECTOR: dict[str, str] = {
    t: sector for sector, tickers in SECTOR_DB.items() for t in tickers
}

# ─────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────

@dataclass
class StockSignal:
    ticker: str
    sector: str
    signal: str
    gap_pct: float
    entry: float
    stop_loss: float
    target1: float
    target2: float
    target3: float
    reference_price: float
    atr: float
    current_price: float


@dataclass
class PositionSize:
    risk_per_share: float
    quantity: int
    capital_required: float
    potential_reward: float
    rr_ratio: float


@dataclass
class BacktestResult:
    total_trades: int
    win_rate: float
    avg_return: float
    profit_factor: float
    best_trade: float
    worst_trade: float
    equity_curve: list[float]
    trade_returns: list[float]
    trade_dates: list[str]

# ─────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def fetch_ohlcv(ticker: str, period: str = "3mo") -> Optional[pd.DataFrame]:
    try:
        df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        if df is None or df.empty or len(df) < 25:
            return None
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df
    except Exception:
        return None


def compute_atr(df: pd.DataFrame, period: int = 14) -> float:
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    return float(tr.rolling(period).mean().iloc[-1])


# ─────────────────────────────────────────────
# STRATEGY LOGIC
# ─────────────────────────────────────────────

def compute_reference_price(prev_open: float, prev_close: float) -> float:
    return (prev_open + prev_close) / 2.0


def compute_gap_pct(today_open: float, reference_price: float) -> float:
    if reference_price == 0:
        return 0.0
    return (today_open - reference_price) / reference_price * 100.0


def determine_signal(gap_pct: float) -> str:
    if gap_pct > 2.0:
        return "SHORT"
    elif gap_pct < -2.0:
        return "LONG"
    return "NO SIGNAL"



def compute_stop_loss(signal: str, entry: float, today_low: float, today_high: float, atr: float) -> float:
    if signal == "LONG":
        return min(today_low, entry - 1.5 * atr)
    elif signal == "SHORT":
        return max(today_high, entry + 1.5 * atr)
    return entry


def compute_targets(entry: float, reference_price: float) -> tuple[float, float, float]:
    reversion = reference_price - entry
    return (
        round(entry + reversion * 0.50, 2),
        round(entry + reversion * 1.00, 2),
        round(entry + reversion * 1.50, 2),
    )

def compute_position_size(entry: float, stop_loss: float, target1: float, max_risk: float) -> PositionSize:
    zero = PositionSize(0, 0, 0, 0, 0)
    try:
        entry = float(entry)
        stop_loss = float(stop_loss)
        target1 = float(target1)
        max_risk = float(max_risk)
    except (TypeError, ValueError):
        return zero

    if any(math.isnan(v) for v in [entry, stop_loss, target1, max_risk]):
        return zero
    if entry <= 0 or stop_loss <= 0 or max_risk <= 0:
        return zero

    risk_per_share = abs(entry - stop_loss)
    if risk_per_share <= 0:
        return zero

    quantity = math.floor(max_risk / risk_per_share)
    capital_required = quantity * entry
    potential_reward = quantity * abs(target1 - entry)
    rr_ratio = potential_reward / max_risk if max_risk > 0 else 0.0

    return PositionSize(
        risk_per_share=round(risk_per_share, 2),
        quantity=quantity,
        capital_required=round(capital_required, 2),
        potential_reward=round(potential_reward, 2),
        rr_ratio=round(rr_ratio, 2),
    )


# SIGNAL GENERATION

def analyze_stock(ticker: str) -> Optional[StockSignal]:
    try:
        df = fetch_ohlcv(ticker)
        if df is None or df.empty or len(df) < 22:
            return None

        prev_row = df.iloc[-2]
        today_row = df.iloc[-1]

        prev_open = float(prev_row["Open"])
        prev_close = float(prev_row["Close"])
        today_open = float(today_row["Open"])
        today_close = float(today_row["Close"])

        if any(math.isnan(v) or v <= 0 for v in [prev_open, prev_close, today_open, today_close]):
            return None

        reference_price = compute_reference_price(prev_open, prev_close)
        gap_pct = compute_gap_pct(today_open, reference_price)
        signal = determine_signal(gap_pct)

        # ATR must be known at entry, so exclude today's forming candle.
        atr = compute_atr(df.iloc[:-1])
        if math.isnan(atr) or atr <= 0:
            atr = 0.01

        entry = today_open
        # At the open, today's known high/low are the open; do not let the plan drift with the forming candle.
        stop_loss = compute_stop_loss(signal, entry, today_open, today_open, atr)
        t1, t2, t3 = compute_targets(entry, reference_price)

        sig_obj = StockSignal(
            ticker=ticker,
            sector=TICKER_TO_SECTOR.get(ticker, "UNKNOWN"),
            signal=signal,
            gap_pct=round(gap_pct, 2),
            entry=round(entry, 2),
            stop_loss=round(stop_loss, 2),
            target1=t1,
            target2=t2,
            target3=t3,
            reference_price=round(reference_price, 2),
            atr=round(atr, 2),
            current_price=round(today_close, 2),
        )

        required_fields = ["signal", "entry", "stop_loss", "target1", "target2", "target3"]
        for field in required_fields:
            val = getattr(sig_obj, field, None)
            if val is None:
                return None
            if isinstance(val, float) and math.isnan(val):
                return None
        return sig_obj
    except Exception as exc:
        print(f"[DEBUG] analyze_stock({ticker}) failed: {exc}")
        return None


@st.cache_data(ttl=300, show_spinner=False)
def scan_all_stocks(tickers: tuple[str, ...]) -> list[StockSignal]:
    results = []
    for ticker in tickers:
        sig = analyze_stock(ticker)
        if sig is not None:
            results.append(sig)
    return results


# BACKTEST

@st.cache_data(ttl=600, show_spinner=False)
def run_backtest(ticker: str, lookback_days: int = 60) -> Optional[BacktestResult]:
    df = fetch_ohlcv(ticker, period="6mo")
    if df is None or len(df) < 30:
        return None

    df = df.tail(lookback_days + 5).copy()
    trade_returns: list[float] = []
    trade_dates: list[str] = []
    equity = 10000.0
    equity_curve: list[float] = [equity]

    # Exclude the latest row so a currently forming candle is not backtested as completed data.
    for i in range(1, len(df) - 1):
        try:
            prev_open = float(df["Open"].iloc[i - 1])
            prev_close = float(df["Close"].iloc[i - 1])
            today_open = float(df["Open"].iloc[i])
            today_close = float(df["Close"].iloc[i])

            ref = compute_reference_price(prev_open, prev_close)
            gap_pct = compute_gap_pct(today_open, ref)
            signal = determine_signal(gap_pct)
            if signal == "NO SIGNAL":
                continue

            if signal == "LONG":
                ret = (today_close - today_open) / today_open * 100.0
            else:
                ret = (today_open - today_close) / today_open * 100.0

            trade_returns.append(round(ret, 3))
            trade_dates.append(str(df.index[i].date()))
            equity *= 1 + ret / 100.0
            equity_curve.append(round(equity, 2))
        except Exception:
            continue

    if not trade_returns:
        return None

    wins = [r for r in trade_returns if r > 0]
    losses = [r for r in trade_returns if r <= 0]
    gross_profit = sum(wins) if wins else 0.0
    gross_loss = abs(sum(losses)) if losses else 0.0
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else float("inf")

    return BacktestResult(
        total_trades=len(trade_returns),
        win_rate=round(len(wins) / len(trade_returns) * 100.0, 1),
        avg_return=round(float(np.mean(trade_returns)), 3),
        profit_factor=profit_factor,
        best_trade=round(max(trade_returns), 2),
        worst_trade=round(min(trade_returns), 2),
        equity_curve=equity_curve,
        trade_returns=trade_returns,
        trade_dates=trade_dates,
    )


# CHARTING AND TABLES

def build_candlestick_chart(df: pd.DataFrame, signal: StockSignal, ticker: str) -> go.Figure:
    df_plot = df.tail(60).copy()
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Candlestick(
        x=df_plot.index,
        open=df_plot["Open"],
        high=df_plot["High"],
        low=df_plot["Low"],
        close=df_plot["Close"],
        name="OHLC",
    ))

    if signal.signal != "NO SIGNAL":
        lines = [
            (signal.entry, "Entry", "#60a5fa"),
            (signal.stop_loss, "Stop Loss", "#f87171"),
            (signal.target1, "Target 1", "#34d399"),
            (signal.target2, "Target 2", "#6ee7b7"),
            (signal.target3, "Target 3", "#a7f3d0"),
            (signal.reference_price, "Reference", "#fde68a"),
        ]
        for price, label, color in lines:
            fig.add_hline(y=price, line_color=color, line_dash="dot", annotation_text=label)

    fig.update_layout(
        title=f"{ticker.replace('.NS', '')} - Gap Mean Reversion",
        paper_bgcolor="#0a0d14",
        plot_bgcolor="#0a0d14",
        font=dict(color="#e5e7eb"),
        height=520,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_rangeslider_visible=False,
    )
    fig.update_xaxes(gridcolor="#1f2937")
    fig.update_yaxes(gridcolor="#1f2937")
    return fig


def signals_to_df(signals: list[StockSignal]) -> pd.DataFrame:
    rows = []
    for s in signals:
        rows.append({
            "Ticker": s.ticker.replace(".NS", ""),
            "Signal": s.signal,
            "Gap %": s.gap_pct,
            "Entry": s.entry,
            "Stop Loss": s.stop_loss,
            "Target 1": s.target1,
            "Target 2": s.target2,
            "Target 3": s.target3,
        })
    return pd.DataFrame(rows)


def render_scanner_table(signals: list[StockSignal]) -> None:
    df = signals_to_df(signals)
    if df.empty:
        st.info("No signals match the current filters.")
        return
    st.dataframe(
        df.style.format({
            "Gap %": "{:+.2f}%",
            "Entry": "{:.2f}",
            "Stop Loss": "{:.2f}",
            "Target 1": "{:.2f}",
            "Target 2": "{:.2f}",
            "Target 3": "{:.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        data=csv,
        file_name=f"gap_signals_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )


# MAIN

def main() -> None:
    st.title("Gap MR Terminal")

    with st.sidebar:
        st.markdown("#### Stock Selection")
        sector = st.selectbox("Sector", list(SECTOR_DB.keys()))
        tickers_in_sector = SECTOR_DB[sector]
        ticker_labels = [t.replace(".NS", "") for t in tickers_in_sector]
        ticker_label = st.selectbox("Stock", ticker_labels)
        ticker_sel = tickers_in_sector[ticker_labels.index(ticker_label)]

        st.markdown("---")
        st.markdown("#### Risk Management")
        max_risk = st.number_input(
            "Max Risk Per Trade (Rs.)",
            min_value=100.0,
            max_value=100000.0,
            value=1500.0,
            step=100.0,
        )

        run_scan = st.button("Refresh Full Scan", type="primary", use_container_width=True)
        st.caption("Data via Yahoo Finance. Not investment advice.")

    with st.spinner("Loading..."):
        sig = analyze_stock(ticker_sel)
        df = fetch_ohlcv(ticker_sel)

    if sig is None or df is None or df.empty:
        st.warning("Could not load data for the selected stock. Try another.")
        return

    cards = [
        ("Current Price", f"{sig.current_price:,.2f}", sig.sector),
        ("Gap %", f"{sig.gap_pct:+.2f}%", "vs reference price"),
        ("ATR (14)", f"{sig.atr:,.2f}", "prior completed candles"),
        ("Reference", f"{sig.reference_price:,.2f}", "prev open/close midpoint"),
    ]
    for col, (label, value, sub) in zip(st.columns(4), cards):
        col.markdown(
            f'<div class="stat-card"><div class="stat-label">{label}</div>'
            f'<div class="stat-value">{value}</div><div class="stat-sub">{sub}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    left_col, right_col = st.columns([1, 2])

    with left_col:
        if sig.signal == "LONG":
            css_cls = "signal-card-long"
            txt_cls = "signal-long-text"
        elif sig.signal == "SHORT":
            css_cls = "signal-card-short"
            txt_cls = "signal-short-text"
        else:
            css_cls = "signal-card-none"
            txt_cls = "signal-none-text"
        st.markdown(
            f'<div class="{css_cls}"><div class="signal-text {txt_cls}">{sig.signal}</div></div>',
            unsafe_allow_html=True,
        )

    with right_col:
        if sig.signal != "NO SIGNAL":
            trade_cols = st.columns(3)
            for col, label, value in [
                (trade_cols[0], "ENTRY", sig.entry),
                (trade_cols[1], "STOP LOSS", sig.stop_loss),
                (trade_cols[2], "TARGET 1", sig.target1),
            ]:
                col.markdown(
                    f'<div class="trade-card"><div class="trade-card-label">{label}</div>'
                    f'<div class="trade-card-value">{value:,.2f}</div></div>',
                    unsafe_allow_html=True,
                )
            tcols = st.columns(3)
            tcols[0].metric("Target 1 (50% rev)", f"{sig.target1:,.2f}")
            tcols[1].metric("Target 2 (100% rev)", f"{sig.target2:,.2f}")
            tcols[2].metric("Target 3 (150% rev)", f"{sig.target3:,.2f}")
        else:
            st.info("No active gap signal for this stock today. Gap is within the 2% threshold.")

    if sig.signal != "NO SIGNAL":
        pos = compute_position_size(sig.entry, sig.stop_loss, sig.target1, max_risk)
        st.markdown("#### Position Size")
        pcols = st.columns(5)
        pcols[0].metric("Risk / Share", f"{pos.risk_per_share:.2f}")
        pcols[1].metric("Quantity", f"{pos.quantity}")
        pcols[2].metric("Capital Req.", f"{pos.capital_required:,.0f}")
        pcols[3].metric("Pot. Reward", f"{pos.potential_reward:,.0f}")
        pcols[4].metric("R/R Ratio", f"{pos.rr_ratio:.2f}x")

    st.plotly_chart(build_candlestick_chart(df, sig, ticker_sel), use_container_width=True)

    if "signals" not in st.session_state or run_scan:
        with st.spinner("Scanning NSE universe..."):
            st.session_state["signals"] = scan_all_stocks(tuple(ALL_TICKERS))
    signals: list[StockSignal] = st.session_state.get("signals", [])

    with st.expander("Show Market Scanner", expanded=False):
        active = [s for s in signals if s.signal != "NO SIGNAL"]
        sig_filter = st.multiselect(
            "Signal",
            options=["LONG", "SHORT"],
            default=["LONG", "SHORT"],
            key="scan_sig",
        )
        filtered = [s for s in active if s.signal in sig_filter]
        st.caption(f"{len(filtered)} signals")
        render_scanner_table(filtered)

    with st.expander("Historical Performance (Backtest)", expanded=False):
        lookback = st.number_input("Lookback (days)", min_value=20, max_value=250, value=60, step=10)
        if st.button("Run Backtest", type="primary"):
            result = run_backtest(ticker_sel, lookback)
            if result is None:
                st.error("Not enough data or no signals found in this period.")
            else:
                bcols = st.columns(6)
                bcols[0].metric("Trades", result.total_trades)
                bcols[1].metric("Win Rate", f"{result.win_rate:.1f}%")
                bcols[2].metric("Avg Return", f"{result.avg_return:+.2f}%")
                bcols[3].metric("Profit Factor", f"{result.profit_factor:.2f}")
                bcols[4].metric("Best Trade", f"{result.best_trade:+.2f}%")
                bcols[5].metric("Worst Trade", f"{result.worst_trade:+.2f}%")

                trade_df = pd.DataFrame({
                    "Trade #": list(range(1, len(result.trade_returns) + 1)),
                    "Date": result.trade_dates,
                    "Return %": result.trade_returns,
                    "Equity": result.equity_curve[1:],
                })
                st.dataframe(trade_df, use_container_width=True, hide_index=True)

    st.markdown(
        '<div class="disclaimer">Past data is for informational purposes only. '
        'This is not investment advice. Trade at your own risk.</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
