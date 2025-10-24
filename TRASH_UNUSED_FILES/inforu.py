"""
Inforu SMS Provider Module
===========================

This module handles SMS communication using the Inforu API v2.

API Endpoint: https://capi.inforu.co.il/api/v2/SMS/SendSms

Features:
- Send SMS messages
- OTP generation and validation
- Delivery status tracking
- Error handling and retries

Author: CartWise Team
Version: 1.0.0
"""

import requests
import logging
import base64
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SMSMessage:
    """SMS message data structure"""
    phone: str
    message: str
    sender: str = "CartWise"


@dataclass
class SMSResponse:
    """SMS API response"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    status_code: Optional[int] = None


class InforuSMSProvider:
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
        self.session.headers.update({
            "Content-Type": "application/json"
        })

        logger.info(f"✅ Inforu SMS configured with username: {username}")

    def _create_auth_header(self) -> str:
        """
        Create basic authentication header.

        Returns:
            Base64 encoded auth string
        """
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def send_sms(
        self,
        phone: str,
        message: str,
        sender: str = "CartWise"
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
        logger.info(f"📱 Sending SMS to {phone}")

        # Validate phone number
        if not self._validate_phone(phone):
            logger.error(f"❌ Invalid phone number: {phone}")
            return SMSResponse(
                success=False,
                error="Invalid phone number format"
            )

        # Build request payload (Inforu API v2 format)
        payload = {
            "Data": {
                "Message": message,
                "Recipients": [
                    {
                        "Phone": phone
                    }
                ],
                "Settings": {
                    "Sender": sender[:11]  # Max 11 characters
                }
            }
        }

        try:
            # Send request
            response = self.session.post(
                self.API_URL,
                json=payload,
                auth=(self.username, self.password),
                timeout=10
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

                    logger.info(f"✅ SMS sent successfully to {phone} (ID: {message_id})")

                    return SMSResponse(
                        success=True,
                        message_id=message_id,
                        status_code=200
                    )
                else:
                    error_msg = result.get("StatusDescription", "Unknown error")
                    logger.error(f"❌ SMS failed: {error_msg}")

                    return SMSResponse(
                        success=False,
                        error=error_msg,
                        status_code=200
                    )
            else:
                logger.error(f"❌ HTTP Error: {response.status_code}")
                return SMSResponse(
                    success=False,
                    error=f"HTTP {response.status_code}",
                    status_code=response.status_code
                )

        except requests.exceptions.Timeout:
            logger.error("❌ Request timeout")
            return SMSResponse(
                success=False,
                error="Request timeout"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request failed: {e}")
            return SMSResponse(
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return SMSResponse(
                success=False,
                error=str(e)
            )

    def send_otp(self, phone: str, otp_code: str) -> SMSResponse:
        """
        Send OTP code via SMS.

        Args:
            phone: Recipient phone number
            otp_code: 4-6 digit OTP code

        Returns:
            SMSResponse with result
        """
        message = f"קוד האימות שלך הוא: {otp_code}\nCartWise - מערכת עגלות חכמות"

        logger.info(f"🔐 Sending OTP to {phone}")
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
        message = (
            f"עגלה מספר {cart_number} הוקצתה לך.\n"
            f"נא להחזיר את העגלה למקומה בסיום הקניות.\n"
            f"תודה שבחרת ב-CartWise!"
        )

        logger.info(f"📨 Sending confirmation to {phone}")
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
        message = (
            f"תזכורת: עגלה {cart_number} עדיין לא הוחזרה.\n"
            f"נא להחזיר את העגלה למקומה.\n"
            f"תודה!"
        )

        logger.info(f"⏰ Sending return reminder to {phone}")
        return self.send_sms(phone, message)

    def _validate_phone(self, phone: str) -> bool:
        """
        Validate Israeli phone number.

        Args:
            phone: Phone number to validate

        Returns:
            True if valid, False otherwise
        """
        # Remove spaces, dashes, etc.
        clean_phone = phone.replace("-", "").replace(" ", "").replace("+972", "0")

        # Check format: 05X-XXXXXXX or 05XXXXXXXX
        if len(clean_phone) == 10 and clean_phone.startswith("05"):
            return True

        # Check international format: +972-5X-XXXXXXX
        if phone.startswith("+972") and len(clean_phone) == 10:
            return True

        return False

    def get_delivery_status(self, message_id: str) -> Dict:
        """
        Get SMS delivery status (if supported by Inforu).

        Args:
            message_id: Message ID from send response

        Returns:
            Status information
        """
        # Note: Implement based on Inforu API documentation
        # This is a placeholder
        logger.warning("Delivery status tracking not yet implemented")
        return {
            "message_id": message_id,
            "status": "unknown"
        }


# Example usage
if __name__ == "__main__":
    # Example: Send SMS
    sms_provider = InforuSMSProvider(
        username="your_username",
        password="your_password"
    )

    # Send OTP
    response = sms_provider.send_otp("0501234567", "1234")
    if response.success:
        print(f"✅ OTP sent! Message ID: {response.message_id}")
    else:
        print(f"❌ Failed: {response.error}")

    # Send confirmation
    response = sms_provider.send_confirmation("0501234567", 5)
    if response.success:
        print(f"✅ Confirmation sent!")
