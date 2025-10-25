"""
FastAPI Application
===================

Main FastAPI application factory.

Author: CartWise Team
Version: 1.0.0
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core import setup_logging, get_logger, settings
from hardware.rs485 import RS485Controller
from api.dependencies import set_lock_controller, init_monitor, shutdown_monitor
from api.routers import auth_router, carts_router, health_router, rentals_router, agent_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI app instance
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(carts_router)
    app.include_router(rentals_router)
    app.include_router(agent_router)  # Agent communication endpoints

    # Mount static files directory
    static_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "public"
    )
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        logger.info(f"Static files mounted from {static_dir}")

    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize hardware connections and services on startup."""
        logger.info("Starting CartWise Pro API Server...")

        # Initialize RS485 controller
        try:
            lock_controller = RS485Controller(
                port=settings.SERIAL_PORT, baudrate=settings.BAUD_RATE
            )
            if lock_controller.connect():
                logger.info("RS485 controller connected")
                set_lock_controller(lock_controller)
            else:
                logger.warning("RS485 controller not available (running in demo mode)")
                set_lock_controller(None)
        except Exception as e:
            logger.error(f"Failed to initialize RS485 controller: {e}")
            set_lock_controller(None)

        # Initialize and start CU16 monitor service
        try:
            init_monitor()
            logger.info("CU16 monitor service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize monitor service: {e}")

        logger.info("CartWise Pro API Server started successfully!")

    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        logger.info("Shutting down CartWise Pro API Server...")

        # Shutdown monitor service
        try:
            shutdown_monitor()
        except Exception as e:
            logger.error(f"Error shutting down monitor: {e}")

        # Disconnect RS485 controller
        from api.dependencies import get_lock_controller

        lock_controller = get_lock_controller()
        if lock_controller:
            lock_controller.disconnect()
            logger.info("RS485 controller disconnected")

        logger.info("Shutdown complete")

    return app
