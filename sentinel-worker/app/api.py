"""
Sentinel-Square Status API
============================
FastAPI server exposing engine state, log history, and real-time log
streaming via Server-Sent Events (SSE). Runs on port 8585.
"""

import json
import asyncio
import logging
from pathlib import Path
from collections import deque

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from config import ALLOWED_ORIGINS, LOG_FILE
from .engine import get_state

logger = logging.getLogger("sentinel.api")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Sentinel-Square API",
    description="Status & monitoring API for the Sentinel-Square content engine",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/status")
async def status():
    """Return current engine state."""
    return get_state()


@app.get("/api/logs/history")
async def log_history(limit: int = 100):
    """Return the last N log entries as a JSON array."""
    if not LOG_FILE.exists():
        return {"logs": []}

    entries: deque = deque(maxlen=limit)
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    entries.append({"raw": line})

    return {"logs": list(entries)}


@app.get("/api/logs")
async def log_stream(request: Request):
    """
    Server-Sent Events stream of activity.log.
    Sends existing entries first, then tails for new ones.
    """

    async def _event_generator():
        # Send existing log entries
        if LOG_FILE.exists():
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        yield {"event": "log", "data": line}

        # Tail the file for new entries
        last_size = LOG_FILE.stat().st_size if LOG_FILE.exists() else 0

        while True:
            if await request.is_disconnected():
                break

            if LOG_FILE.exists():
                current_size = LOG_FILE.stat().st_size
                if current_size > last_size:
                    with open(LOG_FILE, "r", encoding="utf-8") as f:
                        f.seek(last_size)
                        for line in f:
                            line = line.strip()
                            if line:
                                yield {"event": "log", "data": line}
                    last_size = current_size

            # Also send a heartbeat every 15s to keep the connection alive
            yield {"event": "heartbeat", "data": "ping"}
            await asyncio.sleep(3)

    return EventSourceResponse(_event_generator())


@app.get("/api/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "sentinel-square-worker"}
