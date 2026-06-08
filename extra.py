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
    confidence_score: float
    confidence_label: str
    entry: float
    stop_loss: float
    target1: float
    target2: float
    target3: float
    reference_price: float
    atr: float
    current_price: float
    rel_volume: float
    dma20: float
    rsi: float = 50.0


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


def compute_20dma(df: pd.DataFrame) -> float:
    return float(df["Close"].rolling(20).mean().iloc[-1])


def compute_relative_volume(df: pd.DataFrame) -> float:
    avg_vol = df["Volume"].rolling(20).mean().iloc[-2]
    today_vol = df["Volume"].iloc[-1]
    if avg_vol and avg_vol > 0:
        return float(today_vol / avg_vol)
    return 1.0


def compute_rsi(df: pd.DataFrame, period: int = 14) -> float:
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    val = rsi.iloc[-1]
    return float(val) if not np.isnan(val) else 50.0

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


def compute_confidence_score(
    gap_pct: float, atr: float, entry: float, dma20: float, rel_volume: float,
) -> tuple[float, str]:
    gap_abs = abs(gap_pct)
    gap_score = min(gap_abs / 10.0 * 25.0, 25.0)

    if atr > 0 and entry > 0:
        gap_in_price = abs(gap_pct / 100.0 * entry)
        atr_ratio = gap_in_price / atr
        atr_score = min(atr_ratio / 2.0 * 25.0, 25.0)
    else:
        atr_score = 0.0

    if dma20 > 0 and entry > 0:
        dma_dist_pct = abs(entry - dma20) / dma20 * 100.0
        dma_score = min(dma_dist_pct / 5.0 * 25.0, 25.0)
    else:
        dma_score = 0.0

    rvol_score = min((rel_volume - 1.0) / 3.0 * 25.0, 25.0) if rel_volume > 1.0 else 0.0

    total = max(0.0, min(100.0, gap_score + atr_score + dma_score + rvol_score))
    label = "HIGH" if total >= 70 else "MEDIUM" if total >= 40 else "LOW"
    return round(total, 1), label


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
    # Guard against None, NaN, or non-positive inputs
    _zero = PositionSize(0, 0, 0, 0, 0)
    try:
        entry     = float(entry)
        stop_loss = float(stop_loss)
        target1   = float(target1)
        max_risk  = float(max_risk)
    except (TypeError, ValueError):
        return _zero

    if math.isnan(entry) or math.isnan(stop_loss) or math.isnan(target1):
        return _zero
    if entry <= 0 or stop_loss <= 0:
        return _zero

    risk_per_share = abs(entry - stop_loss)
    if risk_per_share <= 0:
        return _zero

    quantity = max(0, math.floor(max_risk / risk_per_share))
    capital_required = round(quantity * entry, 2)
    reward_per_share = abs(target1 - entry)
    potential_reward = round(quantity * reward_per_share, 2)
    rr_ratio = round(potential_reward / max_risk, 2) if max_risk > 0 else 0.0
    return PositionSize(
        risk_per_share=round(risk_per_share, 2),
        quantity=quantity,
        capital_required=capital_required,
        potential_reward=potential_reward,
        rr_ratio=rr_ratio,
    )

# ─────────────────────────────────────────────
# SIGNAL GENERATION
# ─────────────────────────────────────────────

