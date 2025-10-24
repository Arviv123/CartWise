"""
Test different status query methods with KR-CU16
"""
import serial
import time

PORT = "COM4"
BAUDRATE = 19200
STX = 0x02
ETX = 0x03

def calculate_checksum(data: bytes) -> int:
    """Calculate checksum (sum of all bytes, low byte only)."""
    return sum(data) & 0xFF

def send_and_receive(ser, message_bytes, description):
    """Send a message and receive response."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"-> Sending: {message_bytes.hex().upper()}")

    ser.write(message_bytes)
    ser.flush()
    time.sleep(0.5)

    response = ser.read(100)
    if response:
        print(f"<- Received ({len(response)} bytes): {response.hex().upper()}")

        # Try to parse
        if len(response) >= 5:
            print(f"  STX: 0x{response[0]:02X} {'OK' if response[0] == STX else 'BAD'}")
            print(f"  ADDR: 0x{response[1]:02X}")
            print(f"  CMD: 0x{response[2]:02X}")
            if len(response) >= 9:
                print(f"  DATA1: 0x{response[3]:02X} = {bin(response[3])}")
                print(f"  DATA2: 0x{response[4]:02X} = {bin(response[4])}")
                print(f"  DATA3: 0x{response[5]:02X} = {bin(response[5])}")
                print(f"  DATA4: 0x{response[6]:02X} = {bin(response[6])}")
                print(f"  ETX: 0x{response[7]:02X} {'OK' if response[7] == ETX else 'BAD'}")
                print(f"  SUM: 0x{response[8]:02X}")
                # Verify checksum
                expected_sum = calculate_checksum(response[:-1])
                print(f"  Checksum: expected=0x{expected_sum:02X}, got=0x{response[-1]:02X} {'OK' if expected_sum == response[-1] else 'BAD'}")
    else:
        print("<- No response received")

    return response

def main():
    print("\n" + "="*60)
    print("KR-CU16 Status Query Tests")
    print("="*60)

    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0
        )
        print(f"OK - Connected to {PORT} @ {BAUDRATE} baud\n")

        # Test 1: GET_STATUS (0x30) for lock #0
        msg = bytes([STX, 0x00, 0x30, ETX])
        msg += bytes([calculate_checksum(msg)])
        send_and_receive(ser, msg, "Test 1: GET_STATUS (0x30) - Lock #0")

        # Test 2: GET_ALL_STATUS (0x32) with ADDR=0x00
        msg = bytes([STX, 0x00, 0x32, ETX])
        msg += bytes([calculate_checksum(msg)])
        send_and_receive(ser, msg, "Test 2: GET_ALL_STATUS (0x32) - ADDR=0x00")

        # Test 3: GET_ALL_STATUS (0x32) with broadcast ADDR=0xF0
        msg = bytes([STX, 0xF0, 0x32, ETX])
        msg += bytes([calculate_checksum(msg)])
        send_and_receive(ser, msg, "Test 3: GET_ALL_STATUS (0x32) - ADDR=0xF0 (broadcast)")

        # Test 4: RETURN_ALL_DATA command (0x36) - might be request format?
        msg = bytes([STX, 0x00, 0x36, ETX])
        msg += bytes([calculate_checksum(msg)])
        send_and_receive(ser, msg, "Test 4: RETURN_ALL_DATA (0x36) - ADDR=0x00")

        # Test 5: Try GET_STATUS for multiple locks individually
        print(f"\n{'='*60}")
        print("Test 5: Query each lock individually (0-4) using GET_STATUS")
        print(f"{'='*60}")
        for lock_num in range(5):
            msg = bytes([STX, lock_num, 0x30, ETX])
            msg += bytes([calculate_checksum(msg)])
            response = send_and_receive(ser, msg, f"  Lock #{lock_num}")
            time.sleep(0.3)

        ser.close()
        print(f"\n{'='*60}")
        print("Tests completed")
        print(f"{'='*60}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
