"""
Rentals Router
==============

Rental history and management endpoints.

Author: CartWise Team
Version: 1.0.0
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query

from core import get_logger
from models import Rental, RentalHistoryResponse
from api.dependencies import get_rental_db, get_monitor

logger = get_logger(__name__)

router = APIRouter(prefix="/rentals", tags=["Rentals"])


@router.get("/history", response_model=RentalHistoryResponse)
async def get_rental_history(
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    limit: int = Query(100, description="Maximum number of records"),
    rental_db=Depends(get_rental_db),
):
    """
    Get rental history.

    Args:
        phone: Optional phone number to filter by
        limit: Maximum number of records to return

    Returns:
        Rental history with statistics
    """
    logger.info(f"Rental history requested (phone={phone}, limit={limit})")

    rentals = rental_db.get_rental_history(phone=phone, limit=limit)
    stats = rental_db.get_statistics()

    return RentalHistoryResponse(
        rentals=rentals,
        total_count=stats.get("total_rentals", 0),
        active_count=stats.get("active_rentals", 0),
        late_count=stats.get("overdue_rentals", 0) + stats.get("late_returns", 0),
    )


@router.get("/active", response_model=List[Rental])
async def get_active_rentals(
    rental_db=Depends(get_rental_db),
):
    """
    Get all currently active rentals.

    Returns:
        List of active rentals
    """
    logger.info("Active rentals requested")

    all_rentals = rental_db.get_rental_history(limit=1000)
    active_rentals = [r for r in all_rentals if r.status.value == "active"]

    return active_rentals


@router.get("/overdue", response_model=List[Rental])
async def get_overdue_rentals(
    rental_db=Depends(get_rental_db),
):
    """
    Get all overdue rentals.

    Returns:
        List of overdue rentals
    """
    logger.info("Overdue rentals requested")

    overdue = rental_db.get_overdue_rentals()

    return overdue


@router.get("/my-rental")
async def get_my_rental(
    phone: str = Query(..., description="Phone number"),
    rental_db=Depends(get_rental_db),
):
    """
    Get current active rental for a user.

    Args:
        phone: User phone number

    Returns:
        Active rental or 404 if none found
    """
    logger.info(f"Rental lookup for {phone}")

    rental = rental_db.get_active_rental_by_phone(phone)

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="לא נמצאה עגלה פעילה (No active rental found)"
        )

    return {
        "rental": rental,
        "is_late": rental.is_late,
        "time_remaining": str(rental.time_remaining),
        "duration": str(rental.duration),
    }


@router.get("/{rental_id}", response_model=Rental)
async def get_rental(
    rental_id: int,
    rental_db=Depends(get_rental_db),
):
    """
    Get rental by ID.

    Args:
        rental_id: Rental ID

    Returns:
        Rental details
    """
    logger.info(f"Rental {rental_id} requested")

    rental = rental_db.get_rental(rental_id)

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found"
        )

    return rental


@router.get("/stats/summary")
async def get_rental_stats(
    rental_db=Depends(get_rental_db),
):
    """
    Get rental statistics summary.

    Returns:
        Statistics about rentals
    """
    logger.info("Rental statistics requested")

    stats = rental_db.get_statistics()

    return stats


@router.get("/monitor/status")
async def get_monitor_status(
    monitor=Depends(get_monitor),
):
    """
    Get CU16 monitor service status.

    Returns:
        Monitor status information
    """
    if not monitor:
        return {
            "running": False,
            "message": "Monitor not initialized"
        }

    return monitor.get_monitoring_status() if hasattr(monitor, 'get_monitoring_status') else {
        "running": monitor.running if hasattr(monitor, 'running') else False
    }


@router.post("/force-complete/{rental_id}")
async def force_complete_rental(
    rental_id: int,
    rental_db=Depends(get_rental_db),
):
    """
    Force complete a rental (admin/debug use).

    Args:
        rental_id: Rental ID to complete

    Returns:
        Success message
    """
    logger.warning(f"Force completing rental {rental_id}")

    rental = rental_db.get_rental(rental_id)

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found"
        )

    rental.mark_returned()
    rental_db.update_rental(rental)

    return {
        "success": True,
        "message": f"Rental {rental_id} force completed"
    }
