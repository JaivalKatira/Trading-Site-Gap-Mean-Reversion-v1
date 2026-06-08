# Trading-Site-Gap-Mean-Reversion-v1

Gap Mean Reversion Dashboard
A professional Streamlit application for analyzing NSE stocks using a Gap Mean Reversion strategy. Scan multiple stocks, generate LONG/SHORT signals with confidence scores, calculate stop losses and targets, and backtest strategy performance.

Features

Signal Scanner — Scan 90+ NSE stocks across 6 sectors for gap mean reversion opportunities
Confidence Scoring — Multi-factor scoring based on gap size, ATR, DMA distance, and relative volume
Stop Loss & Targets — ATR-based stop losses and 3-tiered mean reversion targets
Position Sizing — Risk-based position sizing with capital required and R/R ratio
Interactive Charts — Plotly candlestick charts with overlaid DMA, SL, and target levels
Backtesting — Historical strategy performance with equity curve
CSV Export — Download scan results


Installation
bashgit clone https://github.com/youruser/gap-mean-reversion.git
cd gap-mean-reversion
pip install -r requirements.txt
streamlit run app.py

Usage

Open the app in your browser (default: http://localhost:8501)
Use the Dashboard tab for a market overview
Navigate to Signal Scanner to run a full sector scan
Use Stock Analysis to deep-dive into any individual stock
Explore the Backtest tab to review historical strategy performance


Folder Structure
gap-mean-reversion/
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation

Strategy Logic
Reference Price
Reference Price = (Previous Open + Previous Close) / 2
Gap Calculation
Gap % = (Today's Open - Reference Price) / Reference Price × 100
Signal Rules
ConditionSignalGap > +2%SHORTGap < -2%LONG-2% ≤ Gap ≤ 2%NO SIGNAL
Confidence Score (0–100)

Gap Size — Larger gaps score higher
ATR Ratio — Gap relative to average true range
DMA Distance — Distance from 20-day moving average
Relative Volume — Volume vs. 20-day average

Score RangeLabel0–39LOW40–69MEDIUM70–100HIGH
Stop Loss
LONG  SL = min(Today's Low,  Entry - 1.5 × ATR)
SHORT SL = max(Today's High, Entry + 1.5 × ATR)
Targets (Mean Reversion)
Target 1 = Entry + (Reference Price - Entry) × 0.50
Target 2 = Entry + (Reference Price - Entry) × 1.00
Target 3 = Entry + (Reference Price - Entry) × 1.50
Position Sizing
Risk Per Share    = abs(Entry - Stop Loss)
Quantity          = floor(Max Risk / Risk Per Share)
Capital Required  = Quantity × Entry
Potential Reward  = Quantity × (Target 1 - Entry)
R/R Ratio         = Potential Reward / Max Risk

Risk Disclaimer

This software is for educational and informational purposes only. It does not constitute financial advice. Trading in equities and derivatives involves substantial risk of loss. Past performance is not indicative of future results. Always consult a SEBI-registered investment advisor before making trading decisions. The authors accept no responsibility for any financial losses incurred through the use of this application.


Future Improvements

Real-time intraday data integration via NSE API
Multi-timeframe analysis (15m, 1H, Daily)
Portfolio-level risk management
Telegram/email alerts for new signals
Options chain integration for gap plays
Machine learning confidence score model
Paper trading simulation mode
