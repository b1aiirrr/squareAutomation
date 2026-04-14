from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime

PERSONA_WEIGHTS = {
    "technical_analyst": 0.30,
    "macro_news": 0.20,
    "educator": 0.20,
    "community": 0.30,
}

PERSONA_PROMPTS = {
    "technical_analyst": [
        "Break down BTC support and resistance with RSI context for intraday traders.",
        "Analyze BNB trend structure with key levels and momentum warning signs.",
        "Create a chartless technical summary with bullish and bearish trigger zones.",
    ],
    "macro_news": [
        "Explain current ETF flow implications for short-term crypto sentiment.",
        "Summarize a global macro development and how it might affect risk assets.",
        "Cover one on-chain or exchange trend with implications for market positioning.",
    ],
    "educator": [
        "Teach one BNB Chain concept with a practical use-case for newcomers.",
        "Explain a Real World Asset tokenization idea in simple terms.",
        "Write an educational thread intro on wallet security and DeFi risk basics.",
    ],
    "community": [
        "Write a reflective community post asking followers about their weekly strategy.",
        "Post a mindset-focused message about discipline, risk, and long-term growth.",
        "Create an engagement question to spark comments from beginner and advanced users.",
    ],
}


@dataclass
class ContentPost:
    persona: str
    prompt: str
    body: str


def choose_persona() -> str:
    personas = list(PERSONA_WEIGHTS.keys())
    weights = list(PERSONA_WEIGHTS.values())
    return random.choices(personas, weights=weights, k=1)[0]


def build_post() -> ContentPost:
    persona = choose_persona()
    prompt = random.choice(PERSONA_PROMPTS[persona])
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    body = (
        f"[{persona.replace('_', ' ').title()}] {prompt}\n\n"
        "NFA. Stay risk-aware and DYOR.\n"
        f"Signal timestamp: {timestamp}"
    )
    return ContentPost(persona=persona, prompt=prompt, body=body)
