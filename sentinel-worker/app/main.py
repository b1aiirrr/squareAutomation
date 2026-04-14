from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .scheduler import Scheduler
from .state import SharedState

BASE_DIR = Path(__file__).resolve().parents[1]
POSTS_FILE = BASE_DIR / "data" / "posts.json"

state = SharedState()
app = FastAPI(title="Sentinel Worker", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    scheduler = Scheduler(state=state, posts_path=POSTS_FILE)
    asyncio.create_task(scheduler.run())
    await state.add_log("info", "Scheduler started")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"ok": "true"}


@app.get("/status")
async def status() -> dict:
    return await state.snapshot()


@app.get("/posts")
async def posts(limit: int = 50) -> dict:
    items = state.post_history[-limit:]
    return {"count": len(items), "items": items}


@app.get("/events")
async def events(request: Request) -> StreamingResponse:
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=100)
    state.subscribers.add(queue)

    async def event_generator():
        try:
            await state.add_log("info", "Dashboard client connected to SSE stream")
            while True:
                if await request.is_disconnected():
                    break
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=15)
                    yield f"data: {item}\n\n"
                except asyncio.TimeoutError:
                    keep_alive = json.dumps({"type": "keepalive"})
                    yield f"data: {keep_alive}\n\n"
        finally:
            state.subscribers.discard(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
