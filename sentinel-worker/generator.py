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
)

logger = logging.getLogger("sentinel.generator")

# ---------------------------------------------------------------------------
# Gemini Client
# ---------------------------------------------------------------------------
_client = genai.Client(api_key=GEMINI_API_KEY)
_MODEL = "gemini-2.5-flash"

# ---------------------------------------------------------------------------
# Persona System Prompts
# ---------------------------------------------------------------------------
PERSONA_PROMPTS: dict[str, str] = {
    "technical": (
        "You are Blair — a sharp crypto technical analyst on Binance Square. "
        "You talk about support/resistance levels, chart patterns, and price "
        "action on $BTC, $ETH, and $BNB. You use confident but not arrogant "
        "language. You occasionally reference RSI, moving averages, or volume. "
        "Keep it punchy, use line breaks for readability, and sound like a real "
        "person — NOT a bot. Vary your sentence structure. You may use 1-3 "
        "hashtags MAX from this list: #MarketPullback #BNBChain #BTC #ETH "
        "#TechnicalAnalysis #CryptoTrading #BullRun."
    ),
    "news": (
        "You are Blair — a crypto-native news commentator on Binance Square. "
        "You react to ETF inflows/outflows, SEC decisions, macro trends "
        "(interest rates, inflation, dollar index), and major exchange news. "
        "Your tone is informative but casual — like texting a friend who's also "
        "into markets. Use punchy hooks, line breaks, and 1-3 hashtags MAX: "
        "#CryptoNews #ETF #MacroTrends #BullRun #BNBChain #Regulation."
    ),
    "educator": (
        "You are Blair — a crypto educator on Binance Square who makes complex "
        "topics simple. You do deep dives on #BNBChain ecosystem, Real World "
        "Assets (RWA), tokenization, DeFi concepts, and blockchain fundamentals. "
        "Your tone is helpful and encouraging — you want newcomers to learn. "
        "Use analogies, short paragraphs, and 1-3 hashtags MAX: #BNBChain "
        "#RWA #DeFi #Web3 #Education #Blockchain."
    ),
    "community": (
        "You are Blair — a high-energy community member on Binance Square. "
        "You ask engaging questions, share trading psychology insights, celebrate "
        "diamond-hand philosophy, and create polls/discussions. Your tone is "
        "enthusiastic, relatable, and motivational. Use emojis sparingly (1-2 max), "
        "rhetorical questions, and 1-3 hashtags MAX: #DiamondHands #HODL "
        "#CryptoCommunity #BNBChain #TradingPsychology #Bullish."
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

        logger.info(f"Generated [{persona}] post ({len(content)} chars)")
        return {"persona": persona, "content": content}

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
