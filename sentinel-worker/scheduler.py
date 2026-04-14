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
from engine import run_cycle, daily_reset, recalculate_sleep_window, init_trading
from .state import SharedState

logger = logging.getLogger("sentinel.scheduler")

_tz = ZoneInfo(TIMEZONE)


class Scheduler:
    def __init__(self, state: SharedState, posts_path):
        self.state = state
        self.posts_path = posts_path
        self.scheduler = AsyncIOScheduler(timezone=_tz)

    # ---------------------------------------------------------------------------
    # Human Jitter
    # ---------------------------------------------------------------------------
    def _random_interval(self) -> int:
        """Return a random interval in minutes between MIN and MAX."""
        return random.randint(MIN_INTERVAL_MINUTES, MAX_INTERVAL_MINUTES)

    def _next_run_time(self) -> datetime:
        """Calculate the next run time with human jitter."""
        interval = self._random_interval()
        next_time = datetime.now(_tz) + timedelta(minutes=interval)
        self.state.next_post_at = next_time
        logger.info(f"Next post scheduled in {interval} min → {next_time.strftime('%H:%M:%S')}")
        return next_time

    # ---------------------------------------------------------------------------
    # Cycle Wrapper (schedules the *next* cycle after completion)
    # ---------------------------------------------------------------------------
    async def _cycle_job(self):
        """Run one content cycle, then schedule the next one."""
        try:
            result = await run_cycle(self.state)
            logger.info(f"Cycle result: {result.get('status', 'unknown')}")
        except Exception as e:
            logger.error(f"Cycle crashed: {e}", exc_info=True)

        # Always schedule the next cycle, even if this one failed
        self._schedule_next_cycle()

    def _schedule_next_cycle(self):
        """Schedule the next content cycle with a random delay."""
        next_time = self._next_run_time()
        self.scheduler.add_job(
            self._cycle_job,
            trigger=DateTrigger(run_date=next_time),
            id="next_cycle",
            replace_existing=True,
            misfire_grace_time=300,
        )

    # ---------------------------------------------------------------------------
    # Startup
    # ---------------------------------------------------------------------------
    async def run(self):
        """
        Initialize and start the scheduler.
        """
        # Initialize trading engine
        init_trading(self.state)
        
        # Calculate today's sleep window
        recalculate_sleep_window()

        # Schedule the first cycle with a short warm-up delay
        warm_up = random.randint(1, 5)
        first_run = datetime.now(_tz) + timedelta(minutes=warm_up)
        self.state.next_post_at = first_run
        self.state.status = "running"

        self.scheduler.add_job(
            self._cycle_job,
            trigger=DateTrigger(run_date=first_run),
            id="next_cycle",
            replace_existing=True,
            misfire_grace_time=300,
        )

        # Daily reset at midnight
        self.scheduler.add_job(
            daily_reset,
            trigger=CronTrigger(hour=0, minute=0),
            id="daily_reset",
            args=[self.state],
        )

        self.scheduler.start()
        logger.info("Scheduler started")

    def stop_scheduler(self):
        """Gracefully shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.state.status = "stopped"
            logger.info("Scheduler stopped")
