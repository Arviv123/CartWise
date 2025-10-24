"""
CU16 Lock Monitor Service
==========================

Background service that monitors KR-CU16 lock controller for cart returns.

This service:
- Runs continuously in background
- Checks lock status every N seconds
- Detects when carts are returned (lock closed + cart inside)
- Updates rental status automatically
- Marks overdue rentals

Author: CartWise Team
Version: 1.0.0
"""

import asyncio
import time
from datetime import datetime
from typing import Optional, Dict

from core import get_logger
from hardware.rs485 import RS485Controller, LockStateData
from utils.database import RentalDatabase
from models import Cart, CartStatus
from models.rental import RentalStatus

logger = get_logger(__name__)


class CU16Monitor:
    """
    Background monitor for KR-CU16 lock controller.

    Continuously monitors lock states and detects:
    - Cart returns (lock closed + infrared detection)
    - Overdue rentals
    - Lock status changes
    """

    def __init__(
        self,
        lock_controller: Optional[RS485Controller],
        rental_db: RentalDatabase,
        carts_db: Dict[int, Cart],
        check_interval: int = 5
    ):
        """
        Initialize monitor service.

        Args:
            lock_controller: RS485 controller for lock communication
            rental_db: Rental database instance
            carts_db: In-memory carts database
            check_interval: Check interval in seconds (default: 5)
        """
        self.lock_controller = lock_controller
        self.rental_db = rental_db
        self.carts_db = carts_db
        self.check_interval = check_interval
        self.running = False
        self._task: Optional[asyncio.Task] = None

        logger.info(f"CU16 Monitor initialized (check interval: {check_interval}s)")

    async def start(self):
        """Start the monitor service in background."""
        if self.running:
            logger.warning("Monitor already running")
            return

        self.running = True
        logger.info("Starting CU16 monitor service...")

        # Start monitoring task
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop(self):
        """Stop the monitor service."""
        if not self.running:
            return

        logger.info("Stopping CU16 monitor service...")
        self.running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("CU16 monitor service stopped")

    async def _monitor_loop(self):
        """Main monitoring loop."""
        logger.info("CU16 monitor loop started")

        while self.running:
            try:
                # Check if controller is available
                if not self.lock_controller:
                    logger.debug("No lock controller available - skipping check")
                    await asyncio.sleep(self.check_interval)
                    continue

                # Get current lock states
                lock_states = self._get_all_lock_states()

                if lock_states:
                    # Check each cart for return
                    await self._check_cart_returns(lock_states)

                    # Check for overdue rentals
                    await self._check_overdue_rentals()

                # Wait before next check
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(self.check_interval)

    def _get_all_lock_states(self) -> Optional[LockStateData]:
        """
        Get state of all locks from controller.

        Returns:
            LockStateData or None if error
        """
        try:
            state = self.lock_controller.get_all_locks_state()
            if state:
                logger.debug("Retrieved lock states from CU16 controller")
            return state

        except Exception as e:
            logger.error(f"Error getting lock states: {e}")
            return None

    async def _check_cart_returns(self, lock_states: LockStateData):
        """
        Check each active cart for return detection.

        Args:
            lock_states: Current lock states from controller
        """
        # Get all active rentals from database
        active_rentals = [
            rental for rental in self.rental_db.get_rental_history(limit=1000)
            if rental.status == RentalStatus.ACTIVE
        ]

        for rental in active_rentals:
            try:
                cart = self.carts_db.get(rental.cart_id)
                if not cart:
                    logger.warning(f"Cart {rental.cart_id} not found in carts_db")
                    continue

                locker_id = cart.locker_id

                # Check if cart is inside and lock is closed
                cart_inside = lock_states.has_cart_inside(locker_id)
                lock_closed = lock_states.is_lock_closed(locker_id)

                if cart_inside and lock_closed:
                    # Cart has been returned!
                    logger.info(f"🎉 Cart {cart.cart_id} returned detected (locker {locker_id})")
                    await self._process_cart_return(rental, cart)

            except Exception as e:
                logger.error(f"Error checking cart {rental.cart_id} return: {e}")

    async def _process_cart_return(self, rental, cart: Cart):
        """
        Process a detected cart return.

        Args:
            rental: Rental record
            cart: Cart object
        """
        # Update rental record
        rental.mark_returned()
        self.rental_db.update_rental(rental)

        # Update cart status
        cart.return_cart()
        cart.mark_available()

        # Log the return
        duration = rental.duration
        is_late = rental.status == RentalStatus.RETURNED_LATE

        logger.info(
            f"✅ Cart {cart.cart_id} returned by {rental.user_phone} "
            f"(duration: {duration}, late: {is_late})"
        )

        if is_late:
            late_by = rental.actual_return - rental.expected_return
            logger.warning(
                f"⚠️  Cart {cart.cart_id} returned LATE by {late_by} "
                f"(expected: {rental.expected_return})"
            )

    async def _check_overdue_rentals(self):
        """Check for overdue rentals and mark them."""
        try:
            overdue_rentals = self.rental_db.get_overdue_rentals()

            for rental in overdue_rentals:
                if rental.status != RentalStatus.OVERDUE:
                    # Mark as overdue
                    rental.mark_overdue()
                    self.rental_db.update_rental(rental)

                    # Update cart status
                    cart = self.carts_db.get(rental.cart_id)
                    if cart:
                        cart.status = CartStatus.IN_USE  # Still in use but overdue

                    overdue_time = datetime.now() - rental.expected_return
                    logger.warning(
                        f"⏰ Cart {rental.cart_id} is OVERDUE by {overdue_time} "
                        f"(user: {rental.user_phone})"
                    )

        except Exception as e:
            logger.error(f"Error checking overdue rentals: {e}")

    def get_monitoring_status(self) -> dict:
        """
        Get current monitoring status.

        Returns:
            Dictionary with monitoring info
        """
        return {
            "running": self.running,
            "check_interval": self.check_interval,
            "controller_connected": self.lock_controller is not None,
            "database_path": self.rental_db.db_path
        }


