# Raspberry Pi Setup Guide
## מדריך הגדרת רספברי פיי

---

## 🎯 מה הרספברי עושה?

הרספברי במערכת CartWise מבצע **שני תפקידים**:

1. **תצוגת ממשק לקוח** - מציג את הממשק בדפדפן (Kiosk Mode)
2. **סוכן מקומי (Local Agent)** - מתחבר לענן ומבצע פקודות על RS485

```
┌────────────────────────────────────────┐
│         Raspberry Pi                    │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  1. Chromium (Kiosk Mode)        │  │
│  │     https://cartwise.onrender.   │  │
│  │     com/                          │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  2. Local Agent (Python)         │  │
│  │     - מקבל פקודות מהענן           │  │
│  │     - שולח פקודות ל-CU16         │  │
│  │     - מדווח סטטוס                │  │
│  └─────────┬────────────────────────┘  │
│            │ RS485                     │
│            ▼                           │
│  ┌──────────────────────────────────┐  │
│  │  RS232→RS485 → CU16 Controller   │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

---

## 📦 התקנה

### שלב 1: התקנת Raspberry Pi OS

1. הורד **Raspberry Pi Imager**: https://www.raspberrypi.com/software/
2. צרוב **Raspberry Pi OS Lite** (64-bit) על כרטיס SD
3. הפעל את הרספברי וחבר למסך

### שלב 2: התקנת תלויות

```bash
# עדכן את המערכת
sudo apt update && sudo apt upgrade -y

# התקן Python 3 ו-pip
sudo apt install -y python3 python3-pip python3-venv git

# התקן Chromium עבור Kiosk Mode
sudo apt install -y chromium-browser unclutter

# התקן X server
sudo apt install -y xorg openbox lightdm
```

### שלב 3: שכפול הקוד

```bash
# צור תיקייה
mkdir -p ~/cartwise
cd ~/cartwise

# העתק את הקבצים מהמחשב או שכפל מ-GitHub
git clone https://github.com/Arviv123/CartWise.git
cd CartWise
```

### שלב 4: התקנת תלויות Python

```bash
# צור virtual environment
python3 -m venv venv

# הפעל virtual environment
source venv/bin/activate

# התקן requirements
pip install -r requirements.txt
```

### שלב 5: הגדרת הרשאות Serial Port

```bash
# הוסף את המשתמש לקבוצת dialout
sudo usermod -a -G dialout $USER

# התנתק והתחבר מחדש כדי שההרשאות ייכנסו לתוקף
# או הרץ:
newgrp dialout
```

---

## ⚙️ תצורה

### צור קובץ תצורה:

```bash
nano ~/cartwise/agent_config.sh
```

הכנס את הפרטים הבאים:

```bash
#!/bin/bash

# Cloud API Configuration
export CLOUD_URL="https://cartwise-cloud.onrender.com"
export BRANCH_ID="branch_001"  # שנה לפי הסניף שלך
export API_KEY="your-secret-api-key-here"  # מפתח API ייחודי

# RS485 Configuration
export SERIAL_PORT="/dev/ttyUSB0"  # או /dev/ttyS0 אם RS232 מובנה
export BAUDRATE="19200"

# Kiosk Mode Configuration
export KIOSK_URL="https://cartwise-cloud.onrender.com/"
export SCREEN_TIMEOUT="300"  # 5 minutes
```

שמור (`Ctrl+O`) וסגור (`Ctrl+X`).

---

## 🚀 הפעלה

### הפעלת Local Agent (ידנית):

```bash
cd ~/cartwise/CartWise
source venv/bin/activate
source ~/cartwise/agent_config.sh

python raspberry_pi/local_agent.py \
    --cloud-url $CLOUD_URL \
    --branch-id $BRANCH_ID \
    --api-key $API_KEY \
    --serial-port $SERIAL_PORT \
    --baudrate $BAUDRATE
```

תראה:
```
============================================================
Starting CartWise Local Agent
============================================================
RS485 controller connected successfully
Successfully registered with cloud
Agent is now running - polling for commands...
============================================================
```

---

## 🖥️ הגדרת Kiosk Mode (מצב קיוסק)

Kiosk Mode מציג את ממשק הלקוח במסך מלא ללא כלי דפדפן.

### צור סקריפט Kiosk:

```bash
nano ~/cartwise/start_kiosk.sh
```

הכנס:

```bash
#!/bin/bash

# Load configuration
source ~/cartwise/agent_config.sh

# Wait for X server
sleep 5

# Hide mouse cursor
unclutter -idle 0.1 &

# Disable screen blanking
xset s off
xset s noblank
xset -dpms

