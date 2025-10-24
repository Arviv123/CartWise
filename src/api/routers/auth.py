"""
Authentication Router
=====================

OTP authentication endpoints.

Author: CartWise Team
Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import Optional

from core import get_logger
from core.constants import HTTPMessages
from models import OTPRequest, OTPVerifyRequest
from api.dependencies import get_otp_manager, get_sms_provider, get_auth_token_manager

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/request-otp")
async def request_otp(
    request: OTPRequest,
    otp_manager=Depends(get_otp_manager),
    sms_provider=Depends(get_sms_provider),
    auth_token_manager=Depends(get_auth_token_manager),
    authorization: Optional[str] = Header(None),
):
    """
    Request OTP code.

    Generates and sends OTP code via SMS.
    If user already has a valid auth token, OTP is not required.

    Args:
        request: Phone number to send OTP to
        authorization: Optional auth token (Bearer token)

    Returns:
        Success message or already authenticated status
    """
    logger.info(f"OTP requested for {request.phone}")

    # Check if user already has valid auth token
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        validated_phone = auth_token_manager.validate_token(token)

        if validated_phone == request.phone:
            logger.info(f"User {request.phone} already authenticated, skipping OTP")
            return {
                "success": True,
                "message": "כבר מאומת (Already authenticated)",
                "already_authenticated": True,
                "phone": request.phone,
            }

    # Generate OTP
    otp_code = otp_manager.generate_otp(request.phone)

    # Send SMS
    sms_response = sms_provider.send_otp(request.phone, otp_code)

    if not sms_response.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{HTTPMessages.SMS_ERROR}: {sms_response.error}",
        )

    logger.info(f"OTP sent to {request.phone}")

    return {
        "success": True,
        "message": HTTPMessages.OTP_SENT,
        "expires_in_minutes": otp_manager.expiration_minutes,
        "already_authenticated": False,
    }


@router.post("/verify-otp")
async def verify_otp(
    request: OTPVerifyRequest,
    otp_manager=Depends(get_otp_manager),
    auth_token_manager=Depends(get_auth_token_manager),
):
    """
    Verify OTP code.

    Args:
        request: Phone and OTP code

    Returns:
        Verification result with authentication token
    """
    logger.info(f"Verifying OTP for {request.phone}")

    is_valid = otp_manager.validate_otp(request.phone, request.otp_code)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=HTTPMessages.INVALID_OTP
        )

    # Generate authentication token for this user
    auth_token = auth_token_manager.generate_token(request.phone)

    logger.info(f"OTP verified for {request.phone}, token generated")

    return {
        "success": True,
        "message": HTTPMessages.OTP_VERIFIED,
        "phone": request.phone,
        "auth_token": auth_token,
        "token_expires_days": 30,
    }
