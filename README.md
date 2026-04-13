<div align="center">

# ⚡ SENTINEL-SQUARE

### Autonomous Content Engine for Binance Square

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-F0B90B?style=flat-square)](LICENSE)

**A production-grade, human-mimicking content engine that autonomously generates and publishes 30–50 crypto posts daily to Binance Square using multi-persona AI, async scheduling, and a real-time monitoring dashboard.**

[Live Dashboard](https://sentinel-square.vercel.app) · [Architecture](#architecture) · [Quick Start](#quick-start) · [Deployment](#deployment)

</div>

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   SENTINEL-SQUARE V4.0                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐     ┌──────────────────────────┐   │
│  │  sentinel-worker │     │   sentinel-dashboard     │   │
│  │  (DigitalOcean)  │     │      (Vercel)            │   │
│  │                  │     │                          │   │
│  │  ┌────────────┐  │     │  ┌────────────────────┐  │   │
│  │  │ scheduler  │  │     │  │  System Status     │  │   │
│  │  │ (APSchedule│  │     │  │  Activity Log (SSE)│  │   │
│  │  │  17-78min) │  │     │  │  Post Countdown    │  │   │
│  │  └─────┬──────┘  │     │  │  Persona Stats     │  │   │
│  │        │         │     │  └────────┬───────────┘  │   │
│  │  ┌─────▼──────┐  │     │           │              │   │
│  │  │  engine    │  │◄────┼───────────┘              │   │
│  │  │ (orchestr.)│  │ REST+SSE                       │   │
│  │  └──┬────┬────┘  │     └──────────────────────────┘   │
│  │     │    │       │                                    │
│  │  ┌──▼┐ ┌▼─────┐ │     ┌──────────────────────────┐   │
│  │  │Gen│ │Publi-│ │     │    External APIs          │   │
│  │  │era│ │sher  │─┼────►│  • Binance Square API     │   │
│  │  │tor│ │      │ │     │  • Google Gemini 2.5      │   │
│  │  │   │ └──────┘ │     │  • CoinGecko (trending)   │   │
│  │  └───┘          │     └──────────────────────────┘   │
│  └─────────────────┘                                    │
└──────────────────────────────────────────────────────────┘
```

## ✨ Key Features

### 🤖 Agentic Workflows
- **Fully autonomous** 24/7 operation with zero human intervention required
- Self-scheduling content cycles with intelligent sleep/wake patterns
- Automatic daily resets and adaptive sleep window randomization

### 🎭 Multi-Persona AI (Human-Synthesis Protocol)
| Persona | Weight | Focus |
|---------|--------|-------|
| 📊 **Technical** | 30% | Support/Resistance on $BTC, $ETH, $BNB |
| 📰 **News** | 20% | ETF flows, macro trends, regulatory updates |
| 🎓 **Educator** | 20% | #BNBChain deep dives, RWA, DeFi concepts |
| 💬 **Community** | 30% | Engagement questions, trading psychology |

### ⏱️ Asynchronous Scheduling
- **Human jitter**: Randomized 17–78 minute posting intervals
- **Sleep mode**: 5-hour overnight window (randomized daily)
- **Anti-bot detection**: Variable sentence structure, casual tone, natural formatting
- Powered by APScheduler with AsyncIO for non-blocking execution

### 📊 Real-Time Dashboard
- Live engine status (Running / Sleeping / Stopped)
- Server-Sent Events (SSE) log streaming
- Countdown timer to next scheduled post
- Persona distribution analytics
- Connection health monitoring

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Content Engine** | Python 3.12, AsyncIO | Async orchestration |
| **LLM** | Google Gemini 2.5 Flash | Multi-persona content generation |
| **Market Data** | CoinGecko API (free) | Live prices + trending coins |
| **Publishing** | Binance Square API | Automated posting |
| **Scheduling** | APScheduler | Human-like timing with jitter |
| **Status API** | FastAPI + Uvicorn | REST + SSE endpoints |
| **Dashboard** | Next.js 15, Tailwind CSS | Real-time monitoring UI |
| **Process Mgmt** | PM2 | Production process management |
| **Hosting** | DigitalOcean + Vercel | Worker + Dashboard |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- A [Binance Square API Key](https://www.binance.com/en/square) (Creator Center)
- A [Google Gemini API Key](https://aistudio.google.com/) (free tier)

### 1. Clone the Repository
```bash
git clone https://github.com/b1aiirrr/squareAutomation.git
cd squareAutomation
```

### 2. Set Up the Worker
```bash
cd sentinel-worker

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 3. Set Up the Dashboard
```bash
cd sentinel-dashboard

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your worker API URL
```

### 4. Run Locally
```bash
# Terminal 1: Start the worker
cd sentinel-worker
python main.py

# Terminal 2: Start the dashboard
cd sentinel-dashboard
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

---

## 🌐 Deployment

### Worker on DigitalOcean

```bash
# SSH into your server
ssh root@46.101.66.34

# Clone the repo
cd /opt
git clone https://github.com/b1aiirrr/squareAutomation.git
cd squareAutomation/sentinel-worker

# Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure secrets
cp .env.example .env
nano .env    # Add your BINANCE_SQUARE_API_KEY and GEMINI_API_KEY

# Open the API port
ufw allow 8585

# Start with PM2
pm2 start "cd /opt/squareAutomation/sentinel-worker && venv/bin/python main.py" \
    --name sentinel-worker \
    --log /var/log/sentinel-worker.log

pm2 save
pm2 startup    # Enable auto-start on reboot
```

### Dashboard on Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import the `b1aiirrr/squareAutomation` repository
3. Set **Root Directory** to `sentinel-dashboard`
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `http://46.101.66.34:8585`
5. Deploy!

---

## 📁 Project Structure

```
squareAutomation/
├── sentinel-worker/          # Python content engine
│   ├── main.py               # Entry point
│   ├── engine.py             # Core orchestrator
│   ├── scheduler.py          # APScheduler with human jitter
│   ├── generator.py          # Gemini LLM + CoinGecko context
│   ├── publisher.py          # Binance Square API client
│   ├── api.py                # FastAPI status server (port 8585)
│   ├── config.py             # Environment configuration
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment template
│
├── sentinel-dashboard/       # Next.js monitoring dashboard
│   ├── app/
│   │   ├── layout.tsx        # Root layout with fonts & SEO
│   │   ├── page.tsx          # Main dashboard page
│   │   └── globals.css       # Design system
│   ├── vercel.json           # Vercel deployment config
│   ├── .env.example          # Environment template
│   └── package.json          # Node dependencies
│
├── README.md                 # This file
└── .gitignore                # Security-first ignore rules
```

---

## 🔐 Environment Variables

### Worker (`sentinel-worker/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `BINANCE_SQUARE_API_KEY` | ✅ | API key from Binance Square Creator Center |
| `GEMINI_API_KEY` | ✅ | Google Gemini API key from AI Studio |
| `TIMEZONE` | ❌ | Default: `Africa/Nairobi` |
| `SLEEP_START_HOUR` | ❌ | Default: `2` (2 AM) |
| `SLEEP_END_HOUR` | ❌ | Default: `7` (7 AM) |
| `MIN_INTERVAL_MINUTES` | ❌ | Default: `17` |
| `MAX_INTERVAL_MINUTES` | ❌ | Default: `78` |
| `DAILY_POST_TARGET` | ❌ | Default: `40` |
| `API_PORT` | ❌ | Default: `8585` |
| `ALLOWED_ORIGINS` | ❌ | CORS origins (comma-separated) |

### Dashboard (`sentinel-dashboard/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ | URL of the worker API (e.g., `http://46.101.66.34:8585`) |

---

## 📄 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/status` | Current engine state (uptime, posts, next post time) |
| `GET` | `/api/logs` | SSE stream of real-time activity logs |
| `GET` | `/api/logs/history?limit=100` | Last N log entries as JSON |
| `GET` | `/api/health` | Simple health check |

---

## 👤 Author

**Blair Momanyi** — [@b1aiirrr](https://github.com/b1aiirrr)

Built with Agentic AI Workflows, Asynchronous Scheduling, and Multi-Persona Content Synthesis.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
