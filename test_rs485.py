"""
Test RS485 Communication with KR-CU16
"""
import serial
import time

# Configuration
PORT = "COM4"
BAUD_RATES = [9600, 19200, 38400]  # Try multiple baud rates

def test_connection(port, baudrate):
    """Test connection at specific baud rate"""
    print(f"\n{'='*60}")
    print(f"Testing: {port} @ {baudrate} baud")
    print(f"{'='*60}")

    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0
        )

        print(f"✓ Port opened successfully")

        # Try to unlock lock #0 (address 0x00)
        # Message: STX(0x02) + ADDR(0x00) + CMD(0x31=UNLOCK) + ETX(0x03) + CHECKSUM
        message = bytes([0x02, 0x00, 0x31, 0x03])
        checksum = sum(message) & 0xFF
        message = message + bytes([checksum])

        print(f"→ Sending UNLOCK command to lock #0")
        print(f"   Message: {message.hex().upper()}")

        ser.write(message)
        ser.flush()

        # Wait for response
        time.sleep(0.5)
        response = ser.read(100)  # Read up to 100 bytes

        if response:
            print(f"← Received response ({len(response)} bytes):")
            print(f"   {response.hex().upper()}")

            # Parse response
            if len(response) >= 5:
                if response[0] == 0x02 and response[-2] == 0x03:
                    print(f"✓ Valid frame structure (STX...ETX)")
                    print(f"  ADDR: 0x{response[1]:02X}")
                    print(f"  CMD: 0x{response[2]:02X}")
                    if len(response) >= 9:
                        print(f"  DATA1 (Lock hooks 1-8): 0x{response[3]:02X} = {bin(response[3])}")
                        print(f"  DATA2 (Lock hooks 9-16): 0x{response[4]:02X} = {bin(response[4])}")
                        print(f"  DATA3 (Infrared 1-8): 0x{response[5]:02X} = {bin(response[5])}")
                        print(f"  DATA4 (Infrared 9-16): 0x{response[6]:02X} = {bin(response[6])}")
                    return True
                else:
                    print(f"✗ Invalid frame markers")
            else:
                print(f"✗ Response too short")
        else:
            print(f"✗ No response received")

        ser.close()
        return False

    except serial.SerialException as e:
        print(f"✗ Serial error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("KR-CU16 RS485 Communication Test")
    print("="*60)

    # Try different baud rates
    for baudrate in BAUD_RATES:
        if test_connection(PORT, baudrate):
            print(f"\n✓✓✓ SUCCESS at {baudrate} baud! ✓✓✓")
            break
        time.sleep(1)
    else:
        print(f"\n✗✗✗ Failed at all baud rates ✗✗✗")
        print("\nTroubleshooting:")
        print("1. Check wiring: A+, B-, GND")
        print("2. Check power to locks")
        print("3. Check CU16 address (should be 0x00)")
        print("4. Try different COM port")
