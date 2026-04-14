# 🚀 Sentinel Square — Autonomous Content & Trading Engine

> **The world's most advanced autonomous Binance Square agent.**
> Built by [@MOMIGI](https://x.com) — Copyright © 2025 MOMIGI. All rights reserved.

[![Vercel](https://img.shields.io/badge/Vercel-Ready-black?style=flat-square&logo=vercel)](https://vercel.com)
[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square&logo=python)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MOMIGI-red?style=flat-square)](LICENSE)

---

## 🎯 What is Sentinel Square?

Sentinel Square is a **fully autonomous AI-powered agent** designed to:

- 📝 **Generate & publish** high-engagement content on Binance Square (40+ posts/day)
- 📊 **Execute intelligent trades** with multi-indicator technical analysis
- 💰 **Maximize rewards** through yield farming, launchpools, and referral optimization
- 🤖 **Cross-post** to multiple accounts simultaneously
- 📈 **Report performance** in real-time via a beautiful dashboard

---

## ⚡ Features

### 🤖 Autonomous Content Engine
- **4 AI Personas**: Technical Sniper, Narrative Hunter, Ecosystem Architect, Sentiment Pulse
- **"Lively" Style**: No robotic headers — sharp hooks, specific $TICKERS, natural emojis
- **Engagement Triggers**: Every post ends with a question/prompt to drive comments
- **Referral CTAs**: Subtle fee discount links (1 in 5 posts)

### 📊 Advanced Trading Engine
- **Multi-Indicator Analysis**: RSI, MACD, Bollinger Bands, EMA crossover
- **Smart Entry Detection**: Only trades when 3+ indicators align
- **Kelly Criterion Position Sizing**: Adaptive sizing based on confidence
- **Risk Management**: 1% position size, -2% SL, +3-5% TP
- **Automated Trade Reports**: Every trade posted to both accounts

### 💰 Rewards Maximization
- **Yield Engine**: Auto-sweeps idle USDT into Simple Earn
- **Launchpool Auto-Staker**: Detects and stakes into new token launches
- **Dual Investment**: Auto-subscribes to dual investment products
- **Referral Optimizer**: Tracks best-performing tickers and amplifies CTAs

### 👥 Multi-Account Support
- **Primary Account**: Trading + Posting
- **Friend Accounts**: Cross-posting of all content
- **Trade Reports**: Posted to ALL accounts simultaneously

### 🎨 Professional Dashboard
- **Real-time SSE Streaming**: Live activity logs
- **Rewards Hub**: Yield, Launchpools, Referrals
- **Trading Stats**: Win rate, total trades, profit/loss
- **Multi-Account Status**: Side-by-side sync status

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SENTINEL SQUARE ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌──────────────┐         ┌──────────────────┐                │
│   │  Vercel      │         │  Remote Server   │                │
│   │  Dashboard   │◄───────►│  (46.101.66.34) │                │
│   │  (Next.js)   │  SSE    │  PM2 + Python    │                │
│   └──────────────┘         └──────────────────┘                │
│         │                            │                           │
│         │                     ┌─────┴─────┐                     │
│         │                     │           │                     │
│         │              ┌─────▼───┐ ┌────▼────┐               │
│         │              │ Engine  │ │ Rewards  │               │
│         │              │ (Trade) │ │ Engine   │               │
│         │              └─────┬───┘ └────┬────┘               │
│         │                    │          │                     │
│         │              ┌─────▼──────────▼────┐               │
│         │              │   Scheduler         │               │
│         │              │ (APScheduler)       │               │
│         │              └─────┬──────────┬────┘               │
│         │                    │          │                     │
│         │              ┌──────▼──┐  ┌───▼────┐               │
│         │              │ Binance  │  │ Binance │               │
│         │              │ Square   │  │ Trading │               │
│         │              │ API      │  │ API     │               │
│         │              └──────────┘  └─────────┘               │
│         │                                                     │
└─────────┴─────────────────────────────────────────────────────┘
```

---

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- PM2 (for production)
- Vercel CLI (for dashboard)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/b1aiirrr/squareAutomation.git
cd squareAutomation/sentinel-worker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### Frontend Setup

```bash
cd sentinel-dashboard
npm install
npm run dev  # Development
npm run build  # Production
```

---

## ⚙️ Configuration

### Environment Variables

```env
# ===========================================
# BINANCE API KEYS
# ===========================================

# Primary Binance Square API (Posting)
BINANCE_SQUARE_API_KEY=your_square_api_key

# Gemini AI for content generation
GEMINI_API_KEY=your_gemini_key

# Trading API (Spot Trading)
TRADING_API_KEY=your_trading_api_key
TRADING_API_SECRET=your_trading_api_secret

# Multi-Account Support
FRIEND_SQUARE_API_KEY=friend_square_api_key

# ===========================================
# REWARDS & MONETIZATION
# ===========================================

# Your Binance referral link
BINANCE_REFERRAL_LINK=https://www.binance.com/referral/...

# ===========================================
# OPERATIONAL SETTINGS
# ===========================================

TIMEZONE=Africa/Nairobi
SLEEP_WINDOW_START=02:00
SLEEP_WINDOW_END=07:00
DAILY_POST_TARGET=40
```

### Trading Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `TRADE_PERCENT_OF_WALLET` | 0.01 | Position size (% of USDT) |
| `STOP_LOSS_PCT` | 0.02 | Stop-loss threshold |
| `TAKE_PROFIT_PCT` | 0.05 | Take-profit target |
| `REFERRAL_CHANCE` | 0.20 | Chance of CTA in post |

---

## 📊 Technical Analysis Indicators

Sentinel Square uses a **multi-indicator scoring system** for trade signals:

| Indicator | Weight | Bullish Signal |
|-----------|--------|----------------|
| **RSI** | 2 points | < 30 (oversold) |
| **MACD** | 2 points | Above signal line + histogram positive |
| **EMA Crossover** | 2 points | Price > 20 EMA > 50 EMA |
| **Bollinger Bands** | 1 point | Near lower band (< 0.3 position) |
| **Volume Spike** | 1 point | Volume > 1.5x average |

**Trade Trigger**: Score ≥ 3 AND RSI < 75

---

## 🎨 Content Personas

### 1. Technical Sniper (30%)
> Focus: Liquidity zones, order blocks, 4H/1D trend shifts
```
$BTC just swept the liquidations at $96,200 — time to watch for reversal.
$BNB holding $580 could be our reload entry 📈
Drop your targets below 👇
#TechnicalAnalysis #PriceAction
```

### 2. Narrative Hunter (20%)
> Focus: Macro trends, ETF flows, Fed decisions
```
ETF inflows just hit $1.2B in 24 hours. DXY dropping.
You know what this means for $BTC...
Who's still holding? 🙋
#CryptoNews #Macro
```

### 3. Ecosystem Architect (20%)
> Focus: BNB Chain, RWA, DeFi education
```
RWA tokenization is the future of finance.
$BNB is quietly building the infrastructure.
Here's why it matters 🎓
#BNBChain #DeFi
```

### 4. Sentiment Pulse (30%)
> Focus: Trading psychology, diamond hands, risk management
```
Hot take: Most traders lose because they overtrade.
Quality over quantity. Someone needed to say it 🔥
What's your $BTC entry? Drop it below 👇
#TradingPsychology
```

---

## 🚀 Deployment

### Remote Server (PM2)

```bash
# SSH into your server
ssh root@your-server-ip

# Navigate to worker directory
cd /opt/squareAutomation/sentinel-worker

# Install dependencies
pip install -r requirements.txt

# Start with PM2
pm2 start main.py --name sentinel-worker

# View logs
pm2 logs sentinel-worker

# Restart on changes
pm2 restart sentinel-worker
```

### Vercel Dashboard

```bash
cd sentinel-dashboard
vercel --prod
```

---

## 📈 Dashboard Sections

### 1. Engine Status
- Live runtime monitor
- Next post countdown
- Sleep window indicator

### 2. Rewards Hub
- 💰 **Yield Engine**: Simple Earn sweep status
- 🚀 **Launchpools**: Active staking opportunities
- 🔗 **Referral CTAs**: Engagement tracking

### 3. Trading Engine
- Position size (1%)
- Stop-loss (-2%)
- Take-profit (+5%)
- Win rate tracking

### 4. Multi-Account Sync
- Primary vs Friend account status
- Post sync progress

---

## 🔐 Security

- **API Keys**: Never commit `.env` files
- **Withdrawals**: Trading API should have withdrawals **disabled**
- **IP Whitelist**: Recommended for production API keys
- **Rate Limiting**: Built-in delays to avoid API throttling

---

## 📝 License

> **Copyright © 2025 MOMIGI. All rights reserved.**

This project is proprietary software. Unauthorized copying, distribution, or use is strictly prohibited.

---

## 👨‍💻 Author

**MOMIGI** — [@MOMIGI](https://x.com)

Built with ❤️ for the Binance Square community.

---

## 🗺️ Roadmap

- [ ] **Futures Trading**: Add perpetual futures support
- [ ] **Copy Trading**: Automatically copy top traders
- [ ] **Telegram Bot**: Send alerts via Telegram
- [ ] **Analytics Dashboard**: Track engagement metrics
- [ ] **Multi-Strategy**: Combine RSI + MACD + AI signals

---

<p align="center">
  <strong>Sentinel Square — Turn your Binance Square presence into an autonomous income machine.</strong>
</p>
