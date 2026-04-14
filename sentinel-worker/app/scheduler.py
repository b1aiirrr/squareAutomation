from __future__ import annotations

import asyncio
import os
import random
from dataclasses import asdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from .engine import build_post
from .state import SharedState, load_posts, save_posts

MIN_JITTER_MINUTES = 17
MAX_JITTER_MINUTES = 78
MIN_POSTS = 30
MAX_POSTS = 50


class Scheduler:
    def __init__(self, state: SharedState, posts_path: Path) -> None:
        load_dotenv()
        self.state = state
        self.posts_path = posts_path
        self.tz = ZoneInfo(os.getenv("TIMEZONE", "Africa/Nairobi"))
        self.sleep_start = self._parse_clock(os.getenv("SLEEP_WINDOW_START", "02:00"))
        self.sleep_end = self._parse_clock(os.getenv("SLEEP_WINDOW_END", "07:00"))
        self.target_posts_today = random.randint(MIN_POSTS, MAX_POSTS)

    def _parse_clock(self, value: str) -> time:
        hour, minute = value.split(":")
        return time(hour=int(hour), minute=int(minute))

    def _in_sleep_window(self, now: datetime) -> bool:
        current = now.timetz().replace(tzinfo=None)
        return self.sleep_start <= current <= self.sleep_end

    def _next_wakeup(self, now: datetime) -> datetime:
        wake = datetime.combine(now.date(), self.sleep_end, tzinfo=self.tz)
        if wake <= now:
            wake = wake + timedelta(days=1)
        return wake

    async def _simulate_publish(self, payload: dict[str, str]) -> None:
        await asyncio.sleep(random.uniform(0.4, 1.4))
        await self.state.add_log("info", f"Published {payload['persona']} post to Binance Square")

    async def run(self) -> None:
        posts = load_posts(self.posts_path)
        for post in posts[-200:]:
            await self.state.add_post(post)

        await self.state.add_log("info", f"Daily target set to {self.target_posts_today} posts")

        while True:
            now = datetime.now(self.tz)
            posted_today = [p for p in posts if p.get("posted_date") == date.today().isoformat()]
            if len(posted_today) >= self.target_posts_today:
                self.target_posts_today = random.randint(MIN_POSTS, MAX_POSTS)
                await self.state.add_log("info", f"Daily target reached. Resetting next target to {self.target_posts_today} posts")
                await asyncio.sleep(60)
                continue

            if self._in_sleep_window(now):
                self.state.status = "sleeping"
                wakeup = self._next_wakeup(now)
                self.state.next_post_at = wakeup.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
                await self.state.add_log("warn", f"Sleep window active until {wakeup.isoformat()}")
                await asyncio.sleep(max((wakeup - now).total_seconds(), 60))
                continue

            self.state.status = "posting"
            post = build_post()
            payload = {
                "persona": post.persona,
                "prompt": post.prompt,
                "body": post.body,
                "posted_at": datetime.utcnow().isoformat(),
                "posted_date": date.today().isoformat(),
                "channel": "binance-square",
            }

            await self._simulate_publish(payload)
            posts.append(payload)
            save_posts(self.posts_path, posts)
            await self.state.add_post(payload)

            wait_minutes = random.randint(MIN_JITTER_MINUTES, MAX_JITTER_MINUTES)
            next_at = datetime.now(self.tz) + timedelta(minutes=wait_minutes)
            self.state.next_post_at = next_at.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
            await self.state.add_log("info", f"Next post scheduled in {wait_minutes} minutes")
            await asyncio.sleep(wait_minutes * 60)
