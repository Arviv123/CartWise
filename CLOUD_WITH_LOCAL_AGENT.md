# CartWise Pro - Cloud + Local Agent Setup
## מדריך הקמת מערכת היברידית: ענן + רספברי מקומי

---

## 🎯 סקירה כללית

מערכת CartWise Pro עכשיו תומכת בארכיטקטורה היברידית:

```
┌─────────────────────────────────────────────────────────────┐
│                   INTERNET / אינטרנט                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Render.com Cloud API                                  │ │
│  │  https://cartwise-cloud.onrender.com                   │ │
│  │  - ממשק REST API                                       │ │
│  │  - אימות SMS (Inforu)                                  │ │
│  │  - ניהול השכרות                                        │ │
│  │  - תקשורת עם agents                                    │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │ HTTPS/Polling                             │
└─────────────────┼─────────────────────────────────────────┬─┘
                  │                                         │
                  ▼                                         │
┌──────────────────────────────────────┐    ┌───────────────┼──┐
│  לקוח בנייד/מחשב                     │    │               │  │
│  https://cartwise-cloud.onrender.com │    │  לקוח במסך    │  │
│                                       │    │  הרספברי      │  │
└──────────────────────────────────────┘    └───────────────┼──┘
                                                             │
                  ┌──────────────────────────────────────────┼─┐
                  │  RASPBERRY PI (בחנות)                    │ │
                  │                                          │ │
                  │  ┌────────────────────────────────────┐  │ │
                  │  │  1. Chromium Kiosk                 │  │ │
                  │  │     מציג ממשק מהענן                │  │ │
                  │  └────────────────────────────────────┘  │ │
                  │                                          │ │
                  │  ┌────────────────────────────────────┐  │ │
                  │  │  2. Local Agent (Python)           │  │ │
                  │  │     - Poll commands from cloud     │  │ │
                  │  │     - Execute RS485 commands       │  │ │
                  │  │     - Report status back           │  │ │
                  │  └──────────┬─────────────────────────┘  │ │
                  │             │ Serial RS485               │ │
                  │             ▼                            │ │
                  │  ┌────────────────────────────────────┐  │ │
                  │  │  RS232→RS485 → CU16 → Locks        │  │ │
                  │  └────────────────────────────────────┘  │ │
                  └──────────────────────────────────────────┴─┘
```

---

## 📦 רכיבי המערכת

### 1. **Cloud API (Render.com)**
- משרת את הממשק ללקוחות
- מנהל אימות SMS
- מנהל השכרות ומעקב
- מתקשר עם רספברי מקומי

### 2. **Raspberry Pi Local Agent**
- מציג ממשק בכיוסק (מסך מגע)
- מקשיב לפקודות מהענן
- שולט במנעולי RS485
- מדווח סטטוס חזרה

### 3. **RS485 Controller**
- KERONG CU16
- 16 מנעולים
- מתאם RS232→RS485

---

## 🚀 שלבי ההתקנה

### שלב 1: פריסת Cloud API (Render.com)

#### 1.1 - צור Web Service ב-Render

1. גש ל: https://dashboard.render.com
2. לחץ **"New +" → "Web Service"**
3. חבר GitHub: `https://github.com/Arviv123/CartWise`
4. הגדרות:
   ```
   Name: cartwise-cloud
   Environment: Docker
   Branch: main
   Region: Frankfurt (או Oregon)
   Instance Type: Starter ($7/mo) - מומלץ!
   ```

#### 1.2 - Environment Variables

הוסף את המשתנים הבאים:

```bash
API_HOST=0.0.0.0
API_PORT=8002
DEMO_MODE=true
INFORU_USERNAME=Arviv123
INFORU_PASSWORD=7d9b64ad-1ece-40be-906b-95ef67bdad2d
```

#### 1.3 - Deploy

לחץ **"Create Web Service"** והמתן 3-5 דקות.

תקבל URL כמו:
```
https://cartwise-cloud.onrender.com
```

#### 1.4 - בדוק שהכל עובד

גש ל:
```
https://cartwise-cloud.onrender.com/docs
```

תראה את ה-API Documentation.

---

### שלב 2: הכנת Raspberry Pi

#### 2.1 - התקנת מערכת הפעלה

1. הורד **Raspberry Pi Imager**
2. צרוב **Raspberry Pi OS Lite (64-bit)**
3. הפעל והתחבר למסך

#### 2.2 - התקנת תלויות

```bash
# עדכן מערכת
sudo apt update && sudo apt upgrade -y

# Python ו-tools
sudo apt install -y python3 python3-pip python3-venv git

# Chromium עבור Kiosk
sudo apt install -y chromium-browser unclutter xorg openbox lightdm

# הורד את הקוד
cd ~
git clone https://github.com/Arviv123/CartWise.git cartwise
cd cartwise

# צור virtual environment
python3 -m venv venv
source venv/bin/activate

# התקן requirements
pip install -r requirements.txt

# הרשאות serial port
sudo usermod -a -G dialout $USER
```

#### 2.3 - צור תצורה

```bash
nano ~/agent_config.sh
```

הכנס:

```bash
#!/bin/bash

# Cloud Configuration
export CLOUD_URL="https://cartwise-cloud.onrender.com"
export BRANCH_ID="branch_001"  # שנה לפי הסניף
export API_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"

# RS485 Configuration
export SERIAL_PORT="/dev/ttyUSB0"
export BAUDRATE="19200"

# Kiosk Configuration
export KIOSK_URL="https://cartwise-cloud.onrender.com/"
```

