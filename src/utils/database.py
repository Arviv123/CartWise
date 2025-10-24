"""
Database Manager
================

SQLite database manager for cart rental history.

Author: CartWise Team
Version: 1.0.0
"""

import sqlite3
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from core import get_logger
from models.rental import Rental, RentalStatus

logger = get_logger(__name__)


class RentalDatabase:
    """
    SQLite database manager for rental records.

    Handles all database operations for rental tracking including:
    - Creating and managing rentals
    - Querying rental history
    - Updating rental status
    - Finding late/overdue rentals
    """

    def __init__(self, db_path: str = "data/rentals.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_data_directory()
        self._init_database()

    def _ensure_data_directory(self):
        """Ensure data directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create rentals table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rentals (
                        rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cart_id INTEGER NOT NULL,
                        user_phone TEXT NOT NULL,
                        locker_id INTEGER NOT NULL,
                        start_time TEXT NOT NULL,
                        expected_return TEXT NOT NULL,
                        actual_return TEXT,
                        status TEXT NOT NULL,
                        notes TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create indexes for faster queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_phone
                    ON rentals(user_phone)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_status
                    ON rentals(status)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cart_id
                    ON rentals(cart_id)
                """)

                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def create_rental(self, rental: Rental) -> int:
        """
        Create a new rental record.

        Args:
            rental: Rental object to create

        Returns:
            rental_id: ID of created rental

        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO rentals (
                        cart_id, user_phone, locker_id,
                        start_time, expected_return, actual_return,
                        status, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rental.cart_id,
                    rental.user_phone,
                    rental.locker_id,
                    rental.start_time.isoformat(),
                    rental.expected_return.isoformat(),
                    rental.actual_return.isoformat() if rental.actual_return else None,
                    rental.status.value,
                    rental.notes
                ))

                rental_id = cursor.lastrowid
                conn.commit()

                logger.info(f"Created rental {rental_id} for cart {rental.cart_id} by {rental.user_phone}")
                return rental_id

        except sqlite3.Error as e:
            logger.error(f"Error creating rental: {e}")
            raise

    def get_rental(self, rental_id: int) -> Optional[Rental]:
        """
        Get rental by ID.

        Args:
            rental_id: Rental ID

        Returns:
            Rental object or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM rentals WHERE rental_id = ?", (rental_id,))
                row = cursor.fetchone()

                if row:
                    return self._row_to_rental(row)
                return None

        except sqlite3.Error as e:
            logger.error(f"Error getting rental {rental_id}: {e}")
            return None

    def get_active_rental_by_phone(self, phone: str) -> Optional[Rental]:
        """
        Get active rental for a user.

        Args:
            phone: User phone number

        Returns:
            Active rental or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM rentals
                    WHERE user_phone = ? AND status = ?
                    ORDER BY start_time DESC
                    LIMIT 1
                """, (phone, RentalStatus.ACTIVE.value))

                row = cursor.fetchone()

                if row:
                    return self._row_to_rental(row)
                return None

        except sqlite3.Error as e:
            logger.error(f"Error getting active rental for {phone}: {e}")
            return None

    def get_active_rental_by_cart(self, cart_id: int) -> Optional[Rental]:
        """
        Get active rental for a cart.

        Args:
            cart_id: Cart ID

        Returns:
            Active rental or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM rentals
                    WHERE cart_id = ? AND status = ?
                    ORDER BY start_time DESC
                    LIMIT 1
                """, (cart_id, RentalStatus.ACTIVE.value))

                row = cursor.fetchone()

                if row:
                    return self._row_to_rental(row)
                return None

        except sqlite3.Error as e:
            logger.error(f"Error getting active rental for cart {cart_id}: {e}")
            return None

    def update_rental(self, rental: Rental) -> bool:
        """
        Update existing rental.

        Args:
            rental: Rental object with updated data

        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE rentals SET
                        cart_id = ?,
                        user_phone = ?,
                        locker_id = ?,
                        start_time = ?,
                        expected_return = ?,
                        actual_return = ?,
                        status = ?,
                        notes = ?
                    WHERE rental_id = ?
                """, (
                    rental.cart_id,
                    rental.user_phone,
                    rental.locker_id,
                    rental.start_time.isoformat(),
                    rental.expected_return.isoformat(),
                    rental.actual_return.isoformat() if rental.actual_return else None,
                    rental.status.value,
                    rental.notes,
                    rental.rental_id
                ))

                conn.commit()
                logger.debug(f"Updated rental {rental.rental_id}")
                return True

        except sqlite3.Error as e:
            logger.error(f"Error updating rental {rental.rental_id}: {e}")
            return False

    def get_rental_history(self, phone: Optional[str] = None, limit: int = 100) -> List[Rental]:
        """
        Get rental history.

        Args:
            phone: Optional phone number to filter by
            limit: Maximum number of records to return

        Returns:
            List of rentals
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if phone:
                    cursor.execute("""
                        SELECT * FROM rentals
                        WHERE user_phone = ?
                        ORDER BY start_time DESC
                        LIMIT ?
                    """, (phone, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM rentals
                        ORDER BY start_time DESC
                        LIMIT ?
                    """, (limit,))

                rows = cursor.fetchall()
                return [self._row_to_rental(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error getting rental history: {e}")
            return []

    def get_overdue_rentals(self) -> List[Rental]:
        """
        Get all overdue rentals (active but past expected return).

        Returns:
            List of overdue rentals
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                now = datetime.now().isoformat()
                cursor.execute("""
                    SELECT * FROM rentals
                    WHERE status = ? AND expected_return < ?
                    ORDER BY expected_return ASC
                """, (RentalStatus.ACTIVE.value, now))

                rows = cursor.fetchall()
                return [self._row_to_rental(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error getting overdue rentals: {e}")
            return []

    def get_statistics(self) -> dict:
        """
        Get rental statistics.

        Returns:
            Dictionary with statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total rentals
                cursor.execute("SELECT COUNT(*) FROM rentals")
                total = cursor.fetchone()[0]

                # Active rentals
                cursor.execute("SELECT COUNT(*) FROM rentals WHERE status = ?",
                             (RentalStatus.ACTIVE.value,))
                active = cursor.fetchone()[0]

                # Overdue rentals
                now = datetime.now().isoformat()
                cursor.execute("""
                    SELECT COUNT(*) FROM rentals
                    WHERE status = ? AND expected_return < ?
                """, (RentalStatus.ACTIVE.value, now))
                overdue = cursor.fetchone()[0]

                # Late returns
                cursor.execute("SELECT COUNT(*) FROM rentals WHERE status = ?",
                             (RentalStatus.RETURNED_LATE.value,))
                late_returns = cursor.fetchone()[0]

                return {
                    "total_rentals": total,
                    "active_rentals": active,
                    "overdue_rentals": overdue,
                    "late_returns": late_returns
                }

        except sqlite3.Error as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    def _row_to_rental(self, row: sqlite3.Row) -> Rental:
        """
        Convert database row to Rental object.

        Args:
            row: SQLite row

        Returns:
            Rental object
        """
        return Rental(
            rental_id=row["rental_id"],
            cart_id=row["cart_id"],
            user_phone=row["user_phone"],
            locker_id=row["locker_id"],
            start_time=datetime.fromisoformat(row["start_time"]),
            expected_return=datetime.fromisoformat(row["expected_return"]),
            actual_return=datetime.fromisoformat(row["actual_return"]) if row["actual_return"] else None,
            status=RentalStatus(row["status"]),
            notes=row["notes"]
        )

    def close(self):
        """Close database connection."""
        logger.info("Database connection closed")
