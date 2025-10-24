"""
CartWise Pro - Server Launcher
===============================

Launches the FastAPI server with proper Python path configuration.

Usage:
    python run_server.py

Author: CartWise Team
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Now import and run
import uvicorn
from core import settings, setup_logging, get_logger
from api import create_app

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create application
app = create_app()

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Starting CartWise Pro Server")
    logger.info(f"Host: {settings.HOST}")
    logger.info(f"Port: {settings.PORT}")
    logger.info(f"API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 80)

    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
    )
