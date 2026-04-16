"""
Sentinel-Square PIXEL Campaign Engine
=====================================
Automates the daily tasks for the PIXEL Binance Square Campaign:
1. Trade PIXEL ($11+ volume)
2. Create short post (>= 100 chars)
3. Create article/long post (>= 500 chars)
"""

import asyncio
import random
import logging
import httpx
from datetime import datetime

from config import BINANCE_SQUARE_API_KEY, FRIEND_SQUARE_API_KEY
from .engine import publish_to_square
from .content_generator import model

logger = logging.getLogger("sentinel.campaign")

async def generate_pixel_content(min_length: int) -> str:
    """Generate high-conviction content specifically for the PIXEL campaign."""
    if not model:
        # Fallback if Gemini is not configured, though unlikely
        base = "The $PIXEL ecosystem is showing massive strength. @Pixels #pixel "
        dummy_text = "Smart money is accumulating here. " * (min_length // 30 + 1)
        return (base + dummy_text)[:max(min_length + 20, len(base) + 20)]

    prompt = f"""
    You are 'MOMIGI', a High-Conviction Analyst on Binance Square.
    Write a highly engaging post about the token $PIXEL and the @Pixels game/ecosystem.
    REQUIREMENTS:
    - Must be strictly MORE than {min_length} characters.
    - Must include exact tags: $PIXEL, @Pixels, and #pixel.
    - Discuss its Stacked ecosystem, recent updates, or why it's a good accumulation zone.
    - End with a question to drive comments.
    - DO NOT include placeholders. Make it authentic.
    """
    
    try:
        response = await model.generate_content_async(prompt)
        text = response.text.strip()
        
        # Ensure mandatory campaign tags
        for tag in ["$PIXEL", "@Pixels", "#pixel"]:
            if tag.lower() not in text.lower():
                text = f"{text}\n{tag}"
                
        # Ensure length requirements
        if len(text) < min_length:
            padding = "\n\n" + "If you haven't looked into the @Pixels ecosystem yet, you are missing out on the future of Web3 gaming. $PIXEL is leading the charge! #pixel" * 3
            text += padding

        return text
    except Exception as e:
        logger.error(f"Failed to generate PIXEL content: {e}")
        return ""

async def execute_pixel_trade(state, client) -> bool:
    """Execute a market buy for $11 of PIXEL to satisfy the trading task."""
    try:
        if not client:
            await state.add_log("warning", "PIXEL Campaign: Trading client not initialized.")
            return False

        symbol = "PIXELUSDT"
        
        # Check USDT balance
        balance = client.get_asset_balance(asset="USDT")
        usdt_balance = float(balance["free"])
        
        if usdt_balance < 11.5:
            await state.add_log("warning", "PIXEL Campaign: Insufficient USDT to execute $11 PIXEL trade.")
            return False

        # Get current PIXEL price
        avg_price_data = client.get_avg_price(symbol=symbol)
        current_price = float(avg_price_data["price"])
        
        # We need slightly more than $10 to ensure fees don't drop it below requirement. Using $11.
        quantity = round(11.0 / current_price, 2) # Adjusted precision, usually 1 or 2 decimals for altcoins
        
        # If amount is too precise, Binance throws LOT_SIZE error. We'll round to whole numbers for PIXEL to be safe.
        quantity = int(quantity) + 1  # Buy next whole integer amount
        
        actual_cost = quantity * current_price
        
        order = client.order_market_buy(symbol=symbol, quantity=quantity)
        
        await state.add_log("info", f"✅ PIXEL Campaign: Executed trade | Bought {quantity} PIXEL (~${actual_cost:.2f})")
        return True
    except Exception as e:
        logger.error(f"PIXEL Campaign trade error: {e}")
        if state:
            await state.add_log("error", f"PIXEL Campaign Trade failed: {e}")
        return False

async def execute_pixel_post(state, is_long: bool):
    """Execute the PIXEL text task (Short post or Long article)."""
    min_length = 550 if is_long else 150
    post_type = "Article" if is_long else "Short Post"
    
    await state.add_log("info", f"⏳ PIXEL Campaign: Generating {post_type} (> {min_length} chars)...")
    
    content = await generate_pixel_content(min_length)
    if not content:
        await state.add_log("error", f"PIXEL Campaign {post_type} generating failed.")
        return
        
    await state.add_log("info", f"✅ PIXEL Content generated (Length: {len(content)} chars)")
    
    # Primary Publish
    if BINANCE_SQUARE_API_KEY:
        res = await publish_to_square(content, BINANCE_SQUARE_API_KEY)
        if res["success"]:
            await state.add_log("info", f"🟢 PIXEL Campaign {post_type} Published (Primary)!")
        else:
            await state.add_log("error", f"❌ Primary PIXEL {post_type} failed: {res.get('error')}")
            
    # Friend Publish
    if FRIEND_SQUARE_API_KEY:
        # Small delay between cross-posting to avoid hitting API limits simultaneously
        await asyncio.sleep(5)
        friend_res = await publish_to_square(content, FRIEND_SQUARE_API_KEY)
        if friend_res["success"]:
            await state.add_log("info", f"🟢 PIXEL Campaign {post_type} Published (Friend)!")
        else:
            await state.add_log("error", f"❌ Friend PIXEL {post_type} failed: {friend_res.get('error')}")

async def run_pixel_campaign(state, client):
    """Orchestrates the 3 campaign tasks with random timer delays."""
    await state.add_log("info", "🚀 Starting Daily PIXEL Campaign routine...")
    
    # Task 1: Trade PIXEL
    await execute_pixel_trade(state, client)
    
    # Random delay 15-30 minutes between actions
    delay1 = random.randint(15, 30)
    await state.add_log("info", f"⏳ PIXEL Campaign: Waiting {delay1} minutes before Short Post...")
    await asyncio.sleep(delay1 * 60)
    
    # Task 2: Short Post
    await execute_pixel_post(state, is_long=False)
    
    # Random delay 15-30 minutes
    delay2 = random.randint(15, 30)
    await state.add_log("info", f"⏳ PIXEL Campaign: Waiting {delay2} minutes before Article Post...")
    await asyncio.sleep(delay2 * 60)
    
    # Task 3: Article (Long Form)
    await execute_pixel_post(state, is_long=True)
    
    await state.add_log("info", "🎯 Daily PIXEL Campaign routine completed!")
