# Hardware Setup & Protocol Documentation
## CartWise Pro

---

## 📡 RS485 Communication Protocol

### Overview

The CartWise Pro system uses RS485 serial communication to control electronic locks on shopping carts. This document describes the complete protocol specification.

### Hardware Requirements

- **Controller**: RS485-compatible lock controller
- **Adapter**: USB-to-RS485 converter
- **Cabling**: Standard RS485 twisted pair
- **Locks**: Electronic solenoid locks with micro-switch

### Connection Diagram

```
[Raspberry Pi] --USB--> [USB-RS485] --RS485--> [Lock Controller] ---> [Locks 1-N]
                                                      |
                                                  [Micro-Switches]
```

---

## 🔌 Serial Configuration

| Parameter | Value |
|-----------|-------|
| **Baud Rate** | 9600 |
| **Data Bits** | 8 |
| **Stop Bits** | 1 |
| **Parity** | None |
| **Flow Control** | None |

---

## 📦 Message Format

All messages follow this binary format:

```
[STX] [CMD] [LOCKER_ID] [DATA] [CRC] [ETX]
```

### Byte Definitions

| Byte | Name | Description | Value |
|------|------|-------------|-------|
| 0 | STX | Start of Text | 0x02 |
| 1 | CMD | Command Code | See commands below |
| 2 | LOCKER_ID | Lock Identifier | 0x01 - 0xFF (1-255) |
| 3+ | DATA | Additional Data | Variable |
| N-1 | CRC | Checksum | XOR of all bytes |
| N | ETX | End of Text | 0x03 |

---

## 🎮 Command Codes

### Lock Command (0x30)

**Description**: Lock a cart

**Format**: `[0x02] [0x30] [LOCKER_ID] [0x00] [CRC] [0x03]`

**Example**: Lock cart #1
```
02 30 01 00 33 03
```

**Response**:
```
02 30 01 01 XX 03  # Success (byte 3 = 0x01)
02 30 01 00 XX 03  # Failure (byte 3 = 0x00)
```

---

### Unlock Command (0x31)

**Description**: Unlock a cart

**Format**: `[0x02] [0x31] [LOCKER_ID] [0x00] [CRC] [0x03]`

**Example**: Unlock cart #1
```
02 31 01 00 32 03
```

**Response**:
```
02 31 01 01 XX 03  # Success
02 31 01 00 XX 03  # Failure
```

---

### Status Query (0x32)

**Description**: Query current lock status

**Format**: `[0x02] [0x32] [LOCKER_ID] [0x00] [CRC] [0x03]`

**Example**: Query cart #1
```
02 32 01 00 31 03
```

**Response**:
```
02 32 01 [STATUS] [CRC] 03
```

**Status Byte**:
- `0x00` = Unlocked
- `0x01` = Locked
- `0xFF` = Error/Unknown

---

### Micro-Switch Status (0x33)

**Description**: Check if cart is physically returned (micro-switch pressed)

**Format**: `[0x02] [0x33] [LOCKER_ID] [0x00] [CRC] [0x03]`

**Example**: Check cart #1
```
02 33 01 00 30 03
```

**Response**:
```
02 33 01 [SWITCH_STATUS] [CRC] 03
```

**Switch Status**:
- `0x00` = Not pressed (cart not in position)
- `0x01` = Pressed (cart returned to position)

---

## 🔐 CRC Calculation

The CRC is a simple XOR checksum of all bytes between STX and CRC (excluding STX and ETX).

**Algorithm**:
```python
def calculate_crc(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte
    return crc & 0xFF
```

**Example**:
```
Message: 02 31 01 00 ?? 03
CRC = 0x31 ^ 0x01 ^ 0x00 = 0x30
Final: 02 31 01 00 30 03
```

---

## 🔄 Automatic Cart Return Detection

### How It Works

1. Customer returns cart to designated position
2. Cart pushes micro-switch
3. Controller detects switch closure
4. Controller sends notification: `02 33 [LOCKER_ID] 01 [CRC] 03`
5. System receives notification
6. System automatically locks the cart
7. Cart marked as available

### Polling vs Event-Driven

**Polling Mode** (Current Implementation):
- System periodically queries switch status
- Interval: Every 5 seconds
- Pro: Simple, reliable
- Con: Slight delay in detection

**Event-Driven Mode** (Future Enhancement):
- Controller sends unsolicited notification on switch change
- Pro: Instant detection
- Con: Requires controller support

---

## 🧪 Testing Commands

### Test Lock/Unlock Cycle

```bash
# Unlock cart 1
echo -ne '\x02\x31\x01\x00\x32\x03' > /dev/ttyUSB0

# Wait 2 seconds
sleep 2

# Lock cart 1
echo -ne '\x02\x30\x01\x00\x33\x03' > /dev/ttyUSB0
```

### Monitor Serial Communication

```bash
# Linux/macOS
cat /dev/ttyUSB0 | hexdump -C

# Or use screen
screen /dev/ttyUSB0 9600
```

---

## 🐛 Troubleshooting

### No Response from Controller

1. **Check connections**:
   ```bash
   ls -l /dev/ttyUSB*
   ```

2. **Test with minicom**:
   ```bash
   minicom -D /dev/ttyUSB0 -b 9600
   ```

3. **Verify permissions**:
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   sudo usermod -a -G dialout $USER
   ```

### Incorrect Responses

- Verify CRC calculation
- Check baud rate matches (9600)
- Ensure correct byte order
- Verify locker_id is valid (1-255)

### Micro-Switch Not Detecting

- Check physical switch installation
- Test switch with multimeter
- Verify wiring to controller
- Test with status query command

---

## 📊 Performance Specifications

| Metric | Value |
|--------|-------|
| Lock Response Time | < 100ms |
| Unlock Response Time | < 100ms |
| Status Query Time | < 50ms |
| Micro-Switch Detection | < 200ms |
| Max Supported Locks | 255 |
| Communication Range | Up to 1200m (RS485) |

---

## 🔧 Advanced Configuration

### Multiple Controllers

For systems with many carts, use multiple controllers:

```python
controller_1 = RS485Controller("/dev/ttyUSB0")  # Carts 1-50
controller_2 = RS485Controller("/dev/ttyUSB1")  # Carts 51-100
```

### Custom Commands

Extend the protocol for custom needs:

```python
class CustomCommand(Enum):
    ALARM = 0x34
    STATUS_LED = 0x35
```

---

## 📞 Support

For hardware support:
- Email: hardware@cartwise.com
- Phone: 050-XXXXXXX

---

**Document Version**: 1.0
**Last Updated**: 2025-01-20
**Author**: CartWise Team
