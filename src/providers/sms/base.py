"""
Base SMS Provider
=================

Abstract base class for SMS providers.

Author: CartWise Team
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class SMSResponse:
    """SMS API response."""

    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    status_code: Optional[int] = None


class SMSProvider(ABC):
    """
    Abstract base class for SMS providers.

    All SMS providers must implement these methods.
    """

    @abstractmethod
    def send_sms(self, phone: str, message: str, sender: str = "CartWise") -> SMSResponse:
        """
        Send an SMS message.

        Args:
            phone: Recipient phone number
            message: Message text
            sender: Sender name

        Returns:
            SMSResponse with result
        """
        pass

    @abstractmethod
    def send_otp(self, phone: str, otp_code: str) -> SMSResponse:
        """
        Send OTP code via SMS.

        Args:
            phone: Recipient phone number
            otp_code: OTP code

        Returns:
            SMSResponse with result
        """
        pass

    @abstractmethod
    def send_confirmation(self, phone: str, cart_number: int) -> SMSResponse:
        """
        Send cart assignment confirmation.

        Args:
            phone: Recipient phone number
            cart_number: Assigned cart number

        Returns:
            SMSResponse with result
        """
        pass
