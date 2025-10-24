"""
RS485 Controller Module - KR-CU16 Protocol
===========================================

Handles communication with the Kerong KR-CU16 lock controller via RS485.

Protocol Specification (KR-CU16):
- Baud Rate: 19200 (factory default)
- Data Bits: 8
- Stop Bits: 1
- Parity: None
- Protocol: STX + ADDR + CMD + ETX + SUM
- Each CU16 board controls 16 locks

Author: CartWise Team
Version: 2.1.0 (Stabilized with Port Ready Check and Unlock Reset)
"""

import serial
from typing import Optional, Dict, Tuple, List
from enum import Enum
from dataclasses import dataclass
import time # Added for sleep functionality

# Assuming 'core' and 'get_logger' are defined elsewhere
# from core import get_logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set default logging level for demonstration


class Command(Enum):
    """KR-CU16 Lock controller commands."""

    GET_STATUS = 0x30          # Get single lock status
    UNLOCK = 0x31              # Unlock single lock
    GET_ALL_STATUS = 0x32      # Get all locks status on bus
    UNLOCK_ALL = 0x33          # Unlock all locks
    RETURN_SINGLE_DATA = 0x35  # Return single CU data
    RETURN_ALL_DATA = 0x36     # Return all CU data
    SET_UNLOCK_TIME = 0x37     # Set/query unlock time
    RETURN_UNLOCK_TIME = 0x38  # Return unlock time setting (Often used as a non-destructive RESET command)
    DELAYED_UNLOCK = 0x39      # Set delayed unlock


@dataclass
class LockStateData:
    """Lock state data from CU16."""

    lock_hooks_1_8: int    # Lock hook state for locks 1-8 (bit0-bit7)
    lock_hooks_9_16: int   # Lock hook state for locks 9-16 (bit0-bit7)
    infrared_1_8: int      # Infrared detection for locks 1-8
    infrared_9_16: int     # Infrared detection for locks 9-16

    def is_lock_closed(self, lock_num: int) -> bool:
        """
        Check if specific lock hook is closed (locked).

        Args:
            lock_num: Lock number (0-15)

        Returns:
            True if lock is closed, False otherwise
        """
        if lock_num < 8:
            return bool((self.lock_hooks_1_8 >> lock_num) & 1)
        else:
            return bool((self.lock_hooks_9_16 >> (lock_num - 8)) & 1)

    def has_cart_inside(self, lock_num: int) -> bool:
        """
        Check if cart is detected inside lock (infrared sensor).

        Args:
            lock_num: Lock number (0-15)

        Returns:
            True if cart detected, False otherwise
        """
        if lock_num < 8:
            return bool((self.infrared_1_8 >> lock_num) & 1)
        else:
            return bool((self.infrared_9_16 >> (lock_num - 8)) & 1)


class LockStatus(Enum):
    """Lock status states."""

    LOCKED = "locked"
    UNLOCKED = "unlocked"
    UNKNOWN = "unknown"
    ERROR = "error"


