"""
Sentinel-Square Configuration Loader
=====================================
Loads and validates all environment variables from .env file.
Provides typed constants used across the entire worker.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env from the sentinel-worker directory
# ---------------------------------------------------------------------------
_env_path = Path(__file__).parent / ".env"
load_dotenv(_env_path)


def _require(key: str) -> str:
    """Return an env var or exit with a clear error message."""
    value = os.getenv(key)
    if not value or value.startswith("your_"):
        print(f"[FATAL] Missing required environment variable: {key}")
        print(f"        Please set it in {_env_path}")
        sys.exit(1)
    return value


# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
BINANCE_SQUARE_API_KEY: str = _require("BINANCE_SQUARE_API_KEY")
GEMINI_API_KEY: str = _require("GEMINI_API_KEY")
BINANCE_REFERRAL_LINK: str = os.getenv("BINANCE_REFERRAL_LINK", "")

# Trading & Multi-Account
TRADING_API_KEY: str = os.getenv("TRADING_API_KEY", "")
TRADING_API_SECRET: str = os.getenv("TRADING_API_SECRET", "")
FRIEND_SQUARE_API_KEY: str = os.getenv("FRIEND_SQUARE_API_KEY", "")

# ---------------------------------------------------------------------------
# Trading Settings
# ---------------------------------------------------------------------------
TRADE_PERCENT_OF_WALLET: float = 0.01  # 1%
STOP_LOSS_PCT: float = 0.02           # -2%
TAKE_PROFIT_PCT: float = 0.05         # +5%

# ---------------------------------------------------------------------------
# Monetization & Engagement
# ---------------------------------------------------------------------------
REFERRAL_CHANCE: float = 0.20  # 1 in 5 posts
ENGAGEMENT_TRIGGERS: list[str] = [
    "Drop your targets below 📉.",
    "Is $BNB ready for the breakout or are we heading back to support?",
    "What's your $BTC target for EOY?",
    "Agree or am I missing something? Let me know in the comments.",
    "Which $ALT are you watching this week?",
]

# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------
TIMEZONE: str = os.getenv("TIMEZONE", "Africa/Nairobi")
SLEEP_START_HOUR: int = int(os.getenv("SLEEP_START_HOUR", "2"))
SLEEP_END_HOUR: int = int(os.getenv("SLEEP_END_HOUR", "7"))
MIN_INTERVAL_MINUTES: int = 15
MAX_INTERVAL_MINUTES: int = 30
DAILY_POST_TARGET: int = 60

# ---------------------------------------------------------------------------
# Binance Square API
# ---------------------------------------------------------------------------
BINANCE_POST_URL: str = (
    "https://www.binance.com/bapi/composite/v1/public/pgc/openApi/content/add"
)

# ---------------------------------------------------------------------------
# Persona Distribution (must sum to 1.0)
# ---------------------------------------------------------------------------
PERSONA_WEIGHTS: dict[str, float] = {
    "technical": 0.30,      # Support/Resistance on $BNB, $BTC, $ETH
    "news": 0.20,           # ETF flows, macro trends
    "educator": 0.20,       # Deep dives into #BNBChain, RWA
    "community": 0.30,      # Engagement questions, trading psychology
}

# ---------------------------------------------------------------------------
# API Server
# ---------------------------------------------------------------------------
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8585"))
ALLOWED_ORIGINS: list[str] = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://sentinel-square.vercel.app,https://squareautomation.vercel.app",
).split(",")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
LOG_FILE: Path = Path(__file__).parent / "activity.log"

# ---------------------------------------------------------------------------
# CoinGecko (free, no key required)
# ---------------------------------------------------------------------------
COINGECKO_TRENDING_URL: str = "https://api.coingecko.com/api/v3/search/trending"
COINGECKO_PRICE_URL: str = "https://api.coingecko.com/api/v3/simple/price"
