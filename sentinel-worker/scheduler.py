"""
Sentinel-Square Scheduler
===========================
Uses APScheduler to run content cycles with randomized human-like intervals.
Handles daily resets and graceful shutdown.
"""

import random
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

from config import (
    TIMEZONE,
    MIN_INTERVAL_MINUTES,
    MAX_INTERVAL_MINUTES,
)
from engine import run_cycle, daily_reset, recalculate_sleep_window, state

logger = logging.getLogger("sentinel.scheduler")

_tz = ZoneInfo(TIMEZONE)
scheduler = AsyncIOScheduler(timezone=_tz)


# ---------------------------------------------------------------------------
# Human Jitter
# ---------------------------------------------------------------------------
def _random_interval() -> int:
    """Return a random interval in minutes between MIN and MAX."""
    return random.randint(MIN_INTERVAL_MINUTES, MAX_INTERVAL_MINUTES)


def _next_run_time() -> datetime:
    """Calculate the next run time with human jitter."""
    interval = _random_interval()
    next_time = datetime.now(_tz) + timedelta(minutes=interval)
    state["next_post_time"] = next_time.isoformat()
    logger.info(f"Next post scheduled in {interval} min → {next_time.strftime('%H:%M:%S')}")
    return next_time


# ---------------------------------------------------------------------------
# Cycle Wrapper (schedules the *next* cycle after completion)
# ---------------------------------------------------------------------------
async def _cycle_job():
    """Run one content cycle, then schedule the next one."""
    try:
        result = await run_cycle()
        logger.info(f"Cycle result: {result.get('status', 'unknown')}")
    except Exception as e:
        logger.error(f"Cycle crashed: {e}", exc_info=True)

    # Always schedule the next cycle, even if this one failed
    _schedule_next_cycle()


def _schedule_next_cycle():
    """Schedule the next content cycle with a random delay."""
    next_time = _next_run_time()
    scheduler.add_job(
        _cycle_job,
        trigger=DateTrigger(run_date=next_time),
        id="next_cycle",
        replace_existing=True,
        misfire_grace_time=300,
    )


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
def start_scheduler():
    """
    Initialize and start the scheduler.
    - First cycle runs after a short random delay (1–5 min)
    - Daily reset at midnight EAT
    """
    # Calculate today's sleep window
    recalculate_sleep_window()

    # Schedule the first cycle with a short warm-up delay
    warm_up = random.randint(1, 5)
    first_run = datetime.now(_tz) + timedelta(minutes=warm_up)
    state["next_post_time"] = first_run.isoformat()
    state["engine_status"] = "running"

    scheduler.add_job(
        _cycle_job,
        trigger=DateTrigger(run_date=first_run),
        id="next_cycle",
        replace_existing=True,
        misfire_grace_time=300,
    )

    # Daily reset at midnight
    scheduler.add_job(
        daily_reset,
        trigger=CronTrigger(hour=0, minute=0, timezone=_tz),
        id="daily_reset",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"Scheduler started. First cycle in {warm_up} min "
        f"({first_run.strftime('%H:%M:%S')} {TIMEZONE})"
    )


def stop_scheduler():
    """Gracefully shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        state["engine_status"] = "stopped"
        logger.info("Scheduler stopped")
