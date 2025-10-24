"""
Validation Utilities
====================

Input validation functions.

Author: CartWise Team
Version: 1.0.0
"""

import re
from typing import Optional


def validate_phone(phone: str) -> bool:
    """
    Validate Israeli phone number.

    Accepts formats:
    - 05X-XXXXXXX or 05XXXXXXXX
    - +972-5X-XXXXXXX

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_phone("0501234567")
        True
        >>> validate_phone("+972501234567")
        True
        >>> validate_phone("123456")
        False
    """
    if not phone:
        return False

    # Remove spaces, dashes, etc.
    clean_phone = phone.replace("-", "").replace(" ", "").replace("+972", "0")

    # Check format: 05X-XXXXXXX or 05XXXXXXXX
    if len(clean_phone) == 10 and clean_phone.startswith("05"):
        return clean_phone.isdigit()

    # Check international format: +972-5X-XXXXXXX
    if phone.startswith("+972") and len(clean_phone) == 10:
        return clean_phone.isdigit()

    return False


def validate_otp_code(code: str, expected_length: int = 4) -> bool:
    """
    Validate OTP code format.

    Args:
        code: OTP code to validate
        expected_length: Expected length of OTP code

    Returns:
        True if valid format, False otherwise

    Examples:
        >>> validate_otp_code("1234", 4)
        True
        >>> validate_otp_code("12", 4)
        False
        >>> validate_otp_code("abcd", 4)
        False
    """
    if not code:
        return False

    # Check length
    if len(code) != expected_length:
        return False

    # Check if all digits
    return code.isdigit()


def validate_cart_id(cart_id: int, min_id: int = 1, max_id: int = 100) -> bool:
    """
    Validate cart ID.

    Args:
        cart_id: Cart ID to validate
        min_id: Minimum valid cart ID
        max_id: Maximum valid cart ID

    Returns:
        True if valid, False otherwise
    """
    return min_id <= cart_id <= max_id


def sanitize_phone(phone: str) -> str:
    """
    Sanitize phone number to standard format.

    Converts various formats to 05XXXXXXXX format.

    Args:
        phone: Phone number to sanitize

    Returns:
        Sanitized phone number

    Examples:
        >>> sanitize_phone("+972-50-123-4567")
        "0501234567"
        >>> sanitize_phone("050-123-4567")
        "0501234567"
    """
    # Remove all non-digit characters except +
    clean = re.sub(r'[^\d+]', '', phone)

    # Convert +972 to 0
    if clean.startswith("+972"):
        clean = "0" + clean[4:]

    return clean
