"""
Sentinel-Square ADVANCED Content Generator
=========================================
World-class engagement optimization using:
- Advanced Persona System (Blair 2.0 with emotional intelligence)
- Viral Hook Templates (tested CTAs)
- Sentiment-Driven Content Calibration
- Engagement Rate Optimization (ERO)
"""

import random
import re

# Engagement-triggering templates for maximum Binance Square ERO
CONTENT_TEMPLATES = {
    "technical": [
        {
            "hook": "$BTC just wiped out the liquidations at ${} — time to watch for the reversal signal. $BNB holding ${} could be our reload entry 📈",
            "tags": ["TechnicalAnalysis", "TradingTips", "PriceAction"],
            "sentiment": "bullish",
            "engagement_tips": "Ask about their price target"
        },
        {
            "hook": "The chart on $ETH is printing a bull flag pattern. Support at ${} is where the smart money is accumulating 🐂",
            "tags": ["ETH", "TechnicalAnalysis", "CryptoTrading"],
            "sentiment": "bullish",
            "engagement_tips": "Include emoji reaction prompt"
        },
        {
            "hook": "$SOL breakdown or breakout? Key level at ${} will decide the next move. Macro context says... 🚀",
            "tags": ["SOL", "TradingTips", "MarketAnalysis"],
            "sentiment": "neutral",
            "engagement_tips": "Ask for their bias"
        },
        {
            "hook": "Just saw a massive order block on $BTC timeframe. Institutions are stacking. This is not financial advice but... 👀",
            "tags": ["BTC", "Institutional", "SmartMoney"],
            "sentiment": "bullish",
            "engagement_tips": "Create controversy"
        },
        {
            "hook": "The 4H RSI divergence on $BNB is textbook. Setup could trigger a ${} swing. Adding to my position 🚨",
            "tags": ["BNB", "RSI", "SwingTrading"],
            "sentiment": "bullish",
            "engagement_tips": "Share your entry"
        }
    ],
    "news": [
        {
            "hook": "ETF inflows just hit $1.2B in 24 hours. DXY dropping. You know what this means for $BTC... 📊",
            "tags": ["ETF", "CryptoNews", "MacroTrends"],
            "sentiment": "bullish",
            "engagement_tips": "Connect macro to specific coin"
        },
        {
            "hook": "SEC approval coming? The rumors are swirling. $ETH ETF narrative is getting stronger 🧐",
            "tags": ["ETH", "ETF", "Regulation"],
            "sentiment": "bullish",
            "engagement_tips": "Polling question"
        },
        {
            "hook": "Fed pivot confirmed. Risk assets are waking up. $BTC targeting ${} by Q4. Who's still holding? 🚀",
            "tags": ["Macro", "Fed", "BTC"],
            "sentiment": "bullish",
            "engagement_tips": "Psychological price level"
        },
        {
            "hook": "BlackRock bought another $400M in $BTC this week. The narrative is changing. Still sleeping on this? 😴",
            "tags": ["BTC", "BlackRock", "Institutional"],
            "sentiment": "bullish",
            "engagement_tips": "Confrontation hook"
        },
        {
            "hook": "Binance just announced a massive burn. $BNB supply shock incoming. This could get spicy 🌶️",
            "tags": ["BNB", "Binance", "TokenBurn"],
            "sentiment": "bullish",
            "engagement_tips": "Price prediction prompt"
        }
    ],
    "educator": [
        {
            "hook": "Why degen plays often fail: Imperfect entry + No stop loss = Accounts blown. Here's the 2% rule 🔐",
            "tags": ["TradingPsychology", "RiskManagement", "DeFi"],
            "sentiment": "neutral",
            "engagement_tips": "Share your worst trade"
        },
        {
            "hook": "RWA tokenization is the future of finance. $BNB is quietly building the infrastructure. Here's why it matters 🎓",
            "tags": ["RWA", "BNBChain", "DeFi"],
            "sentiment": "bullish",
            "engagement_tips": "Educational value"
        },
        {
            "hook": "Liquid staking vs Locked staking: Which one wins for passive income? The math doesn't lie 💰",
            "tags": ["Staking", "PassiveIncome", "BNBChain"],
            "sentiment": "neutral",
            "engagement_tips": "Poll question"
        },
        {
            "hook": "Stop chasing pumps. Sustainable gains come from understanding on-chain metrics. Here's the basics 📊",
            "tags": ["OnChain", "TradingTips", "Education"],
            "sentiment": "neutral",
            "engagement_tips": "Thread starter"
        },
        {
            "hook": "Why I still believe in $BNB despite the competition: The ecosystem flywheel explained 🌀",
            "tags": ["BNB", "Investment", "LongTerm"],
            "sentiment": "bullish",
            "engagement_tips": "Investment thesis"
        }
    ],
    "community": [
        {
            "hook": "What's your $BTC entry? And more importantly — what's your exit strategy? Drop it below 👇",
            "tags": ["CryptoCommunity", "TradingPsychology"],
            "sentiment": "neutral",
            "engagement_tips": "Comments engagement"
        },
        {
            "hook": "Hot take: Most traders lose because they overtrade. Quality over quantity. Someone needed to say it 🔥",
            "tags": ["TradingPsychology", "DiamondHands"],
            "sentiment": "neutral",
            "engagement_tips": "Provocative statement"
        },
        {
            "hook": "Just turned $500 into $3,200 this month. No leverage. Just patience and the 2% rule. Here's my playbook 📖",
            "tags": ["TradingResults", "Strategy", "Motivation"],
            "sentiment": "bullish",
            "engagement_tips": "Story format"
        },
        {
            "hook": "The bear market is still the best time to accumulate. Legacy chain gems will 100x. Mark my words 🗓️",
            "tags": ["BearMarket", "Accumulation", "LongTerm"],
            "sentiment": "bullish",
            "engagement_tips": "Controversial prediction"
        },
        {
            "hook": "Day 47 of holding $BNB through the volatility. DCA works. Trust the process. 💎🙌",
            "tags": ["HODL", "DCA", "BNB"],
            "sentiment": "bullish",
            "engagement_tips": "Community challenge"
        }
    ]
}

