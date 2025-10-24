"""
Authentication Token Manager
=============================

Manages user authentication tokens after OTP verification.

Author: CartWise Team
Version: 1.0.0
"""

import secrets
import time
from typing import Optional, Dict
from datetime import datetime, timedelta

from core import get_logger

logger = get_logger(__name__)


class AuthTokenManager:
    """
    Manages authentication tokens for verified users.

    After a user verifies OTP once, they receive a token that's valid
    for a configurable period (default: 30 days).
    """

    def __init__(self, token_expiry_days: int = 30):
        """
        Initialize token manager.

        Args:
            token_expiry_days: How long tokens remain valid (default: 30 days)
        """
        self.token_expiry_days = token_expiry_days

        # Store tokens: {token: {phone: str, expires_at: datetime}}
        self._tokens: Dict[str, dict] = {}

        # Store phone to token mapping for quick lookup
        self._phone_to_token: Dict[str, str] = {}

        logger.info(f"Auth Token Manager initialized (expiry: {token_expiry_days} days)")

    def generate_token(self, phone: str) -> str:
        """
        Generate a new authentication token for a phone number.

        Args:
            phone: User phone number

        Returns:
            Authentication token (32 character hex string)
        """
        # Clean up any existing token for this phone
        if phone in self._phone_to_token:
            old_token = self._phone_to_token[phone]
            del self._tokens[old_token]

        # Generate secure random token
        token = secrets.token_hex(32)

        expires_at = datetime.now() + timedelta(days=self.token_expiry_days)

        self._tokens[token] = {
            "phone": phone,
            "expires_at": expires_at,
            "created_at": datetime.now()
        }

        self._phone_to_token[phone] = token

        logger.info(f"Generated auth token for {phone} (expires: {expires_at.strftime('%Y-%m-%d %H:%M')})")

        return token

    def validate_token(self, token: str) -> Optional[str]:
        """
        Validate an authentication token.

        Args:
            token: Authentication token to validate

        Returns:
            Phone number if valid, None if invalid/expired
        """
        if token not in self._tokens:
            logger.debug(f"Token not found: {token[:16]}...")
            return None

        token_data = self._tokens[token]

        # Check if expired
        if datetime.now() > token_data["expires_at"]:
            logger.info(f"Token expired for {token_data['phone']}")
            self._remove_token(token)
            return None

        phone = token_data["phone"]
        logger.debug(f"Token validated for {phone}")

        return phone

    def get_token_by_phone(self, phone: str) -> Optional[str]:
        """
        Get the current valid token for a phone number.

        Args:
            phone: User phone number

        Returns:
            Token if exists and valid, None otherwise
        """
        if phone not in self._phone_to_token:
            return None

        token = self._phone_to_token[phone]

        # Validate token is still valid
        validated_phone = self.validate_token(token)

        if validated_phone:
            return token
        else:
            return None

    def is_authenticated(self, phone: str) -> bool:
        """
        Check if a phone number has a valid authentication token.

        Args:
            phone: User phone number

        Returns:
            True if authenticated, False otherwise
        """
        return self.get_token_by_phone(phone) is not None

    def revoke_token(self, token: str) -> bool:
        """
        Revoke (logout) an authentication token.

        Args:
            token: Token to revoke

        Returns:
            True if revoked, False if token not found
        """
        if token not in self._tokens:
            return False

        phone = self._tokens[token]["phone"]
        self._remove_token(token)

        logger.info(f"Token revoked for {phone}")

        return True

    def revoke_phone(self, phone: str) -> bool:
        """
        Revoke all tokens for a phone number.

        Args:
            phone: Phone number to revoke

        Returns:
            True if revoked, False if no tokens found
        """
        if phone not in self._phone_to_token:
            return False

        token = self._phone_to_token[phone]
        self._remove_token(token)

        logger.info(f"All tokens revoked for {phone}")

        return True

    def _remove_token(self, token: str):
        """Remove a token and its phone mapping."""
        if token in self._tokens:
            phone = self._tokens[token]["phone"]
            del self._tokens[token]

            if phone in self._phone_to_token:
                del self._phone_to_token[phone]

    def cleanup_expired(self):
        """
        Clean up expired tokens.

        Should be called periodically to free memory.
        """
        now = datetime.now()
        expired_tokens = []

        for token, data in self._tokens.items():
            if now > data["expires_at"]:
                expired_tokens.append(token)

        for token in expired_tokens:
            self._remove_token(token)

        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")

    def get_stats(self) -> dict:
        """
        Get statistics about active tokens.

        Returns:
            Dictionary with token statistics
        """
        self.cleanup_expired()

        return {
            "active_tokens": len(self._tokens),
            "authenticated_users": len(self._phone_to_token)
        }
