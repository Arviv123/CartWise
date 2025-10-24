"""
Cart Model
==========

Data model for shopping carts.

Author: CartWise Team
Version: 1.0.0
"""

from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CartStatus(str, Enum):
    """Cart status enumeration"""
    AVAILABLE = "available"
    IN_USE = "in_use"
    RETURNED = "returned"
    MAINTENANCE = "maintenance"
    LOCKED = "locked"


class Cart(BaseModel):
    """Shopping cart model"""

    cart_id: int = Field(..., description="Unique cart identifier")
    locker_id: int = Field(..., description="Physical locker ID")
    status: CartStatus = Field(default=CartStatus.AVAILABLE, description="Current cart status")
    assigned_to: Optional[str] = Field(None, description="Phone number of assigned user")
    assigned_at: Optional[datetime] = Field(None, description="Assignment timestamp")
    returned_at: Optional[datetime] = Field(None, description="Return timestamp")
    is_locked: bool = Field(default=True, description="Physical lock status")

    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "cart_id": 1,
                "locker_id": 1,
                "status": "available",
                "assigned_to": None,
                "assigned_at": None,
                "returned_at": None,
                "is_locked": True
            }
        }

    def assign(self, phone: str):
        """Assign cart to a user"""
        self.status = CartStatus.IN_USE
        self.assigned_to = phone
        self.assigned_at = datetime.now()
        self.is_locked = False

    def return_cart(self):
        """Mark cart as returned"""
        self.status = CartStatus.RETURNED
        self.returned_at = datetime.now()
        self.is_locked = True

    def mark_available(self):
        """Mark cart as available for assignment"""
        self.status = CartStatus.AVAILABLE
        self.assigned_to = None
        self.assigned_at = None
        self.returned_at = None
        self.is_locked = True


class CartAssignmentRequest(BaseModel):
    """Request to assign a cart"""
    phone: str = Field(..., description="User phone number")
    otp_code: str = Field(..., description="OTP verification code")


class CartReturnRequest(BaseModel):
    """Request to return a cart"""
    cart_id: int = Field(..., description="Cart ID to return")
    phone: str = Field(..., description="User phone number")