# Start Chromium in kiosk mode
chromium-browser \
    --kiosk \
    --noerrdialogs \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --disable-restore-session-state \
    --disable-notifications \
    --disable-translate \
    --no-first-run \
    --start-fullscreen \
    $KIOSK_URL
```

שמור והפעל הרשאות:

```bash
chmod +x ~/cartwise/start_kiosk.sh
```

---

## 🔄 הפעלה אוטומטית בהדלקה

### 1. הפעלת Local Agent אוטומטית (systemd service):

```bash
sudo nano /etc/systemd/system/cartwise-agent.service
```

הכנס:

```ini
[Unit]
Description=CartWise Local Agent
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/cartwise/CartWise
Environment="PATH=/home/pi/cartwise/CartWise/venv/bin"
EnvironmentFile=/home/pi/cartwise/agent_config.sh
ExecStart=/home/pi/cartwise/CartWise/venv/bin/python raspberry_pi/local_agent.py --cloud-url ${CLOUD_URL} --branch-id ${BRANCH_ID} --api-key ${API_KEY} --serial-port ${SERIAL_PORT} --baudrate ${BAUDRATE}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

שמור והפעל:

```bash
sudo systemctl enable cartwise-agent
sudo systemctl start cartwise-agent
sudo systemctl status cartwise-agent
```

### 2. הפעלת Kiosk Mode אוטומטית:

```bash
mkdir -p ~/.config/openbox
nano ~/.config/openbox/autostart
```

הכנס:

```bash
# Disable screen blanking
xset s off
xset s noblank
xset -dpms

# Start CartWise Kiosk
/home/pi/cartwise/start_kiosk.sh &
```

### 3. הגדר Auto-Login:

```bash
sudo raspi-config
```

- בחר: **System Options** → **Boot / Auto Login** → **Desktop Autologin**

---

## 🧪 בדיקה

### בדוק את ה-Serial Port:

```bash
ls -l /dev/ttyUSB*
# או
ls -l /dev/ttyS*
```

תראה משהו כמו:
```
crw-rw---- 1 root dialout 188, 0 Oct 25 12:00 /dev/ttyUSB0
```

### בדוק חיבור RS485:

```bash
cd ~/cartwise/CartWise
source venv/bin/activate
python test_rs232_adapter.py
```

---

## 📊 ניטור

### לוגים של Local Agent:

```bash
# Live logs
sudo journalctl -u cartwise-agent -f

# Last 100 lines
sudo journalctl -u cartwise-agent -n 100
```

### בדיקת סטטוס:

```bash
sudo systemctl status cartwise-agent
```

---

## 🔧 פתרון בעיות

### בעיה: "Permission denied" על Serial Port

```bash
sudo usermod -a -G dialout $USER
# התנתק והתחבר מחדש
```

### בעיה: Local Agent לא מתחבר לענן

```bash
# בדוק חיבור אינטרנט
ping google.com

# בדוק את ה-URL בדפדפן
chromium-browser https://cartwise-cloud.onrender.com/docs

# בדוק API key
echo $API_KEY
```

### בעיה: RS485 לא עובד

```bash
# בדוק חיבורים פיזיים
# ודא: A→A, B→B, GND→GND

# נסה baud rates אחרים
python raspberry_pi/local_agent.py --baudrate 9600
```

### בעיה: Kiosk לא מופיע

```bash
# בדוק X server
echo $DISPLAY

# הרץ ידנית
DISPLAY=:0 ~/cartwise/start_kiosk.sh
```

---

## 📱 שימוש

אחרי ההתקנה, הרספברי:

1. **יציג את הממשק** על מסך מחובר
2. **יקשיב לפקודות** מהענן
3. **יבצע פקודות** unlock/lock על RS485
4. **ידווח סטטוס** חזרה לענן

הלקוחות יכולים:
- לגשת לממשק דרך המסך המקומי
- או דרך הנייד: `https://cartwise-cloud.onrender.com`

---

## 🔐 אבטחה

### צור API Key ייחודי:

```bash
# יצירת API key אקראי
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

העתק את התוצאה ל-`agent_config.sh`:

```bash
export API_KEY="your-generated-key-here"
```

---

## 📞 תמיכה

אם יש בעיות:

1. בדוק לוגים: `sudo journalctl -u cartwise-agent -f`
2. בדוק סטטוס: `sudo systemctl status cartwise-agent`
3. בדוק Serial Port: `ls -l /dev/ttyUSB*`
4. בדוק חיבור: `ping cartwise-cloud.onrender.com`

---

**גרסה:** 1.0.0
**עודכן:** 2025-10-25
**GitHub:** https://github.com/Arviv123/CartWise
