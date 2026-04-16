"""
Sentinel-Square Status API v5.1
================================
FastAPI server exposing engine state, log history, and real-time log
streaming via Server-Sent Events (SSE). Runs on port 8585.

The scheduler is started/stopped via the lifespan context manager,
ensuring it shares the same asyncio event loop as the API.
"""

import sys
import json
import asyncio
import logging
from pathlib import Path
from collections import deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

# Ensure parent sentinel-worker/ directory is on sys.path for config
_worker_dir = str(Path(__file__).parent.parent)
if _worker_dir not in sys.path:
    sys.path.insert(0, _worker_dir)

from config import ALLOWED_ORIGINS, LOG_FILE
from .engine import get_state
from .state import SharedState
from .scheduler import Scheduler

logger = logging.getLogger("sentinel.api")

# ---------------------------------------------------------------------------
# Shared State & Scheduler (module-level for access by endpoints)
# ---------------------------------------------------------------------------
_state = SharedState()
_scheduler_instance = None


# ---------------------------------------------------------------------------
# Lifespan — starts/stops the scheduler on the SAME event loop as the API
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app):
    """
    FastAPI lifespan handler.
    Startup: initializes the scheduler on uvicorn's event loop.
    Shutdown: gracefully stops the scheduler.
    """
    global _scheduler_instance

    logger.info("Lifespan startup: initializing scheduler on API event loop...")

    posts_path = Path(__file__).parent.parent / "posts.json"
    _scheduler_instance = Scheduler(_state, posts_path)

    # Start the scheduler — APScheduler attaches to the CURRENT (uvicorn's) event loop
    await _scheduler_instance.run()

    # Store state in engine so get_state() works
    from .engine import set_state
    set_state(_state)

    logger.info("Scheduler is now running on the API event loop ✓")
    yield

    # Shutdown
    logger.info("Lifespan shutdown: stopping scheduler...")
    if _scheduler_instance:
        _scheduler_instance.stop_scheduler()
    logger.info("Scheduler stopped cleanly ✓")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Sentinel-Square API",
    description="Status & monitoring API for the Sentinel-Square content engine",
    version="5.1.0",
    lifespan=lifespan,
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
    state = get_state()
    if state and hasattr(state, 'snapshot'):
        return await state.snapshot()
    elif state:
        return state
    return {"status": "initializing"}


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

            # Heartbeat every 15s to keep the connection alive
            yield {"event": "heartbeat", "data": "ping"}
            await asyncio.sleep(3)

    return EventSourceResponse(_event_generator())


@app.get("/api/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "sentinel-square-worker", "version": "5.1.0"}
