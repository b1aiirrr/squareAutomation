"""
Sentinel-Square Core Engine
=============================
Orchestrates the full content cycle: checks sleep window, generates content
via the LLM, publishes to Binance Square, and logs all results.
"""

import json
import logging
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import (
    TIMEZONE,
    SLEEP_START_HOUR,
    SLEEP_END_HOUR,
    DAILY_POST_TARGET,
    LOG_FILE,
    FRIEND_SQUARE_API_KEY,
)
from generator import generate_post
from publisher import publish_post
from trading_engine import TradingEngine
from .state import SharedState

logger = logging.getLogger("sentinel.engine")

# ---------------------------------------------------------------------------
# Global Trading Engine
# ---------------------------------------------------------------------------
_trading_engine = None

def init_trading(state: SharedState):
    global _trading_engine
    _trading_engine = TradingEngine(state)

# ---------------------------------------------------------------------------
# Sleep Window & Reset
# ---------------------------------------------------------------------------
_sleep_window = {"start": f"{SLEEP_START_HOUR:02d}:00", "end": f"{SLEEP_END_HOUR:02d}:00"}

def _now() -> datetime:
    return datetime.now(_tz)

def recalculate_sleep_window():
    global _sleep_window
    jitter = random.randint(-1, 1)
    start_hour = max(0, min(23, SLEEP_START_HOUR + jitter))
    end_hour = start_hour + 5
    if end_hour >= 24:
        end_hour = end_hour - 24

    _sleep_window = {
        "start": f"{start_hour:02d}:00",
        "end": f"{end_hour:02d}:00",
    }
    logger.info(f"Sleep window set: {_sleep_window['start']} – {_sleep_window['end']} {TIMEZONE}")

def is_sleeping() -> bool:
    now = _now()
    start_hour = int(_sleep_window["start"].split(":")[0])
    end_hour = int(_sleep_window["end"].split(":")[0])
    current_hour = now.hour

    if start_hour < end_hour:
        return start_hour <= current_hour < end_hour
    else:
        return current_hour >= start_hour or current_hour < end_hour

async def daily_reset(state: SharedState):
    recalculate_sleep_window()
    await state.add_log("info", f"Daily reset complete. New sleep window: {_sleep_window['start']} - {_sleep_window['end']}")

# ---------------------------------------------------------------------------
# Core Content Cycle
# ---------------------------------------------------------------------------
async def run_cycle(state: SharedState) -> dict:
    """
    Execute one content cycle:
    1. Check sleep window
    2. Check daily post limit
    3. Generate content
    4. Trade if bullish
    5. Publish to Binance Square (Primary + Optional Friend)
    6. Log result
    """
    state.status = "running"

    if is_sleeping():
        await state.add_log("info", "Currently in sleep window — skipping cycle")
        return {"status": "skipped", "reason": "sleep_window"}

    # Daily limit check
    snapshot = await state.snapshot()
    if snapshot["posts_today"] >= DAILY_POST_TARGET:
        await state.add_log("info", f"Daily target reached ({snapshot['posts_today']}/{DAILY_POST_TARGET})")
        return {"status": "skipped", "reason": "daily_limit_reached"}

    # --- Generate content ---
    try:
        post_data = await generate_post()
    except Exception as e:
        await state.add_log("error", f"Content generation failed: {e}")
        return {"status": "error", "reason": f"generation_failed: {e}"}

    persona = post_data["persona"]
    content = post_data["content"]
    tickers = post_data["tickers"]

    # --- Task 2: Trading Engine ---
    trade_info = None
    if _trading_engine:
        trade_info = await _trading_engine.execute_trade_if_bullish(content, tickers)

    # --- Task 4: Human-Persona Sync (Trade Post) ---
    if trade_info:
        trade_content = (
            f"Just entered a long on ${trade_info['symbol'].replace('USDT', '')} at {trade_info['entry']:.4f}. "
            f"Target is {trade_info['tp']:.4f}. Let's see if the bulls hold the line! 🚀📈 #Trading #BinanceSquare"
        )
        trade_post_result = await publish_post(trade_content)
        if trade_post_result["success"]:
            await state.add_log("info", f"Trade post published: {trade_post_result['post_url']}")

    # --- Task 1: Publish & Cross-post ---
    result = await publish_post(content)
    
    # Cross-post to friend if configured
    if FRIEND_SQUARE_API_KEY:
        friend_result = await publish_post(content, api_key=FRIEND_SQUARE_API_KEY)
        if friend_result["success"]:
            await state.add_log("info", f"Cross-posted to friend account: {friend_result['post_url']}")

    # --- Update state ---
    if result["success"]:
        await state.add_post({
            "posted_date": datetime.utcnow().date().isoformat(),
            "persona": persona,
            "post_id": result["post_id"],
            "post_url": result["post_url"],
            "content": content
        })

        await state.add_log("info", f"Published [{persona}] post to Binance Square")
        return {"status": "success", "post_url": result["post_url"]}
    else:
        await state.add_log("error", f"Publishing failed: {result.get('error')}")
        return {"status": "failed", "error": result.get("error")}