def analyze_stock(ticker: str) -> Optional[StockSignal]:
    # Problem 3 fix: entire function wrapped in try/except — never crashes on bad data
    try:
        df = fetch_ohlcv(ticker)
        if df is None or df.empty or len(df) < 22:
            return None

        prev_row  = df.iloc[-2]
        today_row = df.iloc[-1]

        prev_open   = float(prev_row["Open"])
        prev_close  = float(prev_row["Close"])
        today_open  = float(today_row["Open"])
        today_high  = float(today_row["High"])
        today_low   = float(today_row["Low"])
        today_close = float(today_row["Close"])

        # Guard against zero/NaN OHLCV
        if any(math.isnan(v) or v <= 0 for v in [prev_open, prev_close, today_open, today_close]):
            return None

        reference_price = compute_reference_price(prev_open, prev_close)
        gap_pct  = compute_gap_pct(today_open, reference_price)
        signal   = determine_signal(gap_pct)

        atr        = compute_atr(df)
        dma20      = compute_20dma(df)
        rel_volume = compute_relative_volume(df)
        rsi        = compute_rsi(df)

        # Guard zero ATR (Problem 3/robustness)
        if math.isnan(atr) or atr <= 0:
            atr = 0.01  # minimal non-zero fallback so stop-loss math doesn't divide by zero

        entry     = today_open
        stop_loss = compute_stop_loss(signal, entry, today_low, today_high, atr)
        t1, t2, t3 = compute_targets(entry, reference_price)
        conf_score, conf_label = compute_confidence_score(gap_pct, atr, entry, dma20, rel_volume)

        sig_obj = StockSignal(
            ticker=ticker,
            sector=TICKER_TO_SECTOR.get(ticker, "UNKNOWN"),
            signal=signal,
            gap_pct=round(gap_pct, 2),
            confidence_score=conf_score,
            confidence_label=conf_label,
            entry=round(entry, 2),
            stop_loss=round(stop_loss, 2),
            target1=t1,
            target2=t2,
            target3=t3,
            reference_price=round(reference_price, 2),
            atr=round(atr, 2),
            current_price=round(today_close, 2),
            rel_volume=round(rel_volume, 2),
            dma20=round(dma20, 2),
            rsi=round(rsi, 1),
        )

        # Problem 4 fix: validate all required signal fields are present and non-NaN
        required_fields = ["signal", "entry", "stop_loss", "target1", "target2", "target3", "confidence_score"]
        for field in required_fields:
            val = getattr(sig_obj, field, None)
            if val is None:
                return None
            if isinstance(val, float) and math.isnan(val):
                return None

        return sig_obj

    except Exception as exc:
        # Problem 3 fix: log and continue — never propagate to Streamlit UI
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

# ─────────────────────────────────────────────
# BACKTEST
# ─────────────────────────────────────────────

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

            ret = (today_close - today_open) / today_open * 100.0 if signal == "LONG" else (today_open - today_close) / today_open * 100.0
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
    win_rate = len(wins) / len(trade_returns) * 100.0
    gross_profit = sum(wins) if wins else 0.0
    gross_loss = abs(sum(losses)) if losses else 0.0
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else float("inf")

    return BacktestResult(
        total_trades=len(trade_returns),
        win_rate=round(win_rate, 1),
        avg_return=round(float(np.mean(trade_returns)), 3),
        profit_factor=profit_factor,
        best_trade=round(max(trade_returns), 2),
        worst_trade=round(min(trade_returns), 2),
        equity_curve=equity_curve,
        trade_returns=trade_returns,
        trade_dates=trade_dates,
    )

# ─────────────────────────────────────────────
# CHART
# ─────────────────────────────────────────────

