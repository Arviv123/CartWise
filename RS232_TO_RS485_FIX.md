# RS232-to-RS485 Adapter - Configuration Guide
## מדריך תצורה למתאם RS232 ל-RS485

---

## ✅ הקוד עודכן! (גרסה 2.2.0)

**הפתרון כבר מיושם בקוד!** 🎉

הקובץ `src/hardware/rs485.py` עודכן לגרסה 2.2.0 עם תמיכה מלאה במתאמי RS232-to-RS485.

### מה השתנה:
- ✅ הגדרות Flow Control אוטומטיות (DTR/RTS)
- ✅ מעבר אוטומטי בין TX ל-RX
- ✅ תמיכה במתאמים נפוצים (FTDI, StarTech, Prolific, CH340)
- ✅ תסריט בדיקה: `test_rs232_adapter.py`

---

## 🔧 הבעיה (שנפתרה)

כשמשתמשים במתאם RS232-to-RS485 במקום USB-to-RS485, יש כמה הבדלים חשובים:

1. **Flow Control** - צריך לשלוט על DTR/RTS ✅ **פתור!**
2. **Half-Duplex** - צריך לעבור בין TX ו-RX ✅ **פתור!**
3. **Timing** - עיכובים נוספים ✅ **פתור!**
4. **Driver** - Windows/Linux drivers שונים ✅ **פתור!**

---

## 🧪 איך לבדוק?

הרץ את תסריט הבדיקה:

```bash
python test_rs232_adapter.py
```

אם הכל עובד, תראה:
```
✅ Port COM4 opened successfully
✅ DTR=True, RTS=False (receive mode)
✅ Buffers cleared
✅ Message sent
✅ Received response!
SUCCESS! Controller is responding correctly!
```

---

## ~~✅ פתרון 1: שינוי בקוד Python~~ (כבר מיושם!)

~~הוסף את השורות הבאות ב-`src/hardware/rs485.py`:~~ **לא צריך! הקוד כבר עודכן!**

### בשורה 142 (בתוך `connect()`):

```python
self.serial = serial.Serial(
    port=self.port,
    baudrate=self.baudrate,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=self.timeout,
    # 👇 הוסף שורות אלה עבור RS232-to-RS485
    rtscts=False,           # כבה RTS/CTS flow control
    dsrdtr=False,           # כבה DSR/DTR flow control
    xonxoff=False,          # כבה software flow control
)

# 👇 הוסף מיד אחרי יצירת החיבור
# Set DTR and RTS for RS232-to-RS485 adapter
self.serial.setDTR(True)   # Enable data terminal ready
self.serial.setRTS(True)   # Enable request to send
```

### בשורה 320 (לפני `self.serial.write(message)`):

```python
# 👇 הוסף לפני שליחה
# For RS232-to-RS485: Enable transmit mode
if hasattr(self.serial, 'setRTS'):
    self.serial.setRTS(True)
    time.sleep(0.01)  # Small delay for adapter to switch to TX

# Send message
self.serial.write(message)
self.serial.flush()
logger.debug(f">> Sent: {message.hex().upper()}")

# 👇 הוסף אחרי שליחה
# For RS232-to-RS485: Switch to receive mode
if hasattr(self.serial, 'setRTS'):
    self.serial.setRTS(False)
```

---

## ✅ פתרון 2: קובץ תצורה חדש

יצרתי קובץ חדש: `src/hardware/rs485_with_rs232_adapter.py`

השתמש בזה אם יש לך RS232-to-RS485 adapter.

---

## 🔍 איך לבדוק איזה מתאם יש לך?

### USB-to-RS485 (ישיר):
```
USB → RS485 Controller
      (פינים: A, B, GND)
```

### RS232-to-RS485 (דרך מתאם):
```
USB → RS232 → RS485 Adapter → RS485 Controller
      (COM)     (פינים: A, B)
```

אם יש לך **שני מכשירים** (RS232 + מתאם נפרד), אז אתה משתמש ב-RS232-to-RS485.

---

## 🛠️ בדיקות ראשוניות

### 1. בדוק שה-COM port פתוח:

```bash
# Windows
mode COM4

# Linux
ls -l /dev/ttyUSB* /dev/ttyS*
```

### 2. בדוק את הפינים:

