"""
Constants Module
================

Global constants used throughout the application.

Author: CartWise Team
Version: 1.0.0
"""

from enum import Enum


class ProtocolBytes:
    """RS485 Protocol bytes and commands."""

    # Protocol markers
    STX = 0x02  # Start of Text
    ETX = 0x03  # End of Text

    # Commands
    LOCK = 0x30
    UNLOCK = 0x31
    STATUS = 0x32
    MICROSWITCH = 0x33


class OTPConfig:
    """OTP-related constants."""

    # Default values (can be overridden by environment variables)
    DEFAULT_CODE_LENGTH = 4
    DEFAULT_EXPIRATION_MINUTES = 5
    DEFAULT_MAX_ATTEMPTS = 3


class SMSTemplates:
    """SMS message templates in Hebrew."""

    @staticmethod
    def otp_message(otp_code: str) -> str:
        """Generate OTP SMS message."""
        return f"קוד האימות שלך הוא: {otp_code}\nCartWise - מערכת עגלות חכמות"

    @staticmethod
    def confirmation_message(cart_number: int) -> str:
        """Generate cart assignment confirmation message."""
        return (
            f"עגלה מספר {cart_number} הוקצתה לך.\n"
            f"נא להחזיר את העגלה למקומה בסיום הקניות.\n"
            f"תודה שבחרת ב-CartWise!"
        )

    @staticmethod
    def return_reminder_message(cart_number: int) -> str:
        """Generate cart return reminder message."""
        return (
            f"תזכורת: עגלה {cart_number} עדיין לא הוחזרה.\n"
            f"נא להחזיר את העגלה למקומה.\n"
            f"תודה!"
        )


class HTTPMessages:
    """HTTP response messages in Hebrew."""

    # Success messages
    OTP_SENT = "קוד אימות נשלח למספר הטלפון שלך"
    OTP_VERIFIED = "אימות הצליח"
    CART_ASSIGNED = "עגלה הוקצתה לך בהצלחה"
    CART_RETURNED = "תודה! העגלה הוחזרה בהצלחה"

    # Error messages
    INVALID_OTP = "קוד אימות שגוי או פג תוקף"
    NO_CARTS_AVAILABLE = "אין עגלות זמינות כרגע"
    CART_NOT_FOUND = "עגלה לא נמצאה"
    CART_NOT_ASSIGNED_TO_USER = "עגלה זו לא הוקצתה לך"
    LOCK_ERROR = "שגיאה בפתיחת המנעול"
    SMS_ERROR = "שגיאה בשליחת SMS"
    INVALID_PHONE = "מספר טלפון לא תקין"