def build_candlestick_chart(df: pd.DataFrame, signal: StockSignal, ticker: str) -> go.Figure:
    df_plot = df.tail(60).copy()
    dma_series = df["Close"].rolling(20).mean().reindex(df_plot.index)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.78, 0.22],
        vertical_spacing=0.03,
    )

    fig.add_trace(
        go.Candlestick(
            x=df_plot.index,
            open=df_plot["Open"],
            high=df_plot["High"],
            low=df_plot["Low"],
            close=df_plot["Close"],
            name="Price",
            increasing_line_color="#34d399",
            decreasing_line_color="#f87171",
        ),
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df_plot.index, y=dma_series,
            name="20 DMA",
            line=dict(color="#fbbf24", width=1.5, dash="dot"),
        ),
        row=1, col=1,
    )

    last_date = df_plot.index[-1]
    first_date = df_plot.index[0]

    def _hline(y_val, color, label, dash="dash"):
        return go.Scatter(
            x=[first_date, last_date], y=[y_val, y_val],
            mode="lines", name=label,
            line=dict(color=color, width=1.5, dash=dash),
        )

    if signal.signal != "NO SIGNAL":
        fig.add_trace(_hline(signal.entry, "#60a5fa", f"Entry ₹{signal.entry:.2f}", "solid"), row=1, col=1)
        fig.add_trace(_hline(signal.stop_loss, "#f87171", f"SL ₹{signal.stop_loss:.2f}"), row=1, col=1)
        fig.add_trace(_hline(signal.target1, "#34d399", f"T1 ₹{signal.target1:.2f}"), row=1, col=1)
        fig.add_trace(_hline(signal.target2, "#6ee7b7", f"T2 ₹{signal.target2:.2f}"), row=1, col=1)
        fig.add_trace(_hline(signal.target3, "#a7f3d0", f"T3 ₹{signal.target3:.2f}"), row=1, col=1)
        fig.add_trace(_hline(signal.reference_price, "#fde68a", f"Ref ₹{signal.reference_price:.2f}", "dot"), row=1, col=1)

    vol_colors = [
        "#34d399" if float(df_plot["Close"].iloc[i]) >= float(df_plot["Open"].iloc[i]) else "#f87171"
        for i in range(len(df_plot))
    ]
    fig.add_trace(
        go.Bar(x=df_plot.index, y=df_plot["Volume"], name="Volume", marker_color=vol_colors, opacity=0.6),
        row=2, col=1,
    )

    fig.update_layout(
        paper_bgcolor="#0a0d14",
        plot_bgcolor="#0a0d14",
        font=dict(color="#e5e7eb", family="monospace", size=12),
        title=dict(text=f"  {ticker.replace('.NS', '')}  ·  Gap Mean Reversion", font=dict(size=15, color="#e8eaf6")),
        legend=dict(bgcolor="#111827", bordercolor="#1f2937", borderwidth=1, font=dict(size=11)),
        xaxis_rangeslider_visible=False,
        height=680,
        margin=dict(l=10, r=10, t=46, b=10),
    )
    fig.update_xaxes(gridcolor="#1f2937", zerolinecolor="#1f2937")
    fig.update_yaxes(gridcolor="#1f2937", zerolinecolor="#1f2937")

    return fig


# ─────────────────────────────────────────────
# SCANNER TABLE (no pandas Styler.background_gradient)
# ─────────────────────────────────────────────

def signals_to_df(signals: list[StockSignal]) -> pd.DataFrame:
    rows = []
    for s in signals:
        rows.append({
            "Ticker": s.ticker.replace(".NS", ""),
            "Sector": s.sector,
            "Signal": s.signal,
            "Gap %": s.gap_pct,
            "Confidence": s.confidence_label,
            "Score": s.confidence_score,
            "Entry": s.entry,
            "Stop Loss": s.stop_loss,
            "Target 1": s.target1,
            "Target 2": s.target2,
            "Target 3": s.target3,
            "ATR": s.atr,
            "Rel. Volume": s.rel_volume,
        })
    return pd.DataFrame(rows)


