# הגדרת מחשב מרוחק עם בקר RS485
## Setup Guide for Remote Computer with RS485 Controller

---

## 🎯 מטרה

להתקין את ה-**Local Agent** על המחשב שמחובר לבקר CU16, כדי שיוכל:
1. לקבל פקודות מה-API בענן
2. לשלוט במנעולי RS485
3. לדווח סטטוס חזרה

---

## 📋 דרישות

### על המחשב המרוחק (שמחובר לבקר):

- ✅ Windows/Linux
- ✅ Python 3.8+
- ✅ מתאם RS232-to-RS485 מחובר
- ✅ חיבור אינטרנט

---

## 🚀 התקנה מהירה

### שלב 1: הורד את הקוד

```bash
# פתח CMD או PowerShell
cd C:\
git clone https://github.com/Arviv123/CartWise.git
cd CartWise
```

אם אין Git, הורד ZIP:
```
https://github.com/Arviv123/CartWise/archive/refs/heads/main.zip
```
ופתח ל-`C:\CartWise`

---

### שלב 2: התקן Python Dependencies

```bash
pip install -r requirements.txt
```

---

### שלב 3: בדוק איזה COM Port

#### בWindows:

1. פתח **Device Manager** (`devmgmt.msc`)
2. לך ל-**Ports (COM & LPT)**
3. חפש משהו כמו:
   ```
   USB-SERIAL CH340 (COM3)
   או
   USB Serial Port (COM5)
   ```
4. זכור את מספר ה-COM!

#### או בפקודה:

```bash
# Windows
mode

# Linux
ls /dev/ttyUSB*
```

---

### שלב 4: צור API Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**שמור את התוצאה!** למשל:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

---

### שלב 5: הרץ את ה-Local Agent

#### אם ה-API רץ בענן (Render.com):

```bash
python raspberry_pi\local_agent.py ^
    --cloud-url https://cartwise-cloud.onrender.com ^
    --branch-id branch_001 ^
    --api-key a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6 ^
    --serial-port COM3 ^
    --baudrate 19200
```

**שנה:**
- `COM3` → הפורט שמצאת
- `a1b2c3...` → ה-API key שיצרת

#### אם ה-API רץ מקומי (למבחן):

```bash
python raspberry_pi\local_agent.py ^
    --cloud-url http://192.168.1.100:8002 ^
    --branch-id branch_001 ^
    --api-key test-key-123 ^
    --serial-port COM3 ^
    --baudrate 19200
```

**שנה:**
- `192.168.1.100` → ה-IP של המחשב שמריץ את ה-API
- `COM3` → הפורט שלך

---

## ✅ אם הכל עובד, תראה:

```
============================================================
Starting CartWise Local Agent
============================================================
RS485 controller connected successfully
Successfully registered with cloud
Agent is now running - polling for commands...
============================================================
```

ואז כל כמה שניות:
```
Heartbeat sent
```

**מעולה! זה עובד! ✅**

---

## 🧪 בדיקה

### בדוק שה-Agent רואה את הבקר:

בטרמינל, תראה:
```
RS485 controller connected successfully
```

### בדוק שה-Agent מתחבר לענן:

בטרמינל, תראה:
```
Successfully registered with cloud
Heartbeat sent
```

### שלח פקודת ניסיון מה-API:

על המחשב השני (או בדפדפן), גש ל:
```
https://cartwise-cloud.onrender.com/docs
```

חפש את:
```
POST /api/agent/commands
```

שלח:
```json
{
  "branch_id": "branch_001",
  "command_type": "get_status",
  "params": {
    "locker_id": 0
  }
}
```

ב-Agent תראה:
```
Executing command: get_status (ID: xxx-xxx-xxx)
Command result reported: xxx-xxx-xxx - SUCCESS
```

**מצוין! הכל עובד! 🎉**

---

## 🔄 הפעלה אוטומטית (Windows)

### צור קובץ `.bat`:

```bash
notepad C:\CartWise\start_agent.bat
```

הכנס:

```batch
@echo off
cd C:\CartWise
python raspberry_pi\local_agent.py ^
    --cloud-url https://cartwise-cloud.onrender.com ^
    --branch-id branch_001 ^
    --api-key YOUR_API_KEY_HERE ^
    --serial-port COM3 ^
    --baudrate 19200
pause
```

שמור.

### הוסף ל-Startup:

1. לחץ `Win+R`
2. הקלד: `shell:startup`
3. העתק קיצור ל-`C:\CartWise\start_agent.bat`

עכשיו ה-Agent יתחיל אוטומטית בהפעלת המחשב!

---

## 🔧 פתרון בעיות

### בעיה: "could not open port COM3"

**פתרון:**
1. בדוק Device Manager - הפורט קיים?
2. נסה פורט אחר (COM4, COM5...)
3. בדוק שאף תוכנה אחרת לא משתמשת בפורט

### בעיה: "RS485 controller not connected"

**פתרון:**
1. בדוק חיבור USB
2. התקן דרייבר למתאם (CH340, FTDI...)
3. נסה baud rate אחר: `--baudrate 9600`

### בעיה: "Failed to register with cloud"

**פתרון:**
1. בדוק חיבור אינטרנט: `ping google.com`
2. בדוק URL: `curl https://cartwise-cloud.onrender.com/docs`
3. בדוק API key - אותו key שהגדרת בענן?

### בעיה: "No response from controller"

**פתרון:**
1. הרץ את תסריט הבדיקה:
   ```bash
   python test_rs232_adapter.py
   ```
2. בדוק חיבורים פיזיים: A→A, B→B
3. בדוק פולריות
4. ודא שהבקר מופעל

---

## 📊 Logs

ה-Agent מדפיס logs לקונסולה.

אם תרצה לשמור logs לקובץ:

```bash
python raspberry_pi\local_agent.py ... > agent.log 2>&1
```

---

## 🎯 סיכום

אחרי ההתקנה, המערכת תעבוד כך:

```
לקוח (נייד/מחשב)
    ↓
  Cloud API (Render.com)
    ↓
  Local Agent (המחשב שלך)
    ↓
  RS485 Controller
    ↓
  בקר CU16
    ↓
  מנעולים
```

**הכל מוכן! 🚀**

---

## 📞 צריך עזרה?

1. בדוק logs בקונסולה
2. הרץ `test_rs232_adapter.py`
3. בדוק Device Manager
4. ודא חיבור אינטרנט

---

**גרסה:** 1.0.0
**תאריך:** 2025-10-25
**GitHub:** https://github.com/Arviv123/CartWise
