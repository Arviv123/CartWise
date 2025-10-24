"""
Messaging Utilities
===================

Message formatting and template utilities.

Author: CartWise Team
Version: 1.0.0
"""

from core.constants import SMSTemplates


class MessageFormatter:
    """
    Formats messages for different channels (SMS, HTTP responses, etc.).
    """

    @staticmethod
    def format_otp_sms(otp_code: str) -> str:
        """
        Format OTP SMS message.

        Args:
            otp_code: OTP code to include in message

        Returns:
            Formatted SMS message
        """
        return SMSTemplates.otp_message(otp_code)

    @staticmethod
    def format_confirmation_sms(cart_number: int) -> str:
        """
        Format cart assignment confirmation SMS.

        Args:
            cart_number: Assigned cart number

        Returns:
            Formatted SMS message
        """
        return SMSTemplates.confirmation_message(cart_number)

    @staticmethod
    def format_reminder_sms(cart_number: int) -> str:
        """
        Format cart return reminder SMS.

        Args:
            cart_number: Cart number

        Returns:
            Formatted SMS message
        """
        return SMSTemplates.return_reminder_message(cart_number)

    @staticmethod
    def format_success_response(message: str, data: dict = None) -> dict:
        """
        Format success HTTP response.

        Args:
            message: Success message
            data: Additional data to include

        Returns:
            Response dictionary
        """
        response = {"success": True, "message": message}
        if data:
            response.update(data)
        return response

    @staticmethod
    def format_error_response(message: str, code: str = None) -> dict:
        """
        Format error HTTP response.

        Args:
            message: Error message
            code: Optional error code

        Returns:
            Response dictionary
        """
        response = {"success": False, "error": message}
        if code:
            response["error_code"] = code
        return response