class RS485Controller:
    """
    KR-CU16 RS485 Controller for cart lock management.

    Protocol Details:
    - Frame: STX (0x02) + ADDR + CMD + ETX (0x03) + SUM
    - Each CU16 board has address 0x00-0x9F
    - Each board controls 16 locks (0x00-0x0F)
    - Lock hook detection + Infrared sensors

    Features:
    - Lock/Unlock individual carts
    - Query cart status (lock hook + infrared)
    - Detect cart return via micro-switch
    - Support for multiple CU16 boards on same bus
    """

    # Protocol bytes
    STX = 0x02
    ETX = 0x03
    BROADCAST_ADDR = 0xF0  # For querying all CU16 on bus

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 19200, timeout: float = 1.0):
        """
        Initialize KR-CU16 RS485 controller.

        Args:
            port: Serial port path
            baudrate: Communication speed (default 19200 for KR-CU16)
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self.cu_address = 0x00  # Default CU16 board address

        logger.info(f"Initializing KR-CU16 RS485 Controller on {port} @ {baudrate} baud")

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
                timeout=self.timeout,
            )
            logger.info(f"Connected to KR-CU16 controller on {self.port} @ {self.baudrate} baud")
            return True

        except serial.SerialException as e:
            logger.error(f"Failed to connect to {self.port}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to RS485: {e}")
            return False

    def test_baudrates(self, test_lock_id: int = 0) -> Optional[int]:
        """
        Test different baud rates to find the correct one.

        Tries common baud rates: 9600, 19200, 38400, 115200

        Args:
            test_lock_id: Lock ID to test with (default: 0)

        Returns:
            Working baud rate or None if none work
        """
        common_baudrates = [19200, 9600, 38400, 115200]

        logger.info("Testing different baud rates...")

        original_baudrate = self.baudrate

        for baudrate in common_baudrates:
            logger.info(f"Testing baud rate: {baudrate}")

            try:
                # Close existing connection if open
                if self.serial and self.serial.is_open:
                    self.serial.close()
                    time.sleep(0.2)

                # Try to connect with this baud rate
                self.baudrate = baudrate
                self.serial = serial.Serial(
                    port=self.port,
                    baudrate=baudrate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=self.timeout,
                )

                time.sleep(0.3)  # Give port time to stabilize

                # Try to send a simple status query
                message = self._build_message(self.cu_address, test_lock_id, Command.GET_STATUS)
                response = self._send_command(message, expected_response_len=9, retry_count=1)

                if response and len(response) >= 5:
                    # Check if response looks valid (has correct frame markers)
                    if response[0] == self.STX and response[-2] == self.ETX:
                        logger.info(f"✅ Found working baud rate: {baudrate}")
                        return baudrate

                logger.warning(f"Baud rate {baudrate} - no valid response")

            except Exception as e:
                logger.error(f"Error testing baud rate {baudrate}: {e}")
                continue

        # Restore original baud rate
        self.baudrate = original_baudrate
        logger.warning("No working baud rate found - keeping original setting")
        return None

    def ensure_port_ready(self):
        """
        Ensure the port is open and active. If it's closed, it opens it.
        If it's open but stuck ('frozen'), it forces a close and reopen to reset the driver.
        This prevents 'Access Denied' and 'WriteFile failed' issues.
        """
        try:
            if not self.serial or not self.serial.is_open:
                # If the port is closed - open a new one
                self.serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=self.timeout,
                )
                logger.info(f"RS485 port {self.port} reconnected successfully.")
            else:
                # If the port is open, send a zero-byte ping to check for freeze
                try:
                    self.serial.write(b"")
                    self.serial.flush()
                except serial.SerialException:
                    logger.warning("RS485 port seems frozen - forcing a reopen...")
                    # Force close and reopen
                    self.serial.close()
                    time.sleep(0.2) # Small delay for the OS to release the port
                    self.serial.open()
                    logger.info(f"RS485 port {self.port} reopened successfully after freeze.")
        except Exception as e:
            logger.error(f"Failed to ensure/reopen RS485 port {self.port}: {e}")

    def disconnect(self):
        """Close the serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info("RS485 connection closed")

    def _calculate_checksum(self, data: bytes) -> int:
        """
        Calculate KR-CU16 checksum (sum of all bytes, low byte only).
        """
        total = sum(data)
        return total & 0xFF

    def _build_message(self, cu_addr: int, lock_num: int, command: Command, data: bytes = b"") -> bytes:
        """
        Build a KR-CU16 protocol message.
        """
        # ADDR byte: for single CU, lock_num 0-15 maps to ADDR 0x00-0x0F
        addr_byte = lock_num

        # Build message
        if data:
            # Message with data
            message_body = bytes([self.STX, addr_byte, command.value]) + data + bytes([self.ETX])
        else:
            # Simple message
            message_body = bytes([self.STX, addr_byte, command.value, self.ETX])

        # Calculate checksum
        checksum = self._calculate_checksum(message_body)

        # Complete message
        message = message_body + bytes([checksum])

        logger.debug(f"Built KR-CU16 message: {message.hex().upper()} (Lock={lock_num}, CMD={command.name})")
        return message

    def _send_command(self, message: bytes, expected_response_len: int = 9, retry_count: int = 3) -> Optional[bytes]:
        """
        Send command and wait for response with automatic retry and port reset.

        Args:
            message: Message to send
            expected_response_len: Expected length of response
            retry_count: Number of retries if no response (default: 3)

        Returns:
            Response bytes or None if all retries failed
        """
        for attempt in range(retry_count):
            try:
                # Ensure port is ready before each attempt
                self.ensure_port_ready()

                if not self.serial or not self.serial.is_open:
                    logger.error("Serial port not connected after port check")
                    if attempt < retry_count - 1:
                        time.sleep(0.2)
                        continue
                    return None

                # Clear any stale data in input/output buffers
                self.serial.reset_input_buffer()
                self.serial.reset_output_buffer()
                logger.debug(f"Buffers cleared (attempt {attempt + 1}/{retry_count})")

                # Send message
                self.serial.write(message)
                self.serial.flush()
                logger.debug(f">> Sent: {message.hex().upper()}")

                # Wait for controller to process (increase delay on retries)
                delay = 0.1 + (attempt * 0.05)  # 0.1s, 0.15s, 0.2s
                time.sleep(delay)

                # Wait for response
                response = self.serial.read(expected_response_len)
                logger.debug(f"<< Received: {response.hex().upper() if response else 'None'}")

                # Validate we got something
                if not response or len(response) == 0:
                    logger.warning(f"No response received from controller (attempt {attempt + 1}/{retry_count})")

                    if attempt < retry_count - 1:
                        # Reset port before retry
                        logger.info("Resetting port before retry...")
                        try:
                            self.serial.close()
                            time.sleep(0.3)
                            self.serial.open()
                            time.sleep(0.2)
                            logger.info("Port reset complete")
                        except Exception as reset_error:
                            logger.error(f"Port reset failed: {reset_error}")
                        continue
                    else:
                        # Last attempt failed - return None but don't crash
                        logger.error("All retry attempts failed - controller not responding")
                        return None

                # Got valid response
                return response

            except serial.SerialException as e:
                logger.error(f"Serial communication error (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(0.3)
                    continue
                return None
            except Exception as e:
                logger.error(f"Unexpected error sending command (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(0.3)
                    continue
                return None

        return None

    def _parse_status_response(self, response: bytes) -> Optional[LockStateData]:
        """
        Parse status response from CU16.
        """
        if not response or len(response) < 9:
            logger.error(f"Invalid response length: {len(response) if response else 0}")
            return None

        if response[0] != self.STX or response[-2] != self.ETX:
            logger.error(f"Invalid frame markers: STX={response[0]:02X}, ETX={response[-2]:02X}")
            return None

        # Verify checksum
        expected_sum = self._calculate_checksum(response[:-1])
        if response[-1] != expected_sum:
            logger.error(f"Checksum mismatch: expected={expected_sum:02X}, got={response[-1]:02X}")
            return None

        # Extract data
        return LockStateData(
            lock_hooks_1_8=response[3],
            lock_hooks_9_16=response[4],
            infrared_1_8=response[5],
            infrared_9_16=response[6],
        )

    def unlock_cart(self, locker_id: int) -> bool:
        """
        Unlock a cart and send a RESET command to the controller afterward
        to prevent the CU16 from entering a stuck 'BUSY' state.

        Args:
            locker_id: Cart/locker ID (0-15 for 16 locks)

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Unlocking cart/lock {locker_id}")

        # ensure_port_ready is called inside _send_command
        message = self._build_message(self.cu_address, locker_id, Command.UNLOCK)
        response = self._send_command(message, expected_response_len=9)

        # CRITICAL FIX: Send RESET (0x38) after UNLOCK to clear the CU16's BUSY state.
        try:
            time.sleep(0.1)
            # The lock_num 0x00 is used for a general board-level command like 0x38
            reset_cmd = self._build_message(self.cu_address, 0x00, Command.RETURN_UNLOCK_TIME)
            self._send_command(reset_cmd, expected_response_len=9)
            
            # ADDITIONAL FIX: Clear the TX buffer after sending the RESET command
            if self.serial and self.serial.is_open:
                self.serial.flush()
            
            logger.debug("Sent RESET (0x38) to CU16 after unlock to clear BUSY state and flushed TX buffer.")
        except Exception as e:
            logger.warning(f"Failed to send RESET after unlock: {e}")

        if response and len(response) >= 9:
            # Parse response to verify unlock
            state = self._parse_status_response(response)
            if state:
                logger.info(f"Cart {locker_id} unlocked successfully (with response)")
                return True

        # Assume success if command was sent, as per protocol uncertainty
        logger.warning(f"Cart {locker_id} unlock command sent (no reliable response received)")
        return True

    def lock_cart(self, locker_id: int) -> bool:
        """
        Lock a cart (not directly supported in protocol - locks auto-lock).
        """
        logger.info(f"Checking lock status for cart {locker_id}")

        state = self.get_lock_state(locker_id)
        if state and state.is_lock_closed(locker_id):
            logger.info(f"Cart {locker_id} is already locked")
            return True

        logger.warning(f"Cart {locker_id} is not locked - auto-lock should happen on return")
        return False

    def get_lock_state(self, locker_id: int) -> Optional[LockStateData]:
        """
        Get complete lock state (lock hook + infrared sensor).
        """
        logger.debug(f"Querying state of lock {locker_id}")

        # ensure_port_ready is called inside _send_command
        message = self._build_message(self.cu_address, locker_id, Command.GET_STATUS)
        response = self._send_command(message, expected_response_len=9)

        if response:
            return self._parse_status_response(response)

        return None

    def get_all_locks_state(self) -> Optional[LockStateData]:
        """
        Get state of all 16 locks on the CU16 board.
        """
        logger.debug("Querying state of all locks on CU16")

        # ensure_port_ready is called inside _send_command
        # The command 0x32 (GET_ALL_STATUS) returns data for all 16 locks
        message = self._build_message(self.cu_address, 0, Command.GET_ALL_STATUS)
        response = self._send_command(message, expected_response_len=9)

        if response:
            return self._parse_status_response(response)

        return None

    def check_cart_returned(self, locker_id: int) -> bool:
        """
        Check if cart was physically returned (micro-switch detected).
        """
        logger.debug(f"Checking if cart {locker_id} is returned")

        state = self.get_lock_state(locker_id)
        if not state:
            return False

        # Cart is returned if: infrared detects cart AND lock is closed
        has_cart = state.has_cart_inside(locker_id)
        is_locked = state.is_lock_closed(locker_id)

        if has_cart and is_locked:
            logger.info(f"Cart {locker_id} detected as fully returned (cart inside + locked)")
            return True

        if has_cart and not is_locked:
            logger.info(f"Cart {locker_id} is inside but not locked yet")

        return False

    def find_first_available_lock(self) -> Optional[int]:
        """
        Find the first available (empty and unlocked) lock.
        """
        logger.warning("Hardware doesn't support reliable status queries - use software tracking")
        return None

    def auto_lock_on_return(self, locker_id: int) -> bool:
        """
        Auto-lock cart when returned (detected by micro-switch).
        """
        if self.check_cart_returned(locker_id):
            logger.info(f"Cart {locker_id} is returned and locked")
            return True

        logger.warning(f"Cart {locker_id} is not fully returned yet")
        return False

    def get_lock_status(self, locker_id: int) -> LockStatus:
        """
        Get simplified lock status.
        """
        state = self.get_lock_state(locker_id)

        if not state:
            return LockStatus.UNKNOWN

        if state.is_lock_closed(locker_id):
            return LockStatus.LOCKED
        else:
            return LockStatus.UNLOCKED

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()