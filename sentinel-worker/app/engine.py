"""
Sentinel-Square Core Engine v5
=============================
Orchestrates the full content cycle: checks sleep window, generates content
via the LLM, executes trades if bullish, publishes to Binance Square.
"""

import asyncio
import logging
import random
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import httpx

logger = logging.getLogger("sentinel.engine")

# ---------------------------------------------------------------------------
# Config (loaded from environment)
# ---------------------------------------------------------------------------
import os
from dotenv import load_dotenv
load_dotenv()

TIMEZONE = os.getenv("TIMEZONE", "Africa/Nairobi")
SLEEP_START_HOUR = int(os.getenv("SLEEP_WINDOW_START", "2"))
SLEEP_END_HOUR = int(os.getenv("SLEEP_WINDOW_END", "7"))
DAILY_POST_TARGET = int(os.getenv("DAILY_POST_TARGET", "40"))

BINANCE_SQUARE_API_KEY = os.getenv("BINANCE_SQUARE_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TRADING_API_KEY = os.getenv("TRADING_API_KEY", "")
TRADING_API_SECRET = os.getenv("TRADING_API_SECRET", "")
FRIEND_SQUARE_API_KEY = os.getenv("FRIEND_SQUARE_API_KEY", "")
BINANCE_REFERRAL_LINK = os.getenv("BINANCE_REFERRAL_LINK", "")
REFERRAL_CHANCE = 0.20

BINANCE_POST_URL = "https://www.binance.com/bapi/composite/v1/public/pgc/openApi/content/add"

# ---------------------------------------------------------------------------
# Sleep Window
# ---------------------------------------------------------------------------
_tz = ZoneInfo(TIMEZONE)
_sleep_window = {"start": f"{SLEEP_START_HOUR:02d}:00", "end": f"{SLEEP_END_HOUR + 5:02d}:00"}

def recalculate_sleep_window():
    global _sleep_window
    jitter = random.randint(-1, 1)
    start_hour = max(0, min(23, SLEEP_START_HOUR + jitter))
    end_hour = start_hour + 5
    _sleep_window = {"start": f"{start_hour:02d}:00", "end": f"{end_hour:02d}:00"}

def is_sleeping() -> bool:
    now = datetime.now(_tz)
    start_hour = int(_sleep_window["start"].split(":")[0])
    end_hour = int(_sleep_window["end"].split(":")[0])
    current_hour = now.hour
    if start_hour < end_hour:
        return start_hour <= current_hour < end_hour
    return current_hour >= start_hour or current_hour < end_hour

def _now() -> datetime:
    return datetime.now(_tz)

# ---------------------------------------------------------------------------
# Binance Square Publishing
# ---------------------------------------------------------------------------
async def publish_to_square(content: str, api_key: str) -> dict:
    headers = {
        "Content-Type": "application/json",
        "X-Square-OpenAPI-Key": api_key,
        "clienttype": "binanceSkill",
    }
    payload = {"bodyTextOnly": content}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(BINANCE_POST_URL, headers=headers, json=payload)
            data = response.json()

            if response.status_code == 200 and data.get("code") == "000000":
                post_id = data.get("data", {}).get("id", "unknown")
                post_url = f"https://www.binance.com/square/post/{post_id}"
                return {"success": True, "post_id": str(post_id), "post_url": post_url}
            else:
                return {"success": False, "error": data.get("message", "Unknown error")}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------------------------------------------------------------------------
# State Management
# ---------------------------------------------------------------------------
_state = None
_posts = []

def set_state(state):
    global _state
    _state = state

def get_state():
    return _state

def load_posts(path):
    global _posts
    import json
    from pathlib import Path
    p = Path(path) if isinstance(path, str) else path
    if p.exists():
        try:
            with open(p) as f:
                _posts = json.load(f)
        except:
            _posts = []
    return _posts

def save_posts(path, posts):
    import json
    from pathlib import Path
    p = Path(path) if isinstance(path, str) else path
    with open(p, "w") as f:
        json.dump(posts[-500:], f, indent=2, default=str)

# ---------------------------------------------------------------------------
# Content Generation (Advanced)
# ---------------------------------------------------------------------------
async def generate_content_advanced(persona: str) -> tuple[str, list[str]]:
    from .content_generator import generate_content
    
    market_data = {}
    if _trading_client:
        try:
            # Fetch real-time prices for top assets
            tickers = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
            prices = _trading_client.get_all_tickers()
            market_data = {p["symbol"].replace("USDT", ""): float(p["price"]) for p in prices if p["symbol"] in tickers}
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")

    content, tickers = await generate_content(persona, market_data)
    return content, tickers

# ---------------------------------------------------------------------------
# Trading Execution
# ---------------------------------------------------------------------------
_trading_client = None
if TRADING_API_KEY and TRADING_API_SECRET:
    from binance.client import Client
    _trading_client = Client(TRADING_API_KEY, TRADING_API_SECRET)

async def execute_trade_if_bullish(content: str, tickers: list[str]) -> dict | None:
    if not _trading_client:
        return None

    bullish_indicators = ["bullish", "long", "breakout", "🚀", "📈", "buy", "accumulation", "support"]
    is_bullish = any(ind in content.lower() for ind in bullish_indicators)

    if not is_bullish or not tickers:
        return None

    ticker = tickers[0].replace("$", "").upper()
    symbol = f"{ticker}USDT"

    try:
        balance = _trading_client.get_asset_balance(asset="USDT")
        usdt_balance = float(balance["free"])

        if usdt_balance <= 10:
            if _state:
                await _state.add_log("warning", f"Insufficient USDT: {usdt_balance}")
            return None

        trade_amount = usdt_balance * 0.01  # 1% position
        if trade_amount < 10:
            trade_amount = 10

        avg_price = _trading_client.get_avg_price(symbol=symbol)
        current_price = float(avg_price["price"])
        quantity = round(trade_amount / current_price, 4)

        if _state:
            await _state.add_log("info", f"SMART BUY: {quantity} {ticker} (~\${trade_amount:.2f})")

        order = _trading_client.order_market_buy(symbol=symbol, quantity=quantity)

        sl_price = round(current_price * 0.98, 4)
        tp_price = round(current_price * 1.05, 4)

        trade_info = {
            "symbol": symbol,
            "entry": current_price,
            "sl": sl_price,
            "tp": tp_price,
            "quantity": quantity,
            "order_id": order["orderId"],
        }

        if _state:
            await _state.add_log("info", f"Trade: {symbol} @ {current_price} | SL: {sl_price} TP: {tp_price}")

        return trade_info

    except Exception as e:
        if _state:
            await _state.add_log("error", f"Trading Error: {str(e)}")
        logger.error(f"Trading error: {e}")

    return None

# ---------------------------------------------------------------------------
# Daily Reset
# ---------------------------------------------------------------------------
def daily_reset():
    recalculate_sleep_window()
    logger.info(f"Daily reset: {_sleep_window}")

# ---------------------------------------------------------------------------
# Init Trading
# ---------------------------------------------------------------------------
def init_trading(state):
    global _state
    _state = state
    logger.info("Trading engine initialized")

# ---------------------------------------------------------------------------
# Run Cycle
# ---------------------------------------------------------------------------
async def run_cycle(state) -> dict:
    global _posts

    state.status = "running"

    if is_sleeping():
        await state.add_log("info", "Sleeping - skipping cycle")
        return {"status": "skipped", "reason": "sleep_window"}

    persona_weights = {"technical": 0.30, "news": 0.20, "educator": 0.20, "community": 0.30}
    personas = list(persona_weights.keys())
    weights = list(persona_weights.values())
    persona = random.choices(personas, weights=weights, k=1)[0]

    content, tickers = await generate_content_advanced(persona)

    # Execute trade if bullish
    trade_info = await execute_trade_if_bullish(content, tickers)

    # Post trade signal if trade executed
    if trade_info:
        trade_report = (
            f"Just entered a long on ${trade_info['symbol'].replace('USDT', '')} "
            f"at ${trade_info['entry']:.4f}. Target: ${trade_info['tp']:.4f}. "
            f"Stop: ${trade_info['sl']:.4f}. 🚀📈 #Trading #BinanceSquare"
        )
        primary_trade = await publish_to_square(trade_report, BINANCE_SQUARE_API_KEY)
        if primary_trade["success"]:
            await state.add_log("info", f"Trade report posted to Primary: {primary_trade['post_url']}")
        else:
            await state.add_log("error", f"Primary Trade Post failed: {primary_trade.get('error')}")

        if FRIEND_SQUARE_API_KEY:
            friend_trade = await publish_to_square(trade_report, FRIEND_SQUARE_API_KEY)
            if friend_trade["success"]:
                await state.add_log("info", f"Trade report cross-posted to Friend: {friend_trade['post_url']}")
            else:
                await state.add_log("error", f"Friend Trade Post failed: {friend_trade.get('error')}")
        else:
            await state.add_log("warning", "Friend Account API Key missing - skipping cross-post")

    # Post main content to both accounts
    primary_result = await publish_to_square(content, BINANCE_SQUARE_API_KEY)
    if primary_result["success"]:
        await state.add_log("info", f"Main post published to Primary: {primary_result['post_url']}")
    else:
        await state.add_log("error", f"Primary Main Post failed: {primary_result.get('error')}")

    if FRIEND_SQUARE_API_KEY:
        friend_result = await publish_to_square(content, FRIEND_SQUARE_API_KEY)
        if friend_result["success"]:
            await state.add_log("info", f"Main post cross-posted to Friend: {friend_result['post_url']}")
        else:
            await state.add_log("error", f"Friend Main Post failed: {friend_result.get('error')}")
    else:
        await state.add_log("warning", "Friend Account API Key missing - skipping cross-post")

    # Save post
    payload = {
        "persona": persona,
        "content": content,
        "posted_at": datetime.utcnow().isoformat(),
        "posted_date": datetime.utcnow().date().isoformat(),
        "channel": "binance-square",
        "trade_executed": bool(trade_info)
    }
    _posts.append(payload)
    state.posts = _posts

    if primary_result["success"]:
        await state.add_log("info", f"Posted [{persona}]: {content[:60]}...")
        return {"status": "success", "post_url": primary_result.get("post_url")}
    else:
        await state.add_log("error", f"Post failed: {primary_result.get('error')}")
        return {"status": "failed"}