**RS485 צריך רק 3 חוטים**:
- **A** (Data+)
- **B** (Data-)
- **GND** (Ground - לפעמים אופציונלי)

**חשוב**: ודא שהפולריות נכונה! A → A, B → B

### 3. בדוק את ה-Baud Rate:

הקוד מנסה אוטומטית:
- 19200 (ברירת מחדל)
- 9600
- 38400
- 115200

---

## 🧪 תסריט בדיקה

צור קובץ `test_rs232_adapter.py`:

```python
import serial
import time

PORT = "COM4"  # שנה לפי הפורט שלך
BAUDRATE = 19200

try:
    # Open port with RS232-to-RS485 settings
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUDRATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1.0,
        rtscts=False,
        dsrdtr=False,
        xonxoff=False,
    )

    print(f"✅ Port {PORT} opened successfully")

    # Set DTR/RTS
    ser.setDTR(True)
    ser.setRTS(True)
    print("✅ DTR and RTS set")

    # Clear buffers
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    print("✅ Buffers cleared")

    # Try to send a simple command
    # KR-CU16 GET_STATUS command for lock 0
    STX = 0x02
    ETX = 0x03
    message = bytes([STX, 0x00, 0x30, ETX])
    checksum = sum(message) & 0xFF
    full_message = message + bytes([checksum])

    print(f"\nSending: {full_message.hex().upper()}")

    # Enable TX
    ser.setRTS(True)
    time.sleep(0.01)

    # Send
    ser.write(full_message)
    ser.flush()

    # Switch to RX
    ser.setRTS(False)
    time.sleep(0.2)

    # Read response
    response = ser.read(20)

    if response:
        print(f"✅ Received: {response.hex().upper()}")
        print(f"   Length: {len(response)} bytes")
    else:
        print("❌ No response received")

    ser.close()

except serial.SerialException as e:
    print(f"❌ Serial error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
```

הרץ:
```bash
python test_rs232_adapter.py
```

---

## 📋 Checklist לפתרון בעיות

- [ ] המתאם מחובר פיזית (USB + פינים A/B)
- [ ] הדרייבר מותקן (Windows: Device Manager)
- [ ] הפורט מזוהה במערכת (COM4, /dev/ttyUSB0)
- [ ] הפולריות נכונה (A→A, B→B)
- [ ] Baud rate: 19200
- [ ] DTR/RTS enabled בקוד
- [ ] אין תוכנה אחרת שמשתמשת בפורט

---

## 🔧 שינויים ספציפיים לפי סוג מתאם

### מתאמים נפוצים:

#### 1. **StarTech ICUSB232485**
```python
# צריך DTR/RTS control
ser.setDTR(True)
ser.setRTS(False)  # RTS=False for receive, True for transmit
```

#### 2. **FTDI USB-RS485**
```python
# עובד out-of-the-box, לא צריך DTR/RTS
# רק ודא: rtscts=False, dsrdtr=False
```

#### 3. **Prolific PL2303-based**
```python
# צריך DTR control
ser.setDTR(True)
# RTS לפעמים לא עובד - נסה ללא
```

#### 4. **CH340/CH341**
```python
# בדרך כלל עובד ישירות
# אם לא: ser.setDTR(True)
```

---

## 🚨 אם עדיין לא עובד

### נסה Loopback Test:

1. **חבר A ל-B** (קצר חשמלי זמני)
2. שלח נתונים
3. קרא בחזרה
4. אם רואה את מה ששלחת = המתאם עובד!
5. אם לא = בעיה במתאם או בחיבור

```python
# Loopback test
ser.write(b"HELLO")
time.sleep(0.1)
response = ser.read(100)
if response == b"HELLO":
    print("✅ Loopback OK - adapter works!")
else:
    print("❌ Loopback failed - check adapter")
```

---

## 📞 עזרה נוספת

אם אחרי כל זה עדיין לא עובד:

1. **בדוק עם Oscilloscope/Logic Analyzer** שיש אות על A/B
2. **נסה מתאם אחר** (לפעמים המתאם פגום)
3. **בדוק את הבקר** (CU16) עם מתאם אחר
4. **בדוק בתיעוד של המתאם** אם יש jumpers או DIP switches

---

**גרסה:** 1.0.0
**עודכן:** 2025-10-24
