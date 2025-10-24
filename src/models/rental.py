"""
Rental Model
============

Data model for cart rental tracking and history.

Author: CartWise Team
Version: 1.0.0
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field


class RentalStatus(str, Enum):
    """Rental status enumeration"""
    ACTIVE = "active"           # Currently rented out
    RETURNED = "returned"       # Returned on time
    RETURNED_LATE = "returned_late"  # Returned but late
    OVERDUE = "overdue"         # Not returned, past due time
    CANCELLED = "cancelled"     # Rental cancelled


class Rental(BaseModel):
    """
    Shopping cart rental record.

    Tracks the complete lifecycle of a cart rental from assignment to return.
    """

    rental_id: Optional[int] = Field(None, description="Unique rental identifier (auto-generated)")
    cart_id: int = Field(..., description="Cart ID that was rented")
    user_phone: str = Field(..., description="Phone number of renting user")
    locker_id: int = Field(..., description="Physical locker ID used")

    # Timestamps
    start_time: datetime = Field(default_factory=datetime.now, description="Rental start time")
    expected_return: datetime = Field(..., description="Expected return time")
    actual_return: Optional[datetime] = Field(None, description="Actual return time")

    # Status
    status: RentalStatus = Field(default=RentalStatus.ACTIVE, description="Current rental status")

    # Additional info
    notes: Optional[str] = Field(None, description="Additional notes or remarks")

    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "rental_id": 1,
                "cart_id": 5,
                "user_phone": "0501234567",
                "locker_id": 4,
                "start_time": "2025-10-23T10:00:00",
                "expected_return": "2025-10-23T12:00:00",
                "actual_return": None,
                "status": "active",
                "notes": None
            }
        }

    @property
    def is_late(self) -> bool:
        """Check if rental is late (past expected return time)."""
        if self.status == RentalStatus.ACTIVE:
            return datetime.now() > self.expected_return
        elif self.status == RentalStatus.RETURNED:
            return False
        elif self.status == RentalStatus.RETURNED_LATE:
            return True
        return False

    @property
    def time_remaining(self) -> timedelta:
        """Get time remaining until expected return (negative if late)."""
        return self.expected_return - datetime.now()

    @property
    def duration(self) -> timedelta:
        """Get actual or current rental duration."""
        end_time = self.actual_return or datetime.now()
        return end_time - self.start_time

    def mark_returned(self):
        """Mark rental as returned and update status based on timing."""
        self.actual_return = datetime.now()

        if self.actual_return > self.expected_return:
            self.status = RentalStatus.RETURNED_LATE
        else:
            self.status = RentalStatus.RETURNED

    def mark_overdue(self):
        """Mark rental as overdue (not returned past expected time)."""
        if self.status == RentalStatus.ACTIVE:
            self.status = RentalStatus.OVERDUE


class RentalCreateRequest(BaseModel):
    """Request to create a new rental."""
    cart_id: int = Field(..., description="Cart ID to rent")
    user_phone: str = Field(..., description="User phone number")
    locker_id: int = Field(..., description="Locker ID")
    duration_minutes: int = Field(default=120, description="Rental duration in minutes")


class RentalHistoryResponse(BaseModel):
    """Response with rental history."""
    rentals: list[Rental] = Field(..., description="List of rentals")
    total_count: int = Field(..., description="Total number of rentals")
    active_count: int = Field(..., description="Number of active rentals")
    late_count: int = Field(..., description="Number of late/overdue rentals")
