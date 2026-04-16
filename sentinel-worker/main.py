"""
Sentinel-Square — PM2 Entry Point
===================================
This is the entry point that PM2 runs on the server.
It delegates to the app package which contains the actual logic.

PM2 command:
    pm2 start "cd /opt/squareAutomation/sentinel-worker && venv/bin/python main.py"
"""

import sys
from pathlib import Path

# Ensure the sentinel-worker directory is on sys.path
_worker_dir = str(Path(__file__).parent)
if _worker_dir not in sys.path:
    sys.path.insert(0, _worker_dir)

# Launch the app
from app.main import main

if __name__ == "__main__":
    main()
