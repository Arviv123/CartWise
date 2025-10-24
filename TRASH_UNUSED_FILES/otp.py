"""
OTP (One-Time Password) Module
===============================

Handles OTP generation, storage, and validation.

Features:
- Generate random OTP codes
- Store OTP with expiration
- Validate OTP codes
- Auto-cleanup expired codes

Author: CartWise Team
Version: 1.0.0
"""

import random
import string
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OTPEntry:
    """OTP entry with metadata"""
    code: str
    phone: str
    created_at: datetime
    expires_at: datetime
    attempts: int = 0
    max_attempts: int = 3


class OTPManager:
    """
    Manages OTP generation and validation.

    Features:
    - Time-based expiration
    - Attempt limiting
    - Auto-cleanup
    """

    def __init__(self, code_length: int = 4, expiration_minutes: int = 5):
        """
        Initialize OTP manager.

        Args:
            code_length: Length of OTP code (default: 4)
            expiration_minutes: OTP validity duration (default: 5)
        """
        self.code_length = code_length
        self.expiration_minutes = expiration_minutes
        self.otp_storage: Dict[str, OTPEntry] = {}

        logger.info(f"OTP Manager initialized (length={code_length}, expiry={expiration_minutes}min)")

    def generate_otp(self, phone: str) -> str:
        """
        Generate a new OTP code.

        Args:
            phone: Phone number to associate with OTP

        Returns:
            Generated OTP code
        """
        # Generate random numeric code
        code = ''.join(random.choices(string.digits, k=self.code_length))

        # Create OTP entry
        now = datetime.now()
        entry = OTPEntry(
            code=code,
            phone=phone,
            created_at=now,
            expires_at=now + timedelta(minutes=self.expiration_minutes)
        )

        # Store OTP (overwrite if exists)
        self.otp_storage[phone] = entry

        logger.info(f"🔐 Generated OTP for {phone}: {code} (expires in {self.expiration_minutes}min)")

        # Cleanup expired OTPs
        self._cleanup_expired()

        return code

    def validate_otp(self, phone: str, code: str) -> bool:
        """
        Validate an OTP code.

        Args:
            phone: Phone number
            code: OTP code to validate

        Returns:
            True if valid, False otherwise
        """
        logger.info(f"🔍 Validating OTP for {phone}")

        # Check if OTP exists
        if phone not in self.otp_storage:
            logger.warning(f"❌ No OTP found for {phone}")
            return False

        entry = self.otp_storage[phone]

        # Check if expired
        if datetime.now() > entry.expires_at:
            logger.warning(f"❌ OTP expired for {phone}")
            del self.otp_storage[phone]
            return False

        # Check attempts
        if entry.attempts >= entry.max_attempts:
            logger.warning(f"❌ Max attempts exceeded for {phone}")
            del self.otp_storage[phone]
            return False

        # Increment attempts
        entry.attempts += 1

        # Validate code
        if entry.code == code:
            logger.info(f"✅ OTP verified for {phone}")
            # Remove OTP after successful validation
            del self.otp_storage[phone]
            return True
        else:
            logger.warning(f"❌ Invalid OTP for {phone} (attempt {entry.attempts}/{entry.max_attempts})")
            return False

    def get_remaining_time(self, phone: str) -> Optional[int]:
        """
        Get remaining validity time in seconds.

        Args:
            phone: Phone number

        Returns:
            Remaining seconds or None if not found
        """
        if phone not in self.otp_storage:
            return None

        entry = self.otp_storage[phone]
        remaining = (entry.expires_at - datetime.now()).total_seconds()

        return int(max(0, remaining))

    def revoke_otp(self, phone: str) -> bool:
        """
        Revoke (delete) an OTP.

        Args:
            phone: Phone number

        Returns:
            True if OTP was found and deleted
        """
        if phone in self.otp_storage:
            del self.otp_storage[phone]
            logger.info(f"🗑️  OTP revoked for {phone}")
            return True

        return False

    def _cleanup_expired(self):
        """Remove all expired OTPs."""
        now = datetime.now()
        expired_phones = [
            phone for phone, entry in self.otp_storage.items()
            if now > entry.expires_at
        ]

        for phone in expired_phones:
            del self.otp_storage[phone]

        if expired_phones:
            logger.debug(f"🧹 Cleaned up {len(expired_phones)} expired OTPs")

    def get_stats(self) -> Dict:
        """
        Get OTP manager statistics.

        Returns:
            Statistics dict
        """
        self._cleanup_expired()

        return {
            "active_otps": len(self.otp_storage),
            "code_length": self.code_length,
            "expiration_minutes": self.expiration_minutes
        }


# Example usage
if __name__ == "__main__":
    # Create OTP manager
    otp_manager = OTPManager(code_length=4, expiration_minutes=5)

    # Generate OTP
    phone = "0501234567"
    code = otp_manager.generate_otp(phone)
    print(f"Generated OTP: {code}")

    # Validate OTP
    is_valid = otp_manager.validate_otp(phone, code)
    print(f"OTP valid: {is_valid}")

    # Check remaining time
    remaining = otp_manager.get_remaining_time(phone)
    if remaining:
        print(f"Time remaining: {remaining} seconds")

    # Get stats
    stats = otp_manager.get_stats()
    print(f"Stats: {stats}")
