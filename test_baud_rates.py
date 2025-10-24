"""
Baud Rate Tester for KR-CU16
=============================

Tests different baud rates to find the correct one for your controller.

Usage:
    python test_baud_rates.py COM4

Author: CartWise Team
"""

import sys
import time
from src.core import setup_logging, get_logger, settings
from src.hardware.rs485 import RS485Controller

# Setup logging
setup_logging()
logger = get_logger(__name__)


def test_controller(port: str):
    """
    Test controller with different baud rates.

    Args:
        port: COM port to test (e.g., COM4)
    """
    print("=" * 60)
    print("KR-CU16 Baud Rate Tester")
    print("=" * 60)
    print(f"\nTesting port: {port}")
    print("\nThis will try common baud rates: 9600, 19200, 38400, 115200\n")

    # Try to connect with default baud rate first
    print(f"\n1️⃣  Testing with configured baud rate: {settings.BAUD_RATE}")
    print("-" * 60)

    try:
        controller = RS485Controller(port=port, baudrate=settings.BAUD_RATE)

        if not controller.connect():
            print(f"❌ Failed to connect to {port}")
            return

        print(f"✅ Port opened successfully")

        # Try to communicate
        print("\nSending test command (GET_STATUS for lock 0)...")
        time.sleep(0.5)

        state = controller.get_lock_state(0)

        if state:
            print(f"✅ SUCCESS! Communication works with {settings.BAUD_RATE} baud")
            print(f"\nLock State Data:")
            print(f"  - Lock Hooks 1-8:  0x{state.lock_hooks_1_8:02X} (binary: {state.lock_hooks_1_8:08b})")
            print(f"  - Lock Hooks 9-16: 0x{state.lock_hooks_9_16:02X} (binary: {state.lock_hooks_9_16:08b})")
            print(f"  - Infrared 1-8:    0x{state.infrared_1_8:02X} (binary: {state.infrared_1_8:08b})")
            print(f"  - Infrared 9-16:   0x{state.infrared_9_16:02X} (binary: {state.infrared_9_16:08b})")

            controller.disconnect()
            print(f"\n✅ Your controller is working correctly!")
            print(f"📝 Keep BAUD_RATE={settings.BAUD_RATE} in config/.env")
            return
        else:
            print(f"⚠️  Port opened but no valid response received")
            print(f"   This could mean:")
            print(f"   1. Wrong baud rate")
            print(f"   2. Wiring issue (check TX/RX connections)")
            print(f"   3. Controller is not powered")
            print(f"   4. Controller address mismatch\n")

        controller.disconnect()

    except Exception as e:
        print(f"❌ Error: {e}\n")

    # Now try auto-detection
    print("\n2️⃣  Auto-detecting correct baud rate...")
    print("-" * 60)

    try:
        controller = RS485Controller(port=port, baudrate=19200)

        if not controller.connect():
            print(f"❌ Failed to open port {port}")
            return

        working_baudrate = controller.test_baudrates(test_lock_id=0)

        if working_baudrate:
            print(f"\n" + "=" * 60)
            print(f"✅ SUCCESS! Found working baud rate: {working_baudrate}")
            print(f"=" * 60)
            print(f"\n📝 Update your config/.env file:")
            print(f"   BAUD_RATE={working_baudrate}\n")
        else:
            print(f"\n" + "=" * 60)
            print(f"❌ No working baud rate found")
            print(f"=" * 60)
            print(f"\n🔧 Troubleshooting steps:")
            print(f"   1. Check physical connections:")
            print(f"      - RS485 A/B wires connected correctly?")
            print(f"      - GND connected?")
            print(f"   2. Check power:")
            print(f"      - Is controller powered (usually 12V)?")
            print(f"   3. Check controller address:")
            print(f"      - Default is 0x00, yours might be different")
            print(f"   4. Try different COM port:")
            print(f"      - Use Device Manager to verify port number")
            print(f"   5. Swap TX/RX wires:")
            print(f"      - Sometimes they're reversed\n")

        controller.disconnect()

    except Exception as e:
        print(f"❌ Error during auto-detection: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_baud_rates.py <COM_PORT>")
        print("\nExamples:")
        print("  Windows: python test_baud_rates.py COM4")
        print("  Linux:   python test_baud_rates.py /dev/ttyUSB0")
        sys.exit(1)

    port = sys.argv[1]
    test_controller(port)


if __name__ == "__main__":
    main()
