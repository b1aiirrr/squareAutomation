"""
Sentinel-Square Core Engine
=============================
Orchestrates the full content cycle: checks sleep window, generates content
via the LLM, publishes to Binance Square, and logs all results.
"""

import json
import logging
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import (
    TIMEZONE,
    SLEEP_START_HOUR,
    SLEEP_END_HOUR,
    DAILY_POST_TARGET,
    LOG_FILE,
)
from generator import generate_post
from publisher import publish_post

logger = logging.getLogger("sentinel.engine")

# ---------------------------------------------------------------------------
# Engine State (in-memory, reset on restart)
# ---------------------------------------------------------------------------
_tz = ZoneInfo(TIMEZONE)

state = {
    "uptime_start": datetime.now(_tz).isoformat(),
    "posts_today": 0,
    "posts_total": 0,
    "last_post": None,
    "next_post_time": None,
    "sleep_window": {
        "start": f"{SLEEP_START_HOUR:02d}:00",
        "end": f"{SLEEP_END_HOUR:02d}:00",
    },
    "is_sleeping": False,
    "engine_status": "initializing",
}


def _now() -> datetime:
    return datetime.now(_tz)


# ---------------------------------------------------------------------------
# Sleep Window
# ---------------------------------------------------------------------------
def recalculate_sleep_window():
    """
    Generate a randomized 5-hour sleep window for today.
    The start can shift ±1 hour from the configured SLEEP_START_HOUR.
    """
    jitter = random.randint(-1, 1)
    start_hour = max(0, min(23, SLEEP_START_HOUR + jitter))
    end_hour = start_hour + 5
    if end_hour >= 24:
        end_hour = end_hour - 24

    state["sleep_window"] = {
        "start": f"{start_hour:02d}:00",
        "end": f"{end_hour:02d}:00",
    }
    logger.info(
        f"Sleep window set: {state['sleep_window']['start']} – "
        f"{state['sleep_window']['end']} {TIMEZONE}"
    )


def is_sleeping() -> bool:
    """Check if the current time falls within the sleep window."""
    now = _now()
    start_hour = int(state["sleep_window"]["start"].split(":")[0])
    end_hour = int(state["sleep_window"]["end"].split(":")[0])

    current_hour = now.hour

    if start_hour < end_hour:
        sleeping = start_hour <= current_hour < end_hour
    else:
        # Wraps past midnight (e.g., 23:00 – 04:00)
        sleeping = current_hour >= start_hour or current_hour < end_hour

    state["is_sleeping"] = sleeping
    return sleeping


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def _log_activity(entry: dict):
    """Append a structured JSON log entry to activity.log."""
    entry["timestamp"] = _now().isoformat()
    line = json.dumps(entry, ensure_ascii=False)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    logger.debug(f"Logged: {entry.get('event', 'unknown')}")


# ---------------------------------------------------------------------------
# Daily Reset
# ---------------------------------------------------------------------------
def daily_reset():
    """Reset daily counters and recalculate sleep window."""
    prev_count = state["posts_today"]
    state["posts_today"] = 0
    recalculate_sleep_window()
    _log_activity({
        "event": "daily_reset",
        "previous_day_posts": prev_count,
        "new_sleep_window": state["sleep_window"],
    })
    logger.info(f"Daily reset complete. Yesterday's posts: {prev_count}")


# ---------------------------------------------------------------------------
# Core Content Cycle
# ---------------------------------------------------------------------------
async def run_cycle() -> dict:
    """
    Execute one content cycle:
    1. Check sleep window
    2. Check daily post limit
    3. Generate content
    4. Publish to Binance Square
    5. Log result

    Returns the result dict for the scheduler.
    """
    state["engine_status"] = "running"

    # --- Sleep check ---
    if is_sleeping():
        logger.info("Currently in sleep window — skipping cycle")
        _log_activity({"event": "skipped", "reason": "sleep_window"})
        return {"status": "skipped", "reason": "sleep_window"}

    # --- Daily limit check ---
    if state["posts_today"] >= DAILY_POST_TARGET:
        logger.info(
            f"Daily target reached ({state['posts_today']}/{DAILY_POST_TARGET}) "
            "— skipping cycle"
        )
        _log_activity({"event": "skipped", "reason": "daily_limit_reached"})
        return {"status": "skipped", "reason": "daily_limit_reached"}

    # --- Generate content ---
    try:
        post_data = await generate_post()
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        _log_activity({
            "event": "generation_failed",
            "error": str(e),
        })
        return {"status": "error", "reason": f"generation_failed: {e}"}

    persona = post_data["persona"]
    content = post_data["content"]

    # --- Publish ---
    result = await publish_post(content)

    # --- Update state ---
    if result["success"]:
        state["posts_today"] += 1
        state["posts_total"] += 1
        state["last_post"] = {
            "time": _now().isoformat(),
            "persona": persona,
            "status": "success",
            "post_id": result["post_id"],
            "post_url": result["post_url"],
            "content_preview": content[:120] + "..." if len(content) > 120 else content,
        }

        _log_activity({
            "event": "published",
            "persona": persona,
            "post_id": result["post_id"],
            "post_url": result["post_url"],
            "content_preview": content[:120],
            "posts_today": state["posts_today"],
        })

        logger.info(
            f"✓ Published [{persona}] — Post #{state['posts_today']} today "
            f"(#{state['posts_total']} total)"
        )
    else:
        state["last_post"] = {
            "time": _now().isoformat(),
            "persona": persona,
            "status": "failed",
            "error": result["error"],
        }

        _log_activity({
            "event": "publish_failed",
            "persona": persona,
            "error": result["error"],
            "content_preview": content[:120],
        })

        logger.error(f"✗ Publish failed [{persona}]: {result['error']}")

    return {
        "status": "success" if result["success"] else "failed",
        "persona": persona,
        "post_id": result.get("post_id"),
    }


def get_state() -> dict:
    """Return a copy of the current engine state for the API."""
    is_sleeping()  # Refresh sleep status
    return {**state}
