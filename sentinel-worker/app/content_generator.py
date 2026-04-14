"""
Sentinel-Square ULTRA Content Generator v6
=========================================
High-Conviction Degenerate Analyst Persona
MAXIMIZES Write-to-Earn Rewards
"""

import random
import re

# ============================================================================
# HIGH-CONVICTION DEGENERATE ANALYST PERSONA
# ============================================================================
# This persona is BOLD, CONTROVERSIAL, and MAXIMUM ENGAGEMENT
# Converts 1% of viewers into followers
# Feels like being part of a "Private Alpha" group
# ============================================================================

CONTENT_TEMPLATES = {
    "technical": [
        {
            "hook": "Is $BTC setting a trap for the bears? 📉💀",
            "body": "The 4H chart is screaming reversal.\nIf we hold this level, the shorts get squeezed.\nBloodbath incoming for bears.\n\n📊 Chart Summary:\n• RSI: Oversold\n• Support: ${}\n• Resistance: ${}\n• Volume: 🚀 Surge\n\nSmart money is accumulating here.",
            "tags": ["BTC", "CryptoTrading", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "Why I'm not selling my $BNB even at ${} 💎🙌",
            "body": "Everyone panic-selling.\nNot me.\n\nThe smart money knows:\nBNB at this level = generational buying opportunity.\n\n📊 Chart Summary:\n• RSI: Oversold\n• Key Support: ${}\n• Target: ${} 🚀\n• Pattern: Bull flag forming\n\nDiamond hands only. 🔒",
            "tags": ["BNB", "CryptoTrading", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "The $ETH chart is speaking. Are you listening? 👀",
            "body": "Massive liquidation hunt detected.\nInstitutional buyers stepping in at support.\n\n📊 Chart Summary:\n• EMA: Golden cross incoming\n• MACD: Bullish divergence\n• Volume: 📈 Expanding\n• Pattern: Inverse head & shoulders\n\nThis is NOT financial advice.\nBut I'd be buying here. 🚀",
            "tags": ["ETH", "CryptoTrading", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "Bloodbath in $SOL. Here's my play 💰",
            "body": "Retail running for the exits.\nSmart money accumulation zone.\n\n📊 Chart Summary:\n• Support: ${} holding\n• RSI: Deeply oversold\n• Target: ${}\n• Risk/Reward: 🔥 Insane\n\nWho else is loading up? 🙋",
            "tags": ["SOL", "CryptoTrading", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "$BTC: The Liquidation Hunt is ON 🎯",
            "body": "Positions getting liquidated left and right.\nMarket makers hunting stops.\n\n📊 Chart Summary:\n• Sweep complete at ${}\n• Wicks showing exhaustion\n• Reversal indicators: ALL GREEN ✅\n\nShorts trapped.\nBulls loading. 🚀",
            "tags": ["BTC", "CryptoTrading", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
    ],
    "news": [
        {
            "hook": "The narrative is SHIFTING. Here's what nobody is talking about 📢",
            "body": "BlackRock buying the dip.\nETF inflows never stopped.\nDXY weakening.\n\nMacro is aligning for crypto.\n\n📊 What's Moving:\n• Fed: Dovish 🕊️\n• DXY: 📉 Dropping\n• Risk assets: 🚀 Rippling\n\nYou feel it too, right?",
            "tags": ["CryptoNews", "Macro", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "SEC just confirmed something BIG 🧐",
            "body": "The regulatory clarity is coming.\nInstitutional money knows.\n\n📊 Key Signals:\n• ETF approvals: Accelerating\n• Legal clarity: Building\n• Smart money: Positioning\n\nThis is the quiet before the 🚀",
            "tags": ["CryptoNews", "Regulation", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "Binance just made a POWER MOVE. Here's why it matters 👀",
            "body": "The burn announcement.\nThe ecosystem upgrades.\nThe competition falling behind.\n\n📊 Binance Ecosystem:\n• BNB: Undervalued rn\n• New listings: Coming\n• Volume: 📈 Picking up\n\nThe smart money knows.",
            "tags": ["BNB", "CryptoNews", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "The dollar is WEAKENING. Bitcoin knows what's coming 💡",
            "body": "DXY dropping.\nGlobal liquidity expanding.\nHistorical pattern: Bullish.\n\n📊 Macro Setup:\n• DXY: 📉 Breakdown\n• BTC correlation: Inverting\n• Risk assets: Next 🚀\n\nYour move, friend.",
            "tags": ["Macro", "BTC", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "ETF inflows just hit $1.2B. The signal is CLEAR 📊",
            "body": "Institutional money speaking.\nRetail too scared to act.\n\n📊 The Data:\n• ETF flows: 🟢 Bullish\n• Smart money: Accumulating\n• Retail: Panicking\n\nWho's buying here? 💎🙌",
            "tags": ["ETF", "CryptoNews", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
    ],
    "educator": [
        {
            "hook": "Stop doing this with your $BTC. It's costing you a FORTUNE 💸",
            "body": "Retail mistakes I see daily:\n❌ Panic selling bottoms\n❌ Taking profit too early\n❌ Ignoring the macro\n\n📊 The 2% Rule:\nRisk 2% max per trade.\nLet winners run.\nCut losers fast.\n\nThis is how smart money operates. 🔐",
            "tags": ["TradingTips", "CryptoEducation", "MOMIGIAlpha"],
            "sentiment": "neutral",
        },
        {
            "hook": "The $BNB ecosystem explained in 60 seconds 🧠",
            "body": "BNB Chain ecosystem:\n🟡 BNB: Utility token\n🟡 BEP20: Fast/cheap txns\n🟡 DeFi: Growing fast\n🟡 NFTs: Active market\n\n📊 Why it matters:\n• Low fees = adoption\n• Fast = UX\n• Growing = 🚀\n\nNot financial advice. Just facts. 📊",
            "tags": ["BNB", "CryptoEducation", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "Why RWA tokenization will 100x your portfolio 🪙",
            "body": "Real World Assets.\nOn-chain.\nRevolutionary.\n\n📊 The Opportunity:\n• Traditional finance: $600T+\n• On-chain: Growing fast\n• BNB Chain: Leading the way\n\nEarly = Rich. 🚀",
            "tags": ["RWA", "CryptoEducation", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "Stop overtrading. Start making money. Here's how 💰",
            "body": "The hardest lesson:\nQuality > Quantity.\n\n📊 My Rules:\n1. Wait for setups\n2. Cut losses fast\n3. Let winners run\n4. Respect the trend\n\nDiscipline = Profits. 📈",
            "tags": ["TradingTips", "CryptoEducation", "MOMIGIAlpha"],
            "sentiment": "neutral",
        },
        {
            "hook": "What's the difference between HODLing and being a bagholder? 🤔",
            "body": "HODLing: Active belief in thesis.\nBagholding: Hoping without reason.\n\n📊 Know the difference:\n• Good project + bad entry = HODL\n• Bad project = bagholder\n• No thesis = gambling\n\nKnow WHAT you own. 💎",
            "tags": ["TradingTips", "CryptoEducation", "MOMIGIAlpha"],
            "sentiment": "neutral",
        },
    ],
    "community": [
        {
            "hook": "Hot take: Most of you will NOT make it in crypto 🔥",
            "body": "Not trying to be mean.\nJust honest.\n\n📊 Why traders fail:\n• No risk management\n• Emotional decisions\n• Over-leveraging\n• Chasing pumps\n\nSound familiar? 💀\n\nThe survivors do THIS instead:\n1. Study charts\n2. Manage risk\n3. Stay disciplined\n\nAre you in the 5%? 👇",
            "tags": ["TradingPsychology", "CryptoCommunity", "MOMIGIAlpha"],
            "sentiment": "neutral",
        },
        {
            "hook": "Just turned $500 into $3,200. Here's my playbook 📖",
            "body": "No leverage.\nNo luck.\nJust discipline.\n\n📊 My Strategy:\n• 1% risk per trade\n• Wait for setups\n• 3+ indicators agree\n• Let winners run\n\nSimple. Not easy.\n\nWhat's your win rate? 👇",
            "tags": ["TradingResults", "CryptoCommunity", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "The bear market is the BEST time to accumulate 🧠",
            "body": "Everyone running.\nSmart money buying.\n\n📊 The playbook:\n• DCA weekly\n• Don't check charts daily\n• Accumulate the leaders\n• Wait for the narrative\n\nThis is how fortunes are made. 💎🙌\n\nWhen did you start accumulating? 👇",
            "tags": ["HODL", "CryptoCommunity", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "Day 47 of loading up. Still not selling 💎🙌",
            "body": "The chart doesn't lie.\nThe smart money knows.\n\n📊 Why I keep buying:\n• Long-term thesis intact\n• Support holding\n• Institutions accumulating\n• Narrative still early\n\nTrust the process. 📈\n\nAre you still buying? 👇",
            "tags": ["HODL", "CryptoCommunity", "MOMIGIAlpha"],
            "sentiment": "bullish",
        },
        {
            "hook": "The single biggest mistake new traders make 🐍",
            "body": "Chasing winners.\nAlways chasing winners.\n\n📊 The truth:\n• FOMO in = bags\n• Patience = profits\n• First in = wins\n\nSmart money buys when others fear. 💎\n\nDrop a 🔥 if you learned this the hard way 👇",
            "tags": ["TradingPsychology", "CryptoCommunity", "MOMIGIAlpha"],
            "sentiment": "neutral",
        },
    ],
}

# ============================================================================
# ENGAGEMENT TRIGGERS (Comment Bait - CRITICAL for Write-to-Earn)
# ============================================================================
COMMENT_BAITS = [
    "Are you long or short here? Drop a 👇 or 👆 below.",
    "Retweet if you're bullish! 🔥",
    "Tag someone who needs to see this! 👥",
    "Drop a 💎 if you're accumulating!",
    "Comment your $BTC target below! 💬",
    "Who's still holding? 🙋",
    "Bullish or bearish? 👀",
    "Agree or am I missing something? Let me know 👇",
    "Drop a 🚀 if you made it this far!",
    "Which $ALT are you watching? 👇",
]

# ============================================================================
# DASHBOARD LINK (Thumbnail Logic - Makes you look professional)
# ============================================================================
DASHBOARD_LINK = "\n\n📊 Live Dashboard: squareautomation.vercel.app"

# ============================================================================
# REFERRAL CTAS
# ============================================================================
REFERRAL_CTAS = [
    "Ready to start your journey? Join me on Binance: {link}",
    "Trading fees eating your profits? Get a discount here: {link}",
    "Maximize your gains with lower fees: {link}",
]

# ============================================================================
# SPECIAL TICKERS
# ============================================================================
SPECIAL_TICKERS = ["BTC", "ETH", "BNB", "SOL", "MATIC", "ADA", "AVAX", "DOT", "LINK", "ARB"]

# ============================================================================
# MOCK PRICES (Would be fetched from API in production)
# ============================================================================
MOCK_PRICES = {
    "BTC": 96450.0,
    "ETH": 3450.0,
    "BNB": 625.0,
    "SOL": 198.0,
    "MATIC": 0.89,
    "ADA": 0.58,
    "AVAX": 38.50,
    "DOT": 7.85,
    "LINK": 18.20,
    "ARB": 1.12,
}


def generate_content_mock(persona: str) -> tuple[str, list[str]]:
    """
    Generate HIGH-CONVICTION content optimized for Write-to-Earn.
    Every post follows the formula:
    1. Pattern Interrupter Hook (3 seconds)
    2. Bold Body with Alpha Insight
    3. Chart Summary (emojis)
    4. Comment Bait (low-effort question)
    5. Strategic Hashtags
    6. Dashboard Link (optional)
    """
    templates = CONTENT_TEMPLATES.get(persona, CONTENT_TEMPLATES["community"])
    template = random.choice(templates)

    # Get tickers from template
    tickers_in_template = re.findall(r"\$[A-Z]{2,10}", template["hook"] + template["body"])
    if not tickers_in_template:
        tickers_in_template = [f"${random.choice(SPECIAL_TICKERS)}"]

    tickers = [t.replace("$", "") for t in tickers_in_template]
    primary_ticker = tickers[0]

    # Format the hook
    hook = template["hook"]

    # Format the body with prices
    body = template["body"]
    for ticker in tickers:
        if ticker in MOCK_PRICES:
            price = MOCK_PRICES[ticker]
            # Replace first occurrence of ${} with actual price
            if "${}" in body:
                if price > 1000:
                    body = body.replace("${}", f"${price:.0f}", 1)
                else:
                    body = body.replace("${}", f"${price:.2f}", 1)
            # Replace second occurrence
            if "${}" in body:
                if price > 1000:
                    body = body.replace("${}", f"${price:.0f}", 1)
                else:
                    body = body.replace("${}", f"${price:.2f}", 1)

    # If still ${} left, replace with target price
    if "${}" in body:
        target_price = MOCK_PRICES.get(ticker, 1000) * 1.1
        if target_price > 1000:
            body = body.replace("${}", f"${target_price:.0f}")
        else:
            body = body.replace("${}", f"${target_price:.2f}")

    # Ensure primary ticker is in hook
    if f"${primary_ticker}" not in hook:
        hook = hook.replace("$", f"${primary_ticker} ", 1)

    # Format hashtags
    tags = " ".join([f"#{t}" for t in template["tags"]])

    # Select comment bait
    comment_bait = random.choice(COMMENT_BAITS)

    # Combine everything
    content = f"{hook}\n\n{body}\n\n{comment_bait}\n\n{tags}{DASHBOARD_LINK}"

    return content, [f"${t}" for t in tickers]


def should_add_referral(referral_link: str, post_history: list) -> bool:
    """Decide if referral CTA should be added (20% chance, no consecutive)"""
    if not referral_link:
        return False

    if post_history:
        last_post = post_history[-1]
        if isinstance(last_post, dict) and "binance.com/referral" in last_post.get("content", "").lower():
            return False

    return random.random() < 0.20


def format_referral_cta(referral_link: str) -> str:
    """Format referral CTA with link"""
    cta = random.choice(REFERRAL_CTAS)
    return cta.format(link=referral_link)
