"""
RS485 Controller Module
========================

This module handles communication with the cart lock controller via RS485.

Protocol Specification:
- Baud Rate: 9600
- Data Bits: 8
- Stop Bits: 1
- Parity: None

Message Format:
[STX] [CMD] [LOCKER_ID] [DATA] [CRC] [ETX]

Commands:
- 0x30: Lock
- 0x31: Unlock
- 0x32: Status Query
- 0x33: Micro-Switch Status

Author: CartWise Team
Version: 1.0.0
"""

import serial
import logging
from typing import Optional, Dict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(Enum):
    """Lock controller commands"""
    LOCK = 0x30
    UNLOCK = 0x31
    STATUS = 0x32
    MICROSWITCH = 0x33


class LockStatus(Enum):
    """Lock status states"""
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    UNKNOWN = "unknown"
    ERROR = "error"


class RS485Controller:
    """
    RS485 Controller for cart lock management.

    Features:
    - Lock/Unlock individual carts
    - Query cart status
    - Detect cart return via micro-switch
    - CRC checksum validation
    """

    # Protocol bytes
    STX = 0x02  # Start of Text
    ETX = 0x03  # End of Text

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600, timeout: float = 1.0):
        """
        Initialize RS485 controller.

        Args:
            port: Serial port path
            baudrate: Communication speed
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None

        logger.info(f"Initializing RS485 Controller on {port} @ {baudrate} baud")

    def connect(self) -> bool:
        """
        Establish connection to the controller.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            logger.info(f"✅ Connected to RS485 controller on {self.port}")
            return True

        except serial.SerialException as e:
            logger.error(f"❌ Failed to connect to {self.port}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to RS485: {e}")
            return False

    def disconnect(self):
        """Close the serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info("RS485 connection closed")

    def _calculate_crc(self, data: bytes) -> int:
        """
        Calculate CRC checksum.

        Args:
            data: Bytes to calculate CRC for

        Returns:
            CRC checksum value
        """
        crc = 0
        for byte in data:
            crc ^= byte
        return crc & 0xFF

    def _build_message(self, command: Command, locker_id: int, data: bytes = b'') -> bytes:
        """
        Build a protocol message.

        Args:
            command: Command to send
            locker_id: Locker ID (1-255)
            data: Additional data bytes

        Returns:
            Complete message bytes
        """
        # Build message body
        body = bytes([command.value, locker_id]) + data

        # Calculate CRC
        crc = self._calculate_crc(body)

        # Build complete message
        message = bytes([self.STX]) + body + bytes([crc, self.ETX])

        logger.debug(f"Built message: {message.hex()}")
        return message

    def _send_command(self, message: bytes) -> Optional[bytes]:
        """
        Send command and wait for response.

        Args:
            message: Message to send

        Returns:
            Response bytes or None if error
        """
        if not self.serial or not self.serial.is_open:
            logger.error("Serial port not connected")
            return None

        try:
            # Send message
            self.serial.write(message)
            self.serial.flush()
            logger.debug(f"Sent: {message.hex()}")

            # Wait for response
            response = self.serial.read(10)  # Read up to 10 bytes
            logger.debug(f"Received: {response.hex() if response else 'None'}")

            return response if response else None

        except serial.SerialException as e:
            logger.error(f"Serial communication error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error sending command: {e}")
            return None

    def unlock_cart(self, locker_id: int) -> bool:
        """
        Unlock a cart.

        Args:
            locker_id: Cart/locker ID (1-255)

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"🔓 Unlocking cart {locker_id}")

        message = self._build_message(Command.UNLOCK, locker_id)
        response = self._send_command(message)

        if response and len(response) > 0:
            # Check if response indicates success (customize based on your protocol)
            if response[0] == self.STX and response[-1] == self.ETX:
                logger.info(f"✅ Cart {locker_id} unlocked successfully")
                return True

        logger.error(f"❌ Failed to unlock cart {locker_id}")
        return False

    def lock_cart(self, locker_id: int) -> bool:
        """
        Lock a cart.

        Args:
            locker_id: Cart/locker ID (1-255)

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"🔒 Locking cart {locker_id}")

        message = self._build_message(Command.LOCK, locker_id)
        response = self._send_command(message)

        if response and len(response) > 0:
            if response[0] == self.STX and response[-1] == self.ETX:
                logger.info(f"✅ Cart {locker_id} locked successfully")
                return True

        logger.error(f"❌ Failed to lock cart {locker_id}")
        return False

    def get_lock_status(self, locker_id: int) -> LockStatus:
        """
        Query lock status.

        Args:
            locker_id: Cart/locker ID (1-255)

        Returns:
            Lock status
        """
        logger.debug(f"Querying status of cart {locker_id}")

        message = self._build_message(Command.STATUS, locker_id)
        response = self._send_command(message)

        if not response or len(response) < 4:
            return LockStatus.UNKNOWN

        # Parse response (customize based on your protocol)
        # Example: response[2] contains status byte
        # 0x01 = locked, 0x00 = unlocked
        if len(response) >= 4:
            status_byte = response[2]
            if status_byte == 0x01:
                return LockStatus.LOCKED
            elif status_byte == 0x00:
                return LockStatus.UNLOCKED

        return LockStatus.UNKNOWN

    def check_cart_returned(self, locker_id: int) -> bool:
        """
        Check if cart was returned (micro-switch pressed).

        Args:
            locker_id: Cart/locker ID (1-255)

        Returns:
            True if cart is returned, False otherwise
        """
        logger.debug(f"Checking if cart {locker_id} is returned")

        message = self._build_message(Command.MICROSWITCH, locker_id)
        response = self._send_command(message)

        if not response or len(response) < 4:
            return False

        # Parse micro-switch status
        # Example: response[2] = 0x01 means switch pressed (cart returned)
        if len(response) >= 4:
            switch_status = response[2]
            is_returned = (switch_status == 0x01)

            if is_returned:
                logger.info(f"✅ Cart {locker_id} detected as returned (micro-switch pressed)")

            return is_returned

        return False

    def auto_lock_on_return(self, locker_id: int) -> bool:
        """
        Auto-lock cart when returned (detected by micro-switch).

        Args:
            locker_id: Cart/locker ID (1-255)

        Returns:
            True if cart was returned and locked, False otherwise
        """
        if self.check_cart_returned(locker_id):
            logger.info(f"🔄 Cart {locker_id} returned, auto-locking...")
            return self.lock_cart(locker_id)

        return False

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Example usage
if __name__ == "__main__":
    # Example: Using the controller
    with RS485Controller(port="/dev/ttyUSB0", baudrate=9600) as controller:
        # Unlock cart 1
        if controller.unlock_cart(1):
            print("Cart 1 unlocked!")

        # Check status
        status = controller.get_lock_status(1)
        print(f"Cart 1 status: {status.value}")

        # Check if returned
        if controller.check_cart_returned(1):
            print("Cart 1 has been returned!")
            controller.lock_cart(1)
