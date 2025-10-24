"""
CartWise Pro - Main Entry Point
================================

FastAPI backend for smart shopping cart management system.

Features:
- User authentication with OTP
- Cart assignment and management
- RS485 lock control
- SMS notifications
- Real-time status updates

Author: CartWise Team
Version: 1.0.0
"""

import uvicorn
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from core import settings, get_logger
from api import create_app

# Setup logger
logger = get_logger(__name__)

# Create application
app = create_app()


if __name__ == "__main__":
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # Enable auto-reload during development
        log_level="info",
    )