# Synchronous version for blocking environments
class CU16MonitorSync:
    """
    Synchronous version of CU16 monitor (for testing or non-async environments).

    Same functionality as CU16Monitor but uses threading instead of asyncio.
    """

    def __init__(
        self,
        lock_controller: Optional[RS485Controller],
        rental_db: RentalDatabase,
        carts_db: Dict[int, Cart],
        check_interval: int = 5
    ):
        """
        Initialize synchronous monitor service.

        Args:
            lock_controller: RS485 controller for lock communication
            rental_db: Rental database instance
            carts_db: In-memory carts database
            check_interval: Check interval in seconds
        """
        self.lock_controller = lock_controller
        self.rental_db = rental_db
        self.carts_db = carts_db
        self.check_interval = check_interval
        self.running = False

        logger.info(f"CU16 Monitor (Sync) initialized (check interval: {check_interval}s)")

    def start(self):
        """Start the monitor service in background thread."""
        import threading

        if self.running:
            logger.warning("Monitor already running")
            return

        self.running = True
        logger.info("Starting CU16 monitor service (sync)...")

        # Start monitoring thread
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()

    def stop(self):
        """Stop the monitor service."""
        if not self.running:
            return

        logger.info("Stopping CU16 monitor service...")
        self.running = False

    def _monitor_loop(self):
        """Main monitoring loop (synchronous)."""
        logger.info("CU16 monitor loop started (sync)")

        while self.running:
            try:
                if not self.lock_controller:
                    logger.debug("No lock controller available - skipping check")
                    time.sleep(self.check_interval)
                    continue

                lock_states = self._get_all_lock_states()

                if lock_states:
                    self._check_cart_returns(lock_states)
                    self._check_overdue_rentals()

                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(self.check_interval)

    def _get_all_lock_states(self) -> Optional[LockStateData]:
        """Get state of all locks from controller."""
        try:
            state = self.lock_controller.get_all_locks_state()
            if state:
                logger.debug("Retrieved lock states from CU16 controller")
            return state
        except Exception as e:
            logger.error(f"Error getting lock states: {e}")
            return None

    def _check_cart_returns(self, lock_states: LockStateData):
        """Check each active cart for return detection."""
        active_rentals = [
            rental for rental in self.rental_db.get_rental_history(limit=1000)
            if rental.status == RentalStatus.ACTIVE
        ]

        for rental in active_rentals:
            try:
                cart = self.carts_db.get(rental.cart_id)
                if not cart:
                    continue

                locker_id = cart.locker_id
                cart_inside = lock_states.has_cart_inside(locker_id)
                lock_closed = lock_states.is_lock_closed(locker_id)

                if cart_inside and lock_closed:
                    logger.info(f"🎉 Cart {cart.cart_id} returned detected (locker {locker_id})")
                    self._process_cart_return(rental, cart)

            except Exception as e:
                logger.error(f"Error checking cart {rental.cart_id} return: {e}")

    def _process_cart_return(self, rental, cart: Cart):
        """Process a detected cart return."""
        rental.mark_returned()
        self.rental_db.update_rental(rental)

        cart.return_cart()
        cart.mark_available()

        duration = rental.duration
        is_late = rental.status == RentalStatus.RETURNED_LATE

        logger.info(
            f"✅ Cart {cart.cart_id} returned by {rental.user_phone} "
            f"(duration: {duration}, late: {is_late})"
        )

        if is_late:
            late_by = rental.actual_return - rental.expected_return
            logger.warning(f"⚠️  Cart {cart.cart_id} returned LATE by {late_by}")

    def _check_overdue_rentals(self):
        """Check for overdue rentals and mark them."""
        try:
            overdue_rentals = self.rental_db.get_overdue_rentals()

            for rental in overdue_rentals:
                if rental.status != RentalStatus.OVERDUE:
                    rental.mark_overdue()
                    self.rental_db.update_rental(rental)

                    cart = self.carts_db.get(rental.cart_id)
                    if cart:
                        cart.status = CartStatus.IN_USE

                    overdue_time = datetime.now() - rental.expected_return
                    logger.warning(
                        f"⏰ Cart {rental.cart_id} is OVERDUE by {overdue_time} "
                        f"(user: {rental.user_phone})"
                    )

        except Exception as e:
            logger.error(f"Error checking overdue rentals: {e}")