def render_scanner_table(signals: list[StockSignal]) -> None:
    """Render scanner table using plain st.dataframe — no matplotlib dependency."""
    df = signals_to_df(signals)
    if df.empty:
        st.info("No signals match the current filters.")
        return

    # Use Plotly table for rich colouring without matplotlib
    header_vals = list(df.columns)
    cell_vals = [df[c].tolist() for c in df.columns]

    # Colour signal column
    sig_colors = []
    for v in df["Signal"]:
        if v == "LONG":
            sig_colors.append("#052e16")
        elif v == "SHORT":
            sig_colors.append("#450a0a")
        else:
            sig_colors.append("#111827")

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f"<b>{h}</b>" for h in header_vals],
            fill_color="#1f2937",
            font=dict(color="#e5e7eb", size=12),
            align="left",
            height=34,
            line_color="#374151",
        ),
        cells=dict(
            values=cell_vals,
            fill_color=["#111827"] * len(df.columns),
            font=dict(color="#d1d5db", size=12),
            align="left",
            height=30,
            line_color="#1f2937",
            format=[None, None, None, ".2f", None, ".0f",
                    ",.2f", ",.2f", ",.2f", ",.2f", ",.2f", ",.2f", ".2f"],
        ),
    )])
    fig.update_layout(
        paper_bgcolor="#0a0d14",
        margin=dict(l=0, r=0, t=0, b=0),
        height=min(60 + len(df) * 32, 520),
    )
    st.plotly_chart(fig, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download CSV", data=csv,
        file_name=f"gap_signals_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main() -> None:

    # ── SIDEBAR ──────────────────────────────
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center;padding:14px 0 22px;">
                <span style="font-size:32px;">📈</span>
                <div style="font-size:17px;font-weight:700;color:#e8eaf6;margin:6px 0 2px;">Gap MR Terminal</div>
                <div style="font-size:11px;color:#4b5563;">NSE Gap Mean Reversion</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── SECTOR SELECTOR
        st.markdown("#### 🏦 Sector")
        sector_sel = st.selectbox(
            "Select Sector", options=list(SECTOR_DB.keys()),
            label_visibility="collapsed",
        )

        # ── STOCK SELECTOR
        st.markdown("#### 📌 Stock")
        tickers_in_sector = SECTOR_DB[sector_sel]
        ticker_labels = [t.replace(".NS", "") for t in tickers_in_sector]
        ticker_sel_label = st.selectbox(
            "Select Stock", options=ticker_labels,
            label_visibility="collapsed",
        )
        ticker_sel = tickers_in_sector[ticker_labels.index(ticker_sel_label)]

        st.markdown("---")

        # ── RISK MANAGEMENT
        st.markdown("#### 🎯 Risk Management")
        max_risk = st.number_input(
            "Max Risk Per Trade (₹)",
            min_value=100.0, max_value=100000.0, value=1500.0, step=100.0,
        )

        # Load signal for selected stock
        # Auto-recalculates whenever sector, stock, or risk amount changes (no button press needed)
        with st.spinner("Loading..."):
            sig = analyze_stock(ticker_sel)
            df = fetch_ohlcv(ticker_sel)

        # ── Debug log to Streamlit server console ──────────────────────────
        if sig is not None:
            print(
                f"[DEBUG] Ticker={ticker_sel} | Signal={sig.signal} | "
                f"Entry={sig.entry} | StopLoss={sig.stop_loss} | "
                f"RiskPerShare={abs(sig.entry - sig.stop_loss):.2f} | "
                f"Qty={math.floor(max_risk / abs(sig.entry - sig.stop_loss)) if abs(sig.entry - sig.stop_loss) > 0 else 0}"
            )
        else:
            print(f"[DEBUG] Ticker={ticker_sel} | sig=None — no market data returned")

        # ── Position Sizing Section ─────────────────────────────────────────
        st.markdown("---")
        st.markdown("#### 💼 Position Size")

        # Validate signal exists and has usable data
        _entry = getattr(sig, "entry", None) if sig is not None else None
        _sl    = getattr(sig, "stop_loss", None) if sig is not None else None
        _t1    = getattr(sig, "target1", None) if sig is not None else None

        _entry_ok = _entry is not None and not (isinstance(_entry, float) and math.isnan(_entry)) and _entry > 0
        _sl_ok    = _sl    is not None and not (isinstance(_sl,    float) and math.isnan(_sl))    and _sl    > 0

        if not _entry_ok or not _sl_ok:
            st.markdown(
                '<div class="pos-row"><span class="pos-label" style="color:#f87171;">Trade data unavailable</span></div>',
                unsafe_allow_html=True,
            )
        else:
            _risk_per_share = abs(_entry - _sl)
            if _risk_per_share <= 0:
                st.markdown(
                    '<div class="pos-row"><span class="pos-label" style="color:#f87171;">Invalid stop loss calculation</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                pos = compute_position_size(_entry, _sl, _t1, max_risk)
                pos_rows = [
                    ("Risk / Share", f"₹{pos.risk_per_share:.2f}"),
                    ("Quantity",     f"{pos.quantity} shares"),
                    ("Capital Req.", f"₹{pos.capital_required:,.0f}"),
                    ("Pot. Reward",  f"₹{pos.potential_reward:,.0f}"),
                    ("R/R Ratio",    f"{pos.rr_ratio:.2f}×"),
                ]
                for label, val in pos_rows:
                    st.markdown(
                        f'<div class="pos-row"><span class="pos-label">{label}</span>'
                        f'<span class="pos-val">{val}</span></div>',
                        unsafe_allow_html=True,
                    )

        st.markdown("---")
        run_scan = st.button("🔄 Refresh Full Scan", type="primary", use_container_width=True)
        st.markdown(
            '<div style="font-size:10px;color:#374151;text-align:center;margin-top:8px;">'
            'Data via Yahoo Finance.<br>Not investment advice.</div>',
            unsafe_allow_html=True,
        )

    # ── LOAD SCAN SIGNALS ────────────────────
    if "signals" not in st.session_state or run_scan:
        with st.spinner("🔍 Scanning NSE universe..."):
            st.session_state["signals"] = scan_all_stocks(tuple(ALL_TICKERS))

    signals: list[StockSignal] = st.session_state.get("signals", [])

    # ── MAIN CONTENT ─────────────────────────
    if sig is None or df is None or df.empty:
        st.warning("Could not load data for the selected stock. Try another.")
        return

    name = ticker_sel.replace(".NS", "")

    # ── TOP METRIC CARDS ─────────────────────
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("Current Price", f"₹{sig.current_price:,.2f}", sig.sector),
        ("Gap %", f"{sig.gap_pct:+.2f}%", "vs. reference price"),
        ("ATR (14)", f"₹{sig.atr:,.2f}", "average true range"),
        ("Confidence", f"{sig.confidence_score:.0f}/100", sig.confidence_label),
    ]
    for col, (label, value, sub) in zip([c1, c2, c3, c4], cards):
        col.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-label">{label}</div>'
            f'<div class="stat-value">{value}</div>'
            f'<div class="stat-sub">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── SIGNAL + TRADE PLAN ROW ───────────────
    left_col, right_col = st.columns([1, 2])

    with left_col:
        # Signal Card
        if sig.signal == "LONG":
            css_cls = "signal-card-long"
            txt_cls = "signal-long-text"
            icon = "🟢"
        elif sig.signal == "SHORT":
            css_cls = "signal-card-short"
            txt_cls = "signal-short-text"
            icon = "🔴"
        else:
            css_cls = "signal-card-none"
            txt_cls = "signal-none-text"
            icon = "⚪"

        prob_txt = f"Confidence: <b>{sig.confidence_score:.0f}%</b> &nbsp;|&nbsp; {sig.confidence_label}"
        st.markdown(
            f'<div class="{css_cls}">'
            f'<div style="font-size:28px;">{icon}</div>'
            f'<div class="signal-text {txt_cls}">{sig.signal}</div>'
            f'<div class="signal-meta">{prob_txt}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with right_col:
        if sig is None:
            st.info("No trade setup currently available.", icon="ℹ️")
        elif sig.signal != "NO SIGNAL":
            tc1, tc2, tc3 = st.columns(3)
            entry_delta = ""
            sl_pct = (sig.stop_loss - sig.entry) / sig.entry * 100
            t1_pct = (sig.target1 - sig.entry) / sig.entry * 100

            for col, label, value, sub, color in [
                (tc1, "ENTRY", f"₹{sig.entry:,.2f}", "Open price", "#60a5fa"),
                (tc2, "STOP LOSS", f"₹{sig.stop_loss:,.2f}", f"{sl_pct:+.2f}%", "#f87171"),
                (tc3, "TARGET 1", f"₹{sig.target1:,.2f}", f"{t1_pct:+.2f}%", "#34d399"),
            ]:
                col.markdown(
                    f'<div class="trade-card">'
                    f'<div class="trade-card-label">{label}</div>'
                    f'<div class="trade-card-value" style="color:{color};">{value}</div>'
                    f'<div class="trade-card-sub">{sub}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # Sub-targets row
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            sub_cols = st.columns(3)
            for col, label, val in [
                (sub_cols[0], "Target 1 (50% rev)", f"₹{sig.target1:,.2f}"),
                (sub_cols[1], "Target 2 (100% rev)", f"₹{sig.target2:,.2f}"),
                (sub_cols[2], "Target 3 (150% rev)", f"₹{sig.target3:,.2f}"),
            ]:
                col.metric(label, val)
        else:
            st.info("No active gap signal for this stock today. Gap < 2% threshold.", icon="ℹ️")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── MARKET STATISTICS BAR ─────────────────
    rsi_color = "#34d399" if sig.rsi < 30 else "#f87171" if sig.rsi > 70 else "#e5e7eb"
    gap_color = "#34d399" if sig.gap_pct < 0 else "#f87171" if sig.gap_pct > 0 else "#e5e7eb"
    stats_html = f"""
    <div class="stat-bar">
        <div class="stat-bar-item">
            <span class="stat-bar-label">Close</span>
            <span class="stat-bar-val">₹{sig.current_price:,.2f}</span>
        </div>
        <div class="stat-bar-item">
            <span class="stat-bar-label">RSI (14)</span>
            <span class="stat-bar-val" style="color:{rsi_color};">{sig.rsi:.1f}</span>
        </div>
        <div class="stat-bar-item">
            <span class="stat-bar-label">ATR</span>
            <span class="stat-bar-val">₹{sig.atr:,.2f}</span>
        </div>
        <div class="stat-bar-item">
            <span class="stat-bar-label">Volume Ratio</span>
            <span class="stat-bar-val">{sig.rel_volume:.2f}×</span>
        </div>
        <div class="stat-bar-item">
            <span class="stat-bar-label">Gap %</span>
            <span class="stat-bar-val" style="color:{gap_color};">{sig.gap_pct:+.2f}%</span>
        </div>
        <div class="stat-bar-item">
            <span class="stat-bar-label">20 DMA</span>
            <span class="stat-bar-val">₹{sig.dma20:,.2f}</span>
        </div>
        <div class="stat-bar-item">
            <span class="stat-bar-label">Reference</span>
            <span class="stat-bar-val">₹{sig.reference_price:,.2f}</span>
        </div>
    </div>
    """
    st.markdown(stats_html, unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── CHART ────────────────────────────────
    fig = build_candlestick_chart(df, sig, ticker_sel)
    st.plotly_chart(fig, use_container_width=True)

    # ── MARKET SCANNER (collapsed) ────────────
    with st.expander("🔍 Show Market Scanner", expanded=False):
        active = [s for s in signals if s.signal != "NO SIGNAL"]
        active.sort(key=lambda x: x.confidence_score, reverse=True)

        cf1, cf2 = st.columns(2)
        with cf1:
            sig_filter = st.multiselect(
                "Signal", options=["LONG", "SHORT"], default=["LONG", "SHORT"], key="scan_sig"
            )
        with cf2:
            conf_filter = st.multiselect(
                "Confidence", options=["HIGH", "MEDIUM", "LOW"], default=[], key="scan_conf",
                placeholder="All levels"
            )

        filtered = [s for s in active if s.signal in sig_filter]
        if conf_filter:
            filtered = [s for s in filtered if s.confidence_label in conf_filter]

        st.caption(f"{len(filtered)} signals · {len([s for s in filtered if s.signal=='LONG'])} LONG · {len([s for s in filtered if s.signal=='SHORT'])} SHORT")
        render_scanner_table(filtered)

    # ── HISTORICAL PERFORMANCE (collapsed) ────
    with st.expander("📊 Historical Performance (Backtest)", expanded=False):
        lb_col, _ = st.columns([1, 3])
        with lb_col:
            lookback = st.number_input("Lookback (days)", min_value=20, max_value=250, value=60, step=10)

        if st.button("▶ Run Backtest", type="primary"):
            with st.spinner("Running backtest..."):
                result = run_backtest(ticker_sel, lookback)

            if result is None:
                st.error("Not enough data or no signals found in this period.")
            else:
                s1, s2, s3, s4, s5, s6 = st.columns(6)
                s1.metric("Trades", result.total_trades)
                s2.metric("Win Rate", f"{result.win_rate:.1f}%")
                s3.metric("Avg Return", f"{result.avg_return:+.2f}%")
                s4.metric("Profit Factor", f"{result.profit_factor:.2f}")
                s5.metric("Best Trade", f"{result.best_trade:+.2f}%")
                s6.metric("Worst Trade", f"{result.worst_trade:+.2f}%")

                # Equity curve
                fig_eq = go.Figure()
                fig_eq.add_trace(go.Scatter(
                    x=list(range(len(result.equity_curve))),
                    y=result.equity_curve,
                    name="Equity",
                    line=dict(color="#60a5fa", width=2),
                    fill="tozeroy",
                    fillcolor="rgba(96,165,250,0.07)",
                ))
                fig_eq.add_hline(y=10000, line_dash="dot", line_color="#374151", annotation_text="Start ₹10k")
                fig_eq.update_layout(
                    paper_bgcolor="#0a0d14", plot_bgcolor="#0a0d14",
                    font=dict(color="#e5e7eb"),
                    xaxis_title="Trade #", yaxis_title="Equity (₹)",
                    height=340, margin=dict(l=10, r=10, t=10, b=10),
                )
                fig_eq.update_xaxes(gridcolor="#1f2937")
                fig_eq.update_yaxes(gridcolor="#1f2937")
                st.plotly_chart(fig_eq, use_container_width=True)

                # Trade returns
                colors = ["#34d399" if r > 0 else "#f87171" for r in result.trade_returns]
                fig_dist = go.Figure(go.Bar(
                    x=result.trade_dates, y=result.trade_returns,
                    marker_color=colors, name="Return %",
                ))
                fig_dist.add_hline(y=0, line_color="#374151", line_dash="dot")
                fig_dist.update_layout(
                    paper_bgcolor="#0a0d14", plot_bgcolor="#0a0d14",
                    font=dict(color="#e5e7eb"),
                    xaxis_title="Date", yaxis_title="Return %",
                    height=250, margin=dict(l=10, r=10, t=10, b=10),
                )
                fig_dist.update_xaxes(gridcolor="#1f2937")
                fig_dist.update_yaxes(gridcolor="#1f2937")
                st.plotly_chart(fig_dist, use_container_width=True)

                # Trade log — plain st.dataframe, no Styler.background_gradient
                trade_df = pd.DataFrame({
                    "Trade #": list(range(1, len(result.trade_returns) + 1)),
                    "Date": result.trade_dates,
                    "Return %": result.trade_returns,
                    "Equity": result.equity_curve[1:],
                })
                st.dataframe(
                    trade_df.style.format({
                        "Return %": "{:+.3f}%",
                        "Equity": "₹{:,.2f}",
                    }).map(
                        lambda v: "color: #34d399;" if isinstance(v, (int, float)) and v > 0
                        else "color: #f87171;" if isinstance(v, (int, float)) and v <= 0 else "",
                        subset=["Return %"],
                    ),
                    use_container_width=True, hide_index=True,
                )

                csv = trade_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇ Download Trade Log", data=csv,
                    file_name=f"backtest_{ticker_sel}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )

    # ── DISCLAIMER ────────────────────────────
    st.markdown(
        '<div class="disclaimer">⚠ Past data is for informational purposes only. '
        "This is not investment advice. Trade at your own risk.</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
