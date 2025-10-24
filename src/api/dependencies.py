"""
API Dependencies
================

Dependency injection for FastAPI routes.

Author: CartWise Team
Version: 1.0.0
"""

from typing import Dict, Optional
from core import settings, get_logger
from utils import OTPManager, RentalDatabase
from utils.auth_tokens import AuthTokenManager
from providers.sms import InforuSMSProvider
from hardware.rs485 import RS485Controller
from hardware.cu16_monitor import CU16MonitorSync
from models import Cart, CartStatus

logger = get_logger(__name__)

# Global instances (singletons)
_otp_manager: Optional[OTPManager] = None
_sms_provider: Optional[InforuSMSProvider] = None
_lock_controller: Optional[RS485Controller] = None
_carts_db: Optional[Dict[int, Cart]] = None
_rental_db: Optional[RentalDatabase] = None
_monitor: Optional[CU16MonitorSync] = None
_auth_token_manager: Optional[AuthTokenManager] = None


def get_otp_manager() -> OTPManager:
    """Get OTP manager instance."""
    global _otp_manager
    if _otp_manager is None:
        _otp_manager = OTPManager(
            code_length=settings.OTP_LENGTH,
            expiration_minutes=settings.OTP_EXPIRATION_MINUTES,
        )
    return _otp_manager


def get_sms_provider() -> InforuSMSProvider:
    """Get SMS provider instance."""
    global _sms_provider
    if _sms_provider is None:
        _sms_provider = InforuSMSProvider(
            username=settings.INFORU_USERNAME, password=settings.INFORU_PASSWORD
        )
    return _sms_provider


def get_lock_controller() -> Optional[RS485Controller]:
    """Get RS485 lock controller instance."""
    global _lock_controller
    return _lock_controller


def set_lock_controller(controller: Optional[RS485Controller]):
    """Set RS485 lock controller instance."""
    global _lock_controller
    _lock_controller = controller


def get_carts_db() -> Dict[int, Cart]:
    """Get carts database."""
    global _carts_db
    if _carts_db is None:
        # Initialize with default carts
        # Note: locker_id starts from 0 (locker #1 = ADDR 0x00 in KR-CU16 protocol)
        _carts_db = {
            1: Cart(cart_id=1, locker_id=0, status=CartStatus.AVAILABLE, is_locked=True),
            2: Cart(cart_id=2, locker_id=1, status=CartStatus.AVAILABLE, is_locked=True),
            3: Cart(cart_id=3, locker_id=2, status=CartStatus.AVAILABLE, is_locked=True),
            4: Cart(cart_id=4, locker_id=3, status=CartStatus.AVAILABLE, is_locked=True),
            5: Cart(cart_id=5, locker_id=4, status=CartStatus.AVAILABLE, is_locked=True),
        }
        logger.info(f"Initialized {len(_carts_db)} carts in database")
    return _carts_db


def get_rental_db() -> RentalDatabase:
    """Get rental database instance."""
    global _rental_db
    if _rental_db is None:
        _rental_db = RentalDatabase()
        logger.info("Rental database initialized")
    return _rental_db


def get_monitor() -> Optional[CU16MonitorSync]:
    """Get CU16 monitor instance."""
    global _monitor
    return _monitor


def init_monitor():
    """Initialize and start the CU16 monitor service."""
    global _monitor

    if _monitor is not None:
        logger.warning("Monitor already initialized")
        return

    lock_controller = get_lock_controller()
    rental_db = get_rental_db()
    carts_db = get_carts_db()

    _monitor = CU16MonitorSync(
        lock_controller=lock_controller,
        rental_db=rental_db,
        carts_db=carts_db,
        check_interval=5  # Check every 5 seconds
    )

    _monitor.start()
    logger.info("CU16 monitor service started")


def shutdown_monitor():
    """Shutdown the CU16 monitor service."""
    global _monitor
    if _monitor:
        _monitor.stop()
        _monitor = None
        logger.info("CU16 monitor service stopped")


def get_auth_token_manager() -> AuthTokenManager:
    """Get authentication token manager instance."""
    global _auth_token_manager
    if _auth_token_manager is None:
        _auth_token_manager = AuthTokenManager(token_expiry_days=30)
        logger.info("Auth token manager initialized")
    return _auth_token_manager