שמור: `Ctrl+O`, סגור: `Ctrl+X`

הפעל את התצורה:
```bash
chmod +x ~/agent_config.sh
source ~/agent_config.sh
```

**חשוב!** שמור את ה-API_KEY - תצטרך אותו!

---

### שלב 3: הפעלת Local Agent

#### 3.1 - בדיקה ידנית

```bash
cd ~/cartwise
source venv/bin/activate
source ~/agent_config.sh

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
Heartbeat sent
```

**אם רואה את זה - מעולה! זה עובד! ✅**

#### 3.2 - הפעלה אוטומטית (systemd service)

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
WorkingDirectory=/home/pi/cartwise
Environment="PATH=/home/pi/cartwise/venv/bin"
EnvironmentFile=/home/pi/agent_config.sh
ExecStart=/home/pi/cartwise/venv/bin/python raspberry_pi/local_agent.py --cloud-url ${CLOUD_URL} --branch-id ${BRANCH_ID} --api-key ${API_KEY} --serial-port ${SERIAL_PORT} --baudrate ${BAUDRATE}
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

---

### שלב 4: הגדרת Kiosk Mode

#### 4.1 - צור סקריפט Kiosk

```bash
nano ~/start_kiosk.sh
```

הכנס:

```bash
#!/bin/bash

source ~/agent_config.sh

# Wait for X server
sleep 5

# Hide mouse
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
    --no-first-run \
    --start-fullscreen \
    $KIOSK_URL
```

שמור והפעל הרשאות:

```bash
chmod +x ~/start_kiosk.sh
```

#### 4.2 - הגדר Auto-start

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
/home/pi/start_kiosk.sh &
```

#### 4.3 - הגדר Auto-Login

```bash
sudo raspi-config
```

- **System Options** → **Boot / Auto Login** → **Desktop Autologin**

הפעל מחדש:

```bash
sudo reboot
```

---

## ✅ בדיקה מלאה

### 1. בדוק Cloud API

פתח דפדפן וגש ל:
```
https://cartwise-cloud.onrender.com/
```

תראה את ממשק הלקוח.

### 2. בדוק Local Agent

על הרספברי:

```bash
sudo journalctl -u cartwise-agent -f
```

תראה:
```
Heartbeat sent
Agent is now running - polling for commands...
```

### 3. בדוק Kiosk

המסך של הרספברי אמור להציג את הממשק במסך מלא.

### 4. בדוק תקשורת מלאה

1. **במסך הרספברי** או **בנייד** (https://cartwise-cloud.onrender.com):
   - לחץ "לקיחת עגלה"
   - הזן מספר טלפון
   - קבל SMS
   - הזן קוד

2. **הענן** שולח פקודה unlock לרספברי
3. **הרספברי** מבצע unlock על RS485
4. **המנעול** נפתח!

---

## 📊 API Endpoints החדשים

### Agent Communication

```
POST /api/agent/register
POST /api/agent/heartbeat/{branch_id}
GET  /api/agent/commands/{branch_id}
POST /api/agent/command-result
POST /api/agent/disconnect/{branch_id}
```

### דוגמת שימוש (לבדיקה ידנית):

```bash
# Register agent
curl -X POST "https://cartwise-cloud.onrender.com/api/agent/register" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "branch_id": "branch_001",
    "agent_type": "raspberry_pi",
    "version": "1.0.0",
    "capabilities": ["rs485", "cu16_controller"]
  }'

# Get commands
curl -X GET "https://cartwise-cloud.onrender.com/api/agent/commands/branch_001" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 🔧 פתרון בעיות

### בעיה: Agent לא מתחבר לענן

```bash
# בדוק חיבור אינטרנט
ping google.com

# בדוק URL של ענן
curl https://cartwise-cloud.onrender.com/docs

# בדוק logs
sudo journalctl -u cartwise-agent -n 50
```

### בעיה: RS485 לא עובד

```bash
# בדוק serial port
ls -l /dev/ttyUSB*

# בדוק הרשאות
groups  # ודא ש-dialout בתוך הרשימה

# הרץ test
cd ~/cartwise
source venv/bin/activate
python test_rs232_adapter.py
```

### בעיה: Kiosk לא מופיע

```bash
# בדוק X server
echo $DISPLAY

# הרץ ידנית
DISPLAY=:0 ~/start_kiosk.sh

# בדוק logs
cat ~/.xsession-errors
```

---

## 🎉 סיימת!

עכשיו יש לך מערכת מלאה:

✅ **Cloud API** - זמין לכל העולם
✅ **Raspberry Pi Kiosk** - ממשק בחנות
✅ **Local Agent** - שולט במנעולים
✅ **RS485 Communication** - עם תמיכה במתאמים

### מה הלקוחות יכולים לעשות:

1. **במסך בחנות** - השתמש בממשק על הרספברי
2. **בנייד** - גש ל-https://cartwise-cloud.onrender.com
3. **במחשב בית** - גש לאותו URL

הכל עובד עם **אותו** ענן ו**אותו** בקר!

---

**גרסה:** 1.0.0
**עודכן:** 2025-10-25
**GitHub:** https://github.com/Arviv123/CartWise
