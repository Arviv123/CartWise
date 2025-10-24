"""
Health & Stats Router
=====================

Health check and statistics endpoints.

Author: CartWise Team
Version: 1.0.0
"""

from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, JSONResponse
import os

from core import get_logger, settings
from models import HealthResponse, CartStatus
from api.dependencies import get_otp_manager, get_lock_controller, get_carts_db

logger = get_logger(__name__)

router = APIRouter(tags=["Health & Stats"])


@router.get("/", response_class=FileResponse)
async def root():
    """Serve the main customer interface."""
    static_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "public",
        "index.html",
    )
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return JSONResponse({"message": "CartWise Pro API - Use /docs for API documentation"})


@router.get("/health", response_model=HealthResponse)
async def health_check(
    lock_controller=Depends(get_lock_controller),
    carts_db=Depends(get_carts_db),
):
    """
    Health check endpoint.

    Returns system status and component availability.
    """
    active_carts = sum(1 for cart in carts_db.values() if cart.status == CartStatus.IN_USE)

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        rs485_connected=(
            lock_controller is not None
            and lock_controller.serial
            and lock_controller.serial.is_open
            if lock_controller
            else False
        ),
        sms_configured=bool(settings.INFORU_USERNAME and settings.INFORU_PASSWORD),
        active_carts=active_carts,
    )


@router.get("/stats")
async def get_stats(otp_manager=Depends(get_otp_manager), carts_db=Depends(get_carts_db)):
    """
    Get system statistics.

    Returns:
        System statistics
    """
    total_carts = len(carts_db)
    available = sum(1 for c in carts_db.values() if c.status == CartStatus.AVAILABLE)
    in_use = sum(1 for c in carts_db.values() if c.status == CartStatus.IN_USE)
    maintenance = sum(1 for c in carts_db.values() if c.status == CartStatus.MAINTENANCE)

    return {
        "total_carts": total_carts,
        "available": available,
        "in_use": in_use,
        "maintenance": maintenance,
        "otp_stats": otp_manager.get_stats(),
        "timestamp": datetime.now(),
    }
