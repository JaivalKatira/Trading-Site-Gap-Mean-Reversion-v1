"""
Gap Mean Reversion Dashboard
NSE Stock Analysis using Gap Mean Reversion Strategy
"""
 
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
import math
import warnings
 
warnings.filterwarnings("ignore")
 
# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
 
st.set_page_config(
    page_title="Gap Mean Reversion Dashboard",
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
    .stApp { background-color: #0e1117; color: #fafafa; }
    .metric-card {
        background: #1e2130;
        border-radius: 10px;
        padding: 16px 20px;
        margin: 6px 0;
        border-left: 4px solid #4a9eff;
    }
    .metric-label { font-size: 12px; color: #8b95a7; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 24px; font-weight: 700; color: #fafafa; margin-top: 4px; }
    .signal-long {
        background: linear-gradient(135deg, #0d2b1a, #0a3d1f);
        border-left: 4px solid #00c853;
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 700;
        color: #00e676;
        display: inline-block;
    }
    .signal-short {
        background: linear-gradient(135deg, #2b0d0d, #3d0a0a);
        border-left: 4px solid #ff1744;
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 700;
        color: #ff5252;
        display: inline-block;
    }
    .signal-none {
        background: #1e2130;
        border-left: 4px solid #546e7a;
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 700;
        color: #78909c;
        display: inline-block;
    }
    .confidence-high { color: #00e676; font-weight: 700; }
    .confidence-medium { color: #ffab40; font-weight: 700; }
    .confidence-low { color: #ef5350; font-weight: 700; }
    .stTabs [data-baseweb="tab-list"] { background: #1e2130; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #8b95a7; }
    .stTabs [aria-selected="true"] { color: #4a9eff !important; }
    div[data-testid="stMetricValue"] { color: #fafafa; }
    .stDataFrame { border-radius: 8px; overflow: hidden; }
    h1, h2, h3 { color: #e8eaf6 !important; }
    .disclaimer {
        background: #1a1a2e;
        border: 1px solid #3d3d5c;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 12px;
        color: #78909c;
        margin-top: 20px;
    }
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
    """Fetch OHLCV data from Yahoo Finance with error handling."""
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
    """Compute Average True Range."""
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
    """Compute 20-day simple moving average of close."""
    return float(df["Close"].rolling(20).mean().iloc[-1])
 
 
def compute_relative_volume(df: pd.DataFrame) -> float:
    """Compute today's volume relative to 20-day average volume."""
    avg_vol = df["Volume"].rolling(20).mean().iloc[-2]
    today_vol = df["Volume"].iloc[-1]
    if avg_vol and avg_vol > 0:
        return float(today_vol / avg_vol)
    return 1.0
 
# ─────────────────────────────────────────────
# STRATEGY LOGIC
# ─────────────────────────────────────────────
 
def compute_reference_price(prev_open: float, prev_close: float) -> float:
    """Reference price = (previous open + previous close) / 2."""
    return (prev_open + prev_close) / 2.0
 
 
def compute_gap_pct(today_open: float, reference_price: float) -> float:
    """Gap % = (today open - reference price) / reference price."""
    if reference_price == 0:
        return 0.0
    return (today_open - reference_price) / reference_price * 100.0
 
 
def determine_signal(gap_pct: float) -> str:
    """Map gap percentage to trading signal."""
    if gap_pct > 2.0:
        return "SHORT"
    elif gap_pct < -2.0:
        return "LONG"
    return "NO SIGNAL"
 
 
def compute_confidence_score(
    gap_pct: float,
    atr: float,
    entry: float,
    dma20: float,
    rel_volume: float,
) -> tuple[float, str]:
    """
    Compute confidence score 0-100 from four factors.
    Returns (score, label).
    """
    # Factor 1: Gap size (0-25 pts) — bigger gap = higher score, capped at 10%
    gap_abs = abs(gap_pct)
    gap_score = min(gap_abs / 10.0 * 25.0, 25.0)
 
    # Factor 2: ATR ratio (0-25 pts) — gap relative to ATR
    if atr > 0 and entry > 0:
        gap_in_price = abs(gap_pct / 100.0 * entry)
        atr_ratio = gap_in_price / atr
        atr_score = min(atr_ratio / 2.0 * 25.0, 25.0)
    else:
        atr_score = 0.0
 
    # Factor 3: DMA distance (0-25 pts) — price far from DMA = higher reversion potential
    if dma20 > 0 and entry > 0:
        dma_dist_pct = abs(entry - dma20) / dma20 * 100.0
        dma_score = min(dma_dist_pct / 5.0 * 25.0, 25.0)
    else:
        dma_score = 0.0
 
    # Factor 4: Relative volume (0-25 pts) — higher volume = more conviction
    rvol_score = min((rel_volume - 1.0) / 3.0 * 25.0, 25.0) if rel_volume > 1.0 else 0.0
 
    total = gap_score + atr_score + dma_score + rvol_score
    total = max(0.0, min(100.0, total))
 
    if total >= 70:
        label = "HIGH"
    elif total >= 40:
        label = "MEDIUM"
    else:
        label = "LOW"
 
    return round(total, 1), label
 
 
def compute_stop_loss(signal: str, entry: float, today_low: float, today_high: float, atr: float) -> float:
    """Compute ATR-based stop loss."""
    if signal == "LONG":
        return min(today_low, entry - 1.5 * atr)
    elif signal == "SHORT":
        return max(today_high, entry + 1.5 * atr)
    return entry
 
 
def compute_targets(entry: float, reference_price: float) -> tuple[float, float, float]:
    """Compute three mean reversion targets."""
    reversion = reference_price - entry
    t1 = entry + reversion * 0.50
    t2 = entry + reversion * 1.00
    t3 = entry + reversion * 1.50
    return round(t1, 2), round(t2, 2), round(t3, 2)
 
 
def compute_position_size(
    entry: float,
    stop_loss: float,
    target1: float,
    max_risk: float,
) -> PositionSize:
    """Compute position sizing from max risk per trade."""
    risk_per_share = abs(entry - stop_loss)
    if risk_per_share == 0:
        return PositionSize(0, 0, 0, 0, 0)
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
    """Run full gap mean reversion analysis for a single stock."""
    df = fetch_ohlcv(ticker)
    if df is None or len(df) < 22:
        return None
 
    try:
        prev_row = df.iloc[-2]
        today_row = df.iloc[-1]
 
        prev_open = float(prev_row["Open"])
        prev_close = float(prev_row["Close"])
        today_open = float(today_row["Open"])
        today_high = float(today_row["High"])
        today_low = float(today_row["Low"])
        today_close = float(today_row["Close"])
 
        reference_price = compute_reference_price(prev_open, prev_close)
        gap_pct = compute_gap_pct(today_open, reference_price)
        signal = determine_signal(gap_pct)
 
        atr = compute_atr(df)
        dma20 = compute_20dma(df)
        rel_volume = compute_relative_volume(df)
 
        entry = today_open
        stop_loss = compute_stop_loss(signal, entry, today_low, today_high, atr)
        t1, t2, t3 = compute_targets(entry, reference_price)
        conf_score, conf_label = compute_confidence_score(gap_pct, atr, entry, dma20, rel_volume)
 
        return StockSignal(
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
        )
    except Exception:
        return None
 
 
@st.cache_data(ttl=300, show_spinner=False)
def scan_all_stocks(tickers: tuple[str, ...]) -> list[StockSignal]:
    """Scan all tickers and return list of StockSignal objects."""
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
    """
    Backtest gap mean reversion: enter at open, exit at close.
    A trade is triggered when gap > 2% (SHORT) or < -2% (LONG).
    """
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
 
def build_candlestick_chart(
    df: pd.DataFrame,
    signal: StockSignal,
    ticker: str,
) -> go.Figure:
    """Build Plotly candlestick chart with overlays."""
    df_plot = df.tail(60).copy()
 
    dma_series = df["Close"].rolling(20).mean().reindex(df_plot.index)
 
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.04,
    )
 
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df_plot.index,
            open=df_plot["Open"],
            high=df_plot["High"],
            low=df_plot["Low"],
            close=df_plot["Close"],
            name="Price",
            increasing_line_color="#00e676",
            decreasing_line_color="#ff5252",
        ),
        row=1, col=1,
    )
 
    # 20 DMA
    fig.add_trace(
        go.Scatter(
            x=df_plot.index,
            y=dma_series,
            name="20 DMA",
            line=dict(color="#ffab40", width=1.5, dash="dot"),
        ),
        row=1, col=1,
    )
 
    last_date = df_plot.index[-1]
    first_date = df_plot.index[0]
 
    def _hline(y_val: float, color: str, label: str, dash: str = "dash") -> go.Scatter:
        return go.Scatter(
            x=[first_date, last_date],
            y=[y_val, y_val],
            mode="lines",
            name=label,
            line=dict(color=color, width=1.2, dash=dash),
        )
 
    # Signal levels
    if signal.signal != "NO SIGNAL":
        fig.add_trace(_hline(signal.entry, "#4a9eff", f"Entry {signal.entry:.2f}", "solid"), row=1, col=1)
        fig.add_trace(_hline(signal.stop_loss, "#ff5252", f"SL {signal.stop_loss:.2f}"), row=1, col=1)
        fig.add_trace(_hline(signal.target1, "#69f0ae", f"T1 {signal.target1:.2f}"), row=1, col=1)
        fig.add_trace(_hline(signal.target2, "#40c4ff", f"T2 {signal.target2:.2f}"), row=1, col=1)
        fig.add_trace(_hline(signal.target3, "#ea80fc", f"T3 {signal.target3:.2f}"), row=1, col=1)
        fig.add_trace(_hline(signal.reference_price, "#fff176", f"Ref {signal.reference_price:.2f}", "dot"), row=1, col=1)
 
    # Volume bars
    vol_colors = [
        "#00e676" if float(df_plot["Close"].iloc[i]) >= float(df_plot["Open"].iloc[i]) else "#ff5252"
        for i in range(len(df_plot))
    ]
    fig.add_trace(
        go.Bar(
            x=df_plot.index,
            y=df_plot["Volume"],
            name="Volume",
            marker_color=vol_colors,
            opacity=0.7,
        ),
        row=2, col=1,
    )
 
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="#fafafa", family="monospace"),
        title=dict(text=f"{ticker} — Gap Mean Reversion Analysis", font=dict(size=16, color="#e8eaf6")),
        legend=dict(bgcolor="#1e2130", bordercolor="#333", borderwidth=1),
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_xaxes(gridcolor="#1e2130", zerolinecolor="#1e2130")
    fig.update_yaxes(gridcolor="#1e2130", zerolinecolor="#1e2130")
 
    return fig
 
# ─────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────
 
def signal_badge(signal: str) -> str:
    if signal == "LONG":
        return '<span class="signal-long">▲ LONG</span>'
    elif signal == "SHORT":
        return '<span class="signal-short">▼ SHORT</span>'
    return '<span class="signal-none">— NO SIGNAL</span>'
 
 
def confidence_badge(label: str) -> str:
    css = f"confidence-{label.lower()}"
    return f'<span class="{css}">● {label}</span>'
 
 
def metric_card(label: str, value: str) -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """
 
 
def signals_to_df(signals: list[StockSignal]) -> pd.DataFrame:
    rows = []
    for s in signals:
        rows.append({
            "Ticker": s.ticker,
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
 
# ─────────────────────────────────────────────
# TAB: DASHBOARD
# ─────────────────────────────────────────────
 
def render_dashboard(signals: list[StockSignal]) -> None:
    st.markdown("## 📊 Market Overview")
 
    long_sigs = [s for s in signals if s.signal == "LONG"]
    short_sigs = [s for s in signals if s.signal == "SHORT"]
    high_conf = [s for s in signals if s.confidence_label == "HIGH" and s.signal != "NO SIGNAL"]
 
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Stocks Scanned", len(signals))
    col2.metric("LONG Signals", len(long_sigs), delta=f"{len(long_sigs)/max(len(signals),1)*100:.0f}%")
    col3.metric("SHORT Signals", len(short_sigs), delta=f"{len(short_sigs)/max(len(signals),1)*100:.0f}%")
    col4.metric("High Confidence", len(high_conf))
 
    st.markdown("---")
    st.markdown("### 🔥 Top Signals by Confidence")
 
    action_signals = [s for s in signals if s.signal != "NO SIGNAL"]
    action_signals.sort(key=lambda x: x.confidence_score, reverse=True)
    top_signals = action_signals[:9]
 
    if not top_signals:
        st.info("No active signals at this time. Markets may be consolidating.")
        return
 
    cols = st.columns(3)
    for idx, sig in enumerate(top_signals):
        with cols[idx % 3]:
            signal_color = "#00e676" if sig.signal == "LONG" else "#ff5252"
            arrow = "▲" if sig.signal == "LONG" else "▼"
            st.markdown(
                f"""
                <div style="background:#1e2130;border-radius:10px;padding:14px;margin:6px 0;
                            border-top:3px solid {signal_color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:15px;font-weight:700;color:#e8eaf6;">{sig.ticker.replace(".NS","")}</span>
                        <span style="color:{signal_color};font-weight:700;">{arrow} {sig.signal}</span>
                    </div>
                    <div style="color:#8b95a7;font-size:12px;margin-top:4px;">{sig.sector}</div>
                    <div style="margin-top:10px;display:flex;justify-content:space-between;">
                        <span style="color:#78909c;font-size:12px;">Gap</span>
                        <span style="color:{signal_color};font-weight:600;">{sig.gap_pct:+.2f}%</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;">
                        <span style="color:#78909c;font-size:12px;">Entry</span>
                        <span style="color:#fafafa;">₹{sig.entry:.2f}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;">
                        <span style="color:#78909c;font-size:12px;">Confidence</span>
                        <span style="color:{'#00e676' if sig.confidence_label=='HIGH' else '#ffab40' if sig.confidence_label=='MEDIUM' else '#ef5350'};font-weight:700;">{sig.confidence_label} ({sig.confidence_score:.0f})</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
 
    st.markdown("---")
    st.markdown("### 📈 Sector Signal Distribution")
    sector_summary: dict[str, dict[str, int]] = {}
    for s in signals:
        sec = s.sector
        if sec not in sector_summary:
            sector_summary[sec] = {"LONG": 0, "SHORT": 0, "NO SIGNAL": 0}
        sector_summary[sec][s.signal] += 1
 
    sector_df = pd.DataFrame(sector_summary).T.reset_index()
    sector_df.columns = ["Sector", "LONG", "SHORT", "NO SIGNAL"]
    st.dataframe(
        sector_df.style
        .background_gradient(subset=["LONG"], cmap="Greens")
        .background_gradient(subset=["SHORT"], cmap="Reds"),
        use_container_width=True,
        hide_index=True,
    )
 
# ─────────────────────────────────────────────
# TAB: SIGNAL SCANNER
# ─────────────────────────────────────────────
 
def render_scanner(signals: list[StockSignal]) -> None:
    st.markdown("## 🔍 Signal Scanner")
 
    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
        sector_filter = st.multiselect(
            "Filter by Sector",
            options=list(SECTOR_DB.keys()),
            default=[],
            placeholder="All sectors",
        )
    with col_f2:
        signal_filter = st.multiselect(
            "Filter by Signal",
            options=["LONG", "SHORT", "NO SIGNAL"],
            default=["LONG", "SHORT"],
        )
    with col_f3:
        conf_filter = st.multiselect(
            "Filter by Confidence",
            options=["HIGH", "MEDIUM", "LOW"],
            default=[],
            placeholder="All levels",
        )
 
    filtered = signals
    if sector_filter:
        filtered = [s for s in filtered if s.sector in sector_filter]
    if signal_filter:
        filtered = [s for s in filtered if s.signal in signal_filter]
    if conf_filter:
        filtered = [s for s in filtered if s.confidence_label in conf_filter]
 
    filtered.sort(key=lambda x: x.confidence_score, reverse=True)
 
    df = signals_to_df(filtered)
 
    if df.empty:
        st.info("No signals match the current filters.")
        return
 
    st.markdown(f"**{len(df)} signals found**")
 
    def highlight_signal(val: str) -> str:
        if val == "LONG":
            return "background-color: #0d2b1a; color: #00e676; font-weight: bold;"
        elif val == "SHORT":
            return "background-color: #2b0d0d; color: #ff5252; font-weight: bold;"
        return "color: #78909c;"
 
    def highlight_confidence(val: str) -> str:
        if val == "HIGH":
            return "color: #00e676; font-weight: bold;"
        elif val == "MEDIUM":
            return "color: #ffab40; font-weight: bold;"
        return "color: #ef5350;"
 
    styled = (
        df.style
        .map(highlight_signal, subset=["Signal"])
        .map(highlight_confidence, subset=["Confidence"])
        .format({
            "Gap %": "{:+.2f}%",
            "Score": "{:.0f}",
            "Entry": "₹{:.2f}",
            "Stop Loss": "₹{:.2f}",
            "Target 1": "₹{:.2f}",
            "Target 2": "₹{:.2f}",
            "Target 3": "₹{:.2f}",
            "ATR": "₹{:.2f}",
            "Rel. Volume": "{:.2f}x",
        })
    )
 
    st.dataframe(styled, use_container_width=True, hide_index=True, height=500)
 
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download CSV",
        data=csv,
        file_name=f"gap_signals_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )
 
# ─────────────────────────────────────────────
# TAB: STOCK ANALYSIS
# ─────────────────────────────────────────────
 
def render_stock_analysis() -> None:
    st.markdown("## 📉 Stock Analysis")
 
    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        sector_sel = st.selectbox("Select Sector", options=list(SECTOR_DB.keys()))
    with col_s2:
        tickers_in_sector = SECTOR_DB[sector_sel]
        ticker_labels = [t.replace(".NS", "") for t in tickers_in_sector]
        ticker_sel_label = st.selectbox("Select Stock", options=ticker_labels)
        ticker_sel = tickers_in_sector[ticker_labels.index(ticker_sel_label)]
 
    max_risk = st.number_input("Maximum Risk Per Trade (₹)", min_value=100.0, max_value=100000.0, value=1500.0, step=100.0)
 
    if st.button("🔎 Analyze", type="primary"):
        with st.spinner(f"Fetching data for {ticker_sel}..."):
            df = fetch_ohlcv(ticker_sel)
            sig = analyze_stock(ticker_sel)
 
        if df is None or sig is None:
            st.error(f"Could not fetch data for {ticker_sel}. Please try another stock.")
            return
 
        # Metrics row 1
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Price", f"₹{sig.current_price:,.2f}")
        c2.metric("Reference Price", f"₹{sig.reference_price:,.2f}")
        c3.metric("Gap %", f"{sig.gap_pct:+.2f}%")
        c4.metric("ATR (14)", f"₹{sig.atr:,.2f}")
 
        # Signal & confidence
        c5, c6, c7, c8 = st.columns(4)
        with c5:
            st.markdown(f"**Signal**<br>{signal_badge(sig.signal)}", unsafe_allow_html=True)
        with c6:
            st.markdown(f"**Confidence**<br>{confidence_badge(sig.confidence_label)} ({sig.confidence_score:.0f}/100)", unsafe_allow_html=True)
        c7.metric("20 DMA", f"₹{sig.dma20:,.2f}")
        c8.metric("Relative Volume", f"{sig.rel_volume:.2f}x")
 
        st.markdown("---")
 
        if sig.signal != "NO SIGNAL":
            st.markdown("### 🎯 Trade Levels")
            tc1, tc2, tc3, tc4, tc5 = st.columns(5)
            tc1.metric("Entry", f"₹{sig.entry:,.2f}")
            tc2.metric("Stop Loss", f"₹{sig.stop_loss:,.2f}", delta=f"₹{sig.stop_loss - sig.entry:+.2f}")
            tc3.metric("Target 1 (50%)", f"₹{sig.target1:,.2f}", delta=f"₹{sig.target1 - sig.entry:+.2f}")
            tc4.metric("Target 2 (100%)", f"₹{sig.target2:,.2f}", delta=f"₹{sig.target2 - sig.entry:+.2f}")
            tc5.metric("Target 3 (150%)", f"₹{sig.target3:,.2f}", delta=f"₹{sig.target3 - sig.entry:+.2f}")
 
            st.markdown("### 💼 Position Sizing")
            pos = compute_position_size(sig.entry, sig.stop_loss, sig.target1, max_risk)
            pc1, pc2, pc3, pc4, pc5 = st.columns(5)
            pc1.metric("Risk Per Share", f"₹{pos.risk_per_share:.2f}")
            pc2.metric("Quantity", str(pos.quantity))
            pc3.metric("Capital Required", f"₹{pos.capital_required:,.0f}")
            pc4.metric("Potential Reward (T1)", f"₹{pos.potential_reward:,.0f}")
            pc5.metric("R/R Ratio", f"{pos.rr_ratio:.2f}")
 
        st.markdown("### 📈 Price Chart")
        fig = build_candlestick_chart(df, sig, ticker_sel)
        st.plotly_chart(fig, use_container_width=True)
 
        st.markdown(
            '<div class="disclaimer">⚠ Past data is for informational purposes only. '
            "This is not investment advice. Trade at your own risk.</div>",
            unsafe_allow_html=True,
        )
 
# ─────────────────────────────────────────────
# TAB: BACKTEST
# ─────────────────────────────────────────────
 
def render_backtest() -> None:
    st.markdown("## 🧪 Strategy Backtest")
    st.markdown(
        "Rules: **Entry** at today's open when gap signal fires. **Exit** at today's close. "
        "Evaluates performance over the selected lookback period."
    )
 
    col_b1, col_b2, col_b3 = st.columns([2, 2, 1])
    with col_b1:
        bt_sector = st.selectbox("Sector", options=list(SECTOR_DB.keys()), key="bt_sector")
    with col_b2:
        bt_tickers = SECTOR_DB[bt_sector]
        bt_labels = [t.replace(".NS", "") for t in bt_tickers]
        bt_label_sel = st.selectbox("Stock", options=bt_labels, key="bt_stock")
        bt_ticker = bt_tickers[bt_labels.index(bt_label_sel)]
    with col_b3:
        lookback = st.number_input("Lookback (days)", min_value=20, max_value=250, value=60, step=10)
 
    if st.button("▶ Run Backtest", type="primary"):
        with st.spinner("Running backtest..."):
            result = run_backtest(bt_ticker, lookback)
 
        if result is None:
            st.error("Not enough data or no signals found in the lookback period.")
            return
 
        # Stats
        s1, s2, s3, s4, s5, s6 = st.columns(6)
        s1.metric("Total Trades", result.total_trades)
        s2.metric("Win Rate", f"{result.win_rate:.1f}%")
        s3.metric("Avg Return", f"{result.avg_return:+.2f}%")
        s4.metric("Profit Factor", f"{result.profit_factor:.2f}")
        s5.metric("Best Trade", f"{result.best_trade:+.2f}%")
        s6.metric("Worst Trade", f"{result.worst_trade:+.2f}%")
 
        # Equity curve
        st.markdown("### 📊 Equity Curve (₹10,000 start)")
        fig_eq = go.Figure()
        fig_eq.add_trace(
            go.Scatter(
                x=list(range(len(result.equity_curve))),
                y=result.equity_curve,
                name="Equity",
                line=dict(color="#4a9eff", width=2),
                fill="tozeroy",
                fillcolor="rgba(74,158,255,0.08)",
            )
        )
        peak = max(result.equity_curve)
        fig_eq.add_hline(y=10000, line_dash="dot", line_color="#546e7a", annotation_text="Start")
        fig_eq.update_layout(
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            font=dict(color="#fafafa"),
            xaxis_title="Trade #",
            yaxis_title="Equity (₹)",
            height=400,
            margin=dict(l=10, r=10, t=20, b=10),
        )
        fig_eq.update_xaxes(gridcolor="#1e2130")
        fig_eq.update_yaxes(gridcolor="#1e2130")
        st.plotly_chart(fig_eq, use_container_width=True)
 
        # Trade returns distribution
        st.markdown("### 📉 Trade Returns Distribution")
        fig_dist = go.Figure()
        colors = ["#00e676" if r > 0 else "#ff5252" for r in result.trade_returns]
        fig_dist.add_trace(
            go.Bar(
                x=result.trade_dates,
                y=result.trade_returns,
                marker_color=colors,
                name="Return %",
            )
        )
        fig_dist.add_hline(y=0, line_color="#546e7a", line_dash="dot")
        fig_dist.update_layout(
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            font=dict(color="#fafafa"),
            xaxis_title="Date",
            yaxis_title="Return %",
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        fig_dist.update_xaxes(gridcolor="#1e2130")
        fig_dist.update_yaxes(gridcolor="#1e2130")
        st.plotly_chart(fig_dist, use_container_width=True)
 
        # Trade log
        trade_df = pd.DataFrame({
            "Trade #": list(range(1, len(result.trade_returns) + 1)),
            "Date": result.trade_dates,
            "Return %": result.trade_returns,
            "Cumulative Equity": result.equity_curve[1:],
        })
        st.markdown("### 📋 Trade Log")
        st.dataframe(
            trade_df.style.format({
                "Return %": "{:+.3f}%",
                "Cumulative Equity": "₹{:,.2f}",
            }).map(
                lambda v: "color: #00e676;" if isinstance(v, (int, float)) and v > 0 else "color: #ff5252;" if isinstance(v, (int, float)) and v <= 0 else "",
                subset=["Return %"],
            ),
            use_container_width=True,
            hide_index=True,
        )
 
        csv = trade_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Trade Log",
            data=csv,
            file_name=f"backtest_{bt_ticker}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
 
# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
 
def main() -> None:
    # Sidebar
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center;padding:10px 0 20px;">
                <span style="font-size:36px;">📈</span>
                <h2 style="color:#e8eaf6;margin:8px 0 4px;">Gap MR Dashboard</h2>
                <p style="color:#8b95a7;font-size:13px;">NSE Gap Mean Reversion</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
 
        st.markdown("### ⚙️ Settings")
        run_scan = st.button("🔄 Refresh Scan", type="primary", use_container_width=True)
 
        st.markdown("---")
        st.markdown("### 📌 Strategy")
        st.markdown(
            """
            <div style="font-size:13px;color:#8b95a7;line-height:1.8;">
            <b style="color:#e8eaf6;">Reference Price</b><br>
            (Prev Open + Prev Close) / 2<br><br>
            <b style="color:#00e676;">LONG Signal</b><br>
            Gap &lt; -2%<br><br>
            <b style="color:#ff5252;">SHORT Signal</b><br>
            Gap &gt; +2%<br><br>
            <b style="color:#e8eaf6;">Stop Loss</b><br>
            1.5× ATR based<br><br>
            <b style="color:#e8eaf6;">Targets</b><br>
            50% / 100% / 150% reversion
            </div>
            """,
            unsafe_allow_html=True,
        )
 
        st.markdown("---")
        st.markdown(
            '<div style="font-size:11px;color:#546e7a;padding-top:10px;">'
            "Data via Yahoo Finance. For educational use only. Not investment advice.</div>",
            unsafe_allow_html=True,
        )
 
    # Load signals
    if "signals" not in st.session_state or run_scan:
        with st.spinner("🔍 Scanning NSE stocks..."):
            st.session_state["signals"] = scan_all_stocks(tuple(ALL_TICKERS))
 
    signals: list[StockSignal] = st.session_state.get("signals", [])
 
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "🔍 Signal Scanner",
        "📉 Stock Analysis",
        "🧪 Backtest",
    ])
 
    with tab1:
        if not signals:
            st.warning("No data loaded. Click 'Refresh Scan' in the sidebar.")
        else:
            render_dashboard(signals)
 
    with tab2:
        if not signals:
            st.warning("No data loaded. Click 'Refresh Scan' in the sidebar.")
        else:
            render_scanner(signals)
 
    with tab3:
        render_stock_analysis()
 
    with tab4:
        render_backtest()
 
 
if __name__ == "__main__":
    main()