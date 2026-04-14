"""
Sentinel-Square Core Engine
=============================
Orchestrates the full content cycle: checks sleep window, generates content
via the LLM, executes trades if bullish, publishes to Binance Square.
"""

import asyncio
import json
import logging
import random
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import httpx
from binance.client import Client
from binance.exceptions import BinanceAPIException

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
TRADE_PERCENT_OF_WALLET = float(os.getenv("TRADE_PERCENT_OF_WALLET", "0.01"))
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "0.02"))
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "0.05"))

BINANCE_SQUARE_API_KEY = os.getenv("BINANCE_SQUARE_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TRADING_API_KEY = os.getenv("TRADING_API_KEY", "")
TRADING_API_SECRET = os.getenv("TRADING_API_SECRET", "")
FRIEND_SQUARE_API_KEY = os.getenv("FRIEND_SQUARE_API_KEY", "")
BINANCE_REFERRAL_LINK = os.getenv("BINANCE_REFERRAL_LINK", "")
REFERRAL_CHANCE = 0.20

BINANCE_POST_URL = "https://www.binance.com/bapi/composite/v1/public/pgc/openApi/content/add"

# Trading client
_binance_client = None
if TRADING_API_KEY and TRADING_API_SECRET:
    try:
        _binance_client = Client(TRADING_API_KEY, TRADING_API_SECRET)
        logger.info("Binance trading client initialized")
    except Exception as e:
        logger.error(f"Failed to init trading client: {e}")

# ---------------------------------------------------------------------------
# Persona System (The Lively Overhaul)
# ---------------------------------------------------------------------------
SHARED_INSTRUCTIONS = (
    "You are Blair — a sharp, street-smart crypto trader who codes on a ThinkPad. "
    "You've been in the game since the 2017 ICO craze and survived the 2022 deleveraging. "
    "You speak in 'trader-vernacular' — think CT (Crypto Twitter) but professional enough for Binance Square. "
    "No robotic headers, no 'Hey everyone', no formal greetings. "
    "Every post MUST start with a 'Hook' (a sharp question, a contrarian take, or a direct observation). "
    "Use 2-3 specific $TICKERS (e.g. $BTC, $BNB, $SOL) and include emojis naturally. "
    "Line breaks are mandatory for readability. NO markdown (no **, no ##)."
)

PERSONA_PROMPTS = {
    "technical": (
        f"{SHARED_INSTRUCTIONS} "
        "Strategy: Technical Sniper. You focus on liquidity zones, order blocks, and 4H/1D trend shifts. "
        "You're not a moonboy; you're looking for where the big money is positioned. "
        "Mention specific price levels for $BTC or $BNB. Talk about 'sweeping lows' or 'retesting the breakout'. "
        "Tone: Analytical, objective, slightly cynical of 'retail' indicators like basic RSI. "
        "Hashtags: #TechnicalAnalysis #TradingTips #PriceAction."
    ),
    "news": (
        f"{SHARED_INSTRUCTIONS} "
        "Strategy: Narrative Hunter. You connect the dots between macro (Fed, CPI, DXY) and crypto price action. "
        "You're watching ETF inflows like a hawk. You understand how global liquidity drives $BTC. "
        "React to breaking news with 'Signal vs Noise' analysis. "
        "Tone: Fast-paced, informed, focused on the 'Big Picture'. "
        "Hashtags: #CryptoNews #Macro #MarketUpdate."
    ),
    "educator": (
        f"{SHARED_INSTRUCTIONS} "
        "Strategy: Ecosystem Architect. You deep dive into #BNBChain, RWA (Real World Assets), and liquid staking. "
        "You explain *why* a project has value, not just that the price is up. "
        "Break down complex DeFi concepts into 3-4 punchy insights that a a dev would respect. "
        "Tone: Knowledgeable, authoritative, forward-thinking. "
        "Hashtags: #BNBChain #DeFi #Web3Education."
    ),
    "community": (
        f"{SHARED_INSTRUCTIONS} "
        "Strategy: Sentiment Pulse. You're the voice of reason during panics and the reality check during mania. "
        "Share hard truths about trading psychology, risk management, and 'diamond hands' vs 'smart money'. "
        "Ask questions that make people rethink their bias. "
        "Tone: Relatable, experienced, slightly mentor-like but still 'one of us'. "
        "Hashtags: #CryptoCommunity #TradingPsychology #HODL."
    ),
}

PERSONA_WEIGHTS = {"technical": 0.30, "news": 0.20, "educator": 0.20, "community": 0.30}

ENGAGEMENT_TRIGGERS = [
    "Drop your targets below 📉.",
    "Is $BNB ready for the breakout or are we heading back to support?",
    "What's your $BTC target for EOY?",
    "Agree or am I missing something? Let me know in the comments.",
    "Which $ALT are you watching this week?",
]

_refersal_link_ctas = [
    f"Trading these levels on Binance? Get a fee discount here: {BINANCE_REFERRAL_LINK}",
    f"Maximize your gains with lower fees. Join me on Binance: {BINANCE_REFERRAL_LINK}",
    f"Still paying full fees? Use my link for a discount on Binance: {BINANCE_REFERRAL_LINK}",
]

# Gemini client
try:
    from google import genai
    _gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
    _gemini_model = "gemini-2.5-flash"
except:
    _gemini_client = None
    logger.warning("Gemini client not initialized")

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
# Content Generation
# ---------------------------------------------------------------------------
def generate_content_mock(persona: str) -> tuple[str, list[str]]:
    templates = {
        "technical": [
            "$BTC just swept the lows at $96,200. Time to watch for a reversal signal. If $BNB holds $580, we're heading back up 🚀 #TechnicalAnalysis",
            "The 4H chart on $ETH is painting a bull flag. Support at $2,850 is the key. Break above $3,100 and we're flying 📈 #TradingTips",
        ],
        "news": [
            "ETF inflows hitting $800M today. The macro tailwinds are aligning for risk assets. DXY dropping = crypto rip 📊 #Macro",
            "Fed still dovish in this environment. Global liquidity is expanding. Bull case for $BTC strengthening 🚀 #CryptoNews",
        ],
        "educator": [
            "RWA tokenization is the future. $BNB is positioning itself as the backbone for real-world asset DeFi. Here's why it matters 🎓 #BNBChain #DeFi",
            "Liquid staking on BNB Chain lets you earn yield without locking your assets. The flexibility is underrated 💰 #Web3Education",
        ],
        "community": [
            "Hard truth: most traders lose because they don't manage risk properly. 2% rule exists for a reason. Stay disciplined 💎 #TradingPsychology",
            "What's your $BTC entry? And more importantly - what's your exit strategy? Share below 👇 #CryptoCommunity",
        ],
    }
    body = random.choice(templates[persona])
    tickers = list(set(re.findall(r"\$[A-Z]{2,10}", body.upper())))
    return body, tickers

# ---------------------------------------------------------------------------
# Trading Execution
# ---------------------------------------------------------------------------
async def execute_trade_if_bullish(state, content: str, tickers: list[str]) -> dict | None:
    if not _binance_client:
        return None

    bullish_indicators = ["bullish", "long", "breakout", "🚀", "📈", "buy", "target"]
    is_bullish = any(ind in content.lower() for ind in bullish_indicators)

    if not is_bullish or not tickers:
        return None

    ticker = tickers[0].replace("$", "").upper()
    symbol = f"{ticker}USDT"

    try:
        balance = _binance_client.get_asset_balance(asset="USDT")
        usdt_balance = float(balance["free"])

        if usdt_balance <= 10:
            await state.add_log("warning", f"Insufficient USDT balance: {usdt_balance}")
            return None

        trade_amount = usdt_balance * TRADE_PERCENT_OF_WALLET
        if trade_amount < 10:
            trade_amount = 10

        avg_price = _binance_client.get_avg_price(symbol=symbol)
        current_price = float(avg_price["price"])
        quantity = round(trade_amount / current_price, 4)

        await state.add_log("info", f"Executing BUY for {quantity} {ticker} (~\${trade_amount:.2f})")

        order = _binance_client.order_market_buy(symbol=symbol, quantity=quantity)

        sl_price = round(current_price * (1 - STOP_LOSS_PCT), 4)
        tp_price = round(current_price * (1 + TAKE_PROFIT_PCT), 4)

        trade_info = {
            "symbol": symbol,
            "entry": current_price,
            "sl": sl_price,
            "tp": tp_price,
            "quantity": quantity,
            "order_id": order["orderId"],
        }

        await state.add_log("info", f"Trade done: {symbol} @ {current_price}. SL: {sl_price}, TP: {tp_price}")

        trade_post = (
            f"Just entered a long on ${ticker} at ${current_price}. "
            f"Target: ${tp_price}. Stop: ${sl_price}. "
            f"Let's see if the bulls hold! 🚀📈 #Trading #BinanceSquare"
        )
        await state.add_log("info", f"Trade post: {trade_post}")

        return trade_info

    except BinanceAPIException as e:
        await state.add_log("error", f"Binance API Error: {e.message}")
    except Exception as e:
        await state.add_log("error", f"Trading Error: {str(e)}")

    return None

# ---------------------------------------------------------------------------
# Post Building
# ---------------------------------------------------------------------------
def build_post() -> dict:
    personas = list(PERSONA_WEIGHTS.keys())
    weights = list(PERSONA_WEIGHTS.values())
    persona = random.choices(personas, weights=weights, k=1)[0]

    content, tickers = generate_content_mock(persona)

    trigger = random.choice(ENGAGEMENT_TRIGGERS)
    if trigger not in content:
        content += f"\n\n{trigger}"

    if BINANCE_REFERRAL_LINK and random.random() < REFERRAL_CHANCE:
        cta = random.choice(_refersal_link_ctas)
        content += f"\n\n{cta}"

    return {"persona": persona, "content": content, "tickers": tickers}
