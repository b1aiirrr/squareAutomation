
import asyncio
import os
import logging
from dotenv import load_dotenv
from app.content_generator import generate_content
from app.engine import publish_to_square, BINANCE_SQUARE_API_KEY, FRIEND_SQUARE_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pixel_campaign")

async def execute_pixel_campaign():
    load_dotenv()
    
    logger.info("🚀 Starting Immediate PIXEL Campaign Post...")
    
    # PIXEL Campaign specific instructions
    campaign_context = [
        {
            "topic": "PIXEL Campaign",
            "requirement": "Mention @Pixels, use $PIXEL tag, and #pixel hashtag. Minimum 100 characters for post, 500 for article logic.",
            "talking_points": "Pixels & its Stacked ecosystem, original content only."
        }
    ]
    
    # Generate high-conviction content using Gemini with PIXEL context
    content, tickers = await generate_content(
        persona="technical", 
        market_data={"PIXEL": 0.55}, # Mock current price if needed
        trending_topics=campaign_context
    )
    
    # Generated Content:
    # Ensure PIXEL tags are present for the campaign
    if "@Pixels" not in content:
        content = f"@Pixels {content}"
    if "$PIXEL" not in content:
        content = f"$PIXEL {content}"
    if "#pixel" not in content:
        content = f"{content} #pixel"
        
    logger.info(f"Generated Content: \n{content[:200]}...")

    # Publish to Primary Account
    if BINANCE_SQUARE_API_KEY:
        primary_result = await publish_to_square(content, BINANCE_SQUARE_API_KEY)
        if primary_result["success"]:
            logger.info(f"✅ PIXEL Post published to Primary: {primary_result['post_url']}")
        else:
            logger.error(f"❌ Primary PIXEL Post failed: {primary_result.get('error')}")
    
    # Publish to Friend Account
    if FRIEND_SQUARE_API_KEY:
        friend_result = await publish_to_square(content, FRIEND_SQUARE_API_KEY)
        if friend_result["success"]:
            logger.info(f"✅ PIXEL Post cross-posted to Friend: {friend_result['post_url']}")
        else:
            logger.error(f"❌ Friend PIXEL Post failed: {friend_result.get('error')}")

if __name__ == "__main__":
    asyncio.run(execute_pixel_campaign())
