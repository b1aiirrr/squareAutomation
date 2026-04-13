"""
Sentinel-Square Binance Publisher
==================================
Handles posting content to Binance Square via their Creator API.
Implements retry logic with exponential backoff.
"""

import logging
import asyncio

import httpx

from config import BINANCE_SQUARE_API_KEY, BINANCE_POST_URL

logger = logging.getLogger("sentinel.publisher")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 2.0


# ---------------------------------------------------------------------------
# Publish Post
# ---------------------------------------------------------------------------
async def publish_post(content: str) -> dict:
    """
    Publish a text post to Binance Square.

    Args:
        content: Plain text content (may include hashtags).

    Returns:
        {
            "success": True/False,
            "post_id": "...",
            "post_url": "https://www.binance.com/square/post/...",
            "error": None or "error message"
        }
    """
    headers = {
        "Content-Type": "application/json",
        "X-Square-OpenAPI-Key": BINANCE_SQUARE_API_KEY,
        "clienttype": "binanceSkill",
    }

    payload = {"bodyTextOnly": content}

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    BINANCE_POST_URL,
                    headers=headers,
                    json=payload,
                )

                data = response.json()

                # Binance returns {"code": "000000", "data": {"id": "..."}} on success
                if response.status_code == 200 and data.get("code") == "000000":
                    post_id = data.get("data", {}).get("id", "unknown")
                    post_url = f"https://www.binance.com/square/post/{post_id}"

                    logger.info(f"Published successfully → {post_url}")
                    return {
                        "success": True,
                        "post_id": str(post_id),
                        "post_url": post_url,
                        "error": None,
                    }
                else:
                    error_msg = data.get("message", f"HTTP {response.status_code}")
                    logger.warning(
                        f"Binance API error (attempt {attempt}/{MAX_RETRIES}): {error_msg}"
                    )
                    last_error = error_msg

        except httpx.TimeoutException:
            last_error = "Request timed out"
            logger.warning(f"Timeout (attempt {attempt}/{MAX_RETRIES})")

        except Exception as e:
            last_error = str(e)
            logger.warning(f"Request failed (attempt {attempt}/{MAX_RETRIES}): {e}")

        # Exponential backoff before retry
        if attempt < MAX_RETRIES:
            wait = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
            logger.info(f"Retrying in {wait:.1f}s...")
            await asyncio.sleep(wait)

    logger.error(f"All {MAX_RETRIES} attempts failed: {last_error}")
    return {
        "success": False,
        "post_id": None,
        "post_url": None,
        "error": last_error,
    }
