"""
Sentinel-Square — Main Entry Point
====================================
Starts the FastAPI status server and the content scheduling engine.
Run with: python main.py
"""

import signal
import logging
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
 |____/ \__\_\\___/_/   \_\_| \_\_____|   v4.0

 Autonomous Content Engine for Binance Square
 by Blair Momanyi
"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(BANNER)
    logger.info("Starting Sentinel-Square Worker v4.0")

    # Import here to avoid circular imports during config validation
    from scheduler import start_scheduler, stop_scheduler
    from api import app

    # --- Graceful shutdown ---
    def _shutdown(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        stop_scheduler()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # --- Start scheduler ---
    start_scheduler()

    # --- Start API server ---
    logger.info(f"API server starting on {API_HOST}:{API_PORT}")
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="warning",  # Reduce uvicorn noise
    )


if __name__ == "__main__":
    main()
