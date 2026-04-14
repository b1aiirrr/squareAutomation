"""
Sentinel-Square Content Generator
==================================
Fetches live market context from CoinGecko, selects a persona via weighted
random choice, and generates human-like Binance Square posts using Google
Gemini 2.5 Flash.
"""

import random
import logging
from datetime import datetime, timezone

import httpx
from google import genai

from config import (
    GEMINI_API_KEY,
    PERSONA_WEIGHTS,
    COINGECKO_TRENDING_URL,
    COINGECKO_PRICE_URL,
    BINANCE_REFERRAL_LINK,
    REFERRAL_CHANCE,
    ENGAGEMENT_TRIGGERS,
)

logger = logging.getLogger("sentinel.generator")

# ---------------------------------------------------------------------------
# Gemini Client
# ---------------------------------------------------------------------------
_client = genai.Client(api_key=GEMINI_API_KEY)
_MODEL = "gemini-2.5-flash"

# ---------------------------------------------------------------------------
# Persona System Prompts (The "Lively" Overhaul - Extensively Refined)
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

PERSONA_PROMPTS: dict[str, str] = {
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
        "Break down complex DeFi concepts into 3-4 punchy insights that a dev would respect. "
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


# ---------------------------------------------------------------------------
# Market Context Fetcher
# ---------------------------------------------------------------------------
async def fetch_market_context() -> dict:
    """
    Pull trending coins and BTC/ETH/BNB prices from CoinGecko.
    Returns a context dict for the LLM prompt. Fails gracefully.
    """
    context = {
        "trending_coins": [],
        "prices": {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Trending coins
        try:
            resp = await client.get(COINGECKO_TRENDING_URL)
            if resp.status_code == 200:
                data = resp.json()
                coins = data.get("coins", [])[:7]
                context["trending_coins"] = [
                    {
                        "name": c["item"]["name"],
                        "symbol": c["item"]["symbol"],
                        "market_cap_rank": c["item"].get("market_cap_rank"),
                    }
                    for c in coins
                ]
        except Exception as e:
            logger.warning(f"CoinGecko trending fetch failed: {e}")

        # BTC, ETH, BNB prices
        try:
            resp = await client.get(
                COINGECKO_PRICE_URL,
                params={
                    "ids": "bitcoin,ethereum,binancecoin",
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                for coin_id, label in [
                    ("bitcoin", "BTC"),
                    ("ethereum", "ETH"),
                    ("binancecoin", "BNB"),
                ]:
                    if coin_id in data:
                        context["prices"][label] = {
                            "usd": data[coin_id].get("usd"),
                            "change_24h": data[coin_id].get("usd_24h_change"),
                        }
        except Exception as e:
            logger.warning(f"CoinGecko price fetch failed: {e}")

    return context


# ---------------------------------------------------------------------------
# Persona Selection
# ---------------------------------------------------------------------------
def select_persona() -> str:
    """Weighted random selection from the 4 personas."""
    personas = list(PERSONA_WEIGHTS.keys())
    weights = list(PERSONA_WEIGHTS.values())
    return random.choices(personas, weights=weights, k=1)[0]


# ---------------------------------------------------------------------------
# Post Generation
# ---------------------------------------------------------------------------
async def generate_post(persona: str | None = None) -> dict:
    """
    Generate a single Binance Square post.
    Returns: {"persona": str, "content": str}
    """
    if persona is None:
        persona = select_persona()

    # Fetch live market context
    context = await fetch_market_context()

    # Build the user prompt with live data
    context_block = _build_context_block(context)

    user_prompt = (
        f"Write a single Binance Square post right now.\n\n"
        f"LIVE MARKET CONTEXT:\n{context_block}\n\n"
        f"RULES:\n"
        f"- One post only, ready to publish as-is\n"
        f"- Start with a punchy hook (question, bold statement, or hot take)\n"
        f"- Use line breaks between ideas for readability\n"
        f"- Maximum 3 hashtags, placed naturally\n"
        f"- Sound like a REAL person, not a bot\n"
        f"- Vary your writing style — sometimes short and punchy, sometimes a bit longer\n"
        f"- No markdown formatting (no **, no ##, no bullet points)\n"
        f"- Keep it under 280 words\n"
        f"- Do NOT start with 'Hey everyone' or 'Good morning' every time\n"
        f"- Occasionally use a casual tone, slang, or slight imperfection\n"
    )

    try:
        response = _client.models.generate_content(
            model=_MODEL,
            contents=user_prompt,
            config={
                "system_instruction": PERSONA_PROMPTS[persona],
                "temperature": 0.9,
                "top_p": 0.95,
                "max_output_tokens": 600,
            },
        )
        content = response.text.strip()

        # Clean up any accidental markdown the model might add
        content = content.replace("**", "").replace("##", "").replace("* ", "")

        # 1. Add Engagement Trigger (Write to Earn)
        trigger = random.choice(ENGAGEMENT_TRIGGERS)
        if trigger not in content:
            content += f"\n\n{trigger}"

        # 2. Referral Integration (Subtle CTA)
        if BINANCE_REFERRAL_LINK and random.random() < REFERRAL_CHANCE:
            ctas = [
                f"Trading these levels on Binance? Get a fee discount here: {BINANCE_REFERRAL_LINK}",
                f"Maximize your gains with lower fees. Join me on Binance: {BINANCE_REFERRAL_LINK}",
                f"Still paying full fees? Use my link for a discount on Binance: {BINANCE_REFERRAL_LINK}",
            ]
            content += f"\n\n{random.choice(ctas)}"

        logger.info(f"Generated [{persona}] post ({len(content)} chars)")
        
        # Extract tickers for the trading engine ($BNB, $BTC, etc.)
        import re
        tickers = list(set(re.findall(r"\$[A-Z]{2,10}", content.upper())))
        
        return {"persona": persona, "content": content, "tickers": tickers}

    except Exception as e:
        logger.error(f"Gemini generation failed: {e}")
        raise


def _build_context_block(context: dict) -> str:
    """Format market context into a readable block for the LLM."""
    lines = []

    # Prices
    for symbol, data in context.get("prices", {}).items():
        price = data.get("usd", "N/A")
        change = data.get("change_24h")
        change_str = f" ({change:+.1f}%)" if change is not None else ""
        lines.append(f"${symbol}: ${price:,.2f}{change_str}" if isinstance(price, (int, float)) else f"${symbol}: {price}")

    # Trending
    trending = context.get("trending_coins", [])
    if trending:
        names = ", ".join(f"{c['symbol']}" for c in trending[:5])
        lines.append(f"Trending: {names}")

    lines.append(f"Time: {context.get('timestamp', 'unknown')}")

    return "\n".join(lines) if lines else "No live data available — use general market knowledge."