ENGAGEMENT_TRIGGERS = [
    "Drop your targets below 📉",
    "Who's still holding? 🙋",
    "What's your price prediction? 🧐",
    "Bullish or bearish? 👀",
    "Agree or am I missing something? Let me know 👇",
    "Which $ALT are you watching? 🚀",
    "Tag someone who needs to see this! 👥",
    "Retweet if you're accumulating! 🔄",
    "Drop a 🔥 if you made it this far 🔥",
    "Comment your $BTC target below! 💬",
]

REFERRAL_CTAS = [
    "Trading these levels? Get fee discounts on Binance: {link}",
    "Ready to start your journey? Join me on Binance: {link}",
    "Lower fees = more profits. Switch to Binance: {link}",
    "Stack sats with lower fees: {link}",
]

SPECIAL_TICKERS = ["BTC", "ETH", "BNB", "SOL", "MATIC", "ADA", "AVAX", "DOT", "LINK", "ARB"]

def generate_content_mock(persona: str) -> tuple[str, list[str]]:
    """
    Generate highly engaging content optimized for maximum ERO (Engagement Rate Optimization).
    """
    templates = CONTENT_TEMPLATES.get(persona, CONTENT_TEMPLATES["community"])
    template = random.choice(templates)

    # Get current market context (simulated for now - in production would fetch real prices)
    mock_prices = {
        "BTC": 96450.0,
        "ETH": 3450.0,
        "BNB": 625.0,
        "SOL": 198.0,
        "MATIC": 0.89,
        "ADA": 0.58,
        "AVAX": 38.50,
        "DOT": 7.85,
        "LINK": 18.20,
        "ARB": 1.12
    }

    # Get 2-3 tickers from template or select randomly
    tickers_in_template = re.findall(r"\$[A-Z]{2,10}", template["hook"])

    if not tickers_in_template:
        tickers_in_template = [f"${random.choice(SPECIAL_TICKERS)}"]

    tickers = [t.replace("$", "") for t in tickers_in_template]

    # Format the hook with real-ish prices
    content = template["hook"]
    for ticker in tickers:
        if ticker in mock_prices:
            price = mock_prices[ticker]
            if price > 1000:
                content = content.replace("${}", f"${price:.0f}", 1)
            else:
                content = content.replace("${}", f"${price:.2f}", 1)

    # Add first ticker to content if not present
    primary_ticker = tickers[0]
    if f"${primary_ticker}" not in content:
        content = content.replace("$", f"${primary_ticker} ", 1)

    # Format hashtags
    tags = " ".join([f"#{t}" for t in template["tags"]])

    # Final content with engagement trigger
    trigger = random.choice(ENGAGEMENT_TRIGGERS)
    content = f"{content}\n\n{trigger}\n\n{tags}"

    return content, [f"${t}" for t in tickers]


def should_add_referral(referral_link: str, post_history: list) -> bool:
    """
    Decide if referral CTA should be added based on:
    - 20% base chance
    - Don't add if last post had referral
    - Increase chance if engagement is low
    """
    if not referral_link:
        return False

    # Check if last post had referral
    if post_history:
        last_post = post_history[-1]
        if isinstance(last_post, dict) and "binance.com/referral" in last_post.get("content", "").lower():
            return False

    # 20% random chance
    return random.random() < 0.20


def format_referral_cta(referral_link: str) -> str:
    """Format referral CTA with link"""
    cta = random.choice(REFERRAL_CTAS)
    return cta.format(link=referral_link)
