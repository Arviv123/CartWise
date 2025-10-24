"""
Inforu SMS Provider
===================

SMS communication using the Inforu API v2.

Author: CartWise Team
Version: 1.0.0
"""

import requests
import base64
from typing import Optional

from providers.sms.base import SMSProvider, SMSResponse
from core import get_logger
from utils.validation import validate_phone
from utils.messaging import MessageFormatter

logger = get_logger(__name__)


class InforuSMSProvider(SMSProvider):
    """
    Inforu SMS API v2 Provider.

    Handles all SMS communication through the Inforu platform.
    """

    API_URL = "https://capi.inforu.co.il/api/v2/SMS/SendSms"

    def __init__(self, username: str, password: str):
        """
        Initialize Inforu SMS provider.

        Args:
            username: Inforu account username
            password: Inforu account password
        """
        self.username = username
        self.password = password
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({"Content-Type": "application/json"})

        logger.info(f"Inforu SMS configured with username: {username}")

    def send_sms(
        self, phone: str, message: str, sender: str = "CartWise"
    ) -> SMSResponse:
        """
        Send an SMS message.

        Args:
            phone: Recipient phone number (e.g., "0501234567")
            message: Message text
            sender: Sender name (max 11 characters)

        Returns:
            SMSResponse with result
        """
        logger.info(f"Sending SMS to {phone}")

        # Validate phone number
        if not validate_phone(phone):
            logger.error(f"Invalid phone number: {phone}")
            return SMSResponse(success=False, error="Invalid phone number format")

        # Build request payload (Inforu API v2 format)
        payload = {
            "Data": {
                "Message": message,
                "Recipients": [{"Phone": phone}],
                "Settings": {"Sender": sender[:11]},  # Max 11 characters
            }
        }

        try:
            # Send request
            response = self.session.post(
                self.API_URL,
                json=payload,
                auth=(self.username, self.password),
                timeout=10,
            )

            # Check response
            if response.status_code == 200:
                result = response.json()

                # Check if message was sent successfully (Inforu uses StatusId)
                # StatusId = 1 means success
                status_id = result.get("StatusId", 0)

                if status_id == 1:
                    # Get message ID from Data.CustomerMessageID
                    message_id = ""
                    if "Data" in result and result["Data"]:
                        message_id = result["Data"].get("CustomerMessageID", "")

                    logger.info(f"SMS sent successfully to {phone} (ID: {message_id})")

                    return SMSResponse(
                        success=True, message_id=message_id, status_code=200
                    )
                else:
                    error_msg = result.get("StatusDescription", "Unknown error")
                    logger.error(f"SMS failed: {error_msg}")

                    return SMSResponse(
                        success=False, error=error_msg, status_code=200
                    )
            else:
                logger.error(f"HTTP Error: {response.status_code}")
                return SMSResponse(
                    success=False,
                    error=f"HTTP {response.status_code}",
                    status_code=response.status_code,
                )

        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return SMSResponse(success=False, error="Request timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return SMSResponse(success=False, error=str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return SMSResponse(success=False, error=str(e))

    def send_otp(self, phone: str, otp_code: str) -> SMSResponse:
        """
        Send OTP code via SMS.

        Args:
            phone: Recipient phone number
            otp_code: 4-6 digit OTP code

        Returns:
            SMSResponse with result
        """
        message = MessageFormatter.format_otp_sms(otp_code)
        logger.info(f"Sending OTP to {phone}")
        return self.send_sms(phone, message)

    def send_confirmation(self, phone: str, cart_number: int) -> SMSResponse:
        """
        Send cart assignment confirmation.

        Args:
            phone: Recipient phone number
            cart_number: Assigned cart number

        Returns:
            SMSResponse with result
        """
        message = MessageFormatter.format_confirmation_sms(cart_number)
        logger.info(f"Sending confirmation to {phone}")
        return self.send_sms(phone, message)

    def send_return_reminder(self, phone: str, cart_number: int) -> SMSResponse:
        """
        Send cart return reminder.

        Args:
            phone: Recipient phone number
            cart_number: Cart number

        Returns:
            SMSResponse with result
        """
        message = MessageFormatter.format_reminder_sms(cart_number)
        logger.info(f"Sending return reminder to {phone}")
        return self.send_sms(phone, message)
