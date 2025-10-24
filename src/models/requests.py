"""
Request/Response Models
=======================

Pydantic models for API requests and responses.

Author: CartWise Team
Version: 1.0.0
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class OTPRequest(BaseModel):
    """Request OTP for phone number."""

    phone: str = Field(..., description="User phone number")


class OTPVerifyRequest(BaseModel):
    """Verify OTP code."""

    phone: str = Field(..., description="User phone number")
    otp_code: str = Field(..., description="OTP verification code")


class CartAssignmentRequest(BaseModel):
    """Request to assign a cart."""

    phone: str = Field(..., description="User phone number")
    otp_code: str = Field(..., description="OTP verification code")


class CartReturnRequest(BaseModel):
    """Request to return a cart."""

    phone: str = Field(..., description="User phone number")


class CartReturnInitRequest(BaseModel):
    """Request to initiate cart return process (find available lock)."""

    phone: str = Field(..., description="User phone number")


class CartReturnInitResponse(BaseModel):
    """Response with assigned return locker."""

    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Response message")
    locker_number: Optional[int] = Field(None, description="Assigned locker number (0-15)")
    locker_id: Optional[int] = Field(None, description="Locker ID for tracking")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="System status")
    timestamp: datetime = Field(..., description="Response timestamp")
    rs485_connected: bool = Field(..., description="RS485 controller status")
    sms_configured: bool = Field(..., description="SMS provider status")
    active_carts: int = Field(..., description="Number of active carts")
