"""
Sentinel-Square Shared State
===========================
Thread-safe in-memory state manager for the worker.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("sentinel.state")

POSTS_FILE = Path("posts.json")


def load_posts(path: Path = POSTS_FILE) -> list:
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_posts(path: Path, posts: list):
    try:
        with open(path, "w") as f:
            json.dump(posts[-500:], f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed to save posts: {e}")


class SharedState:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._logs = []
        self._posts = []
        self.status = "initializing"
        self.next_post_at = None
        self.engine_status = "offline"
        self.rewards_status = {
            "yield_sweep": None,
            "launchpools": [],
            "referral_ctas": 0,
            "daily_claims": {}
        }

    async def add_log(self, level: str, message: str):
        async with self._lock:
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level,
                "message": message
            }
            self._logs.append(entry)
            self._logs = self._logs[-100:]

            if level == "error":
                logger.error(message)
            else:
                logger.info(message)

    async def add_post(self, post: dict):
        async with self._lock:
            self._posts.append(post)
            self._posts = self._posts[-500:]

    async def snapshot(self) -> dict:
        async with self._lock:
            today = datetime.utcnow().date().isoformat()
            posts_today = sum(
                1 for p in self._posts
                if p.get("posted_date") == today
            )
            return {
                "status": self.status,
                "engine_status": self.engine_status,
                "posts_today": posts_today,
                "posts_total": len(self._posts),
                "last_post": self._posts[-1] if self._posts else None,
                "next_post_at": self.next_post_at,
                "rewards": self.rewards_status,
                "logs": self._logs[-20:],
            }

    async def get_logs(self, limit: int = 50) -> list:
        async with self._lock:
            return self._logs[-limit:]

    async def get_posts(self, limit: int = 50) -> list:
        async with self._lock:
            return self._posts[-limit:]
