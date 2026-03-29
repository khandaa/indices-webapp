This should be a web app that tracks the indices daily prices
It should have a configuration page to manage the master list of indices
Should be able to refresh data manually



The app should have the following features:
- Dashboard to show the indices performance
- Settings page to add/remove indices
- Chart to show the indices performance
- Chart to show the indices performance trend and compare it with other indices
- Manual refresh button
- Auto refresh button

Dashboard should show:
- Current price of each index
- Daily change
- Weekly change
- Monthly change
- Yearly change

show top 3 performers for a timeframe based on the change percentage in last x days/weeks/months/years . This parameter can be configured in settings or from UI

# Application Capabilities

This document outlines all the capabilities and features of the TradingView application.

## Table of Contents
1. [Indices Historical Data](#indices-historical-data)
2. [WhatIf Portfolio Simulation](#whatif-portfolio-simulation)
3. [Equities Data](#equities-data)
4. [Momentum Strategies](#momentum-strategies)
5. [Backtesting](#backtesting)
6. [TradingView Indicators](#tradingview-indicators)
7. [Configuration](#configuration)

---

## Indices Historical Data

### Script: `all-index-data-to-excel-v6.py`

Fetches historical monthly return data for NSE-listed index ETFs and calculates momentum metrics.



use python 3.12 or above for python.
create virtual environment and install the required packages in the requirements.txt file.


**Metrics Calculated:**
- Monthly closing prices
- Monthly Return % (month-over-month)
- Cumulative Return % (since start)
- Rolling 3M Return % (3-month rolling return)

**Features:**
- Highlights top 3 performing indices each month in green
- Auto-adjusts column widths
- Freezes header row and first column

**Output:** Excel file with timestamp (e.g., `all_indices_returns_20260301_145352.xlsx`)

---

## WhatIf Portfolio Simulation

### Script: `all-index-data-to-excel-v6.py` (WhatIf Sheet)

Interactive portfolio simulation sheet that allows users to model different investment scenarios.

**Input Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| Initial Investment Amount | ₹100,000 | Starting capital |
| Top 1 Instrument % | 50% | Allocation to best performer |
| Top 2 Instrument % | 30% | Allocation to 2nd best |
| Top 3 Instrument % | 20% | Allocation to 3rd best |

**Strategy Logic:**
1. Each month, ranks indices by Rolling 3M Return %
2. Allocates capital to top 3 performers based on configured percentages
3. Buys at first trading day of month
4. Sells at last trading day of month
5. Rolls proceeds into next month's positions

**Simulation Tracks:**
- Purchase Month, Date, Price
- Quantity purchased
- Invested amount
- Sale Date, Price, Amount
- Profit/Loss (absolute and %)
- Days held
- Sell reason (Month-End, StopLoss)
- Portfolio available cash

**Performance Metrics:**
- Total trades executed
- Winning trades count
- Win ratio %
- Average profit/loss %

**Features:**
- Formulas dynamically recalculate when parameters change
- Yellow highlighted input cells
- Gray highlighted headers
- Auto-adjusted column widths

---

## Equities Data

### Script: `all-equities-data-to-excel-v1.py`

Fetches historical price and return data for NSE 500 stocks.

**Data Source:** Nifty 500 stock list (from `data/nifty500list_10.csv`)

**Metrics Calculated:**
- Daily closing prices
- Daily Returns % (day-over-day)
- Weekly Returns % (Friday-to-Friday)
- Monthly Returns % (month-end to month-end)

**Output Sheets:**
1. **Prices** - Daily closing prices for all stocks
2. **Daily Returns** - Day-over-day percentage changes
3. **Weekly Returns** - Week-over-week percentage changes (Fridays)
4. **Monthly Returns** - Month-over-month percentage changes

**Features:**
- Top 3 performers highlighted in green each period
- Bold formatting for headers
- Auto-adjusted column widths
- Date formatting (yyyy-mm-dd)

**Output:** `nse500_stock_data.xlsx`

### Script: `get_nse_list.py`

Utility to fetch and manage NSE stock lists.

---

## Momentum Strategies

### Strategy V3: `momentum_strategy_v3.py`

Intraday momentum trading strategy with enhanced features.

**Configuration:**
- Total Capital: ₹500,000
- Max Stocks per Day: 5
- Max Stocks per Sector: 2

**Entry Filters:**
- Minimum Gap: 1.5% (up/down)
- Minimum Volume Ratio: 1.75x (vs 10-day avg)
- Market must be above 20-day MA

**Risk Management:**
- Stop Loss: 2.5%
- Target: 2.0%
- Partial Exit: 1.2% (50% position)
- Trailing Stop: Enabled (triggers at +1%, trails 0.5%)
- Time-Based Exit: 2.5 hours if profitable

**Sector Diversification:**
- Banking: HDFCBANK, ICICIBANK, SBIN, AXISBANK, KOTAKBANK
- IT: TCS, INFY, WIPRO
- Consumer: HINDUNILVR, ITC, TITAN
- Auto: MARUTI
- Telecom: BHARTIARTL
- Diversified: RELIANCE, LT

**Exit Reasons:**
- STOP_LOSS
- TARGET
- PARTIAL_PROFIT
- TRAILING_STOP
- TIME_EXIT
- EOD_CLOSE

---

### Equity Strategy: `momentum_strategy-equity_v1.py`

Long-term equity momentum strategy with monthly/weekly rebalancing.

**Momentum Score Formula:**
```
Momentum Score = (1W Return × 10%) + (1M Return × 30%) + (3M Return × 60%)
```

**Entry Criteria (Monthly):**
- Trend Change = 'Y' (new uptrend)
- Trend Direction = 'Uptrend'
- Ranked by momentum score
- Max 15 positions

**Entry Criteria (Weekly):**
- Weekly Trend Change = 'Y'
- Weekly Trend = 'Uptrend'
- Monthly Trend = 'Uptrend' (confirmation)
- Not already in monthly portfolio

**Position Sizing:**
- Initial: ₹50,000 per position
- Scales with capital growth (1.5x, 2x, 3x, 4x, 5x, 6x)

**Exit Rules:**
- Trend reversal (monthly downtrend)
- Trailing stop-loss (5% for weekly positions)

---

## Backtesting

### Scripts

1. **`run_backtest_30days.py`** - 30-day backtest (V1)
2. **`run_backtest_30days_v2.py`** - 30-day backtest (V2)
3. **`run_backtest_60days_v2.py`** - 60-day backtest (V2)
4. **`backtest_momentum_strategy.py`** - General momentum backtest
5. **`satya-backtest.py`** - Custom backtest utility

**Backtest Features:**
- Configurable date ranges
- Detailed trade logging
- Performance metrics:
  - Total Return %
  - Max Drawdown
  - Sharpe Ratio
  - Win Rate
  - Profit Factor
  - Average Win/Loss
- Sector-wise breakdown
- Daily/weekly/monthly results
- Export to Excel with formatting

**Output:** Timestamped Excel files (e.g., `momentum_backtest_v3_30days_20260206_110204.xlsx`)

---

## TradingView Indicators

### Pine Script: `v2.pine`

Multi-Timeframe Trend Analysis overlay indicator.

**Features:**
- 5 configurable timeframes
- Per-timeframe weights
- EMA (fast/slow) signals
- RSI momentum signals
- Weighted trend score
- Color-coded signal cells
- Aggregate bias label
- Alert conditions

**Inputs:**
- Last Candle (0 = current, 1+ = closed)
- Normalize Total Score (bool)
- EMA Fast/Slow Length
- RSI Length, Up/Down Thresholds
- Timeframe 1-5 (e.g., 15, 75, D, W, M)
- Weight 1-5
- Table Position (4 corners)
- Table BG Transparency
- Show Weights in TF Column

**Default Settings:**
- Timeframes: 15, 75, D, W, M
- Weights: 1, 6, 6, 6, 6
- EMA: 8/21
- RSI: 14, Up: 60, Down: 40

**Alert Conditions:**
- All Timeframes Bullish
- All Timeframes Bearish
- Total Score ≥ threshold
- Total Score ≤ threshold
- Score crosses 0 (up/down)

### Pine Script: `MultiTimeFrame.pine`

Simplified version of the multi-timeframe indicator.

---

## Configuration

### File: `config.py`

Central configuration for the trading strategies.

**Date Range:**
- START_DATE: "2025-01-01"
- END_DATE: "2026-01-14"

**Stock Selection:**
- TOP_N_STOCKS: 8

**Stop Loss:**
- INITIAL_STOP_LOSS_PCT: 7%
- TRAILING_STOP_LOSS_PCT: 7%
- TRAILING_TRIGGER_PCT: 12%

**Portfolio:**
- INITIAL_CAPITAL: ₹100,000

**Momentum Weights:**
- 1W: 10%
- 1M: 30%
- 3M: 60%

**Rolling Windows:**
- 1W: 5 days
- 1M: 21 days
- 3M: 63 days
- 6M: 126 days

**Filtering:**
- MIN_AVG_VOLUME: 50,000
- MAX_VOLATILITY: 4%
- MIN_1M_RETURN: 0%

---

## Data Files

| File | Description |
|------|-------------|
| `data/nifty500list.csv` | Nifty 500 stock symbols |
| `data/nifty500list_10.csv` | Top 10 Nifty 500 stocks |
| `data/stock-price.csv` | Historical stock prices |
| `data/stock-daily-data.csv` | Daily stock data |
| `data/SILVERBEES_monthly_returns.csv` | SilverBees returns |

---

## Output Files

The application generates timestamped Excel files:
- `all_indices_returns_*.xlsx` - Indices data with WhatIf sheet
- `nse500_stock_data.xlsx` - Equities data
- `momentum_backtest_*.xlsx` - Backtest results

---

## Usage Examples

### Get Indices Data
```bash
python all-index-data-to-excel-v6.py
```

### Get Equities Data
```bash
python all-equities-data-to-excel-v1.py
```

### Run Backtest
```bash
python momentum_strategy_v3.py
```
