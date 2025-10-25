"""
RS232-to-RS485 Adapter Test Script
===================================

This script tests communication with the KR-CU16 controller
using an RS232-to-RS485 adapter.

Usage:
    python test_rs232_adapter.py

Author: CartWise Team
Version: 1.0.0
"""

import serial
import time
import sys

# Configuration
PORT = "COM4"  # Change to your COM port
BAUDRATE = 19200

def test_adapter():
    """Test RS232-to-RS485 adapter connectivity."""

    print("=" * 60)
    print("RS232-to-RS485 Adapter Test")
    print("=" * 60)
    print(f"\nPort: {PORT}")
    print(f"Baud Rate: {BAUDRATE}")
    print("\n" + "-" * 60)

    try:
        # Step 1: Open port with RS232-to-RS485 settings
        print("\n[1/5] Opening serial port...")
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0,
            # RS232-to-RS485 adapter settings
            rtscts=False,    # Disable RTS/CTS flow control
            dsrdtr=False,    # Disable DSR/DTR flow control
            xonxoff=False,   # Disable software flow control
        )
        print(f"✅ Port {PORT} opened successfully")

        # Step 2: Set DTR/RTS
        print("\n[2/5] Setting DTR and RTS...")
        ser.setDTR(True)   # Enable data terminal ready
        ser.setRTS(False)  # Start in receive mode
        print("✅ DTR=True, RTS=False (receive mode)")

        # Step 3: Clear buffers
        print("\n[3/5] Clearing buffers...")
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        print("✅ Buffers cleared")

        # Step 4: Build and send test command
        print("\n[4/5] Sending GET_STATUS command to lock 0...")

        # KR-CU16 GET_STATUS command for lock 0
        # Frame: STX (0x02) + ADDR (0x00) + CMD (0x30) + ETX (0x03) + SUM
        STX = 0x02
        ADDR = 0x00  # Lock 0
        CMD = 0x30   # GET_STATUS
        ETX = 0x03

        message = bytes([STX, ADDR, CMD, ETX])
        checksum = sum(message) & 0xFF
        full_message = message + bytes([checksum])

        print(f"   Message: {full_message.hex().upper()}")
        print(f"   Breakdown: STX={STX:02X} ADDR={ADDR:02X} CMD={CMD:02X} ETX={ETX:02X} SUM={checksum:02X}")

        # Switch to TX mode
        ser.setRTS(True)
        time.sleep(0.01)  # Small delay for adapter to switch

        # Send
        ser.write(full_message)
        ser.flush()
        print("✅ Message sent")

        # Switch to RX mode
        ser.setRTS(False)
        time.sleep(0.2)  # Wait for response

        # Step 5: Read response
        print("\n[5/5] Reading response...")
        response = ser.read(20)  # Read up to 20 bytes

        if response and len(response) > 0:
            print(f"✅ Received response!")
            print(f"   Raw bytes: {response.hex().upper()}")
            print(f"   Length: {len(response)} bytes")

            # Parse response
            if len(response) >= 5:
                if response[0] == STX and response[-2] == ETX:
                    print(f"   Frame markers: STX={response[0]:02X} ETX={response[-2]:02X} ✅")

                    # Verify checksum
                    received_sum = response[-1]
                    calculated_sum = sum(response[:-1]) & 0xFF

                    if received_sum == calculated_sum:
                        print(f"   Checksum: {received_sum:02X} ✅")
                        print("\n" + "=" * 60)
                        print("SUCCESS! Controller is responding correctly!")
                        print("=" * 60)
                        return True
                    else:
                        print(f"   Checksum: Expected {calculated_sum:02X}, Got {received_sum:02X} ❌")
                else:
                    print(f"   Invalid frame markers ❌")
        else:
            print("❌ No response received from controller")
            print("\nTroubleshooting:")
            print("1. Check physical connections (A→A, B→B)")
            print("2. Verify controller is powered on")
            print("3. Try different baud rates: 9600, 38400")
            print("4. Check COM port number in Device Manager")
            print("5. Ensure no other software is using the port")

        ser.close()
        return False

    except serial.SerialException as e:
        print(f"\n❌ Serial port error: {e}")
        print("\nPossible causes:")
        print("1. Port already in use by another application")
        print("2. Incorrect port name (check Device Manager)")
        print("3. USB driver not installed")
        return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def main():
    """Main function."""

    # Check if port is specified
    if len(sys.argv) > 1:
        global PORT
        PORT = sys.argv[1]
        print(f"Using port from command line: {PORT}")

    # Run test
    success = test_adapter()

    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
