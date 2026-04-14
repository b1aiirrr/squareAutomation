"""
Sentinel-Square Scheduler
==========================
Uses APScheduler to run content cycles with randomized human-like intervals.
Handles daily resets, rewards optimization, and graceful shutdown.
"""

import asyncio
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
    TRADING_API_KEY,
    TRADING_API_SECRET,
    BINANCE_SQUARE_API_KEY,
    FRIEND_SQUARE_API_KEY,
)
from engine import run_cycle, daily_reset, recalculate_sleep_window, init_trading, load_posts, save_posts, get_state
from rewards_engine import RewardsEngine
from binance.client import Client

logger = logging.getLogger("sentinel.scheduler")

_tz = ZoneInfo(TIMEZONE)


class Scheduler:
    def __init__(self, state, posts_path):
        self.state = state
        self.posts_path = posts_path
        self.scheduler = AsyncIOScheduler(timezone=_tz)
        self.rewards_engine = None

        # Initialize Binance client for rewards
        if TRADING_API_KEY and TRADING_API_SECRET:
            try:
                client = Client(TRADING_API_KEY, TRADING_API_SECRET)
                self.rewards_engine = RewardsEngine(state, client)
                logger.info("Rewards Engine initialized successfully")
            except Exception as e:
                logger.error(f"Failed to init Rewards Engine: {e}")

    def _random_interval(self) -> int:
        return random.randint(MIN_INTERVAL_MINUTES, MAX_INTERVAL_MINUTES)

    def _next_run_time(self) -> datetime:
        interval = self._random_interval()
        next_time = datetime.now(_tz) + timedelta(minutes=interval)
        self.state.next_post_at = next_time
        logger.info(f"Next post scheduled in {interval} min → {next_time.strftime('%H:%M:%S')}")
        return next_time

    async def _cycle_job(self):
        try:
            # Run content + trading cycle
            result = await run_cycle(self.state)

            # Run rewards optimization cycle
            if self.rewards_engine:
                posts = load_posts(self.posts_path)
                reward_results = await self.rewards_engine.run_reward_cycle(posts)

                # Log rewards summary
                if reward_results["launchpools"]:
                    pools = reward_results["launchpools"]
                    await self.state.add_log(
                        "info",
                        f" Rewards: {len(pools)} Launchpools detected | Best tickers: {reward_results['best_tickers']}"
                    )

            logger.info(f"Cycle result: {result.get('status', 'unknown')}")
        except Exception as e:
            logger.error(f"Cycle crashed: {e}", exc_info=True)

        self._schedule_next_cycle()

    def _schedule_next_cycle(self):
        next_time = self._next_run_time()
        self.scheduler.add_job(
            self._cycle_job,
            trigger=DateTrigger(run_date=next_time),
            id="next_cycle",
            replace_existing=True,
            misfire_grace_time=300,
        )

    async def run(self):
        # Initialize trading engine
        init_trading(self.state)

        # Initialize rewards engine
        if self.rewards_engine:
            await self.state.add_log("info", "Rewards Engine: Active")

        # Calculate today's sleep window
        recalculate_sleep_window()

        # Warm-up delay
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
            trigger=CronTrigger(hour=0, minute=0, timezone=_tz),
            id="daily_reset",
            replace_existing=True,
        )

        # Rewards check every hour
        if self.rewards_engine:
            self.scheduler.add_job(
                self._rewards_check_job,
                trigger=CronTrigger(minute=0, timezone=_tz),
                id="hourly_rewards",
                replace_existing=True,
            )

        self.scheduler.start()
        logger.info(f"Scheduler started. First cycle in {warm_up} min ({first_run.strftime('%H:%M:%S')} {TIMEZONE})")

    async def _rewards_check_job(self):
        """Hourly rewards check"""
        if self.rewards_engine:
            posts = load_posts(self.posts_path)
            results = await self.rewards_engine.run_reward_cycle(posts)

            yield_summary = results.get("yield_sweep")
            if yield_summary:
                await self.state.add_log(
                    "info",
                    f" Yield Sweep: ${yield_summary.get('amount_usdt', 0):.2f} @ {yield_summary.get('apr', 0)}% APR"
                )

            pools = results.get("launchpools", [])
            if pools:
                await self.state.add_log(
                    "info",
                    f" Launchpools: {len(pools)} active | Top: {pools[0].get('token', 'N/A')} @ {pools[0].get('apr', 0)}%"
                )


_scheduler = None

def get_scheduler() -> Scheduler:
    global _scheduler
    return _scheduler

async def start_scheduler(state, posts_path):
    global _scheduler
    _scheduler = Scheduler(state, posts_path)
    await _scheduler.run()

def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.scheduler.running:
        _scheduler.scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
