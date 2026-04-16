"""
Sentinel-Square — Main Entry Point v5.1 (Lifespan Fix)
========================================================
Starts the FastAPI server with the scheduler running on the SAME event loop
via FastAPI's lifespan context manager.

Previous bug: asyncio.run(start_scheduler()) created a temporary event loop,
then destroyed it, orphaning all APScheduler jobs. The API started on its own
loop, so the scheduler was brain-dead.

Run from sentinel-worker/ directory:
    python -m app.main
"""

import sys
import signal
import logging
from pathlib import Path

# Ensure the parent sentinel-worker/ directory is on sys.path
# so that 'config' and other top-level modules can be imported
_worker_dir = str(Path(__file__).parent.parent)
if _worker_dir not in sys.path:
    sys.path.insert(0, _worker_dir)

import uvicorn
from config import API_HOST, API_PORT

# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-22s │ %(levelname)-7s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("sentinel")

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
BANNER = r"""
  ____  _____ _   _ _____ ___ _   _ _____ _
 / ___|| ____| \ | |_   _|_ _| \ | | ____| |
 \___ \|  _| |  \| | | |  | ||  \| |  _| | |
  ___) | |___| |\  | | |  | || |\  | |___| |___
 |____/|_____|_| \_| |_| |___|_| \_|_____|_____|
  ____   ___  _   _   _    ____  _____
 / ___| / _ \| | | | / \  |  _ \| ____|
 \___ \| | | | | | |/ _ \ | |_) |  _|
  ___) | |_| | |_| / ___ \|  _ <| |___
 |____/ \__\_\\___/_/   \_\_| \_\_____|   v5.1 (Lifespan)

 Autonomous Content & Rewards Engine for Binance Square
 by Blair Momanyi
"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(BANNER)
    logger.info("Starting Sentinel-Square Worker v5.1 (Lifespan Mode)")

    from .api import app

    # --- Signal handler for graceful shutdown ---
    def _shutdown(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        raise SystemExit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # --- Start uvicorn ---
    # The scheduler starts automatically via FastAPI lifespan events in api.py.
    # Both share uvicorn's asyncio event loop, so APScheduler jobs WILL fire.
    logger.info(f"Starting server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="warning",
        access_log=False,
    )


if __name__ == "__main__":
    main()
