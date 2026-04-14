# Sentinel Square

Sentinel Square is an autonomous AI content system that generates and schedules Binance Square posts while exposing a premium real-time command dashboard for operations oversight.

## Architecture

- `sentinel-worker`: Python 3.12 + FastAPI automation engine, scheduler, API, and SSE stream.
- `sentinel-dashboard`: Next.js 15 App Router dashboard with a dark-mode command center UI.

## Core Capabilities

- **Autonomous throughput:** Targets 30-50 posts every 24 hours.
- **Persona-balanced generation:**
  - 30% Technical Analyst
  - 20% Macro / News
  - 20% Educator
  - 30% Community / Engagement
- **Human protocol:** Randomized 17-78 minute jitter and a daily 5-hour sleep window (`02:00-07:00` EAT by default).
- **Ops visibility:** `/status`, `/posts`, and `/events` endpoints for dashboard and external monitors.
- **Live telemetry:** SSE-backed activity terminal and runtime pulse state.

## Worker Setup

```bash
cd sentinel-square/sentinel-worker
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Worker starts at `http://localhost:8585`.

### Required `.env`

```env
BINANCE_API_KEY=your-binance-api-key
GEMINI_API_KEY=your-gemini-api-key
SLEEP_WINDOW_START=02:00
SLEEP_WINDOW_END=07:00
TIMEZONE=Africa/Nairobi
```

## Dashboard Setup

```bash
cd sentinel-square/sentinel-dashboard
npm install
# optional API override
# set NEXT_PUBLIC_WORKER_URL=http://localhost:8585
npm run dev
```

Dashboard runs at `http://localhost:3000`.

## API Reference

- `GET /health` - quick health probe.
- `GET /status` - status, next post timestamp, counters, recent logs.
- `GET /posts?limit=50` - post history slice.
- `GET /events` - Server-Sent Events log stream.

## Portfolio Positioning

This project demonstrates Blair Momanyi's ability to combine:

- autonomous agent design,
- resilient backend scheduling,
- real-time frontend telemetry,
- and deployment-focused DevOps workflows.

It is presented as an **Autonomous AI Content Agent** for crypto-native community operations.
